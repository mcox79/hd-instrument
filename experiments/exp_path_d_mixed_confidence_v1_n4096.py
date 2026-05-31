"""T1 PATH D MIXED CONFIDENCE v1 at N=4096 (Test 14).

Path D's Bayesian propagation naturally accommodates confidence. We extend
Path D with per-fact confidence weighting in likelihood queries and Bayesian
posterior aggregation. Calibrated reasoning is the distinguishing feature
for regulated industries.

FACT CORPUS (confidence-stratified):
  50% high (1.0), 30% medium (0.7), 20% low (0.4),
  PLUS 5% adversarial low-confidence noisy facts at confidence 0.2 layered on.

EXTENSION:
  Path D's likelihood query computes per-path Bayesian update weighted by
  per-fact confidence. The final posterior includes propagated confidence
  (mean of per-hop confidences for the top path).

METRICS:
  - per-confidence-bucket accuracy (4 buckets: 0.2, 0.4, 0.7, 1.0)
  - calibration: predicted_confidence vs actual_correct fraction per bucket
  - comparison: confidence-blind Path D baseline vs confidence-aware
  - latency overhead (conf vs blind)

PRE-REGISTERED BANDS:
  HP = calibration within +/-15% across 4 confidence buckets (0.2, 0.4, 0.7, 1.0)
       AND accuracy >= confidence-blind baseline in >=3/5 seeds
       AND latency overhead <= 20%.
  HF = calibration miss >40% OR accuracy <80% of confidence-blind baseline.
  MB = otherwise.

PROT-018: _n4096 binds N = 4096.
Anchor: path_d_mixed_confidence_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_d_mixed_confidence_v1_n4096.md
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
    build_shared,
)
from experiments._relation_graph import (  # noqa: E402
    sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_t1pdmc", _ck_path)
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

M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 500
K_PATHS_SMOKE = 50
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS_FULL = 64
N_PATHS_SMOKE = 16

# 4-bucket confidence corpus + adversarial layer
CONF_DIST_BASE = [(1.0, 0.50), (0.7, 0.30), (0.4, 0.20)]
ADVERSARIAL_FRAC = 0.05
ADVERSARIAL_CONF = 0.2
CONF_BUCKETS = [0.2, 0.4, 0.7, 1.0]

HP_CALIB_TOLERANCE = 0.15
HP_LAT_OVERHEAD = 0.20
HF_CALIB_MISS = 0.40
HF_ACC_FRAC = 0.80


def get_output_dir(default_name: str = "path_d_mixed_confidence_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def assign_confidences(M: int, seed: int, device: torch.device) -> torch.Tensor:
    """Assign per-fact confidence values per CONF_DIST_BASE + adversarial overlay."""
    g = torch.Generator(device=device).manual_seed(seed + 4444)
    perm = torch.randperm(M, generator=g, device=device)
    out = torch.zeros(M, dtype=torch.float32, device=device)
    start = 0
    for level, frac in CONF_DIST_BASE:
        n = int(M * frac)
        out[perm[start:start + n]] = level
        start += n
    out[out == 0] = CONF_DIST_BASE[-1][0]
    # Adversarial overlay: replace ADVERSARIAL_FRAC of facts with confidence ADVERSARIAL_CONF
    g2 = torch.Generator(device=device).manual_seed(seed + 5555)
    adv = torch.randperm(M, generator=g2, device=device)
    n_adv = int(M * ADVERSARIAL_FRAC)
    out[adv[:n_adv]] = ADVERSARIAL_CONF
    return out


def path_d_run_conf_aware(codebook: torch.Tensor, W: torch.Tensor,
                          starts: torch.Tensor,
                          relation: Dict[int, int], depth: int, K_paths: int,
                          seed: int, N_use: int,
                          key_idx: torch.Tensor,
                          confs: torch.Tensor,
                          beta: float = 4.0) -> Tuple[torch.Tensor, torch.Tensor]:
    """Path D with confidence-weighted likelihoods + predicted-confidence emission.

    Returns: (correct[B], predicted_conf[B]).
    """
    device = codebook.device
    C = codebook.shape[0]
    B = starts.shape[0]
    correct = torch.zeros(B, device=device, dtype=torch.float32)
    pred_conf = torch.zeros(B, device=device, dtype=torch.float32)

    # Build a quick lookup: source-key -> confidence. Use first matching fact.
    # Default conf for unknown sources = mean of confs (conservative).
    default_conf = float(confs.mean().item())

    def src_conf(src: int) -> float:
        matches = (key_idx == src).nonzero(as_tuple=True)[0]
        if matches.numel() == 0:
            return default_conf
        return float(confs[matches[0]].item())

    for b in range(B):
        start = int(starts[b].item())
        pos = [start]
        cur = start
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                break
            pos.append(int(nxt))
            cur = int(nxt)
        if len(pos) < depth + 1:
            continue
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=K_paths - 1,
            seed=seed + b + depth + start, relation=relation)
        if not decoys:
            continue
        candidates = [pos] + decoys

        K = len(candidates)
        src_list = []
        dst_list = []
        for p in candidates:
            for i in range(depth):
                src_list.append(p[i])
                dst_list.append(p[i + 1])
        src = torch.tensor(src_list, dtype=torch.long, device=device)
        dst = torch.tensor(dst_list, dtype=torch.long, device=device)
        src_v = codebook[src]
        dst_v = codebook[dst]
        out_v = src_v @ W.T
        sims = (out_v * dst_v).sum(dim=1) / N_use
        logits = beta * sims
        log_lik = -torch.nn.functional.softplus(-logits)
        log_lik = log_lik.view(K, depth)

        # Per-hop confidence weights: weight each hop log-likelihood by source-fact confidence
        per_path_confs = torch.zeros(K, depth, device=device, dtype=torch.float32)
        for k, p in enumerate(candidates):
            for i in range(depth):
                per_path_confs[k, i] = src_conf(p[i])

        # Confidence-weighted log-likelihood + log-prior contribution
        # weighted_log_lik = confidence * log_lik. Low-confidence facts contribute less evidence.
        weighted_log_lik = per_path_confs * log_lik
        log_post = weighted_log_lik.sum(dim=1)

        top = int(torch.argmax(log_post).item())
        if top == 0:
            correct[b] = 1.0
        # Predicted confidence = mean per-hop confidence of the chosen path
        pred_conf[b] = float(per_path_confs[top].mean().item())

    return correct, pred_conf


def path_d_run_blind(codebook: torch.Tensor, W: torch.Tensor,
                     starts: torch.Tensor,
                     relation: Dict[int, int], depth: int, K_paths: int,
                     seed: int, N_use: int,
                     beta: float = 4.0) -> torch.Tensor:
    """Confidence-blind Path D baseline (no per-hop conf weighting)."""
    device = codebook.device
    C = codebook.shape[0]
    B = starts.shape[0]
    correct = torch.zeros(B, device=device, dtype=torch.float32)

    for b in range(B):
        start = int(starts[b].item())
        pos = [start]
        cur = start
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None:
                break
            pos.append(int(nxt))
            cur = int(nxt)
        if len(pos) < depth + 1:
            continue
        decoys = sample_incoherent_paths(
            C, depth=depth, n_paths=K_paths - 1,
            seed=seed + b + depth + start, relation=relation)
        if not decoys:
            continue
        candidates = [pos] + decoys

        K = len(candidates)
        src_list = []
        dst_list = []
        for p in candidates:
            for i in range(depth):
                src_list.append(p[i])
                dst_list.append(p[i + 1])
        src = torch.tensor(src_list, dtype=torch.long, device=device)
        dst = torch.tensor(dst_list, dtype=torch.long, device=device)
        src_v = codebook[src]
        dst_v = codebook[dst]
        out_v = src_v @ W.T
        sims = (out_v * dst_v).sum(dim=1) / N_use
        logits = beta * sims
        log_lik = -torch.nn.functional.softplus(-logits)
        log_lik = log_lik.view(K, depth)
        log_post = log_lik.sum(dim=1)
        top = int(torch.argmax(log_post).item())
        if top == 0:
            correct[b] = 1.0
    return correct


def measure_seed(N_use: int, M: int, depth: int, K: int, n_paths: int,
                 seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    confs = assign_confidences(M, seed, device)

    starts = torch.tensor(list(relation.keys())[:n_paths],
                          dtype=torch.long, device=device)

    # Blind baseline
    t0 = time.perf_counter_ns()
    correct_blind = path_d_run_blind(codebook, W, starts, relation, depth, K,
                                     seed, N_use)
    lat_blind = time.perf_counter_ns() - t0
    acc_blind = float(correct_blind.mean().item())

    # Confidence-aware
    t1 = time.perf_counter_ns()
    correct_conf, pred_conf = path_d_run_conf_aware(
        codebook, W, starts, relation, depth, K, seed, N_use,
        key_idx, confs)
    lat_conf = time.perf_counter_ns() - t1
    acc_conf = float(correct_conf.mean().item())

    lat_overhead = (lat_conf - lat_blind) / max(1, lat_blind)

    # Bucket the predicted confidences against the 4 fixed CONF_BUCKETS.
    # For each bucket, compute (predicted_conf_mean, actual_correct_frac).
    bucket_eps = 0.075
    calib = {}
    bucket_devs = []
    for cb in CONF_BUCKETS:
        mask = (pred_conf >= cb - bucket_eps) & (pred_conf <= cb + bucket_eps)
        if mask.sum() > 0:
            predicted = float(pred_conf[mask].mean().item())
            actual = float(correct_conf[mask].mean().item())
            calib[str(cb)] = {"predicted": round(predicted, 4),
                              "actual": round(actual, 4),
                              "n": int(mask.sum().item())}
            bucket_devs.append(abs(predicted - actual))
        else:
            calib[str(cb)] = {"predicted": None, "actual": None, "n": 0}

    mean_calib_dev = sum(bucket_devs) / max(1, len(bucket_devs))
    n_buckets_observed = sum(1 for v in calib.values() if v["n"] > 0)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"seed": int(seed), "M": int(M), "depth": int(depth),
            "K_paths": int(K), "n_paths": int(n_paths),
            "acc_blind": round(acc_blind, 5),
            "acc_conf": round(acc_conf, 5),
            "lat_blind_ns": int(lat_blind),
            "lat_conf_ns": int(lat_conf),
            "lat_overhead": round(lat_overhead, 4),
            "calib_per_bucket": calib,
            "mean_calib_dev": round(mean_calib_dev, 5),
            "n_buckets_observed": int(n_buckets_observed)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("T1_INCONCLUSIVE", "no cells")

    n_seeds = len(cells)
    n_calib_pass = sum(1 for c in cells if c["mean_calib_dev"] <= HP_CALIB_TOLERANCE)
    n_acc_ge_blind = sum(1 for c in cells if c["acc_conf"] >= c["acc_blind"])
    n_lat_ok = sum(1 for c in cells if c["lat_overhead"] <= HP_LAT_OVERHEAD)
    n_acc_below_frac = sum(1 for c in cells
                            if c["acc_blind"] > 0 and
                            c["acc_conf"] < HF_ACC_FRAC * c["acc_blind"])
    n_calib_miss = sum(1 for c in cells if c["mean_calib_dev"] > HF_CALIB_MISS)

    threshold = max(1, (n_seeds * 3) // 5)
    detail = (f"n_seeds={n_seeds} calib_pass={n_calib_pass} "
              f"acc_ge_blind={n_acc_ge_blind} lat_ok={n_lat_ok} "
              f"calib_miss={n_calib_miss} acc_below_frac={n_acc_below_frac}")

    hp = (n_calib_pass >= threshold and
          n_acc_ge_blind >= threshold and
          n_lat_ok >= threshold)
    if hp:
        return ("T1_HARD_PASS", "PATH_D_CALIBRATED: " + detail)
    if n_calib_miss >= threshold or n_acc_below_frac >= threshold:
        return ("T1_HARD_FAIL", "CALIB_OR_ACC_FAIL: " + detail)
    return ("T1_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 20, 8, 17, device)
    assert "mean_calib_dev" in out
    assert out["acc_blind"] is not None and not (out["acc_blind"] != out["acc_blind"])
    assert out["acc_conf"] is not None and not (out["acc_conf"] != out["acc_conf"])
    assert out["n_buckets_observed"] >= 1, \
        f"calibration filter eliminated all buckets at smoke scale ({out})"
    print(f"[selftest] path_d_mixed_confidence_v1_n4096 PASS "
          f"acc_blind={out['acc_blind']:.3f} acc_conf={out['acc_conf']:.3f} "
          f"calib_dev={out['mean_calib_dev']:.3f} "
          f"n_buckets={out['n_buckets_observed']}", flush=True)


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
    n_paths = N_PATHS_SMOKE if smoke else N_PATHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_d_mixed_confidence smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} K={K} n_paths={n_paths} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
        try:
            out = measure_seed(N_cfg, M, depth, K, n_paths, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} acc_blind={out['acc_blind']:.3f} "
                  f"acc_conf={out['acc_conf']:.3f} "
                  f"calib_dev={out['mean_calib_dev']:.3f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_d_mixed_confidence_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "K_paths": K, "n_paths": n_paths,
               "seeds": seeds, "cells": cells,
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
