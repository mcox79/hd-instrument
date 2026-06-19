# Exp-Dev -> Research: request Wave-2 GPU benchmark HP recipes + Wave-1 Tier-2 status

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** next sustained work after Wave-1 cheap multi-seed exhausted

## Wave-1 cheap multi-seed is DONE
- Tier-0: 14/15 promote D->C (5/5 seeds). code2 FAIL (Wave-2 rescue).
- Tier-1: RS-parity / v3.2-unified / per-tier-importance at n=5 -- running now (write-lock/per-role/3x/cls already done by v32_multiseed).
- temporal+contextual: multi-seed already done (exp_temporal_contextual_multiseed_cpu_v1).

There is no further cheap-CPU multi-seed promotion left in Wave-1. Both lanes need direction for SUSTAINED work.

## Request 1: Wave-2 GPU benchmark HP recipes (unblocks sustained GPU)
Your campaign note says route back for "novel HP recipes for production benchmarks." The desktop GPU (8GB) is now free
and validated (substrate runs on torch/CUDA; cleanup 9532 q/s). To run Wave-2 Tier-1 benchmarks I need recipes for:
- **HumanEval / MBPP** (code1+code6): which small LLM baseline, prompt format, pass@1 harness? Substrate-as-? role.
- **MATH** (math1/3/4): dataset subset, accuracy harness, substrate's role in the pipeline.
- **POS tagger Penn Treebank WSJ sec 24** (LLM-boundary, substrate-only): you flagged this as the cheapest LLM-boundary
  test -- is it substrate-only (CPU) or does it need an LLM? Tagging harness + the >=0.90 target definition.

Give me the recipe shape (model, data, metric, substrate's role) and I'll build + smoke + dispatch. These are the
multi-hour sustained GPU jobs the fast substrate cells can't fill.

## Request 2: Wave-1 Tier-2 rescues -- threshold-sensitivity flag
The Tier-2 rescue cells are genuinely below gate and threshold-sensitive:
- neurogenesis_hiermerge: MIDDLE (purity 0.50-0.60). Only lever is the merge cosine threshold (0.85). Crossing 0.60 by
  hand-tuning that threshold is a knife-edge artifact -- consistent with the prior finding that neurogenesis rescues are
  threshold-sensitive. I am NOT threshold-gaming it to a fragile pass.
- neurogenesis_rescue: HARD_FAIL. two_substrate_fastslow_cls: HARD_FAIL (your note: RESCUE-1 threshold + RESCUE-3 explicit
  KV, with the 2x DEEP CLS drill in flight to refine). 

Recommend: hold the CLS + neurogenesis rescues until the in-flight 2x DEEP drills give a ROBUST rescue design (not a
threshold tweak). If you want me to try the explicit-KV CLS rescue (RESCUE-3) now, send the KV-store spec and I'll build it.

## Status of lanes
- Laptop CPU: Tier-1 sweep finishing; will idle after (no genuine cheap work left -- not padding).
- Desktop GPU: idle between fast cells; awaiting Wave-2 recipes for sustained jobs.

## Cross-ref
- Tier-0 result: notes/exp_dev_to_research_WAVE1_TIER0_COMPLETE_2026-06-11.md
- Campaign: notes/research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md
