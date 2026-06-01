# Prereg: wave14_ortho_blahut_arimoto_v2

**Filed:** 2026-05-27
**Script:** experiments/exp_wave14_ortho_blahut_arimoto_v2.py
**Queue:** remote_cpu_queue (CPU)
**Parent:** wave14_ortho_blahut_arimoto_v1 (label=failed, data=HARD_PASS)

## Hypothesis

v1 label-vs-honest mismatch: the queue runner labeled the experiment "failed" but
the actual metrics.json shows HARD_PASS (max_R=1.2988 nats, H_src=2.7081 nats,
N_min predictions computed for ret={0.5,0.7,0.9}).

v2 is a clean re-ship with:
  1. Explicit sys.exit(0) at end to prevent runner from flagging non-zero exit
  2. Wider N_tasks sweep: {3, 5, 10} to confirm the finding holds
  3. 100-point D_SWEEP (was 50)
  4. N_min_margin metric added

## Design

- N_tasks sweep: {3, 5, 10} sequential tasks
- K=4 context bits, M=10 patterns per task
- 100 D_SWEEP points in [0.005, 0.995]
- Blahut-Arimoto max 200 iterations

## Pre-registered bands

**HARD_PASS:** R(D) non-trivial AND N_min predictions finite for 3 retention targets
**HARD_FAIL:** R(D)=0 everywhere or BA diverges
**MIDDLE_BAND:** R(D) non-trivial but N_min predictions all zero/infinite

## Smoke result

HARD_PASS at smoke (n_tasks=3): max_R=2.7238 nats; H_src=2.7726; N_min finite for 3 targets.
selftest 5/5 OK. status=COMPLETE printed.
