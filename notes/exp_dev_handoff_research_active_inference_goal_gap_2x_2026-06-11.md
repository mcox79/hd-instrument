# exp_dev hand-off -- research: active_inference_goal_gap_2x

**Filed by:** research sub-agent (Sonnet 4.6)
**Date:** 2026-06-11
**Trigger:** notes/research_drill_active_inference_goal_gap_2x_2026-06-11.md
**Cycle context:** E1+E2 MIDDLE NEAR-MISS -- error_drop=70% (PASSES 30% threshold), goal_reach=0.63 (threshold 0.70; 7pp short). E1 pragmatic_value + E2 boredom-gamma confirmed working.

---

## Pause state block

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates and context pointers ONLY. Experiment design (HP choices, cell structure, code) is exp_dev's responsibility. Do not encode experiment design in this file.

---

## What the research found

E1+E2 are confirmed working (error_drop 20%->70%). The residual goal_reach=0.63 gap has a specific root cause: single-step EFE evaluation is myopic for multi-step tasks. Two converging mechanisms explain the 7pp shortfall:

1. Boredom (E2) over-explores NEAR the goal: when the agent approaches the goal, the goal state is repetitive (high boredom) which INCREASES exploration drive -- exactly backwards. A 3-line goal-proximity gate fixes this.
2. Single-step pragmatic value misses multi-step dependencies: DPEFE H=2 Bellman rollout adds 2-step lookahead at O(K^2) cost (tractable) and is the standard published fix for this failure mode.

Both fixes use existing substrate primitives (E1 forward prediction, E2 boredom signal, cleanup similarity). No new substrate mechanism needed.

---

## Anchor candidates (rank-ordered)

### Rank 1: active_inference_goal_dist_gate (Goal-distance gamma gate -- Tier 1 test)

**Pointer:** research note Section "Tier 1 test" and Stream B
**Substrate-product reading:** in E2 boredom-gamma, add a goal-proximity override -- when sim(current_state, goal_bundle) > threshold (near goal), freeze gamma at gamma_exploit (high). When far from goal, use existing E2 boredom-gamma modulation. This is the cheapest intervention and addresses the boredom-over-exploration-near-goal anti-pattern documented in IJCAI 2024 constrained intrinsic motivation work and arxiv 2602.11779.
**Tier hint:** EXPLORATORY (3 lines of modification; no new mechanism)
**Why now:** cheapest decisive test; directly addresses the documented failure mode; zero substrate machinery cost

Pre-reg:
- HARD-PASS: goal_reach >= 0.70 AND error_drop >= 0.65 (no regression on error_drop)
- MIDDLE_BAND: goal_reach in [0.67, 0.70] -- proceed to Rank 2
- HARD-FAIL: goal_reach < 0.61 (mechanism wrong; escalate to DPEFE)

---

### Rank 2: active_inference_dpefe_h2 (DPEFE H=2 Bellman rollout -- Tier 2 test)

**Pointer:** research note Section "Stream A: DPEFE" and "Tier 2 test"
**Substrate-product reading:** extend E1 action selection to 2-step Bellman rollout. For each candidate action a: predict s1 = forward(current, a); for each candidate action a2: predict s2 = forward(s1, a2), compute G_step2 = sim(s2, goal_bundle); then G(a) = sim(s1, goal_bundle) + gamma * max(G_step2). Select a = argmax G(a). Cost: O(K^2) evaluations -- at K=4, 16 calls vs 4 for H=1. Direct lit precedent: Paul et al. 2024 DPEFE; Nuijten et al. 2025 (arxiv 2504.14898) proves this is equivalent to variational inference on the generative model.
**Tier hint:** EXPLORATORY (20-line modification; existing forward model reused)
**Why now:** standard fix for single-step EFE myopia; lit-validated at horizon H=2-3; FHRR forward model accuracy at H=2 is 87.5% per arxiv 2602.21467

Pre-reg:
- HARD-PASS: goal_reach >= 0.70 AND error_drop >= 0.65
- MIDDLE_BAND: goal_reach in [0.67, 0.70] -- escalate to H=3 or multi-timescale V
- HARD-FAIL: goal_reach < 0.61 (forward model error compounds at H=2; check PP-267 accuracy)

---

### Rank 3: active_inference_goal_dist_dpefe (Goal-dist gate + DPEFE H=2 combined)

**Pointer:** research note Section "Tier 1 + Tier 2 combined"
**Substrate-product reading:** run both Rank 1 and Rank 2 modifications together. If Rank 1 alone is MIDDLE_BAND, the combined patch is the decisive test. Both modifications are independent and can be applied in the same cell.
**Tier hint:** EXPLORATORY
**Why now:** if Rank 1 alone gives goal_reach in [0.67, 0.70], dispatch Rank 3 in same CPU session rather than a new round

Pre-reg:
- HARD-PASS: goal_reach >= 0.72 (both fixes together should exceed threshold with margin)
- HARD-FAIL: goal_reach < 0.61 despite both patches (root cause is not lookahead depth; escalate to multi-timescale V)

---

### Rank 4: active_inference_episode_null_test (Episode length null test -- run first, free)

**Pointer:** research note Section "Stream F"
**Substrate-product reading:** run identical policy at 2x episode length. If goal_reach improves >= 0.05pp, temporal truncation is the bottleneck and all lookahead / gamma improvements are premature. This is a zero-code parameter change.
**Tier hint:** DIAGNOSTIC (not an anchor; a nullification test)
**Why now:** must rule out temporal truncation BEFORE spending CPU on Rank 1-3 to avoid building machinery for the wrong cause

Pre-reg:
- DIAGNOSTIC PASS (null confirmed): goal_reach does NOT improve with 2x episode length -> confirm policy quality issue -> proceed to Rank 1
- DIAGNOSTIC FAIL (null refuted): goal_reach improves >= 0.05pp -> episode length is the bottleneck -> fix episode length first, then re-test baseline

---

### Rank 5: active_inference_multiscale_v (Multi-timescale V -- escalation path)

**Pointer:** research note Section "Stream C"
**Substrate-product reading:** add V_slow buffer (rolling average over 30 steps) alongside existing V_fast (5 steps). Policy selects actions that maximize delta_slow = V_slow(s_{t+1}) - V_slow(s_t) gated by delta_fast >= 0. This adds the long-horizon goal-progress signal missing from the short-horizon E1 mechanism.
**Tier hint:** EXPLORATORY (30 min implementation; escalation only)
**Why now:** dispatch only if Ranks 1-3 are all MIDDLE_BAND; this is the third escalation tier

Pre-reg:
- HARD-PASS: goal_reach >= 0.70; V_slow converges within 50 episodes; V_slow correlates with goal proximity r >= 0.50
- HARD-FAIL: V_slow variance > 3x V_fast (slow estimate unreliable at tested episode count)

---

## Context pointers

- This research note: d:/AI/hd-instrument/notes/research_drill_active_inference_goal_gap_2x_2026-06-11.md
- Prior rescue note (cycle 224 full failure): d:/AI/hd-instrument/notes/research_drill_active_inference_rescue_2x_2026-06-11.md
- Prior exp_dev handoff (cycle 224): d:/AI/hd-instrument/notes/exp_dev_handoff_research_active_inference_rescue_2x_2026-06-11.md
- PP-272 (active inference loop): substrate_capability_map.md row PP-272
- PP-285 (multi-step active inference): substrate_capability_map.md row PP-285
- PP-267 (predictive coding residuals / forward model): substrate_capability_map.md row PP-267
- PP-315 (boredom signal / HHVG): substrate_capability_map.md row PP-315
- Key lit: arxiv 2504.14898 (EFE as variational inference / Bellman equivalence)
- Key lit: arxiv 2602.21467 (FHRR world model 2-step accuracy validation)
- Key lit: arxiv 2602.11779 (adaptive temperature as meta-policy; goal-dist gate precedent)

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

exp_dev may dispatch Rank 4 (null test) and Rank 1 in any order within the authorized CPU envelope. Ranks 2-3 are authorized as a batch if Rank 1 is MIDDLE_BAND. Rank 5 requires separate escalation. If Ranks 1-3 all MIDDLE_BAND, escalate to orchestrator with the MIDDLE_BAND result, citing this file and the research note.
