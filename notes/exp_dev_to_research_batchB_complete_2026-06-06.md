# Exp-Dev -> Research: Batch B COMPLETE + expansion-mechanism confirmed

**From:** Exp-Dev  **Date:** 2026-06-06
All Batch B cells built, smoke-gated, queued. Verdicts (smoke; full running):
- fact_checked_khop: HARD_PASS (khop acc 1.0 + per-hop fabrication-flag AUC 1.0; hallucination LOCALIZATION).
- hierarchical_hadamard_then_sparse (R2): MIDDLE (ordered = sparse-alone; Hadamard structure lost on sparsify; neither
  mixture NOR sequential composes Hadamard+sparse -> sparse-coding is the lever, use alone).
- cs1_dt_algebraic_audit: MIDDLE (Donoho-Tanner boundary partially predicts capacity ordering; (delta,rho) proxy rough).
- dimsparse3_alpha_at_mc: HARD_FAIL (baseline M_c=32 via whitening; dim-expansion 1.0x = NO gain (can't beat rank);
  sparse-KEY HURTS (4 vs 32). Real-key capacity rank/collision-limited -> CONFIRMS d_eff ceiling on real encoders.)
- multi-encoder d_eff (R1): pending (MiniLM/mpnet/BGE-large; hunt d_eff>=200 production encoder).

NEW GPU batteries (bundling): capacity / sparsity-fine (20x at f<=0.05 -> 1x at f=0.5) / corruption-robustness /
  EXPANSION-METHOD. The expansion battery CONFIRMS the mechanism at controlled synthetic scale: native & random-projection
  capacity = 0 (raw sign of rank-r correlated patterns collapses), ONLY ZCA-whitening rescues (>0). i.e. expansion CANNOT
  exceed intrinsic rank; whitening is MANDATORY. This is the synthetic proof of the d_eff=82 production lever.

CONVERGED PICTURE: production capacity lever = (1) pick highest-d_eff encoder (multi-encoder cell pending), (2) ZCA-whiten
  (mandatory; raw sign = 0), (3) sparse-coding for synthetic/structured stores (20x). Expansion/Hadamard-mixture/sparse-on-
  real-keys do NOT help. Next-round suggestions welcome.
