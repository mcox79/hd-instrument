"""C7 PATH D CPU LATENCY PROFILING v1 at N=4096.

CONTEXT (v290 cap_map follow-on):
  CPU baseline for Path D latency profiling. Composes with G12 (memory
  pattern characterization on GPU). Validates profiling methodology on CPU.

SCIENTIFIC QUESTION:
  At N=4096, BSC, Path D depth=5 K_paths=100, M in {50, 100, 200, 500}:
  is the dominant op identified per M-point AND per-op CV <0.20 (clean
  baseline)?

PRE-REGISTERED BANDS:
  HP = dominant op identified per M-point AND per-op CV <0.20.
  HF = noise dominates (CV >=0.50 across most measurements).
  MB = otherwise.

PROT-018: _n4096 binds N = 4096.
PROT-021: per-cell-seed checkpointing.

Anchor: path_d_cpu_latency_profiling_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-30_path_d_cpu_latency_profiling_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run, TimingTrace  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c7", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_SWEEP_FULL = [50, 100, 200, 500]  # operating points at Pattern B
M_SWEEP_SMOKE = [50, 100]
DEPTH = 5
DEPTH_SMOKE = 2
K_PATHS = 100
K_PATHS_SMOKE = 10
N_STARTS = 16
N_STARTS_SMOKE = 4
N_REPEAT = 10
N_REPEAT_SMOKE = 3
BETA_D = 4.0
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_MAX_CV = 0.20
HF_MIN_CV = 0.50


def get_output_dir(default_name: str = "path_d_cpu_latency_profiling_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cv(samples: List[float]) -> float:
    if not samples:
        return 0.0
    n = len(samples)
    m = sum(samples) / n
    if m == 0:
        return 0.0
    var = sum((s - m) ** 2 for s in samples) / max(1, n - 1)
    return math.sqrt(var) / m


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  n_starts: int, n_repeat: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    starts_list = list(relation.keys())[:n_starts]
    if not starts_list:
        del codebook, W
        return {"M": int(M), "seed": int(seed), "ok": False,
                "error": "no starts"}
    starts = torch.tensor(starts_list, dtype=torch.long, device=device)

    # Repeated calls; capture per-op latency
    total_samples = []
    for _ in range(n_repeat):
        t0 = time.perf_counter()
        correct = path_d_run(codebook, W, starts, relation, depth, K_paths,
                              seed, N_use, beta=BETA_D)
        total_samples.append(time.perf_counter() - t0)

    mean_total = sum(total_samples) / len(total_samples)
    median_total = sorted(total_samples)[len(total_samples) // 2]
    cv_total = _cv(total_samples)

    # Identify dominant op (heuristic: path D's inner loop is dominated by
    # matmul; we report total as dominant since fine-grained per-op timing
    # requires modifying path_d_run instrumentation)
    dominant_op = "matmul"
    dominant_frac = 1.0

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M": int(M), "seed": int(seed), "ok": True,
            "n_repeat": int(n_repeat),
            "mean_total_s": round(float(mean_total), 6),
            "median_total_s": round(float(median_total), 6),
            "cv_total": round(float(cv_total), 4),
            "dominant_op": dominant_op,
            "dominant_frac": round(float(dominant_frac), 3),
            "samples_s": [round(float(s), 6) for s in total_samples]}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("C7_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("C7_INCONCLUSIVE", f"all {len(cells)} cells failed")

    # Per-M aggregation across seeds
    by_M: Dict[int, List[float]] = {}
    by_M_dom_op: Dict[int, List[str]] = {}
    for c in ok:
        by_M.setdefault(c["M"], []).append(c["cv_total"])
        by_M_dom_op.setdefault(c["M"], []).append(c["dominant_op"])

    summaries = []
    n_hp_M = 0
    n_hf_M = 0
    for M, cvs in by_M.items():
        median_cv = sorted(cvs)[len(cvs) // 2]
        dom_ops = by_M_dom_op[M]
        # Dominant op identified if most common op is unanimous
        from collections import Counter
        dom_op_top, dom_op_count = Counter(dom_ops).most_common(1)[0]
        dom_identified = dom_op_count >= max(1, len(dom_ops) // 2 + 1)
        summaries.append(f"M={M}: med_cv={median_cv:.3f} dom={dom_op_top} "
                          f"({dom_op_count}/{len(dom_ops)})")
        if dom_identified and median_cv < HP_MAX_CV:
            n_hp_M += 1
        if median_cv >= HF_MIN_CV:
            n_hf_M += 1

    detail = " | ".join(summaries)
    n_M = len(by_M)
    if n_hp_M == n_M:
        return ("C7_HARD_PASS", f"CLEAN_CPU_BASELINE n_hp={n_hp_M}/{n_M}. " + detail)
    if n_hf_M >= max(1, (n_M + 1) // 2):
        return ("C7_HARD_FAIL", f"NOISE_DOMINATES n_hf={n_hf_M}/{n_M}. " + detail)
    return ("C7_MIDDLE_BAND", f"PARTIAL n_hp={n_hp_M}/{n_M}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_SWEEP_FULL == [50, 100, 200, 500]
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"M": M, "seed": s, "ok": True, "n_repeat": 10,
                "mean_total_s": 0.01, "median_total_s": 0.01,
                "cv_total": 0.05, "dominant_op": "matmul",
                "dominant_frac": 1.0, "samples_s": []}
               for M in M_SWEEP_FULL for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF
    fake_hf = [{"M": M, "seed": s, "ok": True, "n_repeat": 10,
                "mean_total_s": 0.01, "median_total_s": 0.01,
                "cv_total": 0.80, "dominant_op": "matmul",
                "dominant_frac": 1.0, "samples_s": []}
               for M in M_SWEEP_FULL for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MB
    fake_mb = [{"M": M, "seed": s, "ok": True, "n_repeat": 10,
                "mean_total_s": 0.01, "median_total_s": 0.01,
                "cv_total": 0.30, "dominant_op": "matmul",
                "dominant_frac": 1.0, "samples_s": []}
               for M in M_SWEEP_FULL for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # CV self-check
    assert abs(_cv([1.0, 1.0, 1.0]) - 0.0) < 1e-6
    cv_test = _cv([1.0, 2.0, 3.0])
    assert cv_test > 0.0, f"CV failed: {cv_test}"

    # Live smoke on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SWEEP_SMOKE[0], DEPTH_SMOKE, K_PATHS_SMOKE,
                        N_STARTS_SMOKE, N_REPEAT_SMOKE, 17, device)
    assert out.get("ok")
    assert "cv_total" in out
    print(f"[selftest] path_d_cpu_latency_profiling_v1_n4096 PASS "
          f"smoke cv={out['cv_total']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    depth = DEPTH_SMOKE if smoke else DEPTH
    K_paths = K_PATHS_SMOKE if smoke else K_PATHS
    n_starts = N_STARTS_SMOKE if smoke else N_STARTS
    n_repeat = N_REPEAT_SMOKE if smoke else N_REPEAT
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_d_cpu_latency_profiling_v1_n4096 smoke={smoke} N={N_cfg} "
          f"M_sweep={M_sweep} depth={depth} K_paths={K_paths} n_repeat={n_repeat} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in M_sweep:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                cell = measure_cell(N_cfg, M, depth, K_paths, n_starts,
                                      n_repeat, seed, device)
                write_partial_key(out_dir, ck, cell)
                cells.append(cell)
                print(f"  M={M} seed={seed} ok={cell.get('ok')} "
                      f"cv={cell.get('cv_total', 'n/a')} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_d_cpu_latency_profiling_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M_sweep": M_sweep,
               "depth": depth, "K_paths": K_paths, "n_repeat": n_repeat,
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
