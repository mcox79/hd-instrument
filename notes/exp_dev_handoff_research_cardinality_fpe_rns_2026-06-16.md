# exp_dev hand-off — research: cardinality / FPE / RNS counting primitive

**Filed by.** research (Opus)
**Date.** 2026-06-16
**Trigger.** `notes/research_cardinality_fpe_rns_counting_accuracy_2026-06-16.md` — lit-scan finding: NO published paper reports exact-count RMSE or quantifier accuracy at N=4096 for FPE/RNS-HDC; only one prior VSA-cardinality probe exists (Alam 2023 arXiv:2312.15310, subitizing-with-HRR); two external benchmarks are cheap-decisive (Steinert-Threlkeld quantifier-RNN suite + bAbI Task 7 1K). HARD-PASS / HARD-FAIL pre-registered in research note section (c).

**Pause state.** Check `data/orchestrator_paused.flag` before queue_add. exp_dev session is pause-gated; if paused, this hand-off sits in inbox until resume.

Per [[feedback-no-experiment-design-in-prompts]]: research filed structural pointers + pre-registered envelopes. Experiment cell design is exp_dev's province. Do NOT take the HARD-PASS / HARD-FAIL bands in the research note as a finalized cell spec — they are the falsifiability contract. exp_dev designs the cells, smoke-gates, and pre-registers per envelope-fail-bands.

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY) — `anchor_cardinality_primitive_quantifier_rnn_v1`

- **Anchor pointer.** Quantifier-RNN suite from Steinert-Threlkeld & Szymanik (github.com/shanest/quantifier-rnn-learning), generators for at-least-k, exactly-k, majority. Pre-existing public synthetic benchmark; deflated novelty concern.
- **Substrate-product reading.** Tests whether substrate's bundle representation + a candidate FPE/RNS cardinality primitive closes a quantifier-typed operator class. Aligns with Phase B "GROW BASIS" direction per DECISION 142.
- **Tier hint.** Tier-2 basis-gap close candidate (parallel to corr(bundle(a,b),c) Tier-2 close per DECISION 139-141), different signature class (quantifier-typed, not relation-typed).
- **Why now.** Lit-scan finds GENUINE GAP — no published baseline at N=4096 for this exact axis. External benchmark removes ad-hoc-synthetic confound class. Cheap (CPU smoke ~30 min for 5K examples per quantifier class).
- **Falsifiability pre-reg envelope.** Per research note (c): at-least-k accuracy >= 0.90 (HARD-PASS), <= 0.65 (HARD-FAIL). exactly-k accuracy >= 0.80 (HARD-PASS), no separate HARD-FAIL beyond joint MIDDLE-BAND. Multi-seed std <= 0.03 on quantifier accuracy (HARD-PASS), > 0.40 on RMSE (HARD-FAIL). Joint P(both HARD-PASS) = 0.18 deflated.

### Anchor 2 (FLOOR-SANITY) — `anchor_cardinality_babi_t7_1k_v1`

- **Anchor pointer.** bAbI Task 7 (counting) 1K split. Public; Weston et al.
- **Substrate-product reading.** Pure floor-sanity. SOTA saturated (EntNet ~100%, DNC 99.4%); vanilla LSTM 80.4%. Substrate primitive must reach >= 0.85 to claim it does no harm.
- **Tier hint.** NOT a novelty axis — this is a "primitive is functional" floor. Run together with Anchor 1; if Anchor 1 PASSes but bAbI < 0.65, primitive is suspicious (HARD-FAIL).
- **Why now.** Cheapest possible reference floor (1K split). Reading: this anchor cannot move the cap_map by itself; it is a sanity rail for Anchor 1.
- **Falsifiability pre-reg envelope.** >= 0.85 (HARD-PASS / sanity); < 0.65 (HARD-FAIL — primitive harms baseline).

### Anchor 3 (RISK-COVERAGE) — `anchor_cardinality_cleanup_noise_sweep_v1`

- **Anchor pointer.** Cleanup-noise stress sweep at sigma in {0.05, 0.10, 0.20, 0.40} on Anchor 1's at-least-k task.
- **Substrate-product reading.** Two independent sub-agent reports flagged cleanup-noise as the binding constraint at high D. This anchor tests whether primitive's gap over bundle-norm-only baseline survives realistic-noise regimes.
- **Tier hint.** RISK-COVERAGE not Tier — gates Anchor 1's claim that primitive (not cleanup) is load-bearing.
- **Why now.** Per [[feedback-dont-dismiss-adjacent-methods]]: cleanup is mathematically adjacent; dismissing without dispatch is the dominant failure mode (Pattern 5 of meta-map). Pre-register the stress sweep BEFORE running Anchor 1, not as an afterthought.
- **Falsifiability pre-reg envelope.** Primitive's gap over baseline persists at sigma=0.20 with reduction <= 40% (HARD-PASS). Gap collapses to bundle-norm-only floor at sigma=0.20 (HARD-FAIL — primitive does no work above cleanup limit).

## Context pointers (file paths, not summaries)

- Research note: `d:/AI/hd-instrument/notes/research_cardinality_fpe_rns_counting_accuracy_2026-06-16.md`
- Strategic direction (DECISION 142): `memory/substrate_director_session_2026_06_15_to_16_DECISION_142_TIER_2_NOVEL_COMPOSITION_EXISTENCE_PROVEN_USER_INTUITION_VALIDATED_strategic_direction_consolidate_then_grow_basis.md`
- Gap-driven loop precedent: `memory/substrate_gap_driven_loop_END_TO_END_validated_2026-06-15_phase_B_C_abduction_novel_assembly.md`
- Quantifier-RNN code: github.com/shanest/quantifier-rnn-learning (external)
- Alam 2023 HRR-subitizing precedent: arXiv:2312.15310
- Kymn 2024 RHDC: arXiv:2311.04872 (capacity baseline, not cardinality)
- bAbI Task 7: standard, Weston et al.
- Frady-Sommer crosstalk-noise theory: arXiv:1803.00412 (for multi-seed variance prior)

## Contract

- Verify before queue_add (per [[feedback-ship-before-dependency-verified]]):
  1. FPE/RNS encoding primitive exists in `hdlab/` or `reference/`; if not, build the closed-form theory + oracle in `verification/theory.py` FIRST (CLAUDE.md verification discipline).
  2. Bundle-norm-only baseline implementation exists and is benchmarkable on the chosen anchors.
  3. Quantifier-RNN generator script can be vendored / wrapped in `verification/` or `tools/` (it is public BSD code; check license before vendoring).
  4. bAbI T7 1K split downloadable / cached.
- Smoke gate: run Anchor 1 at N=1024 with bundle-size <= 6 first; if RMSE > 2.0 OR quantifier accuracy < 0.40 OR runtime > 10 min per seed, halt and rebuild before scaling to N=4096.
- Pre-register per-cell envelope-fail-bands BEFORE seeding (HARD-PASS / HARD-FAIL / MIDDLE-BAND per anchor).
- Self-test the cardinality primitive's closed-form expected RMSE on a synthetic toy (bundle of 5 FPE-encoded integers, expected exact-count RMSE from crosstalk-noise theory Frady-Sommer 2018) BEFORE running on Anchor 1.
- Reproduce LSTM baseline on chosen quantifier classes BEFORE claiming gap — see Risk 2 in research note.
- Multi-seed: n=5 minimum on Anchor 1; n=3 acceptable on Anchor 2/3 (Anchor 2 is floor-sanity, Anchor 3 is risk-coverage).
- Honest reporting: if HARD-FAIL on any anchor, surface in verdict_msg and per_cell_metrics. Do NOT down-weight or re-scope.

## Autonomy declaration

- exp_dev chooses queue (CPU likely sufficient; GPU acceptable for N=4096 batching).
- exp_dev chooses execution order (recommended: Anchor 2 floor-sanity at N=1024 first to catch primitive bugs cheap; then Anchor 1 at N=1024 smoke; then Anchor 3 cleanup sweep; then Anchor 1 at N=4096 if smoke passes).
- exp_dev estimates ETA; surface if exceeds 6h compute.
- exp_dev applies the standard cell-template / formula-selftests / smoke-gate / REMOTE VERIFY pipeline.
- exp_dev sets verdict_msg and outcome_class per the pre-registered envelope-fail-bands.

## ETA estimate (rough, exp_dev refines)

- CPU smoke: Anchor 2 (bAbI T7 1K) ~15 min; Anchor 1 (quantifier-RNN at N=1024) ~30 min per seed; Anchor 3 (4-sigma sweep) ~2 hours; Anchor 1 at N=4096 ~1-2 hours per seed.
- Total wall-clock with n=5 seeds Anchor 1, n=3 Anchor 2/3: ~8-12 hours CPU; ~2-3 hours GPU if seeds parallelize.

Recommend CPU queue (anchors are small; GPU adds queue contention with substrate-foundation work in flight per DECISION 142 Phase A consolidate).

---

**Verdict wiring.**
- `verdict_msg`: per-anchor HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL plus joint call.
- `outcome_class`: one of {CARDINALITY-PRIMITIVE-LOAD-BEARING, CARDINALITY-PRIMITIVE-REFUTED, CLEANUP-DOMINATES, MIDDLE-BAND, INSTRUMENTATION-FAIL}.
- `per_cell_metrics`: dict with anchor_id -> {accuracy / RMSE, std, sigma (for Anchor 3), band_call}.
