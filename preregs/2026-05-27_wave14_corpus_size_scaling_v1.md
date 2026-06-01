# Pre-registration: wave14_corpus_size_scaling_v1

**Date:** 2026-05-27
**Script:** experiments/exp_wave14_corpus_size_scaling_v1.py
**Queue:** remote_cpu_queue
**ETA:** ~20-30 min CPU (N=1024, 2 seeds, 3 corpus sizes)

## Hypothesis

Substrate's Hebbian W accumulates interference when M_stored > alpha_c * N (tau-limit). At small N=1024, this threshold may already be crossed at large corpus sizes. This probe tests whether bpc decreases monotonically with corpus size and whether the spectral top-edge ratio shows whitening onset.

Source: notes/exp_dev_handoff_corpus_size_scaling_probe_2026-05-27.md
Parent research: notes/research_corpus_size_scaling_2026-05-27.md

## Design

- N = 1024 (CPU-feasible)
- Corpus sizes: 10KB, 100KB, 500KB training bytes
- 2 seeds
- Metrics: bpc, W spectral top-edge ratio, W effective rank

## Pre-registered bands (from handoff)

- **HARD-PASS:** bpc strictly decreasing across all 3 cells AND W top-edge ratio >= 2.0 at largest cell. Tau-limit not binding; corpus-size scaling safe to extrapolate.
- **HARD-FAIL:** bpc non-monotone OR top-edge ratio < 1.5 at largest cell. Tau-limit binding; N-scaling required first.
- **MIDDLE:** monotone bpc but top-edge in [1.5, 2.0]. Further probe needed at larger N.
