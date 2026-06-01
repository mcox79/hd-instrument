# exp_dev -> queue: research surge v276 convergent priorities (2026-05-29)

Filed: 2026-05-29 by exp_dev
Source: notes/research_surge_synthesis_v276_2026-05-29.md + handoff notes

## Shipments

```
queue=overnight_queue name=kf45_pre_argmax_joint_probe_v1_n4096 script=experiments/exp_kf45_pre_argmax_joint_probe_v1_n4096.py prereg=preregs/2026-05-29_kf45_pre_argmax_joint_probe_v1_n4096.md timeout=14400
queue=overnight_queue name=bet_b_tp_hdc_subspace_v1_n2048 script=experiments/exp_bet_b_tp_hdc_subspace_v1_n2048.py prereg=preregs/2026-05-29_bet_b_tp_hdc_subspace_v1_n2048.md timeout=14400
queue=overnight_queue name=bet_b_genreplay_phaseD_v1_n2048 script=experiments/exp_bet_b_genreplay_phaseD_v1_n2048.py prereg=preregs/2026-05-29_bet_b_genreplay_phaseD_v1_n2048.md timeout=14400
queue=overnight_queue name=bet_b_moe_per_task_dg_gating_v1_n2048 script=experiments/exp_bet_b_moe_per_task_dg_gating_v1_n2048.py prereg=preregs/2026-05-29_bet_b_moe_per_task_dg_gating_v1_n2048.md timeout=14400
queue=remote_cpu_queue name=operating_point_singularity_basin_map_v1_n4096 script=experiments/exp_operating_point_singularity_basin_map_v1_n4096.py prereg=preregs/2026-05-29_operating_point_singularity_basin_map_v1_n4096.md timeout=14400
```

## All 5 REMOTE VERIFY: PASS
- overnight_queue pending: 26 (was 23 + 4 new GPU anchors = 27, minus in-flight = 26)
- remote_cpu_queue pending: 10 (was 9 + 1 new CPU anchor = 10)
- All 5 confirmed present in remote queue.json via queue_add.sh exit-0 + VERIFIED message

## Deferred
P2 (BE-1 v2 W-magnitude-operative): needs 1d script-design eng. Not shipped this cycle.
