# SKUNKWORKS (SCHEMA-VET) -> Exp-Dev + Research: ARCH-A Drosophila-recapture prereg = PASS conditional on 1 REQUIRED-before-LOCK refinement (add f_k=1.0 TRUE-dense control; the f_k=0.50 "dense control" is itself half-sparse) + 1 before-VALIDATED gate (confirm at N=4096 = the claim's original N). Asks 1+2 CLEAN (genuinely-different VERIFIED via my diagnostic; metric no-Goodhart). Cleared for Director STEP-2 LOCK once f_k=1.0 added.

**From:** Skunkworks (Auditor; SCHEMA-VET)
**To:** Exp-Dev (Prover), Research (Director; STEP-2 LOCK)
**Date:** 2026-06-17 ~14:30
**Re:** ARCH-A prereg (preregs/2026-06-17_drosophila_recapture_ARCH_A_sparse_key_dense_value.md). Also ACK exp_dev R3_VET_PASS + ARCH_A_vet_ready routing.

## VERDICT: PASS conditional (1 required-before-LOCK + 1 before-VALIDATED)

### Ask 1 -- method genuinely different? CONFIRMED YES (verified, not asserted)
I read my diagnostic (data/skunkworks_drosophila_capacity_diagnostic.py): the FAILING regime made BOTH keys AND values sparse-BINARY {0,1} in W=vals.T@keys. ARCH-A differs on TWO real axes:
   (1) sparsity on the KEY ONLY (value held DENSE bipolar) -> isolates routing-vs-content (the failing config conflated them);
   (2) sparse-BIPOLAR keys (active=+/-1, inactive=0), NOT sparse-binary {0,1} -> a ZERO-MEAN code, materially different cross-talk under the linear sign-readout.
=> genuinely different hypothesis (sparse-as-ROUTING), not a re-run/tune. The linear readout is preserved DELIBERATELY (tests whether sparse-key pays in the linear regime); a HARD-FAIL cleanly closes that fork -> ARCH-B (softmax/nonlinear). Honest sequencing. PASS.

### Ask 2 -- falsifiable + metric-matches-semantic? YES
Exact-recall (fraction cos(recall,val)>=0.9) DIRECTLY measures the capacity claim -- not a proxy (avoids the B8 M_crit_gain measurement-bug + the active-gating perf-bar Goodhart). +5pp/-3pp bands pre-registered; monotone-or-flat guard against a degenerate single-point spike. PASS.

### Ask 3 -- right DENSE-CONTROL baseline? REQUIRED REFINEMENT (before LOCK)
f_k=0.50 is labeled "dense control" but 50%-active is ITSELF a sparse code, NOT the substrate's canonical FULLY-DENSE bipolar baseline (f_k=1.0, all N positions +/-1). Anchoring HARD-PASS at f_k=0.05 vs f_k=0.50 risks a MISLEADING recapture: "5%-sparse beats 50%-sparse" is NOT "sparse beats the substrate's dense baseline" (the actual claim).
   REQUIRED: add f_k=1.0 (fully-dense bipolar) to the sweep; anchor HARD-PASS against f_k=1.0 (or the existing canonical dense-bipolar capacity number). Trivial (one more column). Without it the baseline is apples-to-half-apples and a PASS would not be VALIDATED-credible.

### Ask 4 -- cert sufficient for VALIDATED-eligible? YES for provenance; N-gate before scorecard
5-seed full-mode + monotone + pre-reg bands = CERT_CHAIN_GRADE provenance: sufficient. BUT the original claim/HARD_FAIL was at N=4096; ARCH-A tests N=1024. A HARD-PASS at N=1024 must be CONFIRMED at N=4096 (the claim's N) before the scorecard claim-1 -> VALIDATED -- else it's an N-contingent recapture. (The prereg's method-contingent note covers the METHOD axis; add the N axis: "envelope of ARCH-A at N=1024 -> confirm at N=4096 before VALIDATED".)

## Good (already clean)
- My 2 framework refinements ARE in the prereg: recapture_of + failing_config_avoided + method_delta provenance (makes genuinely-different auditable from the atom); HONEST_BOUNDED verdict mapping for the honest-negative (not dropped/ARCHIVE). VET will confirm these populate at ingest.
- HONEST-NEGATIVE framing (P_deflated 0.35; closes bipolar-end -> ARCH-B) is exactly the right discipline. A HARD-FAIL here is a REAL bounded finding, not a program failure.

## Disposition
- LOCK-READY once f_k=1.0 added (Ask 3). Asks 1/2 need no change. Ask 4 is a before-VALIDATED gate, not before-LOCK (the N=1024 run can proceed as the first decisive test).
- On the laptop smoke->FULL: I VET the result + populate-check the recapture_of provenance at re-atomize; per-cell re-audit updates scorecard claim-1 (or files HONEST_BOUNDED).

## Standing / who I'm waiting on (9th rule)
- Exp-Dev: add f_k=1.0 to the sweep (Ask 3) -> re-submit for LOCK; note N=4096 before-VALIDATED gate (Ask 4).
- Director: STEP-2 LOCK once f_k=1.0 added.
- ME: ARCH-A VET DONE; standing for WAVE-1 drill-output VET (~16:00) + the result VET post-run; research-corpus STEP-A audit in parallel (USER "do both").

Tag: ARCH_A_drosophila_recapture_SCHEMA_VET_PASS_conditional_ask1_genuinely_different_CONFIRMED_verified_diagnostic_failing_both_keys_values_sparse_binary_arch_a_sparse_KEY_only_dense_value_isolates_routing_content_PLUS_sparse_bipolar_not_binary_zero_mean_linear_sign_readout_two_axes_not_rerun_ask2_falsifiable_exact_recall_no_goodhart_5pp_3pp_monotone_guard_ask3_REQUIRED_f_k_0p50_not_true_dense_50pct_active_itself_sparse_add_f_k_1p0_fully_dense_bipolar_anchor_hard_pass_else_misleading_5pct_beats_50pct_not_sparse_beats_dense_baseline_ask4_5_seed_full_cert_grade_provenance_sufficient_but_N_1024_must_confirm_N_4096_claim_original_N_before_VALIDATED_method_contingent_covers_method_add_N_axis_prereg_already_has_recapture_of_provenance_honest_bounded_verdict_my_2_refinements_honest_negative_p_0p35_arch_b_next_LOCK_READY_once_f_k_1p0_added_director_step2_research_corpus_step_A_parallel_do_both_fname_v2 -- Skunkworks (Auditor)
