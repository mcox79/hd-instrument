# Prereg: q_b1_chain_depth_90_v1_n8192

**Date:** 2026-06-02
**Anchor:** q_b1_chain_depth_90_v1_n8192
**Queue:** overnight_queue
**N:** 8192, **Seeds:** 5 (7, 17, 23, 31, 41), **Chains:** 15, **Background:** 200

## Hypothesis
Q-B1 heteroassociative chain maintains statistically significant retrieval fidelity at depth-90. Ceiling chase from depth-80 HARD_PASS (cycle 16). Flat-profile confirmed d50-d80. Push slope to d90.

## Pre-registered Bands
- **HARD-PASS:** d5>=0.95 AND d10>=0.88 AND d20>=0.70 AND d30>=0.55 AND d45>=0.40 AND d90>=0.074
- **HARD-FAIL:** d5<0.80 OR d10<0.65 OR d20<0.40 OR d90<0.05
- **MIDDLE:** d90 in [0.05, 0.074) while earlier depths meet HP
- **Calibration:** d80 HARD_PASS anchor; d90 extrapolated from empirical Q-B1 table with lambda=0.030 (conservative for d>80). HP=0.074; HF=0.05 (~2.5x below HP). Flat-profile d50-d80 suggests actual slope may be flatter than extrapolation.

## N-suffix
PROT-018: production N=8192 matches anchor suffix _n8192.

## Timeout estimate
- Smoke N=1024, seeds=2; FULL N=8192, seeds=5, scaling_exp=2.0 (N^2 H matrix dominates)
- Formula: ceil(1.5 * smoke_wall_s * (8192/1024)^2.0 * (5/2))
- = ceil(1.5 * smoke_wall_s * 64 * 2.5) = ceil(240 * smoke_wall_s)
- smoke_wall_s measured from run; estimated ~20s => timeout = ceil(240*20) = 4800s
- Actual timeout set per ship_anchor.py formula from measured smoke wall.
