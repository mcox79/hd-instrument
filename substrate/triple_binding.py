"""
substrate.triple_binding -- REC-2 + REC-6 implementation.

Binds Wikidata triples (subject, predicate, object) using FHRR algebra:
  binding = subject_FHRR (x) predicate_FHRR   (vsa BIND elementwise)
  object stored as the value in a per-predicate codebook

This realizes both REC-2 ("subject ⊗ predicate → bundled codebook") and REC-6
("per-predicate sharded codebook") per Research's WIKIDATA_INGEST_OPTIMIZATION note.

Why sharded by predicate:
  - Bundle capacity for ~100M-entry single-codebook collapses SNR (per Research drill).
  - Per-predicate shards keep each shard small and queryable.
  - Aligns with substrate's existing per-strength sharding pattern (PP-127/131/132/147).

Storage architecture:
  ShardedTripleCodebook keeps one PerPredicateShard per Wikidata property:
    P31:  {subj_FHRR ⊗ pred_FHRR -> obj_FHRR}
    P21:  {subj_FHRR ⊗ pred_FHRR -> obj_FHRR}
    P569: ...                                 (date-of-birth literal -> hashed-to-FHRR)
"""
from __future__ import annotations
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from substrate.core import DEFAULT_DIM, bind, cidx, similarity, unbind
from substrate.qcode_fhrr import QCodeMapper, code_to_fhrr


# ============================================================
# Per-predicate codebook shard
# ============================================================

@dataclass
class PerPredicateShard:
    """One shard per Wikidata predicate (P31, P21, etc.).

    Stores:
      keys: (N, dim) complex64 array of subj_FHRR ⊗ pred_FHRR bindings
      objects: list[str] of object Q-codes or literals (parallel to keys)
      subject_codes: list[str] of subject Q-codes (parallel to keys; for debug)
    """
    predicate: str
    dim: int
    keys: list = field(default_factory=list)          # list of np.ndarray (complex64, dim)
    objects: list = field(default_factory=list)       # list of str (Q-code or literal)
    subject_codes: list = field(default_factory=list) # list of str
    _keys_matrix: Optional[np.ndarray] = None         # set after finalize()

    def add(self, subject_binding: np.ndarray, subject_code: str, object_value: str) -> None:
        """Append a new (binding, subject, object) tuple."""
        self.keys.append(subject_binding)
        self.subject_codes.append(subject_code)
        self.objects.append(object_value)
        self._keys_matrix = None  # invalidate

    def finalize(self) -> None:
        """Stack keys into a single matrix for fast retrieval."""
        if not self.keys:
            self._keys_matrix = np.empty((0, self.dim), dtype=np.complex64)
            return
        self._keys_matrix = np.stack(self.keys).astype(np.complex64)

    def __len__(self) -> int:
        return len(self.keys)

    def retrieve(self, query_binding: np.ndarray, top_k: int = 5) -> list:
        """Return top-k (object, subject, score) tuples for the query binding.

        Query is typically subj_FHRR ⊗ pred_FHRR (lookup) OR pred_FHRR alone
        (returns all subjects with this predicate).
        """
        if self._keys_matrix is None:
            self.finalize()
        if self._keys_matrix.shape[0] == 0:
            return []
        scores = (self._keys_matrix @ np.conj(query_binding)).real
        top_idx = np.argsort(-scores)[:top_k]
        return [(self.objects[i], self.subject_codes[i], float(scores[i])) for i in top_idx]


# ============================================================
# Sharded triple codebook (one shard per predicate)
# ============================================================

class ShardedTripleCodebook:
    """Per-predicate sharded codebook (REC-6).

    Holds one PerPredicateShard per Wikidata predicate code (P31, P21, etc.).
    Triples are added via add_triple(); queries are dispatched to the right shard.
    """

    def __init__(self, dim: int = DEFAULT_DIM, qcode_mapper: Optional[QCodeMapper] = None):
        self.dim = dim
        self.qcode_mapper = qcode_mapper or QCodeMapper(dim=dim)
        self._shards: dict = {}  # predicate_code -> PerPredicateShard
        self._lock = threading.Lock()

    # --------------------------------------------------------
    # Add triples
    # --------------------------------------------------------

    def add_triple(self, subject_code: str, predicate_code: str, object_value: str) -> None:
        """Bind subject ⊗ predicate and store with object value.

        REC-2: keys[i] = subj_FHRR ⊗ pred_FHRR for the i-th triple in this predicate's shard.
        REC-6: shards[predicate_code] gets its own keys/objects list.
        """
        subj_v = self.qcode_mapper.get(subject_code)
        pred_v = self.qcode_mapper.get(predicate_code)
        binding = bind(subj_v, pred_v)
        with self._lock:
            shard = self._shards.get(predicate_code)
            if shard is None:
                shard = PerPredicateShard(predicate=predicate_code, dim=self.dim)
                self._shards[predicate_code] = shard
            shard.add(binding, subject_code, object_value)

    def finalize_all(self) -> None:
        """Stack all shards' keys into matrices (faster retrieval)."""
        for shard in self._shards.values():
            shard.finalize()

    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    def retrieve_object(self, subject_code: str, predicate_code: str, top_k: int = 1) -> list:
        """Given (subject, predicate), recover top-k object values.

        Query: subj_FHRR ⊗ pred_FHRR matched against this predicate's shard keys.
        Should retrieve the exact triple if it was ingested.
        """
        shard = self._shards.get(predicate_code)
        if shard is None:
            return []
        subj_v = self.qcode_mapper.get(subject_code)
        pred_v = self.qcode_mapper.get(predicate_code)
        query = bind(subj_v, pred_v)
        return shard.retrieve(query, top_k=top_k)

    def subjects_with_predicate(self, predicate_code: str) -> list:
        """List all subject codes that have a triple with this predicate."""
        shard = self._shards.get(predicate_code)
        if shard is None:
            return []
        return list(shard.subject_codes)

    def predicates(self) -> list:
        return list(self._shards.keys())

    def shard_sizes(self) -> dict:
        return {p: len(s) for p, s in self._shards.items()}

    def __len__(self) -> int:
        return sum(len(s) for s in self._shards.values())


# ============================================================
# Self-test
# ============================================================

def _self_test():
    cb = ShardedTripleCodebook(dim=8192)

    # Sample triples (from Wikidata)
    triples = [
        ("Q42", "P31", "Q5"),         # Douglas Adams instance of human
        ("Q42", "P21", "Q6581097"),   # Douglas Adams sex male
        ("Q42", "P569", "1952-03-11"),# Douglas Adams date of birth literal
        ("Q42", "P106", "Q36180"),    # Douglas Adams occupation writer
        ("Q937", "P31", "Q5"),        # Einstein instance of human
        ("Q937", "P21", "Q6581097"),  # Einstein sex male
        ("Q937", "P106", "Q169470"),  # Einstein occupation physicist
        ("Q1", "P31", "Q2018526"),    # Universe instance of physical system
    ]
    for s, p, o in triples:
        cb.add_triple(s, p, o)
    cb.finalize_all()

    # Codebook structure
    assert len(cb) == 8
    assert set(cb.predicates()) == {"P31", "P21", "P569", "P106"}
    sizes = cb.shard_sizes()
    assert sizes["P31"] == 3, sizes
    assert sizes["P21"] == 2, sizes
    assert sizes["P569"] == 1, sizes
    assert sizes["P106"] == 2, sizes

    # REC-2 retrieval: subj (x) pred -> exact object
    result = cb.retrieve_object("Q42", "P31", top_k=1)
    assert result, "no result for Q42 P31"
    obj, subj, score = result[0]
    assert obj == "Q5", f"expected Q5 got {obj}"
    assert subj == "Q42", f"expected Q42 got {subj}"

    result = cb.retrieve_object("Q937", "P106", top_k=1)
    assert result[0][0] == "Q169470", f"expected Einstein's occupation Q169470 got {result[0][0]}"

    # Non-existent triple -> top retrieval still returns something (closest) but with lower score
    result_alt = cb.retrieve_object("Q937", "P31", top_k=3)
    # Should be Q5 (Einstein IS a human)
    assert result_alt[0][0] == "Q5", f"expected Q5 for Einstein P31 got {result_alt[0][0]}"

    # Highest score is the exact match
    correct_score = result[0][2]
    alt_score = result_alt[1][2] if len(result_alt) > 1 else 0
    assert correct_score > alt_score, f"exact match should outscore non-match: {correct_score} vs {alt_score}"

    # Subjects-with-predicate lookup
    subjects_p31 = cb.subjects_with_predicate("P31")
    assert set(subjects_p31) == {"Q42", "Q937", "Q1"}, subjects_p31

    print(f"[substrate.triple_binding] self-test PASS "
          f"({len(cb)} triples across {len(cb.predicates())} predicates; "
          f"subj(x)pred-to-object retrieval correct; per-predicate sharding verified)")


if __name__ == "__main__":
    _self_test()
