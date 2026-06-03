# Prereg: PP-50 kappa_3 delta-alpha N=32768 v3

**Anchor:** pp50_kappa3_delta_alpha_n32768_v3_n32768
**Date:** 2026-06-03
**Queue:** overnight_queue (GPU)

## Hypothesis

The kappa_3 delta-alpha sensitivity at N=32768 (v3 protocol) will confirm the same HP thresholds
as N=16384 v347 (sigma_sep(d=0.04)=642, d=0.01=186, d=0.001=19.3). N^(2/3) scaling should give
~1019 at d=0.04. This is the definitive N=32768 cross-N gate using the same v3 protocol.

## Context

N=65536 failed OOM (~17 GB W matrix on 8 GB display adapter). N=32768 peak VRAM ~1.26 GB
(fits with 6.7 GB margin). v335 N=32768 founding used a different protocol; sigma_sep(d=0.001)
was only 2.55 (below old HP=3.0). This run uses the full v3 protocol (d=0.04, d=0.01, d=0.001).

## Pre-registered thresholds

HARD-PASS: sigma_sep(d=0.04) >= 100 AND sigma_sep(d=0.01) >= 10 AND sigma_sep(d=0.001) >= 3.0
  Rationale: N^(2/3) extrapolation gives ~1019 at d=0.04; HP=100 is ~10% of extrapolation.
  d=0.001 HP=3.0 reflects v335 miss with more probes fix. Conservative and fair.

MIDDLE: sigma_sep(d=0.04) in [50, 100) OR sigma_sep(d=0.01) in [5, 10)
  Interpretation: scaling plateau at N=32768; route to further analysis.

HARD-FAIL: sigma_sep(d=0.04) < 50 OR sigma_sep(d=0.01) < 5
  Interpretation: unexpected N-scaling reversal; requires investigation.

## Calibration note

Prior empirical anchor EXISTS at N=32768 (v335 founding). HP thresholds set at ~10% of
N^(2/3) extrapolation to be generous toward protocol differences. Not a blind calibration probe.

## Config

N = 32768 (PROT-018 binding)
ALPHA_BASE = 0.05
DELTA_ALPHAS = [0.04, 0.01, 0.001]
SEEDS = [7, 17, 23, 31, 41] (5 seeds)
N_PROBES_SENS = 2000

## N-suffix section

Anchor name `_n32768` binds production N=32768. Script line: `N = 32768`.

## PROT-021 compliance

Seed checkpoints keyed with run_mode + N + alpha_base. Smoke runs at N=4096
will not contaminate FULL N=32768 checkpoint keys.

## Timeout estimate

```
smoke_wall_s = 72  (estimated from N^2 scaling: 45s * 4x * 0.4x = 72s/seed)
FULL_N / smoke_N = 32768 / 4096 = 8 (but smoke uses N_ACTIVE=4096, N_PROBES=200)
FULL uses N_ACTIVE=32768, N_PROBES=2000; actual scaling baked in per-seed estimate.
Per-seed FULL estimate = 72s. 5 seeds = 360s.
timeout_s = ceil(1.5 * 360 / 300) * 300 = ceil(1.8) * 300 = 600s
```

timeout_s = 600 (10 minutes; well within 4h limit).

## OOM pre-check

N=32768: Xi = 1638 * 32768 * 4 = 215 MB; V = 32768 * 2000 * 4 = 262 MB per V.
Peak estimate: Xi + 4*V = 0.215 + 1.048 = 1.26 GB / 8 GB total. SAFE.
N=65536 estimated 6.1+ GB (tight) and actually failed at ~17 GB (W matrix allocation in runner
environment). N=32768 is 1/4 the N=65536 cost.

## Formula self-tests (PROT-022)

1. N^(2/3) scaling: 642 * (32768/16384)^(2/3) = 642 * 2^(2/3) = 642 * 1.587 = 1018.9 >> 100
   [INPUT: sigma_n16384=642, N_ratio=2.0] [EXPECTED: ~1019 > 100]
2. M = int(0.05 * 32768) = 1638. [EXPECTED: 1638]
3. Xi VRAM: 1638 * 32768 * 4 = 214,794,240 bytes = 215 MB < 1 GB. [EXPECTED: < 1e9]

## Outcome map

HARD_PASS -> PP-50 N=32768 v3 protocol confirmed; CLOUD auth request filed for N=65536+
MIDDLE_BAND -> investigate probe variance; possible N=32768 scaling plateau
HARD_FAIL -> unexpected reversal; route to research for mechanism investigation

## Cloud routing note

N=65536+ kappa3 delta-alpha protocol requires dedicated headless GPU (no display adapter
VRAM competition). Estimated N=65536 OOM threshold: ~17 GB > 8 GB display GPU.
Recommend Lambda A10 (24 GB VRAM) or A100 (40/80 GB) for N=65536 follow-up.
