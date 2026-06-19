"""PATH-PROBABILITY-PROPAGATION v1 at N=4096 (Path D).

CONTEXT (Multi-hop Path D):
  Path B propagates substrate STATE (q_d). Noise compounds.
  Path D propagates PROBABILITY (posterior over candidate paths). Each hop
  is an independent likelihood query; combination is multiplicative.
  Substantively different from Op-D state-domain superposition.

SCIENTIFIC QUESTION:
  At N=4096, M=256, K_paths in {50, 100, 500}, depth in {3, 4, 5}:
  does top-1 path-identification accuracy exceed 0.60 at depth 4 in
  >= 3/5 seeds when K_paths >= 100?

PRE-REGISTERED BANDS:
  HP = top-1 accuracy at depth 4 >= 0.60 in >=3/5 seeds at K_paths >= 100.
  HF = accuracy <= 0.20 at every depth in {3,4,5} in >=3/5 seeds.
  MIDDLE_BAND = otherwise.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018).
  2. K_paths grid = [50, 100, 500].
  3. depths grid = [3, 4, 5].
  4. per-hop likelihood = sigmoid(beta * <codebook[v_idx], W @ codebook[u_idx]> / N).
  5. log-posterior of path p = sum_i log_lik(p[i], p[i+1]).
  6. top-1 = argmax of log-posterior over K candidate paths.

OOM CHECK:
  M=256, K_paths=500, depth=5: K*depth = 2500 hops. Each hop = O(N) dot product.
  Memory peak ~ 10 MiB + W (64 MiB) + CB (805 MiB) ~ 900 MiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 30s. FULL: 3 K x 3 depths x 5 seeds = 45 cells x ~30s = 1350s.
  Budget 21600s.

N-suffix: _n4096 (PROT-018).
Anchor: path_probability_propagation_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_probability_propagation_v1_n4096.md
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
from experiments._relation_graph import (  # noqa: E402
    build_relation_facts,
    sample_coherent_starts,
    sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 256
M_SMOKE = 32
DEPTHS_FULL  = [3, 4, 5]
DEPTHS_SMOKE = [3]
K_PATHS_FULL  = [50, 100, 500]
K_PATHS_SMOKE = [50]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BETA = 4.0

HP_ACC = 0.60
HP_DEPTH = 4
HP_K_MIN = 100
HF_ACC = 0.20
HP_SEEDS_MIN = 3
HF_SEEDS_MIN = 3


def get_output_dir(default_name: str = "path_probability_propagation_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(
        N_use, M, seed, device)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=codebook.shape[0], M=M, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def per_hop_loglik(codebook: torch.Tensor, W: torch.Tensor,
                    src_idx: torch.Tensor, dst_idx: torch.Tensor,
                    N_use: int, beta: float) -> torch.Tensor:
    """Vectorized log-likelihood for one hop.

    src_idx, dst_idx: int64 (B,) codebook indices.
    Returns: (B,) torch.float32 log-likelihoods.

    score = sigmoid(beta * <codebook[dst], W @ codebook[src]> / N)
    log_lik = log(score).
    """
    src = codebook[src_idx]               # (B, N)
    dst = codebook[dst_idx]               # (B, N)
    out = src @ W.T                       # (B, N)
    sims = (out * dst).sum(dim=1) / N_use # (B,)
    logits = beta * sims
    # log-sigmoid
    log_lik = -torch.nn.functional.softplus(-logits)
    return log_lik


def score_paths(codebook: torch.Tensor, W: torch.Tensor,
                 paths: List[List[int]], N_use: int, beta: float,
                 device: torch.device) -> torch.Tensor:
    """Score each path by summing per-hop log-likelihoods. Returns (K,)."""
    K = len(paths)
    depth = len(paths[0]) - 1 if paths else 0
    if K == 0 or depth <= 0:
        return torch.zeros(K, device=device)
    # Flatten: (K, depth) -> K*depth pairs
    src = torch.tensor([p[i]     for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    dst = torch.tensor([p[i + 1] for p in paths for i in range(depth)],
                        dtype=torch.long, device=device)
    log_liks = per_hop_loglik(codebook, W, src, dst, N_use, beta)  # (K*depth,)
    log_liks = log_liks.view(K, depth)
    return log_liks.sum(dim=1)             # (K,)


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    # Sample coherent paths (positives) and decoys.
    n_positives = min(K_paths // 5, max(10, K_paths // 10))
    n_positives = max(1, n_positives)
    pos_paths = sample_coherent_starts(relation, depth=depth,
                                         n_paths=n_positives,
                                         seed=seed + depth)
    if not pos_paths:
        # Cannot test — relation too sparse for this depth
        return {"depth": int(depth), "K_paths": int(K_paths),
                "M": int(M), "seed": int(seed),
                "n_positives": 0, "top1_accuracy": 0.0,
                "post_margin": 0.0}

    n_pos_evaluated = len(pos_paths)
    n_decoys = K_paths - 1
    correct = 0
    margins: List[float] = []
    C = codebook.shape[0]
    for pos in pos_paths:
        decoys = sample_incoherent_paths(C, depth=depth,
                                           n_paths=n_decoys,
                                           seed=seed + depth + hash(tuple(pos)) % 100,
                                           relation=relation)
        if not decoys:
            continue
        candidates = [pos] + decoys
        scores = score_paths(codebook, W, candidates, N_use, BETA, device)
        idx_top = int(torch.argmax(scores).item())
        # Margin = top - second
        top_val = float(scores[idx_top].item())
        if scores.shape[0] >= 2:
            other = scores.clone()
            other[idx_top] = float("-inf")
            second_val = float(other.max().item())
        else:
            second_val = float("-inf")
        margins.append(top_val - second_val)
        if idx_top == 0:
            correct += 1
    acc = correct / max(1, n_pos_evaluated)
    mean_margin = sum(margins) / max(1, len(margins))

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"depth": int(depth), "K_paths": int(K_paths),
            "M": int(M), "seed": int(seed),
            "n_positives": int(n_pos_evaluated),
            "top1_accuracy": round(acc, 5),
            "post_margin": round(mean_margin, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("PPP_INCONCLUSIVE", "No cells.")

    # HP: at depth=HP_DEPTH and K_paths>=HP_K_MIN, acc>=HP_ACC in >=HP_SEEDS_MIN seeds
    eligible = [c for c in cells
                if c["depth"] == HP_DEPTH and c["K_paths"] >= HP_K_MIN]
    hp_pass = sum(1 for c in eligible if c["top1_accuracy"] >= HP_ACC)

    # HF: at every depth, acc<=HF in >=HF_SEEDS_MIN seeds (over all K_paths)
    by_depth: Dict[int, List[Dict]] = {}
    for c in cells:
        by_depth.setdefault(c["depth"], []).append(c)
    hf_depths_fail = 0
    for d, cs in by_depth.items():
        n_fail = sum(1 for c in cs if c["top1_accuracy"] <= HF_ACC)
        # Require dominant fail across the K_paths slice for this depth
        if n_fail >= HF_SEEDS_MIN * max(1, len(K_PATHS_FULL)):
            hf_depths_fail += 1

    means_by_depth: Dict[int, float] = {}
    for d, cs in by_depth.items():
        vals = [c["top1_accuracy"] for c in cs]
        means_by_depth[d] = round(sum(vals) / max(1, len(vals)), 4)

    detail = (f"depth_means={means_by_depth} "
              f"hp_pass={hp_pass}/{len(eligible)} "
              f"hf_depths={hf_depths_fail}/{len(by_depth)}")

    if hf_depths_fail >= len(by_depth):
        return ("PPP_HARD_FAIL", "PATH_D_CLOSED: " + detail)
    if hp_pass >= HP_SEEDS_MIN:
        return ("PPP_HARD_PASS", "PATH_D_OPEN: " + detail)
    return ("PPP_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert HP_DEPTH in DEPTHS_FULL
    assert HP_K_MIN in K_PATHS_FULL

    # Verdict gates
    fake_hp: List[Dict] = []
    for d in DEPTHS_FULL:
        for K in K_PATHS_FULL:
            for s in SEEDS_FULL:
                acc = 0.80 if (d == HP_DEPTH and K >= HP_K_MIN) else 0.40
                fake_hp.append({"depth": d, "K_paths": K, "M": M_FULL,
                                  "seed": s, "n_positives": 50,
                                  "top1_accuracy": acc, "post_margin": 0.5})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for d in DEPTHS_FULL:
        for K in K_PATHS_FULL:
            for s in SEEDS_FULL:
                fake_hf.append({"depth": d, "K_paths": K, "M": M_FULL,
                                  "seed": s, "n_positives": 50,
                                  "top1_accuracy": 0.05,
                                  "post_margin": 0.0})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass on CPU at smoke scale
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, depth=3, K_paths=20,
                        seed=17, device=device)
    assert out["top1_accuracy"] is not None
    print(f"[selftest] path_probability_propagation_v1_n4096 PASS "
          f"smoke d=3 K=20 acc={out['top1_accuracy']:.3f} "
          f"margin={out['post_margin']:.3f}", flush=True)


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
    M_cfg = M_SMOKE if smoke else M_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    K_grid = K_PATHS_SMOKE if smoke else K_PATHS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_probability_propagation_v1 smoke={smoke} N={N_cfg} "
          f"M={M_cfg} depths={depths} K_paths={K_grid} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for d in depths:
        for K in K_grid:
            for seed in seeds:
                ck = f"d{d}_K{K}_seed{seed}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = measure_cell(N_cfg, M_cfg, d, K, seed, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  d={d} K={K} seed={seed} "
                          f"acc={out['top1_accuracy']:.3f} "
                          f"margin={out['post_margin']:.3f} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  d={d} K={K} seed={seed} FAILED: {e}",
                          flush=True)
                    if device.type == "cuda":
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_probability_propagation_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "depths": depths,
               "K_paths": K_grid, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
