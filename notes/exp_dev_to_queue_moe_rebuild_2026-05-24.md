# exp_dev queue routing note: MoE rebuild unblock

**Filed:** 2026-05-24 by exp_dev sub-agent
**Trigger:** notes/exp_dev_handoff_research_alpha_c_recalibration_2026-05-24.md + notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md
**Status:** SHIPPED + REMOTE VERIFIED

## Queue entries (Schema A)

```
queue=overnight_queue name=wave14_moe_alpha_c_prestep_v2 script=experiments/exp_wave14_moe_alpha_c_prestep_v2.py prereg=preregs/2026-05-24_wave14_moe_alpha_c_prestep_v2.md timeout=2400
queue=overnight_queue name=wave14_moe_shift_partition_v1 script=experiments/exp_wave14_moe_shift_partition_v1.py prereg=preregs/2026-05-24_wave14_moe_shift_partition_v1.md timeout=25200
```

## Dependency check

- exp_wave14_moe_alpha_c_prestep_v2: no upstream dependency (self-contained N=4096 calibration)
- exp_wave14_moe_shift_partition_v1: uses M_per_expert=1600 from recalibrated alpha_c=0.56 theory;
  does NOT depend on prestep_v2 result at runtime (M_per_expert baked in at design time).
  If prestep_v2 returns HARD-PASS with a significantly different alpha_c, verdict_handler should
  note whether M_per_expert needs adjustment and trigger a follow-up sweep.

## Ship verification

Both entries confirmed present in remote overnight_queue/queue.json via SSH poll.
Pre-ship uniqueness check: UNIQUE for both names (no queue.json or event_outcomes collision).

## What to expect

1. wave14_moe_alpha_c_prestep_v2 runs first (~15-30 GPU-min).
   Expected verdict: ALPHA_C_HARD_PASS with alpha_c_measured in [0.50,0.60].
   Key outputs: alpha_c_measured, M_per_expert_recommended, max_closed_form_residual.

2. wave14_moe_shift_partition_v1 runs next (~4-6 GPU-hr).
   Expected verdict: MOE_SHIFT_HARD_PASS or MOE_SHIFT_MIDDLE.
   Key outputs: best_lift_a_vs_c, mode_collapse metrics, monotone_in_K.

## Smoke results summary

prestep_v2: multi-scale smoke N=512 + N=2048 PASS.
  Max residual: 0.0036 (vs closed-form prediction). Well within MIDDLE threshold.

shift_partition_v1: smoke N=512, K in {1,2,4}, 1 seed PASS.
  Suspicious-result gate: CLEAR.
  Walk-back gate: TRIGGERED (d=0.446 < 1.0) -- noted in prereg.
  Best smoke signal: K=4, M=1600, Arm A=0.699 vs Arm C=0.512 (lift +0.187 > HARD-PASS 0.15).
