"""S5 PATH OPTIMIZATION BASELINE v1 at N=4096 (E1.2).

Baseline timing measurement for downstream optimization work. MEASURES
per-op timing at FIXED production config; engineering optimizations
(batched matmul, lower-precision intermediates, vectorized likelihoods)
are downstream work, NOT in this anchor.

SCIENTIFIC QUESTION:
  At N=4096, M=2048, depth=5, K_paths=500 across 5 seeds: what is the
  per-path dominant op + median timing? CV across seeds < 50%?

PRE-REGISTERED BANDS:
  HP = clean baseline emitted: per-path bottleneck op named + median
       timing AND CV across seeds <= 50% for all 3 paths.
  HF = baseline noisy (CV > 50%) across all 3 paths.
  MB = clean for 1-2 paths, noisy for the 3rd.

PROT-018: _n4096.
Anchor: path_optimization_baseline_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_optimization_baseline_v1_n4096.md
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

from experiments._multi_hop_mechanisms import (  # noqa: E402
    TimingTrace, build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s5", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 500
K_PATHS_SMOKE = 50
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 32

HP_CV_THRESHOLD = 0.50


def get_output_dir(default_name: str = "path_optimization_baseline_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_seed(N_use: int, M: int, depth: int, K: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    pos = sample_coherent_starts(relation, depth, N_PATHS, seed)
    neg = sample_incoherent_paths(codebook.shape[0], depth, N_PATHS,
                                    seed, relation=relation)

    tr_b = TimingTrace(); tr_d = TimingTrace(); tr_e = TimingTrace()

    t0 = time.perf_counter_ns()
    _ = path_b_run(codebook, W, starts, depth, N_use, trace=tr_b)
    wall_b = time.perf_counter_ns() - t0

    t1 = time.perf_counter_ns()
    _ = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use,
                    trace=tr_d)
    wall_d = time.perf_counter_ns() - t1

    if pos and neg:
        t2 = time.perf_counter_ns()
        _ = path_e_run(codebook, W, pos, neg, N_use, trace=tr_e)
        wall_e = time.perf_counter_ns() - t2
    else:
        wall_e = 0

    dom_b_op, dom_b_frac = tr_b.dominant_op()
    dom_d_op, dom_d_frac = tr_d.dominant_op()
    dom_e_op, dom_e_frac = tr_e.dominant_op()

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": int(seed),
        "wall_b_ns": int(wall_b),
        "wall_d_ns": int(wall_d),
        "wall_e_ns": int(wall_e),
        "dom_b_op": dom_b_op, "dom_b_frac": round(dom_b_frac, 4),
        "dom_d_op": dom_d_op, "dom_d_frac": round(dom_d_frac, 4),
        "dom_e_op": dom_e_op, "dom_e_frac": round(dom_e_frac, 4),
    }


def _cv(xs: List[float]) -> float:
    if not xs: return 0.0
    mean = sum(xs) / len(xs)
    if mean <= 0: return 0.0
    var = sum((x - mean) ** 2 for x in xs) / len(xs)
    return math.sqrt(var) / mean


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S5_INCONCLUSIVE", "no cells")
    walls_b = [c["wall_b_ns"] for c in cells]
    walls_d = [c["wall_d_ns"] for c in cells]
    walls_e = [c["wall_e_ns"] for c in cells]
    cv_b = _cv(walls_b)
    cv_d = _cv(walls_d)
    cv_e = _cv(walls_e)

    med_b = sorted(walls_b)[len(walls_b) // 2]
    med_d = sorted(walls_d)[len(walls_d) // 2]
    med_e = sorted(walls_e)[len(walls_e) // 2]

    # Most common dom_op per path
    def _mode(xs):
        if not xs: return "none"
        cnt = {}
        for x in xs:
            cnt[x] = cnt.get(x, 0) + 1
        return max(cnt.items(), key=lambda kv: kv[1])[0]

    dom_b = _mode([c["dom_b_op"] for c in cells])
    dom_d = _mode([c["dom_d_op"] for c in cells])
    dom_e = _mode([c["dom_e_op"] for c in cells])

    detail = (f"cv_b={cv_b:.2f} cv_d={cv_d:.2f} cv_e={cv_e:.2f} "
              f"med_b={med_b/1e6:.1f}ms med_d={med_d/1e6:.1f}ms "
              f"med_e={med_e/1e6:.1f}ms dom_b={dom_b} dom_d={dom_d} dom_e={dom_e}")

    n_clean = sum(1 for cv in [cv_b, cv_d, cv_e] if cv <= HP_CV_THRESHOLD)
    if n_clean == 3:
        return ("S5_HARD_PASS", "BASELINE_CLEAN: " + detail)
    if n_clean == 0:
        return ("S5_HARD_FAIL", "BASELINE_NOISY: " + detail)
    return ("S5_MIDDLE_BAND", f"PARTIAL_CLEAN_{n_clean}/3: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 20, 17, device)
    assert out["wall_b_ns"] > 0
    print(f"[selftest] path_optimization_baseline_v1_n4096 PASS "
          f"dom_b={out['dom_b_op']} dom_d={out['dom_d_op']} "
          f"dom_e={out['dom_e_op']}", flush=True)


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
    M = M_SMOKE if smoke else M_PROD
    depth = DEPTH_SMOKE if smoke else DEPTH
    K = K_PATHS_SMOKE if smoke else K_PATHS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_optimization_baseline smoke={smoke} N={N_cfg} "
          f"M={M} depth={depth} K={K} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_seed(N_cfg, M, depth, K, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} wb={out['wall_b_ns']/1e6:.1f}ms "
                  f"wd={out['wall_d_ns']/1e6:.1f}ms we={out['wall_e_ns']/1e6:.1f}ms "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_optimization_baseline_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "K_paths": K, "seeds": seeds,
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
