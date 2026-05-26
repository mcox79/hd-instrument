# Prereg — K4 Cross-modal binding (synthetic image embeddings)

**Anchor**: `wave14_k4_cross_modal_binding_v1`
**Queue**: overnight_queue (GPU)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

K4 KILLER Tier-2 untested. Substrate can bind text-concept atoms with
synthetic image embeddings projected into substrate N-dim space via fixed
random linear projection. If substrate cannot survive this synthetic-image
floor, no choice of real image encoder will rescue it.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: mean cross-modal recall cosine >= 0.50 AND lift over
  null-baseline (random N-d vectors) >= +0.15 across >=4 of 5 seeds.
  -> K4 ✅ at synthetic floor; image-encoder choice is the critical path.
- **HARD-FAIL**: mean cross-modal recall cosine < 0.20 OR lift over baseline
  < +0.05. -> K4 KILLER at substrate-binding level.
- **MIDDLE-BAND**: any intermediate; report bands.

## Parameters (exp_dev autonomy)

- N (substrate dim) = 4096 FULL / 512 smoke
- N_img_dim = 256 (stand-in image encoder dim)
- M pairs = 200 FULL / 40 smoke
- Seeds = {7, 17, 23, 31, 41} FULL

## ETA

GPU FULL ~10-30 min.

## Smoke outcome

Smoke at N=512 single-seed: cos=0.058 lift=0.060 -> HARD_FAIL borderline at
small N. M=200 at N=4096 may dramatically improve via N-scaling — FULL is
informative.
