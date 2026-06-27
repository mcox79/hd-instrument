"""Substrate-native ultrametric clustering / coarse-graining of atoms.

Collapse high-cosine atom clusters into representative + residual codes via
ultrametric distance on W rows (single-linkage agglomerative). Substrate-native
RG coarse-graining = the missing COMPOSITIONAL ABSTRACTION primitive.

Brain analog: schema-fast-track / Tse-Morris consolidated clusters; brain
shifts from per-instance encoding to schema-level recall after consolidation.

Math analog: ultrametric distance from spin-glass theory (Mehta-Schwab
variational RG); metastable basin hierarchy.

Mechanism (NumPy; no torch dependency):
  D[i,j] = 1 - cosine(W[i], W[j])
  ultrametric_distance via single-linkage agglomerative clustering
  cluster_assign by threshold (within-cluster cosine >= cosine_thresh AND
                                size >= min_cluster_size)
  representative = mean (centroid) of cluster atoms' W rows
  residual code = atom's deviation from centroid (1-of-K identity tag)

ASCII-only. No emojis. No em-dashes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass(frozen=True)
class UltrametricConfig:
    """Ultrametric clustering hyperparameters.

    cosine_thresh: within-cluster cosine floor (default 0.85 = USER spec).
    min_cluster_size: minimum atoms-per-cluster (default 5 = USER spec).
    representative_mode: 'centroid' (default; mean of cluster) or 'first' (lowest
                        index in cluster; deterministic).
    """
    cosine_thresh: float = 0.85
    min_cluster_size: int = 5
    representative_mode: str = "centroid"


def cosine_distance_matrix(W: np.ndarray) -> np.ndarray:
    """Pairwise cosine distance D[i,j] = 1 - cos(W[i], W[j]).

    W: shape (n_atoms, n_dim). Returns symmetric matrix (n_atoms, n_atoms).
    """
    if W.ndim != 2:
        raise ValueError(f"W must be 2D; got shape {W.shape}")
    norms = np.linalg.norm(W, axis=1, keepdims=True)
    norms = np.where(norms > 1e-12, norms, 1.0)
    Wn = W / norms
    cos_sim = Wn @ Wn.T
    cos_sim = np.clip(cos_sim, -1.0, 1.0)
    return 1.0 - cos_sim


def single_linkage_clusters(D: np.ndarray, max_distance: float) -> List[List[int]]:
    """Single-linkage agglomerative clustering at max_distance threshold.

    Returns list of clusters (each cluster = list of atom indices).
    Uses union-find for O(n^2 log n).
    """
    n = D.shape[0]
    if D.shape[0] != D.shape[1]:
        raise ValueError(f"D must be square; got {D.shape}")
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # Single-linkage: union any pair within max_distance.
    iu = np.triu_indices(n, k=1)
    pairs = list(zip(iu[0].tolist(), iu[1].tolist(), D[iu].tolist()))
    pairs.sort(key=lambda t: t[2])
    for i, j, d in pairs:
        if d > max_distance:
            break
        union(i, j)

    clusters_map: dict[int, list[int]] = {}
    for idx in range(n):
        root = find(idx)
        clusters_map.setdefault(root, []).append(idx)
    return list(clusters_map.values())


def filter_qualifying_clusters(
    clusters: List[List[int]],
    W: np.ndarray,
    cfg: UltrametricConfig,
) -> List[List[int]]:
    """Keep clusters meeting BOTH:
      (1) size >= min_cluster_size
      (2) min within-cluster cosine >= cosine_thresh
    """
    qualifying = []
    for cl in clusters:
        if len(cl) < cfg.min_cluster_size:
            continue
        sub = W[cl]
        norms = np.linalg.norm(sub, axis=1, keepdims=True)
        norms = np.where(norms > 1e-12, norms, 1.0)
        subn = sub / norms
        cos_mat = subn @ subn.T
        # Diagonal is 1.0; minimum off-diagonal is the limiting within-cluster cosine.
        np.fill_diagonal(cos_mat, np.inf)
        min_cos = float(np.min(cos_mat))
        if min_cos < cfg.cosine_thresh:
            continue
        qualifying.append(cl)
    return qualifying


def compute_representatives(
    clusters: List[List[int]],
    W: np.ndarray,
    cfg: UltrametricConfig,
) -> np.ndarray:
    """Return shape (n_clusters, n_dim) matrix of representative vectors."""
    reps = np.zeros((len(clusters), W.shape[1]), dtype=W.dtype)
    for ci, cl in enumerate(clusters):
        if cfg.representative_mode == "centroid":
            reps[ci] = np.mean(W[cl], axis=0)
        elif cfg.representative_mode == "first":
            reps[ci] = W[cl[0]]
        else:
            raise ValueError(f"unknown representative_mode {cfg.representative_mode}")
    return reps


def cluster_atom_lookup(clusters: List[List[int]], n_atoms: int) -> np.ndarray:
    """Per-atom cluster_id (-1 = unclustered)."""
    lookup = np.full(n_atoms, -1, dtype=np.int64)
    for ci, cl in enumerate(clusters):
        for a in cl:
            lookup[a] = ci
    return lookup


def collapse_W_via_clusters(
    W: np.ndarray,
    clusters: List[List[int]],
    cfg: UltrametricConfig,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Collapse W: clustered atoms replaced by their cluster representative;
    unclustered atoms unchanged.

    Returns:
      W_collapsed:    shape (n_atoms, n_dim) -- clustered atoms set to representative
      reps:           shape (n_clusters, n_dim) -- representatives
      cluster_lookup: shape (n_atoms,) -- cluster_id per atom, -1 if unclustered

    capacity_drop = number of clustered atoms - number of clusters (the COMPRESSION
    saved: K atoms collapse to 1 representative + (K-1) freed slots).
    """
    reps = compute_representatives(clusters, W, cfg)
    cluster_lookup = cluster_atom_lookup(clusters, W.shape[0])
    W_collapsed = W.copy()
    for ci, cl in enumerate(clusters):
        for a in cl:
            W_collapsed[a] = reps[ci]
    return W_collapsed, reps, cluster_lookup


def effective_capacity_used(cluster_lookup: np.ndarray) -> int:
    """Effective capacity = unique slots used = (unclustered atom count) +
    (number of distinct clusters)."""
    n_unclustered = int(np.sum(cluster_lookup == -1))
    n_clusters = int(len(np.unique(cluster_lookup[cluster_lookup >= 0])))
    return n_unclustered + n_clusters


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_cosine_distance_matrix() -> bool:
    W = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    D = cosine_distance_matrix(W)
    assert D.shape == (3, 3)
    assert abs(D[0, 1]) < 1e-9, f"identical rows D[0,1]={D[0,1]}"
    assert abs(D[0, 2] - 1.0) < 1e-9, f"orthogonal D[0,2]={D[0,2]}"
    return True


def _selftest_single_linkage_synthetic() -> bool:
    """Construct 50 atoms in 5 known clusters of 10; verify clustering recovers."""
    rng = np.random.RandomState(0)
    n_clusters_true = 5
    cluster_size = 10
    dim = 256  # higher dim -> random noise more orthogonal -> cleaner clusters
    # Cluster centers (random unit vectors; nearly orthogonal at dim=256).
    centers = rng.randn(n_clusters_true, dim)
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)
    # Atoms = center + small noise. Noise scale 0.02 at dim=256 -> within-cluster
    # cosine ~ 0.999 (sqrt(dim*noise^2) << 1).
    atoms = []
    for ci in range(n_clusters_true):
        for _ in range(cluster_size):
            atom = centers[ci] + 0.02 * rng.randn(dim)
            atom /= np.linalg.norm(atom)
            atoms.append(atom)
    W = np.array(atoms)
    D = cosine_distance_matrix(W)
    # Cluster at distance threshold 0.10 (cosine 0.90).
    clusters = single_linkage_clusters(D, max_distance=0.10)
    # Expect at least n_clusters_true clusters of size>=cluster_size.
    big_clusters = [c for c in clusters if len(c) >= cluster_size]
    assert len(big_clusters) == n_clusters_true, (
        f"expected {n_clusters_true} clusters of size >= {cluster_size}; "
        f"got {len(big_clusters)} (all clusters: sizes={[len(c) for c in clusters]})"
    )
    return True


def _selftest_filter_qualifying() -> bool:
    """Cluster size + cosine threshold filtering."""
    rng = np.random.RandomState(42)
    cfg = UltrametricConfig(cosine_thresh=0.85, min_cluster_size=5)
    # 7 atoms with high mutual cosine; 3 atoms isolated.
    dim = 256
    base = rng.randn(dim)
    base /= np.linalg.norm(base)
    cluster_atoms = []
    for _ in range(7):
        a = base + 0.02 * rng.randn(dim)
        a /= np.linalg.norm(a)
        cluster_atoms.append(a)
    isolated = [rng.randn(dim) / np.linalg.norm(rng.randn(dim)) for _ in range(3)]
    W = np.array(cluster_atoms + isolated)
    D = cosine_distance_matrix(W)
    clusters = single_linkage_clusters(D, max_distance=0.10)
    qualifying = filter_qualifying_clusters(clusters, W, cfg)
    assert len(qualifying) == 1, f"expected 1 qualifying cluster; got {len(qualifying)}"
    assert len(qualifying[0]) == 7, f"expected cluster of 7; got {len(qualifying[0])}"
    return True


def _selftest_collapse_capacity_drop() -> bool:
    """Verify collapse: 50 atoms in 5 clusters of 10 -> effective capacity 5
    (with no unclustered). Capacity drop = 50-5 = 45 atoms freed."""
    rng = np.random.RandomState(7)
    cfg = UltrametricConfig(cosine_thresh=0.85, min_cluster_size=5)
    n_clusters_true = 5
    cluster_size = 10
    dim = 256
    centers = rng.randn(n_clusters_true, dim)
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)
    atoms = []
    for ci in range(n_clusters_true):
        for _ in range(cluster_size):
            atom = centers[ci] + 0.02 * rng.randn(dim)
            atom /= np.linalg.norm(atom)
            atoms.append(atom)
    W = np.array(atoms)
    D = cosine_distance_matrix(W)
    clusters = single_linkage_clusters(D, max_distance=0.10)
    qualifying = filter_qualifying_clusters(clusters, W, cfg)
    W_col, reps, lookup = collapse_W_via_clusters(W, qualifying, cfg)
    assert reps.shape == (5, dim)
    eff_cap = effective_capacity_used(lookup)
    assert eff_cap == 5, f"effective capacity 5 expected; got {eff_cap}"
    # All atoms within cluster point to same row in W_col (their cluster rep).
    for ci, cl in enumerate(qualifying):
        for a in cl:
            assert np.allclose(W_col[a], reps[ci])
    return True


def _selftest_no_clusters_when_orthogonal() -> bool:
    """Atoms with random independent unit vectors should NOT cluster at
    cos >= 0.85."""
    rng = np.random.RandomState(11)
    cfg = UltrametricConfig(cosine_thresh=0.85, min_cluster_size=5)
    n = 30
    dim = 256
    W = rng.randn(n, dim)
    W /= np.linalg.norm(W, axis=1, keepdims=True)
    D = cosine_distance_matrix(W)
    clusters = single_linkage_clusters(D, max_distance=0.15)
    qualifying = filter_qualifying_clusters(clusters, W, cfg)
    assert len(qualifying) == 0, f"expected 0 qualifying clusters in random; got {len(qualifying)}"
    return True


def _selftest() -> None:
    _selftest_cosine_distance_matrix()
    _selftest_single_linkage_synthetic()
    _selftest_filter_qualifying()
    _selftest_collapse_capacity_drop()
    _selftest_no_clusters_when_orthogonal()
    print("[ultrametric_clustering selftest] PASS  cosD+SL+filter+collapse+null", flush=True)


if __name__ == "__main__":
    _selftest()
