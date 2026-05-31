# G6 Modern Hopfield Replication GPU v1 at N=8192

## Anchor
modern_hopfield_replication_gpu_v1_n8192

## Queue
overnight_queue (GPU)

## Script
experiments/exp_modern_hopfield_replication_gpu_v1_n8192.py

## Scientific question
T3 used BSC at N=16384 default beta. G6 tests at N=8192 with VARIED beta to see
whether Modern Hopfield activation is beta-robust or beta-specific.

## Pre-registered bands
- HARD_PASS: max_M_at_95_recall >= N at >= 2/4 beta values (beta-robust).
- HARD_FAIL: max_M_at_95_recall = N/4 across all beta (beta-specific).
- MIDDLE_BAND: otherwise.

## Config
- N = 8192 (PROT-018 _n8192)
- Beta sweep [1.0, 4.0, 16.0, 64.0]
- M sweep [N/4, N/2, N, 2N] = [2048, 4096, 8192, 16384]
- Codebook: BSC, C = 16384
- Seeds: [7, 17, 23]
- N_PROBE = 200; RECALL_THRESHOLD = 0.95
- Readout: softmax-attention with inverse-temperature beta:
  weights = softmax(beta * K @ q / N), out = weights @ V

## Self-test
- N_FULL == 8192
- Verdict gates HP/HF/MB exercised
- Live CPU smoke at N=1024 with beta in [4, 16]

## Timeout estimate
- smoke wall ~5s
- 4 beta * 4 M * 3 seeds = 48 cells; max M = 2N = 16384; modest matrix work
- scaling_exp = 2.0; estimate = ceil(1.5 * 5 * 8^2 * 3) = 1440s. Add margin
  for softmax + attention readout at 16384x16384.
- timeout_s = 21600 (user spec).

## Importance
HIGH - first beta-replication of T3 finding.
