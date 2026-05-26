# Prereg: wave14_streaming_NESS_eta_sweep_v1

**Date**: 2026-05-23 (emergency refill batch #3)
**Queue**: overnight_queue (GPU)
**Hypothesis class**: Cap 3 NESS robustness under streaming noise

## Scientific claim under test
GLAUBER_BIMODAL_KERDOCK (v164b) established bimodal stationary P(q) for the Kerdock-Hebbian Hopfield network. This experiment asks: does the bimodality survive when streaming bit-flip noise at rate eta is injected at every Glauber sweep (modeling read-channel corruption)?

## Design
- N=4096, alpha=0.10 (sub-critical AGS regime)
- beta in {0.5, 1.0, 2.0, 4.0} (paramagnet through retrieval phase)
- eta in {0.001, 0.01, 0.1, 1.0} (5 orders of magnitude of noise)
- 10 seeds per (beta, eta) cell
- n_burn=400, n_collect=600 sweeps per chain
- Per-sweep: Glauber update + per-spin iid bit-flip with prob eta

## Hard-fail thresholds
- Self-test 4/4 verdict-branch sanity
- Baseline eta=0.001 + beta=4 cell must reach bimodal_score >= 0.5 (substrate retrieval still works at near-zero noise)
- metrics.json validate + atomic write

## Verdict labels
- NESS_BIMODAL_ROBUST: overall bimodal fraction > 0.5 AND largest-eta cell fraction > 0.3
- NESS_BIMODAL_FRAGILE: overall bimodal fraction <= 0.3
- NESS_BIMODAL_MIXED: 0.3 < fraction <= 0.5
- NESS_INCONCLUSIVE

## Expected runtime
N=4096 Hebbian W matvec dominated. 4 beta * 4 eta * 10 seeds * 1000 sweeps = 160,000 sweeps. With ~50ms/sweep on remote CPU/GPU matmul: ~30-45 min wallclock.

## Implications
- ROBUST => Cap 3 NESS envelope wide; substrate-product story for online-read inference holds
- FRAGILE => Cap 3 envelope is narrow; substrate needs error-correction layer for streaming
