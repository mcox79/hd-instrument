"""Ingest tools for substrate self-index.

Reads JSONL corpus drops from Research (or anywhere) and adds them to the
appropriate partition in PartitionedStore. Idempotent: re-running an ingest
updates existing atoms without losing the relation graph.

Atom JSONL format (one Atom.to_dict() per line):
    {"id": "T2/fhrr_bind", "name": "FHRR binding", "corpus": "math",
     "tier": "T2", "kind": "primitive", "description": "...",
     "aliases": [...], "metadata": {...}}

Relation JSONL format (one Relation.to_dict() per line, qualified ids):
    {"src_id": "concept::PP-364", "tgt_id": "math::T3/viterbi",
     "rel_type": "USES", "metadata": {...}}

Note for relations: src_id and tgt_id must be QUALIFIED ids (e.g.,
'concept::PP-364', not just 'PP-364') so the partitioned store can route
them correctly across partitions.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Relation, RelationType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestReport:
    """Summary of an ingest run."""
    atoms_added: int
    atoms_updated: int
    relations_added: int
    relations_skipped: int       # duplicates or invalid
    errors: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "atoms_added": self.atoms_added,
            "atoms_updated": self.atoms_updated,
            "relations_added": self.relations_added,
            "relations_skipped": self.relations_skipped,
            "errors": list(self.errors),
        }


def ingest_atoms_jsonl(
    pstore: PartitionedStore,
    path: Path,
    source: str = "manual",
    note: str = "",
) -> tuple[int, int, list[str]]:
    """Ingest atoms from a JSONL file. Returns (added, updated, errors)."""
    path = Path(path)
    added = updated = 0
    errors = []
    if not path.exists():
        return 0, 0, [f"file not found: {path}"]
    with open(path, encoding="utf-8") as f:
        for line_n, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                d = json.loads(line)
                atom = Atom.from_dict(d)
            except Exception as e:
                errors.append(f"line {line_n}: parse error: {e}")
                continue
            was_present = pstore.has_atom(atom.qualified_id)
            try:
                pstore.add_atom(atom, source=source, note=note)
                if was_present:
                    updated += 1
                else:
                    added += 1
            except Exception as e:
                errors.append(f"line {line_n}: store error: {e}")
    return added, updated, errors


def ingest_relations_jsonl(
    pstore: PartitionedStore,
    path: Path,
    source: str = "manual",
    note: str = "",
) -> tuple[int, int, list[str]]:
    """Ingest relations from a JSONL file. Returns (added, skipped, errors)."""
    path = Path(path)
    added = skipped = 0
    errors = []
    if not path.exists():
        return 0, 0, [f"file not found: {path}"]
    with open(path, encoding="utf-8") as f:
        for line_n, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                d = json.loads(line)
                src = d["src_id"]
                tgt = d["tgt_id"]
                rt = RelationType(d["rel_type"])
            except Exception as e:
                errors.append(f"line {line_n}: parse error: {e}")
                continue

            # Both endpoints must exist before we add a relation
            if not pstore.has_atom(src):
                errors.append(f"line {line_n}: src atom missing: {src}")
                skipped += 1
                continue
            if not pstore.has_atom(tgt):
                errors.append(f"line {line_n}: tgt atom missing: {tgt}")
                skipped += 1
                continue

            try:
                pstore.add_relation(src, rt, tgt, source=source, note=note)
                added += 1
            except ValueError as e:
                errors.append(f"line {line_n}: blocked: {e}")
                skipped += 1
            except RuntimeError as e:
                errors.append(f"line {line_n}: cap reached: {e}")
                skipped += 1
            except Exception as e:
                errors.append(f"line {line_n}: store error: {e}")
                skipped += 1
    return added, skipped, errors


def ingest_corpus_bundle(
    pstore: PartitionedStore,
    atoms_path: Optional[Path] = None,
    relations_path: Optional[Path] = None,
    source: str = "manual",
    note: str = "",
) -> IngestReport:
    """Convenience: ingest atoms then relations from two JSONL files.

    Order matters: atoms first so relations can resolve both endpoints.
    """
    a_added = a_updated = 0
    r_added = r_skipped = 0
    errors: list[str] = []
    if atoms_path is not None:
        a_added, a_updated, e1 = ingest_atoms_jsonl(pstore, atoms_path, source=source, note=note)
        errors.extend(e1)
    if relations_path is not None:
        r_added, r_skipped, e2 = ingest_relations_jsonl(pstore, relations_path, source=source, note=note)
        errors.extend(e2)
    return IngestReport(
        atoms_added=a_added,
        atoms_updated=a_updated,
        relations_added=r_added,
        relations_skipped=r_skipped,
        errors=tuple(errors),
    )
