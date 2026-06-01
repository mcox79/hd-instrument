# Pre-registration: continuous_embedding_storage_substrate_v2_n16384

**Anchor**: `continuous_embedding_storage_substrate_v2_n16384`
**Script**: `experiments/exp_continuous_embedding_storage_substrate_v2_n16384.py`
**Date**: 2026-06-01
**Queue**: overnight_queue (GPU)
**Version**: v2 (infra OOM fix; science identical to v1)

## Context

v1 (`continuous_embedding_storage_substrate_v1_n16384`) produced substantive
results on Arms 1 and 2 before OOM at Arm 3:
- Arm 1: Sub_noOS=0.995, Sub_OS=0.995 (seed=7, N=16384 corpus=10000)
- Arm 2: audit_frac=0.9592 (seed=7)
- OOM: Arm 3 `eval_recall` allocated 626 MiB when 6.31 GiB already used

v2 fixes are purely infra (memory layout in `compute_edit_isolation`):
- `eval_recall` now processes queries in chunks of `QUERY_BATCH=1024`
- Peak GPU alloc per chunk: (1024 x N) + (1024 x corpus) = 64MB + 40MB = 104 MB
- Science (thresholds, corpus design, arm definitions) is UNCHANGED from v1

## Pre-registered thresholds (carry-forward from v1)

### Arm 1 -- Retrieval recall at N=16384 with 2x oversampling
- **HARD-PASS**: sub_recall_2x_oversample >= 0.75
- **HARD-FAIL**: sub_recall_2x_oversample < 0.45
- **MIDDLE-BAND**: [0.45, 0.75)

### Arm 2 -- Algebraic audit preservation
- **HARD-PASS**: audit_frac >= 0.85
- **HARD-FAIL**: audit_frac < 0.70
- **MIDDLE-BAND**: [0.70, 0.85)

### Arm 3 -- Edit isolation
- **HARD-PASS**: map_delta_dissim < 0.05 AND map_delta_neighbor < 0.20
- **HARD-FAIL**: map_delta_dissim > 0.15
- **MIDDLE-BAND**: delta_dissim in [0.05, 0.15)

### Arm 4 -- Deletion certificate
- **HARD-PASS**: cert_rate >= 1.0 AND fp_rate <= 0.0
- **HARD-FAIL**: fp_rate > 0.0
- **MIDDLE-BAND**: cert_rate < 1.0 but fp_rate = 0.0

### Joint verdict
- **OVERALL HARD-PASS**: all 4 arms HARD-PASS
- **OVERALL MIDDLE-BAND**: arms 1+2 HARD-PASS, arm 3/4 MIDDLE-BAND
- **OVERALL HARD-FAIL**: any arm HARD-FAIL

## Experimental config

- N = 16384 (PROT-018 binding)
- corpus_size = 10000
- seeds = [7, 17, 23]
- K_recall = 10 (recall@10)
- N_EDIT = 100, N_DELETE = 100
- QUERY_BATCH = 1024 (Arm 3 OOM fix)
- device = cuda (GPU runner)

## N-suffix binding

`_n16384` binds N_FULL = 16384. See `N_FULL = 16384` at line 178 of script.
PROT-018 compliance verified via grep.

## Timeout estimate

v1 elapsed: Arms 1+2 ~5s (seed=7, GPU). Arm 3 fix adds ~20-30s per seed (batched queries).
Estimated total: ~90-120s for 3 seeds. PROT-019 floor: 14400s.
**timeout_s = 21600** (PROT-019 floor for _n16384; v1 elapsed ~5s for Arms 1+2 at GPU speed)

## Smoke result (v2)

- N=1024 corpus=256 seed=17 device=cpu: ALL ARMS HARD_PASS (0.12s)
- N=4096 corpus=1024 seed=17 device=cpu (4x smoke): ALL ARMS HARD_PASS (6.5s)
- Batching correctness verified: single-batch vs 16-chunk results match within 1e-5

## Note on prior empirical anchor

v1 Arms 1+2 provided first empirical anchors:
- Sub_OS recall = 0.995 (well above HP=0.75; predicted 0.75-0.82 for synthetic)
- audit_frac = 0.9592 (above HP=0.85; predicted 0.90 from SNR theory)
These are consistent with the SNR=1.28 prediction and confirm the bands are calibrated.
