#!/usr/bin/env python3
"""Item 4 catalog audit: scour all AUDIT_LESSON atoms + verify composes_with /
parent_of / strengthens cross-refs RESOLVE to real atoms (the value-RESOLVES
discipline applied to the AUDIT_LESSON catalog itself). + categorize by
referent-class + reconcile duplicate instance_numbers + surface conceptual-
shorthand cross-refs.

Per Skunkworks 3rd 20h sprint Item 4 + post-unfreeze worklist handoff.
"""
import json
import re
from pathlib import Path
from collections import defaultdict, Counter


ROOT = Path("data/substrate_index")


def load_atoms(kind=None):
    """Yield (corpus, atom_dict) for every atom (optionally of given kind)."""
    for atoms_file in ROOT.glob("*/atoms.jsonl"):
        corpus = atoms_file.parent.name
        with atoms_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if kind is None or a.get("kind") == kind:
                    yield corpus, a


def load_qualified_ids():
    """Build set of all qualified_ids (corpus::id) + bare ids."""
    qids = set()
    bare = {}
    for atoms_file in ROOT.glob("*/atoms.jsonl"):
        corpus = atoms_file.parent.name
        with atoms_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                aid = a.get("id")
                if not aid:
                    continue
                qid = f"{corpus}::{aid}"
                qids.add(qid)
                bare.setdefault(aid, set()).add(qid)
    return qids, bare


def resolve(value, qids, bare):
    if not value:
        return ("empty", None)
    if value in qids:
        return ("qualified", value)
    if value in bare:
        cands = bare[value]
        if len(cands) == 1:
            return ("bare", next(iter(cands)))
        return ("bare_ambiguous", sorted(cands))
    for c in ("math", "concept", "meta", "school", "science",
              "research_history", "decision_history", "findings_history",
              "verdict_history", "results_history", "methodology"):
        cand = f"{c}::{value}"
        if cand in qids:
            return ("corpus_inferred", cand)
    return ("phantom", None)


# Recognized AUDIT_LESSON referent-classes (manual taxonomy from substrate text)
REFERENT_CLASSES = {
    "verify_the_referent": ["verify_the_referent", "verify-the-referent",
                            "verify_referent", "VERIFY_THE_REFERENT"],
    "negativity_bias_symmetric": ["NEGATIVITY_BIAS", "negativity_bias",
                                  "negativity-bias-symmetric"],
    "corpus_completeness": ["corpus_completeness", "CORPUS_COMPLETENESS"],
    "degenerate_regime": ["DEGENERATE_REGIME", "degenerate_regime"],
    "discrimination_regime": ["discrimination_regime", "DISCRIMINATION_REGIME"],
    "actual_not_bar": ["actual_not_bar", "actual-not-bar", "ACTUAL_NOT_BAR"],
    "no_self_certify": ["no_self_certify", "no-self-certify-by-fiat"],
    "edge_metadata_drop": ["metadata_drop", "metadata-drop",
                           "first_class_rel_type"],
    "checkpoint_resume": ["checkpoint_resume", "checkpoint-resume",
                          "long_cells", "kill_restart"],
    "atom_add_mechanism": ["atom_add_mechanism", "atom-add-mechanism",
                           "batched_add"],
    "device_exercise": ["device_exercise", "GPU_routed_not_exercised",
                        "device-exercise"],
    "cert_architecture_separation": ["cert_architecture",
                                     "engine_checklist_separation",
                                     "engine/checklist"],
    "value_resolves": ["value_resolves", "value-RESOLVES",
                       "5_layer_verify_referent"],
}


def classify_lesson(name, desc, md):
    text = " ".join([name or "", desc or "", json.dumps(md or {})]).lower()
    matches = []
    for cls, kws in REFERENT_CLASSES.items():
        for kw in kws:
            if kw.lower() in text:
                matches.append(cls)
                break
    return matches


def main():
    lessons = list(load_atoms("audit_lesson"))
    print(f"AUDIT_LESSON atoms total: {len(lessons)}")
    print()

    qids, bare = load_qualified_ids()
    print(f"Total qualified_ids in Store: {len(qids)}")
    print()

    # ---- Instance number reconciliation ----
    instances = defaultdict(list)
    for corpus, a in lessons:
        md = a.get("metadata") or {}
        inst = md.get("instance_number")
        if inst is not None:
            instances[inst].append(a["id"])

    dup_instances = {k: v for k, v in instances.items() if len(v) > 1}
    print("=" * 80)
    print("PART 1: DUPLICATE instance_numbers (Item-4 cleanup queue; Skunkworks-offered)")
    print("=" * 80)
    print(f"Distinct instance_numbers: {len(instances)}")
    print(f"Duplicates: {len(dup_instances)}")
    for inst, atom_ids in sorted(dup_instances.items()):
        print(f"  instance_number={inst}  -> {len(atom_ids)} atoms: {atom_ids}")
    print()

    # ---- Cross-ref resolution ----
    REF_FIELDS = ["composes_with", "parent_of", "strengthens", "supersedes",
                  "child_of", "siblings", "composes_with_siblings", "depends_on"]

    cross_refs = []
    for corpus, a in lessons:
        md = a.get("metadata") or {}
        for field in REF_FIELDS:
            val = a.get(field) or md.get(field)
            if val is None:
                continue
            if isinstance(val, str):
                vals = [val]
            elif isinstance(val, list):
                vals = [str(v) for v in val if v]
            else:
                continue
            for v in vals:
                cross_refs.append({
                    "lesson_id": a["id"],
                    "field": field,
                    "value": v,
                })

    print("=" * 80)
    print("PART 2: composes_with / parent_of / strengthens RESOLUTION")
    print("=" * 80)
    print(f"Total cross-refs: {len(cross_refs)}")
    print()

    by_status = defaultdict(list)
    for ref in cross_refs:
        status, resolved = resolve(ref["value"], qids, bare)
        ref["status"] = status
        ref["resolved"] = resolved
        by_status[status].append(ref)

    print("By resolution status:")
    for status, refs in sorted(by_status.items(), key=lambda kv: -len(kv[1])):
        print(f"  {status:25s}  {len(refs)}")
    print()

    # Phantom + conceptual-shorthand detection
    phantoms = by_status.get("phantom", [])
    print(f"PHANTOMS ({len(phantoms)}): cross-refs that don't resolve to any atom")
    print("(Skunkworks Item-4 worklist: '34 conceptual cross-refs + 8 expected memory-file refs')")
    print()

    # Categorize phantoms: memory-file-ref vs conceptual-shorthand vs unknown
    memory_file_pat = re.compile(r"^[a-z_]+_\d{4}-\d{2}-\d{2}", re.IGNORECASE)
    conceptual_pat = re.compile(r"^[A-Z_]{4,}$|_meta_lens|_NOT_REFUTATION|_SYMMETRIC$|^USER_LOCKED|_DIRECTIVE_|_DISCIPLINE")
    memory_refs = []
    conceptual_refs = []
    unknown_phantoms = []
    for p in phantoms:
        v = p["value"]
        if memory_file_pat.search(v) or "MEMORY" in v.upper() or v.endswith(".md"):
            memory_refs.append(p)
        elif conceptual_pat.search(v) or v.isupper() or "_meta_lens" in v or "_NOT_" in v:
            conceptual_refs.append(p)
        else:
            unknown_phantoms.append(p)

    print(f"  memory-file refs (expected; not atom-refs): {len(memory_refs)}")
    print(f"  conceptual shorthand (categorize/mark): {len(conceptual_refs)}")
    print(f"  unknown phantoms (investigate): {len(unknown_phantoms)}")
    print()

    if unknown_phantoms:
        print("Unknown phantoms (first 20):")
        for p in unknown_phantoms[:20]:
            print(f"  {p['lesson_id']}.{p['field']} = '{p['value']}'")
        if len(unknown_phantoms) > 20:
            print(f"  ... + {len(unknown_phantoms) - 20} more")
        print()

    if conceptual_refs:
        print("Conceptual shorthand sample (first 15):")
        for p in conceptual_refs[:15]:
            print(f"  {p['lesson_id']}.{p['field']} = '{p['value']}'")
        if len(conceptual_refs) > 15:
            print(f"  ... + {len(conceptual_refs) - 15} more")
        print()

    # ---- Referent-class taxonomy ----
    print("=" * 80)
    print("PART 3: REFERENT-CLASS taxonomy (categorization)")
    print("=" * 80)

    class_counts = Counter()
    no_class = []
    multi_class = []
    for corpus, a in lessons:
        matches = classify_lesson(a.get("name"), a.get("description"), a.get("metadata"))
        if not matches:
            no_class.append(a["id"])
            class_counts["UNCLASSIFIED"] += 1
        else:
            for m in matches:
                class_counts[m] += 1
            if len(matches) > 1:
                multi_class.append((a["id"], matches))

    print("By referent-class (atoms can match multiple):")
    for cls, n in class_counts.most_common():
        print(f"  {cls:35s} {n}")
    print()
    print(f"Multi-class (overlap; first 10):")
    for atom_id, classes in multi_class[:10]:
        print(f"  {atom_id}: {classes}")
    print()
    print(f"UNCLASSIFIED ({len(no_class)}; not matching any of {len(REFERENT_CLASSES)} taxonomy classes):")
    for aid in no_class[:15]:
        print(f"  {aid}")
    if len(no_class) > 15:
        print(f"  ... + {len(no_class) - 15} more")
    print()

    # ---- Output ----
    out = {
        "scour_ts": "2026-06-19",
        "audit_lesson_total": len(lessons),
        "instance_dup_count": len(dup_instances),
        "instance_dups": {str(k): v for k, v in dup_instances.items()},
        "cross_ref_total": len(cross_refs),
        "cross_ref_by_status": {k: len(v) for k, v in by_status.items()},
        "phantoms_total": len(phantoms),
        "phantom_memory_file_refs": len(memory_refs),
        "phantom_conceptual_shorthand": len(conceptual_refs),
        "phantom_unknown": len(unknown_phantoms),
        "referent_class_counts": dict(class_counts),
        "unclassified_count": len(no_class),
    }
    print("=" * 80)
    print("SUMMARY (Item 4 catalog audit output for Skunkworks reactive)")
    print("=" * 80)
    print(json.dumps(out, indent=2))

    out_path = Path("data/audit_lesson_catalog_audit_2026-06-19.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print()
    print(f"Inventory written: {out_path}")


if __name__ == "__main__":
    main()
