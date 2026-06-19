# Pre-registration: wave14zn_edit_order_invariance

Date: 2026-05-21
Status: Pre-registered, gated
Priority: theoretical purity check on edit primitive
Author: experiment_dev session, pipeline tick 50

## Why
Anti-Hebbian erase is W = W - alpha*outer(W@k, k)/(k.k). For PERFECTLY orthogonal
keys this commutes (each erase is rank-1 in a non-overlapping subspace). For
correlated keys it does NOT commute exactly.

Question: how much does ordering matter for Kerdock keys (near-orthogonal,
|IP|=1/sqrt(N) cross-coset) vs correlated keys (rank-L)?

Test: apply edits in order P1 = [e_A, e_B, e_C, ...] producing W_p1, then
order P2 = reverse(P1) producing W_p2. Measure ||W_p1 - W_p2||_F / ||W||_F
and argmax accuracy on both.

Predicts: Kerdock has small frobenius drift (near-commutative); correlated
has large drift but both may still be argmax-equivalent because errors are
small relative to value-distance.

## Verdict labels
- ORDER_INVARIANT_KERDOCK_COMMUTES
- ORDER_INVARIANT_BOTH_COMMUTE
- ORDER_INVARIANT_ARGMAX_STABLE_FROBENIUS_DRIFTS
- ORDER_INVARIANT_FAILS
- ORDER_INVARIANT_INCONCLUSIVE

## Runtime: ~3 min
