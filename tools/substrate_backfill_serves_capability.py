"""Backfill `serves_capability` field on existing math/concept atoms.

Per FINDINGS #18 usability gap analysis 2026-06-11 + USER green-light:
substrate must know which capabilities each atom serves so retrieval can be
capability-anchored, not just semantic.

Strategy (substrate-on-substrate, no LLM-as-judge):

1. Identify CAPABILITY atoms: concept atoms whose id starts with `cap_` OR
   whose metadata has solution_history populated (these ARE the capabilities).

2. For each capability atom, scan its `solution_history` -- each entry has
   `solution_atom_id` which points to a math/algorithm primitive. Reverse-map:
   that math primitive SERVES this capability.

3. Additionally use `current_best_solution` field directly.

4. Cross-corpus: capability concept atoms point to math primitives by
   qualified id (math::T2/fhrr_bind etc.).

5. Update math atoms' `serves_capability` field with the union of all
   capabilities whose solution_history references them.

6. Report coverage: how many math atoms now have serves_capability? Universal
   levers (e.g. discriminative_perceptron) should show up serving 5+ caps.

Per rule 8 us-or-substrate: this is substrate-self-inference (substrate reads
its own solution_history to backfill its own reverse index). No external LLM.

Usage:
    python tools/substrate_backfill_serves_capability.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("backfill_serves_capability")

DATA_ROOT = Path("data/substrate_index")


def identify_capability_atoms(pstore: PartitionedStore) -> list[Atom]:
    """A capability atom is one with non-empty solution_history OR
    current_best_solution. Concept partition is the natural home for these."""
    out = []
    for atom in pstore.all_atoms():
        if atom.current_best_solution or atom.solution_history:
            out.append(atom)
    return out


def build_reverse_index(cap_atoms: list[Atom]) -> dict[str, set[str]]:
    """Returns map: solver_atom_qualified_id -> set of capability_qualified_ids
    that the solver serves (per any entry in solution_history or current_best_solution).
    """
    reverse: dict[str, set[str]] = defaultdict(set)
    for cap in cap_atoms:
        cap_qid = cap.qualified_id
        if cap.current_best_solution:
            reverse[cap.current_best_solution].add(cap_qid)
        for entry in cap.solution_history:
            sol_id = entry.get("solution_atom_id")
            if sol_id:
                reverse[sol_id].add(cap_qid)
    return reverse


def apply_backfill(pstore: PartitionedStore, reverse: dict[str, set[str]],
                   dry_run: bool) -> dict:
    """For each solver atom in the reverse index, write its serves_capability
    field (union of new + existing)."""
    stats = {
        "atoms_examined": 0,
        "atoms_updated": 0,
        "atoms_no_match": 0,
        "atoms_already_complete": 0,
        "solvers_missing": [],
    }
    for solver_qid, cap_set in reverse.items():
        # solver_qid may be qualified (math::T2/foo) or bare (T2/foo)
        atom = pstore.get_atom(solver_qid) if pstore.has_atom(solver_qid) else None
        if atom is None:
            # Try bare-id fallback across partitions
            bare = solver_qid.split("::", 1)[-1]
            for corpus_name in ("math", "concept", "meta", "school"):
                trial = f"{corpus_name}::{bare}"
                if pstore.has_atom(trial):
                    atom = pstore.get_atom(trial)
                    solver_qid = trial
                    break
        if atom is None:
            stats["solvers_missing"].append(solver_qid)
            stats["atoms_no_match"] += 1
            continue
        stats["atoms_examined"] += 1
        existing = set(atom.serves_capability)
        new = existing | cap_set
        if new == existing:
            stats["atoms_already_complete"] += 1
            continue
        if not dry_run:
            updated_atom = Atom(
                id=atom.id,
                name=atom.name,
                corpus=atom.corpus,
                tier=atom.tier,
                description=atom.description,
                kind=atom.kind,
                aliases=atom.aliases,
                metadata=atom.metadata,
                algebra=atom.algebra,
                signature=atom.signature,
                complexity=atom.complexity,
                equivalences=atom.equivalences,
                concept_links=atom.concept_links,
                current_best_solution=atom.current_best_solution,
                solution_history=atom.solution_history,
                serves_capability=tuple(sorted(new)),
            )
            pstore.add_atom(updated_atom, source="backfill_serves_capability",
                            note=f"Backfilled serves_capability from {len(cap_set)} capability solution_histories")
        stats["atoms_updated"] += 1
    return stats


def report_universal_levers(pstore: PartitionedStore, top_n: int = 15) -> list[tuple[str, int, list[str]]]:
    """List atoms sorted by number of capabilities they serve."""
    out = []
    for atom in pstore.all_atoms():
        n = len(atom.serves_capability)
        if n > 0:
            out.append((atom.qualified_id, n, list(atom.serves_capability)))
    out.sort(key=lambda x: -x[1])
    return out[:top_n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Report only; do not write")
    ap.add_argument("--report-only", action="store_true", help="Just report current state")
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-backfill: %d total atoms", len(pstore.all_atoms()))

    if args.report_only:
        levers = report_universal_levers(pstore)
        print("\nCurrent serves_capability state:")
        for qid, n, caps in levers:
            print(f"  {qid}: serves {n} cap(s)")
            for c in caps[:5]:
                print(f"    - {c}")
        return

    cap_atoms = identify_capability_atoms(pstore)
    log.info("identified %d capability atoms (with solution_history or current_best_solution)",
             len(cap_atoms))

    reverse = build_reverse_index(cap_atoms)
    log.info("reverse index: %d distinct solver atoms referenced", len(reverse))

    stats = apply_backfill(pstore, reverse, dry_run=args.dry_run)

    print("\n" + "=" * 78)
    print(f"BACKFILL {'DRY-RUN' if args.dry_run else 'APPLIED'}")
    print("=" * 78)
    print(json.dumps({k: v for k, v in stats.items() if k != "solvers_missing"},
                     indent=2))
    if stats["solvers_missing"]:
        print(f"\n{len(stats['solvers_missing'])} solver references could not be matched:")
        for s in stats["solvers_missing"][:10]:
            print(f"  - {s}")

    levers = report_universal_levers(pstore)
    print("\nTop atoms by capabilities served (universal levers surface here):")
    for qid, n, caps in levers[:10]:
        print(f"  {qid:55s}  serves {n} cap(s)")

    out = DATA_ROOT / "bench_reports" / f"backfill_serves_capability_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "dry_run": args.dry_run,
        "stats": stats,
        "top_levers": [{"atom": q, "n_caps": n, "caps": c} for q, n, c in levers],
    }, indent=2), encoding="utf-8")
    log.info("wrote backfill report -> %s", out)


if __name__ == "__main__":
    main()
