# exp_dev hand-off -- research: unified-solver SVAMP rescue (2x DEEP)

filed-by: research:opus
trigger: 2x DEEP drill on unified-solver SVAMP collapse (specialized 0.297 -> unified 0.147 under MAWPS-heavy pool); user-requested research drill 2026-06-11
research-note: d:/AI/hd-instrument/notes/research_drill_unified_solver_svamp_rescue_2x_2026-06-11.md
pause-state: check data/orchestrator_paused.flag before queueing; if paused, file as authorized anchor for next refill

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists anchor CANDIDATES with substrate-product reading and tier hints; exp_dev owns the implementation design.

## Anchor candidates (rank-ordered)

### Anchor 1. SVAMP-RESCUE-A: per-benchmark context-binding in unified solver
- anchor pointer: research note, Path A (context-binding TP-HDC pattern)
- substrate-product reading: single-solver API surface with provably-separated context subspaces via orthogonal context HVs; per-inference (op, benchmark_context, margin) triple is the audit envelope for the auditable-AI-memory v1 demo
- tier hint: TIER A (cheap decisive test, single CPU cell, < 1 hr, no GPU)
- why-now: Path A is the cheap-decisive shipping order; mechanism-ready (substrate PP-346 + TP-HDC literature precedent); structurally identical to image-schema polysemy rescue (0.342 -> 1.000 HP)
- pre-reg: HARD-PASS unified-with-context SVAMP >= 0.80 x specialized SVAMP AND unified-with-context MAWPS >= 0.95 x current unified MAWPS; HARD-FAIL unified-with-context SVAMP < 1.10 x current unified-uncontextualized SVAMP OR MAWPS drops below 0.90 x current unified MAWPS

### Anchor 2. SVAMP-RESCUE-B: cleanup-margin-gated soft mixture-of-experts (depends on A)
- anchor pointer: research note, Path B (substrate-native router via cleanup margin)
- substrate-product reading: no learned router needed; substrate cleanup margin IS the natural router signal; combine per-benchmark Tier-2 schemas with shared Tier-1 cleanup
- tier hint: TIER A (additive on top of Anchor 1; soft mixture is one-line addition)
- why-now: ship after Anchor 1 PASS; pairs A+B is the natural unified-solver-v2
- pre-reg: HARD-PASS soft-margin macro-mean strictly above A-only AND strictly above hard-arg-max-on-context-tag routing; HARD-FAIL within +/- 1 SE of A-only

### Anchor 3. SVAMP-RESCUE-C: inverse-frequency / effective-number reweighting (ablation / control)
- anchor pointer: research note, Path C (Salmani-Worah 2025 + Cui 2019 reweighting)
- substrate-product reading: amplitude reweighting at prototype bundling; weaker mechanism (does not change geometry); use as ablation to validate H3
- tier hint: TIER B (control / ablation; ship only if Anchor 1 PARTIAL; small CPU cell)
- why-now: if A PARTIAL, C tests whether the residual gap is class-imbalance vs representational-interference
- pre-reg: HARD-PASS-of-the-NEGATIVE reweighting-alone SVAMP improvement < 0.5 x context-binding SVAMP improvement (expected); HARD-FAIL reweighting alone recovers >= 0.8 x context-binding gain (would mean the issue is class-imbalance not representational-interference and would refute the binding-priority claim)

### Anchor 4. SVAMP-RESCUE-D: interleaved anti-curriculum (additive layer on top of A+B+C)
- anchor pointer: research note, Path D (anti-curriculum + interleaved per-batch balance)
- substrate-product reading: training-order layer; brittle without binding; only ship after A+B
- tier hint: TIER C (additive only after A+B+C ship; do not ship as primary)
- why-now: HOLD until A and B verdicts in; combine with C in single cell when ready
- pre-reg: HARD-PASS anti-curriculum order combined with C closes >= 30 percent of unified-vs-specialized SVAMP gap; HARD-FAIL no closure

## Context pointers (file paths, not summaries)

- research note (full mechanism + math + citations): d:/AI/hd-instrument/notes/research_drill_unified_solver_svamp_rescue_2x_2026-06-11.md
- prior exp_dev report (unified seed-robust 0.442; specialized macro 0.538): d:/AI/hd-instrument/notes/exp_dev_to_research_UNIFIED_044_CODE_4D_TASKFIT_2026-06-11.md
- multibench source data: data/exp_phase4b_multibench_solver_cpu_v1/metrics.json
- richfeat SVAMP specialized baseline: data/exp_phase4b_svamp_richfeat_cpu_v1/metrics.json
- unified multiseed source: data/exp_phase4b_unified_multiseed_cpu_v1/metrics.json
- PP-346 / image-schema polysemy rescue (structurally identical mechanism): memory file substrate_representation_artifacts_rescued_2026-06-10.md
- substrate-classical NL methods memory (Tier-2 bundle pattern this builds on): substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md

## Contract section

- exp_dev owns the implementation design and the smoke-gate methodology per [[feedback-smoke-test-methodology]] (composition-matched smoke + CI-band rule + multi-seed at HP boundaries)
- per [[feedback-method-overclaim-lift-validation]]: validate LIFT > 2 x SE on Anchor 1 (single-seed pass alone is not sufficient — multi-seed required at HP boundary)
- substrate hyperdimensional bipolar context HVs at N=1024; orthogonality is by construction (|<ctx_i, ctx_j>| ~ 1/sqrt(N)); no additional codebook training needed for context HVs
- generic-math terms only if any further off-platform queries needed per [[feedback-query-privacy-decomposition]]

## Autonomy declaration

exp_dev is autonomous on:
- whether to ship Anchor 1 alone first or A+B together as single cell
- choice of substrate variant for binding (XOR / circular-conv) — match current unified-solver pipeline
- smoke configuration and seed count
- whether to also ablate Anchor 3 in the same cell as Anchor 1 (efficient since both touch the prototype bundling step)
- when to escalate back to research (if HARD-FAIL on Anchor 1, file a routing-back note and research will drill into why binding failed)

Research is on hand for: HP tuning questions, mechanism clarifications, or HARD-FAIL diagnosis.
