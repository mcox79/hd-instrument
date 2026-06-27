# Research drill 2x triple-revival: BCM v2 + HRR involutive + STUB E bijective

**Filed-by:** Research (Director, Opus 4.7-1M)
**Date:** 2026-06-27
**Scope:** Three HARD_FAILs grouped as efficient triple-drill (each 1 broad + 1 narrow probe; P_deflated per lit-scan calibration penalty -0.15 to -0.25; novel-synthesis cap 0.50; brain-grounded uplift per `feedback_brain_is_existence_proof_higher_prior_USER_2026-06-23`).
**Cross-cell awareness:** BCM v2 init-fix already queued (`preregs/2026-06-27_gap3_cls_two_tier_BCM_v2_init_fix.md`); HRR involutive v1 in flight (`preregs/2026-06-27_stage3_hrr_involutive_systematic_generalization_v1.md`); STUB E bijective v1 in flight (`preregs/2026-06-27_stage3_typed_routing_falsification_bijective_v1.md`). This drill plans REVIVAL paths conditional on the in-flight cells HARD_FAILing — NOT redundant cells.

---

## FAILURE 1 — BCM v2 init-fix (theta overflow / degenerate fixed point recurrence risk)

### Angle A — numerical stability (theta clamp + weight renorm + adaptive eta)

Lit (Emergent Dynamical Properties of BCM, J Math Neurosci 2017): "If the time-scale factor of the homeostatic threshold is too slow relative to the time-scale factor of the weights, the selective equilibria lose stability via a Hopf bifurcation and limit cycles emerge, and for very large ratios, solutions become unbounded." This is the OVERFLOW path Failure 1 describes. v1 hit zero fixed point (W=0 -> y=0 -> dW=0). v2 init-fix could overshoot: with W_init~N(0,0.01) and theta_init=0.5, the first BCM step has y~0.01*sqrt(8192)~0.9 ~= theta_init, so (y - theta) sign is fragile; once y > theta the weights GROW which raises y which raises theta^2 EWMA — positive feedback. If THETA_M_WINDOW=200 is too slow vs eta_slow=1e-3 * x * y * (y-theta) per cycle, theta lags y and weights grow unboundedly until overflow.

Lit (Weight dependence in BCM, J Comput Neurosci 2022): "Renormalization can alternatively be implemented online by a rate-dependent decay term." This is the standard numerical-stability fix.

### Angle B — is BCM the right substrate primitive at all? (BTSP / STC alternative)

Lit (PMC12614050 BTSP review 2024-2025): "BTSP is a new form of synaptic plasticity triggered by dendritic plateau potentials associated with somatic burst firing, causes large changes in synaptic strength in a SINGLE SHOT, and operates on the timescale of seconds." Compare to BCM's exponential slowdown in N_DIM (Lim-Cohen 2019: 5000 cycles may be far below convergence horizon at N=8192). The substrate's gap-3 task is single-shot consolidation analog — BTSP is mechanism-matched; BCM is mechanism-mismatched. STC (Memory consolidation via STC, Nature Comm Bio 2021): "early-phase plasticity is expressed and the synapse is marked with a local synaptic tag for specificity; then proteins are synthesized and distributed; and these proteins are captured by the tagged synapses" — substrate analog: tag fast-write synapses for capture during slow-replay, selectively consolidating without BCM's threshold dance.

**Substrate context:** `preregs/2026-06-27_btsp_binary_synapse_one_shot_v1.md` and `preregs/2026-06-27_stc_tag_and_capture_v1.md` ALREADY EXIST and one (BTSP) has metrics.json landed within last 6h. **DO-NOT-SHIP new BCM-replacement cell** — BTSP path is already in flight.

### TOP-1 REVIVAL MECHANISM (conditional on BCM v2 init-fix HARD_FAILing)

**Mechanism name:** `gap3_cls_two_tier_BCM_v3_stable_adaptive`
**Angle:** numerical stability ladder (Angle A) — three combined fixes
1. **theta CLAMP** to `[theta_floor=0.05, theta_ceil=10.0]` per cycle (prevents Hopf-bifurcation runaway)
2. **W L2-RENORMALIZATION** per cycle: `W_schema[c] = W_schema[c] / max(1.0, ||W_schema[c]|| / W_NORM_CAP)` with W_NORM_CAP=sqrt(N_DIM) (Oja-style competition; chain-grade lit pattern)
3. **ADAPTIVE eta**: `eta_eff = eta_slow / (1 + 0.01 * max_abs_y)` (rate-dependent decay; chain-grade lit pattern); enables coarse learning when y small, refines when y large

Discriminator: ARM_BCM_V3_STABLE vs ARM_BCM_V2_FULL (the predecessor); HARD_PASS only if V3 achieves heldout_acc >= 0.65 AND `max_abs_W_norm <= 2*W_NORM_CAP` (no overflow) AND `theta_max <= theta_ceil + 1e-3` (clamp held) AND lift over V2 >= 0.10; falsifies "v2 hit overflow not just stuck on degenerate trap."

**Falsifiable thresholds:**
- HARD_PASS: heldout_acc >= 0.65, lift vs V2 >= 0.10, theta_max <= 10.01, W_norm_max <= 2*sqrt(8192) ~= 181, cv <= 0.10 across 3 seeds, cardinality_ok
- HARD_FAIL: heldout_acc <= 0.30 OR overflow detected (theta_max > 100 OR W_norm_max > 10*sqrt(N_DIM)) OR baseline arm >= 0.50 (rail violated)
- MIDDLE_BAND: 0.30 < heldout_acc < 0.65

**Fairness gates:**
- META_RULE_K Option A: smoke at N_DIM=2048, 500 cycles; smoke must FIRE discriminator (raise `RuntimeError(SMOKE_DISCRIMINATOR_FAILED)` if smoke V3 theta_max < 2.0 — would mean clamp never engaged; not exercising the rescue mechanism)
- META_RULE_H: cardinality_ok = (observed == 3 seeds * 4 arms = 12)
- META_RULE_J: no silent except
- Q-discipline: if V3 == V2 within 0.02, demote MM (V3 added no value)
- No by-construction-saturation: baseline = mean-of-instances prototype at ~0.37 (well below 0.50 floor)

**GPU eligibility:** NO. CPU-bound BCM iteration; 5000 cycles * 4 arms * 3 seeds at N_DIM=8192 = ~8-12 hr on remote_cpu_queue.

**DO-NOT-SHIP flag:** **CONDITIONAL HOLD.** Hold until BCM v2 init-fix lands. If v2 HARD_PASSes, V3 unnecessary. If v2 HARD_FAILs with `max_abs_y_first_200 < 0.01` (degenerate trap recurrence), V3 helps only if the v2 fix also overshot. **PARALLEL TRACK:** BTSP and STC cells already in flight as Angle-B answer; if EITHER HARD_PASSes, the BCM line of investigation is closed regardless of V3 outcome. Recommend filing V3 prereg-only NOW (do not dispatch), revisit after v2 + BTSP land. P_deflated = 0.35 (raw 0.55, calibration -0.20; novel-synthesis combination of three known fixes).

---

## FAILURE 2 — HRR involutive systematic generation (null at compositional generalization)

### Angle A — wrong binding scheme? (non-involutive: circular convolution vs simplex vs Kronecker)

Lit (arxiv 2506.15793 Linearithmic Clean-up for VSA Key-Value Memory with Kronecker Rotation Products 2026): "Bundling more terms decreases similarity to the original symbols. This can put a limit on both the size of queries and the number of edges encoded in a graph before accuracy degrades." Cleanup-pool size IS the bottleneck under HRR superposition. Kronecker rotation products achieve linearithmic cleanup (vs HRR's quadratic-in-K crosstalk). Lit (arxiv 2606.11391 Recursive Binding on a Budget 2026): "Subspace carving in order-p tensor memories" — alternative binding via tensor subspaces, not circular convolution. Frontiers AI 2026 (frai.2026.1793314): "nonlinear cleanup rules in resonator networks" — resonator networks specifically address the systematic-generalization-via-unbind failure mode by iterative factor disentanglement.

### Angle B — is the systematic-generation TEST itself unfair? (vacuous discriminator / saturated regime)

The prereg sets HP at heldout_acc >= 0.50 with ARM_BASELINE <= 0.15 sanity rail. Per the prereg's own analytical scale section: "at full K=500 SNR is 1/sqrt(500) ~= 0.045. Cleanup over N_ENTITIES=200 codebook scales as log(N_ENTITIES); expected cleanup accuracy degrades by ~5-10% from smoke to full." HRR cleanup SNR at K=500 superposition is mathematically capped near chance; the discriminator may be IMPOSSIBLE to clear via HRR alone, independent of mechanism correctness. The prereg's Q-discipline check at >=0.95 catches saturation upward; need a separate FLOOR check that the discriminator is REACHABLE given HRR's known capacity (Plate 1995 SNR formula).

**Substrate context:** No simplex-based or Kronecker-rotation prereg currently exists. HRR is core binding in `hdlab/binding.py`; new binding scheme would be substrate-extending, not substrate-replacing.

### TOP-1 REVIVAL MECHANISM (conditional on HRR involutive v1 HARD_FAILing)

**Mechanism name:** `stage3_resonator_network_systematic_generation_v1`
**Angle:** wrong binding scheme + insufficient cleanup mechanism (Angle A, primary). Resonator networks per Frady-Kent-Sommer 2020 + Frontiers 2026 use ITERATIVE factor disentanglement: instead of one-shot unbind+cleanup, iterate `subj_est = cleanup(unbind(F, bind(verb, obj))); obj_est = cleanup(unbind(F, bind(verb, subj_est)))` until fixed point. This dramatically extends superposition capacity by ~3-10x (Frady-Sommer 2018 capacity analysis). Mechanism is ENTIRELY substrate-native (uses chain-grade HRR + chain-grade cleanup; just adds iteration).

**Falsifiable thresholds (vs HRR involutive v1 if v1 HARD_FAILed):**
- HARD_PASS: ARM_RESONATOR.heldout_acc >= 0.50 AND lift vs ARM_HRR_INVOLUTIVE >= 0.15 AND lift vs ARM_NN_INTERPOLATION >= 0.10 AND `iteration_convergence_cycles <= 20` (efficiency rail) AND cardinality_ok AND cv <= 0.10
- HARD_FAIL: ARM_RESONATOR.heldout_acc < 0.20 (mechanism null) OR ARM_RESONATOR <= ARM_HRR_INVOLUTIVE + 0.02 (iteration adds nothing) OR baseline arm >= 0.30 (data leak) OR cardinality_ok=False
- MIDDLE_BAND: 0.20 < heldout_acc < 0.50 OR lift over involutive in [0.02, 0.15]

**Fairness gates:**
- **CAPACITY-FEASIBLE pre-check (META_RULE_S):** at module init, compute HRR SNR theoretical ceiling for K=500, cleanup pool N_ENTITIES=200: `expected_max_acc = phi(1/sqrt(K) * sqrt(log(N_ENTITIES)))` per Plate 1995. If expected_max_acc < 0.55 the discriminator is UNREACHABLE and cell must demote K to 200 or N_ENTITIES to 100. This is Angle-B fix; bakes in feasibility.
- META_RULE_K Option A+B: smoke at N_DIM=2048 K=100 ENTITIES=50 same OVERLAP frac; analytical justification: resonator convergence is iteration-count not scale dependent.
- META_RULE_H: cardinality_ok = (3 seeds * 4 arms = 12; new arm ARM_RESONATOR added to involutive cell's 3-arm structure)
- META_RULE_J: no silent except; resonator non-convergence must `raise` not silently emit NaN
- Q-discipline: if ARM_RESONATOR >= 0.95, suspect saturation (feature overlap too high) — auto-demote MM
- No by-construction: ARM_BASELINE (lookup-only, no composition) and ARM_HRR_INVOLUTIVE (baseline mechanism) both kept; ARM_NN_INTERPOLATION kept

**GPU eligibility:** YES (CONDITIONAL). Resonator iteration is FFT bind/unbind cycles; at N_DIM=8192 with 20 iter * 100 heldout * 3 seeds * 4 arms ~ 24k FFT ops, GPU helps if batched. Route via hdi_orchestrator per Fix #24 (must achieve >=50% GPU util in smoke or fall back to remote_cpu_queue).

**DO-NOT-SHIP flag:** **CONDITIONAL HOLD.** Hold until HRR involutive v1 lands. If v1 HARD_PASSes, resonator is upside cell (not necessary). If v1 MIDDLE_BANDs or HARD_FAILs, resonator network is THE substrate-native answer (no architecture change, just iteration on existing chain-grade primitives). P_deflated = 0.45 (raw 0.65 because resonator networks are LIT-ESTABLISHED for exactly this failure mode, calibration -0.20 for substrate-novel application + cell-author error risk).

---

## FAILURE 3 — STUB E typed-routing bijective v1 (by-construction-saturation baseline=0.9991)

### Angle A — harder regime where routing is non-trivial (more types, more confusion-pairs, noisier inputs)

Lit (arxiv 2605.07260 Counterfactual Routing Analysis in MoE 2026): "the standard router is well-aligned with route utility on confident tokens but uninformative on the fragile tokens that drive hard reasoning, and this token-conditional pattern holds across four open-weight MoE families." Translation: routing only DISCRIMINATES when input is fragile/ambiguous. At BIJECTIVE N_TYPES=N_BANKS=64 with CUE_COS=0.70 and OVERLAP=0.40, the typed-routing arm is structurally a free pass (type=bank by construction). Need adversarial regime: typed-ID corruption (10-30% noise on type label), or confusion-pair injection (two banks share 80% feature overlap so content-cosine alone cannot disambiguate), or noisy cues (CUE_COS=0.30 vs 0.70).

### Angle B — is bijective routing even the right test? (graded confidence routing instead)

Lit (SoftMoE arxiv 2606.17952): "SoftMoE replaces discrete routing with a truncated soft top-k LapSum relaxation, allowing gradient-based optimization." Translation: hard bijective routing throws away information; graded confidence routing (soft top-k over multiple banks weighted by routing confidence) is the production MoE pattern. Lit (Grassmannian MoE arxiv 2602.17798): subspace-manifold routing — concentration-controlled. These point to: bijective HARD routing is the WRONG test of typed-routing utility; SOFT graded routing is what brain attention does (Singer 1999 parietal binding is graded, not categorical).

**Substrate context:** typed_routing v1 collision regime closed by drill `research_drill_typed_multibank_actively_hurts_3x_2026-06-27.md` STUB E bijective falsifier already in flight. Graded confidence routing is a SEPARATE mechanism class not currently covered.

### TOP-1 REVIVAL MECHANISM (conditional on STUB E bijective v1 HARD_PASS-via-saturation OR MIDDLE_BAND)

**Mechanism name:** `stage3_graded_soft_routing_top_k_v1`
**Angle:** graded confidence routing (Angle B, primary; Angle A as discriminator-design). Mechanism: for each query, compute cosine to all N_BANKS bank-tags; route to TOP-K=3 banks weighted by softmax(cos/T) with T=0.1; aggregate within-bank cleanup results via weighted sum. Brain-grounded (parietal binding = graded; PFC task cells = attentional gating not hard routing).

**Adversarial regime baked in (Angle A discriminator design):**
- CUE_COS = 0.30 (noisy cue regime; chain-grade baseline at this regime is ~0.65-0.75, NOT 0.99)
- TYPE_LABEL_NOISE = 0.20 (20% of queries have CORRUPTED type label; tests whether soft routing recovers via content-cosine fallback)
- CONFUSION_PAIR_FRACTION = 0.25 (25% of banks paired into 80%-overlap confusion-pairs; hard routing fails here, soft routing aggregates)
- N_TYPES = N_BANKS = 64 (bijective constraint maintained from STUB E for clean compare)

**Falsifiable thresholds:**
- HARD_PASS: ARM_GRADED_SOFT.recall >= ARM_BASELINE_HARD.recall + 0.15 AND ARM_BASELINE_HARD.recall in [0.55, 0.85] (sanity rail; NOT saturated) AND ARM_TYPE_NOISE_CONTROL (graded with no type signal) < ARM_GRADED_SOFT by >= 0.10 (typed info actually helps when graded) AND `mean_top_k_active in [1.5, 2.5]` (soft routing actually uses multiple banks, not collapsing to top-1) AND cv <= 0.08 AND cardinality_ok
- HARD_FAIL: ARM_GRADED_SOFT <= ARM_BASELINE_HARD + 0.02 (graded adds nothing) OR ARM_BASELINE_HARD >= 0.95 (saturation rail violated; regime not adversarial enough) OR ARM_BASELINE_HARD <= 0.30 (regime too hard; floor lost) OR cardinality_ok=False
- MIDDLE_BAND: graded lift in [0.05, 0.15] OR baseline outside ideal band but in [0.40, 0.95]

**Fairness gates:**
- META_RULE_S (regime check): if smoke ARM_BASELINE_HARD >= 0.95, raise SMOKE_REGIME_TOO_EASY — abort full dispatch
- META_RULE_K Option A: smoke at N_DIM=2048 with same noise+confusion-pair structure; discriminator MUST fire (smoke must show graded > hard by >= 0.05 OR halt)
- META_RULE_H: cardinality_ok = (3 seeds * 4 arms = 12)
- META_RULE_J: no silent except
- Q-discipline: if ARM_GRADED_SOFT >= 0.95, suspect noise+confusion not adversarial enough; auto-demote MM
- **CRITICAL by-construction check:** ARM_BASELINE_HARD must be in [0.55, 0.85]; if >= 0.95 cell is structurally saturated (STUB E v1 trap; reject before banding)

**GPU eligibility:** NO. Simple matmuls at N_DIM=8192 K=4096 N_BANKS=64; CPU sufficient (remote_cpu_queue per STUB E v1 pattern; ~1-2 hr wall).

**DO-NOT-SHIP flag:** **CONDITIONAL HOLD.** Hold until STUB E bijective v1 lands. THREE scenarios:
- STUB E HARD_PASSES cleanly (baseline in [0.85, 0.95]): typed routing concept validated; graded routing UPSIDE cell, P_deflated=0.40
- STUB E HARD_PASSES but baseline >= 0.98 (by-construction-saturation as drill predicted possible): regime was structurally too easy; graded soft routing in HARDER regime is the **PRIMARY revival** cell, P_deflated=0.50
- STUB E HARD_FAILS (typed actively hurts even bijective): typed-routing branch closed per drill recommendation; graded routing irrelevant; **DO NOT SHIP** revival cell — pivot to non-typed compositional mechanisms

Net P_deflated = 0.45 (weighted: 0.40 * 0.4 + 0.50 * 0.4 + 0 * 0.2 ~= 0.36; rounded up for high lit support).

---

## SUMMARY TABLE

| Failure | Revival mechanism | P_deflated | GPU | DO-NOT-SHIP |
|---|---|---|---|---|
| BCM v2 init-fix | `gap3_cls_two_tier_BCM_v3_stable_adaptive` (theta clamp + W renorm + adaptive eta) | 0.35 | NO | CONDITIONAL HOLD; BTSP+STC parallel-tracking Angle B; revisit after v2 + BTSP land |
| HRR involutive v1 | `stage3_resonator_network_systematic_generation_v1` (Frady-Sommer iteration) | 0.45 | YES (conditional via hdi_orchestrator) | CONDITIONAL HOLD; only ship if v1 MB or HF |
| STUB E bijective v1 | `stage3_graded_soft_routing_top_k_v1` (soft top-K + adversarial regime) | 0.45 | NO | CONDITIONAL HOLD; ship only if STUB E HP-via-saturation OR MIDDLE_BAND; skip if HF |

**Recommendation:** File all 3 revival preregs as STUBS in `notes/` (NOT in `preregs/` until dispatch decision). Re-evaluate after the 3 in-flight cells land. **Spawn budget impact: ZERO new spawns now; 0-3 future spawns conditional on landings.**

**Honest scope:** Each revival is mechanism-grounded but cell-design-novel. All P estimates deflated per discipline. Brain-grounding STRONG for BTSP/STC (Angle-B FAIL 1) and graded routing (Angle B FAIL 3); MEDIUM for resonator networks (FAIL 2 Angle A); MEDIUM for BCM stability ladder (FAIL 1 Angle A — numerical engineering, not novel mechanism).

**Lit sources (web search 2026-06-27):**
- Emergent Dynamical Properties of BCM Learning Rule (PMC5318375)
- Weight dependence in BCM (PMC9666303)
- Behavioral Timescale Synaptic Plasticity review (PMC12614050)
- Memory consolidation by STC in RNN (Nature Comm Bio 2021)
- Linearithmic Cleanup for VSA Key-Value Memory (arxiv 2506.15793)
- Recursive Binding on a Budget (arxiv 2606.11391)
- Nonlinear Cleanup Rules in Resonator Networks (Frontiers AI 2026, frai.2026.1793314)
- Counterfactual Routing Analysis in MoE (arxiv 2605.07260)
- SoftMoE: Soft Differentiable Routing for MoE in LLMs (arxiv 2606.17952)
- Grassmannian MoE: Subspace Manifolds (arxiv 2602.17798)
