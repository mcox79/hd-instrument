# exp_dev hand-off -- research: biological distributed coordination (2x drill)

## Header

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_biological_distributed_coordination_2x_2026-06-07.md

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs all anchors autonomously from the pointers below. No inline experiment design is provided here.

---

## Pause state block

Experiments are PAUSE-GATED. Check data/orchestrator_paused.flag before dispatching. If paused, queue anchor candidates for next resume cycle.

---

## Anchor candidates (rank-ordered)

### 1. CORROBORATE-GATE-SMOKE (tier: CPU-smoke, ~2 min laptop)
Anchor pointer: immune corroboration gossip mechanism (Deep Dive C in research note)
Substrate-product reading: Does adding a counter-propagating DAMP signal to gossip-style shard coordination suppress adversarial-shard content vs naive broadcast? The novel element vs existing gossip literature is the anti-inflammatory counter-signal.
Tier hint: Laptop CPU smoke. N=16 shards, 5 adversarial, 100 queries, 3 gossip rounds.
Why now: Cheapest test to validate the key novel mechanism. 2-minute run. Cheap decisive test in the research note.
Pre-reg bands from note: HARD-PASS adversarial content <10% AND accuracy within 3 pp. HARD-FAIL adversarial content >20% OR accuracy drop >5 pp.

### 2. PHEROMONE-DECAY-WEIGHT (tier: CPU-smoke, ~5 min laptop)
Anchor pointer: temporal-decay weight on shard contributions (Deep Dive A in research note)
Substrate-product reading: Does exponentially-decayed confidence weight outperform static confidence weight on a workload where query-relevant shards shift over time? Extension of existing K-hop bundling.
Tier hint: Laptop CPU smoke. N=32 shards, shifting-relevance workload (relevance of each shard changes every 500 queries), 2000 total queries.
Why now: Low engineering cost, extends existing architecture, clear pre-reg bands.
Pre-reg bands: HARD-PASS >5 pp retrieval quality improvement. HARD-FAIL <1 pp difference.

### 3. QUERY-PATH-CACHE (tier: CPU-remote, ~30 min)
Anchor pointer: slime-mold path reinforcement -> query-path caching (Part 1 item 4 in research note)
Substrate-product reading: Does prefix-match caching of frequently-traversed cross-shard query sequences reduce mean latency on a repeat-pattern workload?
Tier hint: Remote CPU. N=64 shards, 10k queries, 30% repeat-prefix workload.
Why now: Moderate cost, strong P_deflated (0.40), clear engineering path.
Pre-reg bands: HARD-PASS >30% latency reduction. HARD-FAIL <5% improvement.

### 4. COOCCURRENCE-DEFRAG (tier: CPU-remote, ~2 hours; requires logging infra)
Anchor pointer: hippocampal replay -> background defragmentation (Deep Dive B in research note)
Substrate-product reading: Does background migration of frequently-co-accessed facts onto shared shards reduce cross-shard query rate?
Tier hint: Remote CPU with logging infrastructure as prerequisite. N=128 shards, 100k queries, co-occurrence matrix construction + migration run.
Why now: Highest novelty, addresses root cause of cross-shard load. Prerequisites: query-access-pattern logging must be built first. Sequence after CORROBORATE-GATE-SMOKE validates the corroboration mechanism.
Pre-reg bands: HARD-PASS cross-shard query rate falls >20%. HARD-FAIL rate unchanged or increases.

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_biological_distributed_coordination_2x_2026-06-07.md
Prior biological drill (storage side): d:/AI/hd-instrument/notes/research_drill_biological_precedents_animal_scales_substrate_2x_2026-06-04.md
Template for v195 pipeline: d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md

Relevant lit (from research note citations):
- arxiv 2512.03285 (gossip substrate for agentic AI -- near-direct engineering precedent for CORROBORATE-GATE)
- arxiv 2508.01531 (gossip protocols for emergent coordination)
- PMC4792674 (hippocampal computation -- Deep Dive B background)

---

## Contract section

exp_dev owns all anchor design decisions. The research note provides mechanism descriptions and pre-reg bands; exp_dev translates these to concrete script + queue_add.sh calls per its standard protocol.

Sequencing suggestion (not binding): CORROBORATE-GATE-SMOKE first (cheapest, highest novelty). If HARD-PASS: proceed to PHEROMONE-DECAY-WEIGHT and QUERY-PATH-CACHE. COOCCURRENCE-DEFRAG requires logging infrastructure as prerequisite -- flag to orchestrator if not yet built.

## Autonomy declaration

exp_dev is autonomous for all anchor design, script writing, pre-flight checks, and dispatch decisions. This file is a pointer set, not a prescription. exp_dev should override sequencing suggestions if resource constraints or queue state require it.
