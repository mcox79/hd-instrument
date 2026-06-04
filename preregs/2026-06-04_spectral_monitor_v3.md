# Prereg: substrate_spectral_monitor_overfitting_v3_n4096 (v2 rescue continuation)

## Context
v381 cap_map. v2 MIDDLE_BAND: seeds_hp=2/3 (leads=[365,2140,None]; mean_lead=1252.5).
Seed 3 val_overfit_step=None (TRAIN_CHARS=150000 still insufficient). sub_overfit_detected=3/3.
Rescue v3: TRAIN_CHARS=400000 (2.67x), N_STEPS=9000 (1.8x). Seed 3 is the scale-gate blocker.

## Pre-registered bands (inherited from v1/v2; relaxed scale)
HARD-PASS: kappa_4_excess exceeds threshold >= HP_LEAD=50 steps before val_loss overfitting
  onset, across 3/3 seeds.
MIDDLE-BAND: lead 20-49 steps OR 2/3 seeds (v3 would be same as v2 if seed 3 still fails).
HARD-FAIL: lead < 20 steps OR substrate lags val_loss overfitting onset >= 2/3 seeds
  OR val_overfit_step=None 0/3 seeds.

## Hypothesis
TRAIN_CHARS=400000 / N_STEPS=9000 provides sufficient training length for seed 3 to reach
val overfit phase. Sub spectral signal is already consistent at step 200 (v1+v2 confirmed).

## Timeout estimate
v2 wall unknown (no elapsed_s from metrics). Conservative: 3x v2 estimated wall.
Using 5400s ceiling. CPU queue (remote_cpu_queue).

## N-suffix binding (PROT-018)
Anchor _n4096; N_OBS_FULL=4096 asserted at production run.
