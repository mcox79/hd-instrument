# exp_dev hand-off -- research: Development-Speed Acceleration Phase 4a Infrastructure

## Filed-by
Research sub-agent, 2026-06-05

## Trigger
Research note: notes/research_drill_dev_speed_acceleration_phase4a_infrastructure_2x_2026-06-05.md
Topic: 2x deep drill on dev-speed bottlenecks across training/digestion, tooling, process, and paradigm-change levers.

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
CPU-only anchors (A2-smoke, B1-prototype) are not pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY -- process change, 1-2 days, no GPU)
Pointer: Section C2 of research note (pre-registered rescue paths)
Substrate-product reading: Every cell shipped without pre-registered rescue cells incurs ~0.5-1 day "what next" latency after a HARD-FAIL event. Pre-registering rescue cells at ship time eliminates this latency structurally.
Tier hint: Process change + template update; no code required beyond checklist enforcement. Zero compute cost.
Why-now: Immediately applicable to the next queued cell. Compounds over all future cells. Highest ROI per engineering day of any item on this list.
Task: Update the cell spec template (or queue_add.py validation) to require per-cell rescue cell pointers before admission. Implement as a checklist gate. Define the three rescue slots: HF_R1 (parameter neighborhood), HF_R2 (alternative architecture), HF_R3 (cap_map adjacent variant). Add template to standard cell handoff format.

### Anchor 2 (HIGH PRIORITY -- CPU, 1-2 days build + $200-400 cloud)
Pointer: Section A2 of research note (Wikipedia activation pre-extraction cache)
Substrate-product reading: Current extraction cost for Wikipedia-derived experiments is ~$30-86 per 1M facts + 10h wall. A one-time pre-extraction of mean-pooled layer-10 activations for all of Wikipedia (~6.7M articles) compressed to ~9 GB eliminates this cost for every future Wikipedia-derived experiment.
Tier hint: One-time H100 batch run (~1-2h compute). Index via faiss HNSW post-extraction. Storage ~9 GB compressed (zstd).
Why-now: Any Wikipedia-derived experiment in Phase 4 benefits immediately. Pays back within 5 cells.
Task: Build extraction script for mean-pooled layer-10 activations over all Wikipedia article introductions (or full articles, filtered to English). Validate on 10K articles (CPU smoke) before committing to full H100 run. Store as compressed npz + faiss index. Report: compression ratio achieved, lookup latency per query, sample retrieval quality on 100 known facts.

### Anchor 3 (HIGH PRIORITY -- 5-7 days, CPU/GPU mixed)
Pointer: Section B1 of research note (standardized substrate eval harness)
Substrate-product reading: Each new substrate variant currently requires 4-6h of manual scaffold: directory setup, import boilerplate, capability metrics, smoke-test wiring. A unified `python eval_substrate <variant>` harness auto-runs all registered capability benchmarks and produces a JSON report. This is the single largest structural lever on cell cycle time (3-5x smoke throughput).
Tier hint: Start with a 1-2 day prototype covering 3 capability dims (cheap decisive test: if under 20 min end-to-end for a known cell, the investment pays off in under 10 cells). Full harness in 5-7 days.
Why-now: Compounds over all remaining Phase 4 cells (~30-45 day roadmap). Earlier investment = more compound return.
Task: Design and implement SubstrateVariant interface (write, read, N, M parameters). Implement auto-runner over CCC-1-v2 capacity benchmark + 2 other capability dims. Validate on 2 existing cell variants. Report: scaffold time before vs after (minutes), harness extensibility assessment.

### Anchor 4 (MEDIUM PRIORITY -- 3-5 days + $10-30 cloud)
Pointer: Section A1 of research note (student distillation)
Substrate-product reading: Training a 50M-100M student model to mimic Llama-1B mid-layer geometry gives ~15-20x extraction speedup forever after (~$1.50 per 1M facts vs $30). This is a perpetual multiplier on every future extraction-based experiment.
Tier hint: Requires GPU training run ($10-30 cloud). Validate quality preservation on a held-out fact set before committing to full deployment (cosine-similarity >=75% criterion from research note).
Why-now: Recommended AFTER A2 (Wikipedia cache) validates the extraction pipeline is correct. Phase 4 week 2-3.
Task: Train student model mimicking Llama-1B layer-10 geometry. Use layer-mimicry distillation loss (cosine alignment + MSE on projected activations). Validate: cosine similarity between teacher and student representations on 1K held-out facts. Success criterion: >=75% mean cosine similarity (per research note HARD-PASS threshold).

---

## Context pointers

- Research note (full analysis, algebraic + citations): notes/research_drill_dev_speed_acceleration_phase4a_infrastructure_2x_2026-06-05.md
- Cap map (current capability state): notes/substrate_capability_map.md
- Post-compaction brief: notes/orchestrator_post_compaction_brief.md

---

## Contract

The research note has completed the algebraic analysis + literature scan for all 16 items across 4 categories. Exp_dev owns: anchor grid design, parameter sweep bounds, threshold formulas, queue assignment, smoke vs full designation, and timeout calculation per [[feedback-per-experiment-timeout-required]].

## Autonomy declaration

Exp_dev has full autonomy to: sequence the anchors above, adjust priority based on current queue state, combine anchors into a single batch run, add sub-anchors within each task, and determine CPU vs GPU routing per [[feedback-route-gpu-vs-cpu-by-torch-not-N]]. The research note provides the WHY; exp_dev owns the HOW.
