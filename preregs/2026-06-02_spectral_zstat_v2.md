# Pre-registration: spectral_zstat_v2

**Date:** 2026-06-02
**Anchor:** spectral_zstat_v2
**Script:** experiments/exp_spectral_zstat_v2.py
**Queue:** remote_cpu_queue
**Timeout:** 1800s

## Scientific question

Does the MP spectral Z-statistic distinguish duplicate-loaded Hopfield matrices
(increasing k duplicates) with Z growing linearly in k and a detectable knee at
k_crit = 3 * N^(1/3)?

## Design fix from v1

v1 timed out at 300s due to O(k*N^2) sequential outer product loop.
v2 uses vectorized build_w_vectorized(): dups.T @ dups / N = O(M*N).
Estimated FULL time ~500s.

## Bands (pre-registered)

**HARD-PASS (HP):**
- >= 80% seeds have crossing point Z >= 3.0 at some k in sweep
- Spearman rho(k, Z) >= 0.70 (monotone Z vs k)

**MIDDLE:**
- 50-79% seeds show crossing, OR Spearman 0.40-0.69

**HARD-FAIL (HF):**
- < 20% seeds show Z >= 3.0, OR Spearman < 0.20

## Smoke result
HARD_PASS: crossing_seeds=2/2 (100%), median_k3=6 (theory=48.0), Spearman=1.000
Wall time: 26s (2 seeds). FULL estimate: ~500s (5 seeds, larger k sweep).

## PROT-018
Anchor does not contain _nN suffix. Production N=4096 declared in script.
