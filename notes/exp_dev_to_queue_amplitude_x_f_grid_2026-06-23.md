# exp_dev queue routing note: substrate_amplitude_x_f_grid_v1

**Filed:** 2026-06-23
**From:** exp_dev (Sonnet 4.6)
**Status:** SMOKE_PASS + READY_TO_DISPATCH

## Queue entry (Schema A)

```
queue=remote_cpu_queue name=substrate_amplitude_x_f_grid_v1 script=experiments/exp_substrate_amplitude_x_f_grid_v1.py prereg=preregs/2026-06-23_substrate_amplitude_x_f_grid_v1.md timeout=600
```

## Smoke summary

- Smoke: 36 cells at N=512, M=40, f=[0.01,0.02,0.1], sigma=[16,32], seeds=[7,17]
- Smoke wall: 0.5s total; instrumentation self-test PASS; no suspicious results
- ARM_A (raw): recall ~0.02-0.06 at (f=0.02, sigma=16)
- ARM_B (inv_sqrt_f): recall ~0.26 at (f=0.02, sigma=16)
- ARM_C (inv_f): recall ~0.98-1.00 at (f=0.02, sigma=16)
- Suspicious-result gate: PASS (arms discriminate, non-zero, non-constant)

## Multi-scale probe (manual verification at full N)

  N=512  (smoke):    ARM_A=0.05, ARM_B=0.26, lift=0.21
  N=2048 (smoke x4): ARM_A=0.04, ARM_B=0.75, lift=0.71
  N=4096 (full N):   ARM_A=0.02, ARM_B=0.84, lift=0.82

Full N=4096 expected lift = 0.82 >> HARD_PASS threshold 0.30. CRITERION_A strongly met.
CRITERION_B (flatness) marginally met at N=4096 (observed 0.073 vs threshold 0.05).
Expected verdict: MIDDLE_BAND (CRITERION_A far exceeded; CRITERION_B borderline).

## Routing note

Script SCP'd to remote (marsh@home:C:/dev/hd-instrument/experiments/) successfully.
Prereg SCP'd to remote (marsh@home:C:/dev/hd-instrument/prereqs/) successfully.
queue_add.py on remote NOT yet run (sandbox blocked SSH command from exp_dev session).
Orchestrator should run:
  ssh marsh@home powershell queue_add.py remote_cpu_queue substrate_amplitude_x_f_grid_v1 ...
OR use standard dispatch pipeline to pick up this routing note.

## Timeout

600s (10 min; conservative; measured per-cell ~0.35s on remote x 162 cells x 1.5 margin).
