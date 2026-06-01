# Pre-registration: aging_exponent_mu_v1

**Date:** 2026-06-01
**Anchor:** aging_exponent_mu_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_aging_exponent_mu_v1.py
**Cap_map row:** PP-33 aging-class sub-row

## Scientific question
Q19: Does the substrate's C(t, t_w) trajectory yield fitted mu distinguishable from
mu=0 (simple aging) and mu=1 (no aging)?

## Pre-registered bands
- HARD-PASS: mu in (0,1) for all 5 seeds AND bootstrap CI width < 0.10 AND
             mean_mu > 2*sigma from both 0 and 1 (distinguishable from both bounds).
- MIDDLE: mu in [0,1] but CI width >= 0.10 OR seeds disagree (>= 1 seed outside (0,1)).
- HARD-FAIL: mu undefined or out of [0,1] for >= 3 seeds.

## Design
- N=4096, M=200 (alpha=0.049)
- t_w grid FULL: {50, 100, 200}; SMOKE: {50, 100}
- delta_t FULL: {1, 2, 5, 10, 20, 50, 100, 200}; SMOKE: {1, 2, 5, 10, 20}
- Fit: C = A * exp(-(delta_t/tau)^(1-mu)) via scipy curve_fit
- 100-resample bootstrap for CI
- 5 seeds

## Formula self-tests
1. C(t_w, t_w) = 1.0 (self-overlap).
2. Stretched-exp: mu=0 -> plain exp(-t/tau). mu=1 -> const. mu in (0,1) -> intermediate.

## Timeout estimate
smoke_wall_s=4.2s, FULL: ceil(1.5 * 4.2 * (3/2 t_w) * (8/5 delta_t) * (5/2 seeds))
= ceil(1.5 * 4.2 * 1.5 * 1.6 * 2.5) = ceil(37.8) = 38 -> 300. timeout=900 (ceiling for dynamics).

## N-suffix note
No _nN suffix. Production N=4096 per PROT-018 rule 3.

## Smoke result
run_mode=smoke, verdict=MIDDLE_BAND mean_mu=0.2564, elapsed=4.2s. Metrics non-null. PASS gate.
mu=0.26 at smoke is in (0,1) -- promising signal that mu is distinguishable at full scale.
