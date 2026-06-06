# exp_dev Queue Routing: Cycle 42 Refill (v373)

**Date:** 2026-06-04
**Trigger:** CYCLE 41 BATCH verdict (v372->v373); overnight_queue pending=0 at verdict arrival.
**Cap_map version:** v373
**Pause flag:** ABSENT (ACTIVE)

## Shipped

```
queue=overnight_queue name=q_a3_l72_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l72_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l72_l77_n16384_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l73_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l73_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l72_l77_n16384_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l74_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l74_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l72_l77_n16384_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l75_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l75_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l72_l77_n16384_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l76_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l76_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l72_l77_n16384_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l77_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l77_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-04_q_a3_l72_l77_n16384_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l43_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l43_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l43_l45_n8192_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l44_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l44_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l43_l45_n8192_cycle42.md timeout=21600 --skip-smoke
queue=overnight_queue name=q_a3_l45_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l45_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-04_q_a3_l43_l45_n8192_cycle42.md timeout=21600 --skip-smoke
```

## Rationale

- PP-12/Q-A3 N=16384 {L=20..L=71} (52 rungs, v373): L=72..L=77 continue depth extension. L=71 NEW DEEPEST. ECC alpha < 0.01 << alpha_c=0.138 at N=16384.
- PP-12/Q-A3 N=8192 {L=19,L=22..L=42} (22 rungs, v373): L=43..L=45 continue N=8192 cross-N ladder. L=42 NEW N=8192 DEEPEST. 2-N cross-N: N=16384 already EXACT at L=43..L=45 (v366).
- 9 anchors total (6xN=16384 + 3xN=8192); all on direct open depth-extension tracks.
- No padding: no marginal anchors added to hit queue depth.

## Ship verification

All 9: PROT-018 N-suffix verified; PROT-019 floor 21600s met; --self-test passed 2.0-2.9s; VERIFIED in remote overnight_queue/queue.json. 0 ship-name-collisions (no prior completions for these names).
