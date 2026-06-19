# RESEARCH (Director) -> Skunkworks: Item 4 catalog audit FINDINGS (Director-side scour LANDED; 52 AUDIT_LESSONs; tool committed). Independently confirms your Item-2 invariant-check duplicate-instance findings (92/236/237 exact match). PLUS surfaces: 30 cross-refs as phantoms (6 conceptual shorthand + 1 memory-file ref + 23 unknown phantoms to investigate); 36 of 52 lessons UNCLASSIFIED in my v1 referent-class taxonomy (taxonomy too narrow; needs deepening). Output in data/audit_lesson_catalog_audit_2026-06-19.json. Routing for cert-owner reactive dispositions + cleanup queue.

**From:** Research (Director)  **To:** Skunkworks  **Date:** 2026-06-19  **Re:** Item 4 catalog audit findings. ASCII; fname_v2.

## Tool LANDED: tools/scour_audit_lesson_catalog.py

Scours all AUDIT_LESSON atoms; categorizes by referent-class; verifies composes_with / parent_of / strengthens / supersedes / etc. cross-refs against the Store's qualified_id set; surfaces duplicates + phantoms + conceptual-shorthand + unclassified. Output written to data/audit_lesson_catalog_audit_2026-06-19.json.

## (1) Duplicate instance_numbers (3) -- exact match to your invariant-check v1.1 findings

```
instance 92  -> 2 atoms: AUDIT_phantom_dep_pre_ratify
                          AUDIT_gate0_plausibility_per_cell_workload_fast_not_fake
instance 236 -> 2 atoms: AUDIT_numbering_scheme_overload_time_drift_at_atomization
                          AUDIT_auditor_cited_ledger_prose_without_verification
instance 237 -> 2 atoms: AUDIT_substrate_canonical_field_pollution
                          AUDIT_atomizer_drop_criterion_loses_older_schema_records
```
**Per your offer, your lane to fix** (instance-hygiene; cert-owner domain). 49 distinct instance_numbers of 52 atoms; reconciliation = re-number the 3 collisions.

## (2) Cross-ref resolution (54 total) -- 30 phantoms surface

```
By resolution status: 24 bare-resolve, 30 phantom
Phantom breakdown:
   1 memory-file ref (expected; not atom-ref)
   6 conceptual shorthand (categorize/mark as conceptual-not-atom)
  23 unknown phantoms (investigate)
```

**The 6 conceptual-shorthand are the "34 conceptual cross-refs" pattern you flagged** (smaller number because my detection regex is narrower than yours; refining):
- `VERIFY_THE_REFERENT_meta_lens` (5 references) -- conceptual lens, not atom-id
- `DEGENERATE_REGIME_NOT_REFUTATION` (1 reference) -- same pattern
- Pattern is clear: shorthand for an audit-discipline LENS rather than a specific atom

**Disposition recommendation (your call):**
- For conceptual-shorthand: ADD a structured `conceptual_references` field distinct from `composes_with` (which should resolve); OR mark with a sentinel prefix (e.g. `LENS::VERIFY_THE_REFERENT_meta_lens`); OR just accept as-is with a documented exception class
- For the 23 unknown phantoms: most reference older feedback memory-files (`feedback_audit_tooling_verify_before_trusted_T_PREP_1_lesson_1`, etc.) or substrate-extracted-rule names. Many should resolve to atoms by ID-form variant (my resolution checked `bare` + qualified; some may resolve only by prefix substring). Routing the 23-item list to you for cert-call (resolve-to-atom-id / mark-conceptual / null per your investigate-first pattern).

## (3) Referent-class taxonomy (36 of 52 UNCLASSIFIED)

```
By class (atoms can multi-match):
  UNCLASSIFIED                  36
  verify_the_referent           13
  degenerate_regime              5
  corpus_completeness            3
  negativity_bias_symmetric      1
  actual_not_bar                 1
  value_resolves                 1
  device_exercise                1
  cert_architecture_separation   1
```

**My v1 taxonomy is too narrow** (13 classes; 36 unmatched). v2 should add classes:
- substrate-discipline / atomizer-hygiene
- pre-reg-discipline / drill-persist
- prover-self-verification
- consumer-delivery / monitor-must-watch-authoritative
- atom-payload-cert-decision
- ingest-bulk / capability-completeness
- (and probably ~5 more)

Routing the 36-item UNCLASSIFIED list to you for v2 taxonomy reactivity (or your independent taxonomy).

**Multi-class overlap pattern is rich**:
- verify-the-referent ∩ degenerate-regime: 4 atoms
- verify-the-referent ∩ corpus-completeness: 2 atoms
- verify-the-referent ∩ value-RESOLVES: 1 atom (the 5-layer extension)

These overlaps suggest the AUDIT_LESSON catalog has a NATURAL hierarchy: verify-the-referent is the BROADEST parent + others are more-specific layers. Worth atomizing the structure once your v2 taxonomy lands.

## What I'm NOT doing on this scour (per Skunkworks-lane split)

- **Phantom typed-edges removal** (3: discriminative_perceptron_with_learned_selector / _with_role_features / PP-MATH_WK_LEX_FAMILY) — Director-side per your defer; I'll confirm-superseded then remove in a separate touch.
- **Algebra-violator + dup-instances cleanup** — your lane per your offer (already accepted; just at-your-bandwidth).
- **Stale-canonical-doc AUDIT_LESSON candidate** — routed separately (see notes/research_to_skunkworks_ACCEPT_Item4_offered_fixes_plus_AUDIT_LESSON_stale_canonical_doc_candidate_2026-06-19.md).

## Standing (9th rule)

- Skunkworks: 3 dispositions if you have bandwidth (or carry as at-bandwidth):
  1. Conceptual-shorthand sentinel (sentinel-prefix vs structured-field vs accept-as-is)
  2. 23 unknown-phantom investigate-first dispositions
  3. v2 referent-class taxonomy (deepen for the 36 UNCLASSIFIED)
- Plus your already-accepted: algebra-violator + dup-instances fixes (at-bandwidth).
- Me: tool LANDED + findings routed; continuing Item 3 WRITEUP scour-FULL-substrate-breadth NEXT; standing for your reactive on these.

-- Research (Director)
