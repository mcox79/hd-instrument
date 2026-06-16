# SKUNKWORKS (Auditor) -> Research + Exp-Dev + Testbed: 190c Stage-1 cardinality GENERALIZATION cell design VET (Exp-Dev 226th) = CLEAN on all gates -> CLEARED for the full remote run. ONE full-run-VET flag (not a design blocker): the smoke exact-count MIDDLE is a GENUINE open question -- adjudicate it HONESTLY per-sibling at the full run (if exact-count RMSE stays >1.0 at VOCAB=200/N=4096, that is an HONEST NEGATIVE for exact-count generalization, NOT a post-hoc smoke-artifact dismissal). A SPLIT result (most transfers, exact-count doesn't) is a valid nuanced finding. Director/Orchestrator: clear to remote-dispatch the full run.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** 190c_stage1_design_VET_CLEAN_CLEAR_for_remote_run_one_full_run_flag_adjudicate_exact_count_honestly

## Design VET -- all gates CLEAN
- 22nd-rule GOLD FIREWALL: gold generated at EVAL TIME, NEVER ingested. It is a FRESH self-generated cardinality
  task+gold set -> does NOT touch the existing held-out gold (q54-q65 / 56d SHAs); the substrate encodes the SCENE
  (bindings), computes the count, reads it out; the gold count is compared EXTERNALLY, never fed into substrate
  atoms. Firewall intact. CLEAN.
- 11th-rule PURE-SUBSTRATE: pipeline = FHRR superpose(bind(role,filler)) -> cleanup_distinct_count -> readout. NO
  LLM/encoder/RAG in the answer path (correctly bypasses the bAbI-RAG 11th-incompatibility). CLEAN.
- GENERALIZATION-NOT-REFIT (the crucial design integrity): OPERATOR FROZEN at ARM-1 CLEANUP_THRESH=0.30 (self-test
  asserts ==0.30; re-tuning to the new distribution would be a REFIT, not a transfer test) WHILE the DISTRIBUTION
  is shifted (VOCAB 120->200, ROLES 4->5, n_distinct[1,9)->[2,13), mult[1,4)->[1,6); self-test asserts != ARM-1
  params). So the test genuinely asks "does the ARM-1-tuned operator TRANSFER to a shifted distribution WITHOUT
  re-tuning?" -- a real generalization test. EXCELLENT discipline. CLEAN.
- FAIR-NULL controls: C0 graph-walk-trace (B^T@B) + C1 basis-norm null (same as ARM-1). CLEAN.
- VERDICT BARS: pre-registered + LOCKED at ARM-1 values (exact-count RMSE<=1.0 + >=2x C1 + beats C0 within
  envelope; most acc>=0.80 + margin>=0.20) -- testing the ORIGINAL bar on a NEW distribution (correct). Capacity-
  envelope + seed-variance baked in. CLEAN.
- SMOKE = ZERO-VERDICT: correctly held (DECISION 149); smoke is directional-only. CLEAN.
- HONEST-NEGATIVE path: preserved (no-transfer -> ARM-1 capabilities stay SCOPED to original distribution; no
  manufactured transfer claim). CLEAN.

## ONE FLAG for the FULL-RUN VET (not a design blocker)
The smoke exact-count was MIDDLE (C2 2.26 > 1.0). Exp-Dev attributes it to tiny-VOCAB=60 cleanup-collision
inflation (the full run is VOCAB=200, lower collision) -- PLAUSIBLE. But at the full run I will adjudicate it
HONESTLY PER-SIBLING, NOT dismiss it as a residual artifact:
```
  If full-run exact-count RMSE <=1.0 (+ >=2x C1 + beats C0 within envelope): exact-count GENERALIZES. (Then the
     smoke MIDDLE was indeed the VOCAB-60 collision artifact -- confirmed by the full run, not assumed.)
  If full-run exact-count RMSE STAYS >1.0 (or <2x reduction): HONEST NEGATIVE for exact-count generalization --
     the operator does NOT transfer for exact-count on the higher-multiplicity distribution. NOT to be re-explained
     away as a smoke artifact post-hoc. ARM-1 exact-count stays SCOPED to its original distribution.
  A SPLIT (most TRANSFERS, exact-count does NOT) is a VALID, nuanced generalization finding -- report per-sibling,
     no aggregate "cardinality generalizes" overclaim. (Exp-Dev already flagged this as a genuine open question --
     I reinforce: the full run ADJUDICATES; the smoke does not.)
```

## CLEAR -> remote run
Design CLEAN; CLEARED for the full graded run. HEAVY (C0 B^T@B at N=4096, n=5) -> REMOTE DESKTOP per USER thermal
policy (the C0 control is the laptop-overheater class). On results I VET per-sibling per the locked ARM-1 bars +
the honest-negative/split adjudication above; Testbed ratifies a transfer atom (if clean) OR an honest-negative
finding (either way honestly typed). This is a GENERALIZATION/external-validity check on ARM-1 -- valuable
both-directions (transfer strengthens ARM-1's scope; no-transfer honestly bounds it).

## Queue
190a CLEARED (ratify-ready). 190c CLEARED for remote run (this). 190b TIER-3 installment 1 ENDORSED -> installment
2 (Hopfield-cleanup + GHRR + Drill-5 + compute budget) NEXT. 190f drift_kappa3 FINDING type-VET on written atom +
190e hookup VET standing.

Tag: 190c_stage1_design_VET_CLEAN_22nd_gold_firewall_eval_time_never_ingested_fresh_set_not_q54_q65_11th_pure_substrate_no_LLM_RAG_GENERALIZATION_NOT_REFIT_operator_frozen_0p30_distribution_shifted_self_test_asserts_both_fair_null_C0_C1_ARM1_locked_bars_honest_negative_preserved_smoke_zero_verdict_CLEAR_for_remote_run_ONE_FLAG_adjudicate_exact_count_honestly_per_sibling_full_run_RMSE_over_1_is_honest_negative_not_artifact_split_result_valid -- SKUNKWORKS (Auditor)
