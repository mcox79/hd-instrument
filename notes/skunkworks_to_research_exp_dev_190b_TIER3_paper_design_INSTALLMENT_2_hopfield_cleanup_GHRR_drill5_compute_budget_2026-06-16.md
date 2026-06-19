# SKUNKWORKS (Auditor) -> Research + Exp-Dev: 190b Phase C TIER-3 architecture PAPER-DESIGN -- INSTALLMENT 2 (PRIMITIVE 2 Hopfield-cleanup + PRIMITIVE 3 GHRR + Drill-5 fold + compute budget + cross-primitive integration + honest overall capability surface). PAPER-DESIGN ONLY. Headline honest call: primitives 1-2 (residue-FPE + Hopfield-cleanup) are WELL-GROUNDED (closed-form candidates + real literature + clear capability + connect to ARM-1/ARM-2); PRIMITIVE 3 GHRR is the FRONTIER/UNCERTAIN one (variant-undetermined + needed-capability open) -> per my G-gates it is RESEARCH-DRILL, NOT yet architecture. Recommend foundation-first (1->2), GHRR gated on a future variant+needed-capability+closed-form.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** 190b_TIER3_paper_design_INSTALLMENT_2_hopfield_cleanup_GHRR_drill5_compute_budget

## PRIMITIVE 2 -- MODERN HOPFIELD-AS-CLEANUP-HEAD (scoped; the kernel-aware cleanup)
```
  WHAT: modern Hopfield retrieval (Ramsauer 2020) = single-step softmax-weighted projection onto stored patterns:
     xi_new = X * softmax(beta * X^T * xi), X = codebook, xi = noisy query, beta = inverse-temperature.
     High beta -> retrieves nearest stored pattern with EXPONENTIAL storage capacity. This is CLEANUP with a
     beta-controlled, kernel-aware readout (vs naive max-cos nearest-neighbor).
  WHY (role): the KERNEL-AWARE cleanup that resolves Primitive-1's continuous-FPE near-neighbor confusion (the
     G5(b) uncertainty + the ARM-1 mode-ii FPE-phase-kernel concern + Drill 3/4's identified mitigation). DIRECTLY
     connects to the ARM-1 dual-head control I designed (modern-Hopfield as the alternate cleanup head) -- deferred
     for the integer arm (clean), it IS Primitive 2 for the continuous TIER-3 regime. Coherent, not new-from-nowhere.
  G1 CLOSED-FORM: beta closed-form per Ramsauer Theorem-4 (beta = f(N, |patterns|, Delta_min separation); the
     one-step retrieval-error bound + exponential capacity are closed-form). NO learned beta (11th rule). CANDIDATE.
  G2 CHTV-1: Ramsauer et al. 2020 "Hopfield Networks is All You Need" (Theorem-3 capacity, Theorem-4 closed-form
     beta). Citable; atom claim bounded to the proved bounds. CANDIDATE.
  G3 L6-PROOF: the retrieval-error bound + exp-capacity are PROVABLE theorems; beta derivable from Delta_min.
     Axiom-terminating soundness core. CANDIDATE.
  G4 SUBSTRATE-INTERNAL: softmax-weighted matmul over the codebook, beta closed-form -> substrate ops, no learning.
     CLEAN. (cap_pres: it's an ADDITIVE alternate cleanup head; naive-max-cos stays default; same as my ARM-1 spec.)
  G5 CAPABILITY-SURFACE + UNCERTAINTY (honest):
     OPENS: robust cleanup over continuous-FPE (resolves the near-neighbor confusion Primitive 1 alone cannot);
        exponential capacity (more stored patterns than naive cleanup).
     UNCERTAIN: (a) the closed-form beta assumes a separation Delta_min; for continuous-FPE codewords (arbitrarily
        close on the V^x continuum) Delta_min -> 0 as resolution increases -> the capacity/error bound DEGRADES at
        fine resolution. So Primitive 2 MITIGATES but does NOT eliminate the continuous-resolution limit -> there
        is a RESOLUTION/CAPACITY ENVELOPE (honest: not unbounded). (b) does Hopfield-cleanup over a RESIDUE-FPE
        product-kernel substrate (Primitive 1) retain the closed-form guarantee? -> verify (Drill 5).
     -> HONEST: Primitive 2 is the right continuous-cleanup primitive AND it has a principled envelope; the
        envelope (resolution vs capacity) must be CHARACTERIZED, not assumed unbounded.
```

## PRIMITIVE 3 -- GHRR (Generalized Holographic Reduced Representation) -- FRONTIER / NOT-YET-ARCHITECTURE
```
  WHAT: GHRR generalizes HRR (circular convolution) / FHRR (elementwise unit-phasor) binding to BLOCK-structured
     or MATRIX-VALUED binding (block-local circular convolution; matrix/quaternion/Clifford-algebra binding) ->
     richer binding semantics (e.g. non-commutative/order-sensitive binding without explicit permutation;
     higher-arity role structure).
  WHY (intended role): tier-3 binding FHRR cannot express; operates on the residue-FPE + Hopfield-cleanup foundation.
  G1 CLOSED-FORM: binding/unbinding fidelity + crosstalk/capacity have closed-form bounds FOR A CHOSEN VARIANT
     (generalizing FHRR SNR). CANDIDATE -- but VARIANT-DEPENDENT.
  G2 CHTV-1: generalized-HRR / matrix-VSA / Clifford-VSA literature. Citable, BUT multiple competing variants ->
     the citable closed-form depends on WHICH variant.
  G3 L6-PROOF: provable for a chosen variant. CANDIDATE (variant-dependent).
  G4 SUBSTRATE-INTERNAL: matrix/block binding = substrate ops, no learning. CLEAN.
  G5 CAPABILITY-SURFACE + UNCERTAINTY (the BIGGEST uncertainty of the three):
     INTENDED: richer binding (non-commutative / higher-arity / matrix-valued roles) FHRR can't express.
     OPEN (gates NOT yet met): (i) WHICH variant? -- G1/G3 closed-form depends on it, undetermined. (ii) does the
        richer binding OPEN a NEEDED substrate capability, or is it a generalization with NO CONSUMER (the
        FLOATING-FACT risk at the ARCHITECTURE level -- same 76th-instance discipline: don't build infrastructure
        with no consumer)? Currently NO identified tier-3 capability REQUIRES GHRR over FHRR.
     -> RULING (per my G-gates): GHRR is NOT yet TIER-3-architecture-ready. It meets G4 + has G1-G3 candidates
        IF a variant is fixed, but it FAILS G5's needed-capability test (no consumer identified). -> Scope GHRR as
        a RESEARCH-DRILL (variant survey + identify a capability that genuinely REQUIRES it) PROMOTABLE to
        architecture only once G5-needed-capability + a fixed variant + its closed-form are established. Do NOT
        commit build effort to GHRR ahead of that (refuse-to-invent-infrastructure, 21st rule, at the arch layer).
```

## DRILL 5 -- continuous-FPE (190d) -- FOLDED as the de-risk of Primitives 1+2's continuous-regime uncertainties
```
  Drill 5 = continuous-valued FPE (Frady-Sommer 2021 + Kymn 2024). It is NOT a separate primitive; it is the
     SCOPING/VERIFICATION of: Primitive-1 G5(a) the residue PRODUCT-KERNEL closed form at scale + G5(b) continuous
     capacity; and Primitive-2 G5(a) the RESOLUTION/CAPACITY ENVELOPE for Hopfield-cleanup over continuous-FPE.
  Scope: derive/verify the continuous-FPE similarity kernel + the resolution-vs-capacity tradeoff + whether the
     residue product-kernel holds (base independence). Output: the continuous-regime envelope that bounds
     Primitives 1+2's honest capability claims. -> Drill 5 GATES the continuous-magnitude capability surface;
     until it lands, Primitives 1+2's continuous claims are PREVIEW, not load-bearing.
```

## COMPUTE BUDGET (for any FUTURE build; paper-design only)
```
  Primitive 1 residue-FPE: LIGHT (FFT-based encoding; cheap). Build est ~days.
  Primitive 2 Hopfield-cleanup: MEDIUM build + HEAVY verification (the resolution/capacity envelope across a
     (resolution, |M|, beta) grid = remote GPU, like the ARM-1 capacity-envelope work). Build+verify ~days-week.
  Drill 5: LIGHT-MEDIUM (kernel derivation + envelope verification; some remote for the grid).
  Primitive 3 GHRR: DEFERRED (variant survey first; budget undetermined until G5-needed-capability established).
  -> Phase C foundation (1 + 2 + Drill 5) is a bounded, mostly-light + one-heavy-verification arc; GHRR is held.
```

## CROSS-PRIMITIVE INTEGRATION + HONEST OVERALL CAPABILITY SURFACE
```
  STACK: residue-FPE (continuous-magnitude encoding) -> Hopfield-cleanup (robust continuous readout within the
     resolution/capacity envelope) -> [GHRR held]. Together 1+2 OPEN continuous-magnitude reasoning the current
     binary/integer substrate cannot: graded "how much", ordering, interpolation, continuous attributes -- WITHIN
     the Drill-5-characterized envelope.
  HONEST OVERALL: Primitives 1-2 are SOLID TIER-3 candidates (closed-form gates + real literature + clear NEEDED
     capability [continuous magnitude] + coherent extension of ARM-1/ARM-2's FPE work). Primitive 3 GHRR is
     SPECULATIVE (no identified needed-capability + variant-undetermined) -> research-drill, not architecture.
  RECOMMENDATION: Phase C TIER-3 = build FOUNDATION-FIRST (residue-FPE + Hopfield-cleanup, de-risked by Drill 5);
     hold GHRR as a research-drill until it earns the G5 needed-capability + variant + closed-form. This keeps
     TIER-3 honest (2 well-grounded primitives + 1 honestly-deferred) rather than committing to a 3-primitive
     stack where the 3rd has no consumer.
```

## Net
TIER-3 paper-design COMPLETE (installments 1+2). Architecture: residue-FPE -> Hopfield-cleanup (foundation, SOLID,
closed-form candidates, de-risked by Drill 5) + GHRR (FRONTIER, research-drill not architecture until G5-needed-
capability + variant + closed-form). Per-primitive G1-G5 gates applied; honest uncertainties (continuous-resolution
envelope; residue product-kernel; GHRR consumer) flagged not hidden. PAPER-DESIGN ONLY; no atoms; no execution.
This is the Phase C architectural scoping the Director dispatched (190b) + Drill 5 folded (190d). Standing for: 190a
+ 190c remote RESULTS VET (both executing); 190f atom type-VET; 190e hookup VET. Director/USER: the foundation-first
+ GHRR-held recommendation is a Phase-C-scope call (yours).

Tag: 190b_TIER3_INSTALLMENT_2_primitive2_hopfield_cleanup_ramsauer_thm4_closed_form_beta_kernel_aware_resolves_continuous_FPE_near_neighbor_connects_ARM1_dual_head_G5_resolution_capacity_envelope_delta_min_to_zero_at_fine_resolution_NOT_unbounded_primitive3_GHRR_FRONTIER_variant_undetermined_NO_consumer_floating_fact_at_arch_layer_76th_discipline_NOT_yet_architecture_research_drill_promotable_drill5_folded_derisk_continuous_regime_product_kernel_resolution_tradeoff_compute_budget_foundation_light_plus_one_heavy_verification_GHRR_deferred_recommendation_foundation_first_GHRR_held_honest_2_solid_plus_1_deferred -- SKUNKWORKS (Auditor)
