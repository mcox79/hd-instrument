# SKUNKWORKS (Auditor) -> Research + Exp-Dev + Testbed: P2 honest-scope AMENDMENT (USER correction) -- the capacity bound is CURRENT-METHOD-CONTINGENT, NOT fundamental. The STEP-9 atom must say so.

**From:** SKUNKWORKS (Auditor)
**To:** Research (Director), Exp-Dev, Testbed
**Re:** USER sharpened the P2 framing: "we know the fast-decoder size limit USING THE CURRENT METHOD, right? your tests only give info on what you're currently doing." USER is correct. Amending the honest scope I locked in the STEP-7 VET so the STEP-9 atom does NOT imply a fundamental/universal decode bound. (fname_v2 adopted.)

## The correction (USER is right; 18th-rule refuse-what-can't-prove)
My STEP-7 VET honest scope said "resonator log-scaling WITHIN a capacity envelope (~6-7 bases / R<=255255)" -- correct
that the envelope is tied to the recipe, but INSUFFICIENTLY EXPLICIT that this is a CURRENT-METHOD property, not a
fundamental bound. The test measured ONE implementation; it gives info about THAT implementation, not about what
fast residue decode can achieve in principle. I cannot PROVE a fundamental bound (only one method tested) -> by the
18th rule I must NOT claim one.

## What the GATE-F result DOES establish (valid)
The CURRENT METHOD -- the OLS-Gram resonator recipe (Gram-correction + soft phasor + random restarts +
reconstruction-accept), at hypervector dimension N=4096, at the FIXED pre-registered budget (RESON_RESTARTS=6,
RESON_ITERS=60), on the residue-FPE codebook (simplex-correlated per-base codewords) -- decodes accurately with
sub-linear-ish work up to ~6 coprime bases (R<=255255), degrades at 7 (R=4.85M, acc 0.96), and collapses at 8
(R=111M, acc 0.01). That is a valid, real measurement OF THIS METHOD'S envelope.

## What it does NOT establish (UNTESTED; must not be implied)
Whether fast residue decode is FUNDAMENTALLY bounded at ~6-7 bases. It is NOT. Untested levers that could move the wall:
- LARGER N: resonator/VSA capacity scales with the hypervector dimension; N=4096 is one point. Larger N likely
  extends the envelope. UNTESTED.
- LARGER FIXED BUDGET: a fixed-but-larger restart/iter budget could push the wall further at fixed (still
  R-independent) cost. UNTESTED. (Distinct from per-scale-growing budget, which would not be log-scaling.)
- DIFFERENT DECODER: exact Kymn OLS-projection (without the random-restart heuristic), Wasserstein/Sinkhorn, or a
  structured factorizer could have a different/larger capacity. UNTESTED (Director deferred Wasserstein as
  consumer-pull future work).
- DIFFERENT ENCODING: a non-simplex-correlated or differently-constructed codebook could decode further. UNTESTED.

## Required STEP-9 atom scope (amends the locked scope)
Phrase the bound as: "GATE-F establishes that THE CURRENT OLS-Gram resonator recipe, at N=4096 and the fixed
pre-registered budget, decodes the residue-FPE codebook within a capacity envelope of ~6-7 coprime bases; beyond it,
accuracy collapses and work grows super-0.5. This is the envelope OF THIS METHOD/CONFIGURATION -- NOT a fundamental
bound on fast residue decoding. Extension via larger N, larger fixed budget, or a different decoder/encoding is
UNTESTED (future work / consumer-pull)." Do NOT write "the fast-decoder size limit" or "residue-FPE is bounded at
6-7 bases" without the method/config qualifier.

## Generalizes to BOTH honest-bounds (P1 + P2)
Same discipline for P1: GATE-C1's break is "THIS continuous-residue ENCODING's product-kernel does not factor," NOT
"continuous-magnitude residue is fundamentally impossible." Both Phase-C TIER-3 honest-bounds are bounds on the
SPECIFIC methods tested, not proofs of fundamental impossibility. The honest claim is "these methods are bounded
here (these configs)" -- NOT "residue-FPE is fundamentally bounded." (P1 atom landed; flagging the interpretation;
the foundation-picture framing should carry this qualifier.)

## Disposition
- Verdict P2_HONEST_BOUNDED UNCHANGED (the method's envelope is real). Only the SCOPE PROSE is sharpened
  (method-contingent, not fundamental). kymn ADD (7 deps) + GATE-D/E findings UNCHANGED.
- Testbed STEP-9: encode the method-contingent scope above; do not imply a universal decode bound.
- WAITING ON Research (Director): STEP-8 ratify with this scope amendment folded in.

Tag: P2_honest_scope_amendment_USER_correction_capacity_bound_is_CURRENT_METHOD_contingent_NOT_fundamental_OLS_Gram_recipe_N_4096_fixed_budget_6_60_residue_FPE_codebook_envelope_6_7_bases_valid_measurement_of_THIS_method_untested_levers_larger_N_larger_budget_different_decoder_kymn_exact_OLS_wasserstein_sinkhorn_different_encoding_could_move_wall_18th_rule_refuse_what_cant_prove_cannot_claim_fundamental_bound_only_one_method_tested_STEP_9_atom_must_say_method_contingent_not_universal_generalizes_to_P1_C1_break_this_encoding_not_fundamental_both_honest_bounds_method_contingent_not_impossibility_verdict_unchanged_only_scope_prose_sharpened_fname_v2_adopted -- SKUNKWORKS (Auditor)
