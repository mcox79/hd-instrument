# Exp-Dev -> Research: N2 (LLM-triples K-hop) -- substrate is fine, EXTRACTION QUALITY is the gap

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** N2 / I2 substrate_llm_triples_khop (HIGHEST)

Built N2: Qwen-2.5-1.5B-Instruct extracts (s|r|o) triples from HotpotQA gold passages -> discrete FHRR KG -> substrate K-hop.
Smoke (n=8): answer-recall=0.25, extraction-coverage=0.75.
  - Coverage 0.75: Qwen DOES extract the answer entity as a KG node 75pct of the time.
  - Recall 0.25: but the K-hop from the question entity reaches the answer only ~25pct -- the extracted KG is NOT TRAVERSABLE.
  - Entity-resolution rescue (canonicalize entities by shared content-token + token-overlap start match) lifted recall
    0.125 -> 0.25, confirming resolution is PART of the gap, but not the whole gap.

Diagnosis (honest): the substrate K-hop is not the bottleneck -- R1 (oracle-structured, same data) = recall@1 1.0; I1
(synthetic KG) = 0.72. The bottleneck is EXTRACTION QUALITY: Qwen-1.5B extracts entities but not the connected relational
chain (the bridge link across the two passages is missing/inconsistent), so the 2-hop path doesn't exist in the KG. This is
exactly the note's anticipated "escalate to a stronger extractor."

Recommendation (pick one, both need provisioning):
  1. Stronger extractor: Llama-3.1-8B-Instruct triple extraction (Testbed-GPU) -- likely the real lever per HippoRAG/BridgeRAG
     (they use GPT-3.5/4-class extractors). Re-run N2 with the same substrate K-hop.
  2. Better extraction prompt + canonicalization: few-shot triple-extraction prompt that forces a connected chain through the
     bridge entity + stronger entity-linking (alias table). Cheaper, may partially close the gap on Qwen-1.5B.
The full N2 run (n=60) is queued for the record; expect HARD_FAIL/MID with the same diagnosis.
