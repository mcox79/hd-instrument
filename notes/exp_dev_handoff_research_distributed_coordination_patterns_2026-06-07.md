# exp_dev hand-off -- research: distributed coordination patterns

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_distributed_coordination_patterns_3x_2026-06-07.md

## Pause state block

This hand-off was written while experiments may be paused. Check data/orchestrator_paused.flag
before dispatching. If paused: queue the anchor candidates below for next resume cycle.

Per [[feedback-no-experiment-design-in-prompts]]: no experiment design is encoded here.
exp_dev reads the research note and designs the experiment from the findings independently.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP PRIORITY): Confidence-weighted bundling smoke

- Anchor pointer: Pattern 1 from research note -- soft-Krum confidence-weighted bundle sum.
- Substrate-product reading: confidence-weighted aggregation addresses the wrong-answer
  corruption identified in the K-hop noise drill. ~50 LOC change; directly testable on
  existing shard test harness.
- Tier hint: Tier 1 / v1 scope. Low engineering overhead. Cheap decisive test is enumerated
  in research note (100-shard harness, 1000 queries, 5 min wall).
- Why now: this is the 50-LOC fix from the K-hop drill, now confirmed by federated learning
  lit (FedAvg / Krum / geometric median). Cross-shard K-hop is the identified biggest gap
  from Phase 2 GOLD findings. Pattern 1 is the lowest-overhead first intervention.

### Anchor 2: CRDT quorum bundle formalization

- Anchor pointer: Pattern 4 from research note -- G-Vector + OR-Set + G-Counter CRDT bundle.
- Substrate-product reading: makes the bundle operation provably idempotent and convergent
  (Strong Eventual Consistency). Theoretical guarantee useful for enterprise customers.
- Tier hint: Tier 2 / v1-v2 scope. ~1 week engineering. No new infrastructure.
- Why now: CRDT theory is solid (ACM Computing Surveys 2024 confirmed). The OR-Set shard-ID
  tracking is a prerequisite for Pattern 2 (hierarchical routing) anyway.

### Anchor 3: Hierarchical routing B_eff measurement

- Anchor pointer: Pattern 2 from research note -- sqrt(S) sub-cluster fanout reduction.
- Substrate-product reading: at 10K shards, hierarchical routing reduces effective wrong-answer
  exposure from 10,000 to ~100. This is the v2 enabling architecture.
- Tier hint: Tier 2 / v2 scope. 2-3 weeks engineering. Medium overhead.
- Why now: Phase 2 GOLD findings identified cross-shard K-hop as biggest architectural gap.
  Pattern 2 is the structural fix. Empirical B_eff measurement can be done on a simulated
  1K-shard harness as a planning experiment before full implementation.

---

## Context pointers (file paths, not summaries)

- Primary research note: d:/AI/hd-instrument/notes/research_drill_distributed_coordination_patterns_3x_2026-06-07.md
- K-hop noise research (most recent, referenced): d:/AI/hd-instrument/notes/research_drill_khop_noise_model_selection_2x_2026-06-07.md
- Phase 2 GOLD findings: d:/AI/hd-instrument/notes/phase2_5x_chains_gold_findings_2026-06-07.md
- Post-compaction brief (for full substrate state): d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md

---

## Contract section

- exp_dev reads the research note, not this hand-off, for technical content.
- exp_dev designs experiments independently based on the anchor descriptions above.
- exp_dev does NOT encode experiment parameters from this hand-off file.
- Anchor 1 is the highest priority; dispatch it first on next exp_dev cycle.

## Autonomy declaration

exp_dev is fully autonomous on experiment design for all three anchors above. The research note
provides the theoretical framework; exp_dev translates to concrete experiment spec independently.
Orchestrator approves queue dispatch as usual (pause-gated).
