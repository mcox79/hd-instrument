# exp_dev Queue Routing: Cycle 33 Refill

**Date:** 2026-06-03
**Trigger:** v364 CYCLE 33 verdict batch; GPU overnight_queue at 0 pending post-verdict.
**Pause flag:** ABSENT (ACTIVE)

## Anchors shipped

```
queue=overnight_queue name=q_a3_l37_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l37_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l37_l38_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l38_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l38_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l37_l38_n16384.md timeout=21600
```

## Rationale

Q1 (HIGH): L=37 and L=38 at N=16384 extend the depth ladder beyond the FIRST L=36 result (v364).
If BOTH pass, N=16384 leads N=4096 tested ceiling (L=35) by 3 rungs, triggering the PP-12/Q-A3
band-lift from 0.75-0.90 to 0.78-0.92 (per v364 band-lift eligibility analysis).
Scripts pre-existed from v363 refill cycle. Self-test passed remotely (2.8-2.9s).
PROT-018/019/021/022 all verified at gate.

## Deferred items (not shipped)

Q2 (L=36 N=4096): no script exists; lower priority since L=36 at N=16384 already confirmed.
Q3 (N=8192 L=26-28): CPU priority 7 pending in remote_cpu_queue; no urgent gap.
Q4 (PP-50 sigma_g R2 baseline): free diagnostic (sigma_g=0 check; no compute needed); 
  strategy can execute directly without a queued experiment.

## Remote verify

- q_a3_l37_cross_layer_composition_v1_n16384: VERIFIED present in remote overnight_queue/queue.json (exit 0)
- q_a3_l38_cross_layer_composition_v1_n16384: VERIFIED present in remote overnight_queue/queue.json (exit 0)
