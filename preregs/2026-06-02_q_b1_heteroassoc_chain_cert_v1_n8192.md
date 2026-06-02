# Prereg: q_b1_heteroassoc_chain_cert_v1_n8192

**Date:** 2026-06-02
**Anchor:** q_b1_heteroassoc_chain_cert_v1_n8192
**Queue:** overnight_queue (GPU)
**Script:** experiments/exp_q_b1_heteroassoc_chain_cert_v1_n8192.py

## Scientific question

Q-B1 at N=8192: Same as N=4096 but at production-N envelope.
Does depth-3 heteroassoc chain + deletion cert hold at N=8192?

## Pre-registered bands

Same as N=4096 version:
HARD-PASS: depth1 >= 0.90, depth3 >= 0.80, deletion_sim <= 0.50.
MIDDLE: depth1 >= 0.90, depth3 in [0.60, 0.80).
HARD-FAIL: depth3 < 0.60.

## Smoke result (pre-ship gate)

Run: N=8192, 5 chains, M_bg=10, 2 seeds, 10 trials.
Result: HARD_PASS. depth1=0.999, depth3=0.998, deletion_sim=0.004.
Elapsed=58.4s. (Higher elapsed due to N=8192 matrix operations.)

Walk-back: far above HP thresholds. No walk-back.

## Timeout estimate

Smoke: 58.4s at N=8192, 5 chains, 2 seeds, 10 trials, M_bg=10.
FULL: N=8192, 15 chains, 5 seeds, 50 trials, M_bg=30.
scaling_exp = 1.5 (matrix operations scale super-linearly with N for heteroassoc builds).
timeout_s = ceil(1.5 * 58.4 * (5/2) * (15/5) * (50/10)) = ceil(1.5 * 58.4 * 2.5 * 3 * 5)
          = ceil(3285) = 3600s. Flagged as >2h potential run - 3600s should cover it.

## N-suffix binding (PROT-018)

Anchor name contains _n8192; script production N=8192 confirmed.

## Cap_map connection

Production-N envelope for heteroassociative chain + deletion cert.
Extends Q-B1 from N=4096 to N=8192.
