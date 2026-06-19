# Pre-registration: q_a3_l2_cross_layer_composition_v1_n4096

**Date:** 2026-06-02
**Script:** experiments/exp_q_a3_l2_cross_layer_composition_v1_n4096.py
**Queue:** overnight_queue
**N:** 4096 (PROT-018 binding)
**Seeds:** [7, 17, 23, 31, 41]
**Smoke result:** HARD_PASS (all=1.0000; outer_fid=1.0, inner_fid=1.0, l2_acc=1.0)

## Hypothesis

L=2 Hadamard-binding composition (xi_outer = xi_context * xi_inner) supports:
- Outer fidelity >= 0.93: outer layer retrieval accurate
- Inner fidelity >= 0.93: inner layer retrieved via xi_outer_retrieved * xi_context_q
- L2 accuracy >= 0.85: full cross-layer composition accuracy

M_inner=200 (alpha=0.049), M_outer=100 (alpha=0.024) at N=4096.

## Metrics

- `outer_fid`: cosine similarity of retrieved outer pattern
- `inner_fid`: cosine similarity of retrieved inner pattern after unbinding
- `l2_acc`: fraction of fully correct L2 compositions

## Thresholds (pre-registered)

**HARD_PASS:** outer_fid >= 0.93 AND inner_fid >= 0.93 AND l2_acc >= 0.85
**HARD_FAIL:** any fidelity < 0.60 OR l2_acc < 0.50
**MIDDLE_BAND:** above HF, below HP

Walk-back note: smoke was perfect (all 1.0); production M_inner=200 vs smoke M_inner=50 may show degradation. HP thresholds set conservatively.

## Timeout

600s (from: smoke <1s * 5 seeds * 1.5 overhead * N scale = 600s estimated)
