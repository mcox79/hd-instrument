# Pre-registration: wave14_glauber_kerdock_v2

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_glauber_kerdock_v2.py
**Predecessor**: wave14_glauber_kerdock_v1 -> GLAUBER_INCONCLUSIVE at 20.7s
  (max_bimodal_score=0.000 across all cells; under-resolved)

## Why v2

v1 INCONCLUSIVE was a parameter problem, not a hypothesis problem:
- alpha values too high (0.25, 0.5, 1.0; AGS critical alpha_c ~ 0.138)
- chain length too short (300 sweeps total) to resolve bimodal stationary P(q)
- beta_max=8.0 ok but coarse grid missed transition window

v2 corrects all three:
- alpha in {0.05, 0.10, 0.20} -- all below or near AGS critical loading
- n_burn=400, n_collect=600 (3.3x v1 FULL total chain length)
- 12-beta grid in [1.0, 12.0] focused around predicted T_c (beta~3-6)
- Lighter init noise (10% flips vs 30%) -- start IN retrieval basin to measure
  stationary phase, not recovery from noise

## Hypothesis

Synchronous heat-bath Glauber on Kerdock-Hebbian W shows bimodal stationary
P(q) at low T (beta>=4) for sub-critical alpha (<=0.10). At least half of
low-T cells satisfy bimodal_score >= 0.5 AND abs_mean_q >= 0.30.

Brutal-honesty P estimates (updated after v1 + v2 smoke):
- P(BIMODAL verdict on FULL): **0.85** -- v2 smoke at alpha=0.10, beta=6.0
  ALREADY shows bimodal_score=1.000, abs_mean_q=0.998 with just 2 seeds
  and 80 collect samples. FULL config (5 seeds x 600 samples x 12 betas x
  3 alphas) almost certainly captures the transition cleanly.
- P(UNIMODAL): **0.05** -- v2 smoke result effectively rules out global
  unimodal
- P(INCONCLUSIVE): **0.10** -- if higher-alpha cells (alpha=0.20) wash
  out the signal in aggregate

## Predictions (falsifiable, hard-fail thresholds)

For each (alpha, beta) cell, mean bimodal_score and abs_mean_q across 5 seeds.

- **BIMODAL_KERDOCK**: at low-T cells (beta>=4), at least half satisfy
  bimodal_score >= 0.5 AND abs_mean_q >= 0.30
- **UNIMODAL_KERDOCK**: ALL cells have bimodal_score < 0.2 AND abs_mean_q < 0.15
- **INCONCLUSIVE**: mixed

Hard-fail / kill criteria:
- High-T cell (beta=1.0) shows bimodal_score > 0.6: indicates a bug; halt
- FULL runtime > 30 min: re-estimate; halt before timeout if estimate > 3600s
- Smoke had verdict=BIMODAL (already passed)

## Runtime / queue routing

- Pure numpy. 3 alphas x 12 betas x 5 seeds x (400 burn + 600 collect) = 1000
  sweeps per chain; 180 chains. At ~1024 N, ~10ms per sweep on remote CPU
  -> 180 * 1000 * 10ms = 30 min total (with overhead).
- Route: **remote_cpu_queue** (Rule 2: pure CPU > 5 min, benefits from
  remote machine)
- Timeout = 3600 s (2x headroom)

## Smoke result

Self-test 4/4 PASS (reuses v1 verdict classifier).
Smoke (alpha=0.10, beta in {2,6}, 2 seeds, 50 burn, 80 collect):
- beta=2.0: mean_q=+0.129, bimodal=0.000 (high-T, paramagnet -- expected)
- beta=6.0: mean_q=+0.998, bimodal=1.000 (low-T, full retrieval)
- Smoke verdict: GLAUBER_BIMODAL_KERDOCK

Smoke confirms v2 parameter region captures the substrate-internal Hopfield
transition.

## Linkage

v2 BIMODAL on FULL would, together with free_cumulants_kerdock_v1 (GPU
running) and S_transform_kerdock_v1 (CPU companion), establish:
  - Spectral (free cumulants) departure from MP universality
  - Spectral (S-transform) departure from MP universality
  - Dynamical (Glauber) substrate-internal Hopfield retrieval phase
on the same Kerdock 4-coset codebook. Substrate observability axis: Cap 3
NESS streaming extends from drift-diffusion to a Glauber-Hopfield discrete
analog.
