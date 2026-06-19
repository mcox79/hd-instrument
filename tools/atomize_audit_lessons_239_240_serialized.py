#!/usr/bin/env python3
"""DEPRECATED 2026-06-19: this tool is the INST-239/240 INCIDENT ORIGIN.

It uses raw-JSONL string-append (json.dumps(atom_dict)) which BYPASSES the
Atom dataclass constructor + skips to_dict serialization. It wrote
tier="TIER_METHODOLOGY" (enum NAME) instead of "T_methodology" (enum VALUE)
into atoms.jsonl. Atom.from_dict(d) then threw ValueError("'TIER_METHODOLOGY'
is not a valid Tier") -> PartitionedStore().all_atoms() raised -> THE WHOLE
STORE WAS UNLOADABLE. Skunkworks emergency-repaired.

THIS TOOL IS PRESERVED FOR HISTORY (the inst-240 self-referential witness
references this very atomization). DO NOT RE-RUN. The atoms inst-239 + inst-240
already exist in the canonical Store (post-Skunkworks-repair); re-running would
attempt to add duplicates + likely trip a Store-LOAD-gate failure.

CANONICAL SAFE REPLACEMENT (use for any future AUDIT_LESSON atomization):
  -> tools/atomize_audit_lesson_template_SAFE.py
     Uses Atom-construction (enum MEMBERS) + ps.add_atom (to_dict) +
     fresh-Store all_atoms() round-trip gate. Composes Exp-Dev's reference
     pattern + inst-240's rule + the 4-layer protection (unique-tmp + sync
     pre-push load-gate + explicit-staging + name-one-owner).

EXECUTION REFUSED unless --acknowledge-deprecated-incident-origin is passed.

Original docstring preserved below:

----- ORIGINAL DOCSTRING -----
Co-author + atomize AUDIT_LESSON instances 239 (no-Goodhart) and 240
(discipline-change-silently-breaks-cross-layer-output-protocol).

Per Skunkworks 2026-06-19 routing: serialized raw-JSONL append on meta partition
(avoid concurrent write-race that two parallel atomizations would cause).

Both atoms per Skunkworks's SCHEMA-VET conventions:
- kind=audit_lesson; tier=TIER_METHODOLOGY; pq=None
- composes_with values must resolve to real atoms (value-RESOLVES discipline)
- new field placements per MUST-FIX semantics: all in metadata
- raw-JSONL append + verify via raw re-read (no get_atom; no silent-fail)
  [THIS DOCSTRING NOTED RAW-JSONL APPEND AS SAFE; THE ENUM-NAME-VS-VALUE BUG
   PROVED IT WASN'T. INST-240'S WHOLE LESSON IS THAT RAW-PRESENCE NECESSARY +
   STORE-LOAD-ROUND-TRIP SUFFICIENT.]
"""

import json
import sys

# Deprecation gate (refuse to execute without explicit ack)
if __name__ == "__main__" and "--acknowledge-deprecated-incident-origin" not in sys.argv:
    print(__doc__.split("----- ORIGINAL DOCSTRING -----")[0])
    print()
    print("REFUSED: this tool is the inst-239/240 incident origin (deprecated).")
    print("Use tools/atomize_audit_lesson_template_SAFE.py for new AUDIT_LESSON")
    print("atomization (Atom-construction + ps.add_atom + Store-LOAD gate).")
    print()
    print("To bypass this gate (NOT RECOMMENDED; would re-run the dangerous path):")
    print("  python tools/atomize_audit_lessons_239_240_serialized.py \\")
    print("    --acknowledge-deprecated-incident-origin")
    sys.exit(1)
import os
from pathlib import Path

ROOT = Path("data/substrate_index")
META_PARTITION = ROOT / "meta" / "atoms.jsonl"


VERIFY_THE_REFERENT_ATOM = (
    "AUDIT_verify_the_referent_check_passed_on_wrong_object_"
    "verify_referent_reaches_consumer"
)
DEGENERATE_REGIME_ATOM = (
    "AUDIT_degenerate_regime_not_refutation_non_discriminating_test_"
    "is_non_test_verify_regime_discriminating_before_verdict"
)
MONITOR_AUTHORITATIVE_ATOM = (
    "AUDIT_monitor_must_watch_authoritative_source_not_derived_log_"
    "producer_liveness_false_green"
)


ATOM_239_NO_GOODHART = {
    "id": "AUDIT_no_goodhart_metric_measures_claimed_thing_target_corrupts_measure",
    "name": (
        "No-Goodhart discipline: the metric must measure the claimed thing; "
        "the target corrupts the measure"
    ),
    "kind": "audit_lesson",
    "tier": "TIER_METHODOLOGY",
    "corpus": "meta",
    "description": (
        "When a measure becomes a target, it ceases to be a good measure "
        "(Goodhart's law). Applied to cert-discipline: every cert atom's "
        "metric MUST measure what its HEADLINE claims, NOT a proxy that is "
        "game-able by optimization or that drifts under selection.\n\n"
        "Operational test: would optimizing this metric maximally produce "
        "the claimed capability? If 'no' or 'unclear' -> the metric is a "
        "proxy, not the thing.\n\n"
        "Examples this catches: capacity-bar reached by smoke-saturating "
        "proxy; recall inflated by selecting easy queries; AUROC at the "
        "bound by degenerate sparsity; PASS verdict on a "
        "discriminating-regime-failure."
    ),
    "metadata": {
        "provenance_quality": None,
        "instance_number": 239,
        "confirmed_or_candidate": "CONFIRMED",
        "lesson_class": "discipline_anti_over_claim",
        "witnesses_count": 3,
        "first_witness": "T3/EXP_substrate_m4d_degoodhart_dev_tune_heldout",
        "composes_with": [
            VERIFY_THE_REFERENT_ATOM,
            DEGENERATE_REGIME_ATOM,
        ],
        "conceptual_references": [
            {
                "value": "actual_not_bar",
                "backing_atom_proposed": None,
                "confidence_score": 0,
                "note": (
                    "Concept-label (compare actual value to bar, both "
                    "directions); no AUDIT atom exists yet. Skunkworks "
                    "flagged as NEXT catalog-completeness gap (same "
                    "pattern as no-Goodhart pre-fill: used as meta-lens, "
                    "not anchored)."
                ),
            },
        ],
        "witness_summaries": [
            {
                "type": "experiment",
                "atom_id": "T3/EXP_substrate_m4d_degoodhart_dev_tune_heldout",
                "summary": (
                    "Held-out target-set vs train-tune divergence -- the "
                    "standard no-Goodhart experimental harness."
                ),
            },
            {
                "type": "discipline_application_corrected",
                "summary": (
                    "The held-out FACT-FABRICATION metric (Item-1 PART_OF + "
                    "M1 HYPERNYM + HYP-5) honestly measures coverage-"
                    "completion on held-out edges -- do NOT advertise THOSE "
                    "held-out tests as inference-transfer. SEPARATELY, "
                    "compositional reasoning IS cert-proven "
                    "(compositional_generalization K20=1.00 + FB15k-237 + "
                    "cross-layer + resonator + counterfactual). The no-"
                    "Goodhart discipline keeps the held-out metric scoped "
                    "to what it measures (fact-fabrication absence) "
                    "WITHOUT denying the proven reasoning capability. "
                    "(Per Skunkworks's FIX 4: corrected from a pre-"
                    "correction over-generalization; negativity-bias-"
                    "symmetric in action on the discipline atom itself.)"
                ),
            },
            {
                "type": "discipline_application",
                "summary": (
                    "The metric-mismatch lesson (existing AUDIT atom: switch-"
                    "metrics-once-principled-pre-registered) is a sibling "
                    "instance: the metric must test the mechanism on its "
                    "claimed benefit, not a proxy."
                ),
            },
        ],
        "operational_test": (
            "Would optimizing this metric maximally produce the claimed "
            "capability? If 'no' or 'unclear' -> the metric is a proxy."
        ),
        "cited_in_unbound_references": [
            "no_goodhart",
            "no_goodhart_anchor_layer",
            "no_goodhart_metric_measures_claimed_thing",
        ],
    },
}


ATOM_240_SILENT_LOSS_FAMILY = {
    "id": (
        "AUDIT_discipline_change_silently_breaks_cross_layer_output_protocol_"
        "enumerate_consumers"
    ),
    "name": (
        "Discipline-change silently breaks cross-layer output protocol; "
        "enumerate output-consumers"
    ),
    "kind": "audit_lesson",
    "tier": "TIER_METHODOLOGY",
    "corpus": "meta",
    "description": (
        "A discipline/format change at one layer SILENTLY breaks an output "
        "protocol at another layer when the output-state is not pre-"
        "verified across the layer-cross-section.\n\n"
        "Operational rule: when adopting a discipline (style/cap/format/"
        "schema), ENUMERATE all OUTPUT-CONSUMERS of the affected artifacts "
        "(parsers, monitors, serializers, filters) + verify each still "
        "parses/matches. Cross-layer changes need cross-layer verify-the-"
        "referent. Raw presence / sender-sent is NECESSARY but NOT "
        "SUFFICIENT; verify the consumer RECEIVES + PARSES."
    ),
    "metadata": {
        "provenance_quality": None,
        "instance_number": 240,
        "confirmed_or_candidate": "CONFIRMED",
        "lesson_class": "cross_layer_silent_loss_family",
        "witnesses_count": 3,
        "first_witness": "patch_generator_if_v_filter_dropped_emptied_fields_2026_06_19",
        "composes_with": [
            VERIFY_THE_REFERENT_ATOM,
            MONITOR_AUTHORITATIVE_ATOM,
        ],
        "conceptual_references": [
            {
                "value": "verify_OUTPUT_not_liveness",
                "backing_atom_proposed": MONITOR_AUTHORITATIVE_ATOM,
                "confidence_score": 99,
                "source_tag": "skunkworks_vet",
                "note": (
                    "The unifying meta-lens: verify the output-state "
                    "(consumer-receives-it), not the liveness (sender-"
                    "sent-it). This atom IS the family witness."
                ),
            },
            {
                "value": "store_drops_unmodeled_fields",
                "backing_atom_proposed": None,
                "confidence_score": 0,
                "note": (
                    "Concept ref to "
                    "[[reference_store_drops_relation_edge_metadata_role_"
                    "on_source_atom]] (memory reference; not an atom)."
                ),
            },
        ],
        "memory_references": [
            "reference_store_drops_relation_edge_metadata_role_on_source_atom_2026-06-18",
        ],
        "witness_summaries": [
            {
                "type": "instance_1",
                "tag": "patch_generator_if_v_filter_dropped_emptied_fields",
                "date": "2026-06-19_morning",
                "caught_by": "Research_symmetric_apply_then_verify",
                "summary": (
                    "Item 4 v2 patch generator's `{k: v for k, v in d.items() "
                    "if v}` filter dropped fields where ALL entries had "
                    "moved (empty new-list). Apply tool didn't touch those "
                    "fields -> source-field phantoms persisted. Caught by "
                    "post-apply scour."
                ),
            },
            {
                "type": "instance_2",
                "tag": "top_level_memory_references_lost_on_to_dict",
                "date": "2026-06-19_morning",
                "caught_by": "Skunkworks_round_trip_survival_test",
                "summary": (
                    "Item 4 v2.1 patch wrote memory_references + "
                    "conceptual_references as TOP-LEVEL JSONL keys; Atom "
                    "dataclass schema doesn't model them; Atom.to_dict() "
                    "drops them -> silent loss on next Store-native flush. "
                    "Caught by Skunkworks's to_dict round-trip-survival "
                    "test. MUST-FIX: relocate into metadata."
                ),
            },
            {
                "type": "instance_3",
                "tag": "filename_cap_dropped_to_recipient_monitor_silently_filtered",
                "date": "2026-06-19_afternoon",
                "caught_by": "USER",
                "summary": (
                    "Filename-cap discipline (<=120 char) adopted bilaterally "
                    "by Skunkworks + Research dropped the 'to_<recipient>' "
                    "addressing from outbound filenames. The notes_monitor.sh "
                    "filter (matched: <session>|to_all|_all_) silently "
                    "filtered 3 substantive Skunkworks notes addressed to "
                    "Research. Idle gap USER caught. Fix: 2-layer (broaden "
                    "monitor filter + preserve to_<recipient> within cap)."
                ),
            },
        ],
        "operational_rule": (
            "Cross-layer verify-the-referent: when adopting a discipline, "
            "enumerate output-consumers + verify each still parses. "
            "Verify the consumer RECEIVES + PARSES, not just sender SENT."
        ),
        "skunkworks_authored_research_co_authored": True,
    },
}


def append_atoms_serialized(atoms_to_append):
    """Serialized raw-JSONL append on meta/atoms.jsonl.
    Per Skunkworks 2026-06-19: avoid concurrent write-race by serializing
    multiple atomizations through one tool-run.
    """
    # Read current contents (pre-snapshot)
    existing_lines = []
    if META_PARTITION.exists():
        with META_PARTITION.open(encoding="utf-8") as f:
            existing_lines = f.readlines()
    n_pre = len([l for l in existing_lines if l.strip()])
    print(f"Pre-append meta partition: {n_pre} lines")

    # Append each atom
    tmp = META_PARTITION.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.writelines(existing_lines)
        for atom in atoms_to_append:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, META_PARTITION)

    # Verify via raw re-read
    with META_PARTITION.open(encoding="utf-8") as f:
        new_lines = f.readlines()
    n_post = len([l for l in new_lines if l.strip()])
    print(f"Post-append meta partition: {n_post} lines (expected: "
          f"{n_pre + len(atoms_to_append)})")
    return n_pre, n_post


def verify_atom_landed(atom_id):
    """Raw re-read to verify atom present with expected key fields."""
    with META_PARTITION.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            if a.get("id") == atom_id:
                # Verify key fields per Skunkworks VET conventions
                if a.get("kind") != "audit_lesson":
                    return False, f"kind mismatch: {a.get('kind')}"
                if a.get("tier") != "TIER_METHODOLOGY":
                    return False, f"tier mismatch: {a.get('tier')}"
                md = a.get("metadata") or {}
                if md.get("provenance_quality") is not None:
                    return False, f"pq should be None"
                if md.get("instance_number") is None:
                    return False, "instance_number missing"
                # Verify metadata-placement of new fields
                for top_key in ("memory_references", "conceptual_references",
                                "cross_ref_annotations"):
                    if top_key in a:
                        return False, (f"TOP-LEVEL {top_key} present "
                                       f"(silent-loss risk; must be in metadata)")
                return True, f"OK (inst {md.get('instance_number')})"
    return False, "atom not found"


def main():
    print("=" * 80)
    print("CO-AUTHOR + ATOMIZE inst 239 (no-Goodhart) + inst 240 (silent-loss)")
    print("SERIALIZED (avoid meta-partition write-race per Skunkworks)")
    print("=" * 80)
    print()

    atoms_to_append = [ATOM_239_NO_GOODHART, ATOM_240_SILENT_LOSS_FAMILY]

    print("Atom 239 id:", ATOM_239_NO_GOODHART["id"])
    print("Atom 240 id:", ATOM_240_SILENT_LOSS_FAMILY["id"])
    print()

    n_pre, n_post = append_atoms_serialized(atoms_to_append)
    if n_post != n_pre + len(atoms_to_append):
        print(f"FAIL: line-count mismatch (pre {n_pre} + {len(atoms_to_append)} "
              f"!= post {n_post})")
        return

    print()
    print("VERIFY (raw JSONL re-read; no get_atom; no silent-fail risk)")
    print("-" * 80)
    for atom in atoms_to_append:
        ok, msg = verify_atom_landed(atom["id"])
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {atom['id'][:60]:60s}  {msg}")

    print()
    print("CO-AUTHOR + ATOMIZE COMPLETE. Route to Skunkworks for landed-VET on")
    print("both (round-trip-survival + unbound-ref-resolution + 5-rules-apply).")


if __name__ == "__main__":
    main()
