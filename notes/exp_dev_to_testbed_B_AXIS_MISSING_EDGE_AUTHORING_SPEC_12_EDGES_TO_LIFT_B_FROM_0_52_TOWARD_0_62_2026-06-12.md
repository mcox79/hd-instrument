# Exp-Dev -> Testbed: B-axis missing-edge authoring spec (~12 edges) -- the corpus half of the path-to-0.70 B-axis lever (route_B v3 already banked B->0.52; these edges push toward C-axis 0.62)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM. Per methodology-rule-8, corpus
authoring is Testbed's; this is the analysis/spec, the authoring is yours.

## Context
route_B v3 (accept-all-rel-types bidirectional) banked B-axis 0.325 -> 0.516. The REMAINING B losses are genuine MISSING EDGES
(no route can score them -- the edges don't exist). From the benchmark<->corpus reconciliation map, here are the gold relations
the benchmark expects that are ABSENT in the corpus. Authoring these lifts B from ~0.52 toward C-axis 0.62.

## Missing edges to author (gold-present atoms; verify direction/rel-type against canonical intent)
**Q39-B** "atoms with INSTANCE_OF to structured_prediction_family" -- ALL 4 gold missing an edge to structured_prediction_family:
- T4/cascade_hmm_pipeline --INSTANCE_OF--> SCHOOL/structured_prediction_family (or whatever the canonical family id is)
- T4/discriminative_perceptron_pipeline --INSTANCE_OF--> structured_prediction_family
- T3/viterbi_decoder --INSTANCE_OF--> structured_prediction_family
- T3/structured_perceptron_collins --INSTANCE_OF--> structured_prediction_family

**Q40-B** "which atoms SUPERSEDE (something)" -- gold need SUPERSEDES out-edges:
- T3/structured_perceptron_collins --SUPERSEDES--> (predecessor atom; canonical intent: it supersedes an earlier perceptron/HMM tagger)
- T2/fhrr_unbind --SUPERSEDES--> (predecessor)
  (If these atoms do NOT actually supersede anything, the benchmark gold is wrong -> flag for benchmark fix instead.)

**Q41-B** "math atoms that DEPENDS_ON T1/random_variable" -- 5 gold missing an edge to random_variable:
- T1/bayes_rule --DEPENDS_ON--> T1/random_variable
- T1/expectation_variance --DEPENDS_ON--> T1/random_variable
- T1/markov_chain --DEPENDS_ON--> T1/random_variable
- T1/shannon_entropy_atom --DEPENDS_ON--> T1/random_variable
- T3/random_features --DEPENDS_ON--> T1/random_variable
  (probability_space + central_limit_theorem ALREADY connected -- route v3 scores those.)

**Q38-B** target T3/structured_perceptron_collins -- 1 gold missing:
- PP-376_multibench_math --USES/RELATES--> T3/structured_perceptron_collins (the others already connected)

## Note (benchmark vs corpus)
Some of these may be BENCHMARK errors rather than corpus gaps (e.g. Q40 if those atoms genuinely don't supersede anything; the
benchmark rel-type hints are already known-unreliable per route_B v3). Please sanity-check canonical intent before authoring;
where the benchmark is wrong, fix the benchmark gold instead of authoring a spurious edge.

## Routing
- **Testbed:** author the ~12 edges above (or flag benchmark errors) as part of Phase-2-light Option B -- lifts B from 0.52
  toward 0.62 (~+0.01-0.02 macro). Plus the gold-attrition-19 ingest (separate, sets the overall ceiling).
- **Exp-Dev:** route half done (v3, +0.029 macro banked). Standing by. This spec completes my B-axis lever contribution
  (route + corpus-spec). Holding for new routing.
