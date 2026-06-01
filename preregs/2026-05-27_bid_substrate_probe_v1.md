# Pre-registration: bid_substrate_probe_v1 (Binary Intrinsic Dimension substrate probe)

**Date filed:** 2026-05-27
**Anchor:** bid_substrate_probe_v1
**Script:** experiments/exp_bid_substrate_probe_v1.py
**Queue:** remote_cpu_queue
**Parent handoff:** notes/exp_dev_handoff_research_negative_results_meta_analysis_2026-05-27.md

## Hypothesis

The substrate's accessible bipolar state space has an intrinsic dimension (measured via
TwoNN BID estimator) that falls OUTSIDE all three known Hopfield class bands
(retrieval, spin-glass, paramagnetic), providing framework-free evidence for novel-class
status (H1). This directly tests the P(H1)=0.42 posterior from the 15-rejection meta-analysis.

## Experiment design

- N sweep: [512, 1024, 2048]
- Seeds: [7, 17, 23, 31, 41] (5 seeds full)
- M_stored: int(0.14 * N) per seed (standard ALPHA_C = 0.14 operating load)
- S_probes: 200 probe samples per (N, seed)
- BID estimator: TwoNN Pareto MLE (Facco et al. 2017; d = 1/mean(log(mu_i)))
- Hamming distance used for bipolar vectors

## Known Hopfield class BID reference bands

| Class | BID band | At N=1024 | At N=2048 |
|---|---|---|---|
| Retrieval | [1.0, 2.5] (absolute) | [1.0, 2.5] | [1.0, 2.5] |
| Spin-glass | [N/4, N/2] | [256, 512] | [512, 1024] |
| Paramagnetic | [N-5, N] | [1019, 1024] | [2043, 2048] |

Source: arxiv 2601.17427 (dimensionality of Hopfield models).

## Pre-registered thresholds

### HP1 (novel class by BID geometry)
- bid_estimate at N=1024 lies outside ALL THREE reference bands
- In >= 4/5 seeds (fraction >= 0.80)
- => P(H1) updates to >= 0.65

### HP2 (BID-vs-P(q) joint signature is substrate-distinctive)
- HP1 condition satisfied AND
- mean_overlap at N=1024 NOT matching retrieval (>0.7 with HP1 outside retrieval-band BID)
- => substrate-native fingerprint confirmed

### HP3 (BID thermodynamically stable)
- bid_estimate / N within +/- 5% across N in {512, 1024, 2048}
- => BID is a true thermodynamic invariant, not finite-N artifact

### HF1 (substrate is a known class)
- bid_estimate at N=1024 falls INSIDE one of the 3 reference bands
- In >= 4/5 seeds
- => H2 prevails; P(H2) updates to >= 0.55

### HF2 (BID unstable across N)
- bid_estimate / N drifts >= 20% from N=512 to N=2048
- => BID is finite-N artifact; no phase claim possible

### MIDDLE_BAND
- HP1 pass but HP3 fail, OR
- <4/5 seeds outside known classes at N=1024

## Calibration probe note

Smoke at N=512: BID=48.69, NOT in any known class band.
- Retrieval band [1.0, 2.5]: bid=48.69 >> 2.5. Not retrieval.
- Spin-glass band [128, 256]: bid=48.69 < 128. Not spin-glass.
- Paramagnetic band [507, 512]: bid=48.69 << 507. Not paramagnetic.
Substrate BID falls in an intermediate range (~N/10 at N=512) that matches no known class.
This is a STRONG preliminary H1 signal - the full run will determine if this is stable.

## Timeout estimate

Smoke: N=512, 1 seed -> 0.2s.
Full: N in {512, 1024, 2048}, 5 seeds.
- N=512 scaling from smoke: 0.2s/seed * 5 seeds = 1s for N=512
- N=1024: scaling_exp=1.5 -> 0.2 * (1024/512)^1.5 * 5 = 0.2 * 2.83 * 5 = 2.83s
- N=2048: 0.2 * (2048/512)^1.5 * 5 = 0.2 * 8.0 * 5 = 8s
- Total: ~12s for full run.
- Safety margin: 1.5 * 12 = 18s. Generous ceiling: 1800s.
- timeout_s = 1800 (well under 14400s threshold)

NOTE: TwoNN inner loop is O(S^2) for pairwise distances; S=200 fixed. Dominant cost is
W-matrix construction O(M * N^2). At N=2048, M=286 patterns: 286 * 2048^2 ~ 1.2e9 ops.
With numpy vectorized outer products, ~5-10s per seed at N=2048. Revised estimate: 5 seeds * 10s * 3 N = 150s * 1.5 safety = 225s. 1800s is 8x margin - very safe.

## N-suffix

No _nN suffix. Multi-N sweep; no single N is primary. Production N sweep = [512, 1024, 2048].

## Self-tests verified (pre-ship)

1. TwoNN formula: mu=[2.0,2.0,2.0] -> d_hat=1.4427 (matches 1/log(2) exactly)
2. Hamming distance: identical vectors -> 0, antipodal vectors -> N
3. TwoNN on 20 N=8 samples: returns finite d_hat > 0
4. run_one_seed(N=64, seed=17): bid non-null, mean_overlap in [0,1]
5. Multi-scale N=64 and N=256: both finite
6. Selftest PASSED printed to stdout before sweep begins
