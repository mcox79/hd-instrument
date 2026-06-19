# Prereg: wave15_ewc_betB_smoke_v1

**Date**: 2026-05-24
**Author**: orchestrator main thread (under FULL AUTONOMY)
**Queue**: remote_cpu_queue
**ETA**: 60-90 min CPU at N=4096
**Script**: `experiments/exp_wave15_ewc_betB_smoke_v1.py`

## Source

Independent EWC rehab implementation for Bet B retention, complementary
to wave14e_betB_ewc_smoke_v1. This variant uses:
- Different lambda grid: {0.0, 1e-2, 1e-1, 1.0, 10.0} (wider range)
- Different Fisher-estimation formulation (per-batch SGD-style accumulation)
- 2-phase only (Phase A + Phase B; no Phase C); cleaner retention measurement

Tier-2 candidate B1 from `notes/research_15_angles_triage_2026-05-24.md`.

## Mechanism

Same canonical EWC formulation: Fisher diagonal
F_ij = E[(d log p / d W_ij)^2] over Phase-A retrieval samples; quadratic
penalty lambda * F * (W - W_A) applied during Phase-B updates.

## Hypothesis (one-line)

At best lambda in {1e-2, 1e-1, 1.0, 10.0}, retention_A is >=5pp higher than
lambda=0 baseline, with at most 3pp degradation on Phase-B fit (gain_B).

## Design

| Config | N | seeds | epochs_a | epochs_b | bytes/corpus | batch | lambdas |
|---|---|---|---|---|---|---|---|
| Full | 4096 | {7,17,23,31,41} | 3 | 3 | 100,000 | 64 | {0, 0.01, 0.1, 1.0, 10.0} |

## Verdicts

### HARD PASS - `EWC_PASS`

Best non-zero lambda yields retention_A lift >= 0.05 over lambda=0 with
gain_B degradation <= 0.03.

### HARD FAIL - `EWC_KILLED`

Best non-zero lambda has retention_A LESS than lambda=0 baseline (EWC
hurts retention).

### PARTIAL - `EWC_PARTIAL`

retention_A lift in [0.02, 0.05) (consistent direction but sub-threshold).

### INCONCLUSIVE - `EWC_INCONCLUSIVE`

retention_A lift < 0.02 (no detectable effect at tested lambda grid).

## Self-tests (passed locally 2026-05-24)

`--self-test`: 5/5 verdict synthetic cells pass.

## Smoke gate (passed locally 2026-05-24)

`--smoke` (N=1024, 1 seed, 2 epochs A + 1 epoch B, 3000 bytes,
lambdas {0.0, 1.0}):
- lam=0.0: retention_A=0.987 gain_B=0.443
- lam=1.0: retention_A=1.000 gain_B=0.724
- VERDICT: EWC_INCONCLUSIVE (lift +0.013 below 0.02 threshold)

Smoke INCONCLUSIVE is expected at smoke scale where Phase-A is already
saturated at retention=0.987; full N=4096 with deeper Phase-A training
exposes the catastrophic-forgetting regime where EWC has room to lift.

## Memory / wallclock budget

- W per cell: 4096 x 4096 float32 ~ 64 MB; Fisher ~ 64 MB
- 5 lambdas x 5 seeds = 25 train passes
- Estimated wallclock: 60-90 min remote CPU
- Timeout: 5400s

## Filing on outcome

- HARD PASS: cap_map Bet B row -> FULL (was PARTIAL); v182 bump.
- HARD FAIL: file 5 rescue sketches; cap_map row PARTIAL with PROVISIONAL.
- PARTIAL: cap_map row PARTIAL with annotation; trigger 2x Research drill.
- INCONCLUSIVE: no row movement.

## Notes / caveats

- This is the PARALLEL EWC anchor to wave14e_betB_ewc_smoke_v1 (different
  scaffolding, different lambda grid). Both shipping increases the
  probability that one of them gives clean signal; if both PASS, EWC is
  validated through 2 independent implementations.
- Per [[feedback-no-smoke]]: pure rescue probe for Bet B, NOT a new
  capability. If passes, Bet B flips from 73% to >80%.
