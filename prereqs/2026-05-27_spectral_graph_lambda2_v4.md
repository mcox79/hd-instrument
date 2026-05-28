# Pre-registration: spectral_graph_lambda2_v4

**Filed:** 2026-05-27  
**Script:** experiments/exp_spectral_graph_lambda2_v4.py  
**Queue:** remote_cpu_queue  
**Timeout:** 3600s

## Scientific question

Does lambda_2 (algebraic connectivity of substrate Laplacian) positively or negatively
correlate with task-A retention across N in [512, 1024, 2048] and 5 seeds?

v2 HARD_PASS: corr=0.615 at N=[256,512] 2-seed multi-N.
v3 MIDDLE_BAND: corr=-0.881 at N=512 single-seed.
v2/v3 sign-flip demoted spectral-graph row 🟢 -> 🟡 at v234.
Primary rescue (v234): "multi-seed FULL at multiple N."

## Parent verdicts

- spectral_graph_lambda2_v2: HARD_PASS corr=0.615, N=[256,512], seeds=[7,17]
- spectral_graph_lambda2_v3: MIDDLE_BAND corr=-0.881, N=512, seed=17 (single-seed)
- Sign-flip caused 🟢 -> 🟡 demotion (v234)

## Pre-registered thresholds

HARD_PASS (row 🟡 -> 🟢): mean_corr across all seeds at N=1024 >= 0.55 AND
  monotone lambda_2 decrease in >= 3/5 seeds at N=1024.
  Positive correlation confirmed at multi-N multi-seed: spectral connectivity is
  a valid substrate health metric.

HARD_FAIL (sign confirmed negative): mean_corr <= -0.25 at N=1024 AND
  negative sign in >= 4/5 seeds. Anti-correlation confirmed: lambda_2 ANTI-predicts
  retention at multi-seed multi-N scale. Row 🟡 confirmed honestly negative.

MIDDLE_BAND: Inconsistent sign across seeds at N=1024 -- seed-variance dominates.

## Formula self-tests (from script)

1. lambda_2 of zero W = 0
2. lambda_2 >= 0 for loaded sub-capacity W
3. Retention at alpha_B=0: high (no overwrite)
4. Fiedler eigenvector sum near 0
5. run_one_seed returns all required fields, all finite

## Justification

Directly resolves the v234 primary rescue for the spectral-graph row demotion.
The v2/v3 sign-flip is the most significant unresolved sign-conflict in the current
cap_map (a 🟢 row was demoted based on ONE contradicting single-seed result). This
v4 with 3 N-values × 5 seeds provides 15 cells of data to settle the question.
Structural substrate characterization: lambda_2 as basin-geometry proxy.

## Production config

N_VALUES_FULL=[512,1024,2048], SEEDS_FULL=[7,17,23,31,41],
ALPHA_B_VALUES=[0.0,0.05,0.10,0.15,0.20,0.30,0.50], timeout=3600s
