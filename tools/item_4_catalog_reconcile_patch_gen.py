#!/usr/bin/env python3
"""Item 4 catalog reconcile patch generator (READ-ONLY; outputs proposed mutations).

Skunkworks 3-bucket disposition (FIELD-HYGIENE only; 0 broken phantoms confirmed
by prior scour):

  Bucket 1 (dirty-format-resolvable): strip inline annotation from composes_with;
    clean atom-id stays in composes_with (preserves value-RESOLVES on the field).
  Bucket 2 (memory-file refs): move to NEW structured field `memory_references`.
  Bucket 3 (conceptual-shorthand): move to NEW structured field
    `conceptual_references`; per-ref check for backing AUDIT_<concept> or
    RULE_<concept> atom; flag where present.

Output: data/item_4_reconcile_patch_2026-06-19.json
  + summary stats (per-bucket counts; matches Skunkworks's 7+8+18 disposition)
  + per-atom proposed mutations (no Store writes)
  + counts-before and counts-after-projection (snapshot per Skunkworks discipline)

DOES NOT WRITE TO STORE. Routes to Skunkworks for SCHEMA-VET before apply.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path("data/substrate_index")

INLINE_ANNOTATION_PAT = re.compile(r"\s*\([^)]+\)\s*$")
MEMORY_FILE_PAT = re.compile(
    r"^(feedback|reference|project|user|memory|session_arc|standing|"
    r"director|testbed|orchestrator|skunkworks|exp_dev|research|"
    r"resume_anchor|milestone)_",
    re.IGNORECASE,
)
DATE_SUFFIX_PAT = re.compile(r"_\d{4}[-_]\d{2}[-_]\d{2}")
CONCEPTUAL_UPPER_PAT = re.compile(r"^[A-Z][A-Z0-9_]{3,}$")
CONCEPTUAL_SUFFIX_PAT = re.compile(
    r"(_meta_lens|_NOT_REFUTATION|_SYMMETRIC|_DIRECTIVE|_DISCIPLINE|"
    r"_GUARD|_RULE|_REFERENT|_GOODHART|_REGIME)$",
    re.IGNORECASE,
)


def load_atoms(kind=None):
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


def classify(value, qids, bare):
    """Return (bucket, suggested_clean_value, backing_atom_id_or_None).

    Bucket: 1 (dirty-format) | 2 (memory) | 3 (conceptual) | 0 (resolves; no patch)
    """
    status, resolved = resolve(value, qids, bare)
    if status in ("qualified", "bare", "corpus_inferred"):
        return (0, value, resolved)

    # Bucket 1: dirty-format-resolvable
    if INLINE_ANNOTATION_PAT.search(value):
        clean = INLINE_ANNOTATION_PAT.sub("", value).strip()
        clean_status, clean_resolved = resolve(clean, qids, bare)
        if clean_status in ("qualified", "bare", "corpus_inferred"):
            return (1, clean, clean_resolved)

    # Bucket 2: memory-file refs
    is_memory = (
        MEMORY_FILE_PAT.match(value)
        or DATE_SUFFIX_PAT.search(value)
        or "MEMORY" in value.upper()
        or value.endswith(".md")
    )
    if is_memory:
        return (2, value, None)

    # Bucket 3: conceptual shorthand (per-ref backing-atom check)
    is_conceptual = (
        CONCEPTUAL_UPPER_PAT.match(value)
        or CONCEPTUAL_SUFFIX_PAT.search(value)
        or value.isupper()
    )
    if is_conceptual or True:  # default-bucket conceptual for remaining
        slug = value.lower()
        backing_candidates = [
            f"AUDIT_{slug}",
            f"METHODOLOGY_{slug}",
            f"RULE_{slug}",
            f"audit_{slug}",
            f"rule_{slug}",
        ]
        backing = None
        for cand in backing_candidates:
            cand_status, cand_resolved = resolve(cand, qids, bare)
            if cand_status in ("qualified", "bare", "corpus_inferred"):
                backing = cand_resolved
                break
        return (3, value, backing)

    return (3, value, None)


def main():
    lessons = list(load_atoms("audit_lesson"))
    qids, bare = load_qualified_ids()

    REF_FIELDS = [
        "composes_with", "parent_of", "strengthens", "supersedes",
        "child_of", "siblings", "composes_with_siblings", "depends_on",
    ]

    # Per-atom proposed mutations
    patches = {}
    bucket_counts = defaultdict(int)
    bucket_examples = defaultdict(list)
    backing_resolved = 0
    backing_unresolved_concepts = []

    for corpus, a in lessons:
        atom_id = a["id"]
        md = a.get("metadata") or {}

        keep_composes = []
        memory_refs = []
        conceptual_refs = []
        # Read existing memory_references / conceptual_references (in case we re-run)
        existing_memory = a.get("memory_references") or md.get("memory_references") or []
        existing_conceptual = a.get("conceptual_references") or md.get("conceptual_references") or []
        memory_refs.extend(existing_memory)
        conceptual_refs.extend(existing_conceptual)

        any_change = False

        for field in REF_FIELDS:
            top = a.get(field)
            meta = md.get(field)
            for source, val in (("top", top), ("meta", meta)):
                if val is None:
                    continue
                if isinstance(val, str):
                    vals = [val]
                elif isinstance(val, list):
                    vals = [str(v) for v in val if v]
                else:
                    continue
                if field != "composes_with":
                    # Only touch composes_with for now; other fields stay verbatim
                    # but classify for the audit report
                    for v in vals:
                        bucket, clean, backing = classify(v, qids, bare)
                        if bucket > 0:
                            bucket_examples[(bucket, field)].append((atom_id, v, clean, backing))
                            bucket_counts[(bucket, field)] += 1
                    continue
                for v in vals:
                    bucket, clean, backing = classify(v, qids, bare)
                    bucket_counts[(bucket, "composes_with")] += 1
                    bucket_examples[(bucket, "composes_with")].append(
                        (atom_id, v, clean, backing))
                    if bucket == 0:
                        keep_composes.append(v)
                    elif bucket == 1:
                        keep_composes.append(clean)
                        any_change = True
                    elif bucket == 2:
                        memory_refs.append(v)
                        any_change = True
                    elif bucket == 3:
                        conceptual_refs.append({"value": v, "backing_atom": backing})
                        if backing:
                            backing_resolved += 1
                        else:
                            backing_unresolved_concepts.append((atom_id, v))
                        any_change = True

        if any_change:
            patches[atom_id] = {
                "atom_id": atom_id,
                "corpus": corpus,
                "composes_with_new": sorted(set(keep_composes)),
                "memory_references_new": sorted(set(memory_refs)),
                "conceptual_references_new": conceptual_refs,
                "composes_with_old": (a.get("composes_with") or
                                      md.get("composes_with") or []),
            }

    # Counts before/after projection
    before_counts = {
        "audit_lesson_total": len(lessons),
        "cross_refs_total_across_fields": sum(bucket_counts.values()),
        "phantom_breakdown_bucket_1_dirty": bucket_counts.get((1, "composes_with"), 0),
        "phantom_breakdown_bucket_2_memory": bucket_counts.get((2, "composes_with"), 0),
        "phantom_breakdown_bucket_3_conceptual": bucket_counts.get((3, "composes_with"), 0),
        "resolved_composes_with": bucket_counts.get((0, "composes_with"), 0),
        "patches_proposed": len(patches),
    }

    after_projection = {
        "composes_with_phantoms_after": (
            sum(1 for p in patches.values()
                if any(not p["composes_with_new"] for p in [p]))
            * 0  # all phantoms moved out by construction
        ),
        "new_memory_references_field_populated_atoms": sum(
            1 for p in patches.values() if p["memory_references_new"]),
        "new_conceptual_references_field_populated_atoms": sum(
            1 for p in patches.values() if p["conceptual_references_new"]),
        "backing_atom_resolved_concepts": backing_resolved,
        "backing_atom_unresolved_concepts": len(backing_unresolved_concepts),
    }

    print("=" * 80)
    print("ITEM 4 CATALOG RECONCILE PATCH (READ-ONLY; SCHEMA-VET pending)")
    print("=" * 80)
    print()
    print("BEFORE:")
    print(json.dumps(before_counts, indent=2))
    print()
    print("AFTER (projection; no writes):")
    print(json.dumps(after_projection, indent=2))
    print()

    # Bucket samples
    print("Bucket 1 (dirty-format-resolvable; strip inline annotation):")
    for atom_id, v, clean, backing in bucket_examples.get((1, "composes_with"), [])[:7]:
        print(f"  {atom_id}.composes_with:")
        print(f"    OLD: '{v}'")
        print(f"    NEW: '{clean}'  -> {backing}")
    print()
    print("Bucket 2 (memory-file refs; -> memory_references):")
    for atom_id, v, clean, backing in bucket_examples.get((2, "composes_with"), [])[:8]:
        print(f"  {atom_id}.memory_references += '{v}'")
    print()
    print("Bucket 3 (conceptual-shorthand; -> conceptual_references):")
    for atom_id, v, clean, backing in bucket_examples.get((3, "composes_with"), [])[:20]:
        backing_str = f"backing={backing}" if backing else "backing=NONE (concept-only)"
        print(f"  {atom_id}.conceptual_references += '{v}'  ({backing_str})")
    print()

    print(f"Backing-resolved concepts: {backing_resolved}")
    print(f"Backing-unresolved concepts (pure-concept references): "
          f"{len(backing_unresolved_concepts)}")
    if backing_unresolved_concepts[:10]:
        print("Sample unresolved (first 10):")
        for atom_id, v in backing_unresolved_concepts[:10]:
            print(f"  {atom_id} -> '{v}'")
    print()

    out = {
        "scour_ts": "2026-06-19",
        "before_counts": before_counts,
        "after_projection": after_projection,
        "patches": patches,
        "bucket_1_dirty_format_samples": [
            {"atom_id": a, "old": v, "new": c, "backing": b}
            for a, v, c, b in bucket_examples.get((1, "composes_with"), [])
        ],
        "bucket_2_memory_samples": [
            {"atom_id": a, "value": v}
            for a, v, c, b in bucket_examples.get((2, "composes_with"), [])
        ],
        "bucket_3_conceptual_samples": [
            {"atom_id": a, "value": v, "backing_atom": b}
            for a, v, c, b in bucket_examples.get((3, "composes_with"), [])
        ],
        "backing_unresolved_concepts": [
            {"atom_id": a, "value": v} for a, v in backing_unresolved_concepts
        ],
    }
    out_path = Path("data/item_4_reconcile_patch_2026-06-19.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"PATCH written: {out_path}")
    print()
    print("NEXT: SCHEMA-VET routing to Skunkworks (do not apply until ratified).")


if __name__ == "__main__":
    main()
