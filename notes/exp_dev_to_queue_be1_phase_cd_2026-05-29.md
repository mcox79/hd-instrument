# Queue Ship Note: BE-1 + Phase Region C/D Anchors

Filed: 2026-05-29
Status: SCRIPTS READY, SMOKES PASS -- SSH OFFLINE, QUEUE PENDING MAIN THREAD
Note: SSH to marsh@home unavailable (remote offline ~24h). Ship commands below.
Execute once SSH recovers (post-reset, ONLOGON).

## BE-1 Precision Floor Sweep (TASK A -- 6 GPU anchors)

```
queue=overnight_queue name=kf2_be1_fp32_n8192 script=experiments/exp_kf2_be1_fp32_n8192.py prereg=preregs/2026-05-29_kf2_be1_n8192.md timeout=21600
queue=overnight_queue name=kf2_be1_fp16_n8192 script=experiments/exp_kf2_be1_fp16_n8192.py prereg=preregs/2026-05-29_kf2_be1_n8192.md timeout=21600
queue=overnight_queue name=kf2_be1_int8_n8192 script=experiments/exp_kf2_be1_int8_n8192.py prereg=preregs/2026-05-29_kf2_be1_n8192.md timeout=21600
queue=overnight_queue name=kf2_be1_int4_n8192 script=experiments/exp_kf2_be1_int4_n8192.py prereg=preregs/2026-05-29_kf2_be1_n8192.md timeout=21600
queue=overnight_queue name=kf2_be1_int2_n8192 script=experiments/exp_kf2_be1_int2_n8192.py prereg=preregs/2026-05-29_kf2_be1_n8192.md timeout=21600
queue=overnight_queue name=kf2_be1_int1_n8192 script=experiments/exp_kf2_be1_int1_n8192.py prereg=preregs/2026-05-29_kf2_be1_n8192.md timeout=21600
```

Justification: BE-1 precision floor sweep per v269 strategy (cheapest path to category-defining
cost advantage). Parent: v268 kf2_cross_codebook_v2_n8192 HARD_PASS. Characterizes INT8/INT4/etc
isolation retention for product deployment cost claims.

## Phase Region C/D Probe (TASK B -- 4 GPU anchors)

```
queue=overnight_queue name=region_c_kf1_n4096_beta64_mfrac4 script=experiments/exp_region_c_kf1_n4096_beta64_mfrac4.py prereg=preregs/2026-05-29_phase_region_cd_n4096.md timeout=14400
queue=overnight_queue name=region_c_kf2_n4096_beta64_mfrac4 script=experiments/exp_region_c_kf2_n4096_beta64_mfrac4.py prereg=preregs/2026-05-29_phase_region_cd_n4096.md timeout=14400
queue=overnight_queue name=region_d_kf1_n4096_beta64_mfrac12 script=experiments/exp_region_d_kf1_n4096_beta64_mfrac12.py prereg=preregs/2026-05-29_phase_region_cd_n4096.md timeout=14400
queue=overnight_queue name=region_d_kf2_n4096_beta64_mfrac12 script=experiments/exp_region_d_kf2_n4096_beta64_mfrac12.py prereg=preregs/2026-05-29_phase_region_cd_n4096.md timeout=14400
```

Justification: Phase region C/D probe per v269 strategy (beta > beta_c unprobed regime).
Parent: t1_beta_sweep_v1_n4096 (v267 HARD_PASS, beta_c~10-16 localized).
TCFT and Saad-Solla versions blocked (Tier-2; see notes/exp_dev_to_strategy_phase_cd_tcft_ss_blocker_2026-05-29.md).

## Bash Commands to Execute (once SSH is up)

```bash
cd d:/AI/hd-instrument
# BE-1 anchors
bash tools/orchestrator/queue_add.sh overnight_queue kf2_be1_fp32_n8192 experiments/exp_kf2_be1_fp32_n8192.py preregs/2026-05-29_kf2_be1_n8192.md 21600
bash tools/orchestrator/queue_add.sh overnight_queue kf2_be1_fp16_n8192 experiments/exp_kf2_be1_fp16_n8192.py preregs/2026-05-29_kf2_be1_n8192.md 21600
bash tools/orchestrator/queue_add.sh overnight_queue kf2_be1_int8_n8192 experiments/exp_kf2_be1_int8_n8192.py preregs/2026-05-29_kf2_be1_n8192.md 21600
bash tools/orchestrator/queue_add.sh overnight_queue kf2_be1_int4_n8192 experiments/exp_kf2_be1_int4_n8192.py preregs/2026-05-29_kf2_be1_n8192.md 21600
bash tools/orchestrator/queue_add.sh overnight_queue kf2_be1_int2_n8192 experiments/exp_kf2_be1_int2_n8192.py preregs/2026-05-29_kf2_be1_n8192.md 21600
bash tools/orchestrator/queue_add.sh overnight_queue kf2_be1_int1_n8192 experiments/exp_kf2_be1_int1_n8192.py preregs/2026-05-29_kf2_be1_n8192.md 21600
# Phase region anchors
bash tools/orchestrator/queue_add.sh overnight_queue region_c_kf1_n4096_beta64_mfrac4 experiments/exp_region_c_kf1_n4096_beta64_mfrac4.py preregs/2026-05-29_phase_region_cd_n4096.md 14400
bash tools/orchestrator/queue_add.sh overnight_queue region_c_kf2_n4096_beta64_mfrac4 experiments/exp_region_c_kf2_n4096_beta64_mfrac4.py preregs/2026-05-29_phase_region_cd_n4096.md 14400
bash tools/orchestrator/queue_add.sh overnight_queue region_d_kf1_n4096_beta64_mfrac12 experiments/exp_region_d_kf1_n4096_beta64_mfrac12.py preregs/2026-05-29_phase_region_cd_n4096.md 14400
bash tools/orchestrator/queue_add.sh overnight_queue region_d_kf2_n4096_beta64_mfrac12 experiments/exp_region_d_kf2_n4096_beta64_mfrac12.py preregs/2026-05-29_phase_region_cd_n4096.md 14400
```

## Smoke Gate Results (all passed)

BE-1 smokes (N=1024, 1 seed):
- fp32: iso=0.01010, wall=0.28s PASS
- int8: iso=0.02020, wall=0.25s PASS
- int1: iso=0.00000, wall=0.24s PASS (binary W; iso=0 expected at small N)

Phase region smokes (N=1024, 1 seed):
- region_C kf1: retention=1.00000, wall=0.17s PASS
- region_D kf1: retention=0.30245, wall=0.43s PASS (overcapacity suppression visible)
- 4x scale: ret_C_4x=1.0, ret_D_4x=0.334 PASS

## TCFT/Saad-Solla Blocker

See notes/exp_dev_to_strategy_phase_cd_tcft_ss_blocker_2026-05-29.md.
These variants require retrofitting Hopfield retrieval beta into TCFT (2-4h engineering; Tier-2).
