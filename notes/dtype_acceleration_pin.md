# PINNED: dtype / Tensor Core acceleration

Date pinned: 2026-05-18
Status: Open. Defer until N=4096 Wave 1 experiments complete, OR until we
want to scale to N ≥ 16384 / 1MB+ corpus where the speed penalty becomes
blocking.

## Problem

All FHRR atoms and W are stored as `complex64` (FP32 real + FP32 imag).
PyTorch's BLAS for complex64 falls back to plain FP32 CUDA cores. RTX 4060
Ti's Tensor Cores accelerate FP16/BF16/TF32 matmul by 5-10× but cannot
operate on complex types directly. We are leaving ~8× speedup on the table
for the entire training and inference hot loop.

This became visible at N=16384 (W=2GB) where the wall time was ~6× higher
than the FLOPs prediction predicted, because the bandwidth-bound matmul
couldn't be partially absorbed by Tensor-Core-accelerated compute.

## Graded fix path

### Step 1 — Free check: TF32 matmul mode (1 line)
```python
torch.set_float32_matmul_precision("high")
```
Expected speedup for us: **zero**. TF32 is for real-valued FP32 matmul;
complex64 matmul does not use it. Worth confirming before any other work.
Falsifies the "free win" hypothesis cleanly.

### Step 2 — Real-valued split (1 day, ~2-5× speedup)

Represent each complex FHRR vector of length N as a pair of real vectors
(Re, Im) of length N each. Same memory footprint (2N FP32 = N complex64).

Helpers needed:
```python
def complex_mul(a_re, a_im, b_re, b_im):
    """Returns (re, im) of element-wise complex product."""
    return a_re * b_re - a_im * b_im, a_re * b_im + a_im * b_re

def complex_matmul(A_re, A_im, B_re, B_im):
    """Returns (re, im) of A @ B as complex."""
    return (A_re @ B_re - A_im @ B_im,
            A_re @ B_im + A_im @ B_re)

def complex_conj(x_re, x_im):
    return x_re, -x_im
```

Refactor scope:
- `hdlab/atoms.py`: `make_atom_fhrr` returns (re, im) tuple
- `hdlab/binding.py`: bind/unbind operate on tuples
- All experiment files: replace `@` involving complex with `complex_matmul`,
  `.conj()` with `complex_conj`, `.abs()` with `sqrt(re² + im²)`
- Verification: each experiment that currently produces a known result
  (e.g., 2.4994 baseline) must reproduce within FP32 tolerance.

Speedup mechanism: FP32 matmul via cuBLAS uses Tensor Cores in TF32 mode
(FP32 input, FP32 output, but multiplications done at TF19 precision).
For our FHRR phase data, TF19 precision is plenty — phases are bounded.

Expected speedup: 2-5× on the matmul hot path. Memory same.

### Step 3 — FP16 / BF16 (additional 2-4× over Step 2, ~1 day verification)

Once real-valued, switch the dtype to FP16 or BF16. FHRR phasors have
bounded magnitude (~unit), so dynamic range is not a blocker. Precision
loss is the concern: 2.4994 → 2.4994 ± 0.005 is acceptable, 2.4994 → 2.55
is not. Run the baseline at each dtype and compare.

BF16 has wider range but no fp16 ops on RTX 4060 Ti Tensor Cores (it does
have BF16 ops on Ampere/Ada). FP16 has wider Tensor Core support but
narrower range.

Recommend BF16 if it works, FP16 as a fallback. Both give Tensor Core
acceleration for the matmul hot path.

## Should we do this NOW?

No, not yet. Reasoning:
- N=4096 runs in 52s. Everything in the Wave 1 queue is tractable.
- The work is high-confidence-low-risk but not zero-risk. Verification
  against current baseline (2.4994) is mandatory before we trust new results.
- The marginal value is for N ≥ 16384, 1MB+ corpus, and faster
  multi-seed runs. Until we *want* those things, the speedup is unused.

## When to revisit

Trigger conditions (any of):
1. We commit to a Wave 2 1MB+ corpus run.
2. We need 5-seed runs to take less than ~10 min total.
3. We want N ≥ 16384 in the scaling story.
4. We see a tractable Tensor Core path in a related paper (e.g., DeltaNet
   reference impl) we can lift directly.

## Cost-benefit summary

| Item | Wall-time cost | Speedup factor | Verification cost |
|---|---|---|---|
| Step 1 (TF32 mode) | 1 min | 1× (no effect on complex) | 0 |
| Step 2 (real-valued split) | 1 day | 2-5× | 1 day (re-run baseline at every variant) |
| Step 3 (FP16/BF16) | 1 day extra | 2-4× over Step 2 | 1 day extra |

So full path: ~4 days total work, 5-20× speedup on hot loop.
Defer until trigger conditions met.
