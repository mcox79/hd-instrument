# exp_dev hand-off -- research: Tier-5 substrate-self-knowledge benchmark v1

Filed-by: research (Opus)
Filed: 2026-06-12 (drill filed 2026-06-11 evening)
Trigger: notes/research_drill_substrate_tier_5_benchmark_design_2x_2026-06-12.md (read this FIRST -- authoritative spec)
Pause state: respect data/orchestrator_paused.flag; this hand-off is design-spec only (no queue add); pickup is exp_dev autonomous decision per skill contract

Per [[feedback-no-experiment-design-in-prompts]] -- this file gives ANCHORS not experiment recipes. exp_dev designs cells.

## Anchor candidates (rank-ordered)

### A1 -- BENCHMARK-PARTITION-V1 (rank 1; SHIP CANDIDATE)
Anchor pointer: substrate-self-index 9th partition `benchmark/` carrying ~100 Q atoms across types A-G + ~20% unanswerable + ground-truth atom-refs.
Substrate-product reading: directly delivers Findings 18 Gap 3 + Gap 7 closure as a shippable feature ("ask substrate what it knows"); auditable-AI-memory-subsystem strategic direction support; LLM differentiator via honest abstention (AbstentionBench frontier-LLM <1% abstention baseline).
Tier hint: Tier B on initial v1 ship; Tier A if F+G surfaces 1+ event passing F1-F4 within 60 days post math+science corpus phase.
Why-now: Findings 18 explicitly named this gap; companion pathway drill M1 needs an operational detection channel; substrate-self-index 15 modules are deployed and ready; cost ~3 days dev + 1 day research authoring.
Implementation contract pointers:
 - drill section (b) steps 1-6 = end-to-end design
 - section (e) Component 1 = partition design
 - section (e) Component 2 = 4-cell TP/FN/TN/FP metric
 - section (e) Component 3 = template-instantiate generation
 - section (e) Component 5 = unanswerable-Q reservation
 - section (f) = 7 example templates (one per type)
 - section (g) = measurement plan (setup -> baseline -> watch -> sustained-rate)

### A2 -- F1-F4 FILTER PIPELINE INFRASTRUCTURE (rank 2; COMPANION ANCHOR)
Anchor pointer: pipeline routing Type F+G benchmark answers through 4-stage filter (in-substrate analog + literature analog + cell-test direction + independent-verifier reproducibility).
Substrate-product reading: reusable infrastructure for ALL Tier-5 candidate events not just benchmark; becomes the Tier-5 detection backbone per companion pathway drill.
Tier hint: Tier B (infrastructure rather than capability); Tier A status follows if it catches 1+ M1 event.
Why-now: M1 detection needs operational channel; F-G benchmark answers are the highest-volume source of Tier-5 candidates expected over next 60 days; cell-test queue is ready; WebSearch budget exists.
Implementation contract pointers:
 - companion drill: notes/research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md section (b) steps F1-F4
 - this drill: section (e) Component 4 = how to route benchmark answers into the filter

### A3 -- BASELINE BENCHMARK RUN PRE-CORPUS (rank 3; CALIBRATION ANCHOR)
Anchor pointer: run benchmark v1 against current substrate state (583 atoms, 8 partitions) BEFORE math+science corpus phase ingest.
Substrate-product reading: establishes Tier-4 baseline calibration curve; all Tier-5 deltas measured relative to this baseline.
Tier hint: methodology / measurement-foundation anchor (no tier in itself); enables tier assignment for A1.
Why-now: must happen BEFORE corpus phase ingest to be valid baseline; corpus ingestion is on the immediate near-term roadmap per Day 2 directive.
Implementation contract pointers:
 - this drill section (g) "baseline measurement (T1, end of day 3)" block
 - 4-cell confusion + F1 per type + HONESTY + DISCOVERY metrics required at baseline

## Context pointers (file paths, no summaries)

- notes/research_drill_substrate_tier_5_benchmark_design_2x_2026-06-12.md (this drill -- authoritative spec)
- notes/research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md (M1-M5 milestones + F1-F4 filter)
- notes/research_drill_substrate_self_discovery_validation_2x_2026-06-11.md (companion validation drill)
- notes/research_to_testbed_FINDINGS_18_ENDORSED_SCIENCE_TAXONOMY_INCOMING_2026-06-11.md (Findings 18 endorsement, Gap 3 + Gap 7 origin)
- notes/research_to_testbed_SCIENCE_ALGEBRA_TAXONOMY_2026-06-11.md
- backend/substrate_index/ (15 modules, 4 partitions, the reuse target for benchmark partition)
- memory/substrate_self_index_foundational_tool.md
- memory/substrate_two_axes_semantic_vs_content_referenced_2026-06-11.md
- memory/substrate_content_sources_us_or_substrate_2026-06-11.md (rule 8 -- Research authors templates; substrate extends via Layer 3)
- memory/feedback_literature_is_not_oracle_2026-06-11.md
- memory/feedback_dont_parrot_drill_defeatism_2026-06-11.md

## Contract section

This file:
 - DOES name anchors and pointer-to-spec
 - DOES NOT design cells or specify hyperparameters
 - DOES NOT trigger queue add (exp_dev decides pickup per pause flag + queue depth)
 - DOES re-iterate that template authoring is RESEARCH responsibility (drill section f preview) -- exp_dev runs harness, not template authoring
 - Pre-registered HARD-PASS / HARD-FAIL / MIDDLE-BAND thresholds in this drill section (c) -- exp_dev must respect these at v1 ship time

Sequence dependency:
 1. Research authors 35 templates + ~20 unanswerable-Q + F-G curated ground-truth list (~1 day; not exp_dev work)
 2. exp_dev implements partition + auto-instantiation + ground-truth derivation + run-harness + metrics (~2 days)
 3. exp_dev wires F1-F4 filter routing for Type F+G answers (~1 day)
 4. exp_dev runs baseline benchmark (~1 hr CPU + report)
 5. exp_dev integrates weekly-run watch (cron or manual) for Tier-5 watch phase

## Autonomy declaration

exp_dev decides: implementation language for run-harness; metric reporting format; whether benchmark partition uses same schema as existing 8 partitions or extended schema; whether unanswerable-Q ground-truth is sentinel-atom or null-pointer; cell-test queue cadence for F1-F4 stage 3; whether baseline run happens on home (GPU) or local (CPU) runner.

exp_dev does NOT decide: question type taxonomy (A-G fixed in drill); 4-cell metric requirement (mandatory per MEDLEY-BENCH); 20% unanswerable reservation (mandatory for HONESTY axis); F1-F4 filter steps (fixed in companion pathway drill); HP/HF/MB thresholds in drill section (c).
