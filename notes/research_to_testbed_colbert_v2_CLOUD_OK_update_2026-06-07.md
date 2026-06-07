# Research -> Testbed: ColBERT-v2 CLOUD GH200 APPROVED (cloud pause lifted)

**From:** Research session
**To:** Testbed
**Date:** 2026-06-07
**Re:** research_to_testbed_colbert_v2_routing_directives — REVERSING the local-first call.

User lifted the overnight cloud pause and authorized cloud for ColBERT if genuinely a
good fit. Re-evaluating: ColBERT-v2 IS a genuine cloud fit.

## Revised lane: CLOUD GH200

Reasoning:
- ColBERT-v2 default model + index over distractor passages + sentence-transformers
  stack + query batch processing typically peaks at 10-14 GB VRAM
- 4060 Ti has 8 GB — ~30-50% chance of OOM during index build
- If local OOMs, fallback to cloud burns 1-2 hr of wasted setup time
- Cloud GH200 ~$7 deterministic vs local-then-fallback expected wall time
- Your safety stack is battle-tested for cloud dispatch
- The "cloud only when absolutely necessary" rule IS met here — hardware-bound need

## All other directives unchanged

- colbert-ai direct (skip ragatouille langchain dependency)
- HotpotQA distractor 1k passages FIRST (apples-to-apples with bge-small r@2=0.42 baseline)
- 100 bridge questions; measure recall@2 + recall@10
- HARD-PASS: recall@2 >= 0.55 (gates user-level decision on 2-3 week integration)
- BORDER: 0.50-0.55
- HARD-FAIL: < 0.50 (multi-hop precision conceded; demo leans on already-HP hotpot_3baseline
  answer-F1 at RAG parity)
- File verdict with substrate-implication framing; DO NOT start integration work regardless
  of outcome — user-level architectural decision required
- Sequence after running entropy-max real-encoder + bge@d=30 pre-test (or in parallel
  if Testbed has the bandwidth)

## Cost envelope

- Today's spend ~$37 prior cloud cells (CELL-2/CELL-3/CELL-4 + cluster-leak debug)
- + ~$7 ColBERT cloud = ~$44 total today
- Within reasonable bound for the user's authorization given the strategic value of
  ColBERT pre-test (gates multi-hop precision retrieval upgrade decision)

## Cross-references

- Original routing (local-first; superseded): notes/research_to_testbed_colbert_v2_routing_directives_2026-06-07.md
- Testbed handoff questions: notes/testbed_to_research_colbert_v2_handoff_questions_2026-06-07.md
- 2-hour high-priority battery (entropy-max URGENT still running on local GPU): notes/research_to_exp_dev_2hour_high_priority_battery_2026-06-07.md

---

**END.**

**Testbed:** dispatch CLOUD GH200 per your original default plan. Apply HARD-PASS / BORDER /
HARD-FAIL autonomously. File verdict to Research with substrate-implication framing on
completion. Wait for architectural decision before any integration work.
