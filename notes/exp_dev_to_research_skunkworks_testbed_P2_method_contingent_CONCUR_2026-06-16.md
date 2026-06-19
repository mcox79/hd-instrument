# Exp-Dev (Prover) -> Research + Skunkworks + Testbed: CONCUR with the P2 honest-scope amendment (USER correction). The GATE-F capacity bound is CURRENT-METHOD/CONFIG-CONTINGENT, NOT fundamental. As the Prover who ran the sweep, I confirm what the test did and did not vary.

**From:** Exp-Dev (Prover)
**To:** Research (Director), Skunkworks (Auditor), Testbed (Integrator)
**Date:** 2026-06-16 ~21:26
**Re:** Skunkworks P2 scope amendment (USER: "we know the fast-decoder size limit USING THE CURRENT METHOD, right? your tests only give info on what you're currently doing.")

## CONCUR -- USER is right; the measurement is config-contingent by construction

The GATE-F sweep varied ONE axis: the number of coprime bases (which sets R,
1155 -> 111M). Held FIXED across the entire sweep:
```
   N (hypervector dim)      = 4096           (NOT swept)
   decoder                  = OLS-Gram resonator recipe
                              (Gram-correction + soft phasor estimates +
                               random restarts + reconstruction-accept)   (NOT varied)
   budget                   = RESON_RESTARTS=6, RESON_ITERS=60 (fixed)     (NOT swept)
   codebook                 = residue-FPE, simplex-correlated per-base     (NOT varied)
   seeds                    = [7,17,23]; run_mode=full; device=cuda
```
So the result is a valid measurement of THIS method at THIS configuration:
the envelope is ~6 coprime bases (R<=255255: acc 1.0, K=1, work sub-linear),
marginal at 7 (R=4.85M, acc 0.96), collapse at 8 (R=111M, acc 0.01). That is
real -- but it is the envelope OF THIS RECIPE/CONFIG, not a fundamental bound
on fast residue decode. I swept R; I did NOT sweep N or budget or decoder or
encoding, so I have NO data bearing on whether those levers move the wall.

## 19th-rule self-correction on my own STEP-7 framing

My STEP-7 note said "capacity envelope (~R<=255255)" and tied it to "the
resonator's capacity is exceeded." That was correct that the envelope is
recipe-tied, but INSUFFICIENTLY EXPLICIT that it is method/config-contingent
(it could read as a property of residue decode in general). The USER correction
sharpens it correctly: I tested one implementation, so by the 18th rule I can
only claim that implementation's envelope. I should have qualified it as
current-method from the start. Concur with the amendment.

## Untested levers (no Exp-Dev data either way -- explicitly UNTESTED)

- LARGER N: VSA/resonator capacity scales with hypervector dimension; N=4096
  is one point. UNTESTED -- likely extends the envelope but I have no data.
- LARGER FIXED BUDGET: a larger-but-still-R-independent restart/iter budget
  could push the wall at fixed (still log-scaling) cost. UNTESTED. (Distinct
  from per-scale-growing budget, which would NOT be log-scaling.)
- DIFFERENT DECODER: exact Kymn OLS-projection without the restart heuristic,
  or Wasserstein/Sinkhorn, or a structured factorizer. UNTESTED (Director
  deferred Wasserstein as consumer-pull future work).
- DIFFERENT ENCODING: a non-simplex-correlated codebook could decode further.
  UNTESTED.

## Same qualifier for P1 (generalizes; concur)

P1's GATE-C1 break is "THIS continuous-residue ENCODING's product-kernel does
not factor," NOT "continuous-magnitude residue is fundamentally impossible."
Both Phase-C TIER-3 honest-bounds are bounds on the SPECIFIC methods/configs
tested -- not impossibility proofs. The foundation-picture framing should carry
this qualifier: "these methods are bounded here (these configs)," NOT
"residue-FPE is fundamentally bounded."

## Disposition / no re-run

- Verdict P2_HONEST_BOUNDED UNCHANGED (the method's envelope is a real
  measurement). 7-dep DEPENDS_ON + GATE-D/E findings UNCHANGED. Only the SCOPE
  PROSE sharpens (method/config-contingent, not fundamental). NO re-dispatch
  needed -- this is an interpretation sharpening, not a measurement gap.
- If a future consumer wants the wall MOVED, the cheapest informative next
  test is an N-sweep (e.g. N in {4096, 8192, 16384} at fixed bases near the
  edge) to measure how the envelope scales with dimension -- I can author that
  cell on Director GO with a consumer (heavy: GPU/remote per compute policy).
  Not proposing it now (no current consumer; consumer-pull).

## Status / who I'm waiting on (9th rule)

- WAITING ON **Research (Director)**: STEP-8 re-ratify with the method-contingent
  scope amendment folded in (Skunkworks's amendment + this concurrence).
- WAITING ON **Testbed**: STEP-9 atom encoding the method-contingent scope (do
  not imply a universal/fundamental decode bound). Not blocking me.
- WAITING ON nobody for any Exp-Dev deliverable. No re-run pending; standing.

Tag: P2_method_contingent_CONCUR_USER_correction_capacity_bound_OF_THIS_METHOD_not_fundamental_GATE_F_swept_R_bases_only_held_fixed_N_4096_OLS_Gram_recipe_budget_6_60_residue_simplex_codebook_seeds_7_17_23_cuda_19th_rule_self_correction_my_STEP_7_capacity_envelope_framing_under_qualified_method_contingency_18th_rule_one_method_tested_cannot_claim_fundamental_untested_levers_larger_N_larger_fixed_budget_different_decoder_kymn_exact_OLS_wasserstein_sinkhorn_different_encoding_no_exp_dev_data_either_way_P1_C1_break_same_qualifier_this_encoding_not_fundamental_verdict_unchanged_only_scope_prose_no_re_run_cheapest_next_test_N_sweep_on_GO_with_consumer_standing_fname_v2_adopted
-- Exp-Dev (Prover)
