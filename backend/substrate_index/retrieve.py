"""Retrieval interface for substrate self-index.

Three primary query modes:
1. semantic(text)              - bge similarity over all atom semantic vectors
2. structural(atom_id, rel)    - typed-edge neighbors lookup
3. hybrid(text, filters)       - semantic retrieval with corpus/tier/relation filters

All return ranked AtomCandidate lists with scores. Latency is sub-ms after warmup
since substrate state is in memory.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from backend.substrate_index.encode import AtomEncoder, AtomVectors
from backend.substrate_index.schema import (
    Atom,
    Corpus,
    QueryResult,
    RelationType,
    Tier,
)
from backend.substrate_index.store import Store

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AtomCandidate:
    """One atom returned from retrieval with its score + provenance."""
    atom_id: str
    score: float           # similarity in [0, 1] or rank-derived score
    via: str = "semantic"  # "semantic" / "structural:<rel_type>" / "hybrid"


class Retriever:
    """Composed retrieval over store + encoder.

    Holds in-memory vector matrices (semantic + composite) for vectorized
    cosine retrieval. Re-encode on Store updates is the caller's job; call
    rebuild_index() after add/remove batches.
    """

    def __init__(self, store: Store, encoder: AtomEncoder):
        self.store = store
        self.encoder = encoder
        self._vectors: dict[str, AtomVectors] = {}
        self._semantic_matrix: Optional[np.ndarray] = None
        self._composite_matrix: Optional[np.ndarray] = None
        self._id_order: list[str] = []

    # ------------------------------------------------------------
    # Index build / rebuild
    # ------------------------------------------------------------

    def rebuild_index(self) -> None:
        """Re-encode all atoms in the store and rebuild matrices."""
        atoms = self.store.all_atoms()
        if not atoms:
            self._vectors = {}
            self._semantic_matrix = None
            self._composite_matrix = None
            self._id_order = []
            return
        self._vectors = self.encoder.encode_atoms(atoms)
        self._id_order = [a.id for a in atoms]
        n = len(atoms)
        dim = self.encoder.dim
        sm = np.zeros((n, dim), dtype=np.float32)
        cm = np.zeros((n, dim), dtype=np.float32)
        for i, aid in enumerate(self._id_order):
            sm[i] = self._vectors[aid].semantic
            cm[i] = self._vectors[aid].composite
        self._semantic_matrix = sm
        self._composite_matrix = cm
        logger.info("retriever index built: %d atoms", n)

    def get_vectors(self, atom_id: str) -> Optional[AtomVectors]:
        return self._vectors.get(atom_id)

    # ------------------------------------------------------------
    # Semantic retrieval
    # ------------------------------------------------------------

    def semantic(
        self,
        text: str,
        top_k: int = 10,
        corpus_filter: Optional[Corpus] = None,
        tier_filter: Optional[Tier] = None,
        use_composite: bool = True,
    ) -> list[AtomCandidate]:
        """Bge similarity retrieval. Optional corpus or tier filter.

        use_composite=True uses the composite vector (which includes tier+corpus
        tag bindings); False uses the pure semantic vector. Composite is preferred
        when the query mentions tier/corpus context; pure semantic is preferred
        for plain language descriptions.
        """
        if self._semantic_matrix is None:
            return []
        q = self.encoder.encode_query_text(text)
        matrix = self._composite_matrix if use_composite else self._semantic_matrix
        scores = matrix @ q  # cosine since both L2-normalized

        # Apply filters
        keep = np.ones(len(self._id_order), dtype=bool)
        if corpus_filter is not None or tier_filter is not None:
            for i, aid in enumerate(self._id_order):
                a = self.store.get_atom(aid)
                if corpus_filter is not None and a.corpus != corpus_filter:
                    keep[i] = False
                if tier_filter is not None and a.tier != tier_filter:
                    keep[i] = False
            scores = np.where(keep, scores, -1.0)

        order = np.argsort(-scores)[:top_k]
        return [
            AtomCandidate(
                atom_id=self._id_order[i],
                score=float(scores[i]),
                via="semantic",
            )
            for i in order
            if scores[i] > -1.0
        ]

    # ------------------------------------------------------------
    # Structural retrieval
    # ------------------------------------------------------------

    def structural(
        self,
        atom_id: str,
        rel_type: Optional[RelationType] = None,
        direction: str = "out",
    ) -> list[AtomCandidate]:
        """Typed-edge neighbors of atom_id.

        direction = "out" -> atoms reachable from atom_id via rel_type
        direction = "in"  -> atoms reaching atom_id via rel_type
        rel_type = None   -> any relation type
        """
        if direction == "out":
            neighbors = self.store.out_neighbors(atom_id, rel_type)
        elif direction == "in":
            neighbors = self.store.in_neighbors(atom_id, rel_type)
        else:
            raise ValueError(f"direction must be 'in' or 'out', got {direction}")
        via = f"structural:{rel_type.value if rel_type else 'any'}:{direction}"
        return [AtomCandidate(atom_id=n, score=1.0, via=via) for n in sorted(neighbors)]

    # ------------------------------------------------------------
    # Hybrid retrieval
    # ------------------------------------------------------------

    def hybrid(
        self,
        text: str,
        top_k: int = 10,
        corpus_filter: Optional[Corpus] = None,
        tier_filter: Optional[Tier] = None,
        also_link_via: Optional[RelationType] = None,
    ) -> list[AtomCandidate]:
        """Semantic retrieval, then optionally expand each result via a relation type.

        Useful for queries like "find atoms similar to X and what they USE":
            hybrid("HMM-like global decoder", also_link_via=RelationType.USES_SUBPROC)
        Returns the semantic matches plus their linked atoms (de-duplicated).
        """
        seeds = self.semantic(text, top_k=top_k, corpus_filter=corpus_filter, tier_filter=tier_filter)
        if also_link_via is None:
            return seeds
        seen = {c.atom_id: c for c in seeds}
        for c in seeds:
            linked = self.store.out_neighbors(c.atom_id, also_link_via)
            for ai in linked:
                if ai not in seen:
                    seen[ai] = AtomCandidate(
                        atom_id=ai,
                        score=0.5 * c.score,
                        via=f"hybrid:{c.via}->{also_link_via.value}",
                    )
        return sorted(seen.values(), key=lambda c: -c.score)[: top_k * 2]

    # ------------------------------------------------------------
    # Substrate-algebraic stub (leverages the existing PP-225 / PP-258 paths)
    # ------------------------------------------------------------

    def algebraic(
        self,
        atom_id: str,
        rel_type: RelationType,
        top_k: int = 5,
    ) -> list[AtomCandidate]:
        """Substrate-algebraic query: 'what is atom_id related to via rel_type'.

        Computes query_vec = atom_id_vec + rel_type_vec (bundled superposition),
        then cosine-retrieves against the composite matrix.

        This is a 'what does substrate think comes next when you bind X and R'
        query that does NOT use the typed-edge index. Comparing its answer
        against structural() gives a measure of how well substrate's
        algebraic-encoding intuition matches its stored relations.
        """
        vecs = self.get_vectors(atom_id)
        if vecs is None or self._composite_matrix is None:
            return []
        q = vecs.identity + self.encoder.rel_type_vector(rel_type)
        q = q / (np.linalg.norm(q) + 1e-12)
        scores = self._composite_matrix @ q
        order = np.argsort(-scores)[:top_k]
        return [
            AtomCandidate(
                atom_id=self._id_order[i],
                score=float(scores[i]),
                via=f"algebraic:{rel_type.value}",
            )
            for i in order
            if self._id_order[i] != atom_id  # exclude the seed
        ]

    # ------------------------------------------------------------
    # Wrap into a QueryResult for metrics scoring
    # ------------------------------------------------------------

    def as_query_result(self, qid: str, candidates: list[AtomCandidate],
                       latency_ms: float = 0.0) -> QueryResult:
        return QueryResult(
            qid=qid,
            returned_atom_ids=tuple(c.atom_id for c in candidates),
            returned_relations=(),  # populated by Reasoner if relation-aware query
            latency_ms=latency_ms,
            raw_scores=tuple(c.score for c in candidates),
        )
