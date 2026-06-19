# PINNED: dtype / Tensor Core acceleration

Date pinned: 2026-05-18
Date revised: 2026-05-18 (after empirical test + literature audit below)
Status: **CLOSED for action at current scale.** Conclusion: do nothing.
Reopen only if specific trigger conditions (listed at bottom) fire.

## Problem

All FHRR atoms and W are stored as `complex64` (FP32 real + FP32 imag).
At N=16384 (W=2GB), per-epoch wall time was ~6× higher than a FLOPs-only
prediction implied. We assumed this was because PyTorch's complex64 BLAS
couldn't use Tensor Cores, and a real-valued split would enable them.

## Empirical test (2026-05-18)

**Implementation:** `exp_combined_relu_realvalued_charlm.py`. Replaced every
complex matmul with 4 explicit FP32 real matmuls (paired-tensor representation:
each complex N-vector stored as `(re, im)` two FP32 N-vectors). Enabled TF32
mode via `torch.set_float32_matmul_precision("high")`. Vectorized pool
insertion via `index_copy_`. Same seed, same hyperparameters.

**Result at N=4096:**

| Metric | complex64 baseline | real-valued + TF32 |
|---|---|---|
| epoch 1 bpc | 2.8688 | 2.8688 ✓ (math correct) |
| epoch 5 bpc | 2.5380 | 2.5380 ✓ |
| ep1 wall | 4.4s | 18.3s |
| ep5 wall | 18.3s | 116.0s |
| Per-epoch (ep1→ep5) | 3.5s | 24.4s |
| Speedup factor | 1.0× | **0.14× (7× SLOWER)** |

Math correctness confirmed to 4 decimals on test bpc. Speed regression is
unambiguous.

## Why the naive split is slower

cuBLAS's complex64 GEMM is internally implemented as 4 fused real-GEMM
operations with shared memory reuse across the four sub-products: a single
read of `A_re` and `A_im` feeds both `A_re @ B_re` and `A_re @ B_im`, etc.
Splitting the operation into 4 explicit PyTorch matmul calls forces:
- 4 separate kernel launches per complex matmul
- HBM rereads of operands (no fusion across the 4 sub-matmuls)
- No cross-product memory reuse

The TF32 speedup over plain FP32 on Ada Lovelace (RTX 4060 Ti) is modest —
~1.5-2× for medium-large GEMMs, not the 5-8× achievable with FP16/BF16.
That ~1.5× is not enough to offset the 4× kernel overhead + bandwidth cost
of the split implementation.

**Naive lesson:** "use Tensor Cores" needs FP16/BF16 to be worth the rewrite.
TF32 alone is too small a gain to compensate for any structural rearrangement.

## Revised path forward

### What does NOT work (per empirical test)
1. ~~Real-valued (re, im) split with FP32 + TF32 mode.~~ Slower at all tested
   sizes. cuBLAS complex64 is already efficient enough that splitting
   regresses.

### What MIGHT work (untested)
1. **FP16/BF16 paired representation.** Same `(re, im)` split BUT in FP16
   or BF16, where Tensor Cores give 8× over FP32. Requires verifying that
   FHRR unit-magnitude phasors maintain precision under FP16. ~2-3 days
   work + verification. Higher upside (potentially 4-6× actual speedup)
   but also higher risk of numerical drift breaking results.
2. **Packed real GEMM.** Stack `(re, im)` along a new dim so that ONE 2N×2N
   real GEMM produces both real and imaginary outputs. Memory cost ~2×.
   Lets cuBLAS handle the fusion. ~1-2 days work.
3. **torch.compile() + amp.autocast on the existing complex64 path.** Newest
   PyTorch can sometimes fuse complex64 ops into single kernels. Low risk,
   low effort — worth a 1-hour spike before bigger rewrites.

### What clearly works (do this first)
1. Stay on complex64 for N ≤ 4096 (current best). No speed problem at this
   scale. The Wave 1 experiment queue runs in minutes per variant.
2. Treat N ≥ 16384 as the trigger to attempt option 3 (torch.compile) first,
   then option 1 (FP16 paired) only if (3) doesn't help. Don't do option 1
   speculatively — empirical EV is now lower than the original estimate.

## Cost-benefit, revised

| Path | Wall-time cost | Expected speedup | Risk |
|---|---|---|---|
| ~~Real-valued FP32 split~~ | 1 day done | **0.14× (regression)** | High — empirically failed |
| torch.compile() spike | 1 hour | 1-3× (uncertain) | Low |
| FP16/BF16 paired | 2-3 days | 4-6× (uncertain) | High — precision unknown |
| Packed 2N×2N real GEMM | 1-2 days | 2-3× (uncertain) | Medium |

## Meta-lesson for the playbook

Karpathy's "predict the result first" rule applied: I predicted 2-5×
speedup, measured 0.14×. Predictions about performance optimizations on
specific hardware are HIGH variance — production GEMM libraries are
heavily tuned and beating them via reimplementation is rare.

**Add to playbook:** before any "this will be faster" rewrite, run a
1-batch benchmark on the proposed new code path FIRST. If the benchmark
doesn't show a speedup, don't do the rewrite.

## Literature audit (2026-05-18, after empirical failure)

A focused research pass confirmed the empirical result with citations.
Summary of the findings (full notes in agent transcript):

1. **cuBLAS complex64 GEMM does NOT use Tensor Cores at all.**
   The `CUBLAS_COMPUTE_32F_FAST_TF32` and `_FAST_16F` enums exist only for
   real `CUDA_R_32F` inputs. The complex variants `CUDA_C_32F` /
   `cublasCgemm` have no documented tensor-core math mode and dispatch
   to FP32 SM cores. There is no PyTorch issue or NVIDIA release note
   announcing a change in this through CUDA 13.2 (Apr 2026).
   Source: NVIDIA cuBLAS docs.

2. **TF32 toggles do literally nothing for complex64.**
   `torch.backends.cuda.matmul.allow_tf32 = True` and
   `torch.set_float32_matmul_precision("high")` only affect real FP32
   matmul. Our experiment confirmed this — the `set_float32_matmul_precision`
   line in the failed rewrite did not change anything for the complex64
   baseline.

3. **The naive (re, im) split is structurally slower.** cuBLAS's
   `cgemm` is already a single fused complex kernel with good memory
   coalescing. Decomposing into 4 PyTorch real matmuls launches 4
   separate kernels and triples memory traffic — matches our 7× slowdown.

4. **DeltaNet, Gated DeltaNet, and Mamba intentionally avoid complex.**
   They explicitly rewrite recurrences as real matmuls "to leverage
   tensor cores" (DeltaNet 2024 §hardware-efficient). Mamba uses real
   diagonals (S4D-Real); only Mamba-3 reintroduces complex, and that as
   a *data-dependent rotary embedding* applied to real tensors. The
   Schlag IDSIA fast-weight toolkit ships a custom real-valued CUDA
   kernel — no complex path. The mainstream literature has voted with
   their feet: complex on GPU is not worth the tooling pain at scale.

5. **torch.compile is buggy on complex64 as of 2026** (PyTorch issue
   #171850). Not a reliable acceleration route.

6. **The only credible speedup path** is `torch.view_as_real` + packed
   2N×2N real GEMM, which doubles arithmetic and is only a win when N is
   large enough that the tensor-core benefit exceeds the 2× arithmetic
   penalty. At N=4096 this is firmly NOT the case. Even at N=16384,
   marginal — would need Nsight Compute profiling to verify tensor-core
   engagement before believing the rewrite is worth it.

## Recommended action (final)

**Do nothing. complex64 is the right choice at our scale.** At N≤16384
with B=64, our hot-loop GEMMs are sub-millisecond on plain CUDA cores.
We are bandwidth-bound long before compute-bound, and cublasCgemm is
already a single fused kernel with good memory coalescing.

Engineering budget should go to the algorithmic side (the FHRR memory
itself, the Hebbian update rule), where the ceiling is much higher than
a 2× kernel win.

## Trigger conditions to reopen

Reopen this pin only if ALL of the following hold:
1. We have profiled the current implementation with Nsight Compute and
   confirmed that GEMM is the dominant cost (not Python overhead,
   pool insertion, or data loading).
2. N ≥ 32768 is necessary for an experiment we actually want to run.
3. A 60-line micro-benchmark (per Q5 of the audit: warmup + ≥100
   timed reps with `torch.cuda.Event`, median + p10/p90) shows a clear
   ≥2× speedup from `torch.view_as_real` + packed-real GEMM at the
   target N.

If only condition (2) fires without (1) and (3), the right move is to
profile and benchmark, NOT to rewrite.

## Benchmark protocol (lifted from literature audit Q5)

When we eventually do need to benchmark a rewrite candidate:

```python
import torch
torch.backends.cudnn.benchmark = True
# Lock GPU clocks if possible (nvidia-smi -lgc <max_freq>)

def benchmark(fn, *args, warmup=20, iters=100):
    for _ in range(warmup): fn(*args)
    torch.cuda.synchronize()
    events = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True))
              for _ in range(iters)]
    for s, e in events:
        s.record(); fn(*args); e.record()
    torch.cuda.synchronize()
    times = sorted(s.elapsed_time(e) for s, e in events)
    return {"median_ms": times[iters // 2], "p10_ms": times[iters // 10],
            "p90_ms": times[9 * iters // 10]}
```

Decision rule: if surrogate predicts < 1.5× and we cannot prove tensor-core
engagement via Nsight Compute, **do not rewrite.** Below 2×, kernel-launch
overhead and memory-traffic increase routinely erase predicted gains.
