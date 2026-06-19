# Pre-registration: tcft_erase_time_v1_n2048

**Date:** 2026-05-28
**Anchor:** tcft_erase_time_v1_n2048
**Queue:** remote_cpu_queue
**Script:** experiments/exp_tcft_erase_time_v1_n2048.py
**Parent:** tcft_m_sweep_v3_n8192_5seed (HARD_PASS; Spearman=-1.000)

## Hypothesis

TCFT quality (variance_ratio) improves with both M (more context) and erase_time
(more selective erasure) at N=2048. erase_time is an additional TCFT parameter axis.

## Protocol

3 seeds x 5 M values x 5 erase_time values x N=2048. Spearman rank correlation.

## Pre-registered bands

HARD_PASS: Spearman_r(variance_ratio, M) <= -0.90 at >= 3/5 erase_time values
  AND variance_ratio(erase_time=16) < variance_ratio(erase_time=1) at M=512 at >= 3/5 seeds.

HARD_FAIL: Spearman_r > -0.50 at all erase_times (no M-dependence).

MIDDLE_BAND: M-dependence confirmed but erase_time has no additional effect.

## Formula self-tests

1. N=2048 (PROT-018 binding).
2. Spearman_r is rank correlation. Perfect anti-monotone: Spearman_r = -1.0.
3. variance_ratio = mean(variance_at_M) / variance_at_baseline.
4. 1/sqrt(M) scaling: var_ratio(256) = var_ratio(128) / sqrt(2).

## Timeout estimate

75 cells x 40s/cell = 3000s. Safety ceil(1.5 * 3000) = 4500s.
Exceeds 2h flagged for visibility. timeout_s = 7200.
