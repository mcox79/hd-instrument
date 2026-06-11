# Pre-registration: substrate_gpu_throughput_v1

**Date:** 2026-06-11
**Anchor:** substrate_gpu_throughput_v1
**Queue:** overnight_queue (GPU)
**N:** 8192, **V (codebook):** 20000, **NQ (queries):** 4000, **Device:** CUDA

## Scientific question
How fast is substrate cleanup (nearest-codebook value lookup) on GPU? Production substrate-as-LLM-memory does a cleanup
on every recall, so the query rate over a realistic value codebook (V=20000) determines whether substrate memory is
real-time. Measures batched-cleanup queries/sec and GPU-vs-CPU speedup at N=8192 complex64 on CUDA, with a recall
correctness check (throughput must not be bought with wrong answers).

## Pre-registered bands

**HARD-PASS:** GPU batched cleanup >= 5000 queries/sec over V=20000 AND recall == 1.0 (>=0.999).

**MIDDLE:** 1000-5000 q/s with recall >= 0.99.

**HARD-FAIL:** < 1000 q/s OR recall < 0.99.

## Calibration rationale
5000 q/s over a 20K codebook is a real-time bar for an LLM-memory backend (sub-millisecond per lookup amortized in a
batch). The operation is a single (NQ,N)x(N,V) complex matmul + argmax, which GPUs do extremely well, so >=5000 q/s is
expected; falling short would indicate a complex-dtype or memory-bandwidth bottleneck worth surfacing before deployment.
Smoke (V=2000 CPU fallback) confirmed recall=1.0 and the logic; the GPU run quantifies the production rate.

## N-suffix section
N=8192 complex64; V=20000 codebook (~3.2 GB? no -- 20000x8192 complex64 = ~1.3 GB; safe on shared 8GB). Fast (one matmul, seconds).
Per-trial checkpoint via _seed_checkpoint.
