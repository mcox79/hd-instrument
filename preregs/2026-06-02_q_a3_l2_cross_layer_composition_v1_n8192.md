# Pre-registration: q_a3_l2_cross_layer_composition_v1_n8192

**Date:** 2026-06-02
**Script:** experiments/exp_q_a3_l2_cross_layer_composition_v1_n8192.py
**Queue:** overnight_queue (GPU)
**N:** 8192 (PROT-018 binding)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (outer_fid=1.0, inner_fid=1.0, l2_acc=1.0; wall=7.6s/seed)

## Hypothesis

Q-A3 L=2 cross-layer composition at N=8192 (n4096 PASSed in v333). Production-envelope
extension: larger N should reduce interference and improve fidelity (expected >= n4096 result).

## Metrics

- `outer_fidelity`: L2 outer-layer retrieval fidelity
- `inner_fidelity`: L2 inner-layer retrieval fidelity (after decode)
- `l2_accuracy`: fraction of L2 queries where inner retrieval succeeds (cosine > 0.5)

## Thresholds (pre-registered)

**HARD_PASS:** outer_fidelity >= 0.93 AND inner_fidelity >= 0.93 AND l2_accuracy >= 0.85
**HARD_FAIL:** any fidelity < 0.60 OR l2_accuracy < 0.50
**MIDDLE_BAND:** 2/3 conditions met

## Timeout estimate

smoke_wall_s=7.6, FULL_N/smoke_N=1 (same N), FULL_seeds/smoke_seeds=2.5, scaling_exp=1.5
timeout = ceil(1.5 * 7.6 * 1.0 * 2.5) = ceil(28.5) -> 900s

## N-suffix binding

PROT-018: anchor name contains _n8192; N = 8192 in script (verified).
