# Pre-registration: wave14yk_edit_query_undercapacity

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yk_edit_query_undercapacity.py](../experiments/exp_wave14yk_edit_query_undercapacity.py)
Priority source: under-capacity envelope characterization for edit-then-query
Author: experiment_dev session, pipeline tick 21

## Why

yb tested edit-then-query at M=N=4096 (BOTH_PASS). yh tests at M=2N
(over-capacity). yk tests at M=N/2=2048 (UNDER-capacity, well within v1's
envelope). Characterizes the lower envelope — should pass cleanly with
both arms, baseline for envelope shape.

## Hypothesis

At N=4096, M=N/2=2048 Kerdock keys, 30 edits, 5 seeds: BOTH arms pass
edit-then-query (Kerdock and correlated). At under-capacity, the
correlated arm's cross-talk isn't enough to break the test.

## Verdict labels

- `EDIT_QUERY_UC_BOTH_PASS` — both arms pass at M=N/2 (baseline)
- `EDIT_QUERY_UC_CORRELATED_FAILS` — correlated fails even at under-capacity
  (would suggest the failure mode kicks in below M=N)
- `EDIT_QUERY_UC_KERDOCK_FAILS` — Kerdock fails (regression)
- `EDIT_QUERY_UC_INCONCLUSIVE`

## Operational definition

Reuses yb pipeline. M_STORED = N/2.

## Expected runtime: 1-2 min
