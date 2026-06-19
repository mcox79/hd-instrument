# exp_dev hand-off -- research: substrate competitive landscape 2x

**Filed-by:** research sub-agent
**Date:** 2026-06-09
**Trigger:** Competitive landscape drill (2x depth) completed
**Research note path:** d:/AI/hd-instrument/notes/research_drill_substrate_competitive_landscape_2x_2026-06-09.md

Per [[feedback-no-experiment-design-in-prompts]]: This file names anchor candidates and context pointers only. exp_dev designs all experiment specifics autonomously.

---

## Pause state

Standard pause gate applies. exp_dev checks data/orchestrator_paused.flag before dispatch.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): Independent retrieval benchmark on public dataset

**Anchor pointer:** Retrieval latency + recall validation on a public ANN benchmark dataset (e.g., SIFT-1M, GloVe-1.2M, or equivalent)

**Substrate-product reading:** The competitive analysis confirmed that every substrate retrieval claim (sub-ms p95 at 100M scale) is currently an internal benchmark. No independent validation exists. Qdrant achieves 20ms p95 at 1B vectors; substrate claims sub-ms at 100M. The gap is the key differentiator claim. Without independent benchmark numbers, enterprise procurement and v1 demo comparisons are unsupported.

**Tier hint:** Tier-1 CPU/local (SIFT-1M fits in memory; no GPU needed; ann-benchmarks compatible harness)

**Why now:** This is the cheapest decisive test identified in the research note. It resolves the most load-bearing uncertainty in the competitive positioning in 2-4 hours of engineering time. It directly feeds the v1 demo vs Qdrant head-to-head. Competitor numbers (Qdrant 20ms p95) are public and validated; substrate's numbers are not.

---

### Anchor 2: Multi-hop Datalog vs GraphRAG hallucination head-to-head

**Anchor pointer:** Multi-hop compositional retrieval (Datalog^neg operators) vs GraphRAG on a public multi-hop QA benchmark (e.g., HotpotQA subset or MuSiQue)

**Substrate-product reading:** The competitive analysis found that GraphRAG's LazyGraphRAG + ToG-2 achieve 20-40% hallucination rate on complex multi-hop reasoning chains. Substrate's Datalog^neg compositional operators should reduce this via algebraic (deterministic) composition. The multi-hop revival priority (MEMORY.md: project_multihop_revive_priority) is directly supported by this head-to-head.

**Tier hint:** Tier-2 local GPU (Pythia-1.4B or Llama-1B as LLM backbone; multi-hop KB construction required)

**Why now:** The competitive gap is confirmed by the lit scan. GraphRAG is the SOTA benchmark target. A clean head-to-head on a public dataset (not substrate-internal) generates a publishable comparison artifact and directly tests the North Star claim (functional system beats LLMs of relative size). This is the highest-signal v1 demo candidate.

---

### Anchor 3: Merkle audit chain correctness + tamper-evidence smoke

**Anchor pointer:** PP-184 Merkle audit chain under concurrent write + erasure load; verify tamper-evidence property

**Substrate-product reading:** The competitive analysis confirmed no competitor has cryptographic audit of retrieval-layer erasure. PP-184 is substrate's unique compliance primitive. The HARD-FAIL threshold for this primitive is: Merkle audit chain fails tamper-evidence test under concurrent write load. This needs a concrete empirical test before any compliance positioning claim is made to external parties.

**Tier hint:** Tier-1 local CPU (pure hash computation; no GPU; concurrent write simulation via threading)

**Why now:** EDPB enforcement in 2025-2026 (30 DPAs investigating right to erasure) is the demand-pull that makes this commercially relevant NOW. The compliance positioning is the strongest differentiator claim that no competitor can match architecturally. But it is only defensible if the mechanism has been empirically tested under realistic concurrent load.

---

### Anchor 4: LangChain/LlamaIndex retriever adapter (integration layer)

**Anchor pointer:** Implement a LangChain-compatible retriever adapter wrapping substrate retrieval (BaseRetriever interface) and a LlamaIndex QueryEngine adapter

**Substrate-product reading:** The competitive analysis found that ecosystem gap is the dominant near-term blocking weakness. Every competitor has LangChain/LlamaIndex integration. Without these adapters, substrate cannot be evaluated by any developer using the standard RAG stack. This is not a research question; it is an engineering task that unblocks all downstream evaluation.

**Tier hint:** Tier-0 local CPU (pure Python wrapping; no GPU; no model training)

**Why now:** This is a prerequisite for the multi-hop head-to-head (Anchor 2) and for any external demo. The integration layer is 1-2 days of engineering. The competitive analysis confirms this is the blocking dependency for enterprise evaluation conversations.

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_substrate_competitive_landscape_2x_2026-06-09.md
- Multi-hop revival priority: d:/AI/hd-instrument/memory/project_multihop_revive_priority.md
- North Star: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- Post-compaction brief (exp-dev state): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Production architecture locked: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md

---

## Contract

exp_dev autonomously decides: which anchor(s) to ship, in what order, experiment design details, hyperparameters, smoke gate criteria, and queue placement. This file provides ranked priorities and context only.

## Autonomy declaration

exp_dev may reorder, split, combine, or defer these anchors based on queue state, runner availability, and smoke gate results. The ranking above is research-informed guidance, not a constraint.
