# C3 Substrate State Compression v1 at N=4096

## Anchor
substrate_state_compression_v1_n4096

## Queue
remote_cpu_queue

## Script
experiments/exp_substrate_state_compression_v1_n4096.py

## Scientific question
Test 3 compression approaches on substrate W. Measure compression ratio AND
KF (killer feature) preservation AND retrieval accuracy.

## Pre-registered bands
- HARD_PASS: at least one config achieves >= 4x compression AND retrieval
  >= 95% AND all KFs pass (KF-1 deletion-cert + KF-2 drift-norm + KF-3 edit
  consistency).
- HARD_FAIL: all configs lose KFs (no config preserves any KF).
- MIDDLE_BAND: otherwise.

## Approaches
- A "low-rank SVD": ranks [N/8, N/4, N/2] = [512, 1024, 2048]
- B "sparse threshold": thresholds [0.01, 0.05, 0.1]
- C "quantization": INT4, INT8, INT16

## Killer features tested
- KF-1: deletion certificate (after rank-1 subtract, deleted target NOT returned)
- KF-2: drift / Frobenius norm preserved within 10%
- KF-3: edit consistency (rank-1 edit on compressed W yields NEW value)

## Config
- N = 4096 (PROT-018 _n4096)
- M = 2048
- N_PROBE = 100 retrieval queries
- Seeds: [7, 17, 23, 31, 41]

## Self-test
- Verdict gates HP/HF/MB exercised with corrected MB case
- Live CPU smoke at N=1024 M=128 n_probe=16

## Timeout estimate
- smoke wall ~3s
- 5 seeds * 9 configs; SVD is the heavy op (~30s at N=4096)
- scaling_exp = 1.5; estimate = ceil(1.5 * 3 * 4 * 5 * 9 / 1) ~ 800s
- timeout_s = 14400 (user spec).

## Importance
HIGH - production engineering for substrate state compaction.
