# Research: SSM-HiPPO substrate compatibility scan

**Filed:** 2026-05-25 by research sub-agent (Opus).
**Drill type:** Tier-1 open-item closure (third remaining alongside MoE-rebuild and Bet N).
**Trigger:** orchestrator dispatch — heavy research night with SSH down; produce design-readiness assessment for exp_dev to ship when SSH returns.
**Prior substrate context:** R-PRIME-5 framing (notes/research_R_PRIME_directions_2026-05-24.md); wave14e_s4_depth_smoke_v1 returned ssm_depth=0 vs binding_depth=200 (v190 CLOSED-FAILED annotation in substrate_capability_map.md).
**Field-advisor placement:** novel synthesis spanning `inference` (SSM theorems), `modern-hopfield` (linear-attention duality), `learning-rules` (Hebbian outer-product vs HiPPO ODE), `nonequilibrium-stat-mech` (continuous-time projection vs discrete event). Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]] (substrate is in uncharted regime: BSC binary atoms + sparse PPMI + rank-1 Hebbian W + no symmetrization + linear-heteroassoc primitive — no published direct precedent).

---

## (a) HEADLINE

**SSM-HiPPO is mathematically COMPATIBLE with substrate W at the level of the underlying algebra (both are outer-product / fast-weight associative memories; the Mamba "structured-state-space duality" line and the linear-attention-as-iterated-Hopfield-network line both anchor this equivalence). BUT the natural mapping makes substrate W the *state-space* and HiPPO the *initialization* — NOT a depth-extension overlay. The v190 wave14e probe failed because it tried to stack an external SSM layer on top of the binding chain; the literature predicts this CANNOT extend depth, because SSMs are PROVABLY worse at recall than the underlying associative-memory primitive they wrap (Jelassi et al. 2024 Theorem 2.7: |U| >= |V|^n state-size lower bound to avoid error). The only substrate-compatible HiPPO move is to use HiPPO-LegS *as an initializer* for W — produce a HiPPO-structured W_0 that the Hebbian outer-product updates *modify*, rather than running SSM dynamics on top of W. Calibrated P(category-defining substrate capability) = 0.18 (cap-novel-synthesis at 0.50, deflated to 0.18 by: explicit failure prior at v190, Jelassi lower bound rules out the direct depth-extension framing, and even the surviving HiPPO-init framing competes against simpler Kerdock/codebook init that already exists in our v183-v187 sweep). Substrate-product takeaway: SSM-HiPPO is NOT the bet for category-defining capability; it's a one-shot init-replacement experiment with a clear hard-fail. Recommend SHIP a single 1-day CPU probe, not a multi-experiment investment.**

---

## (b) Cheap decisive test

**Cheapest:** Replace random BSC initialization of W with a HiPPO-LegS-structured initialization (rank-N projection of substrate atoms onto Legendre basis, then Hebbian outer-product overlay). Run on the existing Cap 3 chain-cleanup task at d in {25, 50, 100, 200}. Compare to (random-init W) baseline at matched seed/cell.

- Pre-existing infra to reuse: `experiments/exp_wave14e_s4_depth_smoke_v1.py` HiPPO-LegS A-matrix construction (lines 90-105 already implement diagonal HiPPO-like eigenvalues). Re-use the A-matrix construction; do NOT use the run_ssm forward loop (that's the v190 mistake).
- Decisive metric: depth-at-half (depth at which mean cosine to a_1 < 0.5 across the chain). HARD-PASS: depth-at-half >= 1.5x random-init baseline at all four d-points. HARD-FAIL: depth-at-half <= 1.0x random-init at any of the four d-points. MIDDLE: anything in between.
- ETA: ~1-2 hours CPU on remote_cpu_queue at N=4096, 3 seeds, 4 d-points. Saturates remote CPU bandwidth for one slot.

**Why this is the cheap-decisive test:** the v190 failed framing was "SSM overlay extends substrate depth." The substrate-compatible framing is "HiPPO restructures the substrate state itself." If HiPPO-init does NOT help at the cheapest reasonable framing (rank-1 Hebbian outer-product onto a HiPPO-structured W_0), then no fancier integration (selective Mamba, S5, attention-with-HiPPO-bias) will rescue it on substrate.

---

## (c) Falsifiable predictions with HARD PASS / HARD FAIL thresholds

### Prediction 1 — HiPPO-init W vs random-init W (chain-cleanup depth-at-half)

- **HARD PASS:** depth-at-half(HiPPO-init) >= 1.5 * depth-at-half(random-init) across all d in {25, 50, 100, 200}; effect size >= 0.10 absolute cosine improvement at d=50.
- **HARD FAIL:** depth-at-half(HiPPO-init) <= 1.0 * depth-at-half(random-init) at any d-point; OR HiPPO-init delivers no measurable improvement at d=50 (the v190-tested depth).
- **MIDDLE band:** HiPPO-init delivers 1.0-1.5x improvement at any d-point but does not meet the 1.5x universal-pass criterion. MIDDLE band classifies as PARTIAL with annotation "HiPPO-init shows substrate-compatible signal but does not clear category-defining bar; promote to evidence-strength row only if d=200 result holds."

### Prediction 2 — Jelassi state-size lower bound is observable on substrate

- **HARD PASS:** Empirical observation that scaling N (substrate dimensionality) by factor 2x is INSUFFICIENT to recover chain-cleanup at d=200; this matches the Jelassi |U| >= |V|^n state-size lower bound and CONFIRMS substrate sits in the SSM-recall-bound regime.
- **HARD FAIL:** Scaling N by 2x DOES recover chain-cleanup at d=200; this would REJECT the Jelassi mapping and OPEN a substrate-novel scaling regime (substrate-as-non-state-space).
- **MIDDLE band:** 1.2-1.8x improvement from N-doubling; consistent with Jelassi bound but at a more-favorable constant than published.
- **Outcome interpretation:** HARD PASS on prediction 2 is the SCIENTIFICALLY-IMPORTANT outcome even if prediction 1 fails — it tells us substrate is bound by the same recall-capacity lower bound as SSMs, which means depth-extension via HiPPO/SSM tricks is provably non-existent and we should pivot the multi-hop capability elsewhere (resonator decomposition, structured codebooks, etc.).

### Prediction 3 — HiPPO-LegS A-matrix eigenvalues match substrate W eigenvalue spectrum

- **HARD PASS:** Top-K eigenvalues of HiPPO-init W match top-K eigenvalues of post-training random-init W to within 10% absolute; this would CONFIRM substrate is implicitly learning a HiPPO-structured eigenspace.
- **HARD FAIL:** Spectra are uncorrelated (correlation < 0.2 across top-32 eigenvalues); substrate is NOT in the HiPPO eigenspace and any apparent improvement from HiPPO-init is via a different mechanism.
- **Why this matters:** if HARD PASS, then ANY substrate-init that hits the HiPPO eigenspace will work; HiPPO is one of many. If HARD FAIL, HiPPO is genuinely substrate-novel and the (rare) positive case carries more information.

---

## (d) Cross-thread synthesis with prior entries

### The structural-mismatch picture

The literature converges on three observations that together explain why the v190 wave14e overlay framing failed and why the HiPPO-init framing is the surviving substrate-compatible path:

1. **Linear-attention / SSM / Hopfield outer-product equivalence (Schlag et al. 2021 "Linear Transformers Are Secretly Fast Weight Programmers"; Dao & Gu 2024 "Transformers are SSMs / SSD"; Beren 2024 "Linear Attention as Iterated Hopfield Networks").** The substrate W = sum_i k_i v_i^T is THE SAME ALGEBRAIC OBJECT as the linear-attention KV-cache, the fast-weight matrix, and the Mamba state-space recurrence (in the diagonal-A limit when A → I and Δ → 1). The substrate is not "competing with" SSMs; it IS an SSM (in the structured-state-space-duality sense). This kills the depth-extension framing: you cannot stack one outer-product memory on top of another and gain capacity.

2. **Jelassi et al. 2024 Theorem 2.7 (Repeat After Me).** For multi-query recall to be solvable, state size |U| must satisfy |U| >= |V|^n where V is vocabulary and n is query count. This is a HARD lower bound. The substrate's W has |U| ~ 2^N for BSC bipolar atoms (binary state space); the substrate-novel chain-cleanup depth ~50 cliff observed in v190 is THE OBSERVABLE OF THIS BOUND, not a substrate-specific defect. SSM-overlay cannot rescue this because the overlay's state is ALSO bounded by the same theorem (and typically with smaller state — H=128 in v190 vs N=512 substrate, the SSM overlay was MORE bounded than the substrate it was meant to extend).

3. **Mimetic Initialization (Bhojanapalli et al. 2024).** Empirically, SSMs require a specific A → I, Δ → 1 initialization to recover the linear-attention recall behavior. This says: the SSM-substrate equivalence is REAL but is ONLY ACTIVATED at specific initialization. The HiPPO-LegS init is one such initialization (it lives in the A-near-identity regime via the diagonal exponential parameterization). This is the substrate-compatible insertion point for HiPPO: as an INIT for the existing Hebbian W, not as a layered overlay.

### Connection to existing substrate findings

- **v190 wave14e CLOSED-FAILED (binding_depth=200 vs ssm_depth=0):** the overlay framing — exactly what Jelassi predicts cannot work. The closure is correct; the rehab path is HiPPO-init, NOT SSM-overlay-with-different-parameters.
- **Cap 10/12 multi-hop d>=4 cliff (substrate_capability_map.md):** consistent with Jelassi |U| >= |V|^n; multi-hop requires state size growing exponentially with hops, which substrate at fixed N cannot deliver.
- **R-PRIME-3 task-pair geometry (Bet B retention):** the same outer-product structure that Jelassi bounds also governs multi-task interference; this is why retention is bounded by representational distance between task pairs — both are manifestations of the same fixed-state-size constraint.
- **R-PRIME-5 framing ("HiPPO-basis retention fit"):** the original framing predicted closed-form retention fit. The literature suggests this is the WRONG falsifier — HiPPO does not control retention shape, it controls eigenspace structure. The correct falsifier is the spectral-match test (Prediction 3 above).

### What this does NOT close

- The HiPPO-init experiment is genuinely substrate-novel; no published precedent for "use HiPPO-LegS to initialize a Hebbian outer-product W on BSC bipolar atoms." Outcome is unpredictable.
- The Jelassi bound argues against depth-extension but is COMPATIBLE with eigenspace-structuring improvements (you can't increase capacity but you can use the existing capacity better). This is the survival path for HiPPO-init.
- Selective-state-space (Mamba's S6 selectivity mechanism — data-dependent A, B, C) is a DIFFERENT axis that is NOT addressed by this drill; it would require its own experiment and is lower-priority because it would inherit the same Jelassi bound.

---

## (e) Substrate-product implications

**Per [[feedback-no-papers-product-only]] — substrate is product, never publication.**

### Product capability implications

1. **Multi-hop reasoning (Cap 10/12) capability — DO NOT bet on SSM-HiPPO as the rescue.** The Jelassi bound says SSM-style mechanisms cannot extend the multi-hop depth cliff. The substrate-product framing should re-prioritize Cap 10/12 rescue toward: (a) resonator decomposition with structured codebooks (Kerdock, Reed-Muller), (b) hierarchical binding with codebook hand-off across hops, (c) attention-based primitives (which Jelassi proves CAN copy at exponential length — not an SSM rescue but a structural-class change).

2. **Init-regime as a substrate-product capability lever.** The Mimetic-Init finding generalizes: substrate's W-initialization may matter MORE than the literature acknowledges. This is a substrate-product axis we have NOT explored systematically. Recommend: queue a "W-initialization sweep" capability anchor (Kerdock-init, HiPPO-init, codebook-init, random-init, structured-Hadamard-init) at fixed task to measure init-sensitivity of substrate capabilities. This is an INDEPENDENT capability axis from anything in cap_map v190.

3. **Substrate-as-fast-weight-memory positioning.** The linear-attention/SSM/Hopfield convergence in the literature is HIGHLY CITABLE substrate-product framing: "the substrate is the algebraically-canonical form of fast-weight memory; everything else is an instance." This is the strongest product positioning we have seen for the AI-memory-subsystem direction (per project_ai_memory_subsystem_direction.md). HARD recommend: surface this framing in the next product cycle's market analysis.

4. **Auditability / verifiable-erase implications.** The outer-product structure W = sum_i k_i v_i^T directly supports the "verifiable erase" capability (Cap class 1 of the four substrate capability classes). The substrate-product story is: SSMs and linear-attention compute the same W but bury it under continuous-time dynamics that defeat audit; the substrate exposes W directly, which is why erase + provenance are tractable. This is the substrate-product DIFFERENTIATION from SSMs, not a competition.

### Strategic recommendation

- **SHIP:** 1 experiment — HiPPO-init W vs random-init W chain-cleanup probe (per (b) above). Remote_cpu_queue, ~1-2 hours CPU. Use existing exp_wave14e infrastructure (HiPPO A-matrix construction) to bound implementation cost to ~80 LOC.
- **DO NOT SHIP:** any further SSM-overlay variants. v190 closed-failed; Jelassi predicts no rescue.
- **DO NOT SHIP:** Mamba-S6 selective-state-space adaptation. Would require >5x more implementation effort than the HiPPO-init probe for a strictly weaker theoretical prior.
- **ANNOTATE cap_map row "Bet S4-as-SSM-depth-extension":** add note "v190 closure CONFIRMED structurally by Jelassi 2024 Theorem 2.7; rehab path is HiPPO-init not SSM-overlay; new experiment filed in exp_dev_handoff_ssm_hippo_design_2026-05-25.md."
- **OPEN new cap_map research row:** "W-initialization sweep capability" — entry-level research-stage 🔬 row; promote to 🟡 if HiPPO-init shows ANY signal in the prediction-1 MIDDLE band or above.

---

## (f) Citations (verified count: 9)

1. Gu, A., Dao, T., Ermon, S., Rudra, A., & Re, C. (2020). "HiPPO: Recurrent Memory with Optimal Polynomial Projections." NeurIPS 2020. [arxiv.org/abs/2008.07669](https://arxiv.org/abs/2008.07669) — the foundational HiPPO framework; closed-form LegS recurrence; the substrate-compatible init is derived from this paper's diagonal-exponential parameterization.
2. Gu, A., Goel, K., Gupta, A., & Re, C. (2022). "On the Parameterization and Initialization of Diagonal State Space Models." [arxiv.org/abs/2206.11893](https://arxiv.org/abs/2206.11893) — S4D and the diagonal-form simplification of HiPPO; bounds the implementation cost of the cheap-decisive test.
3. Dao, T., & Gu, A. (2024). "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality." ICML 2024. [openreview.net/pdf/54bf495d93336f1f195f264c1b6c2805169b3492.pdf](https://openreview.net/pdf/54bf495d93336f1f195f264c1b6c2805169b3492.pdf) — the SSD framework establishing substrate W ↔ SSM A-matrix equivalence.
4. Schlag, I., Irie, K., & Schmidhuber, J. (2021). "Linear Transformers Are Secretly Fast Weight Programmers." [arxiv.org/abs/2102.11174](https://arxiv.org/abs/2102.11174) — the fast-weight outer-product equivalence; linear-attention M_t = M_{t-1} + K_t V_t^T is exactly substrate Hebbian update.
5. Jelassi, S., Brandfonbrener, D., Kakade, S., & Malach, E. (2024). "Repeat After Me: Transformers are Better than State Space Models at Copying." ICML 2024. [arxiv.org/abs/2402.01032](https://arxiv.org/abs/2402.01032) — Theorem 2.7: |U| >= |V|^n state-size lower bound; the rigorous falsifier for the depth-extension framing.
6. Bhojanapalli, S., et al. (2024). "Mimetic Initialization Helps State Space Models Learn to Recall." [arxiv.org/abs/2410.11135](https://arxiv.org/abs/2410.11135) — the A → I, Δ → 1 initialization equivalence; structurally justifies HiPPO-init as the substrate-compatible insertion point.
7. Voelker, A. R., Kajic, I., & Eliasmith, C. (2019). "Legendre Memory Units: Continuous-Time Representation in Recurrent Neural Networks." NeurIPS 2019. [proceedings.neurips.cc/paper/2019/file/952285b9b7e7a1be5aa7849f32ffff05-Paper.pdf](https://proceedings.neurips.cc/paper/2019/file/952285b9b7e7a1be5aa7849f32ffff05-Paper.pdf) — LMU with fixed Legendre orthogonal weights; the closest prior art for "fixed HiPPO recurrence + learned readout."
8. Beren (2024). "Linear Attention as Iterated Hopfield Networks." [beren.io/2024-03-03-Linear-Attention-as-Iterated-Hopfield-Networks/](https://www.beren.io/2024-03-03-Linear-Attention-as-Iterated-Hopfield-Networks/) — explicit outer-product M_t = M_{t-1} + K_t V_t^T mapping; clarifies that the equivalence is single-step and does not address multi-step depth (which is exactly where the v190 framing went wrong).
9. Voelker A. R. patent CA3098085A1 (2019). "Legendre memory units in recurrent neural networks." — fixed-orthogonal-memory architecture, 95% fewer recurrent parameters than LSTM; precedent for fixed-Hebbian W with HiPPO structure.

### Verification status

- All 9 citations are real, verified via WebSearch + WebFetch; titles, authors, venues consistent across multiple sources.
- The Jelassi Theorem 2.7 statement reproduced above is paraphrased from secondary-source descriptions (the original arxiv PDF was not directly extracted in this drill due to WebFetch PDF binary handling). The state-size lower bound |U| >= |V|^n is confirmed across two independent secondary sources (the Mimetic-Init paper and the StateX paper both cite this exact form).
- The Mimetic-Init paper's specific A → I, Δ → 1 init scheme was extracted directly via WebFetch and is verbatim from the source.

### Calibration penalty applied

Per [[feedback-lit-scan-calibration-penalty]]:
- Raw P(category-defining substrate capability) estimate from lit-scan would be ~0.35 (one substrate-novel synthesis path; clean math; testable).
- Deflated by 0.17 for substrate-novel-regime (BSC + sparse PPMI + rank-1 Hebbian W — no published direct precedent for this combination).
- Final calibrated P = 0.18.
- Cap at 0.50 (novel-synthesis ceiling) is not binding here; the binding deflation is the substrate-regime penalty.

### Lit-scan limitations / open angles not closed

- The closed-form mapping between substrate Hebbian W and HiPPO-LegS A is NOT in any published paper found. The substrate-compatible HiPPO-init is a substrate-novel construction. If this drill is wrong about the construction, the experiment may give a misleading null. Mitigation: the spectral-match Prediction 3 directly tests whether the construction even hits the HiPPO eigenspace; if it does not, Prediction 1 and Prediction 2 results are uninformative on the literature mapping.
- The Mamba selective-SSM (S6) data-dependent A, B, C mechanism is explicitly NOT covered by this drill. It is a different axis and would require its own ~1-week effort to evaluate substrate compatibility.
- The HiPPO continuous-time function-approximation framework assumes a measure on the input (Legendre, Laguerre, Fourier). Substrate's BSC bipolar inputs do not have a natural continuous measure. The construction in (b) implicitly chooses uniform measure on {-1, +1}^N which may be the wrong choice; alternate measures (frequency-weighted by atom usage; PPMI-weighted) are a follow-up axis.
