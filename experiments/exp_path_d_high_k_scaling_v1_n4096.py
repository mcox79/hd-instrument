"""G2 PATH D HIGH-K SCALING v1 at N=4096.

CONTEXT (Batch 1 #2):
  Q3 validated Path D up to K_paths=1000. Production LLM applications
  require K_paths in the 5000-10000 range. This anchor confirms that
  scaling remains approximately linear (slope <= 1.1) and accuracy
  remains >= 0.95 at K=5000.

SCIENTIFIC QUESTION:
  Holding M=8192, depth=5, N=4096 BSC: does Path D maintain >=0.95
  accuracy at K_paths in {1500, 2000, 3000, 5000} AND does
  log(latency) vs log(K) regress with slope <= 1.1?

PRE-REGISTERED BANDS:
  HP = accuracy >= 0.95 at K=5000 in >=3/5 seeds AND scaling slope <= 1.1
       (linear with small headroom).
  HF = accuracy < 0.70 at any K OR scaling slope >= 1.5 (super-linear).
  MB = otherwise.

PER-CELL CHECKPOINT (PROT-021): yes.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. K_GRID_FULL = [1500, 2000, 3000, 5000].
  3. SEEDS_FULL = 5 seeds. 4 K x 5 seeds = 20 cell-seeds.
  4. Scaling slope = log-log OLS of mean_latency vs K (per-seed mean
     then mean across seeds).
  5. HP accuracy gate uses K=5000 only.

OOM CHECK:
  N=4096, M=8192, depth=5, K_max=5000. K x depth indices = 25k longs = 200kB.
  Codebook C=16384 x 4096 = 256 MiB. W = 64 MiB. Peak under 400 MiB.

TIMEOUT ESTIMATE:
  Per cell (K=5000, depth=5, N_STARTS=16) approx 30-60s.
  Smoke (K=20, N=1024) ~5s. FULL: 20 cell-seeds * 60s = 1200s, with margin
  to ~3600s. Budget 14400s per user spec.

N-suffix: _n4096 (PROT-018).
Anchor: path_d_high_k_scaling_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_d_high_k_scaling_v1_n4096.md
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

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import build_relation_facts  # noqa: E402
from experiments._multi_hop_mechanisms import path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g2", _ck_path)
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

M_FIXED = 8192
DEPTH_FIXED = 5
K_GRID_FULL  = [1500, 2000, 3000, 5000]
K_GRID_SMOKE = [20, 50, 100]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_STARTS = 16

BETA_D = 4.0

# Pre-registered thresholds
HP_ACC_AT_KMAX = 0.95
HP_SLOPE_MAX = 1.1
HP_SEEDS_AT_KMAX = 3
HF_ACC_MIN_ANYK = 0.70
HF_SLOPE_MIN = 1.5


def get_output_dir(default_name: str = "path_d_high_k_scaling_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    starts_list = list(relation.keys())[:N_STARTS]
    if not starts_list:
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {"M": int(M), "depth": int(depth), "K_paths": int(K_paths),
                "seed": int(seed), "accuracy": 0.0, "n_eval": 0,
                "lat_ns": 0, "mem_cuda_delta_mib": 0.0}
    starts = torch.tensor(starts_list, dtype=torch.long, device=device)

    cuda_mem_start = (torch.cuda.memory_allocated(device)
                       if device.type == "cuda" else 0)
    t0 = time.perf_counter_ns()
    correct = path_d_run(codebook, W, starts, relation, depth, K_paths,
                          seed, N_use, beta=BETA_D)
    lat_ns = time.perf_counter_ns() - t0
    cuda_mem_peak = (torch.cuda.max_memory_allocated(device)
                      if device.type == "cuda" else 0)
    cuda_delta = cuda_mem_peak - cuda_mem_start

    acc = float(correct.mean().item())
    n_eval = int(correct.shape[0])

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
    return {"M": int(M), "depth": int(depth), "K_paths": int(K_paths),
            "seed": int(seed), "accuracy": round(acc, 5), "n_eval": n_eval,
            "lat_ns": int(lat_ns),
            "mem_cuda_delta_mib": round(cuda_delta / 1024 / 1024, 3)}


def _log_log_slope(xs: List[float], ys: List[float]) -> float:
    """OLS slope of log(y) vs log(x). Returns float or NaN if insufficient."""
    pos = [(math.log(x), math.log(y)) for x, y in zip(xs, ys)
            if x > 0 and y > 0]
    if len(pos) < 2:
        return float("nan")
    n = len(pos)
    mx = sum(p[0] for p in pos) / n
    my = sum(p[1] for p in pos) / n
    num = sum((p[0] - mx) * (p[1] - my) for p in pos)
    den = sum((p[0] - mx) ** 2 for p in pos)
    if den <= 0:
        return float("nan")
    return num / den


def compute_verdict(cells: List[Dict], K_grid: List[int],
                     seeds: List[int]) -> Tuple[str, str]:
    if not cells:
        return ("G2_INCONCLUSIVE", "no cells")

    K_max = max(K_grid)

    # Per-K mean accuracy and mean latency across seeds
    by_K_acc: Dict[int, List[float]] = {}
    by_K_lat: Dict[int, List[float]] = {}
    for c in cells:
        K = c["K_paths"]
        by_K_acc.setdefault(K, []).append(c["accuracy"])
        if c["lat_ns"] > 0:
            by_K_lat.setdefault(K, []).append(c["lat_ns"] / 1e9)

    # Accuracy >= HP_ACC_AT_KMAX at K_max in >=HP_SEEDS_AT_KMAX/N seeds
    acc_kmax = by_K_acc.get(K_max, [])
    n_hit_kmax = sum(1 for a in acc_kmax if a >= HP_ACC_AT_KMAX)

    # HF check: accuracy < HF_ACC_MIN_ANYK at any K (mean across seeds)
    mean_per_K = {K: sum(vs) / len(vs) for K, vs in by_K_acc.items() if vs}
    hf_violation_K = [K for K, m in mean_per_K.items() if m < HF_ACC_MIN_ANYK]

    # Scaling slope: per-K mean latency, log-log fit
    Ks_sorted = sorted(by_K_lat.keys())
    xs = [float(K) for K in Ks_sorted]
    ys = [sum(by_K_lat[K]) / len(by_K_lat[K]) for K in Ks_sorted]
    slope = _log_log_slope(xs, ys)

    detail = (f"K_max={K_max} acc_at_K_max_per_seed={acc_kmax}; "
              f"n_hit_kmax={n_hit_kmax}/{len(acc_kmax)} "
              f"(need>={HP_SEEDS_AT_KMAX}); "
              f"mean_acc_per_K={mean_per_K}; "
              f"slope_log_lat_log_K={slope:.4f} (HP<={HP_SLOPE_MAX}, "
              f"HF>={HF_SLOPE_MIN}); n_cells={len(cells)}")

    if hf_violation_K or (not math.isnan(slope) and slope >= HF_SLOPE_MIN):
        return ("G2_HARD_FAIL", "K_SCALING_BLOWUP: " + detail)
    if (n_hit_kmax >= HP_SEEDS_AT_KMAX
            and not math.isnan(slope) and slope <= HP_SLOPE_MAX):
        return ("G2_HARD_PASS", "K_SCALING_LINEAR_HIGH_K: " + detail)
    return ("G2_MIDDLE_BAND", "K_SCALING_PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_FIXED == 8192
    assert DEPTH_FIXED == 5
    assert K_GRID_FULL == [1500, 2000, 3000, 5000]
    assert len(SEEDS_FULL) == 5

    # Slope sanity
    s = _log_log_slope([1.0, 2.0, 4.0], [1.0, 2.0, 4.0])
    assert abs(s - 1.0) < 1e-6, f"slope 1 expected, got {s}"
    s2 = _log_log_slope([1.0, 2.0, 4.0], [1.0, 4.0, 16.0])
    assert abs(s2 - 2.0) < 1e-6, f"slope 2 expected, got {s2}"

    # HP gate
    fake_hp: List[Dict] = []
    for K in K_GRID_FULL:
        for s_idx, seed in enumerate(SEEDS_FULL):
            fake_hp.append({"M": M_FIXED, "depth": DEPTH_FIXED, "K_paths": K,
                             "seed": seed, "accuracy": 0.97, "n_eval": 16,
                             "lat_ns": int(K * 1e6),  # linear
                             "mem_cuda_delta_mib": 0.0})
    v, _ = compute_verdict(fake_hp, K_GRID_FULL, SEEDS_FULL)
    assert "HARD_PASS" in v, v

    # HF gate (super-linear)
    fake_hf: List[Dict] = []
    for K in K_GRID_FULL:
        for seed in SEEDS_FULL:
            fake_hf.append({"M": M_FIXED, "depth": DEPTH_FIXED, "K_paths": K,
                             "seed": seed, "accuracy": 0.97, "n_eval": 16,
                             "lat_ns": int((K ** 2) * 1e3),  # quadratic
                             "mem_cuda_delta_mib": 0.0})
    v, _ = compute_verdict(fake_hf, K_GRID_FULL, SEEDS_FULL)
    assert "HARD_FAIL" in v, v

    # MB gate (slope OK but accuracy borderline)
    fake_mb: List[Dict] = []
    for K in K_GRID_FULL:
        for seed in SEEDS_FULL:
            acc = 0.90 if K == max(K_GRID_FULL) else 0.96
            fake_mb.append({"M": M_FIXED, "depth": DEPTH_FIXED, "K_paths": K,
                             "seed": seed, "accuracy": acc, "n_eval": 16,
                             "lat_ns": int(K * 1e6),
                             "mem_cuda_delta_mib": 0.0})
    v, _ = compute_verdict(fake_mb, K_GRID_FULL, SEEDS_FULL)
    assert "MIDDLE_BAND" in v, v

    # Smoke forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 256, DEPTH_FIXED, K_GRID_SMOKE[0], 17, device)
    assert out["n_eval"] > 0
    assert out["lat_ns"] > 0
    print(f"[selftest] path_d_high_k_scaling_v1_n4096 PASS smoke "
          f"K={K_GRID_SMOKE[0]} acc={out['accuracy']:.3f} "
          f"lat_ms={out['lat_ns']/1e6:.2f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_use = 256 if smoke else M_FIXED
    K_grid = K_GRID_SMOKE if smoke else K_GRID_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_d_high_k_scaling smoke={smoke} N={N_cfg} "
          f"M={M_use} depth={DEPTH_FIXED} K_grid={K_grid} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for K in K_grid:
        for seed in seeds:
            ck = f"K{K}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body); continue
            try:
                out = measure_cell(N_cfg, M_use, DEPTH_FIXED, K, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  K={K} seed={seed} acc={out['accuracy']:.3f} "
                      f"lat={out['lat_ns']/1e6:.1f}ms "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  K={K} seed={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells, K_grid, seeds)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_d_high_k_scaling_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_use, "depth": DEPTH_FIXED,
               "K_grid": K_grid, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
