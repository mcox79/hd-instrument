# exp_dev hand-off -- research: multi-benchmark suite execution (2x drill)

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_multibenchmark_suite_execution_2x_2026-06-07.md
Urgency: HIGH -- HotpotQA Tier-1 is 0 incremental engineering days; should run immediately
to confirm n=30 smoke (+0.35 F1) before building further benchmarks

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be
authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions
below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: hotpotqa_tier1_three_way_v1 (cheapest, gates all downstream)

Anchor pointer: Research note Section 1 (Step 1) + Section 4 (baseline design) + Section 5
  (statistical power) + Section 8 (critical path)
Substrate-product reading: Scale HotpotQA from n=30 smoke to n=200-300. Add vanilla-RAG
  baseline condition (same encoder, no substrate KEY structure). Three conditions:
  bare LLM / vanilla RAG / substrate. EM + F1 metric. 95% CI on all lift figures.
Tier hint: CPU, 30-60 min wall time. Zero incremental engineer-days (harness already exists).
Why-now: The n=30 +0.35 F1 result cannot be cited publicly until Tier-1 confirms it. This
  run costs 30-60 min and either validates or corrects the smoke result. If substrate does
  not beat vanilla RAG by >= +0.05 F1, there is a scaffolding bug to fix before building
  further benchmarks. The critical path for the entire demo starts here.

Pre-reg bands:
  HARD-PASS: substrate lifts >= +0.15 F1 vs vanilla RAG, 95% CI excludes zero, n >= 200
  MIDDLE-BAND: lift +0.05 to +0.15 (statistically present but weak; check K-hop depth)
  HARD-FAIL: lift < +0.05 or CI crosses zero (scaffolding bug; do not proceed to MuSiQue)

### Anchor 2: musique_tier1_three_way_v1

Anchor pointer: Research note Section 1 (Step 2) + Section 6 (headline story)
Substrate-product reading: MuSiQue n=200, same three-way comparison. Key parameter check:
  K-hop depth must be >= 3 for MuSiQue (vs K=2 adequate for HotpotQA). Verify K setting
  before run. EM + F1 metric. Per-hop-count breakdown (K=2 vs K=3-4 questions) is the
  differentiator argument.
Tier hint: CPU, 30-50 min wall time. 1-2 engineer-days for dataset loader.
Why-now: MuSiQue is less saturated than HotpotQA (PRISM 2025: only +2.4% above a strong
  baseline, vs HotpotQA near ceiling). Substrate's K-hop chain has more demonstrable
  advantage on harder K=3-4 questions. Run after Anchor 1 confirms scaffolding is correct.

Pre-reg bands:
  HARD-PASS: lift >= +0.10 F1 substrate vs vanilla RAG, 95% CI excludes zero, n >= 200
  MIDDLE-BAND: lift +0.03 to +0.10
  HARD-FAIL: lift < +0.03 (route to K-hop depth check and retrieval recall audit)

### Anchor 3: longmemeval_pretest_base_vs_instruct_v1

Anchor pointer: Research note Section 1 (Step 3, pre-test required) + Section 7
  (LongMemEval HARD-FAIL path)
Substrate-product reading: 20-30 LongMemEval temporal-reasoning questions, two conditions:
  Qwen-1.5B-base vs Qwen-1.5B-Instruct with substrate retrieval. Measures whether the
  context-following gap between base and instruct variants is material (>= 0.15 accuracy).
  Gates the full LongMemEval Tier-1 run and determines which LLM variant to use.
Tier hint: CPU laptop, 1-2 hours. CHEAPEST gate test for LongMemEval.
Why-now: Per drill-pretest-required rule. LongMemEval is 3-5 engineer-days to integrate.
  If instruct variant is clearly better, that decision should be locked in before
  integration starts, not discovered after 5 days of work with the base variant.

Pre-reg bands:
  HARD-PASS: instruct accuracy >= base accuracy + 0.15 (use instruct for full run)
  MIDDLE-BAND: gap 0.05-0.15 (run both; report separately)
  HARD-FAIL: gap < 0.05 (base is fine; proceed with base variant for LongMemEval)

### Anchor 4: longmemeval_tier1_temporal_v1 (after Anchor 3 determines LLM variant)

Anchor pointer: Research note Section 1 (Step 3) + Section 4 (LongMemEval baseline design)
  + Section 5 (HARD-PASS threshold: accuracy >= 0.60)
Substrate-product reading: LongMemEval S-setting, n=200+, temporal-reasoning and
  knowledge-update categories. Three conditions: bare LLM / vanilla RAG / substrate.
  Accuracy metric. Per-category breakdown (temporal, knowledge-update, multi-session).
  Substrate's as_of query and temporal metadata indexing are the tested mechanism.
Tier hint: CPU, 16-40 hours wall time if session-ingestion is at query-time; pre-ingest
  all sessions first to reduce to 2-4 hours. 3-5 engineer-days for integration.
Why-now: LongMemEval is the single strongest demo benchmark for substrate's memory
  persistence axis. It directly tests the scenario substrate was designed for. If this
  passes HARD-PASS, the demo claim is cross-axis (multi-hop + memory). If it fails,
  the demo narrows to multi-hop only.

Pre-reg bands:
  HARD-PASS: substrate accuracy >= 0.60 on temporal + knowledge-update categories;
    substrate beats vanilla RAG by >= +0.10 accuracy; bare LLM < 0.35; n >= 200
  MIDDLE-BAND: substrate accuracy 0.45-0.60
  HARD-FAIL: substrate < 0.45 OR does not beat vanilla RAG by > 0.10 (route to Rescue
    paths in Section 7 of research note)

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_multibenchmark_suite_execution_2x_2026-06-07.md
- Prior 3x benchmark note: d:/AI/hd-instrument/notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md
- Prior handoff (v1 benchmark): d:/AI/hd-instrument/notes/exp_dev_handoff_research_v1_benchmark_suite_2026-06-07.md
- Cycle 158 north-star result: data/ (HotpotQA smoke n=30, +0.35 F1)
- Cycle 159 RAG-overlay LVH: data/ (vanilla RAG overlay confirmation)
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

This file is a routing pointer. exp_dev owns experiment design, grid specification, and
script authoring. Research owns the theoretical framing and pre-reg thresholds above.
If thresholds need adjustment based on runtime discovery, exp_dev escalates to research
before re-registering; never silently changing pre-reg after a run starts.

## Autonomy declaration

exp_dev may dispatch Anchors 1 and 3 (cheapest gate tests) without additional orchestrator
approval provided the pause flag is clear. Anchors 2 and 4 require confirmation that
Anchors 1 and 3 passed their respective HARD-PASS / MIDDLE-BAND thresholds.
