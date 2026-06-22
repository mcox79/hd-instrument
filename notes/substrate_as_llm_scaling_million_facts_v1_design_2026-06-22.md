# Substrate-as-LLM scaling cell (million-facts) — design

**Date:** 2026-06-22 (Director main-thread design while v2c + r2c run)
**Anchor name:** substrate_as_llm_scaling_million_facts_v1
**Strategic alignment:** direct USER substrate-as-LLM-substitute target (50GB / 100M facts long-horizon)
**Status:** design draft; ready when GPU capacity opens

## Why this cell

USER strategic target: substrate stores 100M facts at compound chain-grade so it can substitute for LLM as the memory layer. Current state:
- 600K patterns chain-grade-validated at N=2048 via sparse × K × D multiplicative composition (per banked feedback `substrate_mine_capacity_before_extrapolating`)
- p1 v2 CERT 590 proves phase-action portability at LLM-class N=65536
- Modern Hopfield + p1 v3 confirmed substrate's effective capacity exceeds 0.14·N classical bound IN OUR CONFIG (Skunkworks correctly noted the bound applies to different mechanism; our bound is unknown but higher)

This cell tests a 10× lift over current baseline: **substrate stores ≥1M facts at chain-grade quality, at LLM-class N=16384**. If it passes, we have a chain-grade-evidenced path to substrate-as-LLM-substitute (1M facts × 100 = 100M facts; per-fact memory cost ~50KB compounds to ~50GB substrate).

## What this cell does

- **Ingest**: 1M synthetic (k, v) facts where k = bipolar HD key, v = bipolar HD value
- **Storage**: implicit-W Hebbian (W never materialized at N=16384; 1M outer-products stored as cumulative W via lazy formulation)
- **Sparse-keys**: k-WTA at sparsity s=0.05 (per brain-drill #1; though n4 HARD_FAILed, the brain-drill ISN'T discredited — the failure was in within-concept floor not in compositional storage; sparse keys may still help capacity)
- **Multiplicative composition**: 1M facts factored as K=1000 anchors × D=1000 relations (the multiplicative-composition pattern that already validated 600K @ N=2048)
- **Retrieval**: query k', retrieve top-1 v via implicit-W: y = (1/N) · K^T · (K · q'); snap to argmax(cos(y, codebook))
- **Capacity arms** (Fix #16 discriminator):
  - DENSE_HEBBIAN: classical dense bipolar keys, no sparse-VQ — baseline (expected to fail at 1M @ N=16384)
  - SPARSE_VQ_KEYS: k-WTA s=0.05 sparse keys — substrate's lever
  - MULTIPLICATIVE_COMP: K=1000 anchors × D=1000 relations multiplicative composition
- **Probe noise**: low (NOISE_FRAC=0.05) — at this scale even gentle noise tests the storage; basin-edge probe is separate concern per Skunkworks

## Pre-reg HARD bands

- HARD_PASS: SPARSE_VQ_KEYS OR MULTIPLICATIVE_COMP achieves recall@1 ≥ 0.85 at M=1M, AND outperforms DENSE_HEBBIAN by ≥0.30 (mechanism-discriminating). cv ≤ 0.05. n_llm_calls=0.
- HARD_FAIL: NEITHER mechanism reaches recall@1 ≥ 0.40 at M=1M (substrate cannot store 1M at LLM-class N=16384 even with composition).
- MIDDLE_BAND: in between.

## Cost / routing

- **N_DIM=16384** (LLM-class but tractable; 4× smaller than p1 v2's 65536 — keeps GPU memory bounded)
- **Memory**: W matrix at N=16384 implicit is 0 (not materialized); K matrix at M=1M × N=16384 sparse (s=0.05) ≈ 3.3GB float32 — fits VRAM
- **Wall estimate**: ingest 1M × outer-product on GPU at N=16384 batched at chunk=4096 = ~250 chunks × 5ms = ~1.25s ingest; recall 1000 probes × 3 arms × matmul (1M, 16384) @ (16384, 1000) = ~2 min × 3 seeds × 3 arms = ~20-30 min total wall on GPU
- **Route**: overnight_queue (GPU) per Fix #22 (matmul shape clearly GPU-bound); Fix #24 mandate applies (GPU util ≥50%)

## What this cell DOES NOT test

- 100M facts (this is 10× lift to 1M, not 167× lift to 100M)
- Real NL benchmark (synthetic keys/values; the `substrate_native_qa_hotpotqa_v1` cell I designed earlier handles the real-benchmark question)
- Multi-domain modular substrate (single W matrix; modular requires brain-drill #6 cortical-microcircuit cell which is separate)
- Continual ingest (this is one-shot ingest; continual is c2's domain)
- Generation (g1b chain-grade covers that; this is storage-only)

## Composition path

This cell is one node in the substrate-as-LLM chain:

```
substrate_as_llm_scaling_million_facts_v1 (THIS CELL: 1M facts @ N=16384 chain-grade)
  → substrate_as_llm_scaling_10M_facts_v2 (10× lift; N=32768; modular W or larger K×D)
    → substrate_as_llm_scaling_100M_facts_v3 (100× lift; N=65536; multi-W or hierarchy)
      → substrate-as-LLM-substitute SHIPPED
```

Each lift validates the next. The shape of the failure (if any) tells us where the scaling wall is.

## Pre-dispatch checks (Fix #26)

- `python tools/predispatch_check.py substrate scaling million facts` — likely PROCEED (this is novel; no prior cell)
- Verify hdlab/kg_traversal + hdlab/whitening primitives current
- Verify GPU has 8GB free VRAM for the K matrix (sparse 3.3GB + working set)

## When to dispatch

After r2c lands (~30min) AND v2c lands (~75-150min) — to free spawn budget AND have CPU-side results to interpret first. If both land HARD_PASS, the substrate's state at CERT 591+ is ripe for the scaling demo.

If v2c HARD_PASS: it shows substrate self-mapping works at full-Store scale → adding 1M synthetic facts is incremental.

If v2c HARD_FAIL or MIDDLE_BAND: the scaling cell remains valuable as an independent test of storage-capacity, decoupled from self-mapping.

## What this cell does NOT need

- New hdlab/ primitive (uses kg_traversal.KGStore + whitening + refuse_gate — all already shipped)
- New research drill (composition pattern is well-established from 600K @ N=2048 baseline)
- LLM forward calls (substrate-only-decode gate preserved)
- New benchmark or corpus (synthetic; future cells will use real benchmarks)

— Director (pre-design; ready when capacity opens)
