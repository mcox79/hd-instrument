# Pre-registration: wave14_betB_replay_hA_direct_v1

Date: 2026-05-26
Experiment file: experiments/exp_wave14_betB_replay_hA_direct_v1.py
Queue: overnight_queue

## Context
v209 REPLAY mechanism narrowing:
  - H-C (effective-N-doubling) REFUTED: replay > 2x-data by +16.5pp
  - H-B (interference-reduction) INCONCLUSIVE: direct_lift=0.123 < 0.15 threshold
  - H-A (consolidation) FAVORED: residual hypothesis

H-A prediction: replay timing matters. Inter-phase (between stages) > intra-phase (within stages)
by >= 0.05 retention. This distinguishes sleep-like offline consolidation from data augmentation.

## Design
- 3 arms x 5 seeds x N=4096
- Arm 1 (H-A INTER-PHASE): replay injected at START of each new phase (between phases A->B, B->C, C->D)
- Arm 2 (INTRA-PHASE control): standard M1 hierreplay (interleaved within phases)
- Arm 3 (NO-REPLAY): zero replay floor
- Metric: retention = bpc_fresh / bpc_after_ABCD for corpus A

## Pre-registered bands
HARD-PASS (H-A consolidation confirmed):
  ret(Arm1) - ret(Arm2) >= 0.05 AND ret(Arm1) >= 0.80 AND ret(Arm2) > ret(Arm3)
HARD-FAIL (H-A rejected, timing irrelevant):
  |ret(Arm1) - ret(Arm2)| < 0.02 OR ret(Arm1) < ret(Arm3)
MIDDLE: lift in [0.02, 0.05) or weak/inconsistent consolidation signal

## Falsifiable predictions
- If H-A: inter-phase consistently EXCEEDS intra-phase across seeds
- If H-A fails / data-augmentation: Arm1 ~= Arm2 (timing doesn't matter)
- Arm2 > Arm3 should hold regardless (basic replay benefit)
- Walk-back: if smoke |Arm1 - Arm2| < 0.03, run FULL at N*2 or 10 seeds

## Smoke result
N=512 smoke: inter=0.947 intra=0.962 noreplay=0.920 lift=-0.015 -> HA_MIDDLE
(single epoch, 1 seed, N=512 -- smoke verdict expected to be unreliable)

## Self-test inputs/outputs
- retention formula: bpc_fresh=2.0, bpc_after=2.5 -> ret=0.8
- HP_INTERPHASE_LIFT=0.05 > HF_TIMING_IRRELEVANT=0.02 (correct ordering)
- N_FULL=4096, 5 seeds
