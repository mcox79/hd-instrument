# 2026-06-23 brain_compose_fair_harness_debug_v2 -- BRAIN_COMPOSE OOM FIX

## Anchor
`brain_compose_fair_harness_debug_v2`

## Status
- Prereg authored 2026-06-23 (exp_dev; debug-and-ship cycle)
- Queue: `overnight_queue` (GPU, marsh@home)
- Timeout: 5400s (90min safety margin; v2 BRAIN_COMPOSE ingest unchains the OOM)
- Estimated wall: 25-45 min GPU full
- Parent: `fair_harness_substrate_as_lm_v1` (HARD_PASS via SPARSE_BIPOLAR BPC,
  but ARM_SUBSTRATE_BRAIN_COMPOSE failed with CUDA OOM on all 3 seeds)

## Cell
`experiments/exp_brain_compose_fair_harness_debug_v2.py`

## Root cause analysis (v1 BRAIN_COMPOSE failure)
v1 metrics.json showed `bpc_best=Infinity, top1=NaN, mrr=NaN` for ARM_SUBSTRATE_BRAIN_COMPOSE
on all 3 seeds. Initial framing (in the spawn brief) was "numerical inf/nan bug". Per-seed
inspection revealed the per-unit `compute_error` field:

```
OutOfMemoryError: CUDA out of memory. Tried to allocate 3.05 GiB. GPU 0 has a total
capacity of 8.00 GiB of which 329.00 MiB is free. 6.80 GiB allowed
```

This is NOT a math bug. The cell sentinel-fills `inf` for `bpc_best` and `NaN` for top-1/MRR
when `compute_failed=True`; the verdict_msg then propagated `BRAIN_COMPOSE=FAIL` without
distinguishing OOM from numerical pathology.

**Allocation site** (line 403 of v1 `build_pc_stack_gpu`):

```python
cumulative_pred_NEW = torch.zeros((src_keys.shape[0], dim), dtype=TORCH_DTYPE, device=device)
```

At FULL scale: `src_keys.shape[0]=100_000` (N_TRAIN) and `dim=8192`. That's
`100_000 * 8192 * 4 bytes = 3.05 GiB` -- matches the OOM message exactly.

**Peak GPU memory estimate at v1 BRAIN_COMPOSE production scale**:

| Tensor | Bytes |
|---|---|
| E_used [V, dim] = [4000, 8192]  | 128 MB |
| src_keys_train [100k, 8192]     | 3.05 GB |
| src_keys_held [20k, 8192]       | 600 MB |
| Ws (3 layers) [8192, 8192]      | 768 MB |
| cumulative_pred_norm [100k, 8192] | 3.05 GB |
| cumulative_pred_NEW [100k, 8192]  | 3.05 GB (transient at end of each layer) |
| **Peak**                        | **~10.7 GB**  |

Budget allowed = 6.8 GB. Bust by ~4 GB. The "smoke gate" at N_DIM=512 N_TRAIN=2000
allocated `cumulative_pred_NEW = 4 MB` and trivially passed -- the smoke could not
catch the production-scale OOM because the bug is shape-dependent.

## v2 fix (memory plumbing only; zero methodology change)

1. **Drop the persistent inter-layer `cumulative_pred_norm[N_TRAIN, dim]` tensor.**
   Layer i > 0 now recomputes the prior cumulative prediction PER CHUNK via
   `_chunk_prior_cum_norm(src_chunk_raw, Ws[:i])`. Each call allocates only
   `[INGEST_CHUNK, dim]`, which is ~128 MB at production scale and is freed immediately
   when the chunk ends. Trade: O(n_layers**2) = 6 W-forwards per chunk (vs 1 in the
   broken v1 path). For pc_layers=3 this is trivial vs the ~3 GB freed.

2. **Free `src_keys_train` BEFORE recall starts** in `compute_arm_logits`. Recall uses
   only `src_keys_held` (600 MB). Frees another ~3.05 GB.

3. **`torch.cuda.empty_cache()` between PC layers** and between ingest/recall phases.

4. **GPU-mem budget projection at config-load time** via
   `project_brain_compose_peak_gb(N_TRAIN, N_HELD, N_DIM, PC_N_LAYERS, V)`. Warns
   loudly if projected peak > 70% of total GPU. Won't bomb out but won't silently
   waste 30s of dispatch+seed setup either.

**v2 projected peak (production scale, same N_DIM=8192 N_TRAIN=100k)**:
- ingest peak: E_used + src_train + src_held + Ws = 0.128 + 3.05 + 0.6 + 0.768 = **4.55 GB**
- recall peak: E_used + src_held + Ws + pred_held + logits = 0.128 + 0.6 + 0.768 + 0.6 + 0.128 = **2.22 GB**

Both fit comfortably in the 6.8 GB allowed budget.

Everything else (TEMP_GRID, LAMBDA_GRID, joint sweep, verdict bands, all other arms,
encoder loader, READOUT_DEGENERATE gate, ALL self-tests T1-T10) is byte-identical to v1.
This is a memory-plumbing fix, not a methodology change.

## Arms (4; identical to v1)
1. **ARM_UNIGRAM** -- analytic floor
2. **ARM_SUBSTRATE_WORD2VEC_DENSE** -- word2vec encoder + rank-1 Hebbian W
3. **ARM_SUBSTRATE_SPARSE_BIPOLAR** -- word2vec encoder + sparse-bipolar f=0.05
4. **ARM_SUBSTRATE_BRAIN_COMPOSE** -- PC 3-layer + sparse + lock-in + WM HRR-slots
   (with v2 memory-plumbing fix)

## Config (PRODUCTION SCALE GPU; identical to v1)
- V=4000 vocab, N_TRAIN=100_000 text8 tokens, N_HELD=20_000
- N_DIM=8192, seeds=[7,17,23]
- Encoder: word2vec-google-news-300, GENSIM_CACHE_DIR=`data/gensim_cache_v2`
- INGEST_CHUNK=4096, RECALL_BATCH=256
- TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- PC_N_LAYERS=3, CONTEXT_WINDOW=5, LOCK_IN_FREQ_STEP=31

## Pre-reg HARD bands (identical to v1 parent)

### HARD_PASS (substrate-as-LM works under fair harness; chain-grade-eligible V2)
Any of:
- **HARD_PASS_BPC**: any substrate arm clears `bpc_best < unigram_bpc - 0.3` bits
- **HARD_PASS_TOP1**: any substrate arm clears `top1_acc > unigram_top1 + 2 * sigma_seeds`
- **HARD_PASS_MRR**: any substrate arm clears `mrr_at_10 >= unigram_mrr + 0.02`

### HARD_FAIL (substrate-as-LM genuinely fails even under fair harness)
ALL of:
- ALL 3 substrate arms fail HARD_PASS_BPC AND HARD_PASS_TOP1 AND HARD_PASS_MRR
- AND `raw_bpc_at_T1_L1` is NOT near `-log2(1/V) +/- 0.5`

### MIDDLE_BAND
Substrate beats unigram on at least one metric but doesn't cross HP bar.

### READOUT_DEGENERATE
If `raw_bpc_at_T1_L1` near `-log2(1/V) +/- 0.5` AND no substrate arm HP, classify as
`READOUT_DEGENERATE_NOT_SUBSTRATE_FAILURE` (NOT HARD_FAIL).

### BRAIN_COMPOSE-specific debug bands (v2 spawn brief)
- **DEBUG_PASS**: BRAIN_COMPOSE arm produces FINITE values (any of bpc<inf, top1!=NaN,
  mrr!=NaN) on >= 2 of 3 seeds. The OOM fix is validated; whether it ALSO clears a
  margin bar is the underlying-mechanism question (orthogonal to this debug cycle).
- **DEBUG_FAIL**: BRAIN_COMPOSE still inf/nan on >= 2 of 3 seeds. Then the fix
  is wrong OR a different (non-OOM) numerical pathology exists; root-cause re-debug
  required.

## Mandatory sanity self-tests (in cell --self-test; T1-T10 from v1 + new T11-T12)
- T1-T10: identical to v1 (trigram, mockKV, peakedT001, uniformT10, lam0=unigram,
  lam1=raw_sub, MRR planted, sparse-bipolar, verdict bands, LLM counter zero)
- **T11 (NEW)**: `build_pc_stack_gpu` at smoke-shape (V=64, dim=128, n=200, 3 layers)
  returns 3 Ws of shape [128,128] all finite.
- **T12 (NEW)**: `pc_stack_forward_gpu` on the T11 Ws returns finite pred [50, 128]
  AND finite cosine logits [50, V] AND finite softmax-at-T=0.5.

All 12 tests PASS in laptop self-test.

## Smoke (CPU, N_DIM=512 N_TRAIN=2000)
Verified locally before dispatch:
- BRAIN_COMPOSE arm returns bpc=5.579 top1=0.3306 mrr=0.4013 (all finite)
- WORD2VEC_DENSE / SPARSE_BIPOLAR also finite (regression-clean)
- Smoke wall 40s laptop CPU (< 180s budget)

## Routing rationale
- GPU REQUIRED per Fix #24 (matmul-bound; PC training + sparse-bipolar + lock-in).
- Estimated 25-45 min GPU wall (v1 was 5min/seed for 3-arm + 0.2s BRAIN_COMPOSE
  failure; v2 BRAIN_COMPOSE now actually runs ingest ~3-5 min/seed; 3 seeds = ~15-25 min
  for BRAIN_COMPOSE + ~10-15 min for the other arms ~ ~25-40 min total).
- Timeout 5400s (90min) = 2x-3x safety margin.
- PROT-021: timeout 5400 < 14400 so no checkpoint-import required; per-seed
  checkpoint is in place (defensive).

## Pre-dispatch checklist
- [x] commit script + prereg before remote dispatch (commit-first discipline)
- [x] --self-test PASS on laptop .venv (T1-T12)
- [x] --smoke PASS on laptop CPU (all 4 arms finite)
- [x] HDLAB_EXP_NAME passed via queue_add.sh
- [x] run_mode default = full at production scale (no `_smoke` substring)
- [x] commit hash recorded in queue_add ship sentinel

## Cites
- preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md (parent)
- experiments/exp_fair_harness_substrate_as_lm_v1.py (parent cell; root-cause source)
- USER_2026-06-22 Fix #24 (GPU dispatch must use GPU)
- USER_2026-06-22 Fix #28 (verify per-arm metrics before cross-cell convergence claims)
- METHODOLOGY: re-claim "ARM_SUBSTRATE_BRAIN_COMPOSE FAIL" framing in v1 verdict_msg
  was over-claim per Fix #28; per-seed compute_error was OOM not math; this v2 cycle
  unblocks the compose-mechanism question.
