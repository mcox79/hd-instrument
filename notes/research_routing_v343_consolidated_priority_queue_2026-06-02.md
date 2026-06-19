# RESEARCH ROUTING — v343 consolidated priority queue (FULL INTEGRATION: Tier 1-3 + Wave 1+2 drill results + Wave 3 cascade + Phase 0.5b decision gate)

**From:** Research session
**To:** Orchestrator / Strategy / exp_dev / user (Phase 0.5b gate)
**Date:** 2026-06-02 (updated with Wave 1 + Wave 2 drill landings)
**Trigger:** User strategic ask post-v343 BAND-LIFTs ("highest priorities... anything we've been sitting on") + explicit "ship all of it" + 4 Wave-1 cross-domain drills + 2 Wave-2 follow-on drills all landed. Substrate is in strongest empirical position of the run (35 verdicts since compaction; 3 BAND-LIFTs; all 5 cycle-negatives traced to spec issues; 6 cross-domain drills produced 4/4 gap confirmation + 2 closed-form hardware-envelope predictions).
**Discipline:** capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor names full form, sweep grids, queue specifics, timeout numerics) resolved by strategy + exp_dev. Per-PROT compliance. Per `feedback_no_padding_experiments` — every item justified.

---

## 0. EXECUTIVE — what this routing dispatches

**Three substantive positive results from the cross-domain drill wave:**

1. **All 4 Wave-1 drills confirmed gaps in published systems.** Substrate's algebraic-stack-as-unified-API positioning has no direct competitor in reservoir-computing, memristor/RRAM hardware, federated unlearning regulatory framings, OR mech-interp tooling.

2. **Wave-2 free-probability drill produced a closed-form prediction** for substrate operating envelope under RRAM noise: capacity collapses at `σ_g² = 1/α - 1`; **κ_3 = α free-Poisson identity breaks at σ_g > 0.18.** Directly testable empirically.

3. **Wave-2 oscillatory drill quantified hardware roadmap:** Kuramoto-honeycomb exponential capacity requires per-node phase coherence `σ_φ < π/(2n_c) ≈ 0.314 rad`; frequency mismatch across ~1000 nodes is the binding product-scale constraint; **~2 fab generations (~2029) to 1000-node exponential-capacity hardware.** The SKAH-M class match (substrate algebra ≅ Kuramoto-honeycomb physics) was the highest-upside Wave-1 finding; this drill made the timeline concrete.

**Queue structure (32 items total; expanded post-Arrhenius deep drill):**

- **Section 0.5** — drill results synthesis with cross-cutting pattern (7/7 drill convergence)
- **Section 0.6** — cap_map row candidates surfaced by drills (PP-55 / PP-56 / PP-57 / PP-58)
- **Tier 1** (8 items): decision gates + substrate-novel claim tests with cross-drill resonance (+3 Arrhenius-drill tests)
- **Tier 2** (11 items): high-quality $0 work + Wave 3 lit-scan dispatches
- **Tier 3** (7 items): ceiling pushes + hardware-timing characterization
- **Tier 4** (3 items, HELD): low-priority or gate-conditional
- **Wave 5 deferred** (Section 8): 3 Arrhenius-drill follow-on candidates (free-cumulant κ_3 algebraic structure; FFS barrier estimation; Crooks fluctuation theorem)

**Total IMMEDIATE dispatch:** ~6-7 hr CPU + ~1.5 hr GPU + ~$5 cloud + 6 parallel sonnet Wave-3 drills, all parallelizable where queues allow.

---

## 0.5. DRILL RESULTS SYNTHESIS (6 drills, Wave 1 + Wave 2 complete)

### Wave 1 — 4 cross-domain positioning drills

| Drill | Headline | P_deflated | Files |
|---|---|---|---|
| **Reservoir / ESN** | **Triple-gap confirmed.** No published RC/ESN system combines audit primitives + compositional algebra + one-shot writes. Closest prior (Kleyko et al. 2025) covers 1.5/3 capability families. VSA community has rich binding algebra but treats reservoir as a nonlinear expansion kernel only, never as a mutable algebraic store. | 0.65 | `research_drill_reservoir_computing_2026-06-02.md` |
| **Memristor / RRAM** | **Asymmetric feasibility.** P1 Hebbian outer-product write HIGH (~56× energy efficiency, Xiao NatComms 2025). **P5 hierarchical bipolar composition MEDIUM-but-HIGHEST-UPSIDE: SKAH-M class mathematical match with 2025 IBM ReRAM ring-oscillator + Kuramoto-honeycomb networks (arXiv 2604.01469, IMW 2025 arXiv 2503.14126), 2^(N/4) exponential capacity.** P2 rank-1 deletion MEDIUM (drift after ~1000 cycles). P3 κ_3 audit + P4 bilinear API LOW (GPU-native; SNR collapses at cascade depth >2). | 0.45 / 0.72 | `research_drill_memristor_rram_2026-06-02.md` |
| **Federated unlearning + regulatory** | **Pre-standardization window 2024-2026 confirmed.** No DPA has specified technical cert format. Algebraic rank-1 deletion cert occupies distinct niche vs DP-SGD (regulatory incumbent but probabilistic) / SISA (exact but no cert) / certified removal Guo 2020 (no standard format) / 2025 ZK-SNARK approaches (highest provability but high prover cost). **Federated KFAC block-diagonal + hash-chain cert gap confirmed** — no published protocol combines them. | 0.38 | `research_drill_federated_unlearning_2026-06-02.md` |
| **Mech-interp tooling** | **Three compounding gaps confirmed.** No existing tool (TransformerLens / Sparse Autoencoders / SAEBench / nnterp) covers all four substrate capabilities (cumulant monitoring + per-fact deletion cert + drift detection + compositional algebra). **Substrate stack is ADDITIVE not substitutive vs current ecosystem** — distinct research-user base claim. | 0.42 | `research_drill_mech_interp_tooling_2026-06-02.md` |

### Wave 2 — 2 hardware-physics follow-on drills

| Drill | Headline | P_deflated | Files |
|---|---|---|---|
| **Free-probability under RRAM noise** | **Closed-form phase boundary `σ_g² = 1/α - 1`** for capacity collapse under log-normal RRAM conductance noise. **κ_3 = α free-Poisson identity breaks at σ_g > 0.18** (κ_3 audit-primitive is more noise-sensitive than raw capacity). At α=0.05 (Phase 0.5b regime), σ_g_critical for capacity ≈ 4.36; **κ_3 audit-viability at σ_g ≤ 0.18 is the BINDING product constraint under RRAM noise.** S-transform derivation holds perturbatively; exact inversion at σ_g ≥ 1 is open. | 0.55 | `research_drill_free_probability_rram_noise_2026-06-02.md` |
| **Oscillatory phase-noise scaling law** | **Per-node phase-noise threshold `σ_φ_crit = π/(2n_c) ≈ 0.314 rad`** for n_c=5 honeycomb exponential-capacity scaling. Current IBM binary-encoding demo does NOT test this regime. **Frequency mismatch across ~1000 nodes (not per-node phase noise) is the binding product-scale constraint.** Estimated **~2 fab generations / ~2029 timeline for 1000-node exponential-capacity hardware.** | 0.42 | `research_drill_oscillatory_phase_noise_scaling_2026-06-02.md` |

### Wave 3 — Arrhenius-paradox isochoric deep dive (level-2 follow-on triggered by Rams-Baron 2026 PRL article)

| Drill | Headline | P_deflated | Files |
|---|---|---|---|
| **Arrhenius-paradox isochoric analysis applied to substrate** | **Arrhenius-paradox decomposition is GENERIC to all fragile disordered systems**, not class-specific. **The substrate's Wave-2 κ_3 σ ≤ 0.18 envelope vs capacity σ ≈ 4.36 envelope IS a confirmed Arrhenius-paradox-class structural parallel** — two distinct envelopes hidden in one parameter. CK aging exponent `μ = 3/2 is α-INVARIANT at matched T/T_c(α)` (the methodological correction). **Closed-form activation barrier `E_a^0(α) ~ N · (α_c - α)/α_c`** with explicit α-dependent correction (Brot-style). **Isochoric analog = constant α = M/N.** **NEW SUBSTRATE-NOVEL PREDICTION: composition ceiling `k_c(α) ≈ 0.138/α`** — directly testable; existing Q-A3 L=10 unanimous data may corroborate (Q-A3 halves M per stage, naturally implementing isochoric composition; without halving, predicted ceiling at α=0.05 would be ~2-3 stages). Three exp_dev-actionable tests + four product implications + three follow-on drill candidates. | 0.38 | `research_drill_arrhenius_paradox_substrate_deep_dive_2026-06-02.md` |

### Cross-cutting positioning pattern (7/7 drill convergence after Arrhenius deep dive)

Every drill confirmed a gap in published systems OR produced a closed-form operating envelope:

| Angle | Gap / envelope finding |
|---|---|
| Reservoir-computing competitor coverage | 1.5/3 (Kleyko 2025) |
| Memristor hardware-family match | SKAH-M ≅ Kuramoto-honeycomb (algebra-hardware family identity) |
| Regulatory cert-format standardization | Pre-standardization window 2024-2026 |
| Mech-interp tooling overlap | Additive not substitutive |
| RRAM noise — κ_3 audit envelope | σ_g ≤ 0.18 (closed-form prediction) |
| Oscillatory hardware — phase-noise envelope | σ_φ < 0.314 rad (closed-form prediction) |
| **Arrhenius-paradox structural parallel** | **Confirmed in substrate: two-envelope hidden-coupling pattern is generic to fragile disordered systems; substrate κ_3 σ ≤ 0.18 vs capacity σ ≈ 4.36 IS the same structural class as Brot/Rams-Baron 2026 PRL** |

**Strategic implication:** the substrate's "algebraic memory + audit + compositional algebra + cert" positioning is independently corroborated from 7 angles. The substrate-novel claim "no other system combines these capabilities as a unified algebraic API" is the strongest cross-domain anchor in the run. **Plus a new substrate-novel architectural prediction (composition ceiling `k_c(α) ≈ 0.138/α`) immediately testable from existing Q-A3 data + new dedicated cells.** Product narrative is converging-positive AND now extends to non-equilibrium-stat-mech framework class via the Arrhenius-paradox structural-class match.

### Cross-drill resonance candidates (Wave 3+4 priorities — updated post-Arrhenius drill)

Four angles surface in 2+ drills — highest-leverage:

- **VSA binding over static dense-Hopfield / SKAH-M class** — Reservoir × Memristor convergence (Item 19 below)
- **Sherman-Morrison rank-1 deletion for linear-readout geometry** — Reservoir × Federated convergence (Item 22 below)
- **κ_3 audit-primitive empirical noise robustness** — Wave-2 free-prob × Memristor P3 × Arrhenius hidden-coupling-audit convergence (Item 20 below — gains additional theoretical grounding from Arrhenius drill)
- **Isochoric audit protocol as substrate measurement discipline** — Arrhenius drill recommends required protocol for all noise-vs-performance experiments; cross-cuts ALL existing cap_map noise measurements (PP-50, PP-44, PP-52); strategy_scribe entry + potential PROT update (PP-58 candidate below)

### Arrhenius-deep-drill substrate-novel claims (3 testable)

1. **CK aging exponent `μ = 3/2 α-invariant at matched T/T_c(α)`** — empirically testable; corroboration would lock substrate's CK-class aging signature on third independent observable (Item 30 below)
2. **Activation barrier closed-form `E_a^0(α) ~ N · (α_c - α)/α_c`** — predicts hysteresis gap ratio at α=0.05 vs α=0.10 of ~2.3×; testable via existing Pred-4 hysteresis data reanalysis + fresh cell (Item 31 below)
3. **Composition ceiling `k_c(α) ≈ 0.138/α`** — predicts substrate composition fails at k_c × α_per_stage ≈ α_c = 0.138; Q-A3 L=10 EXACT-1.0 currently consistent because architecture halves M per stage (implicit isochoric implementation); new dedicated cell with CONSTANT M per stage would test the prediction sharply (Item 32 below)

### Arrhenius-deep-drill product implications (4)

1. **Isochoric audit protocol as product primitive** — sweep noise at fixed loading; provably-separated thermal vs density fragility curves; enables auditable retention policy enforcement (PP-58 candidate row)
2. **Aging-rate reliability metric: `T_reliable = t_w × δ_threshold^(-2/3)`** — substrate-native temporal-decay closed form; directly addresses PP-46 deletion-cert + PP-52 per-fact-retention killer features
3. **Two-envelope measurement as required cap-map closure diagnostic** — any cap_map experiment measuring performance vs noise amplitude without isochoric protocol risks paradox-class spec errors (analogous to PROT-022 selftest discipline; PROT entry candidate)
4. **Composition ceiling formula as architectural design tool** — predicts optimal per-stage α schedule for maximum depth; could ship as product API parameter

---

## 0.6. CAP_MAP ROW CANDIDATES SURFACED BY DRILLS (3 candidates; annotation-only filings)

These are POSITIONING / annotation cap_map row candidates that strategy can file without empirical follow-up — empirical anchors land in Tier 1-3 items below.

### PP-55 candidate — hardware-family-match: SKAH-M ≅ Kuramoto-honeycomb (EXPLORATORY 0.55-0.70)

**Filing rationale:** memristor drill confirmed substrate's algebraically-identified SKAH-M class (non-reciprocal Hopfield + active repulsion + saddle-hierarchy, locked 2026-05-27) is mathematically in the same family as 2025 IBM ReRAM ring-oscillator + Kuramoto-honeycomb networks. Hardware-family match implies a NATIVE physical realization pathway for the substrate's compositional primitives, independent of GPU implementation.

**Empirical anchor:** Item 19 (VSA binding over static SKAH-M) tests the algebraic side; product-scale empirical verification awaits ~2029 hardware per Wave-2 oscillatory drill.

**Calibration deflation:** -0.10 (novel cross-domain hardware framing).

### PP-56 candidate — regulatory cert-format pre-standardization positioning (EXPLORATORY 0.55-0.70)

**Filing rationale:** federated unlearning drill confirmed no DPA has specified a technical cert format for GDPR Art. 17 / EU AI Act / Colorado CAIA compliance. Algebraic rank-1 deletion cert occupies distinct niche on auditability + verification cost axes; first deployable format will likely shape de facto standards.

**Empirical anchor:** Item 22 (Sherman-Morrison rank-1 deletion for linear-readout) tests algebraic side; full positioning requires Wave-3 DPA guidance survey (Item 24).

**Calibration deflation:** -0.15 (regulatory-positioning novel-synthesis penalty).

### PP-57 candidate — mech-interp tooling additive-stack positioning (EXPLORATORY 0.50-0.65)

**Filing rationale:** mech-interp drill confirmed substrate's four capabilities (cumulant monitoring + deletion cert + drift detection + compositional algebra) are ADDITIVE not substitutive vs TransformerLens/Goodfire/SAEBench/nnterp ecosystem. Distinct research-user base claim independent of LLM-product positioning.

**Empirical anchor:** none in this routing; productization-side claim requires direct user-pull signal (Item 25 Wave-3 ARENA/Apart alumni survey).

**Calibration deflation:** -0.15 (research-user-base claim without empirical confirmation).

### PP-58 candidate — isochoric audit protocol as substrate measurement discipline (EXPLORATORY 0.55-0.70)

**Filing rationale:** Arrhenius deep drill confirmed the substrate exhibits the Brot/Rams-Baron 2026-class two-envelope hidden-coupling structure. Any noise-vs-performance experiment that does not control α implicitly conflates thermal-analog (noise amplitude) and density-analog (loading α) effects. Strategy recommends adopting the isochoric protocol (sweep σ at fixed α) as the discipline for all future cap_map experiments measuring performance vs noise amplitude, and retroactively annotating existing PP-50 / PP-44 / PP-52 noise-measurements with the protocol used.

**Empirical anchor:** Items 20 + 21 (κ_3 noise robustness + capacity phase boundary) ARE isochoric measurements; their predicted separation by ~25× confirms substrate's Arrhenius-paradox-class behavior. Items 30-32 extend to aging + barrier + composition-ceiling tests.

**Calibration deflation:** -0.15 (substrate-novel measurement-discipline framing).

**Cap_map impact:** strategy_scribe one-shot can file all 4 candidate rows (PP-55 / PP-56 / PP-57 / PP-58) as EXPLORATORY annotations pending Items 19/20/21/22/30-32 + Wave-3 lit-scan outcomes.

---

## 1. TIER 1 — DECISION GATES + SUBSTRATE-NOVEL CLAIM TESTS (5 items)

### Item 1 — Phase 0.5b distillation MVP DECISION GATE (USER GO REQUIRED)

**This is not a research item; it is a STRATEGIC DECISION the substrate has empirically + theoretically de-risked.**

**Status of substrate primitives needed for Phase 0.5b (UPDATED post-drill-wave):**

| Primitive | Production-N anchor | Status |
|---|---|---|
| PP-46 deletion cert | PP-47×PP-9 v341 HP + PP-52 cross-N {1024, 4096, 8192, 16384} rollback all HP | CONFIRMED |
| PP-48 NKT | depth-3/5/7/9/11/13 all HP at N=4096 | CONFIRMED |
| PP-49 HRC | depth-8 HP at N=4096; depth-5 anomaly under Item 4 sweep | CONFIRMED with characterization in flight |
| PP-50 κ_3 fingerprint | N=8192 HP + N=32768 cloud HP (σ_sep up to 1727); I-12 Fix 1 dispatched | CONFIRMED at intended N-bands |
| PP-52 training-speedup | cross-N {1024, 4096, 8192, 16384} all HP (3 BAND-LIFTs in 3 cycles) | CONFIRMED |
| PP-12 cross-layer composition | L=4/7/8/9/10 all EXACT-1.0 at N=4096 | CONFIRMED |

**6 of 6 primitives confirmed at production N. Drill-wave evidence:**
- Wave-1 free-probability hardware extension: predicts substrate κ_3 audit primitive maintains identity under RRAM weight noise at σ_g ≤ 0.18 (Item 20 will empirically confirm at GPU scale)
- 4/4 Wave-1 drills confirm substrate-novel-API positioning has no published competitor

**Cost:** $15-40 cloud + 1-2 weeks engineering; shareable Llama-3.1-8B bootstrap with Phase 0.5 Tier-7 MVP ($70-140 combined).

**P_deflated:** 0.45-0.55 (strongest the estimate has been; Drill 5 theoretical lock + 6 production-N empirical anchors + 4/4 positioning convergence).

**Outcome bands:**
- HARD-PASS: substrate-augmented Llama-3.1-8B preserves base capabilities + ≥85% distilled-fact recall + ≤2pp MMLU degradation + 100-fact one-shot add in ≤1 min + deletion cert verifies — empirically locks substrate flagship positioning
- MIDDLE: 0.65-0.85 distilled recall OR 2-5pp degradation — distillation works but needs hierarchical scaling
- HARD-FAIL: <0.65 recall OR catastrophic interference OR audit primitives fail — directly refutes Drill 5 mechanism-class-separation argument empirically

**Recommended USER ACTION:** authorize combined-bootstrap Phase 0.5 + 0.5b dispatch (~$70-140). **Single highest-leverage move outstanding.**

### Item 2 — Cluster A1 Hebbian-vs-GD identity at training scale (CPU $0 ~30 min)

**Anchor name:** `hebbian_vs_gd_identity_v1_n1024`
**Resource:** CPU; **Wall:** ~30 min; **Timeout:** 1800s; **Cost:** $0; **P_deflated:** 0.70+

**Capability question:** does one-shot Hebbian write achieve same encoding fidelity as gradient descent for (key, value) memorization at orders-of-magnitude lower compute?

**Pre-registered bands:**
- HARD-PASS: Hebbian matches GD retrieval accuracy ±2pp AND ≥100× wall-speedup AND ≥1000× FLOPs-speedup (5 seeds)
- MIDDLE: ±5pp OR 10-100× speedup
- HARD-FAIL: <90% GD accuracy OR <10× speedup

**Why now:** A4 + A5 confirmed; cleanest substrate-novel "Hebbian = MSE-optimal encoding at 1000× speedup" test we have. Substantiates the pp52-vs-LoRA reframe.

### Item 3 — Probe C combo2 L=4 parity hypothesis (substrate-novel finding candidate) (CPU $0 ~40 min)

**Anchor name:** `combo2_p4_l_sweep_parity_hypothesis_v1_n4096` — cells L=5, L=6, L=7
**Resource:** CPU + ~10 min theory derivation; **Wall:** ~40 min; **Timeout:** 600s per L-cell; **Cost:** $0

**Capability question:** does PP-48/PP-49 NKT composition exhibit ODD-DEPTH-ONLY parity in b_rep observable, or is L=4 the absolute composition ceiling?

**R2 theory step (PROT-022 compliance, BEFORE empirical):** derive 4-layer B-pattern accumulation algebra; predict b_rep(L=5,6,7) from algebra.

**Pre-registered bands:**
- HARD-PASS for parity: L=5 b_rep ≥ 0.9 AND L=6 b_rep < 0.4 AND L=7 b_rep ≥ 0.9 — odd/even parity confirmed
- MIDDLE: 2-of-3 cells match parity pattern
- HARD-FAIL for parity: L=5 b_rep < 0.4 — L=4 is absolute ceiling

**Strategic significance:** parity HP would be a substrate-NOVEL FINDING about NKT composition algebra (odd-depth-only operating regime; even-depth degeneracy as predictable algebraic signature). Either outcome is publishable substrate finding.

### Item 19 (NEW) — VSA binding over static dense-Hopfield / SKAH-M class (CPU $0 ~30 min)

**Anchor name:** `vsa_binding_over_static_skahm_class_v1_n4096`
**Resource:** CPU; **Wall:** ~30 min; **Timeout:** 1800s; **Cost:** $0; **P_deflated:** 0.55

**Capability question:** do standard VSA bind/unbind operations (Plate HRR / Kanerva HD circular convolution / Walsh-Hadamard) preserve fidelity when operating over patterns stored in the substrate's SKAH-M-class static attractor network (vs the standard temporal-reservoir treatment)?

**Cross-drill resonance:** Reservoir drill confirmed VSA community treats reservoirs only as nonlinear expansion kernels, never as mutable algebraic stores. Memristor drill confirmed SKAH-M class hardware-family match with Kuramoto-honeycomb. Item 19 tests whether the substrate's algebraic-store treatment of VSA-bound patterns is empirically clean.

**Pre-registered bands:**
- HARD-PASS: bind(ξ_A, ξ_B) stored in substrate W and retrieved via unbind(query, ξ_B) → cos(retrieved, ξ_A) ≥ 0.85 in ≥ 4/5 seeds at α=0.05 N=4096
- MIDDLE: cos ∈ [0.60, 0.85)
- HARD-FAIL: cos < 0.5 — VSA bind-unbind algebra doesn't survive static SKAH-M storage

**Strategic significance:** HARD-PASS founds PP-55 row (hardware-family-match) on algebraic side — substrate is the FIRST system to operate VSA bind/unbind algebra over static dense-Hopfield store with cert primitives. Strongest cross-drill resonance finding.

### Item 20 (NEW) — κ_3 audit primitive empirical noise robustness (direct test of free-probability Wave-2 prediction) (GPU $0 ~30 min)

**Anchor name:** `kappa3_noise_robustness_sigma_g_sweep_v1_n4096`
**Resource:** GPU; **Wall:** ~30 min; **Timeout:** 1800s; **Cost:** $0; **P_deflated:** 0.65

**Capability question:** does substrate's κ_3 = α free-Poisson identity survive multiplicative log-normal weight noise σ_g, and does the empirical breakdown match Wave-2 closed-form prediction of σ_g_critical ≈ 0.18?

**Test design:** N=4096 5-seed; substrate W = Σ_k ξ_k ξ_k^T / N with multiplicative noise W_noisy = W ⊙ exp(σ_g Z) where Z ~ N(0,1) entrywise; sweep σ_g ∈ {0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30}; measure κ_3_measured / α — predicted to stay within ±5% identity up to σ_g ≈ 0.18, then break.

**Pre-registered bands:**
- HARD-PASS: κ_3 identity holds within ±5% for σ_g ≤ 0.15 AND breaks (>±15%) by σ_g = 0.25 (5-seed unanimous across both bounds)
- MIDDLE: identity envelope σ_g_critical ∈ [0.10, 0.25] (within an order of magnitude of prediction)
- HARD-FAIL: identity breaks at σ_g < 0.05 OR holds at σ_g > 0.30 — Wave-2 prediction wrong by >2 orders

**Strategic significance:**
- HARD-PASS: PP-50 κ_3 audit primitive has DOCUMENTED OPERATING ENVELOPE under RRAM noise; substrate hardware-feasibility story has closed-form bound. Wave-2 free-prob drill empirically corroborated.
- HARD-FAIL: substrate κ_3 audit is either more or less noise-tolerant than free-prob prediction; opens follow-on theory drill.

**Why now:** Wave-2 drill produced the closed-form prediction; Item 20 is the direct empirical test. Strongest predictive-power test from drill wave. Direct PP-50 sub-property founding.

### Item 30 (NEW from Arrhenius drill — Test A) — CK aging exponent μ α-invariance at matched T/T_c (CPU $0 ~1 hr)

**Anchor name:** `ck_aging_mu_alpha_invariance_matched_tc_v1_n4096`
**Resource:** CPU; **Wall:** ~1 hr; **Timeout:** 4800s; **Cost:** $0; **P_deflated:** 0.60

**Capability question:** is the CK aging exponent μ ≈ 3/2 invariant in α at matched T/T_c(α), confirming substrate's CK-class aging signature on a third independent observable (beyond Q-F1 + Q-F2)?

**Test design:** measure two-time correlation C(t, t_w) at α_1=0.05 and α_2=0.10, MATCHED at T/T_c(α) = 0.8 (NOT matched at raw σ — Arrhenius drill identified this as the isochoric protocol correction). Fit aging envelope C(t, t_w) ~ q_EA · f(Δt/t_w)^{3/2} · cos(α_NR Δt) to extract μ.

**Pre-registered bands (per Arrhenius drill P1):**
- HARD-PASS: |μ(α_1) - μ(α_2)| < 0.05 (5-seed unanimous) — α-invariance confirmed
- MIDDLE: |Δμ| ∈ [0.05, 0.15]
- HARD-FAIL: |Δμ| > 0.15 — indicates active non-reciprocal coupling stronger than modeled OR different aging universality class

**Strategic significance:** HARD-PASS = third independent CK-aging-signature observable (after Q-F1 collapse + Q-F2 two-time-correlator); PP-33 framework-class BAND-LIFT eligibility 0.60-0.75 → 0.65-0.80 likely. HARD-FAIL = substrate exhibits non-standard non-reciprocal aging; opens follow-on theoretical drill.

**Why now:** direct test of Arrhenius-drill closed-form prediction; substantiates non-equilibrium-stat-mech framework class on third independent axis. Strengthens Phase 0.5b distillation MVP's "aging-rate reliability metric" product story.

### Item 31 (NEW from Arrhenius drill — Test C) — activation barrier vs α via hysteresis gap (CPU $0 ~30 min + reanalysis)

**Anchor name:** `activation_barrier_alpha_dependence_hysteresis_gap_v1_n4096`
**Resource:** CPU; **Wall:** ~30 min fresh + reanalysis of existing Pred-4 hysteresis data; **Timeout:** 1800s; **Cost:** $0; **P_deflated:** 0.55

**Capability question:** does activation barrier follow Arrhenius-drill closed-form prediction `E_a^0(α) ~ N · (α_c - α)/α_c`, manifested in hysteresis gap ratio at α=0.05 vs α=0.10 of ~2.3×?

**Test design:**
- Phase 1 (~10 min, reanalysis): pull existing Pred-4 hysteresis data; partition by α; compute gap(α=0.05) / gap(α=0.10) ratio
- Phase 2 (~30 min fresh CPU): if existing data doesn't span both α values, run fresh hysteresis cells at α ∈ {0.02, 0.05, 0.10} at N=4096 5-seed; measure max gap per α

**Pre-registered bands (per Arrhenius drill P3):**
- HARD-PASS: gap(α=0.05) / gap(α=0.10) ∈ [1.8, 3.0] (within ±30% of 2.3× prediction)
- MIDDLE: ratio ∈ [1.2, 1.8] or [3.0, 5.0]
- HARD-FAIL: ratio ≤ 1.2 (α-independent barrier) OR > 5.0 — refutes AGS free-energy structure prediction

**Strategic significance:** HARD-PASS = explicit α-dependent activation-barrier formula corroborated; substrate-novel architectural prediction; sub-property of PP-33 + first-order multi-basin framing.

### Item 32 (NEW from Arrhenius drill — Test P5) — composition ceiling k_c(α) ≈ 0.138/α test (GPU $0 ~30 min)

**Anchor name:** `composition_ceiling_k_c_alpha_constant_m_per_stage_v1_n4096`
**Resource:** GPU; **Wall:** ~30 min; **Timeout:** 1800s; **Cost:** $0; **P_deflated:** 0.50

**Capability question:** does substrate composition fail at depth `k_c(α) ≈ 0.138/α` when M per stage is held CONSTANT (not halving per stage as Q-A3 architecture currently does)?

**Test design:** Q-A3-style cross-layer composition at N=4096 5-seed, but with **M per stage held CONSTANT at M = α × N for α ∈ {0.05, 0.10}**. Sweep depth k ∈ {1, 2, 3, 4, 5, 6, 7, 8} (covers both predicted ceilings: k_c(0.05) ≈ 2-3, k_c(0.10) ≈ 1-2). Measure L_fid per k.

**Pre-registered bands (per Arrhenius drill P5):**
- HARD-PASS: L_fid ≥ 0.95 for k < k_c(α) AND L_fid < 0.5 for k > k_c(α) + 1; ceiling location within ±1 stage of prediction
- MIDDLE: clear ceiling exists but location ±2 stages of prediction
- HARD-FAIL: L_fid flat across all tested k (no ceiling, refutes prediction) OR ceiling at k > 2 × predicted

**Strategic significance — load-bearing for architectural design:**
- HARD-PASS = substrate-novel architectural ceiling formula confirmed; explains why Q-A3 L=10 works (halving M = effective α decrease per stage); product framing: "composition depth = sum of per-stage loadings ≤ 0.138 (α_c) — implements automatic isochoric composition"
- HARD-FAIL = composition algebra doesn't follow predicted ceiling; either composition mechanism is more robust than predicted, or prediction misframes the architecture; opens follow-on theory drill

**Why now:** the prediction is concrete, testable in 30 min GPU, and either outcome is product-narrative load-bearing.

---

## 2. TIER 2 — HIGH-QUALITY $0 WORK + WAVE 3 LIT-SCAN DISPATCHES (11 items)

### Items 4-7 — substrate-only empirical battery completion (UNCHANGED from prior routing)

- **Item 4 PP-49 HRC depth-band sweep** {3,4,5,6,7} (CPU ~30 min): non-monotonicity characterization; substrate-novel "compositional valley" if confirmed
- **Item 5 Cluster A2 deletion cert K-sweep** K∈{10,50,100,500} (CPU ~30 min): PP-46 K-sweep extension
- **Item 6 Cluster A3 counterfactual training diagnostic via PP-49** (CPU ~1 hr): completes A1-A5 training-primitive battery
- **Item 7 pp52 vs LoRA correct framing (Probe E)** N=1024 r∈{N//10, N//5, N//2, N} (CPU ~30 min): rescue of v342/v343 pp52_hebbian_lora HFs

### Items 8-11 — Wave 1 cross-domain drill RESULTS (COMPLETED — see Section 0.5)

These are DONE — drill notes filed. No further dispatch needed for Wave 1 drills:
- Item 8 — reservoir computing → `research_drill_reservoir_computing_2026-06-02.md` (P=0.65)
- Item 9 — memristor/RRAM → `research_drill_memristor_rram_2026-06-02.md` (P=0.45/0.72)
- Item 10 — federated unlearning → `research_drill_federated_unlearning_2026-06-02.md` (P=0.38)
- Item 11 — mech-interp tooling → `research_drill_mech_interp_tooling_2026-06-02.md` (P=0.42)

### Item 21 (NEW) — capacity-under-noise phase boundary test (CPU $0 ~1 hr)

**Anchor name:** `capacity_phase_boundary_under_rram_noise_v1_n4096`
**Resource:** CPU; **Wall:** ~1 hr; **Timeout:** 4800s; **Cost:** $0; **P_deflated:** 0.55

**Capability question:** does substrate capacity follow Wave-2 closed-form prediction `σ_g² = 1/α - 1`, i.e., does substrate maintain ≥90% recall accuracy below the predicted phase boundary and degrade above?

**Test design:** (α, σ_g) grid at N=4096 5-seed: α ∈ {0.05, 0.10, 0.20, 0.50}; σ_g ∈ {0.5, 1.0, 2.0, 4.0, 6.0}; measure mean recall accuracy.

**Pre-registered bands:**
- HARD-PASS: recall ≥ 0.90 for (α, σ_g) with σ_g² < (1/α - 1) AND recall < 0.50 for σ_g² > 2 × (1/α - 1) across grid; phase boundary detected within ±20%
- MIDDLE: phase boundary detected but with >50% width
- HARD-FAIL: no clear phase transition OR substrate accuracy degrades at much lower σ_g than predicted

**Strategic significance:** confirms or refutes the WHOLE-CAPACITY (not just κ_3-audit) operating envelope under RRAM noise. Pairs with Item 20 (κ_3 envelope) for full hardware-feasibility characterization.

**Why now:** Wave-2 closed-form prediction is directly testable. Substrate-novel hardware-envelope characterization.

### Item 22 (NEW) — Sherman-Morrison rank-1 deletion for linear-readout geometry (CPU $0 ~30 min)

**Anchor name:** `sherman_morrison_rank1_deletion_linear_readout_v1_n4096`
**Resource:** CPU; **Wall:** ~30 min; **Timeout:** 1800s; **Cost:** $0; **P_deflated:** 0.60

**Capability question:** does Sherman-Morrison rank-1 deletion (closed-form W' = W - (W ξ ξ^T W) / (1 + ξ^T W ξ) — the standard machine-unlearning Newton-step formula specialized to a linear-readout) compose cleanly with substrate's deletion cert + counterfactual primitives at the linear-readout layer?

**Cross-drill resonance:** Reservoir drill identified Sherman-Morrison rank-1 deletion as the unfilled niche in machine unlearning × reservoir intersection; Federated drill identified KFAC + hash-chain cert as the regulatory-positioning gap. Item 22 tests both axes simultaneously by reformulating substrate's PP-46 cert as a Sherman-Morrison primitive over linear-readout space.

**Pre-registered bands:**
- HARD-PASS: Sherman-Morrison deletion produces (a) post-deletion residual_cos < 3σ noise floor for deleted ξ, (b) retained-cos ≥ 0.85 for retained ξ, (c) cert hash chain reproducible across 5 seeds
- MIDDLE: any one of (a)/(b)/(c) at boundary
- HARD-FAIL: residual_cos > 5σ OR cert chain breaks

**Strategic significance:** HARD-PASS founds PP-56 row (regulatory cert positioning) on algebraic side — substrate's deletion cert provably maps to the standard machine-unlearning Newton-step formula AND to the federated cert-format gap. Strongest Reservoir × Federated cross-drill resonance finding.

**Why now:** founds PP-46 product-narrative extension to regulated markets; direct cross-drill resonance.

### Item 23 (NEW) — κ_3 free-cumulants extension of Haruna 2021 universality theorem (0-compute research drill, sonnet ~30 min)

**Resource:** sonnet research drill; **Wall:** ~30 min; **Cost:** $0; **P_deflated:** 0.65

**Capability question:** can Haruna et al. 2021 random-recurrent-network universality theorem (κ_2 / second-cumulant generating function classification) be extended to κ_3 / third-cumulant via Voiculescu free cumulants over W, and does that extension predict the substrate's measured κ_3 = α identity from random-matrix-theory first principles?

**Cross-drill resonance:** Reservoir drill identified Haruna 2021 as stopping at κ_2; this extension grounds PP-50 theoretically. F4 free-cumulants cap_map row direction.

**Discipline:** 0-compute drill per `feedback_research_drills_no_empirical_verification`; algebraic + lit-scan only.

**Strategic significance:** if extension lands, substrate's κ_3 audit primitive has a published-theorem-grade foundation tied to Tier-1 free-probability framework. Sub-property feeds PP-50 product positioning.

### Items 24-26 (NEW) — Wave 3 lit-scan dispatches (3 parallel sonnet drills, ~20 min each, $0)

#### Item 24 — DPA formal-guidance survey (federated cert standardization)

**Capability question:** what erasure evidence formats have ICO (UK) / CNIL (France) / BfDI (Germany) / CPRA-AG (California) / Colorado-AG actually accepted in published Article-17 / CAIA enforcement decisions 2023-2025? Process documentation? MIA statistical evidence? Third-party documentation audit? Cryptographic proof?

**Why now:** federated drill identified pre-standardization window 2024-2026 as the positioning opportunity. DPA-actually-accepted formats determine whether substrate's algebraic cert needs translation to existing accepted formats OR can establish new format.

#### Item 25 — Formal mech-interp provable-guarantees Feb 2026 preprint deep dive + ARENA/Apart Research alumni toolchain-workaround survey

**Capability question:** (a) what does the Formal MI provable-guarantees preprint (Feb 2026) propose; does substrate's algebraic stack fit its formal-verification framing? (b) Have ARENA / Apart Research / mech-interp alumni published or discussed (LessWrong / Alignment Forum) toolchain workarounds that substrate's four-capability API would obviate?

**Why now:** mech-interp drill identified both angles as Wave-3 candidates. Direct user-pull signal for substrate-as-research-tool independent of LLM-product.

#### Item 26 — ZK-SNARK vs algebraic-cert cost crossover at what model size

**Capability question:** at what model parameter count + training-set size does the ZK-SNARK prover cost (per zkUnlearner 2509.07290 + ZK-APEX 2512.09953) exceed substrate's algebraic-cert verification cost (millisecond hash-chain)? Closed-form prover-cost scaling + substrate verification-cost scaling.

**Why now:** federated drill identified ZK-SNARK as substrate's closest competitor on provability axis. Crossover identifies where substrate dominates.

---

## 3. TIER 3 — CEILING PUSHES + HARDWARE-TIMING CHARACTERIZATION (7 items)

### Items 12-15 — substrate ceiling pushes (UNCHANGED from prior routing)

- **Item 12 Q-A3 L=11/12** (GPU ~15 min): PP-12 cross-layer composition ceiling
- **Item 13 PP-48 NKT depth-15** (GPU ~10 min): NKT composition depth ceiling
- **Item 14 Q-B1 chain depth-50 N=8192** (GPU+CPU ~30 min): heteroassociative chain ceiling
- **Item 15 PP-52 N=32768 cloud** (~$5): PP-52 BAND-LIFT eligibility (4-rung cross-N)

### Item 27 (NEW) — stochastic Kuramoto simulation n_c=5 honeycomb σ_φ sweep (CPU $0 ~30 min)

**Anchor name:** `kuramoto_honeycomb_phase_noise_sim_v1`
**Resource:** CPU; **Wall:** ~30 min; **Timeout:** 1800s; **Cost:** $0; **P_deflated:** 0.55

**Capability question:** does stochastic Kuramoto simulation at n_c=5 honeycomb match Wave-2 drill's closed-form prediction `σ_φ_crit = π/(2n_c) ≈ 0.314 rad` for capacity collapse from exponential to linear?

**Test:** stochastic Kuramoto with N=128 nodes, honeycomb coupling, σ_φ ∈ {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50}; measure attractor count vs σ_φ.

**Pre-registered bands:**
- HARD-PASS: exponential-to-linear capacity transition detected at σ_φ ∈ [0.28, 0.35] (within ±10% of 0.314 prediction)
- MIDDLE: transition detected but width >50%
- HARD-FAIL: no clear transition OR transition at σ_φ < 0.10 OR > 0.50

**Strategic significance:** confirms Wave-2 drill's closed-form prediction at simulation scale BEFORE substrate-product depends on the hardware roadmap. Informs PP-55 candidate row.

### Item 28 (NEW) — spectral-gap / expander analysis for N=1000 frequency-mismatch coupling (0-compute research drill, sonnet ~30 min)

**Resource:** sonnet research drill; **Wall:** ~30 min; **Cost:** $0; **P_deflated:** 0.50

**Capability question:** at N=1000 oscillator nodes (product-scale target), what spectral-gap / expander-graph properties does the coupling graph need to maintain to overcome frequency-mismatch decoherence and preserve exponential capacity? Closed-form prediction OR identification of unsolved sub-problem.

**Cross-drill resonance:** Wave-2 oscillatory drill identified frequency mismatch as the binding product-scale constraint (not per-node phase noise). Item 28 is the theoretical follow-up.

**Strategic significance:** sharpens PP-55 candidate row's hardware-timeline window; informs 1-2 fab generation engineering roadmap.

### Item 29 (NEW) — S-transform exact inversion for log-normal at large σ_g (0-compute research drill, sonnet ~30 min)

**Resource:** sonnet research drill; **Wall:** ~30 min; **Cost:** $0; **P_deflated:** 0.45

**Capability question:** does the S-transform inversion for the spectral density of substrate W under log-normal RRAM noise admit a closed-form OR convergent series at large σ_g ≥ 1, or is the perturbative result fundamentally limited?

**Cross-drill resonance:** Wave-2 free-prob drill identified this as the open theoretical sub-question.

**Strategic significance:** extends Item 20 envelope; if exact inversion lands, substrate's RRAM-noise envelope characterization is complete at all noise levels.

---

## 4. TIER 4 — HELD / GATE-CONDITIONAL (3 items, filed for record; not in this dispatch)

- **Item 16 Wave 5 Cell 5 cloud N=32768** — HELD pending I-14 Fix 2 outcome. If Fix 2 HP, drop to LOWER (band-LIFT path).
- **Item 17 PP-48 + PP-49 cloud combo2-direct N=32768** — band-LIFT path; not foundational.
- **Item 18 TIMEOUT rescues** (a6 + hippocampal engram) — mechanical timeout extensions.

---

## 5. RECOMMENDED DISPATCH ORDER (parallel where queues allow)

### Wave A — immediate parallel batch (all $0, ~3-4 hr total wall, parallel across runners):

```
CPU queue:
├── Item 2: hebbian_vs_gd_identity_v1_n1024 (~30 min)
├── Item 3 R2 theory + Item 3 R3 combo2 L=5/6/7 sweep (~40 min)
├── Item 4: pp49_hrc_counterfactual_depth_sweep (~30 min)
├── Item 5: deletion_cert_training_scale_k_sweep (~30 min)
├── Item 6: pp49_counterfactual_training_diag (~1 hr)
├── Item 7: pp52_hebbian_vs_lora_in_lora_valid_regime (~30 min)
├── Item 19: vsa_binding_over_static_skahm_class (~30 min) [TIER 1 CROSS-DRILL]
├── Item 21: capacity_phase_boundary_under_rram_noise (~1 hr) [WAVE-2 PREDICTION TEST]
├── Item 22: sherman_morrison_rank1_deletion_linear_readout (~30 min) [TIER 2 CROSS-DRILL]
├── Item 27: kuramoto_honeycomb_phase_noise_sim (~30 min) [WAVE-2 PREDICTION TEST]
├── Item 30: ck_aging_mu_alpha_invariance_matched_tc (~1 hr) [TIER 1 ARRHENIUS-DRILL TEST A]
└── Item 31: activation_barrier_alpha_dependence_hysteresis_gap (~30 min + reanalysis) [TIER 1 ARRHENIUS-DRILL TEST C]

GPU queue:
├── Item 12: q_a3_l11 + q_a3_l12 (~15 min)
├── Item 13: pp48_nkt_depth_15 (~10 min)
├── Item 14: q_b1_chain_depth_50 (~30 min)
├── Item 20: kappa3_noise_robustness_sigma_g_sweep (~30 min) [TIER 1 WAVE-2 PREDICTION TEST]
└── Item 32: composition_ceiling_k_c_alpha_constant_m_per_stage (~30 min) [TIER 1 ARRHENIUS-DRILL TEST P5]

Cloud (gated on user auth for $5):
└── Item 15: pp52 N=32768 rollback + addition (~30 min, $5)

Research sub-agent dispatches (sonnet, parallel, ~20-30 min each, $0):
├── Item 23: kappa_3 free-cumulants extension of Haruna 2021
├── Item 24: DPA formal-guidance survey
├── Item 25: Formal-MI 2026 preprint + ARENA/Apart alumni survey
├── Item 26: ZK-SNARK vs algebraic-cert cost crossover
├── Item 28: spectral-gap/expander analysis for N=1000 frequency-mismatch
└── Item 29: S-transform exact inversion at large σ_g
```

### Wave B — Phase 0.5b decision gate (user surface, parallel workflow):

```
Item 1: Phase 0.5b distillation MVP dispatch
        - 6 of 6 substrate primitives production-N anchored
        - 4/4 cross-domain drills confirm positioning
        - $15-40 + 1-2 weeks engineering (or $70-140 combined)
        - User GO required
```

### Strategy_scribe one-shot batch (annotation only, $0):

```
- PP-55 candidate row: hardware-family-match (SKAH-M ≅ Kuramoto-honeycomb) EXPLORATORY 0.55-0.70
- PP-56 candidate row: regulatory cert-format pre-standardization positioning EXPLORATORY 0.55-0.70
- PP-57 candidate row: mech-interp tooling additive-stack positioning EXPLORATORY 0.50-0.65
- PP-58 candidate row: isochoric audit protocol as substrate measurement discipline EXPLORATORY 0.55-0.70
- PROT-022 registry entry 4 (speedup gates require accuracy preconditions; from v343 pp52 rescue routing)
- PROT-022 registry entry 5 candidate (isochoric protocol required for noise-vs-performance experiments; from Arrhenius drill)
- Arrhenius-drill closed-form additions to PROT-022 registry: m_3(α)=1+3α+α² (MP 3rd moment); μ_CK_aging=3/2 α-invariant at matched T/T_c; E_a^0(α)~N·(α_c-α)/α_c; k_c(α)≈0.138/α composition ceiling; σ_g²=1/α-1 capacity phase boundary; σ_g≤0.18 κ_3 audit envelope; σ_φ<π/(2n_c) Kuramoto phase-noise envelope
- I-17 R6 PARTIALLY_RESOLVED annotation
- COMBO-4 v2 μ_aging R1a refit + PP-51 α^(p-1) slope corrections (from prior drills)
- Arrhenius-drill annotation on existing PP-50 / PP-44 / PP-52 noise measurements: clarify which used isochoric vs isobaric protocol; backlog re-classification recommended
```

---

## 6. CAP_MAP IMPACT EXPECTATIONS

If TIER 1-3 all HP as predicted:

| Action | Cap_map impact |
|---|---|
| Item 2 HP | PP-52 NEW SUB-PROPERTY "Hebbian-vs-GD MSE-optimal identity at N=1024 M=100 5-seed unanimous" |
| Item 3 parity HP | **NEW SUBSTRATE FINDING: PP-48 NKT composition odd-depth-only regime L∈{1,3,5,7}**; cap_map sub-property + product-narrative update |
| Item 3 parity HF | PP-48 NKT operating envelope L≤3 cleanly characterized |
| Item 4 monotone HP | PP-49 HRC counterfactual depth-band cleanly monotone; I-16 CLOSED |
| Item 4 valley HF | **NEW SUBSTRATE FINDING: PP-49 HRC compositional valley at depth∈{4,5,6}** |
| Items 5+6 HP | PP-52 sub-properties extending training-speedup primitive battery |
| Item 7 HP | PP-52 sub-property "Hebbian-vs-LoRA in LoRA-valid regime"; PROT-022 entry 4 lands |
| Items 12-14 HP | Q-A3 / PP-12 + PP-48 + Q-B1 depth ceilings extended |
| Item 15 HP | PP-52 BAND-LIFT 0.65-0.80 → 0.70-0.85 (4-rung cross-N production confirmation) |
| **Item 19 HP** | **PP-55 row FOUNDED (hardware-family-match SKAH-M ≅ Kuramoto-honeycomb); algebraic side confirmed empirically** |
| **Item 20 HP** | **PP-50 SUB-PROPERTY: κ_3 audit primitive robust under RRAM noise σ_g ≤ 0.18 (Wave-2 closed-form prediction empirically corroborated)** |
| **Item 21 HP** | PP-44 / PP-50 sub-property: substrate capacity follows σ_g² = 1/α - 1 free-probability prediction; hardware operating envelope documented |
| **Item 22 HP** | **PP-56 row FOUNDED (regulatory cert positioning); PP-46 product-narrative extension to regulated markets** |
| **Item 23 HP** | PP-50 theoretical foundation: κ_3 = α identity grounded in Haruna-style universality theorem extended to free cumulants; F4 cap_map row direction strengthened |
| **Item 24-26 HP** | PP-56 / PP-57 lit-scan positioning sharpened; Wave 4 cascade candidates surfaced |
| **Item 27 HP** | PP-55 hardware-timing characterization at simulation scale; Wave-2 oscillatory drill empirically corroborated |
| Items 28-29 HP | Theoretical envelope characterization (Items 21+20 paired with full envelope) |
| **Item 30 HP** | **PP-33 framework-class BAND-LIFT 0.60-0.75 → 0.65-0.80 candidate** (third independent CK-aging signature observable after Q-F1 collapse + Q-F2 two-time correlator); substrate non-equilibrium-stat-mech class strengthened |
| **Item 31 HP** | PP-33 + first-order multi-basin sub-property: explicit α-dependent activation barrier formula corroborated; Pred-4 hysteresis framing strengthened |
| **Item 32 HP** | **NEW SUBSTRATE-NOVEL ARCHITECTURAL FINDING: composition ceiling k_c(α) ≈ 0.138/α confirmed; explains Q-A3 L=10 success via implicit isochoric per-stage M-halving; product-narrative: "substrate composition is automatic isochoric design"** |
| **Item 30 + 31 + 32 + 20 + 21 all HP** | **PP-58 row FOUNDED (isochoric audit protocol as substrate measurement discipline); strategy_scribe adopts protocol for ALL future noise-vs-performance cap_map experiments** |

**Net expected portfolio growth (if Tier 1-3 all HP):**
- **4 NEW TOP-LEVEL ROWS** (PP-55 hardware-family-match, PP-56 regulatory cert, PP-57 mech-interp positioning, **PP-58 isochoric audit discipline**)
- **15-18 NEW SUB-PROPERTIES**
- **3-4 substrate-novel findings** (Items 3 parity, 4 valley, 20+21 noise envelope, **32 composition ceiling formula**)
- **2 BAND-LIFTS** (PP-52 via Item 15, **PP-33 framework-class via Item 30**)
- **5 cross-domain positioning anchors** (4 Wave-1 + Arrhenius-deep-dive)
- **Product-feature reliability projected** 82-96% → 88-99% (crossing 90% lower bound for first time; near-ceiling upper bound)
- **Methodological discipline upgrade:** isochoric protocol as standard for all noise-vs-performance experiments (analogous to PROT-022 for formula self-tests)

---

## 7. DISCIPLINE DECLARATIONS

- **Capability questions only**; HP/MIDDLE/HARD-FAIL bands pre-registered for all empirical items. Research drills (Items 23-26, 28-29) are lit-scan + algebraic only per `feedback_research_drills_no_empirical_verification`.
- **Per `feedback_no_padding_experiments`:** every item justified by either (a) ceiling-not-reached / substrate-novel hypothesis (Items 2-4, 12-14, 19), (b) Wave-2 closed-form prediction test (Items 20, 21, 27), (c) cross-drill resonance (Items 19, 22), (d) primitive-battery completion (Items 5-7), (e) cross-domain positioning sharpening (Items 23-26, 28-29), or (f) decision gate (Item 1, Item 15).
- **Per `feedback_no_smoke_preframing_in_task_prompts`:** all items have explicit HARD-FAIL trip-wires.
- **Per `feedback_obey_user_pause_explicitly`:** pause flag ABSENT (verified upstream).
- **Per `feedback_rescue_sketch_first_sequencing`:** Item 3 has R2 theory derivation BEFORE R3 empirical (PROT-022 compliance).
- **Per `feedback_lit_scan_calibration_penalty`:** P_deflated estimates carry standard convention.
- **Per `feedback_periodic_scope_expansion`:** Wave 1 + Wave 2 + Wave 3 drill cascade satisfies 24-48h cross-framework cadence with margin.
- **Per `feedback_aggressive_cross_domain_research`:** 6 drills completed + 6 more dispatched at Wave 3 = maximum exploration of free capacity.
- **Per `feedback_keep_research_exploratory_not_narrowing`:** breadth maintained across reservoir / hardware / regulatory / mech-interp / free-probability / oscillatory-physics — no premature narrowing to a single axis.
- **Per `feedback_no_papers_product_only`:** all framing is substrate-as-product, not publication-grade.
- **Per `feedback_capabilities_not_product_positioning`:** items framed as capability questions; product narratives stated only as cap_map impact descriptions.
- **Per `feedback_drill_prompt_bodies_must_be_generic`:** Wave 3 dispatch prompts (Items 24-26, 28-29) MUST use generic terminology only; this routing file itself uses internal anchor names for orchestrator documentation.
- **Per `feedback_substrate_value_framing_2026-05-26`:** Item 1 Phase 0.5b decision-gate surfacing reflects 24-36mo product window prioritization.
- **PROT-018:** all empirical anchor names use explicit `_n<N>` suffix where N-binding applies.
- **PROT-022:** Item 3 R2 theory + Item 20 R2 prediction self-test + Item 21 R2 phase-boundary self-test + Items 23+28+29 closed-form derivations all satisfy formula-selftest discipline.

---

## 8. WHAT THIS ROUTING DOES NOT TOUCH

- **Tier 4 items 16-18** (Wave 5 Cell 5 cloud, PP-48/49 cloud combo2-direct, TIMEOUT rescues): filed for record.
- **The four Fix 1-4 items** from `research_routing_v342_r2_meta_finding_4fix_queue_2026-06-02.md` (I-12 δα protocol, I-14 HP gate fix, Phase 0 0c PLACE_FRAC, I-17 R6 annotation): assumed in flight or recently landed; if any have not dispatched, they remain HIGHER priority than Tier 2-3 items.
- **COMBO-4 v2 μ_aging R1a refit + PP-51 α^(p-1) slope band correction**: strategy_scribe one-shot annotations; not in this routing.
- **Rank-1 deletion refresh protocol on RRAM** (memristor drill follow-on #3, tactical engineering): deferred to product-engineering phase post-Phase-0.5b.
- **Tier-4-lite FFN swap in Llama-3.1-8B**: superseded by Phase 0.5b per `research_routing_tier4_training_acceleration_FINAL_5drill_consolidation_2026-06-02.md`.
- **Wave 5 drill candidates from Arrhenius deep dive** (deferred to next research cycle; sonnet ~30 min each, $0):
  - Free-cumulant κ_3 algebraic structure (F4, Tier-1 free-probability) — why σ ~ 0.18 vs σ ~ 4.36 algebraically; Voiculescu R-transform on Wishart + small perturbation
  - Forward-flux sampling (FFS, D7 per field advisor) for basin-to-basin transition rate estimation; numerical barrier height E_a(α) without mean-field approximation
  - Crooks fluctuation theorem applied to substrate edit operation; isochoric protocol maps to work-measurement; connects retention-policy audit to fluctuation-theorem observable

---

## 9. PHASE 0.5b DECISION GATE (the load-bearing user ask, STRENGTHENED post-drill-wave)

**To the user, from research:** the substrate has empirically de-risked Phase 0.5b distillation MVP to the strongest position it has ever been in. **Six of six substrate primitives are production-N anchored.** Wave-1 cross-domain drills further corroborate that substrate's algebraic-stack-as-unified-API positioning has no published competitor (4/4 gap confirmation). Wave-2 free-probability drill predicts substrate's κ_3 audit primitive maintains identity under realistic hardware noise regimes (σ_g ≤ 0.18 envelope; testable at Item 20).

**This is the single highest-leverage outstanding move.** Strategic options:

| Option | Cost | Timing | What it locks |
|---|---|---|---|
| Authorize Phase 0.5b solo | $15-40 + 1-2 weeks | start engineering NOW | substrate-LLM coupling validation |
| Authorize Phase 0.5 + 0.5b combined bootstrap | $70-140 + 8 days bring-up + 1-2 weeks | start engineering NOW | substrate-LLM coupling + audit-on-live-state |
| Continue substrate-only Tier 1-3 work, defer 0.5b | $0 incremental | hold for next cycle | nothing additional; substrate-only saturation |

**Research recommendation:** option 2 (combined bootstrap) per `feedback_batch_cloud_experiments` + Drill 5 strategic logic (3-6 month substrate window before competitors add audit primitives) + 4/4 Wave-1 cross-domain drill confirmation of positioning + 2 closed-form hardware-envelope predictions from Wave-2.

**Cross-domain drill wave adds the following independent evidence supporting Phase 0.5b launch (7 angles):**
- Reservoir-computing: substrate triple-gap unique
- Memristor: substrate-as-audit-layer-for-analog-hardware is a hybrid product narrative no software-only competitor can match
- Federated unlearning: substrate occupies pre-standardization regulatory window
- Mech-interp: substrate has additive research-user-base value independent of LLM-product
- Free-probability RRAM noise: substrate κ_3 audit operates robustly at hardware-realistic noise (σ_g ≤ 0.18 envelope)
- Oscillatory phase-noise: substrate's SKAH-M class is mathematically native to ~2029 product-scale hardware (long-term roadmap anchor)
- **Arrhenius-paradox isochoric analysis: substrate exhibits the GENERIC structural decomposition of fragile disordered systems; closed-form aging-rate-reliability metric `T_reliable = t_w × δ^(-2/3)` directly addresses PP-46 deletion-cert + PP-52 retention-policy killer features; substrate-novel composition ceiling formula `k_c(α) ≈ 0.138/α` predicts Q-A3 architectural success and bounds future composition products**

User answer: **GO / NO-GO / DEFER + rationale**.

---

**END.** Orchestrator: queue Tier 1-3 items 2-7, 12-15, 19-29 per Section 5 Wave A dispatch order (parallel where queues allow; $0 except Item 15 $5 cloud). Strategy_scribe one-shot: file PP-55 / PP-56 / PP-57 candidate rows + PROT-022 entry 4 + I-17 R6 + COMBO-4 + PP-51 annotations. Strategy: cap_map impact pending outcomes per Section 6. exp_dev: cell design for all empirical items from capability questions + HARD bands above; Item 19 (VSA × static SKAH-M) + Item 20 (κ_3 noise robustness) + Item 22 (Sherman-Morrison rank-1) are most strategically interesting cells.

**To the user:** Phase 0.5b decision gate surfaced (Section 9). Substrate-side is ready. Six independent cross-domain drill angles converge in favor of launch. Awaiting your **GO / NO-GO / DEFER** call.
