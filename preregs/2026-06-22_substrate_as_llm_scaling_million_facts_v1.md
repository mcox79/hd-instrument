# substrate_as_llm_scaling_million_facts_v1 -- pre-reg

**Date locked:** 2026-06-22
**Anchor name:** substrate_as_llm_scaling_million_facts_v1
**Routing:** overnight_queue (GPU) per Fix #22 (N_DIM=16384, M=1M facts, matmul-bound storage + recall)
**Strategic alignment:** USER L1 strategic vision -- substrate-as-LLM-substitute storage chain (50GB / 100M facts long-horizon)
**Design source:** notes/substrate_as_llm_scaling_million_facts_v1_design_2026-06-22.md

## What this cell tests

10x lift over existing 600K-facts-chain-grade-at-N=2048 baseline. Target: substrate stores
M=1,000,000 synthetic (key, value) facts at LLM-class N=16384 with chain-grade recall.

Storage mechanisms tested via 3-arm Fix #16 discriminator (DENSE_HEBBIAN as expected-fail
CAN-FAIL control for harness validity):

1. `DENSE_HEBBIAN` -- baseline; dense bipolar keys; classical implicit-W Hebbian. EXPECTED
   to fail at M=1M / N=16384 (M/N=61 well past classical 0.14*N bound). CAN-FAIL test
   confirms the harness can detect a failure.
2. `SPARSE_VQ_KEYS` -- k-WTA sparse keys at s=0.05 (brain-drill #1 sparsity lever); keeps
   key collisions low via sparse-coding capacity.
3. `MULTIPLICATIVE_COMP` -- 1M facts factored as K=1000 anchors x D=1000 relations
   (multiplicative composition; the pattern that already validated 600K @ N=2048).

## Pipeline (zero LLM forward calls at inference)

```
Per arm:
  ingest M=1M (key, value) facts via implicit-W Hebbian
    DENSE_HEBBIAN:        K[i] = random bipolar dense [N]
    SPARSE_VQ_KEYS:       K[i] = k-WTA(random Gaussian [N], s=0.05) bipolar
    MULTIPLICATIVE_COMP:  K[i] = anchors[i%1000] * relations[i//1000]  (HD binding)
  recall:
    query   = K[i] + noise (NOISE_FRAC=0.05)
    y       = (1/N) * V^T (K @ q)         (implicit-W single-matmul; no W materialized)
    pred    = argmax_j cos(y, codebook V[j])
    metric  = recall@1
```

Substrate-only-decode gate: `_LLM_CALL_COUNTER == 0` asserted at exit.

## Pre-reg HARD bands

**HARD_PASS** (locked; substrate-as-LLM-substitute storage chain advances):
- `SPARSE_VQ_KEYS` OR `MULTIPLICATIVE_COMP` mean recall@1 at M=1M `>= 0.85` (chain-grade
  storage of 1M facts at LLM-class N)
- AND `(best_substrate_mechanism_recall@1 - DENSE_HEBBIAN_recall@1) >= +0.30`
  (mechanism-discriminating: composition lever does the work, not raw capacity)
- AND `cv across 3 seeds for the passing arm <= 0.05`
- AND `n_llm_calls == 0`

**HARD_FAIL** (locked):
- NEITHER `SPARSE_VQ_KEYS` NOR `MULTIPLICATIVE_COMP` reaches recall@1 `>= 0.40` at M=1M
  (substrate cannot store 1M facts at N=16384 even with sparse-VQ + composition levers)
- OR `n_llm_calls > 0` (substrate-only-decode gate violated)

**MIDDLE_BAND**: in between.

## Discriminating-regime check (Fix #16)

- If DENSE_HEBBIAN recall@1 >= 0.40 at M=1M: harness either has a bug OR the 0.14*N
  classical bound does NOT apply to bipolar-bound-implicit-W in this regime. Both warrant
  re-examination before treating PASS as chain-grade.
- If SPARSE_VQ_KEYS PASSes but MULTIPLICATIVE_COMP FAILs (or vice versa): the working
  lever is identified; backlog the failing mechanism for follow-up.
- If both PASS: substrate has TWO independent storage mechanisms reaching 1M at N=16384.

## Per-arm metrics (Fix #28)

Per (seed, arm):
- `recall_at_1` (correctness of argmax(cos(y, codebook)) per query)
- `recall_at_5`
- `mean_score_correct` (cos(y, true_v))
- `mean_score_decoy` (cos(y, random other v))
- `ingest_wall_s`, `recall_wall_s`

## Routing + cost

- N_DIM = 16384 (LLM-class; 4x smaller than p1 v2 N=65536; VRAM-bounded for 8GB GPU)
- M = 1,000,000 facts; N_PROBES = 1000 query subsample for recall measurement
- 3 arms x 3 seeds = 9 (ingest + recall) cycles
- Memory: sparse K is ~3.3GB at s=0.05 (M=1M x N=16384 x s=0.05 x 4 bytes); dense K is
  65GB unmaterialized. We stream chunks for ingest and never materialize full dense K.
- Routes to `overnight_queue` GPU; target GPU util >= 50% in smoke per Fix #24
- Estimated wall: 30-60 min on GPU (90 min timeout slack)

## Fix inventory

- Fix #14 commit before remote dispatch
- Fix #16 3-arm discriminator (DENSE_HEBBIAN as expected-fail CAN-FAIL control)
- Fix #17 measurement strict (per-arm recall from sub-records, not pooled)
- Fix #22 GPU routing for N_DIM >= 8192 + matmul-heavy
- Fix #24 torch.cuda + batched ops + GPU util >= 50%
- Fix #26 predispatch_check PROCEED (verified 2026-06-22; 0 matching atoms, novel)
- Fix #28 per-arm metrics in `per_unit` list

## Self-tests (`--self-test`)

1. Bipolar key gen returns shape (n_dim,) with values in {-1, +1}
2. k-WTA at s=0.05 yields sparsity (nonzeros / n_dim) within [0.04, 0.06]
3. Multiplicative composition K=anchor * relation has expected magnitude
4. Implicit-W recall on tiny M=10 / N=128 recovers stored values at recall@1 = 1.0
5. `_LLM_CALL_COUNTER[0] == 0` after smoke

## Honest scope

- Synthetic (key, value) facts (no real benchmark; that is substrate_native_qa_hotpotqa_v1's
  job; this cell is the storage-capacity arm of the substrate-as-LLM proof chain)
- N_DIM=16384, M=1M; not 100M (that is the v3 cell down-chain)
- NOISE_FRAC=0.05 (low; basin-edge stress is separate concern per Skunkworks)
- Single-W matrix per arm (no modular substrate; brain-drill #6 is separate)
- One-shot ingest (no continual; c2/c3 cells own that)
- Storage-only (generation is g1b's chain-grade domain)
- Pairs with substrate_native_qa_hotpotqa_v1 (storage at scale + real-benchmark generation)

## Composition path (down-chain)

```
substrate_as_llm_scaling_million_facts_v1 (THIS CELL: 1M @ N=16384)
  -> substrate_as_llm_scaling_10M_facts_v2 (10x lift; N=32768)
    -> substrate_as_llm_scaling_100M_facts_v3 (100x lift; N=65536; multi-W)
      -> substrate-as-LLM-substitute SHIPPED
```
