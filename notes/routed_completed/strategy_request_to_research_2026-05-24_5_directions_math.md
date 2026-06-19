# Strategy -> Research request — 5 directions pure-math drills (2026-05-24)

**From**: Orchestrator inline (Strategy role) acting on user-delivered substantive 5-direction analysis
**To**: Research (next cycle)
**Cap_map**: v183 (commit cf69a58)
**Source analysis**: `notes/research_5_new_directions_2026-05-24.md`
**Pause state**: ACTIVE
**Companion Exp Dev request**: `notes/strategy_request_to_exp_dev_2026-05-24_5_new_directions.md` (empirical ships)

## Why this hand-off exists

Per [[feedback-no-experiment-design-in-prompts]]: orchestrator hands the QUESTION; Research finds the closed form. This file states two pure-math drills (NOT empirical experiments) extracted from the user's 5-direction analysis. Both are PURE-MATH derivations that empirical work depends on.

Per [[feedback-dispatch-wrappers-default]]: Agent tool unavailable in sub-agent context. This routing note enables the next Research cycle to pick up these drills.

Per [[feedback-2x-means-depth]]: these are NEW directions, not 2x re-runs.

## Drill 1 — PAC-Bayes bounds for outer-product Hebbian memories under sequential tasks (Direction 1 adjunct)

**Question**: What is the PAC-Bayes generalization bound for outer-product Hebbian memories (W = sum_k v_k v_k^T) trained on sequential tasks T_1, T_2, ..., T_K? Specifically:

1. Does the standard PAC-Bayes posterior-prior KL bound apply to substrate Hebbian retrieval, or does the substrate's no-gradient training violate the framework's assumptions?
2. If a PAC-Bayes bound exists for this setting, what is its form? Express as a function of:
   - M (substrate width or pool size)
   - K (number of sequential tasks)
   - n_k (samples per task)
   - sigma (substrate noise scale or readout cleanup tolerance)
3. Does the bound predict a phase transition at the M / (K x n_k) ratio that would correspond to Bet B's empirical retention ceiling?

**Cheap decisive test criterion**: a closed-form upper or lower bound on retention_A as a function of M with explicit constants, OR a published-literature derivation that maps to the substrate's outer-product Hebbian setting.

**Adjacent literature angles**:
- McAllester PAC-Bayes original (1999) for the classical setting
- Catoni PAC-Bayes (2007) for refined bounds
- Maurer (2004) PAC-Bayes for Hebbian / kernel methods
- Sequential / continual-learning PAC-Bayes bounds: search "PAC-Bayes continual learning sequential", "PAC-Bayes memory replay"
- Free-probability angle: M-P / BBP machinery from R16 may give a sharper bound for the outer-product setting specifically

**Discipline citation**: Per [[feedback-query-privacy-decomposition]] use generic math terms in external queries ("PAC-Bayes outer-product memory", "Hebbian generalization bound", "continual learning generalization bound"); do NOT include substrate-novel mechanism names.

**Deliverable**: a research note at `notes/research_PAC_Bayes_Hebbian_outer_product_<date>.md` (Research picks exact name) with:
- Closed-form bound (if extractable from literature)
- Mapping from substrate variables (M, K, n_k, sigma) to the bound's variables
- Specific prediction for Bet B retention ceiling at M_current and Bet B's empirical (K=3, n_k= current Bet B values)
- Verdict on whether bound predicts capacity-bound vs interference-bound regime (closes Direction 1's theoretical adjunct)

## Drill 2 — Closed-form M_c prediction for MoE cross-talk phase transition (Direction 4)

**Question**: Derive the critical M_c above which MoE gating noise drops below cleanup tolerance, using the M-P/BBP machinery from R16. Specifically:

1. Set up: MoE with K experts, each expert is a substrate-W cell, gating distributes queries across experts. Cross-talk between experts manifests as residual cosine similarity in the wrong-expert's bundle. Cleanup tolerance is the substrate's readout decoder margin.
2. Use M-P bulk + BBP outlier-eigenvalue machinery (R16's noise-sigma=16 prediction infrastructure) to derive M_c as a function of:
   - K (expert count)
   - cleanup_tolerance (substrate readout decoder margin)
   - sigma (gating noise scale)
3. Goal: a closed-form M_c such that for M > M_c, MoE PASS predicted; for M < M_c, MoE FAIL predicted.

**Cheap decisive test criterion**: a closed-form M_c formula expressed in terms of K, cleanup_tolerance, sigma -- ideally to within 20% of the empirical pass/fail boundary observed in the current MoE 3/8-cell run.

**Reference**: `notes/research_R16_free_probability_predictions_2026-05-21.md` for the M-P / BBP machinery; R16's noise-sigma=16 prediction is the existence proof that this machinery extracts substrate-novel phase transitions.

**Adjacent literature angles**:
- BBP (Baik-Ben Arous-Peche) phase transition for spiked covariance models
- Marchenko-Pastur for outer-product spectra
- Free-probability lens (R-transform / S-transform) for cross-talk computation
- MoE cross-talk literature: search "mixture of experts gating noise capacity", "expert cross-talk tolerance"
- VSA / HRR capacity bounds for K-superposed bindings

**Discipline citation**: Per [[feedback-query-privacy-decomposition]] use generic math terms ("BBP phase transition spiked covariance", "mixture of experts capacity gating", "MP outlier eigenvalue").

**Deliverable**: a research note at `notes/research_MoE_M_c_phase_transition_<date>.md` (Research picks exact name) with:
- Closed-form M_c formula
- Comparison to current MoE 3/8 cells empirical pass/fail boundary
- Predicted M_c value with explicit constants
- Confidence interval / known approximations
- Verdict on whether M_c moves MoE row from "3/8 cells pass" to "passes above predicted M_c" in cap_map

Once delivered, the empirical verification ship (Direction 4 in the exp_dev request) unblocks.

## Discipline citations

- Per [[feedback-no-experiment-design-in-prompts]]: Research owns the derivation strategy; this note hands the QUESTION.
- Per [[feedback-query-privacy-decomposition]]: use generic math terms in external queries.
- Per [[feedback-2x-means-depth]]: these are NEW drills, not 2x re-runs.
- Per [[feedback-subagent-model-optimization]]: lit-scan sub-agents default to Sonnet; main Research synthesis is Opus.
- Per [[feedback-lit-scan-calibration-penalty]]: substrate is in uncharted regime for outer-product PAC-Bayes; deflate agent P estimates by 0.15-0.25; cap novel-synthesis P at 0.50.

## Deadline / urgency

- **Drill 2 (M_c)** is BLOCKING for Direction 4 empirical ship. Higher priority.
- **Drill 1 (PAC-Bayes)** is adjunct to Direction 1 empirical M-sweep; lower priority but informative for verdict reading.

Both drills are scope-expansion candidates from the user's analysis -- they extend cap_map characterization rather than closing rescue paths.

## No blockers

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
