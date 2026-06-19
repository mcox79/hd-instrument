# Pre-registration: wave14_moe_remoe_relu_router_v1

**Date:** 2026-05-27
**Script:** experiments/exp_wave14_moe_remoe_relu_router_v1.py
**Queue:** remote_cpu_queue (CPU; ~2000-4000s)
**Trigger:** exp_wave14_moe_cosine_router_v1 returns COSINE_ROUTER_HARD_FAIL

## Hypothesis

ReLU-gated routing (ReMoE ICLR 2025 style) applied to cosine-dot scores gives
dynamic K_eff ~ K/2 for BSC anchors, potentially resolving the entropy collapse.

## Design

K sweep: {4, 8, 16, 32, 64}, N=4096, 3 seeds, 3 variants: ReLU-cosine,
Threshold-cosine (tau = 0.1*sqrt(N)), Top-2 cosine.

## Pre-registered bands

- **HARD-PASS:** K_eff@K=16 in [6, 12] AND entropy < 2.5b AND retention_delta >= -0.005
- **HARD-FAIL:** K_eff < 2 or > 14 OR entropy > 3.5b OR retention_delta < -0.015
- **MIDDLE:** partial improvement; test at larger N
