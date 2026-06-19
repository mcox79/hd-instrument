# Pre-registration: multiagent_coord_competing_v1

**Date:** 2026-06-02
**Anchor:** multiagent_coord_competing_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_multiagent_coord_competing_v1.py

## Scientific question (9-Handoff: multi-agent competing writes)
When Team A writes N_A=4 times and Team B writes N_B=1 time into a shared Hopfield W
near 71% capacity, does write frequency determine retrieval priority?
Prediction: Team A patterns retrieve more accurately than Team B patterns (delta >= 0.15).
Minority coalition (Team B) retains usable recall (acc >= 0.50).

## Pre-registered thresholds
- HARD-PASS: delta_majority >= 0.15 AND minority_acc >= 0.50 (write-count determines priority; minority retains recall)
- MIDDLE: delta_majority in [0.05, 0.15) OR minority_acc in [0.30, 0.50)
- HARD-FAIL: delta_majority < 0.05 (no write-count effect at near-capacity)

## Calibration note
Requires near-capacity load (71% of alpha_c) to show competition effects.
M_PAT = int(0.35 * ALPHA_C * N) = ~197 at N=4096 FULL. Walk-back borderline
(smoke delta=0.158, within 5% of HP=0.15) but not applied as seeds are already 5.

## Smoke result
HARD_PASS: delta_majority=0.158, minority_acc=0.827 (smoke N=1024, M_PAT=49, 2 seeds)
