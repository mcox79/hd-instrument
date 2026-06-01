# Prereg: bursty_write_stepdown_v1

**Filed:** 2026-06-01
**Anchor:** bursty_write_stepdown_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_bursty_write_stepdown_v1.py

## Hypothesis

After burst of B=100 patterns onto steady-state M=500, overlap drops within 2x
theory and stays flat for 1000 read-only steps (no recovery). Theory: closed-form
prediction Deltam ~ (B/N)*phi(1/sqrt(alpha_0))/alpha_0^(3/2) and no-recovery theorem.

## Pre-registered bands

- HARD-PASS: drop < 2x theory AND m flat at step 1000 (|recovery| < 0.005).
- MIDDLE: drop 2-5x theory OR small recovery (0.005-0.020).
- HARD-FAIL: drop > 5x theory OR recovery > 0.020 (spontaneous recovery contradicts no-recovery theorem).

## Design

N=2048, M_steady=500 (alpha=0.244), B=100. 1000 read-only steps. 5 seeds.

## Timeout estimate

~8s total. timeout_s = 300 (floor).

## N-suffix note

No _nN suffix. Production N = 2048; burst-tolerance at M/N=0.244.
