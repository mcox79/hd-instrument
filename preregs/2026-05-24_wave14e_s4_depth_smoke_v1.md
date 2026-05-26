# Pre-reg: SSM/S4 depth re-queue (corrected task wrapper)

**Date**: 2026-05-24
**Script**: `experiments/exp_wave14e_s4_depth_smoke_v1.py`
**Queue**: remote_cpu_queue (CPU-bound HiPPO recurrence with N<=4096)
**Designed by**: exp_dev re-ship per `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md` Anchor 4
**Re-ship rationale**: prior run failed at task-design level not substrate-level; this re-queues against script's existing falsifier bands.

## Hypothesis

SSM extends the chained-cleanup depth past the d~50 cliff observed on the binding-only substrate. Mechanism: complex-diagonal state-space h_{t+1} = A h_t + B x_t with HiPPO-like decay; readout against codebook.

## Parameters (from script)

- N_FULL = 4096
- D_MAX_FULL = 200
- H_FULL = 128 (SSM hidden states)
- Seeds: [7, 17, 23, 31, 41]
- N_PROBES_FULL = 50

## Falsifier bands (from script)

- **HARD-PASS**: SSM depth-at-half >= 1.5x binding-only depth-at-half (PASS_RATIO=1.5)
- **HARD-FAIL**: SSM depth-at-half <= 1.0x binding-only depth-at-half (HARD_FAIL_RATIO=1.0)
- **PARTIAL/MIDDLE**: ratio in (1.0, 1.5)

## Per user analysis

Substrate W as state transition matrix, key as input, value as readout, standard copy-task or selective-copying benchmark. The script's depth-at-half metric operationalizes this against the chained-cleanup substrate.

## Discipline citations

- Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL falsifiable BEFORE running (taken from script's `compute_verdict`).
- Per [[feedback-rehabilitation-after-rejection]]: this is the corrected-task re-queue of the prior smoke-failed S4 attempt.

## Estimated wallclock

CPU at N=4096 d_max=200 H=128 5 seeds: ~30-90 min.
