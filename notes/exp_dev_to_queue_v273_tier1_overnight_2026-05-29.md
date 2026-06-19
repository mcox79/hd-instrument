# exp_dev routing note: v273 Tier-1 overnight refill

**Filed:** 2026-05-29 by exp_dev (sonnet)
**Trigger:** strategy_request_to_exp_dev_v273_overnight_refill_user_strategy_2026-05-29.md
**Status:** ALL 5 SHIPPED + REMOTE VERIFIED

## Shipped anchors (Schema A)

```
queue=overnight_queue name=kf2_be1_soft_readout_n8192 script=experiments/exp_kf2_be1_soft_readout_n8192.py prereg=prereqs/2026-05-29_kf2_be1_soft_readout_n8192.md timeout=21600
queue=overnight_queue name=kf2_be1_retrieval_acc_n8192 script=experiments/exp_kf2_be1_retrieval_acc_n8192.py prereg=prereqs/2026-05-29_kf2_be1_retrieval_acc_n8192.md timeout=21600
queue=overnight_queue name=kf5_fine_beta_betac_n4096 script=experiments/exp_kf5_fine_beta_betac_n4096.py prereg=prereqs/2026-05-29_kf5_fine_beta_betac_n4096.md timeout=14400
queue=overnight_queue name=bet_b_cl_wide_phaseA_v1 script=experiments/exp_bet_b_cl_wide_phaseA_v1.py prereg=prereqs/2026-05-29_bet_b_cl_wide_phaseA_v1.md timeout=1500
queue=overnight_queue name=bet_b_cl_frozen_phaseA_v1 script=experiments/exp_bet_b_cl_frozen_phaseA_v1.py prereg=prereqs/2026-05-29_bet_b_cl_frozen_phaseA_v1.md timeout=900
```

## Smoke results summary

| Anchor | Smoke Verdict | Key metric |
|---|---|---|
| kf2_be1_soft_readout_n8192 (A1) | HARD_FAIL (smoke) | INT1/FP32 ratio=0.03 (flat; W-magnitude insensitive under softmax readout) |
| kf2_be1_retrieval_acc_n8192 (A2) | HARD_FAIL (smoke) | INT1 acc=0.780 vs FP32 acc=0.755 (insensitive at smoke scale) |
| kf5_fine_beta_betac_n4096 (B1) | MIDDLE_BAND | softmax_conf signal=0.58 (large), edit_iso=0.0 |
| bet_b_cl_wide_phaseA_v1 (C1) | HARD_PASS | ret_A=1.000, ret_B=0.907, ret_C=0.851 |
| bet_b_cl_frozen_phaseA_v1 (C2) | HARD_PASS | ret_A=1.000, ret_B=0.906, ret_C=0.896 |

## Notes

- A1 and A2 smoke HARD_FAIL: both show quantization-insensitive behavior. This is a
  meaningful scientific result (not an instrumentation failure). W-magnitude appears
  genuinely not operative in both isolation and retrieval metrics at smoke scale.
  FULL runs at N=8192 will confirm definitively.
- C1 and C2 smoke HARD_PASS: both architectural rescues for Bet B show very strong
  smoke results (ret_A=1.000). The smoke-to-full gap from v2 history was -0.103 on ret_A,
  so FULL expected ~0.85-0.90 -- above the 0.80 threshold. These are the most promising
  rescue results to date.
- B1: softmax_conf shows clear beta transition (signal=0.58) but edit_iso is flat at
  smoke scale. FULL at N=4096 with 3 M_fracs may reveal whether additional metrics
  show near-boundary steerability.
- Remote verify: all 5 anchors confirmed present in remote overnight_queue/queue.json
  (queue_add.sh exit 0 + VERIFIED log line for each).
