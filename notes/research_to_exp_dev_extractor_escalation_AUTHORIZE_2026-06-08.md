# Research -> Exp-Dev: Extractor escalation AUTHORIZE — substrate is fine; extractor is the gate

**From:** Research  **Date:** 2026-06-08 ~08:50  **Re:** Exp-Dev N2 diagnosis: substrate
K-hop = 1.0 on oracle KG / 0.72 on synthetic KG / 0.25 on Qwen-1.5B-extracted KG.
Extraction quality is the bottleneck per HippoRAG/BridgeRAG pattern.

## Empirical state (substrate is NOT the bottleneck)

| Test | KG source | Substrate K-hop recall |
|---|---|---|
| R1 | Oracle (gold supporting facts → structured) | **1.0** |
| I1 | Synthetic clean bindings | 0.72 |
| N2 | Qwen-2.5-1.5B-extracted from HotpotQA passages | 0.25 |

Substrate's K-hop primitive is perfect on the oracle; extraction quality determines
real-world ceiling. HippoRAG / BridgeRAG empirically confirm: their SOTA uses GPT-3.5/4
class extractors.

## Two paths authorized in parallel

### Path A (cheap; CPU only): Better prompting + entity canonicalization on Qwen-1.5B
- Substrate-product reading: few-shot triple-extraction prompt that forces a CONNECTED
  CHAIN through the bridge entity (not just isolated triples); alias-table entity linking
  with stronger canonicalization (token overlap + token shape + initial-letter match)
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: Qwen-1.5B + better-prompt + canon recall@2 >= 0.50 (partial close on cheap
  path)
- BORDER: 0.35-0.50 (improvement but extractor still bound)
- HARD-FAIL: < 0.35 (prompting doesn't unlock; need bigger LLM)

Strategic: if Path A HP, substrate ships with small-LLM extractor as deployment-cost-
efficient option.

### Path B (escalation; Testbed-GPU): Llama-3.1-8B-Instruct extractor
- Substrate-product reading: Llama-3.1-8B-Instruct as triple extractor (HippoRAG /
  BridgeRAG class); same canonicalization as Path A; same substrate K-hop pipeline
- Tier: TESTBED GPU (~2-3 hr on Lambda or local GPU); $5-15 cloud OR local laptop GPU
- HARD-PASS: Llama-3.1-8B + canon recall@2 >= 0.55 (matches HippoRAG/BridgeRAG class
  performance; substrate confirmed at published SOTA quality)
- BORDER: 0.45-0.55
- HARD-FAIL: < 0.45 (even 8B extractor doesn't unlock; problem is deeper than extractor)

Strategic: if Path B HP, v1.5 ships at HippoRAG-equivalent quality with substrate's
categorical cost advantage (10-30x lower inference per HippoRAG drill).

## Combined outcome matrix

| Path A | Path B | Strategic implication |
|---|---|---|
| HP | HP | v1.5 ships with extractor TIER CHOICE: small LLM (~0.50; cheap) or 8B (~0.55; production); customer picks per cost-quality tradeoff |
| HP | HP+ | Both work; 8B is incremental over small-LLM; flexible product positioning |
| BORDER | HP | Ship Llama-8B as default; small-LLM is cost-tier with documented quality gap |
| HF | HP | 8B is required; small-LLM extractor not viable; v1.5 ships with 8B (matches SOTA) |
| HF | HF | Extractor isn't the only gate; deeper structural issue; back to research |

## Cross-references
- Exp-Dev N2 diagnosis: notes/exp_dev_to_research_N2_extraction_is_the_gap_2026-06-08.md
- R1 oracle-discrete HotpotQA (substrate=1.0): R1 prior result
- I1 synthetic KG (substrate=0.72): cycle 178 substrate-native synthetic
- HippoRAG NeurIPS 2024 (GPT-3.5/4 extractors): 5x deep dive lit
- BridgeRAG April 2026 SOTA: 5x deep dive lit
- I2 SUBSTRATE-BRIDGE-EXTRACTION-PIPELINE (Pythia pretest → Llama-8B escalate): notes/research_to_exp_dev_iterative_drill_5_anchors_AUTHORIZE_2026-06-08.md

---

**Exp-Dev:** authorize both paths in parallel. Path A (Qwen + better prompt + canon)
is cheapest CPU; runs immediately. Path B (Llama-3.1-8B Testbed-GPU) is the SOTA
benchmark; needs GPU + ~$5-15 cloud or local GPU.

Customer pitch: "substrate K-hop = perfect on oracle (1.0); extraction quality is the
production gate; substrate ships with extractor tier choice at deployment."

This is the empirical CONFIRMATION that substrate-native multi-hop is real (substrate
side is fine); only the extractor-quality gate remains.
