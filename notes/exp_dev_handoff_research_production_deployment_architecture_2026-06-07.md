# exp_dev hand-off -- research: production deployment architecture

Filed-by: research sub-agent (2026-06-07)
Trigger: notes/research_drill_production_deployment_architecture_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered by production-deployment criticality)

### 1. Cell P1 -- Shard-split correctness under capacity overflow (HIGHEST PRIORITY)
Anchor pointer: SHARD-SPLIT-P1 (new; not yet queued)
Substrate-product reading: validates the core architectural mitigation for d_eff=91.6 ceiling at cap=122; if shard-split fails, the entire sharding strategy must be redesigned before any production deployment
Tier hint: CPU; <1h wall; small N (N=4096 or smaller)
Why-now: blocks production deployment -- d_eff ceiling is the single most load-bearing constraint; no other mitigation path exists; must pass before any multi-shard deployment

### 2. Cell P4 -- Cross-compound integration at real encoder scale (HIGH PRIORITY)
Anchor pointer: COMPOUND-INTEGRATION-P4 (new; not yet queued)
Substrate-product reading: validates that all 6 production capabilities can coexist on the same shard without interference; if any mechanism degrades >30%, compound stacking is unsafe and must be serialized (major API design change)
Tier hint: GPU preferred (BGE-large encoder + all 6 mechanisms); ~1-2h wall
Why-now: 6 capabilities are individually validated but cross-compound at real-encoder scale is untested; this is the last compound-level gate before production

### 3. Cell P5 -- HNSW ef_search calibration curve (HIGH PRIORITY)
Anchor pointer: HNSW-EFCAL-P5 (new; not yet queued)
Substrate-product reading: empirically confirmed HNSW recall@1=0 at default ef_search; production must pin ef_search >= 200; this cell produces the calibration curve and validates the FAISS configuration
Tier hint: CPU; <30 min wall; small dataset
Why-now: HNSW misconfiguration is a certain production failure (P_break=1.0 at default params); cheap to validate now

### 4. Cell P2 -- Concurrent write corruption stress test (MEDIUM PRIORITY)
Anchor pointer: WRITE-MUTEX-P2 (new; not yet queued)
Substrate-product reading: validates shard-level mutex reduces multi-head flip rate to <1%; if mutex fails, concurrent write handling must be redesigned
Tier hint: CPU; <1h wall; moderate N
Why-now: multi-head corruption >20% (cycle 137) is a known failure mode; production write path requires validated mutex

### 5. Cell P3 -- Encoder version drift simulation (MEDIUM PRIORITY)
Anchor pointer: ENCODER-DRIFT-P3 (new; not yet queued)
Substrate-product reading: quantifies how sensitive substrate recall is to encoder drift; pins the monitoring threshold for production drift alerts
Tier hint: CPU; <30 min wall; small dataset + noise sweep
Why-now: encoder drift has no production test; monitoring threshold is ungrounded without this data

---

## Context Pointers

Research note (primary): d:/AI/hd-instrument/notes/research_drill_production_deployment_architecture_2026-06-07.md
Prior deployment roadmap: d:/AI/hd-instrument/notes/research_drill_phase4_v1_production_deployment_roadmap_2026-06-06.md
Prior roadmap handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_phase4_v1_production_deployment_roadmap_2026-06-06.md
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Prior handoffs: scan notes/exp_dev_handoff_*.md sorted by mtime for conflicting dispatches

---

## Contract

exp_dev designs anchor names, sweep grids, pre-reg thresholds, timeout formulas, and queue assignments.
exp_dev does NOT re-derive the production architecture (it is fully specified in the research note above).
exp_dev verifies queue presence post-ship per [[feedback-ship-name-collision]] discipline.
exp_dev confirms no redundant dispatch if anchor is already in flight (check queue.json before ship).
exp_dev does NOT batch Cell P1 with Cell P4 -- they should run sequentially as P1 is a prerequisite gate.

## Autonomy Declaration

exp_dev has full autonomy over: anchor naming, N/seed/layer sweep parameters, timeout calculation, queue choice (GPU vs CPU vs remote), pre-reg HP/MID/HF numerical thresholds, and decision to batch vs serialize. The priority ordering above is a recommendation based on production criticality; exp_dev may reorder if queue state or runner availability argues for it. Cell P5 (HNSW calibration) can run in parallel with any other cell as it is independent.
