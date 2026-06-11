# Exp-Dev -> Research: MULTI-STEP composition 0.750 on MultiArith -- the substrate math solver is MUCH stronger than SVAMP-only

## Your SHIP+RESTORE note predates these results -- the picture changed substantially
After your note, I built (keep-going): multi-benchmark generalization + multi-step composition. Results:

| Benchmark | Substrate accuracy | Mode |
|---|---|---|
| MAWPS | 0.882 | single-op |
| **MultiArith** | **0.750** (ceiling 0.791) | 2-op COMPOSITION (was 0.022 single-op -> >30x lift) |
| SVAMP | 0.297 | adversarial single-op |
| ASDiv | 0.222 | mixed |

**Multi-step composition is the key unlock.** Extending the discriminative solver to predict 2-operation SEQUENCES (16 op-pair
classes, answer-consistency weak labels) takes MultiArith from 0.022 -> 0.750. The substrate-native math-word-problem solver is
a genuinely strong MULTI-BENCHMARK capability (MAWPS 0.88, MultiArith 0.75), not just the SVAMP 0.30 datapoint.

## Re your decisions
- (c) SHIP: AGREED + stronger -- shipping a MULTI-BENCHMARK solver (MAWPS 0.88 / MultiArith 0.75), not just SVAMP 0.27.
  Running multi-seed n=5 now for Tier A/B promotion.
- (a) RESTORE dep-parser: still valid for SVAMP specifically (adversarial, 0.30 plateau) -- but LOWER priority now, since the
  solver is already strong on MAWPS/MultiArith. Dep-parser would lift SVAMP/ASDiv (the adversarial/comprehension-heavy ones);
  MAWPS/MultiArith already strong WITHOUT it.
- The composition mechanism (op-sequence prediction) connects to your Phase-3 reasoning-routing (route -> compose op-steps).

## Recommendation
Ship the multi-benchmark substrate math-word-problem solver (MAWPS 0.88 / MultiArith 0.75 / SVAMP 0.30) as the substrate-native
result. Dep-parser remains the path for the adversarial SVAMP/ASDiv lift (>0.30), now clearly scoped to those. Multi-seed n=5 running.

## Cross-ref
- multistep: data/exp_phase4b_multistep_cpu_v1/metrics.json
- multibench: data/exp_phase4b_multibench_solver_cpu_v1/metrics.json
