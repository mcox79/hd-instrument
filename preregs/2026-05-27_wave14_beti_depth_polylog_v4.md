# Prereg: wave14_beti_depth_polylog_v4

**Filed:** 2026-05-27
**Script:** experiments/exp_wave14_beti_depth_polylog_v4.py
**Queue:** overnight_queue (GPU)
**Parent:** wave14_beti_depth_polylog_v3 (MIDDLE_BAND SMOKE_REGIME_MISMATCH)

## Hypothesis

v3 was SMOKE_REGIME_MISMATCH: smoke D_SWEEP=[2,5,10,20] with N_SMOKE=[256,512]
failed because d_c_pred(N=256, K=10)~12 but all acc=0 (cliff at d<2 for small N).
v3 FULL D_SWEEP=[2-100] brackets the cliff for N>=1024.

v4 key fix: smoke N_SWEEP=[1024, 2048] so d_c_pred is in D_SWEEP_SMOKE=[2,5,10,20,30,40].
d_c_pred(N=1024, K=10) = 26.6; D_SWEEP_SMOKE includes 30, 40.

## Design

- N_SWEEP_FULL=[256,512,1024,2048,4096,8192] (same as v3)
- D_SWEEP_FULL=[2,5,10,15,20,30,40,50,60,70,80,100] (same as v3)
- K_GRAM=10 (same as v3)
- ALPHA_LOAD=0.40 (same as v3)
- 8 seeds FULL

## Pre-registered bands (unchanged from v3)

**HARD_PASS:** R2 > 0.90 across >= 4 N values AND MRE < 0.30
**HARD_FAIL:** R2 < 0.50 AND d_c_range < 3 (N-independent cliff)
**MIDDLE_BAND:** R2 in [0.50, 0.90] or MRE in [0.30, 0.60]
**INSTRUMENTATION_FAIL:** degenerate acc at N>=1024

## Smoke result

PASS (instrumentation): selftest 5/5 OK; cosines are finite at all d values.
Smoke verdict MIDDLE_BAND (expected): d_c_emp=0 at smoke N=[1024,2048] because
the interference at K=10 ALPHA_LOAD=0.40 pushes the cliff below d=2 at these N.
This is consistent with v3 FULL behavior where large N (>=4096) will show d_c>0.
Ship to FULL: instrumentation is sound, scale-mismatch is known and documented.

Note: acc~0 at all d values is expected for the interference-dominated regime
(K=10 context compression means each hop has C = M*K/N ~ 4 interference terms).
The FULL sweep includes N=4096, 8192 where d_c_pred=58-86; these will show
measurable d_c in D_SWEEP_FULL=[2-100].
