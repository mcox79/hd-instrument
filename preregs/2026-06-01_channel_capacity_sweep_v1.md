# Prereg: channel_capacity_sweep_v1

Date: 2026-06-01
Anchor: channel_capacity_sweep_v1
Queue: remote_cpu_queue
Script: experiments/exp_channel_capacity_sweep_v1.py
Source: research_capabilities_expansion_round3_8_drills_2026-06-01.md Drill 8 M4

## Scientific question

Does substrate achieve >= 25% of Hopfield critical capacity (alpha_c * N = 141
at N=1024) when measured at low-load M values (M <= 0.10 * N = 102)?

Metric: C_eff = M * acc(M,N). Fraction = C_eff / M_crit.
alpha_c = 0.138 (Hopfield 1982 classical result; bipolar random patterns).

## Design

N=1024. SMOKE: M sweep {32, 64, 128}, seeds=[17].
FULL: M sweep {32, 64, 128, 192, 256}, seeds=[7,17,23,31,41].
Pure CPU. Expected FULL wall: ~10 min.

## Pre-registered bands

HARD-PASS: at M <= 0.10 * N (102 patterns):
           mean retrieval acc >= 0.95 AND
           mean C_eff/M_crit >= 0.25 (for low-load M values only).

HARD-FAIL: acc < 0.50 at M=64 OR mean C_eff/M_crit < 0.10 at low-load M.

MIDDLE: between HP and HF.

Calibration probe (no prior empirical anchor for cap fraction):
bands widened per policy. Theoretical: at M=32 frac=0.23, M=64 frac=0.45,
mean=0.34. HP=0.25 = theoretical * 0.74 (within +-50% of theory).
HF=0.10 is 1/3 of theoretical (clear failure).

## Timeout estimate

FULL: smoke_wall_s=5s, FULL_N/smoke_N=1 (same N), FULL_seeds/smoke_seeds=5,
scaling_exp=1.0 (linear sweep).
timeout_s = ceil(1.5 * 5 * 1 * 5) = 38s.
PROT-019 floor 3600s. timeout_s = 3600.

## PROT-018

No _nN suffix. Production N=1024 stated here per PROT-018 rule 3.
M is the primary axis.

## Middle-band outcome plan

If MIDDLE: cap_map row annotated "achieves X% theoretical capacity at low load
(M <= 0.10*N)". Route to Strategy for next step (higher N sweep or alternate
capacity definition). Explore load curve shape.
