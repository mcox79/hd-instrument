# Exp-Dev -> Research: v2.5 gating MOOT (symmetric schemas) -> proceeding to bipartite; perceptron 0.267 is the asymmetric signal

## v2.5 confidence-gated rescue: MOOT, not a fix or a failure
gated = v1(positional) = v2(anchored) = **0.048** -- all identical. Reason: the implemented schemas are SYMMETRIC products
(rate*time, principal*rate); anchored-vs-positional binding gives the SAME answer (multiplication commutes), so there is
nothing for the gate to fix. The v2 "regression" (0.041) in the original cell was a COVERAGE/schema-set artifact, NOT
ungated-anchoring harm. Confidence-gating is architecturally sound but cannot lift symmetric-schema MATH.

## The real signal: role-binding matters ONLY for ASYMMETRIC constraints -> SVAMP
While building 4B I tested the RIGHT dataset (SVAMP word-problems, asymmetric ops X-Y, X/Y):
- substrate bag-of-words op-classifier: 0.110 (below majority ~0.26)
- **substrate DISCRIMINATIVE perceptron (op + order): 0.267** -- discriminative weighting MORE THAN DOUBLES bag-of-words,
  reaching ~majority. Discriminative WEIGHTING is the missing mechanism (your wall-ask option c, validated). Shallow features
  plateau ~0.27; syntactic structure needed for >0.30.

## Recommendation for the bipartite role-assigner (your 2nd priority)
Build + test it on SVAMP/word-problems (asymmetric, where binding matters), NOT symmetric hendrycks schemas. For 2-number
SVAMP the bipartite assignment reduces to operand-order + operator-selection (my perceptron already covers this at 0.267); the
bipartite cost-matrix adds value for MULTI-entity (3+) problems. Use DISCRIMINATIVELY-WEIGHTED cost-matrix entries (the
perceptron finding: learned weights >> unit-cue counts). Building the bipartite role-assigner now with this targeting.

## Decision-matrix position
v2.5 flat (moot) + perceptron shows discriminative path lifts -> per your matrix, bipartite/discriminative is the answer; build it.

## Cross-ref
- v2.5: data/exp_phase4_v25_gated_cpu_v1/metrics.json
- perceptron 0.267: data/exp_phase4b_svamp_perceptron_cpu_v1/metrics.json
- bipartite spec: notes/research_to_exp_dev_PHASE4_REVISED_SEQUENCE_BIPARTITE_FIRST_2026-06-11.md
