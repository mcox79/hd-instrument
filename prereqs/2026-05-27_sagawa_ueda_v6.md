# Pre-registration: sagawa_ueda_v6

**Filed:** 2026-05-27  
**Script:** experiments/exp_sagawa_ueda_v6.py  
**Queue:** remote_cpu_queue  
**Timeout:** 3600s

## Scientific question

Does the vectorized Sagawa-Ueda bound (su_frac = fraction of patterns satisfying the
bound) hold at FULL N=8192, 5 seeds after the v5 timeout is resolved by vectorization?

v5 timed out at 1800s (default) after 4 seeds; vectorized O(N^2 + M*N) per-target
reduces cost from O(M*N^2) scalar loop.

## Parent verdict

- sagawa_ueda_deletion_cert_v3: FAILED (TIMEOUT at N=4096)
- sagawa_ueda_v5: FAILED (TIMEOUT at N=8192, 4/5 seeds completed, all su_frac=1.0)
- sagawa_ueda_deletion_cert_v1, v2: MIDDLE_BAND positive smoke (su_frac=1.0 at small N)

## Pre-registered thresholds (from v6 script docstring)

HARD_PASS (HP1): su_frac >= 0.80 in >= 3/5 seeds at N=8192  
HARD_PASS (HP2): mean_su_frac >= 0.90 across all seeds  
HARD_FAIL (HF): su_frac <= 0.50 in >= 3/5 seeds (bound fails for majority of patterns)  
MIDDLE_BAND: su_frac in (0.50, 0.80) or inconsistent across seeds

## Formula self-tests (from script)

1. Vectorized vs scalar inner-product agrees to 1e-6 at smoke scale
2. su_frac = 1.0 for M=1 (single pattern: no cross-terms, bound trivially satisfied)
3. su_frac >= 0.0 for all cells (bound is physical)
4. Multi-scale: N_smoke and N_smoke*4 both produce non-sentinel su_frac

## Justification

Primary rescue for the deletion-certificate killer-feature. Sagawa-Ueda is the
second non-eq FULL anchor needed (after Crooks FT v153). At v241 tcft_n8192_v5
timeout, sagawa_ueda_v5 was simultaneously failing for same root cause (timeout
not set). v6 fixes both with vectorization + explicit --timeout 3600.

## Production config

N=8192, ALPHA_RATIO=0.125 (M=1024), SEEDS=[7,17,23,31,41], timeout=3600s
