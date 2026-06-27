# 2X RESEARCH DRILL — PFC Controller v2 Depth-12 cv-Collapse

**Date:** 2026-06-27
**Author:** research (Opus 4.7-1M)
**Trigger:** pfc_controller_softmax_margin_abstain_v2 FULL HARD_FAIL at depth=12 (cv=0.249, lift=+0.152, mechanism halved from smoke).
**Diagnosis seed:** smoke at depth=6 was CLEAN HARD_PASS (SOFTMAX=0.383, cv=0.061). Full at depth=12 collapsed: SOFTMAX=0.156, cv=0.249, and ARGMAX (0.170) BEATS SOFTMAX. Partial-metrics inspection at depth=6 already shows abstain_rate=0.70 (above the 0.4 ceiling) — gate confidence was failing at the smoke depth and just hadn't crossed cv-bar yet. Depth=12 exposes the underlying fact.

---

## ZEROETH PASS — WHAT THE DATA ACTUALLY SAYS

Three orthogonal signals from the full result, not just verdict line:

1. **Mechanism magnitude HALVED** (0.383 → 0.156 from depth=6 to depth=12). Not noise; this is a systematic exponential-looking decay. Ratio 0.156 / 0.383 = 0.407, which is roughly the kind of number you get from (1-eps)^6 with eps in [0.13, 0.17].
2. **cv EXPLODED 4x** (0.061 → 0.249). Per-seed accuracy is now scattered. Random-router-like variance is creeping in not because the gate became random, but because the gate fires CORRECTLY some seeds and CATASTROPHICALLY some seeds — bimodal failure, not Gaussian degradation.
3. **ARGMAX > SOFTMAX at depth=12.** This is the diagnostic gem. The "smooth + top-2 + abstain" sophistication HURTS at deep regimes. It mixes errors instead of committing — and committing wrong once at depth=12 is actually better than spreading the error across two operators twelve times.

The smoke partial-metrics already showed the failure mode: at smoke-depth=6 the with_abstain arm fired identity 70% of the time. The smoke just classified that as "abstain working" — but 70% identity at depth=6 means at depth=12 you'd be abstaining ~95% (compounded), which is indistinguishable from "do nothing" — which IS the SINGLE_FIXED_OP_0 baseline.

This is a textbook **discriminator-must-survive-scale violation** (META_RULE_M, USER 2026-06-26). The smoke discriminator (cv ≤ 0.10 at depth=6) was satisfied not by mechanism strength but by smoke-depth-not-being-stressful-enough.

---

## ANGLE A — DEPTH-SCALING THEORY (why routing-quality decays exponentially)

The per-hop routing decision has an error probability eps. The chain succeeds only if EVERY hop routes correctly. P(chain) = (1-eps)^k.

Fit to data: with mechanism magnitude 0.383 at k=6 and 0.156 at k=12, and assuming a constant single-hop baseline ~0.005, the "lift above baseline" goes 0.378 → 0.152. Ratio 0.402. (1-eps)^6 = 0.402 → eps ~= 0.143. So roughly 14% per-hop error rate is consistent with both observations.

**This is fundamental, not mechanism-specific.** Brains hit it too. The literature solutions are well-known and converge on three families:

**A.1 — Bidirectional / meet-in-the-middle search.** Run depth=6 from start AND depth=6 from goal; intersect at the middle. Effective depth halves. Mechanism lift at apparent_depth=12 should recover to ~depth=6 numbers (~0.38). This is exactly what biological planning does (PFC builds forward + backward chains and merges). And it's standard in graph search (BFS-from-both-ends cuts complexity from b^d to 2·b^(d/2)).

  - **Substrate-native path:** the per-step gate is run twice: once on the current state moving forward, once on the goal-state hint moving backward via inverse-operator. The substrate already has inverse-binding (FHRR / HRR have well-defined unbind). When the two trajectories agree on an operator at any meeting hop, lock in that hop and recurse. Cost: 2x the encoder + a meet-test per hop. Cheap.

**A.2 — Error-correcting cleanup at each hop.** Drop in a Hopfield attractor or codebook-nearest-neighbor cleanup AFTER each operator application. eps drops from 0.14 to maybe 0.04 because the attractor maps small drifts back to clean states. (1-0.04)^12 = 0.61 — almost full recovery. This is the cortical-hierarchy mechanism from the 2026-06-10 biological-mechanisms drill ("ATTRACTOR-AT-EACH-LEVEL"). Substrate has Hopfield cleanup; it's only used at retrieval, not mid-trajectory.

**A.3 — Backward induction from goal (Bellman / dynamic programming).** Plan from goal backward via inverse-operators; the gate at each hop conditions on the planned-from-goal next-state. This restructures the routing problem so error doesn't compound across hops; each hop is a local decision conditioned on a known target.

Of these, **bidirectional is the cheapest substrate-native fix and has the cleanest falsifier.** A.2 is the next-best, slightly more substrate-coupled (needs per-level codebooks).

---

## ANGLE B — WHY SOFTMAX-BEATS-ARGMAX-AT-6 BUT LOSES-AT-12

Two regimes are at war:

- **Information-amplification regime (depth small).** The cosine landscape between state and operator-keys has soft slopes; the right answer is barely better than the wrong answer. Argmax throws away the gradient. Softmax preserves rank information and mixes top-K to spread the bet. With low error per hop and only a few hops, mixing top-2 reduces variance and lifts mean accuracy. Wins by +0.039 at depth=6.

- **Error-compounding regime (depth large).** Each softmax mix injects a second operator's noise into the trajectory. Over 12 hops that second-best-operator noise compounds. Argmax commits to one operator — if it's wrong, it's deterministically wrong, but the error doesn't BLEED into the trajectory. Argmax becomes more stable.

You can see this in the signal-to-noise math: softmax-mix-of-top-2 has SNR per hop equal to (top1 - top2) / sqrt(top1^2 + top2^2). If top2 cosine is close to top1 (which happens in the harder problems substrate hits at depth=12), softmax mixes ~50/50 and effectively becomes random-of-top-2 — that's 50% wrong-operator rate. Argmax picks top1 — wrong only when top1 itself is wrong (~14% per-hop).

**Substrate-physics interpretation:** at small depths, smooth routing is information-amplifying because the operator manifold's curvature is small and top-2 mixing samples the local optimum. At large depths, the trajectory enters regions where the cosine landscape between state and operator-keys is flat (mutually-confusable operators), and smooth routing becomes information-destroying — top-2 mixing samples noise.

**Substrate-native fix:** depth-adaptive routing. Use softmax for shallow hops (depth ≤ 6) and argmax for deep hops (depth ≥ 8). Mathematically: schedule T(k) = T_0 · (k_threshold / k) so T goes to 0 (argmax) as depth grows. Or, margin-gate per hop: if (top1 - top2) > margin, fire argmax; else abstain. The abstain rate is already 0.70 at depth=6 — the gate ALREADY KNOWS it's uncertain, the v2 mechanism just isn't acting on that information in a useful way (identity-fallback at 70% rate means most hops are skipped).

The cleanest single-cell discriminator: run pure-argmax v1 at depth=12 vs softmax v2 at depth=12 vs depth-adaptive v3 at depth=12. If pure-argmax beats both, the sophistication was the problem.

---

## TOP-2 REVIVAL CELLS (FALSIFIABLE, SHIP-READY)

### REVIVAL CELL 1: pfc_controller_bidirectional_meet_in_middle_v3

**Hypothesis:** Mechanism magnitude at apparent_depth=12 will recover to ~smoke depth=6 numbers (SOFTMAX ~0.35-0.40, cv < 0.10) when search is run from BOTH ends with meet-in-the-middle merge. The depth-decay is fundamental and the fix is to halve effective depth.

**Arms (5):**
1. ARM_FORWARD_ONLY_SOFTMAX_V2 (control: v2 at depth=12 — known HARD_FAIL, 0.156/0.249)
2. ARM_FORWARD_ONLY_ARGMAX (control: v1 mechanism at depth=12)
3. ARM_BIDIRECTIONAL_SOFTMAX (mechanism: 6 forward + 6 backward, meet-in-middle)
4. ARM_BIDIRECTIONAL_ARGMAX (mechanism: same but argmax gate)
5. ARM_DIAG_ORACLE (depth=12 ceiling)

**Discriminator (META_RULE_K, fires at smoke):**
- HARD_PASS: BIDIRECTIONAL_SOFTMAX accuracy ≥ 0.30 AND cv ≤ 0.12 AND lift over FORWARD_ONLY_V2 ≥ +0.12 (i.e. recovers >75% of the gap to smoke depth=6)
- MIDDLE_BAND: bidirectional lifts +0.05 to +0.12 over forward (mechanism partially works)
- HARD_FAIL: bidirectional ≤ forward + 0.03 (meet-in-middle is dead at substrate)

**Smoke-at-full-depth (Fix #22):** smoke runs at N=4096, depths={6, 12} (not {3,6}). Discriminator-must-survive-scale: smoke MUST fire at depth=12. If smoke-bidirectional at depth=12 doesn't lift, kill before full dispatch.

**Substrate cost:** uses existing FHRR-inverse for backward trajectories. ~2x compute of v2 (two trajectories). No GPU. Remote_cpu.

**Cardinality_ok:** 5 arms × 2 depths × 5 seeds = 50 units (full); 5 arms × 2 depths × 3 seeds = 30 (smoke).

**P estimate (lit-deflated):** 0.55. Bidirectional search is one of the oldest CS tricks; meet-in-middle has a half-century of proof. Substrate-native variant uncertain only at the "merge step" — how do we test that two trajectory states meet? Cosine threshold (e.g. cos > 0.7) is the obvious choice; if substrate-cosine ceiling at depth=6 is sufficient, this works. Brain-grounding (forward-backward PFC planning) raises prior. Capped at 0.55 (novel-synthesis cap).

---

### REVIVAL CELL 2: pfc_controller_depth_adaptive_argmax_v3

**Hypothesis:** Pure argmax at depth=12 will OUTPERFORM v2 softmax+abstain because v2's mechanism INJECTS top-2 noise that compounds. Depth-adaptive routing (softmax shallow, argmax deep) will be the global best.

**Arms (5):**
1. ARM_PURE_ARGMAX_V1 (v1 mechanism, baseline; expected to lift at depth=12)
2. ARM_SOFTMAX_V2 (control: known HARD_FAIL at depth=12)
3. ARM_DEPTH_ADAPTIVE_T_SCHEDULE (T(k) = 0.3 · (6/k); soft for k ≤ 6, hard for k > 6)
4. ARM_MARGIN_GATED_ARGMAX (fire argmax only if top1-top2 > 0.10; abstain otherwise)
5. ARM_DIAG_ORACLE

**Discriminator (META_RULE_K, fires at smoke):**
- HARD_PASS: ARM_PURE_ARGMAX_V1 or ARM_DEPTH_ADAPTIVE beats ARM_SOFTMAX_V2 by ≥ +0.05 at depth=12 AND cv ≤ 0.15 AND lift over SINGLE ≥ +0.10
- MIDDLE_BAND: ordering as predicted but lifts smaller
- HARD_FAIL: SOFTMAX_V2 still best at depth=12 (Angle B is wrong)

**Smoke-at-full-depth:** N=4096, depths={6, 12}. Both ARGMAX-class arms MUST be eval'd at depth=12 in smoke. Cardinality: 5 × 2 × 3 = 30 units smoke; 5 × 2 × 5 = 50 full.

**Substrate cost:** trivial (uses existing argmax + temperature scheduler). No new substrate primitives. No GPU.

**P estimate (lit-deflated):** 0.50. The diagnostic signal (lift_argmax = -0.014 at depth=12) is already direct evidence that argmax beats softmax at depth. This is essentially "rerun v1 at depth=12 and watch it win." Brain-grounded (PFC commits to discrete plans at deep planning, doesn't mix). Risk: pure-argmax may also decay (eps_argmax still ~0.14, so depth=12 still suffers); depth-adaptive may not improve over pure-argmax. Capped at 0.50.

---

## CROSS-CELL DECISION TABLE

- BIDIRECTIONAL PASS, ARGMAX FAIL → halving effective depth is the answer; ship REVIVAL_1 as v3
- ARGMAX PASS, BIDIRECTIONAL FAIL → smooth-mixing was the bug, not depth-decay; ship REVIVAL_2 as v3
- BOTH PASS → compose: bidirectional + depth-adaptive-argmax in v4 (each fixes a different failure mode; expected lift higher than either alone)
- BOTH FAIL → depth=12 is not substrate-tractable with current encoder; route to Angle A.2 (per-hop attractor cleanup) as next drill OR accept depth=6 as the operating regime

---

## DISPATCH ORDER

1. **REVIVAL_2 first.** Cheaper (no new substrate primitives), faster smoke (just re-runs v1 + temperature schedule at depth=12), most direct discriminator (lift_argmax was already -0.014 — confirm at smoke and immediately).
2. **REVIVAL_1 in parallel on remote_cpu.** Bidirectional needs inverse-operator integration and merge-test — slightly more substrate work; longer smoke. But it tests the more fundamental hypothesis.

Both forward-only, no GPU. Both run on remote_cpu via hdi_orchestrator (heavy: N=4096, multi-arm, multi-depth, 5 seeds — laptop CPU would take 8h+).

---

## TIES TO PRIOR WORK

- The biological-mechanisms drill (2026-06-10) called out "ATTRACTOR-AT-EACH-LEVEL" as the highest-value engineering target. Angle A.2 of this drill is the same recommendation, now triggered by direct empirical evidence at depth=12. If REVIVAL_1 + REVIVAL_2 both fail, A.2 becomes the immediate next cell.
- The v1 → v2 revival drill (2026-06-27 morning) chose Angle A (tighten gate). The v2 result is empirical proof that Angle A was insufficient at deep regimes — gating quality is not the whole story. This drill is its successor; the right answer was Angle B (depth-scaling math), not gate sophistication.
- META_RULE_M (discriminator-must-survive-scale, USER 2026-06-26) caught a fourth recurrence today. v2 smoke at depth=6 with HARD_PASS framing was the failure mode — the smoke discriminator was insufficient. Both revival cells in this drill ship with discriminator-fires-at-full-depth as a hard pre-reg requirement.

---

## FILES

- **This drill:** d:/AI/hd-instrument/notes/research_drill_2x_pfc_v2_depth12_cv_collapse_2026-06-27.md
- **Source HARD_FAIL (full):** d:/AI/hd-instrument/data/exp_pfc_controller_softmax_margin_abstain_v2/metrics.json
- **Source HARD_PASS (smoke):** d:/AI/hd-instrument/data/exp_pfc_controller_softmax_margin_abstain_v2_smoke/metrics.json
- **Partial showing abstain=0.70 at depth=6:** d:/AI/hd-instrument/data/exp_pfc_controller_softmax_margin_abstain_v2_smoke/partial_metrics_7.json
- **Predecessor drill (Angle A revival; v1 → v2):** d:/AI/hd-instrument/notes/research_drill_2x_pfc_controller_revival_2026-06-27.md
- **Biological-mechanisms support (ATTRACTOR-AT-EACH-LEVEL):** d:/AI/hd-instrument/notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
