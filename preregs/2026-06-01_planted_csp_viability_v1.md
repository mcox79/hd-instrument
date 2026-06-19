# Prereq: planted_csp_viability_v1

## Scientific question
Planted MAX-CUT, 3-SAT, clique viability via substrate Hopfield retrieval.

## Pre-registered bands
HARD-PASS: all 3 classes achieve acc > 0.80 in >= 4/5 seeds.
MIDDLE: >= 2 classes achieve acc > 0.80.
HARD-FAIL: <= 1 class achieves acc > 0.80 in >= 3/5 seeds.
Calibration probe; +-50%.

## N-suffix
No _nN suffix; production N=1024; rationale: CPU budget.

## Timeout estimate
smoke_wall_s=0.2. ceil(1.5 * 0.2 * (5/2)) = 0.75s -> timeout_s=300.

## Date
2026-06-01
