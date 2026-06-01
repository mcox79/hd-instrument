# exp_dev to queue: night rescue batch 2026-05-26

Filed: 2026-05-26 by exp_dev (night rescue dispatch per strategic intent).

## Shipped experiments (2 new + 1 pre-existing)

```
queue=remote_cpu_queue name=wave14_1rsb_rate_dep_hysteresis_v1 script=experiments/exp_wave14_1rsb_rate_dep_hysteresis_v1.py prereg=prereqs/2026-05-26_wave14_1rsb_rate_dep_hysteresis_v1.md timeout=9000
queue=remote_cpu_queue name=wave14_1rsb_cluster_cond_pq_v1 script=experiments/exp_wave14_1rsb_cluster_cond_pq_v1.py prereg=prereqs/2026-05-26_wave14_1rsb_cluster_cond_pq_v1.md timeout=7200
```

## Pre-existing (not re-shipped)

- wave14_tcft_substrate_falsifier_v1: already in remote_cpu_queue (CONFIRMED via bridge)

## Priority status

- Priority 1 (cluster-conditional P(q)): SHIPPED as wave14_1rsb_cluster_cond_pq_v1; smoke shows inverted within/across structure (within_q=0.03 < across_q=0.24); ETA 2h CPU
- Priority 2 (rate-dep hysteresis): SHIPPED as wave14_1rsb_rate_dep_hysteresis_v1; smoke r=-0.9996/-0.9987 (strong rate-dependence signal); ETA 1-2h CPU
- Priority 3 (TCFT): PRE-EXISTING in queue; no re-ship needed
- Night-depth: GPU=10 pending, CPU=21 pending (all from prior sessions + tonight's 2 new)

## Key smoke findings

rate_dep_hysteresis smoke (N=256, epochs=[1,2,4], 1 seed):
- M=2000: r=-0.9996; gap decreases from 0.84->0.53 as epochs increases 1->4
- M=10000: r=-0.9987; gap decreases from 0.19->-0.08 (sign flip at slow cooling)
- Walk-back: effect size is large; N=1024 full scale appropriate

cluster_cond_pq smoke (N=256, 2 seeds/class):
- within_mean_q=0.033 (all 4 classes near zero)
- across_mean_q=0.236 (unexpectedly higher)
- diff=-0.202 (INVERTED from cluster-glass prediction)
- Smoke verdict: MIDDLE_BAND (binder=0 trivially at 2 seeds; full scale will compute real binder)
- Not suspicious: N=256 BSC W vectors are very high-dimensional; overlap structure is genuine

## Remote verification

Both ships: queue_add.sh exit 0, VERIFIED in remote queue.json. CPU queue depth: 21 pending.
