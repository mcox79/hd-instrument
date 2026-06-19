# Pre-registration: substrate_gpu_capacity_scaling_v1

**Date:** 2026-06-11
**Anchor:** substrate_gpu_capacity_scaling_v1
**Queue:** overnight_queue (GPU)
**Dims:** {4096, 8192, 16384, 32768}, **K-grid:** {100..6400}, **V:** 5000, **Device:** CUDA

## Scientific question
How does substrate shard capacity (max facts-per-shard at recall >= 0.90) scale with vector dimension N? Production must
size N for a target facts-per-shard; the VSA capacity law predicts capacity grows ~linearly with N. Measures recall of a
single additive FHRR shard holding K bound key->value pairs (cleanup over a V=5000 codebook) across N and K on CUDA. The
large-N sweep (up to 32768) is GPU-specific -- CPU is too slow for it.

## Pre-registered bands

**HARD-PASS:** capacity(N) monotonically increasing in N AND capacity(32768) >= 4x capacity(4096) (dimension-capacity
scaling law holds; production sizing is predictable).

**MIDDLE:** monotonic but ratio < 4x.

**HARD-FAIL:** capacity non-monotonic in N (no clean scaling law).

## Calibration rationale
VSA/HRR theory says additive-bundle capacity scales ~linearly with dimension. Going from N=4096 to N=32768 is an 8x dim
increase, so a >=4x capacity increase is a conservative bar for the law holding (sub-linear tolerated). Smoke (N=4096 vs
8192, CPU fallback) already showed K=100 -> K=400 (4x for a 2x dim jump), consistent with the law; the full GPU run maps
the curve to 32768 for production sizing tables.

## N-suffix section
Dims up to 32768 complex64 (a few thousand vectors; tiny memory, fits 8GB). Fast (matmuls) on GPU. Per-N checkpoint.
