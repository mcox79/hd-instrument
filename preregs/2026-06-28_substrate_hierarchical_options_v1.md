# Pre-reg: substrate_hierarchical_options_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** research drill 3x post-v1+revival HARD_FAILs on closed-form D_macro mechanism class.
  Drill: `notes/research_sutton_precup_options_hierarchical_planning_redesign_2026-06-28.md`
  Hand-off: `notes/exp_dev_handoff_research_sutton_precup_options_hierarchical_planning_2026-06-28.md`
**Anchor:** `data/exp_substrate_hierarchical_options_v1/metrics.json`
**Script:** `experiments/exp_substrate_hierarchical_options_v1.py`

## Prior HARD_FAILs (verified on disk)
- `data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json` -- HARD_FAIL TREE=0.000 FLAT=0.133
- `data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json` -- HARD_FAIL SC=0.000 DJ=0.000 BOTH=0.000 FLAT=0.067

Root cause (drill diagnosis): closed-form D_macro pseudoinverse averages parallel-block primitive effects into mush; the modeling class is wrong.

## Mechanism (Sutton-Precup 1999 options framework)

Options dissolve the state-delta modeling problem. An option `(I, pi, beta)` does NOT predict transitions -- it FIRES until termination triggers. No D_macro to fit.

THREE-CHANNEL encoding (NOT bundled HRR; bundling is what averaged v1 + revival into mush):
- **pi (internal policy)** -- per-option small primitive codebook + `iter_cleanup_chain` rollout. MEASURED@CG (multi-hop depth-15).
- **beta (termination)** -- cos(state_t, beta_target_o) >= tau_beta calibrated per option; max-steps fallback. HYPOTHESIZED@cosine-as-termination-signal -- the load-bearing substrate-physics test.
- **I (initiation set)** -- partition-routing-style anchor bank per option; max-cos(state, I_anchors_o) >= tau_I. MEASURED@CG (partition routing M=10M).

## Arms (6) -- discriminator isolates each piece of the 3-channel encoding

1. `ARM_OPTIONS_FULL` -- full pi/beta/I composition (mechanism under test)
2. `ARM_POLICY_ONLY` -- pi alone (no I gating, no beta termination; fixed max-steps; ablation)
3. `ARM_INIT_ONLY` -- pi + I (initiation gating) but NO beta termination (max-steps only)
4. `ARM_TERM_ONLY` -- pi + beta (cosine termination) but NO I gating (all options always eligible)
5. `ARM_CLOSED_FORM_BASELINE` -- v1/revival D_macro mechanism (regression baseline; predicted HARD_FAIL replicating prior)
6. `ARM_RANDOM` -- pure random floor

(Note: 6-arm structure per hand-off. The drill called for `ARM_FLAT_PREPLAY_K128_D6` + `ARM_REPRODUCE_RAIL` + `ARM_OPTIONS_NO_BETA` + `ARM_OPTIONS_RANDOM_PI` etc. The exp_dev hand-off prompt narrowed to 6 arms isolating the 3 channels. Both serve the same purpose; I'm using the 6-arm structure from the hand-off prompt. CLOSED_FORM_BASELINE replaces flat-preplay because it directly tests the prior HARD_FAIL mechanism class.)

## Pre-reg bands (LOCKED at module init; PROSPECTIVE)

### HARD_PASS (ALL of)
- `ARM_OPTIONS_FULL` solve_rate >= 0.55  [HYPOTHESIZED@ from drill section c]
- `ARM_OPTIONS_FULL` - `ARM_POLICY_ONLY` >= +0.10  [pi+beta+I composition lift over pi alone]
- `ARM_OPTIONS_FULL` - `ARM_CLOSED_FORM_BASELINE` >= +0.30  [options vs prior-class regression]
- `ARM_OPTIONS_FULL` - `ARM_RANDOM` >= +0.40  [mechanism load-bearing]
- `ARM_OPTIONS_FULL` solve_rate in [0.30, 0.95]  [un-saturated; META_RULE_AG]
- `ARM_CLOSED_FORM_BASELINE` < 0.20  [sanity: replicates prior HARD_FAIL]
- `ARM_RANDOM` < 0.05  [floor]
- arms_distinct == True (SHA-256 per-arm seq trace across all 6 critical pairs)
- cv across seeds (`ARM_OPTIONS_FULL`) <= 0.15

### MIDDLE_BAND (HARD_PASS_PARTIAL)
- `ARM_OPTIONS_FULL` in [0.30, 0.55) AND lift over POLICY_ONLY >= +0.05 AND lift over RANDOM >= +0.25

### HARD_FAIL (ANY of)
- `ARM_OPTIONS_FULL` <= 0.20 -> **THIRD-FAILURE GATE**: third consecutive HARD_FAIL on hierarchical-planning mechanism class -> close capability box; file capability-closed atom; reframe M3 demo around non-hierarchical conversation classes
- `ARM_OPTIONS_FULL` within 0.05 of `ARM_RANDOM` -> pi not executing properly; cell-bug not framework-failure
- arms_distinct == False -> cell bug
- `ARM_CLOSED_FORM_BASELINE` >= 0.30 -> SANITY: prior HARD_FAIL did not replicate; investigate before reading mechanism arms

### SANITY breaches (verdict UNKNOWN; redesign before reading mechanism)
- `ARM_RANDOM` > 0.10 -> regime too easy; floor breach

## Smoke gate (MUST pass before full dispatch)
- `ARM_OPTIONS_FULL` > `ARM_POLICY_ONLY` by > 0.10 (beta + I contribute)
- `ARM_OPTIONS_FULL` in [0.30, 0.95] (un-saturated; META_RULE_AG)
- `ARM_CLOSED_FORM_BASELINE` < 0.20 (replicates prior HARD_FAIL)
- `ARM_RANDOM` < 0.05
- arms_distinct == True via SHA-256
- cardinality_ok per pre-reg

## Cardinality (META_RULE_AH)
- EXPECTED_N_UNITS_SMOKE = 6 arms * 1 seed * 20 goals = 120
- EXPECTED_N_UNITS_FULL  = 6 arms * 3 seeds * 50 goals = 900
- HARD_FAIL_CARDINALITY_BREACH: observed < expected

## Domain
- 4-block BlocksWorld with N_POS=3 (slot_A/B/C; no held -- simpler than v1's 8-block to compensate for novel mechanism complexity per drill 4-block spec in section 3)
- 6 actions: pick_up_A, pick_up_B, swap_AB, swap_AC, rotate_BC, clear_all
- 3 hand-defined options (drill spec): `stack_pair`, `clear_then_grab`, `relocate`
- Composite goal regime: MIN_OPTIMAL=4 (smoke) / 5 (full); composite_depth=6
- N_DIM = 8192

## CRLB / chance floor (computed in code)
- Pure chance A=6 depth=6: 6^-6 = 2.14e-5
- K=64 rerank UB: ~0.04
- HARD_PASS lift over chance: 0.55 / 2.14e-5 = ~25000x (well above instrument noise floor)

## Compute (per-formula, in code)
- Per-option beta calibration: 200 * 8192 = 1.64M flops (per option, x3 = 4.9M)
- Per-option I bank fit: 32 * 8192 = 262k flops (per option, x3 = 786k)
- Per-goal worst-case: 6 depth * 8 max-steps-per-option * (I_check 3*32*N + pi_step A*N + beta_check N) = ~40M flops
- Smoke total: 6 arms * 1 seed * 20 goals * 40M = ~4.8B flops -> ~5s pure compute -> ~25s wall (5x overhead)
- Full total: 6 arms * 3 seeds * 50 goals * 40M = ~36B flops -> ~37s pure compute -> ~110s wall (3x overhead remote_cpu)
- Drill estimate (conservative; includes BFS oracle + composite-goal sampling): 20-40min smoke / 1-2hr full
- Per-experiment timeouts: smoke=2400s; full=9000s

## Self-test (--self-test mode)
- N_DIM=1024, 1 seed, 4 goals, depth=4
- Verify: arms_distinct, RANDOM < 0.10, all 6 arms produce non-empty per-arm dict, ARM_OPTIONS_FULL >= 0 (no NaN), no silent except: skipped failures

## Discipline markers
- ASCII-only; __main__ guard; SystemExit re-raise BEFORE BaseException sentinel
- L1-L4 hardening: L1 early metrics-write at init / L2 per-arm runtime / L3 outer try / L4 import-sentinel
- META_RULE_AC -- cross-thread cohabit (drill targets v1 + revival + leverages refuse-gate + partition routing + multi-hop CG)
- META_RULE_AF -- arms-must-differ SHA-256; HARD_FAIL on collision
- META_RULE_AH -- atomic-final-metrics-write (tmp+os.replace) + cardinality_ok
- META_RULE_AG -- un-saturated band [0.30, 0.95] for HARD_PASS
- META_RULE_AL -- 3-channel encoding (pi/beta/I) BEFORE planner readout; encoding choice IS the substrate-physics fix
- META_RULE_AN -- empirical baseline (RANDOM + CLOSED_FORM ablations)
- Substrate-doesn't-know-anything compliance: no language tokens, options encode SUBSTRATE-NATIVE state representations only
- Number tagging: MEASURED@/HYPOTHESIZED@ per primitive
- No silent except blocks; halt + record on cos NaN / partition routing miss / refuse-gate calibration empty
- Discriminator-must-survive-scale: smoke at full N=8192 composite-depth=6 with all 3 options active

## THIRD-FAILURE GATE behavior
If `ARM_OPTIONS_FULL` <= 0.20 at smoke:
1. Do NOT dispatch full.
2. Write verdict HARD_FAIL with `_third_failure_gate_triggered=True` in metrics.
3. File capability-closed atom: `notes/exp_dev_capability_closed_hierarchical_planning_2026-06-28.md` (for Skunkworks atomization).
4. Recommend M3 demo reframing away from deep-composite hierarchical planning.

## Brain analog
- Sutton-Precup-Singh 1999 options framework (AIJ 112:181) -- SMDP at option boundaries; no per-step prediction
- Bacon-Harb-Precup 2017 option-critic (validates options-without-hand-crafted-termination feasible)
- Botvinick 2009 / Jin-Tecuapetla-Costa 2014 -- BG striatum sequence chunking; dorsolateral pi vs dorsomedial beta separable
- Plate 1995 ch.6 -- HRR chunking; options are temporal complement to Plate's structural chunking

## Cross-thread coupling
- M3 USER concern #5 (hierarchical goal-decomposition) -- if HARD_PASS, gates conversation-with-multi-step-plan capability
- M4 substrate-as-research-director -- Director options ("mine-cap-map", "design-cell", "audit-verdict") each with own beta termination

## Honest discount
- P_deflated = 0.38 per drill section a (raw 0.55 + brain existence proof +0.10 + substrate-mining +0.05 - calibration penalty -0.20 - novel-composition cap -0.10 - twice-burned discount -0.02)
- Default classification expectation = MIDDLE_BAND; cert-owner Skunkworks tiers up
- Twice-burned mechanism class; honest framing = "if THIS also fails, the capability box closes"
