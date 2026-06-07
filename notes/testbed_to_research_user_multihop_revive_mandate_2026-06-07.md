# Testbed -> Research: USER MANDATE — multi-hop revival required (do not accept closure)

**From:** Testbed
**To:** Research (primary) + Exp-Dev (inform)
**Date:** 2026-06-07 evening
**Re:** User strategic redirect on multi-hop precision retrieval closure.

## User mandate (verbatim)

> "i want to make sure we revive multihop I think it's extremely important"

> "only research will do this work and will route to you. this session focuses on
> test building and cloud implementation"

## What this means

User does NOT accept Research's formal closure of the multi-hop precision path after
3 HARD_FAILs (substrate-as-ranker / substrate-as-filter / ColBERT-v2). User explicitly
mandates revival.

Research owns the revival design lane. Testbed (this session) executes whatever Research
routes. Testbed will NOT propose revival experiments unprompted.

## What Research should consider (informational, not directive)

The 3 closed sub-paths shared a common assumption that may not be necessary:
- All were **single-shot retrieval** (one retrieve step per question)
- All were at **fair LLM size = 1.5B** (no larger-LLM control)
- All used **generic encoders** (no multi-hop-specific fine-tuning)
- Substrate was tested only at **100K facts** (not the 1M v1-deployment scale)

Plausible revival vectors (Research's design lane — not Testbed's proposal):
- Iterative retrieval (retrieve -> generate hop-1 -> re-retrieve)
- Multi-stage cascade (sparse + dense + rerank composed)
- Larger LLM control (Llama-3-8B baseline; isolates whether ceiling is LLM vs retrieval)
- Substrate-augmented iterative retrieval (substrate stores intermediate hops as facts)
- Multi-hop-specific architectures (IRCoT, DPR-HOTPOT, Graph-of-thoughts)
- ColBERT-v2 with HotpotQA-tuned encoder (vs generic colbert-ir/colbertv2.0)
- Substrate at 1M scale (the CELL-4 100K result is clean; 1M behavior unknown)

These are Research's to evaluate, prioritize, and route. Testbed has the cloud + safety
stack ready to execute any routing.

## Customer narrative implication

The current locked customer story emphasizes "substrate ties RAG on multi-hop, beats
RAG on single-hop, adds moat features." User believes this is too defensive on the
multi-hop axis. If Research can revive even one multi-hop precision path (substrate or
otherwise), the customer narrative strengthens materially.

## Cross-references

- ColBERT-v2 closure: notes/research_to_testbed_colbert_path_closed_v1_2026-06-07.md
- CELL-COLBERT HARD_FAIL: notes/testbed_note_colbert_v2_hotpot_distractor_v1_2026-06-07.md
- Cycle 161 substrate compositional verify HF: scorecard
- Cycle 164 composition regime A HF: scorecard
- Cycle 164 hotpot_3baseline 96pct RAG parity: notes/orchestrator_to_research_results_summary_2026-06-07_cycle164.md

---

**END.**

**Research:** please treat the multi-hop closure as a working hypothesis, not settled.
User wants revival experiments designed and routed. Testbed standing by to execute.

**Standing memory:** [[project-multihop-revive-priority]] now in Testbed's memory and
will persist across compactions.

**In flight on Testbed right now:** CELL-SPECDEC (Qwen-1.5B speculative decoding pre-test;
~30-60 min wall; dispatched cloud GH200 per perf_bottlenecks_v1_1 routing). Verdict
will be filed when complete. Multi-hop revival routings can land in parallel.
