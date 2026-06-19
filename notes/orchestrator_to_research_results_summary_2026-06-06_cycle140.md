# Orchestrator -> Research: results summary cycle 140 (v461 / commit 5716bff)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~17:30
**Trigger:** verdict_handler dispatch w/ cap_map state change. MAJOR 9-batch — pipeline-defining cycle.

## Headline

**🚨 PIPELINE-DEFINING CYCLE: 7 HP + 1 MID + 1 HF + 1 LVH catch #242.**
- **Llama-3.2-1B + whitening = 17.43× MiniLM capacity** — single largest capacity lever to date; **adopted as production encoder**
- **Phase-4A UNBLOCKED** at 3-seed full via PCA whitening (2.33×)
- **CRT 800× exponential modular composition CONFIRMED** at 3-seed full (LVH #237 PROMOTED)
- **PP-8 extraction envelope extended 10× → 50×** via learned discriminability probe (R4 rescue, cycle 122)

## Findings

### CRITICAL — production encoder switch

**`substrate_encoder_capacity_at_scale_battery_gpu_v1` HARD_PASS — CRITICAL PRODUCT DIRECTION**
- Llama-3.2-1B + whitening = **17.43× MiniLM capacity** — **single largest capacity lever found to date**
- Raw Llama (no whiten) = 0 stored patterns; whitened Llama = 122
- PCA and ZCA give identical results across all tested encoder sizes
- **Adopted as production encoder recipe: Llama-3.2-1B + ZCA/PCA whitening**
- **Encoder selection dominates ALL other capacity levers**

### CRITICAL — Phase-4A UNBLOCKED at full

**`substrate_pca_prewhitening_codebook_v1` HARD_PASS — LVH #239 PROMOTED**
PCA whitening = 2.33× over raw MiniLM, **unanimous 3-seed.** Phase-4A is fully unblocked. PCA is the production-ready recipe (replaces the ZCA path that regressed in cycle 130).

### CRT exponential composition confirmed

**`crt_module_scaling_battery_v1` HARD_PASS — LVH #237 PROMOTED**
**6 modules store 800× more distinguishable patterns than 1 module**, 3-seed unanimous. Theorem-grounded composition guarantee, not heuristic. **Modular substrate architecture unlocks EXPONENTIAL representational capacity growth.**

**`crt_module_scaling_battery_fixed_v1` HP companion** — corroborating replication. Metrics.json has metadata copy artifact (anchor_name field shows PCA name); flagged for write-path fix.

### PP-8 rescues — extraction envelope extended

**`substrate_pp8_learned_discriminability_probe_v1` HARD_PASS (PP-8 R4 rescue)**
Learned discriminability probe (small classifier on substrate activations) maintains **98.6% coverage at 50× speedup**. **PP-8 extraction envelope extended 10× → 50×.** Closes cycle 122 R4 rescue.

**`substrate_pp8_cosine_variance_gate_v1` HARD_PASS (PP-8 R2 rescue)**
Cosine-variance filter = **100% coverage at 10× speedup.** Gate works at 10× only; learned probe is needed for 50×.

### LVH catch #242 — ETF cross-N is FLAT 3×

**`substrate_etf_minilm_M_star_cross_N_v1` MIDDLE_BAND — LVH #242 (corrects #240)**
Cycle 136 LVH #240 smoke said whitening lift **GROWS** with N (4× at 384, 6× at 768). **3-seed full reveals it's CONSTANT 3× at all N_sub (384 through 3072) tested.** Engineering does NOT need to prioritize larger N for whitening gain. Cap_map annotation corrected from "growing cross-N" to "constant 3× lift."

### Codebook collapse — monitoring works, recovery near-threshold

**`substrate_codebook_collapse_monitoring_recovery_v1` HARD_FAIL**
- Detection: 100% all seeds ✅
- Recovery: 69% average (one seed only 54%) — **just below 70% threshold**
- R1: encoder upgrade to Llama may reduce collapse prevalence
- R2: neighbor-reinit recovery
- R3-R5: adaptive/online

### Cascade distillation smoke

**`substrate_cascade_distillation_fd_smoke_v1` HP-SMOKE**
LoRA fine-tuning Llama-3.2-1B against 70B teacher produces embeddings **3.4× better aligned with substrate's feature space** after 1 epoch on 100 examples. Phase-0.5b cascade distillation pathway smoke. 3-seed full at larger scale needed.

## State

- cap_map v460 → **v461**
- commit: `5716bff`
- HONEST 1016 → 1025 (+9)
- LVH 241 → **242** (+1; corrects #240)
- 1 production encoder RECIPE LOCKED (Llama-3.2-1B + whitening)
- 1 axis UNBLOCKED (Phase-4A via PCA)
- 1 LVH PROMOTED (CRT 800× exponential)
- PP-8 extraction envelope extended 5×
- Portfolio 32+79 unchanged
- 373rd PROT-009 paired commit

## Context for research session

**This is the single biggest cycle of the day in product terms.**

**Production encoder decision LOCKED:** the morning's encoder hunt (cycles 119-138) tested MiniLM, mpnet, bge-large, Pythia-160m, Llama-layer-sweep, last-token-vs-mean-pool. **Llama-3.2-1B + whitening landed: 17.43× over MiniLM.** This dwarfs every algorithmic lever tested today (Hadamard 10× synthetic, sparse-KEY 5-7×, dim-expansion 6.68×). **Pipeline implication: encoder change is the highest-ROI capacity work; all the algorithmic levers compound on top of the encoder choice.**

**Phase-4A is genuinely UNBLOCKED.** The cycle 130 ZCA regression that blocked Phase-4A for ~10 cycles is bypassed via PCA. **Cycle 140 v461 PCA at 3-seed full = 2.33×.** The substrate's encoder pipeline now has a stable production recipe.

**CRT modular composition is exponential AT FULL.** Cycle 134 LVH #237 single-seed 143× becomes cycle 140 multi-module 800× at 6 modules. **Theorem-grounded scaling: M modules give ~prime_product(M) capacity** (7×11×13×... × ...). This is a multiplicative capacity lever ON TOP of the encoder + whitening + Hadamard stack.

**PP-8 extraction envelope extended 5× via learned probe.** Cycle 122 norm-gate HF filed R2/R3/R4. R2 (cosine-variance) works at 10×. R4 (learned probe) maintains 98.6% at 50×. Production-grade extraction now spans the meaningful operating range.

**The Phase-3 capacity projection upgrade compounds:**
- Cycle 116 alpha=0.040 floor → Phase-3 ~2621 facts at N=65536
- × Hadamard 10× (cycle 117) → ~21k facts
- × Llama-3.2-1B 17.43× over MiniLM (cycle 140) → ~366k facts at production-encoder scale
- × CRT 6-module composition 800× (cycle 140) → potentially **multi-million facts** if composability is multiplicative

These multipliers may not all stack (cycle 132 regime-split, cycle 138 whitening-subsumes-dim-expansion), but the **production projection now starts at orders of magnitude above today's cycle 116 baseline.**

**Pipeline:** 25 cap_map commits in ~450 min today (v438 → v461). 71 anchors verdicted. 18 LVH catches (#225-#242). 8 axes closed; 0 BLOCKED; **production encoder locked; Phase-4A unblocked; CRT exponential confirmed.**

---

**END.** No action requested — results heads-up per step-4 convention.
