# exp_dev hand-off -- research: End-to-End Composition Cascade Closure (3x)

## Filed-by
Research sub-agent, 2026-06-07

## Trigger
Research note: notes/research_drill_composition_cascade_closure_3x_2026-06-07.md
Topic: 3x deep drill on composition cascade closure; optimal architecture for v1.1 ship

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
CPU-only anchors (B1a pre-test, B2, B3) are not pause-gated.
GPU anchor (B4 load test) requires pause-gate check.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides task + why + contract only.
Exp_dev designs sweep parameters, threshold formulas, script implementations, and queue routing.

---

## Anchor candidates (rank-ordered)

### Anchor B1 (HIGHEST PRIORITY -- CPU pre-test, 30 min, gates decisive test)
Pointer: Section 9 (cheap pre-test) of research note
Substrate-product reading: Five serial 5-minute pre-tests that confirm each component loads,
  produces sensible output, and that the parallel 3-stage plumbing assembles without errors.
  This 30-minute pre-test catches the most common integration bugs (model loading failures,
  encoding format mismatches, context assembly crashes) before committing 2 hours to the
  full decisive test. Pre-test E (stub plumbing check) is the most critical -- if the
  3-stage parallel structure crashes on stub inputs, the decisive test cannot run.
Tier hint: CPU-only for pre-tests A-E; no Qwen GPU needed for stubs; Qwen CPU load for test D.
Why-now: Without the pre-test, the decisive test has a 35% chance of failing in the first
  10 minutes on an infrastructure problem. The pre-test converts this to a known-clean start.
Contract: If any pre-test fails, diagnose and fix BEFORE running decisive test (Anchor B2).

### Anchor B2 (HIGH PRIORITY -- CPU or GPU, 2 hrs, integration go/no-go gate)
Pointer: Section 8 (decisive composition test) of research note
Substrate-product reading: Assembles the 3-stage parallel v1.1 pipeline (NER + bge-small
  Path A + bge-small entity Path B, parallel Stage 1; re-ranked context assembly Stage 2;
  Qwen 1.5B generation Stage 3) with top-15 entity retrieval (Patch B pre-applied).
  Runs 100 HotpotQA dev bridge questions. Measures compound F1 plus per-component
  telemetry. This is the primary gate for all v1.1 demo work. Nothing downstream is
  defensible without this number.
Tier hint: GPU preferred for latency measurement; CPU acceptable for correctness-only run
  (3-4 hrs wall time at CPU Qwen speed; latency numbers not valid for SLA claims on CPU).
  No hyperparameter sweep; single configuration; binary architectural gate.
Why-now: The 2x drill showed compound accuracy at 0.47. The 3x drill's 3-stage parallel
  architecture predicts 0.645 post-patches. Whether the actual assembled pipeline is above
  0.55 (HARD-PASS) or below 0.40 (HARD-FAIL) gates all downstream engineering work.
  10-14 engineer-days of patch work depend on this 2-hour measurement.
HARD-PASS: F1 >= 0.55 on 100 questions; P50 latency <= 900ms on GPU; zero model crashes.
MIDDLE-BAND: F1 in [0.40, 0.55]; use per-query ablation data to identify weakest component.
HARD-FAIL: F1 < 0.40; OR any model crashes; OR P50 latency > 2s on GPU. Diagnose:
  check NER accuracy separately (target >= 0.55); check retrieval hit rate at top-15
  (target >= 0.72); check Qwen output coherence (does it produce strings, not errors?).

### Anchor B3 (MEDIUM PRIORITY -- CPU, 1 hr, confidence scoring calibration)
Pointer: Section 6 Option D (per-query reliability score) + Section 10 HP4/HF3 of research note
Substrate-product reading: Using the per-query results from Anchor B2, compute the correlation
  between top-1 cosine score and answer correctness. Sweep cosine threshold alpha in
  [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]. Also compute Qwen logit entropy for each
  answer. Build a composite score (linear combination of cosine + entropy). Report best
  alpha and best composite weight for precision >= 0.75 at recall >= 0.40.
  This converts 53% silent failure into flagged failure -- a product-critical change
  requiring < 1 day to implement after calibration is done.
Tier hint: CPU analysis of B2 results; no additional model inference needed.
Why-now: Confidence scoring is the minimum safety feature required before any external demo.
  It ships in the same engineering sprint as the pipeline assembly. The calibration must
  happen on real (not synthetic) pipeline output -- hence depends on B2 completing.
HARD-PASS: some alpha achieves precision >= 0.75 at recall >= 0.40.
HARD-FAIL: no alpha achieves precision >= 0.55 (cosine alone is not predictive of correctness).
  If HARD-FAIL: test Qwen logit entropy alone; if also < 0.55 precision, investigate
  cross-encoder re-ranking (bge-reranker) as an alternative confidence signal.

### Anchor B4 (MEDIUM PRIORITY -- CPU, 30 min, layer priority instruction validation)
Pointer: Section 1.4 (query routing risk) + Section 6 Option I (demo/production mode) of research note
Substrate-product reading: Constructs 30 synthetic conflict test cases where a Wikipedia-style
  fact and a customer-override fact about the same entity are injected into Qwen 1.5B context,
  tagged [W] and [C] respectively, with the system prompt priority instruction active.
  Measures fraction of cases where Qwen uses the [C] (customer) fact.
  Required before any demo involving customer-specific knowledge override scenarios.
Tier hint: CPU; Qwen 1.5B inference; no retrieval substrate needed (facts injected directly).
Why-now: The customer override scenario is one of the 6 planned demo scenarios. If Qwen
  does not follow the [C] priority instruction reliably, that demo scenario fails visibly.
  30-minute test prevents demo failure from a known addressable issue.
HARD-PASS: >= 27/30 cases (90%) use the [C] fact.
HARD-FAIL: < 18/30 cases (60%) use the [C] fact. Fix: move [C] facts to the TOP of the
  context window (above [W] facts); LLMs show primacy bias -- facts at top of context
  are used preferentially at 1.5B scale.

### Anchor B5 (LOW PRIORITY -- GPU, 1.5 hrs, load test; gated on B2 PASS)
Pointer: Section 4 Patch A (self-healing + concurrency) + Section 10 HP1/HF1 of research note
Substrate-product reading: Validates whether the Misra-Gries background aggregator causes
  throughput degradation under concurrent query load in the 3-stage parallel architecture.
  The 2x drill identified this risk (P=0.55 that concurrency degrades throughput > 50%
  at 10 QPS). This anchor runs 300 queries at 5 QPS for 60 seconds through the composed
  pipeline with background Misra-Gries running. Measures throughput + latency under load.
Tier hint: GPU; 300 queries; Misra-Gries running in background thread.
Dependency: B2 must PASS first. No point load-testing a pipeline that fails at 1 QPS.
HARD-PASS: throughput >= 4 QPS at 5 QPS target; P90 latency <= 1.5s.
HARD-FAIL: throughput < 2.5 QPS; OR P90 > 3s; OR Misra-Gries update latency P90 > 200ms.
  If HARD-FAIL: move Misra-Gries to subprocess (asyncio.subprocess or multiprocessing.Process);
  investigate Python GIL interaction with PyTorch tensor operations.

---

## Context pointers

- Research note (this drill): notes/research_drill_composition_cascade_closure_3x_2026-06-07.md
- Prior 2x composition drill: notes/research_drill_v11_composition_risks_2x_2026-06-07.md
- Prior 2x handoff: notes/exp_dev_handoff_research_v11_composition_risks_2026-06-07.md
- Bridge-ID 2x drill: notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md
- Sleep defrag 2x drill: notes/research_drill_sleep_defrag_scaling_adversarial_2x_2026-06-07.md
- Pattern B 3x drill: notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
- Post-compaction brief (afternoon): notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

## Contract

B1 (pre-test) must complete before B2 (decisive test). B3 depends on B2 results (uses B2 output data). B4 is independent of B2 (can run in parallel; requires Qwen only, not the full pipeline). B5 requires B2 PASS.

If B2 returns HARD-FAIL: do NOT proceed to B3/B5. File a diagnosis note identifying which specific component is failing (NER accuracy? Retrieval hit rate? Qwen coherence?). The diagnosis gates the architectural decision: is this a tuning failure (within the 3-stage architecture) or a fundamental architecture failure requiring redesign?

If B2 returns MIDDLE-BAND: proceed to B3 and B4. Use per-query data from B2 to identify the weakest component. The 3x research note's Section 4 (patch priority stack) gives the sequencing: Patch A (already applied in B2 setup) -> Patch B (top-15, already applied) -> Patch C (two-tier Misra-Gries, 2 days) -> Patch D (entity encoder, 3-5 days).

## Autonomy declaration

Exp_dev designs all sweep parameters, threshold formulas, script implementations, and queue routing. This file provides task framing and empirical context only. The component integration sequence, file format for telemetry logging, and specific Qwen prompt template are exp_dev's design decisions.
