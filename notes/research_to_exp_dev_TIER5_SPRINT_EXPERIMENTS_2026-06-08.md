# Research -> Exp-Dev: TIER 5 SPRINT experiments AUTHORIZE

**From:** Research  **Date:** 2026-06-08 ~19:45 UTC
**Re:** Tier 5 SPRINT SPEC just filed; user "begin routing now." Concise batch.

## Panel A (Tier 5a substrate-KV production) — empirical extensions

### T5a-S1: Substrate-KV at M=50000 (capacity ceiling probe)
- Tier: LOCAL GPU
- HARD-PASS: recall@1 >= 0.95 at M=50000 (probe ceiling beyond M=10000 cycle 191 HP)

### T5a-S2: Substrate-KV at M=100000 (production scale)
- Tier: LOCAL GPU
- HARD-PASS: recall@1 >= 0.90 at M=100000

### T5a-S3: Llama-3.1-8B substrate-KV (third LLM family validation)
- Tier: LOCAL GPU 4-bit quant
- HARD-PASS: recall@1 >= 0.95 at M=2000 with Llama-3.1-8B encoder
- Strategic: confirms substrate-KV across Pythia + Qwen + Llama families

### T5a-S4: Substrate-KV with 200M-fact backing KB (end-to-end production test)
- Tier: LOCAL GPU
- HARD-PASS: end-to-end query (user query -> substrate retrieval over 200M -> LLM answer) <2s; correct facts retrieved

## Panel B (Tier 5b substrate-attention-layer PoC) — novel engineering

### T5b-1: Pythia-160M layer 6 attention substitution scaffold
- Substrate-product reading: modify Pythia-160M layer 6 attention forward; substitute K/V with substrate-retrieval-derived vectors; projection layer (substrate N=8192 -> Pythia hidden 768); confirm forward pass produces output
- Tier: LOCAL GPU
- HARD-PASS: modified Pythia-160M produces non-NaN output on simple prompts; substrate retrievals logged per token
- HARD-FAIL: catastrophic shape mismatches or attention diverges

### T5b-2: Substrate-attention layer perplexity baseline
- Substrate-product reading: WikiText perplexity comparison: bare Pythia-160M vs substrate-attention-modified Pythia-160M
- Tier: LOCAL GPU
- HARD-PASS: modified perplexity within 5x of baseline (PoC quality acceptable; categorical demonstration matters)
- BORDER: within 10x (still PoC-acceptable; demo positions as research)

### T5b-3: Substrate-attention generation quality on demo queries
- Substrate-product reading: 30 demo questions; bare Pythia-160M vs substrate-attention-modified Pythia-160M; qualitative assessment of generated text
- Tier: LOCAL GPU
- HARD-PASS: modified version visibly uses substrate facts in >= 50% of demo queries; output coherent enough to read

### T5b-4: Pythia-1.4B fallback substrate-attention (if T5b-1 too rough at 160M)
- Substrate-product reading: same as T5b-1/2/3 but Pythia-1.4B (larger; more coherent)
- Tier: LOCAL GPU
- HARD-PASS: same gates as T5b-1/2/3 but with Pythia-1.4B

## KB ingestion (200M-fact target; shared by both panels)

### KB-1: Wikidata full ingest (~100M triples)
- Tier: LOCAL CPU/GPU
- HARD-PASS: 100M triples ingested; sample recall@1 >= 0.95

### KB-2: ConceptNet ingest (~8M assertions)
- Tier: LOCAL CPU
- HARD-PASS: 8M assertions ingested

### KB-3: Wikipedia 5.84M ingest (already in flight per cycle 190)
- Status: 100k HP cycle 190; 1M running per cycle 191
- HARD-PASS: 5.84M articles ingested

### KB-4: arXiv abstracts (~2M papers)
- Tier: LOCAL CPU
- HARD-PASS: 2M abstracts -> ~10M facts ingested

### KB-5: PubMed abstracts (~30M)
- Tier: LOCAL CPU
- HARD-PASS: 30M abstracts ingested

## Recommended sequencing

1. T5a-S1 + T5a-S2 (capacity ladder; cheap GPU; validates production scale)
2. KB-1 Wikidata (primary KB; structured triples; no extraction needed)
3. T5b-1 Pythia-160M scaffold (engineering kickoff; cheap iteration)
4. KB-2 ConceptNet (cheap; common-sense base)
5. T5b-2 perplexity baseline (gate for T5b-3 demo quality)
6. T5a-S3 Llama-3.1-8B (validation; broader claim)
7. T5b-3 demo query quality (decisive for Panel B feasibility)
8. KB-4 arXiv (background)
9. KB-5 PubMed (background; biggest)
10. T5a-S4 end-to-end with 200M KB (Panel A integration test)

## Cross-references
- Tier 5 SPRINT SPEC: notes/research_to_testbed_TIER5_SPRINT_SPEC_2026-06-08.md
- Tier 5 D1/D2/D3 empirical: cycles 185 + 190 + 191
- Pythia-160M substrate-KV (D1): cycle 185

---

**Exp-Dev:** authorize all; sequence per above. Panel A (Tier 5a) anchors validate
production-scale claims. Panel B (Tier 5b) anchors prove substrate-as-attention is
feasible. KB ingestion runs in parallel.

User flag: I'm at context limit; prepping for compaction. Continue execution per
sequence; results synthesize when context returns.
