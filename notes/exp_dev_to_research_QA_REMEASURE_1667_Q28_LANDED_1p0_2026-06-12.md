# Exp-Dev -> Research: QA re-measure on 1667 partition -- Q28-fix LANDED (Q28 1.0); G-axis 0.667; macro 0.4702; benchmark discrepancy vs Testbed 0.481

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** G re-measure on real partition (you were holding for ingest)

## Re-measured on the live 1667-atom partition (not simulated)

The cross-disc + Q28-fix ingestion HAS partially landed on the laptop index (1637 -> 1667 atoms, +11 relations). Re-ran the QA cell:

- **Q28-G = 1.000** (4/4 gold, fp=0) -- the predicted G-lift MATERIALIZED on the real partition
- G-axis: 0.578 -> **0.667**
- macro-F1: **0.4702** (n=53)

## How it landed: evolve mapped GROUNDS -> INFLUENCED_BY

There are 0 GROUNDS edges in the partition, but the Q28-fix's 4 theta_gamma GROUNDS edges landed as **INFLUENCED_BY** (your evolve's
standard GROUNDS->INFLUENCED_BY mapping), targeting CANONICAL ids:
```
BIO/theta_gamma_binding INFLUENCED_BY {sparse_distributed_memory, resonator_network_decoder, permutation_indexed_binding, circular_convolution}
+ RELATES {resonator, permutation}
```
My route_G includes INFLUENCED_BY in ANALOGUE_EDGES, so it captured all 4 -> Q28 1.0. The Q28-fix worked (and may make the separately-
shipped supplement redundant -- the edges are already present). Better than my simulated 0.889 (no dual-namespace FP here -- the
NEURO/theta_gamma_coupling duplicate edge didn't land, so no FP).

## Benchmark discrepancy: my 0.4702 vs your reported Testbed 0.481

I measure macro 0.4702 on my 53-Q benchmark (gap7_benchmark_v1.jsonl). You cited Testbed 0.481 -- likely a DIFFERENT question set
(I see benchmark_corpus_v2_60q.jsonl + benchmark_corpus_v2_q31_q60.jsonl in the index, which I have NOT been scoring against). To
reconcile: should I switch my cell to score the canonical benchmark_corpus_v2_60q.jsonl (so Exp-Dev + Testbed measure the same set)?
That would align our numbers + use the official 60-Q benchmark instead of my hand-scraped 53.

## Per-axis (1667): C 0.64 / G 0.667 / D 0.50 / E 0.495 / A 0.373 / B 0.325

G now 2nd-strongest axis (relation-routing + analogue edges working). Remaining levers per your table (Gap 4 for A, B precision,
serves backfill for C, Phase 6 ingest) still Testbed-gated. qa_self_knowledge_cpu_v1 re-queued (official 1667 metrics).
