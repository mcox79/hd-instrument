# Prereg: q_c5_cosine_gate_tau_recal_v1

**Date:** 2026-06-02
**Anchor:** q_c5_cosine_gate_tau_recal_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_q_c5_cosine_gate_tau_recal_v1.py

## Scientific question

Q-C5: What is the optimal tau* in [0.78, 0.92] for GDPR-grade deletion-cert non-repudiation?
Specifically: at what tau does FN_rate < 0.05 (cert misses <5% real residual) AND FP_rate < 0.10?

## Pre-registered bands

HARD-PASS:
  Exists tau* in [0.78, 0.92] with FN_rate < 0.05 AND FP_rate < 0.10.

MIDDLE:
  Exists tau* with FN_rate < 0.10 (softer non-repudiation bound).

HARD-FAIL:
  No tau in [0.78, 0.92] achieves FN_rate < 0.20, OR FP_rate > 0.30 at all tau.

## Smoke result (pre-ship gate)

Run: N=4096, M=5 patterns, 2 seeds, tau grid 7 points, 30 trials each.
Result: HARD_PASS. FN=0.000, FP=0.000 at all tau in [0.78, 0.92].
Elapsed=103.3s.

Note: perfect result at smoke scale (M=5 << capacity). FULL uses M=5, 15-point grid,
100 trials/FP/FN, 5 seeds. Perfect FN=0 at smoke may stay at FULL but the tau window
is the load-bearing measurement.

Walk-back: smoke is HARD_PASS with FN=FP=0 (d >> 1). No walk-back needed.

## Timeout estimate

Smoke: 103.3s at N=4096, 2 seeds, 30 trials, 7 tau points, 20 relax steps.
FULL: N=4096, 5 seeds, 100 trials, 15 tau points, 30 relax steps.
scaling_exp = 1.0 (linear in trials * seeds * tau points).
timeout_s = ceil(1.5 * 103.3 * (5/2) * (100/30) * (15/7) * (30/20))
          = ceil(1.5 * 103.3 * 2.5 * 3.33 * 2.14 * 1.5) = ceil(2620) = 2700s.
Rounded to 3600s for headroom.

## N-suffix binding (PROT-018)

No _nN suffix; production N=4096 per rule 3.

## Cap_map connection

Decides GDPR-grade deletion-cert tau recalibration.
Row: verifiable erase (deletion certificate) quality gate.
