"""T5 PATH B SUBCAPACITY CHARACTERIZATION v1 at N=4096 (Test 24).

Path B operates as a continuous-output substrate. Pattern B LLM integration
operates at M=50-500 (well sub-capacity). Characterize Path B specifically
at this Pattern B regime.

SETUP:
  N=4096, BSC, Path B ONLY. M sweep [50, 100, 200, 500]. depth in [3, 5, 8].
  5 seeds.

COMPARISON:
  - Path B continuous-output vs Path D Bayesian at the same operating points
    (latency + accuracy).
  - Multi-hop depth in [3, 5, 8].
  - Continuous-representation advantages:
      * geometric interpolation between facts (cosine similarity between
        interpolated query and expected output).

METRICS:
  - per-M per-depth accuracy (Path B vs Path D).
  - per-M per-depth latency (Path B vs Path D).
  - geometric-interpolation cosine score (Path B-specific).

PRE-REGISTERED BANDS:
  HP = Path B at Pattern B regime (M <= 500) achieves >=0.90 accuracy
       AND latency < Path D
       AND geometric-interpolation cosine >= 0.85.
  HF = Path B accuracy < 0.70 at any M in sweep OR latency > Path D.
  MB = otherwise.

PROT-018: _n4096 binds N = 4096.
Anchor: path_b_subcapacity_characterization_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_b_subcapacity_characterization_v1_n4096.md
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

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_b_run, path_d_run,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_t5pb", _ck_path)
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

M_SWEEP_FULL = [50, 100, 200, 500]
M_SWEEP_SMOKE = [50, 200]
DEPTH_SWEEP_FULL = [3, 5, 8]
DEPTH_SWEEP_SMOKE = [3]
K_PATHS = 100
K_PATHS_SMOKE = 20
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS_FULL = 24
N_PATHS_SMOKE = 8

HP_ACC = 0.90
HP_GEOM_COS = 0.85
HF_ACC = 0.70


def get_output_dir(default_name: str = "path_b_subcapacity_characterization_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_geometric_interpolation(codebook: torch.Tensor, W: torch.Tensor,
                                     relation: Dict[int, int],
                                     starts: torch.Tensor,
                                     depth: int, N_use: int) -> float:
    """Compute mean cosine similarity between Path B continuous response
    (without final argmax) and the expected output vector.
    """
    device = codebook.device
    cosines = []
    for b in range(starts.shape[0]):
        start = int(starts[b].item())
        cur = start
        ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = int(nxt)
        if not ok:
            continue
        target_vec = codebook[cur]
        q = codebook[start:start + 1].clone()
        for _ in range(depth):
            q = q @ W.T
        q_flat = q.squeeze(0)
        num = (q_flat * target_vec).sum()
        den = (q_flat.norm() * target_vec.norm()).clamp_min(1e-9)
        cos = float((num / den).item())
        cosines.append(cos)
    if not cosines:
        return 0.0
    return sum(cosines) / len(cosines)


def measure_cell(N_use: int, M: int, depth: int, K: int, n_paths: int,
                 seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]

    starts = torch.tensor(list(relation.keys())[:n_paths],
                          dtype=torch.long, device=device)
    targets = []
    for k in starts.tolist():
        cur = int(k); ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                ok = False
                break
            cur = int(nxt)
        targets.append(cur if ok else -1)
    tgt = torch.tensor(targets, dtype=torch.long, device=device)
    valid = tgt >= 0

    # Path B
    t0 = time.perf_counter_ns()
    pred_b = path_b_run(codebook, W, starts, depth, N_use)
    lat_b = time.perf_counter_ns() - t0
    acc_b = float((pred_b[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0

    # Path D (comparison)
    t1 = time.perf_counter_ns()
    correct_d = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    lat_d = time.perf_counter_ns() - t1
    acc_d = float(correct_d.mean().item())

    # Geometric interpolation (Path B specific)
    geom_cos = measure_geometric_interpolation(codebook, W, relation, starts,
                                                depth, N_use)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"M": int(M), "depth": int(depth), "seed": int(seed),
            "K": int(K), "n_valid": int(valid.sum().item()),
            "acc_b": round(acc_b, 5), "acc_d": round(acc_d, 5),
            "lat_b_ns": int(lat_b), "lat_d_ns": int(lat_d),
            "lat_b_faster_than_d": bool(lat_b < lat_d),
            "geom_cos_b": round(geom_cos, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("T5_INCONCLUSIVE", "no cells")

    # Aggregate by (M, depth); HP requires HP_ACC and lat_b<lat_d and geom>=HP_GEOM_COS
    # in >=3/5 seeds for ALL (M, depth) cell groups (M is in Pattern B regime since
    # the sweep is bounded at M<=500).
    by_cell: Dict[Tuple[int, int], List[Dict]] = {}
    for c in cells:
        key = (c["M"], c["depth"])
        by_cell.setdefault(key, []).append(c)

    hp_groups = 0
    hf_triggers = []
    for k, v in by_cell.items():
        n_seeds = len(v)
        threshold = max(1, (n_seeds * 3) // 5)
        n_acc_hp = sum(1 for c in v if c["acc_b"] >= HP_ACC)
        n_lat_ok = sum(1 for c in v if c["lat_b_faster_than_d"])
        n_geom_ok = sum(1 for c in v if c["geom_cos_b"] >= HP_GEOM_COS)
        n_acc_hf = sum(1 for c in v if c["acc_b"] < HF_ACC)
        n_lat_hf = sum(1 for c in v if not c["lat_b_faster_than_d"])
        if (n_acc_hp >= threshold and
            n_lat_ok >= threshold and
            n_geom_ok >= threshold):
            hp_groups += 1
        if n_acc_hf >= threshold:
            hf_triggers.append(f"{k}=acc_hf{n_acc_hf}")
        if n_lat_hf >= threshold:
            hf_triggers.append(f"{k}=lat_hf{n_lat_hf}")

    n_groups = len(by_cell)
    detail = (f"n_groups={n_groups} hp_groups={hp_groups} "
              f"hf_triggers={len(hf_triggers)}")
    if n_groups > 0 and hp_groups == n_groups and not hf_triggers:
        return ("T5_HARD_PASS", "PATH_B_SUBCAPACITY_KILLER: " + detail)
    if hf_triggers:
        return ("T5_HARD_FAIL",
                f"PATH_B_FAILS_PATTERN_B: {detail} triggers={hf_triggers[:5]}")
    return ("T5_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 50, 2, 10, 8, 17, device)
    assert out["acc_b"] is not None and not (out["acc_b"] != out["acc_b"])
    assert out["geom_cos_b"] is not None
    assert "lat_b_faster_than_d" in out
    assert out["n_valid"] > 0, f"validity filter eliminated all paths at smoke: {out}"
    print(f"[selftest] path_b_subcapacity_characterization_v1_n4096 PASS "
          f"acc_b={out['acc_b']:.3f} acc_d={out['acc_d']:.3f} "
          f"geom_cos={out['geom_cos_b']:.3f} "
          f"lat_b<d={out['lat_b_faster_than_d']}", flush=True)


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
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    depths = DEPTH_SWEEP_SMOKE if smoke else DEPTH_SWEEP_FULL
    K = K_PATHS_SMOKE if smoke else K_PATHS
    n_paths = N_PATHS_SMOKE if smoke else N_PATHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_b_subcapacity_characterization smoke={smoke} N={N_cfg} "
          f"M_sweep={M_sweep} depths={depths} K={K} n_paths={n_paths} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in M_sweep:
        for depth in depths:
            for seed in seeds:
                ck = f"M{M}_d{depth}_s{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body)
                        continue
                try:
                    out = measure_cell(N_cfg, M, depth, K, n_paths, seed,
                                       device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  M={M} d={depth} s={seed} "
                          f"acc_b={out['acc_b']:.3f} acc_d={out['acc_d']:.3f} "
                          f"geom={out['geom_cos_b']:.3f} "
                          f"lat_b<d={out['lat_b_faster_than_d']} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  M={M} d={depth} s={seed} FAILED: {e}",
                          flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_b_subcapacity_characterization_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M_sweep": M_sweep, "depths": depths, "K_paths": K,
               "n_paths": n_paths, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
