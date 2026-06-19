# Prereg: wave14_moe_top_edge_v4

**Date:** 2026-05-26
**Parent:** wave14_moe_top_edge_v3 (in-flight; N=16384 discrimination test)
**Trigger:** ship when v3 returns FREE_ADDITIVE_HARD_PASS (offset_ratio ~1.0 at N=16384)
**Question:** Does the free-additive formula converge as a function of N, and what is the convergence rate?

## Hypothesis
If v3 confirms the finite-N hypothesis (v1/v2 offset was 1/sqrt(N) artifact), then the
full N-scaling curve should show offset_ratio converging to 1.0 with rate A/sqrt(N).
This v4 fits that convergence curve across N in {4096, 8192, 16384, 32768}.

## Design
- N sweep: {4096, 8192, 16384, 32768}
- K in {2, 4} (decisive cells from v3)
- M_per_expert = 1600 * N/4096 (proportional)
- 5 seeds per (N, K) cell
- GPU overnight_queue (~6-8 hrs)
- sigma_top computed via power iteration at N=32768 (full SVD too slow)

## Pre-registered bands
- **HARD_PASS**: offset_ratio at N=32768 >= 0.85 AND convergence fit R^2 >= 0.70
- **HARD_FAIL**: offset_ratio at N=32768 < 0.75 (persistent offset not explained by finite-N)
- **MIDDLE_BAND**: offset improves monotonically but < 0.85 at N=32768
- **INSTRUMENTATION_FAIL**: OOM at N=32768 OR non-finite ratio

## Calibration
Prior anchor: v1 (N=4096) offset ~0.50; v3 (N=16384) to be measured. If v3 ~0.75-0.80,
convergence to 1.0 at N=32768 requires ~0.90+. Bands set accordingly.

## Middle-band outcome plan
If MIDDLE_BAND: route to N>=65536 probe OR DMPK fallback (exp_wave14_moe_top_edge_dmpk_v1).
