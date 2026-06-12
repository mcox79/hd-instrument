"""Sparse-neighborhood-first ranking infrastructure for Phase-2-light
substrate-guided proposal tool (Cycle 50 Research direction).

Per strategy_request_to_research v586 specification hint:
> Rank candidate-atom-author prompts by ascending density of the nearest existing
> cluster (sparse-neighborhood-first authoring).
> Reject candidate atoms whose nearest-cluster density exceeds a threshold
> (empirically calibrated against batch-2 vs Cycle 49 contrast).

This module provides:
- rank_candidates_sparse_first(candidates, pstore, ai): list[CandidateRank]
- density_weighted_score(candidate_vec, pstore, ai): float (lower density = higher score)

Used by Phase-2-light Component 4 (Z-counts curriculum-difficulty ranker, modified
to also incorporate cluster-density signal).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .cluster_density import (
    cluster_atom_counts,
    cluster_centroids,
    nearest_cluster_with_density,
    proposal_route,
)


@dataclass
class CandidateRank:
    candidate_id: str
    candidate_vec: np.ndarray
    nearest_cluster: Optional[int]
    nearest_density: int
    nearest_similarity: float
    novelty: float
    route: str
    rank_score: float


def density_weighted_score(
    candidate_vec: np.ndarray,
    pstore,
    ai,
    novelty_weight: float = 0.7,
    sparse_weight: float = 0.3,
    high_density_penalty: int = 30,
) -> float:
    """Composite score = novelty_weight * novelty + sparse_weight * (1 - density/max_density).

    Higher score = more interesting candidate (novel OR fills sparse cluster).
    Atoms whose nearest cluster has density >= high_density_penalty get sparse_weight
    component = 0 (no bonus for joining saturated cluster).

    Returns float in [0, 1].
    """
    cid, density, sim = nearest_cluster_with_density(candidate_vec, pstore, ai)
    novelty = 1.0 - max(sim, 0.0)
    counts = cluster_atom_counts(pstore)
    max_density = max(counts.values()) if counts else 1
    if density >= high_density_penalty:
        sparse_component = 0.0
    else:
        sparse_component = 1.0 - (density / max_density)
    return novelty_weight * novelty + sparse_weight * sparse_component


def rank_candidates_sparse_first(
    candidates: list[tuple[str, np.ndarray]],
    pstore,
    ai,
    novelty_weight: float = 0.7,
    sparse_weight: float = 0.3,
    high_density_penalty: int = 30,
) -> list[CandidateRank]:
    """Rank candidates with sparse-neighborhood-first priority.

    Args:
        candidates: list of (candidate_id, candidate_vec) pairs from Phase-2-light
            Components 1-2 (atom-gap extraction + distant supervision seed).
        pstore + ai: substrate state to compute density/novelty against.

    Returns:
        list of CandidateRank sorted by rank_score descending (highest first;
        sparse-neighborhood-first means high novelty + low cluster density wins).
    """
    results = []
    for cid_str, vec in candidates:
        cid, density, sim = nearest_cluster_with_density(vec, pstore, ai)
        novelty = 1.0 - max(sim, 0.0)
        route = proposal_route(vec, pstore, ai,
                                high_density_threshold=high_density_penalty)
        score = density_weighted_score(vec, pstore, ai,
                                        novelty_weight, sparse_weight, high_density_penalty)
        results.append(CandidateRank(
            candidate_id=cid_str,
            candidate_vec=vec,
            nearest_cluster=cid,
            nearest_density=density,
            nearest_similarity=sim,
            novelty=novelty,
            route=route["route"],
            rank_score=score,
        ))
    results.sort(key=lambda r: -r.rank_score)
    return results
