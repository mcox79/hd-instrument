"""Per-cluster density measurement helper for Phase-2-light substrate-guided
proposal tool (Cycle 50 Research direction).

Provides:
- cluster_atom_counts(pstore): dict {cluster_id -> n_atoms}
- cluster_centroids(pstore, ai): dict {cluster_id -> centroid_vector (composite_hrr space)}
- cluster_for_atom(qid, ai, pstore): int (cluster_id)
- nearest_cluster_with_density(candidate_vec, ai, pstore): (cluster_id, density, distance_to_centroid)

Used by Phase-2-light Component 3 (hybrid-encoder cluster-novelty filter):
- High-density existing cluster (>30 atoms) + low novelty -> SKIP (saturation; distractor density risk)
- Low-density cluster (<10 atoms) + low novelty -> PROPOSE as UPDATE
- High novelty -> PROPOSE as CREATE
"""
from __future__ import annotations
from typing import Optional
from collections import defaultdict

import numpy as np


def cluster_for_atom(atom) -> Optional[int]:
    """Return cluster_id (category_int from algebra dict) or None."""
    alg = atom.algebra or {}
    cat = alg.get("category_int")
    if cat is None:
        return None
    try:
        return int(cat)
    except (ValueError, TypeError):
        return None


def cluster_atom_counts(pstore) -> dict[int, int]:
    """Per-cluster atom count (category_int -> n_atoms with that category)."""
    counts: dict[int, int] = defaultdict(int)
    for a in pstore.all_atoms():
        c = cluster_for_atom(a)
        if c is not None:
            counts[c] += 1
    return dict(counts)


def cluster_centroids(pstore, ai, vector_mode: str = "structural") -> dict[int, np.ndarray]:
    """Per-cluster centroid vector (mean of cluster atoms' algebra/composite HRR).

    vector_mode='structural' (algebra_hrr; collisions desirable) is the natural
    choice for cluster-novelty filtering because clusters ARE defined by algebra.
    vector_mode='identity' (composite_hrr) gives a slightly different per-cluster
    centroid that reflects per-atom identity within cluster.
    """
    by_cat: dict[int, list[np.ndarray]] = defaultdict(list)
    for a in pstore.all_atoms():
        c = cluster_for_atom(a)
        if c is None:
            continue
        av = ai._atom_vectors.get(a.qualified_id)
        if av is None:
            continue
        v = av.algebra_hrr if vector_mode == "structural" else av.composite_hrr
        if v is None:
            continue
        by_cat[c].append(v)
    centroids: dict[int, np.ndarray] = {}
    for c, vecs in by_cat.items():
        m = np.mean(np.stack(vecs), axis=0)
        n = np.linalg.norm(m)
        centroids[c] = m / (n + 1e-12)
    return centroids


def nearest_cluster_with_density(
    candidate_vec: np.ndarray,
    pstore,
    ai,
    vector_mode: str = "structural",
) -> tuple[Optional[int], int, float]:
    """For a candidate atom vector, find the nearest cluster + report its density.

    Returns (cluster_id, n_atoms_in_cluster, cosine_to_centroid).
    cluster_id is None if no clusters exist; n_atoms=0 + cosine=0 in that case.
    """
    centroids = cluster_centroids(pstore, ai, vector_mode)
    if not centroids:
        return None, 0, 0.0
    counts = cluster_atom_counts(pstore)
    n_cand = np.linalg.norm(candidate_vec)
    cand_unit = candidate_vec / (n_cand + 1e-12) if n_cand > 0 else candidate_vec
    best_cid = None
    best_sim = -1.0
    for c, centroid in centroids.items():
        s = float(cand_unit @ centroid)
        if s > best_sim:
            best_sim = s
            best_cid = c
    density = counts.get(best_cid, 0) if best_cid is not None else 0
    return best_cid, density, best_sim


def proposal_route(
    candidate_vec: np.ndarray,
    pstore,
    ai,
    high_density_threshold: int = 30,
    low_density_threshold: int = 10,
    novelty_threshold: float = 0.30,
) -> dict:
    """Phase-2-light Component 3 routing decision for a candidate atom.

    Returns dict with route in {'SKIP', 'UPDATE', 'CREATE', 'SHARES_MATH_MULTI'}
    + nearest cluster info + density signal.
    """
    cluster_id, density, similarity = nearest_cluster_with_density(
        candidate_vec, pstore, ai, vector_mode="structural"
    )
    # novelty = 1 - similarity (cosine in [-1, 1] but typically [0, 1] for HRR atoms)
    novelty = 1.0 - max(similarity, 0.0)

    # Cross-cluster connectivity: find all clusters with similarity above threshold
    centroids = cluster_centroids(pstore, ai, vector_mode="structural")
    n_cand = np.linalg.norm(candidate_vec)
    cand_unit = candidate_vec / (n_cand + 1e-12) if n_cand > 0 else candidate_vec
    multi_clusters = []
    for cid, c_vec in centroids.items():
        s = float(cand_unit @ c_vec)
        if s >= 0.50:  # threshold for "fits in this cluster too"
            multi_clusters.append((cid, s))

    decision: dict = {
        "nearest_cluster": cluster_id,
        "nearest_density": density,
        "nearest_similarity": similarity,
        "novelty": novelty,
        "multi_cluster_membership": multi_clusters,
    }

    if len(multi_clusters) >= 2:
        decision["route"] = "SHARES_MATH_MULTI"
        decision["reason"] = f"candidate in {len(multi_clusters)} cluster centroids; SHARES_MATH edge candidates"
    elif density >= high_density_threshold and novelty < novelty_threshold:
        decision["route"] = "SKIP"
        decision["reason"] = f"cluster {cluster_id} density {density} saturated (>{high_density_threshold}); novelty {novelty:.2f} below threshold"
    elif density < low_density_threshold and novelty < novelty_threshold:
        decision["route"] = "UPDATE"
        decision["reason"] = f"cluster {cluster_id} sparse ({density} atoms); proposing UPDATE to nearest atom"
    elif novelty >= novelty_threshold:
        decision["route"] = "CREATE"
        decision["reason"] = f"novelty {novelty:.2f} above threshold; new-cluster CREATE candidate"
    else:
        decision["route"] = "PROPOSE"
        decision["reason"] = f"cluster {cluster_id} mid-density {density}; CREATE default"

    return decision
