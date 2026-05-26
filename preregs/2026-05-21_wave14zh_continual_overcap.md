# Pre-registration: wave14zh_continual_overcap

Date: 2026-05-21
Status: Pre-registered, gated
Priority: combines continual editing + over-capacity (M=2N)
Author: experiment_dev session, pipeline tick 44

## Why
yc tested continual editing at M=N (HOLDS to 2000). yh tested edit-then-query
at M=2N (one-shot edits, KERDOCK_PASS). zh tests SEQUENTIAL editing at M=2N.

Stress combination: over-capacity AND continual updates. Predicted to hold
based on prior results, but combination not directly verified.

## Verdict labels
- CONTINUAL_OC_KERDOCK_HOLDS
- CONTINUAL_OC_BOTH_HOLD
- CONTINUAL_OC_KERDOCK_FAILS_AT_<I>
- CONTINUAL_OC_INCONCLUSIVE

## Runtime: ~5 min
