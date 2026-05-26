# Pre-registration: wave14yt_edit_query_4N

Date: 2026-05-21
Status: Pre-registered, gated
Priority: edit-then-query at M=4N over-capacity
Author: experiment_dev session, pipeline tick 27

## Why
yh tested M=2N (KERDOCK_PASS). yt tests M=4N — extends envelope to
the boundary of Bet 2 v3's validated 4-coset codebook capacity.

## Verdict labels
- EDIT_QUERY_4N_BOTH_PASS
- EDIT_QUERY_4N_KERDOCK_PASS
- EDIT_QUERY_4N_KERDOCK_FAILS
- EDIT_QUERY_4N_INCONCLUSIVE

## Operational definition
M = 4N = 16384 keys sampled from 4-coset codebook (uses ALL codewords).
Other params same as yb/yh.

## Runtime: ~5 min
