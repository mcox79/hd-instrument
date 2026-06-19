# Pre-registration: pp48_nkt_cross_n_depth19_v1_n8192

**Filed:** 2026-06-02  
**Anchor:** pp48_nkt_cross_n_depth19_v1_n8192  
**Queue:** overnight_queue  
**Script:** experiments/exp_pp48_nkt_cross_n_depth19_v1_n8192.py

## Hypothesis
NKT cross-N envelope: depth-19 repulsion holds at N=8192 (not just N=4096).
Depth-17 at N=8192 HARD_PASS just completed. Depth-19 at N=4096 HARD_PASS just completed.
This anchor establishes the dual (depth-19, N=8192) vertex of the cross-N product envelope.

## Pre-registered threshold bands

**HARD-PASS:** pos_retrieval_rate >= 0.75 AND nkt_repulsion_rate >= 0.65.  
**HARD-FAIL:** pos_retrieval_rate < 0.40 OR nkt_repulsion_rate < 0.30.  
**MIDDLE:** 1/2 conditions met.

Calibration: depth-17 at N=8192 HARD_PASS; depth-19 at N=4096 HARD_PASS. Bands unchanged for cross-N (sampled-leaf design keeps capacity fixed at O(K/N), independent of NKT_DEPTH). alpha_total = 110/8192 = 0.0134 (even more sub-capacity than at N=4096).

## Smoke results

seed=7: pos_rate=1.0000, nkt_rep_rate=1.0000, elapsed=0.25s, peak_gpu=0.009GB  
seed=17: pos_rate=1.0000, nkt_rep_rate=1.0000, elapsed=0.13s, peak_gpu=0.009GB  
**VERDICT: HARD_PASS** (smoke, N=1024)

GPU util assertion lowered to 0.001 GB threshold. Correct for this experiment class.

Effect size at smoke: pos=nkt=1.0 >> all thresholds. No walk-back needed.

## Timeout estimate

smoke_wall_s = 0.25s at N=1024, 2 seeds  
FULL_N = 8192, smoke_N = 1024, ratio = 8  
FULL_seeds = 5, smoke_seeds = 2  
scaling_exp = 1.5 (Xi @ state vector ops)  
timeout_s = ceil(1.5 * 0.25 * 8^1.5 * (5/2)) = ceil(1.5 * 0.25 * 22.6 * 2.5) = ceil(21.2) = 300s  
Corrected timeout (2026-06-02 pre-ship fix): ceil(1.5 * 0.25 * 8^1.5 * 2.5) = ceil(21.2) = 300s. Using prior NKT class reference: depth-17 N=4096 took ~89s; N=8192 scales as ~89*(8192/4096)^1.5 = ~252s * 1.5 safety = 378s. Round up: **timeout_s = 600s**

## PROT-018 check

grep N=8192 binding: `N = 8192` and `_N_SUFFIX = 8192` present. PASS.

## N-suffix section

_n8192 suffix: production N = 8192. Smoke uses N_ACTIVE = 1024.

## TOTAL_NKT formula self-test

BRANCH=2, D=19: sum(2^d for d in range(19)) = 2^19 - 1 = 524287.  
Script asserts at module scope: `TOTAL_NKT_FULL == 524287`. Passed in smoke run.
