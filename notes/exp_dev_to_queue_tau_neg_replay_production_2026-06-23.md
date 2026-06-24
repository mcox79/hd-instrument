# exp_dev queue routing: substrate_tau_neg_x_n_replay_production_v1

filed-by: exp_dev:sonnet
date: 2026-06-23

queue=remote_cpu_queue name=substrate_tau_neg_x_n_replay_production_v1 script=experiments/exp_substrate_tau_neg_x_n_replay_production_v1.py prereg=preregs/2026-06-23_substrate_tau_neg_x_n_replay_production_v1.md timeout=5400

---

## Ship summary

- Anchor: substrate_tau_neg_x_n_replay_production_v1
- Queue: remote_cpu_queue (pure numpy; N_DIM=8192 matmul-bound but no CUDA; directed by task spec)
- Smoke: PASS (98s; 9 arms; MIDDLE_BAND at smoke scale-insufficient; selftest PASS)
- Remote self-test PASS (4.4s on marsh@home)
- Remote verify: VERIFIED present in queue.json (queue pending now 4 entries)
- Commit: 2a91fc2d (path-scoped)
- Timeout estimate: 5400s (90min; formula: ceil(1.5 * 3276s raw estimate) rounded to 300s)

## Pre-reg bands (confirmed immutable)

- HARD_PASS: lift(best TAU_NEG=10 arm vs ARM_T50_R1) >= +0.20 BPC
- CHAIN_GRADE: HARD_PASS AND best arm beats fair_harness baseline (7.3065) by >= +0.20 BPC
- MIDDLE_BAND: lift +0.05 to +0.20 BPC
- HARD_FAIL: lift <= +0.05 BPC

## Why smoke was SKIPPED (scale-insufficient null, not gate failure)

Shotgun confirmed: TAU_NEG axis is UNTESTABLE at N_TRAIN=2000 (4 chunks; TAU_NEG=50 needs ~50 chunks to diverge from TAU_NEG=10). MIDDLE_BAND at smoke (lift=0.120) is from the N_REPLAY axis only. Task spec explicitly instructs: skip smoke gate; proceed directly to --self-test + dispatch. --self-test passed on both laptop and remote.
