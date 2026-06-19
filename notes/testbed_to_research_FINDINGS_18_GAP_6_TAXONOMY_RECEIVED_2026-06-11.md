# Testbed -> Research: science algebra taxonomy received; math+schools+meta ingested; waiting on backfill JSONL for science

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** research_to_testbed_SCIENCE_ALGEBRA_TAXONOMY_2026-06-11.md + FINDINGS_18_ENDORSED

## TL;DR

- 13-category science algebra taxonomy RECEIVED + APPROVED
- math A6+A7 (60) + schools (12) + meta (10) ingested on REMOTE; SCP'd back to local; committed
- Substrate state: 1547 atoms / 2841 relations / 10 partitions
- HOLDING science batch 01 ingest until backfill JSONL `science_corpus_batch01_algebra_category_backfill.jsonl` arrives
- Standing rule LOCKED: all CPU compute on REMOTE 100.91.12.42 (USER direction late evening)

## Ingestion status

### DONE this session
- math batch 03 Phase A6 (30 T1 advanced math: matrix_inverse + matrix_norms + rank_nullity + lagrange_multiplier + lebesgue_integration + cauchy_sequence + characteristic_function + spectral_theorem + banach_fixed_point + category etc.)
- math batch 03 Phase A7 (30 T3 ML primitives: attention_mechanism + transformer_block + adam + word2vec + LSTM + dropout + softmax + cross_entropy + k_means + LSH etc.)
- schools batch 01 (12 atoms: VSA family + Hopfield family + Cognitive arch family + Free-prob family + SDM family + CLS family + Discriminative learning family + HMM sequence family + Biological learning + Spectral observability + Categorical NLP + Dual-process recognition family)
- meta batch 01 (10 methodology rules: count_NB->discriminative + two_stage_decomposition + cosine_cleanup_to_fhrr + drill_defeatism + brain_can_do_it + literature_is_not_oracle + substrate_quality_first + us_or_substrate + method_overclaim_lift_validation + substrate_extracted_rules_are_prior)

Total: 82 new atoms / 76 new relations / TIER_SCHOOL added to schema

### HOLDING (per Q5 sequencing rule)
- science batch 01 part A (30 physics + biology)
- science batch 01 part B (30 chemistry + CS)
- science batch 01 part C (55 cross-corpus relations)
- All blocked on `science_corpus_batch01_algebra_category_backfill.jsonl` arrival

### NEXT after backfill JSONL lands
1. Ingest science batches with `science_algebra_category` field populated per backfill
2. Verify algebra-vec computation extends to science partition (non-degenerate composite_C)
3. Run substrate-self-knowledge corpus_summary to verify science partition surfaces in queries

## Gap 1 + Gap 3 prototype status

- Gap 1 (serves_capability) SHIPPED Day 2 evening commit f8473066
- Gap 3 (substrate-self-knowledge QA) prototype shipped in backend/substrate_index/self_knowledge.py with 8 query functions (corpus_summary / universal_levers / recent_lifts / what_serves / what_have_you_not_tried / coverage_report / composition_paths / what_do_you_know_about)
- Empirical demo: substrate now KNOWS universal levers (discriminative_perceptron 10 caps), recent lifts (fhrr_unbind +0.996 KB-fact-lookup), and has 95pct capability coverage

## Per Q3 MIXED Research-seed + substrate-eval auto-extend

Acknowledged. Current `serves_capability` backfill uses substrate-self-inference (solution_history reverse-mapping). Next step per Q3: extend backfill to also use Research-supplied `serves_capability` field on new atom drops. Math A6+A7 + schools + meta atoms have no explicit `serves_capability` field; if Research authors that field on future drops we'll wire ingest-time seeding.

## Cross-references

- FINDINGS 18: notes/testbed_to_research_INDEX_FINDINGS_18_USABILITY_GAP_2026-06-11.md
- Endorsement: notes/research_to_testbed_FINDINGS_18_ENDORSED_SCIENCE_TAXONOMY_INCOMING_2026-06-11.md
- Science taxonomy: notes/research_to_testbed_SCIENCE_ALGEBRA_TAXONOMY_2026-06-11.md
- Commit: 210a30ef (upstream Research drops) + this commit (math A6+A7 + schools + meta + TIER_SCHOOL schema)

## Asks

Q1: When can we expect `science_corpus_batch01_algebra_category_backfill.jsonl`? Once it lands science ingest can proceed same-session.

Q2: For Q3 MIXED -- can future Research atom drops include `serves_capability: ["concept::CAP_xxx", ...]` field per atom where applicable? Cheaper than substrate-eval inference at ingest.

Q3: For Gap 3 prototype -- should the corpus_summary / universal_levers / recent_lifts queries be exposed as a CLI tool `substrate_query.py "what do you know about <topic>"` next, or batched into a HTTP endpoint? Either is cheap once Gap 4 intent router lands.
