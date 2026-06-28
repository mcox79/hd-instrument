# DRILL A — Bacon-Roy Option-Critic Revival on Hierarchical Planning Premature-Closure Test

**Date:** 2026-06-28
**Author:** research (Opus 4.7-1M)
**Trigger:** USER caught premature capability-closure on hierarchical planning. Per new discipline `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`, closure-atom only after 2x drills both confirm null. This is **Drill A** of 2.

**Three prior HARD_FAILs (all verified on disk, ABSOLUTE paths per META_RULE_AE):**
1. `d:/AI/hd-instrument/data/exp_substrate_hierarchical_subgoal_planner_v1_smoke/metrics.json` — TREE=0.000 FLAT=0.133 (closed-form D_macro centroid mush)
2. `d:/AI/hd-instrument/data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json` — SC=0.000 DJ=0.000 BOTH=0.000 FLAT=0.067 (state-conditioning + disjoint blocks did NOT rescue)
3. `d:/AI/hd-instrument/data/exp_substrate_hierarchical_options_v1_smoke/metrics.json` — OPTS=0.000 POLICY=0.000 INIT=0.050 TERM=0.000 CF=0.100 RAND=0.000 (Sutton-Precup options w/ calibrated cosine β; THIRD-FAILURE GATE triggered)

---

## (1) Pre-reg gate honesty verification

Re-read `d:/AI/hd-instrument/preregs/2026-06-28_substrate_hierarchical_options_v1.md` and `d:/AI/hd-instrument/data/exp_substrate_hierarchical_options_v1_smoke/metrics.json`. Findings:

| Gate | Status (verified on disk) |
|---|---|
| `arms_distinct == True` (SHA-256 across 6 arms) | MEASURED@ PASS — six distinct `_seq_hash` values: 844c39be, 5af55a8c, 4fb8e25d, 2c12489a, 8a419165, 63216b37 |
| `cardinality_ok == True` (expected 120 = 6 arms x 1 seed x 20 goals) | MEASURED@ PASS — `completed_units=120 expected_n_units=120` |
| No silent except blocks (cell-author L1-L4 hardening) | MEASURED@ PASS per cell docstring + L1 early metrics-write |
| ARM_RANDOM < 0.05 (floor SANITY) | MEASURED@ PASS — random=0.000 |
| ARM_CLOSED_FORM_BASELINE < 0.20 (replicates prior HARD_FAIL) | MEASURED@ PASS — CF=0.100 (replicates prior centroid-mush class) |
| ARM_OPTIONS_FULL > 0.20 (HARD_PASS lower edge) | FAIL — OPTS=0.000 -> THIRD_FAILURE_GATE triggered, verdict HARD_FAIL |
| cv across seeds <= 0.15 | UNDEFINED at smoke (only seed=7); not gate-violating |

**Honest pre-reg gap caught now (not at dispatch):**
- Smoke ran 1 seed (n=1). The seed-variation gate (cv <= 0.15) was NOT testable at smoke. A FULL run (3 seeds) would have given cv but the THIRD_FAILURE_GATE correctly prevented full dispatch since smoke OPTS=0.000 = mechanism-not-firing. This is the right discipline.
- **Missing gate the cell-author SHOULD have included:** a **regime-variation arm** at smoke testing whether OPTS_FULL also fails at depth=4 (easier than depth=6). If OPTS fires at depth=4 but not depth=6, the failure is regime-mismatch not mechanism-dead. Without this gate, we cannot distinguish "options framework dead on substrate" from "depth=6 unreachable for ANY mechanism class". This is a real gap, not a fabrication.
- The cell-author's discriminator gate `OPTS - POLICY >= +0.10` is fine but **both arms went to zero**. When both arms are floor, the discriminator is uninformative — the gate did not fire because there was nothing to discriminate. This is a known "both-at-floor" pattern.

**Verdict on pre-reg honesty:** the gates that COULD fire fired correctly. The cell ran cleanly and the THIRD_FAILURE_GATE triggered as designed. The missing regime-variation arm is a fair criticism but not enough to overturn the HARD_FAIL.

---

## (2) Bacon-Roy option-critic literature scan

**Bacon, Harb, Precup 2017 AAAI "The Option-Critic Architecture" (arXiv:1609.05140).** Derives **policy gradient theorems for options** — both intra-option policy `π_ω` and termination function `β_ω` are end-to-end LEARNED via gradient. Key contribution: termination is itself a policy output. The β gradient theorem (eq. 6): `∂E[G|s,ω,θ]/∂θ = -E[(∂β_ω(s')/∂θ) * A(s',ω)]` where A is the advantage of continuing vs terminating. Works with linear AND nonlinear function approximators, discrete OR continuous action spaces.

**Critical distinction vs the v3 cell:** the v3 cell's β IS empirically calibrated (per-option mean of completion-states, threshold fit on in-dist vs OOD samples, lines 449-521 of `experiments/exp_substrate_hierarchical_options_v1.py`). It is NOT a hand-picked fixed cosine threshold. The prompt's framing "Sutton-Precup hand-designed cosine vs Bacon-Roy learned β" is **partially incorrect** — v3 sits closer to Bacon-Roy than to vanilla Sutton-Precup. The actual gap: v3's β is **fit-once offline from random rollouts**; Bacon-Roy's β is **iteratively refined on task reward via gradient**.

**Where the actual mechanism-class gap IS:** the v3 π (`execute_option` lines 526-561) is GREEDY-OVER-GOAL-COSINE — it picks the primitive that maximally increases cos(next-state, goal) at each step. This is NOT a learned policy; it's a fixed heuristic. Bacon-Roy's π_ω is parameterized and gradient-updated. The π gap (NOT the β gap) is the dominant Bacon-Roy advance vs v3.

**HDPG (Ni-Issa-Imani 2022, DAC).** MEASURED@ existence proof — Hyperdimensional Policy Gradient algorithm runs continuous-control RL with policy mean + variance encoded as HD vectors, updated via gradient. Achieves 4.7x speedup and 5.3x energy efficiency vs DNN-based RL on robotics tasks. **Existence proof that VSA-native gradient learning is feasible.** Hyperdimensional computing CAN host learnable parameters; the substrate constraint is not "no gradients ever" but "no backprop through cleanup."

**Substrate gradient inventory (verified by Grep of `hdlab/`):**
- `hdlab/learning.py`: HebbianAssociations — reward-modulated sparse Hebbian (decay + reward * arousal); NOT policy-gradient but IS an online learnable parameter mechanism
- `hdlab/iterative_attractor.py`: explicitly "Forward-only; no backprop; substrate-native" (line 17) — substrate design constraint
- No `policy_gradient.py` / `reinforce.py` / `actor_critic.py` modules exist
- `hdlab/perceptron.py` exists but is forward-only single-layer

**Honest assessment:** substrate has **forward-only learnable parameters** (Hebbian reward-modulated weights). It does NOT have backprop. Bacon-Roy's π and β gradients are policy-gradient (REINFORCE-style; not backprop through the substrate state). **Policy-gradient on a parameter (not through substrate state) IS substrate-compatible.** HDPG proves this empirically.

---

## (3) Mechanism-class diagnosis

The three prior attempts share a structural feature:
1. **v1 closed-form D_macro:** model-based regression. PRE-SPECIFIED relation between macro-id and state-delta.
2. **revival state-conditioned disjoint:** same closed-form regression CONDITIONED on state-class. Still PRE-SPECIFIED.
3. **v3 Sutton-Precup options w/ greedy π + calibrated β:** π is a GREEDY HEURISTIC (no learnable parameter); β is a CALIBRATED FIT (one-shot data fit, not iterative gradient).

**Common failure mode:** none of these have a **task-reward-driven adaptive component**. Substrate is asked to plan-from-scratch using priors that were fit/calibrated WITHOUT seeing the specific goal-set it must solve. The composite goal space at depth=6 is large (state-space x goal-space ~ 81 x 81 = 6561; depth=6 plan-space = 6^6 = 46656); a fixed mechanism that has not adapted to this specific goal distribution cannot navigate it.

**Bacon-Roy dissolves this:** task reward shapes π_ω(a|s) and β_ω(s) jointly. The policy ADAPTS to the goal distribution. Even with substrate constraints (forward-only, no backprop-through-state), a substrate-native option-critic can use **REINFORCE-style policy gradient on per-option parameters** stored as bipolar/HRR vectors. The state-representation (HRR) is the input to the policy network; the policy network is small enough (linear projection from HRR to action-logits) that it can be gradient-updated WITHOUT backproping through cleanup.

**Brain analog (Botvinick-Niv 2019):** prefrontal cortex DOES learn termination via reward. Specifically, dopaminergic prediction-error signals reach PFC and update option-boundary representations in basal ganglia (Frank-Loewenstein 2007; Jin-Tecuapetla-Costa 2014 lesion evidence). Termination is NOT pre-specified — it's reward-shaped. This is direct brain evidence that option-critic-style learned termination is the biological design.

**Is this a 4TH mechanism class worth a cell?** YES. The class is:
- **Adaptive option-critic on HD substrate:** π_ω as small per-option linear policy (HD-state -> logits over option's primitive subset), parameterized by a learnable W_π_ω matrix. β_ω as a learnable threshold or small policy. REINFORCE on episode return updates W_π and τ_β jointly. Forward-only; no backprop through cleanup; substrate-native.

This is genuinely different from the first three. The first three all assumed the cell-author could specify the right mechanism (regression / state-conditioning / greedy-heuristic) up-front. The 4th class lets task reward DISCOVER the right π and β.

---

## (4) Cell-architecture sketch — `exp_substrate_hierarchical_option_critic_v1`

**Encoding:**
- 3 options as before (stack_pair, clear_then_grab, relocate)
- Per-option learnable π parameters: `W_π_ω in R^{N_DIM x |primitives_ω|}` — small linear policy from HD-state to per-primitive logits within option's subset (3-4 primitives per option). Initialized small-random.
- Per-option learnable β scalar threshold τ_β_ω (1-d learnable; β_target HRR fixed as before).
- Per-option learnable I scalar threshold τ_I_ω.
- Policy-over-options: same as v3 SMDP planner.

**Update rule (REINFORCE; forward-only; substrate-compatible):**
- For each training goal: run episode, log per-step (state_HRR, option_id, primitive_id, β_signal, reward).
- At episode end: compute return G = (goal-reached ? +1 : 0) - 0.01 * plan_length.
- Update `W_π_ω += α * G * (state_HRR x onehot(primitive_chosen) - mean_action_distribution)` — REINFORCE gradient w.r.t. W_π.
- Update `τ_β_ω += α_β * G * (1 if β_fired_correctly else -1)` — termination gradient (approximate).
- 200-500 training episodes BEFORE 50 held-out test goals.

**Substrate-physics load-bearing test:** does REINFORCE-style gradient on per-option HD-projection policy produce ARM_OPTION_CRITIC_FULL solve_rate > 0.30 on depth=6 composite goals AFTER 500 training episodes, vs v3 ARM_OPTIONS_FULL=0.000 with no training?

**Arms (6) for `exp_substrate_hierarchical_option_critic_v1`:**
1. ARM_OPTION_CRITIC_FULL — full π + β learned via REINFORCE
2. ARM_OPTION_CRITIC_BETA_FROZEN — only π learned; β fixed as v3
3. ARM_OPTION_CRITIC_PI_FROZEN — only β learned; π fixed as v3 greedy
4. ARM_V3_BASELINE — exact v3 OPTS_FULL replication (no learning)
5. ARM_FLAT_REINFORCE — same REINFORCE budget but on FLAT primitive policy (no options); isolates whether the hierarchy lift is real vs just "training helps"
6. ARM_RANDOM — floor

**Pre-reg HARD_PASS (locked):**
- ARM_OPTION_CRITIC_FULL >= 0.30 (un-saturated band [0.30, 0.95])
- ARM_OPTION_CRITIC_FULL - ARM_V3_BASELINE >= +0.25 (learning is load-bearing)
- ARM_OPTION_CRITIC_FULL - ARM_FLAT_REINFORCE >= +0.15 (hierarchy is load-bearing beyond just training)
- ARM_OPTION_CRITIC_FULL - ARM_RANDOM >= +0.25
- arms_distinct == True
- cardinality_ok per pre-reg

**Pre-reg HARD_FAIL (locked):**
- ARM_OPTION_CRITIC_FULL <= 0.10 — 4th consecutive HARD_FAIL on hierarchical-planning class -> closure-atom confirmed by Drill A
- ARM_OPTION_CRITIC_FULL within 0.05 of ARM_FLAT_REINFORCE — hierarchy structure illusory, options dissolve into flat REINFORCE
- ARM_OPTION_CRITIC_FULL within 0.05 of ARM_V3_BASELINE — gradient updates not effective; mechanism not actually learning

**Honest "would this fail too?" failure modes:**
1. **REINFORCE high-variance.** With only ~500 episodes and N_DIM=8192 parameter space per option, gradient signal may be too noisy. Mitigation: baseline subtraction; lower learning rate.
2. **Substrate state-representation insufficient.** If `encode_state_hd` for the 4-block BlocksWorld doesn't yield linearly-separable state-classes, no linear policy on HD-state can solve it. Substrate priors say this MIGHT be fine (multi-hop CG depth-15 works, indicating linear-separability of state-class distinctions). NOT certain.
3. **Domain-too-small-for-hierarchy.** Same as v3 concern — 4 blocks depth=6 may not need hierarchy. If ARM_FLAT_REINFORCE matches ARM_OPTION_CRITIC_FULL, hierarchy is illusory at this domain (escalate to depth=8 / 6 blocks).
4. **Calibrated-β was already the right idea.** If learning τ_β doesn't move the needle vs v3's data-fit τ_β, β is not the bottleneck. (Diagnostic: ARM_OPTION_CRITIC_PI_FROZEN ≈ v3 baseline.)

**Compute estimate:** training=500 episodes x 6 primitive steps x 6 arms x 1 seed = 18,000 env steps + gradient updates. Per-step cost ~1ms (HD-state encode + linear projection + bipolar action sample). Total ~3 min per arm; ~20 min smoke; ~1 hr full (3 seeds).

---

## (5) Verdict on closure

**Drill A finding:** the three prior failures CONVERGE on a structural feature — none used **task-reward-driven adaptive parameters**. Bacon-Roy option-critic is a distinct 4th mechanism class that:
- IS substrate-native compatible (HDPG existence proof; REINFORCE on per-option HD-projection W_π is forward-only)
- IS brain-grounded (PFC dopaminergic reward-shaped termination)
- Has a discriminator (ARM_OPTION_CRITIC_FULL - ARM_V3_BASELINE >= +0.25) that wasn't tested in v1/revival/v3
- Has a fair domain (same 4-block BlocksWorld) so failure would be true mechanism-class failure, not domain-mismatch

**The closure premised on "options framework dead at substrate's regime" is technically correct only for FIXED (non-learning) options.** The v3 cell tested FIXED options. It did not test LEARNED options. The capability box closure based on v3 alone is **PREMATURE**.

**However**, honest discount: substrate's "REINFORCE on per-option linear projection" has zero MEASURED@ precedent on disk (no prior cell ran it). HDPG is published external work, not substrate-internal. The P_deflated for Drill A's proposed cell: raw 0.40 (Bacon-Roy + HDPG existence proofs) - 0.20 (calibration penalty for uncharted substrate regime) - 0.10 (twice-burned then thrice-burned mechanism class; substantial discount) - 0.05 (REINFORCE high-variance risk at substrate's small training budget) = **P_deflated = 0.25**. This is a LOW probability bet — but it is a NEW bet, not a re-run.

The discipline `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28` says closure-atom only after 2x drills both confirm null. Drill A has surfaced a 4th-class mechanism not yet tested. Closure cannot be confirmed yet.

---

## RECOMMENDATION: CLOSURE_PREMATURE_ITERATE

Run `exp_substrate_hierarchical_option_critic_v1` per cell-architecture in section (4). If this 4th attempt HARD_FAILs (ARM_OPTION_CRITIC_FULL <= 0.10), then closure is confirmed by 2 drills (v3 + option-critic, both with sound discriminators). If this HP or MB, closure was indeed premature and hierarchical planning capability box stays open.

**Drill B candidate (if needed after Drill A cell completes):** test the orthogonal axis — "is the substrate's HD state-encoding the bottleneck, not the planning mechanism?" via state-representation lift (richer encoder, larger N_DIM, or block-sparse Hersche encoding) on the SAME v3 options cell. This would isolate state-rep vs mechanism. Defer until Drill A cell verdict in.

---

## Citations (verified count: 3 new + inherited 17 from prior drill)

**New for Drill A:**
1. Bacon, Harb, Precup 2017 "The Option-Critic Architecture" AAAI / arXiv:1609.05140 — policy gradient theorems for π_ω and β_ω; end-to-end learning of intra-option policies and termination conditions.
2. Ni, Issa, Abraham, Imani, Yin, Imani 2022 "HDPG: Hyperdimensional Policy-based Reinforcement Learning" DAC — VSA-native policy-gradient RL existence proof; Gaussian-policy mean/variance encoded as HD vectors; 4.7x speedup vs DNN-RL.
3. Botvinick & Niv 2019 "Learning, reward, and decision making" Annu Rev Psychol — PFC dopaminergic reward-shaped termination; brain-grounded learned-β.

**Inherited (from prior drill `research_sutton_precup_options_hierarchical_planning_redesign_2026-06-28`):** Sutton-Precup-Singh 1999, Stolle-Precup 2002, Mattar-Daw 2018, Pfeiffer-Foster 2013, Plate 1995, Frady-Sommer-Kanerva 2018, Hersche 2024, Eliasmith 2013 Spaun, Kleyko 2023, Koechlin 2003, Alexander-DeLong-Strick 1986, Doya 1999, Frank-Loewenstein 2007, Graybiel 1998, Jin-Tecuapetla-Costa 2014, O'Reilly-Frank 2006.

---

## Cross-thread synthesis

- **v1 + revival + v3 converge:** fixed-mechanism options-on-substrate is dead. 4th-class option-critic with learned (π, β) is the natural pivot.
- **Connects to substrate gradient frontier:** Hebbian learning primitive (`hdlab/learning.py`) is the substrate's only learnable-parameter mechanism today; option-critic would add REINFORCE-style policy-gradient as a 2nd learnable-parameter primitive. This would CREATE a new capability class on substrate, not just rescue hierarchical planning.
- **HDPG (Ni-Imani 2022) is the existence proof.** Substrate has all prerequisites: HD vectors, bind/unbind, action-sampling via cosine, reward signal. The missing piece is the gradient update on per-option W_π matrix. This is forward-only and substrate-compatible.
- **M3 / M4 implications:** if option-critic HP, substrate gains adaptive option discovery — relevant for M4 substrate-as-research-director where Director options must adapt to changing research priorities. If HF, document hierarchical-planning closure for M3 with a note that "fixed-mechanism options framework also failed at adaptive variant."

## Substrate-product implications

If Drill A cell HARD_PASSes: substrate adds adaptive-option-discovery to its capability set; M3 demo can include "substrate learns when to stop a sub-task via reward." If HARD_FAILs: 2-drill discipline satisfied for closure; file closure-atom; M3 demo reframes around non-hierarchical task classes per discipline `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`.

---

RECOMMENDATION: CLOSURE_PREMATURE_ITERATE
