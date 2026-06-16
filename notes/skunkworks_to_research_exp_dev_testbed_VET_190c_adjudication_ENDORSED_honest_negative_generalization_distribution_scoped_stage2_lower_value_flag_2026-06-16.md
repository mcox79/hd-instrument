# SKUNKWORKS (Auditor) -> Research + Exp-Dev + Testbed: BINDING VET of 190c per-sibling adjudication (Exp-Dev 232nd) = ENDORSED. I independently read the SOURCE metrics.json (not the orchestrator preview); Exp-Dev's per-sibling adjudication MATCHES my reading EXACTLY. VERDICT: HONEST-NEGATIVE for ARM-1 cardinality GENERALIZATION; capabilities are DISTRIBUTION-SCOPED (real on their original regime; do NOT reach ARM-1 HARD_PASS precision on the shifted higher-count distribution at N<=4096). My DECISION-197 flag VINDICATED (exact-count RMSE 5.60 >> 1.0 = honest-negative, NOT a smoke artifact; Exp-Dev honestly retracted its smoke-artifact hypothesis -- 9th catch). File as a FINDING (honest type). + Stage-2 external-data procurement is now LOWER VALUE (flag to USER before spending).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** VET_190c_adjudication_ENDORSED_honest_negative_generalization_distribution_scoped_stage2_lower_value_flag

## Source-verified (I read data/exp_cardinality_generalization_stage1_190c_cpu_v1/metrics.json, run_mode=full)
```
  EXACT-COUNT: N=2048 C0=15.74/C1=79.73/C2=14.09(std0.86)/env=T -> MIDDLE; N=4096 C0=15.78/C1=79.93/C2=5.60(std0.47)/env=T -> MIDDLE
  MOST(A>B):   N=2048 C1=0.531/C2=0.673(std0.023)/no-drift -> MIDDLE; N=4096 C1=0.543/C2=0.775(std0.015)/no-drift -> MIDDLE
  prereg bars (locked in file): exact RMSE<=1.0 + >=2x C1; most acc>=0.80 + margin>=0.20.
```
Exp-Dev's adjudication numbers MATCH the source exactly (cell-verdict-sourced, not preview). VET binding.

## Per-sibling VET (ENDORSE Exp-Dev's adjudication)
- EXACT-COUNT -> HONEST-NEGATIVE (filed MIDDLE). At N=4096 C2=5.60 BEATS C0 (15.78) + reduces C1 (79.93) by 14.3x
  (>=2x) -> mechanism escapes controls (NOT a HARD_FAIL). BUT absolute RMSE 5.60 >> the 1.0 bar (ARM-1 hit 0.209)
  -> does NOT achieve ARM-1-grade exact-count precision on the higher-count distribution. Per my DECISION-197 flag:
  RMSE>1.0 at full = HONEST-NEGATIVE, NOT artifact-dismissal. CONFIRMED.
- MOST(A>B) -> MIDDLE. N=4096 acc 0.775, margin 0.232 (CLEARS >=0.20 margin; no drift) but acc 0.775 < 0.80 bar
  (misses by 2.5pts). Close, does not clear -> MIDDLE. CONFIRMED.
- OVERALL: NEITHER sibling clears HARD_PASS generalization -> ARM-1 cardinality capabilities are DISTRIBUTION-SCOPED
  (original n_distinct[1,9)/mult[1,4) regime). NO manufactured transfer claim. ARM-1 original atoms UNAFFECTED
  (this BOUNDS their scope; it does not retract them).

## Both-directions honesty -- VERIFIED on both sides
- MY FLAG VINDICATED: I explicitly flagged (190c design VET) "exact-count RMSE>1.0 at full = honest-negative, NOT
  auto-artifact; do not dismiss the smoke MIDDLE." The full run (RMSE 5.60, WORSE than smoke's 2.26) confirms it.
  Exp-Dev HONESTLY RETRACTED its smoke-artifact hypothesis (predicted VOCAB=200 would clear it; it did not -> the
  driver was the COUNT-RANGE shift, not VOCAB). 9th verify-before-asserting catch. Exemplary both-directions.
- DON'T UNDER-CLAIM (confirmed): the mechanism TRANSFERS DIRECTIONALLY (C2 beats both controls on an unfit
  distribution -> cleanup_distinct_count is a real generalizing-in-direction primitive, not an overfit); N-scaling
  helps MONOTONICALLY (exact 14.09->5.60; most 0.673->0.775). The CAPACITY-BOUNDED trend (improving + within-
  envelope) is correctly framed as an UNTESTED OBSERVATION (a higher-N run MIGHT clear it), NOT a pass-claim. I
  CONFIRM this framing: do NOT spin the trend into a pass; the MEASURED result at N<=4096 is MIDDLE/honest-negative.

## FILING -- ENDORSE (FINDING, honest type)
concept::FINDING_cardinality_distribution_scoped_generalization (kind:FINDING; NOT a transfer-capability HARD_PASS).
metric_type AGGREGATE (exact-count RMSE) + RATIO (most acc) -- honest per-sibling types. relates the ARM-1 atoms.
Documents the honest SCOPE BOUNDARY of the ARM-1 cardinality capabilities (real but distribution-scoped; mechanism
escapes controls everywhere; absolute precision degrades on harder distributions; N-scaling helps; capacity-bounded
untested). cap_pres=1.0 trivial (ARM-1 atoms unchanged). Testbed: STRICT type-discipline (FINDING + AGGREGATE/RATIO;
prose by MEASURED values; the capacity-bounded extrapolation labeled UNTESTED). Director: atom-vs-note his call.

## DOWNSTREAM FLAG -- Stage-2 external-data procurement now LOWER VALUE (USER)
ENDORSE Exp-Dev's flag: Stage-1 (controlled generalization) is HONEST-NEGATIVE -> external real-task transfer
(Stage-2) is UNLIKELY to clear the ARM-1 bar (the controlled shift already misses it). Honest to flag to USER
BEFORE procuring Stage-2 external data: the expected value dropped (don't spend procurement effort on a likely-
negative). NOT a hard no -- the USER may want the external data-point anyway -- but the honest expected-value update
is: lower. Surface to USER.

## Consolidation (both Phase-C-tail substrate-internal stretch-arcs now honest-negative)
190a (push ARM-3 uniqueness via prototype-retrieval): HONEST-NEGATIVE (algebraic; ARM-3 stays QUALIFIED).
190c (generalize ARM-1 cardinality to a harder distribution): HONEST-NEGATIVE (distribution-scoped).
-> BOTH stretch-arcs on the EXISTING capabilities came back honest-negative -- cleanly, cheaply (190a saved the GPU
   via algebra; 190c was a bounded 269s run). This HONESTLY BOUNDS the existing capabilities (real, but scoped /
   not-unique) -- it does NOT retract them. The genuine load-bearing forward growth is the USER-gated TIER-3
   FOUNDATION build (Primitives 1+2, foundation-first, literature-grounded by R1+R2). The substrate is honestly
   characterized: what it has (scoped), what it doesn't (general cardinality / unique tier-2 discovery via these
   tasks), and where the next real growth is (TIER-3, USER's call).

Tag: VET_190c_ENDORSE_source_metrics_verified_exact_count_RMSE_5p60_far_above_1p0_honest_negative_my_DECISION197_flag_vindicated_smoke_artifact_diagnosis_WRONG_expdev_retracted_9th_catch_most_acc_0p775_misses_0p80_margin_0p232_passes_MIDDLE_both_siblings_MIDDLE_ARM1_DISTRIBUTION_SCOPED_no_transfer_claim_mechanism_transfers_directionally_beats_controls_N_scaling_helps_capacity_bounded_UNTESTED_observation_not_pass_FINDING_filing_AGGREGATE_RATIO_relates_ARM1_atoms_stage2_external_data_LOWER_VALUE_flag_USER_both_phase_C_tail_arcs_honest_negative_existing_capabilities_bounded_real_growth_is_USER_gated_TIER3_foundation -- SKUNKWORKS (Auditor)
