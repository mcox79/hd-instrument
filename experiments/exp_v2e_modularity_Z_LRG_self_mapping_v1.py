"""v2e_modularity_Z_LRG_self_mapping_v1 -- Gap-2 V3-gate via intrinsic multi-scale clustering.

REVIVAL series gate after v2c HARD_FAIL + v2d HARD_FAIL on substrate-native self-mapping.
The 5x-deeper drill in notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md
concluded the discriminator family (external lexical ground-truth like v1 families) is
structurally degenerate at production scope (2/20 anchors in v1 -> ARI upper-bounded by ~0.1).

This cell abandons external ground truth and instead uses INTRINSIC multi-scale measures:

  1. Modularity-Z score vs degree-preserving null (Reichardt-Bornholdt Potts ground state).
     At gamma in {0.5, 1.0, 2.0, 4.0}, compute Q_real - Q_null normalized by std(Q_null) over
     50 degree-preserving rewires of the adjacency. Real substrate structure -> Z >> 0
     at the best gamma; degree-preserved random rewire -> Z ~ 0 at every gamma.

  2. Laplacian Renormalization Group stability across diffusion timescales tau (Villegas
     et al. 2023 2406.02337). For tau in {0.1, 1.0, 10.0}, smooth the adjacency by
     heat-kernel-thresholded normalized Laplacian, re-cluster, measure ARI between
     partitions at adjacent tau values. Scale-invariant structure -> stable across tau.

  3. Sparse-ensemble allocation (Tonegawa engram-cell analog). 20 iterations of softmax
     reallocation with cluster-size decay; substrate-native iterative_attractor primitive
     composed with the Louvain partition. Diagnostic only in this cell.

The 2 arms (REAL substrate adjacency vs SHUF degree-preserved rewire) re-use most of v2c's
adjacency-build pipeline (char_trigram + KGStore + 2-hop Jaccard); the new primitives
operate on the adjacency matrix, not on the substrate KG end-to-end.

PRE-REG HARD bands (per Director task spec 2026-06-23; SIMPLER than full v2e drill):
  HARD_PASS: mod_Z(REAL) >= 3.0 at any gamma AND LRG_stability >= 0.5 across at least
             2 tau values AND mod_Z(REAL) / mod_Z(SHUF) >= 2.0.
  MIDDLE_BAND: mod_Z(REAL) in 1.5-3.0 (partial signal characterization).
  HARD_FAIL: mod_Z(REAL) < 1.5 at every gamma OR mod_Z(REAL) / mod_Z(SHUF) < 1.1.

Sanity self-test (--self-test): on a planted 2-block partition (50 atoms, strong-intra /
weak-inter edges), mod_Z(REAL) >> mod_Z(SHUF). Endpoint check; sys.exit(0) on pass.

ASCII-only. Per-seed checkpoint. Substrate-only-decode (zero LLM forward calls).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

# v2c primitives parse argv at import; strip our own argv to avoid sys.exit(0).
_saved_argv = sys.argv[:]
sys.argv = [sys.argv[0]]
from experiments.exp_substrate_self_map_v2c_full_store_v1 import (
    load_chain_grade_atom_ids, load_atomized_atom_ids, load_relations_for,
    encode_atoms_substrate, build_kg, two_hop_neighborhood, jaccard,
    atom_id_short, atom_retrieval_recall, sample_relation_pairs,
)
sys.argv = _saved_argv

_LLM_CALL_COUNTER = [0]

ANCHOR_NAME = "v2e_modularity_Z_LRG_self_mapping_v1"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

# ----- pre-registered HARD thresholds -----
MOD_Z_PASS = 3.0
MOD_Z_RATIO_PASS = 2.0
MOD_Z_FAIL = 1.5
MOD_Z_RATIO_FAIL = 1.1
LRG_STABILITY_PASS = 0.5    # ARI between adjacent-tau partitions
LRG_N_TAU_REQUIRED = 2      # at least 2 tau pairs above threshold
RECALL_PASS = 0.95
RECALL_FAIL = 0.50

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# Config
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 4096                  # per Director spec; matches v2c production
    MAX_INGEST_TRIPLES = 5000
    N_ANCHORS = 30                # chain-grade-only; full would be 150
    N_RELATION_SAMPLES = 10
    K_SET = 12
    N_NULL_REWIRES = 50
    JACCARD_TAU = 0.05            # threshold for binary adjacency; lower at small scope
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    MAX_INGEST_TRIPLES = None
    N_ANCHORS = 150
    N_RELATION_SAMPLES = 20
    K_SET = 16
    N_NULL_REWIRES = 100
    JACCARD_TAU = 0.10

GAMMA_SWEEP = [0.5, 1.0, 2.0, 4.0]
TAU_SWEEP = [0.1, 1.0, 10.0]
ALLOC_ITERS = 20
ALLOC_TEMP = 0.5
ALLOC_DECAY = 0.05

CONFIG_VERSION = (
    "v2e-modularity-Z-LRG: char_trigram + KGStore + 2hop-Jaccard adjacency + "
    "modularity-Z (Louvain @ gamma sweep) vs degree-preserving null + Laplacian-RG "
    "tau-sweep stability + sparse-ensemble allocation (Tonegawa analog); N%d "
    "n_anchors=%d n_rel_samples=%d kset=%d n_null=%d jac_tau=%.2f gammas=%s taus=%s "
    "bands mod_Z>=%.1f ratio>=%.1f lrg_stab>=%.2f recall>=%.2f"
) % (N_DIM, N_ANCHORS, N_RELATION_SAMPLES, K_SET, N_NULL_REWIRES, JACCARD_TAU,
     GAMMA_SWEEP, TAU_SWEEP, MOD_Z_PASS, MOD_Z_RATIO_PASS, LRG_STABILITY_PASS,
     RECALL_PASS)


# ===== adjacency build (weighted) =====

def build_jaccard_adjacency(anchors: list[int], neighborhoods: dict[int, set[int]]
                            ) -> np.ndarray:
    """Build n_anchors x n_anchors weighted adjacency from pairwise Jaccard of neighborhoods."""
    n = len(anchors)
    A = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        ni = neighborhoods.get(anchors[i], set())
        for j in range(i + 1, n):
            nj = neighborhoods.get(anchors[j], set())
            w = jaccard(ni, nj)
            A[i, j] = w
            A[j, i] = w
    return A


def threshold_adjacency(A: np.ndarray, tau: float) -> np.ndarray:
    """Zero entries below tau; keep weights elsewhere (no diagonal)."""
    B = A.copy()
    B[B < tau] = 0.0
    np.fill_diagonal(B, 0.0)
    return B


# ===== modularity + Louvain =====

def louvain_partition(A: np.ndarray, gamma: float, seed: int) -> np.ndarray:
    """Louvain community detection on weighted adjacency with resolution gamma.
    Returns labels[n]; isolated nodes get unique singleton labels.
    """
    import networkx as nx
    n = A.shape[0]
    G = nx.from_numpy_array(A)
    if G.number_of_edges() == 0:
        return np.arange(n, dtype=np.int64)
    # networkx 3.x Louvain
    comms = nx.community.louvain_communities(G, weight="weight", resolution=gamma,
                                              seed=int(seed))
    labels = np.zeros(n, dtype=np.int64)
    for ci, comm in enumerate(comms):
        for node in comm:
            labels[int(node)] = ci
    return labels


def modularity_Q(A: np.ndarray, labels: np.ndarray, gamma: float) -> float:
    """Newman modularity Q with resolution gamma. A symmetric weighted.
    Q = (1/2m) sum_ij [A_ij - gamma * k_i * k_j / 2m] * delta(c_i, c_j)
    """
    m = A.sum() / 2.0
    if m <= 0:
        return 0.0
    k = A.sum(axis=1)
    Q = 0.0
    n = A.shape[0]
    for i in range(n):
        for j in range(n):
            if labels[i] != labels[j]:
                continue
            Q += A[i, j] - gamma * k[i] * k[j] / (2.0 * m)
    return float(Q / (2.0 * m))


def degree_preserving_rewire(A: np.ndarray, rng: np.random.Generator,
                              n_swaps_per_edge: int = 10) -> np.ndarray:
    """Configuration-null adjacency: degree-preserving edge rewire (double-edge-swap).
    For weighted graph, treat (i,j) edges with weight > 0 as units; swap endpoints.
    """
    import networkx as nx
    G = nx.from_numpy_array(A)
    if G.number_of_edges() < 2:
        return A.copy()
    n_swaps = max(10, n_swaps_per_edge * G.number_of_edges())
    try:
        H = nx.algorithms.swap.double_edge_swap(G.copy(), nswap=n_swaps,
                                                  max_tries=n_swaps * 10,
                                                  seed=int(rng.integers(0, 2**31 - 1)))
    except (nx.NetworkXAlgorithmError, nx.NetworkXError):
        return A.copy()
    return nx.to_numpy_array(H, weight="weight", dtype=np.float32)


def modularity_Z_score(A: np.ndarray, gamma: float, n_rewires: int,
                        rng: np.random.Generator, base_seed: int) -> dict:
    """Compute modularity Z score at resolution gamma against degree-preserving null."""
    labels_real = louvain_partition(A, gamma, seed=base_seed)
    Q_real = modularity_Q(A, labels_real, gamma)
    Q_nulls = []
    for k in range(n_rewires):
        A_null = degree_preserving_rewire(A, rng, n_swaps_per_edge=5)
        labels_null = louvain_partition(A_null, gamma, seed=base_seed + 100 + k)
        Q_nulls.append(modularity_Q(A_null, labels_null, gamma))
    Q_null_mean = float(np.mean(Q_nulls)) if Q_nulls else 0.0
    Q_null_std = float(np.std(Q_nulls)) if Q_nulls else 1e-8
    if Q_null_std < 1e-6:
        Q_null_std = 1e-6
    Z = (Q_real - Q_null_mean) / Q_null_std
    n_clusters_real = int(len(set(labels_real.tolist())))
    return {
        "gamma": gamma,
        "Q_real": round(float(Q_real), 4),
        "Q_null_mean": round(Q_null_mean, 4),
        "Q_null_std": round(Q_null_std, 4),
        "Z": round(float(Z), 3),
        "n_clusters": n_clusters_real,
        "labels": labels_real.tolist(),
    }


# ===== Laplacian RG (heat-kernel diffusion) =====

def laplacian_heat_kernel_partition(A: np.ndarray, tau: float, seed: int) -> np.ndarray:
    """Compute heat-kernel exp(-tau * L_norm); cluster the heat-smoothed adjacency."""
    n = A.shape[0]
    d = A.sum(axis=1)
    d_safe = np.where(d > 0, d, 1.0)
    D_inv_sqrt = 1.0 / np.sqrt(d_safe)
    # Normalized Laplacian L = I - D^-1/2 A D^-1/2
    L_norm = np.eye(n, dtype=np.float64) - (D_inv_sqrt[:, None] * A.astype(np.float64)
                                              * D_inv_sqrt[None, :])
    # Symmetric eigendecomp; small n (<=150) so dense is fine
    w, V = np.linalg.eigh(L_norm)
    # heat kernel
    H = (V * np.exp(-tau * w)[None, :]) @ V.T
    # symmetrize numerical
    H = 0.5 * (H + H.T)
    # nonneg adjacency for clustering
    H_pos = np.clip(H, 0.0, None)
    np.fill_diagonal(H_pos, 0.0)
    return louvain_partition(H_pos.astype(np.float32), gamma=1.0, seed=seed)


def ari(a: np.ndarray, b: np.ndarray) -> float:
    """Adjusted Rand Index between two label arrays (no sklearn dep needed; use a small impl)."""
    from collections import Counter
    n = len(a)
    if n == 0:
        return 0.0
    contingency: dict[tuple[int, int], int] = defaultdict(int)
    for i in range(n):
        contingency[(int(a[i]), int(b[i]))] += 1
    sum_comb_c = 0
    for cnt in contingency.values():
        sum_comb_c += cnt * (cnt - 1) // 2
    a_counts = Counter(a.tolist())
    b_counts = Counter(b.tolist())
    sum_comb_a = sum(c * (c - 1) // 2 for c in a_counts.values())
    sum_comb_b = sum(c * (c - 1) // 2 for c in b_counts.values())
    total = n * (n - 1) // 2
    if total == 0:
        return 1.0
    expected = (sum_comb_a * sum_comb_b) / total
    max_ = 0.5 * (sum_comb_a + sum_comb_b)
    if max_ - expected == 0:
        return 0.0
    return float((sum_comb_c - expected) / (max_ - expected))


def lrg_stability(A: np.ndarray, taus: list[float], seed: int) -> dict:
    """Run LRG at each tau; compute pairwise ARI between adjacent tau partitions."""
    partitions = {}
    for tau in taus:
        partitions[tau] = laplacian_heat_kernel_partition(A, tau, seed)
    pair_aris = []
    for i in range(len(taus) - 1):
        t1, t2 = taus[i], taus[i + 1]
        pair_aris.append({
            "tau_a": t1, "tau_b": t2,
            "ari": round(ari(partitions[t1], partitions[t2]), 4),
            "n_clusters_a": int(len(set(partitions[t1].tolist()))),
            "n_clusters_b": int(len(set(partitions[t2].tolist()))),
        })
    n_above = sum(1 for p in pair_aris if p["ari"] >= LRG_STABILITY_PASS)
    return {
        "taus": taus,
        "pair_aris": pair_aris,
        "n_pairs_above_threshold": n_above,
        "mean_pair_ari": round(float(np.mean([p["ari"] for p in pair_aris])) if pair_aris
                                else 0.0, 4),
    }


# ===== sparse-ensemble allocation (Tonegawa engram analog) =====

def sparse_ensemble_allocate(E_anchors: np.ndarray, labels_init: np.ndarray,
                              n_iters: int, temp: float, decay: float) -> dict:
    """Iterative softmax reallocation:
      cluster_centroid = mean of member vectors
      cluster_assignment(t+1) = softmax((1/temp) * (E @ centroid - decay * cluster_size))
    """
    n_anchors = E_anchors.shape[0]
    # Initial: each label gets a centroid; relabel to dense
    uniq = sorted(set(labels_init.tolist()))
    label_to_dense = {lab: i for i, lab in enumerate(uniq)}
    labels = np.array([label_to_dense[int(l)] for l in labels_init], dtype=np.int64)
    K = len(uniq)
    if K == 1:
        return {"converged": True, "final_labels": labels.tolist(),
                "ari_init_vs_final": 1.0, "n_iters": 0}
    # Normalize E for stable softmax
    E = E_anchors.astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True) + 1e-8
    E_u = E / norms
    init_labels = labels.copy()
    for it in range(n_iters):
        # centroid_k = sum_{i in k} E_u[i] / count_k
        centroids = np.zeros((K, E_u.shape[1]), dtype=np.float32)
        sizes = np.zeros(K, dtype=np.float32)
        for i in range(n_anchors):
            centroids[labels[i]] += E_u[i]
            sizes[labels[i]] += 1.0
        sizes_safe = np.where(sizes > 0, sizes, 1.0)
        centroids = centroids / sizes_safe[:, None]
        # scores: (n_anchors, K)
        scores = (E_u @ centroids.T) - decay * sizes[None, :]
        # softmax over K with inverse-temp 1/temp
        z = scores / max(temp, 1e-6)
        z = z - z.max(axis=1, keepdims=True)
        ez = np.exp(z.astype(np.float64))
        probs = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        new_labels = np.argmax(probs, axis=1).astype(np.int64)
        if np.array_equal(new_labels, labels):
            converged = True
            labels = new_labels
            return {
                "converged": converged,
                "final_labels": labels.tolist(),
                "ari_init_vs_final": round(ari(init_labels, labels), 4),
                "n_iters": it + 1,
            }
        labels = new_labels
    return {
        "converged": False,
        "final_labels": labels.tolist(),
        "ari_init_vs_final": round(ari(init_labels, labels), 4),
        "n_iters": n_iters,
    }


# ===== sanity self-test: planted 2-block partition =====

def _selftest():
    """Endpoint: planted 2-block adjacency -> mod_Z(REAL) >> mod_Z(SHUF)."""
    import torch  # noqa: F401 (consistency with v2c style)
    n = 50
    rng = np.random.default_rng(42)
    A = np.zeros((n, n), dtype=np.float32)
    # 2 blocks of 25; strong intra, weak inter
    for i in range(n):
        for j in range(i + 1, n):
            same_block = (i < 25) == (j < 25)
            p = 0.7 if same_block else 0.05
            if rng.random() < p:
                w = float(0.5 + rng.random() * 0.5)
                A[i, j] = w
                A[j, i] = w
    A_thr = threshold_adjacency(A, 0.0)
    z_real = modularity_Z_score(A_thr, gamma=1.0, n_rewires=20,
                                 rng=np.random.default_rng(7), base_seed=7)
    # Shuffle: degree-preserving rewire of the planted graph itself
    A_shuf = degree_preserving_rewire(A_thr, np.random.default_rng(99), n_swaps_per_edge=5)
    z_shuf = modularity_Z_score(A_shuf, gamma=1.0, n_rewires=20,
                                 rng=np.random.default_rng(8), base_seed=8)
    print("[selftest] planted-2-block: Z_REAL=%.2f Z_SHUF=%.2f n_clusters_real=%d "
          "n_clusters_shuf=%d" % (z_real["Z"], z_shuf["Z"], z_real["n_clusters"],
                                    z_shuf["n_clusters"]), flush=True)
    # The planted graph should have Z >> 0; rewire should drop Z meaningfully.
    assert z_real["Z"] >= 2.0, "planted 2-block self-test FAIL: Z_REAL=%.2f < 2.0" % z_real["Z"]
    assert z_real["Z"] > z_shuf["Z"], (
        "planted 2-block self-test FAIL: Z_REAL=%.2f not greater than Z_SHUF=%.2f"
        % (z_real["Z"], z_shuf["Z"])
    )
    # Also exercise LRG + allocation on the planted graph
    lrg = lrg_stability(A_thr, [0.1, 1.0, 10.0], seed=11)
    print("[selftest] LRG stability mean_pair_ari=%.3f n_above_thr=%d"
          % (lrg["mean_pair_ari"], lrg["n_pairs_above_threshold"]), flush=True)
    E_demo = rng.standard_normal((n, 64)).astype(np.float32)
    alloc = sparse_ensemble_allocate(E_demo, np.array(z_real["labels"]),
                                      n_iters=10, temp=ALLOC_TEMP, decay=ALLOC_DECAY)
    print("[selftest] allocation converged=%s n_iters=%d ari_init_vs_final=%.3f"
          % (alloc["converged"], alloc["n_iters"], alloc["ari_init_vs_final"]), flush=True)
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated in selftest"
    print("[selftest] PASS: modularity-Z + LRG + allocation compose; n_llm_calls=0",
          flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== per-seed runner =====

def run_seed(seed: int, combined_atoms: list[str], triples_str: list[tuple[int, str, int]],
             rel_types: list[str], n_chain_grade: int) -> dict:
    t_start = time.time()
    rng = np.random.default_rng(seed)
    n_ent = len(combined_atoms)
    rel_to_idx = {r: i for i, r in enumerate(rel_types)}
    n_rel = len(rel_types)
    triples_idx = [(s, rel_to_idx[r], o) for (s, r, o) in triples_str]

    t_enc0 = time.time()
    E_np, encoder = encode_atoms_substrate(combined_atoms, N_DIM)
    t_enc = round(time.time() - t_enc0, 1)
    print("  [seed=%d] encoded %d atoms at N=%d in %.1fs"
          % (seed, n_ent, N_DIM, t_enc), flush=True)

    n_probe = min(n_ent, 200)
    recall = atom_retrieval_recall(E_np, combined_atoms, encoder, n_probe,
                                    np.random.default_rng(seed + 1))

    # anchors from chain-grade prefix only
    if n_chain_grade <= N_ANCHORS:
        anchors = list(range(n_chain_grade))
    else:
        anchors = sorted(rng.choice(n_chain_grade, N_ANCHORS, replace=False).tolist())
    print("  [seed=%d] %d anchors chosen from %d chain-grade prefix"
          % (seed, len(anchors), n_chain_grade), flush=True)

    # Build substrate KG once (REAL)
    t_kg0 = time.time()
    kg_real = build_kg(E_np, triples_idx, n_ent, n_rel, N_DIM, seed)
    t_kg = round(time.time() - t_kg0, 1)
    print("  [seed=%d] KG built in %.1fs" % (seed, t_kg), flush=True)

    pairs = sample_relation_pairs(n_rel, N_RELATION_SAMPLES,
                                    np.random.default_rng(seed + 2))

    # 2-hop neighborhoods for anchors
    t_nbr0 = time.time()
    nbr: dict[int, set[int]] = {}
    for a in anchors:
        nbr[a] = two_hop_neighborhood(kg_real, a, pairs, K_SET)
    t_nbr = round(time.time() - t_nbr0, 1)
    print("  [seed=%d] 2-hop neighborhoods built in %.1fs"
          % (seed, t_nbr), flush=True)

    # Build weighted adjacency from pairwise neighborhood Jaccard
    A_raw = build_jaccard_adjacency(anchors, nbr)
    A_real = threshold_adjacency(A_raw, JACCARD_TAU)
    # ARM SHUF: degree-preserving rewire of REAL adjacency
    A_shuf = degree_preserving_rewire(A_real, np.random.default_rng(seed + 3),
                                       n_swaps_per_edge=10)
    print("  [seed=%d] adjacency: real edges=%d shuf edges=%d (tau=%.2f)"
          % (seed, int((A_real > 0).sum() // 2), int((A_shuf > 0).sum() // 2),
             JACCARD_TAU), flush=True)

    # Modularity-Z sweep on both arms
    t_modz0 = time.time()
    modz_real_sweep = []
    modz_shuf_sweep = []
    for gamma in GAMMA_SWEEP:
        zr = modularity_Z_score(A_real, gamma, N_NULL_REWIRES,
                                  np.random.default_rng(seed + 10 + int(gamma * 10)),
                                  base_seed=seed)
        zs = modularity_Z_score(A_shuf, gamma, N_NULL_REWIRES,
                                  np.random.default_rng(seed + 20 + int(gamma * 10)),
                                  base_seed=seed + 1)
        # drop verbose labels in summary
        zr_summary = {k: v for k, v in zr.items() if k != "labels"}
        zs_summary = {k: v for k, v in zs.items() if k != "labels"}
        modz_real_sweep.append({**zr_summary, "labels": zr["labels"]})
        modz_shuf_sweep.append(zs_summary)
        print("    [seed=%d gamma=%.1f] Z_real=%.2f Z_shuf=%.2f K_real=%d K_shuf=%d"
              % (seed, gamma, zr["Z"], zs["Z"], zr["n_clusters"], zs["n_clusters"]),
              flush=True)
    t_modz = round(time.time() - t_modz0, 1)

    # Best gamma by Z(real)
    best_real = max(modz_real_sweep, key=lambda r: r["Z"])
    best_gamma = best_real["gamma"]
    best_Z_real = best_real["Z"]
    # SHUF Z at the same gamma
    same_gamma_shuf = next(s for s in modz_shuf_sweep if s["gamma"] == best_gamma)
    best_Z_shuf = same_gamma_shuf["Z"]

    # LRG stability across tau
    t_lrg0 = time.time()
    lrg_real = lrg_stability(A_real, TAU_SWEEP, seed=seed)
    lrg_shuf = lrg_stability(A_shuf, TAU_SWEEP, seed=seed + 100)
    t_lrg = round(time.time() - t_lrg0, 1)

    # Sparse-ensemble allocation diagnostic (on best-gamma REAL labels)
    t_alloc0 = time.time()
    init_labels = np.array(best_real["labels"], dtype=np.int64)
    E_anchors = E_np[np.array(anchors, dtype=np.int64)]
    alloc = sparse_ensemble_allocate(E_anchors, init_labels, ALLOC_ITERS,
                                       ALLOC_TEMP, ALLOC_DECAY)
    t_alloc = round(time.time() - t_alloc0, 1)

    elapsed = round(time.time() - t_start, 1)
    print("  [seed=%d] DONE in %.1fs | best gamma=%.1f Z_real=%.2f Z_shuf=%.2f "
          "ratio=%.2f | LRG_real n_above=%d mean_ari=%.3f | alloc conv=%s "
          "ari=%.3f | recall=%.3f"
          % (seed, elapsed, best_gamma, best_Z_real, best_Z_shuf,
             best_Z_real / max(best_Z_shuf, 1e-3),
             lrg_real["n_pairs_above_threshold"], lrg_real["mean_pair_ari"],
             alloc["converged"], alloc["ari_init_vs_final"], recall), flush=True)

    return {
        "seed": seed,
        "_ckpt_key": str(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_chain_grade_atoms": n_chain_grade,
        "n_atoms_universe": n_ent,
        "n_relation_types": n_rel,
        "n_triples": len(triples_idx),
        "n_anchors": len(anchors),
        "n_real_edges": int((A_real > 0).sum() // 2),
        "n_shuf_edges": int((A_shuf > 0).sum() // 2),
        "atom_retrieval_recall": round(recall, 4),
        "elapsed_s": elapsed,
        "t_encoding_s": t_enc,
        "t_kg_build_s": t_kg,
        "t_neighborhoods_s": t_nbr,
        "t_modularity_Z_s": t_modz,
        "t_lrg_s": t_lrg,
        "t_alloc_s": t_alloc,
        "best_gamma": best_gamma,
        "best_Z_real": best_Z_real,
        "best_Z_shuf": best_Z_shuf,
        "Z_ratio_real_over_shuf": round(best_Z_real / max(best_Z_shuf, 1e-3), 3),
        "modularity_Z_real_sweep": [
            {k: v for k, v in r.items() if k != "labels"} for r in modz_real_sweep
        ],
        "modularity_Z_shuf_sweep": modz_shuf_sweep,
        "lrg_real": lrg_real,
        "lrg_shuf": lrg_shuf,
        "allocation_diag": alloc,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


# ===== verdict =====

def verdict(per_seed_records: list[dict]) -> Tuple[str, str]:
    if not per_seed_records:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed records")
    best_Z_real = [p["best_Z_real"] for p in per_seed_records]
    best_Z_shuf = [p["best_Z_shuf"] for p in per_seed_records]
    z_ratios = [p["Z_ratio_real_over_shuf"] for p in per_seed_records]
    lrg_n_above = [p["lrg_real"]["n_pairs_above_threshold"] for p in per_seed_records]
    lrg_mean_ari = [p["lrg_real"]["mean_pair_ari"] for p in per_seed_records]
    recalls = [p["atom_retrieval_recall"] for p in per_seed_records]
    llm_calls = [p.get("n_llm_calls", 0) for p in per_seed_records]
    mean_Z_real = float(np.mean(best_Z_real))
    mean_Z_shuf = float(np.mean(best_Z_shuf))
    mean_ratio = float(np.mean(z_ratios))
    mean_lrg_above = float(np.mean(lrg_n_above))
    recall_mean = float(np.mean(recalls))

    # Any-gamma rule on mean Z; also any-seed Z >= MOD_Z_PASS check
    any_gamma_pass = max(best_Z_real) >= MOD_Z_PASS
    any_gamma_fail_floor = max(best_Z_real) < MOD_Z_FAIL  # every seed best-Z < floor

    summary = (
        "best_Z_real_mean=%.2f (pass %.1f fail %.1f) | best_Z_shuf_mean=%.2f | "
        "Z_ratio_mean=%.2f (pass %.1f fail %.1f) | LRG_n_above_mean=%.1f (pass %d) "
        "LRG_mean_ari=%.3f | recall=%.3f | n_llm=%d"
    ) % (mean_Z_real, MOD_Z_PASS, MOD_Z_FAIL, mean_Z_shuf, mean_ratio,
         MOD_Z_RATIO_PASS, MOD_Z_RATIO_FAIL, mean_lrg_above, LRG_N_TAU_REQUIRED,
         float(np.mean(lrg_mean_ari)), recall_mean, max(llm_calls))

    if max(llm_calls) > 0:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode violated; n_llm_calls>0. "
                + summary)
    if recall_mean < RECALL_FAIL:
        return ("HARD_FAIL", "HARD_FAIL: atom retrieval recall below floor. " + summary)
    if any_gamma_fail_floor:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate self-mapping null even with right discriminator "
                "(every seed best Z_real < %.1f at every gamma). Encoder substitution "
                "indicated per 5x drill. " % MOD_Z_FAIL + summary)
    if mean_ratio < MOD_Z_RATIO_FAIL:
        return ("HARD_FAIL",
                "HARD_FAIL: REAL/SHUF Z ratio below floor (%.2f < %.1f); degree-preserved "
                "rewire as structured as real. " % (mean_ratio, MOD_Z_RATIO_FAIL) + summary)
    # HARD_PASS gates
    pass_modZ = any_gamma_pass
    pass_ratio = mean_ratio >= MOD_Z_RATIO_PASS
    pass_lrg = mean_lrg_above >= LRG_N_TAU_REQUIRED
    pass_recall = recall_mean >= RECALL_PASS
    pass_no_llm = max(llm_calls) == 0
    if pass_modZ and pass_ratio and pass_lrg and pass_recall and pass_no_llm:
        return ("HARD_PASS",
                "HARD_PASS: substrate exhibits intrinsic multi-scale community structure; "
                "modularity-Z >= %.1f at some gamma + LRG stability across >=%d tau pairs + "
                "REAL/SHUF ratio >= %.1f. " % (MOD_Z_PASS, LRG_N_TAU_REQUIRED, MOD_Z_RATIO_PASS)
                + summary)
    # MIDDLE band: partial signal
    if MOD_Z_FAIL <= mean_Z_real < MOD_Z_PASS:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: partial signal; mod_Z(REAL) in [%.1f, %.1f) at best gamma. "
                "Characterize which bar failed. " % (MOD_Z_FAIL, MOD_Z_PASS) + summary)
    return ("HARD_FAIL", "HARD_FAIL: below pre-reg bars. " + summary)


# ===== main =====

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION), flush=True)
    t0 = time.time()
    print("[load] cert_ledger chain-grade atoms...", flush=True)
    chain_grade_atoms = load_chain_grade_atom_ids()
    print("  -> %d chain-grade atoms" % len(chain_grade_atoms), flush=True)
    print("[load] atomized atom universe across all corpora atoms.jsonl...", flush=True)
    atomized = load_atomized_atom_ids()
    print("  -> %d atomized atom_ids" % len(atomized), flush=True)
    print("[load] FULL-Store relations admit...", flush=True)
    load_rng = np.random.default_rng(0)
    triples_str, rel_types, combined_atoms, n_chain_grade = load_relations_for(
        chain_grade_atoms, atomized, MAX_INGEST_TRIPLES, load_rng)
    print("  -> %d admitted triples; %d distinct relation types"
          % (len(triples_str), len(rel_types)), flush=True)
    print("  -> %d combined atoms (%d chain-grade prefix + %d frontier)"
          % (len(combined_atoms), n_chain_grade, len(combined_atoms) - n_chain_grade),
          flush=True)
    if not triples_str or not rel_types:
        print("[error] no admitted triples; aborting", flush=True)
        sys.exit(2)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s"
          % (len(done), len(SEEDS), remaining), flush=True)

    for s in remaining:
        rec = run_seed(s, combined_atoms, triples_str, rel_types, n_chain_grade)
        write_partial(out_dir, s, rec)

    agg = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    v, vmsg = verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION,
        "per_seed": per_seed,
        "zero_llm_calls_at_inference": all(p.get("n_llm_calls", 0) == 0 for p in per_seed),
        "elapsed_s": round(time.time() - t0, 1),
        "DESIGN_NOTE": (
            "v2e intrinsic multi-scale discriminator (modularity-Z vs degree-preserving "
            "null + Laplacian-RG tau-sweep stability + sparse-ensemble allocation). "
            "Abandons external lexical ground truth per 5x drill conclusion that v1 "
            "families are structurally degenerate (~2/20 anchors matched at smoke). "
            "Two arms: REAL substrate adjacency vs SHUF degree-preserved rewire. "
            "HARD_PASS = real exhibits multi-scale community structure; HARD_FAIL = "
            "substrate self-mapping null even under right discriminator (forces encoder "
            "substitution per drill, not another discriminator attempt)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
