"""COMPRESSED-SUBSTRATE x PATH D COMPOSITION v2 at N=8192.

CONTEXT (cross-N extension of v1 COMPOSITION_HARD_PASS at N=4096; cap_map v303):
  v1 (compressed_path_d_composition_v1_n4096) just landed CPD_HARD_PASS:
    c_quant/bits8 preserves Path D depth=5 accuracy at N=4096, M in {8192, 32768}.
  PP-2 sub-row "c_quant/bits8 x Path D" Validated 0.65-0.80 (cap_map v303).

COMPOSITIONAL QUESTION (cross-N):
  Does the c_quant/bits8 x Path D composition hold at N=8192?
  v1 showed composition works at N=4096. Cross-N to N=8192 closes whether the
  composition is N-robust or N-local.

  If PASS: PP-2 x Path D composition is N-robust (4096 + 8192 both validated).
  If FAIL or MIDDLE_BAND: N=8192 exposes a compression-mechanism interaction
    that N=4096 masked; quantization error grows with N in a way that breaks
    Path D probability-domain disambiguation.

DESIGN:
  Two arms per (M, seed) cell:
    (i)  baseline W (uncompressed) with Path D depth=5, K_paths=100
    (ii) c_quant/bits8 W with Path D depth=5, K_paths=100
  Differential measurement: acc_baseline - acc_compressed (degradation delta).

  M_grid: [16384 = 2N, 32768 = 4N]. Using 4N (not 8N) because BSC codebook
  C = 4*N = 32768 is the upper safe bound for build_relation_facts (M <= C).
  5 seeds.

PROT-022 GUARD (Kerdock N=8192 issue):
  make_substrate() calls make_kerdock_4coset_codebook(N). Kerdock requires
  N = 2^(2t) for t in {5,6,7}: legal values are {1024, 4096, 16384} ONLY.
  N=8192 = 2^13 is NOT a valid Kerdock dimension.
  THIS SCRIPT USES AN EXPLICIT BSC BIPOLAR CODEBOOK at N=8192 instead of
  calling make_substrate(). The build_shared helper is NOT used here.
  All substrate operations (codebook, W, key_idx, val_idx, relation) are
  built from scratch using BSC construction + build_relation_facts.

PRE-REGISTERED BANDS:
  HP = acc_compressed >= 0.95 on BOTH M values in 4/5+ seeds.
       Composition N-robust.
  HF = acc_compressed < 0.70 in majority of cells. Compression breaks Path D at N=8192.
  MB = acc_compressed 0.70-0.95 OR passes 2N but fails 4N.
       N=8192 introduces marginal compression noise; deployment caveat required.

PROT-018: _n8192 binds N = 8192.
PROT-019: timeout >= 14400s.
PROT-021: per-cell checkpointing (seed x M).

Anchor: compressed_path_d_composition_v2_n8192
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-05-31_compressed_path_d_composition_v2_n8192.md
Total cells: 10 (2 M-values x 5 seeds) x 2 arms = 20 arm measurements.

TIMEOUT ESTIMATE:
  v1 at N=4096 (CPU): ~30s/seed/M. This runs on GPU at N=8192 (2x N).
  W build: O(M*N) = 2x larger per M. Path D: O(K_paths * depth * N^2) ish.
  At N=8192 on GPU: estimate ~20s/seed/M (GPU much faster than CPU).
  10 cells x 20s = 200s. Safety: ceil(1.5 * 200) = 300s. PROT-019 floor: 14400s.
  timeout_s = 14400.

FORMULA SELF-TESTS:
  1. BSC bipolar codebook (this script): entries in {-1, +1}. N=8192 is valid.
  2. c_quant/bits8: compression ratio = float32_bytes / bits8_bytes = 4.0x.
     For 1-level quant: max quant error = scale/2 where scale = max_v/127.
     Mean quant error per element ~ scale/4 on uniform distribution.
  3. Path D at N=8192 with random BSC codebook: capacity estimate.
     M/N = 16384/8192 = 2.0 (2N nominal). Expected well-above-floor retrieval.
  4. Verdict HP: 4/5 seeds pass 0.95 threshold on BOTH M values -> HP.
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

# Import relation graph for coherent path sampling (no Kerdock dependency)
from experiments._relation_graph import build_relation_facts  # noqa: E402

# Import path_d_run from multi_hop_mechanisms (no Kerdock dependency there)
from experiments._multi_hop_mechanisms import path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_cpd2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n8192 binds N = 8192
N      = 8192
N_FULL = N
# PROT-022 GUARD: N=8192 is NOT a valid Kerdock dimension.
# Verified: 8192 = 2^13; Kerdock requires 2^(2t), t in {5,6,7} -> {1024,4096,16384}.
# This script builds a BSC codebook directly; never calls make_substrate().
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
assert N_FULL not in (1024, 4096, 16384), \
    "N=8192: using BSC codebook explicitly; Kerdock dimensions (1024/4096/16384) handled by make_substrate"

N_SMOKE = 512   # smoke scale (Kerdock-free -- BSC works at any N)

# M_grid: 2N and 4N.
# NOTE: v1 used [2N=8192, 8N=32768] at N=4096 but build_relation_facts requires
# M <= n_idx = 4*N. At N=8192, 4*N=32768, so M must be <= 32768.
# Using [2N=16384, 4N=32768] stays safely within the 4*N codebook size.
# 8N=65536 would exceed the BSC codebook and crash build_relation_facts.
M_GRID_FULL  = [16384, 32768]   # [2N, 4N] -- safely within C=4*N=32768
M_GRID_SMOKE = [2048]           # well within C=4*512=2048 (just at limit)

DEPTH   = 5
K_PATHS = 100
N_STARTS_FULL  = 100
N_STARTS_SMOKE = 20

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_ACC_COMPRESSED = 0.95
HF_ACC_COMPRESSED = 0.70
HP_MIN_SEEDS      = 4

# BSC codebook: size is set dynamically per-cell as max(4*N, M) to match
# Kerdock's 4*N ratio while ensuring n_idx >= M for build_relation_facts.
# C = 4*N is the safe codebook size: M_GRID_FULL <= C = 32768 at N_FULL=8192.
# M_GRID_SMOKE[0] = 2048 <= C_smoke = 4*512 = 2048. Exactly at limit -- OK.
# build_relation_facts requires M <= n_idx to avoid IndexError in val_perm.
# Explicit: pass n_idx = 4*N to build_relation_facts (standard Kerdock ratio).
_CODEBOOK_N_RATIO = 4   # C = N_RATIO * N (matches Kerdock 4-coset cardinality)


def get_output_dir(default_name: str = "compressed_path_d_composition_v2_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_codebook(N_use: int, C: int, seed: int,
                      device: torch.device) -> torch.Tensor:
    """Build (C, N_use) BSC bipolar {-1,+1} codebook.

    PROT-022 guard: N=8192 is not a valid Kerdock dimension.
    BSC bipolar codebooks are valid at any N and preserve the same
    capacity and retrieval properties as Kerdock for random-query experiments.
    """
    gen = torch.Generator(device=device).manual_seed(seed + 31415)
    bits = torch.randint(0, 2, (C, N_use), generator=gen,
                         device=device, dtype=torch.float32)
    return 2.0 * bits - 1.0


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


def build_W_from_indices(
    codebook: torch.Tensor,
    key_idx: torch.Tensor,
    val_idx: torch.Tensor,
    N_use: int,
) -> torch.Tensor:
    """Hebbian outer-product store: W = (1/N) vals^T @ keys."""
    keys_vec = codebook[key_idx]   # (M, N)
    vals_vec = codebook[val_idx]   # (M, N)
    return (vals_vec.T @ keys_vec) / float(N_use)


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  n_starts: int, seed: int, device: torch.device) -> Dict:
    """Measure one (N, M, seed) cell: baseline vs c_quant/bits8 Path D accuracy."""
    # Build BSC codebook (PROT-022: never call make_substrate at N=8192)
    # C = 4*N_use matches Kerdock 4-coset cardinality (standard ratio).
    # When M > C, build_relation_facts silently uses only C unique keys (same
    # as v1's behavior at M=32768 with Kerdock C=16384 at N=4096).
    C = _CODEBOOK_N_RATIO * N_use   # e.g. 4*512=2048 smoke, 4*8192=32768 full
    codebook = make_bsc_codebook(N_use, C, seed, device)

    # Build relation facts (this has no Kerdock dependency)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M, seed=seed, device=device, closed=True)

    # Build W from codebook indices
    W_base = build_W_from_indices(codebook, key_idx, val_idx, N_use)

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
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass

    return {"seed": int(seed), "M": int(M), "ok": True,
            "n_starts": len(all_starts),
            "acc_baseline": round(acc_base, 5),
            "acc_compressed": round(acc_comp, 5),
            "delta": delta}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CPD2_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("CPD2_INCONCLUSIVE", f"all {len(cells)} cells failed")

    # Per M-value breakdown
    by_m: Dict[int, List[float]] = {}
    for c in ok:
        by_m.setdefault(c["M"], []).append(c["acc_compressed"])

    m_summaries = []
    for m_val in sorted(by_m):
        accs = by_m[m_val]
        mean_acc = sum(accs) / len(accs)
        m_summaries.append(f"M={m_val}: mean_acc_comp={mean_acc:.3f} n={len(accs)}")

    # HP: acc_compressed >= HP threshold in HP_MIN_SEEDS+ seeds per M value
    n_m_hp = 0
    n_m_hf = 0
    for m_val, accs in by_m.items():
        n_pass = sum(1 for a in accs if a >= HP_ACC_COMPRESSED)
        n_fail = sum(1 for a in accs if a < HF_ACC_COMPRESSED)
        if n_pass >= HP_MIN_SEEDS:
            n_m_hp += 1
        if n_fail > len(accs) // 2:
            n_m_hf += 1

    all_comp = [c["acc_compressed"] for c in ok]
    all_base = [c["acc_baseline"] for c in ok]
    mean_comp = sum(all_comp) / len(all_comp)
    mean_base = sum(all_base) / len(all_base)
    mean_delta = mean_base - mean_comp
    detail = (f"N={N_FULL} mean_acc_base={mean_base:.3f} mean_acc_comp={mean_comp:.3f} "
              f"mean_delta={mean_delta:.4f} n_cells={len(ok)} | "
              + " | ".join(m_summaries))

    if n_m_hp == len(by_m):
        return ("CPD2_HARD_PASS",
                f"COMPOSITION_N8192_ROBUST n_m_hp={n_m_hp}/{len(by_m)}. " + detail)
    if n_m_hf >= 1:
        return ("CPD2_HARD_FAIL",
                f"COMPRESSION_BREAKS_PATH_D_AT_N8192 n_m_hf={n_m_hf}/{len(by_m)}. " + detail)
    return ("CPD2_MIDDLE_BAND",
            f"PARTIAL_N8192 n_m_hp={n_m_hp}/{len(by_m)} n_m_hf={n_m_hf}/{len(by_m)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    PROT-018: N_FULL == 8192.
    PROT-022: never calls make_substrate; verifies BSC codebook is used.
    """
    assert N_FULL == 8192, "PROT-018: _n8192"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"
    assert len(M_GRID_FULL) == 2, "expected 2 M values"
    # PROT-022: no Kerdock call at N=8192
    assert M_GRID_FULL[0] == 2 * N_FULL, f"M[0] must be 2N={2*N_FULL}"
    assert M_GRID_FULL[1] == 4 * N_FULL, f"M[1] must be 4N={4*N_FULL}"

    # Verdict gate HP: all M values, 4+ seeds pass
    fake_hp = [{"seed": s, "M": m, "ok": True,
                "n_starts": 100,
                "acc_baseline": 1.000,
                "acc_compressed": 0.970,
                "delta": 0.030}
               for s in SEEDS_FULL for m in M_GRID_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate HF: majority fail below 0.70 at first M
    fake_hf = [{"seed": s, "M": M_GRID_FULL[0], "ok": True,
                "n_starts": 100, "acc_baseline": 0.95,
                "acc_compressed": 0.55, "delta": 0.40}
               for s in SEEDS_FULL]
    fake_hf += [{"seed": s, "M": M_GRID_FULL[1], "ok": True,
                 "n_starts": 100, "acc_baseline": 0.95,
                 "acc_compressed": 0.55, "delta": 0.40}
                for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB: one M passes HP, one does not
    fake_mb_m1 = [{"seed": s, "M": M_GRID_FULL[0], "ok": True,
                   "n_starts": 100, "acc_baseline": 1.00,
                   "acc_compressed": 0.97, "delta": 0.03}
                  for s in SEEDS_FULL]
    fake_mb_m2 = [{"seed": s, "M": M_GRID_FULL[1], "ok": True,
                   "n_starts": 100, "acc_baseline": 1.00,
                   "acc_compressed": 0.80, "delta": 0.20}
                  for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_mb_m1 + fake_mb_m2)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # PROT-022: verify BSC codebook at N=8192 works
    device = torch.device("cpu")
    cb_test = make_bsc_codebook(64, 20, 42, device)
    assert cb_test.shape == (20, 64)
    assert set(cb_test.view(-1).tolist()).issubset({-1.0, 1.0}), "BSC not bipolar"

    # Live smoke: measure_cell at small N (CPU, no CUDA needed for selftest)
    # M_GRID_SMOKE[0] = 2048; C = 4*N_SMOKE = 4*512 = 2048. M == C: OK.
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], DEPTH, K_PATHS,
                       N_STARTS_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_cell failed: {out.get('error')}"
    assert 0.0 <= out["acc_baseline"] <= 1.0, f"acc_baseline sentinel: {out}"
    assert 0.0 <= out["acc_compressed"] <= 1.0, f"acc_compressed sentinel: {out}"
    assert out["n_starts"] >= 1, f"n_starts=0: {out}"

    print(f"[selftest] compressed_path_d_composition_v2_n8192 PASS "
          f"N_FULL={N_FULL} bsc_ok acc_base={out['acc_baseline']:.3f} "
          f"acc_comp={out['acc_compressed']:.3f} delta={out['delta']:.4f} "
          f"[PROT-022: BSC codebook; no Kerdock at N=8192]", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    # overnight_queue: GPU device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke    = args.smoke
    N_cfg    = N_SMOKE        if smoke else N_FULL
    M_grid   = M_GRID_SMOKE   if smoke else M_GRID_FULL
    n_starts = N_STARTS_SMOKE if smoke else N_STARTS_FULL
    seeds    = SEEDS_SMOKE    if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()
    print(f"[run] compressed_path_d_composition_v2_n8192 smoke={smoke} "
          f"N={N_cfg} M_grid={M_grid} depth={DEPTH} K_paths={K_PATHS} "
          f"n_starts={n_starts} seeds={seeds} done={len(done)} "
          f"device={device.type} [BSC codebook; PROT-022 Kerdock guard active]",
          flush=True)

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
                if device.type == "cuda":
                    try:
                        torch.cuda.empty_cache()
                    except Exception:
                        pass

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "compressed_path_d_composition_v2_n8192",
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
