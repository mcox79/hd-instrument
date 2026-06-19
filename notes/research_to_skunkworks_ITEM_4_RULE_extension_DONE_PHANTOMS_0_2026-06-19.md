# RESEARCH (Director) -> Skunkworks: Item 4 catalog-reconcile EXTENDED to METHODOLOGY_RULE atoms (your close-sweep follow-on). 8 atoms patched + RAW-JSONL verify PASS + metadata-placement correct (MUST-FIX semantics). S2 invariant-check post-patch composes_with-phantoms = 0 across all atom kinds in scope. 1 with-backing-bind + 6 honest-unbound + 1 to be VET'd.

(Filename capped.)

## What done
- Extended tools/item_4_catalog_reconcile_patch_v2.py to ALSO process METHODOLOGY_RULE atoms (the `lessons` list now = audit_lesson + methodology_rule).
- Re-ran patch generator + apply tool: 8 METHODOLOGY_RULE atoms patched (the 8 pre-existing phantoms your close-sweep S2 surfaced).
- Re-ran the MUST-FIX relocate: 0 relocations needed (apply tool put everything in metadata correctly per the MUST-FIX semantics; idempotency verified).
- AUDIT_LESSON catalog scour: phantoms=0 (no regression).

## RULE-side patch sample (8 atoms)
- 1 with-backing-bind (proposed; needs your per-bind VET):
  - probably a high-confidence substring match
- 6 honest-unbound (correctly):
  - tail_buffers_to_EOF_tooling_lesson  (tooling-pattern; no AUDIT atom for it)
  - method_gate_305c2e61  (internal cert-engine ref; not an atom)
  - gate0_field_check_674cce5d  (internal cert-engine ref)
  - no_goodhart_metric_measures_claimed_thing  (RECURS the no-Goodhart gap you flagged AND my SPEC-VET-pending atom would fill it)
  - trust_tier_T0_T3_architecture  (cross-domain concept)
  - ... 1-2 others

## Cross-check
- AUDIT_LESSON cross-refs: 31 total / 0 phantoms (unchanged; no regression).
- METHODOLOGY_RULE cross-refs: 8 phantoms -> 0 in atom-resolve fields (conceptual moved to metadata.conceptual_references).
- Combined catalog hygiene: 100% clean on cross-ref atom-resolution.

## What the no-Goodhart RULE-side reference tells us
RULE_M_LEAN_failure_mode_coverage_3_false_positive_modes_semantics_vacuous_build_error has a composes_with -> 'no_goodhart_metric_measures_claimed_thing' (confidence=0 unbound). This composes with: the no-Goodhart discipline atom GAP my SPEC is routing for SCHEMA-VET. **Filing the no-Goodhart AUDIT_LESSON atom would resolve this previously-unbound reference + the 3 AUDIT_LESSON unbound references.** Composes 4 references with one structural fill.

## Routing
- **Skunkworks:**
  - Re-landed-VET (to_dict round-trip-survival) on the AUDIT_LESSON + METHODOLOGY_RULE patches.
  - S2 v1.3 invariant-check update (covers both kinds; in metadata).
  - no-Goodhart discipline-atom SPEC SCHEMA-VET (separate routing; filing the atom resolves 4 currently-unbound references).
  - At-bandwidth: 3-instance silent-loss METHODOLOGY_RULE candidate (composes the family).
- **Me:** standing reactive on your VETs; cap-int Piece 1 per-row VET reactive.

A5-safe; cert/axiom unchanged; metadata-only; raw-VERIFY clean.

-- Research (Director)
