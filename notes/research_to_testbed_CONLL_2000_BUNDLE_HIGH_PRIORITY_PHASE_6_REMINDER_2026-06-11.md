# Research -> Testbed: CoNLL-2000 chunking data bundle HIGH PRIORITY + Phase 6 parameterization reminder + math batch 03 Phase A1 + 4 retrieval histories ingest

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Exp-Dev Priority 3 chunking DATA-BLOCKED on CoNLL-2000 + Phase 6 parameterization Day 2 readiness

## TL;DR

- **CoNLL-2000 bundle HIGH PRIORITY**: Exp-Dev Priority 3 chunking blocked; standard CoNLL-2000 train.txt/test.txt -> experiments/data/conll2000.json with tokens/pos/chunk_bio
- **Phase 6 parameterization GO** (per Findings 16 Q2 YES): math batch 03 Phase A1 (30 atoms) + 4 retrieval histories (4 atoms) ready for ingest via parameterized evolve.py
- Math batch 03 Phase A1 JSONL ready: data/substrate_index/math_corpus_batch03_phase_A.jsonl
- 4 retrieval histories JSONL ready: data/substrate_index/concept_corpus_retrieval_histories_findings_14.jsonl
- Hypothesis 1 status check requested (Phase 1 evolve.py NOVEL drop verdict)

## Priority 1: CoNLL-2000 chunking data bundle

Exp-Dev Priority 3 chunking cell DATA-BLOCKED. Per their note:
- `load_dataset('conll2000')` + `eriktks/conll2000` use script-based loaders the installed datasets version rejects
- `tomaarsen/conll2000` doesn't exist
- Not in HF cache; runner has no network

Bundle request:
- Source: standard CoNLL-2000 distribution
- Format: experiments/data/conll2000.json with tokens / pos / chunk_bio fields
- Splits: train + test (standard CoNLL-2000 splits)
- Validation: BIO-format chunk labels match standard distribution

UD-EWT fallback is CIRCULAR (UD-EWT chunk labels DERIVED from POS → POS-cascade tests tautologically). Clean Priority 3 test requires human-annotated CoNLL-2000.

This is HIGH PRIORITY because:
- Tier 4 first-appearance validation (substrate-extracted methodology rule RULE_count_nb_to_discriminative_perceptron via PP-364 POS-HMM -> chunking cascade)
- Transfer-conditions framework P1 prediction (HARD-PASS chunk-F1 >= 0.93)
- Dual-purpose substrate-product milestone

Time estimate: similar bundling to past datasets (ATIS / AG-News / UD-EWT); ~30-60 min.

## Priority 2: Phase 6 parameterization (per Findings 16 Q2 answered YES)

Generic phase function spec per my response:
```python
def evolve_phase_N(
    source_glob: str,
    target_partition: str,
    pre_register_hypothesis: Optional[Dict],
    ingest_validator: Callable,
    re_classification_subset: Optional[List[str]] = None,
):
    ...
```

Day 2 invocations ready:
- **Phase 6a**: math batch 03 Phase A1 ingest
  - source_glob: "data/substrate_index/math_corpus_batch03_*.jsonl"
  - target_partition: math
  - pre_register: 30 new T1/T2/T3 atoms (foundational + Findings 11 ACCEPT)
  - expected post-ingest: math partition 60 → 90 atoms; new DEPENDS_ON edges to brain-analogue primitives
- **Phase 6b**: 4 retrieval histories ingest
  - source_glob: "data/substrate_index/concept_corpus_retrieval_histories_*.jsonl"
  - target_partition: concept
  - pre_register: 4 new capability atoms with solution_history fields
  - expected: concept partition 62 → 66 atoms; structural-binding rule promotion from n=1 to n=3 medium-confidence

Day 2-3 continuing:
- Phase 6c-6h: math batch 03 Phase A2-A7 (Research authoring; 30-50 atoms per batch)
- Phase 6i+: science batch 01 part 1+ (physics + biology priority Day 3-4)

## Priority 3: Phase 1 Hypothesis 1 verdict status check

Per Findings 16 + my response: pre-registered NOVEL drop validation in flight.

HARD-PASS (predicted): NOVEL post-ingest < 10% on drill files
MIDDLE: 10-30% NOVEL
HARD-FAIL: NOVEL >= 30% (substrate-eval recall problem; investigate before further ingest)

Status check requested. If HARD-PASS: confirms substrate-self-referential pipeline; continue Phase 2-5 + Phase 6.

If MIDDLE/HARD-FAIL: pause + diagnose before Phase 6 invocation.

## Priority 4: Phase 2-5 status check

Background task running Phase 2-5 (decision_history + findings_history + verdict_history + results_history).

Expected state post-Phase-2-5:
- decision_history populated (~60+ atoms from research_to_*.md + testbed_to_*.md routings)
- findings_history populated (~16+ atoms from testbed_to_research_INDEX_FINDINGS_*.md)
- verdict_history populated (~20+ atoms from exp_dev_to_research_*.md)
- results_history populated (1+ atom from strategy_decisions_2026-06-11.md)

Status check requested.

## Substrate state target post Day 2

| Source | Atoms added | Total |
|---|---|---|
| Pre Phase 1 | -- | 134 |
| Phase 1 (research_history) | 449 | 583 |
| Phase 2-5 (decision/findings/verdict/results history) | ~100+ | ~683+ |
| Phase 6a (math batch 03 Phase A1) | 30 | ~713+ |
| Phase 6b (4 retrieval histories) | 4 | ~717+ |
| Phase 6c-6h (math batch 03 Phase A2-A7 over Day 2-3) | 200-400 | ~917-1117 |
| Phase 6i+ (science batch 01) | 200-400 Day 3-4 | ~1100-1500 |

Substrate corpus approaching 1000+ atoms within Day 2-3. Cycle #14 BMA corpus-deficiency root cause addressed at scale.

## Cross-references

- Findings 16 + my response: notes/research_to_testbed_FINDINGS_16_Q1_Q2_Q3_ANSWERED_2026-06-11.md
- Math batch 03 Phase A1: data/substrate_index/math_corpus_batch03_phase_A.jsonl + research_to_testbed_MATH_BATCH_03_PHASE_A_30_ATOMS_READY_2026-06-11.md
- 4 retrieval histories: data/substrate_index/concept_corpus_retrieval_histories_findings_14.jsonl
- USER math+science ingestion: notes/research_to_testbed_USER_MASSIVE_MATH_SCIENCE_INGESTION_PRIORITY_2026-06-11.md
- Exp-Dev Priority 3 DATA-BLOCK: notes/exp_dev_to_research_PRIORITY3_DATA_BLOCKED_CONLL2000_CYCLE_SUMMARY_2026-06-11.md
- Substrate-as-self-extending-engine memory + BMA corpus-deficiency memory

---

**Testbed:** Priority 1 CoNLL-2000 bundle HIGH PRIORITY Exp-Dev Priority 3 chunking blocked + Priority 2 Phase 6 parameterization GO Day 2 invocations math batch 03 Phase A1 30 atoms (math partition; Phase 6a) + 4 retrieval histories (concept partition; Phase 6b) ready + Phase 6c-6h continuing Day 2-3 math batches + Phase 6i+ science batches Day 3-4 + Priority 3 Hypothesis 1 verdict status check requested HARD-PASS predicted < 10pct NOVEL drop + Priority 4 Phase 2-5 status check requested ~100+ atoms across decision/findings/verdict/results history partitions + substrate state target post Day 2 ~1000+ atoms + monitor strengthened sender-agnostic wildcards + mtime-aware + persistent + pre-populated seen_file (no testbed notes missed; latest acknowledged = Findings 16).
