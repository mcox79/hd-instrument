#!/usr/bin/env python3
"""Item 4 catalog reconcile patch v2 (READ-ONLY; per Skunkworks SCHEMA-VET):

Per Skunkworks Item 4 v1 SCHEMA-VET PASS + Q1/Q2 answers (2026-06-19):
- Q1 = B (all 8 ref fields uniformly; value-RESOLVES is field-agnostic).
- Q2 = substring-scan + 3-token guard + per-bind-confidence-report;
       binds are PROPOSALS (Skunkworks VETs each); unbound-is-OK (don't force-bind).
- Annotation handling: where stripped annotation carries recoverable info
  (instance_number; candidate-status) -> drop (info IS in the resolved atom);
  where non-recoverable -> move to cross_ref_annotations field.

A5-safe (metadata-only; tier/pq/relevance untouched; snapshot-before captured).
Output: data/item_4_reconcile_patch_v2_2026-06-19.json
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path("data/substrate_index")

INLINE_ANNOTATION_PAT = re.compile(r"\s*\([^)]+\)\s*$")
INSTANCE_NUM_PAT = re.compile(r"instance\s+(\d+)", re.IGNORECASE)
CANDIDATE_STATUS_PAT = re.compile(
    r"(CONFIRMED|CANDIDATE|NEW|PENDING|RATIFIED|TENTATIVE)\s+child",
    re.IGNORECASE,
)
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
ATOM_FIELDS = [
    "composes_with", "parent_of", "strengthens", "supersedes",
    "child_of", "siblings", "composes_with_siblings", "depends_on",
]


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
    audit_atom_ids = []
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
                if a.get("kind") == "audit_lesson":
                    audit_atom_ids.append(aid)
    return qids, bare, audit_atom_ids


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


def parse_annotation(annotation):
    """Extract instance_num + candidate-status from inline annotation.
    Returns (instance_num, status, raw_annotation, is_recoverable).
    Recoverable means the info is reflected in the resolved atom's metadata.
    """
    instance_num = None
    status = None
    m = INSTANCE_NUM_PAT.search(annotation)
    if m:
        instance_num = int(m.group(1))
    m = CANDIDATE_STATUS_PAT.search(annotation)
    if m:
        status = m.group(1).upper()
    is_recoverable = (instance_num is not None or status is not None)
    return instance_num, status, annotation, is_recoverable


# Skunkworks-VET'd missed-bindings (per-bind VET 2026-06-19; symmetric-verify
# caught 4 true backings the 3-token guard under-bound). Concept-key (lowercase)
# -> verified backing audit atom-id.
SKUNKWORKS_VETTED_BINDS = {
    "discriminating_regime_guard":
        "AUDIT_degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict",
    "discriminating_regime_guard_c1_8a_8b_refuse_gate_preregs":
        "AUDIT_degenerate_regime_not_refutation_non_discriminating_test_is_non_test_verify_regime_discriminating_before_verdict",
    "monitor_consumer_can_die_inbox_authoritative_9th_rule":
        "AUDIT_monitor_must_watch_authoritative_source_not_derived_log_producer_liveness_false_green",
    "100th_rule_audit_tooling_must_self_verify":
        "AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable",
}


def substring_bind_concept(concept_value, audit_atom_ids):
    """Per-Q2 substring-scan with 3-token guard + Skunkworks-VET'd missed-binds.

    Returns (backing, confidence_score, source_tag).
    Source tag: 'token_scan' | 'skunkworks_vet' | None.
    Confidence = number of underscore-tokens that overlap (>= 3 to bind by scan),
    or 99 if Skunkworks explicitly VET'd the bind.
    """
    norm = concept_value.lower().strip()

    # Check Skunkworks-VET'd missed-bindings first (these supersede the token scan)
    if norm in SKUNKWORKS_VETTED_BINDS:
        return (SKUNKWORKS_VETTED_BINDS[norm], 99, "skunkworks_vet")

    norm_tokens = set(norm.split("_"))
    norm_tokens.discard("")
    if len(norm_tokens) < 3:
        return (None, 0, None)

    best_backing = None
    best_overlap = 0
    for aid in audit_atom_ids:
        aid_tokens = set(aid.lower().split("_"))
        aid_tokens.discard("")
        aid_tokens.discard("audit")
        overlap = len(norm_tokens & aid_tokens)
        if overlap >= 3 and overlap > best_overlap:
            best_overlap = overlap
            best_backing = aid
    if best_backing:
        return (best_backing, best_overlap, "token_scan")
    return (None, 0, None)


def classify_value(value, qids, bare, audit_atom_ids):
    """Classify a cross-ref value -> (bucket, clean_value, backing, annotation_info, confidence)

    Bucket: 0 (resolves) | 1 (dirty-format) | 2 (memory) | 3 (conceptual)
    annotation_info: dict with annotation/recoverable for cross_ref_annotations field
    confidence: substring-bind confidence (for bucket 3)
    """
    annotation_info = None
    confidence = 0
    backing = None

    status, resolved = resolve(value, qids, bare)
    if status in ("qualified", "bare", "corpus_inferred"):
        return (0, value, resolved, None, 0)

    # Bucket 1: dirty-format-resolvable
    if INLINE_ANNOTATION_PAT.search(value):
        annotation_match = INLINE_ANNOTATION_PAT.search(value)
        annotation = annotation_match.group(0).strip()
        clean = INLINE_ANNOTATION_PAT.sub("", value).strip()
        clean_status, clean_resolved = resolve(clean, qids, bare)
        if clean_status in ("qualified", "bare", "corpus_inferred"):
            inst, candidate_status, raw, is_recoverable = parse_annotation(annotation)
            annotation_info = {
                "raw": annotation,
                "instance_num": inst,
                "candidate_status": candidate_status,
                "is_recoverable": is_recoverable,
            }
            return (1, clean, clean_resolved, annotation_info, 0)

    # Bucket 2: memory-file refs
    is_memory = (
        MEMORY_FILE_PAT.match(value)
        or DATE_SUFFIX_PAT.search(value)
        or "MEMORY" in value.upper()
        or value.endswith(".md")
    )
    if is_memory:
        return (2, value, None, None, 0)

    # Bucket 3: conceptual shorthand
    backing, confidence, source = substring_bind_concept(value, audit_atom_ids)
    return (3, value, backing, None, confidence)


def main():
    # Per Skunkworks 2026-06-19 close-sweep: extend reconcile to METHODOLOGY_RULE
    # atoms (8 pre-existing phantoms; same treatment as AUDIT_LESSON).
    lessons = list(load_atoms("audit_lesson")) + list(load_atoms("methodology_rule"))
    qids, bare, audit_atom_ids = load_qualified_ids()

    patches = {}
    bucket_counts = defaultdict(int)
    bucket_examples = defaultdict(list)
    proposed_binds = []
    non_recoverable_annotations = []
    recoverable_dropped = []

    for corpus, a in lessons:
        atom_id = a["id"]
        md = a.get("metadata") or {}

        # Per-field updated values
        field_new_values = {f: [] for f in ATOM_FIELDS}
        fields_touched = set()  # fields that had any original content
        memory_refs = list(a.get("memory_references") or
                           md.get("memory_references") or [])
        conceptual_refs = list(a.get("conceptual_references") or
                               md.get("conceptual_references") or [])
        cross_ref_annotations = list(a.get("cross_ref_annotations") or
                                     md.get("cross_ref_annotations") or [])

        any_change = False

        for field in ATOM_FIELDS:
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
                for v in vals:
                    fields_touched.add(field)
                    bucket, clean, backing, ann_info, conf = classify_value(
                        v, qids, bare, audit_atom_ids)
                    bucket_counts[(bucket, field)] += 1
                    bucket_examples[(bucket, field)].append(
                        (atom_id, v, clean, backing, ann_info, conf))
                    if bucket == 0:
                        field_new_values[field].append(v)
                    elif bucket == 1:
                        field_new_values[field].append(clean)
                        if ann_info and not ann_info["is_recoverable"]:
                            cross_ref_annotations.append({
                                "source_field": field,
                                "resolved_atom": clean,
                                "annotation": ann_info["raw"],
                            })
                            non_recoverable_annotations.append({
                                "atom_id": atom_id, "field": field,
                                "value": v,
                            })
                        elif ann_info:
                            recoverable_dropped.append({
                                "atom_id": atom_id, "field": field,
                                "original": v, "stripped": clean,
                                "annotation": ann_info["raw"],
                            })
                        any_change = True
                    elif bucket == 2:
                        memory_refs.append(v)
                        any_change = True
                    elif bucket == 3:
                        entry = {"value": v, "backing_atom_proposed": backing,
                                 "confidence_score": conf}
                        conceptual_refs.append(entry)
                        proposed_binds.append({
                            "atom_id": atom_id, "field": field,
                            "value": v, "backing_proposed": backing,
                            "confidence": conf,
                        })
                        any_change = True

        if any_change:
            patches[atom_id] = {
                "atom_id": atom_id,
                "corpus": corpus,
                # Emit field_new_values for ALL fields_touched (even if empty
                # list -- means all entries moved to memory_/conceptual_refs;
                # source field must be cleared so phantoms don't persist).
                "field_new_values": {k: sorted(set(field_new_values[k]))
                                     for k in fields_touched},
                "memory_references_new": sorted(set(memory_refs)),
                "conceptual_references_new": conceptual_refs,
                "cross_ref_annotations_new": cross_ref_annotations,
            }

    # Counts before/after
    before = {
        "audit_lesson_total": len(lessons),
        "cross_refs_total_across_8_fields": sum(bucket_counts.values()),
        "patches_proposed": len(patches),
    }
    by_bucket = defaultdict(int)
    by_field = defaultdict(int)
    for (bucket, field), n in bucket_counts.items():
        by_bucket[bucket] += n
        by_field[field] += n
    before["by_bucket"] = {f"bucket_{k}": v for k, v in by_bucket.items()}
    before["by_field"] = dict(by_field)

    binds_summary = {
        "proposed_binds_total": len(proposed_binds),
        "with_backing_proposed": sum(1 for b in proposed_binds if b["backing_proposed"]),
        "unbound_proposed": sum(1 for b in proposed_binds if not b["backing_proposed"]),
        "binds_by_confidence": defaultdict(int),
    }
    for b in proposed_binds:
        binds_summary["binds_by_confidence"][b["confidence"]] += 1
    binds_summary["binds_by_confidence"] = dict(binds_summary["binds_by_confidence"])

    after = {
        "atom_resolve_fields_phantoms_after": 0,
        "memory_references_field_populated_atoms": sum(
            1 for p in patches.values() if p.get("memory_references_new")),
        "conceptual_references_field_populated_atoms": sum(
            1 for p in patches.values() if p.get("conceptual_references_new")),
        "cross_ref_annotations_field_populated_atoms": sum(
            1 for p in patches.values() if p.get("cross_ref_annotations_new")),
        "annotation_drops_recoverable": len(recoverable_dropped),
        "annotation_preserves_non_recoverable": len(non_recoverable_annotations),
        "binds_summary": binds_summary,
    }

    print("=" * 80)
    print("ITEM 4 v2 PATCH (READ-ONLY; Q1=B all 8 fields; Q2=substring binds proposed)")
    print("=" * 80)
    print()
    print("BEFORE:")
    print(json.dumps(before, indent=2))
    print()
    print("AFTER (projection; no writes):")
    print(json.dumps(after, indent=2))
    print()

    # Sample buckets across all fields
    print("Bucket 1 sample (dirty-format-resolvable; strip + annotation handled):")
    seen = 0
    for (bucket, field), examples in bucket_examples.items():
        if bucket != 1:
            continue
        for atom_id, v, clean, backing, ann, conf in examples[:3]:
            recoverable = ann and ann["is_recoverable"]
            print(f"  {atom_id}.{field}:")
            print(f"    OLD: '{v}'")
            print(f"    NEW: '{clean}'  ->  {backing}")
            print(f"    annotation '{ann['raw'] if ann else ''}'  "
                  f"recoverable={recoverable}  -> "
                  f"{'drop' if recoverable else 'cross_ref_annotations'}")
            seen += 1
            if seen >= 6:
                break
        if seen >= 6:
            break
    print()

    print("Bucket 3 sample (conceptual; proposed binds with confidence):")
    high_conf = sorted(proposed_binds, key=lambda b: -b["confidence"])
    for b in high_conf[:10]:
        backing = b["backing_proposed"] or "UNBOUND"
        print(f"  {b['atom_id']}.{b['field']} -> '{b['value']}' (confidence={b['confidence']})")
        print(f"    backing_proposed: {backing}")
    print()

    print(f"Proposed binds with backing: {binds_summary['with_backing_proposed']}")
    print(f"Proposed binds unbound (honest): {binds_summary['unbound_proposed']}")
    print()
    print("ALL BINDS REQUIRE SKUNKWORKS PER-BIND VET (per Q2).")

    out = {
        "scour_ts": "2026-06-19",
        "schema_version": "v2",
        "scope": "all_8_ref_fields_uniformly",
        "before_counts": before,
        "after_projection": after,
        "patches": patches,
        "proposed_binds_for_VET": proposed_binds,
        "recoverable_annotations_dropped": recoverable_dropped[:30],
        "non_recoverable_annotations_preserved": non_recoverable_annotations[:30],
    }
    out_path = Path("data/item_4_reconcile_patch_v2_2026-06-19.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print()
    print(f"v2 PATCH written: {out_path}")


if __name__ == "__main__":
    main()
