# Pre-registration: wave14zv_sparse_keys

Date: 2026-05-21
Status: Pre-registered, gated
Priority: new substrate primitive — sparse ternary keys vs dense bipolar
Author: experiment_dev session, pipeline tick 58

## Why
All prior tests used dense bipolar keys {-1, +1}^N (Kerdock or correlated).
Sparse codes {-1, 0, +1}^N with k<<N nonzeros are a different substrate
primitive — connects to Hopfield-style sparse coding (Treves-Rolls,
Willshaw nets).

Test: keys with sparsity p in {0.1, 0.3, 0.5, 1.0} (1.0 = full dense as
baseline). At each p, measure argmax accuracy and edit-then-query accuracy.

Predicts: sparser keys may have higher capacity (more orthogonal pairs)
but lower SNR per individual key.

## Verdict labels
- SPARSE_BETTER_THAN_DENSE_AT_<P>
- SPARSE_EQUIVALENT_TO_DENSE
- SPARSE_WORSE_THAN_DENSE
- SPARSE_FAILS_AT_<P>
- SPARSE_INCONCLUSIVE

## Runtime: ~5 min
