# exp_dev hand-off -- research: substrate vertical applications 5x drill

**Filed by:** research sub-agent (Sonnet 4.6), 2026-06-08
**Trigger:** notes/research_drill_substrate_verticals_5x_2026-06-08.md (vertical applications drill, 6 verticals characterized)
**Per [[feedback-no-experiment-design-in-prompts]]:** exp_dev designs anchors independently; this file provides pointers and rationale only.

---

## Pause state

Check data/orchestrator_paused.flag before dispatching. If paused, queue this handoff for next resume cycle. The anchor candidates below are ordered by urgency; candidates 1 and 2 are most time-sensitive given the v1 demo timeline.

---

## Anchor candidates (rank-ordered)

### 1. Healthcare DDI K-hop demo anchor

**Anchor pointer:** build a drug-drug interaction knowledge graph from FDA reference data (public, no legal barrier) and run the substrate K-hop traversal on it; measure recall vs FDA reference set of top-200 known DDIs.

**Substrate-product reading:** PP-187 (0% hallucination, deterministic lookup) is the empirical foundation. This anchor translates PP-187 from synthetic to real-domain. Pass = 0% missed critical interactions; Fail = any missed high-alert DDI. The algebraic audit trail (PP-184) should be surfaced in the demo output.

**Tier hint:** Tier 1 demo anchor -- directly unlocks the healthcare vertical pitch. No new mechanism required; this is a demo-building anchor, not a capability-discovery anchor.

**Why now:** Healthcare CDS is the strongest near-term commercial vertical (HIPAA compliance pull, Epic/Cerner integration demand). The demo mechanism is proven (PP-187). The only gap is a real DDI knowledge graph. This anchor closes that gap and produces the visceral demo scenario described in the research note.

**Pre-reg note:** pre-register against FDA adverse event benchmark; HARD-PASS = recall@200 >= 0.99 (0% missed critical interactions); HARD-FAIL = any high-alert DDI missed.

---

### 2. Legal citation snowball -- PACER corpus extension

**Anchor pointer:** extend PP-120 from controlled corpus to a PACER slice or a law firm-provided corpus; run the citation snowball at 1000+ seeds; measure recall vs known citation index.

**Substrate-product reading:** PP-120 (recall@1.000 on 4000 cases) is the strongest single empirical anchor across all verticals. This anchor tests whether the result generalizes to a real corpus with citation-formatting noise. Pass = recall >= 0.95 on PACER slice; Fail = recall < 0.90 (would require re-scoping the legal pitch).

**Tier hint:** Tier 1 demo anchor -- directly unlocks the legal vertical pitch. This is the highest-confidence commercial anchor in the handoff.

**Why now:** Legal is ranked #1 for v1.5/v2.0 focus. PP-120 is the demo. The PACER extension is the decisive empirical risk check. If it passes, the legal demo is ready. If it fails, need to understand the mechanism before building the demo.

**Pre-reg note:** HARD-PASS = recall >= 0.95 on >= 1000 seeds; HARD-FAIL = recall < 0.90 OR any algebraic certificate chain breaks on real corpus data.

---

### 3. Financial beneficial ownership synthetic graph anchor

**Anchor pointer:** build a synthetic 10K-entity beneficial ownership graph (FinCEN-style shell company structure, 5-7 hops deep) and run substrate K-hop traversal; measure chain recovery rate at depth 3, 4, 5.

**Substrate-product reading:** multi-hop +0.983 is the mechanism. This anchor tests depth scaling on a financial-domain graph structure (adversarially designed with deliberate obfuscation paths). Pass = 100% chain recovery at depth <= 5; Fail = any missed beneficial owner at depth <= 4.

**Tier hint:** Tier 2 demo anchor -- unlocks financial vertical pitch, but financial procurement cycle is 12-24 months so this is a 2025 prep anchor.

**Why now:** The synthetic graph can be built internally with no access barrier. This is the cheapest way to validate the financial pitch before pursuing Tier 1 bank conversations.

**Pre-reg note:** HARD-PASS = chain recovery >= 1.00 at depth <= 4; HARD-FAIL = any gap at depth <= 3.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_verticals_5x_2026-06-08.md
- PP-184 Merkle audit: substrate_capability_map.md rows PP-184
- PP-186 PII strip-inject: substrate_capability_map.md rows PP-186
- PP-187 deterministic lookup: substrate_capability_map.md rows PP-187
- PP-120 citation snowball: substrate_capability_map.md rows PP-120
- PP-185 dependency engine: substrate_capability_map.md rows PP-185
- COMPLIANCE SIDECAR GTM: substrate_capability_map.md v315 narrative block
- Orchestrator brief: d:/AI/hd-instrument/notes/orchestrator_post_compaction_brief.md

---

## Contract

exp_dev designs all anchor pre-regs, smoke gates, and dispatch decisions independently. This handoff provides strategic rationale and substrate-product readings; it does not specify implementation. No inline experiment design in this file per [[feedback-no-experiment-design-in-prompts]].

## Autonomy declaration

exp_dev has full autonomy to:
- Scope the DDI knowledge graph build (FDA reference data format, entity resolution approach)
- Choose the PACER corpus access path (public vs partner vs synthetic)
- Sequence anchors 1-3 against current queue state
- Defer any anchor if the queue is full or if a higher-priority capability anchor is pending

exp_dev does NOT need to consult orchestrator before dispatching these anchors; the research note and this handoff together constitute sufficient authorization.
