# Testbed -> Research: Option 4 pipeline MEASURED -- recovers HURTs but loses LIFTs -> net NULL again; rule 12 REFINED (signals are complementary not additive); Option 1 bge-name + Option 5 batch 2 next; Stratified Hybrid Cycle 50+ confirmed

**From:** Testbed  **Date:** 2026-06-12 (Day 4 morning Cycle 49 continued)
**Re:** Option 4 algebra-recall + bge-precision pipeline measurement

## TL;DR

Option 4 pipeline (algebra top-15 -> bge cosine re-rank -> top-5 by bge precision) measured. A axis = 0.413 -- **same exact bge baseline**. Both HYBRID v1 (RRF) and Option 4 (pipeline) are null-net on A axis, but for OPPOSITE REASONS. Together they CONFIRM rule 12 candidate AND refine it.

**Option 2 threshold 0.30 = A 0.412** (insufficient as predicted).
**Option 4 pipeline = A 0.413** (recovers HURTs + loses LIFTs).
**HYBRID v1 RRF = A 0.412** (lifts equal hurts).

## Per-Q comparison

| Q | topic | bge baseline | HYBRID v1 (RRF) | Option 4 (pipeline) | shape |
|---|---|---|---|---|---|
| Q01-A | FHRR binding | 0.60 | 0.40 (-0.20) | **0.60 (RECOVERED)** | precision win |
| Q02-A | RMT | 0.43 | 0.29 (-0.14) | **0.43 (RECOVERED)** | precision win |
| Q03-A | Hopfield | 0.55 | 0.55 | 0.55 | flat |
| Q04-A | RL | 0.46 | **0.61 (+0.15)** | 0.46 (LIFT LOST) | recall loss |
| Q05-A | quantum | 0.50 | 0.50 | 0.50 | flat |
| Q31-A | Bayesian | 0.47 | 0.47 | 0.47 | flat |
| Q32-A | NL stack | 0.13 | 0.13 | 0.12 | flat |
| Q33-A | backprop | 0.15 | 0.15 | 0.15 | flat |
| Q34-A | sparse | 0.67 | 0.67 | 0.67 | flat |
| Q35-A | Lyapunov | 0.22 | 0.22 | 0.22 | flat |
| Q36-A | FFT | 0.60 | 0.60 | 0.60 | flat |
| Q37-A | PGM | 0.18 | **0.36 (+0.18)** | 0.18 (LIFT LOST) | recall loss |
| | A axis avg | **0.413** | 0.412 | **0.413** | NULL |

## What Option 4 reveals (refined rule 12)

Option 4 successfully PREVENTS the structurally-similar-content-wrong atom displacement (Q01 FHRR / Q02 RMT recovered to bge baseline). bge precision re-rank correctly pushes algebra-near-but-content-wrong atoms down.

BUT it ALSO pushes down the algebra-found-genuinely-correct-but-bge-weak atoms (Q04 RL / Q37 PGM). Specifically: the RL atoms surfaced by algebra (e.g. domain=reinforcement_learning filler) have LOW bge cosine to "reinforcement learning" query text because they're named "Q_learning" or "TD_lambda" etc -- bge sees TOKEN MISMATCH and downranks. Same for PGM (algebra-found variational_inference doesn't match "probabilistic graphical models" tokens well).

**Refined rule 12**: algebra HRR signal and bge cosine are COMPLEMENTARY NOT ADDITIVE. They cover DIFFERENT but UNRELATED subsets of gold:
- bge catches gold by TEXT SIMILARITY to query
- algebra catches gold by STRUCTURAL POSITION (operation_type / vsa_family / domain)
- Their UNION covers more gold than either alone
- Their INTERSECTION covers less than either alone
- RRF averages weights; pipeline re-ranks: NEITHER fusion preserves the union

Per substrate-product positioning: substrate has two valid retrieval primitives; the engineering question is HOW TO COMBINE without losing each one's contribution.

## What both null-nets together tell us

bge-baseline 0.413 = bge's ceiling on current 1742-atom corpus.
HYBRID-RRF 0.412 = bge ceiling + algebra lifts cancel algebra hurts.
Option 4 pipeline 0.413 = bge ceiling + algebra atoms whose bge score is high enough to survive re-rank (which equals bge picks themselves) + algebra atoms with low bge score (filtered out).

Either way: **A axis 0.413 is the empirical ceiling at 13.8% algebra coverage with current parser + current bge encoding**.

This makes Option 1 (bge-name encoder) and Option 5 (breadth-50 batch 2 ingest) the load-bearing levers, not further fusion algorithm tuning at current authoring.

## Recommended sequence (Cycle 50 open)

1. **Option 1 NOW (~half day)**: bge-name encoder. Independent of HYBRID. Expected +0.04-0.08 per Exp-Dev empirical. A axis 0.413 -> ~0.45-0.50 raw. If shipped together with Option 4 pipeline, expect ~0.46-0.52.
2. **Option 5 AFTER Option 1 measurement (~30 min Research)**: breadth-50 batch 2 with bge-name-friendly atom naming (atom name should include canonical-discipline tokens that bge can latch onto).
3. **Stratified Hybrid Cycle 50+ (deferred)**: math drill 6-layer architecture. Confirmed deferred per your direction.

Per substrate-quality-first + drill-defeatism + brain-can-do-it: the path forward is COMPOUND levers (Option 1 + 5 + later 4 re-cal with better-named atoms), not another fusion-algorithm-only tweak.

## Substrate-product positioning insight (worth memory entry)

**Algebra HRR catches what bge can't (structural-position-defined gold) AND bge catches what algebra can't (text-similarity-defined gold). They are PARTITIONS not a HIERARCHY.** Fusion strategies that AVERAGE (RRF) or RANK-DOMINATE (pipeline) all lose to UNION strategies (return top-K by either, dedupe). Cycle 50+ Stratified Hybrid is the only architecture that respects partition structure.

This is similar to count_NB-vs-discriminative_perceptron pattern from rule 1 -- both retrieval primitives are weakly dominated by neither; substrate's strength is in COMPOSING them.

## Honest scope

- Pre-reg HP F1 >= 0.50 macro A axis: FAIL (0.413)
- Pre-reg MID 0.45-0.50: FAIL (0.413 below 0.45)
- Cycle 49 close verdict: HYBRID architecture exploration COMPLETE (3 variants tried: RRF 0.412 / threshold 0.412 / pipeline 0.413); all null-net at 13.8% algebra authoring
- Substrate-extracted methodology rule 12 candidate REFINED: signals complementary not additive
- Path forward: Option 1 + Option 5 + later compound (not more fusion tuning)

## Cross-references

- Bench reports: `data/substrate_index/bench_reports/benchmark_v1_178127{1653,2076,2200}.json` (HYBRID v1 / Option 2 / Option 4)
- Code: `tools/substrate_benchmark.py:193-244` (answer_type_A Option 4 pipeline)
- Research direction note: `notes/research_to_testbed_HYBRID_NULL_NET_OPTION_SELECT_OPT_4_PRIMARY_OPT_2_DIAG_OPT_1_PARALLEL_RULE_12_CANDIDATE_2026-06-12.md`

## Routing

**Testbed**: Standing by; will start Option 1 (bge-name encoder) on green light. Cycle 49 measurement complete.
**Research**: rule 12 refinement -- partitions not hierarchy; Option 1 / 5 ordering call; Stratified Hybrid Cycle 50+ confirmed.
**Exp-Dev**: continuing L-B Few-shot transfer + L-A NER + Cell 2 PP-394.

---

**Testbed Cycle 49 CLOSED**: HYBRID architecture explored 3 variants ALL null-net A=0.412-0.413 + substrate-extracted methodology rule 12 candidate REFINED algebra HRR + bge cosine are partitions not hierarchy fusion-only tuning has hit ceiling at 13.8% algebra coverage + path-forward is Option 1 bge-name encoder INDEPENDENT half-day +0.04-0.08 expected + Option 5 breadth-50 batch 2 targeted at bge-name-friendly atom names + Stratified Hybrid Cycle 50+ deferred per direction + standing by for green light.
