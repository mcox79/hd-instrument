# Research -> Exp-Dev: N1c + N1d + N1e alternatives test AUTHORIZE

**From:** Research  **Date:** 2026-06-08 ~03:45  **Re:** User authorized 3 test anchor
additions to fill alternative-mechanism coverage gaps.

## Gap 1 filled — single-shot + LLM attention on NATIVE substrate

### Anchor N1c: single-shot + LLM attention on structured-triple substrate
- Substrate-product reading: same NER+relation extraction ingest as N1; at query time,
  retrieve top-k STRUCTURED BINDINGS (not paragraphs); LLM gets question + top-k
  structured triples as context; LLM attention spans across triples; measure recall@2 + F1
- Tier: LOCAL CPU (~2 hr)
- HARD-PASS: native-substrate single-shot + attention recall@2 >= PP-99's 0.501 AND
  matches RAG within 2pp (proves structure helps LLM attention OR at least doesn't hurt)
- BORDER: 0.40-0.50 (structure helps less than expected; matches fuzzy single-shot)
- HARD-FAIL: < 0.40 (structured triples are HARDER for LLM attention to reason over
  than fuzzy passages; counter-intuitive)

Strategic: tests whether substrate's structuring is COMPATIBLE with single-shot+attention
pattern (transformers' production multi-hop). If HP, substrate ships both regimes
together; if HF, two distinct deployment patterns.

## Gap 2 filled — parallel sub-question decomposition

### Anchor N1d: parallel sub-question decomposition on NATIVE substrate
- Substrate-product reading: small LLM (Pythia-160M or Qwen-1.5B) generates K=3 parallel
  sub-questions from the original question; all K queried against substrate (structured
  triples) in parallel; results fused by LLM into final answer
- Tier: LOCAL CPU (~2-3 hr); requires Pythia-160M or constrained-generation LLM
- HARD-PASS: parallel sub-question + native substrate recall@2 >= 0.55 (alternative
  decomposition mechanism validated)
- HARD-FAIL: < 0.45 (parallel decomp doesn't help; iterative-reformulation lossiness
  extends to parallel decomp)

### Anchor N1e: parallel sub-question decomposition on NON-NATIVE (fuzzy) substrate
- Substrate-product reading: same parallel-decomp as N1d but against fuzzy bge-small
  substrate (no structured triples); tests if parallel decomp rescues fuzzy regime
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: parallel sub-question + fuzzy substrate recall@2 >= 0.55 (parallel rescues
  fuzzy regime; alternative to single-shot+attention)
- HARD-FAIL: < 0.45 (parallel decomp on fuzzy also fails; confirms fuzzy regime is
  bottleneck regardless of decomposition strategy)

Strategic: N1d/N1e together test whether parallel decomp is decomposition-pattern or
regime-pattern; orthogonal axis from iterative-vs-single-shot debate.

## Combined outcome interpretation

| N1c | N1d | N1e | Strategic implication |
|---|---|---|---|
| HP | HP | HF | Native substrate compatible with both single-shot+attention AND parallel decomp; product offers either at deployment |
| HP | HP | HP | Parallel decomp works regardless of regime; substrate-agnostic mechanism; product simplifies |
| HF | HP | HF | Native substrate needs parallel decomp not single-shot+attention; routing matters |
| HF | HF | HF | Only single-shot+attention works (PP-99 only path); native substrate ships only for KG QA |
| HP | HF | HF | Native + single-shot+attention is the path; parallel decomp dead like iterative |

## Cross-references

- iterative_regime_crossover HP (universal principle): notes/exp_dev_to_research_universal_principle_reproduced_2026-06-08.md
- Cycle 178 PP-99 single-shot+attention: notes/orchestrator_to_research_results_summary_2026-06-08_cycle178.md
- N1-N3 / R1-R3 original battery: notes/research_to_exp_dev_NATIVE_substrate_multihop_HotpotQA_2026-06-07.md
- N1b + T5-1 additions: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md
- I1-I5 drill anchors: notes/research_to_exp_dev_iterative_drill_5_anchors_AUTHORIZE_2026-06-08.md

---

**Exp-Dev:** authorize all 3 additions per user. N1c is cheapest + most strategic (tests
if structure helps LLM attention reader). N1d / N1e test untested parallel-decomp
alternative. ~6-8 hr CPU total. Combined with HYBRID-ARCHITECTURE 5x drill (just
dispatched, ~30-40 min), this closes the alternative-mechanism coverage gap.

Sequencing: N1c first (cheapest; resolves architectural question quickest); then N1d
(parallel decomp); then N1e (regime ablation). Pythia-160M sanity-check before any
Qwen-1.5B escalation for parallel decomp.
