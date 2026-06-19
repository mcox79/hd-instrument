# Pre-registration: combo2_p4_l3_signed_am_v1_n4096

**Date:** 2026-06-02
**Script:** experiments/exp_combo2_p4_l3_signed_am_v1_n4096.py
**Queue:** overnight_queue (GPU)
**N:** 4096 (PROT-018 binding)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (l3_fid=1.0, b_repulsion=1.0, parity_contam=0.0; wall=0.32s/seed)

## Hypothesis

Wave 4 COMBO-2: p=4 polynomial DAM + L3 hierarchical composition + signed-AM B-pattern
repulsion at N=4096 produces measurable end-to-end capability. Unlocked by COMBO-1 v2
HP1+HP2 PASS (p>2 viability confirmed).

## Metrics

- `l3_fidelity_A`: end-to-end L3 fidelity (noisy L3 query -> L1 comparison)
- `b_repulsion_rate`: fraction of B-patterns repelled from attractor basin
- `parity_contamination`: fraction of A-retrievals contaminated by B-attractor basin

## Thresholds (pre-registered)

**HARD_PASS:** l3_fidelity_A >= 0.85 AND b_repulsion_rate >= 0.95 AND parity_contamination <= 0.05
**HARD_FAIL:** l3_fidelity_A < 0.50 OR b_repulsion_rate < 0.50
**MIDDLE_BAND:** 2/3 conditions met

## Timeout estimate

smoke_wall_s=0.32, FULL_N/smoke_N=1 (same N), FULL_seeds/smoke_seeds=2.5, scaling_exp=1.5
timeout = ceil(1.5 * 0.32 * 1.0 * 2.5) = ceil(1.2) -> 600s (padded for 5 seeds x larger M)

## N-suffix binding

PROT-018: anchor name contains _n4096; N = 4096 in script (verified).
