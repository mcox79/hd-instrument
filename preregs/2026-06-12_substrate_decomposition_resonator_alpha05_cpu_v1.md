# Pre-registration: PP-407 alpha=0.5 verification (identity-augmented resonator decomposition)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_decomposition_resonator_alpha05_cpu_v1.py
**Routing:** strategy_request PP-407 alpha=0.5 verification (Cycle 250, PP-410 follow-on). Substrate-quality-first; NO LLM frame.
**Lane:** local_cpu_queue.

## Purpose
Verify the alpha=0.5 identity-augmentation fix (which recovered PP-406 composition cleanup 0.889 -> 1.0) GENERALIZES to the
PP-407 resonator DECOMPOSITION (precision@1 at K=241/F=3/noise=0 = 0.911 plain). Run the resonator decode with atoms encoded as
algebra_hrr + 0.5*name_token_HRR vs plain algebra_hrr, across the PP-407 grid; report lift.

## Pre-registered bands (strict-HP target = precision@1 at K=241/F=3/noise=0)
- **HARD-PASS:** augmented precision@1 >= 0.95.
- **MIDDLE:** [0.90, 0.95) (lift but not strict bar; alpha sweep may help).
- **HARD-FAIL:** < 0.90 (fix does not generalize to resonator-iteration cleanup).
- **UNKNOWN:** corpus load fails.

## Substrate-product artifact (stands alone, no LLM frame)
Whether the two-vector architecture (structural algebra_hrr for similarity; identity-augmented for compose/decode/cleanup)
generalizes from composition to resonator decomposition -- 2nd-appearance evidence for the encoding-discriminability rule.
