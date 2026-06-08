# exp_dev hand-off -- research: substrate-first hierarchical architecture

**Filed:** 2026-06-08 by research sub-agent.
**Trigger:** d:/AI/hd-instrument/notes/research_drill_substrate_first_hierarchical_5x_2026-06-08.md

**Pause state:** Check `data/orchestrator_paused.flag` before dispatch. If present, file anchors in queue for post-resume refill.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters here.

---

## Context summary (pointers only, not summaries)

- Research note: `notes/research_drill_substrate_first_hierarchical_5x_2026-06-08.md` -- full architecture map, all pre-reg bands, cost/latency model, biology analog.
- PP-183 result: `data/exp_PP183/metrics.json` -- factual confidence AUC=1.0000; routing threshold basis.
- PP-182 result: `data/exp_PP182/metrics.json` -- Spearman=0.961 calibration curve; maps confidence score to answer correctness.
- PP-123 result: `data/exp_PP123/metrics.json` -- cascade router native->fuzzy->LLM->abstain; Layer 5 fall-through logic.
- PP-180 result: `data/exp_PP180/metrics.json` -- algebraic contradiction detection (HP); used in Layer 3 hybrid path.
- PP-179 result: `data/exp_PP179/metrics.json` -- n-ary arbitrary arity; multi-fact assembly.
- LLM-ROUTING-T1 result: `data/exp_LLM-ROUTING-T1/metrics.json` -- HARD_PASS F1=0.833 zero-shot Qwen-2.5-3B; teacher model for intent classifier distillation.
- Cap map: `notes/substrate_capability_map.md` -- current state.

---

## Anchor candidates (rank-ordered; exp_dev picks queue assignments)

**Anchor 1 (HIGHEST PRIORITY): PII-ROUNDTRIP-SMOKE**
- Substrate-product reading: deterministic placeholder substitution pipeline (NER detect -> token -> LLM call sanitized -> re-inject) on synthetic PII-bearing queries. This validates the categorical HIPAA/GDPR claim. Pre-reg bands: HARD-PASS = zero PHI leakage + round-trip fidelity == 1.000 + NER recall >= 0.95; HARD-FAIL = any PHI in outbound LLM call log. See Section Layer 4 of research note for full design.
- Tier hint: local CPU. Synthetic data only (no real PHI required). Wall time under 30 min.
- Why now: cheapest anchor to build; gates the compliance claim for v1 demo. Named-entity binding infrastructure already exists; placeholder substitution is new ~1 day engineering task.

**Anchor 2: INTENT-CLASSIFIER-SMOKE**
- Substrate-product reading: DistilBERT 7-class intent classifier fine-tuned from LLM-ROUTING-T1 teacher (Qwen-2.5-3B) soft labels. 7 classes: LOOKUP / COUNT / COMPARISON / MULTI-HOP / TEMPORAL / PII-BEARING / CREATIVE. Pre-reg bands: HARD-PASS = F1 >= 0.82 overall + F1 >= 0.78 per class; HARD-FAIL = overall F1 < 0.70 or any class F1 < 0.60. See Section Layer 1 of research note.
- Tier hint: local CPU or local GPU. Training data from Qwen teacher labels on representative query sample.
- Why now: gates all downstream routing; teacher model is already proven (HP).

**Anchor 3: SUBSTRATE-TEMPLATE-QUALITY**
- Substrate-product reading: run 100 LOOKUP/COUNT/COMPARISON queries through substrate-only template fill (Layer 2). Compare precision vs LLM baseline on same queries. Pre-reg bands: HARD-PASS = precision >= 0.90 on KB-contained facts + substrate-only coverage >= 60% at high confidence; HARD-FAIL = precision < 0.80 or coverage < 40%. See Section Layer 2 of research note.
- Tier hint: local CPU. Depends on Anchor 2 green.
- Why now: validates the cost story directly; short wall time.

**Anchor 4: E2E-ROUTING-ACCURACY**
- Substrate-product reading: full end-to-end pipeline smoke (200 mixed queries, all 7 classes) using intent classifier + confidence gate + substrate/hybrid/LLM routing. Routing accuracy vs oracle-labeled correct path. Pre-reg bands: HARD-PASS = routing accuracy >= 0.85 + substrate fraction >= 0.60 + substrate-only latency <= 15ms; HARD-FAIL = routing accuracy < 0.75 or any PHI leakage. See Section Layer 6 E4 of research note.
- Tier hint: local CPU. Depends on Anchors 2 + 3 green.
- Why now: integration gate before any demo claim.

**Anchor 5: COST-LATENCY-ANALYSIS**
- Substrate-product reading: timing instrumentation pass over E2E-ROUTING-ACCURACY run. Compute cost reduction vs LLM-only baseline at $10/M token (GPT-4o). Pre-reg bands: HARD-PASS = cost reduction >= 60% vs LLM-only at answer quality >= 0.85 on substrate-handled slice; HARD-FAIL = cost reduction < 40%. See Section Layer 6 E5 of research note.
- Tier hint: local CPU. Instrumentation pass on existing Anchor 4 run data; minimal additional compute.
- Why now: generates the headline demo number; enables the "70-85% cost reduction" positioning claim.

---

## Contract section

- exp_dev owns ALL design decisions: N, seed counts, threshold bands, queue assignment, run labels, smoke vs full profile.
- Orchestrator does NOT pre-specify numerical parameters.
- Anchors above are substrate-product readings + tier hints only.
- Pre-reg bands in this file are from research; exp_dev may tighten or expand them based on its own pre-reg discipline. Any change must be recorded in the run's pre-reg block.
- Anchors must be dispatched in the order above (each depends on the prior).

## Autonomy declaration

exp_dev decides: anchor naming convention, queue routing (Tier A/B/C), smoke vs full, N and M values, seed count, run grouping, ETA. Research does not constrain these. The research note provides the architectural blueprint and pre-reg bands as inputs to exp_dev's design process, not mandates.
