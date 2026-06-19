# exp_dev hand-off -- research: v1.1 Component Composition Integration Risks (2x)

## Filed-by
Research sub-agent, 2026-06-07

## Trigger
Research note: notes/research_drill_v11_composition_risks_2x_2026-06-07.md
Topic: 2x operational drill on v1.1 component composition integration risks after 7+ individual-component HPs

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
CPU-only anchors (A1, A3) are not pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY -- CPU, ~2 hrs, resolves the integration go/no-go decision)
Pointer: "Cheap decisive test" section + Test 1 section of research note
Substrate-product reading: Assembles all currently implemented components in one process with
  per-component telemetry. Measures actual compound F1 on 50 HotpotQA bridge questions.
  This number determines whether the composition problem is smaller than predicted (F1 >= 0.55)
  or requires architectural diagnosis (F1 < 0.35) before further investment.
  This test gates ALL other v1.1 engineering work. Nothing else is defensible until this runs.
Tier hint: CPU (Qwen 1.5B can run on CPU for smoke; GPU preferred for realistic latency);
  no sweep; single configuration; binary gate.
Why-now: The compound formula predicts F1 = 0.43-0.52 at current component values.
  Whether the actual composed result is above or below 0.43 determines the sequencing of
  everything that follows. If above: proceed to Test 2 (ablation). If below 0.35: diagnose
  the architecture before any tuning. 2 hours of run time vs weeks of misdirected engineering.
Task: Load DistilBERT-NER + bge-small (or Llama L15) + Qwen 1.5B + pre-trained substrate.
  Instrument with per-component wall-time logging. Run 50 HotpotQA dev bridge questions.
  Measure: (a) bridge-ID accuracy (NER output vs ground-truth bridge), (b) retrieval hit rate
  (correct fact in top-5), (c) multi-hop F1 (EM + partial), (d) per-component latency
  breakdown (NER/retrieval/L2/Qwen), (e) total P90 latency.
  HARD-PASS: F1 >= 0.55 on 50 queries; P90 latency <= 1.4s.
  MIDDLE-BAND: F1 in 0.40-0.54 range (proceed to ablation to identify which component to fix).
  HARD-FAIL: F1 < 0.35; OR P90 latency > 3s on warm GPU.

### Anchor 2 (HIGH PRIORITY -- CPU, ~1 hr, confidence scoring precision test)
Pointer: Risk 3 (silent failure mode) + HF3 section of research note
Substrate-product reading: Validates that top-1 retrieval cosine similarity is a useful proxy
  for answer correctness. Precision >= 0.75 at flagging wrong answers is required before
  customer demo. This converts 53% silent failure rate to flagged failures -- a product-critical
  change that takes 1 day to implement and 1 hour to validate.
Tier hint: CPU; piggybacks on Anchor 1 results (just add the cosine-vs-correctness analysis);
  no additional model loading needed.
Why-now: Confidence scoring is the single cheapest safety feature for the demo. It does not
  require fixing any failure mode -- it just flags them. Should ship in the same engineering
  sprint as the pipeline assembly.
Task: Using the 50-query run from Anchor 1, compute: for each query where the ground-truth
  answer is wrong, record top-1 cosine score. For each query where answer is correct, record
  top-1 cosine. Plot (or compute): precision/recall of a cosine threshold classifier at
  alpha = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]. Report best alpha (precision >= 0.75).
  HARD-PASS: some alpha achieves precision >= 0.75 at recall >= 0.40 for flagging wrong answers.
  HARD-FAIL: no alpha achieves precision >= 0.55 (cosine is not useful as confidence proxy;
    need alternative -- Qwen logit entropy or token-level calibration).

### Anchor 3 (MEDIUM PRIORITY -- CPU, ~30 min, layer priority signal validation)
Pointer: Section 1.4 (query routing risk) + HP5 section of research note
Substrate-product reading: Validates that a simple system prompt priority tag ("Customer facts
  tagged [C] override general knowledge tagged [W]") achieves >= 88% override success on
  30 constructed conflict cases. This is a 0.5-day implementation that reduces the router
  wrong-layer risk from P=0.35 to P=0.12. Required for any demo involving customer-specific
  overrides of Wikipedia baseline facts.
Tier hint: CPU; Qwen 1.5B inference only; 30 test cases; no retrieval substrate needed (facts
  can be injected directly into context for this test).
Why-now: The customer override scenario is one of the 6 demo scenarios. If override success
  rate is < 70%, the demo scenario fails visibly. 30-minute test prevents demo embarrassment.
Task: Construct 30 test cases where a Wikipedia-style fact conflicts with a customer-override
  fact. Both are injected into Qwen context, tagged [W] and [C] respectively. System prompt
  includes priority instruction. Measure: fraction of cases where Qwen's answer uses the
  [C] fact vs [W] fact.
  HARD-PASS: >= 27/30 cases (90%) use the [C] fact.
  HARD-FAIL: < 18/30 cases (60%) use the [C] fact (system prompt priority is unreliable
    at 1.5B; need alternative implementation: prepend [C] facts, not inject alongside [W]).

### Anchor 4 (MEDIUM PRIORITY -- GPU, ~1.5 hrs, load test at 10 QPS)
Pointer: Test 3 section + Risk 1 section of research note
Substrate-product reading: Validates whether Misra-Gries background aggregator causes
  throughput degradation under concurrent query load. P=0.55 that concurrency degrades
  throughput by > 50% at 10 QPS if synchronization is not implemented correctly.
  If it does degrade, the fix (async process for aggregator) is 1 day of work that must
  happen before any multi-tenant demo.
Tier hint: GPU; 600 queries at 10 QPS for 60 seconds; Misra-Gries running background.
Why-now: Load failure is a silent demo risk. The demo may work perfectly at 1 QPS (as all
  individual component tests ran) but fail at 5 concurrent users. Finding this in engineering
  validation (1.5 hrs) beats finding it live in front of a customer.
Task: Run 600 HotpotQA queries at 10 QPS concurrently through the full pipeline. Record:
  throughput (queries/sec), latency P50/P90/P99, and Misra-Gries update latency distribution
  (measured separately in the background thread).
  HARD-PASS: throughput >= 7 QPS; P90 latency <= 2s; Misra-Gries update P90 <= 50ms.
  HARD-FAIL: throughput < 4 QPS; OR P90 latency > 4s; OR Misra-Gries update P90 > 500ms
    (GIL contention detected; must move to subprocess).

---

## Context pointers

- Research note (this drill): notes/research_drill_v11_composition_risks_2x_2026-06-07.md
- Bridge-ID 2x drill: notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md
- Sleep defrag 2x drill: notes/research_drill_sleep_defrag_scaling_adversarial_2x_2026-06-07.md
- Substrate pretraining drill: notes/research_drill_substrate_pretraining_general_knowledge_3x_2026-06-07.md
- Demo pipeline architecture drill: notes/research_drill_demo_pipeline_architecture_2x_2026-06-07.md
- Pattern B production stack compat drill: notes/research_drill_pattern_b_production_stack_compat_3x_2026-06-07.md
- Post-compaction brief (afternoon): notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

## Contract

A1 and A2 are coupled (A2 reuses A1 results). Run A1 first; A2 is a 30-min analysis pass on
the same data. A3 is independent and can run in parallel with A1 if GPU is occupied. A4
requires A1 to have passed (no point load-testing a pipeline that fails at 1 QPS).

If A1 returns HARD-FAIL (F1 < 0.35): do NOT proceed to A2/A3/A4. File a diagnosis note
identifying which component is responsible for the failure (check: is bridge-ID accuracy
below 0.50? Is retrieval hit rate below 0.70? Is Qwen generating coherently at all?).
The composition problem is architectural, not tuning-level.

If A1 returns MIDDLE-BAND (0.40-0.54): proceed to A2 and A3; use ablation data to identify
the weakest component; sequence its fix as the highest-priority engineering task.

## Autonomy declaration

Exp_dev designs all sweep parameters, threshold formulas, script implementations, and
queue routing. This file provides task framing and empirical context only.
