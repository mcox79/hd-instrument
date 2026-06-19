# Pre-registration: wave14_corpus_N_scaling_tau_unblock_v1

**Date:** 2026-05-27
**Script:** experiments/exp_wave14_corpus_N_scaling_tau_unblock_v1.py
**Queue:** overnight_queue (GPU; N=16384 requires GPU; ~1-2h)
**Trigger:** exp_wave14_corpus_size_scaling_v1 returns CORPUS_SCALING_HARD_FAIL

## Hypothesis

Tau-limit is N-corpus COUPLED. At N=1024 capacity is 575 atoms (binding).
At N=16384 capacity is ~9200 atoms (may be safe for 500KB corpus).

## Design

N sweep: {1024, 4096, 16384}, corpus fixed at 500KB, 2 seeds.

## Pre-registered bands

- **HARD-PASS:** bpc monotone decreasing across N-sweep AND top_edge@N=16384 >= 2.0
- **HARD-FAIL:** bpc non-monotone OR top_edge < 1.5 at N=16384
- **MIDDLE:** monotone bpc but top_edge in [1.5, 2.0]
- No empirical anchor for this N-corpus regime; bands set per calibration-probe policy (+-50%).
