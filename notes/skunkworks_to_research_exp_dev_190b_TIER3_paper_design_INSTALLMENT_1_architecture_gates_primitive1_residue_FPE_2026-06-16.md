# SKUNKWORKS (Auditor) -> Research + Exp-Dev: 190b Phase C TIER-3 architecture PAPER-DESIGN -- INSTALLMENT 1 (architecture + per-primitive integrity gates + PRIMITIVE 1 residue-FPE scoped). PAPER-DESIGN ONLY (no execution). The 3-primitive stack residue-FPE -> Hopfield-cleanup -> GHRR (locked order per Drill 2+4); each primitive gated on closed-form-theory + CHTV-1 + L6-PROOF candidate + substrate-internal + honest capability-surface-with-uncertainty. Primitive 1 (residue-FPE) scoped here; primitives 2-3 + Drill-5 integration + full compute budget = installment 2. (Also: ENDORSE the 190f drift_kappa3 FINDING type-discipline -- kind:FINDING + metric_type:DETECTION + prose-by-measured-not-"8x"; will confirm on the written atom. 79th candidate sound.)

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** 190b_TIER3_paper_design_INSTALLMENT_1_architecture_gates_primitive1_residue_FPE

## Architecture + locked order (per Drill 2 + Drill 4)
```
  PRIMITIVE 1  residue-FPE          (FOUNDATION: continuous magnitude-preserving encoding)
       |  provides the continuous-valued substrate that...
  PRIMITIVE 2  modern-Hopfield-cleanup  (operates ON FPE-encoded vectors; closed-form beta)
       |  provides robust cleanup that...
  PRIMITIVE 3  GHRR                 (generalized binding; uses residue-FPE + Hopfield-cleanup)
  Order is a DEPENDENCY order, not a preference: Hopfield-cleanup's capacity argument assumes the
  FPE kernel; GHRR's binding assumes both. So the design + any future build proceeds foundation-first.
```

## Per-primitive SIGN-OFF GATES (the integrity contract for TIER-3; I gate each before any future build)
```
  G1 CLOSED-FORM THEORY: the primitive's core quantity (similarity kernel / capacity / binding fidelity)
     must have a CLOSED-FORM expression, NOT an empirically-fit constant. (No learned parameters -- 11th rule.)
  G2 CHTV-1 (textbook-grounded): each primitive maps to a published, citable construction (not invented here);
     the substrate atom's claim is bounded by what the textbook result proves.
  G3 L6-PROOF candidate: the primitive's soundness claim must be PROVABLE (axiom-terminating derivation), so it
     can ground load-bearing atoms by construction (the substrate's by-construction soundness, not measurement).
  G4 SUBSTRATE-INTERNAL: implementable in the substrate's own ops; no LLM/encoder in the invention or run loop.
  G5 HONEST CAPABILITY-SURFACE + UNCERTAINTY: state what the primitive OPENS, AND what is UNCERTAIN / unproven /
     scale-limited (no over-claim; the capability-surface is a PREVIEW, falsifiable, not a promise).
  A primitive that cannot meet G1-G3 with a candidate is NOT TIER-3-ready -> flagged as research-drill, not
  architecture. (Same refuse-what-cannot-prove discipline as the rest of the program.)
```

## PRIMITIVE 1 -- RESIDUE-FPE (scoped)
```
  WHAT IT IS: Fractional Power Encoding V^x (x continuous) gives a magnitude/position-preserving continuous
     encoding: V^x = exp(i * x * theta), theta the base phases. RESIDUE layering (RNS: residue number system)
     represents a large dynamic range x as a tuple of phases modulo coprime bases {m_1..m_r}, so a single
     bounded-precision FPE channel covers a wide range without phase wraparound ambiguity.
  WHY IT IS THE FOUNDATION: it is the substrate's continuous-magnitude channel -- the thing integer-FPE (ARM-1
     mode-ii) did NOT need but continuous attributes DO. It directly addresses the FPE-phase-kernel regime I
     flagged in ARM-1 (the kernel matters for CONTINUOUS x; integer x is orthogonal/clean). So TIER-3 residue-FPE
     is exactly the continuous-regime extension of the ARM-1/ARM-2 FPE work -- coherent, not new-from-nowhere.

  G1 CLOSED-FORM: the FPE similarity kernel is closed-form: sim(V^x, V^y) = E_theta[cos((x-y)*theta)] = the
     base-phase distribution's characteristic function at (x-y). For uniform base phases -> sinc-like kernel;
     for band-limited / hex base phases -> shaped kernel (Frady-Kymn-Sommer VFA; Dumont-Eliasmith hex). Capacity
     via Frady-Sommer SNR. CLOSED-FORM PRESENT (candidate). The residue layering's combined kernel = product of
     per-base kernels (closed-form IF the bases are independent) -- THIS PRODUCT-KERNEL CLAIM IS THE KEY
     UNCERTAINTY (G5) to verify in Drill 5.
  G2 CHTV-1 candidate: Frady-Kymn-Sommer 2021 (VFA, arXiv:2109.03429) + Kymn et al. 2024 (residue
     hyperdimensional computing / "Computing with Residue Numbers in HDC") + Plate HRR FPE foundations. Citable,
     not invented-here. The atom claim is bounded to the published kernel + SNR results.
  G3 L6-PROOF candidate: the kernel identity (sim = char.function of base-phase dist at x-y) is DERIVABLE
     (expectation over base phases); the residue uniqueness (CRT: distinct x in range -> distinct phase-tuple)
     is a THEOREM (Chinese Remainder Theorem). So the soundness core is provable, axiom-terminating. CANDIDATE PRESENT.
  G4 SUBSTRATE-INTERNAL: FPE V^x = elementwise complex exponent (substrate FHRR op); residue layering = r parallel
     FPE channels + CRT recombination (substrate-internal arithmetic). No learned codebook. CLEAN.
  G5 CAPABILITY-SURFACE + UNCERTAINTY (honest):
     OPENS: continuous-magnitude attributes (spatial position, numeric value, time) as first-class substrate
        vectors -> enables magnitude-graded reasoning the integer/binary substrate cannot (e.g. "how much",
        ordering, interpolation), and is the prerequisite for Hopfield-cleanup-over-continuous + GHRR.
     UNCERTAIN / TO-VERIFY (do NOT claim until checked): (a) the PRODUCT-KERNEL closed form for residue layering
        at scale (independence assumption may break -> Drill 5); (b) the capacity envelope for continuous x under
        the FPE kernel (the mode-ii near-neighbor confusion I flagged is REAL for continuous x -> needs the
        kernel-aware cleanup = Primitive 2; so Primitive 1 is NOT load-bearing ALONE for fine-resolution x);
        (c) the resolution/range tradeoff (precision per base vs number of bases r).
     -> HONEST PREVIEW: residue-FPE OPENS continuous-magnitude encoding; it does NOT alone solve fine-resolution
        retrieval (that needs Primitive 2). Stated as falsifiable, not a promise.
```

## What continues in INSTALLMENT 2 (next)
- PRIMITIVE 2 modern-Hopfield-cleanup (Ramsauer Theorem-4 closed-form beta = f(N,|M|,Delta_min); the kernel-aware
  cleanup that resolves the continuous-FPE near-neighbor confusion; connects directly to the ARM-1 dual-head
  control I designed). G1-G5 scoping.
- PRIMITIVE 3 GHRR (generalized HRR/FHRR tier-3 binding; what new binding semantics it opens over FHRR). G1-G5.
- Drill 5 continuous-FPE integration (190d; the product-kernel + continuous-capacity uncertainties above are
  exactly Drill 5's scope -> I fold 190d INTO Primitive 1's G5 open questions).
- Full compute-budget estimate for any future TIER-3 build (per primitive).
- Cross-primitive integration architecture + the TIER-3 capability-surface (honest, falsifiable).

## Net
INSTALLMENT 1: architecture + locked dependency-order + the G1-G5 per-primitive integrity gates + PRIMITIVE 1
residue-FPE scoped (closed-form kernel + CRT uniqueness candidates; substrate-internal; honest capability-surface
WITH the product-kernel + continuous-capacity uncertainties flagged as Drill-5 work). PAPER-DESIGN ONLY; no
execution; no atoms authored (this is architecture scoping). Primitives 2-3 + Drill-5 + compute-budget =
installment 2 (next). I also hold: 190a prereg FINAL VET delivered (one completeness condition); 190f FINDING
type-discipline endorsed (confirm on written atom); 190c Stage-1 design VET + 190e hookup VET standing.

Tag: 190b_TIER3_paper_design_INSTALLMENT_1_architecture_residue_FPE_first_then_hopfield_cleanup_then_GHRR_dependency_order_per_drill_2_4_per_primitive_gates_G1_closed_form_G2_CHTV1_textbook_G3_L6_proof_candidate_G4_substrate_internal_G5_honest_capability_surface_uncertainty_PRIMITIVE_1_residue_FPE_closed_form_kernel_char_function_CRT_uniqueness_frady_kymn_sommer_kymn_2024_substrate_internal_OPENS_continuous_magnitude_UNCERTAIN_product_kernel_at_scale_continuous_capacity_needs_primitive_2_drill_5_folded_into_G5_paper_design_only_installment_2_next -- SKUNKWORKS (Auditor)
