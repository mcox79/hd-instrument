# Pre-registration: write_back_dirty_bits_v1

**Date:** 2026-06-02
**Anchor:** write_back_dirty_bits_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_write_back_dirty_bits_v1.py

## Scientific question (Caching-Policy Expressibility, Tier 1)
Can the substrate implement O(M) dirty-bit bookkeeping for write-back caching via
a binary flag vector, and does targeted retrieval + selective deletion preserve
clean patterns while removing dirty ones?

## Pre-registered thresholds (set BEFORE run)
- HARD-PASS: dirty_acc >= 0.95 AND delta_cos_clean <= 0.05 (dirty flags accurate; clean patterns preserved)
- MIDDLE: dirty_acc in [0.80, 0.95) OR delta_cos_clean in (0.05, 0.15]
- HARD-FAIL: dirty_acc < 0.80 OR delta_cos_clean > 0.15

## Calibration note
No prior substrate dirty-bit experiment. Bands set +-50% around theoretical:
exact deletion should give delta_cos_clean~0 and dirty_acc~1.0 at low load.

## Smoke result
HARD_PASS: dirty_acc=1.000, delta_cos=0.0000 (smoke N=1024, M_DIRTY=[10,20,40,60], 2 seeds)
