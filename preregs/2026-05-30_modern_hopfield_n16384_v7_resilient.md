# Pre-reg: modern_hopfield_n16384_v7_resilient

**Date:** 2026-05-30
**Anchor:** modern_hopfield_n16384_v7_resilient (S4, EC1)
**Script:** experiments/exp_modern_hopfield_n16384_v7_resilient.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** N=16384 Modern Hopfield activation test, robust to
v6 outcome.

## Hypothesis

At N=16384 with BSC codebook, at least one of three resilient codebook
construction strategies (a/b/c) succeeds, and max_M_at_95_recall
exceeds N/4 = 4096 -- the Modern Hopfield exponential-bend signature.

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | construction succeeds AND median max_M > N/4 (= 4096) across seeds       |
| HARD_FAIL    | all 3 strategies OOM across all 3 seeds                                  |
| MIDDLE_BAND  | construction works at smaller M but OOMs at N cell                       |

## Self-test

- N == 16384 (PROT-018).
- Smoke at N=1024 verifies strategy_a_chunked succeeds and max_M is non-zero.
- 3 strategies (a_chunked, b_streaming, c_cpu_upload) all exist as callables.

## OOM check (CRITICAL)

- Smoke verified construction success at N=1024 with strategy (a) within
  budget. FULL at N=16384 begins with strategy (a); if it OOMs at runtime,
  strategy (b) falls back to single-codeword streaming; if THAT OOMs,
  strategy (c) constructs on CPU then chunked-uploads to GPU.
- Estimated peak GPU memory at N=16384 BSC: codebook (49152 codewords *
  16384 floats * 4 bytes = 3.2 GiB) + W (1 GiB) + per-store buffers ~1 GiB
  = ~5.5 GiB. Within 8 GiB budget.

## Timeout estimate

3 seeds x ~4 M-points per seed. Per-M wall at N=16384 ~300-600s.
3 * 4 * 600 = 7200s baseline + construction overhead.
**timeout_s = 43200** per user spec; >7200s flagged for user visibility
in For You log entry. **NOTE: timeout > 14400s requires explicit user
approval per role contract.** User explicitly authorized "TIMEOUT: 43200s"
in dispatch.

## Production config

N=16384, M sweep = [N/8, N/4, N/2, N] = [2048, 4096, 8192, 16384].
3 seeds = [7, 17, 23].

## N-suffix binding

_n16384 -> production N = 16384 (PROT-018).
