# Pre-registration: q_a3_l3_cross_layer_composition_v1_n4096

**Date:** 2026-06-02
**Script:** experiments/exp_q_a3_l3_cross_layer_composition_v1_n4096.py
**Queue:** remote_cpu_queue
**N:** 4096 (PROT-018 _n4096 suffix)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (L1_fid=1.0, L2_fid=1.0, L3_fid=1.0, l3_acc=1.0; wall~1.1s)
**Timeout:** 300s (fast algebraic; N=4096 5-seed)

## Hypothesis

Q-A3 L=3 Hadamard cross-layer composition. Prior: L=2 HARD_PASS at N=4096 and N=8192.
L=3 extends with one more Hadamard binding level.

## Metrics

- `l1_fidelity`, `l2_fidelity`, `l3_fidelity`: per-level cosine fidelity
- `l3_accuracy`: end-to-end L=3 query accuracy

## Thresholds

HARD-PASS: all 4 conditions (L1/L2/L3_fid>=0.90, l3_acc>=0.80) in >=4/5 seeds.
HARD-FAIL: any fidelity<0.60 or l3_acc<0.40.
MIDDLE: 3/4 conditions met.
