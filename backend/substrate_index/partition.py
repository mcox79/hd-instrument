"""Partitioned-substrate-with-role-binding architecture.

Per Research SELF_INDEX_RESCOPE_ENDORSED 2026-06-11 Refinement 3:
- math, concept, meta are SEPARATE Store instances (separate dirs on disk)
- explicit cross-store linking via qualified ids ('math::T2/bind', 'concept::PP-364')
- design AGAINST 4 failure modes:
  1. meta-rule self-collapse  -> meta atoms cannot have outgoing relations to themselves
  2. string-similarity laundering  -> metrics report exact failure mode, not "understanding"
  3. hand-coded scaling  -> structural cap on hand-authored relations (warn at 5K, hard cap at 10K)
  4. unbounded self-reference  -> all path queries have max_depth termination

Cross-store relations are stored canonically in the SOURCE atom's partition
(so removing the source partition's atom cascades the cross-store edges).
The partitioned wrapper also maintains a reverse-lookup so the target partition
can find incoming cross-store edges in O(1).
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

from backend.substrate_index.schema import (
    Atom,
    Corpus,
    Relation,
    RelationType,
)
from backend.substrate_index.store import Store

logger = logging.getLogger(__name__)


# Hand-coded scaling caps per design-against rule 3
HAND_AUTHORED_RELATION_WARN = 5000
HAND_AUTHORED_RELATION_HARD_CAP = 10000


@dataclass(frozen=True)
class QualifiedAtomId:
    """Cross-store identifier; e.g., math::T2/bind, concept::PP-364, meta::drill-defeatism."""
    corpus: Corpus
    local_id: str

    def __str__(self) -> str:
        return f"{self.corpus.value}::{self.local_id}"

    @classmethod
    def parse(cls, qualified: str) -> "QualifiedAtomId":
        if "::" not in qualified:
            raise ValueError(f"not a qualified id: {qualified!r} (expected 'corpus::local_id')")
        partition, local = qualified.split("::", 1)
        return cls(corpus=Corpus(partition), local_id=local)


class PartitionedStore:
    """Three separate substrate stores + explicit cross-store linking.

    Public surface mirrors Store but works on qualified ids.

    Cross-store relations are persisted via the source partition's Store (the
    source atom's outgoing edge). The wrapper maintains an additional in-memory
    reverse index so the target partition can answer 'who from outside points
    at me via R' efficiently.
    """

    def __init__(self, root: Path):
        self.root = Path(root)
        self.math = Store(self.root / "math")
        self.concept = Store(self.root / "concept")
        self.meta = Store(self.root / "meta")
        self.school = Store(self.root / "school")  # per Research SCHOOLS_CORPUS proposal
        # Per Research FINDINGS_08_VALIDATE_METHODOLOGY_PARTITION 2026-06-11:
        # substrate-proposed partition empirically surfaced by composite C NOVEL cluster
        self.methodology = Store(self.root / "methodology")
        # Per Research SCIENCE_BATCH_01 2026-06-11 + USER massive math+science directive:
        self.science = Store(self.root / "science")
        # Per Research SUBSTRATE_AS_FULL_RESEARCH_LEDGER + AUTO_INGEST_VIA_EVOLVE_PY
        # 2026-06-11: six new partitions for auto-ingest of all research artifacts
        self.research_history = Store(self.root / "research_history")
        self.decision_history = Store(self.root / "decision_history")
        self.results_history = Store(self.root / "results_history")
        self.findings_history = Store(self.root / "findings_history")
        self.verdict_history = Store(self.root / "verdict_history")
        self.memory_history = Store(self.root / "memory_history")
        self._stores = {
            Corpus.MATH: self.math,
            Corpus.CONCEPT: self.concept,
            Corpus.META: self.meta,
            Corpus.SCHOOL: self.school,
            Corpus.METHODOLOGY: self.methodology,
            Corpus.SCIENCE: self.science,
            Corpus.RESEARCH_HISTORY: self.research_history,
            Corpus.DECISION_HISTORY: self.decision_history,
            Corpus.RESULTS_HISTORY: self.results_history,
            Corpus.FINDINGS_HISTORY: self.findings_history,
            Corpus.VERDICT_HISTORY: self.verdict_history,
            Corpus.MEMORY_HISTORY: self.memory_history,
        }
        # Cross-store reverse index: tgt_qualified_id -> set of (src_qualified_id, rel_type)
        self._cross_in: dict[str, set[tuple[str, RelationType]]] = defaultdict(set)
        self._rebuild_cross_index()

    def _rebuild_cross_index(self) -> None:
        """Walk each partition's relations and build the cross-store reverse index.

        A relation is 'cross-store' if its src and tgt live in different partitions.
        We store the canonical edge in the source partition's Store (with local_id
        equal to qualified id for both sides). Reverse lookup is via this dict.
        """
        self._cross_in.clear()
        for corpus, store in self._stores.items():
            for src_local, rt, tgt_local in store.iter_relations():
                # Heuristic: if src or tgt local id contains "::", it's a qualified id
                # referring to another partition.
                if "::" in tgt_local:
                    self._cross_in[tgt_local].add((f"{corpus.value}::{src_local}", rt))

    # ------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------

    def _store_for(self, corpus: Corpus) -> Store:
        return self._stores[corpus]

    def get_atom(self, qualified_id: str) -> Optional[Atom]:
        try:
            q = QualifiedAtomId.parse(qualified_id)
        except ValueError:
            # Search all partitions; ambiguous if found in multiple
            for store in self._stores.values():
                a = store.get_atom(qualified_id)
                if a is not None:
                    return a
            return None
        return self._store_for(q.corpus).get_atom(q.local_id)

    def has_atom(self, qualified_id: str) -> bool:
        return self.get_atom(qualified_id) is not None

    def all_atoms(self) -> list[Atom]:
        out = []
        for store in self._stores.values():
            out.extend(store.all_atoms())
        return out

    def all_qualified_ids(self) -> set[str]:
        out = set()
        for corpus, store in self._stores.items():
            for atom in store.iter_atoms():
                out.add(f"{corpus.value}::{atom.id}")
        return out

    # ------------------------------------------------------------
    # Add atom
    # ------------------------------------------------------------

    def add_atom(self, atom: Atom, source: str = "manual", note: str = "") -> None:
        """Add an atom to the appropriate partition based on its corpus."""
        # Failure mode #1 guard: meta atoms cannot reference themselves
        # (relations are checked in add_relation; here we just route the atom)
        self._store_for(atom.corpus).add_atom(atom, source=source, note=note)

    def remove_atom(self, qualified_id: str, source: str = "manual", note: str = "") -> bool:
        q = QualifiedAtomId.parse(qualified_id)
        ok = self._store_for(q.corpus).remove_atom(q.local_id, source=source, note=note)
        if ok:
            # Drop cross-store reverse entries pointing to this atom
            self._cross_in.pop(qualified_id, None)
            # Also drop cross-store entries where this atom was the source
            self._rebuild_cross_index()
        return ok

    # ------------------------------------------------------------
    # Add relation -- handles within-store and cross-store
    # ------------------------------------------------------------

    def add_relation(
        self,
        src_qualified_id: str,
        rel_type: RelationType,
        tgt_qualified_id: str,
        source: str = "manual",
        note: str = "",
    ) -> None:
        """Add a relation between two qualified atom ids."""
        src_q = QualifiedAtomId.parse(src_qualified_id)
        tgt_q = QualifiedAtomId.parse(tgt_qualified_id)

        # Failure mode #1 guard: meta atoms cannot have outgoing relations into themselves
        if src_q.corpus == Corpus.META and tgt_q.corpus == Corpus.META and src_q.local_id == tgt_q.local_id:
            raise ValueError(
                f"meta-rule self-collapse blocked: meta atom {src_qualified_id} "
                f"cannot have a relation to itself"
            )

        # Failure mode #3 guard: hand-coded scaling cap
        if source == "manual":
            total = sum(len(s._all_relations) for s in self._stores.values())
            if total >= HAND_AUTHORED_RELATION_HARD_CAP:
                raise RuntimeError(
                    f"hand-authored relation hard cap ({HAND_AUTHORED_RELATION_HARD_CAP}) "
                    f"reached: {total} relations. Switch to auto-extraction (evolve.py) "
                    f"or revise architecture."
                )
            if total == HAND_AUTHORED_RELATION_WARN:
                logger.warning(
                    "hand-authored relation count reached warn threshold %d; "
                    "consider switching to auto-extraction soon",
                    HAND_AUTHORED_RELATION_WARN,
                )

        # Within-store: just delegate to the source's Store using local ids
        if src_q.corpus == tgt_q.corpus:
            rel = Relation(src_id=src_q.local_id, tgt_id=tgt_q.local_id, rel_type=rel_type)
            self._store_for(src_q.corpus).add_relation(rel, source=source, note=note)
            return

        # Cross-store: store in source's Store with qualified target id
        rel = Relation(
            src_id=src_q.local_id,
            tgt_id=tgt_qualified_id,  # full qualified to disambiguate
            rel_type=rel_type,
        )
        self._store_for(src_q.corpus).add_relation(rel, source=source, note=note)
        self._cross_in[tgt_qualified_id].add((src_qualified_id, rel_type))

    # ------------------------------------------------------------
    # Neighbor queries -- handles within-store and cross-store transparently
    # ------------------------------------------------------------

    def out_neighbors(
        self,
        qualified_id: str,
        rel_type: Optional[RelationType] = None,
    ) -> set[str]:
        """Atoms reachable from qualified_id via rel_type. Returns qualified ids."""
        q = QualifiedAtomId.parse(qualified_id)
        store = self._store_for(q.corpus)
        raw_neighbors = store.out_neighbors(q.local_id, rel_type)
        # Within-store neighbors are local ids; cross-store are qualified.
        out = set()
        for n in raw_neighbors:
            if "::" in n:
                out.add(n)
            else:
                out.add(f"{q.corpus.value}::{n}")
        return out

    def in_neighbors(
        self,
        qualified_id: str,
        rel_type: Optional[RelationType] = None,
    ) -> set[str]:
        """Atoms reaching qualified_id via rel_type. Returns qualified ids."""
        q = QualifiedAtomId.parse(qualified_id)
        store = self._store_for(q.corpus)
        # Within-partition in-neighbors
        local_in = store.in_neighbors(q.local_id, rel_type)
        out = {f"{q.corpus.value}::{n}" for n in local_in}
        # Cross-store in-neighbors
        for src_qual, rt in self._cross_in.get(qualified_id, set()):
            if rel_type is None or rt == rel_type:
                out.add(src_qual)
        return out

    # ------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------

    def stats(self) -> dict:
        """Aggregate stats across all partitions."""
        out = {
            "partitions": {},
            "total_atoms": 0,
            "total_relations": 0,
            "cross_store_relations": len(set().union(*self._cross_in.values())) if self._cross_in else 0,
        }
        for corpus, store in self._stores.items():
            s = store.stats()
            out["partitions"][corpus.value] = s
            out["total_atoms"] += s["n_atoms"]
            out["total_relations"] += s["n_relations"]
        return out

    def iter_all_relations(self) -> Iterator[tuple[str, RelationType, str]]:
        """Yield (qualified_src, rel_type, qualified_tgt) for all relations."""
        for corpus, store in self._stores.items():
            for src_local, rt, tgt_local in store.iter_relations():
                src_q = f"{corpus.value}::{src_local}"
                tgt_q = tgt_local if "::" in tgt_local else f"{corpus.value}::{tgt_local}"
                yield (src_q, rt, tgt_q)
