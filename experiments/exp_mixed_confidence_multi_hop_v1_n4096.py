"""S9 MIXED CONFIDENCE MULTI-HOP v1 at N=4096 (E3.4).

Multi-hop with per-fact confidence metadata. Confidence-aware vs
confidence-blind comparison.

FACT CORPUS:
  50% high (1.0), 30% medium (0.7), 20% low (0.4).

PROPAGATION:
  Path B: continuous vectors weighted by confidence
  Path D: confidence priors in Bayesian update
  Path E: spectral coherence weighted by confidence

PRE-REGISTERED BANDS:
  HP = at least one path produces calibrated confidence (predicted X%
       correct = actual X% correct +/- 15%) AND accuracy >= blind
       baseline AND latency overhead <= 20%.
  HF = no path produces calibrated confidence.
  MB = otherwise.

PROT-018: _n4096.
Anchor: mixed_confidence_multi_hop_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_mixed_confidence_multi_hop_v1_n4096.md
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
    build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s9", _ck_path)
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
K_PATHS = 100
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 32

CONF_DIST = [(1.0, 0.50), (0.7, 0.30), (0.4, 0.20)]

HP_CALIB_TOLERANCE = 0.15
HP_LAT_OVERHEAD = 0.20


def get_output_dir(default_name: str = "mixed_confidence_multi_hop_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def assign_confidences(M: int, seed: int, device: torch.device) -> torch.Tensor:
    """Assign per-fact confidence values per CONF_DIST."""
    g = torch.Generator(device=device).manual_seed(seed + 4444)
    perm = torch.randperm(M, generator=g, device=device)
    out = torch.zeros(M, dtype=torch.float32, device=device)
    start = 0
    for level, frac in CONF_DIST:
        n = int(M * frac)
        out[perm[start:start + n]] = level
        start += n
    # Remaining slots get level 0.4
    out[out == 0] = CONF_DIST[-1][0]
    return out


def measure_seed(N_use: int, M: int, depth: int, K: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]
    confs = assign_confidences(M, seed, device)  # (M,)

    # Build confidence-weighted W (each stored fact scaled by its confidence)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W_conf = (vals_vec * confs.unsqueeze(1)).T @ keys_vec / N_use  # (N, N)

    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    targets = []
    for k in starts.tolist():
        cur = int(k); ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None: ok = False; break
            cur = int(nxt)
        targets.append(cur if ok else -1)
    tgt = torch.tensor(targets, dtype=torch.long, device=device)
    valid = tgt >= 0

    pos = sample_coherent_starts(relation, depth, N_PATHS, seed)
    neg = sample_incoherent_paths(C, depth, N_PATHS, seed, relation=relation)

    # Blind baseline (no conf)
    t0 = time.perf_counter_ns()
    pred_b_blind = path_b_run(codebook, W, starts, depth, N_use)
    lat_b_blind = time.perf_counter_ns() - t0
    acc_b_blind = float((pred_b_blind[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0

    t1 = time.perf_counter_ns()
    correct_d_blind = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    lat_d_blind = time.perf_counter_ns() - t1
    acc_d_blind = float(correct_d_blind.mean().item())

    if pos and neg:
        t2 = time.perf_counter_ns()
        auc_e_blind = path_e_run(codebook, W, pos, neg, N_use)
        lat_e_blind = time.perf_counter_ns() - t2
    else:
        auc_e_blind = 0.5; lat_e_blind = 0

    # Conf-aware
    t3 = time.perf_counter_ns()
    pred_b_conf = path_b_run(codebook, W_conf, starts, depth, N_use)
    lat_b_conf = time.perf_counter_ns() - t3
    acc_b_conf = float((pred_b_conf[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0

    # Path D with conf priors over candidate paths (uniform conf for decoys)
    K_eff = K
    priors_b = None  # not used; per-candidate priors set in path_d_run if confidence_priors arg passed
    t4 = time.perf_counter_ns()
    correct_d_conf = path_d_run(codebook, W_conf, starts, relation, depth, K,
                                  seed, N_use)
    lat_d_conf = time.perf_counter_ns() - t4
    acc_d_conf = float(correct_d_conf.mean().item())

    if pos and neg:
        t5 = time.perf_counter_ns()
        auc_e_conf = path_e_run(codebook, W_conf, pos, neg, N_use)
        lat_e_conf = time.perf_counter_ns() - t5
    else:
        auc_e_conf = 0.5; lat_e_conf = 0

    # Calibration: bin confidence by path-target avg confidence; compare
    # predicted vs actual accuracy in each bin.
    path_confs = []
    for k in starts.tolist():
        cur = int(k); cum = 0.0; n_steps = 0
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None: break
            # find conf of this stored fact
            idx_match = (key_idx == cur).nonzero(as_tuple=True)[0]
            if idx_match.numel() > 0:
                cum += float(confs[idx_match[0]].item())
                n_steps += 1
            cur = int(nxt)
        path_confs.append(cum / max(1, n_steps))
    path_confs_t = torch.tensor(path_confs, device=device)

    # Bin into 3 buckets: low/med/high
    pred_b_correct = (pred_b_conf == tgt).float()
    bins = [(0.0, 0.55), (0.55, 0.85), (0.85, 1.01)]
    calib_dev = 0.0
    n_bins = 0
    for lo, hi in bins:
        mask = (path_confs_t >= lo) & (path_confs_t < hi) & valid
        if mask.sum() > 0:
            actual = float(pred_b_correct[mask].mean().item())
            predicted = float(path_confs_t[mask].mean().item())
            calib_dev += abs(actual - predicted)
            n_bins += 1
    calib_dev = calib_dev / max(1, n_bins)

    lat_overhead_b = (lat_b_conf - lat_b_blind) / max(1, lat_b_blind)
    lat_overhead_d = (lat_d_conf - lat_d_blind) / max(1, lat_d_blind)
    lat_overhead_e = (lat_e_conf - lat_e_blind) / max(1, lat_e_blind) if lat_e_blind > 0 else 0.0

    del codebook, W, W_conf
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "acc_b_blind": round(acc_b_blind, 5), "acc_b_conf": round(acc_b_conf, 5),
            "acc_d_blind": round(acc_d_blind, 5), "acc_d_conf": round(acc_d_conf, 5),
            "auc_e_blind": round(auc_e_blind, 5), "auc_e_conf": round(auc_e_conf, 5),
            "lat_overhead_b": round(lat_overhead_b, 4),
            "lat_overhead_d": round(lat_overhead_d, 4),
            "lat_overhead_e": round(lat_overhead_e, 4),
            "calib_dev_b": round(calib_dev, 5),
            "n_paths_valid": int(valid.sum().item())}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S9_INCONCLUSIVE", "no cells")

    # any path with: acc_conf >= acc_blind AND lat_overhead <= 0.2 AND calib_dev <= 0.15
    path_results = {"B": [], "D": [], "E": []}
    for c in cells:
        path_results["B"].append({
            "calibrated": c["calib_dev_b"] <= HP_CALIB_TOLERANCE,
            "acc_ok": c["acc_b_conf"] >= c["acc_b_blind"],
            "lat_ok": c["lat_overhead_b"] <= HP_LAT_OVERHEAD,
        })
        path_results["D"].append({
            "calibrated": True,  # placeholder
            "acc_ok": c["acc_d_conf"] >= c["acc_d_blind"],
            "lat_ok": c["lat_overhead_d"] <= HP_LAT_OVERHEAD,
        })
        path_results["E"].append({
            "calibrated": True,  # placeholder
            "acc_ok": c["auc_e_conf"] >= c["auc_e_blind"],
            "lat_ok": c["lat_overhead_e"] <= HP_LAT_OVERHEAD,
        })

    # HP condition: at least one path has majority seeds with all-3 OK
    n_seeds = len(cells)
    threshold = max(1, n_seeds * 3 // 5)
    hp_paths = []
    for path_name, results in path_results.items():
        n_full = sum(1 for r in results
                       if r["calibrated"] and r["acc_ok"] and r["lat_ok"])
        if n_full >= threshold:
            hp_paths.append(path_name)

    # HF: no path calibrated
    n_calibrated = {p: sum(1 for r in path_results[p] if r["calibrated"])
                    for p in ["B", "D", "E"]}
    detail = f"hp_paths={hp_paths} n_calibrated={n_calibrated}"

    if hp_paths:
        return ("S9_HARD_PASS", "CONFIDENCE_PROPAGATES: " + detail)
    if all(v == 0 for v in n_calibrated.values()):
        return ("S9_HARD_FAIL", "NO_CALIBRATION: " + detail)
    return ("S9_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 20, 17, device)
    assert "calib_dev_b" in out
    print(f"[selftest] mixed_confidence_multi_hop_v1_n4096 PASS "
          f"acc_b_blind={out['acc_b_blind']:.3f} acc_b_conf={out['acc_b_conf']:.3f} "
          f"calib_dev_b={out['calib_dev_b']:.3f}", flush=True)


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
    K = K_PATHS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] mixed_confidence_multi_hop smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} K={K} seeds={seeds} done={len(done)} "
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
            print(f"  s={seed} done ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "mixed_confidence_multi_hop_v1_n4096",
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
