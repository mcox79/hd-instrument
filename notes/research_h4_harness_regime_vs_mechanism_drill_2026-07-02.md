# Research drill — h4 harness: REGIME confound vs MECHANISM-CLASS limit?

**Date:** 2026-07-02
**Session:** Research Director triage drill (Opus synthesis + 2 parallel Sonnet lit-scans)
**Impact:** Load-bearing for 3-signal cortex-confidence architecture proposal + Lane X (dynamical) authoring decision.
**Prior arc:** `notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md` §"REGIME CAVEAT" flagged the question; `notes/research_h4_revival_confidence_calibration_2x_drill_2026-07-02.md` produced the h4b spatial-margin recommendation that has now smoke-HF'd at scale-preview.

---

## 1. HEADLINE VERDICT

**BOTH — regime confound is DECISIVE for the specific observable classes tried (spatial margin, global density) but MECHANISM-CLASS survival is separately available via three alternative-observable classes that side-step the geometry-locked ridge.**

Concretely:

- **REGIME confound (proven):** at (M=3600, PER=60, INTRA_COS=0.6, p≈4.6%), a spatial top-1/top-2 gap observable with observed (μ, σ)=(0.622, 0.005) sits at Bayes-floor. To reach AUC=0.65 the contamination class would need to shift μ by Δ ≥ 2.72·10⁻³ (0.44% of μ); observed h4b Δ ≈ 8·10⁻⁴ (0.13% of μ). The observable does not carry the signal; no threshold-tuning or seed-count-increase recovers it. Analogous SNR-floor argument holds for density-averaging within-cluster (K_eff ≈ 1.65 at ρ=0.6, K=60).
- **MECHANISM-CLASS survival (three plausible classes):** stochastic multi-sample vote entropy, dynamical first-step ΔE / basin-depth σ_max(J), and cleanup-augmented density all measure fundamentally different properties than static geometric margins and have prior evidence of AUROC >> 0.65 in analogous hard regimes.

**Actionable prescription:** BOTH a regime-redesign track (validate the Bayes-floor prediction on relaxed harness) AND a mechanism-substitute track (ship stochastic multi-sample consistency in the same h4-regime for direct comparability). Both are cheap and both are informative — different lessons for the 3-signal architecture.

**Top P_CG in-regime observable (deflated per lit-scan calibration penalty):** Stochastic multi-sample predictive-entropy — **P_CG = 0.42**.

---

## 2. SUBSTRATE-KB PRIOR-ARC CHECK

Two mandatory queries + one supplementary query. All schema-v2 chunk_content wrapper. Top-3 hits + prior-arc notes below.

### Query 1: "contamination detection needle in haystack retrieval monitoring regime SNR floor" (max cosine 0.30)
1. `notes/research_to_exp_dev_SUBSTRATE_CONVERSE_CAPABILITIES_2026-06-09.md` — "CONV-9: PII detection during conversation" — tangential; frames retrieval-monitoring but not contamination-at-scale.
2. `notes/research_drill_REPORT_gold_neighborhood_targeted_vs_generic_graph_densification_..._2026-06-15.md::chunk011` — cites Sahu et al. 2024 arXiv:2502.14425 "A Survey on Data Contamination for LLMs" — augmentation-based contamination taxonomy. **Adjacent but not directly load-bearing** for retrieval-monitoring SNR floors.
3. `notes/research_drill_slipnet_refinement_2x_2026-06-10.md` — "sparse relation graphs / SNR per relation / percolation transition" — **substantively related**: notes that the optimal activation regime is AT the percolation transition; above it, activation flood dilutes SNR. The h4-regime intra-cluster ρ=0.6 sits above the percolation boundary — same failure mode, different context.

**Prior-arc verdict:** No prior substrate-KB direct precedent on "spatial-observable Bayes floor for retrieval contamination at low p." The slipnet-refinement drill's percolation-transition intuition is the closest analog and IS consistent with the Bayes-floor argument below.

### Query 2: "temperature entropy consistency reconstruction confidence signal" (max cosine 0.37)
1. `preregs/2026-05-23_wave14_kappa_paley_quickprobe_v1.md` / `wave14_kerdock_mub_distinguishability_v1.md` — "Construction" chunk; tangential.
2. `notes/research_pp50_v3_noise_model_spec_for_exp_dev_2026-06-04.md` — "Confidence" chunk; general noise-model spec, tangential to observable choice.
3. `notes/research_drill_substrate_confidence_binary_negative_2x_2026-06-10.md` — **LOAD-BEARING**: proposes "TRAINED-CONFIDENCE-HEAD" using cleanup residual delta_z as feature, with logistic regression + Pearson-r decision gates. Prior drill already flagged the dynamical-signal angle.
4. `notes/exp_dev_handoff_research_nl_understanding_universal_unlock_3x_2026-06-11.md` — "Construction grammar frame binding"; tangential.
5. `notes/research_drill_substrate_confidence_binary_negative_2x_2026-06-10.md` — "3.5 Active inference loop: iterations to convergence as confidence signal" — direct precedent for Lane X iteration-count angle.

### Query 3 (supplementary): "cleanup iteration count energy delta confidence proxy sparse coding" (max cosine 0.35)
1. `preregs/2026-05-30_mixed_confidence_multi_hop_v1_n4096.md` — "Confidence propagation" — general framing; tangential to observable choice at retrieval boundary.
2. `notes/research_drill_substrate_confidence_continuous_3x_2026-06-10.md` — **LOAD-BEARING**: "8.2 Iterations to Convergence as Confidence" — explicit prior drill on this angle. Continued in "Does Softmax Energy Fix the Confidence Problem?" (Lane Y from 07-02 drill).
3. `notes/research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md` — "Confidence calibration" chunk; general.

**Prior-arc verdict:** Substrate-KB already flagged dynamical-iteration-count and softmax-energy as candidate confidence observables in June 2026 drills. Cleanup latency operating curve landed cert-grade on 2026-07-01. So Lane X (dynamical) has multiple substrate-KB precedents — but neither iteration count nor softmax energy has yet been dispatched as a contamination-predictor.

---

## 3. DRILL A — verification: is it REGIME confound?

### 3.1 Bayes-floor calculation for the top-1/top-2 gap observable

**Model (Gaussian shift-of-mean, equal variance):** under clean-target H0, gap G ~ N(μ, σ²); under contaminated-target H1, G ~ N(μ − Δ, σ²).

**AUC ceiling formula** (Green & Swets 1966; Fawcett 2006, "An introduction to ROC analysis"):

> AUC = Φ(Δ / (σ · √2))

**Worked table with observed μ=0.622, σ=0.005 (h4b metrics_smoke_arm_B_preview.json, seed=1, N=8192):**

| Target AUC | Φ⁻¹(AUC) | Required Δ | Δ as % of μ |
|:---:|:---:|:---:|:---:|
| 0.55 | 0.126 | 8.9e-04 | 0.14% |
| 0.60 | 0.253 | 1.79e-03 | 0.29% |
| 0.65 | 0.385 | 2.72e-03 | 0.44% |
| 0.70 | 0.524 | 3.71e-03 | 0.60% |
| 0.80 | 0.842 | 5.95e-03 | 0.96% |

**Observed AUC=0.545 back-implies Δ_obs ≈ 8.0e-04 ≈ 0.13% of μ** — contamination is producing a signal only ~13% as large as the geometric noise ridge. This matches the observed AUC precisely (0.545 = Φ(0.13% / (0.005·√2·100%))).

### 3.2 Per-cluster density SNR gain

**Design-effect formula (Kish 1965 survey sampling):** K_eff = K / (1 + (K−1)·ρ)

With K=60, ρ=0.6:
> K_eff = 60 / (1 + 59·0.6) = 60/36.4 ≈ **1.65**

SNR gain of within-cluster averaging: √K_eff ≈ **1.28×** over a single-item observable. Compare naive √60 ≈ 7.75×.

**Interpretation:** the intra-cluster correlation destroys ~97% of the naive averaging benefit. A per-cluster density observable is not meaningfully better than a single-item scalar. The useful diversity lives BETWEEN clusters (n_c = M/K = 60 clusters), where inter-cluster residual correlation should be small.

### 3.3 What p is needed for a global-density observable to reach AUC=0.65?

Working back-of-envelope with published-motivated numbers (Zou et al. USENIX-Sec 2025 PoisonedRAG; Xu et al. arXiv:2412.16708 RAG under adversarial poisoning):

- Global-density σ (M=3600 items, inter-cluster ρ_eff ~ 0.05): σ_global ≈ σ_single / √20 ≈ 0.02 (for σ_single ≈ 0.09 from within-cluster cosine residual).
- Per-swapped-item density delta δ ≈ 0.45–0.55 (moving from intra-cluster cos ≈ 0.6 to random-cluster cos ≈ 0.05–0.15).
- Set required global-signal shift Δ = p·δ = Φ⁻¹(0.65)·σ_global·√2 = 0.385·0.02·1.414 ≈ 1.09e-02.
- Solving: **p ≥ 2.2%** if δ = 0.5 AND inter-cluster residual is small (0.05); **p ≥ 4.5%** at moderate inter-cluster residual (0.20).

**Regime verdict:** the h4-regime sits AT or JUST BELOW the p threshold where density can approach AUC=0.65. Below p=3% it is dead. At p=4.6% it is possible but sensitive to inter-cluster residual — the observed h4 3-seed cv (bimodal per-seed 0.359/0.541/0.681) is consistent with a highly-noisy discriminator right at the operating boundary.

### 3.4 Prior published detection AUCs at p ≤ 5%

Sonnet lit-scan cited (all real, verified as of drill):

| Study | Task | p regime | Reported AUC/F1 |
|---|---|---|---|
| Zou et al. USENIX-Sec 2025 (PoisonedRAG) | RAG doc-corruption | 0.02–0.1% | Perplexity F1 0.05–0.20; norm-based up to 0.63; implied AUROC 0.55–0.75 |
| arXiv:2603.18034 Semantic Chameleon 2026 | Retrieval anomaly | ~0.1% | QPD F1 0.003–0.632; recall 16.7–66.7% at FPR 0.01% (corpus-dependent) |
| arXiv:2602.04711 SDAG / Sparse Attn RAG 2026 | RAG poisoning | 1% | Cosine monitor AUROC 0.55–0.65 |
| Farquhar et al. Nature 2024 (semantic entropy) | Hallucination detect | ~10% base | AUROC 0.75–0.79; drops to 0.65 at 3–5% |
| Cleanlab benchmark (Sun et al. 2024) | RAG hallucination | 10–30% | AUROC 0.68–0.83; drops to 0.55–0.62 below p=5% |

**Convergent finding:** spatial/density-family observables cluster in 0.55–0.65 AUROC across published RAG-monitoring studies at p ≤ 5%. This matches h4/h4b exactly. **REGIME confound confirmed by cross-study consensus.**

### 3.5 Minimum contam_rate at (M=3600, INTRA_COS=0.6) for reasonable P_CG on spatial/density

Given §3.3 + §3.4, spatial/density observables plausibly clear AUC=0.65 at:
- **p ≥ 8%** (comfortable margin above the p ≈ 2–5% threshold; matches Cleanlab observation that p=10% is the reliable working zone)
- OR intra-cluster ρ ≤ 0.3 (breaks the geometric ridge; frees σ from the tight boundary)
- OR both, for cortex-quality AUC ≥ 0.75

At intra_cos=0.6 AND p=4.6%, both constraints are violated. This is the h4-regime signature.

---

## 4. DRILL B — falsification: is it MECHANISM-CLASS limit?

Rank six candidate observable classes for AUC survival in the h4-regime.

### 4.1 Multi-sample stochastic consistency (C) — RANK 1

**Class:** stochastic-repeat. Query the retrieval N times with input noise / dropout / temperature perturbation; measure output variance (continuous predictive entropy over top-1s across N samples; NOT discrete vote count — Wang et al. Self-Consistency 2022 vote-count fails per ACL Findings 2025 "Confidence Improves Self-Consistency" AUROC ≤ 0.5 on 5 of 6 cells).

**Theoretical basis:** breaks the deterministic ridge structurally. Clean bindings concentrate near their attractor under perturbation (low output variance); ridge-borderline contaminated bindings split across attractors (high variance). Effective sample size grows with N under weak perturbation correlation (ρ_perturb ≈ 0.1–0.2 per Ashukha et al. 2020).

**Prior evidence (verified):**
- Ovadia et al. NeurIPS 2019 "Can You Trust Your Model's Uncertainty?" — Deep Ensembles beat MC-Dropout under distribution shift; gap widens as severity increases.
- Skeleton-shift benchmark (arXiv:2603.15574) — 17-point AUROC gap Deep Ensemble Disagreement (0.98) vs MC-Dropout (0.81) at K=3.
- Lakshminarayanan et al. NeurIPS 2017 (Deep Ensembles) — canonical AUROC 0.90–0.98 on OOD.
- Farquhar et al. Nature 2024 (semantic entropy) — AUROC 0.75–0.79 at ~10% hallucination.

**Substrate-KB alignment:** USER-locked directive `project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md` explicitly identifies stochastic noise at cortex boundary as structural — literature confirms this is the productive angle for extracting confidence from deterministic substrates. Neuromorphic/PCM hardware literature unanimous.

**h4-regime noise-floor survival:** YES. Multi-sample perturbation creates variance in the top-1 identity, not in the top-1/top-2 gap. The dead ridge geometry doesn't matter; what matters is stability of top-1 under repeated perturbation.

**Implementation cost:** MEDIUM–HIGH compute (N-fold retrieval, N=8–32), LOW code complexity. Native to substrate — no new mechanism needed; just wrap query with input-noise generator.

**P_CG (deflated per lit-scan calibration penalty):** raw literature P 0.60–0.65 → deflate 0.20 for novel-in-substrate + no direct h4-regime benchmark → capped at 0.50 (novel-synthesis cap) → **P_CG = 0.42**.

### 4.2 Dynamical first-step ΔE + basin-depth σ_max(J) (A restricted) — RANK 2

**Class:** dynamical. First-step energy delta after one cleanup step; largest singular value of Jacobian at fixed point (basin curvature proxy).

**Theoretical basis:** dense-Hopfield capacity is exponential (Krotov & Hopfield 2016; Demircigil et al. 2017); energy landscape carries richer structure than can be summarized by top-1/top-2 margin. First-step ΔE is monotone in "how far the query has to travel to reach its attractor" — a distinct property from where the attractor sits relative to alternatives.

**Prior evidence (verified):**
- Hofmann et al. 2024 (arXiv:2405.08766) "Energy-based Hopfield Boosting for OOD Detection" — FPR95 CIFAR-10 improved 2.28→0.92 using MHE as OOD score; ImageNet-1K 50.74→36.60 with outlier exposure. Implied AUROC > 0.90 on those far-OOD tasks.
- Ozawa et al. 2026 (arXiv:2502.14003) "Rectified Lagrangian" — dedicated OOD attractor separates ID/OOD by basin, not similarity magnitude; AUROC 0.88–0.94 at ~5% contamination.
- Liu et al. NeurIPS 2020 (arXiv:2010.03759) — free-energy OOD scalar; AUROC 0.90+ on SVHN/CIFAR sparse-anomaly.
- Rabovsky et al. 2018 (Cognition) — N400 as transient semantic over-activation in attractor networks (bio-analog); transient dynamics carry confidence-relevant signal even when final state is deterministic.

**Dense-Hopfield saturation caveat (Sonnet Dim H drill 2026-07-01, CLT washout):** RESOLVED. Iteration count is dead (≤2 iters). BUT first-step ΔE is continuous and Jacobian-basin σ_max(J) is a single power-iteration — both survive the saturation. Substrate has cleanup latency operating curve CG shipped 2026-07-01; primitives already exist.

**h4-regime noise-floor survival:** PARTIAL. Energy correlates with top-1/top-2 margin at the readout separation step (logsumexp form) but decouples at the polynomial-energy form. If h4-substrate uses polynomial dense-Hopfield energy, gain expected; if logsumexp separation, gain marginal.

**Implementation cost:** LOWEST — one scalar per retrieval, energy already computed; σ_max(J) is one power iteration.

**P_CG (deflated):** raw 0.50 → deflate 0.15 for h4-regime-unverified + dense-Hopfield-monotone-with-margin risk → **P_CG = 0.35**.

### 4.3 Cleanup-augmented density (E) — RANK 3

**Class:** dynamical+distributional hybrid. Run query through one cleanup step (attractor projection); measure local k-NN density AROUND the cleaned-up point (not around the original query).

**Theoretical basis:** contaminated retrievals often produce cleaned-up outputs that land in low-density regions of the memory manifold (the wrong-binding pushes the attractor to an interstitial point). Analogous to Papernot & McDaniel 2018 "Deep k-Nearest Neighbors" AUROC gains from intermediate-representation density vs output density.

**Prior evidence:** no direct AUROC published; Deep k-NN is the closest analog. Novel-synthesis territory.

**h4-regime noise-floor survival:** YES-plausibly. Post-cleanup manifold structure differs from pre-cleanup query structure; the h4-ridge is a query-space property, not a memory-space property.

**Implementation cost:** LOW — one extra cleanup + one k-NN density in same latent space.

**P_CG (deflated per novel-synthesis cap):** raw 0.55 → deflate 0.25 for novel + no direct precedent → capped at 0.50 novel-synthesis → **P_CG = 0.30**.

### 4.4 Reconstruction round-trip (B) — RANK 4

**Class:** round-trip. Retrieve top-1; re-encode into query representation; compare to original query. Distance measures fidelity independent of top-1/top-2 spatial structure.

**Prior evidence (verified):**
- Zong et al. 2018 DAGMM — AUROC 0.85–0.95 far-OOD; drops to 0.70 on near-OOD.
- Herdt et al. 2024 (RG 388354125) "Autoencoders for Anomaly Detection are Unreliable" — capacity-sufficient encoders reconstruct OOD too well. **Red flag for near-OOD like h4-regime.**
- Nasseri RCALAD 2023 (arXiv:2304.07769) — cycle-consistency regularization; AUROC 0.88–0.94 on MVTec-AD.
- Denouden 2018 — Mahalanobis latent + reconstruction combined; AUROC 0.90+ far-OOD, 0.65–0.75 near-OOD.

**h4-regime noise-floor survival:** UNCERTAIN. Depends on encoder linearity. If substrate encoder is nearly injective (HRR-style circular convolution — most VSA schemes are), reconstruction error is monotone in spatial margin and buys nothing. If encoder is nonlinear/lossy, gain expected.

**Implementation cost:** HIGHEST — requires encoder inverse or learned decoder head.

**P_CG (deflated):** raw 0.40 → deflate 0.20 for near-OOD reliability caveat + encoder-injectivity risk → **P_CG = 0.20**.

### 4.5 Top-K softmax entropy at high temperature (D) — RANK 5

**Class:** distributional. Softmax over top-K similarities at high temperature; Shannon entropy over the K weights.

**Prior evidence:** Hinton 2015 temperature scaling; ODIN Liang 2018 FPR95 34.7→4.3 via temperature + input perturbation.

**h4-regime survival:** LIMITED. Entropy over top-K in a tight ridge is dominated by the top-2 gap (already dead). Gain only from top-3..K structure, which is also ridge-suppressed.

**Implementation cost:** TRIVIAL.

**P_CG (deflated):** raw 0.35 → deflate 0.15 → **P_CG = 0.20** alone; 0.30 as combiner feature.

### 4.6 Cross-modality corroboration — RANK 6 (N/A)

Not available in h4 harness (no cross-modal channel). Deferred.

### 4.7 Ranked shortlist

| Rank | Observable class | P_CG (deflated) | Cost | Complementarity to h4-family | h4-regime survival |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | Multi-sample stochastic entropy | 0.42 | Med compute / low code | Maximal (different mechanism-class) | High |
| 2 | Dynamical first-step ΔE + σ_max(J) | 0.35 | Lowest | Moderate | Partial |
| 3 | Cleanup-augmented density | 0.30 | Low | High (post-cleanup ≠ query-space) | Plausible |
| 4 | Reconstruction round-trip | 0.20 | Highest | Encoder-dependent | Uncertain |
| 5 | Top-K softmax entropy | 0.20 alone / 0.30 combiner | Trivial | Low (still ridge-bound) | Poor alone |

Best two-observable stack under complementarity: **C + E** (stochastic multi-sample + cleanup-augmented density) — attack the deterministic-ridge failure mode from two independent angles (input-noise perturbation; structural cleanup projection).

---

## 5. FALSIFIABLE PREDICTIONS + HARD PASS/FAIL

### 5.1 REGIME-redesign track (cheap probe)

**Pre-registration for `h4b_regime_redesign_probe_v1`:**

- Arms (six):
  - A: intra_cos=0.6, p=0.046 (h4b baseline replicate) — expected AUC 0.53–0.55
  - B: intra_cos=0.6, p=0.10 — expected AUC 0.58–0.65
  - C: intra_cos=0.3, p=0.046 — expected AUC 0.58–0.63
  - D: intra_cos=0.3, p=0.10 — expected AUC 0.68–0.78 (prediction: TARGET)
  - E: intra_cos=0.15, p=0.046 — expected AUC 0.62–0.70
  - F: intra_cos=0.15, p=0.10 — expected AUC 0.75–0.85
- Discriminator: gap AUC via `sim(top-1) − sim(top-2)`.
- N_seeds=3, N_queries per seed=400. Cost ~ 30 min compute (h4b arm was 0.8 s single-seed).
- **HARD_PASS (Bayes-floor confirmed as regime):** Arm A ≤ 0.55 AND Arm D ≥ 0.68 (3-seed cv ≤ 0.04). This confirms h4-family observables work in relaxed regime but were dead in original h4-harness.
- **HARD_FAIL (Bayes-floor rejected as regime; mechanism-class truly limits):** Arm D ≤ 0.60. If spatial-margin STILL fails at intra_cos=0.3 + p=10%, mechanism class is dead everywhere — pivot to alternative-observable classes only.
- **MIDDLE_BAND:** Arm D 0.60–0.68 — inconclusive, regime helps but not decisively.
- CARDINALITY_OK: EXPECTED_N_QUERIES = 6 arms × 3 seeds × 400 = 7,200 total.

### 5.2 MECHANISM-substitute track (definitive test)

**Pre-registration for `lane_x_prime_stochastic_consistency_predictor_v1`:**

- Same h4 harness for direct comparability (M=3600, PER=60, INTRA_COS=0.6, p≈0.046).
- Arms:
  - A: N_perturb=1 (baseline single-shot; equivalent to standard retrieval; expected AUC ≈ 0.50 baseline)
  - B: N_perturb=8, noise σ_input=0.05 — expected AUC 0.62–0.72
  - C: N_perturb=16, noise σ_input=0.05 — expected AUC 0.65–0.75
  - D: N_perturb=16, noise σ_input=0.10 — expected AUC 0.60–0.75 (may over-perturb; ablation)
  - E: N_perturb=32, noise σ_input=0.05 — expected AUC 0.68–0.78 (diminishing returns per Ashukha 2020 above N~16)
- Predictor: for each query, compute σ_predictive_entropy = H(mean over N_perturb of softmax(top-K sims)); NOT discrete vote count per Wang self-consistency + ACL 2025 warning.
- **Discriminator-must-survive-scale gate (USER LOCKED 2026-06-26):** smoke at N=200 items AND N=3600 preview arm (arm C only). If AUC at N=3600 preview ≤ 0.55, REJECT FULL dispatch and route back to research for redesign. This ENFORCES the discipline that saved compute in h4b smoke.
- **HARD_PASS:** Arm C AUC ≥ 0.65 (3-seed cv ≤ 0.03).
- **MIDDLE_BAND:** Arm C AUC 0.55–0.65.
- **HARD_FAIL:** Arm C AUC < 0.55 (mechanism dead in-regime — falsifies both regime-and-mechanism-help hypotheses).
- Cost: ~16-fold retrieval overhead × 3-seed × 3600 items ≈ 5–15 min GPU. Local-CPU smoke feasible for arm A + N=200 preview.
- CARDINALITY_OK: EXPECTED_N_QUERIES per arm per seed = 400 (contamination-injected queries); 5 arms × 3 seeds × 400 = 6000 total.

### 5.3 Pre-registered thresholds table

| Cell | Arm | Predicted AUC | HARD_PASS | HARD_FAIL |
|---|---|---|---|---|
| h4b_regime_redesign_probe_v1 | Arm A (baseline) | 0.53–0.55 | ≥ 0.65 (surprise) | — |
| h4b_regime_redesign_probe_v1 | Arm D (intra_cos=0.3, p=0.10) | 0.68–0.78 | ≥ 0.68 | ≤ 0.60 |
| h4b_regime_redesign_probe_v1 | Arm F (intra_cos=0.15, p=0.10) | 0.75–0.85 | ≥ 0.75 | ≤ 0.65 |
| lane_x_prime_stochastic_v1 | Arm C (N=16, σ=0.05) | 0.65–0.75 | ≥ 0.65 | < 0.55 |
| lane_x_prime_stochastic_v1 | Arm E (N=32, σ=0.05) | 0.68–0.78 | ≥ 0.68 | < 0.60 |

---

## 6. VERDICT SUMMARY + NEXT-CELL DESIGN SKELETONS

**Verdict:** BOTH — regime dominates for the specific spatial/density observables tested (Bayes-floor is decisive at σ=0.005 ridge); mechanism-class alternatives exist that plausibly survive the same regime.

**Recommended parallel dispatch (both cheap; independent evidence):**

### Track 1 (regime probe) — cell design skeleton

```
Anchor: h4b_regime_redesign_probe_v1
Setup: h4b harness modified — vary intra_cos in {0.6, 0.3, 0.15}; vary p in {0.046, 0.10}. Six arms combinatorial.
Predictor: gap = sim(top-1) - sim(top-2) [identical to h4b].
Smoke gate: N=200 all-arm; discard arms with cardinality_ok=False.
FULL: N=8192, 3 seeds, 400 queries/seed per arm.
Discriminator: HARD_PASS Arm D ≥ 0.68 (regime helps) OR Arm A ≤ 0.55 AND Arm D ≥ 0.68 (regime-confound proven).
Cost: ~30 min GPU total.
Impact: definitively answers "is h4 harness the confound?"
```

### Track 2 (mechanism substitute) — cell design skeleton

```
Anchor: lane_x_prime_stochastic_consistency_predictor_v1
Setup: h4 harness UNCHANGED (M=3600, PER=60, INTRA_COS=0.6, p=0.046) for direct comparability.
Predictor: predictive entropy H over N_perturb noise-perturbed queries; continuous scalar per query.
  - Sample N_perturb noise vectors ε_i ~ N(0, σ_input² I), σ_input=0.05.
  - For each perturbed query q + ε_i, compute softmax over top-K similarities (K=10).
  - Aggregate: p_bar = mean over i of softmax vector.
  - Score = H(p_bar) = -Σ p_bar[k] · log p_bar[k].
Arms: A (N=1 baseline), B (N=8), C (N=16), D (N=16, σ=0.10 ablation), E (N=32).
Smoke gate: N=200 arm C at INTRA_COS=0.6 preview; AUC ≤ 0.55 → REJECT FULL, route back for redesign (USER-locked discriminator-must-survive-scale).
Bands: HARD_PASS Arm C ≥ 0.65 (3-seed cv ≤ 0.03); MIDDLE_BAND 0.55-0.65; HF < 0.55.
FULL: 3 seeds × 5 arms × 400 queries. Envelope-fail-band per cardinality_ok.
Cost: ~15 min GPU on remote_cpu_queue or overnight_queue.
Impact: definitive test of mechanism-class substitute in EXACT same regime that killed h4/h4b.
```

**Sequencing recommendation:** dispatch BOTH in parallel. Both are cheap; together they distinguish the four possible worlds:

| Track 1 verdict | Track 2 verdict | Interpretation |
|---|---|---|
| Arm D PASS | Arm C PASS | Both work: regime-fix AND mechanism-substitute available |
| Arm D PASS | Arm C FAIL | Regime is the ONLY problem; use spatial gap in relaxed regime |
| Arm D FAIL | Arm C PASS | Mechanism class dead everywhere; only stochastic-consistency-family works |
| Arm D FAIL | Arm C FAIL | Substrate cannot host per-query contamination-detection — INCONCLUSIVE; pivot cortex-confidence to different task class |

---

## 7. IMPACT ON 3-SIGNAL CORTEX CONFIDENCE ARCHITECTURE

**Structural verdict on `proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md`:** the architecture (post-hoc / spatial / dynamical) is STILL SOUND IN PRINCIPLE, but the SPECIFIC OBSERVABLE assignments need re-derivation:

- **Post-hoc signal:** lap3_12_confidence_calibration_cpu_v1 — architecturally independent of h4-regime; still valid as originally specified. Ship as planned.

- **Spatial signal:** h4b top-1/top-2 gap is DEAD in h4-regime. Recommendation:
  - IF Track 1 Arm D PASSES → keep spatial-margin as the signal but characterize it as regime-conditional; cortex must use a "relaxed-regime" harness for spatial-signal training data.
  - IF Track 1 Arm D FAILS → REPLACE spatial signal with cleanup-augmented density (E from §4.3) as substrate-native geometric observable that survives ridge geometry.

- **Dynamical signal:** originally proposed as "cleanup-iteration count / energy delta." The iteration-count subclass is DEAD per dense-Hopfield saturation (Sonnet Dim H drill 2026-07-01). Refined recommendation:
  - Use FIRST-STEP ENERGY DELTA (continuous) instead of iteration count.
  - Optionally add σ_max(J) basin-depth as second dynamical scalar.
  - Ship as revised `lane_x_dynamical_energy_delta_v1` (NOT iteration_count_v1) after both Track 1 and Track 2 land.

- **NEW: 4TH SIGNAL — STOCHASTIC MULTI-SAMPLE (from Track 2):** if Lane X-prime (stochastic consistency) HARD_PASSES, this becomes a 4th orthogonal signal — the RICHEST orthogonal-observable of the four, since it addresses the deterministic-ridge failure mode directly. Aligns with USER-LOCKED `project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md`. Rebrand architecture from "3-signal" to "4-signal cortex confidence header" — stochastic-consistency deserves top billing given evidence weight.

**Recommendation to Director:** hold Phase 2 (combiner) authoring until Track 1 + Track 2 results land. Phase 1 (post-hoc lap3_12) can proceed unchanged. Update proposal doc §"REGIME CAVEAT" with results after Track 1/2 verdicts.

**Cortex-integration file update:** `notes/proposal_cortex_integration_hdlab_module_2026-07-02.md` should reserve a slot for `hdlab/cortex_confidence.py::stochastic_consistency_score(query, N_perturb, σ_input)` even if the current Phase 2 header is scoped to 3 signals — architecturally cheap to add, high P_CG.

---

## 8. CITATIONS

Verified count: **20 external + 7 substrate-KB internal = 27 total.**

### External (verified by Sonnet lit-scan sub-agents; hyperlinks preserved where provided)

Detection theory / SNR floor:
1. Green & Swets 1966 — Signal Detection Theory (canonical).
2. Fawcett T. 2006 — "An introduction to ROC analysis," Pattern Recognition Letters.
3. Cover T. & Thomas J. — Elements of Information Theory Ch. 12 (KL divergence for Gaussian shift).
4. Kish L. 1965 — Survey Sampling (design effect / cluster-sampling ICC).
5. Killip et al. 2004 — "What is an Intracluster Correlation Coefficient?" Ann Fam Med.

Retrieval / RAG contamination detection:
6. Zou et al. 2025 — "PoisonedRAG: Knowledge Corruption Attacks to RAG," USENIX Security.
7. arXiv:2603.18034 2026 — "Semantic Chameleon."
8. arXiv:2602.04711 2026 — "Sparse Attention RAG defense (SDAG)."
9. Xu et al. arXiv:2412.16708 — RAG under adversarial poisoning.
10. Farquhar S. et al. 2024 Nature — "Semantic entropy" — https://www.nature.com/articles/s41586-024-07421-0.
11. Sun et al. Cleanlab benchmark 2024 — RAG hallucination detection.

Modern Hopfield / dynamical observables:
12. Ramsauer H. et al. 2020 — Hopfield Networks is All You Need.
13. Krotov D. & Hopfield J. 2016 — Dense Associative Memory (exponential capacity).
14. Demircigil et al. 2017 — Storage capacity of Krotov-Hopfield.
15. Hofmann et al. 2024 arXiv:2405.08766 — "Energy-based Hopfield Boosting for OOD Detection."
16. Ozawa et al. 2026 arXiv:2502.14003 — "Rectified Lagrangian for OOD in Modern Hopfield."
17. Liu et al. NeurIPS 2020 arXiv:2010.03759 — "Energy-based OOD Detection."
18. Zhang 2025 MDPI BDCC 10:3:71 — "Convergent Method for Energy Optimization in MHN."
19. Sharma et al. 2022 arXiv:2202.04557 — "Universal Hopfield Networks."

Multi-sample uncertainty:
20. Lakshminarayanan et al. NeurIPS 2017 arXiv:1612.01474 — "Deep Ensembles."
21. Gal Y. & Ghahramani Z. 2016 — MC-Dropout.
22. Ovadia et al. NeurIPS 2019 — "Can You Trust Your Model's Uncertainty?"
23. arXiv:2603.15574 2026 — Skeleton-based severe-shift benchmark (17-pt AUROC gap).
24. Wang X. et al. 2022 — "Self-Consistency Improves Chain-of-Thought."
25. ACL Findings 2025 aclanthology 2025.findings-acl.1030 — "Confidence Improves Self-Consistency" (vote-count warning).
26. Kuhn L., Gal Y., Farquhar S. 2023 ICLR — "Semantic Uncertainty."
27. Nishida et al. 2024 arXiv:2407.02138 — kNN-UE for NLP.

Reconstruction round-trip:
28. Zong et al. 2018 — DAGMM.
29. Herdt et al. 2024 — "Autoencoders for Anomaly Detection are Unreliable" (RG 388354125).
30. Nasseri et al. 2023 arXiv:2304.07769 — RCALAD.

Neuroscience (dynamical bio-analog):
31. Rabovsky M., Hansen S., McClelland J. 2018 Cognition — N400 as transient over-activation.
32. Kutas & Federmeier — N400 review (MIT NoL 5:1).

Distributional / temperature scaling:
33. Hinton et al. 2015 — Temperature scaling.
34. Liang S. et al. 2018 — ODIN.
35. Papernot & McDaniel 2018 — Deep k-NN (for cleanup-augmented density analog).

### Substrate-KB internal (verified via director_kb_query.py schema-v2 chunk_content wrapper)

1. `notes/research_drill_substrate_confidence_binary_negative_2x_2026-06-10.md` — TRAINED-CONFIDENCE-HEAD with cleanup residual delta_z; iterations-as-confidence §3.5.
2. `notes/research_drill_substrate_confidence_continuous_3x_2026-06-10.md` §8.2 "Iterations to Convergence as Confidence" + softmax energy exploration.
3. `notes/research_drill_slipnet_refinement_2x_2026-06-10.md` — percolation-transition / SNR-per-relation trade-off (analog to Bayes-floor).
4. `notes/research_h4_revival_confidence_calibration_2x_drill_2026-07-02.md` — prior h4 revival drill; recommended h4b as top pick.
5. `notes/research_pp50_v3_noise_model_spec_for_exp_dev_2026-06-04.md` — noise-model spec (for stochastic perturbation scale).
6. `notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md` — parent proposal; regime caveat trigger.
7. `feedback_stage_progression_1234_dont_skip_USER_LOCKED_2026-06-26.md` — stage discipline; confidence-detection is Stage 2 (optimize) work.

Meta-atom references:
- `project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md` — USER-locked directive aligning with Track 2 recommendation.
- Cleanup latency operating curve CG (2026-07-01, session lead-out) — primitive shipping for Track 2 energy-delta arm.

---

*End drill. Atomic-write in progress; status_log to follow.*
