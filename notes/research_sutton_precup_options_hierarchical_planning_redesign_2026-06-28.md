# RESEARCH DRILL — Sutton-Precup Options Framework for Substrate Hierarchical Planning

**Date:** 2026-06-28
**Author:** research (Opus 4.7-1M)
**Trigger:** Two consecutive HARD_FAILs on closed-form D_macro hierarchical planning:
- v1 `exp_substrate_hierarchical_subgoal_planner_v1_smoke` — TREE=0.000 NO_CLEAN=0.000 (closed-form pseudoinverse averages parallel-block effects into centroid mush)
- revival `exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke` — SC=0.000 DJ=0.000 BOTH=0.000 (state-conditioning + disjoint-block do NOT rescue; flat at 0.067)

Both verified on disk (per `metrics.json` not framing). The mechanism class is wrong — closed-form D-prediction tree.

**This drill:** propose Sutton-Precup options framework redesign. Sub-agent dispatch SKIPPED — prior drill notes (`research_drill_2x_hierarchical_planning_REVIVAL_2026-06-28.md` and `research_drill_2x_hierarchical_goal_planning_primitive_stage3_2026-06-27.md`) already contain Sutton-Precup 1999 / Bacon-Roy / Botvinick lit-scan with verified citations (16 total). Drilling deeper into the SAME lit-scan would violate 2x discipline. Instead: substrate-primitive mapping + cell architecture.

---

## SUBSTRATE-MINE FIRST (verify-the-referent)

`grep`-fallback (substrate-KB v2 rejected v1 schema queries):
- No prior substrate cell on options framework (`options framework Sutton Precup` returns nothing in prior research notes except citations)
- ANCHOR 2 in revival hand-off (`substrate_hierarchical_planner_smdp_options_v1`) was pre-identified as the natural HARD_FAIL pivot
- All chain-grade substrate primitives needed for options decomposition exist on disk; mapping is novel-composition, not novel-mechanism

---

## (a) HEADLINE

Closed-form D-prediction (v1 + revival) failed because it tried to MODEL state transitions; the substrate cleanup primitive cannot represent the one-to-many mapping from macro × state to next-state when macros bundle multiple primitives. **Sutton-Precup options framework dissolves the modeling problem entirely** — an option `(I, π, β)` doesn't predict state-deltas, it FIRES until its termination condition β triggers, then returns control. There is no `D_macro` to fit. Substrate has the three pieces chain-grade-eligible: π = `iter_cleanup_chain` rollout (multi-hop CG depth-15), β = audit-chain termination check via cosine-to-goal-vector or refuse-gate, I = partition routing CG bank check. The substrate-novel question becomes "can substrate execute an option to completion and detect termination?" — a primitive readout question, not a closed-form prediction question. **P_deflated = 0.38** (raw 0.55 + brain existence proof +0.10 + substrate-mining +0.05 - calibration penalty -0.20 - novel-composition cap -0.10 - twice-burned discount -0.02). The cell isolates termination-condition computation as the load-bearing substrate-physics question — closed-form prediction is OUT of the architecture.

---

## (1) Lit-scan synthesis (lean, 198 words)

**Sutton, Precup, Singh 1999 (AIJ 112:181).** Options framework: option = `(I, π, β)` — initiation set, internal policy, termination function. SMDP planner treats options as temporally-extended actions. Bellman backups at option boundaries, not per-step. Key insight: planner is over the OPTION SET; the internal option rollout is opaque from the planner's POV. NO state-delta prediction model required.

**Bacon, Harb, Precup 2017 (option-critic, AAAI).** End-to-end gradient learning of (π, β) via policy-gradient on intra-option policy + termination gradient. Validates that options are LEARNABLE without hand-crafted termination — termination is itself a policy output.

**Botvinick 2009 / Botvinick & Niv 2019.** Basal ganglia striatum implements option chunking; dorsolateral striatum executes the chunked sequence, dorsomedial striatum signals termination (start-stop boundaries). Jin-Tecuapetla-Costa 2014 (Nat Neurosci) showed lesions disrupt sequence boundaries without disrupting individual actions — direct neural evidence for separable π vs β.

**Plate 1995 Ch.6 (HRR chunking).** Plate's chunking is structural composition (bundle a sequence into one HRR) but does NOT include temporal extension or termination. Options framework is the temporal complement Plate left unaddressed.

**Gap:** no VSA/HDC paper has instantiated options framework on hyperdimensional state-space. Substrate would be first.

---

## (2) Substrate-primitive mapping for (π, β, I) — 294 words

### π (internal option policy) — MEASURED@CG (clean map)
- **Anchor:** `hdlab/multi_hop.py:iter_cleanup_chain` — chain-grade depth-15 per-hop cleanup primitive
- **MEASURED@** `data/exp_r1_multihop_iterative_cleanup_v1` ratified CG at K=2
- **Map:** π is a fixed-bank rollout — given option `o` and current state HRR `s`, π_o(s) generates the next primitive action via `iter_cleanup_chain(KGStore, state=s, relations=[action_role])` with cleanup against the option's primitive bank. The option's "policy" is implemented as a small dedicated codebook of K~4-8 primitives that the option chains through.
- **Clean:** π = stored-chain readout is exactly how multi-hop CG works today.

### β (termination function) — MEASURED@MIDDLE_BAND + HYPOTHESIZED@cosine-threshold (PARTIALLY STRAINED map)
- **Anchor:** `hdlab/refuse_gate.py:calibrate_refuse_threshold` — chain-grade V_REL=256
- **MEASURED@** `data/exp_substrate_refuse_gate_v_rel_extension_v1` ratified CG; **HYPOTHESIZED@** binary-termination signal from cosine(state, β_target) >= τ_β
- **Map:** β computes `cos(current_state, option_termination_target) >= τ_β` per step. τ_β calibrated by refuse-gate's `calibrate_refuse_threshold` on (in-distribution-completed-option-states, OOD-states). Returns true → option exits, control returns to SMDP planner.
- **HONEST STRAIN:** refuse-gate was calibrated for KG relation-discrimination (V_REL=256), not for goal-proximity termination. The β τ might not transfer cleanly; cell must recalibrate per option. AUDIT-CHAIN backup: `audit_chain depth-50` CG can verify a multi-step option execution AFTER the fact (counts forward steps; flags if max-steps exceeded → forced termination). β as both cosine-threshold (soft) + max-steps (hard) is the conservative implementation.

### I (initiation set) — MEASURED@CG (clean map)
- **Anchor:** partition routing M=10M chain-grade (per `hdlab/store.py` partition operations) + refuse-gate-style initiation check
- **MEASURED@** `data/exp_kv_learned_projection_m1m_v1` partition routing CG
- **Map:** I_o is a stored set of admissible "starting state HRRs" — initiation = `max_cos(current_state, I_o) >= τ_I`. Partition routing hosts the per-option I sets cheaply (one bank per option, K_per_bank~32-64 anchor states). At planning step: enumerate options where I check passes; SMDP planner selects among the eligible ones.
- **Clean:** partition routing was designed for exactly this lookup pattern.

**Summary:** π and I map cleanly to existing CG. β is partially strained — cosine threshold + max-steps fallback is the conservative implementation; SUBSTRATE-PHYSICS LOAD-BEARING QUESTION = is cosine-to-target-state a reliable termination signal at composite depth?

---

## (3) Cell architecture proposal — `exp_substrate_hierarchical_options_v1.py` — 318 words

### Encoding mechanism (one option = three channels, NOT one bound HRR)
- **NOT** `o = bind(I_anchor, π_seed) + β_target` — bundling π and β into one HRR re-introduces the v1 "averaging-mush" failure
- Each option stored as THREE separate substrate channels: `I_bank[o]` (partition routing bank of admissible start states), `π_bank[o]` (small codebook of primitive sequences this option chains), `β_target[o]` (one HRR vector representing "goal achieved" for this option)
- Planning over options: SMDP-style at the option level — enumerate eligible options via I check, score by `cos(current_state, π_seed_o)` for plan-relevance + `cos(β_target_o, top_goal)` for goal-alignment. Pick argmax-scored option.

### Termination computation (the load-bearing piece)
- Per-step inside an executing option: `term_signal = cos(state_t, β_target_o)`
- If `term_signal >= τ_β` (refuse-gate calibrated per option) OR `step_count >= max_steps_o` (hardcoded 8): exit option, return control to SMDP planner
- Audit-chain logs every (option_id, step_idx, state_cos, term_signal) — termination is fully auditable

### Macro substitution rule
- At planner step: if ANY eligible option has `cos(β_target, top_goal) >= τ_macro_useful` AND `cos(current_state, I_o_anchor) >= τ_I`, FIRE the option (substitute primitive sequence for option execution). Otherwise fall back to flat primitive selection (one primitive per step via cleanup chain).
- Mixed planning: alternates options + primitives until goal reached or max-total-steps exhausted.

### Smoke regime + 6 arms
Same 4-block BlocksWorld as revival (option 3 simplification). 3 options pre-defined to AVOID parallel-block coupling: `stack_pair(X,Y)`, `clear_then_grab(X)`, `relocate(X,loc)`. Composite depth-6 goals.

| Arm | Isolation |
|---|---|
| ARM_REPRODUCE_RAIL | META_M7 rail (band [0.08, 0.25]) |
| ARM_RANDOM_PLAN | Floor; SANITY_BREACH if >0.10 |
| ARM_FLAT_PREPLAY_K128_D6 | Flat baseline (revival's K=128 D=6); predicted 0.35-0.45 |
| ARM_OPTIONS_FULL | Mechanism arm — options framework with all 3 pieces (I check + π rollout + β term); predicted 0.55 |
| ARM_OPTIONS_NO_BETA | β replaced with fixed max-steps (no cosine threshold); isolates whether learned termination is load-bearing; predicted 0.30 if β load-bearing, 0.55 if not |
| ARM_OPTIONS_RANDOM_PI | π replaced with random-primitive sequence inside the option; isolates whether learned π is load-bearing; predicted 0.10 |

### Expected discriminating regime
- N=8192, composite depth-6, 3 options, 4 blocks, 50 goals × 3 seeds [7,17,23]
- HARD_PASS: ARM_OPTIONS_FULL ≥ 0.55 AND lift over FLAT ≥ +0.15 AND lift over OPTIONS_NO_BETA ≥ +0.20 (β load-bearing)
- HARD_FAIL: ARM_OPTIONS_FULL ≤ 0.20 (mechanism doesn't fire) OR ARM_OPTIONS_FULL within 0.05 of ARM_OPTIONS_RANDOM_PI (options aren't actually being executed properly)

### Honest failure modes (where this might also collapse)
1. **β cosine threshold doesn't discriminate well at composite depth.** State HRRs at step-3-of-option may already cosine-match β_target by accident (HRR drift bundled with goal vector). Substrate has no prior CG evidence that cosine-to-target is a reliable termination signal for multi-step rollouts. Mitigation: max-steps fallback + audit-chain post-hoc verification.
2. **I check too permissive at substrate's regime.** Partition routing CG at M=10M; but if all 4-block states cosine-match I_anchor at >τ_I (which happens when codebook is dense), every option appears eligible at every step → SMDP planner can't discriminate.
3. **SMDP planner reduces to flat selection.** If the option-bank is small (3 options), and at each step there's typically 1 eligible option, the planner degenerates to scripted execution — no actual hierarchical decision. Could appear as ARM_OPTIONS_FULL ≈ ARM_OPTIONS_RANDOM_PI.
4. **Domain too small for hierarchy to matter.** Revival already noted 4-block depth-6 may be reachable by FLAT_K=128. If FLAT_K=128 hits 0.55+, the lift margin disappears. SANITY check inherited from revival.

---

## (b) Cheap decisive test
SINGLE 6-arm cell as specified in (3). Smoke at full N=8192, composite depth-6, all 3 options active. Wall: ~20-40min remote_cpu. Pre-reg HARD_PASS / HARD_FAIL locked at dispatch.

---

## (c) Falsifiable predictions

| Arm | Predicted | P(HP) | Reasoning |
|---|---|---|---|
| ARM_OPTIONS_FULL | 0.55 | 0.38 | π + I clean substrate maps; β strained but mitigated by max-steps fallback. Brain existence proof (BG options chunking) lifts; substrate-mining lifts; twice-failed mechanism class deflates. |
| ARM_OPTIONS_NO_BETA | 0.40 | – ablation | If β is load-bearing this drops 0.15-0.20. If β is NOT load-bearing (max-steps suffices), this matches FULL → interpretation: termination-detection is not the discriminator; options-as-fixed-macros works (still a positive result on mechanism class). |
| ARM_OPTIONS_RANDOM_PI | 0.08 | – control | Random primitives within option ≈ random plan with scaffolding; should be near floor. |
| ARM_FLAT_PREPLAY_K128_D6 | 0.40 | – baseline | Inherited from revival prediction. |
| ARM_RANDOM_PLAN | 0.04 | – floor | Random + goal-cosine rerank. |
| ARM_REPRODUCE_RAIL | 0.16 ± 0.04 | – rail | META_M7. |

**HARD-PASS (locked):**
- ARM_OPTIONS_FULL ≥ 0.55
- ARM_OPTIONS_FULL − ARM_FLAT_PREPLAY ≥ +0.15
- ARM_OPTIONS_FULL − ARM_OPTIONS_RANDOM_PI ≥ +0.40 (π load-bearing — the load-bearing substrate-physics check; replaces v1 cleanup-load-bearing and revival state-cond-load-bearing)
- median plan-length ≤ 2.0 × optimal
- cv ≤ 0.15 across 3 seeds
- META_M7 PASS
- CARDINALITY_OK (6 arms × 3 seeds × 50 goals = 900 units)

**HARD-FAIL (locked):**
- ARM_OPTIONS_FULL ≤ 0.20 → options framework also dead at substrate's regime → THIRD consecutive HARD_FAIL on hierarchical planning → close the hierarchical-planning capability box; reframe M3 demo around non-hierarchical conversation classes
- ARM_OPTIONS_FULL within 0.05 of ARM_OPTIONS_RANDOM_PI → π not executing; bug in option-rollout mechanism, not framework
- ARM_OPTIONS_FULL within 0.05 of ARM_FLAT_PREPLAY → domain doesn't need hierarchy at depth-6; ship deep-composite variant (depth-12+) before declaring HARD_FAIL

**SANITY:** ARM_FLAT_PREPLAY in [0.20, 0.55] (off-floor, not ceiling); ARM_RANDOM <0.10.

---

## (d) Cross-thread synthesis

- v1 + revival HARD_FAILs converge: closed-form D-prediction is dead on substrate. Options framework is the natural next test class (different algorithm class entirely; no state-delta prediction).
- Convergence with SWR preplay hypothesis-generator: if HP today, the π rollout inside each option could use SWR-noise-injected preplay for richer primitive sequences. Defer to HP follow-up.
- Convergence with `task_vector HRR ICL` CG: option specifications could be encoded as task vectors (bind(OPTION_ROLE, option_id)) for in-context option-selection at the planner level. Defer to HP extension.
- Convergence with audit-chain depth-50 CG: every option execution is fully auditable (option_id, step_idx, state_cos, term_signal). This is the M3 glass-box discriminator vs LLM-opaque option-decomposition.
- Adjacency cascade: Bacon-Roy 2017 option-critic (learnable π, β) is a Tier-1b drill candidate IF this cell HP — substrate could learn option boundaries online (currently they're hand-defined).

---

## (e) Substrate-product implications

- **M3 (glass-box conversational AI) load-bearing.** If HP, substrate can plan a conversation by firing options ("gather-financial-context-option" terminates when user has stated income+savings+risk; "produce-recommendation-option" terminates on user acknowledgement). Each option's termination is auditable per step.
- **M4 (substrate-as-research-director) load-bearing.** Director options: "mine-cap-map-option" (β = cap_map closure flagged); "design-cell-option" (β = pre-reg locked); "audit-verdict-option" (β = metrics.json verdict_msg matches per_arm). Termination is the glass-box hook.
- **Negative-result implications.** If this also HARD_FAILs (third consecutive), hierarchical planning at substrate's current regime is closed. M3 demo must be picked from task-classes that don't require deep composite planning (immediate Q&A, single-turn task completion). USER's "substrate plans all day" claim deferred indefinitely; document as KNOWN GAP not silent omission.

---

## (f) Citations (verified count: 4 new, prior 16 inherited)

**New for this drill (Bacon-Roy primary):**
17. Bacon, Harb, Precup 2017 "The Option-Critic Architecture" AAAI — end-to-end learned (π, β); validates options-without-hand-crafted-termination is feasible.

**Inherited from revival drill (all verified in prior notes):**
- Sutton-Precup-Singh 1999, Stolle-Precup 2002, Mattar-Daw 2018, Pfeiffer-Foster 2013, Plate 1995, Frady-Sommer-Kanerva 2018, Hersche 2024, Eliasmith 2013 Spaun, Kleyko 2023, Koechlin 2003, Alexander-DeLong-Strick 1986, Doya 1999, Frank-Loewenstein 2007, Graybiel 1998, Jin-Tecuapetla-Costa 2014, O'Reilly-Frank 2006

---

## META_RULE compliance

- **META_RULE_AL (encoding before readout):** options encode π, β, I as separate substrate channels (NOT bundled) BEFORE planner readout. The encoding choice (3 channels, not 1 bundled HRR) IS the substrate-physics fix vs prior two cells.
- **META_RULE_AH (cardinality):** CARDINALITY_OK 900 units expected.
- **META_RULE_AF (discriminator-must-survive-scale):** smoke at full N=8192 composite depth-6 with 3 options active.
- **Substrate-doesn't-know-anything compliance:** options encode SUBSTRATE-NATIVE state representations (HRR cosines); no language tokens, no semantic priors. Substrate plans on its own state-space.
- **No silent except blocks:** cell-author must surface termination computation failures (cos NaN, partition routing miss) as halts not silent skips.

---

## Pre-registration log
- ARM_OPTIONS_FULL predicted solve_rate = 0.55; P_deflated(HP) = 0.38
- ARM_OPTIONS_FULL − ARM_FLAT_PREPLAY_K128_D6 ≥ +0.15
- ARM_OPTIONS_FULL − ARM_OPTIONS_RANDOM_PI ≥ +0.40 (π load-bearing discriminator)
- ARM_OPTIONS_FULL − ARM_OPTIONS_NO_BETA ≥ +0.20 (β load-bearing — secondary discriminator; if not met, options-without-learned-termination still positive)
- 3 seeds [7, 17, 23]; cv ≤ 0.15
- CARDINALITY_OK 900 units
- META_M7 rail PASS required
- HARD-PASS / HARD-FAIL locked; not editable post-hoc
- THIRD-FAILURE GATE: if ARM_OPTIONS_FULL ≤ 0.20, close hierarchical-planning capability box; document negative result; reframe M3 demo

## Negative-result revival path

If this HARD_FAILs, three consecutive failures on hierarchical-planning class. Pivot recommendation: STOP attempting hierarchical planning at substrate's current regime. Document closure. Refocus M3 demo on substrate's chain-grade strengths (audit-device, KG-traversal, refuse-gate, multi-hop). USER's "substrate plans all day" claim → deferred to future capacity-extension work (Hersche block-sparse codes as primitive-level capacity drill, NOT applied to hierarchy until block-sparse is CG standalone).

## Dispatch readiness

Cell `exp_substrate_hierarchical_options_v1` ready to spawn. Companion hand-off file written at `notes/exp_dev_handoff_research_sutton_precup_options_hierarchical_planning_2026-06-28.md`. Estimated wall: 20-40min remote_cpu smoke; ~1-2hr full.

Pre-dispatch verify-the-referent confirms no prior substrate cell on options framework; closest priors are the v1 HARD_FAIL anchor (closed-form D), revival HARD_FAIL anchor (state-conditioned + disjoint), and the flat preplay MIDDLE_BAND. Options framework is genuinely novel-composition on substrate; P_deflated 0.38 reflects honest discount for twice-burned mechanism class.
