# Exp-Dev -> Research: Batch B progress -- fact_checked_khop HP + hierarchical MIDDLE (ordering doesn't compose) + 3 GPU batteries

**From:** Exp-Dev  **Date:** 2026-06-06
- fact_checked_khop: HARD_PASS (smoke). K-hop acc 1.0 (K=2,3,5) + per-hop fabrication-flag AUC 1.0. Per-hop hallucination
  LOCALIZATION works -- composition unique vs frontier LLM. Queued CPU.
- hierarchical_hadamard_then_sparse (addendum R2): MIDDLE. ordered = sparse-alone (0.70 vs hadamard 0.40); sparsifying
  Hadamard rows destroys the orthogonality -> sparse component dominates, Hadamard adds nothing. Like the naive mixture
  (LC1 HF) but un-ordered: NEITHER mixture NOR sequential composes Hadamard+sparse. Sparse-coding is the dominant lever;
  use it alone. Queued CPU.
- GPU batteries (bundling per user rule): capacity / sparsity-fine (full f-curve: 20x at f<=0.05 -> 1x at f=0.50) /
  corruption-robustness -- all bundled, GPU-sustained.
Remaining Batch B: dimsparse3_alpha_at_mc (sparse-KEY at M_c on Pythia, but d_eff=18 means tiny effective dim -- expect
weak), cs1_dt_algebraic, neg1 (low prio). multi-encoder d_eff (mpnet/BGE) pending.
