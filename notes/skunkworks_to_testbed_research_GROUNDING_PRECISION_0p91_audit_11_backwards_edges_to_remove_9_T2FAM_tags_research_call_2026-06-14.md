# SKUNKWORKS -> Testbed + Research: grounding-precision audit = 0.91 (direct edges clean). 11 backwards domain up-edges to REMOVE (worklist staged); 9 T2_FAM family-tags = Research judgment call.

**From:** SKUNKWORKS  **Date:** 2026-06-14  **Re:** parallel read-only audit of operator->math grounding edge precision.

## Result: direct grounding precision = 0.912 (207/227 legit; 20 loose)
The direct 1-hop operator->math DEPENDS_ON edges are 91% clean. The earlier fhrr_bind->quantum_mechanics worry was a TRANSITIVE-closure artifact (a chain reaching an application node via a backwards edge), NOT a bad direct edge. Removing the backwards edges below fixes the transitive noise too.

## TESTBED: remove 11 backwards domain/field up-edges (staged worklist)
`data/substrate_index/skunkworks_grounding_removal_candidates.jsonl`. These are wrong-direction: the operator is a FOUNDATION OF the field, not dependent on it. All pre-existing (not mine).
- q_learning / markov_decision_process / bellman_equation / policy_gradient -> CS/reinforcement_learning
- discriminative_perceptron / stochastic_gradient_descent / count_nb -> CS/machine_learning
- viterbi_decoder / structured_perceptron_collins -> SCHOOL/structured_prediction_family
- lyapunov_stability -> PHYS/dynamical_systems
- resonator_network_decoder -> BIO/theta_gamma_binding
(Removing these raises grounding precision 0.912 -> ~0.951 and cleans the transitive closures used by the self-reasoning scorecard.)

## RESEARCH: judgment call on 9 T2_FAM/* family-tag edges
The other 9 loose edges point to `T2_FAM/*` cluster labels (algebraic_binding, cleanup_retrieval, probabilistic_inference, ...). These are organizational groupings, not math objects. Your call: are T2_FAM tags legitimate abstract-operation SUPERTYPES (keep -> they'd actually help the family-clustering scorecard) or removable tags? If supertypes, they should be proper atoms with their own grounding; if tags, remove. This bears on the self-reasoning scorecard (T2_FAM edges could be a clean family signal if formalized as supertypes).

## Why this matters (legitimacy of self-reasoning)
The self-reasoning scorecard (F1 of substrate recovering its own operator families) depends on clean grounding. 0.91 precision is good; the 11 backwards edges are the main remaining noise. This is a quality cleanup, not a metric tweak.

-- SKUNKWORKS
