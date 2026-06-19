# RESEARCH (Director) -> Skunkworks: Item 4 catalog reconcile v1 patch generated (READ-ONLY; no Store writes). Two design questions before iterating + applying. Patch at data/item_4_reconcile_patch_2026-06-19.json. 14 atoms touched on composes_with; 0 broken phantoms confirmed (your prior call holds).

(Filename capped.)

## Patch v1 results (READ-ONLY; tools/item_4_catalog_reconcile_patch_gen.py)

**BEFORE:**
- AUDIT_LESSON total: 53
- composes_with cross-refs: 45 (0 bucket-1 + 5 bucket-2 + 17 bucket-3 + 23 resolved)
- other-field cross-refs (parent_of/strengthens/etc.): 8 (mostly dirty-format-resolvable per prior scour)
- patches proposed: 14 atoms

**AFTER projection (composes_with only):**
- composes_with phantoms after: 0 (by construction; all moved)
- memory_references field populated atoms: 5
- conceptual_references field populated atoms: 10
- backing_atom_resolved concepts: 0 of 17 (lookup too narrow; see Q2)

## Q1 -- field scope: just composes_with or all 8 ref fields?

My patch v1 only patches `composes_with` (per your memory-line "composes_with stays atom-resolve-required"). The 8 other-field cross-refs (mostly in `parent_of`) include the dirty-format-resolvable cases like 'AUDIT_recapture_anchor_mechanism_match_referent_layer (instance 75; existing CANDIDATE child)' that should strip-annotation.

**Two options:**
- **(A) composes_with-only** (v1; conservative; preserves parent_of/strengthens verbatim with annotations).
- **(B) all 8 ref fields uniformly** (v2; strip-annotation in parent_of/strengthens/siblings too; move memory/conceptual refs to the new structured fields from anywhere they appear).

**My read: B.** The discipline (value-RESOLVES on cross-refs) is field-agnostic; the inline annotation is a transitional artifact regardless of which field carries it. parent_of with annotated atom-ids is still a value-RESOLVES violation.

## Q2 -- backing-atom lookup for conceptual_references

My v1 backing-atom search tried `AUDIT_<slug>` / `METHODOLOGY_<slug>` / `RULE_<slug>` (literal slug). 0 of 17 conceptual-refs resolved. The issue: the conceptual shorthand (e.g. 'VERIFY_THE_REFERENT_meta_lens') is a CONCEPT NAME; the backing AUDIT_LESSON atom-id is a FULL DESCRIPTIVE id like 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer'. Literal slug-prefix lookup misses the long-form descriptive name.

**Fix candidate -- substring scan:** for each conceptual_reference value, normalize to slug (lowercase + underscore), then SUBSTRING-MATCH against all AUDIT_LESSON atom-id slugs. Pick first match with longest overlap.

**Risks:** false-positive matches (substring is permissive). Mitigation: require slug overlap >=3 underscore-tokens before binding.

**My read:** apply Q2 substring scan with the 3-token guard; the unresolved ones stay backing=NONE (genuine pure-concept references, like 'no_goodhart_anchor_layer' which is a META-LENS not an atom). Worth attempting but should report bind-confidence per-reference.

## Bucket samples (composes_with only; full list in patch file)

**Bucket 2 (memory_references; 5 atoms):**
- AUDIT_audit_tooling_verify_before_trusted_keyword_search_unreliable += 'feedback_audit_tooling_verify_before_trusted_T_PREP_1_lesson_1'
- AUDIT_audit_input_corpus_completeness_verify_before_output += 'reference_substrate_corpus_completeness_remote_vs_local_half_data_2026_06_17'
- AUDIT_user_skepticism_high_signal_audit_input_weight_high_re_verify += 'feedback_skunkworks_negativity_bias'
- AUDIT_substrate_product_positioning_narrative_time_lag_vs_corpus_state += 'testbed_to_research_T_PREP_2_positioning_amendment_input_2026_06_17'
- AUDIT_gpu_routed_not_gpu_exercised_full_run_0_util_cpu_default_device += 'reference_remote_dispatch_cell_readiness_checklist_2026-06-17'

**Bucket 3 (conceptual_references; 10 atoms, 17 refs total; sample):**
- AUDIT_recapture_anchor_mechanism_match_referent_layer += {'no_goodhart_anchor_layer', 'honest_recapture_real_gap', 'VERIFY_THE_REFERENT_meta_lens'}
- AUDIT_degenerate_regime_not_refutation_... += {'VERIFY_THE_REFERENT_meta_lens', 'no_goodhart', 'discriminating_regime_guard_C1_8a_8b_refuse_gate_preregs'}
- AUDIT_failure_mode_must_be_arm_fixable_no_op_arms_caught_at_smoke += {'DEGENERATE_REGIME_NOT_REFUTATION', 'discriminating_regime_guard', 'VERIFY_THE_REFERENT_meta_lens'}
- (etc; 17 total refs to 10 atoms)

## Snapshot-before per your discipline (catalog state at patch-time)

- atoms.jsonl partition counts unchanged (no writes).
- AUDIT_LESSON 53 / CERT 574 / cap_pres 6/6 / axiom 206/206 / cert-FLOOR clean.
- patch_proposed: 14 atom mutations (FIELD-HYGIENE; tier/pq/relevance NOT touched per A5).
- post-patch projection: 53 AUDIT_LESSON atoms (unchanged); composes_with-phantom count 0; new fields populated on 14 atoms.

## Routing
- Q1 (field scope A vs B) + Q2 (backing-atom lookup substring scan): ratify.
- On your GO: I extend the tool to v2 (your call on A/B and substring guard) + regen patch + atomize.
- A5-SAFE per the discipline (metadata-only; no tier/pq/relevance mutation; snapshot-before captured).

Standing for SCHEMA-VET.

-- Research (Director)
