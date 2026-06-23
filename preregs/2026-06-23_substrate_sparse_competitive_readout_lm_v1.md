# 2026-06-23 substrate_sparse_competitive_readout_lm_v1 -- SPARSE COMPETITIVE READOUT

## Anchor
`substrate_sparse_competitive_readout_lm_v1`

## Status
- Prereg authored 2026-06-23 (exp_dev)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 5400s (1.5h)
- Estimated wall: 30-60 min GPU

## Cell
`experiments/exp_substrate_sparse_competitive_readout_lm_v1.py`

## Why now (USER directive 2026-06-23 brain-existence-proof)
Substrate's current readout is argmax over scores = a linear operation. The brain
does NOT do this. Cortex uses sparse competitive activation (~1-3% firing rate)
via K-WTA lateral inhibition plus a Tonegawa-CREB excitability bias. This
mechanism is empirically validated in mammalian cortex. Substrate just needs
to implement it.

The HYPOTHESIS this cell tests in isolation: **non-linear sparse competitive
readout alone breaks the rank-1 cap** that prior substrate-as-LM cells run
into. If TRUE, we don't need to rewrite the W matrix; the bottleneck was the
linear argmax all along.

## Mechanism (at READ time, not write time)
- Substrate W produces a score vector E_lookup @ (W @ key) over V vocab
- Instead of `argmax(scores)`, do:
  1. `top-K` over the V positions (K-WTA)
  2. (optional) bias by per-vocab Tonegawa excitability trace
     `scores = scores * (1 + beta * E_norm[i])`
  3. log-softmax over the K survivors; others mass to zero
- Excitability trace E[i]:
  - per-vocab-position scalar; updated during W-build
  - `E[i] += alpha` when position fires; `E *= decay` per step
  - alpha=0.01, decay=0.99 (chunked: decay^chunk_size at boundary)

## Arms (5; SHARED W+E across all sparse arms; readout layer differs)
1. **ARM_UNIGRAM** -- analytic floor BPC=7.738 reference
2. **ARM_RANK1_ARGMAX** -- current substrate readout (K_eff=1); rank-1 cap reference
3. **ARM_SPARSE_COMPETITIVE_K10** -- K-WTA top-10 + masked softmax
4. **ARM_SPARSE_COMPETITIVE_K100** -- K-WTA top-100 + masked softmax
5. **ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100** -- top-100 + Tonegawa excitability
   bias (DECISIVE arm)

## Config (PRODUCTION SCALE GPU)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7,17,23]
- Encoder: char_trigram (clean comparison; single encoder isolates readout effect)
- All ops via torch.cuda (Fix #24): matmul + topk + masked softmax batched
- INGEST_CHUNK=4096, RECALL_BATCH=256
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0] (log-linear interp with unigram)
- EXCITABILITY_ALPHA=0.01, EXCITABILITY_DECAY=0.99, EXCITABILITY_BETA=1.0
- TOPK_LIST=[10, 100]

## Pre-reg HARD bands
- **HARD_PASS:** `ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100` BPC < `ARM_RANK1_ARGMAX`
  BPC - 0.5 AND decisive BPC < 7.5 AND cv <= 0.05. Non-linear sparse competitive
  readout breaks rank-1 cap; brain-existence-proof K-WTA+excitability mechanism
  validated in substrate; chain-grade evidence; the readout layer was the
  bottleneck not the W matrix.
- **HARD_FAIL:** ALL competitive arms (K10, K100, EXCIT_K100) BPC >= `ARM_RANK1_ARGMAX`.
  Non-linear readout does NOT help; rank-1 cap is structurally in the W matrix.
  Pivot to W-build architectural changes (multi-head / multi-rank / projection).
- **MIDDLE_BAND:** competitive lifts over rank-1 but doesn't meet HP bars (delta < 0.5
  or absolute >= 7.5). Characterize K-sweep and excitability beta.

## Sanity self-tests (in cell --self-test)
- T1 char_trigram bipolar
- T2 K=1 reproduces argmax (rank-1 endpoint check: top prob = 1.0 at argmax)
- T3 K=V reproduces plain log_softmax (full endpoint check)
- T4 K=2 keeps exactly 2 nonzero per row
- T5 excitability bias makes high-exc position win on tied scores
- T6 W + excitability trace; exc non-uniform after training (fires-more pos has higher exc)
- T7 log-linear endpoints (lambda=1 raw substrate / lambda=0 unigram)
- T8 verdict bands HP / HF / MID with synthetic units
- T9 unigram analytic max-class
- T10 LLM-call counter zero

## Brain-sparsity sanity (logged per-arm at runtime)
- Sparse competitive arms should show `fraction_above_uniform ~ K/V` (1-3% at K=40-100, V=4000)
- This is the brain-existence-proof target: cortex shows ~1-3% sparse activation

## Routing rationale
- GPU REQUIRED per Fix #24: torch.cuda for matmul (8192x8192 W) + topk over 4000 positions
  + masked softmax all batched
- Estimated 30-60min GPU wall at 100k tokens x 5 arms x 3 seeds
- SHARED W+E across all sparse arms (only readout differs) saves 4x compute vs
  per-arm fresh W
- Timeout 5400s = 1.5h buffer; under PROT-019 floor of 21600s only because
  this is _lm_v1 not _n8192_ suffix (intentional; N_DIM is config not anchor name)
- PROT-021: timeout < 14400 so no checkpoint-import required, BUT cell uses
  `_seed_checkpoint` anyway for per-seed resume on partial timeout

## Cites
- experiments/exp_substrate_as_lm_composed_primitives_GPU_v1.py -- parent pattern
- experiments/exp_excitability_gated_substrate_cpu_v1.py -- Tonegawa-CREB prior
  (HARD_PASS 2026-06-11)
- experiments/exp_n4_kwta_soft_decode_v1.py -- kwta soft-decode prior
  (HARD_FAIL 2026-06-22; different design: this cell uses ISOLATED readout
  sweep on SHARED W with explicit rank1-vs-competitive delta gate; prior used
  composed cleanup-VQ which conflated multiple changes)
- USER 2026-06-23 brain-existence-proof for K-WTA + excitability
- USER 2026-06-22 GPU dispatch must use GPU (Fix #24)

## Pre-dispatch
- predispatch_check: PROCEED (anchor-specific 0 prior landings; broader keyword
  search shows 1 HARD_PASS Tonegawa prior + 2 HARD_FAIL unrelated kwta cells;
  this cell's isolated-readout design distinct from prior failures)
