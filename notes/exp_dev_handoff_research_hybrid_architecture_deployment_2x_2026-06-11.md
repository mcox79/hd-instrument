# exp_dev hand-off -- research: hybrid_architecture_deployment_2x

**Filed-by:** research sub-agent
**Date:** 2026-06-11
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_hybrid_architecture_deployment_2x_2026-06-11.md

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the exact implementation. This file gives
the anchor candidates, context pointers, and decision logic. No code or cell designs inline.

---

## Pause state

Not paused. Normal dispatch rules apply. CPU-local preferred for routing-threshold tests (no GPU needed).

---

## Anchor candidates (rank-ordered)

### 1. CASCADE-ROUTING-THRESHOLD (Pattern 4 gate test) -- HIGHEST PRIORITY
**Pointer:** Research Section 7 Test A
**Substrate-product reading:** Quantify what fraction of queries substrate handles at high confidence; this
is the cost-savings number for the Pattern 4 commercial case. If >40% of queries route substrate-only,
the LLM API cost argument is real and quantifiable.
**Why now:** Pattern 2 is production-ready today; Pattern 4 is the 3-6 month target. This test sets the
routing threshold and answers "how much does Pattern 4 save vs Pattern 2?" The answer is a business number.
**Tier hint:** Tier A (routing calibration is a commercial readiness test, not a capability discovery)
**Gate pre-reg:**
- HARD-PASS: Spearman r(substrate_confidence, retrieval_accuracy) >= 0.60 AND >40% queries route
  substrate-only at confidence > 0.85
- HARD-FAIL: Spearman r < 0.40 OR substrate-only fraction < 20%
**Note:** Use a real domain query set (not synthetic). Legal or financial text preferred. Substrate KB from
existing PP-225 production KB (fb15k-237 or a domain-specific loaded KB).

---

### 2. SUBSTRATE-AS-FAITHFULNESS-JUDGE (Pattern 4 cascade verify) -- HIGH PRIORITY
**Pointer:** Research Section 7 Test C + PP-228
**Substrate-product reading:** If substrate audit trail can serve as a faithfulness judge (F1 > 0.70),
the production stack simplifies from "LLM + vector DB + faithfulness judge" to "LLM + substrate." Eliminates
one paid inference component. This is a direct cost reduction.
**Why now:** Faithfulness judges are the 2026 production standard for RAG quality control. Substrate PP-228
categorical audit is already built; this test checks whether it generalizes to semantic faithfulness.
**Tier hint:** Tier B (novel application of an existing capability to a new role)
**Gate pre-reg:**
- HARD-PASS: F1 > 0.70 on 100 LLM-generated answers vs substrate KB facts
- HARD-FAIL: F1 < 0.40
**Note:** CPU-local. Does not require LLM inference if LLM answers are pre-generated. Pre-generate 100
answers with any available LLM baseline and pass to substrate audit path.

---

### 3. PATTERN1-DOMAIN-SPECIFIC-POS (structured-domain parse) -- MEDIUM PRIORITY
**Pointer:** Research Section 7 Test B
**Substrate-product reading:** If POS accuracy on structured domains (finance/legal/code) is >= 0.92,
Pattern 1 (substrate-front) becomes viable for those domains TODAY. This unlocks the sub-ms parsing
claim for enterprise structured-domain deployments.
**Why now:** The 0.906 general POS result is the lower bound. Domain-specific accuracy is likely higher
(closed vocabulary, less polysemy). Confirming 0.92+ on finance domain extends Pattern 1 viability.
**Tier hint:** Tier B (extension of existing capability to production domain)
**Gate pre-reg:**
- HARD-PASS: Finance/legal domain POS accuracy >= 0.92 on Penn Treebank WSJ finance section
- HARD-FAIL: Domain POS accuracy < 0.85 (worse than or equal to general domain)
**Note:** CPU-local. Penn Treebank WSJ finance is a subset of the standard dataset. Sub-4-hour run.

---

### 4. MCP-ENDPOINT-SUBSTRATE (Pattern 2 production integration) -- MEDIUM PRIORITY
**Pointer:** Research Section 6 (MCP compatibility)
**Substrate-product reading:** Substrate exposing a MCP endpoint makes it compatible with every 2026
LLM agent framework without custom integration. This is zero-engineering-cost distribution. The endpoint
wraps substrate.retrieve() and substrate.log() per the MCP tool spec.
**Why now:** MCP became the December 2025 standard; 2026 production deployments expect it. Being MCP-
compatible is table stakes for any enterprise LLM integration. The substrate engineering cost is low
(one MCP wrapper around existing substrate API).
**Tier hint:** Tier C (infrastructure, not capability -- but enables deployment of all Tier A capabilities)
**Gate pre-reg:** Not a gate test -- this is an integration milestone.
**Note:** Not a data experiment. This is a software integration task. Flag to exp_dev whether this is
in scope or should be routed to product/testbed.

---

### 5. TEMPORAL-ROUTING-POLICY (Pattern 4 with temporal state) -- LOWER PRIORITY, STRATEGIC
**Pointer:** Research Section 9 (temporal+contextual cross-thread)
**Substrate-product reading:** Routing decisions themselves as a temporal policy over conversation history.
A substrate that routes better over time (per-user query patterns) is a self-improving production system.
This is a differentiator vs fixed-routing competitors.
**Why now:** Lower priority than 1-3. The temporal+contextual mechanism is validated (PP-350 n=5 seeds).
Applying it to routing is the strategic next step, but the commercial case needs 1-3 done first.
**Tier hint:** Tier C (research hypothesis; temporal policy mechanism exists; application to routing is new)
**Gate pre-reg:**
- HARD-PASS: Temporal routing policy achieves >= 10% higher substrate-only routing rate after 100 queries
  vs static threshold routing on the same query stream (learning curve visible)
- HARD-FAIL: No learning curve after 100 queries (temporal routing adds no value vs static threshold)
**Note:** CPU-local. Requires a query stream with repeated topic patterns to show temporal learning.

---

## Context pointers (file paths, not summaries)

- Research note (full synthesis): d:/AI/hd-instrument/notes/research_drill_hybrid_architecture_deployment_2x_2026-06-11.md
- POS tagger result: d:/AI/hd-instrument/notes/exp_dev_to_research_WAVE2_RECIPES_AND_TIER2_STATUS_2026-06-11.md
- Slipnet polysemic ceiling: d:/AI/hd-instrument/notes/exp_dev_to_research_WAVE2_RESCUE_BATCH1_2026-06-11.md
- PP-228 categorical audit: d:/AI/hd-instrument/notes/capability_matrix_HONEST_AUDIT_2026-06-11.md
- PP-225 production scale fact memory: same
- PP-227 hybrid LM+fact-KV: same
- Temporal+contextual meta-pattern: d:/AI/hd-instrument/notes/exp_dev_to_research_TEMPORAL_CONTEXTUAL_3DOMAINS_2026-06-11.md
- Sprint-4 v3.2 wrapper: d:/AI/hd-instrument/notes/exp_dev_to_research_SPRINT4_ENGINEERED_WRAPPER_VALIDATED_2026-06-11.md
- Substrate vs LLM boundary (empirical): d:/AI/hd-instrument/notes/exp_dev_to_research_SUBSTRATE_VS_LLM_BOUNDARY_2026-06-10.md
- LLM boundary engineering framing: d:/AI/hd-instrument/notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md

---

## Contract section

This hand-off is a RESEARCH DELIVERABLE pointing at exp_dev-actionable experiments. The experiments are
ranked. Anchor 1 (CASCADE-ROUTING-THRESHOLD) is the highest commercial priority: it produces the cost
savings number for the Pattern 4 pitch. Anchors 2 and 3 are the quality and precision complements.

The research note does NOT pre-design the experiment cells. Per [[feedback-no-experiment-design-in-prompts]],
exp_dev designs the implementation given the anchor candidates and gate pre-regs above.

---

## Autonomy declaration

exp_dev has full autonomy to:
- Design the implementation for any anchor in this file
- Choose the order of dispatch based on queue state
- Adjust gate thresholds by +/-0.05 based on domain-specific prior knowledge
- Skip Anchor 4 (MCP endpoint) if it is out of scope for the experiment queue

exp_dev does NOT have autonomy to:
- Expand Pattern 5 (substrate-only) to open-domain NL without a domain classifier gate
- Treat the slipnet 0.42 ceiling as solved (it is an honest architectural constraint)
- Claim the routing threshold works without running Test A first
