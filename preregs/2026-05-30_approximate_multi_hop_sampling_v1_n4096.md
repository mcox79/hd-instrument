# Pre-reg: approximate_multi_hop_sampling_v1_n4096

**Date:** 2026-05-30
**Anchor:** approximate_multi_hop_sampling_v1_n4096 (S10, E6.2)
**Script:** experiments/exp_approximate_multi_hop_sampling_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Approximate multi-hop via random sampling;
latency-accuracy tradeoff per path.

## Hypothesis

At least one of B/D/E achieves >=3x latency reduction with <=5% accuracy
loss at some sampling rate (in 3+ seeds).

## Pre-registered bands

| Outcome      | Condition                                                                |
|--------------|--------------------------------------------------------------------------|
| HARD_PASS    | >=1 path: >=3x speedup AND <=5% acc loss in >=3/5 seeds                  |
| HARD_FAIL    | All 3 paths degrade >50% even at 75% sampling rate                       |
| MIDDLE_BAND  | otherwise                                                                |

## Sampling per path

- Path B: sample subset of W columns at each retrieval (col_rate).
- Path D: sample subset of candidate paths for likelihood (path_sample_rate).
- Path E: top-k partial spectral decomposition (spectrum_rate).

Rates: [0.10, 0.25, 0.50, 0.75, 1.00].

## Self-test

- N == 4096 (PROT-018).
- Smoke at N=1024 M=256 produces rate_results for 2 rates per path.

## Accuracy normalization

E uses AUC -> (auc - 0.5) * 2 for fair comparison vs B/D accuracy in
[0,1].

## Timeout estimate

5 seeds x 5 rates x 3 paths = 75 measurements. Per measurement ~2s
including sampling overhead. ~150s baseline + GPU compile.
**timeout_s = 14400** per user spec.

## Production config

N=4096, M=2048, depth=5, K_paths=500, rates=[0.10,0.25,0.50,0.75,1.00],
seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
