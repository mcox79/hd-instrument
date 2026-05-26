# Pre-registration: wave14zs_reversibility_long

Date: 2026-05-21
Status: Pre-registered, gated
Priority: extend zj — does reversibility hold at 500 cycles?
Author: experiment_dev session, pipeline tick 55

## Why
zj held at 50 cycles for BOTH arms (correlated didn't fail). Either:
- 50 cycles too short to expose drift, OR
- Same-key reversal genuinely doesn't accumulate error (algebra closure)

Test: 500 cycles. If still BOTH_HOLD, mechanism is truly closure-preserving.
If correlated fails but Kerdock holds, key structure matters at scale.

## Verdict labels (inherited from zj with cycle count to 500)
- REVERSIBLE_KERDOCK_HOLDS_TO_<N>
- REVERSIBLE_KERDOCK_DRIFTS_AT_<I>
- REVERSIBLE_BOTH_HOLD
- REVERSIBLE_BOTH_DRIFT
- REVERSIBLE_INCONCLUSIVE

## Runtime: ~10 min
