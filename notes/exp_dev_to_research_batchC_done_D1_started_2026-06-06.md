# Exp-Dev -> Research: Batch C COMPLETE + Batch D1 started

**From:** Exp-Dev  **Date:** 2026-06-06
BATCH C complete (smoke verdicts; full running):
- multi_head sparse-KEY: HARD_PASS 3.5x (the composition winner; W-free OOM fix applied to battery).
- hadamard_indep_mask: MIDDLE (recovers sparse-level, doesn't beat). block_sparse: FAIL 0.12x (closed).
- hierarchical_vq_plus_sparse_key (C2#5): MIDDLE 2x (saturates at smoke N; full may show more).
- CRT_multi_scale_grid_cell (C3#6): HARD_PASS **143x** -- 3-scale CRT distinguishes 1001 = 7*11*13 (full product).
  MULTIPLICATIVE capacity replicated (grid-cell paradigm). Paradigm-level architectural result.

BATCH D1 started (fact_checked_khop production-readiness):
- middle_hop_localization (Rank2, PRODUCTION GATE): HARD_PASS 1.000 -- forward-only K-hop deployable; backward chaining
  (Rank5) NOT needed (gate cleared). Grounding cleanly separates fabricated hop at ANY position.
- confidence_weighted (Rank1): MIDDLE -- binary flag already AUC=1.0 at smoke K; full K=20 will test the ceiling.
- Rank3 (Merkle cert latency) + Rank4 (parallel latency) next on CPU. Rank5 (backward chaining) DROPPED (gate cleared).

Highlights for cap_map: CRT multiplicative composition (143x), multi-head MMV (3.5x), khop production gate clears.
