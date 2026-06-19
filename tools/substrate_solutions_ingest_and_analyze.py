"""Ingest solution-history JSONL into capability atoms + run all 7 queries.

Per user direction 2026-06-11 late evening: each capability has a current-best
mathematical solution; replacements DO NOT delete the old, they're marked
obsolete. This populates that history for 14 well-documented capabilities
and runs substrate-internal analyses on the resulting graph.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dataclasses import replace as dc_replace

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType
from backend.substrate_index.solutions import (
    cliff_detector,
    cross_capability_best_overlap,
    current_best_table,
    replacement_prediction,
    revert_history,
    solution_lineage,
    stale_solutions,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("solutions_run")

DATA_ROOT = Path("data/substrate_index")
JSONL = DATA_ROOT / "concept_corpus_solution_histories.jsonl"


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-ingest: %d atoms", len(pstore.all_atoms()))

    # Ingest / update capability atoms with solution_history
    updated = added = 0
    supersedes_added = 0
    with JSONL.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                new_atom = Atom.from_dict(rec)
            except Exception as e:
                log.error("line %d: %s", line_no, e)
                continue
            existing = pstore.get_atom(new_atom.qualified_id)
            if existing is None:
                pstore.add_atom(new_atom, source="solution_histories",
                                note="Capability + solution history hand-authored from memory + cap_map")
                added += 1
            else:
                # Patch fields onto existing atom
                merged = dc_replace(
                    existing,
                    current_best_solution=new_atom.current_best_solution or existing.current_best_solution,
                    solution_history=new_atom.solution_history or existing.solution_history,
                )
                pstore.remove_atom(new_atom.qualified_id, source="solution_histories",
                                   note="updating with solution_history")
                pstore.add_atom(merged, source="solution_histories",
                                note="solution_history field populated")
                updated += 1

            # Wire SUPERSEDES relations between consecutive solutions
            entries = list(new_atom.solution_history)
            entries.sort(key=lambda e: e.get("adopted_date") or "")
            for i in range(1, len(entries)):
                old_id = entries[i - 1].get("solution_atom_id")
                new_id = entries[i].get("solution_atom_id")
                if old_id and new_id and old_id != new_id:
                    try:
                        pstore.add_relation(new_id, RelationType.SUPERSEDES, old_id,
                                            source="solution_histories",
                                            note=f"in {new_atom.qualified_id}")
                        supersedes_added += 1
                    except Exception:
                        pass

    log.info("ingest: added=%d updated=%d supersedes_added=%d", added, updated, supersedes_added)

    # ============================================================
    # Run 7 queries
    # ============================================================
    print("\n" + "=" * 80)
    print("SOLUTION-HISTORY ANALYSIS on substrate's capability atoms")
    print("=" * 80)

    # Q1: current_best_table
    cbt = current_best_table(pstore)
    capabilities_with_solutions = {k: v for k, v in cbt.items() if v is not None}
    print(f"\n--- Q1: current_best_table ({len(capabilities_with_solutions)} capabilities with current-best) ---")
    for cap, sol in sorted(capabilities_with_solutions.items()):
        sol_short = sol.split("::")[-1] if sol else None
        cap_short = cap.split("::")[-1]
        print(f"  {cap_short:<40s}  -> {sol_short}")

    # Q3: cross_capability_best_overlap (universal levers)
    overlap = cross_capability_best_overlap(pstore)
    universal_levers = {sol: caps for sol, caps in overlap.items() if len(caps) >= 3}
    print(f"\n--- Q3: cross_capability_best_overlap (universal levers: solutions current-best for >=3 capabilities) ---")
    for sol, caps in overlap.items():
        sol_short = sol.split("::")[-1]
        marker = " *UNIVERSAL LEVER*" if len(caps) >= 3 else ""
        print(f"  {sol_short:<40s}  {len(caps):3d} capabilities{marker}")
        if len(caps) >= 3:
            for c in caps:
                print(f"      - {c.split('::')[-1]}")

    # Q6: cliff_detector
    cliffs = cliff_detector(pstore, min_lift=0.10)
    print(f"\n--- Q6: cliff_detector (single-step replacements with lift >= 0.10) ---")
    for c in cliffs[:20]:
        cap_short = c.capability_qualified_id.split("::")[-1]
        from_short = c.from_solution.split("::")[-1]
        to_short = c.to_solution.split("::")[-1]
        print(f"  +{c.lift:.3f} ({c.metric_name})  {cap_short}")
        print(f"    {from_short} -> {to_short}  (cliff_score {c.cliff_score:.3f}; {c.source})")

    # Q5: revert_history
    reverts = revert_history(pstore)
    print(f"\n--- Q5: revert_history ({len(reverts)} REVERTED entries) ---")
    for r in reverts:
        cap_short = r.capability_qualified_id.split("::")[-1]
        sol_short = r.reverted_solution.split("::")[-1]
        print(f"  {cap_short}: reverted {sol_short}")
        print(f"    reason: {r.reason}")
        print(f"    source: {r.source}")

    # Q4: stale_solutions
    stale = stale_solutions(pstore, days_threshold=15)
    print(f"\n--- Q4: stale_solutions (current-best not challenged in >=15 days) ---")
    for s in stale[:15]:
        cap_short = s.capability_qualified_id.split("::")[-1]
        sol_short = s.current_best.split("::")[-1] if s.current_best else None
        print(f"  {cap_short}  ({sol_short})  adopted {s.adopted_date}  {s.days_since_adopted}d ago")

    # Q7: replacement_prediction on capabilities whose current-best is NOT
    # the dominant universal lever
    universal_lever_ids = {sol for sol, caps in overlap.items() if len(caps) >= 3}
    print(f"\n--- Q7: replacement_prediction for capabilities with non-lever current-best ---")
    prediction_count = 0
    for cap_id in cbt:
        cur = cbt[cap_id]
        if not cur or cur in universal_lever_ids:
            continue
        pred = replacement_prediction(pstore, cap_id)
        if pred is not None and pred.pattern_strength >= 0.5:
            prediction_count += 1
            cap_short = cap_id.split("::")[-1]
            old_short = cur.split("::")[-1]
            new_short = pred.predicted_replacement.split("::")[-1]
            print(f"  {cap_short}: predict {old_short} -> {new_short}")
            print(f"    strength={pred.pattern_strength:.2f}; evidence={[e.split('::')[-1] for e in pred.pattern_evidence]}")
    if prediction_count == 0:
        print(f"  (no high-strength predictions; either all caps already use a universal lever or insufficient cross-capability data)")

    # Persist
    stats = pstore.stats()
    out = DATA_ROOT / "bench_reports" / f"solution_histories_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "ingest": {"added": added, "updated": updated, "supersedes_relations": supersedes_added},
        "post_atoms": stats["total_atoms"],
        "post_relations": stats["total_relations"],
        "current_best_table": cbt,
        "universal_levers": {k: v for k, v in overlap.items() if len(v) >= 3},
        "cliffs": [c.to_dict() for c in cliffs[:30]],
        "reverts": [r.to_dict() for r in reverts],
        "stale": [s.to_dict() for s in stale],
    }, indent=2), encoding="utf-8")
    log.info("wrote analysis report -> %s", out)


if __name__ == "__main__":
    main()
