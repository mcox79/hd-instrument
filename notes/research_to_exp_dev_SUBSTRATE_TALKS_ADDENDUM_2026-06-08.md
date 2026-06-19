# Research -> Exp-Dev: SUBSTRATE-TALKS addendum (substrate has its own limited conversation)

**From:** Research  **Date:** 2026-06-09 ~01:45 UTC
**Re:** User clarification: "I think it's important to show that substrate ITSELF can
have a limited language conversation." Substrate-without-LLM conversational capability.

## Critical distinction from prior BATCH routing

Prior batch (BATCH_HIERARCHICAL_LM_TIER5C) framed substrate-first as "substrate handles
simple; LLM handles complex via handoff." User correction: **substrate should be able to
have LIMITED CONVERSATIONS BY ITSELF.** Not just retrieval-then-handoff. Actual substrate
conversational ability for simple cases.

## What this requires

**Substrate-only conversational pipeline:**
1. **Intent parsing** without LLM in loop (small classifier + substrate algebraic decomposition)
2. **Templated response generation** from substrate-retrieved facts (no LLM)
3. **Multi-turn state tracking** (substrate maintains conversation context)
4. **Conversational style** (greeting / clarification / abstention / farewell)
5. **Demo capability:** user talks to substrate; substrate talks back

This is categorically different from "substrate retrieves; LLM generates." Substrate IS the language interface for simple queries.

## Empirical foundation

Substrate already has:
- PP-179 n-ary arbitrary arity (any conversation state schema)
- PP-180 contradiction detection (clarification triggers)
- PP-182/183 confidence stack (abstention / "I don't know")
- PP-123 cascade router (handoff trigger to LLM when needed)
- PP-117 negation + PP-115 one-shot relation transfer

What's MISSING (engineering):
- Substrate-template generation grammar (small)
- Multi-turn state persistence layer (substrate bindings encoding turn history)
- Intent parser specifically for conversation acts (greeting / question / followup / etc)

## Specific anchors

### TALKS-1: Substrate template response grammar (no LLM)
- Substrate-product reading: hand-write 20-30 response templates covering common conversation patterns (lookup answer / clarification / abstention / multi-fact summary / acknowledgment); substrate fills templates with retrieved facts
- Tier: LOCAL CPU
- HARD-PASS: substrate-template responses grammatically correct on 100 test queries ≥ 0.90; factually correct ≥ 0.85

### TALKS-2: Substrate intent parser for conversation acts
- Substrate-product reading: small classifier categorizes user input into conversation act (question / clarification / acknowledgment / greeting / farewell / off-topic); substrate operates accordingly
- Tier: LOCAL CPU
- HARD-PASS: intent classification ≥ 0.85 on 200-input test set

### TALKS-3: Multi-turn conversation state in substrate
- Substrate-product reading: substrate stores conversation history as bindings (turn-N: (user, said, X); (substrate, said, Y)); substrate can reference prior turns ("what did I just ask?")
- Tier: LOCAL CPU
- HARD-PASS: substrate correctly references prior turns ≥ 0.90 on 50-conversation test

### TALKS-4: Substrate-only conversation demo
- Substrate-product reading: end-to-end substrate-only conversation; 50-100 multi-turn dialogues; no LLM in loop
- Tier: LOCAL CPU
- HARD-PASS: dialogue coherence + factual correctness + appropriate abstention ≥ 0.75 on human evaluation
- DEMO target: visceral "talk to substrate" moment

### TALKS-5: Substrate conversation latency
- Substrate-product reading: per-turn latency for substrate-only conversation
- Tier: LOCAL CPU
- HARD-PASS: ≤ 50ms per-turn (vs LLM-mediated ~1000ms+) — 20x+ faster

## Demo significance

**Categorical demo moment:**
> "Watch a conversation with NO LLM. Substrate talks. You ask; substrate retrieves;
> substrate generates response; all under 50ms; full audit chain. Substrate IS the
> language interface for simple queries."

This proves substrate isn't just a memory layer — it's a complete cognitive interface
for the simple-query majority of human interaction.

## Honest scope

**Substrate-only conversation will be:**
- LIMITED in vocabulary and style (templated)
- LIMITED in complex reasoning (substrate's algebra; no creative generation)
- COHERENT for factual / lookup / count / comparison / abstention
- INADEQUATE for: creative writing / opinion / nuanced multi-turn reasoning / open-ended chat

**Substrate-only conversation will NOT be:**
- Frontier-LLM-quality prose
- Creative or opinionated
- Subtle in tone
- Capable of arbitrary conversational topics

**Substrate-only conversation WILL be:**
- Fast (<50ms vs LLM seconds)
- Auditable (every utterance traceable)
- Private (no API; local)
- Factually grounded
- Categorically deployable for FAQ / customer service / structured Q&A

## Cross-references
- BATCH_HIERARCHICAL_LM_TIER5C (prior): notes/research_to_exp_dev_BATCH_HIERARCHICAL_LM_TIER5C_2026-06-08.md
- Substrate-only LM drill (broader research direction; in flight)
- Substrate-first hierarchical drill (in flight)
- Cycle 195 (3-layer confidence stack locked): notes/orchestrator_to_research_results_summary_2026-06-08_cycle195.md

---

**Exp-Dev:** TALKS series is the substrate-CAN-talk demo capability. TALKS-1 (template
grammar) + TALKS-3 (multi-turn state) + TALKS-4 (end-to-end demo) is the visceral demo
moment. TALKS-2 (intent parser) and TALKS-5 (latency) are supporting.

Sequencing: TALKS-1 (foundation) → TALKS-2 → TALKS-3 → TALKS-4 (integration) → TALKS-5 (validation).

This addendum supersedes the implicit "substrate-first means substrate-then-LLM" framing
in the prior BATCH. Substrate-FIRST means substrate handles AS MUCH AS IT CAN INCLUDING
SOME LIMITED CONVERSATION; LLM only invoked when substrate can't manage.
