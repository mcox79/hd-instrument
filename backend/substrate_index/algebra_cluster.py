"""Layer 3: algebra-cluster archaeology.

Per Research DEEP_SELF_EVALUATION_PROGRAM_ENDORSED 2026-06-11 priority 3:
clusters atoms by algebra_hrr / signature_hrr / semantic_vec / tier / family-tag
and surfaces atoms in the wrong cluster (mis-tag candidates).

Empirical 27-tag refactor input: substrate's own algebra-vec clustering may
disagree with Research's family-tag assignments; disagreements are candidate
refactor suggestions.

Strategic: substrate uses its own structure to propose refinements to that
same structure. Closes the self-improvement loop without LLM-as-judge.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from backend.substrate_index.algebra_index import AlgebraIndex
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, RelationType, Tier

logger = logging.getLogger(__name__)


# ============================================================
# Agglomerative clustering helper (pure numpy)
# ============================================================


def _agglomerative_cluster(
    matrix: np.ndarray,
    distance_threshold: float = 0.5,
) -> list[list[int]]:
    """Single-linkage agglomerative clustering on a vector matrix.

    Returns a list of clusters; each cluster is a list of row indices.

    distance_threshold: maximum cosine DISTANCE (1 - cosine_similarity) for
    two clusters to merge. Lower = tighter clusters.
    """
    n = matrix.shape[0]
    if n == 0:
        return []
    # Cosine similarity matrix (matrix already L2-normalized assumed)
    sim = matrix @ matrix.T
    dist = 1.0 - sim
    np.fill_diagonal(dist, np.inf)

    clusters: list[set[int]] = [{i} for i in range(n)]
    cluster_dist = dist.copy()

    while True:
        # Find min off-diagonal distance
        min_val = cluster_dist.min()
        if min_val > distance_threshold or np.isinf(min_val):
            break
        i, j = np.unravel_index(np.argmin(cluster_dist), cluster_dist.shape)
        if i == j:
            break
        # Merge cluster j into cluster i
        clusters[i] = clusters[i] | clusters[j]
        clusters[j] = set()
        # Update distance: single-linkage = min between any pair
        for k in range(len(clusters)):
            if k == i or not clusters[k]:
                continue
            d = min(dist[a, b] for a in clusters[i] for b in clusters[k])
            cluster_dist[i, k] = d
            cluster_dist[k, i] = d
        # Mark cluster j as gone
        cluster_dist[j, :] = np.inf
        cluster_dist[:, j] = np.inf

    return [sorted(list(c)) for c in clusters if c]


# ============================================================
# Layer 3 main analyses
# ============================================================


@dataclass(frozen=True)
class MisTagCandidate:
    """An atom that disagrees with its family-tag's algebra-cluster centroid."""
    atom_id: str
    name: str
    declared_family_tags: tuple[str, ...]
    algebra_cluster_id: int
    algebra_cluster_members: tuple[str, ...]
    inferred_family_candidate: Optional[str]
    confidence: float

    def to_dict(self) -> dict:
        return {
            "atom_id": self.atom_id,
            "name": self.name,
            "declared_family_tags": list(self.declared_family_tags),
            "algebra_cluster_id": self.algebra_cluster_id,
            "algebra_cluster_members": list(self.algebra_cluster_members),
            "inferred_family_candidate": self.inferred_family_candidate,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ClusterArchaeologyReport:
    """Full Layer 3 output."""
    n_atoms_clustered: int
    algebra_clusters: tuple[tuple[str, ...], ...]
    signature_clusters: tuple[tuple[str, ...], ...]
    mistag_candidates: tuple[MisTagCandidate, ...]
    cluster_to_family_overlap: dict   # algebra_cluster_id -> {family_tag: count}

    def to_dict(self) -> dict:
        return {
            "n_atoms_clustered": self.n_atoms_clustered,
            "algebra_clusters": [list(c) for c in self.algebra_clusters],
            "signature_clusters": [list(c) for c in self.signature_clusters],
            "mistag_candidates": [c.to_dict() for c in self.mistag_candidates],
            "cluster_to_family_overlap": {
                str(k): dict(v) for k, v in self.cluster_to_family_overlap.items()
            },
        }


def archaeology(
    pstore: PartitionedStore,
    algebra_index: AlgebraIndex,
    distance_threshold: float = 0.3,
) -> ClusterArchaeologyReport:
    """Run Layer 3 archaeology against current substrate state.

    Steps:
    1. Cluster atoms by algebra_hrr (substrate-internal algebra structure)
    2. Cluster atoms by signature_hrr (substrate-internal signature structure)
    3. Compare algebra clusters to declared family-tag membership
       - Atoms in same algebra cluster that share family-tag = consistent
       - Atoms in same algebra cluster that disagree on family-tag = mistag candidate
       - Atoms in different algebra clusters but same family-tag = family-tag too broad
    """
    # Gather atoms with algebra_hrr populated
    algebra_ids = []
    algebra_rows = []
    signature_ids = []
    signature_rows = []
    for atom_id, av in algebra_index._atom_vectors.items():
        if av.algebra_hrr is not None:
            algebra_ids.append(atom_id)
            algebra_rows.append(av.algebra_hrr)
        if av.signature_hrr is not None:
            signature_ids.append(atom_id)
            signature_rows.append(av.signature_hrr)

    if not algebra_rows:
        return ClusterArchaeologyReport(
            n_atoms_clustered=0,
            algebra_clusters=(),
            signature_clusters=(),
            mistag_candidates=(),
            cluster_to_family_overlap={},
        )

    algebra_mat = np.stack(algebra_rows)
    signature_mat = np.stack(signature_rows) if signature_rows else None

    # Cluster
    algebra_clusters_idx = _agglomerative_cluster(algebra_mat, distance_threshold)
    algebra_clusters = tuple(
        tuple(algebra_ids[i] for i in c) for c in algebra_clusters_idx
    )
    signature_clusters_idx = (
        _agglomerative_cluster(signature_mat, distance_threshold)
        if signature_mat is not None else []
    )
    signature_clusters = tuple(
        tuple(signature_ids[i] for i in c) for c in signature_clusters_idx
    )

    # Build atom_id -> family_tag membership lookup
    atom_family_tags: dict[str, list[str]] = {}
    # Track which atoms ARE family-tags (skip them from mistag detection;
    # a family-tag atom can't be a mistag candidate of itself or others)
    family_tag_atoms: set[str] = set()
    for atom in pstore.all_atoms():
        if atom.kind.value == "family_tag":
            family_tag_atoms.add(atom.qualified_id)
            members = atom.metadata.get("members") or atom.metadata.get("family_tag_members") or []
            for m in members:
                qid = m if "::" in m else f"{atom.corpus.value}::{m}"
                atom_family_tags.setdefault(qid, []).append(atom.qualified_id)

    # For each cluster, compute family-tag overlap
    cluster_to_family_overlap: dict[int, dict[str, int]] = {}
    for cid, cluster in enumerate(algebra_clusters):
        overlap: dict[str, int] = {}
        for aid in cluster:
            for ft in atom_family_tags.get(aid, []):
                overlap[ft] = overlap.get(ft, 0) + 1
        cluster_to_family_overlap[cid] = overlap

    # Surface mistag candidates: atom whose declared family-tag has < 50% of
    # its algebra-cluster co-members
    mistag_candidates: list[MisTagCandidate] = []
    for cid, cluster in enumerate(algebra_clusters):
        if len(cluster) < 2:
            continue
        majority_family = None
        majority_count = 0
        for ft, count in cluster_to_family_overlap[cid].items():
            if count > majority_count:
                majority_family = ft
                majority_count = count
        if majority_family is None:
            continue
        cluster_size = len(cluster)
        for aid in cluster:
            if aid in family_tag_atoms:
                # Self-reference guard: family-tag atoms are not mistag
                # candidates of themselves (caught in FINDINGS_06)
                continue
            declared = atom_family_tags.get(aid, [])
            if majority_family not in declared and majority_count > cluster_size // 2:
                atom = pstore.get_atom(aid)
                if atom is None:
                    continue
                mistag_candidates.append(MisTagCandidate(
                    atom_id=aid,
                    name=atom.name,
                    declared_family_tags=tuple(declared),
                    algebra_cluster_id=cid,
                    algebra_cluster_members=tuple(cluster),
                    inferred_family_candidate=majority_family,
                    confidence=round(majority_count / cluster_size, 2),
                ))

    return ClusterArchaeologyReport(
        n_atoms_clustered=len(algebra_ids),
        algebra_clusters=algebra_clusters,
        signature_clusters=signature_clusters,
        mistag_candidates=tuple(mistag_candidates),
        cluster_to_family_overlap=cluster_to_family_overlap,
    )


# ============================================================
# Cross-domain equivalence DISCOVERY
# ============================================================


@dataclass(frozen=True)
class EquivalenceCandidate:
    """Pair of atoms that may be EQUIVALENT_UNDER some transformation.

    Surfaced from: high algebra_hrr cosine + low semantic_vec cosine
    (algebra similar; descriptions diverge => candidate cross-domain pair).
    """
    atom_a: str
    atom_b: str
    algebra_sim: float
    semantic_sim: float
    divergence: float  # algebra_sim - semantic_sim; higher = more interesting
    existing_relation: Optional[str]  # if a relation already exists between them

    def to_dict(self) -> dict:
        return {
            "atom_a": self.atom_a,
            "atom_b": self.atom_b,
            "algebra_sim": round(self.algebra_sim, 3),
            "semantic_sim": round(self.semantic_sim, 3),
            "divergence": round(self.divergence, 3),
            "existing_relation": self.existing_relation,
        }


def discover_equivalence_candidates(
    pstore: PartitionedStore,
    algebra_index: AlgebraIndex,
    semantic_vectors: dict[str, np.ndarray],
    algebra_threshold: float = 0.5,
    semantic_threshold: float = 0.5,
    min_divergence: float = 0.2,
    top_k: int = 20,
) -> list[EquivalenceCandidate]:
    """Surface candidate EQUIVALENT_UNDER pairs from algebra-semantic divergence.

    Logic per FINDINGS_04: atoms with similar algebra but divergent semantic
    descriptions are candidates for cross-domain equivalence (e.g.,
    FHRR_bind FFT-dual circular_convolution: same algebra, different domain
    description).

    Args:
        algebra_threshold: minimum algebra cosine to consider pair
        semantic_threshold: maximum semantic cosine (we want LOW semantic)
        min_divergence: minimum algebra_sim - semantic_sim
        top_k: limit on returned candidates (sorted by divergence)

    Returns:
        list of EquivalenceCandidate sorted by divergence desc
    """
    # Build aligned matrices
    atom_ids = []
    alg_rows = []
    sem_rows = []
    for atom_id, av in algebra_index._atom_vectors.items():
        if av.algebra_hrr is None or atom_id not in semantic_vectors:
            continue
        atom_ids.append(atom_id)
        alg_rows.append(av.algebra_hrr)
        sem_rows.append(semantic_vectors[atom_id])
    if len(atom_ids) < 2:
        return []
    alg_mat = np.stack(alg_rows)
    sem_mat = np.stack(sem_rows)
    alg_sim = alg_mat @ alg_mat.T
    sem_sim = sem_mat @ sem_mat.T

    # Existing relations (any type) -> set of qualified-id pairs
    existing: dict[tuple[str, str], str] = {}
    for src, rt, tgt in pstore.iter_all_relations():
        existing[(src, tgt)] = rt.value
        existing[(tgt, src)] = rt.value  # symmetric for discovery

    n = len(atom_ids)
    candidates: list[EquivalenceCandidate] = []
    for i in range(n):
        for j in range(i + 1, n):
            a_sim = float(alg_sim[i, j])
            s_sim = float(sem_sim[i, j])
            div = a_sim - s_sim
            if a_sim < algebra_threshold:
                continue
            if s_sim > semantic_threshold:
                continue
            if div < min_divergence:
                continue
            candidates.append(EquivalenceCandidate(
                atom_a=atom_ids[i],
                atom_b=atom_ids[j],
                algebra_sim=a_sim,
                semantic_sim=s_sim,
                divergence=div,
                existing_relation=existing.get((atom_ids[i], atom_ids[j])),
            ))
    candidates.sort(key=lambda c: -c.divergence)
    return candidates[:top_k]
