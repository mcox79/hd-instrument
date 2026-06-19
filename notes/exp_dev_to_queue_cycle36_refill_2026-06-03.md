# exp_dev Queue Routing: Cycle 36 Refill (v367)

**Date:** 2026-06-03
**Trigger:** pp49_hrc_depth_parity_discriminator Wave-5 Decisive #3 MIDDLE_BAND; GPU overnight_queue at 0 pending.
**Cap_map version:** v367
**Pause flag:** ABSENT (ACTIVE)

## Shipped

```
queue=overnight_queue name=q_a3_l48_cross_layer_composition_v1_n16384 script=experiments/exp_q_a3_l48_cross_layer_composition_v1_n16384.py prereg=preregs/2026-06-03_q_a3_l48_cross_layer_composition_v1_n16384.md timeout=21600
queue=overnight_queue name=q_a3_l28_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l28_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-03_q_a3_l28_cross_layer_composition_v1_n8192.md timeout=21600
```

## Rationale

- PP-12/Q-A3 N=16384 series {L=20..L=47}: L=48 extends 29th rung; band-lift streak maintained.
- PP-12/Q-A3 N=8192 cross-N: L=28 is 8th rung; bridges gap toward N=16384 frontier at L=47.
- GPU queue empty; highest strategic priority per cycle 33 routing note (Q1 + Q3).
- No padding: both anchors are directly on the open cap_map depth-extension track.

## Blocked

- pp49_hrc_protocol_artifact_nscale_v1_n8192: INSTRUMENTATION_SUSPECT (pred_cos=1.0 exact
  at all depths; degenerate single-pattern W_cf without background memory). See
  notes/exp_dev_to_strategy_instrumentation_suspect_pp49_nscale_2026-06-03.md for redesign spec.
  Needs strategy response before re-ship.

## Ship verification

Both anchors: queue_add.sh exit 0 + "VERIFIED present in remote overnight_queue/queue.json".
PROT-018: N suffix binding confirmed (N=16384, N=8192). PROT-019: timeout=21600s (floor met).
