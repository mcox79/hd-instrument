# Prereg: pp12_capacity_ondemand_w_v1_n16384

**Date:** 2026-06-04
**Anchor:** pp12_capacity_ondemand_w_v1_n16384
**PROT-018:** _n16384 suffix; production N = 16384.
**PROT-021:** seed checkpoints keyed with run_mode + N.

## Context

PP-12 Q-A3 depth ladder tests COMPOSITIONAL depth at M=2 patterns/layer.
This test probes CAPACITY: maximum M at N=16384 with on-demand W build.
On-demand W = Xi.T @ Xi / N, built per-query, never persisted.
Theoretical capacity: M_crit ~ alpha_c * N = 0.138 * 16384 = 2261 patterns.
Alpha sweep: {0.02, 0.05, 0.08, 0.10, 0.12, 0.138, 0.15, 0.18, 0.20}.

## Pre-registered bands

No prior alpha-sweep at N=16384 (Q-A3 uses alpha=0.0061 only). Calibration probe.
Bands +-50% of theoretical onset alpha_c=0.138 per calibration-probe policy.

- HARD-PASS: recall >= 0.97 at alpha <= 0.10 unanimously (5/5 seeds) AND
             degradation onset (recall < 0.97) in alpha [0.08, 0.20].
- MIDDLE: recall >= 0.85 at alpha <= 0.10 but onset not cleanly identified.
- HARD-FAIL: recall < 0.85 at alpha <= 0.05 (capacity << theoretical prediction)
             OR recall > 0.97 at alpha=0.20 (no degradation even at 1.45*alpha_c).

## Formula self-tests (PROT-022)

1. M_crit = int(0.138 * 16384) = 2261. [EXPECTED: 2261]
2. W on-demand at N=16384: 16384^2 * 4 bytes < 2GB. [EXPECTED: True]
3. Alpha sweep [0.02..0.20] strictly increasing. [EXPECTED: True]
4. Recall at alpha=0.02 non-NaN and > 0. [EXPECTED: True]
5. GPU memory > 0 after W build.

## Multi-scale smoke

alpha is load-bearing; smoke at N=512 and N=2048.

## Timeout estimate

9 alpha * 1.5s/alpha * 5 seeds = 67.5s. ceil(1.5 * 68) = 102s.
Use PROT-019 floor: 21600.
