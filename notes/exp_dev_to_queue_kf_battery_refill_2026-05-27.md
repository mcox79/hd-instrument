# exp_dev_to_queue: KF battery refill (5 anchors)

**Date**: 2026-05-27 23:00
**From**: exp_dev (inline via routing_handler)
**Source routing file**: notes/strategy_request_to_exp_dev_kf_battery_refill_2026-05-27.md

## Shipped anchors

```
queue=overnight_queue name=kf5_steerable_beta_v2 script=experiments/exp_kf5_steerable_beta_v2.py prereg=prereqs/2026-05-27_kf5_steerable_beta_v2.md timeout=3300
queue=overnight_queue name=axis1_mb_chunk2_v1 script=experiments/exp_axis1_mb_chunk2_v1.py prereg=prereqs/2026-05-27_axis1_mb_chunk2_v1.md timeout=3600
queue=overnight_queue name=kf1_hallu_impossibility_v2 script=experiments/exp_kf1_hallu_impossibility_v2.py prereg=prereqs/2026-05-27_kf1_hallu_impossibility_v2.md timeout=10800
queue=overnight_queue name=kf4_drift_detect_v2 script=experiments/exp_kf4_drift_detect_v2.py prereg=prereqs/2026-05-27_kf4_drift_detect_v2.md timeout=2400
queue=overnight_queue name=bet_b_4stage_n16384_v1 script=experiments/exp_bet_b_4stage_n16384_v1.py prereg=prereqs/2026-05-27_bet_b_4stage_n16384_v1.md timeout=7200
```

## Notes

- kf5_steerable_beta_v2: Had GPU generator bug on first run (torch.Generator(device=cuda) incompatible with pa.make_bsc_atoms which calls torch.rand with CPU generator). Fixed to use torch.Generator(device="cpu") for atom creation. Re-queued with --allow-duplicate (run_index=2). REMOTE VERIFIED.
- axis1_mb_chunk2_v1: Already running on GPU as of verification. REMOTE VERIFIED.
- All 5 anchors: smoke passed locally; PROT-018 N-binding verified (no _nN suffix; production N stated in each script); REMOTE VERIFY from queue_add.sh exit-0 with built-in remote verify.
- P6 (kf5_dual_v1 beta-extension) deferred pending kf5_v2 verdict.
