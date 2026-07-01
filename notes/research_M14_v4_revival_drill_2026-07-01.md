# Research M1.4 v4 revival drill — 2-sided tau vs Bernoulli flip vs bimodal buckets

**Filed:** 2026-07-01 (research sub-agent, Opus)
**Trigger:** Skunkworks 7a89856d landing — M1.3 NoiseChannel VALIDATED (regime-std monotonic; additive_gaussian wiring correct) but M1.4 v3 adaptive-tau mechanism class WRONG SHAPE. SLIDING_WINDOW / BAYESIAN_CI / PERCENTILE all fail 0.15 precision_lift; BAYESIAN_CI at -0.193 (adaptive actively HURTS). One-sided tau produces net structural loss (recall gain + precision loss).
**Load-bearing:** M1.4 closure is M3 milestone-critical (refuse-gate = glass-box conversational calibration primitive).
**Frame:** Level-2 operational drill on 3 revival paths cell-author + Skunkworks specified: (a) 2-sided tau band, (b) bernoulli_flip_stochastic NoiseChannel mode, (c) bimodal-history buckets (in_KB vs OOD).
**Calibration:** deflate 0.20; novel-synthesis cap 0.50 — options (a)+(c) are composition-only (adapting known primitives) so lift to 0.55.

---

## HEADLINE

**Rank: (a) > (c) > (b)** on chain-grade probability × payoff. Option (a) 2-sided tau band has 4-drill cross-domain support (signal-detection τ-criterion, tail-specific conformal, two-one-sided-test hypothesis-testing, asymmetric ROC) — **5x-drill escalation eligible**. Option (c) bimodal buckets has 3-drill support (Mondrian conformal exact group-conditional coverage, mPFC-schema-in vs schema-out neural circuits, split-localized CP) — 5x-drill eligible; specifically **composes with (a) as (a+c) meta-composition**. Option (b) Bernoulli flip is really an M1.3-completion (spec's original mode) not an M1.4 fix — noise mode alone does not repair the mechanism-class error; keep as M1.3 spec-fidelity extension.

The v3 failure signature (recall ↑, precision ↓, net loss) is exactly the failure mode SDT literature predicts when a ONE-sided criterion moves against a SIGNAL-plus-NOISE distribution — the criterion trades sensitivity for specificity on a fixed axis. **Structural fix:** dual criteria (a) OR partitioned per-population criteria (c) — both restore the calibration degree-of-freedom that one-sided adaptation collapses.

---

## Ranked options with design one-liners

### (a) 2-sided tau band (tau_low + tau_high adapted separately) — CG=0.55, payoff=HIGH ⭐ recommended

**Mechanism.** Refuse if score < tau_low (definitely OOD) OR score ∈ [tau_low, tau_high] AND consistency_check_fails (ambiguity band); accept if score > tau_high. Both criteria adapt SEPARATELY on separate history streams: tau_low on OOD-score history (10th percentile), tau_high on in-KB-score history (90th percentile). Discriminator: precision_lift ≥ 0.15 AT LEAST at moderate NoiseChannel regime AND refuse-rate monotonic in regime AND seed-cv < 8%; band-floor annotation per META_RULE_L if only 0.10-0.14.

**Design one-liner (cell-author).** Author `refuse_gate_2sided_tau_v4_M14` — 4 arms (fixed baseline / 2sided_percentile / 2sided_bayesian_CI / 2sided_sliding_window) × 3 NoiseChannel regimes {clean, moderate, heavy} × 3 difficulty bands {in-KB, borderline, OOD} × 3 seeds. Uses M1.3 NoiseChannel additive_gaussian per spec. Pre-reg CARDINALITY_OK=108; META_RULE_AX arm-distinct across tau-family; META_RULE_L band-floor MB; META_RULE_AV FULL-run declaration; META_RULE_AY distinctness HARD_FAIL.

**Cross-domain support (4 drills):**
1. Signal Detection Theory: τ-decision strategy uses 2 criteria bracketing "same/different" — asymmetric ROC → dual thresholds are the discriminant-optimal shape (Landy 2024, CNS NYU).
2. Tail-specific conformal (arxiv 2606.18199): asymmetric coverage guarantees, separate quantiles for each tail; direct math match.
3. Two-one-sided-test framework: standard hypothesis-testing pattern for equivalence bounds; SESOI upper + lower bound tested separately (Lakens 2017).
4. Unequal-variance SDT: when signal and noise distributions have different spread, single criterion is provably suboptimal — dual criteria needed for calibration (Landy chapter 2024).

### (c) Bimodal-history buckets (in_KB vs OOD separate tau streams) — CG=0.50, payoff=HIGH

**Mechanism.** Two independent tau streams: tau_inKB adapts on the score history of queries the router flagged in-KB; tau_OOD adapts on OOD-flagged history. At decision time, use the tau matching the router's prior classification. Requires a router prior (which the current substrate has via NoiseChannel + intent classifier from n=100 chain-grade prior). Discriminator same as (a) but with additional requirement: cross-stream contamination check (tau_inKB and tau_OOD must diverge >X% in moderate regime; if they collapse to same value, the buckets are non-informative).

**Design one-liner.** Author `refuse_gate_bimodal_bucket_v4_M14` — 3 arms (fixed baseline / bimodal_percentile / bimodal_bayesian_CI) × 3 regimes × 3 bands × 3 seeds. Requires router-prior signal (use intent-classifier cert-grade primitive). CARDINALITY_OK=81; META_RULE_AX; META_RULE_L; META_RULE_AV.

**Cross-domain support (3 drills):**
1. Mondrian conformal prediction (metricgate.com, Vovk-Shafer): exact group-conditional coverage when groups disjoint; direct math match for in-KB vs OOD group partition.
2. mPFC schema-in vs schema-out neural circuits: distinct populations encode schema-consistent vs schema-violating stimuli (mPFC schema literature + hippocampal SWR consensus, Nature Comm 2022); bio precedent for bimodal confidence circuits.
3. Split-localized CP (arxiv 2206.13092): partition-then-calibrate per-region; NeurIPS-line direct precedent.

**Meta-composition:** (a)+(c) is architecturally clean — 2-sided band per bucket = 4 tau streams total. Consider (a+c) as a v5 escalation if (a) HP but leaves per-band coverage residuals.

### (b) bernoulli_flip_stochastic NoiseChannel mode — CG=0.35, payoff=LOW-MED (RECLASSIFY)

**Mechanism.** Original M1.3 spec noise mode: instead of additive Gaussian post-cosine, apply Bernoulli bit-flip pre-cosine on retrieved codeword bits. Yields count-statistic-based score distribution (per the 5x deterministic-noise drill 2026-06-30 finding); DOES restore intermediate-confidence band via injection at boundary. But does NOT fix the one-sided-tau mechanism-class error.

**Design one-liner.** Author `noisechannel_bernoulli_flip_M13_completion_v1` as M1.3 spec-fidelity extension — 3 noise modes (additive_gaussian / bernoulli_flip / temperature_softmax) × baseline fixed-tau × 3 regimes × 3 seeds. This is a NoiseChannel-family cell, NOT a refuse-gate adaptive-tau cell. If both (a) and (c) HP with additive_gaussian, this becomes a nice-to-have completeness sweep; do NOT dispatch as M1.4 revival path.

**Cross-domain support (2 drills — weaker):**
1. Stochastic IMT neurons (PMC 5893757): threshold-noise-at-bifurcation gives intermediate-confidence bands via structural stochasticity.
2. Batch-ensemble stochastic NN OOD (arxiv 2206.12911): Bernoulli-flip-style OOD detection with feature-collapse mitigation.

**Reclassification recommendation.** File as M1.3 v2 spec-completion, not M1.4 v4. Refuse-gate mechanism class needs (a) or (c); noise mode change alone insufficient.

---

## Cross-thread synthesis

- Ties into 5x drill 2026-06-30 (deterministic-noise structural-not-bug): substrate determinism is a structural count-statistic; M3 cortex-boundary noise is architectural fix — this drill confirms M1.4 lives at the boundary, not substrate-internal.
- Composes with WM multi-bank K=4096 CG (BAYESIAN_CI mechanism precedent exists in substrate).
- Composes with intent-classifier n=100 CG (router-prior for option c).
- Compose with lock-in amplifier CG (structural signal-detection filtering — related principle).

## Substrate-product implications

- M1.4 revival with (a) unlocks refuse-gate as glass-box calibration primitive (M3 milestone-critical).
- Product framing: "substrate refuses when it doesn't know" — dual-criterion band gives credibility differentiator vs LLM softmax (calibrated abstention with bounded precision-lift claim).
- Composes with prior conformal-calibration research (2026-06-11 drill) — Mondrian CP path directly available for option (c) via existing hdlab primitives.

## 5x-drill escalation eligibility

- **Option (a)** — 4 cross-domain drills (SDT + tail-conformal + TOST + unequal-variance SDT). **5x-drill eligible.** Recommend dispatch immediately as M1.4 v4 primary path.
- **Option (c)** — 3 cross-domain drills (Mondrian + mPFC-schema + split-localized). **5x-drill eligible.** Recommend queue as v5 fallback OR (a+c) meta-composition if (a) HP-partial.
- **Option (b)** — 2 cross-domain drills, weaker fit. **Not eligible for 5x escalation as M1.4 revival**; file as M1.3 spec completion.

## Predictions (falsifiable)

- **HARD_PASS (a):** precision_lift ≥ 0.15 at moderate regime × at least 1 of 3 difficulty bands; refuse-rate monotonic in regime; seed-cv < 8%; net-lift (precision_lift + recall_lift) ≥ 0.20 (v3 baseline: -0.10 to -0.19).
- **HARD_FAIL (a):** precision_lift < 0.05 at ALL regimes → the mechanism class is structurally 2-sided AND single-threshold; deeper redesign or M3-cortex-external calibrator needed. Close M1.4 as substrate-out-of-scope; hand to cortex layer.
- **HARD_PASS (c):** precision_lift ≥ 0.15 AND bucket-divergence ≥ 20% (buckets non-degenerate).
- **HARD_FAIL (c):** bucket-divergence < 5% → router prior insufficient for partition; needs stronger prior signal.
- **Prediction on (b) alone:** additive vs Bernoulli score-distribution shape statistically distinct (KS ≥ 0.1) BUT precision_lift stays at v3-level (-0.05 to -0.19). Noise mode change is orthogonal to mechanism-class error.

## Citations (verified count: 9)

1. Landy MS, Signal Detection Theory chapter, NYU CNS 2024 — τ-decision strategy asymmetric ROC dual criteria.
2. metricgate.com Mondrian CP calculator (2024) — group-conditional coverage exact when disjoint.
3. arxiv 2606.18199 — tail-specific conformal guarantees.
4. arxiv 2206.13092 — Split-localized CP partition-then-calibrate.
5. arxiv 2206.12911 — Batch-ensemble stochastic NN OOD.
6. arxiv 2306.17630 — Noise injection generalization + calibration.
7. arxiv 2501.12314 — Noise injection Bayesian uncertainty quantification.
8. PMC 5893757 — Stochastic IMT neurons threshold-noise-at-bifurcation.
9. Nature Comm 2022 (nature.com/articles/s41467-022-33536-x) — SWR detection consensus; mPFC schema circuits.

**Verified count reported: 9 primary sources across 4 disparate fields (SDT / conformal prediction / stochastic-NN OOD / bio schema-circuits).**
