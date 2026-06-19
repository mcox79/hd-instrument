# exp_dev hand-off -- research: substrate-native conformal / Venn calibration on cleanup-margin

Filed-by: research sub-agent (Opus), 2026-06-11
Trigger: notes/research_drill_substrate_conformal_calibration_2x_2026-06-11.md
Pause state: check data/orchestrator_paused.flag before dispatching; experiments below are PENDING user go-ahead

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs anchor mechanics autonomously; this file supplies TASK + WHY + CONTRACT + AUTONOMY pointers only. No sweep grids, no threshold formulas, no anchor names, no queue assignments.

---

## Headline rationale

Substrate cleanup-margin (distance to best vs second-best codebook atom) is mathematically IDENTICAL to the Vovk-Shafer Nearest-Neighbor distance-ratio nonconformity score that powers split conformal prediction. This means substrate already supports finite-sample marginal-coverage guarantees with ZERO architectural changes -- only a calibration-set carve-out and an empirical-quantile lookup. Pilot tests below validate the structural identity empirically on existing substrate infrastructure.

---

## Anchor Candidates (rank-ordered)

### 1. Split-conformal cleanup-margin marginal-coverage pilot (Tier: CPU laptop smoke)
Anchor pointer: Research note Section (b) "Cheap decisive test" + Section (c) HARD-PASS predictions
Substrate-product reading: Validates that every substrate response can ship with a calibrated 90 / 95 / 99 percent confidence set. Direct credibility differentiator vs LLM softmax. Reuses existing substrate library; only the calibration carve-out is new (~30 lines).
Tier hint: laptop CPU; ~30-60 min wall; existing kb25k-class codebook regime; n_cal sweep in standard CP range
Why now: This is the structural validation gate. The lit identity is established (Vovk-Shafer, Orange Conformal NN nonconformity); empirical confirmation on substrate-specific codebooks is what unlocks the product-grade UQ claim.

### 2. Mondrian / class-conditional CP per-atom coverage (Tier: CPU laptop)
Anchor pointer: Research note Section (c) HARD-PASS #3 + Section (d) RC3P subsection
Substrate-product reading: Per-atom finite-sample coverage is decision-grade for compliance / audit. EU AI Act Article 12 traceability pull is already flagged in cap_map row L1.
Tier hint: laptop CPU; same codebook as anchor 1; need n_cal_per_atom of standard CP size per atom
Why now: Marginal coverage alone does not give per-class guarantees; substrate codebooks are Zipfian on real corpora so class-conditional matters. Cheap extension of anchor 1.

### 3. RC3P long-tail rescue for rare atoms (Tier: CPU laptop or remote CPU)
Anchor pointer: Research note Section (d) RC3P subsection; code ref github.com/YuanjieSh/RC3P
Substrate-product reading: NeurIPS 2024 reports ~26% prediction-set-size reduction under long-tail coverage. Substrate codebooks built on real corpora are Zipfian; without RC3P, class-conditional CP over-covers head and under-covers tail.
Tier hint: laptop CPU; codebook with synthetic Zipfian usage frequency on test split; n_cal as per anchor 2
Why now: Only runs if anchor 2 shows per-atom coverage variance above the tolerance band. Otherwise skip -- if uniform coverage already holds, RC3P adds complexity without lift.

### 4. Venn-Abers calibration of binary substrate decisions (Tier: CPU laptop)
Anchor pointer: Research note Section (d) Venn-Abers subsection; arxiv 2205.10586 NLU calibration application
Substrate-product reading: Every binary substrate decision (bind / unbind / match) gets a calibrated probability INTERVAL, not a point. Interval width is itself a substrate-native epistemic-uncertainty signal. Multi-class extension via Johansson 2021 one-vs-rest.
Tier hint: laptop CPU; pair of isotonic regressions per binary decision per atom; n_cal of standard CP size
Why now: Composable with anchors 1-3; tightens product claim from "calibrated set" to "calibrated probability interval per decision". Marginal cost is K isotonic fits.

### 5. Conformalized quantile regression on continuous substrate readouts (Tier: CPU laptop)
Anchor pointer: Research note Section (d) CQR subsection; Romano 2019 arxiv 1905.03222; code github.com/yromano/cqr
Substrate-product reading: Substrate-as-retriever scenarios return real-valued similarity / rank scores. CQR gives adaptive prediction intervals with finite-sample coverage and heteroskedasticity-aware width. Useful for downstream LLM front-ends that need calibrated confidence bands not point estimates.
Tier hint: laptop CPU; existing retrieval-score substrate output; train quantile regressors on residual; small n_cal
Why now: Once anchors 1-2 land, this extends the UQ story from classification-style sets to regression-style intervals -- broadens the product claim across substrate output modalities.

---

## Context Pointers

- Research note (full analysis, formulas, citations): d:/AI/hd-instrument/notes/research_drill_substrate_conformal_calibration_2x_2026-06-11.md
- Shafer-Vovk 2008 tutorial: https://jmlr.csail.mit.edu/papers/volume9/shafer08a/shafer08a.pdf
- Angelopoulos-Bates gentle intro: arxiv 2107.07511 (also 2005.07972 unified review)
- RC3P NeurIPS 2024: arxiv 2406.06818; code github.com/YuanjieSh/RC3P
- Venn-Abers multi-class: PMLR 152 Johansson 2021; github.com/ip200/venn-abers
- CQR Romano 2019: arxiv 1905.03222; code github.com/yromano/cqr
- Conformal beyond exchangeability (covariate shift handling): Barber-Candes-Ramdas-Tibshirani 2023 Annals 51(2)
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md (check for calibration / UQ rows)

---

## Contract

exp_dev is responsible for:
1. Reading the research note in full before designing any anchor
2. Identifying which existing substrate infrastructure (hdlab/ modules) computes the cleanup-margin signal and storing it per query
3. Designing the calibration / test split per [[feedback-metrics-required-fields-write_metrics]]
4. Pre-registering HARD-PASS / HARD-FAIL bands per [[feedback-envelope-expansion-fail-bands]] before queueing (research note section (c) supplies the bands)
5. Verifying timeout formula [[feedback-per-experiment-timeout-required]] for each anchor
6. NOT including mechanism-specific configs or threshold numbers in queue prompts [[feedback-no-experiment-design-in-prompts]]
7. Watching for covariate-shift between calibration and test splits -- if shift suspected, route to weighted-CP / nexCP variants per research note Section (d)
8. Per [[feedback-method-overclaim-lift-validation]]: validate that conformal-set tightness LIFT > 2x SE over a naive top-K baseline, not just absolute set-size threshold

---

## Autonomy

exp_dev decides:
- Which anchor to run first (recommend anchor 1 as cheapest decisive)
- Whether anchors 2-3 run conditional on anchor 1 PASS or unconditionally in same cell
- Substrate library entry point for cleanup-margin extraction
- Calibration / test split mechanics (random vs stratified)
- Whether to use ratio form or negative-margin form of nonconformity (both Vovk-valid; ratio is more numerically stable per research note)
- Whether anchor 4 Venn-Abers extends scope to multi-class one-vs-rest (cost K isotonic fits) or stays binary
- Whether to file a follow-on 3x DEEP drill request to research after seeing pilot results -- specifically the free-probability x calibration cross-link (research note Section (f)) is a high-value future drill

---

## Compliance notes

- No project-specific numerical values in this hand-off (no N, no kb-sizes)
- ASCII-only
- Pre-registered HARD-PASS / HARD-FAIL in research note Section (c)
- Pause-gated per orchestrator paused.flag
