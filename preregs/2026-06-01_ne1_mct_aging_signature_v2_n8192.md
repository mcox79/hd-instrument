# Pre-registration: ne1_mct_aging_signature_v2_n8192

**Date:** 2026-06-01
**Anchor:** ne1_mct_aging_signature_v2_n8192
**Queue:** remote_cpu_queue
**Script:** experiments/exp_ne1_mct_aging_signature_v2_n8192.py
**Motivation:** v1 (N=1024) MIDDLE_BAND -- finite-size effects smeared C(t,t_w) ~ f(t/t_w) scaling.
v2 runs at N=8192 (4x) with wider trajectory grid to resolve aging signature.

---

## Hypothesis

At load alpha >= alpha_c (above the Hopfield retrieval cliff, alpha_c ~ 0.138), the substrate
exhibits aging phenomenology: the two-time correlator C(t,t_w) depends on t and t_w only through
the ratio t/t_w (aging scaling). Below alpha_c, dynamics equilibrate and no aging is present.
This is the MCT signature from Nanomagnetic Hopfield Network (arXiv:2202.02372, Nature Physics 2022).

Finite-size prediction: the t/t_w collapse sharpens as N increases because larger N reduces
fluctuations and sharpens the phase boundary. N=8192 (vs N=1024 in v1) should resolve the signal.

---

## Design

- N = 8192 (PROT-018 binding -- anchor name suffix)
- alpha_grid = [0.05, 0.10, 0.14] (below, near, above alpha_c=0.138)
- t_w grid = [20, 50, 100, 200] (waiting times; extended from v1 [10, 20, 40])
- dt grid = [10, 25, 50, 100, 200, 400] (observation intervals; extended from v1 [5, 10, 20, 40, 80])
- 5 seeds, 5 trials per (seed, alpha)
- Vectorized (parallel-update) stochastic Glauber update; high beta=20 (effectively deterministic)
- Efficient chain: one trajectory per trial; snapshot at t_w checkpoints; run dt more from each

Smoke: N=1024, 2 seeds, 3 trials -- gate only (HP threshold not applied to smoke)

---

## Pre-registered thresholds

### HARD-PASS
At alpha = 0.14 (above alpha_c):
- |Pearson r(log(t/t_w), C(t,t_w))| >= 0.70 in >= 4/5 seeds
  (negative correlation expected: C decreases with t/t_w = aging signature)
- Collapse score >= 2.0 (t/t_w explains more variance than raw t)
Both criteria must be met. Seeds are counted over 5 total.

### HARD-FAIL
- |r| < 0.30 above alpha_c in ALL 5 seeds: aging absent at N=8192 (framework REFUTED)

### MIDDLE_BAND
- Some seeds pass above alpha_c but < 4/5
- OR collapse score 1.5-2.0 (weak aging, inconclusive)
- OR no clear contrast between above/below alpha_c
- Outcome plan: if MIDDLE_BAND, surface to Strategy for PP-33 frame re-evaluation;
  possible rescue paths: (a) N=16384, (b) longer trajectory t_w_max=500/dt_max=1000,
  (c) different initial condition (deep quench from random state rather than noisy pattern)

---

## Calibration context

No prior empirical anchor at N=8192 for aging in binary Hopfield substrate. Bands set at
+-50% of theoretical prediction per calibration-probe policy:
- Theoretical: |r| expected ~0.85-0.95 at large N (from MCT prediction of full t/t_w collapse)
- HP threshold 0.70 = 0.85 * 0.82 (within 50% range)
- HF threshold 0.30 = 0.85 * 0.35 (within 50% range)

v1 result (N=1024): seed=7 showed |r|=0.838/collapse=164 but seed=17 showed |r|=0.006/collapse=0.
At N=8192 the fluctuations should reduce and the signal should be more consistent across seeds.

---

## N-suffix section

PROT-018: anchor name `_n8192` requires production N=8192. Confirmed: `N = 8192` at line ~57.
Smoke uses N_SMOKE=1024 (smaller; allowed per PROT-018 rule 1).

---

## Timeout estimate

- Vectorized Glauber step at N=8192: ~30ms (measured locally)
- Full run: 5 seeds * 3 alphas * 5 trials * (200+400 steps) = 45000 steps
- Wall estimate: 45000 * 0.030s = 1350s + overhead = ~1400s
- Formula: ceil(1.5 * smoke_wall * N_ratio^1.5 * seed_ratio)
  = ceil(1.5 * 5.7s * (8)^1.5 * 2.5) = ceil(1.5 * 5.7 * 22.6 * 2.5) = ceil(483s)
  (direct timing is more accurate; use direct estimate 1400s)
- timeout_s = 21600 (PROT-019 floor for _n8192 anchors; actual estimated wall ~1400s;
  floor applies as a conservative safety margin for unexpected overhead)
- Under the blocking threshold; long-run note: actual wall expected ~1400s, well under 6h.

---

## Walk-back note

Smoke (N=1024, 2 seeds): 1/2 seeds showed strong aging (pearson_r=-0.838), 1/2 showed none.
Effect size at smoke is borderline. FULL run at N=8192 with 5 seeds is the correct resolution
(rather than doubling N further to N=16384 which is beyond PP-33 spec scope). The borderline
smoke is consistent with expected N=1024 finite-size effects that v2 is designed to resolve.
