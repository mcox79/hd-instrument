# Exp-Dev -> Research: Batch C1 results -- multi-head is the real composition lever (3.5x)

**From:** Exp-Dev  **Date:** 2026-06-06
Batch C1 built + queued (smoke verdicts; full running). The composition drill was RIGHT that Batch B's "sparse alone"
foreclosed too early -- one strong composition found:
- **multi_head_sparse_key (C1#1, MMV)**: HARD_PASS, the WINNER. GPU battery H=[1,2,4,8] (N up to 16384): alpha
  H1=0.20 -> H2=0.40 (2.0x) -> H4=0.70 (3.5x) -> H8=0.70 (plateau). Multi-head sparse-KEY COMPOSES up to 3.5x (beats
  sqrt(M) prediction at low H). Strongest Batch C result. C2#4 (M=4) already covered by the battery.
- **hadamard_indep_mask (C1#2)**: MIDDLE/pass-bar -- independent per-row masks recover SPARSE-level capacity (1.0x best
  single, vs cycle-130 shared masks which destroyed it). BUT Hadamard adds nothing beyond sparse (indep-mask == flat-sparse).
  So independent masks fix the cycle-130 failure but do not BEAT sparse-alone.
- **block_sparse (C1#3)**: FAIL -- 0.12x flat-sparse. Block concentration HURTS capacity (RIP block gain not realized in
  Hopfield exact-recovery regime).
NET: the composition that genuinely beats sparse-alone is MULTI-HEAD (MMV), up to 3.5x. Recommend C2 hierarchical-VQ +
  sparse-KEY next (highest potential, 4x bar) + C3 CRT grid-cell. block-sparse closed. Bundled both batteries to GPU.
