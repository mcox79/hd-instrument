# Pre-reg: spectral_path_identification_v1_n4096

**Date:** 2026-05-30
**Anchor:** spectral_path_identification_v1_n4096
**Script:** experiments/exp_spectral_path_identification_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Multi-hop Path E (spectral coherence)

## Hypothesis (RESEARCH-QUALITY; P=0.30-0.40)

The substrate's spectral signature (top-K codebook similarity profile of
substrate responses) carries multi-hop path information: coherent paths
exhibit aligned spectral signatures across consecutive hops, incoherent
paths do not. AUC of coherence-score for coherent-vs-incoherent path
classification reaches >= 0.80 at depth 3.

## Pre-registered bands

| Outcome      | Condition                                                                 |
|--------------|---------------------------------------------------------------------------|
| HARD_PASS    | spectral-coherence AUC >= 0.80 at depth 3 in >=3/5 seeds                  |
| HARD_FAIL    | AUC <= 0.55 at every depth in {2,3} in >=3/5 seeds (no spectral signal)  |
| MIDDLE_BAND  | otherwise                                                                 |

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: this is exploratory. P=0.30-0.40.
KF-45 passed 1/3 channels (commit 919a901) which provides weak prior. HARD_FAIL
set to ~chance to make the negative result decisive.

## Self-test

- N == 4096 (PROT-018).
- roc_auc returns 1.0 for [0.1,0.2,0.8,0.9]/[0,0,1,1] (oriented correctly).
- Verdict gates return HARD_PASS / HARD_FAIL on synthetic cells.
- Forward pass at N=1024, M=32, depth=2 returns AUC in [0,1].

## Timeout estimate

smoke_wall_s ~ 0.1s. FULL: 2 depths x 5 seeds = 10 cells with 80+80 paths each.
scaling_exp=1.5. Estimated ~1200s.
**timeout_s = 21600**

## Production config

N=4096, M=256, depths=[2,3], n_pos=80, n_neg=80, seeds=[7,17,23,31,41],
top_k_sig=16.

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
