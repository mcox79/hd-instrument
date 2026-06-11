# exp_dev hand-off — research: substrate-only NL SYNTHESIS feasibility

Filed-by: research (Opus)
Date: 2026-06-11
Trigger: research_drill_substrate_only_nl_synthesis_2x_2026-06-11.md — 2x DEEP drill verifying frontier-scale claim "LLM front-end stays for NL fluency"
Pause state: respect data/orchestrator_paused.flag; this hand-off is structural, not for immediate dispatch unless pause is lifted.

Per [[feedback-no-experiment-design-in-prompts]] — exp_dev owns the empirical design; this hand-off lists ANCHORS, not cells. Pre-registered HARD-PASS / HARD-FAIL bands live in the research note.

## Anchor candidates (rank-ordered)

### Anchor 1 (Tier-1, highest leverage) — PILOT-NLG-1: substrate-only template-fill on E2E-NLG-cleaned
- Substrate-product reading: tests whether substrate has a structured-NLG capability (BLEU-4 >= 0.40 + slot-error-rate <= 0.10 on E2E test set). PASS opens substrate.generation.TemplateLibrary as a Tier-1 product surface (calibrated form-fill / structured report generation; differentiated vs LLMs on determinism, sub-100ms latency, sub-100MB deployment, conformal coverage on each emitted field).
- Tier hint: Tier-1 (resolves the structured-NLG sub-question of the substrate-LLM boundary memory)
- Why now: pilot uses ONLY existing substrate primitives (binding, bundling, cleanup, trajectory-association, role binding); ~4 hours CPU; if PASS, IMMEDIATELY unlocks 4-5 follow-on domain pilots (WeatherGov, WikiBio, RotoWire, structured-report templates).
- Pre-reg pointer: research_drill_substrate_only_nl_synthesis_2x_2026-06-11.md PREDICTION-1.

### Anchor 2 (Tier-1, structural-decider) — PILOT-NLG-2: substrate-bundled n-gram perplexity benchmark
- Substrate-product reading: tests whether substrate-stored n-gram count distributions CAN be losslessly represented (PP-ratio substrate/KN-4gram in [0.95, 1.30]). PASS validates substrate as a viable storage primitive for ANY count-based language model; FAIL flags codebook-capacity ceiling that bounds Anchor 1 and Anchor 3 from above.
- Tier hint: Tier-1 (foundational; if it fails, Anchors 1 and 3 are likely capped)
- Why now: dependency for Anchor 1 confidence; cheap (~2-4 hours CPU); answers Marchenko-Pastur-edge / codebook-capacity question with empirical data BEFORE bigger pilots commit.
- Pre-reg pointer: PREDICTION-2.

### Anchor 3 (Tier-2, lift-amplifier) — VSA-CFG production-rule grammar constraint on Anchor 1 output
- Substrate-product reading: tests whether resonator-CFG constraint adds incremental BLEU-4 >= 0.03 over Anchor 1 alone. PASS supports a substrate.generation.GrammarConstraint primitive grounded in beim-Graben VSA-CFG framework.
- Tier hint: Tier-2 (depends on Anchor 1 PASS to even be runnable)
- Why now: SECOND if Anchor 1 PASSes; held otherwise.
- Pre-reg pointer: PREDICTION-3.

### Anchor 4 (Tier-2, hybrid validation) — substrate + small TinyStories-class LM hybrid on controlled domain
- Substrate-product reading: tests whether the hybrid retrieve-template + small-LLM-fill outperforms either alone by >= 0.05 BLEU-4 on E2E. Validates the substrate-LLM-honest-hybrid product framing for dialogue / report generation with creative passages.
- Tier hint: Tier-2
- Why now: only if Anchor 1 PASSes (otherwise hybrid is just LLM-only)
- Pre-reg pointer: PREDICTION-5.

### Anchor 5 (HOLD pending Anchor 1) — open-domain ceiling probe
- Substrate-product reading: substrate-only WikiText-103 perplexity vs TinyStories-1M transformer. Bounds the open-domain creative claim. Honest-bound experiment for product positioning.
- Tier hint: Tier-3 (small confidence on substrate-side; bounding-claim experiment)
- Why now: HOLD until Anchor 1 result; only run if user explicitly wants the open-domain bound quantified.
- Pre-reg pointer: PREDICTION-4.

## Context pointers (file paths, not summaries)

- notes/research_drill_substrate_only_nl_synthesis_2x_2026-06-11.md (this hand-off's filing-trigger)
- notes/research_drill_code_synthesis_substrate_feasibility_2x_2026-06-11.md (sibling drill; identical structural argument applied to code; same hybrid-template-fill recipe)
- notes/research_drill_substrate_structured_prediction_2x_2026-06-11.md (CRF/structured-SVM/EBM substrate-native framework; provides decoder machinery for Anchor 1)
- notes/substrate_only_NL_pos_tagger_validated_2026-06-11.md (substrate-classical NL precedent at 0.906; same machinery basis)
- notes/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md (count-based-classical pattern that Anchor 2 directly applies)
- notes/research_drill_substrate_conformal_calibration_2x_2026-06-11.md (calibration math attached to Anchor 1 output)
- notes/substrate_LLM_boundary_decomposition_2026-06-10.md (the boundary memory that Anchor 1 result will revise)

## Contract section

This hand-off:
- pre-registers HARD-PASS and HARD-FAIL thresholds for every anchor
- defers experiment design / cell construction to exp_dev (autonomy declaration below)
- is structural — exp_dev picks order, runner-lane, smoke-vs-full, pre-reg verification
- is pause-gated; does not bypass data/orchestrator_paused.flag

## Autonomy declaration

exp_dev decides:
- which anchor first (recommend Anchor 2 BEFORE Anchor 1 because Anchor 2 validates Anchor 1's storage primitive)
- runner-lane (GPU / CPU / local_cpu_queue)
- smoke-vs-full sequence
- whether to combine Anchor 1 + 3 into a single 2-condition pre-reg
- whether Anchor 5 ever runs (bounding-claim; consult user if it would consume a non-trivial budget)

research is NOT specifying cells; research is specifying capability questions and pass/fail thresholds. exp_dev owns build, smoke gate, queue dispatch, REMOTE VERIFY, and self-test per [[formula-selftests]].
