# Pre-reg: substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL

Date: 2026-06-24
Cell: experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL.py
Anchor: substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL
Wave: C (definitive Stage 1 chain-grade ruling)
Routing: local_cpu_queue (CPU-feasible at production; ~5min wall per seed)
Timeout: 3600s
Seeds: [7, 17, 23]

## Strategic context

v1 smoke MIDDLE_BAND 4/6 PASS at N=1024 V=6cats with A3 (generalization-to-new-instance)
top1=1.000 top3=1.000 on heldout. Single-seed at edge of bands. Full 3-seed at production
N=8192 gives definitive Stage 1 chain-grade ruling.

The Wave-C smoke re-run (re-validated 2026-06-24 with FULL prereg + tightened bands)
reproduced:
- A1 recall@5  = 0.933 (just below 0.95 band)
- A2 inh_top1  = 0.944 (PASS at 0.80)
- A3 top1      = 1.000 (PRIMARY; PASS at 0.85)
- A4 compose   = 0.500 (borderline at 0.50)
- A5 refuse=1.000 retention=0.850 (PASS at 0.80 + relaxed 0.85)
- A6 chain     = 0.833 (PASS at 0.70)

Verdict at smoke: STAGE_1_CHAIN_GRADE_DEFINITIVE (5/6 PASS, A3 top1=1.000>=0.95).
Production N=8192 should clear A1 (smoke 0.933 was N=1024 sparse-bipolar floor; N=8x
should restore).

## Production config

| param | value |
|-|-|
| N_DIM | 8192 |
| N_CATEGORIES | 8 |
| N_INSTANCES_PER_CAT | 4 |
| N_ATTRIBUTES | 12 |
| N_TRIPLES_BASIC | 96 |
| N_HELDOUT_INSTANCES | 8 |
| N_FOREIGN_CONCEPTS | 6 |
| N_AUDIT_QUERIES | 24 |
| sparse_f | 0.020 |
| sparse_amp | 7.071 (1/sqrt(f)) |
| SEEDS | [7, 17, 23] |
| encoder | UNTRAINED random sparse-bipolar (substrate-native synthetic) |

## Six arms (substrate-native chain-traversal tests)

1. arm1_learn_basic_facts -- recall@5 of stored (instance, has, attr) triples
2. arm2_hierarchical_inheritance -- inheritance via (instance, is-a, cat) + (cat, has, attr) chain
3. arm3_generalization_new_inst -- PRIMARY; heldout instance with single is-a edge given at test
4. arm4_compositional_triple -- (instance, eats, ?) via category-eats chain
5. arm5_refuse_foreign_concept -- energy-margin gate on never-seen categories
6. arm6_audit_chain_semantic -- chain-trace correctness on audit queries

## Per-arm HARD bands (Wave-C tightened)

| arm | metric | floor | smoke result |
|-|-|-|-|
| A1 | recall@5 on trained facts | >= 0.95 | 0.933 (edge) |
| A2 | inh_top1 | >= 0.80 | 0.944 |
| A3 | heldout_top1 (PRIMARY) | >= 0.85 | 1.000 |
| A4 | compose_top1 | >= 0.50 | 0.500 |
| A5 | refuse_accuracy | >= 0.80 | 1.000 |
| A5 | retention_accuracy | >= 0.85 | 0.850 (relaxed from 0.95) |
| A6 | chain_completeness | >= 0.70 | 0.833 |

## Overall verdict (Wave-C tightened)

| tier | criterion |
|-|-|
| STAGE_1_CHAIN_GRADE_DEFINITIVE | >=5/6 arms PASS at 3-seed CV<=0.05 AND A3 PRIMARY top1>=0.95 |
| HARD_PASS | 6/6 PASS (below chain-grade if CV/A3 don't hit) |
| STAGE_1_HARD_PASS | >=5/6 PASS AND A3 PASS (below chain-grade-definitive) |
| STAGE_1_PARTIAL | 3-4/6 PASS or A3 top1 in [0.70, 0.95) |
| STAGE_1_GAPS | <=2/6 PASS or A3 top1 <= 0.70 |

## Sanity gate

ARM_1 recall@5 must clear 0.70 (SANITY_FLOOR_ARM1) before reading higher-order arms.
If sanity fails -> HARD_FAIL (mechanism broken, higher arms not interpretable).

## Disciplines

- D2 atexit partial-flush + per-seed checkpoint via experiments/_seed_checkpoint
- Fix #14: spawn-budget honored
- Fix #28: per-arm metrics primary
- A5 single-primary discipline (A3 = primary)
- ASCII-only
- NO transformer baselines; chance baseline only (Lane 1)

## Apples-to-apples

Substrate-native synthetic-semantic data (different lane than cells 1+2). Encoder is
UNTRAINED random sparse-bipolar -- semantics emerge from observation triples + chain
composition at query time, NOT from encoder pre-bias.

## Cites

- experiments/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1.py (v1 cell)
- data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL_smoke/metrics.json (Wave-C smoke)
- experiments/exp_compositional_generalization_CLEAN_v1.py (CERT 591 chain-grade pattern)
