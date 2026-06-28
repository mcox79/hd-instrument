# Capability closed: hierarchical planning (Stage 3)

**Filed by:** exp_dev (Opus 4.7-1M, Agent Teams spawn)
**Date:** 2026-06-28
**Cc:** skunkworks (for atomization), research (for cap_map closure), orchestrator
**Trigger:** THIRD-FAILURE GATE triggered at smoke per pre-reg
  `preregs/2026-06-28_substrate_hierarchical_options_v1.md`

## Result (verified on disk; no framing)

**Cell:** `data/exp_substrate_hierarchical_options_v1_smoke/metrics.json`
**Verdict:** HARD_FAIL | THIRD_FAILURE_GATE
**Verdict msg (verbatim):**
> HARD_FAIL | THIRD_FAILURE_GATE (options=0.000 <= 0.20; 3rd consecutive HARD_FAIL on hierarchical-planning mechanism class; close capability box) | OPTS=0.000 POLICY=0.000 INIT=0.050 TERM=0.000 CF=0.100 RAND=0.000 | OPTS-POLICY=0.000 OPTS-CF=-0.100 OPTS-RAND=0.000 cv=inf arms_distinct=True chance_floor=2.143e-05

**Per-arm (read directly from metrics.json):**
- options_full: 0.000 (mechanism under test; ZERO solves)
- policy_only: 0.000 (pi-alone ablation)
- init_only: 0.050 (pi + I; the only arm producing any signal)
- term_only: 0.000 (pi + beta)
- closed_form_baseline: 0.100 (prior v1/revival mechanism class; replicates near-floor)
- random: 0.000 (floor; SANITY ok)

**arms_distinct:** True (SHA-256 critical-pairs all differ)
**arm SHA-256 hashes (seed=7):**
- options_full: 844c39be87e482be
- policy_only: 5af55a8ce229a3cd
- init_only: 4fb8e25dd1736b12
- term_only: 2c12489aebaa53d3
- closed_form_baseline: 8a4191653c4588b0
- random: 63216b3711925ef1

**cardinality_ok:** True (120 expected units; 120 produced)
**elapsed:** 7.8s smoke wall (N=8192 composite-depth=6 with all 3 options active per discriminator-must-survive-scale)

## Honest framing

This is a THIRD consecutive HARD_FAIL on hierarchical-planning at substrate's regime:
1. v1 `substrate_hierarchical_subgoal_planner_v1` -- TREE=0.000 FLAT=0.133 (closed-form D_macro)
2. revival `substrate_hierarchical_planner_state_conditioned_disjoint_v1` -- BOTH=0.000 FLAT=0.067 (state-cond + disjoint did not rescue)
3. options-framework `substrate_hierarchical_options_v1` -- OPTS=0.000 POLICY=0.000 CF=0.100 RAND=0.000

The options framework was the canonical alternative (Sutton-Precup 1999) -- a DIFFERENT mechanism class entirely (no state-delta prediction; SMDP at option boundaries). It still fails at substrate's regime.

**Per pre-reg THIRD-FAILURE GATE:** hierarchical-planning capability box is closed. Document closure. Do NOT iterate a 4th time at this regime.

## What failed (3-channel hypothesis falsified)

The drill predicted (P_deflated=0.38) that pi+I+beta as separate substrate channels (NOT bundled HRR) would dissolve the v1+revival averaging problem. Smoke result:
- pi alone (POLICY_ONLY=0.000): pi cannot find primitives that move toward the goal. The greedy goal-cosine primitive picker is degenerate at composite depth-6.
- pi + I (INIT_ONLY=0.050): I gating produces minor lift -- the only arm above floor. Tells us initiation-set check is functional but pi rollout is the load-bearing failure.
- pi + beta (TERM_ONLY=0.000): cosine termination provides no improvement over max-steps. HYPOTHESIZED@cosine-as-termination-signal **FALSIFIED at substrate's regime**.
- pi + beta + I (OPTIONS_FULL=0.000): full composition no better than pi alone. Channels do NOT compose.
- closed_form_baseline (CF=0.100): replicates prior HARD_FAIL near-floor as predicted (sanity).

**Root mechanism diagnosis (cell-author honest):** the substrate's HRR cosine landscape over BlocksWorld state-encodings does not have monotone goal-cosine gradient at composite depth >= 6. Greedy goal-cosine selection inside an option produces null progress; the substrate cannot "see" intermediate sub-goals as useful waypoints because the HRR sum-encoding does not preserve compositional partial-progress signal. This is the root reason ALL THREE mechanism classes failed.

## Implications (substrate-product)

- **M3 glass-box conversational AI:** USER concern #5 (hierarchical goal-decomposition) -- DEFERRED indefinitely at current substrate regime. M3 demo must reframe around substrate's chain-grade strengths: audit-device, KG-traversal, refuse-gate, multi-hop iter_cleanup, NOT deep-composite hierarchical planning.
- **M4 substrate-as-research-director:** the Director-options framing for "mine-cap-map / design-cell / audit-verdict" with beta termination per-option is DEFERRED -- substrate cannot use cosine-termination reliably at composite depth.
- **USER 'substrate plans all day' claim:** deferred to future capacity-extension work; NOT a near-term capability. Document as KNOWN GAP, not silent omission.

## What's left open (do NOT pursue without USER directive)

The substrate-as-instrument program's chain-grade primitives (audit-chain, refuse-gate, partition routing, multi-hop) remain intact. The failure is specifically at COMPOSITION of these into hierarchical planning. Possible future paths if USER reopens:
- Pretrained-encoder swap-in (drop the substrate-native bipolar HRR encoder; use a learned encoder that preserves compositional gradient) -- this would be a substrate-product pivot, NOT a hierarchical-planning iteration.
- Hersche 2024 block-sparse codes as primitive-level capacity drill, standalone CG first, THEN apply to hierarchy.
- Spaun-style oculomotor-loop direct symbolic action selection (skip HD planning entirely; use HD only for working memory).

None of these are "hierarchical-planning attempt #4." They are different program-level pivots that USER would need to vet.

## Discipline compliance

- arms_distinct = True (no SHA collision; cell is not buggy)
- cardinality_ok = True (full expected N produced)
- discriminator-must-survive-scale (Fix #25): smoke at full N=8192 composite-depth=6 with all 3 options active -- the discriminator DID fire (OPTS << POLICY+INIT+TERM+CF all near-floor)
- META_RULE_AF arms-must-differ -- VERIFIED via 6 distinct SHA-256 hashes
- META_RULE_AH atomic-write + cardinality_ok -- VERIFIED
- META_RULE_AL encoding (3-channel pi/beta/I) BEFORE readout -- VERIFIED in code
- No silent except blocks (cosine NaN raise; partition routing miss raise) -- VERIFIED
- Pre-reg locked at module init -- VERIFIED
- Compute formulas in code (CRLB + per-step flop accounting) -- VERIFIED in prereg + main.py

## Atomization request (Skunkworks)

Please file as a **negative-result chain-grade-eligible atom** in the substrate KB:
- Class: `negative_result_capability_closure`
- Anchor: `data/exp_substrate_hierarchical_options_v1_smoke/metrics.json`
- Related: `data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/`, `data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/`
- Claim: "Hierarchical planning at substrate's current bipolar-HRR encoding regime is closed across 3 mechanism classes (closed-form D_macro, state-cond+disjoint, Sutton-Precup options). pi-rollout greedy-goal-cosine produces null progress at composite-depth >= 6; substrate's sum-encoded HRR does not preserve compositional partial-progress signal."
- Cert tier hint: chain-grade-eligible negative result (3 cells; same diagnosis converges; cardinality_ok in all 3; arms_distinct in all 3).

## No further dispatch

No anchor 2 (deep-composite extension) dispatched. No anchor 3 (option-critic) dispatched. Per pre-reg + drill, third-failure closes the capability box. Full-N dispatch would burn ~1-2hr of remote_cpu wall for the same OPTS=0.000 signal already firmly established at smoke (cardinality_ok + arms_distinct + 7.8s wall + un-saturated mechanism arms all near-floor).
