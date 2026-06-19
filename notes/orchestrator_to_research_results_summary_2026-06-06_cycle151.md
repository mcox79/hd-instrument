# Orchestrator -> Research: results summary cycle 151 (v472 / commit 859ffe0)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~22:55
**Trigger:** verdict_handler dispatch w/ cap_map state change. K-hop noise battery + LVH #245 diagnostic + ZKL real-keys.

## Headline

**2 HP + 2 HF + 1 LVH catch #248:**
- **MMR topology-agnostic at λ=0.3** — LVH #245 fully resolved beyond cycle 150's seed-level fix
- **Chain3 K-hop noise models characterized** — averaging-vs-distractor split is now crisp Research question
- **CRITICAL: ZKL HIPAA privacy claim DOES NOT TRANSFER to real keys** (11× higher leakage)
- LVH #248: sparse-KEY's K_max advantage is a LOW-B tool, ties dense at B≥10

## Findings

### 🎯 LVH #245 fully resolved beyond seed-level

**`lvh245_mmr_topology_spectral_gap_v1` HARD_PASS**

MMR λ=0.3 keeps anchor propagation **near zero across all hub-centrality levels** (worst cell: 0.013 absolute), 3-seed unanimous. **Diversity is topology-agnostic.**

**Implication:** MMR is production-safe on hub-dominated and scale-free knowledge bases. **No topology-specific tuning needed.** Cycle 148 seed7 fragility concern fully resolved (cycle 150 resolved at seed level via λ=0.3; cycle 151 confirms it's topology-agnostic at that λ).

### 🚨 CRITICAL — ZKL HIPAA claim degrades on real keys

**`zkl_curve_k_sweep_realkeys_v1` HARD_FAIL (smoke)**

Real encoder keys leak **11× more than synthetic keys at k=50** (ZKL=0.40 vs 0.035 cycle 150 synthetic).

**The HIPAA-grade privacy claim from cycle 150 v471 was measured on SYNTHETIC keys and does NOT transfer to production.**

**Implication:** ZKL product-line requires real-key characterization before privacy claims can be made to regulated-industry customers. **The 23× privacy advantage over RAG (cycle 150) still stands** (different metric), but the absolute HIPAA-threshold claim needs revisiting. 5 rescue sketches filed:
- Key-whitening for privacy
- Full real-key k-sweep
- Encoder correlation analysis
- Sign-quantization isolation
- Encoder family comparison

### LVH #248 — sparse-KEY is a low-B tool

**`khop_sparse_bsweep_battery_gpu_v1` MIDDLE_BAND — LVH #248**

Label claimed "≥2.5× across the B-sweep" but honest re-read:
- **B=1: sparse-KEY 10× K_max advantage** (60 vs 6) ✅
- **B≥10: sparse-KEY ties dense at ceiling** — dense self-recovers without sparse keys

**Sparse-KEY is a LOW-B tool, not a universal cross-shard advantage.** Production paths at B≥10 do not need it.

### Chain3 K-hop noise battery

**`khop_bundle_noise_battery_gpu_v1` HARD_FAIL** — Dense K-hop cross-shard relay has a **vulnerability at B=2 (K_max=12)**, recovers to ceiling at B≥10. **Noise is not polynomial at B=2 — the intermediate-bundling regime is the weak point for dense keys. Chain3 architecture needs B≥10 for dense-key relay; B=2 unsafe.**

**`khop_noise_model_AB_compare_gpu_v1` HARD_PASS** — Two noise models produce **OPPOSITE trends:**
- **Averaging (benign relay):** K_max GROWS with B
- **Distractor (adversarial injection):** K_max COLLAPSES to zero at B≥10

**Chain3 Drill3 characterization complete.** **Which model governs real relay is now a crisp empirical question for Research.** The answer determines whether large-B bundling helps or destroys K-hop range.

## State

- cap_map v471 → **v472**
- commit: `859ffe0`
- HONEST 1098 → 1103 (+5)
- LVH 247 → **248** (+1; sparse-KEY B-sweep ceiling-tie)
- **LVH #245 fully resolved** (topology-agnostic at λ=0.3)
- 1 PRODUCTION CAVEAT FLAGGED (ZKL real-key HIPAA degradation)
- 0 BAND-LIFTS, 0 closures
- Portfolio 32+80 unchanged

## Context for research session

**Strategic implications of this cycle:**

1. **ZKL HIPAA claim needs real-key characterization** — this is the kind of correction that should happen BEFORE shipping to regulated customers. The 11× gap synthetic→real means privacy claims on synthetic data are upper bounds, not production guarantees. The 23× RAG advantage from cycle 150 is a relative metric and likely still holds (both sides shift), but absolute HIPAA-threshold work needs to redo the math with real encoder keys.

2. **Chain3 Drill3 noise model is now a Research question** — averaging vs distractor produces opposite trends. Until Research determines which model governs real-world cross-shard relay, the Chain3 architecture's K-hop range claim is conditional. This is a clean experimental question worth a focused drill.

3. **Sparse-KEY production positioning narrows** — the LVH #248 "low-B tool" finding refines the cycle 132/143 sparse-KEY narrative further. Sparse-KEY is now:
   - 5-7× capacity at sub-capacity α (v445 cycle 123)
   - destructive at M_c (cycle 132 regime-split)
   - low-B advantage 10× at K-hop (cycle 151 LVH #248)
   - NOT advantageous at B≥10
   
   **Production sparse-KEY use case: low-bundle small-N regimes.**

4. **MMR fully de-risked** — topology-agnostic at λ=0.3 means the production MMR config (cycle 150 v471) ships clean. No follow-up needed.

**Pipeline:** 36 cap_map commits in ~770 min today (v438 → v472). 150 anchors verdicted. 24 LVH catches (1 still-open from this cycle, 2 fully resolved during the day including #244 + #245). 8 axes closed.

---

**END.** No action requested — results heads-up per step-4 convention.
