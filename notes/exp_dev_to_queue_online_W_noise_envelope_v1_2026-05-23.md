# Exp Dev -> Queue: wave14_online_W_noise_envelope_v1

**Filed**: 2026-05-23
**Routing trigger**: strategy_request_to_exp_dev_post_v158_pipeline_2026-05-23.md (Pick 1)

name=wave14_online_W_noise_envelope_v1 script=experiments/exp_wave14_online_W_noise_envelope_v1.py prereg=preregs/2026-05-23_wave14_online_W_noise_envelope_v1.md timeout=2400

## Smoke gate

PASSED. Smoke at N=1024 n_writes=10 n_seeds=1 noise_levels=[0.0, 0.10]:
- p_flip=0.00: mean_min_acc=1.000 PASS=True
- p_flip=0.10: mean_min_acc=1.000 PASS=True
- VERDICT: ONLINE_W_NOISE_ENVELOPE_FULL_PASS
- metrics.json produced: data/exp_wave14_online_W_noise_envelope_v1_smoke/metrics.json
- Self-test: 5/5 cases PASS
- Elapsed smoke: 0.2s

## FULL config

N=4096, n_writes=50, n_seeds=3, noise_levels=[0.0, 0.05, 0.10, 0.20, 0.30, 0.40]
Runner: CPU (local cpu_runner_local; remote cpu_runner_0 dead since 2026-05-21)
Estimated runtime: <30 min CPU

## Memory budget

- W: N x N float32 = 4096 x 4096 x 4 = 64 MB per seed (sequential on CPU)
- Total peak: ~64 MB. Well under any limit.

## Substrate-product axis

Cap 5 (Gap B Online W updates, Robbins-Monro+SNAP) noise-envelope expansion.
Analogous to Cap 1 and Cap 3 noise-envelope probes (v157/v158 PASS).
Output: noise-band map; informs whether GPU follow-up at N=8192/16384 is warranted.
