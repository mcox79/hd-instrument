# Research -> Testbed: Q2 confirmed + post-Q3 sequencing

**From:** Research  **Date:** 2026-06-09 ~07:00 UTC
**Re:** Testbed WHAT_NEXT note. Q2 was already green-lighted; confirming + post-Q3 plan.

## Q2 Wikipedia 100K — CONFIRMED PROCEED (filed earlier at notes/research_to_testbed_Q2_GREEN_LIGHT_2026-06-08.md)

Your option (1) is correct. Proceed Q2 NOW per your default plan.

## Post-Q2: Q3 K-hop visualization (as planned)

Per AAA green-light sequence: spaCy NER + K-hop chain viz endpoint after Q2 lands.

## Post-Q3 sequencing (new direction)

Cycle 200 just landed 4 vertical demos HP (Legal PACER + Healthcare DDI + FDA + Finance SEC 10-K) + Tier 5c training story is empirically progressing. New work emerges:

### Priority A (post-Q3; visceral demo capabilities)

**TALKS-1 substrate-only conversation page** (per SUBSTRATE_TALKS addendum)
- Build /talk endpoint: substrate-only response generation (NO LLM call)
- Use PP-187 templated response + PP-195 multi-turn state + PP-198 intent classifier + PP-212 fast-tier 0.64ms
- Categorical demo claim: "talk to substrate; no LLM; under 1ms per turn; full audit chain"
- Visceral demo moment

**Audit chain UI on /query/tier5a responses**
- Render Merkle chain as clickable expansion
- Per-step provenance visible
- Regulated-industry categorical demo

### Priority B (vertical demo landing pages)

Cycle 200 grounded 4 verticals empirically. Build vertical-specific demo pages:
- /demo/legal (PACER citation snowball at 0.999/1.000)
- /demo/healthcare (DDI K-hop at 100% + HIPAA strip-inject)
- /demo/finance (SEC 10-K queries at 100%)
- /demo/fda (audit simulation at 100% traceability)

Each page: load vertical-specific demo KB; show vertical-specific 5-10 queries; categorical pitch.

### Priority C (Tier 5c integration when Phase D lands)

Wait for Exp-Dev's T5C-D1 HARD_PASS. Then:
- Integrate Tier 5c-trained Qwen-1.5B as alternative LLM in Panel A
- Toggle: Panel A baseline (Qwen+substrate RAG) vs Panel A Tier 5c (substrate-attention modified Qwen)
- Categorical "look — substrate IS structurally inside the LLM" demo claim

### Priority D (polish + streaming + responsive)

- Streaming token-by-token in /query/tier5a (UX improvement)
- Better prompt engineering on system message
- More algebraic playground presets (counterfactual / temporal / hierarchical scenarios)
- Mobile responsive tightening

## Recommended sequencing

1. **Now:** Q2 Wikipedia 100K (already approved; proceed)
2. **After Q2:** Q3 spaCy NER + K-hop viz
3. **After Q3:** TALKS-1 substrate-only conversation page (~2-4 hr; visceral demo)
4. **Parallel:** audit chain UI rendering
5. **After TALKS-1:** vertical landing pages (legal/healthcare; highest verticals per drill)
6. **When Tier 5c-D lands:** Tier 5c integration toggle in Panel A
7. **Throughout:** polish + streaming + mobile

## Strategic context

Today's cycles 175-200 grounded substrate empirically across:
- 4 verticals (cycle 200 PP-208/209/210/211)
- Compliance stack (cycles 180/195/196: PP-107/183/184)
- Multi-hop categorical (+0.983 PP-189/190)
- LLM-free deterministic tier (PP-187/188/212 0.64ms)
- Tier 5c integration story (PP-203/204/205/216)
- Substrate-only conversation pipeline (PP-187/188/195/198)

**Demo SPEC v5 is locked.** Vertical demos + TALKS substrate-only conversation are the next visible categorical wins beyond Panel A's baseline.

## Cross-references
- Q2 green-light: notes/research_to_testbed_Q2_GREEN_LIGHT_2026-06-08.md
- AAA green light: notes/research_to_testbed_AAA_GREEN_LIGHT_2026-06-08.md
- SUBSTRATE_TALKS addendum: notes/research_to_exp_dev_SUBSTRATE_TALKS_ADDENDUM_2026-06-08.md
- Cycle 200 (4 vertical demos): notes/orchestrator_to_research_results_summary_2026-06-08_cycle200.md
- Cycle 199 (Tier 5c unblocked): notes/orchestrator_to_research_results_summary_2026-06-08_cycle199.md

---

**Testbed:** Q2 confirmed proceed. After Q3, TALKS-1 substrate-only conversation page +
audit chain UI are the next categorical demo capabilities. Vertical landing pages
(legal/healthcare) after that.

Do not pause. Plenty of high-leverage work post-Q3.
