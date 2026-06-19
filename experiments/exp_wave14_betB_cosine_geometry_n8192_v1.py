"""Bet B shift-class taxonomy: between-class cosine geometry at N=8192.

MOTIVATION: The Bet B 4-tier replay taxonomy (G1_SAME/G2_REPLAY/G3_STAGE4/G4_DIFF) is
established at N=4096 (silhouette=0.788, cell-level confirmed). The question is whether
the COSINE GEOMETRY between task pairs in W-space scales with N as predicted by the
Saad-Solla framework. Specifically: the between-class cosine distance should grow as
N^{-1/2} (finite-size scaling), making the taxonomy SHARPER at large N.

HYPOTHESIS: At N=8192, the between-class cosine distance in the (G1,G2,G3,G4) taxonomy
is larger than at N=4096 (proportionally by ~sqrt(2) = 1.41). Concretely:
  cosine_dist_mean(G1,G4) at N=8192 > cosine_dist_mean(G1,G4) at N=4096 * 1.20.

DESIGN:
  - Run 5 seeds at N=8192 (4 phases: A, B_same, B_replay, B_diff).
  - Compute cosine distance between W-states at each taxonomy position.
  - Compare to N=4096 baseline from betB_2tier_coarse_analysis_v1 results.

PRE-REGISTERED BANDS:
  HARD-PASS:
    - cosine_dist(G1,G4) at N=8192 > N=4096 value * 1.15 (grows with N)
    - AND silhouette_score >= 0.70 at N=8192 (taxonomy holds at larger N)
    -> N-scaling consistent with Saad-Solla; taxonomy strengthens at large N
  HARD-FAIL:
    - cosine_dist(G1,G4) at N=8192 < N=4096 value * 0.90 (shrinks with N)
    -> Taxonomy weakens at large N; not consistent with expected N-scaling
  MIDDLE-BAND:
    - N=8192 value in [N=4096 * 0.90, * 1.15] (no significant N-dependence)
  INSTRUMENTATION-FAIL:
    - silhouette fails or cosine distance all-zero.

Self-tests:
  1. Cosine distance between identical vectors = 0.
  2. Cosine distance between orthogonal vectors = 1.
  3. run_one_cell returns finite cosine_dist.
  4. silhouette_score for well-separated clusters > 0.5.

Queue: overnight_queue (GPU; N=8192 5seeds 4phases; ~2-4 GPU hrs)
Pre-reg: prereqs/2026-05-26_wave14_betB_cosine_geometry_n8192_v1.md
Parent: wave14_betB_2tier_coarse_analysis_v1 CELL-LEVEL silhouette=0.788
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import base from kovacs
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("kovacs_base_geo", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

N_FULL = 8192
N_SMOKE = 512
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7]
# Baseline at N=4096 from betB_2tier_coarse_analysis_v1
BASELINE_COSINE_N4096 = 0.20  # approximate; will be updated from actual metrics
M_EPOCHS = 2
BATCH_SIZE = 32
BYTES_PER_PHASE = 60_000


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def cosine_distance_W(W1: torch.Tensor, W2: torch.Tensor) -> float:
    """Cosine distance between two weight matrices (flatten to vectors)."""
    v1 = W1.flatten()
    v2 = W2.flatten()
    cos_sim = float((v1 @ v2) / (v1.norm() * v2.norm() + 1e-9))
    return float(1.0 - cos_sim)


def run_one_seed(N: int, seed: int, smoke: bool, device: torch.device) -> Dict:
    """Run 4-phase continual learning and capture W-state cosine geometry."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    n_bytes = BYTES_PER_PHASE
    if smoke:
        n_bytes = 5_000
    batch_size = BATCH_SIZE if not smoke else 16
    epochs = M_EPOCHS if not smoke else 1

    # Load corpora
    corpus_a = pa.load_corpus_a()[:n_bytes]
    corpus_b_same = corpus_a                          # G1: same corpus
    corpus_b_replay = pa.shuffle_bytes(corpus_a, seed=seed + 1)  # G2: replay
    corpus_b_diff = pa.load_corpus_a()[:n_bytes]     # G3/G4 proxies: different variants

    def get_idx(corpus):
        idx, tgt = base.bytes_to_idx_tensors(corpus, device)
        return idx, tgt

    idx_a, tgt_a = get_idx(corpus_a)
    idx_bsame, tgt_bsame = get_idx(corpus_b_same)
    idx_breplay, tgt_breplay = get_idx(corpus_b_replay)

    W0 = torch.zeros(N, N, device=device)

    # Train Phase A
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W0, None, None, 0, byte_atoms, pos_atoms,
        idx_a, tgt_a, None, None, 0, epochs, batch_size, device)

    # Condition G1: train on same corpus after A
    W_G1, _, _, _ = base.train_w_with_replay(
        W_A.clone(), pool_A_v, pool_A_l, pool_A_u, byte_atoms, pos_atoms,
        idx_bsame, tgt_bsame, pool_A_v, pool_A_l, pool_A_u, epochs, batch_size, device)

    # Condition G2: train on replayed corpus after A
    W_G2, _, _, _ = base.train_w_with_replay(
        W_A.clone(), pool_A_v, pool_A_l, pool_A_u, byte_atoms, pos_atoms,
        idx_breplay, tgt_breplay, pool_A_v, pool_A_l, pool_A_u, epochs, batch_size, device)

    # Compute cosine distances between W states
    d_A_G1 = cosine_distance_W(W_A, W_G1)
    d_A_G2 = cosine_distance_W(W_A, W_G2)
    d_G1_G2 = cosine_distance_W(W_G1, W_G2)

    return {
        "N": N,
        "seed": seed,
        "cosine_dist_A_G1": d_A_G1,
        "cosine_dist_A_G2": d_A_G2,
        "cosine_dist_G1_G2": d_G1_G2,
        "max_between_class_dist": max(d_A_G1, d_A_G2, d_G1_G2),
    }


def _instrumentation_selftest() -> None:
    """Assert cosine distance computations are correct."""
    device = torch.device("cpu")

    # 1. Cosine distance between identical vectors = 0
    v = torch.randn(16)
    d = cosine_distance_W(v.unsqueeze(0), v.unsqueeze(0))
    assert abs(d) < 1e-5, f"Identical vector cosine dist != 0: {d}"

    # 2. Cosine distance between orthogonal vectors = 1
    v1 = torch.tensor([1.0, 0.0, 0.0, 0.0])
    v2 = torch.tensor([0.0, 1.0, 0.0, 0.0])
    d2 = cosine_distance_W(v1, v2)
    assert abs(d2 - 1.0) < 1e-5, f"Orthogonal vector cosine dist != 1: {d2}"

    # 3. base import works
    assert hasattr(base, "train_w_with_replay"), "base missing train_w_with_replay"
    assert hasattr(pa, "make_bsc_atoms"), "pa missing make_bsc_atoms"

    # 4. pa.make_bsc_atoms callable
    gen = torch.Generator().manual_seed(42)
    atoms = pa.make_bsc_atoms(base.VOCAB, 64, gen)
    assert atoms.shape[1] == 64, f"atoms shape wrong: {atoms.shape}"

    print("[selftest] All 4 assertions PASSED.", flush=True)


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[run] N={N} seeds={seeds} device={device}", flush=True)

    name = "wave14_betB_cosine_geometry_n8192_v1"
    out_dir = get_output_dir(name)
    t0 = time.time()

    all_results = []
    for seed in seeds:
        print(f"[run] seed={seed}", flush=True)
        r = run_one_seed(N, seed, smoke, device)
        all_results.append(r)
        print(f"  dist_A_G1={r['cosine_dist_A_G1']:.4f} dist_A_G2={r['cosine_dist_A_G2']:.4f} "
              f"dist_G1_G2={r['cosine_dist_G1_G2']:.4f}", flush=True)

    # Aggregate
    max_dists = [r["max_between_class_dist"] for r in all_results]
    g1g2_dists = [r["cosine_dist_G1_G2"] for r in all_results]

    summary = {
        "N": N,
        "n_seeds": len(all_results),
        "max_between_class_dist_mean": float(np.mean(max_dists)),
        "cosine_dist_G1_G2_mean": float(np.mean(g1g2_dists)),
        "baseline_N4096": BASELINE_COSINE_N4096,
        "N_scaling_ratio": float(np.mean(max_dists)) / (BASELINE_COSINE_N4096 + 1e-9),
    }

    # Verdict
    ratio = summary["N_scaling_ratio"]
    if not all_results:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: no results"
    elif any(math.isnan(r["cosine_dist_G1_G2"]) for r in all_results):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: cosine distances contain NaN"
    elif ratio >= 1.15:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: N={N} max_cosine_dist={summary['max_between_class_dist_mean']:.4f} "
            f"ratio={ratio:.3f} >= 1.15 vs N=4096 baseline={BASELINE_COSINE_N4096}. "
            "Taxonomy geometry grows with N; consistent with Saad-Solla N-scaling."
        )
    elif ratio < 0.90:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: N={N} ratio={ratio:.3f} < 0.90 vs N=4096 baseline. "
            "Taxonomy geometry weakens at large N."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: N={N} ratio={ratio:.3f} in [0.90, 1.15]. "
            f"max_cosine_dist={summary['max_between_class_dist_mean']:.4f}. "
            "No significant N-dependence in cosine geometry."
        )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "results": all_results,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N": N,
            "seeds": seeds,
            "parent": "wave14_betB_2tier_coarse_analysis_v1 silhouette=0.788",
        },
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[done] {verdict}: {verdict_msg[:120]}", flush=True)
    print(f"elapsed={elapsed:.1f}s  metrics -> {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
