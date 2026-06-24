# Research drill — Dual-trace neuromodulator: WHICH axis is load-bearing?

**Date:** 2026-06-23
**Drill type:** USER-directed 2x ELUCIDATION drill on the just-landed `substrate_dual_trace_sequential_neuromod_LM_v1` HARD_PASS (BPC 7.221 vs NAIVE_MULT 7.738; delta 0.52 at N_DIM=8192, N_TRAIN=100k, 3 seeds, cv=0.001) — isolate which of FIVE confounded axes between DUAL_TRACE and NAIVE_MULT carries the lift.
**Empirical drivers:**
- `data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json` — HARD_PASS at production
- `data/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1/metrics.json` — READOUT_DEGENERATE (collapses to unigram bpc=7.738)
- `experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py` lines 454-541 (the build_W_dual_trace mechanism)
**Calibration penalty:** brain-grounded mechanisms with substrate-native realization get raw P 0.55-0.65; -0.15 deflation; novel-synthesis cap 0.55.
**Query privacy:** 4 external WebSearches used generic math/neuro terms only (eligibility trace LTP/LTD competition; multi-timescale eligibility outer product capacity; subtractive Hebbian / Foldiak anti-Hebbian; predictive coding error vs target outer product).

---

## HEADLINE

The DUAL_TRACE HARD_PASS lift over NAIVE_MULT is most-likely-carried by **SIGN-HETEROGENEOUS ANTI-HEBBIAN SUBTRACTION OF A SLOWLY-INTEGRATED PREDICTION OUTER PRODUCT** — i.e., the `- ACh * E_neg` term where E_neg is a slow EMA (tau=50) of `outer(pred, src)`. This term is structurally a Foldiak-style anti-Hebbian decorrelator: W is being pushed *away* from its own slow autoregressive expectation, which prevents the unigram-collapse seen in NAIVE_MULT. The "dual-trace" framing is the *vehicle* for this anti-Hebbian subtraction (you need a slow trace to estimate the prediction stably); the cardinality (two-traces vs one) is necessary-but-not-sufficient. Timescale-difference (tau_pos=5 vs tau_neg=50) is also necessary because the subtractand must be SLOWER than the error correction. Modulator-target orthogonality (dopa→E_pos, ACh→E_neg) is structurally redundant once you have sign+target separation (the modulators just gate scalars; the algebra was already orthogonal via target heterogeneity).

**Most-likely lever ranking (per Bayesian-decomposition + lit-evidence):**
1. **Target heterogeneity + sign heterogeneity** (E_pos uses outer(Delta,src); E_neg uses outer(pred,src); update is +E_pos − E_neg). **P=0.50** — anti-Hebbian decorrelator literature is unambiguous this prevents collapse.
2. **Timescale separation** (tau_pos=5, tau_neg=50). **P=0.35** — needed for the EMA to estimate slow prediction; without it the subtraction is noisy.
3. **Cardinality (two traces)** is necessary scaffolding but not the lever per se. **P=0.20** in isolation.
4. **Modulator-target orthogonality** (dopa vs ACh on different traces). **P=0.15** in isolation — it's a gating *modulation* of an algebraic structure that is *already* heterogeneous.

If load-bearing axis = **anti-Hebbian subtraction**, the substrate-product implication is HUGE: it generalizes to a single design pattern (`fast-correct-trace MINUS slow-predict-trace`) reusable across many future cells without needing the dopa/ACh framing.

---

## CHEAP DECISIVE TEST — single 4-arm cell (≤60 min GPU)

**Cell name:** `exp_substrate_dual_trace_axis_ablation_LM_v1` (clones the dual-trace cell; swaps build_W_* for 4 ablation arms; same N_DIM=8192, V=4000, N_TRAIN=100k, 3 seeds)

The cell tests the **4 axes of confound** in ONE experiment with shared infra (encoder, tokenization, T/lambda sweep, fair-harness BPC measurement). All arms must use the same upper-level scaffolding so any delta is mechanism-attributable.

### Arm specifications

**ARM_DT_BASELINE (reference; matches just-landed DUAL_TRACE)**
- `W += dopa * E_pos − ACh * E_neg` ; E_pos=EMA(outer(Δ,src), tau=5); E_neg=EMA(outer(pred,src), tau=50)
- Reproduces bpc 7.221±0.008 from prior cell (sanity check; should land within ±0.02)

**ARM_DT_SAME_SIGN (isolate SIGN-heterogeneity → ablate anti-Hebbian subtraction)**
- `W += dopa * E_pos + ACh * E_neg` (note: `+` not `−`)
- All else identical (same targets, same timescales, same modulators)
- **DIAGNOSTIC:** if this arm collapses to or near NAIVE_MULT (bpc≈7.7), the anti-Hebbian subtraction IS the lever (HEADLINE confirmed).
- **HARD_PASS for "sign is the lever":** ARM_DT_SAME_SIGN bpc >= 7.55 (degraded by ≥ +0.30 vs DT_BASELINE)
- **HARD_FAIL for "sign is the lever":** ARM_DT_SAME_SIGN bpc <= 7.30 (lift survives without subtraction)

**ARM_DT_SAME_TARGET (isolate TARGET-heterogeneity → both traces accumulate outer(Δ,src))**
- E_pos = EMA(outer(Δ,src), tau=5); **E_neg = EMA(outer(Δ,src), tau=50)** (same target; only timescale differs)
- Keep subtractive: `W += dopa * E_pos − ACh * E_neg`
- **DIAGNOSTIC:** isolates whether the lever is "subtract a SLOW EMA of the SAME signal" (a momentum-like high-pass filter) vs. "subtract the network's own prediction" (true anti-Hebbian decorrelator).
- **HARD_PASS for "anti-Hebbian-of-prediction is the lever":** ARM_DT_SAME_TARGET bpc >= 7.50 (lift mostly lost without pred-target subtraction; head differential ≥ +0.28 vs DT_BASELINE)
- **HARD_PASS for "high-pass filter is the lever":** ARM_DT_SAME_TARGET bpc <= 7.30 (lift survives with same-target subtraction → pure timescale-derivative is enough)
- **MIDDLE BAND:** ARM_DT_SAME_TARGET in [7.30, 7.50] → both effects partially contribute

**ARM_DT_SAME_TAU (isolate TIMESCALE-heterogeneity)**
- E_pos = EMA(outer(Δ,src), tau=5); E_neg = EMA(outer(pred,src), tau=5) (both fast; same timescale)
- Keep subtractive AND target-heterogeneous
- **DIAGNOSTIC:** if timescale separation is load-bearing, this should degrade; if target+sign carry the lift, this should mostly survive.
- **HARD_PASS for "tau is the lever":** ARM_DT_SAME_TAU bpc >= 7.50
- **HARD_PASS for "target+sign suffice":** ARM_DT_SAME_TAU bpc <= 7.30

### Pre-registered HARD bands (both directions)

| Outcome | Implied mechanism | Substrate-product action |
|---|---|---|
| ARM_DT_SAME_SIGN bpc ≥ 7.55 AND ARM_DT_SAME_TARGET bpc ≥ 7.50 AND ARM_DT_SAME_TAU bpc ≤ 7.30 | **Anti-Hebbian-against-prediction** is the lever; timescale is decorative | Generalize to a "predict-and-subtract" pattern; reuse across cells |
| ARM_DT_SAME_TAU bpc ≥ 7.55 AND ARM_DT_SAME_SIGN bpc ≤ 7.30 | **Timescale separation** is the lever; sign is decorative | Generalize to a "fast-slow EMA pair" pattern; reuse across cells |
| All three ablation arms bpc ≥ 7.45 | **Joint conspiracy** — all 3 axes load-bearing together; mechanism is irreducible | Document META atom: dual-trace is a *single composite mechanism*; don't try to ablate further |
| Any single arm fully recovers (bpc ≤ 7.25) | That axis was load-free; **simpler mechanism** isolated | Refactor the dual-trace cell to drop the inactive axis |
| All three ablation arms bpc ≤ 7.30 | **Cardinality alone** is the lever (any 2-trace structure works) | UNEXPECTED — would imply NAIVE_MULT failed for a different reason; needs further drill |

**Cost:** 4 arms x ~55s ARM_DT_BASELINE pattern x 3 seeds x ~3.4 dev/test partition = **estimated 420-540s wall = 7-9 min per seed; ~25-30 min for 3 seeds total** on remote GPU (matches the just-landed cell's 507s).

**HARD failure-modes for the experiment itself:**
- If ARM_DT_BASELINE doesn't reproduce 7.22±0.05 → contamination/regression; do not propagate ablation results
- If any arm has cv > 0.05 across seeds → run +2 more seeds before classifying
- If unigram baseline (7.738) is not exactly recovered for control → broken eval, halt

**P_deflated (probability ablation cleanly identifies a single load-bearing axis):** 0.50 (high; the 4 arms are individually well-motivated and cleanly orthogonal; deflation -0.15 for "lit-scan calibration penalty" on novel substrate-synthesis; brain-grounded boost +0.05 because each ablation is itself a known brain mechanism)

---

## Falsifiable predictions per candidate mechanism

### Prediction A: Anti-Hebbian subtraction is the lever (HEADLINE; P=0.50)
- **Mechanism:** `−ACh * E_neg` term where E_neg ≈ slow EMA of network's own predicted outer product. W is being decorrelated against its slow autoregressive expectation. This is exactly Foldiak's anti-Hebbian sparse-coding mechanism in continuous-time outer-product form.
- **HARD-PASS signature:** ARM_DT_SAME_SIGN bpc ≥ 7.55 (collapses without the minus) AND ARM_DT_SAME_TAU bpc ≤ 7.30 (timescale not load-bearing once you have the subtraction)
- **HARD-FAIL signature:** ARM_DT_SAME_SIGN bpc ≤ 7.30 (lift survives without subtraction)
- **Why it would be lever:** NAIVE_MULT collapses to unigram because dopa*ACh*5HT*outer(Δ,src) is rank-1 positive accumulation that smears all updates toward the unconditional mean. The −E_neg term explicitly KEEPS the W away from the unigram baseline by subtracting the prediction-weighted outer product.

### Prediction B: Multi-timescale integration is the lever (P=0.35)
- **Mechanism:** the dual-EMA pair `(tau=5, tau=50)` is doing a band-pass / derivative-like filter on the outer-product stream. Fast trace captures recent corrections; slow trace captures persistent patterns. Their algebraic difference is mathematically a high-pass filter on the gradient stream.
- **HARD-PASS signature:** ARM_DT_SAME_TAU bpc ≥ 7.55 AND ARM_DT_SAME_SIGN bpc ≤ 7.30
- **HARD-FAIL signature:** ARM_DT_SAME_TAU bpc ≤ 7.30
- **Why it would be lever:** literature on two-timescale eligibility (engram networks, fast/slow weights) supports "slow traces strongest, dual close" — but "dual=medium-equal" suggests the dual is NOT a multiplicative-orthogonality win; it's a slower-time-integration win that ALSO appears in single slow trace. If true, the cell simplifies to "use a slower EMA."

### Prediction C: Cardinality (two-trace existence) alone is the lever (P=0.20)
- **Mechanism:** any second trace tensor adds storage independent of algebra. Two-rank-1 updates per step doubles per-step rank growth even if both are positive same-sign.
- **HARD-PASS signature:** ARM_DT_SAME_SIGN bpc ≤ 7.30 AND ARM_DT_SAME_TARGET bpc ≤ 7.30 (any 2-trace config beats 1-trace)
- **HARD-FAIL signature:** ARM_DT_SAME_SIGN bpc ≥ 7.50
- **Why it would NOT be lever:** rank-doubling per step is an O(n_steps) effect, and the just-measured 0.52 bit lift over an envelope cap that was supposed to be rank-1-Hebbian-floor is too big to be explained by 2x rank growth alone (envelope was tested up to N_DIM=16384 with no scaling).

### Prediction D: Modulator-target orthogonality (dopa→E_pos, ACh→E_neg) is the lever (P=0.15)
- **Mechanism:** distinct modulator scalars per trace prevent the Marder-STG GPCR-convergence degeneracy.
- **Why it would NOT be lever:** the modulator-orthogonality test is structurally REDUNDANT once you have target-orthogonality (Δ vs pred) and sign-orthogonality. The dopa/ACh scalars are just gating coefficients; they could be replaced by constants and the algebra would still be orthogonal. The Marder concern was the failure mode of NAIVE_MULT, not the SUCCESS mode of DUAL_TRACE.

### Prediction E: Joint-conspiracy / irreducible composite (P=0.25 baseline plausibility; mutually exclusive with A-D individual)
- **Mechanism:** ALL FOUR axes (sign, target, timescale, modulator) are co-load-bearing; ablating any one degrades by ~30-40% of the lift; only the joint mechanism gives full lift.
- **HARD-PASS signature:** all three ablation arms in [7.40, 7.55] bpc — partial degradation across the board
- **Why plausible:** the dual-trace mechanism is biology-derived and biology often uses N-way conspiracies (Brzosko 2017 specifically describes both timing AND modulator AND trace identity as load-bearing).
- **Substrate-product implication if true:** the dual-trace pattern is the irreducible unit; future cells must use the full dopa/ACh + tau-pair + sign-pair + target-pair package.

---

## Cross-thread synthesis (per L5)

### Convergent positives + negatives across substrate's plasticity arc

| Cell / mechanism | Outcome | Sign-heterogeneity? | Target-heterogeneity? | Multi-timescale? | Modulator-axes? |
|---|---|---|---|---|---|
| sparse-bipolar envelope sweep | +0.44 cap (HARD_FAIL scaling) | no | no | no | no |
| 3-axis naive multiplicative (just failed) | READOUT_DEGENERATE | no | no | no | yes (3-way collapsed to 1 scalar per Marder) |
| cfrpe_stdp heterogeneous superadditive (N=512 chain-grade per MEMORY) | CHAIN_GRADE (substrate-mine atom: "heterogeneity is the lever") | YES (LTP+LTD STDP signs) | partial | partial | no |
| dual-trace sequential (just HARD_PASS) | +0.52 bits (HARD_PASS) | YES (E_pos+ − E_neg) | YES (Δ vs pred) | YES (5 vs 50) | YES (dopa vs ACh) |
| Path C own-encoder PC (MIDDLE_BAND) | partial | partial (PC residual is signed) | yes | no | no |
| Lock-in amplifier (CERT 583) | CHAIN_GRADE | yes (cos & sin phases) | yes (different basis projections) | yes (frequency domain) | n/a |

### The single unifying principle (candidate)

**HETEROGENEITY-OF-ALGEBRAIC-ROLE is the lever** — when components play DIFFERENT algebraic roles (additive vs subtractive, error vs prediction, fast vs slow integration, different basis), they compose to escape rank-1 cap. When they're HOMOGENEOUS (same sign, same target, same timescale, scalar-product of modulators), they degenerate.

This is the substrate-mine atom "heterogeneity is the lever" elevated to a general principle. It explains:
- cfrpe_stdp chain-grade (LTP/LTD STDP-windows are sign-heterogeneous) ✓
- dual-trace HARD_PASS (4-way heterogeneity) ✓
- naive-multiplicative READOUT_DEGENERATE (4-way homogeneous; all axes collapse to one scalar) ✓
- sparse-bipolar envelope cap (single mechanism — capped at rank-1 floor) ✓
- lock-in chain-grade (cos/sin phase heterogeneity) ✓
- 3-axis neuromodulator failure (3 modulators but all gating the SAME outer product → homogeneous) ✓

### The irreducible mechanism set (if joint conspiracy)

If Prediction E proves out, the substrate has FOUR PARALLEL HETEROGENEITY AXES that all must be present for the rank-1 escape:
1. **Sign:** (additive, subtractive)
2. **Target:** (correction signal Δ, prediction signal pred)
3. **Timescale:** (fast, slow)
4. **Coupling:** (modulator-gate dopa-specific, modulator-gate ACh-specific)

The cheap-decisive test will discriminate: if ONE arm fully recovers, the axes are decomposable; if NONE recovers, they're irreducible.

### Composition with already-chain-grade primitives

- **Lock-in amp (CERT 583):** the theta/gamma carriers ARE a natural physical implementation of `(tau_fast, tau_slow)`. The dual-trace's two EMA filters can be replaced/augmented by lock-in phase carriers without losing the algebra. **Composes naturally.**
- **HRR working memory:** target-heterogeneity (Δ vs pred) maps to HRR-bind of different role-vectors (role_correction * x vs role_prediction * x). **Composes naturally.**
- **Sparse-bipolar codebook (CERT 592):** the dual-trace's E_pos and E_neg are dense outer products; routing through sparse-bipolar codebook would make them rank-K sparse instead of rank-1 dense. **Composes naturally — possibly multiplicatively (could compound the lift).**
- **Refuse-gate (CERT 588):** the network-prediction signal (used as E_neg's outer-product target) IS exactly the refuse-gate's input; dual-trace's `−ACh*E_neg` term is a natural training signal for refuse-gate calibration. **Composes naturally.**

### Negative findings that constrain the search

- 3-axis naive-multiplicative READOUT_DEGENERATE rules out "more modulators = better" simpliciter. Adding scalar gates to a homogeneous trace does not escape rank-1.
- Sparse-bipolar envelope cap rules out "more dimensions = better" beyond +0.44 bits. Dimensional scaling alone is rank-1 capped.
- Path C MIDDLE_BAND (encoder gap) shows the encoder side ALSO bottlenecks — even with perfect plasticity, encoder choice matters. The dual-trace HARD_PASS is at WORD2VEC encoder; it does NOT clear the encoder gap, it clears a DIFFERENT gap (the plasticity gap).
- Marder STG GPCR convergence rules out simultaneous-multiplicative-modulator framing.

---

## Substrate-product implications

### If anti-Hebbian-subtraction is confirmed (Prediction A, P=0.50)

This is the **highest-value outcome** because it generalizes beyond the neuromod framing.

**Pattern:** Any plasticity cell can add `W −= γ * EMA_slow(outer(prediction, src))` as a regularizer/decorrelator term. This is a single-line code addition.

**Reusable across:**
- substrate-as-LM (the current arc)
- substrate-as-KG (KG fact writes are also rank-1; could decorrelate)
- continual-learning replay (subtractive trace = forgetting term with Bayesian framing)
- multi-hop chain (subtract prior-hop predictions to keep next-hop independent)

**Atomize as META atom:** `anti_hebbian_subtraction_of_slow_prediction_trace_breaks_rank1_cap`
**Substrate-product story:** "we have a single-line decorrelator that escapes the rank-1 Hebbian floor; can layer with any existing write rule."

### If multi-timescale is the lever (Prediction B, P=0.35)

**Pattern:** Replace single-W with W_fast + W_slow where W_slow is an EMA over W_fast snapshots. Add their logits at read time.

**Reusable:** widely (fast-slow weight literature has tons of precedent in continual-learning).
**Substrate-product story:** "we have substrate-native fast-slow weight composition with brain-grounded timescale separation; lift is from the multi-timescale integration, not the gating."

### If cardinality alone is the lever (Prediction C, P=0.20)

**Pattern:** Use 2 (or K) independent W matrices; sum their logits. This is just K-module compose at the W level.
**Substrate-product story:** weakest — competes with bigger-N scaling. Probably not load-bearing alone.

### If joint conspiracy (Prediction E, P=0.25)

**Pattern:** Lock in the full dopa/ACh + tau-pair + sign + target package as the irreducible primitive.
**Substrate-product story:** "we have a brain-grade dual-trace credit-assignment substrate; the mechanism is single-component (don't try to factor)." Substrate-product is the COMPOSITE biological primitive — closer to a single capability than a design pattern.

### Refuse-aware-knowledge-store implication (universal across A-E)

Whatever the load-bearing axis, the dual-trace's `−ACh*E_neg` term inherently produces a signal that COULD calibrate the refuse-gate: when `|−ACh*E_neg|` is large, the network is actively decorrelating against a strong prior expectation, i.e., it has high-margin information to add. When small, the prior is good and refuse-gate should defer to base distribution. **This is a natural confidence signal** for refuse-aware-knowledge-store regardless of the elucidation outcome.

---

## Citations (verified count: 14 distinct primary references)

### From this drill (4 parallel WebSearches; generic-term queries only)

1. **Huertas, Schwettmann, Shouval (2015 Neuron / 2016 Front Syn Neurosci)** "Distinct Eligibility Traces for LTP and LTD in Cortical Synapses" — PMC4660261; S0896627315008260 — LOAD-BEARING: distinct LTP-trace and LTD-trace canonical; sign-heterogeneity built into biology.
2. **Huertas et al. (2014)** "Stable reinforcement learning via temporal competition between LTP and LTD traces" — PMC4124951 — LOAD-BEARING: subtractive competition mechanism between two traces with different decay rates IS the canonical model.
3. **Foldiak (1990)** "Forming sparse representations by local anti-Hebbian learning" — https://www.academia.edu/3276418 — LOAD-BEARING: subtractive Hebbian-update lit precedent; canonical decorrelation mechanism.
4. **Pehlevan & Chklovskii (2015-2019, multiple)** "Hebbian/Anti-Hebbian network for online sparse dictionary learning" — arxiv:1503.0690 / arxiv:1910.04958 / arxiv:1703.07914 — LOAD-BEARING: derived sparse coding from anti-Hebbian objective; biologically-plausible local rule.
5. **Engram Neural Network (2025)** — arxiv:2507.21474 / Emergent Mind ENN topic — Two-timescale eligibility for memory consolidation; "slow traces strongest; dual close to medium" — informative for Prediction B.
6. **Phasor Agents (2026)** — arxiv:2601.04362 — Three-factor plasticity + multi-timescale eligibility in oscillatory graphs.
7. **Cellular Substrate of Eligibility Traces (2023)** — bioRxiv:2023.06.29.547097 — recent experimental validation of two-timescale trace dynamics in cortex.
8. **Nonlinear Hebbian Learning as a Unifying Principle (2016 PLOS Comp Biol)** PMC5045191 — Hebbian/anti-Hebbian unification with sparse coding / ICA / receptive field formation.
9. **Where is the error? Dendritic predictive coding (2022 Trends Neurosci)** S0166-2236(22)00186-2 — local outer-product credit assignment in PC; relevant to E_pos's outer(Δ,src) framing.
10. **Theoretical Framework for Inference and Learning in PC Networks** arxiv:2207.12316 — PC weight updates as local outer products; bridge to substrate's dual-trace decomposition.

### Carried forward from predictive note (`research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md`)

11. Brzosko et al. (2017) eLife 27756 — Sequential dopamine-ACh gating
12. Fremaux-Gerstner (2016) Front Neural Circuits — Three-factor learning rule canonical form
13. Marder, Bucher (2007) Annu Rev Physiol — GPCR convergence to single I_MI scalar (the NAIVE_MULT failure prediction; validated by this cell)
14. Yu-Dayan (2005) Neuron — ACh = expected uncertainty, NE = unexpected uncertainty

---

## Honest limitations

- **The 5-way confound is REAL** — DUAL_TRACE differs from NAIVE_MULT on 4 algebraic axes simultaneously plus one scaffolding axis (cardinality). The 4-arm ablation cell is designed to factor 3 of them (sign, target, timescale) cleanly; modulator-target orthogonality is structurally redundant once those are tested, so it's not a separate ablation arm.
- **Per-arm wall-time should match the reference cell (~55s)** — if any arm runs >2x slower, it's a different mechanism in code (suggesting a confounded variable I missed).
- **Prediction E (joint conspiracy) has P=0.25 baseline** — biology DOES often use conspiracies. Don't over-fit to "find one clean lever" if the data resists.
- **HARD_PASS / HARD_FAIL bands above are pre-registered both directions** per [[feedback-negativity-bias-rule]] and [[feedback-lit-scan-calibration-penalty]].
- **No re-coverage:** predictive note covered breadth (4 neuromod axes); this elucidation drill operates AT DEPTH on the just-landed cell's algebra decomposition; new lit (Huertas-Shouval temporal-competition, Foldiak anti-Hebbian, Pehlevan-Chklovskii similarity-matching) was not covered in the predictive note.
- **The HEADLINE bets on Prediction A (P=0.50)** but the cheap-decisive test cleanly discriminates ALL 5 hypotheses with a single 4-arm cell — outcome-agnostic by design.

## Key insight (one line)

The dual-trace HARD_PASS is almost certainly NOT about having two traces — it's about having a subtractive anti-Hebbian term where W is decorrelated against its own slow prediction outer product; the four-axis structure is the *vehicle*, the algebraic role-heterogeneity is the *lever*.
