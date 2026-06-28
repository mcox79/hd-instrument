# exp_dev hand-off — research: multi-hop depth-10 ceiling REVIVAL (2x drill)

**Filed-by:** Research (Opus 4.7 1M; team lead)
**Date:** 2026-06-28
**Trigger:** `notes/research_drill_2x_multihop_depth10_ceiling_REVIVAL_2026-06-28.md` (2x drill on v5 HARD_FAIL_NO_HEADROOM_DEPTH_10)
**Pause state:** orchestrator_paused.flag may be set; consult before dispatch. If paused, file pre-regs only and DO NOT spawn queue_add.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev OWNS cell-design; this handoff provides anchor candidates + context pointers + bands, NOT working code. exp_dev's autonomy includes K/V_C/N tuning, smoke regime, full-N preview arm choice, queue selection.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (RANK 1) — substrate_multihop_partition_oracle_at_v5_regime_revival_c1
- **Tier hint:** chain-grade-eligible if HARD_PASS (verbatim port of substrate-CHAIN_GRADE primitive to harder regime; cone-collapse formula predicts top1@d10 in [0.30, 0.50])
- **Substrate-product reading:** if HARD_PASS, ratifies goal-conditioned-attention as a substrate-API surface (caller provides candidate-set or goal vector; substrate restricts cleanup)
- **Why now:** v5 HARD_FAIL identified the wrong-mechanism-class problem (downstream-of-cleanup vs upstream-of-cleanup); C1 is the cheapest decisive test of the cone-collapse hypothesis
- **Source mechanism:** `experiments/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1.py` lines 267-299 (function `arm_part_oracle_at_depth`)
- **Compute estimate:** smoke ~5min (laptop CPU at N=2048); full ~6hr on remote_cpu_queue
- **P_deflated:** 0.55 (highest; verbatim port of CHAIN_GRADE mechanism)
- **Bands:** see research note PART 4 CELL C1

### ANCHOR 2 (RANK 2) — substrate_multihop_hierarchical_macro_action_depth_reduction_c3
- **Tier hint:** chain-grade-eligible if HARD_PASS (TWO_TIER + separate W_macro; substrate-product leverage is highest because no caller intervention required)
- **Substrate-product reading:** if HARD_PASS, substrate auto-compresses frequent sub-chains into macro-atoms; API surface unchanged
- **Why now:** Botvinick options-framework is brain-grounded + the failed v3 chunked_2hop_decomposition can be CORRECTED via separate W_macro (root-cause was shared-W pollution); D arm = D shared-W reproduces failure as discriminator
- **Source mechanism:** TWO_TIER chain-grade primitive (substrate has this) + macro-atom storage layer (NEW; cell author designs)
- **Compute estimate:** smoke ~10min; full ~9hr on remote_cpu_queue
- **P_deflated:** 0.35 (lower because new composition; pollution-via-shared-W risk known)
- **Bands:** see research note PART 4 CELL C3

### ANCHOR 3 (RANK 3) — substrate_multihop_goal_conditioned_bidirectional_meet_at_v5_regime_c2
- **Tier hint:** CG-eligible if HARD_PASS but more likely MIDDLE_BAND (extending M3 which was already MIDDLE_BAND)
- **Substrate-product reading:** brain-grounded (Pfeiffer-Foster preplay); evidence-second-path if C1 HARD_PASS but caller-doesn't-have-oracle scenario matters
- **Why now:** only dispatch IF C1 lands MIDDLE_BAND (need second evidence path); otherwise defer
- **Source mechanism:** M3 bidirectional primitive (MIDDLE_BAND) + goal-vector conditioning + goal-reachability mask
- **Compute estimate:** smoke ~10min; full ~12hr on remote_cpu_queue
- **P_deflated:** 0.40
- **Bands:** see research note PART 4 CELL C2

---

## Context pointers (file paths, NOT summaries)

- Research drill (LOAD-BEARING; cell author MUST read parts 4 + 5 for arm specs and bands):
  - `d:/AI/hd-instrument/notes/research_drill_2x_multihop_depth10_ceiling_REVIVAL_2026-06-28.md`
- v5 HARD_FAIL metrics (BASELINE rail target):
  - `d:/AI/hd-instrument/data/exp_substrate_multihop_brain_pushback_composition_v5_depth_10_smoke/metrics.json`
- Substrate-CHAIN_GRADE depth-30 reference (C1 source code):
  - `d:/AI/hd-instrument/experiments/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1.py`
  - `d:/AI/hd-instrument/data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json`
- 7-mechanism brain inventory (USER push-back context):
  - `d:/AI/hd-instrument/notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md`
- M3 bidirectional prior (C2 source):
  - `d:/AI/hd-instrument/notes/research_drill_brain_multihop_M3_bidirectional_meet_in_middle_3x_2026-06-27.md`
- Pre-reg for v5 (for cardinality + rail conventions):
  - `d:/AI/hd-instrument/preregs/2026-06-27_substrate_multihop_brain_pushback_composition_v5_depth_10.md`

---

## Recommended dispatch order

1. **C1 FIRST** — cheapest decisive test; smoke gate at full-V_C=1000 smoke-depth=[8,10] must show ARM_B-ARM_A >= 0.05 or BLOCK; full dispatch on smoke HARD_PASS
2. **C3 in parallel** if compute permits (orthogonal mechanism; independent evidence)
3. **C2 LATER** only if C1 lands MIDDLE_BAND

---

## Contract section

- exp_dev decides cell file structure, smoke regime, full-N preview arm, queue (remote_cpu_queue recommended for all three), and which V_C/N pairs to sweep
- All three cells share the v5 regime (N=2048, V_C=1000) as baseline rail — MUST reproduce v5 BASELINE 0.160 +/- 0.05 in every cell (sanity rail)
- All three cells MUST tag META_RULE_AL / AC / H + BIAS-Q / N / S + DISCRIMINATOR-MUST-SURVIVE-SCALE + Fix #28 verify-the-referent
- Compute-formulas-in-code: cone-collapse formula `crosstalk_std = sqrt((V_C_per_hop - 1) / N)` and `predicted_top1_per_step = ...` MUST be in cell source as comments (audit trail for substrate-physics framework)
- All three cells write metrics.json atomically (META_RULE_AH; tmp+os.replace)
- All three cells run a self-test on tiny config before main run

---

## Autonomy declaration

exp_dev MAY:
- Re-scale N or V_C if smoke shows BASELINE rail doesn't reproduce v5 0.160 within tolerance (sanity-rail correction)
- Add additional discriminator arms if cell author identifies a missing control
- Defer C2 indefinitely if C1 HARD_PASS (per recommended dispatch order)
- Combine C1 + C3 into a 2-cell parallel batch
- Add macro-arm or partition-oracle preview arm at smoke to satisfy DISCRIMINATOR-MUST-SURVIVE-SCALE check A

exp_dev MUST NOT:
- Dispatch full-N without smoke HARD_PASS at the cell's smoke gate
- Replace the v5 BASELINE rail with a different regime (the whole point is to test at v5's regime)
- Cite cone-collapse formula as load-bearing without including it in cell source as compute-in-code
- Skip the cardinality_ok declaration

If exp_dev disagrees with anchor ranking, file a reasoning note and proceed with their preferred ranking — the research drill provides decision context, not commands.
