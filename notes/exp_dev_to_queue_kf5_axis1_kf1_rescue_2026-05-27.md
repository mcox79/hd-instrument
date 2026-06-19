# exp_dev -> queue: KF5 v3 + axis1 chunk3 + KF1 tier-1 rescue

**Filed:** 2026-05-27 (evening GPU refill)
**Trigger:** strategy_request_to_exp_dev_v256_kf_battery_v3_followon_2026-05-27.md
**Queue depth at filing:** 0 pending (GPU idle 13min)

## Shipped anchors

```
queue=overnight_queue name=kf5_steerable_beta_v3_n8192 script=experiments/exp_kf5_steerable_beta_v3_n8192.py prereg=preregs/2026-05-27_kf5_steerable_beta_v3_n8192.md timeout=900
queue=overnight_queue name=axis1_mb_chunk3_v1_n4096 script=experiments/exp_axis1_mb_chunk3_v1_n4096.py prereg=prereqs/2026-05-27_axis1_mb_chunk3_v1_n4096.md timeout=900
queue=overnight_queue name=kf1_tier1_rescue_v1_n4096 script=experiments/exp_kf1_tier1_rescue_v1_n4096.py prereg=prereqs/2026-05-27_kf1_tier1_rescue_v1_n4096.md timeout=600
```

## Remote verify status

All 3: REMOTE VERIFY PASS (queue_add.sh exit=0 + remote queue.json confirmed)

## Justification per anchor

**kf5_steerable_beta_v3_n8192:** Strategy v256 routing note priority (d): envelope extension of KF-5 to N=8192.
  Directly tests whether beta-steering is substrate-intrinsic or finite-N artifact.
  Smoke: entropy_range=7.58 bits (strong signal; same as v2). Self-test PASS.

**axis1_mb_chunk3_v1_n4096:** Strategy v256 routing note priority 2: fine-grid M/N in {4.5..12}.
  Chunk-2 HARD_PASS found boundary at M*=M/N~8-16 (ret=1.0 to 0.503). Chunk-3 resolves exact M_50.
  Smoke: transition visible at N=1024 (ret 0.885->0.515 across M/N=5..8). Self-test PASS.

**kf1_tier1_rescue_v1_n4096:** Strategy v256 routing note priority 2: KF-1 Tier-1 rescue.
  v2 MIDDLE_BAND: 5/5 seeds pass 0.001 but not 1e-6 spec (170x off).
  Reformulation: near-uniform bound (10/C = 6.1e-4). N=4096 ratio expected ~2.8x < 10x (HARD_PASS).
  Smoke: above_thresh=0 (structural claim holds); ratio N=1024 high (17x) as expected.

## BLOCKED anchors (not shipped, with justification)

**bet_b_4stage_n16384_batch128_v1:** Task context reported OOM, but remote data shows
  bet_b_4stage_n16384_v1 HARD_PASSed (ret_A=0.911, n_seeds=1). The batch128 rescue is moot.
  Not shipped to avoid padding.

**kf_battery_joint_v1_n4096:** Queue depth=3 after these 3; adding a 4th would exceed
  justified candidate pool. Strategy routing note says "pick 1-3". Deferred to next cycle.
