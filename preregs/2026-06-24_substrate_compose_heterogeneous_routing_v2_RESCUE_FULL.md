# Pre-reg: substrate_compose_heterogeneous_routing_v2_RESCUE_FULL

Date: 2026-06-24
Cell: experiments/exp_substrate_compose_heterogeneous_routing_v2_RESCUE_FULL.py
Anchor: substrate_compose_heterogeneous_routing_v2_RESCUE_FULL
Wave: C (production-scale confirmation of v2_RESCUE smoke HARD_PASS)
Routing: overnight_queue (GPU, marsh@home)
Timeout: 7200s
Seeds: [7, 17, 23]

## Strategic context

v2_RESCUE smoke HARD_PASS at N=1024 N_TRAIN=2000 V=300 showed:
- ARM_FREQ_ROUTED_K2 BPC=6.293 (lead arm)
- ARM_THETA_PHASE_TWO_W BPC=6.379
- ARM_ORTHOG_SUBSPACE BPC=6.391
- ARM_BASELINE_FAIR_HARNESS BPC=5.946 (smoke baseline; differs from production 7.30 rail)
- Freq differential: top1_high=0.577 vs top1_low=0.108 (diff=0.469) -- routing IS active

Sanity rail FAILED at smoke (baseline 5.95 vs rail 7.30) -- expected since synthetic-corpus
smoke regime differs from text8 production. Full-N text8 needed for production-scale ruling
of whether heterogeneous routing breaks the cf-RPE +12% cap at the proper scale.

## Production config

| param | value |
|-|-|
| N_DIM | 8192 |
| VOCAB_CAP | 4000 |
| N_TRAIN | 100_000 |
| N_HELD | 20_000 |
| N_STEPS | 1000 |
| SEEDS | [7, 17, 23] |
| encoder | word2vec-google-news-300 + sparse-bipolar f=0.05 |
| LAMBDA_GRID | [0.1, 0.3, 0.5, 0.7, 1.0] (excludes 0.0 per META C7) |
| TEMP_GRID | [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0] |

## Four arms (1 baseline + 3 heterogeneous-routing architectures)

1. ARM_BASELINE_FAIR_HARNESS -- sanity rail (cf-RPE Hebbian, no routing); must
   reproduce fair-harness 7.3065 +/-0.10
2. ARM_THETA_PHASE_TWO_W -- theta-gamma phase routing (W_enc vs W_ret)
3. ARM_FREQ_ROUTED_K2 -- frequency-routed (rank<=100 high-LR cf-RPE; rank>100 low-LR cf-RPE+STDP)
4. ARM_ORTHOG_SUBSPACE -- Gram-Schmidt orthogonal subspaces (cf-RPE on dim/2; STDP on other dim/2)

## HARD bands (envelope-fail PASS + FAIL)

| tier | floor |
|-|-|
| HARD_PASS_CHAIN_GRADE | best_het BPC <= 6.80 AND baseline_gap >= 0.20 AND cv <= 0.05 |
| HARD_PASS_CAP_BROKEN | best_het BPC <= 6.95 AND baseline_gap >= 0.15 |
| MIDDLE_BAND_PARTIAL | best_het BPC in [6.95, 7.05] |
| MIDDLE_BAND_INTER_GAP | best_het BPC in (7.05, 7.30) |
| HARD_FAIL_DECISIVE | all 3 het arms BPC >= 7.30 |
| HARD_FAIL_HURT | all 3 het arms BPC >= baseline + 0.05 (heterogeneous routing HURTS) |
| HARD_FAIL_PROVENANCE | BASELINE_FAIR_HARNESS BPC outside rail +/-0.10 |

## Sanity rails

- ARM_BASELINE_FAIR_HARNESS within +/-0.10 of fair-harness 7.3065 (HARD_FAIL_PROVENANCE)
- Per-arm discriminating-metrics:
  - THETA_PHASE: encoder/retrieval bank cross-corr < 0.95
  - FREQ_ROUTED: top1_high - top1_low > 0.05 (route IS discriminating)
  - ORTHOG: cross-subspace correlation < 0.70

## Disciplines

- D1 roofline probe (mandatory before FULL)
- D2 atexit partial-flush + per-seed checkpoint
- Fix #14: spawn-budget honored
- Fix #24: GPU dispatch via torch+cuda matmul
- Fix #28: per-arm metrics primary
- ASCII-only

## Apples-to-apples

Same encoder world as Cell 1 (word2vec sparse-bipolar f=0.05). Lane 1 substrate-native.

## Cites

- experiments/exp_substrate_compose_heterogeneous_routing_v2_RESCUE.py (rescue cell)
- data/exp_substrate_compose_heterogeneous_routing_v2_RESCUE_smoke/metrics.json (smoke HARD_PASS)
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)
