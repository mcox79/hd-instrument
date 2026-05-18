# PINNED: dtype / Tensor Core acceleration

Date pinned: 2026-05-18
Date revised: 2026-05-18 (after empirical test below)
Status: Open. The cheap path was empirically tested and **did not work**.
The real speedup path is significantly more work than initially estimated.

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
