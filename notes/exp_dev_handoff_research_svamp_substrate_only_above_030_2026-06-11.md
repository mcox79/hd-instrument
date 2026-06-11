# exp_dev hand-off -- research: SVAMP substrate-only above 0.30 plateau (no dep-parser)

filed-by: research
date: 2026-06-11
trigger: 2x DEEP drill notes/research_drill_svamp_substrate_only_above_030_2x_2026-06-11.md HARD-PASS path identified -- substrate-only CPU experiment ready to ship.

## Pause state

Honor data/orchestrator_paused.flag if present. Anchors below are CPU-only (laptop or home-cpu lane) -- non-blocking to GPU queue. If paused, file annotations only; do not queue_add until resume.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists anchors + pointers. exp_dev OWNS detailed cell design and pre-reg.

## Anchor candidates (rank-ordered)

### Anchor 1 (Tier 1 -- HIGHEST VALUE): SVAMP-VIB-substrate-only smoke

- anchor pointer: extend existing richer-feature discriminative perceptron with Variational Information Bottleneck loss (Zhang ACL 2022; Zou 2023 ESIB on SVAMP precedent)
- substrate-product reading: substrate-native VIB compression provides adversarial-robust feature extraction without any parser dependency. Maps to substrate-product capability "adversarial-robust NL classifier" (enterprise-buyer-relevant differentiator).
- tier hint: Tier 1 -- single highest-value individual lift (+0.02 to +0.04 per Zhang 2022 textual-adv literature; +4.5 percent on SVAMP gap per Zou 2023 ESIB direct precedent)
- why-now: SVAMP plateau at 0.30 is the gating issue for math-word-problem product capability; VIB is the most-cited single substrate-compatible robustness primitive; CPU-only smoke runs in ~1 hour.
- pre-reg envelope: HARD-PASS held-out >= 0.32 (delta >= +0.023 over 0.297 baseline); HARD-FAIL drops >= -0.02; partial 0.30 to 0.32. Compose with anchors 2-4 only if HARD-PASS.

### Anchor 2 (Tier 1): Position-encoded substrate bigram bundles

- anchor pointer: add position-bucket atoms (bucket size 5) bound to token atoms; bundle via superposition; replaces orderless bag-of-words richer features
- substrate-product reading: substrate-native syntactic-order without parser; same algebraic primitive used in substrate POS-tagger (0.906 Penn Treebank validated 2026-06-11 memory)
- tier hint: Tier 1 -- substrate-classical lit empirically validated on adjacent task (POS); direct primitive re-use; cheap.
- why-now: SVAMP adversarial variations include structural-invariance (Patel 2021) -- requires order-sensitivity. Bag-of-words richer features by construction throw this signal away.
- pre-reg envelope: HARD-PASS held-out >= 0.32 (delta >= +0.023); HARD-FAIL delta < +0.01.

### Anchor 3 (Tier 2): Counterfactual question-reordering augmentation

- anchor pointer: deterministic rule-based generator that reverses question + swaps numeric-entity positions on training data; train perceptron on augmented set
- substrate-product reading: substrate-adjunct service "automatic test-set augmentation for NLP pipelines" -- independent revenue surface
- tier hint: Tier 2 -- precedent (Kumar 2022, Liang 2024) shows mixed but positive lift on SVAMP; cheap to implement; gated on Anchor 1 or 2 HARD-PASS for compounding.
- why-now: SVAMP adversarial includes 9 documented variation patterns -- the SAME 9 patterns can be applied programmatically to MAWPS / ASDiv training data.
- pre-reg envelope: HARD-PASS combined-with-A1-or-A2 held-out >= 0.34; HARD-FAIL delta < 0 from rule-based reversal.

### Anchor 4 (Tier 2): Cleanup-margin-gated 2-perceptron ensemble

- anchor pointer: train second perceptron via bagging (different random subsample); use perceptron-2 only when perceptron-1 cleanup-margin below threshold; gating primitive reused from Phase4 v2.5 fix (drill 2026-06-11)
- substrate-product reading: substrate.gating.MarginGatedEnsemble library primitive -- one implementation, multiple downstream classifier uses
- tier hint: Tier 2 -- EnHDC majority-vote precedent (Liu 2022 arXiv 2203.13542) reports 3-7 percent HDC lift; gating signal is substrate-native (cleanup margin).
- why-now: same primitive solves Phase4 v2 regression (parallel substrate workstream). Two product unlocks from one implementation.
- pre-reg envelope: HARD-PASS combined-stack held-out >= 0.35 (full-stack HARD-PASS threshold); HARD-FAIL combined < 0.32.

## Context pointers (not summaries)

- research note (this hand-off's parent): d:/AI/hd-instrument/notes/research_drill_svamp_substrate_only_above_030_2x_2026-06-11.md
- prior dep-parser-refuting drill: d:/AI/hd-instrument/notes/research_drill_phase4_math_role_binding_2x_2026-06-11.md
- bipartite engineered vs learned drill (cost-function pattern): d:/AI/hd-instrument/notes/research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md
- Phase4 v2.5 gating fix (gating primitive source): d:/AI/hd-instrument/notes/research_drill_phase4_v2_anchored_regression_2x_2026-06-11.md
- Tier-2 schema codebook (arithmetic class includes target schemas): d:/AI/hd-instrument/notes/research_drill_tier2_problem_schemas_2x_2026-06-11.md
- substrate POS-tagger 0.906 (position-binding empirical precedent): memory file substrate_only_NL_pos_tagger_validated_2026-06-11.md
- SVAMP dataset: github.com/arkilpatel/SVAMP (1000 items + train splits per Patel 2021)

## Contract section

- pre-registered HARD-PASS / HARD-FAIL bands per anchor (above) MUST be locked in cell metadata BEFORE smoke run
- smoke gate: anchor 1 OR anchor 2 standalone before composing
- self-test: cell must self-test perceptron predict signature (per [[feedback-function-signature-mismatch-self-test-blind]])
- envelope-fail-band methodology applies (per existing exp_dev protocol)
- LIFT validation: delta must exceed 2x SE on held-out (per [[feedback-method-overclaim-lift-validation]])
- no LLM in eval loop (per relational-embedding drill 2026-06-11 hand-off)
- if smoke uses MAWPS / ASDiv for training (likely), confirm SVAMP held-out is genuinely disjoint (no overlap with train)

## Autonomy declaration

exp_dev owns:
- exact cell design and pre-reg envelope numbers (within bands above)
- which lane (laptop cpu_runner_local likely best -- CPU-only; data fits in memory; ~1-4 hr runs)
- queue ordering (recommend A1 alone, then if HARD-PASS, compose A1+A2; gate A3+A4 on A2 outcome)
- self-test sufficiency call

research owns:
- the substrate-product framing and lit precedent grounding
- next-drill identification on PARTIAL / HARD-FAIL outcomes (per research note section "next-drill candidate")
