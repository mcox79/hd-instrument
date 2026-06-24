# exp_dev queue note: substrate_two_codebook_sparse_storage_dense_compose_v1

```
queue=overnight_queue name=substrate_two_codebook_sparse_storage_dense_compose_v1 script=experiments/exp_substrate_two_codebook_sparse_storage_dense_compose_v1.py prereg=preregs/2026-06-23_substrate_two_codebook_sparse_storage_dense_compose_v1.md timeout=3600
```

## Ship summary

Anchor: `substrate_two_codebook_sparse_storage_dense_compose_v1`
Queue: `overnight_queue` (GPU; Fix #22: N_DIM=8192 matmul-bound)
Timeout: 3600s

Hypothesis: two-codebook architecture (sparse for STORAGE, dense for COMPOSE) solves
the zero-product cascade and matched-filter energy loss that cause 3 of 5 recent negatives.

Pre-reg HARD_PASS: ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE lift >= +0.20 bits vs baseline 7.3065
Pre-reg HARD_FAIL: lift <= +0.05

Smoke: PASS (all ST1-ST8 instrumentation self-tests passed, wall=42.8s, 5 arms all non-degenerate)
Multi-scale check (N*4): PASS (N_DIM=2048 no OOM)
Name uniqueness: CLEAR (not in overnight_queue or remote_cpu_queue local files)
Commit: e9fcb50f (path-scoped, A5 compliance)

Source: notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md
P_deflated: 0.55

## Decision log

Routing: overnight_queue (GPU) per Fix #22 (N_DIM=8192) + Fix #24 (torch.cuda used throughout).
Smoke READOUT_DEGENERATE is a smoke artifact (VOCAB_CAP=300 -> vocab_entropy=8.23 near raw_bpc=7.97);
FULL run VOCAB_CAP=4000 gives vocab_entropy=11.97 vs expected raw_bpc~11.6 (safe margin).
All smoke arm BPC values differentiated (5.18, 5.01, 5.38, 5.15 vs unigram 5.52); not all-constant.
LAMBDA_GRID excludes 0.0 per META atom C7 LAMBDA_ZERO_COLLAPSE (guard verified in ST7).
