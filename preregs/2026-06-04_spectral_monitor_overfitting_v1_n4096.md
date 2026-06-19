# Pre-reg: substrate_spectral_monitor_overfitting_v1_n4096 (cycle 44 rescue R1)

**Date:** 2026-06-04
**Anchor:** substrate_spectral_monitor_overfitting_v1_n4096
**Queue:** remote_cpu_queue (CPU)
**N_OBS:** 4096 (PROT-018 binding)
**Seeds:** 3 (seeds 7, 17, 23)
**Cap_map:** Phase A spectral monitor rescue (v375 rung-1 HARD_FAIL rescue R1)

## Scientific question
Does substrate kappa_4_excess predict LLM overfitting onset >= 50 training steps before
val_loss reveals it, consistently across seeds?

## Rescue context
rung1 tinychar spectral monitor HARD_FAIL: convergence phase lags (mean_lead=-11.67 3/3 seeds).
Overfitting phase STRONG SIGNAL: mean_lead=+300 steps (3/3 seeds).
R1 rescue: re-pre-reg with overfitting-phase-only criterion.

## Pre-registered bands (overfitting-phase-only)
- HARD-PASS: kappa_4_excess leads val_loss overfitting onset by >= 50 training steps, 3/3 seeds
- MIDDLE: lead 20-49 steps OR 2/3 seeds
- HARD-FAIL: lead < 20 steps OR substrate lags val_loss on >= 2/3 seeds

## Design changes vs rung1
- Pre-reg criterion: ONLY overfitting phase (convergence + divergence excluded)
- TRAIN_CHARS: 30000 (increased from 20000 to induce reliable overfitting)
- N_STEPS: 2000 (increased from 1000 to ensure overfitting onset observable)
- HP_LEAD: 50 steps (relaxed from rung1 HP=100, appropriate for tinychar scale)
- Corpus repeated 3x to induce overfitting

## PROT compliance
- PROT-018: anchor has _n4096; N_OBS=4096 in FULL mode
- PROT-019: wall floor 21600s; expected elapsed ~60-90s at 3 seeds
- PROT-021: seed checkpoints keyed with run_mode + N_OBS
- PROT-022: kappa_4_excess non-NaN after 5 observe() calls; overfitting detection self-tests
