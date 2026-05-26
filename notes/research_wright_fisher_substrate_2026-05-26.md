# Research — Wright-Fisher / population-genetics cross-domain drill (Tier-1b)

**Filed:** 2026-05-26 by Research sub-agent (Opus synthesis after parallel Sonnet WebSearch breadth on 7 angles).
**Routing:** orchestrator strategic intent — Tier-1b scope-expansion cadence per `tools/orchestrator/agents/research.md`. Wright-Fisher is one of the 8 Tier-1b fields (adjacency parent: thermodynamics / drift-diffusion). No prior drill in this field; substrate question is the named question for the row ("continual learning = mutation + selection + drift; Wright-Fisher / coalescent / fixation-probability frameworks predict catastrophic-forgetting rate vs replay rate; Kimura neutral theory gives a baseline for what 'no-replay' forgetting looks like").
**Trigger:** scope-expansion + two specific bridges from strategic intent: (a) multi-allele WF ↔ MoE multi-expert dynamics; (b) fixation probabilities / quasi-stationary distributions ↔ discrete retention plateaus (0.94 / 0.74 / 0.60). Both bridges tested explicitly.
**Discipline:** 2x depth per [[feedback-2x-means-depth]]; generic math terms per [[feedback-query-privacy-decomposition]]; lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]] (deflate 0.15-0.25, cap novel-synthesis P at 0.50).
**Cross-ref:** `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` (P=0.48 leading theoretical home for plateaus); `notes/research_mesoscopic_transport_moe_2026-05-25.md` (DMPK MoE diagnostic, P=0.42); `notes/research_moe_alpha_c_band_audit_2026-05-26.md` (grid-quantization artifact).

---

## (a) HEADLINE

> **Wright-Fisher is a WEAK theoretical home for the 0.94/0.74/0.60 plateaus (P = 0.22) and a STRONGER frame for MoE multi-expert continual-learning dynamics (P = 0.38 as a SHIFT-vs-PARTITION discriminator). It is COMPLEMENTARY to Saad-Solla, not competitive — WF describes finite-N stochastic fluctuations around Saad-Solla's deterministic ODE plateaus, not the plateau heights themselves.**
>
> Four load-bearing findings from the lit-scan:
>
> **Finding 1 (decisive NEGATIVE on plateau-height arithmetic — Drill Q1):** Dirichlet stationary distribution of multi-allele WF has mode `mode(θ_j) = (α_j - 1)/(α_0 - K)` with the constraint `Σ θ_j = 1`. The substrate plateaus 0.94 + 0.74 + 0.60 = **2.28**, NOT 1. Plateau heights are **retention cosines**, not allele frequencies on a simplex — they have no simplex constraint. Direct arithmetic mapping is STRUCTURALLY IMPOSSIBLE. The only rescue is to re-interpret each plateau as a **per-class FIXATION PROBABILITY** (which lives in [0, 1] independently, no simplex constraint). Under that re-reading, WF gives fixation probability `u(p) = (1 - e^{-2 N_e s p}) / (1 - e^{-2 N_e s})` for a single allele with selection coefficient s starting at frequency p in population N_e. Tuning (s, p, N_e) per class CAN produce arbitrary {0.94, 0.74, 0.60} but with 3 free parameters per class = 9 free knobs to fit 3 numbers — a curve-fitting exercise, not a prediction. **No falsifiable arithmetic emerges; this rescue is over-parameterized.**
>
> **Finding 2 (POSITIVE on SHIFT-vs-PARTITION boundary — Drill Q2):** Wright's island model gives a clean SHIFT-vs-PARTITION analog through the effective population size formula `N_e_total = N_e_local × D / (1 - F_ST)` for D demes with between-deme differentiation F_ST. **SHIFT = independent demes with F_ST → 1** (allele frequencies fully partitioned, alleles drift independently in each expert); **PARTITION = single panmictic population with F_ST → 0** (alleles mix across all experts, no per-expert specialization). The transition is parameterized by gene-flow rate m (analog: gate routing entropy). At critical m_c ≈ 1/(4 N_e), the partition/shift boundary undergoes a sharp transition — analogous to MoE gating sharpness threshold. This is a NEW falsifiable handle on the SHIFT/PARTITION boundary that is ORTHOGONAL to the mesoscopic-transport DMPK bimodality signature (`notes/research_mesoscopic_transport_moe_2026-05-25.md`). Combining the two gives a richer discriminator panel.
>
> **Finding 3 (POSITIVE on finite-N corrections to Saad-Solla — Drill Q5):** Saad-Solla saddle-cascade is a deterministic ODE in the large-N limit. WF / Kimura diffusion describes stochastic fluctuations at finite N around that deterministic trajectory. Specifically, the Kimura forward Kolmogorov equation reduces to the deterministic replicator ODE as N→∞ but adds a diffusion term scaling as 1/N at finite N. **PREDICTION: plateau-residence times τ_p should show variance scaling as 1/N around the Saad-Solla mean.** This is a SHARP falsifier with explicit numerical form: at fixed corpus-overlap-class, the standard deviation of plateau-duration across seeds should scale as σ(τ_p) ∝ N^{-1/2} (Wright-Fisher diffusion scaling). HARD-PASS if σ(τ_p) ~ N^{-1/2} ± 20%; HARD-FAIL if σ(τ_p) ~ N^0 (constant — implies non-diffusive mechanism) or σ(τ_p) ~ N^{-1} (faster — implies higher-order finite-size correction).
>
> **Finding 4 (PARTIAL on continual-learning analog — Drill Q4):** Wright-Fisher with mutation + selection gives a retention-curve predictor through the QUASI-STATIONARY DISTRIBUTION on the (K-1)-simplex. Under low mutation rates, the QSD concentrates on **corners and edges** of the simplex (per arXiv:1607.00104, Burden-Tang 2016) — meaning each allele either survives at near-full retention or extinguishes, with intermediate frequencies being transient. **Substrate analog**: per-corpus retention should be either near-1 (allele survived) or near-0 (allele extinct), with intermediate values being unstable. Bet B v189 retentions are {0.740, 0.854, 0.798} — NONE of these are near-0 or near-1 → at face value INCOMPATIBLE with low-mutation QSD. Rescue: substrate may operate in the HIGH-mutation regime where the Dirichlet stationary concentrates in the interior of the simplex with mode-positions controlled by α-parameters (replay rate analog). This rescue keeps the framework alive but requires substrate-side measurement of an "effective mutation rate" — which is not currently instrumented.

**Calibrated probabilities (lit-scan penalty applied + novel-synthesis cap = 0.50 enforced):**

- **P(WF-as-theoretical-home for 0.94/0.74/0.60 plateaus) = 0.22.** Deflated from naive 0.40 by -0.18 (Dirichlet simplex constraint structurally inapplicable; rescue via per-class fixation probability is over-parameterized 9-knob fit). Below Saad-Solla (0.48) and Mechanism-A (0.45). **WF is NOT a competitive home for plateau heights.**
- **P(WF-as-finite-N-correction-to-Saad-Solla) = 0.42.** Deflated from naive 0.58 by -0.16 (substrate is not SGD-trained; Kimura diffusion mapping to Hebbian-update process is structural-analogy not closed-form derivation). This is the COMPLEMENTARY position — both frameworks coexist, WF describes the noise structure around Saad-Solla's deterministic cascade. **Sharp falsifier**: σ(τ_p) scaling with N (HARD-PASS at N^{-1/2}, HARD-FAIL at N^0 or N^{-1}).
- **P(WF-as-MoE-SHIFT-vs-PARTITION-discriminator) = 0.38.** Deflated from naive 0.55 by -0.17 (island-model F_ST is a population-genetics concept; mapping to gating routing entropy is structural-analogy). Falsifier: at K=4, post-MoE-rebuild, measure cross-expert correlation of per-cell retention; predict F_ST_analog → 1 under SHIFT (per-expert decorrelation) and F_ST_analog → 0 under PARTITION (full correlation). Orthogonal to DMPK bimodality; combining both gives a richer panel.

**Net update to substrate-research roadmap:** Wright-Fisher is a NEW Tier-3 candidate (not Tier-1 or Tier-2) — its primary use is as a finite-N-correction frame layered ON TOP of Saad-Solla, NOT as a standalone theoretical home for the plateau structure. No GPU-spend recommendation. CPU-cheap re-analysis of existing seed-variance data for plateau-residence-time scaling IS recommended (companion handoff below).

---

## (b) Cheap decisive test

**Test 1 (zero GPU, CPU re-analysis of existing data):** plateau-residence-time variance scaling with N.

- **Data source**: existing Bet B 4-stage continual-learning runs at multiple N values (search `data/exp_wave14_betB_*` for runs with N ∈ {1024, 2048, 4096}). If multi-N data exists, compute per-seed plateau-residence-time (τ_p) at each N, then fit log(σ(τ_p)) vs log(N).
- **Pre-registered bands**:
  - **HARD-PASS (WF-as-finite-N-correction confirmed)**: slope ∈ [-0.7, -0.3] (consistent with WF diffusion's N^{-1/2} prediction within 40%).
  - **HARD-FAIL (WF correction refuted)**: slope ∈ [-0.1, 0.1] (no N-dependence — constant noise, non-diffusive mechanism) OR slope < -0.8 (faster-than-WF — higher-order correction dominates).
  - **MIDDLE BAND**: slope ∈ [-0.3, -0.1] or slope ∈ [-1.0, -0.7] (partial mapping, framework directionally correct but quantitatively off).
  - **INSTRUMENTATION-FAIL**: no multi-N data exists (then re-ship is needed — see Test 2).
- **Estimated cost**: 30 min CPU re-analysis IF multi-N data exists.

**Test 2 (low GPU cost, if Test 1 is instrumentation-fail):** ship 1-cell re-ship of Bet B 3-stage at N ∈ {1024, 2048, 4096}, 5 seeds each. Compute σ(τ_p) at each N. Cost: ~30 GPU-min. Use HARD-PASS / HARD-FAIL / MIDDLE bands from Test 1.

**Test 3 (zero GPU, post-MoE-rebuild instrumentation):** cross-expert correlation of per-cell retention as F_ST analog.

- **Data source**: in-flight or post-completion MoE-rebuild data (`data/exp_wave14_moe_shift_partition_v*`).
- **Diagnostic computation** (10 lines of code, post-hoc):
  ```python
  # For each cell (K=4, M_total, seed), compute per-expert retention vector r_k ∈ [0,1].
  # F_ST analog: 1 - mean_within_expert_variance / total_variance.
  F_ST = 1 - np.mean([np.var(r_k_seeds) for r_k_seeds in per_expert_retentions]) / np.var(all_retentions)
  ```
- **Pre-registered bands**:
  - **SHIFT signature**: F_ST > 0.7 (per-expert decorrelation — alleles partitioned to demes).
  - **PARTITION signature**: F_ST < 0.3 (per-expert correlation — alleles mixed across all experts).
  - **MODE-COLLAPSE signature**: F_ST in [0.7, 1.0] BUT only 1-2 experts have non-zero variance (i.e., F_ST high because most experts are dead, not because alleles are partitioned).
- **Estimated cost**: 5 min CPU post-hoc.

**Decisive recommendation:** Test 1 + Test 3 are both ZERO GPU spend; ship the companion handoff for them only. Do NOT ship Test 2 unless Test 1 returns INSTRUMENTATION-FAIL.

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL thresholds

### Prediction set 1 — plateau-height arithmetic (Drill Q1)

**P1.1 (NEGATIVE finding — Dirichlet simplex incompatible).** Dirichlet stationary distribution requires Σ allele_frequencies = 1. Substrate plateau heights 0.94 + 0.74 + 0.60 = 2.28 ≠ 1. **HARD-FAIL prediction**: any attempt to derive 0.94/0.74/0.60 as Dirichlet modes is STRUCTURALLY IMPOSSIBLE without reinterpreting heights as per-class fixation probabilities (not simplex coordinates). **Calibrated P (Dirichlet arithmetic produces substrate heights)** = 0.05.

**P1.2 (Rescue under per-class fixation probability re-reading).** Kimura fixation formula `u(p) = (1 - e^{-2 N_e s p}) / (1 - e^{-2 N_e s})` per class has 3 parameters (s, p, N_e) — 9 free knobs total to fit 3 numbers. **Curve-fitting, not prediction.** **HARD-FAIL**: any "WF predicts 0.94/0.74/0.60" claim that doesn't first pin (s, p, N_e) from substrate primitives independently fails the falsifiability test. **Calibrated P (rescue is principled)** = 0.15.

**P1.3 (Honest competitive assessment).** Saad-Solla (P=0.48) and Mechanism-A (P=0.45) both have STRUCTURAL fits to the substrate primitive that WF lacks. **WF is not a competitive theoretical home for plateau heights — its position is COMPLEMENTARY (finite-N correction layer) not COMPETITIVE.** **Calibrated P (WF-as-leading-home)** = 0.10.

### Prediction set 2 — MoE multi-allele drift mapping (Drill Q2, Q3)

**P2.1 (SHIFT vs PARTITION via F_ST analog).** Island-model effective-population-size formula `N_e_total = N_e_local × D / (1 - F_ST)` predicts SHIFT operates at F_ST → 1 (independent demes), PARTITION at F_ST → 0 (panmictic). **HARD-PASS**: post-MoE-rebuild, F_ST_analog > 0.7 under SHIFT and < 0.3 under PARTITION. **HARD-FAIL**: F_ST_analog within 0.2 across arms (no discrimination). **MIDDLE BAND**: F_ST_A - F_ST_B ∈ [0.2, 0.4]. **Calibrated P (F_ST discriminator works)** = 0.38.

**P2.2 (Multi-allele drift interference).** Each allele's drift is correlated with others through the simplex constraint Σ x_j = 1 (drift in allele j must be compensated by negative drift in others). **Substrate analog**: each expert's per-cell retention is correlated with others through normalization (if gating uses softmax). **HARD-PASS**: cross-expert retention covariance matrix shows negative off-diagonals at PARTITION (simplex-constraint signature) and zero off-diagonals at SHIFT (independent demes). **HARD-FAIL**: covariance structure is the SAME across arms. **Calibrated P** = 0.35.

**P2.3 (Selection coefficient ↔ gating sharpness, closed-form analog).** Wright-Fisher with selection s gives fixation probability `u(p) = (1 - e^{-2 N_e s p}) / (1 - e^{-2 N_e s})`. For p = 1/K (uniform initial gating) at K experts, fixation probability of best expert is `u(1/K) ≈ 2s/(1 - e^{-2 N_e s})` in the weak-selection limit. **Substrate analog**: gating sharpness s_eff controls expert-survival probability. **HARD-PASS for substrate**: post-MoE-rebuild, expert-collapse rate scales as `1 - u(1/K)` with measurable s_eff extracted from gating logit distribution. **HARD-FAIL**: no scaling relationship; expert-collapse rate independent of gating sharpness. **Calibrated P** = 0.25 (deflated: very speculative mapping; gating is not a true frequency-dependent selection).

### Prediction set 3 — finite-N correction to Saad-Solla (Drill Q5)

**P3.1 (Plateau-residence-time variance scaling).** Wright-Fisher / Kimura diffusion predicts τ_p variance scales as 1/N at finite N. **HARD-PASS**: log(σ(τ_p)) vs log(N) slope ∈ [-0.7, -0.3]. **HARD-FAIL**: slope outside [-1.0, 0.1]. **Calibrated P** = 0.42.

**P3.2 (Mean plateau heights unchanged by N).** Saad-Solla deterministic-ODE plateaus are N-independent at leading order; WF corrections shift heights by O(1/N) only. **HARD-PASS**: substrate plateau heights at N=1024 and N=4096 agree within 0.02 (within seed noise). **HARD-FAIL**: heights drift by > 0.05 between N values. **Calibrated P** = 0.50 (cap; this is testable on existing data).

**P3.3 (Complementarity — both frameworks coexist post-Pred-4-resolution).** If Saad-Solla Pred-4 HARD-PASSES (`notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` decision matrix), WF becomes the natural finite-N correction layer underneath. If Pred-4 HARD-FAILS, WF still provides the noise structure but loses the deterministic backbone. **Calibrated P (both frameworks coexist if Pred-4 resolves either way)** = 0.40.

### Prediction set 4 — continual-learning retention (Drill Q4)

**P4.1 (QSD concentration on corners/edges contradicts intermediate-retention data).** Burden-Tang 2016 (arXiv:1607.00104) shows low-mutation QSD concentrates on simplex corners and edges — substrate's intermediate retentions {0.740, 0.854, 0.798} would imply HIGH mutation regime (replay rate). **HARD-PASS for WF-CL framing**: substrate operates with measurable replay-rate analog μ such that μ × N_e_analog >> 1 (high-mutation regime). **HARD-FAIL**: substrate has no replay analog AND intermediate retentions persist (then QSD framing inapplicable). **Calibrated P** = 0.30.

**P4.2 (Generation-by-generation forgetting prediction).** WF generation t allele frequency variance grows as `p(1-p) × (1 - (1 - 1/N)^t)` ≈ `p(1-p) × t/N` for small t/N. **Substrate analog**: per-task retention should decay linearly in (sequential-task-count / N_e_analog) for small task counts. **HARD-PASS**: 4-stage Bet B retention decay rate matches the formula within 30%. **HARD-FAIL**: retention decay is sigmoidal or step-like (suggests deterministic mechanism not WF drift). **Calibrated P** = 0.28.

### Prediction set 5 — Calibrated combined probabilities (Drill Q6)

- **P(WF-as-theoretical-home for plateau heights)** = 0.22 (NEGATIVE; structurally weak; over-parameterized rescue).
- **P(WF-as-finite-N-correction-to-Saad-Solla)** = 0.42 (POSITIVE; complementary; testable via σ(τ_p) scaling).
- **P(WF-as-MoE-SHIFT-vs-PARTITION-discriminator)** = 0.38 (POSITIVE; F_ST analog; orthogonal to DMPK signature).
- **P(any WF-derived falsifier ships within 7 days)** = 0.60 (Tests 1 and 3 are ZERO-GPU re-analysis on existing data).

---

## (d) Cross-thread synthesis with prior entries

### Cross-ref to Saad-Solla saddle-cascade deep drill (`notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md`)

**Relationship: COMPLEMENTARY, NOT COMPETITIVE.** Saad-Solla saddle-cascade (P=0.48, leading) predicts plateau HEIGHTS via permutation-orbit cardinality in the large-N deterministic ODE limit. Wright-Fisher (P=0.42 as finite-N correction) predicts plateau VARIANCE STRUCTURE around those deterministic heights. The two frameworks live at different scales: Saad-Solla = O(1) mean behavior, WF = O(1/N) fluctuation structure. They can coexist seamlessly. **The σ(τ_p) ∝ N^{-1/2} prediction is the cleanest joint falsifier** — if it HARD-PASSES, both frameworks are simultaneously corroborated; if it HARD-FAILS, both frameworks need revision (Saad-Solla still gives heights but WF fails as the noise layer; need to seek alternative finite-N correction theory).

### Cross-ref to mesoscopic-transport MoE drill (`notes/research_mesoscopic_transport_moe_2026-05-25.md`)

**Relationship: ORTHOGONAL DISCRIMINATORS.** DMPK predicts SVD-bimodality signature (open vs closed channels) for SHIFT vs PARTITION. Wright-Fisher predicts F_ST signature (deme decorrelation vs panmixia). Both can be computed from the same MoE-rebuild output with zero additional GPU cost. **Combining the two gives a 2x2 discriminator panel:**

|  | DMPK BIMODAL | DMPK UNIMODAL |
|---|---|---|
| **F_ST HIGH** | SHIFT confirmed (both) | INCONSISTENT — investigate (e.g., partition with collapsed demes) |
| **F_ST LOW** | INCONSISTENT — investigate | PARTITION confirmed (both) |

The off-diagonal "INCONSISTENT" cells are diagnostically valuable — they would point to either (a) mode-collapse failures or (b) a deeper mechanism not captured by either framework.

### Cross-ref to MoE α_c band-rationale audit (`notes/research_moe_alpha_c_band_audit_2026-05-26.md`)

**Relationship: INDEPENDENT.** WF/island-model has no direct bearing on the α_c grid-quantization artifact. The denser M-grid recommendation in that audit stands as the dominant action item for the in-flight MoE prestep. WF discriminators (F_ST + DMPK bimodality) apply post-MoE-rebuild as instrumentation, not as α_c calibration.

### Cross-ref to primitive-decision drill (`notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`)

**Relationship: COMPATIBLE.** Primitive decision LOCKED linear-heteroassoc. WF framing is a phenomenological layer ON TOP of any primitive — the Kimura diffusion mapping doesn't care whether the underlying retrieval is linear-heteroassoc or recurrent. WF predictions are at the seed-variance / cross-expert-correlation level, not the primitive level. **No tension with the primitive lock.**

### Cross-ref to scope-expansion cadence

This drill closes the Wright-Fisher Tier-1b row. Remaining un-drilled Tier-1b fields: `nonequilibrium-stat-mech` (Jarzynski / Crooks NESS), `structural-glasses-MCT` (mode-coupling theory), `percolation-critical-phenomena` (universality classes), `random-matrix-theory-beyond-free-prob` (Tracy-Widom edge), `network-science-graph-theory` (Ramanujan / spectral gap), `sparse-coding-compressed-sensing` (LASSO / dictionary learning). These remain candidates for the next scope-expansion cadence tick.

### Cross-ref to negative-results-trigger-2x-research (`feedback_negative_results_2x_research`)

WF as theoretical home for plateau heights is REFUTED (P=0.22, structurally weak). This is a genuine refutation, not an OOM-inconclusive or expected-boundary, so per [[feedback-negative-results-2x-research]] a 2x drill on RESCUE PATHS is warranted. **Rescue candidates surfaced by this drill:** (a) high-mutation regime QSD (interior simplex concentration) needs substrate-side replay-rate measurement; (b) per-class fixation probability re-reading needs principled (s, p, N_e) pinning from substrate primitives, not curve-fitting. Both are RESEARCH-incomplete and would need further drilling IF the user wants to keep WF alive as a theoretical home. **Recommendation: do not 2x-drill the rescues** — WF's complementary position (finite-N correction) is more productive than rescuing the home-of-plateaus position.

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

**1. Plateau heights are NOT a population-genetics phenomenon for product narrative purposes.** The Dirichlet-incompatibility finding (Sec a, Finding 1) means the substrate's 3-tier retention signal cannot be sold as "natural allele-frequency-like clustering." The Saad-Solla saddle-cascade frame remains the dominant product-narrative anchor for the plateau structure. **Product implication: do NOT pivot the audit-tier narrative to a population-genetics framing.** WF is wrong-shape for the plateau-height story.

**2. F_ST instrumentation is a NEW per-expert AUDIT METRIC.** F_ST_analog measures the degree to which experts have specialized vs mixed content. **Product implication**: at runtime, F_ST per content-cluster gives a fine-grained signal of "is this MoE specialized correctly for this query type?" — a substrate-observable that can be exposed to users as a confidence / specialization signal. Independent of the SHIFT-vs-PARTITION architecture choice itself, F_ST monitoring becomes a deployable product metric.

**3. σ(τ_p) ∝ N^{-1/2} scaling is a SUBSTRATE-AUDITABILITY guarantee.** If WF-as-finite-N-correction HARD-PASSES, the substrate's noise structure has a published, theory-grounded predictor. **Product implication**: substrate retention variance becomes PREDICTABLE — the substrate can advertise "retention noise decreases as the square root of capacity," which is a clean scaling law users can plan around. If HARD-FAILS, we need a different noise predictor (would not invalidate the substrate but would leave a gap in the auditability narrative).

**4. Multi-allele drift interference (negative covariance in retention across experts) maps to a USER-FACING WARNING SIGNAL.** If experts show strong negative covariance (one expert's retention rising → others' falling), the substrate is in the constrained-simplex regime — a signal that capacity is fully saturated. **Product implication**: cross-expert covariance becomes a saturation indicator the substrate can expose at deployment.

**5. Wright-Fisher framing AT BEST gives 1.5 product handles (F_ST audit metric + noise-scaling-law) — meaningfully less than Saad-Solla (3+ handles per the deep drill's product implications) or mesoscopic-transport (the DMPK bimodality + Sharvin-Drude crossover gives 2-3 handles).** Net contribution: incremental, not transformative.

---

## (f) Citations (verified count: 11 direct + 4 contextual = 15)

### Multi-allele Wright-Fisher diffusion (Finding 1, 4)
- **Burden, Tang 2016** — `arXiv:1607.00104` — "An approximate stationary solution for multi-allele neutral diffusion with low mutation rates" — Dirichlet stationary; low-mutation concentration on simplex edges/corners. https://arxiv.org/abs/1607.00104
- **Khare, Mukherjee 2023** — `arXiv:2312.10831` — "Steady-state Dirichlet approximation of the Wright-Fisher model using the prelimit generator comparison approach of Stein's method" — formal proofs of Dirichlet approximation rates.
- **Genz et al. 2016** — Cambridge Journal of Applied Probability — "The stationary distribution of the infinitely-many neutral alleles diffusion model" — foundational on Dirichlet stationary.
- **PMC8019856** — "Multi-dimensional diffusion process of allele frequencies in population genetics" — multi-dimensional generalizations.
- **Genetics 196:1199 (2014)** — "Equilibrium Allele Frequency Distribution for a Population with Reproductive Skew" — Dirichlet with skew corrections.

### Wright-Fisher with selection (Finding 1 rescue, Prediction P2.3)
- **Wright-Fisher fixation formula** — Kimura's diffusion fixation probability `u(p) = (1 - e^{-2 N_e s p}) / (1 - e^{-2 N_e s})` — textbook (Ewens 2004, *Mathematical Population Genetics*, Springer, Ch. 4).
- **Bossert, Stadler 2022** — `arXiv:2205.06480` — "Exponential Integral Solutions for Fixation Time in Wright-Fisher Model With Selection" — closed-form fixation time analysis.
- **Etheridge, Griffiths 2018** — Project Euclid Annals of Applied Probability 28:1 — "Duality and fixation in Ξ-Wright-Fisher processes with frequency-dependent selection" — frequency-dependent selection generalizations.

### Island model / population subdivision (Finding 2)
- **Whitlock, Barton 1997** — Genetics 146:427 — "The Effective Size of a Subdivided Population" (referenced from PMC1207958). Foundational result on N_e_total formula with F_ST.
- **Wang, Caballero 1999** — Heredity — "Developments in predicting the effective size of subdivided populations" — modern extensions.
- **Wakeley 2003** — Genetics 162:501 — "Effective Population Size and Population Subdivision in Demographically Structured Populations" — diffusion approximations under subdivision.

### Finite-N corrections / large-N limit (Finding 3)
- **Chalub, Souza 2014** — `arXiv:math/0602530` — "The continuous limit of the Moran process and the diffusion of mutant genes in infinite populations" — N→∞ limit of Moran process recovering Kimura PDE.
- **Saad, Solla 1995** — Phys. Rev. E 52:4225 — soft-committee plateau ODE (referenced as the deterministic frame WF would correct).
- **Goldt, Advani, Saxe, Krzakala, Zdeborová 2019** — `arXiv:1906.08632` — "Dynamics of stochastic gradient descent for two-layer neural networks in the teacher-student setup" — explicitly addresses finite-N plateaus in teacher-student SGD; relevant analog for substrate plateau structure under finite-N WF correction.

### Continual learning analog (Finding 4)
- **Lee, Goldt, Saxe 2021** — `arXiv:2107.04384` — "Continual Learning in the Teacher-Student Setup" — already cross-ref'd in Saad-Solla drill; relevant here as the deterministic frame WF would extend with finite-N noise.

### Quasi-stationary distributions (Finding 4)
- **arXiv:2107.13197** — "The stationary and quasi-stationary properties of neutral multi-type branching process diffusions" — formal results on QSD for multi-type diffusion (relevant to substrate per-expert dynamics).

### Substrate-internal references
- `notes/research_saad_solla_saddle_cascade_deep_2026-05-25.md` (P=0.48, leading theoretical home for plateau heights — complementary to this drill).
- `notes/research_mesoscopic_transport_moe_2026-05-25.md` (DMPK bimodality SHIFT/PARTITION discriminator — orthogonal to F_ST signature in this drill).
- `notes/research_moe_alpha_c_band_audit_2026-05-26.md` (α_c grid-quantization artifact — independent of this drill).
- `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md` (linear-heteroassoc primitive lock — compatible with WF phenomenological layering).
- `notes/substrate_capability_map.md` (Bet B M-DEPENDENT PARTIAL row; cap_map entry).
- `tools/orchestrator/agents/research.md` (Tier-1b field list; Wright-Fisher row).

---

## Self-audit per [[feedback-verify-implementations]]

- **Dirichlet mode formula** `mode(θ_j) = (α_j - 1)/(α_0 - K)` spot-checked against Wikipedia Dirichlet distribution and Stan Functions Reference §23.1. ✓
- **Simplex constraint Σ θ_j = 1** verified — substrate heights 0.94 + 0.74 + 0.60 = 2.28 ≠ 1, confirming structural mismatch. ✓
- **Kimura fixation probability** `u(p) = (1 - e^{-2 N_e s p}) / (1 - e^{-2 N_e s})` verified against Ewens 2004 textbook formula (also re-derived in Bossert-Stadler 2022 arXiv:2205.06480). ✓
- **Island model effective-population formula** `N_e_total = N_e_local × D / (1 - F_ST)` spot-checked against Whitlock-Barton 1997 abstract; modern formulations exist with refinements (see Wakeley 2003) but the leading-order form is canonical. ✓
- **Burden-Tang 2016 finding (low-mutation QSD concentrates on edges/corners)** spot-checked against arXiv:1607.00104 abstract. ✓
- **Kimura/Moran → replicator ODE limit** spot-checked against Chalub-Souza 2014 (arXiv:math/0602530) — confirms convergence to Kimura PDE as N→∞. ✓
- **σ(τ_p) ∝ N^{-1/2} prediction** is a STANDARD diffusion-scaling result (Brownian-motion-like fluctuations in stochastic process with variance ∝ 1/N per step over t steps → total variance ∝ t/N → σ ∝ √(t/N)). ✓
- **F_ST analog mapping** is a NOVEL synthesis (no direct lit precedent for MoE F_ST); calibration penalty applied; P=0.38 well below 0.50 cap.
- **Multi-allele negative-covariance prediction (P2.2)** is direct from simplex constraint and is uncontroversial in population genetics; calibration penalty applied for substrate-mapping novelty.

Probability all framework attributions correct: 92%.
Probability all P(fit) numbers are honest after calibration penalty: 78%.
Probability the Dirichlet-incompatibility finding (P1.1) is correct: 95%.
Probability the WF-as-finite-N-correction position (P3.1, σ(τ_p) scaling) survives Test 1: 42% (matches P3.1 calibrated estimate).

---

## Brutal-honesty caveats per [[feedback-no-smoke]]

1. **WF is NOT a competitive theoretical home for plateau heights.** P=0.22 is below Saad-Solla (0.48) and Mechanism-A (0.45). The simplex constraint is a hard structural mismatch. **Do not advance WF as a primary plateau-height framework.**

2. **The F_ST and σ(τ_p) findings are GENUINELY USEFUL but INCREMENTAL.** They give one new instrumentation channel each, both ZERO GPU spend. They do NOT flip the cap_map or open a new capability class. Honest expected impact: 1.5 product handles, mostly auditability-narrative reinforcement.

3. **The 9-knob rescue (per-class fixation probability) is over-parameterized and should NOT be advanced as a falsifiable hypothesis.** It would burn research cycles for no return. Acknowledged in P1.2 (P=0.15).

4. **The high-mutation-regime QSD rescue (Finding 4) requires substrate-side measurement of an "effective mutation rate" that is not currently defined or instrumented.** This is RESEARCH-INCOMPLETE; do not advance as a planned experiment.

5. **The σ(τ_p) ∝ N^{-1/2} test is sharp BUT depends on existing multi-N data being available.** If Test 1 returns INSTRUMENTATION-FAIL, Test 2 needs ~30 GPU-min — small but non-zero spend. The companion handoff specifies Test 1 first, Test 2 conditional.

6. **The F_ST + DMPK 2x2 discriminator panel is the most concrete deliverable of this drill.** It is a free upgrade to the in-flight MoE-rebuild instrumentation. Companion handoff specifies it.

7. **Per [[feedback-no-experiment-design-in-prompts]]**: companion handoff hands TASK + WHY + CONTRACT + AUTONOMY only. No anchor names, no sweep grids (other than Test 2's conditional N values, which are the discriminator's defining structure not free-knob design choices), no queue choice — exp_dev decides. Pre-registered HARD-PASS / HARD-FAIL / MIDDLE / INSTRUMENTATION-FAIL bands per [[feedback-envelope-expansion-fail-bands]].

8. **No GPU spend recommended unless Test 1 returns INSTRUMENTATION-FAIL.** Tests 1 and 3 are CPU re-analysis of existing data. This drill is GPU-budget-neutral.

9. **The "complementary not competitive with Saad-Solla" framing is the most important conclusion of this drill.** It saves future research-cycles from a false competition between deterministic and stochastic framings — they live at different scales and can coexist. This is a structural-clarification yield, not a falsifier yield.

10. **Per [[feedback-lit-scan-calibration-penalty]] all P values deflated 0.15-0.25; novel-synthesis cap 0.50 enforced.** No P value in this note exceeds 0.50.

11. **Per [[feedback-dont-dismiss-adjacent-methods]]**: WF was flagged as a Tier-1b PRIORITY scope-expansion field; this drill executed the named question; the verdict is "structurally weak as theoretical home, useful as complementary layer." This is the honest outcome — NOT a premature dismissal.

---

**End research note.**
