# Prereg: wave14_corpus_size_scaling_v2

**Filed:** 2026-05-27
**Script:** experiments/exp_wave14_corpus_size_scaling_v2.py
**Queue:** overnight_queue (GPU)
**Parent:** wave14_corpus_size_scaling_v1 (HARD_FAIL -- smoke-regime N=256 mismatch)

## Hypothesis

v1 HARD_FAIL at N=256 with corpus sizes [10KB, 100KB, 500KB]. The issue:
at N=256, alpha_c*256=144 items, so 500KB corpus hits saturation quickly,
masking any corpus-size benefit. At N=1024 with larger corpus sizes
[100KB, 1MB, 10MB], the tau-limit onset (if any) should be distinguishable
from genuine corpus-size scaling.

Path-(b) P: currently 0.27 (fell from 0.35 after v1 HARD_FAIL).
If this v2 shows CORPUS_SCALING_HARD_PASS, P returns to 0.35+.

## Design

- N=1024 (FULL)
- Corpus sizes: [100_000, 1_000_000, 10_000_000] bytes (100KB / 1MB / 10MB)
- 5 seeds, 5 epochs
- Metrics: bpc, W_top_edge_ratio, effective_rank

## Pre-registered bands

**CORPUS_SCALING_HARD_PASS:** bpc strictly decreasing AND top_edge >= 2.0 at large corpus
-> Path-(b) viable at N=1024

**CORPUS_SCALING_HARD_FAIL:** bpc plateau or top_edge < 1.5 at any corpus >= 1MB
-> Tau-limit binding; path-(b) needs N >> 1024

**MIDDLE_BAND:** monotone but marginal improvement or top_edge in [1.5, 2.0]

**INSTRUMENTATION_FAIL:** NaN bpc

## Calibration band note

No prior empirical anchor at N=1024 with these corpus sizes.
Bands are based on spectral top-edge theory (tau-limit onset at top_edge~1.5).

## Smoke result

HARD_FAIL at N=256 (expected -- smoke N too small for 100KB+ corpus).
Instrumentation passed: selftest 5/5 + 1 run OK.
Multi-scale smoke: N=256 (baseline pass); N=1024 FULL needed for decisive result.
