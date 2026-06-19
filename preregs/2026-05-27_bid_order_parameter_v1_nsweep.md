# Pre-registration: BID Order-Parameter N-Sweep (HP3 Stability Gate) v1

**Date:** 2026-05-27
**Anchor name:** bid_order_parameter_v1_nsweep
**Script:** experiments/exp_bid_order_parameter_v1.py (with --n-sweep flag)
**Queue:** remote_cpu_queue
**Filed by:** exp_dev
**Parent anchor:** bid_order_parameter_v1

---

## Hypothesis (HP3 gate)

HP3: BID is a true thermodynamic quantity, not a finite-N artifact.
Criterion: BID stable within +/- 5% across N in {1024, 2048, 4096}.
If stable: the HP1/HP2 claim from bid_order_parameter_v1 is defensible at scale.
If unstable (>= 20% drift): HF2 -- BID is finite-N noise; no novel-class claim.

This is the "stretch #4" anchor from the BID handoff.

---

## Pre-registered bands

Same reference bands as bid_order_parameter_v1 (N-dependent; see that prereg).

HP3 PASS: max_drift_frac <= 0.05 across N in {1024, 2048, 4096}.
HF2 FAIL: max_drift_frac >= 0.20.
MIDDLE-BAND: 0.05 < max_drift_frac < 0.20.

---

## Calibration note

No prior empirical anchor for BID stability. Bands set per calibration-probe policy:
PASS criterion = 5% (conservative stability requirement for thermodynamic claim).
FAIL criterion = 20% (clear instability).
These are not tight bands -- appropriate for a first measurement.

---

## Smoke results

Smoke (N=256 and N=512, 1 seed):
  N=256: BID=29.19
  N=512: BID=26.86
  Observed drift = |29.19 - 26.86| / 29.19 = 0.080 (8% -- borderline)

Walk-back gate: drift at smoke scale (8%) is above the HP3 pass threshold (5%)
but below the HF2 fail threshold (20%). This makes the full N-sweep critical
to determine if drift is a finite-S artifact (more seeds reduce noise) or real.
Per walk-back policy: FULL sample size is already the designed 5 seeds -- no doubling
needed as this anchor is testing scale not power.

---

## Timeout estimate

Local N-sweep timing (N=1024,2048,4096 x 5 seeds): ~11s
Remote CPU overhead: 10x
timeout_s = ceil(1.5 * 11 * 10) = ceil(165) = 300s

Final timeout_s: 300s
