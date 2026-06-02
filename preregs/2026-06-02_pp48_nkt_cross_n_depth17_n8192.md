# Pre-registration: pp48_nkt_cross_n_depth17_v1_n8192

**Date:** 2026-06-02
**Anchor:** pp48_nkt_cross_n_depth17_v1_n8192
**Queue:** overnight_queue
**N:** 8192, **Seeds:** 5, **NKT depth:** 17

## Scientific question
Does NKT anti-Hebbian repulsion hold at depth-17 when tested at N=8192 (cross-N envelope)?
Extends depth-13 cross-N (N=8192, HARD_PASS) to depth-17.

## Pre-registered bands

**HARD-PASS:** pos_retrieval_rate >= 0.75 AND nkt_repulsion_rate >= 0.65.
**MIDDLE:** 1/2 conditions met.
**HARD-FAIL:** pos_retrieval_rate < 0.40 OR nkt_repulsion_rate < 0.30.

## Calibration rationale
Same bands as depth-13 cross-N which was HARD_PASS. N=8192 gives alpha=0.0134 (even lower than N=4096 0.027). Algebraic argument for repulsion validity is N-agnostic (depends only on alpha < alpha_c). HP bands unchanged from prior confirmed anchors.

## N-suffix section
Anchor _n8192; production N = 8192; scripts enforce N = _N_SUFFIX = 8192.

## Timeout estimate
depth-13 cross-N N=8192 smoke ~ 18s at N=1024 smoke. depth-17 slightly more tree traversal.
formula: ceil(1.5 * 25 * (8192/1024)^1.5 * (5/2)) = ceil(1.5 * 25 * 22.6 * 2.5) = ceil(2119) = 2400
timeout_s = 2400
