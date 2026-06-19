# Research -> Exp-Dev: Batch C AUTHORIZED -- 6 sparse-KEY composition cells (~3-4h CPU; $0)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User
**Date:** 2026-06-06 ~22:15
**Re:** exp_dev_handoff_research_sparse_key_composition_partners_2x_2026-06-06.md (drill output) + composition drill landing
**Subject:** User authorized Batch C from composition drill. Tests whether Batch B's "use sparse alone" framing prematurely foreclosed compound paths. 6 cells; ~3-4h CPU sequential / ~1.5-2h parallel; $0.

---

## User authorized Batch C

Per composition drill's recommendation. 6 cells testing constructions the drill identified as unfairly foreclosed by Batch B's "use sparse alone" conclusion.

### Drill's pull order (use this unless queue state argues differently)

**Batch C1 (cheapest decisive; ship parallel):**

1. **Multi-head sparse-KEY M=2** (FIRST PRIORITY per drill)
   - Anchor pointer: `multi_head_sparse_key_M2_v1`
   - Wall: ~30 min CPU
   - MMV theory (Davies-Eldar 2012) predicts sqrt(M) gain
   - HP: M=2 capacity >= 1.3x M=1 baseline at matched alpha
   - MID: 1.1-1.3x
   - HF: <1.1x (multi-head doesn't compose either)
   - Cheapest decisive; highest P_deflated (0.40)
   - Most precise theoretical prediction

2. **Hadamard + INDEPENDENT per-row masks** (SECOND PRIORITY per drill)
   - Anchor pointer: `hadamard_independent_per_row_mask_v1`
   - Wall: ~30 min CPU
   - Cycle 130 used SHARED masks (orthogonality destroyed)
   - Independent per-row masks may preserve orthogonality + enable Hadamard+sparse stacking
   - HP: compound >= 0.80 * max(Hadamard, sparse) (within 20% of orthogonal compose)
   - MID: > max but < 0.80 product
   - HF: ~ max (independent masks also fail to compose)
   - Resolves strongest unresolved claim in cap_map

3. **Block-sparse nesting outer/inner alpha** (THIRD PRIORITY)
   - Anchor pointer: `block_sparse_nesting_outer_inner_alpha_v1`
   - Wall: ~30 min CPU
   - Block-RIP (Eldar-Mishali 2009) predicts 1.3-2x improvement
   - Cheapest always-on improvement candidate to sparse-KEY
   - HP: block-sparse >= 1.3x flat-sparse at same total density

**Batch C2 (gated on C1 results):**

4. **Multi-head sparse-KEY M=4** (extends if M=2 confirms)
   - Anchor pointer: `multi_head_sparse_key_M4_v1`
   - Wall: ~30 min CPU
   - Tests sqrt(M) scaling at higher M; predicted 30-50x compound with sparse-KEY
   - Only run if C1's M=2 cell HPs

5. **Hierarchical VQ + sparse-KEY (B=8, then B=64)** (FOURTH PRIORITY; highest potential)
   - Anchor pointer: `hierarchical_vq_plus_sparse_key_v1`
   - Wall: ~60 min CPU (or GPU if larger N needed)
   - sqrt(B) gain combined with sparse-KEY
   - Theoretical 30-50x real-encoder
   - HP: hierarchical+sparse >= 4x sparse-alone

**Batch C3 (cross-domain paradigm test):**

6. **CRT multi-scale grid-cell composition** (paradigm-level)
   - Anchor pointer: `crt_multi_scale_grid_cell_composition_v1`
   - Wall: ~45 min CPU (algebraic + synthetic test)
   - Hippocampal/entorhinal grid cells use Chinese Remainder Theorem multi-scale
   - Gives MULTIPLICATIVE composition exponential in module count
   - If substrate can replicate: paradigm-level architectural insight
   - HP: 3-scale CRT >= 2x single-scale baseline; multiplicative scaling visible

---

## Dispatch sequence

**C1 immediate parallel (multi-head M=2 + Hadamard indep masks + block-sparse):**
- 3 cells; ~30 min CPU each; total wall ~30-45 min parallel
- All algebraically grounded; high information per unit time

**C2 conditional (M=4, hierarchical VQ):**
- Only run if C1's multi-head M=2 HPs
- Total wall ~90 min sequential

**C3 cross-domain (CRT multi-scale):**
- Run in parallel with C2 or after
- ~45 min CPU; standalone

Total Batch C wall: ~2-3h sequential / ~1.5h parallel; $0.

---

## Strategic value of this batch

### If multiple cells HP

- Real-encoder compound ceiling 20-35x becomes achievable
- Phase 3 linear-mode revised UPWARD from current ~104k facts
- Production substrate architecture: sparse-KEY + multi-head + hierarchical VQ (cleaner stack than just "use sparse alone")

### If cells HF

- Cleaner empirical closure on composition space
- "Use sparse alone" verdict validated at multiple constructions
- Strategic focus narrows to encoder choice + ZCA whitening + sparse-only sythentic stores

### Either outcome advances the cap_map

The drill explicitly noted: "Either outcome advances the cap_map decisively" (for the Hadamard independent-mask cell). Same applies to multi-head M=2 (decisive at sqrt(M) prediction).

---

## Cross-references

- Composition drill: notes/research_drill_sparse_key_composition_partners_2x_2026-06-06.md
- Original handoff: notes/exp_dev_handoff_research_sparse_key_composition_partners_2x_2026-06-06.md
- Batch B complete: notes/exp_dev_to_research_batchB_complete_2026-06-06.md
- D-RIP unified framework (cross-ref): notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md

---

## Contract

You design anchor specifics, sweep grids, HP/MID/HF thresholds, queue assignments, timeout formulas. Pre-reg per envelope-fail-band protocol. write_metrics() required fields. ASCII-only. Apply [[feedback-no-experiment-design-in-prompts]] -- this handoff names anchors + WHY only.

---

**END.**

**Exp-Dev:** Batch C authorized (6 cells; ~2-3h sequential / ~1.5h parallel; $0). C1 first (multi-head M=2 + Hadamard indep masks + block-sparse; parallel; cheapest decisive). C2 conditional. C3 cross-domain (CRT). Drill pull order is recommended; override if queue state argues differently.

**User:** Batch C (6 cells) routed to Exp-Dev. Total ~3h CPU; $0. Tests 4 composition paths Batch B left untested. Either outcome (HP or HF) advances the cap_map. Strategic value: if multi-head M=2 HPs at sqrt(M) prediction, real-encoder compound ceiling 20-35x becomes achievable; Phase 3 linear-mode revises upward.
