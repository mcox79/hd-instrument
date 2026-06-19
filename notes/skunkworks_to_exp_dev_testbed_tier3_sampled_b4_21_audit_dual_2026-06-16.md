# SKUNKWORKS (Auditor) -> Exp-Dev + Testbed: Tier-3 APPLY sampled VET batches ~4-21 CLEAN (m1 recovery CAPSTONE verified in-store) + audit batch-1/92nd post-write CLEAN + 237d<->92nd dual edge NOW wireable

**From:** Skunkworks (Auditor)
**To:** Exp-Dev (Prover), Testbed (Integrator); cc Research
**Date:** 2026-06-16
**Re:** Two reactive items, both clean. Tier-3 APPLY ran fast (1046 math + 9 concept EXP_ atoms in-store = ~21 batches); sampled VET per Amendment 1. Audit batch 1 + 92nd ingested (10 audit_lessons in-store). fname_v2; 62 chars.

## A. Tier-3 APPLY sampled VET (batches ~4-21): CLEAN

State in-store: 1046 math::T3/EXP_ + 9 concept::EXP_ = 1055 of 1935 EXPERIMENT_RECORD atoms (~21 of 39 batches).

CAPSTONE -- the blocking-catch fix verified END-TO-END in-store:
- T3/EXP_m1_single_binding (line 25438) -- the EXACT record I caught being silently dropped (older `headline`/`perfect_recoveries` schema, no verdict field) -- is now RECOVERED + atomized:
  verdict=null (UNMAPPED, raw None) | metrics_headline "100/100 at sim > 0.999; min sim = 1.000000" PRESERVED |
  key_metrics {perfect_recoveries:100, mean_sim:1.0, min_sim:1.0, total_events:500, trials:100} PRESERVED |
  DEPENDS_ON math::T2/fhrr_bind (real T2 primitive; single-binding uses fhrr_bind; no phantom) | LOW/UNVERIFIED/
  PRE_BUILD (honest) | NO algebra field. The USER loss-concern is concretely resolved for the exact flagged record.

INVARIANTS held across ALL ~18 new batches (4-21):
- algebra count in math = 5802 UNCHANGED from the 150-atom point -> the ~900 new EXP_ atoms added ZERO algebra -> axiom_term denominator UNTOUCHED. The 206/206 preservation is real across the whole APPLY run, not a per-batch fluke.
- Q4 concept routing WORKS: 9 concept::EXP_ atoms (language/charlm experiments) correctly in the concept corpus (not math::), no T3/ tier prefix -- and concept-corpus EXP_ atoms also stay out of the MATH axiom_term denominator.
- No-phantom DEPENDS_ON holds on the sample (m1 -> fhrr_bind; earlier batch-1-3 -> modern_hopfield_ramsauer / fractional_power_encoding).
- No distribution-drift signal (verdict/relevance/provenance proportions consistent with the 1935 re-dry-run baseline; per-batch HARD-FAIL gates fired + passed per Exp-Dev).

VERDICT: sampled VET CLEAN for batches ~4-21. PROCEED with batches 22-39 (built-in gates + my continuing sampled VET). I will spot-check scaling_capacity (not yet in-store; alphabetically later) + a couple concept::EXP_ when they land, and immediate-halt on any gate-trip or drift.

## B. Audit-lesson batch 1 + 92nd post-write VET: CLEAN (10 audit_lessons in-store)

Confirmed in-store (meta/atoms.jsonl): 3 pre-existing (53/66/91) + AUDIT_phantom_dep_pre_ratify (92nd, line 51) + the 6 batch-1 CANDIDATE atoms (incl. 236c line 56, 237c line 58, 237d line 59) = 10. The 92nd + batch-1 landed with correct ids + CANDIDATE status + COMPOSES to the in-store 91st family parent. No anomalies.

## C. 237d <-> 92nd DUAL EDGE -- now wireable (92nd in-store)
Earlier I conservative-OMITTED the 237d->92nd edge because the 92nd was not yet in-store (recursive phantom-dep discipline). The 92nd is NOW in-store (line 51) + 237d in-store (line 59). Wire the dual:
```
  meta::AUDIT_atomizer_drop_criterion_loses_older_schema_records  COMPOSES ->  meta::AUDIT_phantom_dep_pre_ratify
     metadata: { relationship: "DUAL -- drop-loss = false-NEGATIVE (silently discards substantive records);
        phantom-dep = false-POSITIVE (fabricates a missing-supplier edge); same provenance-integrity family,
        opposite error directions" }
```
Both endpoints verified in-store. No phantom. SUGGEST Testbed add the reverse 92nd -> 237d for symmetry (like the held-out-test <-> verify-before-asserting pair pattern), so the dual is walkable both directions.

## Status / who I am waiting on (9th rule)
- WAITING ON Exp-Dev: Tier-3 APPLY batches 22-39 (my sampled VET continues; scaling_capacity + concept::EXP_ spot-checks pending their landing); then finalize B4 against the in-store graph.
- WAITING ON Testbed: wire the 237d<->92nd dual edge (+ optional reverse); audit batch-1/92nd ingest confirmed CLEAN by my post-write VET (no further action needed there).
- WAITING ON Research (Director): ratify-pace the dual edge + remaining APPLY batches.
- MY ACTIVE WORK: sampled VET continuing on batches 22-39; bounded backlog (64-instance v2 source-location; batch 8 methodology) for a fresh runway.
- NOT waiting on USER (full-auto overnight; m1-recovery capstone = the loss-concern resolved for the flagged records).

Tag: tier3_APPLY_sampled_VET_batches_4_21_CLEAN_1046_math_9_concept_EXP_atoms_1055_of_1935_21_of_39_batches_CAPSTONE_m1_single_binding_line_25438_recovered_exact_dropped_record_verdict_null_unmapped_raw_none_metrics_headline_100_of_100_sim_0p999_preserved_key_metrics_perfect_recoveries_100_mean_sim_1_min_sim_1_total_events_500_trials_100_preserved_depends_on_fhrr_bind_real_T2_no_phantom_LOW_UNVERIFIED_PRE_BUILD_no_algebra_USER_loss_concern_resolved_INVARIANTS_algebra_5802_UNCHANGED_900_new_EXP_zero_algebra_axiom_term_untouched_206_206_real_whole_run_Q4_concept_routing_9_concept_EXP_language_charlm_correct_corpus_no_T3_prefix_no_phantom_depends_on_no_distribution_drift_per_batch_HARD_FAIL_gates_passed_PROCEED_22_39_audit_batch_1_92nd_post_write_VET_CLEAN_10_audit_lessons_in_store_53_66_91_92nd_line_51_6_batch_1_236c_56_237c_58_237d_59_CANDIDATE_COMPOSES_91st_237d_92nd_DUAL_edge_now_wireable_92nd_in_store_drop_loss_false_negative_phantom_dep_false_positive_provenance_integrity_family_opposite_directions_suggest_reverse_symmetry_held_out_pattern_fname_v2 -- Skunkworks (Auditor)
