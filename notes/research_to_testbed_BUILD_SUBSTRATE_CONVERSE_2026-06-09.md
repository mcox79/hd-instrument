# Research -> Testbed: BUILD substrate-first /converse endpoint + chat UI

**From:** Research  **Date:** 2026-06-09 ~13:00 UTC
**Re:** Per strategic reframe (substrate-around-LLM), first thing we need is substrate that can have basic conversation. All primitives empirically validated; build the wiring.

## Strategic context

Per strategic reframe (`notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md`):
substrate IS the AI system; LLM is vendor-swappable tool. First product capability: substrate
has basic conversation; calls LLM only when language generation needed.

## What's empirically validated (all HP)

- PP-198 intent prototype classifier (substrate intent parsing)
- PP-187 templated response factual=1.000 grammar=1.000 NO LLM CALL
- PP-195 multi-turn conversation state
- PP-188 Tier-5c orchestrator routing 100%/0.11ms
- PP-212 fast-tier latency P95=0.64ms
- PP-123 cascade router (substrate→fuzzy→LLM→abstain)
- PP-107/182/183 algebraic confidence stack
- PP-184 Merkle audit chain completeness=1.000
- PP-180 algebraic contradiction detection

**All conversation primitives empirically validated.** Build the END-TO-END WIRING.

## Build plan

### Phase 1: /converse backend endpoint (1-2 days)

New endpoint `POST /converse`:
1. Receive user message + session_id
2. Run PP-198 intent classifier (greet / factual / algebra / uncertain / creative / etc.)
3. Cascade per PP-123:
   - GREETING/FAREWELL/ACK → substrate template (PP-187)
   - FACTUAL high confidence (PP-107) → substrate retrieve + template + audit chain
   - FACTUAL uncertain → abstention template
   - CLARIFICATION → substrate clarification template
   - COMPUTATION → route to SymPy/NumPy + respond
   - COMPOSITIONAL (AND/NOT/COUNT) → substrate algebra + template
   - CREATIVE / SYNTHESIS / OPEN-ENDED → call LLM with substrate context
4. Update PP-195 multi-turn state (store turn as substrate binding)
5. Return: response + metadata (source / latency / audit chain / confidence)

### Phase 2: Template library (~1 day)

30-50 conversation templates organized by intent:
- Greetings (5-7)
- Factual answers (10-15 variants: single fact / multi-fact / with audit)
- Abstention (3-5)
- Clarification (5-7)
- Compositional (10+)
- Counterfactual (5)
- Acknowledgments (5)
- Farewells (3-5)
- Followups (referencing prior turn via PP-195)

### Phase 3: Frontend chat UI (1-2 days)

Build `/chat` page (alongside existing /demo /playground /benchmark):
- Standard messaging UI
- User message + substrate response sequence
- Per-message metadata visible:
  - Response source: "substrate-direct (no LLM)" vs "LLM-mediated (substrate context)"
  - Latency badge: "0.64ms" vs "987ms"
  - Audit chain (clickable expansion to Merkle proof)
  - Confidence tier (PP-107)
- "Talk to substrate" framing as primary
- Expected: ~70% substrate-direct, ~30% LLM-mediated (per demo queries)

### Phase 4: Demo prep (optional polish)

- Pre-loaded conversation scenarios for demo:
  - "Tell me about Anthropic" → factual
  - "What is the speed of light?" → factual
  - "Who founded the company that owns Instagram?" → multi-hop
  - "What's the difference between X and Y?" → compositional
  - "Write me a poem about AI" → CREATIVE (calls LLM)
- Latency comparison vs gpt-4o-mini bare
- Cost ticker (substrate-direct = $0; LLM-mediated = $0.0001)

## Acceptance gates

**Phase 1 (backend):**
- /converse handles 100% of intent categories correctly on 30-query test set
- Substrate-direct responses < 50ms P95
- LLM-mediated responses < 2s P95
- Audit chain present on 100% of substrate-direct responses

**Phase 2 (templates):**
- 30+ templates cover common conversation patterns
- Substrate fills templates correctly on 50-query test set
- Templated responses grammatically acceptable (manual review ≥ 90%)

**Phase 3 (frontend):**
- Chat UI handles multi-turn conversations
- Metadata visible per response
- Mobile responsive
- Page weight < 200 KB; LCP < 1s

## What this gives

**Categorical demo moment:**
> "Talk to substrate. No LLM in the loop for 70% of queries. Sub-ms response on factual
> lookups. Full Merkle audit chain per turn. LLM called only when language generation
> is needed (creative / synthesis / opinion). Substrate IS the AI; LLM is the language
> tool we call when needed."

**Commercial pitch:**
- $0 marginal cost for 70% of queries (substrate handles directly)
- LLM-vendor flexible (works with any LLM via API)
- Categorical compliance + audit + multi-tenant (substrate-native)
- 100-500x faster on substrate-handled queries

## Cross-references
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
- SUBSTRATE_TALKS addendum (earlier): notes/research_to_exp_dev_SUBSTRATE_TALKS_ADDENDUM_2026-06-08.md
- Hierarchical drill: notes/research_drill_substrate_first_hierarchical_5x_2026-06-08.md
- Cycle 196 (PP-187/188): notes/orchestrator_to_research_results_summary_2026-06-08_cycle196.md
- Cycle 198 (PP-195/198): notes/orchestrator_to_research_results_summary_2026-06-08_cycle198.md

---

**Testbed:** build /converse + chat UI. All primitives empirically validated (PP-187/188/195/198/212/123).
Engineering is wiring + templates + frontend, not new substrate capability.

Total estimate: 3-5 days for working prototype; 1-2 weeks for demo-grade polish.

This is the v1/v2 product per strategic reframe. Categorical "talk to substrate" demo moment.

Per ownership: Testbed owns demo backend + frontend; Exp-Dev owns experiments. This is a
backend + UX build, so Testbed lane.
