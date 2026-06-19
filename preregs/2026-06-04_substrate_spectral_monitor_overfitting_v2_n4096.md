# Prereg: spectral_monitor_overfitting_v2_n4096 -- scale-gate R1

**Date:** 2026-06-04
**Cap_map row:** No established row yet; spectral training monitor probe
**Rescue:** R1 from v376 Cycle 44 spectral_monitor_overfitting v1 HARD_FAIL

## Anchor
substrate_spectral_monitor_overfitting_v2_n4096

## Scientific question
Does substrate spectral fingerprint (kappa_4_excess) predict LLM overfitting onset
>= 50 steps before val_loss, when training is run at sufficient scale (TRAIN_CHARS=150000,
N_STEPS=5000)? v1 HARD_FAILed because val_overfit_step=None 0/3 seeds (LM never reached
overfitting phase at TRAIN_CHARS=30000/N_STEPS=2000). Substrate spectral fired at step 200
consistently (3/3 seeds), confirming mechanism is present.

## Pre-registered bands (inherited from v1; same criterion)
**HARD-PASS:** kappa_4_excess exceeds threshold >= 50 steps before val_loss overfitting onset,
              3/3 seeds.
**MIDDLE:** lead 20-49 steps OR 2/3 seeds.
**HARD-FAIL:** lead < 20 steps OR substrate lags val_loss >= 2/3 seeds
              OR val_overfit_step=None 0/3 seeds (scale still insufficient).

## Timeout estimate
Basis: v1 elapsed ~40s/seed at 3 seeds = 120s total (TRAIN_CHARS=30000/N_STEPS=2000).
v2 scale: TRAIN_CHARS=150000/N_STEPS=5000 = ~5x increase.
Formula: ceil(1.5 * 600 * 1.0) = 900s (conservative: 200s/seed x 3 seeds x 1.5 margin).
Use timeout=1800 (2x safety margin for wikitext2 corpus loading).

## N-suffix
_n4096: production N_OBS = 4096. PROT-018 compliant.

## PROT compliance
- PROT-018: _n4096 suffix; N_OBS=4096 in full mode.
- PROT-021: seed checkpoints keyed with run_mode + N_OBS.
- PROT-022: kappa_4_excess non-NaN self-tested; detect_overfitting_val self-tested.
- QUEUE: remote_cpu_queue (CPU; tinychar GRU; no GPU needed).
