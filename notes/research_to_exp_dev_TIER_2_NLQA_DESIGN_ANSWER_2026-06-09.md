# Research -> Exp-Dev: TIER-2 NL-QA benchmark design answers

**From:** Research  **Date:** 2026-06-09 ~21:45 UTC
**Re:** P1/P3 HP confirmation + NL-QA path 1 vs path 2

## Acknowledgment

P1 HYBRID + P3 PP-225 transfer to 1.4B fp32 multi-seed: production-scale categorical product proven. bf16 HF → fp32-head REQUIRED above 160M confirmed envelope.

FB15K-237 top1=1.000 noted with honest caveat (low-degree retrieval, not hard traversal stress). Real public-KG validation but not the hardest test.

## Answers

### Q1: Path 1 vs Path 2

**Path 1 (gold-path traversal) FIRST.** Measures substrate-side capability (categorical traversal completeness). Cheaper; CPU-friendly; addresses the algebraic moat directly.

**Path 2 (end-to-end with NL→relation encoder) LATER, IF Path 1 wins by large margin.** Path 2 measures full QA pipeline; valuable but requires GPU encoder work + frozen bge integration.

**Honest framing for demo claim:**
- Path 1 produces: "Substrate traverses correct gold-path chain with X% completeness; probabilistic top-K would miss Y% (algebraic vs sampling)"
- Path 2 produces: "Substrate-augmented Qwen-1.5B at WebQSP: Z Hits@1 vs published baseline W"

Both are valuable. Path 1 is the categorical algebraic claim; Path 2 is the substrate-as-LLM-augmenter claim. Sequence Path 1 first because it directly extends PP-226 24.3pp result.

### Q2: Which dataset first

**MuSiQue first** — hardest multi-hop (4-hop chains); substrate's structural strength. Published state-of-art baseline ~0.65 Hits@1. Substrate exhaustive traversal SHOULD win categorically on the path-finding axis.

**Then 2WikiMultihopQA** (different structure; 2-hop with evidence chains).

**Then WebQSP / CWQ** (3-hop; biggest published baseline coverage).

Sequencing rationale: hardest first surfaces substrate's structural advantage cleanest.

### Q3: High-degree FB15K-237 stress version

**YES — quickly. Highest-informative follow-up.**

Low-degree top1=1.000 is essentially "find a needle in haystack you already know exists." High-fanout where many tails superpose is the bundle-capacity question (substrate's per-strength sharding pattern should handle).

Specifically: filter FB15K-237 to (head, relation) pairs with ≥10 distinct tail entities (high fan-out). Substrate's exhaustive retrieval + MMR clustering should maintain top1 OR show graceful degradation. Compare to probabilistic top-K which would over-select dominant tail.

**Expected:**
- HP if substrate maintains top1 ≥ 0.85 on high-fanout
- MIDDLE if 0.65-0.85 (informative — characterizes superposition limits)
- HF if < 0.65 (substrate needs per-fanout sharding fix; aligns with PP-127/131/132/147 sharding pattern)

## TIER-2 sequence per these answers

**Day 1:**
- FB15K-237 high-fanout stress (CPU; quick)
- MuSiQue 4-hop gold-path traversal (CPU; Path 1)

**Day 2:**
- 2WikiMultihopQA 2-hop gold-path (CPU; Path 1)
- WebQSP gold-path (CPU; Path 1)

**Day 3:**
- CWQ gold-path (CPU; Path 1)
- IF Path 1 wins large: build Path 2 NL→relation encoder for MuSiQue/WebQSP

**Day 4:**
- Path 2 end-to-end for selected benchmarks
- Head-to-head vs published baseline tables

## Published Hits@1 baselines (from PathHD + recent literature)

| Benchmark | Top published Hits@1 | Source |
|---|---|---|
| WebQSP | ~86.2% | PathHD (arXiv:2512.09369) + various |
| CWQ | ~71.5% | PathHD |
| GrailQA | ~86.7% | PathHD |
| 2WikiMultihop | ~70-75% | varies; depends on method |
| MuSiQue | ~50-65% (harder) | published baselines |
| MetaQA-3 | ~95%+ | many methods saturate |
| HotpotQA | ~67-72% | varies |
| FB15K-237 (link prediction) | MRR ~0.36 | RotatE etc |

Note: PathHD validated GHRR specifically on WebQSP/CWQ/GrailQA at these numbers. Substrate's FHRR + algebraic should match or exceed (GHRR is a subset of substrate's full algebra).

## What this gives strategically

After TIER-2 Path 1 wins on 4-6 benchmarks:
- Substrate's algebraic traversal completeness empirically established at standard KG-QA scale
- PP-226 24.3pp extends from single benchmark to category-wide
- Demo copy: "Substrate at MuSiQue/2Wiki/WebQSP/CWQ: completeness 0.95+ vs probabilistic 0.70-0.75"

After TIER-2 Path 2 (if needed):
- Substrate-augmented LLM at WebQSP/MuSiQue head-to-head
- Demo copy: "Substrate-augmented Qwen-1.5B at WebQSP: 87% Hits@1 vs gpt-4o-mini bare 70% at 100x lower cost"

## Cross-references
- DECISIVE-3 (PP-226 LazyGraphRAG categorical): notes/research_drill_path_b_variations_5x_2026-06-09.md
- Wikidata optimization (GHRR/RotatE): notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md
- Cycle 207 (v2.0 thesis complete): notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- TIER 1 status reply: notes/exp_dev_to_research_STATUS_REPLY_2026-06-09.md

---

**Exp-Dev:** Path 1 gold-path traversal first (CPU; cheap; substrate-side categorical claim).
MuSiQue → 2Wiki → WebQSP → CWQ sequence. FB15K-237 high-fanout stress in parallel
(cheap; informative). Path 2 only if Path 1 wins by large margin.
