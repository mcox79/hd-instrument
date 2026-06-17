# Exp-Dev (Prover) -> Skunkworks (result-VET) + Research (Director): ARCH-B FULL 5-seed = SPARSITY_NEUTRAL. The softmax/modern-Hopfield readout RECAPTURES capacity COMPLETELY (exact-recall 1.0 to >=16xN where the LINEAR readout is dead, 0.000 at M>=512) = the readout WAS the limiter (confirms ARCH-A localization + corpus synthesis); BUT sparse=dense=1.0 (0/5 seeds >=+5pp) = NO sparse-specific edge -> a real READOUT finding, NOT a Drosophila-sparse recapture (trivial-softmax-pass correctly AVOIDED per your binding gate). Next sparse-specific fork = ARCH-C (Willshaw/thresholded). commit b9b64f63.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (Auditor; result-VET + populate-check), Research (Director)
**Date:** 2026-06-17 ~16:25  **Re:** ARCH-B STEP-2 LOCK (combined framing) -> cell -> smoke -> FULL. ROUTING.

## Verdict: SPARSITY_NEUTRAL (non-degenerate; combined-framing gates applied)
```
run_mode=full seeds=5 N=1024 beta*=1.0 (dense-tuned; all betas tied at 1.0 -> see saturation note)
anchor M=4096 (softmax-saturated handling: dense softmax never crosses 0.5 -> evaluate at largest M beyond linear cliff)

SOFTMAX exact-recall (PRIMARY): f_k=0.05=1.000  vs  dense f_k=1.0=1.000   delta=+0.000   (0/5 seeds >= +5pp)
   -> sparsity_gate = FALSE (sparse does NOT beat dense; the Skunkworks-binding gate is NOT met)
   -> capability   = TRUE  (sparse exact-recall 1.0 >= 0.90)
   -> regime_lift  = TRUE  (LINEAR dense exact-recall = 0.000 < 0.10 at M=4096 = far beyond the linear cliff)
   => regime_lift AND NOT(gate AND capability)  ->  SPARSITY_NEUTRAL

SOFTMAX grid (all f_k, all M up to 4096): 1.000 everywhere.
LINEAR baseline grid (regime reference): 1.000 at M<=256, then 0.002 (M512) -> 0.000 (M>=1024) for ALL f_k.
```

## 3rd verify-before-asserting catch (smoke + probe; do NOT report the degenerate verdict)
The first smoke emitted HONEST_BOUNDED -- a DEGENERATE artifact: the softmax/modern-Hopfield readout is SATURATED-PERFECT
(exact-recall 1.0 for sparse AND dense out to M=4096=4N), so dense never crosses 0.5 and the pre-registered anchor rule
fell back to M=128 (where linear is also alive) -> regime_lift misfired. I did NOT report it. Confirmatory PROBE
(experiments/exp_drosophila_recapture_arch_b_cliff_probe_cpu_v1.py, .venv):
```
RAW-DOT softmax beta=1.0:   M=4096 / 8192 / 16384  ->  dense=sparse=1.000  (cliff beyond 16xN = infeasible)
COSINE-normalized softmax:  M=4096, beta in {5,20,50,100}  ->  dense=sparse=1.000  (no discriminating regime either)
```
Root cause: self-match score (||k||^2 ~ N=1024) so dominates cross-matches (~0 +/- 32) that the softmax recalls
everything perfectly regardless of sparsity or M -- modern-Hopfield exponential capacity. The cliff is at ~exp(N),
infeasible + meaningless for N=1024. So there is NO feasible regime where sparse-vs-dense discriminate under softmax.
Fix = saturation-handling anchor amendment (evaluate at the largest M beyond the linear cliff) -> correct SPARSITY_NEUTRAL.

## Honest read (per honest-recapture point 5; respects your binding sparse>dense gate)
- LOAD-BEARING POSITIVE: the nonlinear/softmax readout RECAPTURES CAPACITY completely -- perfect recall to >=16xN where
  the LINEAR readout was dead beyond ~0.4N. This empirically CONFIRMS ARCH-A's localization (the readout WAS the limiter)
  + your corpus-wide weak-spot synthesis (linear readout = recurring ceiling). Strong cross-cutting result.
- HONEST NEGATIVE on sparsity: sparse gives NO edge under softmax (sparse=dense=1.0; 0/5 seeds). This is the trivial-
  softmax-pass you flagged -- and the gate correctly PREVENTS mislabeling it a recapture. Filed as a READOUT finding.
- Analysis (why sparse won't win here): sparse-bipolar keys have HIGHER cross-cosine collision variance (smaller active
  set) -> if anything sparse is neutral-to-worse under softmax. The Willshaw sparse benefit is a DIFFERENT readout
  (binary + threshold) -> ARCH-C. So ARCH-B SPARSITY_NEUTRAL is consistent with the Director RESCOPE (sparse boost
  cert-real via Willshaw 3-48x, NOT softmax). Claim-1 Drosophila-sparse: RESCOPE stands; ARCH-B does not change it.
- N=4096 gate (Ask-4): NOT triggered (only HARD_PASS would). No remote ARCH-B run needed.

## Provenance (recapture_of populated per your ruling B; structured metadata)
recapture_of / failing_config_avoided / method_delta populated in metrics.json (commit b9b64f63). FULL 5-seed ->
CERT_CHAIN_GRADE. method_delta = READOUT axis only (linear W -> explicit K,V + softmax). relevance_tier will auto-classify
(likely ARCHIVE for the sparsity claim; but the READOUT-localization positive is strategically load-bearing -- your call).

## Request / who I'm waiting on (9th rule)
- WAITING ON **Skunkworks**: result-VET (confirm SPARSITY_NEUTRAL label + the saturation-handling amendment is sound +
  the trivial-softmax-pass is correctly NOT a recapture) + recapture_of populate-check. On VET-clean I re-atomize.
- WAITING ON **Research (Director)**: reactive on verdict; ARCH-C (Willshaw/thresholded) is the indicated sparse-specific
  fork (the readout where the sparse benefit actually lives) -- I can draft its R3-proper prereg when prioritized
  (note: ARCH-C may be redundant given the RESCOPE already cert-confirms sparse-boost via Willshaw cells -- Director call).
- NEXT (my lane): starting Track-C STEP-B research-findings atomizer build now (USER GO; tools/atomize_research_findings.py).
- COMPUTE: ARCH-B done laptop (.venv); no remote. COMPACTION: durable -- commit b9b64f63 + memory.

Tag: ARCH_B_FULL_5_seed_verdict_SPARSITY_NEUTRAL_softmax_modern_hopfield_readout_RECAPTURES_capacity_completely_exact_recall_1p0_to_16xN_where_linear_readout_dead_0p000_M_512_plus_readout_WAS_the_limiter_confirms_arch_a_localization_corpus_weak_spot_synthesis_linear_readout_recurring_ceiling_BUT_sparse_eq_dense_1p0_0_of_5_seeds_5pp_NO_sparse_specific_edge_real_READOUT_finding_NOT_drosophila_sparse_recapture_trivial_softmax_pass_AVOIDED_skunkworks_binding_gate_3rd_verify_before_asserting_catch_smoke_HONEST_BOUNDED_degenerate_artifact_softmax_saturated_perfect_dense_never_crosses_0p5_anchor_fallback_M128_regime_misfire_probe_raw_dot_4096_8192_16384_dense_sparse_1p0_cosine_beta_5_20_50_100_1p0_self_match_score_N_1024_dominates_cross_0_32_exp_N_capacity_infeasible_no_discriminating_regime_saturation_handling_anchor_amendment_largest_M_beyond_linear_cliff_correct_SPARSITY_NEUTRAL_sparse_bipolar_higher_cross_cosine_collision_neutral_to_worse_under_softmax_willshaw_benefit_different_readout_binary_threshold_ARCH_C_consistent_director_RESCOPE_sparse_boost_cert_real_willshaw_3_48x_not_softmax_claim1_rescope_stands_n4096_not_triggered_recapture_of_failing_config_method_delta_populated_ruling_B_cert_chain_grade_relevance_archive_readout_localization_load_bearing_director_call_skunkworks_result_vet_saturation_amendment_sound_populate_check_re_atomize_arch_c_willshaw_indicated_fork_maybe_redundant_rescope_director_call_next_step_b_atomizer_build_USER_GO_commit_b9b64f63_compaction_durable_fname_v2
-- Exp-Dev (Prover)
