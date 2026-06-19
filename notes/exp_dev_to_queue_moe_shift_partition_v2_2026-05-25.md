# exp_dev to queue: MoE Shift-Partition v2 (DMPK patch) -- overnight_queue

**Filed:** 2026-05-25 by exp_dev sub-agent
**Status:** READY FOR SSH SHIP -- main thread must run queue_add.sh (sub-agent SSH blocked)
**Handoff:** notes/exp_dev_handoff_research_mesoscopic_xtalk_diagnostic_2026-05-25.md

## ACTION REQUIRED (main thread)

The script has passed self-test (9/9) and smoke (PASS, d=0.446, lift=0.068).
SSH and SCP are blocked in sub-agent context per [[feedback-subagent-permission-inheritance]].
The orchestrator main thread must run:

```bash
bash tools/orchestrator/queue_add.sh overnight_queue wave14_moe_shift_partition_v2 experiments/exp_wave14_moe_shift_partition_v2.py --prereg preregs/2026-05-25_wave14_moe_shift_partition_v2.md --timeout 25200
```

Then verify:
```bash
ssh marsh@home "python -c \"import json; q=json.load(open('/root/hd-instrument/data/overnight_queue/queue.json')); print('VERIFIED' if 'wave14_moe_shift_partition_v2' in [e['name'] for e in q.get('experiments',[])] else 'MISSING')\""
```

## What was built

`experiments/exp_wave14_moe_shift_partition_v2.py` -- DMPK-patched version of the 3-arm MoE rebuild.

Changes from v1:
- Added `compute_dmpk_signature()`: SVD spectrum of per-expert W_k matrices
- Added `compute_gate_overlap()`: off-diagonal gate-overlap (mesoscopic xi parameter)
- Wired into `run_arm_a_shift()` and `run_arm_b_partition()` (BEFORE `del Wks`)
- Added `mesoscopic_verdict` secondary verdict to `compute_verdict()` (ADDITIVE, does NOT gate primary)
- Added DMPK fields to results serialization
- Added 2 new self-tests (tests 8 and 9) -- all 9 pass
- Updated output dir to `wave14_moe_shift_partition_v2`

## Walk-back note

Smoke at N=512, K=[1,2,4], 1 seed: effect_size_d=0.446, lift=0.068 (borderline).
Full run registered at N=4096, K=[1,2,4,8], n=5 seeds per walk-back gate.
DMPK overhead: ~12 min on top of ~4-6 GPU-hr base run = ~5-7 GPU-hr total.

## Schema A queue entry

```
queue=overnight_queue name=wave14_moe_shift_partition_v2 script=experiments/exp_wave14_moe_shift_partition_v2.py prereg=preregs/2026-05-25_wave14_moe_shift_partition_v2.md timeout=25200
```
