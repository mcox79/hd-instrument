# Pre-registration: wave14zj_edit_reversibility

Date: 2026-05-21
Status: Pre-registered, gated
Priority: new stress dimension — algebra closure under repeated same-key edits
Author: experiment_dev session, pipeline tick 46

## Why
yb established edit-then-query as KERDOCK_PASS. yc/zh show continual editing
across DIFFERENT keys holds. Open question: what about repeated edits at the
SAME key? Each erase+insert cycle should ideally be the identity-after-reversal,
but numerical drift, key-norm fluctuation, and rank perturbation could accumulate.

Test: for each subject fact i, do N_CYCLES of (erase v_orig, insert v_new),
(erase v_new, insert v_orig). After N cycles, query at k_i; should retrieve
v_orig. Also check kept facts haven't drifted.

This is a genuinely new dimension — it stress-tests algebra closure, not capacity
or continual breadth.

## Verdict labels
- REVERSIBLE_KERDOCK_HOLDS_TO_<N>
- REVERSIBLE_KERDOCK_DRIFTS_AT_<I>
- REVERSIBLE_BOTH_HOLD
- REVERSIBLE_BOTH_DRIFT
- REVERSIBLE_INCONCLUSIVE

## Runtime: ~5 min
