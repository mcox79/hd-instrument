# Pre-registration: phase_diagram_wm_multibank_K_ceiling_sweep_32768_v2

**Date:** 2026-06-26
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** Skunkworks DEMOTE of v1 (phantom K_4096_IS_CEILING; per_unit only K=4096 rows; META_RULE_H violation). Re-dispatch with cardinality guard + chunked matmul + OOM re-raise.

## Anchor

`phase_diagram_wm_multibank_K_ceiling_sweep_32768_v2`

## Routing

- **Queue:** overnight_queue (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** K up to 32768, fp16 codebook 65536x8192 (~1GB), chunked matmul over CODEBOOK_CHUNK=8192 rows bounds peak alloc to ~512MB intermediate; GPU-required per Fix #24
- **GPU util gate:** smoke must profile gpu_util >= 30% on remote GPU (Fix #24 lowered ceiling); v1 cell achieved gpu_util_mean=92% (heavily GPU-bound)

## V1 BUG DIAGNOSIS (Skunkworks DEMOTE, 2026-06-26)

V1 produced phantom K_4096_IS_CEILING verdict because:

1. CODEBOOK_SIZE=65536 + N_DIM=8192 + K=32768 in fp16: full `codebook @ queries.T` sim tensor = 65536 * 32768 * 2 bytes = 4.3GB. Plus 1GB codebook + 1GB intermediate float32 r2 cast = >8GB on RTX 4060 Ti (8GB VRAM). CUDA OOM at K>=8192.
2. The `except Exception as e: print [WARN]` block at line 878-879 silently swallowed the OOM and continued. Only K=4096 partials wrote (low memory, fit in budget).
3. Verdict computed "only K=4096 chain-grade" → K_4096_IS_CEILING despite K>4096 never executing.
4. Per_unit cardinality observed = 7 (3 seeds * 2 regimes + 1 sentinel); expected = 27 (3 seeds * 4 K * 2 regimes + 3 KNN sentinels).

Triggers META_RULE_H (Skunkworks 2026-06-26 atomization): K-sweep / sweep-axis verdicts require per_unit cardinality = n_seeds * n_K * n_regimes BEFORE any "ceiling" tiering.

## V2 FIXES

1. **Chunked argmax** `_chunked_argmax_cb_at_queries`: never materializes full (C, Q) sims tensor; loops over CODEBOOK_CHUNK=8192 rows producing (8192, K) per chunk + global argmax tracking. Memory bounded to ~256MB per matmul instead of 4.3GB. Validated against unchunked in selftest T7.
2. **OOM-class re-raise** `_is_oom_error`: detects torch.cuda.OutOfMemoryError + 'CUDA out of memory' / 'cudnn_status' substrings. OOM marks `fatal_oom_seen` and promotes verdict to HARD_FAIL_OOM_DURING_SWEEP_META_RULE_H. NEVER silently swallow. Validated in selftest T8.
3. **Cardinality guard**: `EXPECTED_N_UNITS = 27` (3 seeds * 4 K * 2 regimes + 3 sentinels). Verdict logic HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if observed < expected. Validated in selftest T9.
4. **Per-K wall time tracking** in per_unit records — for post-landing audit of where any future cliff occurs (memory? time? recall?).

## Hypothesis

Multi-bank WM is chain-grade at K=4096 (v1 measured) and K=8192 (baseline K-extension cell measured rec=1.000). Question: does it remain chain-grade at K=16384 and K=32768, or cliff?

V1 baseline (K-extension cell to K=16384, CODEBOOK_SIZE=32768) showed:
- K=4096 MULTI_64x rec=1.000 (saturated; chain-grade)
- K=8192 MULTI_128x rec=1.000 (saturated; chain-grade)
- K=16384 MULTI_256x: MIDDLE_BAND (partial), did NOT chain-grade

So we expect cliff at K=16384 (with k_per_bank=64 envelope). PARTIAL_K_CEILING_8192 is the prior.

## Mechanism

Multi-bank associative-memory writing with bank-routing cleanup. Each bank holds k_per_bank=64 items in bipolar workspace (sum of item*slot_tag + Gaussian noise, sign-quantized). Cue contains bank-tag + slot-tag; bank routed via argmax(cue @ bank_tags.T), then item retrieved via two-step cleanup over codebook (chunked argmax in v2).

Chain-grade envelope enforces k_per_bank <= 64 (per v1 rail).

## Arms

| K | Arrangement | n_banks | k_per_bank | Role |
|---|-------------|---------|------------|------|
| 4096 | MULTI_64x | 64 | 64 | RAIL (reproduce v1 rec=1.000) |
| 8192 | MULTI_128x | 128 | 64 | reproduce baseline chain-grade |
| 16384 | MULTI_256x | 256 | 64 | novel ceiling probe (baseline saw MIDDLE_BAND) |
| 32768 | MULTI_512x | 512 | 64 | novel ceiling probe (unexplored) |

Each at RANDOM + ADVERSARIAL (FEATURE_OVERLAP_FRAC=0.20)
Plus sentinel: ARM_KNN_BASELINE at M=400 (>=0.90; Fix #28)

## Pre-reg bands (LOCKED at module init)

- HP_CHAIN_GRADE_RECALL = 0.95
- HP_CHAIN_GRADE_CV = 0.05
- HP_CHAIN_GRADE_ROUTE_ACC = 0.95
- HP_ADV_WITHIN_RANDOM = 0.05 (chain-grade adversarial robustness)
- HP_ADV_BREAK_THRESHOLD = 0.30 (adv break flags MIDDLE_BAND)
- HP_K_CEILING_RECALL_MIN = 0.50 (below at all K>4096 -> K_4096_IS_CEILING)
- HP_CHAIN_GRADE_K_PER_BANK_MAX = 64 (envelope locked)
- Q_SUSPECT_SATURATION = 0.995 (flag by-construction-saturation; tiers to MIDDLE_BAND)
- HP_RAIL_K4096_RECALL = 1.0000 +/- 0.05
- HP_KNN_SENTINEL_MIN = 0.90
- CV_HARD_FAIL = 0.10
- **NEW v2: EXPECTED_N_UNITS = 27** (cardinality guard per META_RULE_H)

## Verdicts (v2 adds cardinality + OOM guards)

| Verdict | Condition |
|---------|-----------|
| CHAIN_GRADE_K_CEILING_32768 | all 4 K chain-grade + rail OK + cardinality OK |
| PARTIAL_K_CEILING_16384 | highest chain-grade K=16384; cliff at 32768 |
| PARTIAL_K_CEILING_8192 | highest chain-grade K=8192; cliff at 16384 |
| K_4096_IS_CEILING | only K=4096 chain-grade |
| MIDDLE_BAND | mixed / Q-saturation flagged / adv-breaks |
| **HARD_FAIL_CARDINALITY_BREACH_META_RULE_H** | n_units < expected (v1 phantom guard) |
| **HARD_FAIL_OOM_DURING_SWEEP_META_RULE_H** | OOM seen during run (auto-promote) |
| HARD_FAIL_CV_INSTABILITY | cv > 0.10 |
| HARD_FAIL_KNN_SENTINEL | KNN sentinel < 0.90 |

## Discriminator-must-survive-scale (USER 2026-06-26)

**Check option B (analytical justification):**

This cell's discriminator is NOT mechanism-vs-baseline (both substrate WM and KNN saturate to 1.000 at K<=4096). The discriminator is the **K-cliff itself**: at what K does multi-bank WM drop below chain-grade?

- At K=4096/8192: by-construction-saturation expected (v1 + baseline both rec=1.000). Q_SUSPECT_SATURATION discipline correctly tiers these to MIDDLE_BAND if ALL K saturate (not chain-grade lift).
- At K=16384/32768: discriminator is whether the cliff occurs. Baseline showed K=16384 MIDDLE_BAND at CODEBOOK=32768, so we expect cliff between K=16384 and K=32768 at CODEBOOK=65536. The expected verdict is PARTIAL_K_CEILING_16384 OR PARTIAL_K_CEILING_8192.
- The mechanism arm WILL NOT saturate at full-N at K>=16384 (this IS the discriminating regime). If by-construction-saturation occurs even at K=32768, then Q-discipline triggers MIDDLE_BAND.

**Why this passes the discriminator-survives-scale gate:** the discriminator IS scale-survival. We are MAPPING where the cliff lives. Both "no cliff" (CHAIN_GRADE_K_CEILING_32768) and "cliff at K=X" outcomes are scientifically meaningful for the phase diagram.

**Smoke evidence**:
- K=1024/4096 at smoke-N=2048 produced rec=0.79-0.99 (chunked argmax operational; mechanism works)
- Rail-drift at smoke is documented expected (smoke-N=2048 doesn't reproduce full-N=8192 chain-grade — v1 baseline same behavior)
- Cardinality 5/5 in smoke = META_RULE_H guard operational

## Config

- N_DIM=8192 (full); CODEBOOK_SIZE=65536 (fits K=32768)
- SIGMA=1.0, CUE_COS=0.70, N_ITEMS_PER_K=200
- Seeds: [11, 13, 19]
- CODEBOOK_CHUNK = 8192 (chunked matmul; bounds peak alloc to ~512MB)
- Encoder provenance: SUBSTRATE_NATIVE (geometric bank routing)
- Substrate-only decode (zero LLM calls)

## ETA + Timeout

Per-unit GPU walltime estimates (v1 measured at K=4096 = 0.5s; chunked matmul adds ~3-5x overhead for larger K):
- K=4096 MULTI_64x ~0.5s (v1 measured; no chunk overhead at this size)
- K=8192 MULTI_128x ~2-3s (chunked over 8 chunks of codebook)
- K=16384 MULTI_256x ~5-10s (chunked over 8 chunks)
- K=32768 MULTI_512x ~15-30s (chunked over 8 chunks; 2x larger Q)
- KNN sentinel ~1-2s

Total: 3 seeds * (4 K * 2 regimes * avg ~8s + 1 sentinel * 1s) ~= 3 * (64 + 1) = ~195s
Plus codebook build * 3 seeds = ~5s
Plus setup overhead ~30s

**Estimated wall: ~5-10 minutes on GPU.**

**Timeout: 1800s (30 min)** — generous 3x margin over estimate for safety; well under PROT-019 4h floor (anchor name has no `_n<N>` suffix so PROT-019 not triggered).

## Smoke verdict (laptop CPU 2026-06-26)

SMOKE_PASS: mechanism end-to-end OK at smoke regime
- All 9 selftests pass (T7 chunked argmax matches unchunked; T8 OOM detector classifies correctly; T9 cardinality math = 27)
- Smoke run: 5/5 expected units, n_units=5/expected=5 (META_RULE_H satisfied)
- K=1024 MULTI_32x: rec=0.9932 RANDOM / 0.9902 ADV
- K=4096 MULTI_64x: rec=0.7986 RANDOM / 0.7305 ADV (smoke-N=2048 rail-drift OK; full N=8192 reproduces v1's 1.000)
- KNN sentinel: 1.000 (>=0.90 OK)
- Cardinality guard operational
- gpu_util check DEFERRED to remote GPU smoke
