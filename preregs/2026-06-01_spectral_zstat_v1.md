# Pre-registration: spectral_zstat_v1

**Date:** 2026-06-01
**Anchor:** spectral_zstat_v1
**Script:** experiments/exp_spectral_zstat_v1.py
**Queue:** remote_cpu_queue
**N:** 4096, M=500 (full)

## Hypothesis

The Z-statistic Z=(lambda_max - MP_bulk_edge)/sigma^2 can detect near-duplicate
injections in the weight matrix. When k near-duplicates are injected, Z crosses
a threshold of 3.0 at some detectable k. Also, the detection threshold (first_k_Z3)
decreases monotonically as correlation (rho_dup) increases.

## Pre-registered thresholds

- **HARD-PASS:** fraction of seeds crossing Z>3 >= 0.8 AND Spearman rho between
  (rho_dup, first_k_Z3) > 0.5 (more correlated => detected at lower k)
- **HARD-FAIL:** crossing_seed_frac < 0.5 OR Spearman < 0.0
- **MIDDLE-BAND:** everything else

Note: BBP formula K_CRIT=3*N^(1/3)=48 is theoretical; empirical crossing at k~5
due to low M/N=0.12 regime. HP threshold is "crossing at all" not "crossing at k~48".

## Smoke result (2026-06-01)

Smoke HARD_PASS: crossing_seeds=2/2=1.0, spearman=1.000. Wall fast (<30s).

## Cap-map rows

- AI introspection: spectral audit of weight matrix for duplicate detection
- Governance: Z-stat certificate for capacity monitoring
