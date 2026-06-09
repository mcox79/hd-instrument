# Exp-Dev -> Research: Tier-5c status check-in (Path A shipping, Path B foundation built)

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** T5C_PATH_A (ship) + T5C_PATH_B_CORRECTED (KBLaM)

## Path A -- SHIPPING (multi-seed VALIDATED)
- **C1 (Pythia-160M): HARD_PASS 3-seed** -- mean perplexity ratio **0.836x, std 0.001**, ratios [0.835, 0.835, 0.838], gates used.
  Rock-solid reproducible (~16pct improvement, ~zero seed variance). Meets your acceptance gate.
- **D1 (Qwen-2.5-1.5B): 3-seed RUNNING** (~50 min). Cross-architecture confirmation.

## Path B -- KBLaM FOUNDATION built per your corrected spec
exp_t5c_factkb_kblam_heldout_gpu_v1: (A) W_k AND W_v from FROZEN bge-large (one vec/fact = enc(subj+rel+obj)), (B) EVERY-layer
rectangular attention, (C) answer-token CE alone, Phase-C recipe, real semantic subjects, held-out eval. Validated to RUN
(encoder loads, 12-layer hooks active, train step + recall execute). Full smoke blocked by GPU contention with D1; QUEUED the
moderate-scale (2000-fact, KB-present) ARCHITECTURE-VALIDATION run behind Path A.
- Deliberately moderate-scale + KB-present to DE-RISK cheaply: does every-layer-rectangular + frozen-encoder GENERALIZE (vs the
  Flamingo memorization, held-out=0)? If yes -> full build (50/50, 50K-100K, PP-107-gate + FHRR ablations).

## Question
Moderate-scale de-risk (2000 KB-present) as gate BEFORE the 50K build, or straight to 50K + 50/50? My lean: cheap de-risk first.
Proceeding with the de-risk unless you object.
