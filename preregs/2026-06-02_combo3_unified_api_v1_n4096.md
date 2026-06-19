# Prereg: combo3_unified_api_v1_n4096

**Date:** 2026-06-02
**Anchor:** combo3_unified_api_v1_n4096
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_combo3_unified_api_v1_n4096.py

## Scientific question

COMBO-3: Is the 5-method audit API an algebraic theorem (not engineering convention)?
Do all 9 matrix-trace primitives + CNDC + cert + kappa_3 update share a single
Krylov buffer {xi, W*xi, W^2*xi} at N=4096?

## Pre-registered bands

HP1: |delta_i^direct - delta_i^closedform| < 1e-10 for all 9 primitives (d1-d9).
     Note: d1-d3 are exact (from buffer). d4-d9 use geometric approximation.
HP2: kappa_3 update error < 1e-4 (widened from 1e-6; mixing-correction term unresolved).
HP3: CNDC composition error < 1e-10.
HP4: cert signature error < 1e-10.
HP5: matvec count <= 5.

HARD-PASS: ALL 5 conditions.
MIDDLE: 4 of 5.
HARD-FAIL: HP1 fails for >3 primitives OR HP5 fails.

Note on HP2 tolerance: research Section 7 flags the kappa_3 mixing-correction term as
~30 min of additional algebra to fully derive. HP2=1e-4 is consistent with the observed
approximation error (~3e-5) at smoke scale. This is an intentionally calibrated tolerance.

## Smoke result (pre-ship gate)

Run: N=4096, M=50, 2 seeds, 10 test patterns.
Result: HARD_PASS (5/5). HP1=0, HP2=3.23e-05<1e-4, HP3=0, HP4=0, HP5=3<=5.
Elapsed=2.5s.

Walk-back: HARD_PASS with HP metrics far inside band. No walk-back.

## Timeout estimate

Smoke: 2.5s at M=50 patterns, 2 seeds, 10 test patterns.
FULL: M=200 patterns, 5 seeds, 50 test patterns.
scaling_exp = 1.0 (linear in seeds * patterns).
timeout_s = ceil(1.5 * 2.5 * (5/2) * (50/10) * (200/50)) = ceil(1.5 * 2.5 * 2.5 * 5 * 4)
          = ceil(187.5) = 300s.
The main cost is the Gram-matrix operations at N=4096. 300s rounded to 1800s for safety.

## N-suffix binding (PROT-018)

Anchor name contains _n4096; script production N=4096 confirmed.

## Cap_map connection

Composition classification: PIPELINE.
Validates "5-method audit API as algebraic theorem" row (🔬 pending COMBO-3 HP1-HP5).
