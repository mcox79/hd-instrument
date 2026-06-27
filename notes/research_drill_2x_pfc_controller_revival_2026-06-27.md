# 2X RESEARCH DRILL — PFC Controller Revival (HARD_FAIL smoke)

**Date:** 2026-06-27
**Author:** research (Opus 4.7-1M)
**Trigger:** `pfc_controller_per_step_operator_select_v1` smoke HARD_FAIL — lift=+0.030 (bar +0.15), PFC=0.59 vs Single=0.56, Random=0.01, Oracle=0.99, cv=0.085, n_seeds=2, depth=3.
**Diagnosis seed:** Mechanism shows weak directional signal (PFC > Random, PFC > Single by 0.03). Oracle=0.99 confirms +0.43 headroom exists — failure is in **controller**, not in **operator bank**. Cosine-argmax gate is leaking ~93% of available routing information.

---

## DRIFT-CHECK FIRST (per Fix #28)

Per-arm read: PFC=0.59 ± 0.05, Single=0.56 ± 0.06 — overlap intervals. PFC actually beats Random (0.01) by +0.58 so the gate is doing SOMETHING (it's not random), but the gain over a single fixed operator is within noise. **The honest reading:** controller has SOME signal but is far below what oracle says is possible. This is **revival-eligible, not abandonment-eligible** — the mechanism class works, the specific implementation is too lossy.

---

## ANGLE A — TIGHTEN THE GATING MECHANISM

### A1. Softmax-temperature gate w/ residual feedback (concrete)
Replace `op = argmax(cos(state, op_keys))` with `weights = softmax(cos(state, op_keys) / T); next = sum(w_i * op_i(state))`. Sweep T in {0.1, 0.3, 1.0}. At low T → approaches argmax; at moderate T → mixes top-2 operators per step. **Mechanism advantage:** preserves operator-similarity-rank information that argmax discards. Add residual `gate_input = state + alpha * prev_op_output` (alpha=0.3) so PFC reads its own trajectory — biologically grounded (recurrent PFC loop).
**Risk:** Soft mixing across operators may dilute each operator's effect; mitigation = sparse-top-2 (only mix top-2, zero others).
**P estimate:** 0.40 (lit-deflated; sparse-mixture-of-experts at K=2 has theoretical lift over argmax-K=1 ~0.05-0.15 in MoE literature; substrate-native variant uncertain).

### A2. Cosine-with-margin gate + abstain-fallback (concrete)
Fire selected operator ONLY if `cos(state, top_op) - cos(state, second_op) > margin` (margin=0.1). Otherwise fall back to identity / no-op (which preserves state) or to the best-of-4 single operator. **Mechanism advantage:** the cosine-argmax current failure mode is firing operators when the gate is uncertain — these "low-confidence misfires" pollute the trajectory. Abstain-on-uncertainty matches PFC's actual brain mechanism (gating uncertainty → withhold action).
**Risk:** Too much abstention degenerates to "single operator" arm; mitigation = log abstain-rate and require it stays in [0.1, 0.4].
**P estimate:** 0.45 (forward-only mechanism, no backprop needed, substrate-native, matches WM literature on confidence-gated action selection).

### A3. Learned operator-key attention with backprop (GPU)
Make `op_keys` trainable. Use HeadAttention(state) → softmax over op_keys → weighted sum. Train on (state, target) pairs from a small replay buffer. This is a real attention head — needs GPU + autograd. **Mechanism advantage:** the cosine-argmax assumes operators are well-aligned to state-space basis already; in practice substrate's encoding is char-trigram-shaped, NOT operator-aligned. Letting the gate LEARN its keys closes that gap.
**Risk:** Brings substrate closer to vanilla transformer attention — substrate-product purity violated; mitigation = constrain op_keys to substrate-bipolar space.
**P estimate:** 0.55 (high P because attention IS the brain's PFC mechanism; substrate-product cost = some non-substrate machinery).

---

## ANGLE B — RECONSIDER EXPERIMENTAL DESIGN

### B1. Depth-sweep extended to depth-15 with heterogeneous-density schedule (concrete)
Current smoke runs depth=3 — heterogeneous routing benefit grows with composition depth (each hop's "wrong operator" compounds). Run depth ∈ {3, 6, 10, 15} with the same 4-operator bank, single-vs-pfc-vs-random-vs-oracle arms. **Mechanism advantage:** if controller lift is depth=3:+0.03, depth=6:+0.08, depth=10:+0.15+ — the original cell would have HARD_PASS'd at depth=6+, and the smoke regime is the bug. Tests B = experimental-design failure not mechanism failure.
**Risk:** Compute cost grows ~linearly with depth; mitigation = use smoke N=2048 only.
**P estimate:** 0.50 (medium-high — heterogeneous composition lift IS supposed to scale with depth; current depth=3 smoke is in the saturation tail of single-operator).

### B2. Operator-bank heterogeneity stress test (concrete)
Current 4 operators may be too easy to distinguish OR too similar to discriminate. Sweep two regimes:
- **Easy regime:** 4 operators with very different action (orthogonal binding rotations)
- **Hard regime:** 4 operators where 2 pairs are near-degenerate (cosine 0.7 within pair, 0.1 across)
Single-operator baseline should DOMINATE in easy regime (low routing value) and PFC should LIFT in hard regime (high routing value). If neither regime shows lift, mechanism is broken; if hard regime shows +0.15 lift, the smoke chose wrong regime.
**Risk:** Hard regime may saturate cosine-gate to noise; mitigation = oracle bound check per regime.
**P estimate:** 0.40 (deflated — operator-distinguishability is a known confound; tests B-regime failure honestly).

### B3. State-representation upgrade to orthogonal-role-basis (concrete)
Drill RANK 3 from source was orthogonal-role-basis — current state-vec mixes role+filler in same subspace. Build state as `role_subspace ⊕ filler_subspace` (concatenated halves) and route gate ONLY on role-subspace. **Mechanism advantage:** the gate is asking "what operation to do" which is a ROLE question — cleanly separating role from filler in state-rep should sharpen gate decisions enormously.
**Risk:** Requires substrate-side change; touches partition-routing. Mitigation = run as A/B against current state-rep on PFC arm.
**P estimate:** 0.50 (theoretically strong; substrate-native; matches TPR / VSA-with-roles literature).

---

## TOP-2 REVIVAL CELLS (cross-angle, P-deflated)

### REVIVAL CELL 1: `pfc_controller_softmax_margin_abstain_v2` (Angle A1 + A2 combined)
**P=0.50 (deflated from 0.65)** — combines softmax-temperature mixing with margin-gated abstain.

**Hypothesis:** PFC controller HARD_FAIL was 93% information-loss at the cosine-argmax bottleneck. Replacing with (a) softmax-temperature mixing of top-2 operators when confident, (b) abstain (identity op) when margin < threshold, will close >50% of the oracle gap.

**Arms (4 mandatory + 1 diagnostic):**
1. ARM_PFC_COSINE_ARGMAX_V1 — original failed mechanism (regression check)
2. ARM_PFC_SOFTMAX_T03 — softmax mixing top-2 ops, T=0.3, no abstain
3. ARM_PFC_MARGIN_ABSTAIN — argmax + abstain-if-margin<0.1 (identity fallback)
4. ARM_PFC_SOFTMAX_MARGIN_COMBINED — both A1 + A2 (full mechanism)
5. ARM_DIAG_ORACLE — unchanged oracle bound

**Discriminator (META_RULE_K — fires at smoke):**
- HARD_PASS: COMBINED lift over SINGLE_OPERATOR_BASELINE >= +0.12 AND > COSINE_ARGMAX_V1 by >= +0.07 AND abstain_rate in [0.1, 0.4] AND cv < 0.10
- MIDDLE_BAND: lift in [+0.05, +0.12) OR partial component success
- HARD_FAIL: COMBINED <= COSINE_ARGMAX_V1 + 0.03 (mechanism didn't help) — mechanism class dead

**Fairness gates:** Same operator bank across arms (no shared-W; same seed → same operators). Same state-rep. Smoke FIRES discriminator at depth=3 AND depth=6 (per B1 insight). CARDINALITY_OK: 4 arms × 3 depths × 5 seeds = 60 units.

**Regime/anti-saturation:** Smoke at full N=8192 per Fix #22 (discriminator-must-survive-scale). Two depths (3, 6) in smoke to test B1 hypothesis cheaply.

**GPU:** NO — forward-only, no autograd. Runs on remote_cpu.

---

### REVIVAL CELL 2: `pfc_controller_depth_sweep_heterogeneity_sweep_v2` (Angle B1 + B2 combined)
**P=0.45 (deflated from 0.60)** — tests whether ORIGINAL v1 controller works at the right depth and right operator-distinguishability regime.

**Hypothesis:** Cosine-argmax controller IS sufficient — depth=3 smoke is in the saturation regime where single-operator works fine and routing has nothing to add. At depth>=6 with operator-bank in the HARD-distinguishability regime, the same cosine-argmax controller will lift >+0.15.

**Arms (3 mandatory across 2 sweep axes):**
1. ARM_SINGLE_OPERATOR_BASELINE
2. ARM_PFC_CONTROLLER_COSINE_ARGMAX (the SAME v1 mechanism — pure regime test)
3. ARM_DIAG_ORACLE

**Sweep axes:**
- depth ∈ {3, 6, 10, 15} (4 levels)
- operator_regime ∈ {EASY (orthogonal), HARD (near-degenerate pairs)} (2 levels)

**Discriminator (META_RULE_K):**
- HARD_PASS: PFC lift over SINGLE >= +0.15 at depth>=6 AND in HARD regime, cv<0.10 (proves regime hypothesis)
- MIDDLE_BAND: lift in [+0.08, +0.15) at depth>=6 OR HARD lifts but EASY saturates as predicted
- HARD_FAIL: PFC < SINGLE + 0.05 at ALL depth/regime cells (mechanism truly broken)

**Fairness gates:** Same N, same controller, only depth + regime vary. Single + Oracle re-baselined per regime (different operators = different ceiling). Cardinality: 3 arms × 4 depths × 2 regimes × 5 seeds = 120 units.

**Regime/anti-saturation:** Oracle bound MUST exceed 0.85 in every (depth, regime) cell — if Oracle saturates low, that cell is dropped from discriminator (not a fair test). Saturation-watch on single-operator: if SINGLE >= 0.95 at depth=3 EASY, that's the saturation-detected signal validating the regime-bug hypothesis.

**GPU:** NO — forward-only. Runs on remote_cpu (~4-6h full).

---

## SUMMARY / ROUTING

Both revival cells are honestly P~0.45-0.50 — neither is high-confidence-PASS, but together they discriminate the failure mode:
- If REVIVAL_1 PASS and REVIVAL_2 FAIL → mechanism was lossy (Angle A wins)
- If REVIVAL_2 PASS and REVIVAL_1 FAIL → original mechanism is fine, smoke regime was wrong (Angle B wins)
- If BOTH PASS → both fixes valid, compose them in v3
- If BOTH FAIL → PFC-controller class is dead at substrate; route to alternative (drill RANK 2 schema-replay, drill RANK 3 orthogonal-role-basis)

**Recommended dispatch order:**
1. REVIVAL_1 first (cheaper compute, sharper discriminator, fires at smoke)
2. REVIVAL_2 in parallel on remote_cpu (longer-running regime sweep)

**No GPU required for either** — both forward-only. If REVIVAL_1 HARD_FAIL, escalate to A3 (learned attention, GPU-required).

**Files:**
- This drill: `d:/AI/hd-instrument/notes/research_drill_2x_pfc_controller_revival_2026-06-27.md`
- Source HARD_FAIL: `d:/AI/hd-instrument/data/exp_pfc_controller_per_step_operator_select_v1_smoke/metrics.json`
- Original prereg: `d:/AI/hd-instrument/preregs/2026-06-27_pfc_controller_per_step_operator_select_v1.md`
- Source drill (5x multihop barrier): `d:/AI/hd-instrument/notes/research_drill_5x_multihop_barrier_2026-06-27.md`
- Prior K-scaling collapse evidence: `d:/AI/hd-instrument/data/exp_wave14_moe_attention_routing_v1/metrics.json` (K=4 retention=0.8 OK, K>=8 collapses — confirms E=4 safe in revivals)
