# Pre-registration: wave14_1rsb_pq_retained_v2

Date: 2026-05-26
Experiment file: experiments/exp_wave14_1rsb_pq_retained_v2.py
Queue: overnight_queue

## Context
v1 result: binder=-0.164, n_peaks=4, INCONCLUSIVE at N=2048 (10 seeds).
UV-problem suspected: q_EA~1e-6 tighter than random at N=2048.
v2 probes at N=4096 (20 seeds, tighter KDE_BW=0.02) to attempt resolution.

## Design
- N_FULL=4096, SEEDS_FULL=20, KDE_BW=0.02
- Loads W after M1 hierreplay 4-stage training
- Computes pairwise W-vector overlaps P(q) using Parisi order parameter infrastructure
- Binder cumulant, KDE peak counting, q_EA floor estimate

## Pre-registered bands
HARD-PASS: binder > 0.30 AND n_peaks >= 2 AND mean_q_sig > 5
  (strong 1-RSB signal: bimodal P(q), negative binder, significant q mean)
HARD-FAIL: binder <= 0.05 AND n_peaks <= 1 AND mean_q_sig < 3
  (RS unimodal: flat P(q), positive binder, no q signal)
MIDDLE: anything between (ambiguous; possible UV-problem persisting at N=4096)

## Falsifiable predictions
- If 1-RSB: binder should become MORE negative at larger N (thermodynamic limit sharpens)
- If RS: binder should converge toward 0 or positive at larger N
- MIDDLE matching v1 MIDDLE strengthens RS-unimodal framing (UV-problem is a red herring)

## Calibration note
v1 binder=-0.164 at N=2048 is INCONCLUSIVE. HARD-PASS requires binder > 0.30 -- a clear
jump from v1 is needed, not just marginal improvement. If v2 binder in [-0.30, 0.05], 
classify as MIDDLE and do not upgrade to positive 1-RSB signal.

## Self-test inputs/outputs
- binder_cumulant([1,1,1,1]) -> ~1.0 (all overlaps identical = ferromagnetic = max binder)
- n_peaks detection at unimodal input -> n_peaks=1
- N_FULL=4096 (envelope expansion of v1 N=2048)
