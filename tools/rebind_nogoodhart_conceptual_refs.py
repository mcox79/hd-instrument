#!/usr/bin/env python3
"""Re-bind 4 no-Goodhart conceptual_references to inst-239 (now exists).

Per Skunkworks's per-bind VET (2026-06-19) + Skunkworks's reaffirmation
post-inst-239-atomize: the no-Goodhart concept-refs were correctly-unbound
because no AUDIT_LESSON existed for the discipline. Inst-239 now anchors it.

The 4 unbound refs to re-bind:
- 'no_goodhart' (in AUDIT_LESSON catalog)
- 'no_goodhart_anchor_layer' (in AUDIT_LESSON catalog)
- 'no_goodhart_metric_measures_claimed_thing' (AUDIT + METHODOLOGY_RULE catalog)

Target backing atom:
- AUDIT_no_goodhart_metric_measures_claimed_thing_target_corrupts_measure (inst 239)

Pattern (safe metadata-patch per Skunkworks's refined write-hold posture):
- Load each AUDIT_LESSON + METHODOLOGY_RULE atom
- Find conceptual_references entries with no_goodhart-family value + backing=None
- Set backing_atom_proposed = inst-239 atom-id; confidence_score = 99 (Skunkworks-VET-approved)
- Raw-JSONL rewrite + Store-LOAD verify (per inst-240's rule).
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

INST_239_ID = ("AUDIT_no_goodhart_metric_measures_claimed_thing_"
               "target_corrupts_measure")

NO_GOODHART_VALUES = {
    "no_goodhart",
    "no_goodhart_anchor_layer",
    "no_goodhart_metric_measures_claimed_thing",
}


def rebind_partition(partition_path):
    tmp = partition_path.with_suffix(".jsonl.tmp")
    n_rebinds = 0
    n_atoms_patched = 0
    n_lines = 0
    rebind_log = []
    with partition_path.open(encoding="utf-8") as src, \
         tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            stripped = line.strip()
            if not stripped:
                dst.write(line)
                continue
            try:
                a = json.loads(stripped)
            except json.JSONDecodeError:
                dst.write(line)
                continue
            n_lines += 1
            if a.get("kind") not in ("audit_lesson", "methodology_rule"):
                dst.write(line)
                continue
            md = a.get("metadata") or {}
            crefs = md.get("conceptual_references") or []
            patched_this = False
            for entry in crefs:
                if not isinstance(entry, dict):
                    continue
                val = entry.get("value")
                if val not in NO_GOODHART_VALUES:
                    continue
                if entry.get("backing_atom_proposed"):
                    continue
                entry["backing_atom_proposed"] = INST_239_ID
                entry["confidence_score"] = 99
                entry["source_tag"] = "skunkworks_vet_post_inst_239_atomize"
                entry["note"] = (
                    "Re-bound to inst-239 (no-Goodhart discipline atom; "
                    "atomized 2026-06-19) -- was correctly-unbound previously "
                    "because no AUDIT_LESSON existed; now the target exists."
                )
                n_rebinds += 1
                patched_this = True
                rebind_log.append({
                    "atom_id": a["id"], "ref_value": val,
                })
            if patched_this:
                md["conceptual_references"] = crefs
                a["metadata"] = md
                n_atoms_patched += 1
            dst.write(json.dumps(a, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_rebinds, n_atoms_patched, n_lines, rebind_log


def store_load_verify():
    try:
        from backend.substrate_index.partition import PartitionedStore
    except ImportError as e:
        return False, f"PartitionedStore import failed: {e}"
    try:
        ps = PartitionedStore(ROOT)
        atoms = list(ps.all_atoms())
        return True, f"PASS ({len(atoms)} atoms; Atom.from_dict round-trip clean)"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    print("=" * 80)
    print("RE-BIND no-Goodhart conceptual_references to inst-239")
    print("=" * 80)
    print(f"Target backing: {INST_239_ID}")
    print(f"Values to re-bind: {NO_GOODHART_VALUES}")
    print()

    total_rebinds = 0
    total_atoms = 0
    all_log = []
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n_rebinds, n_atoms, n_lines, log = rebind_partition(partition_path)
        if n_atoms:
            total_rebinds += n_rebinds
            total_atoms += n_atoms
            all_log.extend(log)
            print(f"  {partition_path.parent.name}/atoms.jsonl: "
                  f"{n_atoms} atoms patched / {n_rebinds} refs re-bound "
                  f"({n_lines} total lines)")

    print()
    print(f"TOTAL: {total_atoms} atoms patched / {total_rebinds} refs re-bound")
    print()
    if all_log:
        print("Re-bind details:")
        for entry in all_log:
            print(f"  {entry['atom_id'][:60]:60s} -> '{entry['ref_value']}'")
    print()

    print("=" * 80)
    print("STORE-LOAD verify (per inst-240's rule + Exp-Dev pattern)")
    print("=" * 80)
    ok, msg = store_load_verify()
    print(f"  {msg}")
    if not ok:
        print("FAILED Store-LOAD gate. INVESTIGATE.")
        return
    print()
    print("RE-BIND COMPLETE. Route to Skunkworks for landed-VET (S4 should now")
    print(f"show {total_rebinds} additional bound + correspondingly fewer unbound).")


if __name__ == "__main__":
    main()
