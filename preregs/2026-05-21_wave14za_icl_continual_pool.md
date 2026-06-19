# Pre-registration: wave14za_icl_continual_pool

Date: 2026-05-21
Status: Pre-registered, gated
Priority: cap_map Tier-2 KILLER 'Real-time learning during inference'
Author: experiment_dev session, pipeline tick 34

## Why
Substrate has pool retrieval (validated). za tests if growing the pool
at inference time (each test query adds its (ctx, target) to the pool)
improves bpc over time. Real-time learning without weight updates.

## Verdict labels
- ICL_CONTINUAL_POOL_IMPROVES: continual bpc < static bpc - 0.1
- ICL_CONTINUAL_POOL_HARMS: continual bpc > static bpc + 0.05
- ICL_CONTINUAL_POOL_FLAT: no meaningful change
- ICL_CONTINUAL_POOL_INCONCLUSIVE

## Runtime: ~5 min
