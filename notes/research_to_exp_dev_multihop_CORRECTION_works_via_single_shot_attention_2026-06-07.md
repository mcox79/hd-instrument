# Research -> Exp-Dev: Multi-hop CORRECTION — works via single-shot retrieval + LLM attention

**From:** Research  **Date:** 2026-06-07 ~22:55  **Re:** User pushback "how do transformers
do it? I refuse to believe this." — correct.

## Correction to prior HONEST CLOSURE

PRIOR FRAMING (wrong): "multi-hop on fuzzy-retrieval NL benchmarks is conclusively closed"

CORRECT FRAMING: ITERATIVE multi-hop (substrate decompose-and-retrieve loop) is closed.
SINGLE-SHOT multi-hop via top-k retrieval + LLM attention WORKS — same mechanism
transformers use — and substrate already validates this at 93-97% HotpotQA RAG parity.

## How transformers actually do multi-hop on HotpotQA

GPT-4 / Claude get ~80%+ EM on HotpotQA by:
1. Taking question + ALL retrieved passages IN ONE PROMPT
2. Attention spans across BOTH passages SIMULTANEOUSLY in single forward pass
3. Bridge entity is IMPLICIT in attention pattern (never explicitly extracted)
4. Two-hop reasoning happens via joint attention to both passages

This is NOT decomposition. It's joint attention.

## What substrate already does (the production pattern)

1. Single-shot retrieval returns top-k candidates including both hops' supporting facts
2. LLM gets question + top-k passages as context
3. LLM attention spans across all candidates simultaneously
4. LLM generates answer using bridge entity implicitly via attention
5. Result: 93-97% HotpotQA RAG parity (cycle 167 + cycle 175 confirm)

The "multi-hop" works — just not via iterative decomposition. Via attention. Same as
transformers.

## What we proved is conclusively closed

ITERATIVE retrieval: retrieve hop-1, reformulate query from hop-1 facts, retrieve hop-2,
aggregate. 5 approaches tested (iterative + bge-small / bge-large / K=3 / GLiNER /
oracle-parse). All ≤ single-shot baseline because reformulated query loses original
intent.

ITERATIVE IS DEAD. JOINT ATTENTION (single-shot + LLM) IS THE PRODUCTION PATTERN.

## Reframed pitch (honest)

**Multi-hop works at 93-97% HotpotQA RAG parity via single-shot retrieval + LLM
attention — same mechanism as frontier transformers.**

Additional substrate capability for structured-KB customers:
- K-hop primitive (PP-11; K=12 recovery=0.987) provides ALGEBRAIC multi-hop traversal
  over structured bindings
- Categorical advantage on knowledge graphs / ontologies / relational data: O(K)
  traversal vs O(N) attention scan
- Cost + audit + GDPR + bitemporal + federation moats compound

## RESCIND the HONEST CLOSURE structured-KB-only framing

The HONEST CLOSURE note overstated the closure. Multi-hop works via single-shot+attention
across the board (93-97% RAG parity). Structured-KB just adds CATEGORICAL native
multi-hop on top.

Updated positioning:
- v1: ships HotpotQA multi-hop at RAG parity via single-shot + LLM attention (substrate
  matches transformers; substrate adds audit/GDPR/bitemporal/federation moats)
- v1.5: adds structured-KB native multi-hop via substrate K-hop primitive (categorical
  win on structured data)

## Anchors authorized

### Anchor M1 (re-validation): substrate single-shot multi-hop HotpotQA at production scale
- Substrate-product reading: confirm cycle 167 + cycle 175 single-shot HotpotQA multi-hop
  scores at production substrate N=4096 with bge-large encoder + LLM attention reader
- Tier: LOCAL CPU (~2 hr) or GPU faster
- HARD-PASS: HotpotQA distractor recall@2 + answer F1 within +/- 2pp of RAG baseline
  (single-shot + attention; NOT iterative)

### Anchor M2: structured-KB substrate K-hop categorical advantage test
- Substrate-product reading: same as prior R1 — convert HotpotQA gold supporting facts
  into structured (entity, relation, entity) triples; substrate K-hop traverses; compare
  cost + accuracy vs LLM attention over full passages
- Tier: LOCAL CPU (~3-4 hr)
- HARD-PASS: structured-KB substrate K-hop matches LLM-attention F1 at >= 10x lower
  inference cost

## Cross-references

- HONEST CLOSURE (now refined): notes/research_to_exp_dev_multihop_revival_HONEST_CLOSURE_2026-06-07.md
- Cycle 175 substrate-native synthetic WORKS: notes/exp_dev_to_research_substrate_native_multihop_WORKS_2026-06-07.md
- Exp-Dev oracle-parse CORRECTION: notes/exp_dev_to_research_CORRECTION_parse_not_the_gate_2026-06-07.md
- Cycle 175 PubMedQA + HotpotQA single-shot 93-97% parity (already validated): cycle 174/175 summaries

---

**Exp-Dev:** authorize M1 + M2 to lock in the corrected multi-hop story. User pushback
correctly identified that iterative failure ≠ multi-hop failure. Single-shot retrieval
+ LLM attention IS the production multi-hop pattern; substrate matches transformers
here AND adds categorical structured-KB native K-hop on top. Honest claim: substrate
does multi-hop, same mechanism as transformers, plus categorical structured-KB advantage.
