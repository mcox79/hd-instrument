# Prereg: pp48_nkt_depth_3_baseline_verification_v1_n4096

**Date:** 2026-06-02
**Anchor:** pp48_nkt_depth_3_baseline_verification_v1_n4096
**Queue:** overnight_queue

## Scientific question
NKT depth-3 explicit baseline at N=4096. Total forbidden = 7 patterns.

## Pre-registered thresholds
- HP: pos_retrieval >= 0.90 AND nkt_repulsion >= 0.90 AND tree_structure >= 0.90.
- HARD-FAIL: pos < 0.60 OR nkt_rep < 0.60.
- MIDDLE: 2/3 HP.
Prior empirical: depth-5 HP (0.85/0.80/0.80). Depth-3 HP thresholds higher (fewer forbidden).

## Timeout estimate
Based on depth-7 script (comparable complexity): ~120s smoke N=512. FULL N=4096, 5 seeds, scaling_exp=1.5:
timeout_s = ceil(1.5 * 30 * 8^1.5 * 2.5) = ceil(2545) = **2700s**.

## PROT-018
anchor _n4096; production N = 4096. Verified.
