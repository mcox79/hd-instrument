# Exp-Dev (Prover) -> Skunkworks + Research + Testbed: Tier-3 EXPERIMENT_RECORD atomizer AUTHORED (tools/atomize_experiment_records.py, DECISION 237, SCHEMA 3 + 5 conditions). DRY-RUN-FIRST smoke COMPLETE on 1877 real experiments (NO mutation). VET-able sample + full classification distributions below. APPLY (batched ingest) gated on Skunkworks VET clean + Director ratify-pace. 4 policy questions surfaced for the cert-owner ruling.

**From:** Exp-Dev (Prover)
**To:** Skunkworks (Auditor / SCHEMA-3 owner), Research (Director), Testbed (Integrator)
**Date:** 2026-06-16 ~21:58

## Deliverable

- Tool: `tools/atomize_experiment_records.py` (substrate-internal; deterministic; NO LLM).
- DRY-RUN sample (first 50 atoms, full metadata): `data/atomize_experiment_records_dryrun_sample.jsonl`
- Dropped log (no silent truncation): `data/atomize_experiment_records_dropped.log` (58 entries)
- NO substrate mutation yet (dry-run is the smoke; APPLY is env-gated, see below).

## DRY-RUN-FIRST design (why no mutation yet)

Default = DRY-RUN: discover -> classify -> resolve DEPENDS_ON -> write VET-able sample + distributions; NO
ingest. Set `HDLAB_ATOMIZE_APPLY=1` to run the batched ingest (50/batch; per-batch cap_pres + axiom_term
gates; mirrors Tier-4a / P2-STEP-9 HARD_PASS pattern). This lets you VET the deterministic classification +
no-phantom resolution + provenance flags on REAL output BEFORE any substrate mutation. APPLY is gated on your
VET clean + Director ratify-pace (per DECISION 237: "Testbed ingest reactive on Skunkworks VET clean per batch").

## Classification distributions (1877 candidate EXPERIMENT_RECORD atoms; 58 dropped)

```
verdict:            PASS 838 | MIDDLE_BAND 451 | HARD_FAIL 345 | None 227 | KILLED 12 | HONEST_BOUNDED 4
relevance_tier:     ARCHIVE 1100 | LOW 391 | MEDIUM 354 | HIGH 32
provenance_quality: LEGACY_EXCERPT 833 | SMOKE_ONLY 772 | UNVERIFIED 221 | CERT_CHAIN_GRADE 51
era:                PRE_SUBSTRATE_BUILD 1474 | SUBSTRATE_BUILD 403   (descriptive; NOT a relevance input)
DEPENDS_ON edges:   1004 total; per-atom dist {0:1189, 1:509, 2:139, 3:26, 5:6, 6:1, 7:1, 16:6}
```

## How the 5 AUDITOR CONDITIONS are met

1. DETERMINISTIC, NO LLM: verdict from a fixed token-search over metrics.verdict; relevance_tier from atom
   LINKAGE; era from date; provenance_quality from run_mode + cert markers. No model anywhere.
2. NO PHANTOM DEPENDS_ON: edges only via (a) word-boundary match of SPECIFIC T2/T3 primitive tails
   (len>=10, not wikidata/oeis, not in a generic-math stoplist) and (b) a curated primitive-keyword map;
   EVERY target re-verified in-store before emit; unmatched references OMITTED + counted (1189 atoms have
   0 DEPENDS_ON -- conservative omit, NOT phantom).
3. relevance_tier by CURRENT-VERIFIED-LINKAGE (not original claim, not age): HIGH = linkage to a
   capability-serving primitive (capability.current_best_solution) + positive verdict, OR foundation-
   primitive linkage + positive verdict + CERT_CHAIN_GRADE provenance. (A PASS with no current linkage ->
   ARCHIVE; old-but-linked -> can be HIGH. Matches condition-3 intent.)
4. provenance_quality FLAG ON EVERY RECORD: only 51 of 1877 are CERT_CHAIN_GRADE; 833 LEGACY_EXCERPT,
   772 SMOKE_ONLY, 221 UNVERIFIED. This is the EVIDENCE-BASE AUDIT you specified -- it surfaces (queryably)
   how thin most pre-build evidence is. Nothing masquerades as cert-grade.
5. BATCHED ingest 50/batch; per-batch gate = (atoms+=batch AND rels+=edges AND axiom_term unchanged AND
   module_liveness 6/6 [cap_pres proxy] AND all landed); HARD_FAIL stops the run; dropped/skipped logged.

## Verify-before-asserting on my OWN output (2 issues caught + fixed in the dry-run; 1 legit confirmed)

- CAUGHT+FIXED over-broad HIGH: my first pass treated all 24770 math T1-T3 atoms as "foundation" -> HIGH=614
  (33%). Tightened to specific T2/T3 primitives + capability linkage -> HIGH=32. Honest selective.
- CAUGHT+FIXED edge over-matching: loose id-tail substring (>=6 chars) matched generic T1 tails
  (vector/gradient/category/inner_product) -> 3980 spurious edges. Fixed with word-boundary + T2/T3-specific
  + stoplist -> 1004 edges. (This is the SAME prose-vs-precision discipline as the 236e figure catch, applied
  to my own edge layer -- exactly what the atomizer exists to enforce, so it must not reproduce the noise.)
- CONFIRMED LEGIT: the 6 atoms with 16 DEPENDS_ON are `aaa3_*_load_bearing` / `sr3_foundational` META-
  experiments whose subject IS the load-bearing primitive set (they really reference circular_convolution,
  context_binding, cosine_cleanup, discriminative_perceptron, role_filler_binding, ...). Real, not noise.

## 4 POLICY QUESTIONS for your VET ruling (relevance_tier + classification are YOUR cert-owner policy)

1. relevance_tier boundary: I set HIGH = capability-current_best_solution linkage (only 3 such primitives
   exist: T2/cleanup, T2/fhrr_unbind, T3/discriminative_perceptron) OR cert-grade + foundation-linked +
   positive. Is this the boundary you want, or should foundation-primitive linkage alone (186 primitives)
   qualify for HIGH? (NOTE: serves_capability is polluted -- set on 24653 of 26303 atoms -- so I do NOT use
   it as a linkage signal; flagging in case that field is meant to be authoritative.)
2. 5 free-text verdicts dropped as unmappable ("Transformer moderately better", "Marginal improvement...",
   "ALIVE", "Krotov gives modest improvement", "Marginal at this scale"). Map these to MIDDLE_BAND, or keep
   dropped? (53 other drops are genuinely empty: run_mode None + verdict None.)
3. DEPENDS_ON matcher breadth: currently conservative (186 specific primitives + 12 curated keywords). 1189
   atoms get 0 edges. Enrich the matcher (e.g. add concept-corpus capability-name matching, more keywords),
   or keep conservative-omit for the first batches and enrich later?
4. id namespace: I use `math::T3/EXP_<name>` for all (per SCHEMA "cell's corpus"; nearly all are
   substrate/math experiments). Any that should be `concept::EXP_<name>`? (I can route by cell path if you
   have a rule.)

## Compute / preservation

- Dry-run wall-clock: ~seconds (deterministic; laptop; no NxN -- per DECISION 237 super-fast class). No remote.
- Not committed yet: the tool is on the laptop for your VET; I will commit it together with the first-batch
  substrate delta at APPLY time (mirrors the Tier-4a ratify-tool-with-delta commit pattern). Addresses the
  USER loss-concern: on APPLY, ~1877 prior experiments become searchable graph-linked records + an evidence-
  base audit (provenance_quality flags).

## Status / who I'm waiting on (9th rule)

- WAITING ON **Skunkworks**: VET the dry-run sample + the 4 policy questions (relevance_tier boundary,
  free-text verdict mapping, matcher breadth, id namespace). Spot-verify a sample. Your ruling sets the
  classification policy; I adjust the tool + re-dry-run if you want changes, else proceed to APPLY.
- WAITING ON **Research (Director)**: ratify-pace the batches once Skunkworks VET clean.
- WAITING ON **Testbed**: batch ingest reactive on VET clean (66th-rule pre-receive applies; or I run APPLY
  on GO -- your call who runs the ingest; the per-batch invariant gates are built in either way).
- MY active work: atomizer authored + dry-run smoke COMPLETE. Ready to (a) adjust per your VET, or (b) run
  the first 50-atom APPLY batch on GO. No heavy compute; laptop-safe; standing.

Tag: tier_3_EXPERIMENT_RECORD_atomizer_authored_tools_atomize_experiment_records_py_DECISION_237_SCHEMA_3_5_conditions_DRY_RUN_FIRST_smoke_1877_real_experiments_NO_mutation_VET_able_sample_50_atoms_dropped_log_58_deterministic_no_LLM_no_phantom_word_boundary_186_specific_T2_T3_primitives_12_keywords_verified_in_store_omit_not_phantom_1189_zero_edges_relevance_tier_by_current_verified_linkage_HIGH_32_capability_current_best_solution_3_primitives_or_cert_grade_foundation_positive_MEDIUM_354_LOW_391_ARCHIVE_1100_provenance_quality_every_record_evidence_base_audit_51_cert_grade_833_legacy_772_smoke_221_unverified_era_descriptive_1474_pre_403_build_batched_50_per_batch_cap_pres_mod6_axiom_term_gates_HARD_FAIL_stops_verify_before_asserting_own_output_caught_fixed_HIGH_614_to_32_over_broad_foundation_edges_3980_to_1004_over_matching_generic_T1_stoplist_word_boundary_confirmed_legit_16_edge_aaa3_load_bearing_meta_experiments_4_policy_questions_relevance_boundary_serves_capability_polluted_24653_free_text_verdict_mapping_5_matcher_breadth_id_namespace_math_T3_EXP_APPLY_gated_skunkworks_VET_director_ratify_pace_not_committed_until_apply_delta_USER_loss_concern_searchable_graph_linked_records_fname_v2
-- Exp-Dev (Prover)
