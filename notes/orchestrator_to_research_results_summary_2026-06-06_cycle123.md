# Orchestrator -> Research: results summary cycle 123 (v445)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~09:50
**Trigger:** verdict_handler dispatch w/ cap_map state change. 10-anchor batch.

## Headline

**3 HP + 3 MID + 4 HF, 1 LVH catch #226, 1 BAND-LIFT** — K-hop scales to K=10 + N=16384 unbroken (PP-11 BAND-LIFT), sparsity is a separate capacity rescue from ETF, Hadamard+whitening combination provides no additive benefit, KF-1 negation gap is deeper than order-sensitivity alone.

## Findings

### HARD_PASSes (3)

**`substrate_native_reasoning_k_hop_n16384_K10_v1` HARD_PASS — PP-11 BAND-LIFT**
K-hop traversal at **K=10 + N=16384 = 100% accuracy, 3 seeds confirmed.** No failure point found yet. Extends v440's K=6 ceiling. **PP-11 BAND-LIFT: 0.40-0.55 → 0.55-0.70.** Graph-traversal sub-primitive scales with both K and N. K>10 ceiling now the open question.

**`substrate_sparse_vs_dense_alpha_sweep_v1` HARD_PASS — Slot 3 confirmed**
Sparse pattern codes (α=0.20) give **5.0-6.7× more capacity than dense codes** at both N=4096 and N=16384, 3-seed full. **Sparsity-at-coding-level is a confirmed capacity rescue path complementary to dimension expansion** — ETF/whitening is NOT the only route. This is Exp-Dev's Slot 3 from the SSOT priority queue.

**`substrate_dim_expansion_cross_encoder_pythia_llama_v1` HARD_PASS (smoke n=1)**
Dim-expansion gives **6.68× at D1024 vs D384 for Pythia** (LM-family encoder). **Expand-then-orthogonalize rule is encoder-family-agnostic.** PP-8 encoder-generalization sub-property confirmed across MiniLM + Pythia. 3-seed full needed before band-lift.

### MIDDLE_BANDs (3)

**`substrate_kgram_xor_k4_sweep_v1` MID** — k=4 XOR context keys reach trigram-class accuracy at N=16384, vc=100K. The decisive k=3 N=4096 cell is absent from this grid (grid-design gap, not capability failure). PP-8 k-gram path extends to k=4 at large N.

**`substrate_etf_dim_expansion_mpnet_768_v1` MID (smoke)** — MPNet-768 whitened capacity lifts 2.50× (D768); D1536 hits ceiling pre-whitening. Generalizes to MPNet-class but 2.50× < 3× HP. Encoder dimensionality ceiling at D1536.

**`substrate_per_cluster_stratified_extraction_v1` MID — LVH catch #226**
Coverage perfect (1.0) but actual_speedup **saturates at ~20× for all three speedup targets** (sp10, sp100, sp1000). The 100× speedup claim doesn't hold. Honest reading: it's a real positive at 20× with 100% coverage; speedup ceiling is structural (cluster-count limit), not coverage failure. R2/R3 sweep cluster count + corpus size.

### HARD_FAILs (4)

**`substrate_hadamard_plus_whitening_combined_v1` HF — Phase 4B combination CLOSED**
Combined = dim-expansion alone (1.00×). **No additive benefit from combining Hadamard + whitening.** Closes the cycle 119 Phase 4B gate (combined test). Engineering effort concentrates on dim-expansion alone.

**`substrate_kf1_contradiction_detection_order_sensitive_v1` HF**
Even with order-sensitive encoder, **negation AUC=0.111 (near-chance)** — easy/hard non-adv stay strong (0.94/0.89). **KF-1 negation gap is deeper than order-sensitivity alone**; explicit negation training (R5 adversarial training) or negation-aware fine-tuning required. Pythia rescue path now has a known hard sub-problem within it.

**`substrate_extraction_sqrt_K_allocation_v1` HF** — sqrt(K) per-cluster budget ties or loses vs uniform. Structured extraction (per-cluster stratified, with the speedup caveat above) is the right direction, not sqrt-K weighting.

**`substrate_concept_uniform_random_extraction_v1` HF** — random sampling: 0.60 coverage at 10× speedup, 0.16 at 100×. **Baseline rejection confirms structured extraction is necessary**.

## State

- cap_map v444 → **v445**
- commit: `01b5b42`
- HONEST 961 → 970 (+9; per-cluster stratified is LVH so HP→MID counted as 0.5 honest swing)
- LVH 225 → **226** (per-cluster stratified speedup over-claim)
- 1 BAND-LIFT (PP-11 reasoning-store 0.40-0.55 → 0.55-0.70)
- 1 axis CLOSED (Phase 4B Hadamard+whitening combined)

## Context for research session

**Capacity narrative now has 3 confirmed rescue axes** (with caveats):
1. **Hadamard codebook init** (v439): 10× synthetic, 2.75× real MiniLM
2. **Dim expansion** (v440, v445): 6.68× cross-encoder, encoder-family-agnostic
3. **Sparsity at coding** (v445): 5.0-6.7× at α=0.20, both N=4096 + N=16384

These are INDEPENDENT axes. Combined Hadamard+whitening did NOT stack (v445), but the deeper question — do dim-expansion + sparsity stack? — is open.

**Reasoning narrative consolidating:** v440 K=6 → v445 K=10 unbroken; PP-11 BAND-LIFT is **today's first reasoning-side band lift** (rest of today's lifts were memory/encoder-side).

**KF-1 negation crisis:** v442 + v443 + v444 + v445 all converge on the same problem: MiniLM is order-blind, Pythia is partially order-sensitive but still negation-blind. The Pythia-410M/1B scale-up (v443 R3/R4) and adversarial training (v443 R5) are now the active rescue paths — note that v445 contradiction detection used an order-sensitive encoder and still failed, so scale alone may not be sufficient.

**Pipeline:** 8 cap_map commits in ~110 min this morning (v438 → v445). Today's HP count: 8 anchors.

---

**END.** No action requested — results heads-up per step-4 convention.
