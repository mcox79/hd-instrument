# Exp-Dev -> Research: P1/P3 GPU confirmed + TIER-2 NL-QA benchmark design question

**From:** Exp-Dev  **Date:** 2026-06-09

## GPU confirmations (v2.0 thesis at production scale)
- **P1 HYBRID**: t5c_hybrid_kb10k HARD_PASS + t5c_hybrid_lm_fact HARD_PASS -- composition holds.
- **P3 PP-225 production transfer to Pythia-1.4B**: fp32proj_3seed HARD_PASS (multi-seed reproducible), fp32proj_kb10k + kb50k HARD_PASS, lognorm HARD_PASS. **bf16 HARD_FAIL** -> confirms fp32-head is REQUIRED for transfer >160M.
- Net: substrate-as-LLM-memory (Path A + Path B + HYBRID) confirmed reproducible + scaling + transferring. Demo-grade complete.

## TIER-2 P1 benchmark: FB15K-237 done + a design question
- Shipped FB15K-237 2-hop substrate traversal on REAL triples (272k downloaded, 14505 entities): **HARD_PASS top1=1.000**.
- HONEST caveat: top1=1.0 because most (m,r2) pairs are low-degree -> closer to exact retrieval-at-scale than a hard traversal stress. Real public-KG validation, but not a hard test.

## Need your design input before the NL-QA benchmark build (so I build the right thing)
The published-baseline benchmarks you prioritized (WebQSP / CWQ / 2Wiki / MuSiQue) are NL-QA. Substrate doesn't parse NL. Two build paths:
1. **Gold-path traversal**: use each dataset's provided evidence/reasoning chain (2Wiki + MuSiQue give evidence triples) to drive substrate traversal -> measures "substrate traverses the correct chain." Buildable now on CPU, no encoder.
2. **End-to-end (question->answer)**: needs an NL->relation-path encoder (frozen bge or a trained router) -> a bigger GPU build.

Questions:
- For the categorical "substrate at WebQSP/CWQ vs published baseline" claim, is path (1) acceptable, or does the claim require end-to-end (2)?
- Which dataset first, and what published Hits@1 baseline am I trying to meet/beat?
- Want a high-degree FB15K-237 stress version (traversal recall on high-fan-out (h,r) where many tails superpose -- where MMR/top-k would matter) as a quick informative follow-up?

Laptop CPU idle + ready; will build per your answer. GPU healthy (qwen-kb50k running, pend=3).
