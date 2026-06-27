# Pre-registration: phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1

**Date:** 2026-06-26
**Author:** exp_dev (Opus 4.7 1M)
**Trigger:** USER 2026-06-26 directive "what about phase diagram build out?" via Research routing-correction handoff.

## Anchor

`phase_diagram_wm_multibank_K_ceiling_sweep_32768_v1`

## Routing

- **Queue:** overnight_queue (GPU; remote_gpu via hdi_orchestrator)
- **Reason:** K up to 32768 + fp16 codebook 65536 x 8192 (~1GB) + batched matmul; GPU-required per Fix #24
- **GPU util gate:** smoke MUST profile gpu_util >= 50% on remote GPU; v1 cell achieved gpu_util_mean=52.6%

## Hypothesis

Prior cell `phase_diagram_working_memory_multibank_K_extension_to_16384_v1` landed MIDDLE_BAND with rec=1.000 cv=0.000 at K=4096/8192/16384 (by-construction-saturation prevented chain-grade tier; mechanism worked but couldn't discriminate). USER directive: extend to K in {8192, 16384, 32768} to find the absolute capacity ceiling.

**Question:** does multi-bank WM stay chain-grade at K=32768 (8x past chain-grade K=4096), or does it cliff?

## Mechanism

Multi-bank associative-memory writing with bank-routing cleanup. Each bank holds k_per_bank=64 items in a bipolar workspace (sum of item*slot_tag + Gaussian noise, sign-quantized). Cue contains bank-tag + slot-tag; bank is routed via argmax(cue @ bank_tags.T), then item retrieved via two-step cleanup over codebook.

Chain-grade envelope enforces k_per_bank <= 64 (per v1 cell's rail).

## Arms

| K | Arrangement | n_banks | k_per_bank | Role |
|---|-------------|---------|------------|------|
| 4096 | MULTI_64x | 64 | 64 | RAIL (reproduce v1 rec=1.000) |
| 8192 | MULTI_128x | 128 | 64 | novel ceiling probe |
| 16384 | MULTI_256x | 256 | 64 | novel ceiling probe |
| 32768 | MULTI_512x | 512 | 64 | novel ceiling probe |

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
- Q_SUSPECT_SATURATION = 0.995 (flag by-construction-saturation)
- HP_RAIL_K4096_RECALL = 1.0000 +/- 0.05 (v1 saturated at 1.000)
- HP_KNN_SENTINEL_MIN = 0.90
- CV_HARD_FAIL = 0.10

## Verdicts

| Verdict | Condition |
|---------|-----------|
| CHAIN_GRADE_K_CEILING_32768 | all 4 K chain-grade + rail OK |
| PARTIAL_K_CEILING_16384 | highest chain-grade K=16384; cliff at 32768 |
| PARTIAL_K_CEILING_8192 | highest chain-grade K=8192; cliff at 16384 |
| K_4096_IS_CEILING | only K=4096 chain-grade |
| MIDDLE_BAND | mixed / by-construction-saturated / adv-breaks |
| SANITY_BREACH | rail drift OR KNN sentinel breach |
| HARD_FAIL | substrate-only gate violated OR cv > 0.10 |

## Config

- N_DIM=8192 (full); CODEBOOK_SIZE=65536 (2x v1 to fit K=32768)
- SIGMA=1.0, CUE_COS=0.70, N_ITEMS_PER_K=200
- Seeds: [11, 13, 19]
- Encoder provenance: SUBSTRATE_NATIVE (geometric bank routing)
- Substrate-only decode

## ETA

Per-unit GPU walltime (v1 measured, 4060 Ti 8GB):
- K=4096 MULTI_64x ~0.5s
- K=16384 MULTI_256x ~3-5s
- K=32768 MULTI_512x ~8-12s (estimate; 2x K=16384)
- Total units: 3 seeds x (4 K * 2 regimes + 1 sentinel) = 27 units
- Estimated wall: ~5-8 minutes on GPU
- With smoke + setup overhead: timeout 1800s (30 min)

## Smoke verdict (laptop CPU 2026-06-26)

SMOKE_PASS: mechanism end-to-end OK
- K=1024 MULTI_32x: rec=0.9932 ra=1.0000 (random); rec=0.9902 (adversarial)
- K=4096 MULTI_64x: rec=0.7986 ra=1.0000 (random; smoke regime N=2048 doesn't reproduce full N=8192 chain-grade -- documented "rail_drift OK at smoke")
- KNN sentinel: 1.000 (>=0.90 OK)
- gpu_util check DEFERRED to remote GPU smoke
