# Pre-registration: q3_l2_composition_cpu_v1

**Date:** 2026-06-02
**Anchor:** q3_l2_composition_cpu_v1
**Queue:** remote_cpu_queue

## Hypothesis
L=2 pure outer-product heteroassociative chain at N=4096 achieves end-to-end accuracy >= 0.88
at conservative inner load (M=50, alpha=0.012) and M=200 (alpha=0.049).

## Composition classification
HANDOFF: each hop is independent, matches PP-11 Arm B per-hop independence pattern.

## Pre-registered thresholds
- HARD-PASS: e2e_accuracy >= 0.88 at M=50 (conservative load).
- MIDDLE: 0.70 <= accuracy < 0.88.
- HARD-FAIL: accuracy < 0.70.

## Smoke result
N=4096, M=[50, 200], 2 seeds, 100 queries per (M, seed):
- e2e_acc at M=50: 1.0000 (HARD_PASS)
- e2e_acc at M=200: 1.0000
- Smoke wall: 4.9s

Note: perfect accuracy at 2-step recall at these low loads (alpha<<alpha_c). Expected.

## Timeout estimate
Smoke wall: 4.9s / (2 seeds * 2 M) = ~1.2s per cell.
Full: 5 seeds * 3 M = 15 cells * 1.2s = 18s.
wall = 1.5 * 18 = 27s. timeout=300s.
