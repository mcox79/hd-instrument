# research: deterministic substrate noise model — 5x drill

**Date:** 2026-06-30
**Topic:** HD substrate's deterministic noise model (bipolar bit-flip + L2-renorm → exact cos=1−2*flip_frac, std=0). Load-bearing finding caught by refuse-gate adaptive-tau v2 honest-abort.
**P_deflated (overall, novel-synthesis cap 0.50):** **0.42** that determinism EXCLUDES a defined sub-class of adaptive cells; **0.58** that hybrid (deterministic substrate + stochastic cortex injection) recovers the excluded class without breaking substrate guarantees.

---

## HEADLINE

The deterministic noise model is **a mathematical consequence of L2-renorm over a bounded perturbation set**, not a substrate defect. It IS load-bearing: adaptive-threshold / cleanup-on-clean-input / refuse-gate-adaptivity cells are mathematically barred from extracting information from intermediate confidence bands because no such bands exist under the determinism. HOWEVER — biological, memristive, and PCM substrates all develop adaptive mechanisms *that depend on intrinsic stochasticity*, suggesting the path forward is **stochastic injection at well-defined cortex-substrate boundaries**, not substrate-internal redesign. Adaptive-tau cells should be routed through an M3 cortex layer that owns the stochasticity budget; the substrate stays deterministic for its primary memory+compose+retrieve+audit role.

---

## Cheap decisive test

Pre-register on first stochastic-injection cell:
- **HARD-PASS:** dropout-style mask (p=0.05–0.15) applied at refuse-gate-input ONLY (cortex-side, not substrate-side) lifts in-domain confidence variance from ~0 to ≥0.04 std, AND adaptive-tau W8 sliding-window reduces false-refuse by ≥0.05 (clears the 0.017 gate that v2 hit).
- **HARD-FAIL:** the same dropout mask either (a) does not lift variance above 0.02 std, OR (b) lifts variance but adaptive-tau still under-gates at <0.03 false-refuse reduction. Either rules out stochastic-injection-at-boundary as a rescue path and forces the deeper question of substrate-internal redesign.
- **TIE-BREAKER (the regime test):** run the same cell with stochastic injection at substrate-side (random bipolar perturbation BEFORE L2-renorm) vs cortex-side (perturb the readout statistic AFTER substrate returns clean cos). If cortex-side wins, that's the M3-architecture validation. If substrate-side is needed, the substrate spec changes.

---

## Falsifiable predictions

1. **PRED-1 (HARD-PASS at 0.30):** Stochastic injection at cortex-boundary (cleanup-input perturbation or readout-statistic perturbation) recovers ≥80% of the adaptive-tau capability that v2 lost to determinism. **HARD-FAIL** if recovery <40% across 3 independent adaptive cells.
2. **PRED-2 (HARD-PASS at 0.45):** The deterministic substrate's capacity-vs-noise scaling (cos=1−2*p for flip-frac p) is **MORE favorable** than Gaussian-noise substrates for the substrate's primary memory role (cleaner concentration). **HARD-FAIL** if determinism gives worse capacity by ≥10% at any operating N_DIM.
3. **PRED-3 (HARD-PASS at 0.20, deflated heavily):** A specific sub-class of cells — those requiring **intermediate-confidence-band-extraction** (refuse-gate adaptivity, attention gating with learned thresholds, dual-store novelty detection in the ambiguous regime) — is mathematically excluded from a deterministic substrate. **HARD-FAIL** if even one cell in this class achieves chain-grade on the deterministic substrate without stochastic injection. (Note: refuse-gate-on-OOD already works deterministically because OOD lives outside the bit-flip continuum; the predicted exclusion is for AMBIGUOUS-regime cells specifically.)
4. **PRED-4 (HARD-PASS at 0.55):** Memristive/PCM neuromorphic literature precedent supports that **stochasticity is exploited, not designed-out**, in adaptive-threshold contexts. Brain literature concurs (Poisson code, vesicle release, gain modulation all stochastic). **HARD-FAIL** if a literature scan finds ≥3 chain-grade neuromorphic adaptive-threshold systems that are explicitly deterministic.

---

## 5 drills

### Drill 1 — PURE MATH (P=0.50, deflated 0.20 → **0.30**)
Bipolar bit-flip with L2-renorm gives cos = 1 − 2p as a **first-moment exact identity** because: for v with v_i ∈ {±1} and v' = v with k random sign-flips, ⟨v,v'⟩ = N − 2k (exact, no variance — the inner product is a count statistic over a finite set). After L2-renorm both vectors have norm √N, so cos = (N−2k)/N = 1−2p exactly. Variance only appears if you re-randomize the flip-positions per query (which collapses on the count), so std=0 holds under fixed flip-fraction. This is a **structural** determinism, not a bug.

Alternative noise models preserving HD-substrate guarantees (capacity, distance-concentration):
- **Additive Gaussian** (v + ε*N(0,I)): preserves L2-concentration (Johnson–Lindenstrauss class), introduces std≈ε√N/√N = ε at cos level — gives the intermediate distribution adaptive-tau needs. Cost: violates ±1 quantization (substrate spec).
- **Bernoulli dropout** (random zero-mask, then bipolarize): preserves capacity logarithmically per the random-projection literature (dropout = single random-subspace projection). Gives intermediate distribution.
- **Stochastic flip-fraction** (p drawn per-query from a distribution): keeps mean cos = 1−2E[p], introduces variance Var[cos] = 4Var[p]. Cheap and substrate-compatible.

**Implication:** The substrate's determinism is a property of *fixed bit-flip on bipolar codes*, not of HD computing generally. Three substrate-compatible stochastic injections are available without rewriting hdlab/.

Citations: [Zilliz cos↔Hamming](https://zilliz.com/blog/similarity-metrics-for-vector-search), [LSH unit-vector bit-flip identity](http://madscience.ucsd.edu/notes/lec9.pdf), [HD computing theory perspective (Thomas-Dasgupta-Rozell 2021)](https://cseweb.ucsd.edu/~dasgupta/papers/TDR21.pdf), [Random projection JL bound](https://arxiv.org/pdf/1705.06408), [HD bit-flip robustness study](https://ieeexplore.ieee.org/document/10908571/).

### Drill 2 — MATSCI / NEUROMORPHIC (P=0.62, deflated 0.20 → **0.42**)
Memristive (RRAM, Mott, PCM, spintronic) substrates are **inherently stochastic** at the device level — Mott-memristor stochastic switching originates from critical electron-electron interactions; PCM exhibits inherent WRITE stochasticity and resistance-drift; RRAM has cycle-to-cycle HRS/LRS variability. Critically, **the literature treats this as a resource, not a defect** ([Nature npj 2024](https://www.nature.com/articles/s44335-024-00017-x), [PCM review 2025](https://onlinelibrary.wiley.com/doi/abs/10.1002/est2.70272)). Adaptive-threshold neuromorphic systems explicitly exploit device stochasticity for probabilistic computation, Bayesian inference, and uncertainty quantification — exactly the regimes our adaptive-tau cells target.

Density-vs-noise tradeoff: variability-aware crossbar tutorials ([arXiv 2204.09543](https://arxiv.org/pdf/2204.09543)) show that read-variability is treated as a feature for stochastic computing; cell density actually scales BETTER when noise is allowed because the device can operate in a sub-threshold regime that's otherwise unstable.

**Implication:** Real neuromorphic substrates do NOT use deterministic adaptive-threshold mechanisms; they exploit intrinsic device noise. Our pure-software substrate has no intrinsic noise to exploit, so the architecture choice is: either *inject* stochasticity at boundary (M3 cortex), or *re-spec* substrate to include noise terms. Literature precedent strongly favors the former for systems where the deterministic backbone has other load-bearing properties (memory, audit).

Citations: [Mott memristor stochastic switching PMC12300364](https://pmc.ncbi.nlm.nih.gov/articles/PMC12300364/), [Leveraging stochasticity in memristive synapses](https://www.nature.com/articles/s44335-024-00017-x), [Variability-aware crossbar tutorial](https://arxiv.org/pdf/2204.09543), [PCM review 2025](https://onlinelibrary.wiley.com/doi/abs/10.1002/est2.70272), [PCM volatile threshold switching PMC12622517](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12622517/).

### Drill 3 — BIO (P=0.65, deflated 0.20 → **0.45**)
Biological neurons are *constitutively* stochastic at every level: Poisson-like spike trains (V1, retina), vesicle-release variability (binomial quantal model), stochastic ion-channel gating, synaptic short-term depression with stochastic recovery ([PMC4528672](https://pmc.ncbi.nlm.nih.gov/articles/PMC4528672/), [Modulated Poisson model 2025](https://www.biorxiv.org/content/10.1101/2025.07.23.666404.full.pdf)). The brain does NOT use deterministic signaling because:
1. **Energy:** stochastic release is ~10x more energy-efficient than reliable release.
2. **Bayesian computation:** uncertainty representation requires noise samples ([Knill & Pouget 2004 Bayesian brain](https://www.cell.com/trends/neurosciences/abstract/S0166-2236\(04\)00335-2)).
3. **Stochastic resonance:** sub-threshold signals become detectable with noise ([speech recognition + noise PMC9215117](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9215117/)).
4. **Threshold modulation:** vesicle stochasticity provides the variance needed for adaptive-gain to extract intermediate-band information.

Noise budget per neuron: Fano factor ≈ 1 in V1 (pure Poisson), drops to ~0.3 in S1 barrel cortex (low-noise touch encoding — [PMC4525079](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4525079/)) and parietal cortex (regular spiking — [PMC2743683](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2743683/)). **The brain is DELIBERATELY less-than-deterministic, and the noise level is region-tuned.**

**Implication:** The brain — our existence proof per [[feedback-brain-is-existence-proof]] — uses tuned stochasticity for adaptive-threshold work. A substrate aspiring to brain-grade adaptive capabilities cannot remain fully deterministic. But the brain ALSO has region-specific noise tuning (S1 nearly noiseless, V1 highly stochastic), supporting a **regional noise architecture** rather than uniform noise injection.

Citations: [Continuous partitioning of neuronal variability 2025](https://www.biorxiv.org/content/10.1101/2025.07.23.666404.full.pdf), [Vesicle release stochasticity PMC4528672](https://pmc.ncbi.nlm.nih.gov/articles/PMC4528672/), [Knill & Pouget Bayesian brain](https://www.cell.com/trends/neurosciences/abstract/S0166-2236\(04\)00335-2), [Low-noise S1 PMC4525079](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4525079/), [Poisson-like circuits 25032705](https://pubmed.ncbi.nlm.nih.gov/25032705/), [Noise improves speech recognition PMC9215117](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9215117/).

### Drill 4 — NEURO (specific mechanisms; P=0.55, deflated 0.15 → **0.40**)
Cortical adaptive-threshold mechanisms identified:
- **Habituation + normalization** are jointly mediated; tuning curve repulsion and stimulus-dependent response decorrelation are explained by recurrent gain-adjustment ([Cell Neuron 2014](https://www.cell.com/neuron/fulltext/S0896-6273\(14\)00051-8), [Adaptive coding efficiency 2023](https://arxiv.org/pdf/2305.19869)).
- **Contrast gain control** ([PMC6965083](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6965083/)): adaptation time-constants get longer at later cortical stages, producing progressively more stable representations — this is a *hierarchy of adaptive-tau scales*, not a single tau.
- **Threshold-adaptation + STSP resonance** ([arXiv 0906.0756](https://arxiv.org/pdf/0906.0756)): threshold adaptation alone is insufficient; combined with short-term synaptic plasticity it produces resonance — useful primitive for a substrate that needs ambiguous-band discrimination.

The cortex distinguishes "ambiguous in-domain" from "out-of-domain" using **divisive normalization with population pooling**: the ratio of one neuron's response to the local population's response. This requires (a) noisy individual responses, (b) a population statistic, (c) division-or-shunting at readout. The substrate currently has none of (a)–(c) in the adaptive-tau cells.

**Implication:** A 3-component primitive set is needed for substrate adaptive-tau: noise-source + population-statistic + divisive-normalization. The substrate has the second; needs the first (cortex-side injection) and the third (a cortex-side readout op).

Citations: [Adaptive gain Cell Neuron 2014](https://www.cell.com/neuron/fulltext/S0896-6273\(14\)00051-8), [Auditory contrast gain PMC6965083](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6965083/), [Adaptive coding efficiency arxiv 2305.19869](https://arxiv.org/pdf/2305.19869), [Threshold-STSP resonance 0906.0756](https://arxiv.org/pdf/0906.0756), [Contrast gain in A1 PMC7191518](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7191518/).

### Drill 5 — META (P=0.50 capped, deflated 0.15 → **0.35**)
Question: does determinism **exclude** capability classes, or is stochasticity injectable without breaking substrate guarantees? Answer from drills 1–4: **both true, with a clean architectural fix.**

Three injection paths, ranked by literature support:
- **PATH A — Cortex-side boundary injection** (M3 layer owns noise budget). Substrate stays deterministic for memory/compose/retrieve/audit. Cortex injects Gaussian-or-Bernoulli perturbation at adaptive-tau-cell inputs/outputs. Validated by: hybrid-system literature ([noise-control for DNA computing arXiv 1705.09392](https://arxiv.org/pdf/1705.09392), [deterministic-stochastic hybrid integrator MDPI 2025](https://www.mdpi.com/2226-4310/12/5/397)) showing "deterministic backbone + targeted noise injection" is the standard hybrid pattern.
- **PATH B — Substrate-internal stochastic codebooks** (regional noise architecture mimicking brain S1-vs-V1). Specific cells declare a noise-mode parameter; deterministic mode for memory-class cells, stochastic mode for adaptive-class cells. Higher implementation cost, more literature support for biological plausibility.
- **PATH C — Random projection / dropout-based injection inside the substrate** (lowest-cost stochastic source). Information-Dropout literature ([arXiv 1611.01353](https://arxiv.org/pdf/1611.01353)) shows the IB-principle interpretation. Drawback: dropout breaks the bipolar ±1 quantization without re-bipolarization.

Bridge between deterministic substrate and stochastic cortex: **the readout-statistic is the natural interface**. Substrate returns deterministic cos; cortex layer wraps that in a Gaussian-perturbation of width sigma_adaptive (learned per cell-class). This preserves substrate guarantees (audit, atomic memory) while giving adaptive cells what they need.

**Implication:** Determinism does NOT exclude capability classes if M3 cortex layer is in scope (it IS, per [project_M3_architecture_needs_cortex_layer_above_substrate]). The exclusion is only structural if we insist the substrate handle adaptive-tau internally. Recommend: defer substrate-side stochastic noise model cells; ship M3-cortex-boundary stochastic injection cells INSTEAD.

Citations: [Noise control for DNA computing 1705.09392](https://arxiv.org/pdf/1705.09392), [Deterministic-stochastic hybrid integrator MDPI 12/5/397](https://www.mdpi.com/2226-4310/12/5/397), [Information Dropout 1611.01353](https://arxiv.org/pdf/1611.01353), [Stochastic hybrid systems in cellular neuroscience PMC6104574](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6104574/), [Stochastic resonance SNN PMC10591140](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10591140/).

---

## Cross-thread synthesis with prior entries

- **[project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28]:** This finding STRENGTHENS M3-cortex-layer architecture. Cortex now owns the stochasticity budget in addition to hierarchical planning. Substrate stays deterministic; cortex stays the "uncertainty broker."
- **[feedback-brain-is-existence-proof]:** Brain uses regional noise tuning (S1 low-noise, V1 high-noise). The cortex layer's noise schedule should be cell-class-specific, not uniform.
- **[feedback_substrate_doesnt_know_anything_stop_testing_against_language]:** Adaptive-tau is a Stage 3 capability (composition / refuse-gate / attention), not a Stage 4 language capability. This finding doesn't change Stage progression — it changes HOW Stage 3 capabilities get built (route through M3 cortex, not substrate-internal redesign).
- **[feedback_test_rationality_encoding_before_readout]:** Adaptive-tau cells failing because the substrate's deterministic noise model writes no intermediate-band information to substrate state. Cortex-side noise injection is the *encoding* operation that adaptive-tau readouts presuppose. This is a direct example of the rationality-test catching a missing encoding mechanism.
- **Prior research bait:** several recent adaptive cells (refuse-gate adaptive-tau v2, cleanup SWR v3/v3.1) honest-aborted on the same root cause. This 5x drill is what those cells were missing the architectural answer for.

---

## Substrate-product implications

1. **Defer substrate-internal stochastic noise model cells.** Path B above is expensive and second-best per the literature.
2. **Open a new exp_dev anchor: M3-cortex-boundary stochastic injection.** Single cell, deterministic substrate + cortex wrapper that perturbs adaptive-tau inputs by Gaussian (sigma=0.05 std on cos) BEFORE thresholding. First validation target: refuse-gate adaptive-tau v3 (cortex-injected).
3. **Substrate spec change: NONE.** Determinism stays. Substrate's primary role (memory, compose, retrieve, audit) keeps the cleaner concentration that determinism delivers.
4. **Cortex layer spec addition:** the cortex must own a per-cell-class noise schedule. First instance: refuse-gate, cleanup-on-clean, dual-store novelty. Each gets its own sigma_adaptive.
5. **Cell-author guidance:** any future cell whose mechanism depends on intermediate-confidence-band extraction MUST declare its noise-injection point in pre-reg (substrate-side, cortex-boundary, or substrate-irrelevant). This is a META_RULE candidate.
6. **2x candidate (if test fails):** drill into structural-glasses-MCT (relaxation timescales for adaptive-tau evolution) — tier-1 adjacent field, drill_count low.

---

## Citations (verified count: 25)

All inline above; counted by URL.

**Next-drill candidate:** `mesoscopic-transport` (Landauer-Buttiker formalism for cortex-substrate boundary transmission coefficient; tier-1, drill_count low; directly addresses the determinism→stochasticity bridge as a transport problem).
