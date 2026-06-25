# Pre-reg: substrate_cross_layer_compose_LM_v2_RESCUE_FULL

Date: 2026-06-24
Cell: experiments/exp_substrate_cross_layer_compose_LM_v2_RESCUE_FULL.py
Anchor: substrate_cross_layer_compose_LM_v2_RESCUE_FULL
Wave: C (production-scale confirmation of v2_RESCUE smoke HARD_PASS_CHAIN_GRADE_BONUS)
Routing: overnight_queue (GPU, marsh@home)
Timeout: 7200s
Seeds: [7, 17, 23] (3 for CV<=0.03 discriminator)

## Strategic context

v2_RESCUE smoke HARD_PASS_CHAIN_GRADE_BONUS at N_DIM=512 N_TRAIN=2000 V=300 synthetic-w2v
showed 2-layer INDEPENDENT BPC=5.03 vs 2-layer SHARED-W=5.30 -- separated-W BEATS shared-W
by 0.27 bits (the architectural prediction). Sanity rail FAILED at smoke (baseline 4.89 vs
production rail 7.04 -- expected since synthetic-encoder regime differs). Full-N text8
production needed to claim CHAIN-GRADE at proper scale.

The Wave-C smoke re-run at same anchor (re-validated 2026-06-24 with FULL prereg) reproduced:
- ARM_SINGLE_LAYER_CFRPE   BPC=4.893
- ARM_2_LAYER_INDEPENDENT  BPC=5.030 (LOAD-BEARING)
- ARM_3_LAYER_INDEPENDENT  BPC=5.058
- ARM_2_LAYER_SHARED_W     BPC=5.296
- shared_W_gap = 0.266 (>> 0.15 chain-grade threshold)

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
| OOV fallback | char-trigram bipolar |
| LAMBDA_GRID | [0.1, 0.3, 0.5, 0.7, 1.0] (excludes 0.0 per META C7) |
| TEMP_GRID | [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0] |

## Five arms (ONE knob = n_layers x shared_W)

1. ARM_UNIGRAM
2. ARM_SINGLE_LAYER_CFRPE (sanity rail; must reproduce fair-harness 7.30 +/-0.10)
3. ARM_2_LAYER_INDEPENDENT_CFRPE (LOAD-BEARING architectural prediction)
4. ARM_3_LAYER_INDEPENDENT_CFRPE (depth scan)
5. ARM_2_LAYER_SHARED_W_CFRPE (universal-biology-violation CONTROL)

## HARD bands (envelope-fail PASS + FAIL)

| tier | floor |
|-|-|
| HARD_PASS_CHAIN_GRADE | best_indep BPC <= 6.95 AND shared_w_gap >= 0.15 AND cv <= 0.03 |
| HARD_PASS | best_indep BPC <= 7.20 AND shared_w_gap >= 0.10 |
| MIDDLE_BAND | best_indep BPC in (7.20, 7.40) AND shared_w_gap > 0.05 |
| HARD_FAIL | best_indep BPC >= 7.40 OR shared_w_gap < 0.05 |
| READOUT_DEGENERATE | raw_bpc_at_T1_L1 within +/-0.5 of log2(V) |

## Sanity rails

- ARM_SINGLE_LAYER_CFRPE BPC within +/-0.10 of fair-harness 7.3065 (provenance check)
- ARM_2_LAYER_SHARED_W_CFRPE >= ARM_SINGLE_LAYER_CFRPE BPC (shared-W must not magically help)

## Disciplines

- D1 roofline probe (mandatory before FULL) -- refuses if extrapolated wall > 0.8 * timeout
- D2 atexit partial-flush + per-seed checkpoint (via experiments/_seed_checkpoint)
- Fix #14: spawn-budget honored (in-thread author)
- Fix #24: GPU dispatch via torch+cuda matmul (cf-RPE build_W_stack is matmul-bound)
- Fix #28: per-arm metrics primary; verdict_msg secondary
- ASCII-only

## Apples-to-apples

Cells 1 + 2 (Wave C) share word2vec sparse-bipolar f=0.05 encoder world -- both match the
fair-harness rail. Lane 1 (substrate-native; no transformer baseline).

## Cites

- experiments/exp_substrate_cross_layer_compose_LM_v2_RESCUE.py (rescue cell)
- data/exp_substrate_cross_layer_compose_LM_v2_RESCUE_smoke/metrics.json (smoke HARD_PASS)
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)
