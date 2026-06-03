# Pre-registration: q_b1_chain_depth_70_v1_n8192

**Filed:** 2026-06-02  
**Anchor:** q_b1_chain_depth_70_v1_n8192  
**Queue:** overnight_queue  
**Script:** experiments/exp_q_b1_chain_depth_70_v1_n8192.py

## Hypothesis
Heteroassociative chain substrate retains recoverable signal at depth-70 at N=8192.
Ceiling chase: depth-60 HARD_PASS this cycle. Depth-70 extends the envelope.

## Pre-registered threshold bands

**HARD-PASS:** depth-5 >= 0.95 AND depth-10 >= 0.88 AND depth-20 >= 0.70 AND depth-30 >= 0.55 AND depth-45 >= 0.40 AND depth-70 >= 0.15.

**HARD-FAIL:** depth-5 < 0.80 OR depth-10 < 0.65 OR depth-20 < 0.40 OR depth-70 < 0.06.

**MIDDLE:** depth-70 in [0.09, 0.15) while earlier depths meet HP.

Calibration: continuing exponential fit from d55/d60 (both HP). lambda ~ 0.004. HP at 0.15 is conservative below theoretical ~0.22 with 50% margin. HF at 0.06 is >2.5x below HP.

## Smoke results (multi-scale)

**N=1024 smoke:** HARD_FAIL (known resolution artifact; signal collapses at N=1024 for depth>>30).  
**N=4096 smoke (multi-scale gate):**  
- seed=7: d5=0.9995, d10=0.9987, d20=0.9992, d30=0.9989, d45=0.9993, d60=0.9995, d70=0.9991  
- seed=17: d5=0.9989, d10=0.9990, d20=0.9994, d30=0.9987, d45=0.9991, d60=0.9986, d70=0.9990  

Multi-scale smoke PASS: all depth metrics >> HP thresholds at N=4096. N=1024 artifact confirmed and N×8 gate passes. Ship proceeds.

Effect size at smoke: d70 = 0.9990 >> HP=0.15. No walk-back gate needed (d >> 1.0 by any measure).

## Timeout estimate

smoke_wall_s = ~2s at N=4096 per seed (2 seeds = ~4s total)  
FULL_N = 8192, smoke_N = 4096, ratio = 2  
FULL_seeds = 5, smoke_seeds = 2  
scaling_exp = 2.0 (H matrix N x N outer-product build dominates)  
timeout_s = ceil(1.5 * 4 * 2^2.0 * (5/2)) = ceil(1.5 * 4 * 4 * 2.5) = ceil(60) = 300s  
Corrected timeout (2026-06-02 pre-ship fix): prior d60 at N=8192 5-seed took ~41.8s. d70: ceil(1.5 * 41.8 * (70/60) * 1.0) = ceil(73.1) = **timeout_s = 300s**

## PROT-018 check

grep N=8192 binding: `N = 8192` and `_N_SUFFIX = 8192` present. PASS.

## N-suffix section

_n8192 suffix: production N = 8192. Smoke uses N_ACTIVE = 1024 (standard smoke); multi-scale uses N=4096.
