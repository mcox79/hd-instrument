# Prereg: gpu_large_n_rescue_serialized_v1_n8192

Date: 2026-05-30
Anchor: `gpu_large_n_rescue_serialized_v1_n8192`
Script: `experiments/exp_gpu_large_n_rescue_serialized_v1_n8192.py`
Queue: `overnight_queue` (GPU; runs in a single process, no internal contention)
PROT-018 N-suffix: `_n8192`. Script production `N = 8192` (and sub1 `SUB1_N = 8192`).
PROT-019 timeout floor: 21600s (_n>=8192). Requested 43200s exceeds the floor.
PROT-021 checkpoint: `_seed_checkpoint` per (sub, seed).
Composition class: PIPELINE (3 GPU-failed N-batch anchors serialized into one process).

## Context

N-batch (commit `e457f1e`, dashboard verdict at `947b22e`) returned three
NO_METRICS entries that were diagnosed as PARALLEL-GPU CONTENTION on the
runner machine (8 GiB GPU, multiple python processes competing):

- N5 : `gpu_baseline_expansion_n8192`   -> OOM under contention
- N11: `sparse_w_gpu_integration_n4096` -> STACK_BUFFER_OVERRUN under contention
- N12: `n_scaling_chunked_codebook_n16384` -> OOM under contention

Each script's own `_instrumentation_selftest()` and verdict gate is fine.
Their FULL configs ARE memory-feasible on the 8 GiB GPU when run alone;
the failure mode was the runner's parallel scheduling, not the scripts.

## Question

When all three sub-tests are run SEQUENTIALLY inside a SINGLE python process
(no parallel-GPU contention possible), do all three emit complete metrics?
And if so, do they meet their original v1 HP gates?

The PRIMARY success criterion for this rescue anchor is INSTRUMENTATION
COMPLETENESS -- metrics emission. A sub-test that hits its own HARD_FAIL but
emits metrics is a SUCCESS for this anchor. Only runtime crashes count as
this anchor's HARD_FAIL.

## Design

Single script orchestrating three sub-tests in sequence:

- **sub1 (gpu_baseline_expansion_n8192)**: N=8192, M=N/4=2048, 3 seeds,
  CPU-vs-GPU latency at batches [1, 16, 64, 256], plus retention / above_thresh
  / max_iso KFs on GPU.

- **sub2 (sparse_w_gpu_integration_n4096)**: N=4096, M in [128, 1024, 4096],
  3 seeds, sparse-W on GPU vs dense-GPU latency at batch=1, plus sparse
  retention + KF-2 max_iso, plus mem_savings check (dense_bytes / sparse_bytes).

- **sub3 (n_scaling_chunked_codebook_n16384)**: N=16384, BSC codebook built
  via Kerdock 4-coset CHUNKED CONSTRUCTION (1024 codewords per chunk,
  progressive concat, free intermediates), M sweep [N/8, N/4, N/2, N],
  3 seeds, Modern Hopfield activation test (retention >= 0.95 threshold).

Between sub-tests: `torch.cuda.empty_cache()` + `gc.collect()` +
log memory snapshot. Each sub-test writes its own partial metrics via
`write_partial_key`; final composite metrics.json contains all sub-verdicts
plus the composite verdict.

## Pre-registered composite bands

HARD_PASS:
  All 3 sub-tests emit metrics AND each meets its original v1 HP gate:
  - sub1: mean GPU >= 10x CPU speedup at N=8192 single-op AND all KFs pass
          (retention >= 0.95, above_thresh_frac <= 0.10, max_iso <= 0.10).
  - sub2: sparse_gpu_lat/dense_gpu_lat <= 2 AND mem_savings >= 4x AND
          sparse_retention >= 0.95 AND kf2_max_iso <= 0.05, at all M, in >=2/3 seeds.
  - sub3: chunked construction succeeds AND mean max_M_at_95_recall across
          seeds > N/4 * 1.5 = 6144 (exponential bend at N=16384).

HARD_FAIL (instrumentation-only):
  ANY sub-test CRASHES (RuntimeError / MemoryError / OOM) before emitting
  metrics. The criterion for HARD_FAIL is INABILITY TO PRODUCE METRICS,
  not failure to meet HP. Crashes break the rescue purpose.

MIDDLE_BAND:
  All 3 sub-tests successfully EMIT METRICS, but not all 3 hit HP gates.
  Any combination of sub-HARD_PASS / sub-HARD_FAIL / sub-MIDDLE_BAND that
  produced data is a SUCCESS for the rescue purpose, but the composite
  verdict is MIDDLE_BAND to reflect that some sub-tests didn't pass their
  own HP.

This inversion of normal HP/HF semantics is INTENTIONAL and load-bearing
for this rescue anchor. The user's criterion in the dispatch:
"even a sub-test that HARD_FAILs by exceeding its HP threshold for its own
reasons is a SUCCESS for this rescue anchor because it produced metrics.
Crash = failure; metric = success."

## Verdict reporting

`verdict_msg` reports the three sub-verdicts + any crash details:

```
sub1=<SUB1_HARD_PASS|SUB1_HARD_FAIL|SUB1_MIDDLE_BAND|SUB1_INCONCLUSIVE>
sub2=<SUB2_...>  sub3=<SUB3_...>
[sub1_crash=... sub2_crash=... sub3_crash=...]
```

This supports verdict_handler's "honest re-read" pattern -- the composite
verdict and per-sub-verdicts can be cross-checked against the cells data
in summary.

## Formula self-tests (in script)

- PROT-018: `SUB1_N == 8192`, `SUB2_N == 4096`, `SUB3_N == 16384`.
- HP composite gate: 3 fake HP sub-results -> composite HP.
- HF composite gate: 1 sub crashed -> composite HF (even with 2 HPs).
- MB composite gate: 1 sub MIDDLE_BAND + 2 HP -> composite MB.
- Inner sub2 kernel functional at CPU smoke (N=1024, M=32).

## OOM check

Sequential execution means each sub-test runs at full GPU envelope:

- sub1 peak (N=8192): codebook + W + key/val embeddings = 256 + 256 + 128 = ~640 MiB.
  Plus timing-loop transients: ~100 MiB. ~750 MiB peak. OK.

- sub2 peak (N=4096, M=4096): keys+vals = 128 MiB. W = 64 MiB. codebook = 64 MiB.
  ~256 MiB. OK.

- sub3 peak (N=16384): chunked construction documented at ~6.4 GiB peak
  (4.3 GiB result tensor + 2.1 GiB H + transient). Sits at the 6 GiB budget
  ceiling. The chunked design has been verified vs reference at small N.
  Per-cell retention pass: small additional W = 1 GiB transient.

Between sub-tests: `empty_cache()` returns all reservations to PyTorch's
allocator, and `gc.collect()` deletes any straggling references. Memory
snapshot logged to `mem_log` before / after each sub-test for forensics.

## Multi-scale smoke

Smoke runs all three sub-tests at small N (1024 baseline, 1024 sparse,
1024 chunked) in 1.22s on CPU. Sub1 reports speedup_single=0.00 on CPU
(expected; no GPU available); sub2 and sub3 produce valid metrics.
Composite verdict = RESCUE_MIDDLE_BAND (sub1 INCONCLUSIVE, sub2 MB, sub3 MB)
which is the expected CPU-smoke outcome.

## Walk-back / borderline check

Smoke effect sizes are CPU-only (sub1 expected to fail without GPU). Walk-back
doesn't apply because the production GPU run is what's load-bearing; sub1's
speedup measurement is inherently meaningless on CPU smoke. The FULL run is
the discriminating test.

## Timeout estimate

User dispatch specified `timeout_s = 43200` (12h) "battery scope" for the
3-sub composite. Per-sub estimates:

- sub1 (N=8192, 3 seeds, 4 batch sizes, CPU+GPU dual timing with retention/iso):
  ~30-60 min on GPU contended-free.

- sub2 (N=4096, 3 M, 3 seeds, sparse+dense timing + retention + iso):
  ~15-30 min on GPU contended-free.

- sub3 (N=16384, chunked construction + 3 seeds * 4 M retention):
  Chunked build ~5-10 min; per-cell retention at N=16384 ~5-15 min; total
  ~60-180 min.

Realistic total: 105-270 min (~5h max on a clean GPU). 43200s (12h) provides
significant safety margin for slow nodes, retries, and sub3's chunked
construction worst case. PROT-019 floor for _n8192 is 21600s; 43200s exceeds.

## Dependencies verified

- `experiments/_metric_battery.py` -- present
  (make_substrate, metric_retention, metric_above_thresh_frac, metric_max_iso)
- `experiments/_seed_checkpoint.py` -- present
- `experiments/exp_wave14y_erase_kerdock_v3.py` -- present
  (Kerdock 4-coset reference builder; v3 used by chunked builder)
- Source N-batch scripts also present (for reference equality):
  - `experiments/exp_gpu_baseline_expansion_v1_n8192.py`
  - `experiments/exp_sparse_w_gpu_integration_v1_n4096.py`
  - `experiments/exp_n_scaling_chunked_codebook_v4_n16384.py`

## Risk / interpretation

Best case (RESCUE_HARD_PASS): all 3 sub-tests run clean AND meet HP.
N5, N11, N12 are all resolved; the parallel-GPU-contention diagnosis is
confirmed.

Most likely case (RESCUE_MIDDLE_BAND): all 3 sub-tests run clean and emit
complete metrics; some hit HP, some hit their own HF or MB. This still
COMPLETES THE RESCUE -- the original 3 NO_METRICS are converted into
actionable verdicts.

Worst case (RESCUE_HARD_FAIL): one sub-test still crashes even without
parallel contention. This would falsify the contention diagnosis. Likely
causes: sub3's N=16384 chunked construction hits OOM in single-process mode
too (need finer chunking); sub1's speedup measurement fails on the specific
GPU node. Either case directs follow-on engineering work to a specific sub.

## Composite verdict logic

Composite verdict logic in script `compute_composite_verdict`:

```
if any_sub_crashed -> RESCUE_HARD_FAIL ("INSTRUMENTATION_CRASH")
elif sub1=HP AND sub2=HP AND sub3=HP -> RESCUE_HARD_PASS ("ALL_SUB_PASS")
else -> RESCUE_MIDDLE_BAND ("METRICS_EMITTED_NOT_ALL_HP")
```

## N-suffix

`_n8192` (PROT-018). Script's production `N = 8192` (and `SUB1_N = 8192`).
sub2's N=4096 and sub3's N=16384 are documented script-level constants
covered by the composite anchor's N=8192 binding.
