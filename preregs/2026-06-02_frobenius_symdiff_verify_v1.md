# Pre-registration: frobenius_symdiff_verify_v1

**Date:** 2026-06-02
**Anchor:** frobenius_symdiff_verify_v1
**Script:** experiments/exp_frobenius_symdiff_verify_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 1200s

## Scientific question

Empirically verify: ||W_A - W_B||_F^2 ≈ |A symdiff B| (NOT divided by N).
This is the corrected Frobenius-distance formula for Hopfield matrices.

## Key correction from earlier spec
Original docstring claimed ||W_A-W_B||^2/N ~ |symdiff|/N (wrong by factor N^2).
Correct formula: ||W_A-W_B||^2 ≈ |symdiff| (no N factor).
Verified empirically: frob_sq ≈ 40.0 for 20+20 disjoint patterns at N=4096.

## Bands (pre-registered)

**HARD-PASS (HP):**
- Relative error < 5% for >= 4/5 configs across seeds

**MIDDLE:**
- Max error in [5%, 25%)

**HARD-FAIL (HF):**
- Max relative error > 25% (formula fundamentally wrong)

## Smoke result
HARD_PASS: mean_rel_err=0.001, max_rel_err=0.001 (all 3 configs). Wall time: <5s.
FULL estimate: ~200s (5 seeds, 5 configs including partial overlap cases).

## PROT-018
No _nN suffix. Production N=4096 declared in script.
