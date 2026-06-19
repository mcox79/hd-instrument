# exp_dev hand-off -- research: continual learning forgetting profile

Filed-by: research sub-agent
Trigger: notes/research_drill_continual_learning_forgetting_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered, cheapest decisive first)

### 1. long_sequence_ingest_probe_v1 (TIER 1 -- ~10 min CPU, highest priority)
- Substrate-product reading: measures the actual forgetting curve (retrieval cosine vs M) for items stored early in a shard, at N=16384. If HARD-PASS (item at position 1 maintains cosine > 0.70 up to M = 0.8 * M_c), confirms smooth degradation and validates "avoids catastrophic forgetting" claim with empirical grounding. If HARD-FAIL (cliff before M=500), the production shard sizing assumptions are wrong and need immediate revision.
- Tier hint: CPU smoke; ~10 min wall; DIAGNOSTIC prerequisite for all other forgetting anchors; numpy-only
- Why now: cheapest possible test; closes the largest open uncertainty (whether degradation is smooth or cliff-like); required before making any customer-facing "graceful forgetting" claim

### 2. schema_mediated_consolidation_v1 (TIER 1 -- ~20 min CPU)
- Substrate-product reading: tests whether schema structure (common components across semantically similar stored facts) is preserved better than individual item detail as M grows. If HARD-PASS (schema centroid cosine > 0.80 while individual fact cosine degrades), this is the VSA-predicted schema-preservation property and supports the "biologically-inspired knowledge distillation" claim. If HARD-FAIL (schema and individual degrade equally), the near-orthogonality assumption is violated for real encoder outputs and shard partitioning strategy needs revision.
- Tier hint: CPU; ~20 min wall; Tier-1 (closes schema-retention claim; prerequisite for sleep-defrag narrative)
- Why now: second cheapest test; directly disambiguates whether substrate schema preservation is real or just theoretical; needed before any sleep-defrag product claim

### 3. selectivity_profile_v1 (TIER 1 -- ~15 min CPU)
- Substrate-product reading: tests whether repeatedly-written facts are preferentially retained over single-write facts at M near capacity. Expected outcome: HARD-FAIL (current system has no reinforcement writes on access; retrieval is non-destructive). This is a USEFUL diagnostic HARD-FAIL -- it identifies a concrete engineering gap (need to add access-gated reinforcement writes for frequency selectivity). If unexpectedly HARD-PASS, that would indicate constructive interference is doing implicit reinforcement, which is a significant finding.
- Tier hint: CPU; ~15 min wall; Tier-1 (expected diagnostic FAIL that quantifies gap vs biology/competitors)
- Why now: identifies whether frequency-selectivity is a 0-cost substrate property or a 2-week engineering task; informs product roadmap

### 4. interference_profile_correlated_v1 (TIER 2 -- ~15 min CPU)
- Substrate-product reading: tests whether semantically similar facts (high cosine overlap in encoder space) degrade faster than semantically dissimilar facts within the same shard. If HARD-PASS (similar items degrade 2x faster than dissimilar), confirms that within-domain clustering requires smaller shards (lower M_c_effective for correlated inputs). This is critical for production shard sizing of high-density predicates like is-a and has-property.
- Tier hint: CPU; ~15 min wall; Tier-2 (depends on long_sequence_ingest_probe confirming baseline behavior first)
- Why now: WikiData/ConceptNet ingest has many semantically correlated facts per predicate; understanding the real M_c_effective (vs the random-vector theoretical bound) determines whether current N=16384 is sufficient or N upscaling is needed

### 5. sleep_defrag_at_scale_v1 (TIER 2 -- ~30 min CPU)
- Substrate-product reading: runs PP-141/142 sleep-defrag consolidation pass at M = 0.7 * M_c and M = 0.9 * M_c; measures whether retrieval accuracy improves post-defrag and whether the improvement is durable after 1K subsequent writes. If HARD-PASS (> 5% improvement, durable), PP-141/142 is confirmed as a production-scale optimization and can be included in customer-facing claims. If HARD-FAIL (no improvement or improvement collapses within 100 writes), sleep-defrag is a research-demo mechanism only and should be removed from product narrative until redesigned.
- Tier hint: CPU; ~30 min wall; Tier-2 (depends on schema_mediated_consolidation confirming schema structure first; sleep-defrag's value is conditional on schema being preserved)
- Why now: PP-141/142 is currently claimed in internal documentation; production-scale validation is required before any customer demo includes this as a feature

---

## Honest gap notes (for orchestrator context)

Research finding establishes:
- "Avoids catastrophic forgetting" is defensible in the ML-CF (McCloskey-Cohen) sense; P_deflated=0.90
- Smooth degradation curve is predicted but unconfirmed at production scale; P_deflated=0.50
- Schema preservation is theoretically predicted; P_deflated=0.40; depends on near-orthogonality assumption holding for real encoder outputs
- Frequency selectivity is NOT present in current architecture (reads are non-destructive); this is a known gap vs biology
- Full biological CL (two-system CLS) is not implemented; substrate is hippocampus-only; P_deflated=0.10 for full biological equivalence claim

Primary production risk: capacity exhaustion (M > M_c per shard) for high-density predicates such as is-a, has-property. Recommend adding a shard-load diagnostic (count facts per predicate, flag shards where M > 0.5 * M_c) before any production deployment claim. This is NOT an experiment anchor -- it is a 1-hour diagnostic engineering task.

Expected outcomes:
- long_sequence_ingest_probe: likely PASS (smooth degradation is the VSA prediction; chance of cliff is low if per-predicate sharding is functioning correctly)
- schema_mediated_consolidation: uncertain (P=0.35; depends on real encoder output correlation structure)
- selectivity_profile: likely FAIL (no reinforcement writes in current system; useful diagnostic)
- interference_profile_correlated: uncertain (P=0.45; determines whether N=16384 is sufficient for correlated inputs)
- sleep_defrag_at_scale: uncertain (P=0.35; PP-141/142 has not been tested at M near capacity)

Do NOT dispatch sleep_defrag_at_scale until schema_mediated_consolidation has confirmed that schema structure is preserved at M near capacity. Sleep-defrag's benefit is conditional on schema being there to consolidate.

---

## Context Pointers

- Research note: notes/research_drill_continual_learning_forgetting_2x_2026-06-10.md
- Prior replay drill: notes/research_drill_rem_replay_consolidation_substrate_2x_2026-06-04.md
- Prior sleep-defrag drill: notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md
- Capacity theory: Amit, Gutfreund & Sompolinsky 1985 (M_c = 0.138 * N; cited in research note)
- PP-141/142 implementation: search hdlab/ for sleep-defrag or consolidation keyword
- Wright-Fisher baseline: notes/research_drill_wright_fisher_kimura_substrate_population_genetics_2x_2026-06-04.md

---

## Contract

exp_dev's job: design anchors, set pre-reg thresholds, ship to queue, verify post-ship.
Orchestrator's job: decide which anchors to activate and when.
This file is a ranked option list -- not a dispatch order.

## Autonomy Declaration

exp_dev owns: anchor naming, sweep grid design, threshold formula self-test, queue selection, ETA estimation, smoke vs full run decision.
exp_dev does NOT own: cap_map write decisions, strategy pivots, or composition ordering between these anchors.
