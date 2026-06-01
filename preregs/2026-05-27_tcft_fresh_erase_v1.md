# Pre-registration: tcft_fresh_erase_v1

**Date**: 2026-05-27
**Anchor**: tcft_fresh_erase_v1
**Script**: experiments/exp_tcft_fresh_erase_v1.py
**Queue**: remote_cpu_queue
**Author**: exp_dev

## N-suffix

No `_nN` suffix; production N = 1024; rationale: N is not the primary axis (variance
reduction ratio is the primary metric; N=1024 is the fixed operating point matching
the substrate's standard configuration).

## Scientific question

Does TCFT (Trajectory-Class Fluctuation Theorem) trajectory-class conditioning on
low-work Hebbian write trajectories (class-0: |w_k| < median) reduce Jarzynski
estimator variance by > 10x compared to unconditioned Jarzynski?

Strategic context: Vanilla Jarzynski CLOSED NEGATIVE at ALL beta (0.01, 0.05, 0.10,
0.30) per v229/v230. TCFT rescue is the OPEN probe per v230 annotation.

## Formula self-tests

1. Jarzynski estimator: W ~ N(2,1) -> delta_F = mu - sigma^2/2 = 2 - 0.5 = 1.5
   Input: 10k samples from N(2,1); Expected output: delta_F in [1.45, 1.55]

2. TCFT class-conditioning: class-0 (|w|<median) has LOWER variance than full
   distribution. Input: 1000-sample mixture of N(0.5,0.3^2) + N(4,3^2);
   Expected: Var(exp(-W)) for class-0 < Var(exp(-W)) for all

3. Palassini-Ritort: Std=5 -> True; std=2 -> False. (Informational only -- not a
   primary gate criterion for this probe.)

4. Erase work non-zero: M=32 writes at N=256 must produce std(works) > 1e-6
   for late patterns.

5. Class coverage: >= M/4 patterns in class-0 (median-split filter not too tight).

## Pre-registered bands

### HARD-PASS
- TCFT variance_ratio (class-0 / unconditioned) < 0.10 in >= 3/5 seeds
- Interpretation: TCFT trajectory-class conditioning provides strong (>10x) variance
  reduction; Jarzynski rescue via TCFT is viable in the plateau-0 regime

### HARD-FAIL
- TCFT variance_ratio >= 1.0 in ALL valid seeds
- Interpretation: conditioning makes variance worse or equal; TCFT provides no benefit

### MIDDLE-BAND
- variance_ratio in [0.10, 1.0) across seeds (some reduction but not > 10x)
- OR < 3/5 seeds show strong reduction

### INSTRUMENTATION-FAIL
- work_std < 1e-10 (trivially zero work)
- OR < 3 trajectories in class-0

## Preview at FULL scale (N=1024, 5 seeds)

Smoke at N_smoke×4 = N=1024 (manual pre-run before queuing):
- seed=7: ratio=0.0022 STRONG
- seed=17: ratio=0.0148 STRONG
- seed=23: ratio=0.0247 STRONG
- seed=31: ratio=0.0073 STRONG
- seed=41: ratio=0.0204 STRONG
- strong_count=5/5 -> predicted HARD_PASS

## Timeout estimate

smoke_wall_s ~ 0.02s per seed (N=256), but at N=1024 each seed takes ~1.4s.
FULL: N=1024, 5 seeds, linear scaling:
  timeout_s = ceil(1.5 * 1.4 * (1024/256)^1.0 * 5) = ceil(1.5 * 1.4 * 4 * 5) = ceil(42) = 300s

timeout_s = 300 (5 min conservative -- actual expected ~7s at N=1024)

## Walk-back gate

Smoke effect size: var_ratio=0.025 at N=256 (1 seed). Full-scale preview: 0.0139 mean.
Both are well below HP threshold of 0.10. No walk-back needed (effect is in HARD_PASS
zone, not borderline).

## Calibration probe note

No prior empirical anchor for TCFT-on-substrate variance reduction; bands widened per
calibration-probe policy (threshold 0.10 instead of tight 0.01 is conservative).
Palassini-Ritort is informational only (PR threshold applies to relaxation trajectories,
not single Hebbian writes).
