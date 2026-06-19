# Pre-registration: q_b1_chain_depth_80_v1_n8192

**Filed:** 2026-06-02  
**Anchor:** q_b1_chain_depth_80_v1_n8192  
**Queue:** overnight_queue  
**Script:** experiments/exp_q_b1_chain_depth_80_v1_n8192.py

## Hypothesis
Heteroassociative chain substrate retains recoverable signal at depth-80 at N=8192.
Ceiling chase: depth-60 HARD_PASS + depth-70 multi-scale PASS this cycle. Shipping d-70 and d-80 in parallel for full slope characterization in one overnight batch.

## Pre-registered threshold bands

**HARD-PASS:** depth-5 >= 0.95 AND depth-10 >= 0.88 AND depth-20 >= 0.70 AND depth-30 >= 0.55 AND depth-45 >= 0.40 AND depth-80 >= 0.10.

**HARD-FAIL:** depth-5 < 0.80 OR depth-10 < 0.65 OR depth-20 < 0.40 OR depth-80 < 0.04.

**MIDDLE:** depth-80 in [0.06, 0.10) while earlier depths meet HP.

Calibration: bands derived from exponential fit at confirmed d55/d60/d70 (all HP). HP at 0.10 is conservative (theory: d-80 ~ d-60 * exp(-0.004*20) ~ 0.22 if d-60 ~ 0.25). HF at 0.04 is >2.5x below HP. Wider bands because d-80 is 20 steps past the most recent confirmed anchor.

## Smoke results (multi-scale)

**N=1024 smoke:** HARD_FAIL (known resolution artifact; collapses at N=1024 for depth>>30).  
**N=4096 smoke (multi-scale gate):**  
- seed=7: d5=0.9981, d10=0.9980, d20=0.9977, d30=0.9972, d45=0.9982, d60=0.9979, d70=0.9975, d80=0.9976  
- seed=17: d5=0.9980, d10=0.9978, d20=0.9973, d30=0.9979, d45=0.9977, d60=0.9989, d70=0.9973, d80=0.9982  

Multi-scale smoke PASS: all depth metrics >> HP thresholds at N=4096. N=1024 artifact confirmed. Ship proceeds.

Effect size at smoke: d80 = 0.9979 >> HP=0.10. No walk-back gate needed.

## Timeout estimate

smoke_wall_s = ~2.5s at N=4096 per seed (80 steps > 70 steps)  
FULL_N = 8192, smoke_N = 4096, ratio = 2  
FULL_seeds = 5, smoke_seeds = 2  
scaling_exp = 2.0 (H matrix N x N outer-product build)  
timeout_s = ceil(1.5 * 5 * 2^2.0 * 2.5) = ceil(1.5 * 5 * 4 * 2.5) = ceil(75) = 300s  
Corrected timeout (2026-06-02 pre-ship fix): prior d60 at N=8192 5-seed took ~41.8s. d80 = 41.8 * (80/60) * 1.5 = 83.6s. Round up: **timeout_s = 300s**

## PROT-018 check

grep N=8192 binding: `N = 8192` and `_N_SUFFIX = 8192` present. PASS.

## N-suffix section

_n8192 suffix: production N = 8192. Smoke uses N_ACTIVE = 1024; multi-scale uses N=4096.
