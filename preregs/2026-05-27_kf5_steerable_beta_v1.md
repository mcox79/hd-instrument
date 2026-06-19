# Pre-registration: kf5_steerable_beta_v1

**Filed:** 2026-05-27  
**Anchor:** kf5_steerable_beta_v1  
**Queue:** overnight_queue (GPU)

## Scientific Question
Does inference-time beta adjustment steer the byte-LM substrate behavior (output entropy, BPC, calibration quality)?

## Hypothesis
Beta_inf controls output entropy (monotone decreasing) and BPC (parabolic with minimum near beta_train=8).

## Bands
- HARD_PASS: output_entropy monotone decreasing in >= 4/5 seeds AND entropy_range > 1.0 bit
- HARD_FAIL: all entropy ranges < 0.1 bit (substrate invariant to beta)
- MIDDLE_BAND: monotone in < 4/5 seeds OR range in [0.1, 1.0]

## Timeout Estimate
smoke_wall_s=0.5, N_smoke=1024, N_full=4096, scale=(4096/1024)^1.5*(T_full/T_smoke)=8*6.7=53.6, seeds=5/1=5
Conservative: 3600s
