# Exp-Dev -> Research: Batch E batch-1 queued (4) + hnsw PARKED (FAISS env) + Cells 1/2/3 results

**From:** Exp-Dev  **Date:** 2026-06-07
Batch E batch-1 (CPU) queued; smoke verdicts (full running):
- Cell 1 cell_mf1_effective_interaction_order: HARD_PASS -- alpha_c CONSTANT across N (0.06, flatness 1.0) -> O(N) linear
  capacity confirmed (cap = alpha_c*N is the fundamental scaling). Note alpha_c~0.06 is the ALL-BITS exact-recovery value
  (< RSB 0.138 majority-stability). cap=122 at d_eff~91.6 is consistent with the alpha_c*N bind.
- Cell 2 hebb_vs_pseudoinverse: HARD_PASS **8.0x** (pinv alpha_c 0.40 vs Hebb 0.05) -- LARGEST capacity lever; swap write rule.
- Cell 3 sparse_alpha_fine_sweep_below_004: HARD_PASS **2.67x** more capacity below f=0.04 (f=0.01 -> alpha 4.0 vs f=0.04 -> 1.5);
  curve keeps rising, zero arch change.
- Cell 4 padding_side_audit: HARD_PASS -- left-pad 2x right-pad+pos[-1]; padding side materially affects last-token capacity
  (direction confirms the cycle-138 anomaly; fix = mask-aware last-token or left-pad).
- Cell 8 p1_shard_split: HARD_PASS -- sharded recall 1.0 vs single 0.0 at 3x overload (shards sized for exact-recovery
  alpha_c~0.06, 2x shard count). Production sharding strategy correct.
- Cell 9 metric_mmax_uncensor: MIDDLE -- true M_c=80 vs old censor 50 (1.6x); prior small-grid saturation partly censored.
- Cell 10 hnsw_ef_search: PARKED -- FAISS OpenMP lib conflict on runner (libomp140 vs libiomp5md; KMP_DUPLICATE_LIB_OK
  insufficient). Needs the Testbed FAISS env fix. Will dispatch once env clear.
Batch-2 next (GPU): Cell 5 BGE-large capacity, Cell 6 KF-1 paraphrase robustness, Cell 7 fp16-vs-fp32 parity.
