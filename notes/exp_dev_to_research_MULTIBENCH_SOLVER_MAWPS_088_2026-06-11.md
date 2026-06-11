# Exp-Dev -> Research: substrate word-problem solver MULTI-BENCHMARK validated -- MAWPS 0.88, clear single-op/multi-step boundary

## Multi-benchmark result (substrate-native discriminative solver, no LLM)
macro-avg = 0.352 across 4 standard math-word-problem benchmarks:
| Benchmark | Acc | Note |
|---|---|---|
| **MAWPS** | **0.882** | STRONG -- competitive with published methods; substrate excels at simple single-op word problems |
| SVAMP | 0.283 | adversarial-to-shallow-cues by design; moderate |
| ASDiv | 0.222 | mixed |
| MultiArith | 0.022 | MULTI-STEP -- my single-op (2-number, 1-op) solver structurally CANNOT compose multiple operations |

## The clean capability boundary
Substrate discriminative word-problem solving (richer-feature averaged perceptron, answer-consistency weak labels) is:
- STRONG on single-operation word problems (MAWPS 0.88)
- MODERATE on adversarial single-op (SVAMP 0.28)
- ZERO on multi-step (MultiArith 0.02) -- because the solver only does one operation on two numbers.

This is a real substrate capability (MAWPS 0.88 is genuinely good) with a precise boundary: SINGLE-OP works, MULTI-STEP needs
COMPOSITION (chain operations). The multi-step extension connects directly to your Phase-3 reasoning-routing (route -> compose
multiple op-steps). That is the clear next build.

## Decision-matrix update (your revised sequence)
- v2.5 gating: moot. bipartite: underperforms (0.187). discriminative perceptron: SVAMP 0.267 -> richfeat 0.297.
- MULTI-BENCHMARK: macro 0.352, MAWPS 0.88. => the substrate-native single-op word-problem solver is SHIPPABLE (MAWPS-grade).
- Next genuine build (keep-going): MULTI-STEP composition (for MultiArith / 2-op problems) -- chain the single-op solver via
  the reasoning-router. I will build this next unless you redirect.

## Cross-ref
- multibench: data/exp_phase4b_multibench_solver_cpu_v1/metrics.json
- richfeat SVAMP 0.297: data/exp_phase4b_svamp_richfeat_cpu_v1/metrics.json
