"""Atom encoder for substrate self-index.

Each atom gets:
1. A semantic vector from bge-large (description + aliases) for similarity retrieval
2. A deterministic FHRR identity vector (from atom id hash) for substrate-algebraic binding
3. A composite vector binding [tier_tag] x [corpus_tag] x semantic_vec for tier/corpus-aware retrieval

The composite enables substrate-algebraic queries via the existing FHRR primitives
(PP-225 / PP-258 K-hop): query = atom_vec * rel_type_vec, cleanup -> answer atom.

L2-normalized fp32 output. Same encoder pipeline as backend/kb/wikidata_dump_ingest.py
so vectors are compatible across the substrate.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

from backend.substrate_index.schema import Atom, Corpus, RelationType, Tier

logger = logging.getLogger(__name__)


# Tag vectors are derived from a fixed seed so the same tier/corpus always gets
# the same vector across runs (deterministic FHRR encoding).
_TAG_SEED = 20260611_001


def _tag_vector(label: str, dim: int = 1024) -> np.ndarray:
    """Deterministic unit-modulus FHRR tag vector from a label string.

    Used for tier and corpus tags. Stable across runs.
    """
    h = int(hashlib.sha256(f"substrate_index_tag::{label}".encode()).hexdigest(), 16)
    rng = np.random.default_rng((h % (2**63 - 1)) ^ _TAG_SEED)
    # Random unit-modulus complex phasor, returned as real-imag concat in (dim,)
    # But to keep things simple for cosine-similarity downstream, generate a
    # random L2-normalized real vector instead.
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def _atom_id_vector(atom_id: str, dim: int = 1024) -> np.ndarray:
    """Stable per-atom FHRR-style identity vector."""
    h = int(hashlib.sha256(f"substrate_index_atom::{atom_id}".encode()).hexdigest(), 16)
    rng = np.random.default_rng(h % (2**63 - 1))
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


@dataclass(frozen=True)
class AtomVectors:
    """Cached vector representations for one atom.

    semantic    : bge-large(description + aliases) -> (1024,) L2-normalized
    identity    : deterministic FHRR id vector -> (1024,) L2-normalized
    composite   : semantic + tier_tag + corpus_tag + algebra + signature +
                  complexity bundle, L2-normalized
    algebra     : tag-vector sum over algebraic-properties field, L2-normalized
                  (zero vector for atoms without algebra field)
    signature   : tag-vector sum over signature field, L2-normalized
    complexity  : tag-vector sum over complexity field, L2-normalized

    Per Research ALGEBRA_VEC_SUPPORT 2026-06-11:
    - algebra_vec lets 'shared basis' detection be a cosine query (HMM
      Viterbi + Chu-Liu-Edmonds + Hungarian cluster in algebra-space even
      though their descriptions diverge)
    - signature_vec finds operations with matching input/output shapes
    - complexity_vec finds operations with matching computational class
    - composite combines all four with default weights alpha/beta/gamma/delta
      = 1.0 / 0.5 / 0.3 / 0.2

    All vectors are fp32 + L2-normalized for cosine retrieval.
    """
    atom_id: str
    semantic: np.ndarray
    identity: np.ndarray
    composite: np.ndarray
    algebra: np.ndarray = None
    signature: np.ndarray = None
    complexity: np.ndarray = None


class AtomEncoder:
    """Encode atoms into substrate vectors.

    Wraps backend.llm.bge_encoder.BgeEncoder for the semantic step. Caches
    tier and corpus tag vectors.
    """

    def __init__(self, bge_encoder=None, dim: int = 1024):
        if bge_encoder is None:
            from backend.llm.bge_encoder import get_encoder
            bge_encoder = get_encoder()
        self.bge = bge_encoder
        self.dim = dim
        self._tier_tags = {t: _tag_vector(f"tier::{t.value}", dim) for t in Tier}
        self._corpus_tags = {c: _tag_vector(f"corpus::{c.value}", dim) for c in Corpus}
        self._rel_tags = {r: _tag_vector(f"rel::{r.value}", dim) for r in RelationType}

    def encode_atom(self, atom: Atom) -> AtomVectors:
        """Encode one atom into its vector triple (+ optional algebra subvectors).

        Per FINDINGS_04 Layer 1 attribution (2026-06-11): algebra/signature/
        complexity sub-vectors are KEPT for explicit atom->atom algebra-mode
        retrieval, but EXCLUDED from the free-text composite by default
        (their tag-vector hash subspace is uncorrelated with bge query
        vectors; including them as composite contributions was NET NEGATIVE
        on Q2/Q3).
        """
        # Option 1 Cycle 49 (Exp-Dev empirical + Research direction): bge-NAME encoding.
        # Per exp_dev_to_research_testbed_SEMANTIC_A_V2_CLOSED_NAME_FIELD_IS_THE_LEVER...
        # name field alone +0.04-0.08 over description. Atom id tokens are content-rich
        # discipline markers (math/T2/fhrr_bind -> "fhrr bind"). Aliases retain coverage
        # for synonym matches; description excluded (drag per Exp-Dev finding).
        id_tokens = atom.id.replace("/", " ").replace("_", " ").replace("::", " ")
        text = atom.name + " " + id_tokens
        if atom.aliases:
            text = text + " " + " ".join(atom.aliases)
        semantic = self.bge.encode([text])[0].astype(np.float32)
        semantic = semantic / (np.linalg.norm(semantic) + 1e-12)

        identity = _atom_id_vector(atom.id, self.dim)

        algebra_vec = self._encode_dict_to_vec(atom.algebra) if atom.algebra else None
        signature_vec = self._encode_dict_to_vec(atom.signature) if atom.signature else None
        complexity_vec = self._encode_dict_to_vec(atom.complexity) if atom.complexity else None

        # Per FINDINGS_05 + multi-seed validation 2026-06-11: corpus_tag PURE
        # NOISE (drop) + tier_tag Q5 win 2/5 seeds = COINCIDENCE (drop).
        # Composite simplifies to L2-normalized semantic alone for Index 1.
        # Index 2 (HRR/TPR algebra) provides the substrate-distinguishing
        # signal via algebra_index.py.
        composite = semantic

        return AtomVectors(
            atom_id=atom.id,
            semantic=semantic,
            identity=identity,
            composite=composite,
            algebra=algebra_vec,
            signature=signature_vec,
            complexity=complexity_vec,
        )

    def _encode_dict_to_vec(self, d: dict) -> np.ndarray:
        """Encode a structured-properties dict as a tag-vector sum.

        Each (key, value) becomes a tag derived from a hashed string; the
        atom's vector for that field is the L2-normalized sum of tags for
        all the (key, value) pairs.

        Lists are encoded by tagging (key, each-element) separately.
        Booleans become (key, 'true' | 'false') tags.
        """
        vec = np.zeros(self.dim, dtype=np.float32)
        n = 0
        for k, v in d.items():
            if isinstance(v, bool):
                vec = vec + _tag_vector(f"prop::{k}::{v}", self.dim)
                n += 1
            elif isinstance(v, (str, int, float)) and v is not None:
                vec = vec + _tag_vector(f"prop::{k}::{v}", self.dim)
                n += 1
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, (str, int, float, bool)) and item is not None:
                        vec = vec + _tag_vector(f"prop::{k}::{item}", self.dim)
                        n += 1
            elif isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, bool) or isinstance(sub_v, (str, int, float)):
                        vec = vec + _tag_vector(f"prop::{k}::{sub_k}::{sub_v}", self.dim)
                        n += 1
        if n == 0:
            return None
        return vec / (np.linalg.norm(vec) + 1e-12)

    def encode_atoms(self, atoms: list[Atom]) -> dict[str, AtomVectors]:
        """Encode a batch of atoms (batches bge call, assembles per-atom).

        Per Research ALGEBRA_VEC_SUPPORT: composite includes algebra_vec /
        signature_vec / complexity_vec when populated. Earlier batched
        implementation skipped them; this version matches single-atom
        encode_atom() field-for-field with batched bge.
        """
        if not atoms:
            return {}
        texts = []
        for a in atoms:
            # bge-NAME encoding (Option 1; see encode_atom() above for rationale)
            id_tokens = a.id.replace("/", " ").replace("_", " ").replace("::", " ")
            t = a.name + " " + id_tokens
            if a.aliases:
                t = t + " " + " ".join(a.aliases)
            texts.append(t)
        semantics = self.bge.encode(texts).astype(np.float32)
        out = {}
        for a, sem in zip(atoms, semantics):
            sem = sem / (np.linalg.norm(sem) + 1e-12)
            ident = _atom_id_vector(a.id, self.dim)
            alg = self._encode_dict_to_vec(a.algebra) if a.algebra else None
            sig = self._encode_dict_to_vec(a.signature) if a.signature else None
            cpx = self._encode_dict_to_vec(a.complexity) if a.complexity else None
            # Per FINDINGS_04 + 05 + multi-seed: composite is pure semantic.
            # algebra/signature/complexity sub-vectors KEPT for explicit
            # atom->atom retrieval via algebra_index.py; tier+corpus dropped
            # as noise per multi-seed validation.
            comp = sem
            out[a.id] = AtomVectors(
                atom_id=a.id, semantic=sem, identity=ident, composite=comp,
                algebra=alg, signature=sig, complexity=cpx,
            )
        return out

    def encode_query_text(self, text: str) -> np.ndarray:
        """Encode a free-text query for semantic retrieval."""
        v = self.bge.encode([text])[0].astype(np.float32)
        return v / (np.linalg.norm(v) + 1e-12)

    def rel_type_vector(self, rel: RelationType) -> np.ndarray:
        """Return the FHRR tag vector for a relation type.

        Enables substrate-algebraic queries: atom_id_vec + rel_type_vec
        forms a 'what is X related to via R' query vector.
        """
        return self._rel_tags[rel]
