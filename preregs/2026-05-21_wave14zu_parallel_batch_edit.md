# Pre-registration: wave14zu_parallel_batch_edit

Date: 2026-05-21
Status: Pre-registered, gated
Priority: new mechanism — single batch update vs sequential
Author: experiment_dev session, pipeline tick 57

## Why
All prior edits applied sequentially (one rank-1 update per fact). zu
applies them in ONE batch:
  W_new = W - alpha * (W K^T K (K K^T)^-1)  # batched erase
  W_new = W_new + V_new K^T / N              # batched insert
Or equivalently: project off the span of edited keys, add v_new outer-product.

Batched edit is more product-relevant (single transaction, atomic) and may
have different stability than sequential (no intermediate states).

Compare batched vs sequential at matched n_edit. Should give same final W
for orthogonal keys, may differ for correlated.

## Verdict labels
- BATCH_VS_SEQ_EQUIVALENT
- BATCH_BETTER_THAN_SEQ
- BATCH_WORSE_THAN_SEQ
- BATCH_VS_SEQ_INCONCLUSIVE

## Runtime: ~3 min
