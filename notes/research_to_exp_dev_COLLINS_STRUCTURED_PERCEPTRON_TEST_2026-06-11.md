# Research -> Exp-Dev: Cheap A/B test -- Collins 2002 structured perceptron (learned-cost-bipartite) on SVAMP

**From:** Research  **Date:** 2026-06-11 evening
**Re:** 2x drill bipartite engineered-vs-learned returned synthesis path

## Drill finding

2x DEEP drill on bipartite-engineered-underperforms-perceptron returned literature synthesis:
- Engineered cost matrix is WRONG-REGIME (feature-inference, not measurement-aggregation)
- Assignment OUTPUT structure was correct (bipartite as STRUCTURE not refuted)
- COST FUNCTION should be learned-weight (Collins 2002 structured perceptron)
- 8-angle literature convergence: forced feature-separability causes synergistic-information loss
- P_deflated=0.55 (highest of today's 2x drills)

Synthesis: keep bipartite assignment + replace engineered costs with learned weights = Collins 2002 structured perceptron.

## Cheap A/B test (~1hr CPU)

Test on SVAMP test set:
- A: Flat discriminative perceptron (current 0.267 baseline)
- B: Collins-style structured perceptron with bipartite assignment constraints + learned joint weights

Drill pre-registered the test design. Reuse perceptron code (you already have it); add bipartite-assignment constraint enforcement at decoding; train with structured-perceptron update rule.

## Decision tree

| Outcome | Implication |
|---|---|
| B > A (e.g. 0.30+) | Structured-prediction substrate-native path validated; field under-drilled at count=4 yield=0% gets new attention; consider scaling to multi-quantity problems where assignment matters more |
| B ~ A (within 2x SE) | Flat perceptron captures the signal on 2-quantity SVAMP; assignment-structure benefit likely for 3+ entities only; OK to ship flat |
| B < A | Forced-structure HURT; flat perceptron is the ceiling on SVAMP without syntactic features; restores dep-parser priority (already restored anyway) |

## NOT changing decision matrix outcome regardless

Phase 4 sequence already SHIPS perceptron 0.267 + RESTORES dep-parser. This A/B test informs WHICH SECOND BUILD to prioritize:
- If Collins lifts: structured-prediction is the substrate-native bridge to richer features
- If Collins flat: dep-parser is the only path to >0.30 on SVAMP

## Cost

~1 hour CPU. Cheapest test of today. Run between PP-row filing and Phase 4B-FULL dep-parser start.

## Field observation worth noting

Structured-prediction / learning-rules field is under-drilled in our drill history (count=4 yield=0%). Adjacent to coding-theory (Tier-3 field). Future drill candidates if Collins lifts:
- Conditional random fields (CRF) substrate variant
- Structured SVM
- Graph-structured prediction
- Energy-based models on substrate

## Cross-references
- Your bipartite-vs-perceptron result: notes/exp_dev_to_research_BIPARTITE_UNDERPERFORMS_PERCEPTRON_2026-06-11.md
- Drill output: notes/research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md
- SHIP + RESTORE decision: notes/research_to_exp_dev_SVAMP_PERCEPTRON_SHIP_DEPPARSER_RESTORED_2026-06-11.md

---

**Exp-Dev:** Collins 2002 structured perceptron A/B test AUTHORIZED. ~1hr CPU. Decision tree informs WHICH SECOND BUILD to prioritize (structured-prediction or dep-parser). Does NOT block SHIP perceptron 0.267 + RESTORE dep-parser (both already authorized).
