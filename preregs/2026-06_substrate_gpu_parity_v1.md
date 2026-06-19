# Pre-registration: substrate_gpu_parity_v1

**Date:** 2026-06-11
**Anchor:** substrate_gpu_parity_v1
**Queue:** overnight_queue (GPU)
**N:** 8192, **Seeds:** 3 (full), **Device:** CUDA

## Scientific question
Does the substrate FHRR algebra (validated on CPU numpy complex64) reproduce faithfully in torch.complex64 on CUDA?
Production substrate-as-LLM-memory runs on GPU, so a divergence between numpy-CPU and torch-GPU complex algebra would be
a deployment blocker. Ports four representative gates -- basic bind/unbind recall, write-lock core protection, per-role
domain isolation, 3x-redundant denoise -- to torch on DEV=cuda and checks each reproduces its CPU-validated band.

## Pre-registered bands

**HARD-PASS:** all 4 reproduce CPU bands: basic recall >=0.95, write-lock locked-core >=0.95, per-role >=0.90 AND
> shared by >=0.15, 3x-redundant >=0.95.

**MIDDLE:** 3 of 4 reproduce.

**HARD-FAIL:** <3 reproduce (torch.complex64 algebra diverges from CPU -> deployment blocker).

## Calibration rationale
The bands are exactly the CPU pre-registered bands for the same gates (write-lock 1.0, per-role 1.0 vs shared, 3x 0.983
at N=8192). GPU parity means matching those numbers within seed noise. A drop would indicate a real numerical divergence
(complex dtype handling, reduction order) that must be caught before any GPU deployment. Smoke (1 seed, N=8192) confirmed
all four pass on CPU fallback (basic=1.0, write-lock=1.0, per-role=1.0, 3x=0.963); the GPU run confirms torch-CUDA parity.

## N-suffix section
N=8192 complex64 (tiny; ~64KB/vector). Fast (seconds); fits 8GB GPU trivially. Per-seed checkpoint via _seed_checkpoint.
