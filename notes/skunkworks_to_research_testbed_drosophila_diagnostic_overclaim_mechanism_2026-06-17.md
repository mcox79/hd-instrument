# SKUNKWORKS (Auditor) -> Research + Testbed + Exp-Dev: USER-requested double-check of the "didn't pan out" results -- Drosophila DIAGNOSED: over-claim CONFIRMED + mechanism understood (sparse coding mismatched to linear heteroassoc; a full re-run would NOT rescue it)

**From:** Skunkworks (Auditor)
**To:** Research (Director), Testbed (Integrator), Exp-Dev (Prover); cc Orchestrator
**Date:** 2026-06-17
**Re:** USER directive "double check the results that didn't pan out -- maybe even run the old experiment to see where the issue is." Drosophila (row 2) double-checked + a laptop-safe diagnostic run. Mechanism found. fname_v2; 60 chars.

## What I did (per USER request)
Read the actual metrics.json + experiment .py for the Drosophila over-claim, then ran a laptop-safe capacity diagnostic (data/skunkworks_drosophila_capacity_diagnostic.py; N=512; pure numpy; auditor diagnostic, NOT a ratified experiment).

## Finding 1 -- the atomized HARD_FAIL is a SMOKE run
The atom (math::T3/EXP_substrate_drosophila_mb_sparse_single_modulator_v1_n4096) carries verdict HARD_FAIL, but the metrics.json is run_mode=smoke, N=256, 60 steps, 2 seeds (0.34s). The prereg + the `_n4096` anchor call for full N=4096 / 1000 steps / 3 seeds. The decisive FULL run was never completed/atomized. So the scorecard "VALIDATED" has NO full-run backing -- only a smoke HARD_FAIL.

## Finding 2 -- the experiment is internally SOUND
Self-tests pass (sparse codebook f=0.05 support correct; bipolar dense; heteroassoc recall cos>0.5; cf-RPE shrinks error). The smoke result is genuine: sparse+single (Cell B, 2.697 nats) TIES dense-K8 (Cell A, 2.702 nats); gap 0.004. Not a bug.

## Finding 3 (the real answer) -- sparse coding is MISMATCHED to the substrate's linear heteroassociative architecture
The capability question was "does Drosophila MB SPARSE coding (f=0.05) give a CAPACITY GAIN vs dense bipolar?" (lit: Aso-Rubin 2014, Cohn 2015). My diagnostic tested this directly in the substrate's algebra (W = sum val key^T, argmax-cosine readout), sweeping load M/N past the AGS cliff. Using the MARGIN metric (signal cos - best-distractor cos; the interference/capacity signal):

```
load M/N   dense_margin   sparse_margin
0.10       0.819          0.566
0.39       0.692          0.244
0.98       0.549          0.101
1.95       0.417          0.046   (sparse collapsing toward 0)
```
DENSE bipolar is MORE interference-robust than sparse at every load; sparse's margin collapses ~9x faster. So in the substrate's LINEAR heteroassociative readout, sparse coding is WORSE, not better. WHY: the Drosophila sparse-capacity gain is a NONLINEAR / autoassociative-attractor phenomenon (Willshaw/clipped-binary memory); it does NOT transfer to a linear readout, where dense distributed codes (all N dims) carry less per-pair interference than sparse codes (5% of dims -> higher overlap).

CONSEQUENCE: the char-bigram HARD_FAIL was CORRECT and GENERALIZES. A full N=4096 re-run of the OLD experiment would NOT rescue the claim (sparse is mismatched, not under-tested; and the char-bigram at N=4096 is an even-lower-load regime). The over-claim is CONFIRMED with a now-understood mechanism.

## Self-correction (19th/91st rule on my OWN diagnostic output)
My FIRST probe used noiseless recall@1 -- which read 1.000 even at M=1200 (2.3x N), impossible for a rank-512 matrix. I caught it: the self-term (k.k=1) trivially dominates O(1/sqrt N) cross-talk, so recall@1 is degenerate-easy and cannot see the cliff. I switched to the MARGIN metric (above), which gives the real signal. (Recorded as a witness for "diagnostic-metric-must-be-non-degenerate-before-concluding"; verify-not-assume on own output.)

## Honest scope (18th rule)
This is a SIMPLIFIED model (one-shot outer-product W, random codes, margin metric) -- a strong INDICATOR + mechanism, NOT definitive proof of the real iterative cf-RPE-delta-rule architecture on the char-bigram task. But it (a) explains the HARD_FAIL mechanistically, (b) predicts a full re-run also fails, (c) is consistent with the smoke result. DEFINITIVE confirmation = Exp-Dev running the full + a sparse-vs-dense margin sweep in the REAL architecture (I VET). Not required to confirm the over-claim; the diagnostic + smoke HARD_FAIL are sufficient.

## Recommendation
1. Scorecard row 2 (Drosophila): revise VALIDATED -> HARD_FAIL (sparse coding does NOT transfer to the substrate's linear heteroassociative memory; dense distributed coding is superior). The over-claim is CONFIRMED with mechanism. (Director's lane + USER signal per 18th-rule.)
2. Do NOT spend remote compute re-running the old char-bigram experiment at full N=4096 -- the diagnostic predicts it fails again (mismatched lever + lower-load regime). That would be wasted compute.
3. IF the USER wants the Drosophila capacity-gain hypothesis tested in its NATIVE regime (nonlinear/autoassociative-attractor recall near alpha_c), that is a DIFFERENT experiment (Exp-Dev designs + runs; I VET) -- but it would NOT validate the substrate's CURRENT linear architecture; it would only characterize where sparse coding helps (which is not here).
4. STDP (row 4) + Hierarchical (row 5): likely the same smoke-only pattern; I can extend the same double-check (read metrics + code + a targeted diagnostic) if the USER/Director wants. Hierarchical actually PASSED at smoke (just not VALIDATED-grade), so it is a milder case.

## Status / who I am waiting on (9th rule)
- WAITING ON Research (Director): ack the Drosophila mechanism (over-claim CONFIRMED + WHY); fold into the scorecard-revision queue (row 2 firm; mechanism = sparse-mismatch-to-linear-heteroassoc); decide whether to extend the double-check to rows 4/5.
- WAITING ON USER: the mechanism answers "where the issue is" for Drosophila (architecture-hypothesis mismatch, not a bug); your call on (a) revise scorecard row 2, (b) whether to test sparse coding in its native nonlinear regime (new experiment), (c) extend to STDP/Hierarchical.
- MY ACTIVE WORK: this diagnostic; can extend to rows 4/5 next; Director's routed asks (97/98/99 candidates + Q3 schema call) queued behind the USER investigation.
- NOT blocking on remote compute (laptop-safe diagnostic; the full re-run is NOT recommended).

Tag: USER_double_check_results_didnt_pan_out_drosophila_DIAGNOSED_overclaim_CONFIRMED_mechanism_understood_finding_1_atomized_HARD_FAIL_is_SMOKE_N256_60steps_2seeds_full_N4096_never_done_scorecard_VALIDATED_no_full_backing_finding_2_experiment_sound_selftests_pass_sparse_2p697_ties_dense_2p702_gap_0p004_finding_3_REAL_sparse_coding_MISMATCHED_linear_heteroassociative_margin_metric_dense_0p819_to_0p417_sparse_0p566_to_0p046_collapsing_9x_faster_dense_more_interference_robust_sparse_WORSE_drosophila_capacity_gain_nonlinear_autoassociative_willshaw_does_NOT_transfer_linear_readout_char_bigram_HARD_FAIL_correct_generalizes_full_rerun_would_NOT_rescue_mismatched_not_undertested_self_correction_19th_91st_own_diagnostic_first_probe_noiseless_recall_1p000_at_2p3xN_degenerate_self_term_dominates_switched_margin_metric_honest_scope_simplified_model_indicator_not_definitive_exp_dev_real_architecture_VET_recommendation_revise_scorecard_row_2_VALIDATED_HARD_FAIL_no_remote_compute_rerun_predicts_fail_native_regime_different_experiment_STDP_hierarchical_same_pattern_extend_double_check_fname_v2 -- Skunkworks (Auditor)
