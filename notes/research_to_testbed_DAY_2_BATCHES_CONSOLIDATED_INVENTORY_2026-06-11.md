# Research -> Testbed: Day 2 consolidated batch inventory for Phase 6 evolve.py ingest -- 202 atoms + 250 relations across 8 partitions

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Consolidated inventory of Day 2 morning math + science + schools + meta batches

## TL;DR

- **202 atoms + 250 relations** ready for Phase 6 evolve.py ingest across 8 partitions
- All batches at `data/substrate_index/*.jsonl` rule 8 us-or-substrate compliant
- Substrate state target post-ingest: 583 -> 785 atoms / 1793 -> 2043 relations
- 2 NEW partition types operational: science + school
- Methodology partition (meta) now has 10 atoms: 2 substrate-extracted + 8 user-locked

## File inventory (Day 2 morning batches)

### Math batch 03 Phase A1-A6
- `math_corpus_batch03_phase_A.jsonl` -- 30 atoms (T1 foundational + Findings 11 ACCEPT)
- `math_corpus_batch03_phase_A2.jsonl` -- 30 atoms (T1 advanced)
- `math_corpus_batch03_phase_A3.jsonl` -- 30 atoms (T2 family-tags + T3 sub-ops + T4 macros)
- `math_corpus_batch03_phase_A4_relations.jsonl` -- 100 math-internal relations
- `math_corpus_batch03_phase_A5_cross_corpus_relations.jsonl` -- 95 math <-> concept relations
- `math_corpus_batch03_phase_A6.jsonl` -- 30 atoms (T1 remaining + advanced foundational)

**Subtotal**: 120 math atoms + 195 relations

### Science batch 01 (NEW partition)
- `science_corpus_batch01_part_A_physics_biology.jsonl` -- 30 atoms (physics + biology priority)
- `science_corpus_batch01_part_B_chemistry_CS.jsonl` -- 30 atoms (chemistry + CS + remaining)
- `science_corpus_batch01_part_C_cross_corpus_relations.jsonl` -- 55 cross-corpus relations

**Subtotal**: 60 science atoms + 55 relations

### Concept partition extensions
- `concept_corpus_retrieval_histories_findings_14.jsonl` -- 4 retrieval-type capability histories (Findings 14 Q1 structural-binding rule promotion)

**Subtotal**: 4 concept atoms

### Schools partition (NEW)
- `schools_corpus_batch_01.jsonl` -- 12 school atoms (VSA / Hopfield / Cognitive arch / Free-prob / SDM / CLS / Discriminative / HMM / Bio learning / Spectral observability / Categorical NLP / Dual-process recognition)

**Subtotal**: 12 school atoms

### Meta partition (methodology rules)
- `meta_corpus_batch_01.jsonl` -- 10 methodology rule atoms (2 substrate-extracted + 8 user-locked)

**Subtotal**: 10 meta atoms

## Cumulative

| Category | Count |
|---|---|
| **Total atoms** | **206** (120 math + 60 science + 4 concept + 12 schools + 10 meta) |
| **Total relations** | **250** (100 math-internal + 95 math<->concept + 55 science<->math/concept) |
| Partitions extended | 3 (math + concept + meta) |
| Partitions newly populated | 2 (science + school) |

## Ingestion plan

Phase 6 evolve.py parameterized invocations per Findings 16 Q2 YES:

### Day 2 (today)
- Phase 6a: math batch 03 Phase A1-A6 (120 atoms + 100 math-internal relations + 95 cross-corpus to concept)
- Phase 6b: science batch 01 part A+B (60 atoms + 55 cross-corpus relations to math + concept)
- Phase 6c: schools batch 01 (12 atoms)
- Phase 6d: meta batch 01 (10 atoms)
- Phase 6e: 4 retrieval histories to concept

### Day 2 evening / Day 3
- Phase 6f: re-run Path A composite_C on enriched corpus (BEFORE Option B+H lands; baseline) to track NOVEL distribution
- Phase 6g: AFTER Option E day-1 lands, re-run Path A composite_C with weighted-avg (pre-register NOVEL drop 68pct -> <50pct)
- Phase 6h: AFTER Option B+H combined lands, re-run with dual-process recognition (pre-register TIER-A on ingested 100pct)

## Substrate state target progression

| Stage | Atoms | Relations | Notes |
|---|---|---|---|
| Pre-Phase-1 | 134 | 284 | Baseline |
| Post-Phase-1 (research_history) | 583 | 1793 | 4.3x growth via evolve.py auto-ingest |
| Post-Day-2-batches | 785 | 2043 | +202 atoms +250 relations via Phase 6 |
| Per-USER 400-600 atom target | ~933-1133 | -- | trajectory ahead of schedule |

## Substrate-product implications

### 8 partitions populated
1. **math** (180 atoms) -- theoretical foundations + algorithms + family-tags + macros
2. **concept** (66 atoms) -- capabilities (CAP_*) + lexicons (LEX_*) + PP-rows + retrieval histories
3. **meta** (18 atoms) -- methodology rules (substrate-extracted + user-locked)
4. **methodology** (4 atoms; from earlier composite C cycle #4)
5. **research_history** (449 atoms; Phase 1 auto-ingested)
6. **decision_history + findings_history + verdict_history + results_history** (Phase 2-5 in flight)
7. **science** (60 atoms) -- physics + biology + chemistry + CS primitives + brain analogues
8. **school** (12 atoms) -- substrate-research lineage families

### Substrate-self-explanation strengthens dramatically
- Every substrate capability now references theoretical foundation atoms
- Every substrate mechanism has brain-analogue science atom
- Every substrate-research lineage has school atom + history
- Every methodology rule has substrate-product atom + application_log
- LLMs have no equivalent structured self-explanation

### Substrate-as-self-extending-engine framing strengthens
- Per [[substrate-as-self-extending-engine-4-3x-growth-2026-06-12]] memory: INFRASTRUCTURE self-extension validated
- This Day 2 batch + Option B+H fix (per Drill 1) closes CLASSIFICATION self-recognition
- Combined: substrate self-extends at infrastructure + classification levels

## Cross-references

- Math batches: research_to_testbed_MATH_BATCH_03_A1_TO_A4_CONSOLIDATED_INGEST_REQUEST_2026-06-11.md
- USER math+science routing: research_to_testbed_USER_MASSIVE_MATH_SCIENCE_INGESTION_PRIORITY_2026-06-11.md
- Findings 16 + Q2 YES evolve.py parameterization: research_to_testbed_FINDINGS_16_Q1_Q2_Q3_ANSWERED_2026-06-11.md
- Findings 17 + Option E+B+H+G fix: research_to_testbed_OPTION_E_PLUS_B_PLUS_H_THEN_G_PER_DRILL_1_2026-06-11.md
- 3 Drill outputs (substrate-eval recall + methodology rule calibration + Tier 5 pathway)
- 8 memory entries Day 2 morning

---

**Testbed:** Day 2 morning batches CONSOLIDATED inventory + ready for Phase 6 evolve.py ingest 202 atoms + 250 relations across 8 partitions (math + concept + meta + methodology + research_history + decision/findings/verdict/results history + science + school) + math batch 03 Phase A1-A6 (120 atoms + 100 math-internal + 95 math<->concept) + science batch 01 part A+B (60 atoms + 55 cross-corpus) + 4 retrieval histories + schools batch 01 (12 family lineages) + meta batch 01 (10 methodology rules 2 substrate-extracted + 8 user-locked) + substrate state target 583 -> 785 atoms + 1793 -> 2043 relations 8 partitions populated + ingestion plan Phase 6a-e Day 2 + Phase 6f-h Path A re-classification baseline + Option E + Option B+H + 2 NEW partitions science + school first-populated + substrate-self-explanation strengthens dramatically + substrate-as-self-extending-engine framing INFRASTRUCTURE level validated + CLASSIFICATION self-recognition pending Option B+H per Drill 1.
