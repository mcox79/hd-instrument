"""Indexed graph storage for substrate self-index.

Atoms + typed-edge relations, indexed for the analysis surface the user wants:
- direct retrieval by id
- by-corpus / by-tier subsets
- typed-edge adjacency lookups (in/out by relation type)
- auto-derived HAS_USERS reverse for USES (cross-corpus bidirectional)
- versioned change log (per-atom + per-relation revisions for drift tracking)

Persistence: JSONL files alongside in-memory indexes. Same disk format as
schema.save_atoms/load_atoms but with an audit log appended for evolve.py.
"""
from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Optional

from backend.substrate_index.schema import (
    Atom,
    Corpus,
    Relation,
    RelationType,
    Tier,
    load_atoms,
    load_relations,
    save_atoms,
    save_relations,
)


# ============================================================
# Audit log
# ============================================================


@dataclass(frozen=True)
class ChangeEvent:
    """One change to the index. Append-only audit log."""
    ts: float                 # unix timestamp
    op: str                   # "add_atom" | "update_atom" | "remove_atom" | "add_relation" | "remove_relation"
    target: str               # atom id or "src_id|rel_type|tgt_id"
    note: str = ""            # optional human-readable reason
    source: str = ""          # e.g., "cap_map_cycle_232" / "manual" / "discover"

    def to_dict(self) -> dict:
        return {
            "ts": self.ts,
            "op": self.op,
            "target": self.target,
            "note": self.note,
            "source": self.source,
        }


# ============================================================
# Store
# ============================================================


class Store:
    """In-memory graph store of atoms + typed-edge relations.

    Backed by JSONL files for persistence and an audit log for evolve.py.

    Indexes maintained automatically on insert/remove:
        _by_id          : atom_id -> Atom
        _by_corpus      : Corpus -> set[atom_id]
        _by_tier        : Tier -> set[atom_id]
        _out            : (atom_id, RelationType) -> set[atom_id]   # outgoing edges
        _in             : (atom_id, RelationType) -> set[atom_id]   # incoming edges
        _all_relations  : set of (src, rel_type, tgt) tuples for O(1) existence
    """

    def __init__(self, root: Path):
        self.root = Path(root)
        self.atoms_path = self.root / "atoms.jsonl"
        self.relations_path = self.root / "relations.jsonl"
        self.audit_path = self.root / "audit.jsonl"

        self._by_id: dict[str, Atom] = {}
        self._by_corpus: dict[Corpus, set[str]] = defaultdict(set)
        self._by_tier: dict[Tier, set[str]] = defaultdict(set)
        self._out: dict[tuple[str, RelationType], set[str]] = defaultdict(set)
        self._in: dict[tuple[str, RelationType], set[str]] = defaultdict(set)
        self._all_relations: set[tuple[str, str, str]] = set()

        self._load_from_disk()

    # ------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------

    def _load_from_disk(self) -> None:
        for atom in load_atoms(self.atoms_path):
            self._index_atom(atom)
        for rel in load_relations(self.relations_path):
            self._index_relation(rel)
            # auto-derive HAS_USERS from USES (cross-corpus reverse)
            if rel.rel_type == RelationType.USES:
                derived = Relation(
                    src_id=rel.tgt_id,
                    tgt_id=rel.src_id,
                    rel_type=RelationType.HAS_USERS,
                    metadata={"derived_from": "USES"},
                )
                self._index_relation(derived)

    def _flush_atoms(self) -> None:
        save_atoms(list(self._by_id.values()), self.atoms_path)

    def _flush_relations(self) -> None:
        # Only persist explicit relations, not auto-derived HAS_USERS
        explicit = [
            Relation(
                src_id=src,
                tgt_id=tgt,
                rel_type=RelationType(rel_type_str),
            )
            for (src, rel_type_str, tgt) in self._all_relations
            if rel_type_str != RelationType.HAS_USERS.value
        ]
        save_relations(explicit, self.relations_path)

    def _append_audit(self, event: ChangeEvent) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    # ------------------------------------------------------------
    # Atoms
    # ------------------------------------------------------------

    def _index_atom(self, atom: Atom) -> None:
        self._by_id[atom.id] = atom
        self._by_corpus[atom.corpus].add(atom.id)
        self._by_tier[atom.tier].add(atom.id)

    def add_atom(self, atom: Atom, source: str = "manual", note: str = "") -> None:
        is_update = atom.id in self._by_id
        if is_update:
            old = self._by_id[atom.id]
            self._by_corpus[old.corpus].discard(atom.id)
            self._by_tier[old.tier].discard(atom.id)
        self._index_atom(atom)
        self._flush_atoms()
        op = "update_atom" if is_update else "add_atom"
        self._append_audit(ChangeEvent(
            ts=time.time(), op=op, target=atom.id, note=note, source=source
        ))

    def remove_atom(self, atom_id: str, source: str = "manual", note: str = "") -> bool:
        if atom_id not in self._by_id:
            return False
        atom = self._by_id.pop(atom_id)
        self._by_corpus[atom.corpus].discard(atom_id)
        self._by_tier[atom.tier].discard(atom_id)
        # Cascade: remove all relations touching this atom
        to_remove = [r for r in self._all_relations if r[0] == atom_id or r[2] == atom_id]
        for src, rel_str, tgt in to_remove:
            rt = RelationType(rel_str)
            self._out[(src, rt)].discard(tgt)
            self._in[(tgt, rt)].discard(src)
            self._all_relations.discard((src, rel_str, tgt))
        self._flush_atoms()
        self._flush_relations()
        self._append_audit(ChangeEvent(
            ts=time.time(), op="remove_atom", target=atom_id, note=note, source=source
        ))
        return True

    def get_atom(self, atom_id: str) -> Optional[Atom]:
        return self._by_id.get(atom_id)

    def has_atom(self, atom_id: str) -> bool:
        return atom_id in self._by_id

    def all_atoms(self) -> list[Atom]:
        return list(self._by_id.values())

    def all_atom_ids(self) -> set[str]:
        return set(self._by_id.keys())

    def atoms_by_corpus(self, corpus: Corpus) -> list[Atom]:
        return [self._by_id[aid] for aid in self._by_corpus[corpus]]

    def atoms_by_tier(self, tier: Tier) -> list[Atom]:
        return [self._by_id[aid] for aid in self._by_tier[tier]]

    def iter_atoms(self) -> Iterator[Atom]:
        return iter(self._by_id.values())

    # ------------------------------------------------------------
    # Relations
    # ------------------------------------------------------------

    def _index_relation(self, rel: Relation) -> None:
        triple = (rel.src_id, rel.rel_type.value, rel.tgt_id)
        if triple in self._all_relations:
            return
        self._all_relations.add(triple)
        self._out[(rel.src_id, rel.rel_type)].add(rel.tgt_id)
        self._in[(rel.tgt_id, rel.rel_type)].add(rel.src_id)

    def add_relation(self, rel: Relation, source: str = "manual", note: str = "") -> None:
        triple = (rel.src_id, rel.rel_type.value, rel.tgt_id)
        if triple in self._all_relations:
            return
        self._index_relation(rel)
        # Auto-derive HAS_USERS reverse for USES
        if rel.rel_type == RelationType.USES:
            self._index_relation(Relation(
                src_id=rel.tgt_id,
                tgt_id=rel.src_id,
                rel_type=RelationType.HAS_USERS,
                metadata={"derived_from": "USES"},
            ))
        self._flush_relations()
        self._append_audit(ChangeEvent(
            ts=time.time(),
            op="add_relation",
            target=f"{rel.src_id}|{rel.rel_type.value}|{rel.tgt_id}",
            note=note,
            source=source,
        ))

    def remove_relation(self, src_id: str, rel_type: RelationType, tgt_id: str,
                        source: str = "manual", note: str = "") -> bool:
        triple = (src_id, rel_type.value, tgt_id)
        if triple not in self._all_relations:
            return False
        self._all_relations.discard(triple)
        self._out[(src_id, rel_type)].discard(tgt_id)
        self._in[(tgt_id, rel_type)].discard(src_id)
        # Also remove auto-derived reverse if this was USES
        if rel_type == RelationType.USES:
            self._all_relations.discard((tgt_id, RelationType.HAS_USERS.value, src_id))
            self._out[(tgt_id, RelationType.HAS_USERS)].discard(src_id)
            self._in[(src_id, RelationType.HAS_USERS)].discard(tgt_id)
        self._flush_relations()
        self._append_audit(ChangeEvent(
            ts=time.time(),
            op="remove_relation",
            target=f"{src_id}|{rel_type.value}|{tgt_id}",
            note=note,
            source=source,
        ))
        return True

    def has_relation(self, src_id: str, rel_type: RelationType, tgt_id: str) -> bool:
        return (src_id, rel_type.value, tgt_id) in self._all_relations

    def out_neighbors(self, atom_id: str, rel_type: Optional[RelationType] = None) -> set[str]:
        """Atoms reachable from atom_id via rel_type (or any if None)."""
        if rel_type is not None:
            return set(self._out[(atom_id, rel_type)])
        result = set()
        for rt in RelationType:
            result.update(self._out.get((atom_id, rt), set()))
        return result

    def in_neighbors(self, atom_id: str, rel_type: Optional[RelationType] = None) -> set[str]:
        """Atoms reaching atom_id via rel_type (or any if None)."""
        if rel_type is not None:
            return set(self._in[(atom_id, rel_type)])
        result = set()
        for rt in RelationType:
            result.update(self._in.get((atom_id, rt), set()))
        return result

    def iter_relations(self) -> Iterator[tuple[str, RelationType, str]]:
        for (src, rt_str, tgt) in self._all_relations:
            yield (src, RelationType(rt_str), tgt)

    def relations_by_type(self, rel_type: RelationType) -> list[tuple[str, str]]:
        """Return list of (src, tgt) pairs for the given relation type."""
        return [
            (src, tgt) for (src, rt, tgt) in self._all_relations
            if rt == rel_type.value
        ]

    # ------------------------------------------------------------
    # Stats / introspection
    # ------------------------------------------------------------

    def stats(self) -> dict:
        return {
            "n_atoms": len(self._by_id),
            "n_atoms_by_corpus": {c.value: len(s) for c, s in self._by_corpus.items()},
            "n_atoms_by_tier": {t.value: len(s) for t, s in self._by_tier.items()},
            "n_relations": len(self._all_relations),
            "n_relations_by_type": {
                rt.value: sum(1 for r in self._all_relations if r[1] == rt.value)
                for rt in RelationType
            },
        }
