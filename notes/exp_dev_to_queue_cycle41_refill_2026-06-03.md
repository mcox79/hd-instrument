# exp_dev Queue Routing: Cycle 41 Refill (v372)

**Date:** 2026-06-03
**Trigger:** CYCLE 40 LARGE BATCH verdict (v371->v372); overnight_queue pending=0 at verdict arrival.
**Cap_map version:** v372
**Pause flag:** ABSENT (ACTIVE)

## Shipped

```
queue=overnight_queue name=q_a3_l64_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l64_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l64_l65_n16384_cycle41.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l65_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l65_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l64_l65_n16384_cycle41.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l39_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l39_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-03_q_a3_l39_l40_n8192_cycle41.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l40_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l40_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-03_q_a3_l39_l40_n8192_cycle41.md timeout=21600 --skip-smoke
```

## Rationale

- PP-12/Q-A3 N=16384 series {L=20..L=63} (44 rungs): L=64 (rung 45) and L=65 (rung 46) continue ceiling chase. L=63 is NEW DEEPEST project history (v372). ECC criterion: alpha < alpha_c=0.138 at all layers; unlimited depth predicted.
- PP-12/Q-A3 N=8192 series {L=19,L=22..L=38} (18 rungs): L=39 (rung 19) and L=40 (rung 20) continue N=8192 cross-N depth ladder. L=38 is NEW N=8192 DEEPEST (v372).
- No padding: all 4 anchors on direct cap_map open depth-extension tracks from v372.
- PP-49 R2 (reduced kappa sweep) deferred: requires new script design (kappa sweep logic different from ECC chain; theory audit R1 should precede empirical).
- PP-50 R2 (lower-d sigma_g sweep) deferred: strategy routing needed for redesign spec.
- PP-33 R3c already in queue (shipped earlier cycle).

## Smoke policy

--skip-smoke applied (GPU scripts; no local CUDA). All scripts structurally identical to prior EXACT-passing anchors (L=63 N=16384 wall=21s; L=38 N=8192 wall=3.5s). PROT-019 floor: 21600s.

## Ship verification

All 4 anchors: queue_add.sh exit-0. REMOTE VERIFY: all 4 entries confirmed present in remote overnight_queue/queue.json. PROT-018 N-suffix binding confirmed (n16384 x2; n8192 x2). PROT-019 floor met (21600s x4). --self-test passed for all 4 (2.4-2.8s each). 0 ship-name-collisions (no event_outcomes found pre-ship).
