# exp_dev hand-off -- research: substrate pre-training general knowledge 3x

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md
Urgency: HIGH -- CELL-2 v3 artifact already on runner; v1.1 product layer is 1.5 weeks away pending pre-test validation

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Context

CELL-2 v3 (data/cell2_results/): 5.84M Wikipedia articles, Llama-1B L15 left-pad embeddings, 21 GB on local runner. This cache is the raw material for the pre-trained Wikipedia base layer. The three cheap pre-tests below convert this raw cache into validated evidence for the v1.1 product decision.

All three pre-tests are CPU-laptop runnable. No cloud dispatch required. Each is ~1-2 hours wall time.

---

## Anchor candidates (rank-ordered)

### Anchor 1: substrate_wikipedia_nq_triviaqa_retrieval_v1

Anchor pointer: Research note Section 5, Pre-Test 1. Section 11 v1.1 sequencing.
Substrate-product reading: Builds a Pattern B index on a 50K-article sample from the CELL-2 v3 cache. Samples 500 NQ dev questions + 500 TriviaQA Wikipedia-split questions. Measures retrieval recall@1, @5, @20. This is the primary gate for all pre-trained substrate claims. If recall@5 < 50%, the L15 embeddings are not suitable for Wikipedia retrieval at Pattern B compression -- a fundamental finding that would block v1.1.
Tier hint: CPU laptop. ~1-2 hours wall time. CHEAPEST first gate. Run before any other pre-test.
Why-now: CELL-2 v3 cache is the artifact sitting idle on the runner. The only missing piece is the Pattern B compression + HNSW index build on a sample + 1000-query retrieval sweep. This converts a 21 GB cache into a validated retrieval benchmark result. All downstream v1.1 engineering decisions depend on this number.

Pre-reg bands:
  HARD-PASS: recall@5 >= 65% on NQ AND >= 65% on TriviaQA
  MIDDLE-BAND: recall@5 = 50-65% on either
  HARD-FAIL: recall@5 < 50% on NQ or TriviaQA (encoder mismatch or chunking failure)

P_deflated (theoretical x calibration-deflated): 0.55 for HARD-PASS.

### Anchor 2: substrate_wikipedia_hotpotqa_bridge_coverage_v1

Anchor pointer: Research note Section 3, Pre-Test 2. Section 12 HARD-PASS/FAIL thresholds.
Substrate-product reading: Selects 200 HotpotQA dev questions of bridge type. Checks: (a) is the bridge entity article present in the CELL-2 v3 cache? (b) When queried, does the bridge entity's Wikipedia article appear in top-5 retrieval results? This measures how much the pre-trained Wikipedia base layer solves the INDEX RICHNESS bottleneck identified in the self-improving routing drill (cold-start bridge coverage 55-70%). If bridge entity coverage >= 88%, the INDEX RICHNESS bottleneck is structurally resolved at deployment for general-domain queries.
Tier hint: CPU laptop. ~1 hour wall time. Depends on Anchor 1 HNSW index being built.
Why-now: Self-improving routing drill identified the cold-start bridge coverage gap as the primary multi-hop QA bottleneck. Resolving it with a pre-loaded base is the simplest possible fix. This pre-test quantifies whether the fix works.

Pre-reg bands:
  HARD-PASS: bridge entity found in index >= 88% of bridge questions; top-5 retrieval of bridge article >= 75% when entity present
  MIDDLE-BAND: entity coverage 75-88%; top-5 retrieval 60-75%
  HARD-FAIL: entity coverage < 70% OR top-5 retrieval < 50% when entity present

P_deflated: 0.57 for HARD-PASS.

### Anchor 3: substrate_wikipedia_nq_cold_vs_pretrained_v1

Anchor pointer: Research note Section 5, Pre-Test 3. Section 11 v1.1 sequencing.
Substrate-product reading: Direct head-to-head on 500 NQ questions: cold-start substrate (Layer 1 empty, no pre-trained Layer 0) vs pre-trained Wikipedia substrate (Layer 0 = CELL-2 v3 sample). Measures end-to-end EM improvement attributable to the pre-trained layer alone. This is the v1.1 product justification experiment: quantifies how much the pre-loaded Wikipedia base improves answers at deployment before any customer KB is loaded.
Tier hint: CPU laptop. ~2 hours wall time (two runs). Requires Anchor 1 index.
Why-now: The case for building a pre-trained substrate product layer rests on a measurable EM improvement. Without this number, the v1.1 engineering investment (1.5 weeks) is unjustified. With this number, the investment is grounded.

Pre-reg bands:
  HARD-PASS: pre-trained EM >= cold-start EM + 20 points on NQ
  MIDDLE-BAND: improvement 10-20 points
  HARD-FAIL: improvement < 5 points (indicates pre-trained layer not being accessed; integration bug)

P_deflated: 0.62 for HARD-PASS. Cold-start EM on NQ is near 0% (no Wikipedia means no answers); even a modest retrieval recall translates to large absolute EM improvement.

---

## Sequencing

Run in order: Anchor 1 first (builds the index, validates the encoder path). Anchor 2 second (uses same index, ~1 extra hour). Anchor 3 third (two-run comparison, uses same index).

Total wall time if sequential: ~4-5 hours on CPU laptop.
Can run Anchors 2 and 3 in parallel if runner has two processes available.

All three should complete within a single exp_dev session.

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md (full research note)
- d:/AI/hd-instrument/notes/testbed_to_research_CELL2_v3_COMPLETE_left_pad_cache_2026-06-07.md (CELL-2 v3 completion report; cache location and shard structure)
- d:/AI/hd-instrument/notes/research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md (parametric knowledge gap quantification; prior drill this cycle)
- d:/AI/hd-instrument/data/cell2_results/ (CELL-2 v3 cache; 585 shards at 10K articles each; 21 GB)

---

## Contract

- Exp_dev designs and queues anchors based on research note pointers above.
- Do NOT treat this file as an implementation spec. The anchor pointer references are starting points; exp_dev authors the actual experiment cells.
- Pre-reg bands above are mandatory: register HARD-PASS / MIDDLE-BAND / HARD-FAIL thresholds before running.
- Drill-pretest-required rule applies: run Anchor 1 first and verify recall@5 >= 50% before dispatching Anchors 2 and 3.
- All three are laptop CPU; no cloud authorization needed.
- Laptop runs: foreground timeout not nohup per feedback rule.

---

## Autonomy declaration

Exp_dev has full autonomy on: script design, chunking strategy, HNSW hyperparameters, reader model selection for EM evaluation, exact sample selection from NQ/TriviaQA dev sets.
Exp_dev does NOT have autonomy on: pre-reg bands (pre-registered above), sequencing rule (Anchor 1 before Anchors 2+3), or claiming HARD-PASS without meeting the stated threshold.
