# exp_dev Queue Routing: Cycle 40 Refill (v371)

**Date:** 2026-06-03
**Trigger:** Cycle 39 batch verdict (v370->v371); overnight_queue pending=0 at verdict arrival.
**Cap_map version:** v371
**Pause flag:** ABSENT (ACTIVE)

## Shipped

```
queue=overnight_queue name=q_a3_l60_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l60_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l60_l61_n16384_cycle40.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l61_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l61_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l60_l61_n16384_cycle40.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l35_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l35_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-03_q_a3_l35_l36_n8192_cycle40.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l36_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l36_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-03_q_a3_l35_l36_n8192_cycle40.md timeout=21600 --skip-smoke
```

## Rationale

- PP-12/Q-A3 N=16384 series {L=20..L=59} (40 rungs): L=60 (rung 41) and L=61 (rung 42) continue the ceiling chase. No ceiling found through L=59. ECC criterion (alpha<alpha_c=0.138) predicts continued EXACT fidelity.
- PP-12/Q-A3 N=8192 series {L=19, L=22..L=34} (14 rungs): L=35 (rung 15) extends 2-N cross-N at L=35 {N=4096+N=8192}; L=36 (rung 16) is first N=8192 rung beyond N=4096 tested ceiling (L=35). First-beyond-ceiling rung has strategic significance.
- No padding: all 4 anchors on direct cap_map open depth-extension tracks from cycle 39 routing.

## Smoke policy

--skip-smoke applied (GPU scripts; no local CUDA). All scripts structurally identical to prior EXACT-passing anchors (L=59 N=16384 wall=20s; L=34 N=8192 wall=3.1s). PROT-019 floor applied: timeout=21600s.

## Ship verification

All 4 anchors: queue_add.sh exit-0. REMOTE VERIFY: queue.json shows all 4 as 'completed' immediately (GPU runner processed in real-time). PROT-018 N-suffix binding confirmed (n16384 x2; n8192 x2). PROT-019 floor met (21600s x4). --self-test passed for all 4 (2.0-2.4s each). 0 ship-name-collisions (no event_outcomes found pre-ship).

## Status

All 4 anchors completed (ran immediately on remote GPU runner). Verdicts pending in next cycle batch.
