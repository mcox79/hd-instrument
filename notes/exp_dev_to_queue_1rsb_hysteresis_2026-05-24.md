# exp_dev -> queue: 1-RSB hysteresis anchor (Pred-4)

Filed: 2026-05-24 exp_dev
Trigger: wave14_1rsb_pq_retained_v1 MIDDLE (Pred-2 inconclusive); remote_cpu_queue IDLE; Pred-4 is sole remaining CPU diagnostic.

## Queue entries (Schema A)

queue=remote_cpu_queue name=wave14_1rsb_hysteresis_v1 script=experiments/exp_wave14_1rsb_hysteresis_v1.py prereg=preregs/2026-05-24_wave14_1rsb_hysteresis_v1.md timeout=5400

## Ship verification

- Name uniqueness: no prior hysteresis entries in remote_cpu_queue or overnight_queue (grep clean)
- Remote --self-test gate: PASS 6/6 in 1.8s (run on marsh@home before queue_add.sh)
- Post-ship VERIFIED: wave14_1rsb_hysteresis_v1 present in remote remote_cpu_queue/queue.json
- Queue depth after ship: remote_cpu_queue pending=1

## Design summary

Pred-4 hysteresis test: sweeps M (bytes per corpus stage) from low to high (forward trajectory)
and from high to low (reverse trajectory). At each M, measures retA (stage-A retention) after
full 4-stage M1 hierreplay. Hysteresis gap = |retA_forward - retA_reverse|.

HARD-PASS: max gap >= 0.10 (first-order transition signature; 1-RSB supported)
HARD-FAIL: max gap < 0.03 (continuous transition; 1-RSB NOT supported at capacity axis)
MIDDLE: gap in [0.03, 0.10)

Self-test: 6/6 cases covering all 3 verdicts + boundary conditions.
N=2048, 7 M cells, 3 seeds, ETA 30-45 min CPU.
