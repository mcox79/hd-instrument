# Research -> Exp-Dev: substrate conversational capability extensions (15 anchors)

**From:** Research  **Date:** 2026-06-09 ~14:00 UTC
**Re:** Per strategic reframe + honest re-examination of substrate capabilities, build out the conversational primitives that make substrate-around-LLM categorical at 85-90% substrate-direct (not 70%).

## Strategic context

Substrate's conversational range is BROADER than I'd characterized. Template engineering + substrate algebra can handle:
- Creative forms (haiku, sonnet, limerick)
- Bullet summaries
- Empathic responses
- Translation
- Code patterns
- Opinion expression
- Pattern-based humor

LLM only needed for truly novel fluent generation / spontaneous wit / unscripted complexity.

**Goal:** push substrate-direct to 85-90% of queries via template + substrate algebra extensions.

## Tier 1: highest-leverage conversation primitives (5 anchors)

### CONV-1: Creative form template library
- Substrate-product reading: hand-write templates for haiku (5-7-5) + sonnet (14 lines ABAB rhyme) + limerick (AABBA) + couplet; substrate retrieves topic-relevant words from KB matching syllable/rhyme constraints; fills template
- Tier: LOCAL CPU
- HARD-PASS: substrate generates grammatically-valid haiku for ≥ 80% of 100 test topics; syllable count exact; topic-relevance ≥ 0.70

### CONV-2: Multi-fact summarization
- Substrate-product reading: substrate retrieves top-K facts by PP-107 confidence + PP-206 NDCG ranking; templates "Here are the key facts: 1. X 2. Y 3. Z"; covers single-entity, multi-entity, temporal sequence summaries
- Tier: LOCAL CPU
- HARD-PASS: summaries factually correct ≥ 0.95 + grammatically acceptable ≥ 0.90 on 100 test queries

### CONV-3: Empathic response templates (intent-conditioned)
- Substrate-product reading: PP-198 intent classifier extended to detect emotional intents (sad / frustrated / happy / confused); response template selected per intent; substrate matches user formality level
- Tier: LOCAL CPU
- HARD-PASS: empathic responses appropriately match emotional intent on 200-query test set ≥ 0.85

### CONV-4: Substrate clarification + repair templates
- Substrate-product reading: when ambiguity detected (PP-180 contradiction or multi-interpretation candidates), substrate asks for clarification; when user corrects substrate ("no that's wrong"), substrate updates + acknowledges
- Tier: LOCAL CPU
- HARD-PASS: substrate identifies ambiguity ≥ 0.80; clarification template appropriate ≥ 0.85; correction acknowledgment ≥ 0.95

### CONV-5: Memory decision logic ("what to remember")
- Substrate-product reading: hybrid logic per intent + PP-107 confidence; substrate stores conversation turns by default; auto-extracts facts on high confidence; user-explicit "remember/forget" honored
- Tier: LOCAL CPU
- HARD-PASS: appropriate memory decisions ≥ 0.85 on 200-message test conversations + 100% PP-104 erasure on explicit forget

## Tier 2: substrate range extension (5 anchors)

### CONV-6: Multilingual translation via KB
- Substrate-product reading: Wikidata multilingual entity loading + word-pair triples + grammar templates for basic translation; English ↔ Spanish + English ↔ French at minimum
- Tier: LOCAL CPU
- HARD-PASS: substrate produces grammatically-valid translation on 100 simple sentences ≥ 0.80 (compared to gold standard)

### CONV-7: Code pattern library
- Substrate-product reading: 50+ common code patterns stored as templates (sort, search, recursion, common data structures); substrate retrieves + parameterizes per user query
- Tier: LOCAL CPU
- HARD-PASS: substrate produces syntactically-correct code for 30 common pattern requests ≥ 0.90

### CONV-8: Opinion expression
- Substrate-product reading: substrate stores opinions explicitly ("substrate's view on X is Y"); aggregates source opinions; algebraic rule derivation
- Tier: LOCAL CPU
- HARD-PASS: substrate expresses stored opinions correctly on 100 test queries ≥ 0.95; aggregation appropriate ≥ 0.85

### CONV-9: PII detection during conversation
- Substrate-product reading: PP-186 PII strip-inject pattern adapted to conversation flow; substrate detects PII as user types; offers to handle without storing OR substitute placeholders
- Tier: LOCAL CPU
- HARD-PASS: PII detection ≥ 0.90 recall + ≤ 5% false positive on 200-message test set

### CONV-10: User preference learning
- Substrate-product reading: substrate stores user preferences explicitly (formal/casual, technical/simple, verbose/concise) over multiple sessions; adapts response style
- Tier: LOCAL CPU
- HARD-PASS: substrate preferences correctly applied across 50 conversations ≥ 0.85; user can override at any turn

## Tier 3: substrate algebra extensions (5 anchors; harder R&D)

### CONV-11: Modal logic operators
- Substrate-product reading: extend substrate algebra with necessary (□) and possibly (◇) operators as binding variants; modal reasoning primitives
- Tier: LOCAL CPU
- HARD-PASS: modal reasoning correct on 100 standard modal logic queries ≥ 0.85

### CONV-12: Probabilistic primitives extension
- Substrate-product reading: extend PP-155 continuous strength with full Bayesian primitives (prior/likelihood/posterior bindings); probabilistic update operator
- Tier: LOCAL CPU
- HARD-PASS: probabilistic reasoning correct on 100 Bayesian queries ≥ 0.80

### CONV-13: Higher-order substrate composition
- Substrate-product reading: substrate operations on operations (e.g., "all X such that they satisfy property P"); quantification primitive
- Tier: LOCAL CPU
- HARD-PASS: higher-order queries handled on 50 test queries ≥ 0.80

### CONV-14: Substrate humor templates (pattern-based)
- Substrate-product reading: hand-write 30+ joke templates (knock-knock, pun, wordplay); substrate fills with topic-relevant words from KB
- Tier: LOCAL CPU
- HARD-PASS: humor templates produce grammatically-valid output on 100 test topics ≥ 0.80 (subjective humor quality not gated)

### CONV-15: Substrate-routed tool calls (extension)
- Substrate-product reading: substrate decides when to call SymPy / NumPy / code interpreter / image generator; routing accuracy + tool integration
- Tier: LOCAL CPU
- HARD-PASS: routing accuracy ≥ 0.90 on 200-query mixed-tool benchmark; tool integration latency < 100ms

## Sequencing recommendation

**Day 1-2 (highest leverage; CPU):**
- CONV-1 (creative forms)
- CONV-2 (summaries)
- CONV-3 (empathic templates)
- CONV-5 (memory decision)

**Day 3-4 (range extension):**
- CONV-4 (clarification/repair)
- CONV-6 (translation)
- CONV-9 (PII detection)
- CONV-10 (user preferences)

**Day 5-7 (substrate-tool integration):**
- CONV-7 (code patterns)
- CONV-8 (opinion expression)
- CONV-15 (routed tool calls)

**Week 2+ (algebra extensions R&D):**
- CONV-11/12/13 (modal/probabilistic/higher-order)
- CONV-14 (humor)

## Strategic intent

After this batch lands, substrate-around-LLM can claim:
- **Substrate handles 85-90% of queries directly** (vs prior 70% estimate)
- **LLM called only for genuinely novel fluent generation**
- **Categorical capabilities LLM-alone cannot match:**
  - Sub-ms latency for all substrate-direct (PP-212)
  - Full audit chain per response (PP-184)
  - GDPR exact erasure on demand (PP-104)
  - Multi-tenant isolation (PP-101 = 0.0000)
  - Cross-session persistence (substrate state)
  - Algebraic compositionality (Datalog^neg)

## What this enables for demo

- "Talk to substrate" demo expanded:
  - User asks for haiku → substrate generates (template + KB)
  - User asks for summary → substrate ranks + templates
  - User says something emotional → substrate responds empathically
  - User asks for code → substrate retrieves pattern + parameterizes
  - User asks LLM-required ("write me a novel about X") → routes to LLM
- Cost/latency comparison vs LLM-first becomes more visceral (substrate handles more)

## Cross-references
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
- Substrate /converse build: notes/research_to_testbed_BUILD_SUBSTRATE_CONVERSE_2026-06-09.md
- SUBSTRATE_TALKS addendum (foundation): notes/research_to_exp_dev_SUBSTRATE_TALKS_ADDENDUM_2026-06-08.md
- Substrate-first hierarchical drill: notes/research_drill_substrate_first_hierarchical_5x_2026-06-08.md
- Substrate math drill: notes/research_drill_substrate_math_capabilities_5x_2026-06-08.md

---

**Exp-Dev:** 15 conversational capability anchors across 3 tiers. Tier 1 (5 anchors)
gives highest immediate demo leverage; substrate handles 85-90% directly. Tier 2 (5
anchors) extends range. Tier 3 (5 anchors) extends substrate algebra primitives (R&D).

All CPU-friendly; no GPU needed. Runs alongside Tier 5c Phase C/D + Q2 ingest + other
work without contention.

Substrate's conversational capability extension is the key v1/v2 product investment per
strategic reframe.
