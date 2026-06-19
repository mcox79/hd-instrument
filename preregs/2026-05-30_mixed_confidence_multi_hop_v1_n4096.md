# Pre-reg: mixed_confidence_multi_hop_v1_n4096

**Date:** 2026-05-30
**Anchor:** mixed_confidence_multi_hop_v1_n4096 (S9, E3.4)
**Script:** experiments/exp_mixed_confidence_multi_hop_v1_n4096.py
**Queue:** overnight_queue (GPU)
**Parent priorities:** Per-fact confidence metadata propagation through
multi-hop reasoning.

## Hypothesis

At least one path (B/D/E) produces calibrated confidence output
(predicted X% correct equals actual X% correct +/- 15%) AND
confidence-aware accuracy >= confidence-blind baseline AND latency
overhead <= 20%.

## Pre-registered bands

| Outcome      | Condition                                                              |
|--------------|------------------------------------------------------------------------|
| HARD_PASS    | At least one path: calibrated AND acc>=blind AND lat_overhead<=20%      |
| HARD_FAIL    | No path produces calibrated confidence (calib_dev > 0.15 for all)       |
| MIDDLE_BAND  | otherwise                                                              |

## Fact corpus

- 50% high (1.0), 30% medium (0.7), 20% low (0.4)

## Confidence propagation

- Path B: continuous vectors weighted by confidence (W_conf = (vals *
  conf).T @ keys / N).
- Path D: confidence acts as Bayesian prior (log p added to posterior).
- Path E: spectral coherence; confidence-weighting embedded via W_conf.

## Calibration metric

Path confidence = mean of per-hop fact confidences along the path.
Bin into 3 buckets (low/med/high). calib_dev = mean over buckets of
|predicted_acc - actual_acc|.

## Self-test

- N == 4096 (PROT-018).
- Smoke at N=1024 M=64 produces calib_dev_b and acc_*_blind/conf
  non-null.

## Timeout estimate

5 seeds at fixed config; per seed ~10s on GPU (6 mode-cell calls).
~50s baseline + GPU overhead. **timeout_s = 21600** per user spec.

## Production config

N=4096, M=2048, depth=5, K_paths=100, seeds=[7,17,23,31,41].

## N-suffix binding

_n4096 -> production N = 4096 (PROT-018).
