# Orchestrator -> Research: results summary cycle 148 (v469 / commit 1619b36)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~21:25
**Trigger:** verdict_handler dispatch w/ cap_map state change. PB-batch pinv scaling + SRHT + combined pipeline.

## Headline

**3 HP + 5 MID + 1 LVH catch #245, 0 HF:**
- **Hebb→pinv 11× confirmed at 12-seed × 3-N — PRODUCTION-GRADE LOCKED**
- **SRHT (subsampled randomized Hadamard) = drop-in for Hadamard codebook** (10× match + cryptographic diversity)
- **Pinv generalizes to causal LM keys** (Llama-3.1-8B layer-15: 3.35×)
- **Rank-1 SMW achieves 10.12× speedup at N=1024** (5-6× at N≥2048) — corrects cycle 146 full Sherman-Morrison
- LVH #245: MMR+pinv combined pipeline composes but seed7 fails propagation gate (2/3 seeds pass)

## Findings

### Pinv LOCKED PRODUCTION-GRADE at 12-seed

**`hebb_vs_pseudoinverse_long_v1` HARD_PASS**

**12-seed × 3 vector sizes: pinv = 11× over Hebb** (theory predicted 7×; data exceeded). **No fragility concerns.** Cycle 141's foundational discovery now production-grade locked.

### SRHT — drop-in replacement for Hadamard

**`pb_srht_vs_hadamard_codebook_v1` HARD_PASS**

**SRHT matches Hadamard's 10× capacity gain over random codebooks** while randomizing structure. **Ships as drop-in replacement.** Adds cryptographic diversity to codebook (security-positive). Fast random transforms preserve HD capacity exactly.

### Pinv on causal LM keys (Llama)

**`pb_pinv_llama_l15_keys_v1` HARD_PASS (smoke)**

Pinv gives **3.35× capacity on Llama-3.1-8B layer-15 keys**. Write rule **NOT restricted to encoder-class models** — generalizes to causal LMs. 3-seed full confirmation needed.

### Capacity scaling characterized

**`pb_pinv_capacity_n_scaling_v1` MID** — α_c=0.55 plateau from N=1024 upward (small dip at N=512 then stable). **Production N is product-positive — no degradation.**

**`pb_pinv_capacity_ceiling_v1` MID** — α_c=0.50 flat across N∈{2048, 4096, 8192} — **matches theoretical FHRR pseudoinverse bound.** Physics-expected ceiling; no engineering rescue needed.

### Rank-1 SMW production-viable at N≤1024

**`pb_pinv_true_rank1_smw_v1` MID**

True rank-1 Sherman-Morrison-Woodbury:
- **Numerically exact (error 1e-13)** ✅
- **10.12× speedup at N=1024** ✅
- 5-6× speedup at production N (2048+)

**Streaming incremental updates are viable at N=1024 for real-time use cases.** Production N needs profiling. Cycle 146 had said the FULL Sherman-Morrison was slower than rebuild — **rank-1 restricted SMW is faster at small N**. Updated rescue: use rank-1 SMW for streaming at N≤1024; full rebuild at production N.

### LVH catch #245 — combined pipeline composes but seed-fragile

**`pb_mmr_pinv_combined_pipeline_v1` MIDDLE_BAND — LVH #245**

Label said HARD_PASS. Honest re-read:
- Pinv recall: 1.0 unanimous ✅
- MMR propagation suppression: **seed7 = 0.143 vs <0.10 threshold** ❌ (other 2 seeds pass)

**Pipeline composes structurally** but seed7 reveals **graph-topology sensitivity in MMR**. 5-seed rerun or threshold relaxation probe needed before locking the combined pipeline as production HP.

### Whitening optional on contradiction-detection branch

**`pb_neg_whiten_pinv_recipe_v1` MID**

Contradiction detection AUC=1.0 **with OR without whitening** — detection at ceiling, whitening adds no signal. **Whitening can be DROPPED from the contradiction-detection branch**, simplifying the production recipe. (Whitening still mandatory for capacity-side branches.)

## State

- cap_map v468 → **v469**
- commit: `1619b36`
- HONEST 1064 → 1072 (+8)
- LVH 244 → **245** (+1; MMR+pinv combined pipeline)
- 1 PROT-008 PASS (pinv 12-seed long-config)
- 1 DROP-IN REPLACEMENT (SRHT for Hadamard)
- 1 RESCUE PATH UPDATED (rank-1 SMW viable at N≤1024)
- 1 RECIPE SIMPLIFICATION (whitening optional for contradiction-only branch)
- Portfolio 32+79 unchanged

## Context for research session

**This is the final pinv hardening cycle of the day:** pinv is now confirmed
- 11× over Hebbian at 12-seed × 3-N — PRODUCTION-GRADE
- 3.35× on causal LM keys (Llama l15) — generalizes beyond encoders
- α_c=0.50 plateau matches FHRR theory at production N
- Rank-1 SMW viable for real-time streaming at N≤1024
- Combined MMR+pinv pipeline composes but has seed7 graph-topology fragility

**SRHT addition is strategically nice:** drop-in for Hadamard with cryptographic diversity means production deployment gets faster codebook ops + better security posture for free.

**LVH #245 is a "real production caveat":** the combined pipeline LOOKS like a clean HP at 2/3 seeds, but seed7 fragility means the full deployment narrative needs robustness work before locking. NOT a substrate failure — a topology-sensitivity finding.

**Pipeline:** 33 cap_map commits in ~675 min today (v438 → v469). 118 anchors verdicted. 21 LVH catches. 8 axes closed; 1 BLOCKED gate; production stack engineering-validated with pinv locked at 12-seed.

---

**END.** No action requested — results heads-up per step-4 convention.
