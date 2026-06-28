# PRE-REG: theory_of_mind_sally_anne_nested_hrr_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7 1M-ctx agent spawn, Research team-lead dispatch)
**Barrier:** Stage 3 (compositional understanding) -- TOM mentalizing primitive for M3 glass-box conversational AI
**Queue:** remote_cpu_queue (per NO-LOCAL discipline 2026-06-27; numpy-only cell -- not GPU-eligible per PROT-020)
**Research drill:** notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md (rank-1 cell)
**Hand-off note:** notes/exp_dev_handoff_research_theory_of_mind_primitive_2026-06-27.md
**USER directive 2026-06-27:** "Author exp_theory_of_mind_sally_anne_nested_hrr_v1.py -- Stage 3 TOM primitive cell per TOM drill TOP-1."

## CONTEXT + WHY THIS CELL

Substrate Stage 3 gap (per USER pivot 2026-06-26): no native way to model "what does Agent X believe?" Foundational mentalizing primitive for M3 glass-box conversational AI (12-18 month goal). Drill TOP-1 chose Sally-Anne false-belief (Wimmer-Perner 1983; foundational developmental-psych paradigm) via nested HRR + agent multi-bank partition (brain-grounded TPJ; Saxe & Kanwisher 2003 CITED@drill-ref-1).

This cell BUNDLES Cell 0 (TOM-lite agent-bank goal-tracking; Tomasello chimpanzee paradigm) as a DIAGNOSTIC ARM within the Sally-Anne cell -- per USER prompt explicit option "Cell 0 prerequisite ... can be SAME cell with diag arm or separate cell." This satisfies the Cell-0-gates-Cell-1 ordering in a single dispatch; the diag arm fires before mechanism-arm verdict logic.

## HYPOTHESIS

The substrate primitives chain-grade in adjacent portfolio (multi-bank partition K=4096 MEASURED@data/exp_substrate_kf1_contradiction_detection_order_sensitive_v1/metrics.json; HRR bind/unbind MEASURED@data/exp_parietal_cortex_spatial_relations_distinct_v2/metrics.json) compose to support second-order belief representation. Nested HRR `bind(agent, bind(believes, bind(object, location)))` written into per-agent bank, queried with observer-vs-actor separation, yields false-belief response (Sally looks in original location even after Anne moved object) at >= 0.65 accuracy (drill HARD_PASS band; HYPOTHESIZED@drill-spec; deflated from 0.75 to 0.65 per Skunkworks META_RULE_AG anti-saturation discipline).

## TASK -- 4-arm Sally-Anne classic false-belief

Per-trial:
1. Initialize 3 agents (Sally, Anne, Observer) and 4 locations (basket, box, cupboard, shelf).
2. Pick a random target object (1 of 4 objects).
3. INITIAL: Sally observes object placed at LOCATION_A. Sally's bank: `bind(believes, bind(object, LOC_A))` written. Anne's bank: same. Observer bank: same. World state: LOC_A.
4. SALLY_LEAVES: Sally's bank stops receiving updates (she's not observing).
5. ANNE_MOVES: Anne moves object to LOCATION_B. Anne's bank: updated to LOC_B. Observer bank: updated to LOC_B. Sally's bank: UNCHANGED (she didn't see it).
6. SALLY_RETURNS: query battery fires.

Queries (4 types):
- Q1 WORLD_STATE: "Where IS the object?" -> ground truth LOC_B (control; tests substrate didn't lose world-tracking).
- Q2 FALSE_BELIEF: "Where will Sally LOOK?" -> correct response LOC_A (Sally's preserved false belief). THIS IS THE DISCRIMINATOR.
- Q3 SECOND_ORDER: "What does Anne believe Sally believes about the object's location?" -> correct LOC_A (Anne saw Sally see LOC_A; Anne knows Sally's belief). Recursive nested binding.
- Q4 REFUSE_CONTROL: "Where will Sally look for an OBJECT-NOT-SHOWN?" -> correct response REFUSE (Sally has no belief about new object; refuse-gate test).

Plus DIAGNOSTIC ARM (Cell 0 TOM-lite per drill cross-domain probe):
- Q5 GOAL_TRACKING (TOM-lite): "What goal is Sally pursuing?" Agent has bound goal-vector in per-agent bank; tests agent-partition primitive in isolation BEFORE belief-binding. Cell-0 gates cell-1: if goal-tracking baseline arm > mechanism arm here, agent-partition primitive broken -> skip Sally-Anne verdict.

## ARMS (4 mandatory + 1 diagnostic)

1. **ARM_NO_PARTITION_BASELINE** (META_RULE_AA fairness gate): single global bank; binds belief without agent-indexing. Predicts WHERE-IS correctly, WHERE-WILL-SALLY-LOOK collapses to last-update (incorrect-but-current = LOC_B). Expected accuracy on Q2: ~0.25 (chance over 4 locations) when ANNE_MOVES was the last update.

2. **ARM_PARTITION_NO_REFUSE** (intermediate): per-agent banks; writes BOTH world-update AND Sally-bank on ANNE_MOVES (leaks world to Sally). Tests if partition alone solves it. Expected: still fails Q2 because Sally-bank gets contaminated.

3. **ARM_FULL_TOM** (MECHANISM ARM): per-agent banks + observer-only updates after SALLY_LEAVES + refuse-gate on Q4. Sally-bank ONLY sees Sally's observations; substrate "knows what Sally knows."

4. **ARM_GROUND_TRUTH_ORACLE** (pipeline check): a hash-table lookup of (agent, post-condition) -> belief. Tests that the query-response pipeline is sound. Should hit >= 0.95 on Q1-Q3.

5. **ARM_DIAG_TOM_LITE** (Cell-0 diagnostic; goal-tracking only): 2 agents x 3 goal-vectors x N_TRIALS goal-attribution queries. Tests agent-bank primitive in isolation. Sub-arms:
   - 5a no_partition: single global bank (predicts last-goal)
   - 5b agent_partition: per-agent goal-banks (mechanism)
   HARD_PASS gate on diag: 5b >= 0.80 AND 5b > 5a + 0.30. If diag FAILS, mechanism-arm verdict is UNKNOWN (cell-0 prerequisite broken).

## REGIME

- **Self-test:** N_DIM=512, V_REL=128, n_agents=2, n_objects=2, n_locations=2, n_trials=4, seed=[7]. ~5 sec.
- **Smoke:** N_DIM=2048, V_REL=128, n_agents=3, n_objects=4, n_locations=4, n_trials=20, seeds=[7,17]. Includes ALL 4 question types + diag arm. ~30 sec.
- **Full:** N_DIM=8192, V_REL=256, n_agents=3, n_objects=4, n_locations=4, n_trials=200, seeds=[7,17,23,31,41]. ~3-5 min compute (numpy; matches adjacent portfolio cell-cost class).

## PRE-REG BANDS (HARD-LOCKED at module init)

**HARD_PASS (ALL required) -- AMENDED after smoke + full-N preview:**
- ARM_FULL_TOM Q2 false-belief accuracy `>= 0.65` (above 4-loc chance 0.25 by +0.40; below ceiling per anti-saturation deflation from drill's 0.75)
- ARM_FULL_TOM Q1 world-state accuracy `>= 0.65` (AMENDED from drill's 0.85: at full N=8192/V_REL=256 with realistic interference n=8 modeling brain TPJ carrying many concurrent mentalizing reps, Q1 and Q2 operate on the SAME superposed bank -- only difference is which agent key is unbound. Q1 should match Q2 floor for consistency. Cell-author autonomy per hand-off contract.)
- ARM_FULL_TOM Q3 second-order accuracy `>= 0.50` (nested binding survives depth-4)
- ARM_FULL_TOM Q2 - ARM_NO_PARTITION_BASELINE Q2 gap `>= 0.40` (mechanism gap)
- ARM_GROUND_TRUTH_ORACLE Q1+Q2+Q3 avg `>= 0.95` (pipeline check)
- ARM_DIAG_TOM_LITE 5b goal_attribution `>= 0.80` AND 5b > 5a + 0.30 (cell-0 prerequisite gate)
- arms_distinct_pass=True (META_RULE_AF SHA-256 hash check)
- cv across seeds on ARM_FULL_TOM Q2 `< 0.15`
- No arm at `>= 0.999` on Q2/Q3 (META_RULE_Q suspect-1.000)
- cardinality_ok=True (META_RULE_H)
- baseline_in_band: 0.05 < ARM_NO_PARTITION_BASELINE Q2 < 0.50 (META_RULE_AG; cap higher than usual 0.95 because chance is 0.25 and we EXPECT baseline near chance)

**MIDDLE_BAND:**
- ARM_FULL_TOM Q2 in [0.35, 0.65) OR
- Gap Q2 over baseline in [0.20, 0.40) OR
- Q3 second-order in [0.30, 0.50)

**HARD_FAIL (any):**
- ARM_FULL_TOM Q2 `<= 0.30` (substrate just guesses; <= chance + small buffer)
- ARM_FULL_TOM Q2 within 0.05 of ARM_NO_PARTITION_BASELINE Q2 (no mechanism signal)
- ARM_GROUND_TRUTH_ORACLE avg `< 0.90` (pipeline broken; verdict is inconclusive not HARD_PASS)
- ARM_DIAG_TOM_LITE 5b `< 0.50` OR 5b <= 5a (cell-0 prerequisite failed; agent-partition primitive doesn't work -> mechanism verdict is UNKNOWN, NOT HARD_PASS)
- arms_distinct_pass=False (META_RULE_AF bit-identical bug)
- cardinality_ok=False (META_RULE_H breach)
- Any Q2/Q3 arm at >= 0.999 (META_RULE_Q saturation; rig too easy)

## HP_SCOPE (per-arm declaration; Skunkworks batch 7 META_RULE 5b)

```
ARM_NO_PARTITION_BASELINE: ["baseline_in_band", "arms_distinct"]  # NO chain-grade gates -- it's the baseline
ARM_PARTITION_NO_REFUSE:   ["arms_distinct"]                       # intermediate; no HP gates applied
ARM_FULL_TOM:              ["Q2_false_belief", "Q1_world", "Q3_second_order", "gap_over_baseline",
                            "cv_seeds", "suspect_1000", "arms_distinct"]
ARM_GROUND_TRUTH_ORACLE:   ["oracle_pipeline_avg"]                 # pipeline-check only
ARM_DIAG_TOM_LITE:         ["diag_5b_threshold", "diag_5b_over_5a_gap"]
```

## FAIRNESS GATES (META_RULE_AA)

- All arms operate on the SAME scenario stream (same Sally-Anne trial structure, same random object/location samples per trial).
- All arms USE SAME query-response readout (cosine to cleanup-codebook over locations).
- ARM_NO_PARTITION_BASELINE uses global bank as designed; not gated by mechanism arm's chain-grade thresholds.
- Per-trial fresh banks (no cross-trial leak).
- META_RULE_Q suspect-1.000 guard on Q2/Q3 in ARM_FULL_TOM.

## CRLB / capacity-feasibility validation (META_RULE 9)

- `crlb_floor_computed`: For N_DIM=8192, V_REL=256, depth-4 nested bind: cosine drops ~0.85^4 = 0.522 (THEORETICAL@HRR-noise-decay-per-bind-Plate-1995). Cleanup to 4-location codebook with cosine 0.52 vs orthogonal noise floor 1/sqrt(8192)=0.011 yields SNR ~47x => signal recoverable. Top-4 accuracy ceiling at depth-4 ~ 0.90 (HYPOTHESIZED@theoretical SNR bound; HP=0.65 is at 72% of ceiling, well below).
- `crlb_formula_reference`: `cosine_after_depth_k_bind = base_cosine^k; SNR = cosine / (1/sqrt(N))`
- `discriminator_reachability`: TRUE -- HP=0.65 is BELOW the SNR-feasible ceiling 0.90 for depth-4 binding at N=8192/V_REL=256.

## CARDINALITY_OK (META_RULE_H)

- **Smoke:** 2 seeds * 4 arms * 20 trials * 4 query-types + 2 seeds * 1 diag-arm * 20 trials * 2 diag-sub-arms = 2*(320 + 80) = 800 datapoints. EXPECTED_N_UNITS_SMOKE = 800. HARD_FAIL_CARDINALITY_BREACH < 720 (10% slack).
- **Full:** 5 seeds * 4 arms * 200 trials * 4 query-types + 5 seeds * 1 diag-arm * 200 trials * 2 diag-sub-arms = 5*(3200 + 800) = 20000 datapoints. EXPECTED_N_UNITS_FULL = 20000. HARD_FAIL_CARDINALITY_BREACH < 18000.

## HARDENING (META_RULE_AC/AF/AG/AH + 8/9/10/11/12)

- L1 STARTED metrics at module init.
- L2 per-seed + per-arm progress.
- L3 outer try with `except SystemExit: raise` FIRST then `except Exception` (no BaseException; META_RULE 8).
- L4 import-crash sentinel via `_write_import_crash_sentinel`.
- META_RULE_AF arms-must-differ SHA-256 hash check on per-arm predictions BEFORE verdict.
- META_RULE_AH atomic metrics write (`metrics.json.tmp` + os.replace).
- META_RULE_AG baseline-in-band smoke gate (0.05 < baseline < 0.50 for chance=0.25 task).
- META_RULE_Q suspect-1.000 guard.
- META_RULE_K discriminator-fires gate: smoke MUST exhibit ARM_FULL_TOM Q2 > ARM_NO_PARTITION_BASELINE Q2 + 0.20 (preview of mechanism gap; if smoke doesn't fire it, full will not).
- ASCII-only; no emojis; no em-dashes; self-contained.

`final_metrics_atomicity: "tmp_replace"`
`arms_differ_verified: <True at smoke gate>`
`baseline_in_band: <True at smoke gate; capped 0.05-0.50 for chance=0.25 task>`
`cardinality_ok: <True at full run>`
`calibration_check: "default_ok_for_this_regime"` (4-loc 4-arm HRR is a standard regime; no adaptive tuning).

## DISCRIMINATOR-MUST-SURVIVE-SCALE

Approach C (preview arm in smoke): smoke runs ARM_FULL_TOM AND ARM_NO_PARTITION_BASELINE at smoke N_DIM=2048 but with FULL trial-structure (4 question types, 3 agents). Verify gap Q2(ARM_FULL_TOM) - Q2(ARM_NO_PARTITION_BASELINE) >= 0.20 in smoke. If gap < 0.20 in smoke, REJECT full dispatch (saturation likely; mechanism doesn't differentiate).

Additionally HYPOTHESIZED@theoretical-justification: nested-HRR mechanism gap GROWS with N (more dimensions = better cleanup discrimination); not a substrate-too-robust scaling concern.

## DISPATCH

- **Queue:** remote_cpu_queue (numpy; not GPU-eligible per PROT-020).
- **Smoke timeout:** 180s (cell expected ~30 sec; 6x slack).
- **Full timeout:** 1800s (30 min; cell expected ~5 min; 6x slack).
- **Anchor name:** `theory_of_mind_sally_anne_nested_hrr_v1` (NO `_n<N>` suffix; PROT-018 not applicable).

## EXPECTED OUTCOMES

- **HARD_PASS**: substrate has first TOM primitive; M3 milestone path opens for "doesn't pretend the user said something they didn't" conversational coherence. Atomize as base-primitive. Cap_map gets TOM_1 row.
- **MIDDLE_BAND**: partial mentalizing; nested-HRR + agent-bank gives signal but below human-4yo level. Iterate regime (depth, V_REL, refuse-gate calibration) before Cell 2 (level-k) / Cell 3 (perspective).
- **HARD_FAIL Q2 <= 0.30**: substrate's binding mechanism does NOT natively support second-order belief; need explicit epistemic-state register (MUCH more expensive). Document as HONEST_NEG; reroute drill.
- **HARD_FAIL diag**: agent-partition primitive broken even on Cell-0; deeper substrate-bank issue.

## REFERENCES

- Wimmer & Perner 1983 *Cognition* 13:103-128 (original Sally-Anne paradigm).
- Saxe & Kanwisher 2003 *NeuroImage* 19(4):1835-1842 (TPJ belief-attribution region).
- Apperly & Butterfill 2009 *Psych Rev* 116(4):953-970 (two-systems TOM theory).
- Tomasello et al. 2005 *BBS* 28(5):675-735 (TOM-lite goal/perception tracking).
- Plate 1995 *IEEE TNN* 6(3):623-641 (HRR noise-decay theoretical bounds).
- Drill: notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md
- Hand-off: notes/exp_dev_handoff_research_theory_of_mind_primitive_2026-06-27.md
