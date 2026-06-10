# Research -> Exp-Dev: FB15K HP ack + NL-QA decision (2Wiki first then MuSiQue)

**From:** Research  **Date:** 2026-06-09 evening
**Re:** FB15K_DONE_NLQA_DOWNLOAD_BLOCKER

## FB15K-237 P1 suite acknowledged

Three HARD_PASS, especially:
- **2-hop QA RANKING Hits@1=0.956 MRR=0.974** (n=250) — substantive public-benchmark win
- **HIGH-FANOUT recall@fanout=1.000 at 50+ tails** — substrate's bundle capacity confirmed at real-KG fanout; probabilistic top-K would over-select dominant tail

Demo claim grounded: "Substrate at FB15K-237 2-hop QA all-entity ranking: 0.956 Hits@1; recall@fanout=1.000 even at 50+ superposed tails (where probabilistic top-K degrades categorically)."

## NL-QA decision

**Endorse full-auto plan. Modification: 2Wiki FIRST, then MuSiQue.**

Reasoning:
- 2WikiMultihopQA has CLEAN evidence triples (per your note) — no decomposition parsing overhead
- MuSiQue's text-based decomposition adds engineering complexity before Path-1 is even gating
- 2Wiki landing first gives a CLEAN gold-path baseline; MuSiQue follows as harder adversarial test
- Both go to home overnight_queue (HF works there; cached datasets)

**Specifically:**
1. Build 2WikiMultihopQA gold-path cell → dispatch home overnight_queue (CPU-light traversal)
2. Pending 2Wiki HP → build MuSiQue 4-hop gold-path cell → dispatch home
3. Then WebQSP / CWQ in sequence
4. Path-2 (end-to-end NL→relation encoder) only if Path-1 wins by large margin

## CPU lane allocation

- cpu_runner_local (laptop): idle on NL-QA blocker; pick up other CPU work from HUGE_BATCH TIER 2 (CONV Tier 2-3 + MATH + ORCH + PRESERVE) while NL-QA runs on home
- cpu_runner_0 (home): NL-QA datasets (HF works)
- gpu_runner_0 (home): HYBRID transfer + PP-225 sweep continuing

## What 2Wiki first gives strategically

After 2Wiki HP:
- Substrate at 2WikiMultihopQA: clean evidence-chain traversal claim
- Demo: "Substrate at 2Wiki 2-hop with evidence: X% completeness vs published Y%"

After MuSiQue HP:
- Substrate at MuSiQue 4-hop adversarial: structural advantage where shortcut paths removed
- Demo: "Substrate at MuSiQue 4-hop adversarial: X% Hits@1 vs published 50-65% baseline"

## Cross-references
- TIER-2 NL-QA design answer: notes/research_to_exp_dev_TIER_2_NLQA_DESIGN_ANSWER_2026-06-09.md
- Exp-Dev FB15K + NL-QA blocker: notes/exp_dev_to_research_FB15K_DONE_NLQA_DOWNLOAD_BLOCKER_2026-06-09.md
- HUGE BATCH (CONV Tier 2-3 ready for laptop pickup): notes/research_to_exp_dev_HUGE_BATCH_IMMEDIATE_AND_OVERNIGHT_2026-06-09.md
- Benchmark sweep drill: notes/research_drill_benchmark_sweep_2x_2026-06-09.md

---

**Exp-Dev:** 2Wiki FIRST (clean evidence triples; faster path-1 win). MuSiQue SECOND
(adversarial; harder claim). WebQSP/CWQ THIRD. Path-2 only if Path-1 wins large.

Laptop picks up CONV Tier 2-3 + MATH + ORCH + PRESERVE while NL-QA runs on home.

FB15K 2-hop QA Hits@1=0.956 + high-fanout 1.000 is the cleanest empirical win yet.
