# exp_dev queue ship: cue_clamped_production_v1

**Filed:** 2026-06-23
**From:** exp_dev (sonnet)
**To:** orchestrator / queue runner

## Queue entry (Schema A)

queue=remote_cpu_queue name=substrate_iterative_cleanup_cue_clamped_production_v1 script=experiments/exp_substrate_iterative_cleanup_cue_clamped_production_v1.py prereg=preregs/2026-06-23_substrate_iterative_cleanup_cue_clamped_production_v1.md timeout=5100

## Ship status

REMOTE VERIFY: PASS (queue_add.sh exit 0; VERIFIED present in remote remote_cpu_queue/queue.json)
Remote --self-test: 8.0s PASS
Remote queue pending count after ship: 7

## Routing note

Routed to remote_cpu_queue (not overnight_queue) because the cell is pure numpy
(no torch import); overnight_queue gate rejects numpy-only scripts (q_f5 incident rule).
Cell is matmul-heavy at N=8192 (Fix #22 flag) but uses numpy; remote_cpu_queue
is the correct destination for numpy/N_DIM=8192 runs.

User task spec said "overnight_queue (GPU)" but gate enforces torch requirement.
Production N=8192 matmul at remote CPU (~85 min estimate) is appropriate and faster
than laptop.

## Pre-reg bands (immutable)

- HARD_PASS: best ARM_CLAMPED beats ARM_BASELINE_NO_CLEANUP (7.2268 bpc) by >=+0.10 bits
- CHAIN_GRADE_BONUS: lift >=+0.20 AND beats cf-RPE 7.1052 by >=+0.05
- MIDDLE_BAND: lift +0.03 to +0.10
- HARD_FAIL: lift <=+0.03
- SANITY_RAIL_1: ARM_BASELINE_NO_CLEANUP within +-0.05 of 7.2268
- SANITY_RAIL_2: ARM_SINGLE_STEP within +-0.05 of 7.3753

## Next action on landing

Route to verdict_handler for end-to-end processing per normal pipeline.
