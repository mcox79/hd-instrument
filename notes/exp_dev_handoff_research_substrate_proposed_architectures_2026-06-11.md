# exp_dev hand-off - research: substrate-proposed ARCHITECTURE-CHANGE generation

Filed-by: research (opus, 2026-06-11)
Trigger: notes/research_drill_substrate_proposed_architectures_2x_2026-06-11.md (Tier-4 self-redesign gate enabling drill)
Pause state: respect d:/AI/hd-instrument/data/orchestrator_paused.flag - if set, file anchors for queue-resume; do not ship.

Per [[feedback-no-experiment-design-in-prompts]]: the research note specifies HARD-PASS / HARD-FAIL thresholds; exp_dev owns the cell design (build, smoke, queue, verify) without inline experiment recipes from research.

## Anchor candidates (rank-ordered)

### A1 - ARCH-PROPOSE-1 surrogate (top priority for Tier-4 gate)
- pointer: research note section (b), Pilot ARCH-PROPOSE-1
- substrate-product reading: validates whether substrate-proposed-architecture is empirically achievable on a known cliff-crossing (polysemy 0.42 -> 1.000 via concept-context-binding from cycle 226 memory) BEFORE committing to v4.0 self-redesign engineering.
- tier hint: Tier-2 anchor (~3-6 hr CPU; single-machine).
- why-now: enables Tier-4 gate; rest of Tier-4 pipeline depends on this validating; cheap relative to v4.0 engineering cost.
- pre-reg deltas:
  - HARD-PASS: TOP-1 precision >= 0.85 + Shapley-attribution >= 0.50 to correct binding-operator component.
  - HARD-FAIL: TOP-1 in distractors OR Spearman rho between predicted-lift and empirical-lift <= 0.30.
  - MIDDLE: TOP-1 correct family but Shapley split across distractors -> rescue with ABC (arxiv 2406.07908) instead of pure-SHAP.

### A2 - Substrate-internal causal-SHAP attribution validation on n=10 historical cap_map bumps
- pointer: research note Prediction P2.
- substrate-product reading: validates that causal-SHAP on substrate components correctly identifies which substrate component caused which capability lift. This is the SCORING ORACLE leg of the 4-mechanism stack. Without this, substrate-proposed architecture cannot rank candidates.
- tier hint: Tier-2 anchor (~1-2 hr CPU; uses existing cap_map verdict log as ground truth).
- why-now: enables A1 (A1 requires a working attribution engine); reuses already-logged cap_map history; lowest engineering risk in the stack.
- pre-reg deltas:
  - HARD-PASS: Spearman rho >= 0.60 between Shapley-predicted-lift and empirical-lift on n=10 historical bumps; Shapley-attribution-to-correct-component >= 0.50 of total lift.
  - HARD-FAIL: rho <= 0.25 OR gini on attribution distribution <= 0.15 (attribution noise dominates).
  - MIDDLE: rho in [0.25, 0.60] -> rescue by augmenting Shapley with ABC counterfactual cross-check.

### A3 - Bounded-recursion safety: differential-drift test on substrate-proposed vs fixed-external gate
- pointer: research note Prediction P4.
- substrate-product reading: stress-test that operationalizes the bounded-recursion safety guarantee. If P4 HARD-PASSes, the 1-line invariant "gate-frozen-at-cycle-0, never substrate-proposed" empirically bounds all 4 failure modes (meta-rule-collapse + unbounded-self-reference + Goodhart + evaluation-shift). This is the safety differentiator for the substrate-product Tier-4 story.
- tier hint: Tier-2 anchor (~4-6 hr CPU; requires 5 recursion rounds in each arm).
- why-now: load-bearing for any commercial-grade self-redesign claim; lit-precedent (OpenReview IF0L7HSs3K operator-theoretic contraction argument) is strong but substrate-specific empirical validation is novel.
- pre-reg deltas:
  - HARD-PASS: drift_substrate_gate - drift_fixed_gate >= 0.15 (differential clearly shows substrate-gate collapses while fixed-gate holds).
  - HARD-FAIL: differential <= 0.05 (either fixed-external also collapses, OR substrate-proposed does not collapse - either disconfirms the bound).
  - MIDDLE: 0.05 to 0.15 -> partial confirmation; the bound is real but weaker than operator-theoretic argument predicts.

## Context pointers

- Research note: notes/research_drill_substrate_proposed_architectures_2x_2026-06-11.md
- Triangle math drills (codomain): notes/research_drill_categorical_ai_discocat_2x_2026-06-11.md, notes/research_drill_operator_algebras_subfactor_theory_2x_2026-06-11.md, notes/research_drill_rmt_beyond_free_probability_2x_2026-06-11.md
- Substrate-self-index redesign as working prototype: notes/research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md
- v3.2 engineered-wrapper existence proof: memory/substrate_v32_engineered_wrapper_2026-06-11.md
- Drill-pattern bias (temporal/contextual valid, fixed-structural fail): memory/drill_pattern_temporal_contextual_not_structural_2026-06-11.md
- cap_map verdict log (used as ground truth for A2): data/orchestrator_status_log.jsonl filtered to verdict_handler events
- Layer 1 attribution measurement protocol (FROZEN GATE): existing methodology per notes/research_to_testbed_LAYER1_ATTRIBUTION_VALIDATED_FIX_A_ENDORSED_2026-06-11.md

## Contract

- exp_dev owns: cell design (~lines of python), smoke gate, queue_add, REMOTE VERIFY, self-test per formula-selftests.
- research owns: HARD-PASS / HARD-FAIL thresholds (locked in research note); cross-thread synthesis; rescue routing on MIDDLE.
- strategy owns: cap_map row updates post-verdict; tier-4 gate go/no-go decision.

## Autonomy declaration

exp_dev has autonomy on:
- which anchor to ship first (A2 lowest risk; A1 highest leverage; A3 most differentiating).
- whether to batch A1+A2 in one cycle (A2's attribution engine is a dependency for A1; sequential is safer).
- whether to pad budget for cross-validation (recommended on A1: 1 surrogate + 2 held-out cliff-crossings).

research declares P_deflated:
- A1: 0.50 (the full pipeline; novel-synthesis cap).
- A2: 0.42 (causal-SHAP on substrate is novel application; lit-precedent on standard NNs is strong).
- A3: 0.45 (operator-theoretic precedent strong; differential-test design novel).

If all three HARD-PASS, Tier-4 gate opens and v4.0 substrate-proposed-architecture mechanism can be engineered in 2-4 days (per research note section (e)).
If A2 HARD-FAILs, the scoring oracle leg of the 4-mechanism stack is broken; pivot to ABC-only attribution (arxiv 2406.07908) before re-running A1.
If A1 HARD-FAILs, the retrieval-over-candidates leg fails on the surrogate; pivot to evolutionary-NAS-baseline as a 1000x-more-expensive fallback for Tier-4.
If A3 HARD-FAILs, bounded-recursion safety is not empirically confirmed; freeze Tier-4 until human-review of methodology and consider Tier-5 (multi-substrate ecology with cross-substrate gating) as the safer recursion bound.
