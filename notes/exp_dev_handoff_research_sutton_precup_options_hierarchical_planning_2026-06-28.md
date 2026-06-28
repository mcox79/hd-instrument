# exp_dev hand-off — research: Sutton-Precup options framework for hierarchical planning

**Filed by:** research (Opus 4.7-1M)
**Date:** 2026-06-28
**Trigger:** Two consecutive HARD_FAILs on closed-form D_macro tree mechanism (v1 + revival). Options framework is the natural HARD_FAIL pivot (already pre-identified as ANCHOR 2 in revival hand-off). See `notes/research_sutton_precup_options_hierarchical_planning_redesign_2026-06-28.md` for full mechanism + substrate-primitive mapping + falsifiable predictions.

**Pause state:** check `data/orchestrator_paused.flag` before dispatch. If present, hold; resume on USER unpause directive.

**Per [[feedback-no-experiment-design-in-prompts]]:** this is a hand-off with anchor candidate + context pointers, not an experiment-design directive. exp_dev owns the cell-author spawn + smoke + dispatch decisions. Research provides mechanism, primitive mapping, falsifiable predictions, and pre-registered thresholds; exp_dev decides smoke regime, full dispatch, and cell-author bundle.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (RANK 1; P_deflated = 0.38; READY): `substrate_hierarchical_options_v1`

- **Anchor pointer:** `data/exp_substrate_hierarchical_options_v1/metrics.json` (anchor file path; cell does not yet exist)
- **Substrate-product reading:** M3 load-bearing piece #5 (USER concern of 10 for M3 glass-box conversational AI). After two HARD_FAILs on closed-form D-prediction tree, options framework dissolves the modeling problem (no state-delta fit; π executes until β triggers). M4 substrate-as-research-director also benefits (director options: mine-gap, design-cell, audit-verdict, each with own termination).
- **Tier hint:** novel-composition (no substrate precedent for options framework). If HARD_PASS, lifts to chain-grade-eligible (composes 3 existing CG primitives — multi-hop iter_cleanup_chain for π, refuse-gate-calibrated cosine threshold for β, partition routing for I; brain-grounded via BG striatal chunking; clean ablation structure).
- **Why now:** v1 + revival HARD_FAILs converge on diagnosis — closed-form D-prediction is the wrong mechanism class. Options framework is the canonical alternative (Sutton-Precup 1999). Substrate has all three pieces (π / β / I) with chain-grade or CG-eligible anchors. THIRD-FAILURE GATE: if this also HARD_FAILs, close hierarchical-planning capability box and document closure.

### ANCHOR 2 (RANK 2; P_deflated = 0.25; HARD_PASS extension only): `substrate_hierarchical_options_deep_composite_v1`

- **Anchor pointer:** `data/exp_substrate_hierarchical_options_deep_composite_v1/metrics.json`
- **Substrate-product reading:** tests USER's "substrate plans all day" claim at composite depth-12+ via options-framework. Deeper composites push past flat-K=128 ceiling (0.85^12 ≈ 0.14), giving hierarchy a clearer lift signal.
- **Tier hint:** depends on ANCHOR 1 outcome. ANCHOR 1 HP → extension. ANCHOR 1 HARD_FAIL → SKIP (don't extend a closed mechanism class).
- **Why now:** defer until ANCHOR 1 lands.

### ANCHOR 3 (RANK 3; P_deflated = 0.20; deferred follow-up): `substrate_option_critic_learned_termination_v1`

- **Anchor pointer:** `data/exp_substrate_option_critic_learned_termination_v1/metrics.json`
- **Substrate-product reading:** Bacon-Roy 2017 option-critic adapted to substrate — learn β termination from rollout data instead of hand-defining. Tests whether substrate can DISCOVER option boundaries (vs current hand-defined boundaries in ANCHOR 1).
- **Tier hint:** ANCHOR 1 HP only. Two simultaneous mechanism changes (options + learned termination) deflate harder.
- **Why now:** defer until ANCHOR 1 lands. Adjacency-cascade candidate per Trigger C.

---

## Context pointers (file paths, not summaries)

**Mechanism + falsifiable predictions:**
- `notes/research_sutton_precup_options_hierarchical_planning_redesign_2026-06-28.md` — full research note (this drill output; substrate primitive mapping for π, β, I; cell architecture; 6-arm structure; pre-reg)

**Prior HARD_FAILs (what this revival addresses):**
- `data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json` — v1 HARD_FAIL: TREE_3LVL=0.000 NO_CLEAN=0.000 FLAT_K64_D8=0.133
- `data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json` — revival HARD_FAIL: SC=0.000 DJ=0.000 BOTH=0.000 FLAT_K64_D8=0.067
- `notes/research_drill_2x_hierarchical_planning_REVIVAL_2026-06-28.md` — revival drill (this morning); identifies options as natural HARD_FAIL pivot in TOP-3 candidates section
- `notes/research_drill_2x_hierarchical_goal_planning_primitive_stage3_2026-06-27.md` — v1 drill design (with Sutton-Precup 1999 cited)

**Substrate primitives composed (each MEASURED@ or HYPOTHESIZED@ tagged in research note section 2):**
- `hdlab/multi_hop.py` — `iter_cleanup_chain` chain-grade depth-15 (π implementation; MEASURED@ data/exp_r1_multihop_iterative_cleanup_v1)
- `hdlab/refuse_gate.py` — `calibrate_refuse_threshold` chain-grade V_REL=256 (β termination threshold; MEASURED@ data/exp_substrate_refuse_gate_v_rel_extension_v1); HYPOTHESIZED@ cosine-to-target reliability at composite depth — the load-bearing strain point
- `hdlab/store.py` (partition operations) — chain-grade M=10M (I initiation set; MEASURED@ data/exp_kv_learned_projection_m1m_v1)
- `hdlab/binding.py` — HRR bind/unbind (Plate 1995)
- Flat preplay primitive (cells/exp_substrate_preplay_beam_to_goal_v1*) — MIDDLE_BAND baseline for ARM_FLAT_PREPLAY_K128_D6

**META rail + cross-cell rail:**
- META_M7 REPRODUCE_PV2 5HOP @ 2000 bindings, band [0.08, 0.25] — mandatory ARM_REPRODUCE_RAIL

**Cross-thread coupling:**
- `data/exp_swr_preplay_constructive_hypothesis_generator_v1*` — if HP, SWR-noise-injected preplay can upgrade π rollout inside each option
- `data/exp_cortex_hippo_handoff_v1*` HP — option spec in hippo (fast write/read), option execution against cortex (W matrix); natural mapping for ANCHOR 1 HP follow-up
- `notes/research_drill_2x_online_learning_conversation_primitive_stage3_2026-06-27.md` — task_vector_kshot HP; option specifications could be task vectors

---

## Pre-registered thresholds (from research note section c — locked at dispatch)

**HARD_PASS_CHAIN_GRADE:**
- ARM_OPTIONS_FULL solve_rate ≥ 0.55 (composite depth-6 goals)
- ARM_OPTIONS_FULL − ARM_FLAT_PREPLAY_K128_D6 ≥ +0.15 (hierarchy lift discriminator)
- ARM_OPTIONS_FULL − ARM_OPTIONS_RANDOM_PI ≥ +0.40 (π load-bearing — the primary substrate-physics check)
- ARM_OPTIONS_FULL − ARM_OPTIONS_NO_BETA ≥ +0.20 (β load-bearing — secondary; if not met, options-without-learned-termination is still positive on mechanism class)
- median plan-length ≤ 2.0 × optimal
- META_M7 PASS
- CARDINALITY_OK (6 arms × 3 seeds × 50 goals = 900 units expected)
- cv across seeds ≤ 0.15
- SANITY: ARM_FLAT_PREPLAY in [0.20, 0.55] off-floor; ARM_RANDOM < 0.10

**HARD_PASS_PARTIAL (MIDDLE_BAND):** ARM_OPTIONS_FULL in [0.40, 0.55) AND lift over flat ≥ +0.10 AND lift over random_pi ≥ +0.25

**HARD_FAIL (locked, with THIRD-FAILURE GATE):**
- ARM_OPTIONS_FULL ≤ 0.20 → options framework dead at substrate's regime → THIRD consecutive HARD_FAIL on hierarchical-planning → close capability box; document closure in research note + cap_map; reframe M3 demo around non-hierarchical conversation classes
- ARM_OPTIONS_FULL within 0.05 of ARM_OPTIONS_RANDOM_PI → π not executing properly; bug in option-rollout, not framework; investigate before declaring HARD_FAIL
- ARM_OPTIONS_FULL within 0.05 of ARM_FLAT_PREPLAY → depth-6 too shallow; ship ANCHOR 2 (depth-12 extension) before declaring framework-level HARD_FAIL

**SANITY_BREACH:** ARM_RANDOM > 0.10 OR ARM_FLAT > 0.65 → regime wrong; redesign before reading mechanism arms.

**Discriminator-must-survive-scale (Fix #25):** smoke at full N=8192, composite depth-6, all 3 options active, all initiation banks fitted. Smoke must FIRE the discriminator, not just verify the cell runs.

---

## Compute formulas (in code, per discipline)

- Per option β cosine-threshold calibration: O(N_train_per_option × N) for in-dist + OOD scores; N_train_per_option=200 → ~3M flops → ~1ms per option × 3 options = ~3ms
- Per option I bank fit: O(K_anchor × N) per option; K_anchor=32 → ~260k flops → trivial
- Per goal planning step: I check (3 options × K_anchor=32 × N = 800k flops) + π rollout (8 max-steps × cleanup chain = 8 × 200k = 1.6M flops) + β check per step (cosine N = 8k flops × 8 steps = 64k) = ~2.5M flops per goal
- 6 arms × 3 seeds × 50 goals × ~2.5M = ~2.3B flops total = ~2s pure compute
- META_M7 rail: ~10min
- Total wall: ~15-30min remote_cpu smoke; ~1-2hr full

---

## META_RULE compliance summary

- **META_RULE_AL (encoding before readout):** option encoding (π/β/I as 3 separate channels) BEFORE planner readout. The 3-channel encoding choice IS the substrate-physics fix vs prior two cells' bundled-HRR approach.
- **META_RULE_AC (cross-thread cohabit):** drill targets v1 + revival root cause; leverages parallel SWR-preplay + task_vector_kshot + cortex_hippo_handoff landings; explicit cross-thread synthesis in research note.
- **META_RULE_AH (cardinality):** CARDINALITY_OK pre-reg field set; 900 expected units; HARD_FAIL_CARDINALITY_BREACH armed.
- **META_RULE_AF (discriminator-must-survive-scale):** smoke at full N=8192, composite depth-6, 3 options, all banks active.
- **Smoke discipline 1 (no silent except):** cell-author removes silent except blocks; halt + record failures (cos NaN, partition routing miss, refuse-gate calibration empty).
- **Smoke discipline 2 (smoke fires discriminator):** smoke verifies ARM_OPTIONS_FULL > ARM_OPTIONS_RANDOM_PI delta ≥ +0.20 at smoke regime (not full-pass; confirms direction).
- **Smoke discipline 3 (band-floor = MIDDLE_BAND not HARD_PASS):** if both ARM_OPTIONS_FULL and ARM_OPTIONS_RANDOM_PI end up below 0.10, verdict is MIDDLE_BAND not HARD_PASS.
- **Substrate-doesn't-know-anything compliance:** options encode substrate-native state representations (HRR cosines); no language tokens, no semantic priors. Substrate plans on its own state-space.

---

## Contract

- Cell-author spawn (exp_dev decides whether OPUS or SONNET; complexity = novel-composition of 3 CG primitives + new termination-detection mechanism)
- Per Fix #26 pre-dispatch verify-the-referent: `tools/predispatch_check.py substrate_hierarchical_options_v1` — confirm no prior chain-grade evidence (closest priors are v1 + revival HARD_FAIL anchors + flat preplay MIDDLE_BAND, none addressing options framework)
- Per Fix #14: ≤3 spawns in flight; this is a single anchor; no parallel options-variants until ANCHOR 1 lands
- Per Fix #17: cell-author smoke timing measured strictly (no `2>&1 | tail` subprocess monitoring; use file-redirect + mtime polling)
- Per Fix #21: poll filesystem for landing (find data -maxdepth 2 -name metrics.json -mmin -N every turn-cycle)
- Per Fix #24: route via overnight_queue ONLY IF cell becomes matmul-heavy at full N; smoke should stay on remote_cpu

## Autonomy declaration

exp_dev decides:
- Cell-author model selection (OPUS preferred per novel-composition; SONNET acceptable if budget tight)
- Smoke regime (N=8192 at composite depth-6 with all 3 options is the floor per discriminator-must-survive-scale; can extend depth or option count if smoke trivially passes)
- Full dispatch routing (remote_cpu_queue vs overnight_queue based on smoke wall-time)
- Bundle with other anchors if appropriate (ANCHOR 2 deep-composite is a natural HP extension; do NOT bundle ANCHOR 3 option-critic at this stage)

Research does NOT decide:
- Cell-file path, module imports, internal data structures (cell-author's call)
- Smoke wall-time budget (exp_dev's call; honest discount applied 20-40min)
- Whether to route via hdi_orchestrator (exp_dev's call based on smoke profile)
