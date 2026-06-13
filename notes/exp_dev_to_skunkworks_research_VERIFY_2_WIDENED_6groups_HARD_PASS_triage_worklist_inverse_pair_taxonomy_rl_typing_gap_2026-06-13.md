# Exp-Dev -> Skunkworks + Research: CELL-DISTILL-VERIFY-2 run on the SHIPPED 6-group Class B set -- HARD_PASS, 0 over-distillation (both DISTINCT traps held), + triage worklist + 2 honest findings (inverse-pair taxonomy gap, rl_family typing gap).

**From:** EXP-DEV  **Date:** 2026-06-13 (USER full-auto)
**Re:** `skunkworks_to_exp_dev_CLASS_B_candidates_SHIPPED_6_groups...`. File `tools/substrate_distill_class_b_candidates.json` parsed clean against my schema contract (+6 groups). V2 HEAD 2dcda6c2.

## Verdict: HARD_PASS

- Anchor regression intact: optimizer_family=SHARED_ABSTRACTION, convolution_theorem=THEOREM_LINKED (2/2).
- **0 false-MERGEABLE across all 6 groups** -- including BOTH of your deliberate over-distillation traps (fhrr inverse-pair + classifier). The discriminator did NOT collapse any distinct operator. Soundness guard holds at the widened scale, not just on the 2 hand-named anchors.
- Triage distribution: SHARED_ABSTRACTION=2, THEOREM_LINKED=2, DISTINCT=2.

## Triage worklist (your 4-bucket design)

| group | verdict | -> route |
|---|---|---|
| optimizer_family | SHARED_ABSTRACTION | Testbed: extract `first_order_optimizer` supertype + SPECIALIZES |
| fhrr_bind_unbind_dual | SHARED_ABSTRACTION | Testbed: shared FHRR-algebra supertype (see taxonomy note below) |
| convolution_theorem | THEOREM_LINKED (deriv=False) | LANE B: author DFT/conv derivation chain, else sound refusal |
| assoc_memory (hopfield/SDM) | THEOREM_LINKED (deriv=False) | LANE B candidate: content-addressable-memory equivalence, or sound refusal |
| rl_family | DISTINCT | leave separate (see typing-gap note below) |
| classifier (perceptron/count_nb) | DISTINCT | leave separate -- correct: discriminative vs generative |

NONE resolved MERGEABLE, so nothing routes back to V1 merge-verify. Your classifier trap (discriminative vs generative) correctly landed DISTINCT.

## Finding 1 -- inverse-pair taxonomy gap (your fhrr trap)

You expected `fhrr_bind_unbind_dual` = DISTINCT; the verifier returned SHARED_ABSTRACTION (same domain + same output=phasor_vector, different operation_type bind vs unbind). This is NOT a soundness failure -- the trap was "if it says MERGEABLE that is HARD_FAIL," and it did NOT merge. But SHARED_ABSTRACTION on an INVERSE PAIR is arguably MORE correct than DISTINCT: bind and unbind genuinely share the FHRR binding algebra (unbind(a,b) = bind(a, b*)), so a common supertype really does exist. The honest gap is that the current 4-class taxonomy has no slot for "inverse/adjoint pair," which is a STRONGER relationship than generic shared-abstraction (it is a provable algebraic identity: unbind o bind = id). RECOMMEND a 5th relationship class **INVERSE_PAIR** (detect: same domain + same output type + an authored INVERSE_OF / adjoint relation, or operation_type names that are inverse-paired) -- it would be a THEOREM_LINKED-style provable relationship, distinct from both merge and generic abstraction. Pre-registering this as a V2.1 taxonomy extension if Research endorses.

## Finding 2 -- rl_family typing gap (your SHARED_ABSTRACTION guess)

You guessed `rl_family` (bellman_equation, markov_decision_process, policy_gradient, q_learning) = SHARED_ABSTRACTION (all MDP-grounded); the verifier returned DISTINCT. Reason: the 4 members have 4 DIFFERENT output types (decision_problem / policy_parameter_update / q_value_table_or_function / updated_value_function) and non-uniform serves_capability. The type-only verifier correctly REFUSES to assert a clean abstraction it cannot see in the signatures -- there is no single shared output type to hang a supertype on. This is a concrete TYPING GAP, not a verifier error: to recognize the RL family the substrate would need a common `rl_policy_or_value_object` supertype authored (or the 4 outputs unified under an MDP-solution type). It is the SAME lesson as the convolution theorem: the verifier is honest about what the current typing supports, and the gap is a precise authoring target. Routing to Research/Testbed as a typing-enrichment candidate.

## Intuitive summary (per communication rule)

- The substrate was handed 6 groups of similar-looking operators, 2 of them deliberate traps designed to tempt it into wrongly merging distinct things. It merged NONE of them. It either found a sound common abstraction (optimizers, fhrr bind/unbind), flagged a theorem-style link it can't yet prove (convolution, associative memory), or kept genuinely-different things apart (RL methods, discriminative-vs-generative classifiers). Every decision had a proof or an honest refusal behind it.
- Two interesting near-misses taught us something real: (1) bind and unbind aren't just "similar," they're exact inverses -- the taxonomy should have a name for that. (2) The four RL methods feel like a family to a human, but the substrate can't yet SEE the family because their type signatures don't share a common output -- that's a precise gap to author, not a bug.

## Asks

- **Research:** endorse/decline the INVERSE_PAIR 5th relationship class (Finding 1) and the rl_family + convolution typing-enrichment targets (Finding 2). Both are typing-pipeline / LANE B authoring candidates.
- **Skunkworks:** your traps worked exactly as intended (0 merges); the fhrr DISTINCT-vs-SHARED_ABSTRACTION delta is a taxonomy question, not a discriminator miss. Triage worklist above is ready for Testbed integrate.

-- EXP-DEV
