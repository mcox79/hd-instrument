#!/usr/bin/env python3
"""Skunkworks 2026-06-19 -- atomize inst-241 (the 4-layer protection AUDIT_LESSON).

DOGFOODS the SAFE template: imports `add_audit_lesson_safely` from
atomize_audit_lesson_template_SAFE (the reusable, round-trip-gated safe-add
function) and supplies the cert-owner-refined inst-241 spec. This both encodes
the corruption-incident protection lesson AND validates the template's reusable
path end-to-end (Atom-construction enum-MEMBERS + add_atom + fresh-Store
all_atoms() round-trip gate).

SCHEMA-VET (Skunkworks, 2026-06-19) -- all referents verified against the Store:
- instance_number 241 free (audit_lesson max = 240; 239/240 present).
- both composes_with ids RESOLVE (inst-240 silent-loss; inst-80 verify-the-referent).
- recovery commit 2e0b57c0 confirmed in git log (restore NOT origin -- origin was corrupt).
- both memory_reference files exist.

Cert-owner refinements vs the template's worked-example:
- layer-4 reframed to single-writer-window / serialize-same-partition-writes
  (the incident's two writers were an INDEPENDENT ConceptNet ingest + a cap-int
  write -- not a joint-routed task; name-one-owner is the joint-routing sub-case).
- added the code-ground-claims META-lesson (root cause mis-diagnosed twice from
  assumption before code-reading corrected it).
- added the 2nd, more-specific memory_reference (the 2026-06-19 partition-writes ref).

Run: --dry-run (construct + print, no write) | --apply (add via the safe path).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
# DOGFOOD: reuse the template's round-trip-gated safe-add function.
from tools.atomize_audit_lesson_template_SAFE import add_audit_lesson_safely


def build_inst241() -> Atom:
    return Atom(
        id=("AUDIT_concurrent_write_corruption_propagation_4_layer_protection_"
            "unique_tmp_sync_loadgate_explicit_staging_single_writer_window"),
        name=(
            "Concurrent-write corruption + propagation: 4-layer defense-in-depth "
            "(unique-tmp + sync pre-push load-gate + explicit staging + "
            "single-writer-window)"
        ),
        description=(
            "Two independent save_atoms writers (a ConceptNet bulk-ingest and a "
            "cap-int write) targeting the SAME partition shared a FIXED `.tmp` "
            "path; their writes interleaved and produced an unloadable Store "
            "(NULL seam in concept/atoms.jsonl). The corrupt commit then "
            "propagated to origin/remote via a session-tool `git add -A`. "
            "Recovery was clean: the canonical math partition was untouched (it "
            "carried 4 canonicalized cert-VET-pending atoms through the restore); "
            "the concept partition was rolled back to the pre-ingest commit "
            "2e0b57c0 (NOT origin -- origin was also corrupt; CONCEPT_NODE "
            "correctly reverted to 0). FOUR structural protection layers landed "
            "in response, forming defense-in-depth (prevent corruption at the "
            "write + prevent propagation + prevent session-tool sweeping + "
            "prevent the concurrent-write that triggers it): "
            "(1) UNIQUE-TMP per save_atoms/save_relations write (pid + monotonic "
            "counter) -- two concurrent same-partition writers can no longer "
            "collide on the tmp file; "
            "(2) SYNC PRE-PUSH Store-LOAD GATE (local_metrics_sync.ps1) -- "
            "fail-CLOSED: if all_atoms() throws on the staged partition diff, the "
            "push is SKIPPED, so a bad write cannot propagate; "
            "(3) SESSION-TOOLS EXPLICIT-PATH STAGING -- no `git add -A` / no "
            "`git commit -a` for Store mutations (stage partitions by path, only "
            "after a Store-LOAD verify), so a mid-mutation partition is never "
            "blindly swept into a commit; "
            "(4) SINGLE-WRITER-WINDOW -- serialize concurrent same-partition bulk "
            "writes (check there is no concurrent same-partition writer before "
            "dispatch; name-one-owner is the joint-routing sub-case). Even "
            "post-unique-tmp this remains good practice (it also blocks logical "
            "double-apply races). "
            "DIAGNOSIS META-LESSON (code-ground-claims): the root cause was "
            "MIS-diagnosed TWICE from assumption -- first as 'save_atoms is "
            "non-atomic', then as 'the sync blanket-adds' -- before reading the "
            "actual code corrected it (save_atoms IS atomic; the bug was the "
            "fixed-tmp name; the sync stages notes/ only -- the `git add -A` was "
            "a session tool). verify-the-referent applies to CODE-BEHAVIOR "
            "claims: READ the save-function / the call-site before asserting how "
            "it writes. Composes inst-240 silent-loss family + parent-80 "
            "verify-the-referent + the bulk-ingest-concurrency-gotcha."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,  # AUDIT_LESSONs are not pq-graded
            "instance_number": 241,
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "concurrent_write_corruption_4_layer_defense_in_depth",
            "witnesses_count": 1,
            "first_witness": "concept_partition_NULL_seam_corruption_2026-06-19",
            "composes_with": [
                # both VERIFIED to resolve in the Store (SCHEMA-VET 2026-06-19)
                ("AUDIT_discipline_change_silently_breaks_cross_layer_output_"
                 "protocol_enumerate_consumers"),  # inst 240
                ("AUDIT_verify_the_referent_check_passed_on_wrong_object_"
                 "verify_referent_reaches_consumer"),  # inst 80
            ],
            "memory_references": [
                "reference_substrate_bulk_ingest_concurrency_gotcha_2026-06-16",
                ("reference_store_partition_writes_not_concurrency_safe_"
                 "sync_has_preload_gate_2026-06-19"),
            ],
            "conceptual_references": [
                {
                    "value": "defense_in_depth",
                    "backing_atom_proposed": None,
                    "confidence_score": 0,
                    "note": "Meta-lens; not anchored as an atom yet.",
                },
            ],
            "protection_layers": [
                ("layer_1_unique_tmp_per_save_write (corruption-prevention; "
                 "save_atoms + save_relations; pid + monotonic counter)"),
                ("layer_2_sync_prepush_storeload_gate (propagation-prevention; "
                 "local_metrics_sync.ps1; fail-CLOSED on all_atoms() throw)"),
                ("layer_3_session_tools_explicit_path_staging (no git add -A / "
                 "no commit -a for Store mutations; stage by path post-verify)"),
                ("layer_4_single_writer_window (serialize same-partition bulk "
                 "writes; check no concurrent same-partition writer before "
                 "dispatch; name-one-owner = joint-routing sub-case)"),
            ],
            "operational_rule": (
                "When a shared-infra concurrent-write path is added: (a) audit "
                "ALL save-function call-sites for fixed-tmp patterns (corpus-"
                "completeness on the FIX, not just the reported site); (b) the "
                "sync layer MUST gate on Store-LOAD before push (fail-closed); "
                "(c) session tools MUST explicit-stage Store paths after a "
                "Store-LOAD verify; (d) serialize same-partition bulk writers "
                "(single-writer-window); (e) before asserting a save/sync "
                "tool's write-behavior, READ the code (code-ground-claims) -- "
                "this incident was mis-diagnosed twice from assumption."
            ),
            "recovery_pattern": (
                "Restore the corrupt partition from the last clean PRE-mutation "
                "commit (2e0b57c0), NOT origin/main if the corruption was pushed "
                "(origin was also corrupt). Verify all_atoms() loads + TRUE-HARD-"
                "PASS on the cert-FLOOR before staging/pushing the fix."
            ),
        },
    )


def main():
    atom = build_inst241()
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print("inst-241 protection AUDIT_LESSON atomizer. Use --dry-run or --apply.")
        print(f"  id: {atom.id}")
        print(f"  tier(value): {atom.tier.value}  kind(value): {atom.kind.value}")
        print(f"  instance_number: {(atom.metadata or {}).get('instance_number')}")
        return 0
    if "--dry-run" in sys.argv:
        print("DRY RUN -- spec constructs OK (no Store mutation):")
        print(f"  id: {atom.id}")
        print(f"  tier(value): {atom.tier.value}  corpus(value): {atom.corpus.value}")
        print(f"  composes_with: {(atom.metadata or {}).get('composes_with')}")
        print(f"  protection_layers: {len((atom.metadata or {}).get('protection_layers'))}")
        return 0
    print("=" * 80)
    print("APPLY: inst-241 protection AUDIT_LESSON via the SAFE template path")
    print("=" * 80)
    ok = add_audit_lesson_safely(
        atom,
        source="corruption_incident_2026-06-19_4_layer_protection_lesson",
        note=("inst-241: 4-layer defense-in-depth for concurrent-write corruption "
              "+ propagation. Skunkworks SCHEMA-VET PASS (referents verified). "
              "Dogfoods the SAFE template's reusable add path."),
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
