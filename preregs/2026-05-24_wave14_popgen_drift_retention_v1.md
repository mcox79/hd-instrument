# Prereg — Wright-Fisher population-genetics drift retention model

**Anchor**: `wave14_popgen_drift_retention_v1`
**Queue**: remote_cpu_queue (pure CPU; multi-seed t-sweep)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

Field probe per v195 8-new-fields delivery (POPULATION GENETICS). Substrate's
retention curve may be closed-form-predicted by Wright-Fisher drift:
`retention(t) = exp(-t / (2 N_e))` where N_e is the effective population size
derived from substrate dimension + load.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: Wright-Fisher closed-form prediction tracks measured
  retention within +/-10% across >=4 of 5 time points AND fitted N_e is
  within [N/4, N] (substrate-consistent).
  -> R-PRIME-1-adj population-genetics framing PROMOTED 🔬 -> 🟡; closed-form
  retention predictor candidate.
- **HARD-FAIL**: predicted vs measured deviates by > 0.25 at >=3 of 5 time
  points OR fitted N_e falls outside [N/100, 10*N].
  -> Wright-Fisher drift framing REJECTED.
- **MIDDLE-BAND**: any intermediate.

## Parameters (exp_dev autonomy)

- T grid = {1, 5, 21, 55, 144} FULL / {1, 21, 55} smoke
- N = 4096 FULL / 512 smoke
- M per task = 200 FULL / 30 smoke
- Seeds = {7, 17, 23, 31, 41} FULL

## ETA

Remote CPU FULL ~15-30 min.

## Smoke outcome

Smoke at N=512 single-seed: N_e=32.5 (under PASS [N/4, N]=[128, 512] band ->
HARD_FAIL on N_e range alone). max_dev=0.071 is within band. N=4096 may put
N_e in band — FULL is informative.
