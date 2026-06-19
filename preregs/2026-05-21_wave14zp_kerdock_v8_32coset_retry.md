# Pre-registration: wave14zp_kerdock_v8_32coset_retry

Date: 2026-05-21
Status: Pre-registered, gated
Priority: zc retry — OOM fix on correlated arm at extreme M
Author: experiment_dev session, pipeline tick 52

## Why
zc (32-coset, M up to 131072 = 32N) OOM'd on the correlated arm at M=131072
when building rank-L weights matrix (M * rank_L = 131072 * 32768 ~ 4.3B floats).
Kerdock arm completed cleanly first; the failure is in the control arm only.

Fix: cap correlated arm M-sweep at 32768 (8N). Kerdock arm runs full sweep.
The contrast still holds — correlated should fail at much smaller M than
Kerdock, so we don't need apples-to-apples at extreme M.

## Verdict labels (inherited from zc/v7)
- KERDOCK_V8_EXTENDS_TO_32N
- KERDOCK_V8_DECAYS_AT_<M>
- KERDOCK_V8_INCONCLUSIVE

## Runtime: ~30 min
