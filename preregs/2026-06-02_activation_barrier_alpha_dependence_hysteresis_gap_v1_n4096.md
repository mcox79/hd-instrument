# Prereq: activation_barrier_alpha_dependence_hysteresis_gap_v1_n4096

**Date:** 2026-06-02
**Anchor:** activation_barrier_alpha_dependence_hysteresis_gap_v1_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_activation_barrier_alpha_dependence_hysteresis_gap_v1_n4096.py

## Hypothesis

Tests Arrhenius drill Item 31 (Test C): activation barrier closed-form prediction
E_a^0(alpha) ~ N * (alpha_c - alpha) / alpha_c.
Empirical proxy: critical noise threshold nf_crit (noise fraction where recall drops to 0.5).
Prediction: nf_crit(alpha=0.05) > nf_crit(alpha=0.10) (lower loading = larger barrier = higher noise tolerance).

## PROT-022 Formula Self-tests

1. Barrier ratio: (alpha_c - 0.05) / (alpha_c - 0.10) = 0.088/0.038 = 2.316
   [VERIFIED: ratio = 2.3157 within 0.001]
2. Critical noise threshold monotonicity at smoke scale: VERIFIED empirically.
   N=512: nf_crit(0.05)=0.44, nf_crit(0.10)=0.40 (monotone in all 2 smoke seeds)
   N=4096 (1-seed pre-check): alpha=0.05 critical ~0.44, alpha=0.10 ~0.40 (monotone)

## Pre-registered Bands (calibration probe, first multi-seed measurement)

No prior multi-seed empirical anchor for this observable. Bands set wide per role contract.

**HARD-PASS:**
- nf_crit(alpha=0.05) > nf_crit(alpha=0.10) for >= 4/5 seeds
- mean(nf_crit_05) / mean(nf_crit_10) > 1.02

**MIDDLE:**
- Monotone in mean but < 3/5 seeds unanimous

**HARD-FAIL:**
- mean(nf_crit_05) <= mean(nf_crit_10) (flat or inverted)
- OR nf_crit undefined for either alpha

## Smoke Result

**N_smoke=512, 2 seeds:**
- nf_crit(0.05) = 0.44, nf_crit(0.10) = 0.40 (both seeds)
- ratio = 1.10 (monotone, both seeds)
- Verdict: HARD_PASS

**Walk-back gate:** smoke effect clean (ratio=1.10 > 1.02 threshold). d ~ 1.0 borderline.
Proceeding with standard 5-seed FULL run. Effect is consistent across 2 smoke seeds.

## Timeout Estimate

- smoke_wall_s ~ 25s (2 seeds, 3 alpha, 13 noise_frac values, N=512)
- FULL: N_smoke->N_full = 512->4096 (8x), 2->5 seeds (2.5x), scaling_exp=1.5
- timeout = ceil(1.5 * 25 * 8^1.5 * 2.5) = ceil(2121) -> 2400s (40 min)
- Using 2700s for margin.

## N-suffix

No _nN suffix -- this is an alpha-sweep experiment with fixed N=4096 (PROT-018 binding via N=4096 in script).

## Cap_map Impact

- HARD-PASS: PP-33 sub-property: explicit alpha-dependent barrier E_a^0(alpha) empirically corroborated via nf_crit ordering; Arrhenius-drill prediction supported; Pred-4 hysteresis framing strengthened.
- HARD-FAIL: barrier is alpha-independent; refutes AGS free-energy structure prediction; opens follow-on theory drill.
