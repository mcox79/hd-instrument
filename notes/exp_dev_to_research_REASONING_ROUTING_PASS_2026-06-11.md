# Exp-Dev -> Research: Phase-3 reasoning-routing oracle PASS -- the pipeline pieces all work

## Drill B REASONING-ROUTING-30-ORACLE: HARD_PASS
routing_acc=0.967 (29/30) | answer_acc=0.892. Substrate-as-classifier (prototype-bundle cleanup over 6 reasoning classes:
deductive/Bayesian/causal/counterfactual/temporal/analogical) routes problems to the right primitive; routed validated
primitives solve. The Phase-3 extraction->reasoning BRIDGE works substrate-only, no trained router.

**Honest caveat:** the 30 instances have clean class-signature keywords (your oracle design). Real-text routing would be
noisier (the routing keywords would be embedded in messy NL). The MECHANISM is validated; the end-to-end noise is Phase 4.

## Pipeline status -- all pieces validated individually
| Stage | Result | On |
|---|---|---|
| Extraction (slot-filling) | slot-F1 0.87 / intent 0.85 (Tier A) | ATIS gold |
| Routing (reasoning class) | routing_acc 0.967 | Drill B oracle (clean) |
| Reasoning primitives | PP-343/348/360 etc. 0.9-1.0 | validated |

The pieces work. The OPEN question (my earlier word-problem gate, acc 0.023) is the END-TO-END on real noisy text: real
word-problem -> correct slots -> correct routing -> correct solve, composed. Each stage passes in isolation / on clean inputs;
Phase 4 integration tests whether they compose on real hendrycks MATH + HumanEval (where the inputs are messy, not clean-signal).

## Next
- RT-1 schema retrieval (Drill A 114-schema; ~2hr) -- Phase 2 gate.
- Phase 4 integration: end-to-end on real MATH level-1 + HumanEval-LIGHT (the real test of whether the validated pieces compose
  on noisy real text). This is where the 0.023 word-problem-gate gap gets re-tested with the full pipeline.

## Cross-ref
- routing metrics: data/exp_reasoning_routing_oracle_cpu_v1/metrics.json
- Drill B: notes/research_drill_reasoning_composition_routing_2x_2026-06-11.md
