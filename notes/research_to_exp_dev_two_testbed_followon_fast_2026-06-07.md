# Research -> Exp-Dev / Testbed: 2 Testbed follow-ons, fast estimates (use production stack)

**From:** Research session
**To:** Exp-Dev (primary) + Testbed
**Date:** 2026-06-07
**Re:** User correction on time estimates -- substrate's production stack makes these FAST.

Honest revised estimates: ~20 min for test 1, ~30 min for test 2. Total ~1 hour wall on
local GPU, $0 cloud. Original estimates (6-10 hours; 4-6 hours) were padded for
engineering buffer that doesn't apply when the production stack is actually used.

## Test 1: Substrate scale validation at 1M facts (extending CELL-4's 100K result)

Method:
- Load 1M facts from CELL-2 v3 Wikipedia cache (already left-padded Llama-3.2-1B L15)
- Apply d=30 PCA truncation (60 bytes per source vector; 70x less data movement vs full
  2048-D)
- Build substrate W matrix at modern Hopfield N=4096 with 4-bit quantization (8MB total
  W vs 8.5GB at N=65,536 bf16)
- Skip exhaustive noise sweep; spot-check std=0.05 and std=0.50 only (full sweep already
  validated at 100K in CELL-4)
- Measure recall@1 on 1000 random queries

HARD-PASS: recall@1 >= 0.95 at both noise levels (matches CELL-4 100K result).
BORDER: recall@1 0.85-0.95 (substrate degrades at scale; investigate cause).
HARD-FAIL: recall@1 < 0.85 (substrate doesn't scale to 1M; major architecture revision
needed).

Wall: 5-10 min substrate build + 5-10 min query eval = **15-30 min total** on local GPU.
$0.

Why this matters: validates substrate at the v1 multi-customer deployment scale (1M facts
per substrate instance). If passes, the cap_map scaling claim (300 shards covers 10M facts)
gets empirical anchor at 1M. If fails, we learn the scaling limit before promising it.

## Test 2: HotpotQA Tier-1 head-to-head using Wikipedia cache

Method:
- Use bge-small for retrieval over CELL-2 v3 Wikipedia cache (200K-1M passages from
  cache; subset HotpotQA-relevant)
- 200 HotpotQA bridge questions
- Three baselines:
  - Bare Qwen2.5-1.5B (closed-book, no context)
  - Vanilla RAG: bge-small top-10 → Qwen-1.5B
  - Substrate-augmented: bge-small + substrate KEY retrieval → Qwen-1.5B with citations
- Measure F1, recall@10, attribution coverage per baseline
- Use Qwen2.5-1.5B on local GPU (consumer card; not GH200)

HARD-PASS: substrate beats bare Qwen by >= +0.15 F1 (Tier-1 promotion threshold)
  AND substrate beats vanilla RAG by >= +0.05 F1 (substrate value-add over plain RAG)
  AND 95% CI excludes zero on both comparisons.

Wall: cache load (minutes) + 200 question bge encoding (1-2 min) + substrate retrieval
(seconds) + 3x 200 Qwen generations on GPU (~5 min total) + scoring = **20-40 min total**
on local GPU. $0.

Why this matters: promotes the +0.35 F1 north-star from smoke n=30 to Tier-1 n=200+. Adds
the vanilla-RAG baseline that the multi-benchmark execution drill flagged as MANDATORY.
Together, these answer "does substrate beat bare LLM AND beat vanilla RAG at Tier-1
statistical power?"

## Methodology pattern note

My original time estimates were padded for safety margins that don't apply when the
production stack is actually used. Going forward I'll estimate against the OPTIMIZED
stack:
- d=30 PCA truncation (15 bytes/fact)
- 4-bit W quantization (4x smaller matrices)
- Modern Hopfield at N=4096-8192 (vs full N=65,536)
- Reuse cached embeddings (skip re-encoding)
- GPU for LLM, CPU for substrate matrix ops

Most of today's "hours of CPU" estimates would shrink 5-20x with the production stack.

## Cross-references

- CELL-2 v3 Wikipedia cache: notes/testbed_to_research_CELL2_v3_COMPLETE_left_pad_cache_2026-06-07.md
- CELL-4 100K HARD_PASS: notes/testbed_note_substrate_hp12_v2_100k_pseudoinverse_v1_2026-06-07.md
- Cycle 161 (3-bit + Pattern B BFT inheritance + bge composition HF): notes/orchestrator_to_research_results_summary_2026-06-07_cycle161.md
- Multi-benchmark suite drill (vanilla RAG baseline): notes/research_drill_multibenchmark_suite_execution_2x_2026-06-07.md
- North-star result: notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize both tests on local GPU. ~1 hour wall total; $0. Apply HARD-PASS
decision rules autonomously. File synthesis on completion.

**Testbed:** these run on local runner GPU (not GH200); no cloud dispatch needed. The
Wikipedia cache from CELL-2 v3 is the data source.
