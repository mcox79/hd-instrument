"""Substrate-self-index v2 -- Index 2: HRR/TPR algebra index.

Per Research V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE drill 2026-06-11. Surprise-
triggered drill response to Layer 1 attribution finding that tag-vector
algebra-vec was NET NEGATIVE in the free-text composite.

The fix is architectural: free-text retrieval stays in semantic-bge Index 1
(Fix A; current state); algebra/signature/complexity get their own Index 2
encoded via substrate-native HRR/TPR (Plate FHRR + Smolensky tensor product).
Atom-to-atom shared-basis retrieval routes here. RRF fuses Index 1 + Index 2
when both apply; lexicon intent-router decides.

Architecture catalog (per drill):
1. semantic-only baseline (Fix A current state)
2. semantic + tag-vector composite (REJECTED; FINDINGS_04)
3. HYBRID semantic + HRR/TPR algebra index + RRF + intent router (RECOMMENDED)
4. bge-encode-algebra-as-text (Fix B alternative)
5. co-trained dual embeddings (out of scope for v1; needs alignment training)

This module implements architecture 3. Architecture 4 (Fix B) ships as a
parallel experiment in Day 2 CPU run #1.

Module status: SCAFFOLD. Implementation Day 2 per Research sequencing
recommendation. Public API frozen here so Layer 1 + 3 + 6 harnesses can
target it without rework.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logger = logging.getLogger(__name__)


# ============================================================
# HRR/TPR encoding of an atom's algebra/signature/complexity fields
# ============================================================


@dataclass(frozen=True)
class AlgebraVectors:
    """Substrate-native algebra-index vector triple for one atom.

    algebra_hrr   : HRR-encoded algebra dict via role-filler binding;
                    each (key, value) pair binds key_role_vec * filler_vec;
                    atom-level vector is the BUNDLE (normalized sum) over
                    pairs. (1024,) L2-normalized.
    signature_hrr : Same scheme over the signature dict.
    complexity_hrr: Same scheme over the complexity dict.
    composite_hrr : Optional weighted bundle of algebra + signature + complexity
                    for "atoms with similar structural profile" queries.
    """
    atom_id: str
    algebra_hrr: Optional[np.ndarray] = None
    signature_hrr: Optional[np.ndarray] = None
    complexity_hrr: Optional[np.ndarray] = None
    composite_hrr: Optional[np.ndarray] = None


class AlgebraIndex:
    """Substrate-native HRR/TPR index for algebra/signature/complexity fields.

    Distinguished from the semantic bge index: lives in a 1024-d FHRR phasor
    subspace; cosine similarities are atom-to-atom not query-text-to-atom.
    Free-text queries DO NOT come here.

    Use:
        idx = AlgebraIndex(dim=1024)
        idx.build(pstore)
        nearest = idx.atoms_with_shared_algebra("math::T2/fhrr_bind", top_k=5)
        # -> atoms whose algebra HRR is closest to fhrr_bind's

    Smolensky tensor product is approximated by FHRR phasor bind for the
    role-filler pair encoding (matches substrate's existing primitives).
    """

    def __init__(self, dim: int = 1024):
        self.dim = dim
        self._role_vectors: dict[str, np.ndarray] = {}
        self._filler_vectors: dict[str, np.ndarray] = {}
        self._atom_vectors: dict[str, AlgebraVectors] = {}
        # Stacked matrices for fast cosine
        self._algebra_matrix: Optional[np.ndarray] = None
        self._algebra_atom_ids: list[str] = []

    # ------------------------------------------------------------
    # Role + filler vector helpers
    # ------------------------------------------------------------

    def _role_vector(self, key: str) -> np.ndarray:
        """Stable role vector for an algebra/signature/complexity key
        (e.g., 'structure', 'commutative', 'domain'). Unit-modulus phasor."""
        raise NotImplementedError("Day 2: implement deterministic FHRR phasor")

    def _filler_vector(self, value: str | int | float | bool) -> np.ndarray:
        """Stable filler vector for a value (e.g., 'monoid', 6, True)."""
        raise NotImplementedError("Day 2: implement deterministic FHRR phasor")

    def _bind(self, role: np.ndarray, filler: np.ndarray) -> np.ndarray:
        """FHRR binding (element-wise phasor multiplication) ~ Smolensky tensor
        product approximation."""
        raise NotImplementedError("Day 2: implement FHRR binding")

    def _bundle(self, vectors: list[np.ndarray]) -> np.ndarray:
        """Bundle (normalized sum) over bound role-filler pairs."""
        raise NotImplementedError("Day 2: implement L2-normalized sum")

    # ------------------------------------------------------------
    # Encoding
    # ------------------------------------------------------------

    def encode_atom(self, atom: Atom) -> AlgebraVectors:
        """Encode one atom's algebra/signature/complexity into HRR-bundled vectors."""
        raise NotImplementedError("Day 2: HRR-encode atom")

    def build(self, pstore: PartitionedStore) -> int:
        """Build the algebra index over all atoms with algebra fields populated.

        Returns:
            number of atoms with at least one algebra/signature/complexity field encoded
        """
        raise NotImplementedError("Day 2: build index")

    # ------------------------------------------------------------
    # Retrieval modes (atom-to-atom only; free-text not supported)
    # ------------------------------------------------------------

    def atoms_with_shared_algebra(
        self,
        atom_id: str,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Top-K atoms whose algebra HRR is closest to atom_id's algebra HRR."""
        raise NotImplementedError("Day 2: cosine retrieval against algebra_matrix")

    def atoms_with_shared_signature(
        self,
        atom_id: str,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Top-K atoms whose signature HRR is closest to atom_id's signature HRR."""
        raise NotImplementedError("Day 2")

    def atoms_with_shared_complexity(
        self,
        atom_id: str,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Top-K atoms whose complexity HRR is closest to atom_id's complexity HRR."""
        raise NotImplementedError("Day 2")

    def atoms_with_shared_profile(
        self,
        atom_id: str,
        top_k: int = 10,
        weights: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> list[tuple[str, float]]:
        """Top-K atoms with similar combined algebra/signature/complexity profile."""
        raise NotImplementedError("Day 2: weighted bundle then cosine")


# ============================================================
# RRF fusion (Index 1 + Index 2)
# ============================================================


def reciprocal_rank_fusion(
    *ranked_lists: list[str],
    k: int = 60,
) -> list[tuple[str, float]]:
    """RRF fusion (Cormack 2009): combine multiple ranked lists into one.

    For each item, score = sum over lists of 1/(k + rank_in_list). Items not
    appearing in a list contribute 0 from that list.

    k=60 is the standard recommended value; tunable via RRF-k sweep
    experiment (per drill specification, k=10/30/60/100 sweep).

    Args:
        *ranked_lists: variable number of ranked lists of atom_ids
        k: RRF damping parameter (60 standard)

    Returns:
        list of (atom_id, score) sorted by score descending
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, atom_id in enumerate(ranked):
            scores[atom_id] = scores.get(atom_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])


# ============================================================
# Lexicon intent-router
# ============================================================


# Keywords that signal an algebra-structural query (route to Index 2 + relations)
_STRUCTURAL_KEYWORDS = frozenset({
    "dual", "inverse", "shared", "similar to", "same algebra",
    "shared basis", "equivalent", "frequency domain", "transformation",
    "specializes", "composes", "preserves",
})

# Keywords that signal a free-text semantic query (route to Index 1)
_SEMANTIC_KEYWORDS = frozenset({
    "what is", "describe", "explain", "definition", "example",
    "how does", "why does",
})


@dataclass(frozen=True)
class QueryIntent:
    """Result of lexicon intent classification."""
    raw_query: str
    route_semantic: bool       # use Index 1 (bge semantic)
    route_algebra: bool        # use Index 2 (HRR/TPR algebra)
    route_relations: bool      # use typed-edge relation traversal
    fuse_with_rrf: bool        # combine results via RRF
    detected_keywords: tuple[str, ...]


def classify_query_intent(query_text: str) -> QueryIntent:
    """Lexicon-based intent classifier.

    Lightweight; no ML model required. Detects structural-query keywords
    and routes accordingly. Tested against disclosed + sealed query set
    per drill experiment 3.
    """
    qlower = query_text.lower()
    detected_structural = [k for k in _STRUCTURAL_KEYWORDS if k in qlower]
    detected_semantic = [k for k in _SEMANTIC_KEYWORDS if k in qlower]
    detected = tuple(detected_structural + detected_semantic)

    has_structural = bool(detected_structural)
    has_semantic = bool(detected_semantic)
    # Default: semantic on (free-text retrieval is always useful)
    # Structural on if structural keywords present
    # Relations on if dual/inverse/equivalent/specializes/composes detected
    relation_keys = {"dual", "inverse", "equivalent", "specializes", "composes", "preserves"}
    has_relation_keywords = any(k in qlower for k in relation_keys)

    return QueryIntent(
        raw_query=query_text,
        route_semantic=True,                # always on
        route_algebra=has_structural,
        route_relations=has_relation_keywords,
        fuse_with_rrf=has_structural or has_relation_keywords,
        detected_keywords=detected,
    )


# ============================================================
# Top-level v2 query interface
# ============================================================


class HybridRetriever:
    """V2 top-level retrieval orchestrator.

    Routes queries to Index 1 (semantic) / Index 2 (algebra) / relation
    traversal based on lexicon intent-router. Fuses results via RRF.

    Composes existing Retriever (Index 1) + AlgebraIndex (Index 2) + Store
    typed-edge traversal.
    """

    def __init__(self, semantic_retriever, algebra_index: AlgebraIndex, pstore: PartitionedStore):
        self.semantic = semantic_retriever
        self.algebra = algebra_index
        self.pstore = pstore

    def query(self, query_text: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Run a hybrid query; return RRF-fused top-K with scores."""
        raise NotImplementedError("Day 2: implement query routing + RRF fusion")
