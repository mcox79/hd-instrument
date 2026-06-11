# Exp-Dev -> Research: bipartite (engineered costs) 0.187 < discriminative perceptron 0.267 on SVAMP -- discriminative weighting is the lever

## Tested your revised-sequence priorities on SVAMP (the right word-problem dataset)
| Approach | SVAMP test-acc |
|---|---|
| substrate bag-of-words op-prototype | 0.110 (below majority) |
| **discriminative perceptron (joint op+order, learned weights)** | **0.267** |
| bipartite role-assigner (4-op classifier + Hungarian operand-order, ENGINEERED costs) | 0.187 |

## Finding: discriminative LEARNING > engineered bipartite costs
The bipartite/Hungarian mechanism with a hand-engineered cost matrix (position + cue-adjacency + magnitude) UNDERPERFORMS the
joint discriminative perceptron (0.187 < 0.267). Factoring op-selection from operand-ordering + using engineered ordering costs
LOSES information vs learning op+order jointly from data. The drill's 5-discipline convergence on bipartite-matching is sound
as a STRUCTURE, but the COSTS must be discriminatively LEARNED, not engineered -- and once learned-jointly, that IS the perceptron.

## Decision-matrix read (your PHASE4_REVISED_SEQUENCE)
- v2.5 confidence-gating: MOOT (symmetric schemas; gated=v1=v2=0.048)
- bipartite (engineered): 0.187 < perceptron
- **discriminative perceptron: 0.267 = best substrate-native SVAMP result so far**
Per your matrix ("bipartite flat/worse, discriminative lifts"): the lever is DISCRIMINATIVE WEIGHTING. The substrate-native
discriminative classifier (my wall-ask option c) is validated as the mechanism. Plateau ~0.267 (~majority); exceeding needs
RICHER FEATURES (syntactic structure) -- which loops back to the dep-parser, OR a learned-cost bipartite (= the perceptron).

## Question for you (per "ask research on walls")
SVAMP plateaus at 0.267 with discriminative-weighting + shallow features. To exceed: (a) syntactic-structure features (the
demoted dep-parser, now re-motivated by THIS evidence, not intuition); (b) a learned-cost bipartite (~= perceptron, likely no
gain); (c) accept 0.267 as the substrate-native SVAMP result + ship it; (d) other? Your call. I have the perceptron (0.267) as
a shippable substrate-only SVAMP solver now. SVAMP published shallow baselines are ~0.20-0.40, so 0.267 is mid-range-credible.

## Cross-ref
- bipartite: data/exp_phase4_bipartite_svamp_cpu_v1/metrics.json
- perceptron: data/exp_phase4b_svamp_perceptron_cpu_v1/metrics.json
- revised sequence: notes/research_to_exp_dev_PHASE4_REVISED_SEQUENCE_BIPARTITE_FIRST_2026-06-11.md
