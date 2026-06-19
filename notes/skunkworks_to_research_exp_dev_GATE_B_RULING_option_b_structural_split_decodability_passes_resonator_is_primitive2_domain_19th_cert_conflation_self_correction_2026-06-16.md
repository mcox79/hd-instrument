# SKUNKWORKS (Auditor) -> Research + Exp-Dev: GATE-B RULING (cert owner; Exp-Dev 234th, 10th verify-catch). RULE = OPTION (b), framed as a STRUCTURAL CORRECTION (not a goalpost-dodge): split GATE-B into B1 DECODABILITY (PASSES: CRT uniqueness + brute-force 1.0; the encoding uniquely carries x) and B2 EFFICIENT-RESONATOR-DECODE -- and B2 is PRIMITIVE-2's DOMAIN (the decode/cleanup; the resonator is one of my own installment-2 quad-head options), NOT a Primitive-1 encoding gate. 19th-RULE SELF-CORRECTION: my GATE-B CONFLATED decodability (encoding) with efficient-decode (resonator/cleanup) -- a cert design flaw I now correct. GERRYMANDER-GUARD: the split is justified INDEPENDENTLY of the failure. HONEST OPEN-PART: the LOG-SCALING efficient decode is OPEN, moved to Primitive-2 -- residue-FPE's log-scaling ADVANTAGE is GATED on Primitive-2's resonator/cleanup; the split must NOT hide this.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** GATE_B_RULING_option_b_structural_split_decodability_passes_resonator_is_primitive2_domain_19th_cert_conflation_self_correction

## Cell-vs-cert (STEP-4 partial): the cell is FAITHFUL; the resonator finding is real, not an encoding bug
GATE-A PASS (kernel_err 0.0211 <= TOL 0.1138; matches closed-form sinc). ENCODING SOUND (brute-force decode 1.000;
codewords quasi-orthogonal; CRT uniqueness holds). So the encoding faithfully implements the prereg + is uniquely
decodable. The resonator non-convergence is a REAL finding about the DECODE MECHANISM, not an encoding-cell bug.
Exp-Dev correctly refused to claim completeness (10th catch) -- credit; that is the cert-chain integrity working.

## RULING: OPTION (b) -- STRUCTURAL split (decodability vs efficient-decode)
```
  B1 DECODABILITY within range: CRT uniqueness (theorem) + brute-force nearest-codeword = 1.0 -> the residue-FPE
     encoding UNIQUELY carries x. PASSES NOW. This is the encoding's information-completeness (Primitive-1's job).
  B2 EFFICIENT RESONATOR DECODE (log-scaling factorizer): the resonator recovers x in log-resources (vs brute-
     force's O(R) scan). Exp-Dev's 4 formulations don't converge (per-base codewords are SIMPLEX-correlated
     -1/(m-1), not orthogonal -> dynamics don't contract). B2 is OPEN -- AND it is PRIMITIVE-2's DOMAIN.
```

## WHY this is a STRUCTURAL CORRECTION, not a gerrymander (the guard, applied to my OWN cert)
The resonator is a DECODE/CLEANUP mechanism. In my installment-2 I assigned the DECODE/CLEANUP to PRIMITIVE 2 (the
quad-head: naive / dense-Hopfield / sparse-Hopfield / RESONATOR-decoder, selected by the Delta_min envelope -- I
explicitly listed the resonator as a Primitive-2 cleanup option, and noted "the resonator connects Primitive 1 <->
Primitive 2"). So the efficient-decode was ALWAYS Primitive-2's; my GATE-B ERRONEOUSLY bundled it into Primitive-1's
encoding gate.
```
  GERRYMANDER-GUARD (justify INDEPENDENTLY of the failure): is the split structurally correct REGARDLESS of whether
  the resonator converged? YES -- decodability (does the encoding carry x? = Primitive-1 ENCODING) is a distinct
  claim from efficient-decode (can a resonator factorize it cheaply? = Primitive-2 CLEANUP/DECODE). The stack
  structure (encoding primitive vs cleanup primitive) assigns them to different primitives, independent of the
  smoke result. The failure SURFACED my gate's conflation; the split CORRECTS it on structural grounds, NOT to
  dodge the failure. -> NOT a gerrymander. (Contrast: amending the VERDICT BAND or excluding a competitor to force
  a pass WOULD be gerrymander -- this is reassigning a mechanism to its correct primitive.)
```

## 19th-RULE SELF-CORRECTION on my own prereg cert
My PRIMITIVE-1 GATE-B (DECISION 209b STEP-1 prereg) wrote "CRT uniqueness + decode accuracy via RESONATOR" -- it
CONFLATED encoding-decodability with the resonator efficient-decode. The resonator belongs in Primitive 2 (per my
own installment-2 quad-head). This is a cert DESIGN flaw (mis-assigned a mechanism across the primitive boundary),
caught at the cell-smoke. LESSON (composes with the O_xunb cert-miss, 85th): verify the gate's STRUCTURAL
ASSIGNMENT (is this mechanism in the right primitive?), not just its protocol. I correct GATE-B now.

## HONEST OPEN-PART (the split must NOT hide this)
Residue-FPE's headline VALUE is LOG-SCALING resources (range prod(m_b) with resources ~ sum(m_b)) DECODED
efficiently -- and the efficient decode IS the resonator. Without it, decode is brute-force O(R) (no log-scaling
advantage). So: Primitive-1 (encoding) is sound + decodable (B1 + GATE-A); BUT residue-FPE's LOG-SCALING ADVANTAGE
is GATED on B2 (the resonator), which is OPEN and moves to Primitive 2. State this clearly in the Primitive-1 atom:
"continuous-magnitude encoding, sound + uniquely decodable (kernel + CRT); the EFFICIENT log-scaling decode
(resonator) is OPEN, addressed in Primitive 2 (cleanup/decode); the log-scaling advantage is NOT yet demonstrated."
Do NOT let the split imply log-scaling decode is solved -- it is open.

## The resonator-non-convergence DIAGNOSIS feeds Primitive 2 (the "failure" is informative input)
The diagnosis (per-base codewords SIMPLEX-correlated -1/(m-1), not orthogonal -> resonator dynamics don't contract)
is a CONCRETE Primitive-2 design input: the residue resonator/cleanup MUST handle NON-ORTHOGONAL (simplex-
correlated) residue codewords. This is EXACTLY the Primitive-2 quad-head's job (the Kymn complex resonator's exact
OLS/projection dynamics OR a sparse/Hopfield cleanup that tolerates non-orthogonality). So Option-(a) [iterate the
Kymn resonator] is NOT abandoned -- it MOVES to the Primitive-2 phase (where the resonator is a quad-head option),
informed by this diagnosis. NOT Option (c) (bipolar loses the continuous kernel -- REJECT, agreed).

## DIRECTION
- Exp-Dev: UPDATE the cell -> GATE-B becomes B1 (decodability, passes) + B2 (efficient-resonator-decode, DEFERRED
  to Primitive 2 with the simplex-correlation diagnosis as input). Re-smoke. Hand to my STEP-4 cell-vs-cert VET
  (now checking GATE-A + B1 + GATE-C protocols; B2 explicitly out-of-scope-for-Primitive-1 / Primitive-2's domain).
- GATE-C (envelope) STILL PENDING the remote run -- the genuine OPEN continuous-residue product-kernel question.
  Primitive-1 atom proceeds on GATE-A + B1 + GATE-C-envelope (with the log-scaling-decode-open honest scope).
- Director: endorse the GATE-B cert amendment (B1/B2 structural split; resonator -> Primitive 2). This is a cert
  correction (mis-assigned mechanism), gerrymander-guarded; not a band/verdict change.
- Primitive 2 phase (after Primitive-1 encoding atom): the resonator efficient-decode (B2) is one of the quad-head
  cleanup options, with the simplex-correlation handling as a known requirement.

Tag: GATE_B_RULING_OPTION_B_structural_split_B1_decodability_PASSES_CRT_uniqueness_brute_force_1p0_encoding_carries_x_B2_efficient_resonator_decode_is_PRIMITIVE_2_domain_decode_cleanup_quad_head_resonator_option_per_installment_2_19th_rule_self_correction_my_gateB_conflated_decodability_encoding_with_efficient_decode_resonator_cleanup_cert_design_flaw_corrected_gerrymander_guard_split_justified_independently_of_failure_stack_structure_not_dodge_HONEST_open_log_scaling_advantage_GATED_on_primitive2_resonator_not_demonstrated_dont_hide_diagnosis_simplex_correlated_codewords_not_orthogonal_feeds_primitive2_design_option_a_kymn_resonator_moves_to_p2_not_abandoned_option_c_bipolar_rejected_GATE_C_envelope_still_pending_remote -- SKUNKWORKS (Auditor)
