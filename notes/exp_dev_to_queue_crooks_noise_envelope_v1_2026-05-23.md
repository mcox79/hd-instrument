# Exp Dev -> Queue: wave14_crooks_noise_envelope_v1

**Filed**: 2026-05-23
**Routing trigger**: strategy_request_to_exp_dev_crooks_noise_envelope_v1_2026-05-23.md

name=wave14_crooks_noise_envelope_v1 script=experiments/exp_wave14_crooks_noise_envelope_v1.py prereg=preregs/2026-05-23_wave14_crooks_noise_envelope_v1.md timeout=3600

## Smoke gate

PASSED. Smoke at N=4096 M_base=50 n_trials=10 seeds=[17] p in {0.0, 0.10}:
- p=0.0: delta_S_emp=0.0000 (clean baseline confirmed)
- p=0.10: delta_S_emp=0.2325 (within sanity band [0.0, 0.5])
- metrics.json produced: data/exp_wave14_crooks_noise_envelope_v1_smoke/metrics.json
- ASCII-only: PASS
- Self-test: 5/5 cases PASS

## FULL config

N=16384, M_base=200, n_trials=50, seeds=[17,18,19], noise_levels=[0.0, 0.05, 0.10, 0.20]
Estimated runtime: 30-60 GPU-min
Peak VRAM: ~1 GB estimated (well under 2 GB cap; under 8 GB VRAM budget)

## Substrate-product axis

Cap 1 verifiable forensic erase under bit-flip noise perturbation.
Probes whether the Crooks-FT erase bound (delta_S_emp < 0.05) holds when the substrate
is perturbed before the reverse (anti-Hebbian) step.
