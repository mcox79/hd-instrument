# exp_dev hand-off -- research: substrate 1M+ scale pre-tests

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_1M_scale_risks_2x_2026-06-07.md
Date: 2026-06-07

Per [[feedback-no-experiment-design-in-prompts]]: this file names WHAT to test and the pass/fail criteria. Exp-dev decides implementation, batching, and code.

---

## Pause state block

Check data/orchestrator_paused.flag before acting. If paused, do not queue. File this as a pending handoff. These pre-tests are not time-critical -- they gate v1.1 engineering authorization, which can wait 1-2 cycles.

---

## Context

CELL-4 validated Pattern B recall@1 = 1.0 at M=100K facts (cycle 152). The production v1.1 target is the Wikipedia pre-trained substrate at 5.84M articles (CELL-2 v3 artifact already extracted). The iterative multi-hop drill (2x) identified a hard gap: no empirical validation above 100K, and a hard-infeasible Gram matrix at 1M without algorithm change.

The Gram matrix issue has a clean fix (SMW rank-1 updates, WoodburyLS arxiv 2406.15120). Three pre-tests gate v1.1 authorization, ordered by cost and criticality.

---

## Anchor candidates (rank-ordered)

### 1. Pre-test A: SMW timing at M=1M (tier: CPU smoke, 30 min)

- Anchor pointer: pinv_smw_timing_1M
- Substrate-product reading: Implement Sherman-Morrison-Woodbury rank-1 update for the pseudoinverse. Time M=1M sequential insertions on runner CPU. Report per-update mean and P95 wall time. No GPU needed.
- Tier hint: CPU smoke (fastest, cheapest, gates everything else)
- Why-now: SMW is the gating engineering action for v1.1. If CPU timing fails (> 20 ms/update), streaming write is infeasible and GPU-only path must be decided before any GPU pre-test. Run this FIRST.
- HARD-PASS: mean update time < 5 ms on CPU (1M updates = < 84 min; streaming at 1 fact/sec handled)
- MIDDLE-BAND: 5-20 ms (batch OK; streaming marginal; GPU path recommended)
- HARD-FAIL: > 20 ms (batch ingest > 5 hours; streaming infeasible; GPU-only or algorithm redesign required before v1.1)

### 2. Pre-test B: Pattern B recall at M=500K synthetic facts (tier: GPU smoke, 2-4 hr)

- Anchor pointer: patternb_recall_500k_smoke
- Substrate-product reading: Build a Pattern B substrate with M=500K synthetic triplet facts on local GPU. Measure recall@1, recall@5, and bridge entity coverage on a test set of 1K queries. Compare directly to the M=100K CELL-4 baseline. Report SNR proxy (mean retrieval dot product / std of cross-binding noise sample).
- Tier hint: GPU smoke (local runner; 2-4 hr wall time)
- Why-now: 10x extrapolation from CELL-4. No published empirical data above ~50K in the Hopfield literature. This is the highest-uncertainty empirical claim in the 1M path. Validates (or refutes) the theoretical basin-separation argument before committing to Wikipedia engineering.
- HARD-PASS: recall@1 >= 0.85, recall@5 >= 0.95, bridge coverage >= 75%
- MIDDLE-BAND: recall@1 0.70-0.85, recall@5 0.85-0.95 (addressable with query re-ranking)
- HARD-FAIL: recall@1 < 0.70 OR recall@5 < 0.80 OR bridge coverage < 60% (Hopfield basin shrinkage or binding collision worse than theory; architectural mitigation required before Wikipedia build)

### 3. Pre-test C: Wikipedia 100K article smoke (tier: GPU, 4-8 hr)

- Anchor pointer: wikipedia_100k_substrate_smoke
- Substrate-product reading: Use CELL-2 v3 artifact (5.84M articles extracted; already on runner). Sample 100K articles. Convert to Pattern B format (triplet extraction from Wikipedia text). Build substrate. Measure recall@5 and bridge coverage on a 500-question Wikipedia factual QA test set. CRITICALLY: include a test sub-set specifically targeting the top-50 most-frequent Wikipedia entities (power-law bridge collision test).
- Tier hint: GPU (local runner preferred; cloud if local GPU VRAM < 8 GB for 100K)
- Why-now: This is the GO/NO-GO for v1.1 Wikipedia substrate. If this passes, full 5.84M engineering is authorized. If it fails, entity-type sharding (Option E from research note) must be implemented first. The power-law entity test is the discriminating measurement -- generic random-fact tests will not catch the failure mode.
- HARD-PASS: recall@5 >= 0.80 on general QA; top-50 entity precision >= 0.75; latency < 100 ms
- MIDDLE-BAND: recall@5 0.65-0.80; top-50 entity precision 0.60-0.75 (re-ranking mitigation viable)
- HARD-FAIL: recall@5 < 0.65 OR top-50 entity precision < 0.60 after re-ranking (power-law collision confirmed; entity-type sharding required; v1.1 Wikipedia substrate blocked without architectural change)

---

## Context pointers (files, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_1M_scale_risks_2x_2026-06-07.md
- CELL-4 baseline: check data/exp_patternb_recall_100k/metrics.json for recall@1 = 1.0 reference
- CELL-2 v3 artifact: runner data/cell2_results/ (5.84M Wikipedia articles extracted)
- Pattern B mechanism reference: cap_map rows covering Pattern B L2 normalization (cycle 166 HP)
- SMW formula reference: arxiv 2406.15120 (WoodburyLS 2024)

---

## Contract section

The three pre-tests run in order: A first (gates B and C), B second (gates C), C third (gates full Wikipedia build). If A HARD-FAILs, do not run B or C -- report the timing result to orchestrator for algorithm-change decision. If B HARD-FAILs, do not run C -- report to orchestrator; entity-type sharding is the recommended mitigation. If C HARD-FAILs on power-law entity test specifically (top-50 entity precision < 0.60), the full 5.84M Wikipedia build is blocked pending sharding implementation.

Do not design the SMW implementation in this file. Exp-dev owns the implementation.

---

## Autonomy declaration

Exp-dev may batch Pre-tests A and B together if local GPU is available (A is CPU-only, B is GPU -- they can run in parallel). Pre-test C requires Pre-test B to pass first. Exp-dev decides whether to run C on local GPU or remote GPU based on VRAM availability for 100K Pattern B build.

Priority relative to existing queue: these are v1.1 gating pre-tests. They should be queued at high priority but after any currently-running experiments complete. They are not emergency interrupts.
