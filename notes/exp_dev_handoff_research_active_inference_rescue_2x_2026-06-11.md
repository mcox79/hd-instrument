# exp_dev hand-off -- research: active_inference_rescue_2x

**Filed by:** research sub-agent (Sonnet 4.6)
**Date:** 2026-06-11
**Trigger:** notes/research_drill_active_inference_rescue_2x_2026-06-11.md
**Cycle:** 224 MIDDLE_BAND (active_inference_lite: error_drop=20.5%, goal_reach=0.610)

---

## Pause state block

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates and context pointers ONLY. Experiment design (HP choices, cell structure, code) is exp_dev's responsibility. Do not encode experiment design in this file.

---

## What the research found

Cycle 224 MIDDLE_BAND exposes a well-known split in active inference: perception (minimize current F) and action (minimize expected G over future trajectory). The substrate implements only the perception side. Goal_reach=0.610 stalls because the policy does not evaluate expected free energy -- it has no mechanism to prefer actions that move toward the goal bundle vs. actions that merely reduce current prediction error.

Three root-cause mechanisms, ranked:
1. No expected free energy (EFE) term in action selection (pragmatic value missing)
2. No exploration-exploitation balance (fixed policy precision, no boredom-driven gamma)
3. No forward-model lookahead (cannot evaluate hypothetical action consequences before committing)

Lit precedents confirmed: VSA FHRR world models (arxiv 2602.21467) are a direct algebraic match. Boredom-driven exploration (PMC6349823 HHVG) has a direct substrate-native analog in PP-315.

---

## Anchor candidates (rank-ordered)

### Rank 1: active_inference_efe_patch (E1 -- FULL-FREE-ENERGY-GRADIENT-POLICY)

**Pointer:** research note Section E1
**Substrate-product reading:** upgrade active_inference_lite to compute pragmatic_value = similarity(predicted_next_state, goal_bundle) as part of action selection; add this term to the action score alongside current error reduction. This is a minimal patch to the existing anchor -- no new substrate mechanism.
**Tier hint:** EXPLORATORY (existing anchor rescue; PP-272/285 infrastructure valid)
**Why now:** cheapest decisive test; uses existing retrieval + similarity primitives only; single CPU session; directly addresses the measured gap

Pre-reg:
- HARD-PASS: goal_reach >= 0.70 AND error_drop >= 0.30
- MIDDLE_BAND: goal_reach in [0.65, 0.70]
- HARD-FAIL: goal_reach < 0.61 (wrong diagnosis; escalate to E3)

---

### Rank 2: active_inference_boredom_gamma (E2 -- BOREDOM-AS-EXPLORATION-DRIVE)

**Pointer:** research note Section E2
**Substrate-product reading:** integrate PP-315 boredom signal as a policy precision modulator; high boredom (repeated input) -> reduce gamma (explore); low boredom (novel) -> increase gamma (exploit). Arithmetic gate on existing mechanism, 3-line modification.
**Tier hint:** EXPLORATORY (PP-315 HARD_PASS; integration is arithmetic)
**Why now:** zero new substrate mechanism; PP-315 already runs; can stack on top of E1 in same CPU session

Pre-reg:
- HARD-PASS: goal_reach improvement >= 0.05pp vs E1-only baseline
- HARD-FAIL: boredom integration causes goal_reach regression below 0.610

---

### Rank 3: active_inference_efe_boredom_combined (E1+E2 joint)

**Pointer:** research note Ranked Anchor table, row 3
**Substrate-product reading:** run E1 and E2 together in one anchor; if E1 alone is MIDDLE_BAND, the combined patch is the decisive test.
**Tier hint:** EXPLORATORY
**Why now:** if E1 is MIDDLE_BAND (goal_reach in [0.65, 0.70]), combined patch avoids another dispatch round

Pre-reg:
- HARD-PASS: goal_reach >= 0.72
- HARD-FAIL: goal_reach < 0.61 despite both patches (escalate to E3/E5)

---

### Rank 4: active_inference_temporal_lookahead (E3 -- 2-STEP LOOKAHEAD)

**Pointer:** research note Section E3
**Substrate-product reading:** extend action selection to evaluate 2-step lookahead using PP-267 residual forward model + PP-285 multi-step chain; select action whose k=2 predicted state is most similar to goal bundle.
**Tier hint:** EXPLORATORY (more implementation than E1/E2 but uses existing PP-267+PP-285 primitives)
**Why now:** dispatch only if E1+E2 combined is MIDDLE_BAND; this is the escalation path

Pre-reg:
- HARD-PASS: goal_reach >= 0.72 with k=2
- HARD-FAIL: goal_reach < 0.61 (forward model error compounds)

---

### Rank 5: active_inference_td_error (E9 -- TD PREDICTION ERROR)

**Pointer:** research note Section E9
**Substrate-product reading:** implement TD(lambda) value function using cleanup margins as V(s) proxy; compute TD error delta_t = r_t + gamma * V(s_{t+1}) - V(s_t); policy selects action that maximizes positive delta_t. Uses PP-315 decayed buffer mechanism for rolling V(s) estimate.
**Tier hint:** EXPLORATORY
**Why now:** alternative path if E1/E2/E3 all MIDDLE_BAND; different mechanism (value function vs EFE)

Pre-reg:
- HARD-PASS: goal_reach >= 0.70; V estimates converge within 100 steps
- HARD-FAIL: V variance too high (divergence or oscillation)

---

### Rank 6 (longer-term): active_inference_world_model (E5 -- COMPOSITIONAL FORWARD MODEL)

**Pointer:** research note Section E5 and citations (arxiv 2602.21467)
**Substrate-product reading:** store (state, action, next_state) triples as bound FHRR tuples; retrieve predicted next state for any (state, action) query; use for full MBRL-style planning. Direct algebraic precedent in arxiv 2602.21467.
**Tier hint:** EXPLORATORY -> ESTABLISHED (pending HARD_PASS; lit precedent strong)
**Why now:** highest-leverage long-term investment (opens planning, counterfactual, MBRL); dispatch after E1-E5 rescue chain completes

Pre-reg:
- HARD-PASS: forward_model_accuracy >= 0.85 on held-out transitions; goal_reach >= 0.72
- HARD-FAIL: forward_model_accuracy < 0.70 (capacity cliff; K/N ratio problem)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_active_inference_rescue_2x_2026-06-11.md
- Cycle 224 verdict context: d:/AI/hd-instrument/notes/strategy_decisions_2026-06-10.md (search "active_inference_lite MIDDLE_BAND")
- PP-272 (active inference loop): substrate_capability_map.md row PP-272
- PP-285 (multi-step active inference): substrate_capability_map.md row PP-285
- PP-267 (predictive coding residuals): substrate_capability_map.md row PP-267
- PP-315 (boredom signal): substrate_capability_map.md row PP-315
- PP-318 (frisson/prediction-error-resolution): substrate_capability_map.md row PP-318

---

## Contract section

This hand-off is structural. The research agent identifies rescue mechanisms and ranked anchor candidates. The exp_dev agent owns:
- Cell structure and HP choices
- Code implementation
- Dispatch sequence and timing
- Verdict interpretation (report back to orchestrator/verdict_handler, not to research)

Research does NOT pre-specify code, cell boundaries, or runtime parameters.

---

## Autonomy declaration

exp_dev may dispatch E1 and E2 in any order or combined within the authorized CPU envelope. E3-E6 require separate authorization if E1+E2 are MIDDLE_BAND -- escalate to orchestrator with the MIDDLE_BAND result, citing this file.
