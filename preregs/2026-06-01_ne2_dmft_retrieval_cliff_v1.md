# Prereg: ne2_dmft_retrieval_cliff_v1

**Date**: 2026-06-01
**Anchor**: ne2_dmft_retrieval_cliff_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_ne2_dmft_retrieval_cliff_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (NE-2)

## Hypothesis

DMFT retrieval cliff (Hara-Kabashima 2026): substrate's retrieval overlap m*
drops sharply near alpha_c ~ 0.138, confirming substrate is in the DMFT
universality class. Finite-N corrections ~1.5% at N=1024 per Hara-Kabashima.

## Design

- N = 1024, alpha in {0.08, 0.12, 0.138, 0.16, 0.20}
- 3 retrieval trials per (alpha, seed), 20 synchronous update steps, 5% noise
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: m* >= 0.90 at alpha < 0.12 AND m* <= 0.50 at alpha > 0.15 AND
cliff midpoint (50% overlap crossing) in [0.10, 0.16]; in >= 4/5 seeds.

**HARD-FAIL**: m* < 0.70 at alpha < 0.12 (no retrieval at low load) OR no cliff
(m* range < 0.20 across alpha grid) in >= 4/5 seeds.

**MIDDLE-BAND**: cliff present but outside [0.10, 0.18], or passes in 3/5 seeds.

## No prior direct DMFT test on substrate

Bands widened per calibration-probe policy. Theory predicts cliff at
alpha_c = 0.138 (+-15% window for HARD-PASS; +-30% for MIDDLE-BAND).

## Smoke result

Smoke (3 seeds): cliff observed but shifted toward alpha = 0.16-0.20 at
N=1024 (finite-N effect). MIDDLE_BAND. m* > 0.90 at low alpha confirmed.
Full 5-seed run needed; cliff detection may succeed with more seeds.

## Timeout estimate

smoke_wall_s = 0.3s; scaling linear; 5/3 seed ratio.
timeout_s = ceil(1.5 * 0.3 * 5/3) = 1s -> 300s (PROT-019 floor for CPU).

## N-suffix

No _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
