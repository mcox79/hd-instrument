# Prereg: wave14_moe_shift_K_perarm_v1

**Date:** 2026-05-26
**Parent:** wave14_moe_shift_K_scaling_v2 (in-flight)
**Trigger:** ship when v2 shows DIVERGENCE (Arm_A degrades at K>=32 while Arm_C stable)
**Question:** Which substrate mechanism causes K-scaling divergence?

## Hypothesis
Three candidate mechanisms:
- M1 (capacity saturation): M_per_expert / (alpha_c * N) near 1.0 at high K
- M2 (LSH gating degradation): routing_entropy approaches log2(K) at high K
- M3 (intra-expert interference): inter_expert_cosine >= 0.3 at K>=32

## Design
- K sweep: {2, 4, 8, 16, 32, 64}
- N = 2048, M_per_expert = 800
- 5 seeds, remote_cpu_queue (CPU, ~45-90 min)
- Diagnostic metrics per K: retention_A, routing_entropy (bits), inter_expert_cosine, M_to_capacity_ratio

## Pre-registered bands
- **M2_DOMINANT**: routing_entropy at K=32 >= 3.0 bits AND inter_expert_cosine < 0.2
- **M3_DOMINANT**: inter_expert_cosine at K=32 >= 0.3
- **M1_DOMINANT**: M_to_capacity_ratio >= 0.9 AND routing_entropy < 2.0 bits
- **MIXED**: no single mechanism dominant
- **INSTRUMENTATION_FAIL**: routing_entropy NaN or inter_expert_cosine non-finite

## Calibration
No prior empirical anchor. Thresholds set from theory: M2 threshold from log2(32)/2=2.5b plus margin.
M3 threshold from 0.3 cosine as typical partial-correlation threshold. M1 from 90% alpha_c fill.

## Middle-band outcome plan
MIXED result: dispatch research probe on multi-mechanism interactions in MoE gating.
