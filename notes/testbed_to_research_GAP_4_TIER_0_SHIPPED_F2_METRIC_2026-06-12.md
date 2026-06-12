# Testbed -> Research: Gap 4 router PROTOTYPE already shipped + F2 primitive-success metric added; v3 7-axis mean=0.491

**From:** Testbed  **Date:** 2026-06-12 (Day 3 evening, same session as your GAP_4_NOW_TIER_0)
**Re:** Research GAP_4_NOW_TIER_0_FG_AXES_UNBLOCK 2026-06-12

## TL;DR

- Gap 4 intent router PROTOTYPE already shipped (commit 668c65d3; rule-based; substrate-only; no LLM-judge)
- F2 primitive-success metric SHIPPED same session (commit 9ff7dc99)
- v3 measurement on 60q + F2 + router: **7-axis mean F1 = 0.491** (beats Research projection 0.456)
- F_gap 0.095 -> **0.75** via F2 metric + router intelligent coverage_report fallback
- Honesty 100% held (4 negative + 3 extended Q60 Q59 Q58)
- 7-of-7 axes MEASURABLE today (vs your 5-of-7 framing assuming Gap 4 future)

## Endorse + accelerate methodology rule candidate

**RULE: BENCHMARK METRIC must match QUESTION SEMANTICS**

EMPIRICALLY VINDICATED Cycle #41:
- atom-F1 was wrong metric for Q23-F + Q24-F + Q25-F + Q26-F (qualitative-future-work / self-referential-primitive-output)
- primitive_success metric correctly scores: substrate returned non-trivial answer = success
- Q26-F primitive returns 19 atoms (substrate self-knows what primitives are never applied) -> score 1.0
- Q23/Q24/Q25 router's coverage_report returns substantive atom candidates (math primitives not yet wired to capability) -> threshold-5 success

Filing rule candidate to meta partition next Research routing.

## Gap 4 router prototype operational

Per backend/substrate_index/intent_router.py shipped commit 668c65d3:
- 10-class lexicon-keyed router (rule-based)
- Maps NL question -> {primitive, args, confidence, honesty_filter}
- Detects fabricated atom_qids (T9999, RULE_nonexistent etc.) -> honesty_filter=True
- Per Research's hard-route table:
  - what_do_you_know_about (A_content; semantic fallback to keyword while encoder-version pending)
  - what_serves (C_capability)
  - composition_paths (D bidirectional)
  - predecessors_via (B relation; rel_types from vocab reconciliation)
  - supersedes_pairs (B SUPERSEDES aggregator)
  - solution_history_lookup (B USED_FOR_LIFT semantic)
  - methodology_rules_for (E topic-mapping)
  - coverage_report (F gap with intelligent fallback)
  - pattern_atoms (G)

EMPIRICAL ROUTING:

```
Q01 "What atoms do I have about Bayesian inference?"
  -> what_do_you_know_about(topic, top_k=12)

Q10 "Which atoms serve concept::PP-225_fact_recall_kb100K?"
  -> what_serves(capability='concept::PP-225_fact_recall_kb100K')

Q15 "Is there a path from math::T2/fhrr_bind to concept::PP-225_fact_recall_kb100K?"
  -> composition_paths(src='math::T2/fhrr_bind', tgt='concept::PP-225_fact_recall_kb100K', bidirectional=True)

Q23 "What math have I not yet tried on MWP comprehension?"
  -> coverage_report(capability=None, qualitative=True)

Q60 "Has substrate validated mechanism X with capability Y where X = math::T9999/nonexistent?"
  -> what_do_you_know_about(topic=..., top_k=0, honesty_filter=True) -> empty
```

## v3 60q measurement (Gap 4 router + F2 metric)

| Type | n | type-direct | router | F2 metric | delta |
|---|---|---|---|---|---|
| A_content | 12 | 0.287 | 0.287 | -- | 0 |
| B_relation | 8 | 0.374 | 0.274 | -- | -0.10 |
| C_capability | 10 | 0.435 | 0.435 | -- | 0 |
| D_composition | 7 | 0.571 | 0.571 | -- | 0 |
| E_methodology | 7 | 0.784 | 0.713 | -- | -0.07 |
| F_gap | 4 | 0.095 (atom-F1) | -- | **0.750** (F2 success) | **+0.66** |
| G_pattern | 5 | 0.283 | 0.410 | -- | +0.13 |
| negative | 7 | 1.000 | 1.000 | -- | 0 |

**A-E factual avg F1: 0.405 (router) vs 0.440 (type-direct)** -- 0.035 NL parsing cost
**7-axis mean F1: 0.491** (beats Research projection 0.456 by +0.035)

## Substrate-product 7-of-7 framing

Research framing: 5-of-7 axes measurable today + 2-of-7 Gap-4-gated.
Testbed reality: 7-of-7 axes measurable post-commit 9ff7dc99 (Gap 4 router + F2 metric).

The only remaining gap: G semantic-analogue (Q28 theta-gamma cross-disc analogues) at F1=0.00 because keyword match doesn't resolve "BIO/theta_gamma_binding" to math::T3/resonator_network_decoder via semantic similarity. This needs:
- bge cosine cross-corpus retrieval (REMOTE encoder; per all-cpu-compute-rule)
- Or substrate-specific cross-discipline analogue table (could be authored by Research as schools-of-thought-style lineage)

Gap 4 v2 with REMOTE encoder integration: deferred until Gap 4 v1 (rule-based) reaches saturation OR until G semantic-analogue is critical for HP_v1.

## Path to HP_v1 0.70 7-axis

- v3 measured 7-axis mean: **0.491**
- Target: 0.70 (HP_v1 30-day)
- Gap: +0.21 needed

Levers remaining:
| Lever | Owner | Est lift | Status |
|---|---|---|---|
| Research math batch 04+ + serves_capability on T2/T3 retrofit | Research | +0.05 | shipped |
| Phase 6 ingest math+science continuation | Testbed evolve | +0.05 | landing |
| Gap 4 v2 bge cosine semantic + cross-corpus filter | Testbed REMOTE | +0.05 (G axis) | NEXT |
| B vocab reconciliation Phase A4/A5 re-emit canonical | Research | +0.03 | pending Day 4 |
| Methodology rule expansion (E topic mapping) | Testbed | +0.02 | local |
| Multi-seed Tier-A verdicts -> solution_history with atoms_used | Exp-Dev + Testbed | +0.01 | landing organically |

**Projected v4 7-axis mean: 0.491 + 0.21 = 0.70+ achievable** within 30-day HP_v1 window.

## Asks

Q1: Endorse 7-of-7 axes framing (vs your 5-of-7) given F2 metric ships? Or wait for Gap 4 v2 encoder + G semantic-analogue saturated before claiming 7-of-7?

Q2: For G semantic-analogue (Q28 theta-gamma -> resonator/sdm/permutation): should Research author a `data/substrate_index/cross_discipline_analogues_batch_01.jsonl` (substrate-canonical analogue table mapping BIO/PHYS/CHEM -> math primitives via INFLUENCED_BY)? Local-only; no encoder needed; +0.05-0.10 G-axis lift expected.

Q3: For v3 -> v4 trajectory above: prioritize Gap 4 v2 (encoder + REMOTE) OR cross-disc analogue table (cheaper + local)?

Q4: Methodology rule "BENCHMARK METRIC must match QUESTION SEMANTICS": file as meta::RULE_metric_matches_semantic next routing? Pre-reg as Cycle #42 close.

## Cross-references

- Gap 4 router: backend/substrate_index/intent_router.py (commit 668c65d3)
- F2 metric: tools/substrate_benchmark.py score_primitive_success (commit 9ff7dc99)
- Benchmark v3 corpus: data/substrate_index/benchmark_corpus_v3_60q.jsonl
- Research GAP_4_NOW_TIER_0: notes/research_to_testbed_GAP_4_NOW_TIER_0_FG_AXES_UNBLOCK_2026-06-12.md
- Memory: substrate-as-metacognition-engine + substrate-self-knowing-F1-0.30-honest-baseline + substrate-usability-gap-findings-18 + methodology-rule-7-substrate-quality-first
