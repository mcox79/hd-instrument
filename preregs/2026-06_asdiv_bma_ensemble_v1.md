# Prereg: asdiv_bma_ensemble_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Priority 1 (BMA over existing mechanisms; ~20min, existing primitives).
BMA val-weighted vote over 4 operand-selection strategies (text-order/proximity/magnitude/target) on a shared op-classifier.
Decisive: HARD-PASS>=0.42 (errors decorrelate); HARD-FAIL<=0.39 (errors CORRELATED = comprehension blind-spot).
Smoke: singles ~0.34, BMA 0.34, gain +0.0000 -- correlated. Caveat: tests selection-variance; ~60% items have 2 numbers (no selection choice). Full for the record.
