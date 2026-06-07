# exp_dev hand-off -- research: temporal fact versioning

Filed-by: research sub-agent
Trigger: notes/research_drill_temporal_fact_versioning_2x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered)

### 1. temporal_hash_chain_audit_correctness_v1
- Substrate-product reading: confirms that per-fact hash-chained version history composes correctly with the existing Merkle audit chain; closes the cryptographic audit correctness question before any temporal versioning feature is shipped to production
- Tier hint: laptop CPU smoke; <5 min wall; Tier-1 (correctness gate -- blocks all temporal versioning production work)
- Why now: Pattern D (hash-chained versioning) is the minimum viable temporal extension of the existing HP-12 V1 Merkle chain; correctness must be verified before any capacity or latency cells run

### 2. temporal_filter_latency_overhead_v1
- Substrate-product reading: measures whether validity-interval filtering at retrieval time adds acceptable latency overhead; if HARD PASS, Pattern A (append-only with validity intervals) is production viable without a dedicated time-index; if HARD FAIL, forces Pattern E (two-substrate split) architecture
- Tier hint: laptop CPU; <10 min wall; Tier-2 (architecture decision gate)
- Why now: latency overhead determines which temporal architecture the production system adopts; this is a cheap decisive test that de-risks the 5-6 week engineering investment

### 3. temporal_wikipedia_ceo_retrieval_accuracy_v1
- Substrate-product reading: end-to-end demonstration of temporal substrate on real-world CEO change data from Wikipedia revision history; if HARD PASS (>=95% accuracy over ~200 queries), provides a product-legible demo for healthcare/legal/financial market positioning
- Tier hint: laptop CPU; ~30 min wall including Wikipedia API scraping; Tier-3 (product demo + market validation)
- Why now: this is the most stakeholder-legible cell; connects the substrate capability directly to the Blue Ocean market thesis; run after cells 1+2 confirm implementation correctness

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_temporal_fact_versioning_2x_2026-06-07.md
- Production architecture reference: Merkle/HP-12 V1 at cycle 143; pseudoinverse write rule at cycle 143; sharding 5x at cycle 142
- Competitive landscape: XTDB (bitemporal, no semantic), Datomic (temporal, no semantic), LiveVectorLake arxiv 2601.05270 (dual-tier, no audit chain)
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check verified-memory rows; temporal versioning opens a new capability axis)

---

## Contract

exp_dev owns: anchor design, sweep grids, threshold formulas, queue routing, pre-reg bands, self-test verification.
research handed off: anchor names, WHY, tier hints, context pointers.
exp_dev does NOT inherit specific numerical thresholds from this file as binding contracts -- it pre-registers its own per [[feedback-envelope-expansion-fail-bands]].

## Autonomy Declaration

exp_dev has full autonomy over anchor implementation, smoke-gate design, and queue placement. The three anchors above are suggestions ordered by strategic priority; exp_dev may reorder, split, or combine based on current queue state and runner availability.
