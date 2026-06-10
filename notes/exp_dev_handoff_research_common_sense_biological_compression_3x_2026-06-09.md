# exp_dev hand-off -- research: common-sense biological compression (3x)

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: Research drill on biological compression mechanisms for common-sense knowledge
Research note path: d:/AI/hd-instrument/notes/research_drill_common_sense_biological_compression_3x_2026-06-09.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and context pointers only. exp_dev designs the actual experiment cells.

---

## Pause state block

Experiments are currently authorized per normal queue protocols. These anchors are additive to the existing queue; exp_dev should check current queue depth before scheduling.

---

## Anchor candidates (rank-ordered)

### 1. SCHEMA-LAYER (Tier: smoke / CPU)
Anchor pointer: research note Section 6, Anchor 1
Substrate-product reading: cluster ConceptNet entities by IsA category; compute HD centroid (schema prototype); store instances as (schema_key, delta_binding) pairs; verify that (centroid + delta) retrieval achieves >80% fact recall on held-out category members.
Tier hint: CPU smoke, <2 hours wall time, no GPU needed.
Why now: cheapest test of the highest-value compression mechanism. If this passes, schema-layer implementation is authorized. If it fails (recall <60%), the biological schema-compression argument does not apply to ConceptNet's structure and the whole approach is refuted early.

### 2. HIERARCHICAL INHERITANCE INDEX (Tier: CPU preprocessing)
Anchor pointer: research note Section 6, Anchor 3
Substrate-product reading: precompute IsA chains over ConceptNet; count what fraction of entity-property facts are entailed by (IsA + category-level property) inference at precision >90%. If >20% of facts are entailed, implement inheritance-at-query-time routing.
Tier hint: CPU preprocessing pass on 458K facts, <30 minutes wall time.
Why now: lowest-cost, highest-precision first gate. If ConceptNet hierarchy is too sparse for inheritance to cover >10% of facts, this approach is abandoned without further cost.

### 3. DUAL-PROCESS ROUTING COVERAGE TEST (Tier: CPU + 1 LLM batch)
Anchor pointer: research note Section 6, Anchor 4
Substrate-product reading: sample 500 questions from CommonsenseQA benchmark; route to substrate first; measure hit rate (substrate returns non-empty, relevant answer); measure hybrid (substrate + LLM fallback) accuracy vs LLM-only. Gate: substrate hit rate >50% to justify the dual-process architecture for v1 demo.
Tier hint: CPU for substrate eval + 1 LLM API batch (500 calls); moderate cost.
Why now: most direct test of whether the scale gap matters for the product. If substrate hit rate is only 20%, the gap is structurally critical and higher-priority remediation is needed. If >50%, the hybrid architecture closes the gap adequately for v1 demo.

### 4. PREDICTIVE CODING FACT COMPRESSION (Tier: CPU analysis)
Anchor pointer: research note Section 6, Anchor 5
Substrate-product reading: for 5 ConceptNet categories (animal, vehicle, food, person, building), compute expected property distribution (prototype); measure what fraction of per-entity properties are predictable from category distribution at >90% accuracy. If >60% are predictable, predictive-coding-style storage (store only surprises) cuts explicit store by 30-60% for those categories.
Tier hint: CPU analysis, <1 hour.
Why now: if the fraction is high, this justifies a fact-store refactor before the 1M-fact scale-up. Better to implement now than post-scale-up.

### 5. EPISODIC-TO-SEMANTIC EXTENSION OF PP-141/142 (Tier: CPU, medium cost)
Anchor pointer: research note Section 6, Anchor 2
Substrate-product reading: after sleep-defrag cycle, run cosine-similarity clustering (threshold 0.85) over fact store HD vectors; extract cluster centroids as new semantic nodes; measure storage reduction from centroid substitution. Gate: >10% storage reduction to justify integration into PP-141/142 pipeline.
Tier hint: CPU, <2 hours on 458K facts.
Why now: natural extension of existing PP-141/142 infrastructure. If clustering yields clean centroids, the episodic-to-semantic pipeline is ready for production integration.

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_common_sense_biological_compression_3x_2026-06-09.md
- PP-141/142 implementation: search d:/AI/hd-instrument for PP-141, PP-142 anchor files
- ConceptNet fact store: check d:/AI/hd-instrument/data/ for ConceptNet extraction outputs
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md (if exists)
- Post-compaction brief (context): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md

---

## Contract section

exp_dev owns all experiment cell design, pre-registration, dispatch, and verdict filing. This handoff provides the anchor direction and tier hints only. Do not use the biological mechanism descriptions above as experiment prompts -- those are internal design rationale. Prompt bodies must use generic mathematical terminology per [[feedback-drill-prompt-bodies-must-be-generic]].

All anchors above are CPU-only or single LLM batch; no GPU authorization needed. Run cheapest gates first (Anchor 2 = 30 min, Anchor 1 = 1 hour, Anchor 5 = 2 hours, Anchor 4 = 1 hour + LLM batch, Anchor 3 = 2 hours).

## Autonomy declaration

exp_dev is fully autonomous on: cell design, pre-reg parameters, dispatch order, smoke gate decisions, verdict filing, cap_map annotation for PASS/FAIL results.

exp_dev escalates to orchestrator on: results that fundamentally change product architecture (e.g., HARD-FAIL on Anchor 3 dual-process means scale gap is critical, requires strategy discussion).
