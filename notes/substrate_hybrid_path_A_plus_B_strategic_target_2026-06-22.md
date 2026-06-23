# Substrate hybrid end-state: Path A + Path B in ONE matrix (USER strategic target 2026-06-22)

**Date:** 2026-06-22 (USER directive: "our end state could very well be a combo of A and B")
**Status:** strategic architecture spec; supersedes pure Path A OR pure Path B framings
**Composes with:** L1 directive (substrate-as-LLM-substitute) + L2 MVP frontier + L3 capabilities tier + Phase 1/2/3 substrate self-improvement

## Why hybrid is the right end-state

The substrate's UNIQUE property (vs transformers + RAG-systems): **a single bipolar HD matrix W can simultaneously hold knowledge-graph structure AND language patterns**, retrievable via the SAME Hebbian outer-product mechanism. Transformers + retrieval-augmented-generation systems use TWO separate components (LM + KG database). Ours is ONE.

USER strategic insight 2026-06-22: substrate-native relational HD representation of language ITSELF — cat-dog similarity emerges from co-occurrence in the same W, alongside explicit (cat, IS_A, animal) triples ingested from KG. Both paths use the same primitives:

| Layer | Path A (language patterns) | Path B (knowledge graph) | SAME PRIMITIVE? |
|---|---|---|---|
| Encode | char_trigram + relational-distributional | char_trigram | **YES** (char_trigram_encoder; chain-grade CERT 585) |
| Store | Hebbian outer-product of (word_t, NEXT, word_t+1) | Hebbian outer-product of (s, p, o) | **YES** (KGStore + W matrix) |
| Retrieve | matmul + argmax on word codebook | matmul + argmax on entity codebook | **YES** (same KGStore primitive) |
| Reason | sequence chain (next-token) | multi-hop relation chain | **YES** (multi_hop + SequenceMatrix) |
| Generate | autoregressive sequence | KG walk over W | **YES** (SubstrateGenerator g1b CERT 587) |
| Refuse-gate | confidence-thresholded | confidence-thresholded | **YES** (refuse_gate primitive) |

ALL layers use the SAME chain-grade primitives. Hybrid is architecturally free.

## What the hybrid enables that neither path alone can

1. **Grounded generation**: substrate generates entity sequences (Path B) AS WORDS (Path A). Generated answer is fluent text BECAUSE the substrate knows both relational structure AND word-co-occurrence patterns simultaneously.

2. **Semantic question-understanding**: user asks "what color is the sky?" → char_trigram + relational-distributional encoder finds anchor (concept of "sky" or "blue") via SEMANTIC similarity (not just substring), then KG retrieves grounded fact (sky HAS_PROPERTY blue), then language layer renders as English sentence.

3. **Co-trained-by-design**: every fact ingested as a KG triple ALSO inserts the entity-names into the language layer's vocabulary. Every text ingested for co-occurrence ALSO informs which entity tokens are near each other. The two paths reinforce each other.

4. **Single-matrix economy**: 1M words × 32-dimensional embeddings = 32MB. 1M facts × N=16384 = 32GB. Hybrid uses ONE matrix at the optimal N validated by scaling cell. Whatever capacity bound we discover applies to BOTH paths in the SAME matrix.

5. **Phase 2/3 substrate self-improvement APPLIES TO BOTH PATHS**: substrate self-mapping (v2d running) clusters its own chain-grade atoms — both LM atoms and KG atoms. Autoatom (Phase 2) can propose new linguistic patterns AND new factual relations. Phase 3 substrate-proposes-mathematics could discover patterns spanning BOTH paths.

## Architecture sketch

```
                              USER input (English text)
                                       ↓
                ┌──────────────── ENCODE ────────────────┐
                │  char_trigram (surface)                │
                │  + relational-distributional (semantic)│ ← NEW primitive (drill in flight)
                └────────────────────────────────────────┘
                                       ↓
                              query HD vector q
                                       ↓
        ┌───────────── DUAL RETRIEVAL (same matrix W) ─────────────┐
        │                                                          │
        │  Path B retrieval:                Path A retrieval:      │
        │  score_kg = W_KG @ q              score_lm = W_LM @ q    │
        │  top-K entities                   top-K next-tokens      │
        │  (CONCEPT layer)                  (TOKEN layer)          │
        │                                                          │
        │  W_KG and W_LM are the SAME W (superposition) OR         │
        │  separate decoupled matrices that compose at output.     │
        └──────────────────────────────────────────────────────────┘
                                       ↓
                  ┌─────── REASON (multi-hop) ─────────┐
                  │  iter_cleanup_chain (Path B)       │
                  │  + sequence_predict (Path A)       │
                  │  + refuse_gate (confidence)        │
                  └────────────────────────────────────┘
                                       ↓
                  ┌─────── GENERATE (g1b autoregressive) ───┐
                  │  emit token sequence with both:         │
                  │  - KG entities (Path B retrieved)       │
                  │  - language continuation (Path A)       │
                  └─────────────────────────────────────────┘
                                       ↓
                         response = grounded English sentence
                         (zero LLM/external model anywhere)
```

## What's chain-grade today vs gaps

**Chain-grade (hybrid-ready)**:
- char_trigram_encoder (encode) — CERT 585 n8
- KGStore (Hebbian binding + retrieval) — CERT 584/585/588
- multi_hop (reasoning) — chain-grade primitive
- SubstrateGenerator (generation) — CERT 587 g1b
- SequenceMatrix (sequence memory) — CERT 586 c3
- phase-action portability (LLM-class operating point) — CERT 589/590

**Gaps for hybrid**:
- **Relational-distributional encoder** (Path A semantic layer; "cat ~ dog" from co-occurrence) — NEW; drill in flight 2026-06-22 (research spawn abf8f21c1d09d8d97)
- **Direct-text-as-substrate-triples ingest at scale** (Path A pseudo-LM) — would compose existing primitives but never run at 50M+ scale. Gated on substrate_as_llm_scaling cell verdict (running on GPU now).
- **Entity-sequence → English text rendering** — currently substrate generates `entity → entity → entity` chains. Hybrid would render these as words. Two architectural options:
  - **(a) Word-level co-occurrence layer**: word transitions stored as Hebbian bindings, walk to render
  - **(b) Template-bound relational phrases**: each (subject, relation, object) → known phrase template
  - **(c) Substrate-native text-rendering primitive**: TBD design
- **Capacity at hybrid scale** — Path A 50M+ word-transitions + Path B 10M+ KG triples = 60M+ total Hebbian bindings in one matrix. Scaling cell tests 1M; hybrid needs ~60-100× that.

## Active work alignment

**Cells in flight that compose toward hybrid**:
- substrate_as_llm_scaling_million_facts_v1 (GPU) — validates storage config for both paths
- v2d substrate-self-map (CPU) — Phase 1 of substrate clustering its OWN atoms (will cover both LM and KG atoms)
- r2d bidirectional W (CPU pending) — closes multi-hop chain-grade-promotion (Path B reasoning)
- c2-v2 cascade-STC-SWR (CPU pending) — continual learning so substrate accumulates from chat (works for both paths)
- n5-v2 V_C=4096 frontier (CPU pending) — Path A decode-side closure (bigram-gap revival)
- substrate-native relational-semantic-encoding drill (research spawn) — designs the new primitive Path A needs

**Next-cell candidates after current pipeline lands**:
- `path_a_text_as_substrate_triples_v1` — direct text8 ingest as (word_t, NEXT, word_t+1) Hebbian bindings; tests pseudo-LM viability at substrate scale
- Whatever the relational-semantic-encoding drill produces (drill in flight)
- `hybrid_qa_v1` — QA cell that COMBINES Path B retrieval + Path A generation in one pipeline

## Strategic implications

1. **The L2 MVP frontier** (substrate beats word-bigram on text8) is the Path A milestone. Currently stuck at bigram-gap (4.96 vs 3.84 BPC). The relational-semantic-encoding drill aims AT this bottleneck.

2. **The L3 capability tier** (multi-hop reasoning, continual learning, KG portfolio) IS the Path B milestone. ChainGrade portfolio already strong.

3. **The TRULY unique frontier** is L3-extended: substrate-as-LLM-substitute that BOTH retrieves grounded facts AND generates fluent English. This requires the hybrid. None of Tier-1 — Tier-5 (per prior tier-map) is JUST Path A or JUST Path B; the interesting tiers are inherently hybrid.

4. **Phase 1 → 2 → 3 substrate self-improvement** (USER strategic vision) operates over BOTH paths' atoms uniformly. Autoatom can propose linguistic patterns AND factual patterns alike.

## What this document changes about current direction

- **Stops binary framing**: Path A vs Path B was a false dichotomy. They share primitives + matrix; should be developed in parallel + composed.
- **Adds new spawn**: the relational-semantic-encoding drill (just spawned 2026-06-22) is the load-bearing missing piece. Output will inform what Path A primitive ships next.
- **Re-frames substrate_as_llm_scaling**: not just a Path A capacity test — it validates the storage config for the HYBRID end-state.

— Director (strategic spec; aligns all in-flight + future work toward hybrid end-state per USER directive 2026-06-22)
