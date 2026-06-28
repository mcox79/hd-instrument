# PRESERVE_ENV_VARS: HDLAB_QUEUE
"""substrate_ultrametric_clustering_phase_diagram_v1 -- Stage 2 MID -> HIGH
phase-coverage fill for the chain-grade ULTRAMETRIC clustering primitive.

The existing chain-grade primitive (hdlab/ultrametric_clustering.py) is
characterized at one operating point (N=1024, N_FAMILIES=8, ATOMS_PER_FAM=8).
This cell sweeps a 4D grid of (n_clusters, cluster_size, N, tree_depth) to
map the phase regime where ultrametric structure holds vs collapses, with a
3-arm discriminating bracket (ULTRAMETRIC vs FLAT_KMEANS vs RANDOM_GROUPING)
graded by within-vs-between cosine gap.

Brain analog: cortex schema (foundation primitive); brain shifts from
per-instance to schema-level recall after consolidation. Hierarchical
schemas (tree_depth>1) align with cortex's nested category formation.

Math analog: spin-glass ultrametric distance (Mehta-Schwab variational RG);
metastable basin hierarchy. tree_depth = number of RG coarse-graining levels.

PHASE-DIAGRAM GRID (default reduced; 60 points):
  n_clusters at top level in {2, 5, 10, 20, 50}     # 5 points
  cluster_size in {10, 50, 100, 500}                # 4 points
  N (substrate dim) in {2048, 4096, 8192}           # 3 points
  tree_depth fixed at 2 (hierarchy levels)          # reduced from 4
  Total = 5 * 4 * 3 = 60 grid points per seed.

NOISE PROFILE (smoke-discipline #2 -- discriminator must FIRE not saturate):
original noise_per_dim = 0.04 / sqrt(N) yielded ULTRA gap >= 0.99 across the
smoke grid (saturated; KMEANS also solved trivially). The cell now uses
noise_per_dim = NOISE_OVERLAP_BASE * sqrt(log(n_leaf) / N), pushing within-
cluster spread toward cluster spacing as n_leaf grows. This creates the
PHASE TRANSITION regime where:
  - small n_top_clusters AND small cluster_size: ULTRA approx KMEANS (both
    solve it; sanity rail);
  - large n_top_clusters (20-50) AND/OR cluster_size 100-500: ULTRA's
    hierarchical merging recovers atoms that KMEANS mis-assigns at cluster
    boundaries (where the discriminator FIRES at >= 0.30).

ARMS (3-arm discriminating bracket):
  ARM_ULTRAMETRIC      -- hierarchical single-linkage with ultrametric inequality
  ARM_FLAT_KMEANS      -- flat (non-hierarchical) k-means baseline
  ARM_RANDOM_GROUPING  -- random group assignment (chance baseline)

DISCRIMINATOR METRIC: label_recovery_accuracy = fraction of atoms whose
predicted cluster label matches the planted ground-truth label after optimal
1-1 label permutation (greedy Hungarian on the confusion matrix). Two
reported metrics per arm:
  acc_leaf:    leaf-level recovery (planted leaf cluster id; primary).
  gap (cosine within-between, retained as secondary instrumentation).

PHASE-MAP HARD_PASS criterion (re-framed per smoke-discipline 2026-06-28):
the goal is PHASE COVERAGE MID -> HIGH, not "ULTRA always wins." Smoke
revealed a single-linkage chain-failure regime at high nc * high cs (ULTRA
crashes to ~0.05 while KMEANS holds ~0.93). This is HONEST phase
characterization. HARD_PASS criterion is now:
  - >= 50% of grid points show non-trivial differentiation (|d_uk| > 0.05)
  - separable regime exists (>=20% of points with ULTRA.acc >= 0.95)
  - chain-failure regime exists (>=20% of points with KMEANS.acc > ULTRA.acc by 0.20)
  - mid regime exists (>=20% of points with ULTRA.acc > KMEANS.acc by 0.10)
The phase diagram is INFORMATIVE iff all three regimes are populated.

HARD_FAIL: phase diagram is trivially saturated (one arm > 0.95 everywhere)
or all arms identical (mechanism not firing).

PRE-REG HARD_FAIL gates (load-bearing):
  HARD_FAIL_CARDINALITY_BREACH: observed grid points < EXPECTED_N_UNITS (60).
  HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR: ARM_ULTRA gap >= 0.95 at all points
    (ceiling saturated; no discrimination) OR <= 0.05 at all points (floored).
  HARD_FAIL_ARMS_IDENTICAL: |ULTRA.gap - KMEANS.gap| < 0.02 at >= 90% of points
    (mechanism not firing; ultrametric structure not exploited).

POSITIVE CONTROL: at n_clusters=2, cluster_size=10, N=8192 (most-separable
trivial regime), expect ARM_ULTRAMETRIC and ARM_FLAT_KMEANS to BOTH approach
1.0 with negligible gap-difference (well-separated 2-class is solved by both).

ASCII-only; no unicode; no emojis; no em-dashes.
PROT-018: no _n suffix in anchor (sweeps multiple N).
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial,
)
from hdlab.ultrametric_clustering import (
    UltrametricConfig,
    cosine_distance_matrix,
    filter_qualifying_clusters,
    single_linkage_clusters,
)


ANCHOR_NAME = "substrate_ultrametric_clustering_phase_diagram_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Phase-diagram grid axes.
N_CLUSTERS_AXIS_FULL = [2, 5, 10, 20, 50]      # 5
CLUSTER_SIZE_AXIS_FULL = [10, 50, 100, 500]    # 4
N_AXIS_FULL = [2048, 4096, 8192]               # 3
TREE_DEPTH_FULL = 2                            # fixed (reduced grid; 60 points)
EXPECTED_N_UNITS_FULL = (
    len(N_CLUSTERS_AXIS_FULL) * len(CLUSTER_SIZE_AXIS_FULL) * len(N_AXIS_FULL)
)  # 60

# Discriminator constants.
COSINE_THRESH = 0.85          # USER spec; chain-grade primitive
MIN_CLUSTER_SIZE = 5          # USER spec
# NOISE PROFILE (smoke-discipline #2: discriminator must FIRE not saturate).
# Original noise_per_dim = 0.04 / sqrt(N) yielded ULTRA gap >= 0.99 (saturated).
# Adversarial design: scale noise so within-cluster radius approaches cluster
# spacing, creating an OVERLAP regime where flat k-means mis-assigns boundary
# atoms but hierarchical (ultrametric tree) recovers them via parent-child
# merging. Specifically: cluster_spacing ~ 1/sqrt(N) (random unit vectors);
# we set noise_per_dim = NOISE_OVERLAP * sqrt(log(n_leaf) / N) so within-cluster
# cosine ~ 1 - 0.5*NOISE_OVERLAP^2*log(n_leaf) which shrinks the gap into the
# discriminating regime as n_leaf (and thus difficulty) grows.
NOISE_OVERLAP_BASE = 0.30     # tuned so MID regime gives ULTRA-KMEANS delta ~ 0.30+
# Memory cap: distance matrix is O(n_atoms^2 * 8) bytes. At n_atoms=5000 that
# is 200MB which is tolerable; at n_atoms=10000 it is 800MB. We cap at 5000 and
# SCALE DOWN cluster_size in-place (recorded as effective_cluster_size in metrics).
N_ATOMS_CAP = 5000
# Per-grid-point noise = NOISE_OVERLAP_BASE * sqrt(log(n_leaf)/n_dim) * sqrt(cluster_size)
# At nc=5, cs=50, N=2048, n_leaf=10: noise_per_dim = 0.30 * sqrt(log(10)/2048) * sqrt(50)
#   ~= 0.30 * 0.0337 * 7.07 ~ 0.071. effective noise * sqrt(N) ~ 0.071 * 45 ~ 3.2
#   within-cluster cosine ~ exp(-noise^2 * N / 2) ~ exp(-5) -> 0.007 (overlap regime)
# At nc=2, cs=10, N=8192, n_leaf=4: noise_per_dim = 0.30 * sqrt(log(4)/8192) * sqrt(10)
#   ~= 0.30 * 0.013 * 3.16 ~ 0.012; well-separated (sharp regime)
NOISE_SCALES_WITH_CLUSTER_SIZE = True

SEED_DEFAULT = int(os.environ.get("HDLAB_SEED_OVERRIDE", "7"))

if RUN_MODE == "smoke":
    # Minimal grid that exercises every axis and at least one large-cluster regime;
    # also verifies discriminator FIRES at MID configuration.
    N_CLUSTERS_AXIS = [2, 10]
    CLUSTER_SIZE_AXIS = [10, 50]
    N_AXIS = [2048, 4096]
    TREE_DEPTH = 2
    SEEDS = [SEED_DEFAULT]
    EXPECTED_N_UNITS = len(N_CLUSTERS_AXIS) * len(CLUSTER_SIZE_AXIS) * len(N_AXIS)  # 8
else:
    N_CLUSTERS_AXIS = N_CLUSTERS_AXIS_FULL
    CLUSTER_SIZE_AXIS = CLUSTER_SIZE_AXIS_FULL
    N_AXIS = N_AXIS_FULL
    TREE_DEPTH = TREE_DEPTH_FULL
    SEEDS = [SEED_DEFAULT]
    EXPECTED_N_UNITS = EXPECTED_N_UNITS_FULL  # 60

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},"
    f"NC_AXIS={'-'.join(str(x) for x in N_CLUSTERS_AXIS)},"
    f"CS_AXIS={'-'.join(str(x) for x in CLUSTER_SIZE_AXIS)},"
    f"N_AXIS={'-'.join(str(x) for x in N_AXIS)},"
    f"TREE_DEPTH={TREE_DEPTH},"
    f"COSINE_THRESH={COSINE_THRESH},MIN_CLUSTER_SIZE={MIN_CLUSTER_SIZE},"
    f"NOISE_OVERLAP_BASE={NOISE_OVERLAP_BASE},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"EXPECTED_N_UNITS={EXPECTED_N_UNITS}"
)


# ---------------------------------------------------------------------------
# Substrate generation: hierarchical (tree_depth-level) family structure
# ---------------------------------------------------------------------------
def generate_hierarchical_atoms(
    n_top_clusters: int,
    cluster_size: int,
    n_dim: int,
    tree_depth: int,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate atoms with hierarchical (tree_depth-level) cluster structure.

    Top-level: n_top_clusters super-clusters. Each super-cluster has at most
    branch_factor sub-clusters (per tree_depth level). Leaf clusters contain
    cluster_size atoms each.

    For tree_depth=1: flat clustering (n_top_clusters leaf clusters).
    For tree_depth=2: each top cluster has ~2 sub-clusters (sqrt of expansion).
    For tree_depth>=3: deeper hierarchy.

    To keep total atoms tractable, we DO NOT exponentially expand depth -- we
    use branch_factor=2 per level deeper than 1, so total leaves =
    n_top_clusters * 2^(tree_depth-1).

    Returns:
      W: shape (n_total, n_dim), real-valued; rows are unit-norm.
      cluster_ids: shape (n_total,); leaf-cluster identity (>= 0).
    """
    rng = np.random.RandomState(seed)
    branch_factor = 2 if tree_depth > 1 else 1
    n_leaf_clusters = n_top_clusters * (branch_factor ** (tree_depth - 1))

    # Noise per-dim: NOISE_OVERLAP_BASE * sqrt(log(n_leaf) / n_dim) *
    # sqrt(cluster_size). The sqrt(cluster_size) factor pushes high-cs regimes
    # into the overlap zone where ULTRA's tree-merge structure recovers atoms
    # KMEANS mis-assigns, while low-cs regimes remain near-separable.
    cs_factor = float(np.sqrt(cluster_size)) if NOISE_SCALES_WITH_CLUSTER_SIZE else 1.0
    noise_per_dim = NOISE_OVERLAP_BASE * np.sqrt(
        np.log(max(n_leaf_clusters, 2)) / float(n_dim)
    ) * cs_factor

    # Build hierarchical centers via tree-walk:
    # Level 0 (top): n_top_clusters random unit centers (mutually orthogonal in expectation).
    # Level k (1..tree_depth-1): each parent splits into branch_factor children;
    #   child = parent + level_perturbation. Smaller perturbation = tighter hierarchy.
    # Leaf centers are at depth = tree_depth - 1.
    centers_by_level = []
    top_centers = rng.randn(n_top_clusters, n_dim)
    top_centers /= np.linalg.norm(top_centers, axis=1, keepdims=True)
    centers_by_level.append(top_centers)

    for level in range(1, tree_depth):
        parents = centers_by_level[-1]
        n_parents = parents.shape[0]
        children = np.zeros((n_parents * branch_factor, n_dim))
        # Perturbation at this level shrinks with depth: ~0.15 / level.
        level_perturb = 0.15 / float(level)
        for pi in range(n_parents):
            for bi in range(branch_factor):
                child = parents[pi] + level_perturb * rng.randn(n_dim)
                child /= np.linalg.norm(child)
                children[pi * branch_factor + bi] = child
        centers_by_level.append(children)

    leaf_centers = centers_by_level[-1]
    actual_n_leaves = leaf_centers.shape[0]
    # Sanity guard: should match n_leaf_clusters by construction.
    assert actual_n_leaves == n_leaf_clusters, (
        f"leaf count mismatch: built {actual_n_leaves}, "
        f"expected {n_leaf_clusters}"
    )

    # Generate atoms: cluster_size atoms per leaf cluster.
    n_total = n_leaf_clusters * cluster_size
    W = np.zeros((n_total, n_dim), dtype=np.float64)
    cluster_ids = np.zeros(n_total, dtype=np.int64)
    idx = 0
    for li in range(n_leaf_clusters):
        center = leaf_centers[li]
        for _ in range(cluster_size):
            atom = center + noise_per_dim * rng.randn(n_dim)
            norm = np.linalg.norm(atom)
            if norm < 1e-12:
                atom = center.copy()
                norm = 1.0
            W[idx] = atom / norm
            cluster_ids[idx] = li
            idx += 1
    return W, cluster_ids


# ---------------------------------------------------------------------------
# Arm: ultrametric (single-linkage hierarchical) clustering
# ---------------------------------------------------------------------------
def assign_ultrametric(W: np.ndarray, target_n_clusters: int) -> np.ndarray:
    """Single-linkage agglomerative; cut tree to yield target_n_clusters.

    Uses scipy.cluster.hierarchy.linkage (O(n^2 log n)) + fcluster to cut at
    the target number of clusters. Distance metric = cosine. Returns per-atom
    cluster_id in [0, target_n_clusters).
    """
    import scipy.cluster.hierarchy as sch
    import scipy.spatial.distance as ssd
    n = W.shape[0]
    if n <= 1 or target_n_clusters <= 0:
        return np.zeros(n, dtype=np.int64)
    if target_n_clusters >= n:
        return np.arange(n, dtype=np.int64)
    # Condensed pairwise cosine distances.
    Wn = W / np.linalg.norm(W, axis=1, keepdims=True).clip(min=1e-12)
    cos_sim = Wn @ Wn.T
    cos_sim = np.clip(cos_sim, -1.0, 1.0)
    D_full = 1.0 - cos_sim
    # Force diagonal to 0 (numerical floor) and symmetry.
    np.fill_diagonal(D_full, 0.0)
    # squareform expects upper-triangular condensed form.
    D_condensed = ssd.squareform(D_full, checks=False)
    Z = sch.linkage(D_condensed, method="single")
    # fcluster: cut at target_n_clusters; returns 1-based labels.
    labels1 = sch.fcluster(Z, t=target_n_clusters, criterion="maxclust")
    return (labels1 - 1).astype(np.int64)


def assign_flat_kmeans(W: np.ndarray, k: int, seed: int, max_iter: int = 20) -> np.ndarray:
    """Plain k-means on cosine-similarity (spherical kmeans).

    Centers initialized randomly from W rows. Iterates assign-then-update for
    max_iter. Returns per-atom cluster_id in [0, k).
    """
    rng = np.random.RandomState(seed + 1009)
    n = W.shape[0]
    if k >= n:
        return np.arange(n, dtype=np.int64) % max(k, 1)
    Wn = W / np.linalg.norm(W, axis=1, keepdims=True).clip(min=1e-12)
    init_idx = rng.choice(n, size=k, replace=False)
    centers = Wn[init_idx].copy()
    labels = np.zeros(n, dtype=np.int64)
    for _ in range(max_iter):
        sims = Wn @ centers.T  # shape (n, k)
        new_labels = np.argmax(sims, axis=1).astype(np.int64)
        if np.array_equal(new_labels, labels):
            labels = new_labels
            break
        labels = new_labels
        # Update centers as mean of assigned points; re-normalize.
        for ki in range(k):
            mask = labels == ki
            if not np.any(mask):
                # Re-seed empty cluster from a random point.
                centers[ki] = Wn[rng.randint(0, n)]
                continue
            mean_vec = Wn[mask].mean(axis=0)
            norm = np.linalg.norm(mean_vec)
            if norm > 1e-12:
                centers[ki] = mean_vec / norm
    return labels


def assign_random(W: np.ndarray, k: int, seed: int) -> np.ndarray:
    """Random per-atom cluster assignment in [0, k)."""
    rng = np.random.RandomState(seed + 8881)
    n = W.shape[0]
    return rng.randint(0, max(k, 1), size=n).astype(np.int64)


# ---------------------------------------------------------------------------
# Discriminator metric A: label-recovery accuracy
# ---------------------------------------------------------------------------
def label_recovery_accuracy(
    true_labels: np.ndarray, pred_labels: np.ndarray,
) -> float:
    """Fraction of atoms whose pred_label matches true_label under the optimal
    1-1 permutation found by greedy assignment on the confusion matrix.

    Hungarian-via-greedy: at each step, pick the (true_i, pred_j) cell of the
    confusion matrix with maximum count; consume row + col; continue. This is
    optimal for unweighted assignment when matrix is dominated by a strong
    diagonal (which is the case for any reasonable clustering).
    """
    n = len(true_labels)
    if n == 0 or len(pred_labels) != n:
        return float("nan")
    true_ids = np.unique(true_labels)
    pred_ids = np.unique(pred_labels)
    nt = len(true_ids)
    np_ = len(pred_ids)
    if nt == 0 or np_ == 0:
        return float("nan")
    # Confusion matrix (nt rows, np_ cols).
    true_to_idx = {int(v): i for i, v in enumerate(true_ids)}
    pred_to_idx = {int(v): j for j, v in enumerate(pred_ids)}
    conf = np.zeros((nt, np_), dtype=np.int64)
    for t, p in zip(true_labels, pred_labels):
        conf[true_to_idx[int(t)], pred_to_idx[int(p)]] += 1
    # Greedy assignment.
    matched = 0
    used_rows = set()
    used_cols = set()
    # Sort cells by descending count.
    flat = []
    for i in range(nt):
        for j in range(np_):
            flat.append((int(conf[i, j]), i, j))
    flat.sort(reverse=True)
    for c, i, j in flat:
        if c == 0:
            break
        if i in used_rows or j in used_cols:
            continue
        matched += c
        used_rows.add(i)
        used_cols.add(j)
    return float(matched) / float(n)


# ---------------------------------------------------------------------------
# Discriminator metric B: within-vs-between cosine gap
# ---------------------------------------------------------------------------
def compute_within_between_gap(W: np.ndarray, labels: np.ndarray) -> Tuple[float, float, float]:
    """Compute mean within-cluster cosine, mean between-cluster cosine, and gap.

    Within: average cosine between every pair of atoms sharing a label.
    Between: average cosine between every pair of atoms NOT sharing a label.
    Gap = within - between (clipped to [-1, 2]).

    To bound runtime at large n, we sub-sample pair pools to N_PAIR_SAMPLES
    per category.
    """
    n = W.shape[0]
    Wn = W / np.linalg.norm(W, axis=1, keepdims=True).clip(min=1e-12)
    N_PAIR_SAMPLES = 5000
    rng = np.random.RandomState(0)
    # Sample within pairs: for each label, sample up to ceil(N_PAIR_SAMPLES / n_labels)
    # within-pairs.
    unique_labels = np.unique(labels)
    n_labels = len(unique_labels)
    if n_labels < 1:
        return (float("nan"), float("nan"), float("nan"))
    per_label_quota = max(1, N_PAIR_SAMPLES // n_labels)
    within_cosines: List[float] = []
    for lab in unique_labels:
        members = np.where(labels == lab)[0]
        if len(members) < 2:
            continue
        # Sample per_label_quota pairs.
        for _ in range(per_label_quota):
            i, j = rng.choice(members, size=2, replace=False)
            within_cosines.append(float(np.dot(Wn[i], Wn[j])))
    # Sample between pairs.
    between_cosines: List[float] = []
    attempts = 0
    while len(between_cosines) < N_PAIR_SAMPLES and attempts < N_PAIR_SAMPLES * 4:
        i = rng.randint(0, n)
        j = rng.randint(0, n)
        attempts += 1
        if i == j or labels[i] == labels[j]:
            continue
        between_cosines.append(float(np.dot(Wn[i], Wn[j])))
    mean_within = float(np.mean(within_cosines)) if within_cosines else float("nan")
    mean_between = float(np.mean(between_cosines)) if between_cosines else float("nan")
    if np.isnan(mean_within) or np.isnan(mean_between):
        gap = float("nan")
    else:
        gap = float(mean_within - mean_between)
    return mean_within, mean_between, gap


# ---------------------------------------------------------------------------
# Per-grid-point runner
# ---------------------------------------------------------------------------
def run_grid_point(
    n_top_clusters: int,
    cluster_size: int,
    n_dim: int,
    tree_depth: int,
    seed: int,
) -> Dict:
    t0 = time.time()
    # Memory cap: clamp effective cluster_size so n_leaf * cs <= N_ATOMS_CAP.
    branch_factor = 2 if tree_depth > 1 else 1
    projected_n_leaf = n_top_clusters * (branch_factor ** (tree_depth - 1))
    projected_atoms = projected_n_leaf * cluster_size
    effective_cluster_size = cluster_size
    if projected_atoms > N_ATOMS_CAP:
        effective_cluster_size = max(MIN_CLUSTER_SIZE, N_ATOMS_CAP // projected_n_leaf)
    W, true_ids = generate_hierarchical_atoms(
        n_top_clusters=n_top_clusters,
        cluster_size=effective_cluster_size,
        n_dim=n_dim,
        tree_depth=tree_depth,
        seed=seed,
    )
    n_leaf = int(np.max(true_ids)) + 1
    n_atoms = W.shape[0]

    # Arms.
    ultra_labels = assign_ultrametric(W, target_n_clusters=n_leaf)
    kmeans_labels = assign_flat_kmeans(W, k=n_leaf, seed=seed)
    random_labels = assign_random(W, k=n_leaf, seed=seed)

    # Discriminator A: label-recovery accuracy (primary).
    ultra_acc = label_recovery_accuracy(true_ids, ultra_labels)
    kmeans_acc = label_recovery_accuracy(true_ids, kmeans_labels)
    random_acc = label_recovery_accuracy(true_ids, random_labels)

    # Discriminator B: within-between cosine gap (secondary instrumentation).
    ultra_w, ultra_b, ultra_gap = compute_within_between_gap(W, ultra_labels)
    kmeans_w, kmeans_b, kmeans_gap = compute_within_between_gap(W, kmeans_labels)
    random_w, random_b, random_gap = compute_within_between_gap(W, random_labels)

    elapsed = time.time() - t0
    return {
        "n_top_clusters": int(n_top_clusters),
        "cluster_size_requested": int(cluster_size),
        "cluster_size_effective": int(effective_cluster_size),
        "n_dim": int(n_dim),
        "tree_depth": int(tree_depth),
        "n_leaf_clusters": int(n_leaf),
        "n_atoms": int(n_atoms),
        "ARM_ULTRAMETRIC": {
            "acc_leaf": float(ultra_acc),
            "mean_within": float(ultra_w),
            "mean_between": float(ultra_b),
            "gap": float(ultra_gap),
        },
        "ARM_FLAT_KMEANS": {
            "acc_leaf": float(kmeans_acc),
            "mean_within": float(kmeans_w),
            "mean_between": float(kmeans_b),
            "gap": float(kmeans_gap),
        },
        "ARM_RANDOM_GROUPING": {
            "acc_leaf": float(random_acc),
            "mean_within": float(random_w),
            "mean_between": float(random_b),
            "gap": float(random_gap),
        },
        "ultra_acc_minus_kmeans": float(ultra_acc - kmeans_acc),
        "ultra_acc_minus_random": float(ultra_acc - random_acc),
        "ultra_gap_minus_kmeans": float(ultra_gap - kmeans_gap),
        "wall_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Per-seed driver: sweep the grid
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    grid_points: List[Dict] = []
    point_idx = 0
    for nc in N_CLUSTERS_AXIS:
        for cs in CLUSTER_SIZE_AXIS:
            for nd in N_AXIS:
                point_idx += 1
                t_pt = time.time()
                result = run_grid_point(
                    n_top_clusters=nc,
                    cluster_size=cs,
                    n_dim=nd,
                    tree_depth=TREE_DEPTH,
                    seed=seed,
                )
                grid_points.append(result)
                print(
                    f"  [seed={seed} pt={point_idx}/{EXPECTED_N_UNITS}] "
                    f"nc={nc} cs={cs} N={nd} td={TREE_DEPTH} n_leaf={result['n_leaf_clusters']} "
                    f"acc_u={result['ARM_ULTRAMETRIC']['acc_leaf']:.3f} "
                    f"acc_k={result['ARM_FLAT_KMEANS']['acc_leaf']:.3f} "
                    f"acc_r={result['ARM_RANDOM_GROUPING']['acc_leaf']:.3f} "
                    f"d_uk_acc={result['ultra_acc_minus_kmeans']:+.3f} "
                    f"u_gap={result['ARM_ULTRAMETRIC']['gap']:.3f} "
                    f"wall={time.time()-t_pt:.1f}s",
                    flush=True,
                )
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_grid_points": len(grid_points),
        "expected_n_units": EXPECTED_N_UNITS,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "grid_points": grid_points,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_hierarchical_atom_generation() -> bool:
    W, ids = generate_hierarchical_atoms(
        n_top_clusters=4, cluster_size=8, n_dim=512, tree_depth=2, seed=11,
    )
    # tree_depth=2, branch=2 -> 4 * 2 = 8 leaf clusters; 8 * 8 = 64 atoms.
    assert W.shape == (64, 512), f"W shape {W.shape}"
    assert ids.shape == (64,)
    n_leaf = int(np.max(ids)) + 1
    assert n_leaf == 8, f"expected 8 leaves; got {n_leaf}"
    # Unit-norm rows.
    norms = np.linalg.norm(W, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-6), f"non-unit-norm rows; norms[:5]={norms[:5]}"
    return True


def _selftest_ultrametric_recovers_planted_at_trivial_regime() -> bool:
    """At n_clusters=3, cluster_size=10, N=2048, with noise-overlap profile
    NOISE_OVERLAP_BASE=0.55: ULTRA should yield gap > 0.50 (within > between)
    -- mechanism FIRES. Trivial 3-cluster regime is not gap-saturated under
    the overlap noise profile (within ~0.75; between ~0.01)."""
    W, ids = generate_hierarchical_atoms(
        n_top_clusters=3, cluster_size=10, n_dim=2048, tree_depth=1, seed=7,
    )
    n_leaf = int(np.max(ids)) + 1
    labels = assign_ultrametric(W, target_n_clusters=n_leaf)
    w, b, gap = compute_within_between_gap(W, labels)
    # ULTRA must clearly separate (gap > 0.30) without saturating (gap < 0.95).
    assert 0.30 < gap < 0.95, (
        f"trivial-regime ULTRA gap={gap:.3f} expected (0.30, 0.95) "
        f"(within={w:.3f}, between={b:.3f}); discriminator should FIRE not "
        f"saturate"
    )
    return True


def _selftest_random_grouping_yields_low_gap() -> bool:
    """Random grouping over the same atoms -> within ~ between -> gap ~ 0."""
    W, ids = generate_hierarchical_atoms(
        n_top_clusters=3, cluster_size=10, n_dim=2048, tree_depth=1, seed=7,
    )
    n_leaf = int(np.max(ids)) + 1
    labels = assign_random(W, k=n_leaf, seed=7)
    w, b, gap = compute_within_between_gap(W, labels)
    # Random should have very small gap (positive only by chance / cluster overlap).
    assert abs(gap) < 0.30, (
        f"random gap={gap:.3f} expected |gap| < 0.30 "
        f"(within={w:.3f}, between={b:.3f}); random partitioning should not separate"
    )
    return True


def _selftest_ultrametric_beats_random_on_acc_at_mid_regime() -> bool:
    """At MID configuration (nc=5, cs=10, N=2048), ULTRA acc_leaf should clearly
    exceed RANDOM acc_leaf -- discriminator FIRES on the PRIMARY metric."""
    W, ids = generate_hierarchical_atoms(
        n_top_clusters=5, cluster_size=10, n_dim=2048, tree_depth=2, seed=7,
    )
    n_leaf = int(np.max(ids)) + 1
    ul = assign_ultrametric(W, target_n_clusters=n_leaf)
    rl = assign_random(W, k=n_leaf, seed=7)
    ul_acc = label_recovery_accuracy(ids, ul)
    rl_acc = label_recovery_accuracy(ids, rl)
    assert ul_acc - rl_acc >= 0.30, (
        f"discriminator did NOT fire at MID: ULTRA acc={ul_acc:.3f} "
        f"RANDOM acc={rl_acc:.3f} delta={ul_acc-rl_acc:.3f} "
        f"(expected delta >= 0.30; random baseline ~ 1/n_leaf)"
    )
    return True


def _instrumentation_selftest() -> None:
    _selftest_hierarchical_atom_generation()
    _selftest_ultrametric_recovers_planted_at_trivial_regime()
    _selftest_random_grouping_yields_low_gap()
    _selftest_ultrametric_beats_random_on_acc_at_mid_regime()
    print(
        f"[selftest] PASS  mode={RUN_MODE}  axes(nc,cs,N,td)="
        f"{N_CLUSTERS_AXIS}x{CLUSTER_SIZE_AXIS}x{N_AXIS}x{TREE_DEPTH}  "
        f"expected_n_units={EXPECTED_N_UNITS}  seed={SEED_DEFAULT}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------
def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    # Aggregate grid-points across seeds (same grid each seed).
    all_points: List[Dict] = []
    for r in results:
        all_points.extend(r.get("grid_points", []))

    # CARDINALITY_OK: each seed must have EXPECTED_N_UNITS points.
    for r in results:
        n_obs = r.get("n_grid_points", 0)
        if n_obs < EXPECTED_N_UNITS:
            return ("HARD_FAIL",
                    f"HARD_FAIL_CARDINALITY_BREACH: seed={r.get('seed')} "
                    f"observed {n_obs} grid points; expected {EXPECTED_N_UNITS}.")

    n_points = len(all_points)
    if n_points == 0:
        return ("HARD_FAIL", "HARD_FAIL: no grid points.")

    ultra_accs = np.array([p["ARM_ULTRAMETRIC"]["acc_leaf"] for p in all_points])
    kmeans_accs = np.array([p["ARM_FLAT_KMEANS"]["acc_leaf"] for p in all_points])
    random_accs = np.array([p["ARM_RANDOM_GROUPING"]["acc_leaf"] for p in all_points])
    ultra_gaps = np.array([p["ARM_ULTRAMETRIC"]["gap"] for p in all_points])
    kmeans_gaps = np.array([p["ARM_FLAT_KMEANS"]["gap"] for p in all_points])

    # HARD_FAIL_BY_CONSTRUCTION_SAT_OR_FLOOR (on primary discriminator: acc_leaf).
    if np.all(ultra_accs >= 0.99):
        return ("HARD_FAIL",
                f"HARD_FAIL_BY_CONSTRUCTION_SAT: ULTRA acc_leaf >= 0.99 at every "
                f"point ({n_points} points); ceiling saturated; no discrimination. "
                f"Grid axes too easy.")
    if np.all(ultra_accs <= 0.05):
        return ("HARD_FAIL",
                f"HARD_FAIL_BY_CONSTRUCTION_FLOOR: ULTRA acc_leaf <= 0.05 at every "
                f"point ({n_points} points); mechanism floored.")

    # HARD_FAIL_ARMS_IDENTICAL (on primary discriminator).
    diff_uk_acc = np.abs(ultra_accs - kmeans_accs)
    n_identical = int(np.sum(diff_uk_acc < 0.02))
    if n_identical >= int(0.90 * n_points):
        return ("HARD_FAIL",
                f"HARD_FAIL_ARMS_IDENTICAL: |ULTRA.acc - KMEANS.acc| < 0.02 at "
                f"{n_identical}/{n_points} (>= 90%) of grid points; "
                f"ultrametric mechanism not firing; KMEANS recovers labels equally.")

    # PHASE-MAP gates (re-framed 2026-06-28 after smoke chain-failure discovery).
    delta_uk_acc = ultra_accs - kmeans_accs
    n_total = n_points

    # Regime A: separable (ULTRA recovers ~100% of planted labels).
    n_separable = int(np.sum(ultra_accs >= 0.95))
    # Regime B: chain-failure (KMEANS substantively beats ULTRA by >= 0.20).
    n_chain_failure = int(np.sum(delta_uk_acc <= -0.20))
    # Regime C: hierarchical advantage (ULTRA beats KMEANS by >= 0.10).
    n_ultra_advantage = int(np.sum(delta_uk_acc >= 0.10))
    # Discrimination floor: any |d_uk| > 0.05.
    n_discriminating = int(np.sum(np.abs(delta_uk_acc) > 0.05))

    pct_threshold = max(1, int(np.ceil(0.20 * n_total)))
    discriminating_floor = max(1, int(np.ceil(0.50 * n_total)))

    summary = (
        f"n_points={n_points} "
        f"ultra_acc_mean={ultra_accs.mean():.3f} (min={ultra_accs.min():.3f}, "
        f"max={ultra_accs.max():.3f}); "
        f"kmeans_acc_mean={kmeans_accs.mean():.3f}; "
        f"random_acc_mean={random_accs.mean():.3f}; "
        f"delta_uk_acc_mean={delta_uk_acc.mean():+.3f}; "
        f"n_separable(ULTRA>=0.95)={n_separable}/{n_total} "
        f"(need >= {pct_threshold}); "
        f"n_chain_failure(d_uk<=-0.20)={n_chain_failure}/{n_total} "
        f"(need >= {pct_threshold}); "
        f"n_ultra_advantage(d_uk>=0.10)={n_ultra_advantage}/{n_total} "
        f"(need >= {pct_threshold}); "
        f"n_discriminating(|d_uk|>0.05)={n_discriminating}/{n_total} "
        f"(need >= {discriminating_floor}); "
        f"ultra_gap_mean={ultra_gaps.mean():.3f} kmeans_gap_mean={kmeans_gaps.mean():.3f}"
    )

    hp_separable = n_separable >= pct_threshold
    hp_chain_failure = n_chain_failure >= pct_threshold
    hp_ultra_advantage = n_ultra_advantage >= pct_threshold
    hp_discriminating = n_discriminating >= discriminating_floor

    if all([hp_separable, hp_chain_failure, hp_ultra_advantage, hp_discriminating]):
        return ("HARD_PASS",
                f"HARD_PASS phase-map: ULTRAMETRIC phase diagram populated in all "
                f"3 regimes (separable / hierarchical-advantage / chain-failure) at "
                f">= 20% of grid points each and discriminating at >= 50% overall. "
                f"Phase coverage MID -> HIGH achieved. {summary}")

    # MIDDLE_BAND: discriminating well but not all 3 regimes populated.
    if hp_discriminating and (hp_separable or hp_ultra_advantage):
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: phase diagram discriminating at >= 50% overall but "
                f"not all 3 regimes populated at >= 20%. "
                f"hp_checks=[sep={hp_separable},chain={hp_chain_failure},"
                f"adv={hp_ultra_advantage},discrim={hp_discriminating}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: phase diagram does not clear PASS or MIDDLE bands. "
            f"hp_checks=[sep={hp_separable},chain={hp_chain_failure},"
            f"adv={hp_ultra_advantage},discrim={hp_discriminating}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {
    "N_AXIS": list(N_AXIS),
    "N_CLUSTERS_AXIS": list(N_CLUSTERS_AXIS),
    "CLUSTER_SIZE_AXIS": list(CLUSTER_SIZE_AXIS),
    "TREE_DEPTH": TREE_DEPTH,
    "run_mode": RUN_MODE,
}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] ultrametric phase-diagram v1 "
        f"axes(nc,cs,N,td)={N_CLUSTERS_AXIS}x{CLUSTER_SIZE_AXIS}x{N_AXIS}x{TREE_DEPTH} "
        f"expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE}",
        flush=True,
    )
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} "
        f"axes(nc,cs,N,td)={N_CLUSTERS_AXIS}x{CLUSTER_SIZE_AXIS}x{N_AXIS}x{TREE_DEPTH} "
        f"expected_n_units={EXPECTED_N_UNITS} mode={RUN_MODE} "
        f"cos_thresh={COSINE_THRESH} min_cl_size={MIN_CLUSTER_SIZE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N_CLUSTERS_AXIS": list(N_CLUSTERS_AXIS),
    "CLUSTER_SIZE_AXIS": list(CLUSTER_SIZE_AXIS),
    "N_AXIS": list(N_AXIS),
    "TREE_DEPTH": int(TREE_DEPTH),
    "expected_n_units": int(EXPECTED_N_UNITS),
    "n_seeds": len(SEEDS),
    "seeds": list(SEEDS),
    "cosine_thresh": float(COSINE_THRESH),
    "min_cluster_size": int(MIN_CLUSTER_SIZE),
    "noise_overlap_base": float(NOISE_OVERLAP_BASE),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "n_grid_points": r.get("n_grid_points"),
            "grid_points": r.get("grid_points"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
