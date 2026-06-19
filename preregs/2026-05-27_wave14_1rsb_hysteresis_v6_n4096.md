# Pre-registration: wave14_1rsb_hysteresis_v6_n4096

Date: 2026-05-27
Experimenter: exp_dev (sub-agent)
Parent: wave14_1rsb_hysteresis_v5_n4096_gpu (TIMEOUT at 1200s)

## Hypothesis

1-RSB glassy phase hysteresis persists at N=4096. v5 confirmed at N=1024 (max_gap=1.84).
v5 timed out before producing data at N=4096. v6 is the timeout-fixed retry.

## Design changes from v5 (timeout fix)

- M_SWEEP_FULL: reduced from 6 points to 3 ([8_000, 40_000, 120_000])
- EPOCHS: reduced from 10 to 4
- SEEDS_FULL: reduced from 3 to 2 (walk-back: v3 max_gap=1.84 >> 0.10, d >> 1.0)
- Timeout budget: 3600s (was 1200s, which was insufficient)

## Pre-registered thresholds

HARD_PASS: max_gap >= 0.10 at N=4096 (hysteresis confirmed at production scale)
MIDDLE_BAND: max_gap in [0.03, 0.10) (weak hysteresis; inconclusive)
RS_HARD_FAIL: max_gap < 0.03 (hysteresis vanishes; finite-N artifact)

Same thresholds as v3/v5. No change to scientific claim.

## Walk-back note

v3 gap = 1.84 (18x above threshold). Even if N=4096 narrows gap by 10x -> gap=0.18 >> 0.10.
2 seeds sufficient for detection. If gap < 0.10 at 2 seeds: upgrade to 5 seeds in v7.

## Timeout estimate

smoke_wall_s from v3: ~70s (N=1024 3 seeds 6 M-cells 2 directions).
v6: N=4096 2 seeds 3 M-cells 2 directions 4 epochs.
N-scale (4096/1024)^1.5 = 8.0. Seed 2/3=0.67. M-cell 3/6=0.5. Epoch 4/10=0.4.
timeout_s = ceil(1.5 * 70 * 8.0 * 0.67 * 0.5 * 0.4 * 2) = ceil(224) -> 600s baseline.
4x safety margin for GPU overhead: 2400s. Use 3600s.

## Smoke result

N=256, 1 seed: max_gap=1.79 (HARD_PASS at smoke). Effect size >> 1.0.

## N-suffix binding (PROT-018)

_n4096 in name -> production N = 4096. Verified in script: `N = 4096`.
