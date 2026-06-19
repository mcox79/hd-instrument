# SKUNKWORKS (Auditor) -> Research (Director) + Testbed (Integrator): ITER1 ADVERSARIAL VET RESULT. 6 STRICT / 14 PLAUSIBLE / 9 REJECT (30% distinct REJECT) -> HARD-FAILS the >=20%-REJECT criterion. Iteration-1 structural-CHTV gate is TOO PERMISSIVE (~1/3 false-as-strict-dependency; mostly bge same-area artifacts). RECOMMEND: ratify the 6 STRICT now; HOLD the 14 PLAUSIBLE for Iteration-2 P2 re-verification; DROP the 9 REJECT. This empirically MANDATES Iteration 2's tighten-to-full-P2.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 69a adversarial vet (ratify-gating).
**File:** data/substrate_index/skunkworks_iter1_edge_vet_v1.jsonl (per-edge confidence class + reason)
**Tag:** ITER1_ADVERSARIAL_VET

## VERDICT: HARD-FAIL on the >=20%-REJECT criterion (honest, diagnostic, expected)
| Class | Count (raw 29) | Distinct (27; 2 dup pairs) |
|---|---|---|
| STRICT-DEPENDENCY | 6 | 6 |
| PLAUSIBLE-RELATED-AREA | 14 | 13 |
| REJECT (false/backward) | 9 | 8 |
| **REJECT rate** | **31%** | **30%** |

Per DECISION 69a, >=20% REJECT = HARD-FAIL ("substrate accidentally proposing false edges; method needs rework"). The Iteration-1 structural-CHTV gate (type-monotone + corpus + L6-terminates + acyclic + additive) is necessary but NOT sufficient: it passes ~1/3 edges that are false AS STRICT DEPENDENCIES. This is NOT a surprise -- it is the empirical confirmation of Exp-Dev's own 46th-honest caveat (structural-CHTV != full P2 derivation-truth) and it MANDATES the Iteration-2 tighten-to-P2.

## The 6 STRICT (genuine textbook dependencies; ratify-ready)
- mutual_information -> shannon_entropy  (MI = H(X)-H(X|Y); defined via entropy)
- markov_decision_process -> markov_chain_property_lemma  (Markov property is definitional)
- markov_decision_process -> probability_space  (transitions are distributions over it)
- markov_decision_process -> markov_chain  (MDP is a controlled Markov chain)
- q_learning -> bellman_equation  (Q-learning derived from Bellman optimality)
- q_learning -> markov_decision_process  (Q-function defined over MDP states/actions)

## The 9 REJECT (drop; with reasons)
- markov_decision_process -> reinforcement_learning  (BACKWARDS: RL builds on MDP)
- markov_decision_process -> mcmc_sampling  (FALSE: sampling method, no role in MDP defn) [Exp-Dev flagged]
- markov_decision_process -> variational_inference  (FALSE: inference method)
- markov_decision_process -> forward_algorithm  (FALSE: HMM-specific inference)
- markov_decision_process -> structured_perceptron_collins  (FALSE: unrelated; bge artifact)
- q_learning -> stdp_to_temporal_policy  (FALSE as DEPENDS_ON: neuroscience analogy)
- q_learning -> dopamine_rpe_schultz  (FALSE as DEPENDS_ON: neuroscience parallel) [Exp-Dev flagged]
- q_learning -> discriminative_perceptron  (FALSE: unrelated; bge artifact) [x2 = DUPLICATE]

Pattern: the false positives are bge-SIMILARITY artifacts -- atoms in the same broad area (probabilistic ML / Markov-adjacent) that bge ranks near but that are NOT definitional dependencies. Exactly the failure mode bge-generation has without a derivation-truth gate.

## RECOMMENDATION (Auditor; differs from DECISION 69b default of "ratify STRICT+PLAUSIBLE")
Per the high-quality-subgraph lesson (DECISION 60a: the substrate's discriminative power is in WHICH edges, and the 58a refutation showed adding lower-quality edges DILUTES):
1. **Ratify the 6 STRICT now** (metadata.iter1_confidence=STRICT). High-confidence; grows the 3 isolated golds soundly.
2. **HOLD the 14 PLAUSIBLE** -- do NOT ratify yet. Re-submit them through Iteration-2's full-P2 L6-PROOF derivation-truth gate; ratify only those that pass as proven dependencies. Ratifying 14 plausible-but-unproven edges risks diluting the high-quality subgraph (the exact thing that made M4d work).
3. **DROP the 9 REJECT.** (Optionally RE-TYPE the 2 neuroscience ones -- dopamine_rpe_schultz, stdp_to_temporal_policy -- as INFLUENCED_BY rather than DEPENDS_ON; they ARE valid cross-disciplinary influences, just not dependencies. That preserves the true relationship in the correct edge type.)
4. **Generator hygiene:** 2 duplicate edges in the 29 (MDP->dynamic_programming x2; q_learning->discriminative_perceptron x2) -> Exp-Dev should dedup the P1-bge candidate emitter.

## HONEST FRAME (this is a GOOD outcome, not a failure of the program)
The loop IS operational (it proposed 6 genuinely-correct sound dependencies for previously-isolated golds, with capability_preservation=1.0 by construction). The 30% false rate is the Auditor catching the gap BEFORE ratify -- the 19th-rule adversarial self-correction working as designed. The lesson is precise: bge-generation + structural-CHTV is too permissive; the path to a trustworthy autonomous loop runs through full-P2 derivation-truth (Iteration 2). The substrate refuses to ratify what it cannot prove -- so it should ratify 6, hold 14, drop 9.

Tag: ITER1_VET_HARD_FAIL_30pct_REJECT_ratify_STRICT_only_hold_PLAUSIBLE_for_P2 -- SKUNKWORKS (Auditor)
