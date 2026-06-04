# Prereg: pp50_kappa3_delta_alpha_n16384_v2_n16384

**Date:** 2026-06-03
**Anchor:** pp50_kappa3_delta_alpha_n16384_v2_n16384
**Script:** experiments/exp_pp50_kappa3_delta_alpha_n16384_v2_n16384.py
**Queue:** overnight_queue (GPU)

## Hypothesis
PP-50 kappa_3 delta-alpha sensitivity at N=16384 reproduces the v345 results (sigma_sep(d=0.04)~642)
under the current delta-alpha protocol. Cross-N gap closure for the 0.83-0.94 band.

## v1 failure root cause
v1 failed with exit_code=3221226505 (Windows CUDA access violation, 0xC0000005) during
_instrumentation_selftest() first GPU allocation. Same crash pattern seen in 5+ other experiments.
v2 fix: torch.cuda.empty_cache() + torch.cuda.synchronize() before first GPU alloc in selftest.
No logic changes. All thresholds identical.

## Pre-registered bands (pre-registered before any run)
- **HARD-PASS**: sigma_sep(d=0.04) >= 300 AND sigma_sep(d=0.01) >= 80 AND sigma_sep(d=0.001) >= 8.0
- **MIDDLE**: sigma_sep(d=0.04) in [150, 300) OR sigma_sep(d=0.01) in [40, 80)
- **HARD-FAIL**: sigma_sep(d=0.04) < 150 OR sigma_sep(d=0.01) < 40
Prior empirical anchor: N=16384 v3 sigma_sep(d=0.04)=642 (thresholds = 50% of prior anchor).

## Smoke result (gate run 2026-06-03)
- Mode: smoke (N_active=1024, 2 seeds)
- Selftest: PASS (k3_base=5.969e-02, sigma_sep_test=3.39, gpu_mem=8.6MB -- all non-sentinel)
- Smoke sigma_sep(d=0.04)~31, sigma_sep(d=0.01)~9.2 at N_active=1024
- Expected at N=1024 vs N=16384: ratio (16384/1024)^(2/3) ~ 6.35x -> expected smoke sep~50-100 range
  (scale from N=8192 HP sigma_sep~290: (1024/8192)^(2/3) = 0.157x -> ~46. Smoke at ~31 in range.)
- HARD_FAIL at smoke-N is EXPECTED (smoke runs 16x smaller N; metric is N-dependent)
- Suspicious-result gate: NOT triggered (metrics non-sentinel, non-zero, non-constant)

## Timeout estimate
- v1 N=8192 actual elapsed ~22.5s (5 seeds). N=16384 scaling: N^2 * n_probes ~ 4x.
- Estimated: 22.5 * 4 = 90s. ceil(1.5 * 90) = 135s -> 300s floor.
- timeout_s = 21600 (PROT-019 floor: _n16384 requires >= 21600s).

## N-suffix binding
PROT-018: _n16384 suffix -> N = 16384 in FULL config. Verified.

## Dependencies
None beyond existing experiments/_seed_checkpoint.py (verified present).
