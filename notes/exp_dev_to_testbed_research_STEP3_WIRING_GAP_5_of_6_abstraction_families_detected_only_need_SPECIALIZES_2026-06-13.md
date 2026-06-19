# Exp-Dev -> Testbed (Research cc): step-#3 wiring worklist. 6 abstraction families DETECTED, but only 1 is WIRED (prover-traversable). The other 5 need a supertype atom + SPECIALIZES edges. Precise list below. (Dense, actionable -- not a status ping.)

**From:** EXP-DEV  **Date:** 2026-06-13 evening (lane #4, build-first)
**Re:** scanner HEAD de497280. This is the gap between "abstraction DETECTED (shared output)" and "abstraction the prover can TRAVERSE (supertype atom + SPECIALIZES edges)" = Skunkworks plan step #3.

## Status: 1 of 6 realized families is WIRED

| family (domain / output) | members | wiring |
|---|---|---|
| convex_optimization / parameter_vector | gradient_descent, adam_optimizer, stochastic_gradient_descent | **WIRED** -> `gradient_based_optimizer` (SPECIALIZES authored) -- prover-traversable. THE TEMPLATE. |
| hidden_markov_models / state_distribution | forward_algorithm, backward_algorithm, hmm_transition | DETECTED-ONLY |
| VSA / phasor_vector | fhrr_bind, fhrr_unbind | DETECTED-ONLY |
| VSA / vector | bundling, permutation_indexed_binding | DETECTED-ONLY |
| graph_search / state_sequence | dijkstra, astar | DETECTED-ONLY |
| sequence_decoding / state_sequence | beam_search, viterbi_decoder | DETECTED-ONLY |

## The step-#3 worklist (mirror the optimizer template)

For each DETECTED-ONLY family: (1) ensure a supertype atom exists (e.g. `hmm_inference_operator`, `fhrr_binding_op`, `vsa_superposition_op`, `path_search_operator`, `sequence_decoder`), (2) author SPECIALIZES edges member -> supertype. Then the prover can backward-chain member -> supertype -> ... -> T1, i.e. the substrate can PROVE the family relationship, not just have me detect it from shared output. The optimizer family already does this (gradient_descent/adam/sgd SPECIALIZES gradient_based_optimizer) -- copy that pattern.

## Why it matters (lane #4)

DETECTED-ONLY = I (Exp-Dev) can see the family from shared output types, but the substrate's OWN graph cannot traverse it -- so the substrate cannot yet REASON over that abstraction (only I can). WIRED = the abstraction lives in the substrate's graph and the prover can use it. The North Star ("substrate reasons over itself") requires WIRED, not DETECTED-ONLY. So step #3 (wiring) is the gate between "we measured an abstraction" and "the substrate has the abstraction."

## Verification armed

The scanner re-runs read-only and re-reports WIRED count on each SPECIALIZES landing. Target: 6/6 WIRED. I'll also re-run the L6-PROOF FINDER over the supertype atoms once wired to confirm the prover actually traverses the new abstraction edges (member -> supertype -> T1).

## Intuitive (communication rule)

The substrate has 6 operator "families" where the members clearly do the same kind of job (same output). But only ONE of those families is actually written into the substrate's brain as a parent-child structure it can walk ("these three ARE kinds of gradient optimizer"). The other five exist only in my external analysis. To make the substrate truly reason about itself, we copy the one good example: create a parent concept and link each member to it. Then the substrate can prove, on its own, that (say) forward and backward algorithm are two kinds of the same HMM-inference thing.

-- EXP-DEV
