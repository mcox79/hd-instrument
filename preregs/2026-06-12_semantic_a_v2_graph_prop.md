# Pre-registration: Semantic-A v2 graph propagation over DEPENDS_ON

Date: 2026-06-12
Status: Pre-registered, ready to launch
Experiment file: [exp_semantic_a_v2_graph_prop_gpu_v1.py](../experiments/exp_semantic_a_v2_graph_prop_gpu_v1.py)

## Hypothesis (H)

The substrate's DEPENDS_ON-family edges carry a retrieval signal that bge cosine ignores. Seeding A-axis retrieval on the strong
name-field bge cosine and then spreading activation 1-2 hops along DEPENDS_ON should raise A-axis set-overlap F1 over the name-field
retriever alone (a substrate-product-native signal LLMs lack).

H is operationalized as: `A_F1(name + DEPENDS_ON-prop) - A_F1(name) >= 0.05`.

## Pre-registered outcomes

- HARD-PASS: lift >= +0.05 (structural edges add A-axis retrieval signal)
- MIDDLE: lift +0.02-0.05
- HARD-FAIL: lift < +0.02 (DEPENDS_ON adds no A-axis signal over name-field)

## Method

bge-large name-field encoding of all atoms; per A-question, top-S seeds by name cosine, spreading activation (alpha=0.5, hops=2) over
undirected DEPENDS_ON-family adjacency, re-rank, top-k F1 vs gold. Read-only; canonical set-overlap F1; no LLM-judge.
