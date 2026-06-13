# exp_dev hand-off -- research: smoke-to-full corpus degradation methodology (partition-stratified smoke + substrate-quality-first refinement)

Filed-by: research:opus
Date: 2026-06-12
Trigger: research note `notes/research_drill_smoke_to_full_corpus_degradation_methodology_partition_stratified_smoke_substrate_quality_first_2x_2026-06-12.md` -- partition-composition mismatch identified as dominant cause of -0.17 to -0.44 smoke-to-full P@30 degradation across 3 self-extension iterations.

Pause state: respect `data/orchestrator_paused.flag` -- this hand-off does NOT auto-queue; orchestrator decides when to dispatch exp_dev.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchor candidates + context pointers. exp_dev designs the experiment. Research does not pre-encode cell parameters.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY) -- partition-stratified-smoke validation cell

Pointer: `tools/substrate_self_extension/` (existing Tier-A extractor) + add `--scope partition-stratified-smoke` flag.
Substrate-product reading: validates the substrate-self-extension-smoke-must-be-partition-stratified methodology rule (1st appearance). If HARD-PASS, ships a substrate-product-level methodology artifact.
Tier hint: Tier-3 (substrate methodology rule first-appearance candidate); promotion to Tier-4 on second independent iteration.
Why-now: 3 consecutive self-extension iterations have failed with the same shape; the fix is structural (sampling design), not extractor-level (filter tuning), so additional filter-tuning cycles will not resolve. Lowest-cost-highest-EV next step.
Cheap decisive test (pre-registered in research note): build 30-file stratified smoke (5 per partition x 6 partitions), run extractor, compute gap vs full corpus P@30. HARD-PASS |gap| <= 0.05. HARD-FAIL |gap| > 0.15. MIDDLE [0.05, 0.15] triggers Anchor 2.

### Anchor 2 (CONDITIONAL on Anchor 1 MIDDLE-BAND) -- scope-aware per-partition filter regime

Pointer: `tools/substrate_self_extension/partition_filters/<partition>.yml` (new dir, one config per partition).
Substrate-product reading: addresses residual gap after stratification -- per-partition jargon mask + acceptance threshold per partition class.
Tier hint: Tier-3 substrate-quality-first refinement of existing class-aware tool extension pattern.
Why-now: only if Anchor 1 lands in middle band (stratification helps but does not close gap). Otherwise skip.
Cheap decisive test: per-partition gold-set of n=10 items from each of 6 partitions; tune per-partition threshold to gold; re-run stratified smoke + full corpus; report aggregate + per-partition P@30 + spread.

### Anchor 3 (CONDITIONAL on Anchor 1 HARD-FAIL) -- held-out validation smoke (Goodhart decoupling)

Pointer: separate the smoke into TWO files: `tuning_smoke.txt` (research_drill only, used for parameter fit) and `validation_smoke.txt` (held-out stratified, NEVER touched during parameter fit).
Substrate-product reading: canonical OOD-eval methodology -- the smoke metric must be uncoupled from the parameter-tuning loop or it ceases to predict deployment.
Tier hint: Tier-2 methodology refinement; immediately portable to other substrate smoke pipelines (capability smokes per 2026-06-09 drill).
Why-now: only if Anchor 1 HARD-FAILs -- means even stratified smoke does not predict, suggesting the extractor itself has overfit to research_drill and a structural decoupling is needed.

---

## Context pointers (file paths, not summaries)

- Research note this hand-off ships from: `notes/research_drill_smoke_to_full_corpus_degradation_methodology_partition_stratified_smoke_substrate_quality_first_2x_2026-06-12.md`
- Prior drill on capability smokes (related, different problem): `notes/research_drill_smoke_vs_full_methodology_2x_2026-06-09.md`
- 6-partition design validated empirically: memory file `substrate_self_validates_own_partition_design_at_scale_2026-06-11.md`
- Substrate self-extension memory: `substrate_as_self_extending_engine_2026-06-12.md`
- Substrate-quality-first feedback: `feedback_full_auto_productivity_look_harder_2026-06-12.md`
- Tier-A NL primitives extractor: `tools/substrate_self_extension/` (assumed path; exp_dev verifies)

---

## Contract

- exp_dev designs the cell parameters (smoke set seed, gold-set size, threshold sweep range). Research has provided the pre-registered HARD-PASS / HARD-FAIL bands and the structural recipe (stratified-by-partition, proportional allocation, fixed seed, per-partition reporting).
- Pre-reg discipline: lock the HARD-PASS/FAIL bands BEFORE running the cell; gap thresholds 0.05 / 0.15 are research-pre-registered.
- exp_dev self-tests per formula-selftests; smoke gate before ship; REMOTE VERIFY post-ship.
- Pause-gated: `data/orchestrator_paused.flag` respected.

## Autonomy declaration

exp_dev owns: cell seed, gold-set construction, threshold sweep design, per-partition filter regex authoring (if Anchor 2 triggered), tuning/validation smoke split mechanics (if Anchor 3 triggered), choice of which anchor to run first (Anchor 1 PRIMARY unless ops state indicates otherwise).

Research owns: the methodology rule registration (1st appearance criteria + 2nd appearance trigger), pre-registered gap bands, partition enumeration, lit citations.

Orchestrator owns: dispatch timing, pause-gate enforcement, cap_map row decision after verdict.
