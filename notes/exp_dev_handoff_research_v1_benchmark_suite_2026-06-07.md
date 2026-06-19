# exp_dev hand-off -- research: v1 benchmark suite definition

Filed-by: research sub-agent
Trigger: notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md
Date: 2026-06-07

Per [[feedback-no-experiment-design-in-prompts]]: this file names WHAT to test, not HOW to implement it. Exp-dev decides implementation.

---

## Pause state block

Check data/orchestrator_paused.flag before acting. If paused, do not queue. File this as a pending handoff.

---

## Anchor candidates (rank-ordered)

### 1. MuSiQue K-hop pre-test (tier: CPU smoke)
- Anchor pointer: K-hop retrieval recall on MuSiQue multi-document format
- Substrate-product reading: K=3 cross-document hop, 50-question pilot, recall@2hop and recall@3hop + F1 vs bare Llama-1B baseline on same questions
- Tier hint: CPU smoke (no GPU needed; 50 questions, Llama-1B inference)
- Why-now: Highest P_actionable in the suite (0.57 before deflation). Pre-test gates the entire MuSiQue engineering track. Research predicts recall@2hop >= 70%; HARD-FAIL if < 50%.
- HARD-PASS: recall@2hop >= 70%, F1 improvement >= 10pp vs bare Llama-1B
- HARD-FAIL: recall@2hop < 50% OR F1 improvement < 5pp

### 2. LongMemEval temporal pre-test (tier: CPU smoke)
- Anchor pointer: LongMemEval 50-question pilot, temporal category (as_of queries)
- Substrate-product reading: Session history parser -> substrate temporal insertion (with timestamps) -> Llama-1B generation conditioned on retrieved facts -> accuracy on temporal + knowledge-update question subcategory
- Tier hint: CPU smoke
- Why-now: P_deflated = 0.33 (below 0.35 authorization threshold). Pre-test MUST validate Llama-1B follows retrieved context over parametric memory before engineering authorization. This is the highest-risk empirical assumption in the suite.
- HARD-PASS: temporal category accuracy >= 60% on pilot; Llama-1B demonstrably follows retrieved context
- HARD-FAIL: temporal accuracy < 40% OR Llama-1B ignores retrieved context (context-vs-parametric failure)

### 3. TruthfulQA coverage analysis (tier: CPU, 1 hour)
- Anchor pointer: TruthfulQA 817-question topic classification; identify what fraction overlap with a Wikipedia-derived knowledge store
- Substrate-product reading: topic analysis (offline text classification) + sample population of 100 questions; run MC1 accuracy with substrate-conditioned Llama-1B
- Tier hint: CPU
- Why-now: P_deflated = 0.25 (conditional on coverage). Pre-test gates TruthfulQA track. Research predicts >= 60% coverage; HARD-FAIL if < 40%.
- HARD-PASS: coverage >= 60%, MC1 improvement >= 15pp vs bare Llama-1B
- HARD-FAIL: coverage < 40%

### 4. FActScore 20-entity pilot (tier: CPU, 1-2 hours)
- Anchor pointer: 20-entity Wikipedia biographical fact extraction -> substrate ingestion -> Llama-1B generation -> SAFE or simple NLI-based fact verification
- Substrate-product reading: FActScore on 20 pre-populated entities; compare to Llama-1B generation on same entities without substrate
- Tier hint: CPU
- Why-now: P_deflated = 0.31 (below 0.35 threshold). Pilot gates engineering authorization. Infrastructure dependency: entity fact extraction pipeline.
- HARD-PASS: FActScore >= 65% for pre-populated entities
- HARD-FAIL: FActScore < 45%

### 5. StreamingQA fact-insertion pilot (tier: CPU, 1-2 hours)
- Anchor pointer: 50 post-cutoff StreamingQA questions; manually insert relevant facts; run QA generation; check accuracy
- Substrate-product reading: confirms online extension pipeline works for benchmark facts; validates the 0% -> 100% jargon injection pattern generalizes to StreamingQA format
- Tier hint: CPU
- Why-now: P_deflated = 0.33. Pilot gates streaming pipeline engineering. High strategic value (continual learning narrative).
- HARD-PASS: accuracy >= 75% on manually-inserted facts
- HARD-FAIL: accuracy < 50%

---

## Context pointers (file paths)

- Research note: d:/AI/hd-instrument/notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md
- Production architecture lock: d:/AI/hd-instrument/notes/production_architecture_locked_2026-06-07.md (Llama-1B BASE + left-pad + PCA preferred)
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md (K-hop rows, causal rows, temporal rows)
- Pre-flight checklist: per [[feedback-cloud-dispatch-pre-flight-checklist]] -- all anchors above are CPU, no cloud dispatch needed for pilots

---

## Contract section

Exp-dev: run pilots 1 and 2 first (MuSiQue + LongMemEval pre-tests). They gate the highest-P benchmarks. Do not commit engineering to full benchmark runs before pre-tests pass. All pilots are CPU-only and should run on remote_cpu_queue per [[feedback-route-gpu-vs-cpu-by-torch-not-N]].

## Autonomy declaration

Exp-dev has full autonomy on: script implementation, evaluation harness design, fact extraction pipeline approach, and scheduling order within the ranked list above. Research has specified WHAT to measure (recall metrics, F1, accuracy, HARD-PASS/HARD-FAIL thresholds). HOW to measure is exp-dev's decision.
