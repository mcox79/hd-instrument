# exp_dev queue routing note — morning refill 2026-05-27

**Filed:** 2026-05-27 by exp_dev sub-agent.

## Shipments

```
queue=overnight_queue name=anchor_novel_phase_battery_v1 script=experiments/exp_anchor_novel_phase_battery_v1.py prereg=preregs/2026-05-27_anchor_novel_phase_battery_v1.md timeout=14400
queue=remote_cpu_queue name=wave14_moe_cosine_router_v1 script=experiments/exp_wave14_moe_cosine_router_v1.py prereg=preregs/2026-05-27_wave14_moe_cosine_router_v1.md timeout=3600
queue=remote_cpu_queue name=wave14_corpus_size_scaling_v1 script=experiments/exp_wave14_corpus_size_scaling_v1.py prereg=preregs/2026-05-27_wave14_corpus_size_scaling_v1.md timeout=3600
```

## Rescue probe status (Part 2)

All 4 rescue probes survived the reboot — found in remote queue as pending:
- wave14_1rsb_cluster_cond_pq_v1: PENDING (remote_cpu_queue) -- no re-ship needed
- wave14_1rsb_rate_dep_hysteresis_v1: PENDING (remote_cpu_queue) -- no re-ship needed
- wave14_tcft_substrate_falsifier_v1: PENDING (remote_cpu_queue) -- no re-ship needed
- wave14_kerdock_distance_class_audit_v1: PENDING (remote_cpu_queue) -- no re-ship needed

## Post-ship verification

All 3 new entries confirmed present via queue_add.sh exit-0 + remote JSON verify.
No name collisions detected pre-ship.
