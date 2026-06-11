# Pre-registration: wave1_multiseed_sweep_cpu_v1

**Date:** 2026-06-11
**Anchor:** wave1_multiseed_sweep_cpu_v1
**Queue:** local_cpu_queue
**N:** 8192 (per underlying anchor cell), **Seeds:** 5 (HDLAB_SEED 1..5), **Anchors:** 15

## Scientific question
Are the 15 cycle-224..227 substrate ceiling-win anchors (comm1/2/6/lex, math1/2/3/4/rung3, code1/2/6, lex-wug,
key-rotation, slipnet-noise) SEED-ROBUST, or were their n=1 HARD_PASS verdicts flukes? Re-runs each at n=5 seeds
under its own pre-registered gate and aggregates the verdict distribution to promote D->C (closes LVH-277).
Per Research PROMOTION_CAMPAIGN_WAVES Wave-1 Tier-0.

## Pre-registered bands

**HARD-PASS:**
- >=12 of 15 anchors PROMOTE_C (HARD_PASS in >=4/5 seeds)
- n=1 ceiling wins confirmed seed-robust (not flukes)

**MIDDLE:** 8-11 of 15 anchors promote D->C; remainder seed-fragile.

**HARD-FAIL:** <8 anchors seed-robust OR many n=1 wins were flukes.

## Per-anchor promotion rule
- >=4/5 seeds HARD_PASS -> PROMOTE_C
- 2-3/5 -> SEED_FRAGILE (route to Research; n=1 was a partial fluke)
- <2/5 -> FAIL

## Calibration rationale
12/15 (80%) seed-robustness is the bar for a credible campaign-wide D->C promotion: the cycle-224..227 wins were
single-seed exploratory, so a >=4/5 HARD_PASS threshold per anchor rejects lucky-seed artifacts while tolerating one
genuinely hard seed. Smoke (n=3) showed 14/15 promote with only code2 failing (the known partial/rescue case in Wave-2
Tier-2), so the full n=5 is expected to land HARD-PASS; a drop below 12 would itself be the informative signal.

## N-suffix section
Meta-runner (no N constant of its own); each underlying anchor cell is N=8192 multi-seed. Timeout set to the
n>=8192 multi-seed floor to cover 15 anchors x 5 seeds of subprocess runs.
