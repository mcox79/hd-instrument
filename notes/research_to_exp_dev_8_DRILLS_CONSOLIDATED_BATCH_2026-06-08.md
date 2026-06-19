# Research -> Exp-Dev: 8 capability drills CONSOLIDATED priority batch

**From:** Research  **Date:** 2026-06-09 ~00:30 UTC
**Re:** 8 capability drills all landed today. ~40 anchor candidates across handoffs.
Consolidated priority batch + sequencing.

## Cheap-decisive anchors FIRST (CPU; <2hr each; gate higher-effort work)

### CHEAP-1: Biology contradiction-detection layer (1-week scope; HIGHEST leverage)
- Source: biology drill (Anchor A)
- Substrate-product reading: ACC-style pre-output conflict detection (Botvinick 2001 ACC conflict monitoring; top-1 vs top-2 contradiction check)
- Uses EXISTING top-k similarity; no new mechanisms
- Directly addresses hallucination detection (the highest-probability demo message destroyer)
- HARD-PASS: contradiction detection on 200-item KB >= 90% recall + < 2% FP

### CHEAP-2: Gap-score probabilistic capability upgrade
- Source: biology drill + probabilistic drill consensus
- Substrate-product reading: add gap-score (top-1 minus top-2 similarity) as second-order uncertainty signal
- Maps to neural population code width (Ma 2006)
- Cheap engineering; categorical addition
- HARD-PASS: gap-score correlates with answer correctness (Spearman > 0.7)

### CHEAP-3: PP-107 confidence as probabilistic population code analog
- Source: biology drill cheap decisive test
- Substrate-product reading: 200-item KB graded cosine similarity tiers (0.60-1.00); query under noise; measure Spearman PP-107 vs tier monotonicity
- 30 min CPU
- HARD-PASS: rho > 0.85 + graceful degradation under noise

### CHEAP-4: Substrate cosine factual confidence (verification drill anchor 1)
- Source: verification drill
- Substrate-product reading: PP-107 confidence as factual-correctness predictor at sentence level
- 1-2 hr CPU
- HARD-PASS: confidence score AUC >= 0.9 on factual vs hallucinated claims

### CHEAP-5: PAL-bridge with substrate cache (math drill anchor A)
- Source: math drill
- Substrate-product reading: substrate makes PAL non-amnesic; cache hit rate on GSM8K test set
- HARD-PASS: substrate cache hit rate >= 20% at evaluation; PAL cost reduced

## Production-claim gates (CPU/local GPU; longer runtime)

### GATE-1: PP-155 N=32768 HP rescue (CRITICAL PATH for probabilistic claim)
- Source: probabilistic drill flagged as gate
- Substrate-product reading: continuous-strength MID at N=8192/16384; HP target at N=32768
- HARD-PASS: strongest-wins >= 0.95 at N=32768

### GATE-2: Substrate Merkle audit completeness (verification drill anchor 3)
- Source: verification drill
- Substrate-product reading: Merkle chain coverage for EU AI Act Article 12; 8-week deadline
- HARD-PASS: 100% audit chain completeness on 1000-query benchmark

### GATE-3: Conformal coverage using substrate retrieval score (novel; verification drill)
- Source: verification drill (P_deflated=0.40 novel; no precedent)
- Substrate-product reading: conformal non-conformity measure via substrate score (vs ConU/TECP token entropy)
- HARD-PASS: distribution-free coverage guarantee at alpha=0.1

## Capability-domain anchors (new capability claims)

### CAP-1: Substrate as STRIPS forward-chaining (planning drill SUBSTRATE-KG-PLANNING-GATE)
- 30-min CPU; real-KG 2-hop recall
- HARD-PASS: 2-hop recall >= 0.85

### CAP-2: Substrate as SAT solver (constraint-theorem drill anchor)
- N-queens / Sudoku constraints via substrate cleanup
- HARD-PASS: 8-queens solved with substrate algebra

### CAP-3: Substrate as theorem-dependency memory (math drill anchor B)
- 50 mathlib theorems / 1hr / $0 cheap decisive test
- HARD-PASS: dependency K-hop traversal >= 0.9 recall

### CAP-4: Substrate counterfactual axiom queries (math drill anchor C)
- do() on group axioms; "what theorems hold if commutativity dropped?"
- Direct test of PP-172 in math domain
- HARD-PASS: 80% of derivable theorems correctly excluded

### CAP-5: CLIP multimodal substrate (multimodal drill + roadmap)
- FPE continuous encoding pre-test (30 min CPU)
- HARD-PASS: cross-modal retrieval recall@5 >= 0.7

### CAP-6: Bipolar quantization quality at N=65k (multimodal drill decisive gate)
- Substrate-product reading: literature predicts substrate at higher N exceeds published 1-bit benchmarks at N=768 by JL arguments
- HARD-PASS: recall match @ N=65k bipolar vs floating-point baseline

### CAP-7: Tabular ingest with substrate algebraic SQL (multimodal drill + HDDB 80.6x precedent)
- Substrate-product reading: Excel/CSV rows as substrate triples; SUM/COUNT/AVG via PP-159+extensions
- HARD-PASS: SQL-equivalent queries on TPC-H scaled subset; correctness 100%

## v2.0+ R&D anchors (multi-step engineering; not v1)

### R&D-1: Tier 5c differentiability probe (CPU 20-30 min; gate for all Tier 5c GPU work)
- Already in queue

### R&D-2: Flamingo proper training (GPU-days; T5b proper scope per HARD_PROBLEM finding)
- Full gated cross-attention; multi-layer insert; held-out fact-transmission eval

### R&D-3: Tier 5c surgical modification of pretrained frontier LLM
- Surgical attention-layer replacement on Qwen-2.5-7B or Llama-3.1-8B
- Continued pretraining recovers/preserves conversational quality

### R&D-4: Substrate self-reflection API (roadmap drill)
- Substrate introspection of own state
- Categorical capability LLMs cannot match

### R&D-5: Substrate forking / merging (roadmap drill)
- Knowledge lifecycle management

## Demo-supporting anchors (already in flight or queued; reminders)

- f1 substrate-KV M=50k (capacity ceiling probe)
- t5a_s2 substrate-KV M=100k (production scale)
- substrate_vs_iterative_knnlm (moat hardening vs multi-step RAG)
- legal_citation_snowball sharded full run
- bge-large encoder swap for Panel A
- Wikipedia 100K ingest (after encoder swap)
- spaCy NER → K-hop viz endpoint

## Recommended sequencing

**Day 1 (cheap-decisive sprint):**
- CHEAP-1 (biology contradiction detection)
- CHEAP-2 (gap-score addition)
- CHEAP-3 (PP-107 population code test)
- CHEAP-5 (PAL-bridge)
- Demo-supporting GPU queue (4 new anchors per queue state)

**Day 2 (production gates):**
- GATE-1 (PP-155 N=32768)
- GATE-2 (Merkle audit completeness)
- CAP-1 (planning gate)
- CAP-3 (mathlib K-hop)

**Day 3-5 (capability claim anchors):**
- CAP-2/4/5/6/7 in priority order
- GATE-3 (conformal coverage; speculative novel)

**Week 2+ R&D track:**
- R&D-1 (Tier 5c probe; cheapest gate first)
- R&D-2 (Flamingo proper training)
- R&D-3 (Tier 5c surgical modification)

## Cross-references
- 8 capability drill handoffs (all in notes/):
  - math_capabilities_5x
  - probabilistic_reasoning_5x
  - verification_hallucination_2x (or substrate_verification_2x)
  - planning_open_ended_2x
  - capability_roadmap_5x
  - multimodal_2x
  - constraint_theorem_2x
  - biology_capabilities_5x
- Queue state: notes/exp_dev_to_research_queue_state_for_optimization_2026-06-08.md
- LLM-ROUTING-T1 HARD_PASS: notes/exp_dev_to_research_routing_t1_HARDPASS_2026-06-08.md

---

**Exp-Dev:** consolidated batch. ~25 anchors across cheap-decisive, production-gates,
capability-domain, R&D, demo-supporting. Sequencing recommendation above. You design
actual anchor structure; Research provides strategic priority.

CHEAP-1 (biology contradiction detection layer; 1-week scope; 90% recall / 2% FP HARD-PASS;
maps to Botvinick 2001 ACC) is HIGHEST-LEVERAGE single anchor — direct hallucination
detection addressing highest-probability demo message destroyer.

CHEAP-2 (gap-score addition) is cheapest categorical upgrade (probabilistic population
code analog; biology drill flagged "cheap to add").
