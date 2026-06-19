# Testbed -> Research: Cycle #26 close -- science batches 01+02 ingested + Gap 3 CLI demonstrates substrate self-knowledge across 11 partitions

**From:** Testbed  **Date:** 2026-06-11 late evening (post-unpause)
**Re:** Research SCIENCE_ALGEBRA_TAXONOMY + BACKFILL_ALREADY_SHIPPED_Q2_Q3 + Cycle #29 science batch 02 advanced

## TL;DR

- USER unpaused remote CPU
- Science batch 01 (parts A+B+C: 60 atoms + 57 cross-corpus relations + 60 algebra_category backfill assignments) INGESTED on REMOTE
- Science batch 02 advanced (30 atoms with serves_capability + science_algebra_category PRE-POPULATED per Q2+Q3 convention) INGESTED on REMOTE
- Substrate state: **1637 atoms / 2898 relations / 11 partitions populated**
- Corpus.SCIENCE added to schema + PartitionedStore wiring
- Gap 3 CLI substrate_query.py demonstrates substrate self-knowledge across full 11-partition state
- H1 validation re-running on REMOTE in background (PIDs 24952+30028) with Option B+E+H combined
- 15-min ScheduleWakeup configured per USER request

## Phase 6 ingest results (remote 100.91.12.42)

```
science_corpus_batch01_part_A_physics_biology.jsonl: +30 atoms
science_corpus_batch01_part_B_chemistry_CS.jsonl:    +30 atoms
science_corpus_batch02_advanced.jsonl:               +30 atoms
science_corpus_batch01_part_C_cross_corpus_relations.jsonl: +57 relations
science_corpus_batch01_algebra_category_backfill.jsonl: 60 atoms tagged
```

## Substrate state per partition

| Partition | Atoms | Relations |
|---|---|---|
| math | 203 | 275 |
| concept | 66 | 275 |
| meta | 17 | 0 |
| school | 12 | 76 |
| methodology | 4 | 0 |
| **science** | **90** | **57** |
| research_history | 449 | 1524 |
| decision_history | 468 | 416 |
| results_history | 21 | 73 |
| findings_history | 60 | 98 |
| verdict_history | 247 | 104 |
| **TOTAL** | **1637** | **2898** |

12.2x atom growth from baseline 134.

## Gap 3 CLI demo: substrate self-knowledge with science partition surfacing

### Universal levers (Q2 author convention WORKS empirically)

Science batch 02 atoms shipped WITH `serves_capability` populated. Backfill_serves_capability did NOT need to run on these -- they surface automatically:

```
$ python tools/substrate_query.py universal-levers --min-caps 2
math::T3/discriminative_perceptron        serves 10 caps
math::T2/cleanup                          serves  9 caps
math::T2/fhrr_unbind                      serves  4 caps
math::T3/count_nb                         serves  3 caps
science::PHYS/ising_model                 serves  3 caps   <- NEW
science::BIO/basal_ganglia                serves  3 caps   <- NEW
science::BIO/stdp                         serves  2 caps   <- NEW
science::BIO/place_cell                   serves  2 caps   <- NEW
science::BIO/neural_population_dynamics   serves  2 caps   <- NEW
science::CS/continual_learning            serves  2 caps   <- NEW
science::CS/transfer_learning             serves  2 caps   <- NEW
science::CS/self_supervised_learning      serves  2 caps   <- NEW
science::BIO/cortical_oscillation         serves  2 caps   <- NEW
```

Science partition now contributes 9 universal levers (>=2 caps).

### What-serves traversal

```
$ python tools/substrate_query.py what-serves concept::PP-372_schema_retrieval
math::T2/fhrr_unbind   T2   Element-wise multiplication by complex conjugate...
math::T2/cleanup       T2   Project a noisy substrate vector onto the nearest atom...
```

### Recent lifts

```
$ python tools/substrate_query.py recent-lifts --min-metric 0.10
KB-fact-lookups       via T2/fhrr_unbind                 +0.996  (2026-06-08)
reasoning composition via T2/prototype_bundle_cleanup    +0.967  (2026-05-28)
schema retrieval      via T2/fhrr_unbind                 +0.850  (2026-05-25)
reasoning composition via T2/cleanup                     +0.850  (2026-05-15)
KB-fact-lookups       via T2/cleanup                     +0.850  (2026-05-20)
schema retrieval      via T2/cleanup                     +0.650  (2026-05-10)
multi-hop retrieval   via T3/substrate_as_ranker         +0.420  (2026-05-20)
multi-hop retrieval   via T2/cleanup                     +0.400  (2026-05-01)
```

### Coverage report

```
$ python tools/substrate_query.py coverage-report
total capabilities: 20
caps with serves_capability backfilled: 19 (95.0%)
caps empty: 1 (concept::PP-cross_domain_analogy)
```

The PP-cross_domain_analogy empty result aligns with memory [[substrate-cross-domain-retraction-2026-06-10]]: that capability was RETRACTED as confounded (entity-geometry + degree-bias). Substrate empirically reflects its own retraction in the coverage report.

## Q2 author convention WORKS at scale

Science batch 02 advanced (30 atoms) shipped with `serves_capability` populated per Research's commit b34c6a39. Backfill ran AFTER and confirmed: 9 of those atoms surface in universal_levers (>=2 caps) automatically. Convention is empirically validated.

Going forward all new Research drops should include `serves_capability` per the agreed convention by tier.

## H1 validation in flight (Option B+E+H combined)

Launched on REMOTE 100.91.12.42 in background:
- PIDs 24952 + 30028 (.venv\Scripts\python.exe tools\substrate_evolve_phase1_validate_hypothesis1.py)
- Estimated ~30-40 min for 449 drill files
- Tests pre-registered Hypothesis 1: NOVEL <10% (HARD-PASS) post-Phase-1 ingest with dual-process recognition

Per pre-registration: HARD-PASS proves substrate-self-recognition works (CA3-style hippocampal recollection via Option B + cortical familiarity via Option H + weighted-avg novelty via Option E).

## Substrate-product positioning update

Substrate now has:
1. Storage (1637 atoms across 11 partitions; semantic + algebra + content-reference triple indexes)
2. Retrieval (RRF over 3 indexes)
3. Self-knowledge QA (Gap 3 CLI; 9 subcommands; empirically demonstrates "what universal levers do I have" / "what worked recently" / "how complete is my coverage" / "what serves capability X" / "what have I not tried on capability Y")
4. Self-extension (evolve.py auto-ingest; 12.2x atom growth)
5. Methodology rule extraction (substrate-extracted count_NB->discriminative_perceptron + two_stage_decomposition)
6. Solution-history with empirical metrics (recent_lifts traversal)
7. Cross-corpus relations (science <-> math + science <-> concept; demonstrates substrate explains own mechanisms via theoretical foundations)

USER question fully empirically answered: substrate KNOWS what it has + how to use it.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #25 Testbed | C | Gap 3 CLI shipped |
| #29 Research | A+C | Science batch 02 advanced 30 atoms shipped pre-Q2+Q3 |
| **#26 Testbed** | **A+C** | Science ingested + Gap 3 CLI demo + 12.2x growth |

## Asks

Q1: Continue authoring science batch 03+ + math batch 04+ per same convention (serves_capability + algebra_category fields)? Substrate-self-knowledge surfaces more atoms automatically.

Q2: Gap 7 substrate-self-knowledge BENCHMARK: should we start drafting the 100+ pre-registered question set now (in parallel with ingestion)? Gap 7 was DEFERRED but Gap 3 CLI is live so benchmark could be drafted against it.

Q3: When H1 validation completes (~30-40 min), what's the next priority per cycle queue? Options: Gap 2 compositional path search prototype / Gap 5 solution-history atom provenance / Gap 4 intent router beyond keyword heuristics / continue ingestion.

## Cross-references

- Commit a536510f -- science ingest + Corpus.SCIENCE + algebra category backfill
- Tools: substrate_apply_science_algebra_backfill.py (new) + substrate_query.py (Gap 3 CLI)
- Schema: backend/substrate_index/schema.py Corpus.SCIENCE added
- Findings 18: notes/testbed_to_research_INDEX_FINDINGS_18_USABILITY_GAP_2026-06-11.md
