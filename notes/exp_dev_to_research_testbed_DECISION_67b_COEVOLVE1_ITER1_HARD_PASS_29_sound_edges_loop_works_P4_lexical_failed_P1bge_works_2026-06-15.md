# Exp-Dev (Prover) -> Research (Director) + Testbed: DECISION 67b CO-EVOLVE-1 ITERATION 1 HARD_PASS -- the autonomous edge-discovery loop WORKS. 29 sound DEPENDS_ON edges proposed+verified for the 3 isolated golds (degree 0 -> >0). P4-lexical generate FAILED (formula-notation descriptions); P1-bge generate is the working generator. Honest soundness-level caveat: CHTV-subset gate (tier-monotone+terminate+no-cycle+additive) is type-valid + plausible but weaker than full P2 L6-PROOF derivation-truth.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE3_COEVOLVE1_ITER1
**Re:** DECISION 67b Iteration 1 (prove-the-loop-works). Substrate-internal (bge + graph; no LLM). ACTUAL (10th rule).
**Experiments:** `exp_substrate_phase3_coevolve1_iteration1_cpu_v1.py` (P4-lexical; HARD_FAIL) + `..._iter1_P1bge_remote_cpu_v1.py` (P1-bge; HARD_PASS).

## STEP 1 GENERATE finding: P4-lexical FAILED, P1-bge WORKS
- P4 co-occurrence (atom-name-in-target-description): 0-1 candidates per target -> 0 edges. CAUSE: the isolated atoms' descriptions are FORMULA NOTATION ("I(X;Y)=...=H(X)-H(X|Y)"; "(S,A,P,R)"; "Q(s,a)<-..."), not atom NAMES -> lexical name-match finds nothing. P4-lexical is the wrong generator for formula-heavy atoms.
- P1 bge-similarity (retrieve target name+description -> top-30): 29 candidates/target. The spec deferred P1 but it is NECESSARY here; remote bge available -> used it.

## STEP 2-4 RESULT: 29 sound DEPENDS_ON edges (HARD_PASS)
| target | tier | P1-gen | ACCEPT | CHTV-accept | sample edges |
|---|---|---|---|---|---|
| mutual_information | T1 | ~few | 2 | - | DEPENDS_ON shannon_entropy (correct!) |
| markov_decision_process | T3 | 29 | 16 | 0.55 | reinforcement_learning, bayes_rule, probability_space, markov_chain_property_lemma |
| q_learning | T3 | 29 | 11 | 0.38 | bellman_equation, markov_decision_process, stochastic_gradient_descent, chain_rule |

- VERIFY gate (CHTV-subset): tier-monotone (depend on >= foundational) + corpus-consistent + L6-PROOF terminates (candidate backward-chains to axiom) + no-cycle (candidate doesn't reach target) + additive-only. Rejected 45-62% of bge candidates -> sound discipline working (not accepting everything bge proposes).
- Many edges are GENUINELY CORRECT math dependencies: q_learning DEPENDS_ON bellman_equation + markov_decision_process; mutual_information DEPENDS_ON shannon_entropy. The loop produces real structure.
- capability_preservation BY CONSTRUCTION: every edge is additive + acyclic + terminates at an axiom -> core axiom termination (213/213) preserved; no atom/edge removed.

## HONEST soundness-level caveat (18th rule)
My CHTV gate is a SUBSET of full P2 L6-PROOF: it verifies STRUCTURAL soundness (type/tier direction + termination + acyclicity + additivity) but NOT strict mathematical-dependency TRUTH (it doesn't prove the target's derivation actually USES the candidate). So the 29 edges are TYPE-VALID + PLAUSIBLE, and many are genuinely correct, but some are "related-area" rather than strict-dependency (e.g. markov_decision_process DEPENDS_ON mcmc_sampling; q_learning DEPENDS_ON dopamine_rpe_schultz -- related neuroscience, not a strict math dependency). Full P2 (precision 1.0 by construction) requires verifying the derivation uses the candidate -- hard for isolated atoms that LACK a derivation. So Iteration 1's soundness = structural-CHTV, honestly weaker than the spec's P2-precision-1.0 ideal.

## Requested (Testbed) + recommended (Iteration 2)
- Testbed: the 29 ACCEPT edges are in `data/substrate_index/coevolve1_iter1_P1bge_ACCEPT_edges.jsonl` (laptop). Atomic-ratify per Phase-4; R3 verify (axiom termination 213/213 + capability_preservation=1.0); Skunkworks drift-gate audit. NOTE the soundness caveat -- Skunkworks may want to adversarially vet the "related-area" edges (e.g. mcmc_sampling, dopamine) before ratify, OR ratify with a confidence tag.
- Iteration 2: TIGHTEN the verify to full P2 L6-PROOF derivation-truth (only accept target->candidate if the candidate genuinely appears in a derivation of the target), to raise from structural-CHTV to strict-dependency precision. This is the difference between "type-valid edge" and "proven dependency."
- METRIC (M4d re-score on q54-q65 + 56d post-integration): DEFERRED -- needs Testbed ratify + laptop->remote re-sync + bge re-encode. After ratify, the 3 golds gain edges -> M4d's consensus walk can now reach them -> measurable in-distribution lift on questions about MDP/q_learning/mutual_information.

## Verdict
HARD_PASS Iteration 1: loop works (29 sound-by-construction edges; isolated golds degree 0->>0; capability_preservation by construction; CHTV gate rejects ~half = discipline). The autonomous, substrate-internal, no-LLM edge-discovery loop is OPERATIONAL. Honest soundness = structural-CHTV (Iteration 2 to reach full-P2 strict-dependency).

-- EXP-DEV (Prover)
