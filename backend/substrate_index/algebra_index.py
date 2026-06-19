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

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logger = logging.getLogger(__name__)


_HRR_SEED = 20260612_001  # distinct from semantic tag_seed so subspaces don't collide


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
        """Stable role vector for an algebra/signature/complexity key.

        Deterministic FHRR-style L2-normalized random vector from a hash of
        the role label. Cached on first request.
        """
        if key in self._role_vectors:
            return self._role_vectors[key]
        h = int(hashlib.sha256(f"algebra_role::{key}".encode()).hexdigest(), 16)
        rng = np.random.default_rng((h % (2**63 - 1)) ^ _HRR_SEED)
        v = rng.standard_normal(self.dim).astype(np.float32)
        v = v / (np.linalg.norm(v) + 1e-12)
        self._role_vectors[key] = v
        return v

    def _filler_vector(self, value) -> np.ndarray:
        """Stable filler vector for a value (string / int / float / bool).

        Cached by value-string form. The category-int ('1' vs 'group') case
        is handled by the caller (encode_atom) -- it may emit BOTH the int
        and the string name so cluster-by-int and cluster-by-name agree.
        """
        vstr = str(value)
        cache_key = f"filler::{vstr}"
        if cache_key in self._filler_vectors:
            return self._filler_vectors[cache_key]
        h = int(hashlib.sha256(f"algebra_filler::{vstr}".encode()).hexdigest(), 16)
        rng = np.random.default_rng(h % (2**63 - 1))
        v = rng.standard_normal(self.dim).astype(np.float32)
        v = v / (np.linalg.norm(v) + 1e-12)
        self._filler_vectors[cache_key] = v
        return v

    def _bind(self, role: np.ndarray, filler: np.ndarray) -> np.ndarray:
        """Real-valued FHRR-style binding approximation: element-wise product
        (Hadamard) then L2-normalize.

        For substrate-self-index purposes this approximates Smolensky tensor
        product / Plate HRR binding cleanly: bound vector is composition of
        role + filler subspaces; unbinding via _bind(role, bound) recovers
        approximate filler in the noise-tolerant regime.
        """
        bound = role * filler
        norm = np.linalg.norm(bound)
        if norm < 1e-12:
            return bound
        return bound / norm

    def _bundle(self, vectors: list[np.ndarray]) -> np.ndarray:
        """Bundle (L2-normalized sum) over bound role-filler pairs."""
        if not vectors:
            return np.zeros(self.dim, dtype=np.float32)
        s = np.sum(np.stack(vectors), axis=0)
        norm = np.linalg.norm(s)
        if norm < 1e-12:
            return s
        return (s / norm).astype(np.float32)

    # ------------------------------------------------------------
    # Encoding
    # ------------------------------------------------------------

    def _encode_dict_hrr(self, d: dict) -> Optional[np.ndarray]:
        """HRR-encode a structured-properties dict into a single bundle vector.

        Each (key, value) pair becomes role(key) * filler(value), bound via
        Hadamard product. Lists tag each item separately. Booleans / ints /
        floats become string-form fillers.

        Returns None if the dict yields no encodable pairs.
        """
        if not d:
            return None
        bound = []
        for k, v in d.items():
            r = self._role_vector(k)
            if isinstance(v, bool):
                bound.append(self._bind(r, self._filler_vector(str(v).lower())))
            elif isinstance(v, (str, int, float)) and v is not None:
                bound.append(self._bind(r, self._filler_vector(v)))
                # If int that looks like an algebra-category index (1-13),
                # also emit the named category so int-tagged and name-tagged
                # atoms cluster together. (Per ALGEBRA_VEC_REFINED 13-cat.)
                if k == "algebra_category" and isinstance(v, int) and 1 <= v <= 13:
                    from backend.substrate_index.schema import ALGEBRA_CATEGORIES
                    name = ALGEBRA_CATEGORIES[v - 1]
                    bound.append(self._bind(r, self._filler_vector(name)))
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, (str, int, float, bool)) and item is not None:
                        bound.append(self._bind(r, self._filler_vector(item)))
            elif isinstance(v, dict):
                # Nested dict: prefix sub-key with parent key
                for sub_k, sub_v in v.items():
                    sub_r = self._role_vector(f"{k}.{sub_k}")
                    if isinstance(sub_v, bool):
                        bound.append(self._bind(sub_r, self._filler_vector(str(sub_v).lower())))
                    elif isinstance(sub_v, (str, int, float)):
                        bound.append(self._bind(sub_r, self._filler_vector(sub_v)))
        if not bound:
            return None
        return self._bundle(bound)

    def _name_vec(self, atom: Atom) -> Optional[np.ndarray]:
        """HRR bundle of hashed name + id-path tokens.

        Per strategy_request_v587 (PP-409 production-ship fix): atom name + id
        tokens are an existing identity field carried by every atom. Bundling
        tokenized name/id as filler vectors provides per-atom-distinguishing
        identity component for compose/decode cleanup.
        """
        name_text = (atom.name or "")
        id_text = (atom.id or "").replace("/", " ").replace("_", " ").replace("::", " ")
        tokens = [t.strip().lower() for t in (name_text + " " + id_text).split()
                  if t.strip() and len(t.strip()) >= 2]
        if not tokens:
            return None
        # Each token -> filler vector; bundle via L2-normalized sum.
        vecs = [self._filler_vector(t) for t in tokens]
        return self._bundle(vecs)

    def encode_atom(self, atom: Atom, alpha_name: float = 0.5) -> AlgebraVectors:
        """Encode one atom's algebra/signature/complexity into HRR-bundled vectors.

        TWO-VECTOR ARCHITECTURE per strategy_request_v588 PP-410:
        - algebra_hrr (STRUCTURAL): pure algebra dict bundle. Collisions DESIRABLE
          (identical algebra dicts -> identical vectors by design). Used for
          atoms_with_shared_algebra similarity queries.
        - composite_hrr (IDENTITY): bundle(algebra + signature + complexity)
          + alpha_name * name_vec. Per-atom-unique; collision-resistant. Used
          for compose/decode/cleanup atom-identity queries.

        signature_hrr / complexity_hrr remain as separate vectors per their
        original purpose.

        alpha_name=0.5 is the empirically demonstrated sweet spot per
        Exp-Dev PP-410 alpha sweep (100pct cleanup recovery + 82pct structural
        clustering preserved at alpha=0.5).
        """
        alg = self._encode_dict_hrr(atom.algebra) if atom.algebra else None
        sig = self._encode_dict_hrr(atom.signature) if atom.signature else None
        cpx = self._encode_dict_hrr(atom.complexity) if atom.complexity else None
        name_v = self._name_vec(atom) if alpha_name > 0 else None

        # Identity-augmented composite_hrr per Exp-Dev PP-410 spec:
        #     composite = normalize(algebra_hrr + alpha * name_vec)
        # alpha=0.5 sweet spot: 100pct cleanup + 82pct structural retention.
        # signature_hrr / complexity_hrr remain as separate vectors (their
        # contribution to atom-identity is optional; per-atom uniqueness comes
        # primarily from name_vec which is universally populated).
        if alg is not None:
            if name_v is not None and alpha_name > 0:
                aug = alg + alpha_name * name_v
                aug_norm = np.linalg.norm(aug)
                composite = aug / aug_norm if aug_norm > 1e-12 else alg
            else:
                composite = alg
        else:
            composite = None

        return AlgebraVectors(
            atom_id=atom.qualified_id,
            algebra_hrr=alg,  # PLAIN algebra-dict-only (structural; collisions desirable)
            signature_hrr=sig,
            complexity_hrr=cpx,
            composite_hrr=composite,  # IDENTITY-augmented (collision-resistant)
        )

    def build(self, pstore: PartitionedStore) -> int:
        """Build the algebra index over all atoms with algebra fields populated."""
        atoms = pstore.all_atoms()
        encoded = 0
        algebra_rows: list[np.ndarray] = []
        algebra_ids: list[str] = []
        for atom in atoms:
            av = self.encode_atom(atom)
            self._atom_vectors[av.atom_id] = av
            if av.algebra_hrr is not None:
                encoded += 1
                algebra_rows.append(av.algebra_hrr)
                algebra_ids.append(av.atom_id)
        if algebra_rows:
            self._algebra_matrix = np.stack(algebra_rows)
            self._algebra_atom_ids = algebra_ids
        else:
            self._algebra_matrix = None
            self._algebra_atom_ids = []
        logger.info("algebra_index built: %d atoms with algebra_hrr", encoded)
        return encoded

    # ------------------------------------------------------------
    # Retrieval modes (atom-to-atom only; free-text not supported)
    # ------------------------------------------------------------

    def _retrieve_by_attr(
        self,
        atom_id: str,
        attr_name: str,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Top-K atoms by cosine on the specified AlgebraVectors attribute."""
        if atom_id not in self._atom_vectors:
            return []
        query_vec = getattr(self._atom_vectors[atom_id], attr_name, None)
        if query_vec is None:
            return []
        ids = []
        rows = []
        for aid, av in self._atom_vectors.items():
            if aid == atom_id:
                continue
            v = getattr(av, attr_name, None)
            if v is None:
                continue
            ids.append(aid)
            rows.append(v)
        if not rows:
            return []
        mat = np.stack(rows)
        sims = mat @ query_vec
        order = np.argsort(-sims)[:top_k]
        return [(ids[i], float(sims[i])) for i in order]

    def atoms_with_shared_algebra(self, atom_id: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Top-K STRUCTURAL-SIMILARITY retrieval via plain algebra-dict HRR.

        Per PP-410 two-vector architecture: STRUCTURAL mode.
        Atoms with identical algebra dicts have identical vectors BY DESIGN.
        Use this when looking for "atoms in the same algebraic class".
        """
        return self._retrieve_by_attr(atom_id, "algebra_hrr", top_k)

    def atoms_with_shared_signature(self, atom_id: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Top-K atoms whose signature HRR is closest to atom_id's signature HRR."""
        return self._retrieve_by_attr(atom_id, "signature_hrr", top_k)

    def atoms_with_shared_complexity(self, atom_id: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Top-K atoms whose complexity HRR is closest to atom_id's complexity HRR."""
        return self._retrieve_by_attr(atom_id, "complexity_hrr", top_k)

    def atoms_with_shared_identity(self, atom_id: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Top-K IDENTITY retrieval via composite (identity-augmented) HRR.

        Per PP-410 two-vector architecture: IDENTITY mode.
        composite_hrr = normalize(algebra_hrr + 0.5 * name_vec); collision-resistant
        so this returns ATOM-IDENTITY similar atoms (each specific atom is
        distinguishable from other atoms in the same algebraic class).
        Use this for compose/decode/cleanup/A-axis-content-retrieval queries.
        """
        return self._retrieve_by_attr(atom_id, "composite_hrr", top_k)

    def retrieve_similar(
        self,
        atom_id: str,
        vector_mode: str = "identity",
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Unified retrieval API per strategy_request v588 PP-410.

        vector_mode = "structural": atoms_with_shared_algebra (collisions desirable)
        vector_mode = "identity":   atoms_with_shared_identity (collision-resistant)
        vector_mode = "signature":  atoms_with_shared_signature (signature axis)
        vector_mode = "complexity": atoms_with_shared_complexity (complexity axis)

        Default = "identity" (most common consumer need: atom-specific retrieval).
        """
        mode_to_method = {
            "structural": self.atoms_with_shared_algebra,
            "identity": self.atoms_with_shared_identity,
            "signature": self.atoms_with_shared_signature,
            "complexity": self.atoms_with_shared_complexity,
        }
        method = mode_to_method.get(vector_mode)
        if method is None:
            raise ValueError(
                f"vector_mode must be one of {list(mode_to_method.keys())}; got {vector_mode!r}"
            )
        return method(atom_id, top_k)

    def atoms_with_shared_profile(
        self,
        atom_id: str,
        top_k: int = 10,
        weights: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> list[tuple[str, float]]:
        """Top-K atoms with similar combined algebra/signature/complexity profile.

        Builds the query as weighted bundle of the three sub-vectors; same
        for each atom; cosine-rank.
        """
        if atom_id not in self._atom_vectors:
            return []
        query_av = self._atom_vectors[atom_id]
        def _weighted(av: AlgebraVectors) -> Optional[np.ndarray]:
            parts = []
            if av.algebra_hrr is not None:
                parts.append(weights[0] * av.algebra_hrr)
            if av.signature_hrr is not None:
                parts.append(weights[1] * av.signature_hrr)
            if av.complexity_hrr is not None:
                parts.append(weights[2] * av.complexity_hrr)
            if not parts:
                return None
            return self._bundle(parts)
        q = _weighted(query_av)
        if q is None:
            return []
        ids = []
        rows = []
        for aid, av in self._atom_vectors.items():
            if aid == atom_id:
                continue
            v = _weighted(av)
            if v is None:
                continue
            ids.append(aid)
            rows.append(v)
        if not rows:
            return []
        mat = np.stack(rows)
        sims = mat @ q
        order = np.argsort(-sims)[:top_k]
        return [(ids[i], float(sims[i])) for i in order]


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

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        rrf_k: int = 60,
    ) -> list[tuple[str, float]]:
        """Run a hybrid query; return RRF-fused top-K with scores.

        Routing:
        - Always run Index 1 (semantic)
        - If structural intent detected: also run relations (atom-to-atom
          via typed edges)
        - If structural intent detected AND query mentions a named atom in
          the corpus: also run Index 2 (algebra) starting from that atom
        - Fuse via RRF k

        For atom-to-atom queries (no free text), use the explicit
        algebra.atoms_with_shared_* methods directly.
        """
        intent = classify_query_intent(query_text)
        ranked_lists = []

        # Index 1: semantic always runs
        if self.semantic is not None:
            sem_cands = self.semantic.semantic(query_text, top_k=top_k)
            ranked_lists.append([c.atom_id for c in sem_cands])

        # Index 2: only if query names a known atom AND structural intent
        if intent.route_algebra:
            named_atom = self._extract_named_atom(query_text)
            if named_atom is not None:
                alg_results = self.algebra.atoms_with_shared_algebra(named_atom, top_k=top_k)
                ranked_lists.append([aid for aid, _ in alg_results])

        # Relations: if a relation keyword fires
        if intent.route_relations:
            named_atom = self._extract_named_atom(query_text)
            if named_atom is not None:
                # Get out-neighbors via typed edges; use as a ranked list
                # (order by relation specificity if needed; for now flat)
                rel_neighbors = []
                for rt in RelationType:
                    for n in self.pstore.out_neighbors(named_atom, rt):
                        rel_neighbors.append(n)
                if rel_neighbors:
                    ranked_lists.append(rel_neighbors[:top_k])

        if not ranked_lists:
            return []
        if not intent.fuse_with_rrf or len(ranked_lists) == 1:
            # Return the first non-empty list with synthetic scores
            return [(aid, 1.0 / (i + 1)) for i, aid in enumerate(ranked_lists[0][:top_k])]
        return reciprocal_rank_fusion(*ranked_lists, k=rrf_k)[:top_k]

    def _extract_named_atom(self, query_text: str) -> Optional[str]:
        """Heuristic: find a corpus atom id referenced in the query text.

        Looks for qualified ids (math::...) and unqualified short names that
        match atom ids in the store.
        """
        for atom in self.pstore.all_atoms():
            qid = atom.qualified_id
            local_id = atom.id
            if qid in query_text or local_id in query_text:
                return qid
            # Also check the atom name (case-insensitive)
            if atom.name.lower() in query_text.lower():
                return qid
        return None
