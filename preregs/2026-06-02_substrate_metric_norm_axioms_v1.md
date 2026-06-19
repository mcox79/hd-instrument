# Pre-registration: substrate_metric_norm_axioms_v1

**Date:** 2026-06-02
**Anchor:** substrate_metric_norm_axioms_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_substrate_metric_norm_axioms_v1.py

## Scientific question (PP-41 support)
Do the 4 Frobenius norm axioms (positivity, definiteness, homogeneity, triangle inequality)
hold for the substrate weight matrix W under Hopfield storage?

## Pre-registered thresholds (set BEFORE run)
- HARD-PASS: max_violation < 1e-8 (all 4 axioms hold to machine precision)
- MIDDLE: max_violation in [1e-8, 1e-4] (axioms hold approximately)
- HARD-FAIL: max_violation >= 1e-4 (axiom violated at practical scale)

## Calibration note
Frobenius norm axioms are algebraic identities for real matrices; expected exact pass.
Bands set wide (1e-8 / 1e-4) to accommodate floating-point accumulation at large M.

## Smoke result
HARD_PASS: max_violation=1.78e-15 (smoke N=1024, M_LIST=[5,20,50,100], 50 triples, 5 seeds, 2 seeds smoke)
