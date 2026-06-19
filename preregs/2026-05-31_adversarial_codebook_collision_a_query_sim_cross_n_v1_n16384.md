# Pre-registration: adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384

**Date**: 2026-05-31
**Anchor name**: adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384
**Script**: experiments/exp_adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384.py
**Queue**: overnight_queue (cloud Lambda A10 GPU)
**Total cells**: 15 (3 M-values x 5 seeds)
**PROT-018**: _n16384 suffix binds N = 16384
**Authorization**: user-authorized Lambda batch v2 (commit 2fae636)

## Hypothesis

The a_query_sim defense (cosine similarity threshold >= 0.5 against stored keys)
achieves >= 95% defense rate AND <= 5% false positive rate at N=16384, closing
the single-N caveat on the adversarial-sub-row LIFT from G8_HARD_PASS at N=4096.

## Configuration

- N: 16384 (PROT-018 binding)
- M grid: {4096, 8192, 12288}
- Seeds: [7, 17, 23, 31, 41]
- Attack: codebook-collision pattern (pattern 2, same construction as G8)
- Defense: a_query_sim (threshold=0.5, identical code path to G8)
- n_adv: 32 adversarial queries per cell
- n_leg: 64 legitimate queries per cell

## Pre-registered bands

**HARD-PASS (HP)**:
  defense_rate >= 0.95 AND fp_rate <= 0.05 across ALL 15 cells.
  Interpretation: a_query_sim is robust at N=16384; single-N caveat closed.

**HARD-FAIL (HF)**:
  defense_rate < 0.50 OR fp_rate > 0.20 at ANY single cell.
  Interpretation: defense degrades sharply at 4x scale-up.

**MIDDLE-BAND (MB)**:
  Neither HP nor HF. Some cells pass HP, none fail sharply, OR mixed partial.
  Next step: diagnose which M-value or seed drives the degradation.

## Calibration note

G8_HARD_PASS showed def=1.000 fp=0.000 at N=4096 M=2048. HP band of 0.95/0.05
is slightly narrower than G8's empirical result to allow for N-scaling variance.
This is NOT a calibration-probe (prior empirical anchor exists at N=4096), so
±50% rule does not apply; HP band is informed by G8 result.

## OOM pre-check

N=16384: W matrix = 16384x16384 x float32 = 1.0 GiB.
Codebook at max M=12288 x 16384 = ~0.75 GiB.
Peak memory estimate: ~2 GiB. Under 6 GiB headroom (A10 has 24 GiB).

## Timeout estimate

Smoke: expect ~2-4x G8 smoke time (N scaling ~linear for this experiment).
G8 at N=4096 M=2048 5-seed ran ~3-4 min cloud GPU.
Cross-N at N=16384 3-M x 5-seed = 15 cells: estimate ~15-20 min cloud GPU.
Formula: 1.5 * 240s * (16384/4096)^1.0 * (15/5) = 1.5 * 240 * 4 * 3 = 4320s
Timeout: 5400s (90 min). Well under 14400s gate.

## Strategic value

PASS: adversarial-sub-row LIFT moves 0.45-0.65 -> 0.55-0.75 (cross-N confirmed).
FAIL: single-N characterization only; defense requires re-engineering at scale.

## N-suffix binding

_n16384 suffix: production N = 16384. Confirmed in script: `N_FULL = 16384`.
Smoke runs at N_SMOKE = 1024.
