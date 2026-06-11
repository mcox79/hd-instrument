"""Living-artifact auto-ingest for the substrate self-index.

Reads cap_map cycle notes (strategy_decisions + visibility_decisions) and
auto-ingests new PP rows as concept atoms in the substrate self-index.

Per user direction 2026-06-11: "update it as we build out our capabilities."
The index lives as long as the project does.

What evolves:
1. New PP rows from strategy_decisions       -> new concept atoms
2. LVH catches                                -> REFUTES relations
3. Tier promotions (D->C->B->A)               -> atom metadata + VALIDATES edges
4. BAND LIFT events                           -> atom metadata bumps + version
5. Drill outcomes                             -> concept atoms + ENABLES relations
6. Auto re-run benchmark + drift detection    -> flag regressions

Parsers are tolerant of format variation: cycle notes vary in formatting; we
match on stable markers (PP-NNN: ... HARD_PASS, [LVH-NNN], etc.). When a
parse fails, we log + skip rather than crash -- the audit log preserves what
the system saw.

Auto-extracted relations are flagged with source='auto:cycle_<N>' so the
hand-coded-scaling guard in partition.py doesn't include them.
"""
from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import (
    Atom,
    AtomKind,
    Corpus,
    RelationType,
    Tier,
)

logger = logging.getLogger(__name__)


# ============================================================
# Parsing patterns
# ============================================================


# Match a NEW ROW PP-NNN line; capture (pp_id, anchor, verdict_tag, description-prefix)
NEW_PP_ROW = re.compile(
    r"NEW ROW (PP-\d+):\s*([\w_\-]+(?:_cpu_v\d+|_gpu_v\d+))?\s*(HARD_PASS|MIDDLE_BAND|HARD_FAIL)?[\s\S]*?(?=NEW ROW|\Z)",
    re.MULTILINE,
)

# Match a single LVH line (in or out of a header)
LVH_LINE = re.compile(
    r"LVH-(\d+)[\]:\s]+([^\n]+)",
)

# Match a band lift line
BAND_LIFT = re.compile(
    r"(PP-\d+)\s+BAND LIFT:?\s*([\d.\-]+)\s*->\s*([\d.\-]+)",
)


@dataclass(frozen=True)
class ParsedPpRow:
    """One PP row extracted from a strategy_decisions cycle."""
    pp_id: str
    anchor: Optional[str]
    verdict: Optional[str]
    raw_block: str           # the full text of the PP row entry
    description: str         # extracted first-sentence-ish description
    cycle: Optional[int]     # if we can find the containing cycle number

    def as_concept_atom(self) -> Atom:
        """Convert into a concept-corpus Atom for ingest."""
        # Stable id is the PP-NNN identifier
        # Strip anything past a reasonable description length
        desc = self.description[:600]
        return Atom(
            id=self.pp_id,
            name=f"{self.pp_id} ({self.anchor})" if self.anchor else self.pp_id,
            corpus=Corpus.CONCEPT,
            tier=Tier.TIER_NA,
            kind=AtomKind.PRIMITIVE,
            description=desc,
            aliases=(self.anchor,) if self.anchor else (),
            metadata={
                "verdict": self.verdict or "",
                "cycle": self.cycle if self.cycle is not None else "",
                "auto_extracted": True,
            },
        )


# ============================================================
# Strategy_decisions parser
# ============================================================


def parse_strategy_decisions(text: str) -> tuple[list[ParsedPpRow], list[tuple[str, str]]]:
    """Extract PP rows and LVH events from a strategy_decisions markdown body.

    Returns:
        pp_rows: list of ParsedPpRow
        lvh_events: list of (lvh_id, summary_text)
    """
    pp_rows = []
    # Find all NEW ROW blocks. Use re.finditer on the precompiled NEW_PP_ROW
    # to capture (pp_id, anchor, verdict).
    cycle_match = re.search(r"CYCLE\s+(\d+)", text)
    cycle = int(cycle_match.group(1)) if cycle_match else None

    for m in NEW_PP_ROW.finditer(text):
        pp_id = m.group(1)
        anchor = m.group(2)
        verdict = m.group(3)
        block = m.group(0)
        # Extract first sentence / first ~200 chars as description starting after
        # the verdict tag
        desc_match = re.search(
            rf"{re.escape(pp_id)}:\s*[^.]*\.\s*([^.]*\.[^.]*\.)",
            block,
        )
        description = desc_match.group(0).strip() if desc_match else block[:400].strip()
        pp_rows.append(ParsedPpRow(
            pp_id=pp_id,
            anchor=anchor,
            verdict=verdict,
            raw_block=block.strip(),
            description=description,
            cycle=cycle,
        ))

    lvh_events = []
    for m in LVH_LINE.finditer(text):
        lvh_id = f"LVH-{m.group(1)}"
        summary = m.group(2).strip()
        lvh_events.append((lvh_id, summary))

    return pp_rows, lvh_events


# ============================================================
# Evolve from cycle notes
# ============================================================


@dataclass(frozen=True)
class EvolveReport:
    """Summary of one evolve pass."""
    cycles_processed: int
    atoms_added: int
    atoms_updated: int
    relations_added: int
    lvh_relations_added: int
    errors: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "cycles_processed": self.cycles_processed,
            "atoms_added": self.atoms_added,
            "atoms_updated": self.atoms_updated,
            "relations_added": self.relations_added,
            "lvh_relations_added": self.lvh_relations_added,
            "errors": list(self.errors),
        }


def evolve_from_strategy_files(
    pstore: PartitionedStore,
    strategy_paths: list[Path],
) -> EvolveReport:
    """Read strategy_decisions markdown files and ingest each cycle's new PP
    rows as concept atoms.

    Each file may contain multiple cycles; we parse the whole body.
    """
    atoms_added = atoms_updated = 0
    relations_added = 0
    lvh_relations_added = 0
    errors: list[str] = []
    cycles_processed = 0

    for path in strategy_paths:
        path = Path(path)
        if not path.exists():
            errors.append(f"path not found: {path}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"read error {path}: {e}")
            continue

        # Split by cycle blocks. Cycles begin with '## vNNN -> vNNN CYCLE M'
        # or similar; for robustness we just split on '## v'.
        cycle_blocks = re.split(r"\n##\s+v\d+\s*->", text)
        cycles_processed += max(1, len(cycle_blocks) - 1)
        for block in cycle_blocks:
            pp_rows, lvh_events = parse_strategy_decisions(block)
            for pp in pp_rows:
                atom = pp.as_concept_atom()
                was_present = pstore.has_atom(atom.qualified_id)
                try:
                    pstore.add_atom(
                        atom,
                        source=f"auto:cycle_{pp.cycle or '?'}",
                        note=f"auto-extracted PP row from strategy_decisions",
                    )
                    if was_present:
                        atoms_updated += 1
                    else:
                        atoms_added += 1
                except Exception as e:
                    errors.append(f"{pp.pp_id}: add_atom failed: {e}")

            # LVH events become REFUTES relations from the LVH-tagged atom toward
            # any atom it implicates. For now we can only file the LVH itself
            # as metadata; full REFUTES wiring needs to know which atom is
            # implicated (parse out PP-NNN mentions in the summary).
            for lvh_id, summary in lvh_events:
                pp_mentions = re.findall(r"(PP-\d+)", summary)
                for pp_mention in pp_mentions:
                    src_qid = f"concept::{lvh_id}"
                    tgt_qid = f"concept::{pp_mention}"
                    if not pstore.has_atom(tgt_qid):
                        continue
                    # Ensure LVH atom exists as a stub
                    if not pstore.has_atom(src_qid):
                        stub = Atom(
                            id=lvh_id,
                            name=lvh_id,
                            corpus=Corpus.CONCEPT,
                            tier=Tier.TIER_NA,
                            kind=AtomKind.PRIMITIVE,
                            description=f"Label-vs-Honest event: {summary[:200]}",
                            metadata={"auto_extracted": True, "lvh": True},
                        )
                        pstore.add_atom(stub, source=f"auto:lvh", note=summary[:100])
                        atoms_added += 1
                    try:
                        pstore.add_relation(
                            src_qid, RelationType.REFUTES, tgt_qid,
                            source=f"auto:lvh", note=summary[:100],
                        )
                        lvh_relations_added += 1
                        relations_added += 1
                    except Exception as e:
                        errors.append(f"REFUTES wiring failed {lvh_id}->{pp_mention}: {e}")

    return EvolveReport(
        cycles_processed=cycles_processed,
        atoms_added=atoms_added,
        atoms_updated=atoms_updated,
        relations_added=relations_added,
        lvh_relations_added=lvh_relations_added,
        errors=tuple(errors),
    )


# ============================================================
# Discover-cap_map-files convenience entry point
# ============================================================


def evolve_from_notes_dir(
    pstore: PartitionedStore,
    notes_dir: Path = Path("notes"),
) -> EvolveReport:
    """Find all strategy_decisions_*.md files under notes_dir and ingest them."""
    notes_dir = Path(notes_dir)
    paths = sorted(notes_dir.glob("strategy_decisions_*.md"))
    return evolve_from_strategy_files(pstore, paths)
