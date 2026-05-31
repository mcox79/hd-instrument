"""COMPRESSED-SUBSTRATE x PATH D COMPOSITION v1 at N=4096.

CONTEXT (PP-2 foothold + R-PATH-D-NO-CEILING composition test):
  C3 v2 HARD_PASS (today): c_quant/bits8 preserves KF-1/KF-2/KF-3 at N=4096.
  G7 + G7EXT HARD_PASS (prior): Path D no-ceiling 16N-64N at N=4096.

COMPOSITIONAL QUESTION:
  Does Path D depth=5 maintain perfect (>=0.95) accuracy on a c_quant/bits8
  COMPRESSED substrate W?

  If YES: c_quant/bits8 is production-ready as a compression layer for the
  production-default mechanism. PP-2 foothold is mechanism-compatible.

  If NO: PP-2 foothold caveat tightens -- compression breaks the mechanism
  it's supposed to compress. Important production deployment constraint.

DESIGN:
  Two arms per (M, seed) cell:
    (i)  baseline W (uncompressed) with Path D at depth=5, K_paths=100
    (ii) c_quant/bits8 W with Path D at depth=5, K_paths=100
  Differential measurement: acc_baseline - acc_compressed (degradation delta).

  M_grid: [8192, 32768] (2N=nominal, 8N=over-capacity)
  5 seeds.

PRE-REGISTERED BANDS:
  HP = acc_compressed >= 0.95 on BOTH M values in 4/5+ seeds. Composition
       production-ready.
  HF = acc_compressed < 0.70 in majority of cells. Compression breaks Path D.
  MB = acc_compressed 0.70-0.95 OR passes nominal but fails over-capacity.
       Composition marginal -- deployment caveats required.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-021: per-cell checkpointing (seed x M).

Anchor: compressed_path_d_composition_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_compressed_path_d_composition_v1_n4096.md
Total cells: 10 (2 M-values x 5 seeds) x 2 arms = 20 arm measurements.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402
from experiments._relation_graph import sample_coherent_starts  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_cpd", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024  # must be power-of-2 with even log2 for Kerdock codebook
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M_grid: 2N (nominal) and 8N (over-capacity)
M_GRID_FULL  = [8192, 32768]
M_GRID_SMOKE = [2048]

DEPTH = 5
K_PATHS = 100
N_STARTS_FULL  = 100
N_STARTS_SMOKE = 20
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_ACC_COMPRESSED = 0.95
HF_ACC_COMPRESSED = 0.70
HP_MIN_SEEDS      = 4


def get_output_dir(default_name: str = "compressed_path_d_composition_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compress_quant_bits8(W: torch.Tensor) -> torch.Tensor:
    """c_quant/bits8: per-tensor symmetric INT8 quantization (dequantized)."""
    bits = 8
    max_v = float(W.abs().max().item())
    if max_v == 0:
        return W.clone()
    n_levels = (1 << (bits - 1)) - 1  # 127
    scale = max_v / n_levels
    q = torch.clamp(torch.round(W / scale), -n_levels, n_levels)
    return q * scale


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  n_starts: int, seed: int, device: torch.device) -> Dict:
    codebook, W_base, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    # Compressed W
    W_comp = compress_quant_bits8(W_base)

    # Start nodes: use relation keys capped by n_starts
    all_starts = [k for k in list(relation.keys())[:n_starts]]
    if len(all_starts) < depth + 1:
        del codebook, W_base, W_comp
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": f"not enough relation keys: {len(all_starts)}"}

    starts_t = torch.tensor(all_starts, dtype=torch.long, device=device)

    # Path D on baseline W
    correct_base = path_d_run(
        codebook, W_base, starts_t, relation, depth, K_paths, seed, N_use)
    acc_base = float(correct_base.mean().item())

    # Path D on compressed W
    correct_comp = path_d_run(
        codebook, W_comp, starts_t, relation, depth, K_paths, seed + 1000, N_use)
    acc_comp = float(correct_comp.mean().item())

    delta = round(acc_base - acc_comp, 6)

    del codebook, W_base, W_comp
    return {"seed": int(seed), "M": int(M), "ok": True,
            "n_starts": len(all_starts),
            "acc_baseline": round(acc_base, 5),
            "acc_compressed": round(acc_comp, 5),
            "delta": delta}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CPD_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("CPD_INCONCLUSIVE", f"all {len(cells)} cells failed")

    # Per M-value breakdown
    by_m: Dict[int, List[float]] = {}
    for c in ok:
        by_m.setdefault(c["M"], []).append(c["acc_compressed"])

    m_summaries = []
    for m_val in sorted(by_m):
        accs = by_m[m_val]
        mean_acc = sum(accs) / len(accs)
        m_summaries.append(f"M={m_val}: mean_acc_comp={mean_acc:.3f} n={len(accs)}")

    # HP: acc_compressed >= HP_ACC_COMPRESSED in HP_MIN_SEEDS+ seeds per M value
    n_m_hp = 0
    n_m_hf = 0
    for m_val, accs in by_m.items():
        n_pass = sum(1 for a in accs if a >= HP_ACC_COMPRESSED)
        n_fail = sum(1 for a in accs if a < HF_ACC_COMPRESSED)
        if n_pass >= HP_MIN_SEEDS:
            n_m_hp += 1
        if n_fail > len(accs) // 2:
            n_m_hf += 1

    # Also compute overall stats
    all_comp = [c["acc_compressed"] for c in ok]
    all_base = [c["acc_baseline"] for c in ok]
    mean_comp = sum(all_comp) / len(all_comp)
    mean_base = sum(all_base) / len(all_base)
    mean_delta = mean_base - mean_comp
    detail = (f"mean_acc_base={mean_base:.3f} mean_acc_comp={mean_comp:.3f} "
              f"mean_delta={mean_delta:.4f} n_cells={len(ok)} | "
              + " | ".join(m_summaries))

    if n_m_hp == len(by_m):
        return ("CPD_HARD_PASS",
                f"COMPOSITION_PRODUCTION_READY n_m_hp={n_m_hp}/{len(by_m)}. " + detail)
    if n_m_hf >= 1:
        return ("CPD_HARD_FAIL",
                f"COMPRESSION_BREAKS_PATH_D n_m_hf={n_m_hf}/{len(by_m)}. " + detail)
    return ("CPD_MIDDLE_BAND",
            f"PARTIAL n_m_hp={n_m_hp}/{len(by_m)} n_m_hf={n_m_hf}/{len(by_m)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale."""
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert len(M_GRID_FULL) == 2, f"expected 2 M values"

    # Verdict gate HP: all M values, 4+ seeds pass
    fake_hp = [{"seed": s, "M": m, "ok": True,
                "n_starts": 100,
                "acc_baseline": 1.000,
                "acc_compressed": 0.980,
                "delta": 0.020}
               for s in SEEDS_FULL for m in M_GRID_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate HF: majority of cells below HF threshold at M=8192
    fake_hf = [{"seed": s, "M": 8192, "ok": True,
                "n_starts": 100, "acc_baseline": 0.95,
                "acc_compressed": 0.50, "delta": 0.45}
               for s in SEEDS_FULL]
    fake_hf += [{"seed": s, "M": 32768, "ok": True,
                 "n_starts": 100, "acc_baseline": 0.95,
                 "acc_compressed": 0.50, "delta": 0.45}
                for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB: one M passes, one does not reach HP threshold
    fake_mb_m1 = [{"seed": s, "M": 8192, "ok": True,
                   "n_starts": 100, "acc_baseline": 1.00,
                   "acc_compressed": 0.96, "delta": 0.04}
                  for s in SEEDS_FULL]
    fake_mb_m2 = [{"seed": s, "M": 32768, "ok": True,
                   "n_starts": 100, "acc_baseline": 1.00,
                   "acc_compressed": 0.80, "delta": 0.20}
                  for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_mb_m1 + fake_mb_m2)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # Live smoke: measure_cell at small N
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 1024, DEPTH, K_PATHS, N_STARTS_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_cell failed: {out.get('error')}"
    assert 0.0 <= out["acc_baseline"] <= 1.0, f"acc_baseline sentinel: {out}"
    assert 0.0 <= out["acc_compressed"] <= 1.0, f"acc_compressed sentinel: {out}"
    assert out["n_starts"] >= 1, f"n_starts=0: {out}"
    print(f"[selftest] compressed_path_d_composition_v1_n4096 PASS "
          f"acc_base={out['acc_baseline']:.3f} acc_comp={out['acc_compressed']:.3f} "
          f"delta={out['delta']:.4f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    # PROT: force CPU -- remote_cpu_queue; must never touch CUDA
    device = torch.device("cpu")
    smoke  = args.smoke
    N_cfg    = N_SMOKE       if smoke else N_FULL
    M_grid   = M_GRID_SMOKE  if smoke else M_GRID_FULL
    n_starts = N_STARTS_SMOKE if smoke else N_STARTS_FULL
    seeds    = SEEDS_SMOKE   if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()
    print(f"[run] compressed_path_d_composition_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M_grid={M_grid} depth={DEPTH} K_paths={K_PATHS} "
          f"n_starts={n_starts} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        for M in M_grid:
            ck = f"seed{seed}_M{M}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    continue
            try:
                cell = measure_cell(N_cfg, M, DEPTH, K_PATHS, n_starts, seed, device)
                write_partial_key(out_dir, ck, cell)
                cells.append(cell)
                print(f"  seed={seed} M={M} ok={cell.get('ok')} "
                      f"acc_base={cell.get('acc_baseline','n/a')} "
                      f"acc_comp={cell.get('acc_compressed','n/a')} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  seed={seed} M={M} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "compressed_path_d_composition_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M_grid": M_grid,
               "depth": DEPTH, "K_paths": K_PATHS, "n_starts": n_starts,
               "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
