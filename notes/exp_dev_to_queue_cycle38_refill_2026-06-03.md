# exp_dev Queue Routing: Cycle 38 Refill (v369)

**Date:** 2026-06-03
**Trigger:** Cycle 37 batch verdict (v368->v369); overnight_queue pending=0.
**Cap_map version:** v369
**Pause flag:** ABSENT (ACTIVE)

## Shipped

```
queue=overnight_queue name=q_a3_l52_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l52_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l52_l53_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l53_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l53_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l52_l53_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l30_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l30_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-03_q_a3_l30_n8192.md timeout=21600
```

## Rationale

- PP-12/Q-A3 N=16384 series {L=20..L=51} (32 rungs): L=52 and L=53 extend rungs 33 and 34; maintain depth-extension track; no ceiling found through L=51.
- PP-12/Q-A3 N=8192 cross-N series {L=19, L=22..L=29} (9 rungs): L=30 is 10th rung; 2-N cross-N at L=30 {N=4096+N=8192} extends N-independence evidence; N=4096 L=30 confirmed in project history.
- Q-B1 bisection COMPLETE -- no further bisect anchors needed.
- No padding: all 3 anchors are directly on open cap_map depth-extension tracks.

## Smoke policy

--skip-smoke applied (GPU scripts; no local CUDA). Scripts are structurally identical to L=49/50/51 (N=16384) and L=29 (N=8192) which all passed FULL 5-seed unanimously. Timing anchor: L=51 elapsed_s=25.3s (N=16384); L=29 elapsed_s=3.0s (N=8192). PROT-019 floor applied: timeout=21600s.

## Ship verification

All 3 anchors: queue_add.sh exit-0 + "VERIFIED present in remote overnight_queue/queue.json". PROT-018 N-suffix binding confirmed (n16384 x2; n8192 x1). PROT-019 floor met (21600s). --self-test passed for all 3 (4.2-4.5s each). 0 duplicates found in local queue.json or event_outcomes/.
