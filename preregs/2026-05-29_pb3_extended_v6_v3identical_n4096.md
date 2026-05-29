# Pre-registration: pb3_extended_v6_v3identical_n4096

**Date:** 2026-05-29
**Anchor:** pb3_extended_v6_v3identical_n4096
**Script:** experiments/exp_pb3_extended_v6_v3identical_n4096.py
**Queue:** overnight_queue
**Trigger:** PB-3 2nd-strike rehabilitation gate R2 (cheapest rescue arm)

## Hypothesis
Re-running PB-3 at the exact v3 config (N=4096, same seeds, same betas, same BSC codebook)
will reproduce v3's positive result (ratio=1.64) IF the v4/v5 failures are an N-extension
regime issue. If v6 also shows flat tau_recovery, v3 was an artifact.

## Config
- N_FULL = 4096 (PROT-018: _n4096 suffix binding; matches v3.N = 4096)
- Seeds: [7, 17, 23, 31, 41] (v3-identical)
- Beta sweep: [2, 4, 6, 8, 10, 12, 16] (v3-identical)
- v3-identical: all hyperparameters match v3 exactly

## N-suffix
_n4096 suffix; production N = 4096. PROT-018 satisfied.

## Pre-registered bands
NOT an envelope expansion (re-test of v3 config). Bands NOT widened.
Prior anchor: v3 ratio=1.64, tau_recovery > 0 at {2,4,6,8,10,12,16}.
- HARD_PASS: ratio >= 1.5 AND tau_peak_beta in {6,8,10}.
- HARD_FAIL: tau_recovery < 0.1 at ALL seeds at ALL betas (flat; v3 was artifact).
- MIDDLE_BAND: ratio in [1.0, 1.5) or partial tau signal.

## Timeout estimate
v3 elapsed: ~10800s (3h). v6 is identical config. PROT-019 floor for _n4096 = 14400s.
timeout_s = 14400.

## Smoke result
SELFTEST PASS. tau_ratio=1.0 at smoke scale (1 seed, 2 betas, N=1024) -- expected at smoke.
Non-null metrics. Ship allowed.

## Downstream cap_map move
- HARD_PASS: R2 passes -> proceed to R1 intermediate-N; PB-3 row stays open
- HARD_FAIL: PB-3 critical-slowing 3rd-strike CLOSURE candidate
- MIDDLE_BAND: weaker-than-v3 reproduction; annotation update
