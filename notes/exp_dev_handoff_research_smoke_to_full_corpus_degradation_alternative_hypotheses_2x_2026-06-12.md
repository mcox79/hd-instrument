# exp_dev hand-off -- research: smoke-to-full corpus degradation -- alternative hypotheses 2x drill

Filed-by: research:opus
Date: 2026-06-12
Trigger: research note `notes/research_drill_smoke_to_full_corpus_degradation_alternative_hypotheses_2x_2026-06-12.md`. Diagnoses filter-threshold-curve scale dependence (Heaps + Good-Turing missing-mass) as the new dominant cause candidate after empirical refutation of the partition-stratified-smoke hypothesis from earlier today.

Pause state: respect `data/orchestrator_paused.flag` -- this hand-off does NOT auto-queue; orchestrator decides when to dispatch exp_dev.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchor candidates + context pointers + pre-registered HARD-PASS/FAIL bands. exp_dev designs the cell parameters (smoke seed, threshold-scaling exact value, PPI implementation choice). Research does not pre-encode the cell internals.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY) -- three-design smoke comparison

Pointer: `tools/substrate_self_extension/exp_partition_stratified_smoke_gap_cpu_v1.py` (already exists from this morning's refutation experiment) -- extend with two new design variants.
Substrate-product reading: tests the Heaps-scale-dependence + PPI-calibration replacement methodology for the empirically-refuted partition-stratification rule. If HARD-PASS, ships substrate-extraction-smoke methodology v2.
Tier hint: Tier-3 substrate methodology rule first-appearance candidate (new rule); supersedes the refuted earlier-today rule which should be marked retired.
Why-now: refutation arrived within hours of registration; the methodology blocker on every Phase-2-light extractor cycle is unresolved; lowest-cost-highest-EV diagnostic is to test the named alternatives in one extractor run.

Cheap decisive test (pre-registered by Research):
- Design (A) baseline: OLD homogeneous research_drill smoke at z>=3 (already measured: proxy P@30 = 0.733, gap 0.067).
- Design (B) Heaps-scaled: same files as (A) but with threshold scaled by sqrt(N_full / N_smoke) ~= sqrt(1200/30) = 6.3, so smoke threshold z>=ceil(3/6.3) = z>=1.
- Design (C) PPI-calibrated: use (A) as labeled subset + full-corpus extractor scores as unlabeled proxy; compute Angelopoulos PPI estimate and CI for full-corpus proxy P@30.

HARD-PASS: design (B) gap <= 0.05 AND design (C) PPI estimate matches full within +/- 0.03 with CI half-width <= 0.05.
HARD-FAIL: design (B) gap > 0.15 AND design (C) CI half-width > 0.20.
MIDDLE-BAND [0.05, 0.15]: compose (B) + (C); if composed gap <= 0.05, ship as canonical; otherwise Anchor 2.

### Anchor 2 (CONDITIONAL on Anchor 1 MIDDLE-BAND or partial signal) -- Goodhart-decoupled validation smoke

Pointer: split research_drill into `tuning_smoke_research_drill.txt` (used historically for parameter tuning) + `validation_smoke_research_drill.txt` (NEVER touched during any prior z>=3 tuning).
Substrate-product reading: canonical OOD-eval Goodhart decoupling; restores the smoke-as-prediction property if the smoke and threshold are co-calibrated.
Tier hint: Tier-2 methodology refinement portable to other substrate smoke pipelines.
Why-now: only if Anchor 1 partial-signal indicates threshold-coupling is a residual factor.

Cheap decisive test: run extractor on validation_smoke (Goodhart-decoupled), compute gap vs full corpus; if gap > Anchor 1 (A) baseline gap, Goodhart-coupling is confirmed as the residual cause.

### Anchor 3 (CONDITIONAL on Anchor 1 HARD-FAIL) -- 30-item true-P@K gold set

Pointer: build a hand-annotated gold-standard P@K on 30 substrate atoms manually labeled as TRUE primitive vs FALSE primitive.
Substrate-product reading: resolves whether the proxy P@K is itself the issue (hypothesis 4 in the research note); provides the true-P@K signal Research has been awaiting for canonical claims.
Tier hint: Tier-3 substrate-quality-first ground-truth infrastructure.
Why-now: only if Anchor 1 HARD-FAILs (Heaps mechanism refuted). The proxy may be the source of the smoke-vs-full divergence rather than the smoke itself.

Cheap decisive test: 30 atoms manually labeled (~3 hr annotation), compute true P@K on smoke + full, compute proxy-vs-true Kendall tau. If tau < 0.7, proxy is unreliable and methodology gap is in the proxy, not the smoke.

### Anchor 4 (CONDITIONAL on all above MIDDLE-BAND) -- statAP/infAP pool-based estimator

Pointer: implement Aslam-Pavlu-Yilmaz statAP for substrate-extraction-pool sampling with importance weights.
Substrate-product reading: replaces threshold-based smoke entirely with a non-uniform-sampled-pool with importance-weighted Horvitz-Thompson estimator; gives valid CIs at any K, any N.
Tier hint: Tier-3 methodology infrastructure; if it works, becomes the canonical substrate-evaluation-pool primitive across all extraction pipelines.
Why-now: only if Anchors 1-3 give no clean signal; investment of ~1 day to implement.

---

## Context pointers (file paths, not summaries)

- Research note this hand-off ships from: `notes/research_drill_smoke_to_full_corpus_degradation_alternative_hypotheses_2x_2026-06-12.md`
- Empirical refutation experiment (this morning): `tools/substrate_self_extension/exp_partition_stratified_smoke_gap_cpu_v1.py`; saved batches `data/substrate_index/bench_reports/partition_stratified_smoke_batches.json`
- Refuted earlier-today research note (still valid as a record of refuted hypothesis): `notes/research_drill_smoke_to_full_corpus_degradation_methodology_partition_stratified_smoke_substrate_quality_first_2x_2026-06-12.md`
- Companion refuted handoff: `notes/exp_dev_handoff_research_smoke_to_full_corpus_degradation_partition_stratified_smoke_2026-06-12.md`
- Prior 2026-06-09 capability-smoke drill (DIFFERENT failure mode, do not conflate): `notes/research_drill_smoke_vs_full_methodology_2x_2026-06-09.md`
- Memory refutation flag: `substrate_stratified_smoke_does_not_help_diffuse_jargon_handled_by_recurrence_2026-06-12.md`
- Substrate-quality-first feedback: `feedback_full_auto_productivity_look_harder_2026-06-12.md`

---

## Contract

- exp_dev designs cell parameters (smoke seed, exact threshold-scaling formula, PPI implementation library choice, gold-set construction protocol). Research has provided the pre-registered HARD-PASS / HARD-FAIL bands and the structural recipe (Heaps-scaling, PPI calibration, Goodhart decoupling).
- Pre-reg discipline: lock HARD-PASS / HARD-FAIL bands BEFORE running cells; gap thresholds 0.05 / 0.15 are research-pre-registered. PPI CI half-width 0.05 / 0.20 are research-pre-registered.
- exp_dev self-tests per formula-selftests; smoke gate before ship; REMOTE VERIFY post-ship.
- Pause-gated: `data/orchestrator_paused.flag` respected.
- Methodology-ledger discipline: if Anchor 1 HARD-FAIL, register new rule retirement signal (refuted Heaps-scale-dependence hypothesis); if HARD-PASS, promote the new rule from candidate to confirmed.

## Autonomy declaration

exp_dev owns: cell seed, exact threshold-scaling value (sqrt(40)~6.3 is the principled choice but exp_dev may tune within [4, 10]), PPI library choice (Angelopoulos `ppi-py` if available, else custom implementation), gold-set annotation protocol if Anchor 3 triggered, choice of which anchor to run first (Anchor 1 PRIMARY unless ops state indicates otherwise).

Research owns: methodology rule registration (1st-appearance criteria for the new rule + retirement signal for the refuted rule), pre-registered gap and CI bands, mechanism-class enumeration, lit citations.

Orchestrator owns: dispatch timing, pause-gate enforcement, cap_map row decision after verdict, retirement of the earlier-today refuted methodology-rule from any active rule registry.
