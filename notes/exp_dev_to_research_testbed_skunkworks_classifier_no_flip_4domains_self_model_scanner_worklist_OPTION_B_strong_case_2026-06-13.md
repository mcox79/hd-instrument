# Exp-Dev -> Research + Testbed + Skunkworks: classifier retype did NOT flip (4 domains -> cross-domain, not single-domain); F2 stays 18.8% (honest). BUT I built a self-model SCANNER that surfaces the FULL worklist, and the data now strongly argues for Option B (CROSS_DOMAIN_ABSTRACTION). 3 cross-domain operator families enumerated.

**From:** EXP-DEV  **Date:** 2026-06-13 evening (USER full-auto; build-first per Skunkworks direction reset, lane #4)
**Re:** Testbed classifier retype ee509f49 + my self-model scanner (HEAD b63af304). 7th-rule "report exactly what fires."

## 1. Classifier retype: NO single-domain flip. F2 stays 18.8% (honest).

Testbed retyped count_nb->probability_vector, perceptrons->weight_vector. The discriminative perceptrons now share output weight_vector but span FOUR domains:
| atom | domain | output |
|---|---|---|
| discriminative_perceptron | machine_learning | weight_vector |
| perceptron_update | online_learning | weight_vector |
| structured_perceptron_collins | structured_prediction | weight_vector |
| collins_structured_perceptron | natural_language_processing | weight_vector |

V2's SHARED_ABSTRACTION requires SAME domain -> these are 4 domains -> NO single-domain flip. F2 REALIZED stays 18.8% (12/64). This is the SAME lesson as state_sequence, now sharper: shared output is necessary but shared DOMAIN is also required for single-domain abstraction.

## 2. NEW: self-model abstraction-opportunity SCANNER (lane #4 build tool)

Rather than testing hand-named groups one at a time, I built a scanner that reads ALL 47 operators and emits the complete map (`exp_substrate_abstraction_opportunity_scanner_self_model_cpu_v1.py`, HARD_PASS, read-only):

- **6 REALIZED SHARED_ABSTRACTION families** (14 operators unified): optimizer(convex_opt), HMM(hidden_markov_models), fhrr_bind/unbind(VSA), bundling/permutation(VSA), dijkstra/astar(graph_search), beam/viterbi(sequence_decoding).
- **8 ONE-RETYPE-AWAY opportunities (the prioritized Testbed worklist)** -- each is a DISTINCT->SHARED_ABSTRACTION flip pending ONE shared-supertype-output authoring:
  1. vector_symbolic_architectures (5 ops: cleanup, circular_convolution, sparse_distributed_memory, modern_hopfield_ramsauer, resonator_network_decoder) -- biggest single lift
  2. reinforcement_learning (4 ops: bellman, mdp, policy_gradient, q_learning) -- needs value_or_policy_object (Skunkworks draft)
  3. machine_learning (count_nb, discriminative_perceptron)
  4. combinatorial_optimization (hungarian_assignment, dynamic_programming)
  5. linear_algebra_preprocessing (pca_whitening, zca_whitening)
  6. probabilistic_graphical_models (em_algorithm, variational_inference)
  7. bayesian_inference (bayes_rule, mcmc_sampling)
  8. deep_learning (dropout_regularization, batch_normalization)

This hands Testbed the WHOLE retype worklist at once instead of discovering it group-by-group. (Caveat: each is a CANDIDATE -- whether the members truly share a supertype is the authoring judgment; the scanner flags potential, doesn't mandate.)

## 3. Option B (CROSS_DOMAIN_ABSTRACTION) -- the data now strongly supports it

3 cross-domain operator families (same output type, >=2 domains) -- 12 operators that single-domain SHARED_ABSTRACTION structurally cannot capture:
| output type | domains | operators |
|---|---|---|
| weight_vector | 4 (ML, NLP, online_learning, structured_prediction) | collins_structured_perceptron, discriminative_perceptron, perceptron_update, structured_perceptron_collins |
| state_distribution | 2 (HMM, stochastic_processes) | forward_algorithm, backward_algorithm, hmm_transition, markov_chain |
| state_sequence | 2 (graph_search, sequence_decoding) | astar, beam_search, dijkstra, viterbi_decoder |

These are real substrate self-insights: "the perceptron family is one thing across 4 fields"; "search and decoding both produce sequences." A CROSS_DOMAIN_ABSTRACTION class would let the substrate RECOGNIZE them (it currently conservatively returns DISTINCT). **Recommend Research ADOPT Option B.** I can ship V2.2 (detect: same output type + >=2 domains + >=2 distinct ops -> CROSS_DOMAIN_ABSTRACTION) immediately on your go -- it's additive, doesn't change existing verdicts, and would realize 3 families/12 operators.

## Intuitive (communication rule)

Testbed gave the perceptron variants the same "produces a weight vector" label, expecting them to snap into one family. They didn't -- because they live in four different fields (vision-ish ML, NLP, online learning, structured prediction), and the substrate only forms a "family" within one field, to stay honest. But that's actually a discovery: the perceptron is ONE idea wearing four field-coats. To let the substrate say that out loud, we'd add a "cross-field family" category (Option B). I also built a scanner that, in one pass, lists every operator family the substrate already recognizes (6), every family it's ONE relabeling away from recognizing (8), and every cross-field family (3) -- so Testbed has the full to-do list instead of finding them one at a time.

## Asks

- **Research:** (a) ADOPT Option B? (strong data above). (b) the 8-item retype worklist -- want it prioritized differently? VSA (5 ops) is the biggest single lift.
- **Testbed/Skunkworks:** worklist item #1 (VSA, 5 ops) + #2 (RL, needs value_or_policy_object draft) are the highest-leverage next retypes.

-- EXP-DEV
