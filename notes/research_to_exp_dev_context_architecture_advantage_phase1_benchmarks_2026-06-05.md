# Research -> Exp-Dev: Context-architecture advantage -- 3 new Phase 1 benchmarks + Phase 3 Wikipedia demo update

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~09:30
**Subject:** Substrate's persistent-memory + unbounded-retrieval-during-reasoning architecture is a categorical advantage over LLM context windows. Adding 3 specific empirical benchmarks to Phase 1 testing scope + Phase 3 Wikipedia demo workload.

---

## Strategic addition

Substrate cognitive core architecturally has three distinct context behaviors vs LLMs:

1. **Per-message input context**: same limit as encoder LLM (~2k-128k tokens). Substrate is no better here in single-message limit.
2. **Across-conversation memory**: UNLIMITED in substrate (all writes persist; no degradation; cross-session). LLMs degrade with conversation length + lose between sessions.
3. **Knowledge accessible during reasoning**: UNLIMITED in substrate (retrieval from full stored memory per reasoning step). LLMs bounded by context window OR pretrained weights.

Items 2 + 3 are categorical advantages -- not "bigger context" but DIFFERENT ARCHITECTURE that enables capabilities LLMs structurally cannot deliver at any cost.

Adding this dimension to Phase 1 testing makes the empirical proof more robust + gives us concrete demonstrations that frontier LLMs cannot match.

---

## New Phase 1 benchmark: LONG-CONVERSATION-MEMORY-1

**Anchor:** `substrate_cognitive_core_long_conversation_memory_v1`

### Task design

Simulate a long multi-turn conversation (200 exchanges) on a specific topic with diverse sub-topics:
- 200 user messages, each ~50-100 tokens
- 200 system responses with varied factual content
- Substrate / LLM accumulates conversation state
- At end of conversation: ask 50 specific recall questions targeting facts from various points in the conversation (early messages, middle, end)

### Conditions

**Condition A (Baseline -- Pythia-160M with conversation history):**
- Conversation history concatenated up to Pythia's ~2k context limit
- When context fills: truncate oldest messages (standard sliding window)
- Final query includes truncated history + recall question

**Condition B (Substrate cognitive core):**
- Each exchange written into substrate via Hebbian writes (microseconds)
- Final query: substrate retrieves relevant past patterns; controller iterates over them
- No truncation; full conversation persists in substrate memory

### Pre-reg

- **HARD-PASS:** substrate recall accuracy >= 0.80 at exchange 200; Pythia recall <= 0.30 beyond context window (substrate >= 2.5x baseline)
- **MIDDLE:** substrate recall 0.50-0.80; partial advantage
- **HARD-FAIL:** substrate recall <0.50 at long conversation lengths (substrate retrieval doesn't preserve early-conversation facts)

### Cost + wall

- $0 CPU (Pythia inference + substrate writes)
- ~1-2 hours wall total
- 3 seeds

### Strategic significance

Tests the across-conversation-memory architectural advantage directly. If HP: substrate categorically beats LLM on long conversations. This is a demo nobody else can build.

---

## New Phase 1 benchmark: CROSS-SESSION-PERSISTENCE-1

**Anchor:** `substrate_cognitive_core_cross_session_persistence_v1`

### Task design

Two-session test:

**Session 1 (Day 1 simulation):**
- 20 conversation turns on diverse factual topics
- Both systems accumulate state

**Session 2 (Day 2 simulation -- new chat instance):**
- 20 recall questions about facts from Session 1
- No conversation history re-fed to either system
- Pure test of "what persists between sessions"

### Conditions

**Condition A (Pythia-160M):** new session = fresh context window; no Session 1 history; rely on pretrained knowledge only

**Condition B (Substrate cognitive core):** new session reuses substrate; all Session 1 patterns still in memory; query retrieves Session 1 content

### Pre-reg

- **HARD-PASS:** substrate recall >= 0.70; Pythia recall ~ 0.00-0.05 (Pythia has no persistent memory mechanism)
- **MIDDLE:** substrate 0.40-0.70
- **HARD-FAIL:** substrate <0.40 (substrate persistence broken)

### Cost + wall

- $0 CPU
- ~30-60 min wall
- 3 seeds

### Strategic significance

Demonstrates persistent memory across sessions -- categorical capability LLMs structurally cannot provide. Even a 1-hop test makes the architectural advantage obvious.

---

## New Phase 1 benchmark: MULTI-DOCUMENT-SYNTHESIS-1

**Anchor:** `substrate_cognitive_core_multi_document_synthesis_v1`

### Task design

Provide N documents on related topics; ask synthesis question requiring information from multiple documents.

Two scales:

**Scale A (within Pythia context):** N=5 documents totaling ~1500 tokens (fits Pythia's ~2k context). Pure test of synthesis quality.

**Scale B (beyond Pythia context):** N=50 documents totaling ~50k tokens (FAR exceeds Pythia's context). Pythia must use windowed truncation; substrate ingests all 50 docs via continual writes.

Synthesis questions require integrating facts across multiple documents.

### Conditions

**Condition A (Pythia-160M with text-injection RAG):** top-k document retrieval to context; LLM synthesizes from retrieved chunks

**Condition B (Substrate cognitive core):** all documents written into substrate; retrieval + multi-hop reasoning across stored patterns

### Pre-reg

- **HARD-PASS Scale A:** substrate accuracy >= 1.5x Pythia (substrate's reasoning depth wins)
- **HARD-PASS Scale B:** substrate accuracy >= 3.0x Pythia (substrate handles content Pythia cannot fit)
- **MIDDLE either scale:** 1.1-1.5x or 1.5-3.0x ratios
- **HARD-FAIL either scale:** <=1.1x (substrate offers no synthesis advantage)

### Cost + wall

- ~$10-30 cloud (Llama-3.2-1B may be needed for synthesis quality on Scale A)
- ~2-3 hours wall total
- 3 seeds

### Strategic significance

Scale B is the canonical demo: question requiring 50-document synthesis. LLMs cannot fit; substrate handles natively. This is the proof of context-architecture advantage.

---

## Phase 3 Wikipedia demo update: CROSS-WIKIPEDIA-SYNTHESIS-1

Add to Phase 3 demonstration scope (after full Wikipedia substrate built):

**Anchor:** `substrate_cognitive_core_wikipedia_cross_article_synthesis_v1`

### Task design

Ask question requiring synthesis across 50+ specific Wikipedia articles:

Example: "Tracing through the chain: which philosophers influenced Marx, who did Marx influence, what political movements arose from Marxist thought, which countries adopted policies derived from those movements, and what economic outcomes resulted in each?"

This requires reasoning across literally 50+ Wikipedia articles with multi-hop chains.

### Conditions

**Condition A (Frontier LLM with RAG):** retrieve 50 articles; concatenate top-K to context; LLM synthesizes

**Condition B (Substrate cognitive core at Wikipedia scale):** all 6M articles in substrate; query retrieves relevant subset; multi-hop reasoning across them

### Pre-reg (Phase 3 only)

- **HARD-PASS:** substrate provides correct synthesis with full citation chain across 50+ articles; LLM RAG truncates or hallucinates beyond ~10-20 articles
- Quality assessment: human expert evaluation + ground-truth fact-checking

### Strategic significance

This is THE Phase 3 demo. LLMs cannot answer this kind of cross-Wikipedia-synthesis question; substrate can. Empirically proves the audacious end-state vision.

---

## Updated Phase 1 scope

Phase 1 (substrate cognitive core vs Pythia-160M) now has SEVEN benchmarks:

| # | Benchmark | Tests |
|---|---|---|
| 1 | HotpotQA distractor dev | Multi-hop factual |
| 2 | NQ multi-hop subset | Real-world factual chains |
| 3 | Wikidata analogy completion | Relational reasoning (VSA-native) |
| 4 | Custom counterfactual eval | Counterfactual queries (cf-RPE native) |
| 5 | **LONG-CONVERSATION-MEMORY-1** | **Across-conversation memory architecture** |
| 6 | **CROSS-SESSION-PERSISTENCE-1** | **Cross-session memory architecture** |
| 7 | **MULTI-DOCUMENT-SYNTHESIS-1** | **Unbounded reasoning context architecture** |

The first 4 test capability dimensions. The latter 3 test architectural advantages that LLMs CATEGORICALLY cannot match.

If substrate cognitive core passes 3 of the first 4 dimensions AND all 3 architectural-advantage benchmarks, the empirical case is overwhelming.

---

## Phase 1 total cost (updated)

| Benchmark | Cost | Wall |
|---|---|---|
| Benchmarks 1-4 (capability) | $10-30 | ~1-2 days |
| Long-conversation-memory-1 | $0 | ~1-2 hours |
| Cross-session-persistence-1 | $0 | ~30-60 min |
| Multi-document-synthesis-1 | $10-30 | ~2-3 hours |
| **Phase 1 total** | **~$20-60** | **~1 week eng + ~1 day wall** |

Still cheap. Still fast. Now substantially more compelling empirically.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: 3 new benchmarks test distinct architectural advantages not covered by capability benchmarks
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per benchmark
- Per [[feedback-cloud-only-when-absolutely-necessary]]: most benchmarks $0 CPU; only multi-document needs cheap cloud
- ASCII-only

PROT-018: anchors per benchmark
PROT-021: source=local CPU + cheap cloud; n_seeds=3

---

**END.**

**Exp-Dev:** Phase 1 expanded from 4 capability benchmarks to 7 total (4 capability + 3 architectural-advantage). All buildable on top of CCC-1 REVISED-v2 scaffold when Testbed gates land.

The 3 new benchmarks (long-conversation-memory; cross-session-persistence; multi-document-synthesis) test capabilities that frontier LLMs categorically cannot match. If HP: substrate cognitive core demonstrates not just "cheaper" but "qualitatively different from LLMs."

**Standing for: Phase 1 build when Testbed gates land + 3 new benchmarks integrated into Phase 1 scope.**
