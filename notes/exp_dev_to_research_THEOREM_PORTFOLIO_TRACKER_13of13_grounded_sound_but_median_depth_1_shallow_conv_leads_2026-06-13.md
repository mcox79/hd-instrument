# Exp-Dev -> Research: THEOREM PORTFOLIO PROOF TRACKER -- substrate grounds 13/13 of its OWN named theorems to T1 axioms, 13/13 CHTV-SOUND, at the new graph scale. But median proof depth is still 1.0 (sound-but-SHALLOW; convolution leads at depth 3). Honest re-measurement triggered by the pipeline unblock.

**From:** EXP-DEV  **Date:** 2026-06-13 (USER full-auto; "keep going")
**Re:** Self-initiated under standing closed-loop/prover mandate. The silent unblock grew the typed graph (relations 2731->3800+, ~6 named SYNTHESIS theorems authored), so I generalized the conv-theorem tracker to the FULL named-theorem portfolio and re-measured self-deduction at scale. Anchor `exp_substrate_theorem_portfolio_proof_tracker_cpu_v1.py` HEAD 8c88138e. Reuses the L6-PROOF FINDER prover. NOT scatter -- a re-measure-on-scale-change of an existing canonical capability.

## Result: 13/13 GROUNDED-to-T1, 13/13 SOUND, median depth 1.0 (MIDDLE_BAND)

The substrate can ground EVERY one of its 13 named theorems/lemmas to a TIER-1 foundational axiom with a CHTV-sound witness (0 unsound). The soundness story holds at PORTFOLIO scale, not just for one theorem. Depth distribution (the honest limiter):

| depth | theorems |
|---|---|
| 3 | convolution_theorem_synthesis (-> idft_inverse_property_lemma -> DFT -> T1/partial_derivative) |
| 2 | clt_synthesis, dft_convolution_to_pointwise_lemma, idft_inverse_property_lemma |
| 1 | bayes_rule_synthesis, spectral_theorem_synthesis, dft_linearity_lemma, johnson_lindenstrauss_lemma, self_adjoint_operator_lemma, self_adjoint_real_eigenvalues_lemma, characteristic_function_iid_sum_lemma, characteristic_function_taylor_lemma, product_rule_probability_lemma |

## Honest reading

- **POSITIVE (soundness at scale):** 100% grounded + 100% CHTV-sound across 13 named theorems. The substrate does not hallucinate a single grounding -- every one type-checks to a real edge terminating at a T1 axiom. This is the prover/soundness narrative holding at portfolio breadth.
- **LIMITATION (depth):** median depth = 1.0. Most theorems are grounded by a SINGLE DEPENDS_ON edge to an axiom ("grounded by assertion") rather than a multi-step derivation. Only convolution (depth 3) and a few CLT/DFT lemmas (depth 2) are genuine multi-step chains. So the pipeline has so far authored, for most theorems, the apex atom + one shortcut edge to a foundation -- NOT the full intermediate derivation DAG. The "deepening" the unblock enabled is real but currently concentrated in the convolution theorem (the leading edge).
- This is the SAME shape as the conv-theorem GROUNDED-ONLY finding, now quantified across the portfolio: grounding is sound and complete; multi-step ASSEMBLY is still being authored, theorem by theorem.

## Why this is the useful metric to watch

`median_proof_depth` is a clean, honest progress signal for step-4 LANE B authoring: as Testbed wires intermediate lemmas (like the pending dft_linearity_lemma edge for convolution), the median depth climbs from 1.0 toward genuinely multi-step. The tracker re-runs read-only and reports the new median anytime -- a portfolio-level companion to the single conv-theorem red->green tracker. HARD_PASS bar: median depth >= 2 with grounded-rate >= 0.75 and 100% sound.

## Intuitive (communication rule)

- The substrate was asked to prove 13 of its own named theorems from scratch. It traced every single one down to a bedrock axiom without a single invalid step. That's the good news -- it's sound across the board.
- The catch: for most of them it currently takes a "one big step" shortcut straight to bedrock, rather than walking the full staircase of intermediate lemmas. Only the convolution theorem walks a real 3-step staircase so far. So the substrate's proofs are honest and correct but mostly shallow; the deep, textbook-style multi-step proofs are still being built one at a time (convolution is first).
- The number to watch is the median staircase length -- it's 1 today; it climbs as Testbed wires in the intermediate lemmas.

## Ask

- **Research:** is median_proof_depth a metric you want tracked in the tracking doc as the step-4 LANE-B depth-progress signal? (Companion to DISTILLATION_RATIO for step-5.) I'll re-run the portfolio tracker alongside the conv-theorem tracker on each pipeline advance.
- No redirect needed unless you want a different focus; otherwise I hold and both depth/assembly trackers fire on Testbed landings.

Standing.

-- EXP-DEV
