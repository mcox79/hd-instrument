"""Backfill `atoms_used` field on existing solution_history entries (Gap 5).

Per FINDINGS #18 Gap 5 + Research Cycle #26 Q3 sequence (Gap 5 FIRST):
substrate needs atom-level provenance for methodology rule calibration +
recent_lifts traversal + substrate-as-metacognition self-improvement loop.

Each capability atom has solution_history entries:
    {solution_atom_id, adopted_date, replaced_date, replacement_reason,
     empirical_metric, source, status}

This tool adds `atoms_used: List[atom_id]` derived from the solution atom's:
1. concept_links (cross-corpus atom_ids the solution explicitly references)
2. decomposes_to (sub-ops the solution composes)
3. outgoing USES / USES_SUBPROC / DEPENDS_ON edges

The result: "when capability X lifted +0.85 via solution_atom_id S on date D,
which atoms were load-bearing in that solution?" -- atoms_used answers it.

NO encoder load; pure index walk. Local-allowed per all-cpu-compute-remote rule.

Usage:
    python tools/substrate_backfill_atoms_used.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("backfill_atoms_used")

DATA_ROOT = Path("data/substrate_index")

_INFER_EDGE_TYPES = {RelationType.USES, RelationType.USES_SUBPROC,
                     RelationType.DEPENDS_ON, RelationType.COMPOSES}


def _resolve_solver(pstore: PartitionedStore, sol_id: str):
    """sol_id may be qualified (math::T2/foo) or bare (T2/foo). Resolve."""
    if pstore.has_atom(sol_id):
        return pstore.get_atom(sol_id)
    bare = sol_id.split("::", 1)[-1]
    for corpus_name in ("math", "concept", "meta", "school", "methodology", "science"):
        trial = f"{corpus_name}::{bare}"
        if pstore.has_atom(trial):
            return pstore.get_atom(trial)
    return None


def infer_atoms_used(pstore: PartitionedStore, solver_atom: Atom) -> list[str]:
    """Derive load-bearing atoms from the solver atom's structure.

    Sources of evidence (union):
    - concept_links (explicit cross-corpus references)
    - metadata.decomposes_to (sub-ops the solver wires together)
    - outgoing typed edges (USES / USES_SUBPROC / DEPENDS_ON / COMPOSES)
    """
    atoms_used = set()
    for cl in (solver_atom.concept_links or []):
        atoms_used.add(cl)
    for dt in solver_atom.metadata.get("decomposes_to", []) or []:
        atoms_used.add(dt)
    # outgoing edges
    for rel_type in _INFER_EDGE_TYPES:
        for tgt in pstore.out_neighbors(solver_atom.qualified_id, rel_type):
            atoms_used.add(tgt)
    return sorted(atoms_used)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-backfill: %d atoms", len(pstore.all_atoms()))

    capability_atoms = [a for a in pstore.all_atoms()
                        if a.current_best_solution or a.solution_history]
    log.info("capability atoms with solution_history: %d", len(capability_atoms))

    n_caps_updated = 0
    n_entries_updated = 0
    n_entries_already = 0
    n_solver_missing = 0
    all_atoms_used_examples = []

    for cap in capability_atoms:
        new_history = []
        history_changed = False
        for entry in cap.solution_history:
            entry = dict(entry)
            if "atoms_used" in entry and entry["atoms_used"]:
                n_entries_already += 1
                new_history.append(entry)
                continue
            sol_id = entry.get("solution_atom_id")
            if not sol_id:
                new_history.append(entry)
                continue
            solver = _resolve_solver(pstore, sol_id)
            if solver is None:
                n_solver_missing += 1
                new_history.append(entry)
                continue
            atoms_used = infer_atoms_used(pstore, solver)
            entry["atoms_used"] = atoms_used
            n_entries_updated += 1
            history_changed = True
            if len(all_atoms_used_examples) < 5:
                all_atoms_used_examples.append({
                    "cap": cap.qualified_id, "sol": sol_id,
                    "atoms_used": atoms_used[:8],
                })
            new_history.append(entry)
        if history_changed and not args.dry_run:
            new_atom = Atom(
                id=cap.id, name=cap.name, corpus=cap.corpus, tier=cap.tier,
                description=cap.description, kind=cap.kind, aliases=cap.aliases,
                metadata=cap.metadata, algebra=cap.algebra, signature=cap.signature,
                complexity=cap.complexity, equivalences=cap.equivalences,
                concept_links=cap.concept_links,
                current_best_solution=cap.current_best_solution,
                solution_history=tuple(new_history),
                serves_capability=cap.serves_capability,
            )
            pstore.add_atom(new_atom, source="backfill_atoms_used",
                            note=f"backfilled atoms_used on {sum(1 for h in new_history if h.get('atoms_used'))} entries")
            n_caps_updated += 1

    print("\n" + "=" * 78)
    print(f"GAP 5 BACKFILL {'DRY-RUN' if args.dry_run else 'APPLIED'}")
    print("=" * 78)
    print(json.dumps({
        "n_capability_atoms": len(capability_atoms),
        "n_caps_updated": n_caps_updated,
        "n_entries_updated": n_entries_updated,
        "n_entries_already": n_entries_already,
        "n_solver_missing": n_solver_missing,
    }, indent=2))

    print(f"\nExamples (first 5):")
    for ex in all_atoms_used_examples:
        print(f"  {ex['cap']:50s} via {ex['sol']:35s}")
        print(f"    atoms_used: {ex['atoms_used']}")

    out = DATA_ROOT / "bench_reports" / f"backfill_atoms_used_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "dry_run": args.dry_run,
        "stats": {
            "n_caps": len(capability_atoms),
            "n_caps_updated": n_caps_updated,
            "n_entries_updated": n_entries_updated,
            "n_entries_already": n_entries_already,
            "n_solver_missing": n_solver_missing,
        },
        "examples": all_atoms_used_examples,
    }, indent=2), encoding="utf-8")
    log.info("wrote report -> %s", out)


if __name__ == "__main__":
    main()
