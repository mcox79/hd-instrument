"""Reasoning over the substrate self-index.

Three reasoning modes:
1. Multi-hop traversal      : transitive closure over typed edges with depth cap
2. Pattern matching         : find atoms satisfying complex relation predicates
3. Substrate-algebraic      : leverage FHRR-style identity + rel-type binding for
                              'what does substrate think comes next' queries
                              (compared against typed-edge ground truth for
                              measuring algebraic vs structural agreement)

Per Research Refinement 3 design AGAINST rule 4 (unbounded self-reference):
all traversals are explicitly depth-bounded; default max_depth = 6.

This module operates over PartitionedStore (qualified ids) for cross-store
reasoning. Within-store reasoning can use relate.py functions on individual
stores.
"""
from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np

from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.retrieve import AtomCandidate, Retriever
from backend.substrate_index.schema import Corpus, RelationType, Tier

logger = logging.getLogger(__name__)


# ============================================================
# Multi-hop transitive reasoning
# ============================================================


@dataclass(frozen=True)
class HopResult:
    """One atom reachable via a multi-hop path from the seed."""
    atom_id: str
    hop_depth: int
    via_path: tuple[str, ...]              # qualified ids in the chain
    via_rels: tuple[RelationType, ...]      # parallel to via_path[1:]


def transitive_neighbors(
    pstore: PartitionedStore,
    seed_id: str,
    rel_type: RelationType,
    max_depth: int = 6,
    direction: str = "out",
) -> list[HopResult]:
    """All atoms reachable from seed via `rel_type` within max_depth hops.

    Returns HopResults sorted by depth then alphabetically. Useful for
    transitive USES queries like 'what does PP-364 transitively use'.
    """
    if not pstore.has_atom(seed_id):
        return []

    visited = {seed_id}
    results: list[HopResult] = []
    queue: deque = deque([(seed_id, [seed_id], [])])

    while queue:
        node, path, rels = queue.popleft()
        if len(path) > max_depth + 1:
            continue
        if direction == "out":
            neigh = pstore.out_neighbors(node, rel_type)
        else:
            neigh = pstore.in_neighbors(node, rel_type)
        for nxt in neigh:
            if nxt in visited:
                continue
            visited.add(nxt)
            new_path = path + [nxt]
            new_rels = rels + [rel_type]
            results.append(HopResult(
                atom_id=nxt,
                hop_depth=len(new_path) - 1,
                via_path=tuple(new_path),
                via_rels=tuple(new_rels),
            ))
            queue.append((nxt, new_path, new_rels))

    return sorted(results, key=lambda r: (r.hop_depth, r.atom_id))


# ============================================================
# Pattern matching
# ============================================================


@dataclass(frozen=True)
class AtomPredicate:
    """A predicate over atoms. Used by find_atoms_matching().

    All non-None fields are AND-combined. None means 'don't constrain'.
    Sets can be used for IN-style filters (any element matches).

    in_corpus              : restrict to this corpus
    in_tier                : restrict to this tier
    has_outgoing_to        : atom must have an outgoing edge to ANY of these qualified ids
    has_outgoing_rel_type  : atom must have at least one outgoing edge of this type
    has_outgoing_to_all    : atom must have outgoing edges to ALL of these (same rel_type)
    has_incoming_from      : atom must have an incoming edge from ANY of these qualified ids
    via_rel_type           : required relation type when combined with has_outgoing_to_all
    custom                 : arbitrary callable(qualified_id, pstore) -> bool
    """
    in_corpus: Optional[Corpus] = None
    in_tier: Optional[Tier] = None
    has_outgoing_to: Optional[set[str]] = None
    has_outgoing_rel_type: Optional[RelationType] = None
    has_outgoing_to_all: Optional[set[str]] = None
    has_incoming_from: Optional[set[str]] = None
    via_rel_type: Optional[RelationType] = None
    custom: Optional[Callable[[str, PartitionedStore], bool]] = None

    def matches(self, qualified_id: str, pstore: PartitionedStore) -> bool:
        atom = pstore.get_atom(qualified_id)
        if atom is None:
            return False
        if self.in_corpus is not None and atom.corpus != self.in_corpus:
            return False
        if self.in_tier is not None and atom.tier != self.in_tier:
            return False
        if self.has_outgoing_rel_type is not None:
            if not pstore.out_neighbors(qualified_id, self.has_outgoing_rel_type):
                return False
        if self.has_outgoing_to is not None:
            out_all = pstore.out_neighbors(qualified_id, self.via_rel_type)
            if not (out_all & self.has_outgoing_to):
                return False
        if self.has_outgoing_to_all is not None:
            out_all = pstore.out_neighbors(qualified_id, self.via_rel_type)
            if not self.has_outgoing_to_all.issubset(out_all):
                return False
        if self.has_incoming_from is not None:
            in_all = pstore.in_neighbors(qualified_id, self.via_rel_type)
            if not (in_all & self.has_incoming_from):
                return False
        if self.custom is not None and not self.custom(qualified_id, pstore):
            return False
        return True


def find_atoms_matching(
    pstore: PartitionedStore,
    predicate: AtomPredicate,
) -> list[str]:
    """Return all qualified atom ids matching the predicate.

    Use case from Research's pre-registered queries: 'find all T4 atoms whose
    USES set includes count-NB AND HMM Viterbi'.
    """
    matches = []
    for qid in pstore.all_qualified_ids():
        if predicate.matches(qid, pstore):
            matches.append(qid)
    return sorted(matches)


# ============================================================
# Substrate-algebraic reasoning
# ============================================================


@dataclass(frozen=True)
class AlgebraicAgreement:
    """How well substrate-algebraic prediction matches the typed-edge ground truth.

    For each (seed, rel_type) pair, the algebraic top-K candidates are compared
    against the structural neighbors. Agreement metrics:
      precision@k : fraction of algebraic top-K that ARE structural neighbors
      recall@k    : fraction of structural neighbors that are in algebraic top-K
      f1@k        : harmonic mean
    Aggregate these across many (seed, rel_type) pairs to get a system-level
    measure of substrate's algebraic self-reasoning quality.
    """
    seed_id: str
    rel_type: RelationType
    algebraic_top_k: tuple[str, ...]
    structural_neighbors: tuple[str, ...]
    precision_at_k: float
    recall_at_k: float
    f1_at_k: float


def algebraic_agreement(
    pstore: PartitionedStore,
    retriever: Retriever,
    seed_id: str,
    rel_type: RelationType,
    k: int = 5,
) -> AlgebraicAgreement:
    """Compute algebraic-vs-structural agreement for one (seed, rel_type) pair.

    Substrate-algebraic prediction (retriever.algebraic) is the 'what does
    substrate think comes next when you bind seed_id with rel_type' answer.
    Structural neighbors are the ground truth typed-edge targets.

    A high agreement score across many seeds/relations means substrate's
    pure-algebraic intuition matches its stored relations -- a precondition
    for trusting algebraic queries when structural lookup is unavailable.
    """
    algebraic_cands = retriever.algebraic(seed_id, rel_type, top_k=k)
    algebraic_ids = [c.atom_id for c in algebraic_cands]
    # Structural neighbors: out direction by convention for algebraic-style query
    structural = pstore.out_neighbors(seed_id, rel_type)

    if not algebraic_ids and not structural:
        # Vacuous; both empty
        return AlgebraicAgreement(
            seed_id=seed_id, rel_type=rel_type,
            algebraic_top_k=(), structural_neighbors=(),
            precision_at_k=1.0, recall_at_k=1.0, f1_at_k=1.0,
        )

    alg_set = set(algebraic_ids)
    str_set = set(structural)
    intersection = alg_set & str_set
    precision = len(intersection) / max(1, len(alg_set))
    recall = len(intersection) / max(1, len(str_set))
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return AlgebraicAgreement(
        seed_id=seed_id,
        rel_type=rel_type,
        algebraic_top_k=tuple(algebraic_ids),
        structural_neighbors=tuple(sorted(structural)),
        precision_at_k=round(precision, 3),
        recall_at_k=round(recall, 3),
        f1_at_k=round(f1, 3),
    )


def system_algebraic_agreement(
    pstore: PartitionedStore,
    retriever: Retriever,
    rel_type: RelationType,
    k: int = 5,
    sample_size: Optional[int] = None,
) -> dict:
    """Aggregate algebraic agreement across all atoms for a given rel_type.

    Returns macro-averaged precision / recall / f1 over the sampled seeds.
    """
    seeds = sorted(pstore.all_qualified_ids())
    if sample_size is not None and sample_size < len(seeds):
        import random
        seeds = random.sample(seeds, sample_size)
    if not seeds:
        return {"n": 0, "mean_precision": 0.0, "mean_recall": 0.0, "mean_f1": 0.0}
    ps, rs, fs = [], [], []
    for seed in seeds:
        a = algebraic_agreement(pstore, retriever, seed, rel_type, k=k)
        ps.append(a.precision_at_k)
        rs.append(a.recall_at_k)
        fs.append(a.f1_at_k)
    n = len(seeds)
    return {
        "n": n,
        "rel_type": rel_type.value,
        "k": k,
        "mean_precision": round(sum(ps) / n, 3),
        "mean_recall": round(sum(rs) / n, 3),
        "mean_f1": round(sum(fs) / n, 3),
    }


# ============================================================
# Combined reasoning: structural + semantic + algebraic for one query
# ============================================================


@dataclass(frozen=True)
class ReasonedAnswer:
    """A reasoned answer combining all three modes."""
    seed_id: str
    rel_type: Optional[RelationType]
    structural_neighbors: tuple[str, ...]
    semantic_top_k: tuple[str, ...]
    algebraic_top_k: tuple[str, ...]
    consensus: tuple[str, ...]              # atoms agreed on by all three modes
    disagreement: dict                     # what each mode found uniquely


def reason(
    pstore: PartitionedStore,
    retriever: Retriever,
    seed_id: str,
    rel_type: Optional[RelationType] = None,
    semantic_text: Optional[str] = None,
    k: int = 5,
) -> ReasonedAnswer:
    """Run all three reasoning modes for one query and report consensus + disagreement.

    The 'consensus' set is the strongest signal -- atoms that all three modes
    agree on -- and is the recommended answer. Disagreement highlights gaps:
    - semantic-only: substrate description-similar but not structurally related
    - structural-only: stored relation but not semantic-similar (potential
      misencoded atom)
    - algebraic-only: substrate's algebra suggests a connection that isn't stored
      (possible gap to add as a real relation)
    """
    structural = set()
    if rel_type is not None:
        structural = pstore.out_neighbors(seed_id, rel_type)

    semantic_ids = []
    if semantic_text is not None:
        sem_cands = retriever.semantic(semantic_text, top_k=k)
        semantic_ids = [c.atom_id for c in sem_cands if c.atom_id != seed_id]

    algebraic_ids = []
    if rel_type is not None:
        alg_cands = retriever.algebraic(seed_id, rel_type, top_k=k)
        algebraic_ids = [c.atom_id for c in alg_cands]

    str_set = set(structural)
    sem_set = set(semantic_ids)
    alg_set = set(algebraic_ids)

    consensus = str_set & sem_set & alg_set if (str_set and sem_set and alg_set) else (
        (str_set & sem_set) or (str_set & alg_set) or (sem_set & alg_set)
    )

    disagreement = {
        "structural_only": sorted(str_set - sem_set - alg_set),
        "semantic_only": sorted(sem_set - str_set - alg_set),
        "algebraic_only": sorted(alg_set - str_set - sem_set),
    }

    return ReasonedAnswer(
        seed_id=seed_id,
        rel_type=rel_type,
        structural_neighbors=tuple(sorted(structural)),
        semantic_top_k=tuple(semantic_ids),
        algebraic_top_k=tuple(algebraic_ids),
        consensus=tuple(sorted(consensus)),
        disagreement=disagreement,
    )
