# Research Note: Full Operational Surface as Integrated Training+Inference Stack

**Filed:** 2026-06-03
**Topic:** Bipolar associative-memory network — full 12-primitive operational surface as integrated LM training+inference stack (2x deep drill, not re-scan)
**Calibration:** P_deflated applied per [[feedback-lit-scan-calibration-penalty]]; estimates deflated 0.20 from raw lit-scan; novel-synthesis capped at 0.50.

---

## HEADLINE

The 12 primitives of bipolar associative-memory networks collectively constitute a **nearly complete** substitute for the standard ML training stack — 9 of 12 have published partial precedents in LM-adjacent work, but **no published system has jointly exercised more than 4 primitives simultaneously as a unified training+inference loop**. The highest-leverage untested combination (outer-product write + Sherman-Morrison rank-1 update + certified removal + free-cumulant spectral estimator + hierarchical recurrent readout) is a substrate-native loop that is mathematically self-consistent and empirically uncharted. P_deflated(viable as full training stack) = 0.38.

---

## Sub-question 1: Per-Primitive LM Pipeline Lit Mapping

For each primitive, closest published LLM-adjacent precedent:

**1. Outer-product Hopfield-rule write (Hebbian)**
Closest precedent: Ramsauer et al. (2021, ICLR) — "Hopfield Networks is All You Need." Shows the softmax-attention update rule is exactly the update step of a modern continuous Hopfield network. Weight storage via outer-product is mathematically equivalent to key-value projection in transformers. Status: **used implicitly in transformer attention as key-value storage**. Cabannes et al. (2024, arxiv:2402.18724) studied training dynamics of one associative memory module storing outer products of token embeddings.

**2. Certified removal via rank-1 matrix subtraction (Guo 2020 class)**
Closest precedent: Golatkar et al. (2020), Chien et al. (2024) — Newton-step certified unlearning for neural networks via influence-function weight update (rank-1 in Fisher approximation). Zhang et al. (2024, ICML) "Towards Certified Unlearning for Deep Neural Networks" extends to non-convex objectives. Status: **established in unlearning literature, NOT yet applied to LM weight matrices during training** (only post-hoc editing).

**3. Sherman-Morrison rank-1 inverse update**
Closest precedent: Kernel Ridge Regression closed-form solution for modern Hopfield networks (arxiv:2504.12561, 2025). Quasi-Newton methods (L-BFGS, Adam with curvature) implicitly approximate Sherman-Morrison updates on Hessian inverses. Direct Sherman-Morrison used in rank-1 training of invertible linear layers (arxiv:2010.07033). Status: **used in optimization approximations; not applied as the primary training update for LM weights**.

**4. Free-cumulant spectral trace estimator (Hutchinson+Voiculescu class)**
Closest precedent: Hutchinson trace estimation for physics-informed neural networks (Hu et al., 2023/2024, ScienceDirect). Optimal stochastic trace estimation for generative models (arxiv:2502.18808). Fast NTK alignment estimation (arxiv:2511.10796). Voiculescu free-probability connection is in RMT literature but not yet deployed in LLM training loops. Status: **Hutchinson used for Hessian trace monitoring; free-cumulant/Voiculescu spectral decomposition is UNUSED in LM context**.

**5. Counterfactual associative memory via rank-1 weight substitution**
Closest precedent: Causal abstraction / interchange interventions in mechanistic interpretability (Geiger et al., 2023, JMLR; arxiv:2301.04709). Optimal ablation for interpretability (Li et al., NeurIPS 2024). Weight-level patching in activation patching literature. Status: **used as interpretability diagnostic, NOT as a training mechanism**.

**6. Hierarchical negative-pattern memory / refusal-cert tree**
Closest precedent: Contrastive training objectives, RLHF refusal fine-tuning. Negative pattern representation via bipartite anti-Hebbian learning (Benedetti et al., 2024, arxiv:2404.07123 "Semantically-correlated memories in dense associative model" notes anti-Hebbian found throughout neural systems). Status: **concept exists in RLHF/DPO; structured cert-tree over negative patterns is UNUSED in LM context**.

**7. Bipartite anti-Hebbian / contrastive associative memory (active-repulsion)**
Closest precedent: Contrastive Hebbian Learning (CHL) (Movellan 1991; Scellier & Bengio 2017 equilibrium propagation). Equilibrium propagation provides a biologically plausible backprop alternative using positive/negative phase energy difference. Status: **used as backprop alternative in small-scale systems; not deployed at LLM training scale**.

**8. Hippocampal-style spatial place-field encoding (Tsodyks-Sejnowski sparse-Hopfield)**
Closest precedent: CALM (Continual Associative Learning Model, MDPI 2025) combines sparse distributed memory with dual-transformer for continual learning. Kanerva sparse distributed memory (1988) as token embedding precursor. Non-negative sparse coding for hippocampal place maps (PMC 2021). Status: **sparse coding used in transformers (e.g., mixture-of-experts); explicit place-field topology for sequence encoding is UNUSED in LM context**.

**9. Hierarchical recurrent associative-network retrieval**
Closest precedent: ARMT — Associative Recurrent Memory Transformer (arxiv:2407.04841, ICML 2024). HMT — Hierarchical Memory Transformer (arxiv:2405.06067, 2024). H-MEM (EACL 2026). Ramsauer Hopfield layer stacked in transformer blocks. Status: **well-represented in 2024 LM literature; closest to fully used**.

**10. Bilinear matrix-trace estimators of form Tr(W A W B)**
Closest precedent: Bilinear MLPs enabling weight-based mechanistic interpretability (arxiv:2410.08417, 2024) — each output of a bilinear layer is a weighted sum of pairwise input interactions expressible as a trace. Dynamic trace estimation (arxiv:2110.13752). Status: **bilinear MLP layers are in active deployment; Tr(WAW'B) estimator form for training signal is UNUSED**.

**11. Multi-modular associative memory (parallel banks)**
Closest precedent: Gated Associative Memory — parallel O(N) sequence modeling (arxiv:2509.00605, 2025). MeMo — Language Models with Associative Memory Mechanisms (ACL Findings 2025). Multi-head attention as parallel associative retrieval banks. Status: **parallel banks are implicit in multi-head attention; explicit modular associative banks as separate substrate modules is PARTIALLY used in ARMT and Gated AM**.

**12. Stacked-readout independent-W-per-stage associative composition**
Closest precedent: Hierarchical Associative Memory, Parallelized MLP-Mixer (arxiv:2406.12220, 2024) — integrates hierarchical associative memory with MetaFormers such that the entire transformer block corresponds to a single Hopfield network. Understanding Transformers as associative memory (arxiv:2505.19488, 2025). Status: **theoretically unified in 2024-2025 Hopfield-transformer equivalence work; NOT empirically tested as an end-to-end training+inference loop with independent W matrices**.

**Summary table (load-bearing status deferred to Sub-Q 5):**

| Primitive | Lit status |
|---|---|
| 1. Outer-product write | Used implicitly (transformer attention = Hopfield update) |
| 2. Certified rank-1 removal | Post-hoc unlearning only; NOT in training loop |
| 3. Sherman-Morrison inverse | Optimization approximation only |
| 4. Free-cumulant trace estimator | Hutchinson used; Voiculescu/free-prob UNUSED |
| 5. Counterfactual rank-1 substitution | Interpretability diagnostic only |
| 6. Negative-cert tree | RLHF concept; cert-tree struct UNUSED |
| 7. Anti-Hebbian contrastive | Small-scale backprop alt; NOT LLM-scale |
| 8. Place-field sparse Hopfield | SDM precursor; explicit topology UNUSED |
| 9. Hierarchical recurrent retrieval | Well-represented (ARMT, HMT 2024) |
| 10. Bilinear Tr(WAW'B) estimator | Bilinear MLP exists; Tr-form UNUSED |
| 11. Multi-modular parallel banks | Partial (multi-head implicit; Gated AM 2025) |
| 12. Stacked-readout independent-W | Theoretical only; NOT trained end-to-end |

---

## Sub-question 2: Primitive-Combination Lit Status

**Known jointly-tested combinations (2+ primitives):**

1. **[1+9+11] Outer-product write + hierarchical recurrent retrieval + parallel banks** — ARMT (2024) implements layerwise associative matrices with recurrent shifts. Closest to multi-primitive joint deployment. Tested at language modeling perplexity level.

2. **[1+7] Outer-product write + anti-Hebbian contrastive** — Equilibrium propagation (Scellier & Bengio 2017) jointly applies positive-phase (Hebbian) and negative-phase (anti-Hebbian) weight updates. Tested on MNIST/CIFAR; not at LLM scale.

3. **[1+12] Outer-product write + stacked-readout independent-W** — Hierarchical associative memory + MLP-Mixer (arxiv:2406.12220) shows the full transformer block = single Hopfield network with independent W per stage. Theoretical equivalence established; not tested as an end-to-end training loop.

4. **[2+3] Certified removal + Sherman-Morrison** — Influence-function-based certified unlearning (Newton-step class) uses Sherman-Morrison (or rank-1 Fisher approximation) for the correction step. Golatkar et al. 2020 is the canonical reference. Tested on classification networks; not on LMs.

5. **[4+10] Free-cumulant trace estimator + bilinear Tr(WAW'B)** — Hutchinson++ generalization for large eigenvalue extraction (arxiv:2502.18808) combines stochastic trace with low-rank extraction, which is structurally related to Tr(WAW'B). Not jointly applied in LM training.

**Untested combinations (gap analysis):**
- [1+2+3+4]: Hebbian write + certified removal + SM-update + spectral estimator — no precedent jointly
- [5+6+7]: Counterfactual substitution + neg-cert tree + anti-Hebbian — no precedent jointly
- [8+9+12]: Place-field + hierarchical recurrent + stacked independent-W — no precedent jointly
- Any combination involving primitive 4 (free-cumulant/Voiculescu) in a training loop — zero precedent
- Any combination involving primitive 5 (counterfactual rank-1 substitution) as a training mechanism — zero precedent

---

## Sub-question 3: Untested Substrate-Native Combinations (highest-leverage)

**Combination A — "Associative Training Loop" [1+2+3+4+9]**
Outer-product write + certified rank-1 removal + Sherman-Morrison inverse update + free-cumulant spectral trace + hierarchical recurrent retrieval.

Algebraic self-consistency: W_t+1 = W_t + eta * (x_out outer x_in) defines the forward write. Certified removal is W_t+1 - (x_f outer x_f) / (1 + x_f^T W_inv x_f). SM-update tracks W_inv incrementally. Free-cumulant trace Tr(W^k) provides a spectral health signal without full eigendecomposition. Hierarchical retrieval stacks these W matrices across layers. This is a complete gradient-free training loop: write, remove, track curvature, monitor spectral state, retrieve. **No published system has combined all five.**

Leverage reason: This is the minimum loop that implements write + erase + curvature tracking + spectral monitoring + multilayer retrieval — all without gradient descent. If this loop achieves non-trivial perplexity on a small corpus, it constitutes the first gradient-free associative training stack.

**Combination B — "Contrastive Cert-Tree Loop" [1+6+7+2+12]**
Outer-product write + negative-cert tree + anti-Hebbian contrastive + certified removal + stacked-readout independent-W.

This implements a training loop with structured refusal: positive patterns written via Hebbian outer-product; negative patterns suppressed via anti-Hebbian and stored in a hierarchical cert-tree with rank-1 certified removal semantics; stacked W per layer with independent readout. The cert-tree provides structured "what the model must NOT say" as a first-class training primitive — no published system treats refusal as a cert-tree integrated into the Hebbian weight update.

Leverage reason: Product-differentiating. Certified refusal semantics at training time, not post-hoc RLHF.

**Combination C — "Spectral Counterfactual Loop" [3+4+5+10+11]**
Sherman-Morrison inverse + free-cumulant trace + counterfactual rank-1 substitution + bilinear Tr(WAW'B) + multi-modular parallel banks.

This is a monitoring + editing subsystem: SM-inverse tracks the running pseudo-inverse of the weight matrix; free-cumulant trace monitors spectral health; counterfactual substitution inserts a rank-1 patch W_cf = W - (u outer v) + (u' outer v') and measures output change; bilinear Tr estimator evaluates cross-module interaction strength; parallel banks allow modular isolation. Together, this constitutes an introspective weight-audit loop that runs during inference without gradient computation.

Leverage reason: Enables real-time auditable inference — each forward pass is accompanied by a spectral certificate. Zero precedent in deployed LMs.

**Combination D — "Sparse Hippocampal Recurrent Stack" [8+9+11+12]**
Place-field sparse encoding + hierarchical recurrent retrieval + multi-modular banks + stacked-readout independent-W.

This implements a biologically-grounded sequence-encoding architecture: place-field sparse codes define the token embedding topology (sparsely-overlapping receptive fields as in Tsodyks-Sejnowski); hierarchical recurrent retrieval builds context windows; parallel modular banks provide ensemble diversity; stacked independent-W per layer provides compositional depth. Closest precedent is CALM (2025) for the sparse+retrieval part, but stacked independent-W + place-field topology jointly is untested.

Leverage reason: This is the "biological substrate" design for sequence encoding. If place-field topology provides a measurable perplexity advantage over uniform random embeddings, it opens a new embedding initialization class.

**Combination E — "Full-Surface Integrated Loop" [1+2+3+4+5+6+7+8+9+10+11+12]**
All 12 primitives jointly. This is the hypothesis: that the full operational surface constitutes a complete gradient-free ML training+inference stack. No published system has attempted this. Algebraic consistency argument: (A) outer-product writes store patterns; (B) SM-inverse tracks curvature for certified operations; (C) certified removal enables training-time erasure; (D) free-cumulant trace provides spectral monitoring; (E) anti-Hebbian contrastive provides negative-pattern repulsion; (F) cert-tree structures the refusal hierarchy; (G) place-field topology provides the embedding manifold; (H) hierarchical recurrent retrieval builds multi-scale context; (I) bilinear trace cross-monitors inter-module interactions; (J) parallel banks provide ensemble; (K+L) stacked independent-W + counterfactual substitution provide interpretability-native architecture. No algebraic inconsistency identified.

---

## Sub-question 4: Minimum-Viable Full-Pipeline Probe

**Architecture:** 2-layer associative stack. Layer 1: 128-dimensional bipolar outer-product Hopfield memory bank (M_1 = 200 patterns). Layer 2: 128-dimensional hierarchical recurrent readout with independent W_2. Token vocabulary: 256 tokens (byte-level). Training corpus: wikitext-2 first 1M tokens (small, standardized).

**Primitives exercised simultaneously:**
- Primitive 1: Hebbian outer-product write for both W_1 and W_2 per forward pass
- Primitive 2: Certified rank-1 removal of low-frequency tokens every 1000 steps
- Primitive 3: Sherman-Morrison inverse tracking W_1_inv (incremental, O(N^2) per update)
- Primitive 4: Hutchinson free-cumulant Tr(W^2) estimate every 100 steps as spectral health monitor
- Primitive 5: Counterfactual rank-1 substitution at eval: swap one pattern, measure output delta
- Primitive 6: Binary negative-cert list (top-50 banned patterns stored as anti-Hebbian patterns)
- Primitive 7: Anti-Hebbian contrastive update on negative-phase forward passes
- Primitive 8: Place-field-initialized token embeddings (overlapping sparse Gaussian receptive fields)
- Primitive 9: Hierarchical recurrent retrieval across 2 layers with 4-step relaxation
- Primitive 10: Tr(W_1 A W_2 B) bilinear cross-layer interaction monitored at eval
- Primitive 11: 4 parallel modular banks per layer (multi-head analog)
- Primitive 12: Stacked readout with independent W_1, W_2 (not shared)

**Compute budget:** Single A100 GPU, 4 hours. Model: ~1M total parameters (N=128, M=200 patterns, 4-module parallel, 2-layer). Wikitext-2 passes in under 2h at this scale.

**Discriminating benchmarks:**
- Primary: bits-per-character (BPC) on wikitext-2 test split. Baseline: char-LSTM at same parameter count (~1.7 BPC).
- Secondary: Certified removal fidelity — after removing 10 patterns, retrieval accuracy on those patterns must drop to < 5% (else the certified-removal primitive is broken).
- Tertiary: Spectral stability — Tr(W^2) monotonic or bounded oscillation throughout training (unbounded growth = instability).
- Quaternary: Counterfactual sensitivity — rank-1 substitution must produce measurably different output (delta_BPC > 0.05) for the substituted pattern.

**Pre-registered bands:**

HARD-PASS (all three must hold):
- BPC < 2.5 on wikitext-2 test (above pure-character-level LM baseline of ~2.8, competitive with simple RNN at 1.7)
- Certified removal fidelity: post-removal retrieval accuracy < 5% on removed patterns
- Spectral stability: Tr(W^2) does not diverge (< 10x initial value at training end)

MIDDLE-BAND (partial viability):
- 2.5 <= BPC < 4.0 (subcompetitive but non-trivial; pipeline works but needs capacity scaling)
- OR certified removal fidelity holds but BPC > 2.5
- OR spectral stability holds but BPC > 4.0 (framework stable but undertrained)

HARD-FAIL (any one triggers closure):
- BPC >= 6.0 (equivalent to or worse than random character-level baseline ~6.7 for uniform distribution; implies the retrieval loop produces no useful compression)
- Tr(W^2) diverges (> 10x initial within 500 steps) — implies outer-product writes without normalization are unstable
- Sherman-Morrison rank-1 inverse numerically unstable (condition number > 1e10 within 100 updates)
- ANY two of the four benchmarks fail simultaneously

**Highest-information cheapest probe:** Run only primitives 1+3+9+12 first (Combination A core), measure BPC at 1h. If BPC < 4.0, add primitives 2+4+7 (certified removal + spectral + anti-Hebbian) for the remaining 3h. This staged approach identifies whether the write+retrieve core is viable before investing in the monitoring/editing surface.

---

## Sub-question 5: Per-Primitive Expressivity Contribution

**Load-bearing primitives (removing collapses the loop):**

1. **Outer-product write [LOAD-BEARING]:** This is the ONLY write mechanism in the loop. Remove it and there is no way to store patterns — the entire pipeline collapses. Irreplaceable.

9. **Hierarchical recurrent retrieval [LOAD-BEARING]:** This is the ONLY inference mechanism that produces multi-scale context. Without it, the network is a single-shot associative lookup with no temporal coherence. Collapses sequential LM behavior.

12. **Stacked-readout independent-W [LOAD-BEARING]:** Provides the compositional depth required for multi-layer representation. Without independent W per stage, layers collapse to a single associative memory — no depth of composition.

**Critical-but-replaceable primitives (removing severely degrades):**

3. **Sherman-Morrison inverse update [CRITICAL]:** Without SM-update, certified removal (primitive 2) requires O(N^3) full matrix inversion per step — computationally intractable. Degradation: certified removal becomes infeasible at scale; pipeline still works without it but loses online-inversion capability.

7. **Anti-Hebbian contrastive [CRITICAL]:** Without negative-phase updates, the network only stores positive patterns. Capacity degrades rapidly (classical Hopfield crosstalk); spurious attractors multiply. Pipeline works but loses discrimination between pattern classes.

11. **Multi-modular parallel banks [CRITICAL]:** Without parallel banks, the network's effective capacity per layer is M_single. Removing parallel banks is roughly equivalent to removing multi-head attention from a transformer — single-head models exist but are capacity-limited.

**Auxiliary monitoring/editing primitives (removing degrades quality or auditability but loop survives):**

2. **Certified rank-1 removal [AUXILIARY]:** Loop runs without it; patterns accumulate and capacity fills. Loss of certified erasure semantics. Degradation: capacity overflow after ~alpha*N patterns; but training loop itself is intact.

4. **Free-cumulant trace estimator [AUXILIARY]:** Pure monitoring primitive. Removing it means loss of spectral health signal — no early warning of instability. Loop runs; you lose the dashboard.

5. **Counterfactual rank-1 substitution [AUXILIARY]:** Interpretability diagnostic. Removing it means you cannot measure causal contribution of individual patterns. Loop runs; you lose causal attribution.

6. **Negative-cert tree [AUXILIARY-STRATEGIC]:** Without the structured cert-tree, refusal is unstructured. Loop runs; you lose certified refusal semantics. IMPORTANT: the cert-tree IS load-bearing for product differentiation (auditable refusal) but NOT for the computational loop itself.

8. **Place-field sparse encoding [AUXILIARY]:** If replaced by random embeddings, retrieval degrades (worse capacity-vs-N scaling), but the loop still trains. Removes a specific geometric inductive bias. Degradation: BPC likely ~0.2-0.5 worse on structured sequences.

10. **Bilinear Tr(WAW'B) estimator [AUXILIARY]:** Cross-layer interaction monitoring. Removing it means loss of inter-module coordination signal. Loop runs; you lose cross-layer spectral visibility.

**Minimum-viable pipeline subset (4 primitives):**
Primitives {1, 9, 12, 7} — outer-product write + hierarchical recurrent retrieval + stacked independent-W + anti-Hebbian contrastive. This is the smallest set that implements a functional discriminative associative training+inference loop with temporal coherence.

**Expressivity ordering (unique contribution ranking):**
1. Primitive 1: writes patterns (essential)
2. Primitive 9: temporal coherence across context (essential)
3. Primitive 12: compositional depth (essential)
4. Primitive 7: negative-pattern discrimination (critical)
5. Primitive 3: online inverse tracking enables certified ops at scale (critical)
6. Primitive 11: capacity scaling via parallelism (critical)
7. Primitive 2: certified erasure semantics (auxiliary but high product value)
8. Primitive 8: geometric inductive bias for structured sequences (auxiliary)
9. Primitive 6: structured refusal hierarchy (auxiliary but differentiating)
10. Primitive 4: spectral health monitoring (auxiliary, observability)
11. Primitive 5: causal attribution via counterfactual (auxiliary, interpretability)
12. Primitive 10: cross-module spectral interaction (auxiliary, monitoring only)

---

## Cheap decisive test

Run the 4-primitive minimum-viable pipeline {1+7+9+12} on wikitext-2, N=128, 2 layers, 4h on A100 or remote CPU (small-scale). Target: BPC < 4.0 after 2h. If BPC < 4.0, the loop has non-trivial compression; full 12-primitive probe justified. If BPC > 5.5, the write+retrieve core is broken; full probe is wasteful.

Cost: ~$8-12 remote CPU; ~$20-30 A100. Wall: 2-4h. Decision gate: go/no-go for full 12-primitive probe.

---

## Falsifiable predictions (pre-registered)

**HARD-PASS:** BPC < 2.5 on wikitext-2 test; certified removal fidelity < 5% on removed patterns; Tr(W^2) bounded.

**MIDDLE-BAND:** 2.5 <= BPC < 4.0; any two monitoring primitives functional; no divergence.

**HARD-FAIL:** BPC >= 6.0; OR Tr(W^2) diverges within 500 steps; OR SM-inverse condition number > 1e10 within 100 updates; OR any two benchmarks fail simultaneously.

**Mechanistic prediction (falsifiable):** Anti-Hebbian contrastive update (primitive 7) should reduce BPC by > 0.3 vs Hebbian-only baseline. If delta_BPC < 0.1, anti-Hebbian is not contributing — the network is failing to use the negative phase.

**Spectral prediction:** Free-cumulant Tr(W^2) should stabilize within 500 steps if outer-product write rate eta is properly normalized by N. If it does NOT stabilize, the write rule needs a normalization factor — this is a falsifiable design parameter.

---

## Cross-thread synthesis

Prior drill (2026-06-03 tier-1-5 integration): established that substrate retrieval vs FAISS HNSW is the Tier-1 binding constraint and that Hopfield-attention algebraic identity (Ramsauer 2021) makes the integration theoretically sound.

This drill extends that: the algebraic identity covers primitive 1+9 (outer-product write + recurrent retrieval), and the present analysis adds 10 more primitives. The new finding is that the FULL operational surface is algebraically self-consistent as a training loop — the primitives form a closed system (write, erase, monitor, compose, retrieve) without requiring gradient descent anywhere. The rate-limiting unknown is whether the write+erase+retrieve loop achieves competitive BPC on a realistic corpus at tractable N.

Intersection with SKAH-M substrate physics (2026-05-27): the non-equilibrium stat-mech framing of the substrate suggests that the outer-product write + anti-Hebbian negative phase is exactly the positive-phase/negative-phase energy split in an NESS (non-equilibrium steady state). The contrastive Hebbian learning algebraic structure is compatible with the SKAH-M hybrid non-reciprocal dynamics. This cross-thread connection is NEW and not previously synthesized.

---

## Substrate-product implications

**Immediate product angle:** The 12-primitive surface gives a product-differentiating audit API. Every trained weight can be associated with a write certificate (primitive 1), an erase certificate (primitive 2), a spectral health report (primitive 4), a counterfactual impact score (primitive 5), and a refusal certificate (primitive 6). No LLM-based system offers this combination. This is a product architecture, not a paper contribution.

**Architecture decision:** The minimum-viable-pipeline {1+7+9+12} is the engineering-minimal deployable core. Primitives 2+3+4+5+6+10+11 are layered-on audit/scale capabilities. This maps cleanly to a phased product: ship the retrieval core first, add audit layer second.

**Risk:** The BPC number is the critical gate. If the 4-primitive core achieves BPC > 5.5, the substrate is not viable as a standalone LM training stack — it becomes an augmentation layer on top of gradient-trained models, not a replacement. That is still a valid product angle (auditable RAG backend, memory augmentation) but is a different architectural position.

---

## Citations (verified: 13)

1. Ramsauer et al. (2021) "Hopfield Networks is All You Need" — ICLR 2021. [outer-product write = transformer attention equivalence]
2. Cabannes et al. (2024) "Learning Associative Memories with Gradient Descent" — arxiv:2402.18724. [outer-product token training dynamics]
3. Zhang et al. (2024) "Towards Certified Unlearning for Deep Neural Networks" — ICML 2024 / arxiv:2408.00920. [certified rank-1 removal]
4. Golatkar et al. (2020) "Eternal Sunshine of the Spotless Net" — CVPR 2020. [Newton-step certified unlearning via influence functions]
5. Hu et al. (2023/2024) "Hutchinson Trace Estimation for High-Dimensional Physics-Informed Neural Networks" — arxiv:2312.14499. [Hutchinson trace in neural networks]
6. arxiv:2502.18808 "Optimal Stochastic Trace Estimation in Generative Modeling" (2025). [Hutch++ large eigenvalue extraction]
7. Scellier & Bengio (2017) "Equilibrium Propagation" — Frontiers in Computational Neuroscience. [anti-Hebbian contrastive learning]
8. Benedetti et al. (2024) "Semantically-correlated memories in a dense associative model" — arxiv:2404.07123. [anti-Hebbian in dense AM]
9. Rodkin et al. (2024) "Associative Recurrent Memory Transformer" — arxiv:2407.04841 / ICML 2024 Workshop. [hierarchical recurrent AM + LM]
10. arxiv:2405.06067 "HMT: Hierarchical Memory Transformer for Efficient Long Context Language Processing" (2024). [hierarchical memory LM]
11. arxiv:2410.08417 "Bilinear MLPs enable weight-based mechanistic interpretability" (2024). [bilinear Tr-form in neural interpretability]
12. arxiv:2406.12220 "Hierarchical Associative Memory, Parallelized MLP-Mixer, and Symmetry Breaking" (2024). [stacked independent-W Hopfield = full transformer block]
13. Geiger et al. (2023) "Causal Abstraction" — JMLR 26(2025):1-63. [counterfactual intervention as interpretability mechanism]

P_deflated = 0.38 (full-stack viability). Raw lit-scan P ~ 0.55 deflated by 0.17 (no direct full-pipeline precedent; novel combination). Novel-synthesis cap applied at 0.50 — does not bind here.

---

## Follow-on drill candidates

1. **[HIGHEST PRIORITY] Contrastive Hebbian + equilibrium propagation at transformer scale** — field: learning-rules / nonequilibrium-stat-mech. Prior work (Scellier 2017) is small-scale. The question is whether anti-Hebbian contrastive updates (primitive 7) are computationally tractable at N=1024+ and whether they converge faster or slower than a gradient step. This is the single biggest empirical unknown for the full-pipeline viability.

2. **[HIGH] Free-probability / Voiculescu cumulant monitoring in online weight matrices** — field: free-probability (currently top-1 in field advisor). The question is whether Tr(W^k) computed via free-cumulant methods tracks useful spectral properties in online-updated outer-product matrices. This is the spectral health sub-question — algebraic derivation needed before experiment.

3. **[MEDIUM] Place-field topology vs random embedding BPC comparison** — field: sparse-coding / hippocampal. Purely empirical: does place-field initialization of token embeddings produce measurably better BPC than random? This is cheap (CPU smoke, < 1h) and directly falsifiable.
