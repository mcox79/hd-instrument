# exp_dev -> queue: CYCLE 28 refill (2026-06-03)

Queue was at 0 after CYCLE 27 batch. Pipeline-pacing refill. NOT_PAUSED confirmed.

## Shipped

```
queue=overnight_queue name=q_a3_l24_cross_layer_composition_v1_n8192 script=experiments/exp_q_a3_l24_cross_layer_composition_v1_n8192.py prereg=preregs/2026-06-03_q_a3_l24_cross_layer_composition_v1_n8192.md timeout=21600
queue=overnight_queue name=q_a3_l30_cross_layer_composition_v1_n4096 script=experiments/exp_q_a3_l30_cross_layer_composition_v1_n4096.py prereg=preregs/2026-06-03_q_a3_l30_cross_layer_composition_v1_n4096.md timeout=14400
```

## Rationale

1. **q_a3_l24_cross_layer_composition_v1_n8192** -- PP-12/Q-A3 N-scale gap closure.
   N=8192 series now {L=19, L=22, L=23}; L=24 is next cheapest gap closure.
   Prior L=23 N=8192 HARD_PASS EXACT-class (v358; 4.31s wall). Estimated wall ~5s.
   PROT-018: N=8192 verified. PROT-019: timeout=21600s (tier floor for _n8192).

2. **q_a3_l30_cross_layer_composition_v1_n4096** -- PP-12/Q-A3 ceiling chase.
   L-series L=2..L=29 all EXACT-1.0000 (15 consecutive extensions; v358).
   16th L-extension; ceiling not found at L=29. Estimated wall ~2s.
   PROT-018: N=4096 verified. PROT-019: timeout=14400s (tier floor for _n4096).

## Ship verification

Both anchors: queue_add.sh exit 0 + VERIFIED in remote overnight_queue/queue.json.
No name collisions (pre-ship bridge check OK for both).

## Not shipped (considered but deferred)

- Q-B1 d=287 bisect: would require a new script (bisect_d287); deferred to next cycle.
  The d=275--300 onset window is narrow; d=275 HP just confirmed; R1 condition audit
  (free; ~5 min read of script params) should happen before next bisect.
  Q-B1 d=287 is ready as a ~1200s wall GPU run when condition audit completes.

- PP-58 R2 theory recalibration: pure theory task (~4h); no compute; not an exp_dev item.
  Surface to orchestrator for theory-session routing if applicable.
