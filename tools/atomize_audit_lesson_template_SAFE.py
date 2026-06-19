#!/usr/bin/env python3
"""SAFE atomize-AUDIT_LESSON template (the inst-239/240 incident lesson encoded).

Per the cap-int + corruption-incident cycle 2026-06-19:
- inst-239/240 atomization caused the Store-unloadable incident (raw-JSONL append
  wrote tier="TIER_METHODOLOGY" enum NAME instead of "T_methodology" enum VALUE;
  Atom.from_dict threw on load; PartitionedStore broke; emergency repair needed).
- ROOT FIX: use Atom-construction with enum MEMBERS + add_atom (which calls
  to_dict that serializes enum.value correctly) + fresh-Store all_atoms() gate
  (which catches any to_dict / from_dict round-trip violation).
- THIS TEMPLATE encodes the safe pattern + serves as the reference for any
  future AUDIT_LESSON (or similar atom-add) work.

USAGE PATTERN (copy this file + adapt):

  1. Define your atom spec via Atom construction:
       atom = Atom(
           id="AUDIT_<descriptive_id>",
           name="<short headline>",
           description="<full description>",
           kind=AtomKind.AUDIT_LESSON,
           tier=Tier.TIER_METHODOLOGY,   # MEMBER (enum), serialized as value
           corpus=Corpus.META,           # MEMBER, serialized as value
           algebra=None,
           metadata={
               "provenance_quality": None,  # AUDIT_LESSONs aren't pq-graded
               "instance_number": <max+1>,
               "confirmed_or_candidate": "CONFIRMED",
               "composes_with": [
                   "AUDIT_<resolvable_id_1>",
                   ...
               ],
               # other AUDIT_LESSON-convention fields
           },
       )

  2. Use ps.add_atom (the standard write path):
       ps = PartitionedStore(Path("data/substrate_index"))
       ps.add_atom(atom, source="<source_tag>", note="<context>")

  3. Verify via fresh-Store all_atoms() round-trip:
       ps2 = PartitionedStore(Path("data/substrate_index"))
       atoms = list(ps2.all_atoms())  # raises if Atom.from_dict fails on any line
       found = next((a for a in atoms if a.id == atom.id), None)
       assert found is not None and found.tier == Tier.TIER_METHODOLOGY, \
              "round-trip survival check failed"

WHY THIS PATTERN IS SAFE (composes inst-240's witnesses):
- Atom.__init__ validates enum-MEMBERship at construction time (no NAME-vs-VALUE bug).
- to_dict() serializes enum.value automatically (no raw-string mismatch).
- Fresh PartitionedStore + all_atoms() does Atom.from_dict on every line ->
  authoritative no-corruption proof (catches any silent-loss-at-the-layer-cross-section).
- The atomic save_atoms (post layer-1 unique-tmp fix 2026-06-19) is concurrency-safe.
- The sync pre-push Store-LOAD gate (layer-2 2026-06-19) prevents propagation
  of any bad write that slips through.

NEVER USE (deprecated; caused inst-239/240 incident):
- Raw-JSONL string-append (json.dumps(atom_dict)) -- bypasses Atom construction;
  enum-NAME-vs-VALUE bug + skips to_dict serialization.
- Raw-JSONL verify-only (json.loads round-trip) -- catches malformed JSON but
  NOT Atom.from_dict enum violations.

EXAMPLE (the protection-layer AUDIT_LESSON Skunkworks has queued at-bandwidth):
- See `_example_protection_layer_audit_lesson()` below for the concrete pattern
  applied to the corruption-protection lesson from 2026-06-19.
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


def add_audit_lesson_safely(atom: Atom, source: str, note: str,
                            store_root: Path = Path("data/substrate_index")) -> bool:
    """Add an AUDIT_LESSON atom via the safe pattern.

    Returns True on success (added + round-trip survives), False on failure.
    Idempotent: if atom.id already exists, returns True without re-adding.
    """
    ps = PartitionedStore(store_root)
    qid = f"{atom.corpus.value}::{atom.id}"
    if ps.get_atom(qid) is not None:
        print(f"SKIP (idempotent): {atom.id} already present.")
        return True

    print(f"ADDING: {atom.id}")
    print(f"  kind: {atom.kind.value}")
    print(f"  tier: {atom.tier.value}")
    print(f"  corpus: {atom.corpus.value}")
    print(f"  pq: {(atom.metadata or {}).get('provenance_quality')}")
    print(f"  instance_number: {(atom.metadata or {}).get('instance_number')}")

    ps.add_atom(atom, source=source, note=note)

    # Fresh-Store all_atoms() round-trip verify (the inst-240 gate)
    ps2 = PartitionedStore(store_root)
    atoms = list(ps2.all_atoms())
    found = next((a for a in atoms if a.id == atom.id), None)
    if found is None:
        print(f"  FAIL: atom not found post-add")
        return False
    if found.tier != atom.tier:
        print(f"  FAIL: tier mismatch (expected {atom.tier}, got {found.tier})")
        return False
    if found.kind != atom.kind:
        print(f"  FAIL: kind mismatch (expected {atom.kind}, got {found.kind})")
        return False
    md = found.metadata or {}
    expected_pq = (atom.metadata or {}).get("provenance_quality")
    if md.get("provenance_quality") != expected_pq:
        print(f"  FAIL: pq mismatch")
        return False
    print(f"  PASS: round-trip survival OK (Atom.from_dict clean)")
    return True


def _example_protection_layer_audit_lesson() -> Atom:
    """The concrete example: the protection-layer lesson from 2026-06-19.

    Captures the corruption-incident lessons (4 protection layers; unique-tmp
    + sync pre-push gate + name-one-owner + explicit-staging) -- the structural
    answer to "how do we prevent THIS happening in 6 months."

    Skunkworks would have ultimate cert-owner-rights on the exact spec; this is
    the template-form Director would route for SCHEMA-VET.
    """
    return Atom(
        id=("AUDIT_concurrent_write_corruption_propagation_4_layer_protection_"
            "atomic_tmp_uniqueness_sync_loadgate_explicit_staging_name_one_owner"),
        name=(
            "Concurrent-write corruption + propagation: 4-layer protection "
            "(atomic unique-tmp + sync pre-push load-gate + explicit staging + "
            "name-one-owner)"
        ),
        description=(
            "A concurrent partition-write collision (two save_atoms writers "
            "sharing a fixed `.tmp` path) interleaved and produced an "
            "unloadable Store (NULL bytes at the seam). The corrupt commit "
            "then propagated to origin/remote via session-tool `git add -A`. "
            "Recovery was clean (the canonical Store was the math partition, "
            "untouched; concept rolled back to pre-ingest 2e0b57c0). 4 "
            "structural protection layers landed in response: "
            "(1) unique-tmp per save_atoms write (pid + monotonic counter); "
            "(2) sync pre-push Store-LOAD gate (fail-CLOSED if all_atoms() "
            "throws -> push skipped); "
            "(3) session-tools adopt explicit-path staging (no `git add -A` / "
            "no `git commit -a` for Store mutations); "
            "(4) cert-owner names ONE owner for joint-routed atom-write tasks "
            "(prevents parallel-kickoff timing-conflicts). The 4 layers form "
            "defense-in-depth: prevent corruption at origin + prevent "
            "propagation + prevent session-tool sweeping + prevent owner-"
            "ambiguity. Composes inst-240 silent-loss family + parent-80 "
            "verify-the-referent + reference_substrate_bulk_ingest_"
            "concurrency_gotcha."
        ),
        kind=AtomKind.AUDIT_LESSON,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata={
            "provenance_quality": None,
            "instance_number": 241,  # +1 after inst 240; Skunkworks confirms before atomize
            "confirmed_or_candidate": "CONFIRMED",
            "lesson_class": "concurrent_write_corruption_4_layer_protection",
            "witnesses_count": 1,
            "first_witness": "concept_partition_line_8915_NULL_corruption_2026-06-19",
            "composes_with": [
                ("AUDIT_discipline_change_silently_breaks_cross_layer_output_"
                 "protocol_enumerate_consumers"),  # inst 240
                ("AUDIT_verify_the_referent_check_passed_on_wrong_object_"
                 "verify_referent_reaches_consumer"),
            ],
            "memory_references": [
                ("reference_substrate_bulk_ingest_concurrency_gotcha_"
                 "2026-06-16"),
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
                "layer_1_unique_tmp_per_save_write (corruption-prevention; "
                "save_atoms + save_relations)",
                "layer_2_sync_prepush_storeload_gate (propagation-prevention; "
                "local_metrics_sync.ps1)",
                "layer_3_session_tools_explicit_staging (session-tool "
                "discipline; no -A / no commit -a)",
                "layer_4_cert_owner_names_one_owner (joint-routing fix; "
                "prevents parallel-kickoff)",
            ],
            "operational_rule": (
                "When a shared-infra concurrent-write path is added, audit "
                "ALL save-function call-sites for fixed-tmp patterns (corpus-"
                "completeness on the FIX, not just the reported sites). + "
                "the sync layer MUST gate on Store-LOAD before push. + "
                "session tools MUST explicit-stage. + joint-routed atom-"
                "writes need name-one-owner."
            ),
            "skunkworks_at_bandwidth_atomize_candidate": True,
        },
    )


def main():
    if "--dry-run" not in sys.argv and "--apply" not in sys.argv:
        print("USAGE: template script. To use this for a real atomize:")
        print("  1. Copy this file + adapt the atom spec")
        print("  2. Route to Skunkworks for SCHEMA-VET")
        print("  3. Run with --apply (after Skunkworks concurs)")
        print()
        print("Example atom spec for the protection-layer AUDIT_LESSON:")
        atom = _example_protection_layer_audit_lesson()
        print(f"  id: {atom.id[:80]}")
        print(f"  kind: {atom.kind.value}")
        print(f"  tier: {atom.tier.value}")
        print(f"  pq: {(atom.metadata or {}).get('provenance_quality')}")
        print(f"  instance_number: {(atom.metadata or {}).get('instance_number')}")
        print()
        print("Pattern is documented in the module docstring.")
        return 0

    if "--dry-run" in sys.argv:
        print("DRY RUN: would atomize the example protection-layer AUDIT_LESSON.")
        atom = _example_protection_layer_audit_lesson()
        print(f"  id: {atom.id}")
        print("  (no Store mutation; use --apply to actually add)")
        return 0

    # --apply path
    atom = _example_protection_layer_audit_lesson()
    print("=" * 80)
    print("APPLYING (--apply): example protection-layer AUDIT_LESSON")
    print("=" * 80)
    ok = add_audit_lesson_safely(
        atom,
        source="corruption_incident_2026-06-19_4_layer_protection_lesson",
        note=(
            "Encodes the 4-layer protection lesson from the 2026-06-19 "
            "concept-partition NULL-corruption incident. Composes inst-240 + "
            "parent-80. Skunkworks SCHEMA-VET pending before --apply."
        ),
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
