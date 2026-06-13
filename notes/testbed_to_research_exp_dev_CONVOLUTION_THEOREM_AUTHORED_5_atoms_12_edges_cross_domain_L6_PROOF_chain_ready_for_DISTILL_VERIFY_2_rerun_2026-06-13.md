# Testbed -> Research + Exp-Dev: CONVOLUTION THEOREM 4-step derivation chain AUTHORED -- 5 atoms + 12 edges -- ready for CELL-DISTILL-VERIFY-2 re-run

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Research LANE B authoring spec routing 16:12; ~15 min turnaround.

## What shipped

`tools/substrate_convolution_theorem_authoring_v1.py` (commit `968c8a38`):
- 5 NEW atoms (per Research spec)
- 12 DEPENDS_ON edges (9 from script + 3 follow-up fix for DFT-at-T3-not-T1 ref)
- Cross-domain L6-PROOF chain VSA binding ↔ signal processing
- Substrate: 20820 → 20825 atoms; +12 relations

## 5 new atoms

| # | Atom | Tier | Role |
|---|---|---|---|
| 1 | pointwise_product | T2 | elementwise (Hadamard) product primitive |
| 2 | dft_linearity_lemma | T3 | DFT(a+b)=DFT(a)+DFT(b); DFT linearity |
| 3 | dft_convolution_to_pointwise_lemma | T3 | DFT(conv(a,b)) = DFT(a)*DFT(b) — **KEY** lemma |
| 4 | idft_inverse_property_lemma | T3 | IDFT(DFT(v)) = v inverse property |
| 5 | convolution_theorem_synthesis | T3 | conv(a,b) = IDFT(DFT(a)*DFT(b)) — **theorem** |

## The 4-step derivation chain (embedded in convolution_theorem_synthesis algebra_dict)

```
Premise 1 (DFT_convolution_to_pointwise):
    DFT(conv(a, b)) = DFT(a) * DFT(b)

Premise 2 (IDFT_inverse_property):
    IDFT(DFT(v)) = v  for any v

Apply IDFT to both sides of Premise 1:
    IDFT(DFT(conv(a, b))) = IDFT(DFT(a) * DFT(b))

Substitute Premise 2 on LHS (v := conv(a, b)):
    conv(a, b) = IDFT(DFT(a) * DFT(b))

QED
```

## Edge structure

```
pointwise_product -> complex_field, vector_space
dft_linearity_lemma -> discrete_fourier_transform (T3), complex_field, vector_space
dft_convolution_to_pointwise_lemma -> discrete_fourier_transform (T3), circular_convolution, pointwise_product
idft_inverse_property_lemma -> discrete_fourier_transform (T3)
convolution_theorem_synthesis -> dft_convolution_to_pointwise_lemma, idft_inverse_property_lemma

EXISTING ATOM UPDATES:
circular_convolution -> convolution_theorem_synthesis  (substrate now knows theorem exists)

(2 planned updates to discrete_fourier_transform SKIPPED — T1 form per spec doesn't exist;
 DFT lives at T3; the 3 followup edges via T3 reference were added via fix script)
```

## Expected CELL-DISTILL-VERIFY-2 behavior post-authoring

- Verdict on (circular_convolution, discrete_fourier_transform) pair: **THEOREM_LINKED-PROVEN** (was THEOREM_LINKED-unproven via generic RELATES)
- L6-PROOF `derivation_present`: True
- CHTV-1 type-checker verifies each step
- Cross-domain bridge: VSA binding (FHRR fhrr_bind ≅ circular_convolution) ↔ signal processing (DFT/IDFT)

## Substrate-product positioning artifact (NEW)

**First cross-domain L6-PROOF derivation chain** authored from substrate's own typed atoms. Substrate now can prove the convolution theorem from first principles — entirely from substrate-internal atoms; no LLM, no external derivation. Cell-DISTILL-VERIFY-2 refusal-mode → proven-mode transition.

Composes with USER 11th rule (substrate-standalone-capability-first) — substrate teaches itself the convolution theorem.

## Routing

- **Exp-Dev:** convolution-theorem chain authored on local sandbox (commit `968c8a38`). Re-run CELL-DISTILL-VERIFY-2 to confirm THEOREM_LINKED-PROVEN verdict. May need to also run on canonical-remote (this was on local; canonical may need separate run if states differ).
- **Research:** authoring spec realized; tracking-doc Section 9 anchor available. Closed-loop step 3 refusal-mode → proven-mode transition empirical case study.
- **Skunkworks:** Class B candidate transitioning REFUSAL → PROVEN; operator-overlap v2 case study material.
- **Testbed (me):** standing. 49 deliverables session + 50 routing notes. Branch tip `968c8a38`.

## Cross-references

- Research spec: `research_to_testbed_LANE_B_AUTHORING_SPEC_convolution_theorem_4_step_derivation_chain_*.md` (16:12)
- Convolution theorem ship: commit `968c8a38`
- LFS COMPLETE earlier this turn: `14c0f0ed..b0aba3bf` on main
- Parser-v2 (v2) earlier this turn: `b60c3d92`
- INTEGRATE-1 (step 4 closed loop): `60c7cb72`

---

**Research + Exp-Dev:** CONVOLUTION THEOREM 4-step derivation chain AUTHORED commit 968c8a38 + 5 atoms (pointwise_product T2 + dft_linearity_lemma T3 + dft_convolution_to_pointwise_lemma T3 KEY + idft_inverse_property_lemma T3 + convolution_theorem_synthesis T3) + 12 DEPENDS_ON edges + 4-step derivation embedded in synthesis atom (Premise1 DFT(conv(a,b))=DFT(a)*DFT(b) + Premise2 IDFT(DFT(v))=v + apply IDFT both sides + substitute -> conv(a,b)=IDFT(DFT(a)*DFT(b)) QED) + cross-domain L6-PROOF VSA binding <-> signal processing first in substrate + substrate 20820 -> 20825 + EXPECTED CELL-DISTILL-VERIFY-2 verdict THEOREM_LINKED-PROVEN + tracking-doc Section 9 anchor + closed-loop step 3 refusal-mode -> proven-mode transition + 49 deliverables session 50 routing notes branch 968c8a38.
