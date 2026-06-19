# Research -> Exp-Dev: BATCH ROUTING — hierarchical + substrate-only LM + Tier 5c arch + cycle 195 follow-ups

**From:** Research  **Date:** 2026-06-09 ~01:30 UTC
**Re:** User direction "route them." Consolidating in-flight drill anchors + cycle 195 follow-ups.

## A. SUBSTRATE-FIRST HIERARCHICAL anchors (per user "substrate handles simple; LLM handles complex" architecture)

### A1: Substrate intent classifier (distill from Qwen-2.5-3B teacher)
- Substrate-product reading: small BERT-class classifier (~100M params; <5ms) categorizes queries (lookup/count/comparison/multi-hop/creative); distilled from LLM-ROUTING-T1 teacher
- Tier: LOCAL GPU
- HARD-PASS: 0.78+ accuracy from 0.833 teacher; <5ms latency

### A2: Substrate templated response for common query categories
- Substrate-product reading: for top 10 query categories, substrate retrieves + applies template; no LLM call
- Tier: LOCAL CPU
- HARD-PASS: templated response factually correct + grammatically acceptable on 100-query test set ≥ 0.90

### A3: PII strip-and-inject HIPAA pattern
- Substrate-product reading: substrate detects PII via named-entity bindings; placeholder substitution; LLM processes sanitized; substrate re-injects PII into result
- Tier: LOCAL CPU
- HARD-PASS: 100% PII removal pre-LLM + 100% accurate re-injection post-LLM; end-to-end factually correct ≥ 0.95

### A4: Hierarchical routing accuracy at scale
- Substrate-product reading: end-to-end substrate-first routing on diverse 500-query benchmark; measure substrate-handled vs LLM-handed-off vs abstain
- Tier: LOCAL CPU
- HARD-PASS: 65%+ substrate-handled (correct + faster than LLM baseline) + <5% wrong-routing

### A5: Cost/latency benchmark substrate-first vs LLM-first
- Substrate-product reading: 1000-query workload; measure total API cost + median latency for substrate-first vs gpt-4o-mini-only baseline
- Tier: LOCAL CPU
- HARD-PASS: ≥ 50% API cost reduction + ≥ 5x median latency reduction

## B. SUBSTRATE-ONLY LM anchors (per user "can substrate understand language?")

### B1: Substrate codebook on word2vec/BERT compression
- Substrate-product reading: train substrate codebook (VQ-VAE-style) on pretrained word embeddings; measure semantic similarity preservation
- Tier: LOCAL CPU
- HARD-PASS: substrate-projected embeddings retain ≥ 0.85 cosine similarity vs original on STS-B; ≥ 0.7 on intrinsic word similarity benchmarks

### B2: Substrate-only TinyStories LM (rung-1 scale)
- Substrate-product reading: substrate-attention all layers; train on TinyStories corpus; measure next-token prediction
- Tier: LOCAL GPU
- HARD-PASS: substrate-only LM perplexity within 5x of small-transformer baseline; coherent 50-token generations
- BORDER: within 10x perplexity (PoC acceptable for research positioning)

### B3: Substrate distillation from Qwen-1.5B-Instruct
- Substrate-product reading: distill Qwen-1.5B language behavior into substrate codebook + ops; teacher-student
- Tier: LOCAL GPU
- HARD-PASS: distilled substrate LM matches teacher next-token prediction within 10% on held-out

### B4: Substrate-attention all-layer Pythia-160M (LARS-VSA replica)
- Substrate-product reading: replace ALL Pythia-160M attention with substrate-attention; continued pretrain
- Tier: LOCAL GPU
- HARD-PASS: modified Pythia-160M perplexity within 5x of baseline + substrate retrievals demonstrably used per token

### B5: Substrate-LLM joint pretraining smoke test
- Substrate-product reading: substrate + small LLM trained jointly; substrate codebook evolves with LLM weights
- Tier: LOCAL GPU
- HARD-PASS: joint training stable (no codebook collapse); perplexity competitive with substrate-frozen baseline

## C. TIER 5C ARCH anchors (from architecture/speed/routing drill)

### C1: Substrate-orchestrator routing benchmark CPU
- Substrate-product reading: substrate decomposes queries into tool calls via Datalog^neg; LLM invoked once at end for formatting; comparison vs ReAct baseline
- Tier: LOCAL CPU
- HARD-PASS: substrate-orchestrator beats ReAct on multi-hop factual queries at ≥ 50% lower latency

### C2: GPU codebook retrieval benchmark (gates GPU Tier 5c)
- Substrate-product reading: substrate codebook resident on GPU; retrieval via cuBLAS matmul; measure per-lookup latency
- Tier: LOCAL GPU
- HARD-PASS: <0.1ms per-lookup at 100K-fact codebook (P95)

### C3: Lightweight router distillation from Qwen-2.5-3B
- Substrate-product reading: 100M-param classifier distilled from Qwen-2.5-3B routing teacher; <5ms decision
- Tier: LOCAL GPU
- HARD-PASS: ≥ 0.78 accuracy (vs teacher 0.833); <5ms latency; 10-500x routing speedup vs LLM

### C4: Semantic positional encoding probe (Pythia-160M)
- Substrate-product reading: replace Pythia RoPE with substrate-derived semantic positional encoding; measure perplexity + downstream tasks
- Tier: LOCAL GPU
- HARD-PASS: perplexity within 20% of baseline + substrate-positional shows position-aware retrieval

### C5: Substrate-conditioned softmax hallucination probe (TriviaQA)
- Substrate-product reading: substrate atom-vocabulary distributions bias LLM output logits at generation; measure hallucination reduction
- Tier: LOCAL GPU
- HARD-PASS: ≥ 30% hallucination reduction vs unconditioned baseline on TriviaQA

## D. CYCLE 195 FOLLOW-UPS

### D1: PP-181 gap-score multi-seed promotion (MID→HP gate)
- Substrate-product reading: cycle 195 PP-181 MID-HP at AUC=0.781 single-seed; 3-seed averaging should clear VALIDATED threshold
- Tier: LOCAL CPU
- HARD-PASS: 3-seed mean AUC ≥ 0.80 + variance < 0.02

### D2: PP-155 per-strength-level sharding (new rescue axis after N-scaling stalled)
- Substrate-product reading: PP-127 universal sharding pattern applied to continuous-strength; shard by strength tier
- Tier: LOCAL CPU
- HARD-PASS: strongest-wins ≥ 0.95 per shard; cross-shard fusion ≥ 0.93

## Recommended sequencing

**Day 1 (cheapest CPU; highest leverage):**
- D1 (PP-181 multi-seed) + D2 (PP-155 sharding rescue) — close out cycle 195 MID
- A3 (PII strip-and-inject) — HIPAA categorical capability
- B1 (substrate codebook on word2vec/BERT) — substrate-LM foundation
- C1 (substrate-orchestrator routing CPU) — Tier 5c arch first gate

**Day 2 (medium CPU/GPU):**
- A1 (intent classifier) + A2 (templated responses) — hierarchical foundation
- C3 (lightweight router distillation) — routing speedup gate
- A4 (hierarchical routing accuracy)

**Day 3 (heavier GPU):**
- A5 (cost/latency benchmark)
- B2 (substrate-only TinyStories LM)
- C2 (GPU codebook retrieval)

**Day 4-5 (R&D):**
- B3/B4/B5 (substrate-LM training paths)
- C4/C5 (semantic pos encoding + conditioned softmax)

## Strategic context

**Substrate cycle 195 just empirically validated my consolidated batch** — 3-layer confidence stack LOCKED (PP-180 contradiction + PP-182 tiered + PP-183 factual AUC=1.0000). This is the EU AI Act Article 12 primary technical backing. 8-week window.

**Architectural framing now sharpest yet:** substrate as System 1 (fast/intuitive/algebraic; 70% of queries); LLM as System 2 (deliberate/creative/conversational; 30%). Biology analog: cerebellum/basal ganglia vs PFC. Empirically grounded for v1 demo.

**Substrate-only LM path is research-grade exploration** — LARS-VSA + GHRR-Transformer are existence proofs; substrate's FHRR has Wirtinger-differentiability structural advantage. Not v1 demo; v2.0+/research positioning.

## Cross-references
- Cycle 195 results: notes/orchestrator_to_research_results_summary_2026-06-08_cycle195.md
- 8 drills consolidated batch: notes/research_to_exp_dev_8_DRILLS_CONSOLIDATED_BATCH_2026-06-08.md
- Substrate-first hierarchical drill (in flight): notes/research_drill_substrate_first_hierarchical_5x_2026-06-08.md (when lands)
- Substrate-only LM drill (in flight): notes/research_drill_substrate_only_language_model_5x_2026-06-08.md (when lands)
- Tier 5c arch/speed/routing drill: notes/research_drill_tier5c_architecture_speed_routing_5x_2026-06-08.md

---

**Exp-Dev:** ~17 new anchors filed across 4 priority groups. Sequencing recommendation
prioritizes cheapest CPU + highest categorical capability gain. D1+D2 close out cycle 195
MIDs. A3 PII strip-and-inject is highest-categorical-leverage for HIPAA pitch.
Substrate-only LM (B series) is research/v2.0+ exploration.

When in-flight drills land, additional anchor refinements may follow.
