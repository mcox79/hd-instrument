# Exp Dev -> Queue: wave14_streaming_noise_envelope_v1

**Filed**: 2026-05-23
**Routing trigger**: strategy_request_to_exp_dev_post_v157_envelope_expansion_2026-05-23.md

name=wave14_streaming_noise_envelope_v1 script=experiments/exp_wave14_streaming_noise_envelope_v1.py prereg=preregs/2026-05-23_wave14_streaming_noise_envelope_v1.md timeout=3600

## Smoke gate

PASSED. Smoke at N=2048 M=50 burn_in=10 steady=20 n_blocks=2 seeds=[17] p in {0.0, 0.10}:
- p=0.0: throughput_ratio=0.970 (clean baseline confirmed)
- p=0.10: throughput_ratio=0.881 (below threshold at small N; sanity band [0.0, 10.0] satisfied)
- metrics.json produced: data/exp_wave14_streaming_noise_envelope_v1_smoke/metrics.json
- ASCII-only: PASS
- Self-test: 5/5 cases PASS

## FULL config

N=16384, M=200, burn_in=100, steady=200, n_blocks=3, seeds=[17,18,19],
noise_levels=[0.0, 0.05, 0.10, 0.20]
Estimated runtime: 30-60 GPU-min
Peak VRAM: ~2.4 GB transient estimate (float32 W + bool mask + W_noisy; well under 8 GB hardware cap).
If smoke on GPU shows peak >3 GB: switch W to bfloat16 (reduces peak to ~1.34 GB) and re-smoke.

## Substrate-product axis

Cap 3 streaming inference (NESS drift-diffusion) under bit-flip noise perturbation.
Probes whether the cycle 173 STREAMING_CONTINUOUS_PASS throughput criterion holds when
the substrate is perturbed before each streaming step (noise applied per query, i.i.d.).
Symmetrical probe to cycle 177 Cap 1 noise-envelope (which returned KILL).
