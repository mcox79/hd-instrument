# Pre-reg: substrate_path_c_x_adaptive_cfrpe_3arm_v1

Date: 2026-06-24
Author: exp_dev (cell author)
Routing: overnight_queue (GPU; matmul-heavy; per Fix #24 GPU dispatch must actually use GPU)
Status: pre-registered, smoke-pending

## Hypothesis

Path C substrate-OWNED PC encoder + per-token adaptive cf-RPE matches or beats word2vec-borrowed encoder + per-token adaptive cf-RPE on text8 next-token BPC.

Two prior landings (both MIDDLE_BAND, full mode):
- word2vec + per-token adaptive cf-RPE: BPC=6.9920 (substrate_cfrpe_per_token_adaptive_lr_v1 MIDDLE_BAND, lift=0.3452 vs Hebbian baseline 7.3372)
- Substrate-OWNED PC encoder + Hebbian: BPC=7.6184 (path_c_substrate_owned_encoder_FAIR_HARNESS_v2 MIDDLE_BAND; lost to word2vec_sparse_bipolar 7.3065 on BPC by ~0.31)

Never tested: substrate-OWNED PC encoder x per-token adaptive cf-RPE. The PC encoder underperformed word2vec at BPC under simple Hebbian; per-token adaptive cf-RPE adds 0.34 bits when paired with word2vec. Does the combined system close the gap (substrate-OWNED encoder + best plasticity vs word2vec-borrowed encoder + best plasticity)?

## Arms (3 arms x 3 seeds, text8 N_TRAIN=100k V=4000 N_DIM=8192)

1. ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE
   - word2vec-google-news-300 projected to N_DIM=8192, sparse-bipolar f=0.05.
   - Per-token adaptive cf-RPE rule (median-normalized; clamp [0.25, 4.0]; LR=0.5; N_STEPS=5000; INGEST_BATCH=64).
   - Provenance rail: reproduce substrate_cfrpe_per_token_adaptive_lr_v1 BPC=6.9920 +/- 0.05.

2. ARM_PC_ENCODER_HEBBIAN_REFERENCE
   - Substrate-OWNED 3-layer Hebbian-PC encoder (Rao-Ballard local update; NO backprop; Tonegawa write-time competitive allocation at L3; PC_ALPHA=0.05 PC_BETA=2.0 PC_N_LAYERS=3 PC_N_PASSES=1 PC_TRAINING_TOKENS=100000), sparse-bipolar f=0.05 applied AFTER PC encoder.
   - Rank-1 Hebbian W (one-pass outer-product) for plasticity.
   - Provenance rail: reproduce path_c_substrate_owned_encoder_FAIR_HARNESS_v2 PC-arm BPC=7.6184 +/- 0.05.

3. ARM_PC_ENCODER_PER_TOKEN_CFRPE
   - PC encoder identical to arm 2 (substrate-OWNED 3-layer Hebbian-PC with Tonegawa).
   - sparse-bipolar f=0.05 applied AFTER PC encoder.
   - Per-token adaptive cf-RPE rule identical to arm 1 plasticity step.
   - THE materially-new science test.

All three arms share: text8 corpus, V=4000 vocab, N_TRAIN=100000, N_HELD=20000, N_DIM=8192, sparse-bipolar f=0.05, joint (T, lambda) sweep over TEMP_GRID=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0] and LAMBDA_GRID=[0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0] (C7-compliant; excludes 0.0), MRR_K=10. Per-arm sanity diagnostics: PC mechanism (S1-S4) for arms 2/3; per-token LR ratio stats for arms 1/3.

## Lane

LANE 1: substrate-native capability test. INTRA_LANE_DELTA varies ENCODER PARADIGM only (word2vec borrowed vs substrate-OWNED PC) given the SAME best plasticity (per-token adaptive cf-RPE) across arms 1 and 3. Arm 2 is provenance + ablation rail (encoder=PC, plasticity=Hebbian-only).

CONFOUND_AUDIT:
- Encoder paradigm (varies) — arm-1 vs arm-3 isolates this.
- Plasticity rule (held constant arm-1 vs arm-3 = per-token adaptive cf-RPE; ablated arm-2 vs arm-3 = Hebbian vs cf-RPE).
- Scale (held constant; same N_DIM, N_TRAIN, V across arms).

Single primary metric: BPC.
PRIMARY ARM: ARM_PC_ENCODER_PER_TOKEN_CFRPE.

## HARD pre-reg bands

Symmetric, locked before dispatch. Compared against PRIMARY ARM BPC mean across seeds.

PROVENANCE RAILS (sanity, NOT verdict-blocking on their own):
- ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE BPC within +/- 0.05 of 6.9920.
- ARM_PC_ENCODER_HEBBIAN_REFERENCE BPC within +/- 0.05 of 7.6184.

PRIMARY VERDICTS (Fix #28 — per-arm metrics, no cross-arm narratives):
- HARD_PASS_PATH_C_VIABLE: ARM_3_BPC <= ARM_2_BPC - 0.30 (per-token cf-RPE substantially helps PC encoder; >=0.30 lift).
- HARD_PASS_CLOSES_GAP: ARM_3_BPC <= 7.10 (PC encoder + per-token cf-RPE within 0.1 of word2vec + per-token cf-RPE ~6.99).
- HARD_PASS_BREAKS_GAP: ARM_3_BPC <= 7.00 (substrate-OWNED matches OR beats word2vec equivalent at the per-token cf-RPE setpoint). Chain-grade-bonus.
- MIDDLE_BAND: 7.10 < ARM_3_BPC < 7.50 (per-token cf-RPE adds something to PC encoder but doesn't close).
- HARD_FAIL: ARM_3_BPC >= 7.60 (PC encoder fundamentally limits cf-RPE benefit; the encoder is the bottleneck not the plasticity).

CV gate: ARM_3 bpc_cv across 3 seeds <= 0.10 OR verdict downgraded one tier.

Order of evaluation:
1. Provenance rails: if EITHER ref arm misses by > 0.05, flag PROVENANCE_DRIFT (verdict still computed but tagged).
2. CV gate.
3. PRIMARY band classification by ARM_3 BPC.

## Smoke gate (mandatory)

Before dispatch:
- `--self-test` exits 0 (unit instrumentation: PC forward shape/norm, Tonegawa excit evolves, per-token LR ordering OK, joint_sweep finite, C7 LAMBDA_GRID excludes 0.0, sparse-bipolar count exact, pre-reg band ordering well-formed).
- `--smoke` runs all 3 arms at N_TRAIN=2000 V=300 N_DIM=512 PC_TRAINING_TOKENS=1000 N_STEPS=200 SEEDS=[0] under ~180s, produces valid metrics.json with REQUIRED_FIELDS.

## Runtime estimate

Smoke wall ~120s on laptop CPU at N_DIM=512 V=300. FULL scale-up:
- N_DIM=512 -> 8192 (16x along matmul dim; PC training 1024-batch matmul scales O(D^2) -> 256x)
- N_TRAIN=2000 -> 100000 (50x along Hebbian/cf-RPE outer-loop)
- V=300 -> 4000 (~13x; mostly affects recall logits)
- seeds 1 -> 3

A clean upper-bound estimate via the formula: timeout_s = ceil(1.5 * 120 * (8192/512)^1.5 * (3/1)) where scaling_exp=1.5 (matmul-heavy with cf-RPE inner-loop).
  = ceil(1.5 * 120 * 64 * 3) = ceil(34560) = 34560s ~ 9.6h.

PROT-019 floor at _n>=8192 = 21600s (6h). Will dispatch at 21600s timeout. This matches Path C v2 actual wall (~2.5h GPU full per fair_harness_v2 landing) plus per-token cf-RPE adds ~20% per inner-loop step. Conservative.

Per Fix #24: cell uses torch.cuda. PROT-020 ROUTING-SANITY GATE should pass for overnight_queue.

## Apples-to-apples (master checklist)

- LANE 1 declared: substrate-native capability.
- CONFOUND_AUDIT: encoder paradigm vs cf-RPE rule vs scale (covered above).
- INTRA_LANE_DELTA: arm 1 -> arm 3 varies ENCODER only (one knob).
- Single primary metric: BPC.
- PRIMARY arm: ARM_PC_ENCODER_PER_TOKEN_CFRPE pre-registered.

## Disciplines

- ASCII-only.
- Fix #14 ONE cell.
- Fix #26 predispatch_check.py reports PROCEED (verified 2026-06-24).
- Fix #28 per-arm metrics (no cross-arm summary verdicts in verdict_msg).
- A5 path-scoped commit; never `git add -A`.
- C7: LAMBDA_GRID excludes 0.0 (anti-calibration-collapse).
- Per-seed checkpoint via `_seed_checkpoint`; atexit synthesizer for partial timeout.
- HDLAB_EXP_NAME-driven output dir.
- Self-test asserts mechanism + verdict bands well-formed BEFORE dispatch.

## Why this matters

Standing USER emphasis: Path C IS the substrate-product answer. The combination "substrate-OWNED encoding + best plasticity" has not been tested. Strong HARD_PASS_BREAKS_GAP validates the substrate-product narrative (best plasticity lifts the substrate encoder to match the borrowed encoder); HARD_FAIL or MIDDLE_BAND constrains where the encoder vs plasticity bottleneck sits.

## Cites

- experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py (PC encoder source)
- experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py (per-token adaptive cf-RPE source)
- data/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2/metrics.json (PC encoder BPC=7.6184 reference)
- data/exp_substrate_cfrpe_per_token_adaptive_lr_v1/metrics.json (per-token cf-RPE BPC=6.9920 reference)
- USER_2026-06-23_Path_C_substrate_owned_encoder_is_the_answer
- USER_2026-06-22_Fix24_GPU_must_use_GPU
- feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22.md
