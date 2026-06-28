# exp_dev hand-off — research: dlPFC WM state-tracker 4-primitive composition

**Filed-by:** research (Director)
**Date:** 2026-06-28
**Trigger:** `notes/research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md` — drill verdict = `NEED_MORE_DRILL` (signal-shape adapter design required before cell-author spawn)
**Pause state:** check `data/orchestrator_paused.flag` before any experiment dispatch

**Per [[feedback-no-experiment-design-in-prompts]]:** this handoff names anchors + provides pointers, does NOT design the experiment. exp_dev (cell-author / orchestrator) decides anchor selection + pre-reg authoring per their autonomy.

---

## Anchor candidates (rank-ordered)

### Rank 1 (RECOMMENDED — drill, not ship): `adapter_design_drill_wm_to_schema_bayes_signal_shape_v1`

- **Type:** research-internal adapter-design drill, NOT a substrate cell yet
- **Substrate-product reading:** specifies the mechanism for Edge-1 (WM-bank output → schema-Bayes input) injection. Three sub-mechanisms to evaluate:
  - **Sub-A:** state-context as PRIOR (multiply prior over schemas by similarity to WM state vector)
  - **Sub-B:** state-context as additional evidence (inject WM slot as fake-evidence entry; needs evidence weight calibration)
  - **Sub-C:** state-conditioning variant of schema-Bayes (replace schema-Bayes primitive with one that takes state-vector as additional input slot)
- **Tier hint:** research-grade (no chain-grade primitive exists for any of A/B/C yet)
- **Why-now:** Path 1 + Path 2 both HARD_FAILED today on signal-shape mismatch; spawning C_PATH3 cell naively would HARD_FAIL again with same root cause; adapter design is the cheap precursor
- **Substrate-KB cross-check:** `python d:/AI/hd-instrument/tools/substrate_capability_registry.py --capability working_memory` shows 27 WM landings including chain-grade `substrate_wm_multibank_K_cliff_phase_diagram_v1` 3-seed HARD_PASS

### Rank 2 (CONDITIONAL — ship IFF adapter sub-A is mathematically obvious): `exp_substrate_partition_oracle_pfc_wm_state_tracker_v1`

- **Anchor pre-reg:** see `notes/research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md` section "Cheap decisive test"
- **5 arms:** A_BASELINE / B_PATH2_PERCHAIN / C_PATH3_WM_STATE_TRACKER / D_ORACLE_PER_HOP / E_RANDOM
- **HARD_PASS:** C in [0.50, 0.95] AND C − B ≥ 0.30 AND C − A ≥ 0.20 AND per-hop part-acc > 0.50
- **HARD_FAIL:** C ≤ 0.30 OR C − B < 0.10 OR C < A
- **Tier hint:** chain-grade-eligible IF HARD_PASS (closes multi-hop barrier 1)
- **Why-now:** if Rank 1 adapter drill identifies a trivial state-context-injection mechanism (sub-A as prior modulation), this cell tests it end-to-end
- **Why-NOT-now:** if Rank 1 says adapter requires learning / co-training, this cell is DEAD and shouldn't ship

### Rank 3 (FALLBACK if both above fail): `exp_substrate_per_state_schema_selector_v1` (NEW PRIMITIVE)

- **Type:** new primitive class (5th primitive beyond current chain-grade portfolio)
- **Mechanism:** per-state-conditioned schema policy selection (Sutton-Precup analog WITHOUT pre-trained per-state policies)
- **Substrate-product reading:** would require either a per-state-trained schema head (multiple schema primitives stacked) OR a meta-schema that conditions on state vector
- **Why-now:** ONLY if Rank 1 + Rank 2 both close as HARD_FAIL — diagnoses brain-faithful 4-primitive composition as insufficient
- **Tier hint:** research-grade; very speculative; defer until Rank 1+2 close

---

## Context pointers (file paths, not summaries)

- `notes/research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md` — this drill (full design + audit + verdict)
- `data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json` — MIDDLE_BAND baseline reference (ORACLE_B=0.835, BASELINE=0.295 at depth 15)
- `data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1/metrics.json` — WM bank chain-grade HARD_PASS reference
- `notes/research_drill_brain_multihop_M2_pfc_scratchpad_separate_W_3x_2026-06-27.md` — prior PFC-scratchpad drill (different functional requirement: clean intermediates, not state-context bias)
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_chain_grade_primitives_not_trivially_composable_2026-06-28.md` — load-bearing discipline rule (Edge-1 SHAPE_MISMATCH per this rule)
- `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_functional_requirement_first_test_design_USER_2026-06-28.md` — load-bearing discipline rule (4 of 5 FRs already covered)

---

## Contract

- exp_dev / cell-author owns: pre-reg authoring including state-context injection mechanism specification, smoke gate at full depth (Check A discriminator-must-survive-scale), Fix #17 runtime measurement
- exp_dev / orchestrator owns: queue routing (substrate cell → remote_cpu OR remote_gpu per Fix #24 heuristic at N=8192)
- research (me) owns: Rank-1 adapter-design drill (would be a follow-up drill, not delegated)

## Autonomy declaration

- exp_dev decides anchor selection (Rank 1 vs Rank 2 vs deferral)
- exp_dev / cell-author owns pre-reg authoring
- exp_dev / orchestrator owns dispatch (pause-gated)
- I do NOT design the experiment; I provide anchor pointers + signal-shape audit + functional-requirement decomposition

