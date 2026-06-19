"""Shared SPREAD-ATTENTION test harness for the nonlinear-readout frontier (Director-queued 2026-06-17).

WHY: 3 cells today (ARCH-B, 8b, C1) hit the SELF-DOMINANCE wall -- i.i.d.-random bipolar keys + raw-dot -> exactly ONE
stored pattern matches -> softmax (any readout) collapses to near-ONE-HOT -> readout-FAMILY differences (softmax vs
entmax vs sparsity vs linear) are INDISTINGUISHABLE (DEGENERATE corner). To DISCRIMINATE readout families we need a
regime where attention genuinely SPREADS over multiple candidates. This module provides that, reusably + with a built-in
discriminating-regime guard (verify_spread), so C1 + refuse-gate + future Cx test in a NON-degenerate regime.

MECHANISM: CLUSTERED / CORRELATED keys. n_clusters centroids; each key = a centroid with a fraction of bits flipped
(near-duplicate). A query (a cluster member) is then similar to ALL ~cluster_size members of its cluster -> softmax
SPREADS attention over the cluster (nonzero-count ~ cluster_size > 1) -> entmax (sparse) keeps the top-few = the regime
where readout-family genuinely differs (recall AND compute). cluster_size = the tunable SPREAD parameter (1 = i.i.d.
degenerate; larger = more spread). Each key keeps its OWN value -> recall must return the query's own value (so a
near-collision cluster genuinely stresses the readout, not a trivial lookup).

Skunkworks SCHEMA-VETs this separately as harness-discipline. Deterministic (seeded). ASCII-only.
"""
from __future__ import annotations
import numpy as np


def make_clustered_keys(M: int, n: int, cluster_size: int, g: np.random.Generator, flip_frac: float = 0.12):
    """(M,n) bipolar keys in M/cluster_size clusters of near-duplicates (centroid + flip_frac bits flipped).
    cluster_size=1 -> i.i.d.-random (degenerate). Returns (keys, cluster_id per key). Larger cluster_size = MORE spread."""
    cluster_size = max(1, cluster_size)
    n_clusters = max(1, M // cluster_size)
    centroids = (g.integers(0, 2, size=(n_clusters, n)).astype(np.float32) * 2 - 1)
    keys = np.empty((M, n), dtype=np.float32)
    cid = np.empty(M, dtype=np.int64)
    k_flip = max(0, int(flip_frac * n))
    for i in range(M):
        c = i % n_clusters
        cid[i] = c
        key = centroids[c].copy()
        if k_flip > 0:
            idx = g.choice(n, size=k_flip, replace=False)
            key[idx] *= -1.0                      # flip -> near-duplicate of the centroid (cluster member)
        keys[i] = key
    return keys, cid


def cosine_scores(Q: np.ndarray, K: np.ndarray) -> np.ndarray:
    """(Qn,Kn) cosine similarities in [-1,1]. CRITICAL for spread: raw-dot scores are O(N) scale -> softmax(beta*dot)
    one-hots for ANY beta (exp domination of any O(N) gap) regardless of clustering -- THIS is the self-dominance wall
    ARCH-B/C1 hit. Cosine puts scores in O(1) range so a tuned beta gives genuine SPREAD over near-neighbors."""
    Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12)
    Kn = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-12)
    return Qn @ Kn.T


def make_noisy_queries(keys: np.ndarray, noise_frac: float, g: np.random.Generator) -> np.ndarray:
    """Queries = keys with noise_frac bits flipped (partial/noisy cue). Degrades exact self-match so cluster-mates
    genuinely compete -> spread. noise_frac=0 -> exact self (no spread even clustered)."""
    Q = keys.copy()
    if noise_frac > 0:
        n = keys.shape[1]; kf = max(1, int(noise_frac * n))
        for i in range(keys.shape[0]):
            idx = g.choice(n, size=kf, replace=False)
            Q[i, idx] *= -1.0
    return Q


def verify_spread(weights: np.ndarray, min_nonzero: float = 2.0) -> dict:
    """Discriminating-regime guard: does the readout genuinely SPREAD (nonzero-count > min_nonzero)?
    weights: (Q,M) row-stochastic readout weights. Returns {mean_nonzero, spreads}."""
    nz = (weights > 1e-9).sum(axis=1).mean()
    return {"mean_nonzero_count": float(nz), "spreads": bool(nz > min_nonzero)}


def _selftest():
    g = np.random.default_rng(0)
    N = 256

    def softmax(Z):
        Z = Z - Z.max(1, keepdims=True); E = np.exp(Z); return E / E.sum(1, keepdims=True)

    # 1) RAW-DOT one-hots regardless of clustering (the self-dominance wall):
    keys8, _ = make_clustered_keys(128, N, 8, g)
    raw = verify_spread(softmax(1.0 * (keys8 @ keys8.T)))
    print(f"[selftest] RAW-DOT (cluster_size=8, exact query): mean_nonzero={raw['mean_nonzero_count']:.2f} "
          f"spreads={raw['spreads']}  <- expect ~1 (one-hot; the wall)")

    # 2) COSINE + clustered + NOISY cue + tuned beta -> genuine SPREAD (the discriminating regime):
    Q8 = make_noisy_queries(keys8, 0.15, g)
    S = cosine_scores(Q8, keys8)
    print("[selftest] COSINE + cluster_size=8 + noisy-cue(0.15), beta sweep:")
    for beta in (5, 10, 20, 40, 80):
        s = verify_spread(softmax(beta * S))
        print(f"    beta={beta:3d}: mean_nonzero={s['mean_nonzero_count']:.2f} spreads={s['spreads']}")
    print("[selftest] expect a moderate beta -> genuine SPREAD (nonzero >> 1, ~ cluster size) = discriminating regime.")


if __name__ == "__main__":
    _selftest()
