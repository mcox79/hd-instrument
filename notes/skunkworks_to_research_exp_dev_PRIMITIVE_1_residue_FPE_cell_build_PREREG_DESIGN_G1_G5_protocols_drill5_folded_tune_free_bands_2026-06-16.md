# SKUNKWORKS (Auditor) -> Research + Exp-Dev: PRIMITIVE 1 (residue-FPE) cell-build PREREG DESIGN (DECISION 209b STEP 1; cert-chain design contract). Instantiates installment-1 + R2 literature base; Drill-5 folded into GATE-C. PRE-REGISTERED + TUNE-FREE; honest-negative path per gate. KEY: GATE-C (G5) is the genuinely OPEN question (the COMBINED continuous-residue product-kernel + envelope) -- and per my own O_xunb cert-miss lesson, GATE-C VERIFIES per-base independence rather than ASSUMING it. Primitive-1's load-bearing claim is BOUNDED by the GATE-C-characterized envelope (not assumed unbounded). On Director ratify -> Exp-Dev authors cell (STEP 3) -> I cell-vs-cert VET (STEP 4).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** PRIMITIVE_1_residue_FPE_cell_build_PREREG_DESIGN_G1_G5_protocols_drill5_folded_tune_free_bands

## CELL PIPELINE (what Exp-Dev authors per this prereg; STEP 3)
```
  ENCODE: value x -> residue-FPE vector.
     - base FPE: V^x = elementwise complex exponent exp(i * x * theta), theta = base phases ~ chosen distribution
       (uniform OR band-limited; the distribution SHAPES the kernel per Frady-Sommer VFA). Unit-magnitude (FHRR).
     - RESIDUE LAYERING: r coprime bases {m_1..m_r}; per-base channel encodes (x mod m_b) as an FPE phase;
       represents x over range prod(m_b) with resources ~ sum(m_b) (log-scaling per Kymn residue-HDC).
  DECODE: residue-tuple -> x via CRT recombination + resonator/cleanup factorization (Kymn resonator).
  Substrate-internal: complex-exponent elementwise + r-parallel-channels + CRT recombine = FHRR ops; NO learned
     codebook (11th rule). queue-compatible (--self-test/--smoke/full); torch.cuda batched (USER GPU directive).
```

## GATE-A (G1 closed-form kernel) -- LIGHT; laptop-OK
```
  PROTOCOL: measure sim(V^x, V^y) = (1/N) Re<V^x, V^y> across a grid of d=(x-y); compare to the CLOSED-FORM
     base-phase characteristic function E_theta[cos(d*theta)] (the predicted kernel).
  PASS (tune-free): max_d | measured_sim(d) - closed_form_kernel(d) | <= TOL (TOL pre-registered, e.g. 0.02 +
     3*sqrt(1/N) finite-N band). i.e. the measured kernel MATCHES the closed-form within the finite-N fluctuation.
  HONEST-NEGATIVE: if measured diverges from closed-form beyond TOL -> the base-phase model is wrong / the kernel
     is not as derived -> Primitive 1 G1 NOT met -> STOP (re-derive; do not build on an unverified kernel).
```

## GATE-B (G3 CRT uniqueness + decode) -- LIGHT; laptop-OK
```
  PROTOCOL: (i) CRT uniqueness: confirm distinct integers x in [0, prod(m_b)) map to distinct residue-tuples
     (CRT theorem; assert in self-test). (ii) decode accuracy: encode x -> residue-FPE -> CRT+resonator decode ->
     recover x; measure recovery accuracy over the representable range, multi-seed (n>=3).
  PASS (tune-free): CRT uniqueness holds (theorem) AND decode_acc = 1.0 within the representable INTEGER range (or
     >= a pre-registered bar, e.g. 0.99, accounting for resonator convergence). 
  HONEST-NEGATIVE: decode_acc < bar within range -> the residue decode (resonator) doesn't converge -> Primitive 1
     integer-residue decode bounded -> honest scope (range-limited).
```

## GATE-C (G5 -- the OPEN question; Drill-5 folded) -- MEDIUM-HEAVY; REMOTE desktop
This is the genuinely open part (R2: literature does integer-residue + continuous-FPE SEPARATELY; the COMBINED
continuous-residue product-kernel is unestablished). Per my O_xunb cert-miss lesson: VERIFY independence, don't assume.
```
  TEST C1 -- PRODUCT-KERNEL (base independence for CONTINUOUS x):
     The residue-FPE combined kernel SHOULD factor as the PRODUCT of per-base kernels IFF the bases are independent.
     PROTOCOL: measure the COMBINED kernel sim(residueFPE(x), residueFPE(y)) across continuous d=(x-y); compare to
     the PRODUCT of per-base closed-form kernels prod_b E_theta_b[cos(d*theta_b)].
     PASS (product-kernel holds): max_d | combined_measured(d) - product_of_per_base(d) | <= TOL.
     HONEST-NEGATIVE (independence breaks): combined diverges from the product -> the per-base channels are NOT
        independent for continuous x -> Primitive 1's continuous-residue use is BOUNDED (the clean product-kernel
        does not hold); integer-residue (GATE-B) + single-channel continuous-FPE (GATE-A) uses STAY valid; honest
        scope filed. >>> THIS IS THE VERIFY-NOT-ASSUME GATE (the O_xunb lesson: do not assume the enumerated
        structure's algebraic property; MEASURE it). <<<
  TEST C2 -- RESOLUTION/CAPACITY ENVELOPE:
     PROTOCOL: characterize min-distinguishable Delta_x (resolution) vs range/capacity across the FPE band-limit
     (base-phase bandwidth) + |codebook|, as a FUNCTION (sweep; report the envelope, not a single point).
     RESULT (not pass/fail): the envelope IS the deliverable -- it BOUNDS Primitive 1's continuous-magnitude claim.
     HONEST: if the continuous envelope is NARROW at fine resolution -> fine-resolution continuous magnitude NEEDS
        Primitive 2 (Hopfield/resonator cleanup) -> Primitive 1 alone is coarse-resolution-bounded (per installment-1
        G5(b) + R2). The envelope hands the resolution budget to Primitive 2's design.
```

## HONEST SCOPE (LOCKED in the prereg)
```
  GROUNDED (R2): integer-residue (Kymn, GATE-B) + single-channel continuous-FPE/SSP (Frady/Komer-Eliasmith, GATE-A)
     -- established separately.
  OPEN (GATE-C): the COMBINED continuous-residue PRODUCT-KERNEL + the continuous resolution/capacity envelope.
  PRIMITIVE-1 LOAD-BEARING CLAIM = continuous-magnitude encoding WITHIN the GATE-C-characterized envelope; NOT
     assumed unbounded. A NARROW envelope or a broken product-kernel = HONEST BOUNDED SCOPE (still a valid atom for
     the regime where it holds), NOT a manufactured general claim.
```

## PRE-REGISTERED VERDICT (tune-free; honest-negative per gate)
```
  PRIMITIVE-1 ATOM earns load-bearing IFF: GATE-A PASS (kernel matches closed-form) AND GATE-B PASS (CRT decode
     within range) AND GATE-C C1 characterized (product-kernel holds OR honest-bounded) AND C2 envelope reported.
  The atom's PROSE is scoped to the GATE-C envelope (the regime where the product-kernel holds + the resolution it
     supports). If C1 honest-negative (independence breaks) -> file Primitive-1 as integer-residue + single-channel-
     continuous (bounded), NOT combined-continuous-residue (honest). If GATE-A or GATE-B fail -> STOP (re-derive).
  metric_type: AGGREGATE (kernel-match error + decode RMSE) + the envelope as a FUNCTION (not a scalar).
```

## CERT-CHAIN + compute
- Cert chain (84th candidate): THIS prereg = design contract (STEP 1). Director ratify (STEP 2). Exp-Dev authors
  cell faithfully (STEP 3). I cell-vs-cert VET (STEP 4) -- verify the cell implements GATE-A/B/C protocols + the
  tune-free bands + the honest scope (the O_xunb lesson: I will verify the cell's gate IMPLEMENTATIONS, incl that
  GATE-C C1 genuinely measures combined-vs-product, not assumes it). Director ratify cell (STEP 5). Orchestrator
  dispatch (STEP 6: G1/G2/G3 light laptop; GATE-C remote). I results VET per these locked bands (STEP 7).
- Compute: GATE-A + GATE-B LIGHT (laptop). GATE-C MEDIUM-HEAVY (remote desktop: product-kernel sweep + envelope
  characterization across (bases, bandwidth, |codebook|, resolution) grid) per USER thermal policy.

## Status / queue
PRIMITIVE 1 prereg DESIGN DELIVERED (this; PRIORITY 1). Ready for Director ratify -> Exp-Dev cell author -> my
cell-vs-cert VET. Drill 5 folded into GATE-C (no separate prereg). My secondary queue: 190e hookup VET (DECISION
209c; 11th-firewall + 22nd-provenance + atomic-rollback) NEXT; 190f + 190c FINDING type-VETs on Testbed landings;
ARM-3 Option C scoping (background low-priority). Exp-Dev's Primitive-2 cell-gate sketch (parallel) informs the
next phase. PAPER-DESIGN ONLY; no atoms; no execution until ratify + cell + cell-vs-cert VET.

Tag: PRIMITIVE_1_residue_FPE_cell_build_PREREG_encode_complex_exponent_residue_layering_coprime_bases_CRT_decode_resonator_GATE_A_G1_closed_form_kernel_measured_vs_char_function_TOL_GATE_B_G3_CRT_uniqueness_decode_acc_GATE_C_G5_OPEN_product_kernel_base_independence_VERIFY_NOT_ASSUME_O_xunb_lesson_resolution_capacity_envelope_as_function_honest_scope_combined_continuous_residue_is_open_load_bearing_WITHIN_envelope_not_unbounded_tune_free_bands_honest_negative_per_gate_cert_chain_compute_light_G1_G2_G3_heavy_GATE_C_remote -- SKUNKWORKS (Auditor)
