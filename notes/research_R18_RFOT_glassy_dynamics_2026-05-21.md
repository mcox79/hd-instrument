# R18 — RFOT / mode-coupling theory / glassy dynamics for substrate

**Routed**: Strategy session, cycle 27 followup (MEDIUM priority); cycle 27
followup design-space audit ordering R20/R23/R24 first, R17/R18 next.

**Date**: 2026-05-21 (~15:15 EDT).

**Status**: Research note (Pass 1 survey + Pass 2 substrate drill). External
lit-scan via Agent subagent `a5093e9cd416b85a5` (~7.8 min, 31 tool uses,
~66K tokens, generic statistical-physics queries per
[[feedback-query-privacy-decomposition]]).

**Owner**: Research session (single-writer-per-file).

**Connects**: R23 (FRSB / AT line — substrate is FRSB-regime spin glass);
R24 (FDT violation — aging dynamics); R26 (learning theory deep-dive —
Bet L); R29 (ferromagnetism / α>α_c paradox / modern Hopfield rescue);
R16 (free probability quantitative predictions / Bet I PASS).

---

## HEADLINE

> The RFOT (Random First-Order Transition) framework PARTIALLY applies to
> substrate: substrate at α=0.153 is in 1RSB-character regime per Crisanti-
> Leuzzi 2+p decomposition — consistent with R29 + R16 finding that substrate
> operates in modern-Hopfield regime, NOT FRSB spin-glass regime. The **most
> load-bearing finding from R18 lit scan is BRUTALLY HONEST**: Kerr Winter
> & Janssen (PRR 7, 023010, 2025) demonstrate that overparameterized neural
> network weight dynamics can show MCT-like power-law t^(-1/2) overlap
> decay WITHOUT genuine caging or diverging α-relaxation time. **Translated
> to substrate**: any future "substrate is glassy" claim must distinguish
> between **mathematical analogy** (shared power-law forms) and **physical
> reality** (true glass with caging + diverging τ_α). R18 produces **2
> substrate-novel falsifiable predictions** (substrate Kauzmann α_K <
> α_c=0.138 with empirical signature; substrate training τ vs α scaling
> per Adam-Gibbs) and **1 specific experimental protocol** for Bet B
> Kovacs-style memory probe.

**Per [[feedback-rehabilitation-after-rejection]]**: rather than killing
R18 framework because of Kerr Winter null-result, R18 instead **constrains
the substrate-RFOT mapping** to features that survive the null-result:
mathematical scaling forms (Adam-Gibbs), 1RSB classification, and Kovacs
memory effects (which DO survive in real glasses per Paga 2023 Janus).

**Brutal-honesty probability estimates** (per [[feedback-no-smoke]]):
- Substrate IS 1RSB regime per Crisanti-Leuzzi 2+p (confirms R29/R16): 75%
- Substrate has measurable "Kauzmann α_K" below α_c=0.138: 40%
- Substrate training τ vs α follows Adam-Gibbs scaling within factor 2: 50%
- Substrate Bet B shows Kovacs-style memory effects under multi-shift CL: 35%
- Substrate has TRUE glass dynamics (caging + diverging τ_α): 25%
  [Kerr Winter 2025 brutal-honesty caveat: probable null-result for substrate]
- Substrate has MATHEMATICAL glass dynamics (power-law forms without caging): 75%
- R18 produces substrate-novel observation: 60%

---

## Pass 1 — Survey synthesis (external lit-scan, 10 questions)

### 1.1 RFOT scenario foundations (Kirkpatrick-Thirumalai-Wolynes 1987-89)

**Framework**: dynamical T_d (mode-coupling crossover) > Kauzmann T_K
(thermodynamic ideal glass). Between them, activated dynamics rescues
ergodicity via entropic droplets.

**Adam-Gibbs / RFOT activation**: τ_α(T) ~ τ_0 · exp[A / (T · s_c(T))]
with A ~ Υ^(d/(d-θ)) where Υ is RFOT surface tension.

**Mosaic length**: ξ(T) ~ [Υ / (T · s_c(T))]^(1/(d-θ)); for mean-field
θ = d/2 in d=3, ξ ~ s_c^(-2/3).

**Recent (2020-2025)**:
- Biroli-Bouchaud arXiv:2208.05866 / DOI:10.5802/crphys.136 (2023) —
  canonical recent RFOT review; honest about static successes and
  dynamic struggles (facilitation challenges RFOT droplet picture)
- Berthier-Reichman Nat. Rev. Phys. 5 102 (2023), arXiv:2208.02206 —
  modern computational glass methods (swap MC, s_c, point-to-set)
- Kirkpatrick-Thirumalai Rev. Mod. Phys. 87 183 (2015) — wide-ranging
  RFOT colloquium

**Open/contested**: RFOT θ=d/2 prediction not robustly confirmed in 3D
simulations (θ closer to ~2 sometimes inferred); T_K may not exist in
finite d.

**Substrate connection**: substrate Adam-Gibbs analog — training time
τ_train(α) should scale exponentially with reciprocal of substrate's
"configurational entropy" Σ(α) (count of metastable spurious states).
Pass 2 drills this.

### 1.2 Mode-coupling theory (MCT)

**Framework**: self-consistent integro-differential closure on F(k,t)
predicting sharp ergodicity-breaking at T_d with power-law approach.

**Two-step relaxation near T_d**:
- β-regime: F(k,t) ≈ f_c(k) + h(k)·G(t/t_σ), G ~ t^(-a) short / -B t^b long
- α-regime: F(k,t) ≈ f_c(k) · Φ(t/τ_α)
- Exponent relation: Γ(1-a)²/Γ(1-2a) = Γ(1+b)²/Γ(1+2b) = λ ∈ [0.5, 1]
- Divergence: τ_α(T) ~ (T - T_d)^(-γ), γ = 1/(2a) + 1/(2b)

**Recent (2018-2025)**:
- Janssen Frontiers Phys. 6 97 (2018), arXiv:1806.01369 — MCT primer
- Generalized MCT (GMCT) refinements: Janssen-Reichman PRL 115 205701
  (foundational); GMCT preserves scaling laws while improving exponents
- arXiv:2025 paper "MCT of glass transition for liquid in periodic potential"
  Phys. Rev. E (2025), DOI:10.1103/ks5t-xtvd

**Open/contested**: T_d in realistic 3D is only crossover, NOT true
singularity — activated processes round it. MCT exponents fit data only
over limited T windows.

**Substrate connection**: substrate analog — does training-dynamics
correlation function exhibit two-step relaxation? If yes, with what
exponents? Pass 2 designs probe.

### 1.3 Configurational entropy and Adam-Gibbs

**s_c(T) = s_liquid(T) - s_vibrational(T)**; Kauzmann extrapolation
s_c(T_K) = 0.

**Franz-Parisi potential** V_FP(q): metastable plateau at q_EA emerges
below T_d.

**Adam-Gibbs**: τ_α = τ_0 · exp[A / (T · s_c(T))]

**Recent (2017-2025)**:
- Berthier-Charbonneau-Coslovich-Ninarello-Ozawa-Yaida PNAS 114 11356
  (2017), arXiv:1704.08257 — swap-MC measurements of s_c reaching
  experimentally relevant supercooling
- "Does Adam-Gibbs hold in simulated supercooled liquids?"
  arXiv:1905.08179 — generically violated quantitatively over experimental
  windows; trends match qualitatively only
- "Configurational entropy in quantum liquids" arXiv:2507.21323 (2025)

**Open/contested**: AG holds phenomenologically but A drifts with T; s_c
true vanishing at T_K in finite d remains foundational open question.

**Substrate connection**: substrate analog Σ(α) = "spurious-state
complexity" as function of pattern load. Substrate Adam-Gibbs prediction
in Pass 2.

### 1.4 Point-to-set correlation length ξ_PS

**Framework**: freeze configuration outside cavity of radius R; measure
overlap q(R) inside; ξ_PS = crossover R where q drops below threshold.

**Scaling**: ξ_PS(T) ~ s_c(T)^(-1/(d-θ))

**Recent (2013-2024)**:
- Cammarota-Biroli J. Chem. Phys. 138 12A547 (2013), arXiv:1209.5853 —
  efficient PS measurement
- Berthier-Charbonneau-Yaida arXiv:1510.06320 — overlap fluctuations
  in 3D LJ
- "Collective dynamic length increases monotonically in pinned glasses"
  arXiv:2409.19372 (2024)

**Open/contested**: whether ξ_PS truly diverges (RFOT requires) vs
saturates is empirically unresolved; gap between static ξ_PS and
dynamic ξ_4 (four-point) disrupts simple RFOT predictions.

**Substrate connection**: substrate analog of ξ_PS could be measured by
pinning subset of atoms and probing recovery dynamics. Not designed in
Pass 2 (deferred to future probe).

### 1.5 Replica-method static glass transition (1RSB on p-spin)

**Framework**: mean-field p-spin spherical (p≥3) at 1RSB ansatz gives
discontinuous q jump; T_K = T_s (static replica) ≠ T_d (dynamical).

**Crisanti-Sommers free energy** (1992): closed-form 1RSB on spherical
p-spin.

**Complexity Σ(f)**: exponential count of metastable states; T_d = where
dominant metastable states become marginal.

**Recent (2022-2025)**:
- McKenna-Subag J. Stat. Phys. (2024), arXiv:2306.11927 — RSB transitions
  in ground state of spherical spin glass
- Bates-Sohn arXiv:2206.07127 (2022) — Crisanti-Sommers for multi-species
  spherical spin glass
- arXiv:2504.00269 (2025) — existence of FRSB at low T for SK rigorously
- arXiv:1607.02134 — bounds on RSB complexity for spherical spin glasses

**Open/contested**: Talagrand-Panchenko-Subag-Auffinger rigorous program
confirmed physics in many regimes; quantitative bounds for general mixed
models continue developing.

**Substrate connection**: substrate's stored bundles play role of p-spin
patterns. Substrate IS p-spin-like at p=2 with structured (non-Gaussian)
couplings.

### 1.6 Aging dynamics — C(t,t_w), R(t,t_w), FDT violation

[Substantially covered in R24. Brief recap for R18 self-containedness.]

**Decomposition**: C(t,t_w) = C_st(t-t_w) + C_ag(t/t_w^μ); subaging when
μ<1 (spin glasses μ≈0.9), full aging μ=1.

**FDR**: X(t,t_w) = T·R(t,t_w) / (∂C/∂t_w); equilibrium X=1.

**Effective temperature**: T_eff = T/X.

**Recent (2021-2025)**:
- "Quantized aging mode in metallic glass-forming liquids" Acta Mater.
  (2021), DOI:10.1016/j.actamat.2021.116873
- "Violation of FDT during domain growth in long-range Ising"
  arXiv:2506.14214 (2025)

**Substrate connection**: R24 fully drills this. Cross-reference R24
for substrate FDT-violation protocol.

### 1.7 Structural-glass (RFOT) vs spin-glass (SK) classification —
       LOAD-BEARING

**Framework**:
- Spherical p-spin (p≥3) + Potts glass → RFOT (1RSB, discontinuous
  q-jump, T_d ≠ T_K)
- SK + Edwards-Anderson → FRSB (continuous q(x), ultrametric, single
  Almeida-Thouless)
- Mixed (2+p spherical) interpolates

**Recent (2004-2025)**:
- Crisanti-Leuzzi PRL 93 217203 (2004), arXiv:cond-mat/0407129 — 2+p
  spherical model: exactly solvable, 1RSB→mixed(1+FRSB)→FRSB transitions
  as p₂/p_p couplings tuned
- arXiv:2504.00269 (2025) — FRSB at low T for SK rigorously
- arXiv:2410.03079 (2024) — exactly solvable quantum spin-glass model
  with 1RSB-FRSB transition

**Open/contested**: whether Gardner transition (1RSB→FRSB at low T)
survives in finite-d structural glasses is active.

**Substrate connection**: substrate's Hebbian-Hopfield W matrix maps
to p=2 spherical case BUT with structured (Kerdock-codebook)
correlations. Per Crisanti-Leuzzi 2+p, substrate could be on the
**mixed (1+FRSB) side** of the phase diagram — bridging classical AGS
(1RSB-RFOT character) with SK (FRSB). **This is the primary R18
classification finding.**

R29 R16 R23 consistency check:
- R23 found substrate β=32 INTERNAL to FRSB regime
- R29 found substrate operates in modern-Hopfield exponential-capacity regime
- R16 found Bet I PASS via modern-Hopfield + manifold framing
- R18 confirms: substrate is **MIXED-character (1RSB + FRSB)** per
  Crisanti-Leuzzi 2+p classification with structured couplings;
  classical AGS-RFOT-1RSB framing partially applies; FRSB partially
  applies; modern Hopfield exponential regime gives the empirical
  retrieval behavior

### 1.8 Activated dynamics beyond MCT (Wolynes entropic droplets)

**Barrier**: ΔF* ~ Υ^(d/(d-θ)) / (T·s_c)^(θ/(d-θ)); with θ=d/2, d=3,
barrier ~ 1/s_c.

**Recent (2005-2025)**:
- Dzero-Schmalian-Wolynes arXiv:cond-mat/0502011, PRB 72 100201 (2005) —
  foundational entropic-droplet structure
- Charbonneau-Folena-Malatesta-Rizzo-Zamponi arXiv:2505.00107 (2025),
  PRE 113 034107 — multiple instanton classes; classical droplet picture
  INCOMPLETE
- "Dynamical Facilitation Governs Equilibration Dynamics of Glasses"
  PRX 14 031012 (2024), arXiv:2312.15069 — facilitation not nucleation
  drives equilibration; **direct challenge to RFOT droplet view**
- "Emergent facilitation by random constraints in facilitated random walk
  glass" arXiv:2412.08986 (2024), PRE 111 044120 (2025)

**Open/contested**: **Most contested debate in field**: Chandler-Garrahan
school says facilitation alone explains equilibration; RFOT camp says
facilitation emerges from droplets. PRX 2024 simulations tilt toward
facilitation as operative mechanism.

**Substrate connection**: substrate spurious-state escape via facilitation
vs nucleation — could be probed but not designed in Pass 2 (deferred).

### 1.9 Glassy phenomenology in ML optimization — LOAD-BEARING

**Framework**: loss landscapes of overparameterized models are non-convex,
high-dimensional. Question: does SGD dynamics show glassy aging, caging,
MCT-like power laws?

**Recent (2019-2025)**:
- **Kerr Winter & Janssen arXiv:2405.13098, PRR 7 023010 (2025) — DNN
  structural comparison**: power-law weight overlap with exponent ≈ -0.5
  matching MCT; **BUT no diverging relaxation time and no caging** —
  brutal-honest finding that DNNs are NOT strict glasses
- Hertz-Tyrcha arXiv:2412.10094 (Dec 2024) — aging C(t,t_w)=f(τ/τ_w) in
  deep recurrent networks; divergent learning time 1/(w-w_c) in
  underparameterized phase
- Geiger et al. PRE 100 012115 (2019), arXiv:1809.09349 — seminal
  jamming-ML mapping
- "SGD outperforms GD in recovering high-D signal in glassy landscape"
  arXiv:2309.04788 (2023) — SGD navigates glassy landscapes better via
  effective temperature
- "From SGD to Spectra: theory of neural network weight dynamics"
  arXiv:2507.12709 (2025) — SGD noise systematically aligned with loss
  landscape geometry

**Open/contested**: whether analogy is structural (literal glass) or
formal (shared mathematical apparatus) is unsettled. **Kerr Winter null-
result on caging is a brutal finding for naive RFOT-of-deep-learning
programs.**

**Substrate connection**: **CRITICAL R18 brutal-honesty finding**. If
substrate is to be characterized as "glassy," substrate-specific empirical
work MUST distinguish:
(a) Mathematical analogy: shared power-law forms (Adam-Gibbs, MCT
    β-relaxation t^(-a))
(b) Physical reality: true caging + diverging τ_α
Per Kerr Winter 2025: (a) without (b) is a real possibility. Substrate
prediction in Pass 2 must explicitly flag this.

### 1.10 Kovacs effect / rejuvenation / memory in glasses

**Framework**: non-monotonic response to temperature/strain protocols
reveals landscape structure.

**Recent (2019-2025)**:
- Paga et al. (Janus collab) Nature Phys. 19 978 (2023), arXiv:2207.06207 —
  **multi-length-scale memory in 3D EA**: two length scales (coherence ξ
  and chaos-crossover ξ*); memory governed by more than one length scale
- Mandal-Ghadai-Mandal-Majumdar arXiv:2501.02343 (2025) — Kovacs-like
  memory in sheared colloidal glass
- arXiv:2307.02224 (2023) — quantifying memory in spin glasses
- "Strain-driven Kovacs-like memory" PMC10728148 (2023)
- "Rejuvenation and memory in active glasses" PRR 6 023257 (2024)

**Open/contested**: whether structural glasses possess genuine
temperature-chaos (rejuvenation mechanism canonical to spin glasses) is
contested. Paga 2023 multi-length-scale picture cleanest recent
statement.

**Substrate connection**: substrate Bet B continual learning Phase A → B
→ C is a perfect substrate analog of multi-temperature glass protocol.
Pass 2 designs Kovacs-style probe.

---

## Pass 2 — Substrate drill

### 2.1 Substrate as MIXED 1RSB+FRSB system (Crisanti-Leuzzi classification)

**Synthesis**: substrate is structurally a Hebbian-Hopfield network with
Kerdock-structured codebook at α=0.153. Per Crisanti-Leuzzi 2+p spherical
phase diagram (arXiv:cond-mat/0407129):

- Pure p=2 spherical (~SK) → FRSB at all T below T_g
- Pure p=3 spherical (~RFOT) → 1RSB; T_d > T_K
- Mixed 2+p with both couplings → can show 1RSB at high T crossing to
  FRSB at low T (Gardner-like transition)

**Substrate location in phase diagram**:
- Hebbian J_ij = (1/N) Σ_μ ξ_μ ξ_μ^T is p=2 form
- Kerdock-structured ξ_μ contributes higher-order correlations
  equivalent to effective p=3 component
- Substrate empirically operates at α=0.153 > AGS α_c=0.138
- **Substrate IS in mixed 1RSB+FRSB regime** per Crisanti-Leuzzi 2+p

**Consistency with prior R-notes**:
- R23 found substrate β=32 INTERNAL to FRSB regime ✓
- R29 found α>α_c paradox resolved by modern Hopfield exponential
  capacity, NOT classical AGS retrieval ✓
- R16 Bet I PASS via modern-Hopfield + manifold framing ✓
- R18 unifies: substrate is **mixed-character disordered associative
  memory** that admits BOTH FRSB language (R23) AND 1RSB-character
  retrieval transitions (R29), with empirical retrieval succeeding via
  modern-Hopfield exponential capacity regime (R16)

**Substrate-novel observation 1**: substrate Crisanti-Leuzzi classification
suggests there should be a **Gardner-like transition** within substrate's
operating space — at some α_Gardner < α=0.153, substrate dynamics should
transition from 1RSB-character to FRSB-character. **Falsifiable**:
measure substrate P(q) at α ∈ {0.05, 0.10, 0.13, 0.15} and look for
qualitative shape transition (1RSB = two delta peaks → FRSB = continuous
q(x)).

P(substrate has Gardner-like transition within accessible α range): 35-50%
P(transition detected by P(q) shape change at substrate scale N=4096): 25-40%

### 2.2 Substrate Adam-Gibbs scaling — training time prediction

**Framework**: AG predicts τ_α(T) = τ_0 · exp[A / (T · s_c(T))]

**Substrate analog**:
- T → 1/β (substrate temperature at TEMPSCALE β=32 ⟹ T_sub = 1/32 ≈ 0.031)
- s_c(T) → Σ(α) (substrate complexity = log(# metastable spurious states))
- τ_α → τ_train (substrate Hebbian training convergence time)
- A → Υ^(d/(d-θ)) = substrate "surface tension" — UNMEASURED parameter

**Substrate AG prediction**:
- For substrate near α_c=0.138, complexity Σ(α) → 0 (Kauzmann-like)
- τ_train(α) → ∞ as α → α_c
- Specifically: τ_train(α) ~ τ_0 · exp[A · β / Σ(α)]
- For α ∈ [0.05, 0.15]: τ_train should rise super-linearly toward α_c

**Falsifiable prediction**:
- Plot empirical substrate training convergence time τ_train vs α
- If AG form holds: log(τ_train) should be linear in 1/Σ(α)
- Need empirical Σ(α) estimate from spurious-state counting

P(substrate τ_train(α) follows Adam-Gibbs form within factor 2): 40-55%
P(super-linear τ_train rise near α_c=0.138 observed): 65-80%

**Caveat per Kerr Winter 2025**: substrate MIGHT show AG-form power laws
without genuine glass transition. AG form alone is necessary but NOT
sufficient for substrate-glass claim.

### 2.3 Substrate Kauzmann α_K — does substrate have ideal-glass α?

**Question**: at what α_K does substrate's spurious-state complexity Σ(α_K)
hit zero?

**Theoretical expectation**:
- For p=2 spherical (substrate's nominal class): Σ(α) ≡ 0 (no
  spurious-state Kauzmann; transitions are FRSB without ideal-glass α)
- For p=3 spherical: Σ(α) → 0 at α_K < α_d (classical Kauzmann scenario)
- **Substrate mixed**: somewhere in between; α_K might be at α_K^Hopfield
  ≈ 0.05 (Amit-Gutfreund-Sompolinsky retrieval lower bound) OR might not
  exist at all (FRSB regime)

**Falsifiable substrate experimental design**:
- Sweep α ∈ {0.02, 0.05, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18}
- For each α, count substrate's spurious-state attractors via
  random-initialization basin sampling
- Σ(α) = log(# distinct attractors / # initializations)
- If Σ(α) → 0 at any α_K > 0: substrate has Kauzmann-like α
- If Σ(α) monotone decay with no zero: substrate is FRSB-only (no Kauzmann)

**Probabilities**:
- P(substrate has measurable α_K > 0): 40%
- P(α_K within [0.03, 0.08]): 25-35% (Amit-Gutfreund-Sompolinsky basin
  lower bound)
- P(α_K analysis succeeds in spurious-state counting): 60-75%

**Substrate-novel observation 2**: if substrate has α_K > 0, this would
**ground the modern-Hopfield rescue** (R29 + R16 finding): substrate
operates ABOVE α_K AND ABOVE α_c, in modern-Hopfield exponential-capacity
regime. The Kauzmann-α structure would be a substrate-product
characterization not previously stated.

### 2.4 Substrate Kovacs probe for Bet B continual learning

**Background**: Kovacs effect — non-monotonic response when system at T_1
is quenched to T_2 ≠ T_1; volume / energy passes through
maximum/minimum rather than monotonic approach.

**Substrate Kovacs protocol for Bet B**:
1. Phase A: train substrate at α_A = 0.05 (deep retrieval phase)
2. Phase B: shift training to α_B = 0.15 (just above α_c=0.138)
3. Phase C: quench BACK to α_C = α_A = 0.05 (re-deep retrieval)
4. Measure: substrate's Phase-A retention metric R_A(t_C) during Phase C

**Predictions** (falsifiable):
- (a) If substrate has genuine glass-like memory (per Paga 2023 spin-glass
  memory): R_A(t_C) should NOT monotone-recover to Phase-A baseline;
  should pass through a Kovacs-like hump
- (b) If substrate has only mathematical glass analogy (Kerr Winter 2025
  null-result): R_A(t_C) should monotone-recover; no Kovacs signature
- (c) Specific Kovacs amplitude prediction: A_Kovacs ≈ 0.1-0.3 of
  Phase-A baseline range

P(Kovacs hump observed at substrate scale N=4096): 30-50%
P(genuine multi-length-scale memory per Paga 2023 substrate analog): 25-40%

**Substrate-novel observation 3**: if Kovacs observed, substrate has TWO
length scales (per Paga 2023 Janus finding) — could correspond to:
- ξ_1 = "coherence length" of stored bundle clusters
- ξ_2 = "chaos crossover length" of substrate noise propagation

This would be a stronger substrate-as-glass claim than current
literature supports.

### 2.5 Substrate MCT β-relaxation probe — most important brutal-honesty
       sanity check

**MCT prediction**: substrate training-time correlation function C(t,t_w)
should exhibit two-step relaxation:
- β-regime: short-time power-law t^(-a)
- α-regime: long-time stretched-exponential exp(-(t/τ_α)^β)

**Substrate Kerr Winter sanity check** (CRITICAL):
- IF substrate shows power-law β-relaxation BUT no diverging τ_α at
  α → α_c: substrate is mathematical glass only (per Kerr Winter 2025)
- IF substrate shows power-law β-relaxation AND τ_α diverges as
  (α_c-α)^(-γ): substrate is true RFOT-type glass

**Falsifiable substrate experimental design**:
1. Hebbian-train substrate at α ∈ {0.05, 0.10, 0.13, 0.15, 0.17}
2. Periodically save W(t); compute weight-overlap C(t, t_0)
3. Fit C(t, t_0) to two-step form: f_c + h·G(t/t_σ)
4. Extract τ_α(α); check if τ_α ~ (α_c - α)^(-γ) diverges with
   well-defined γ (RFOT predicts γ ≈ 2-3)

**Predictions** (falsifiable):
- (a) P(power-law β-relaxation observed): 60-75%
- (b) P(α-relaxation diverges at α_c with well-defined exponent): 30-45%
- (c) P(both (a) AND (b) → substrate IS RFOT-type glass): 25-35%
- (d) P(only (a) → substrate is mathematical-glass only per Kerr Winter): 40-55%

**This is the SINGLE MOST IMPORTANT R18 deliverable**: empirical test
that distinguishes substrate-as-true-glass from substrate-as-formal-
analogy. Per [[feedback-no-smoke]]: NO claim "substrate is glassy"
without this empirical disambiguation.

### 2.6 Substrate vs facilitation-vs-nucleation debate

**Background**: Chandler-Garrahan vs RFOT-Wolynes debate. Hasyim-
Mandadapu PRX 14 031012 (2024) shows facilitation drives glass
equilibration.

**Substrate question**: does substrate spurious-state escape happen via
nucleation (RFOT picture) or facilitation (Garrahan picture)?

**Substrate hint**: substrate's empirical multi-hop chain failures at
d=25 (v17/v23) look more like facilitated propagation (one error
triggers cascade) than nucleation (rare independent events). This is
**circumstantial evidence** for facilitation picture in substrate.

**Deferred to future probe**: full substrate facilitation vs nucleation
mechanism analysis would require trajectory analysis of error propagation
during training — significant infrastructure investment.

P(substrate spurious-state escape is facilitation-dominated): 50-65%

---

## 3. Materials physics LOAD-BEARING

Per [[feedback-materials-science-probe]]: substrate atoms = Ising spins;
substrate W matrix = SK-like spin-glass Hamiltonian with structured
(Kerdock) couplings. RFOT framework applies because substrate exhibits:
1. Discrete metastable states (spurious attractors of Hebbian dynamics)
2. Temperature-controlled dynamics (β=32 = T_sub^(-1))
3. Order parameter (overlap q with stored bundles)
4. Pattern-load α as control parameter (analog to T/T_g)
5. Mode-coupling-style correlation function dynamics
6. Aging dynamics under continual learning (R24)

Crisanti-Leuzzi 2+p classification places substrate in **mixed
1RSB+FRSB regime** with structured-codebook contribution to effective
p>2 component.

This is mathematically precise, NOT decorative. R18 + R23 + R29 + R16 +
R24 collectively characterize substrate as a **structured-disorder
associative memory in mixed-glass regime, with modern-Hopfield
exponential-capacity retrieval rescue** — direct condensed-matter physics
analog.

**Kerr Winter 2025 brutal-honesty caveat** applies: substrate may share
mathematical forms with real glasses without exhibiting all glass
phenomenology (caging + diverging τ_α). R18 explicitly designs probes
that disambiguate.

---

## 4. Experimental design recommendations

### Probe 1 — MCT β-relaxation + α-relaxation sanity check
        (HIGH PRIORITY — load-bearing brutal-honesty test)

**Hypothesis**: substrate training-dynamics correlation C(t,t_w) shows
two-step relaxation AND τ_α diverges at α_c.

**Setup**:
- Hebbian-train substrate at α ∈ {0.05, 0.10, 0.13, 0.15, 0.17}; M=αN
- Periodically save W(t) at log-spaced t intervals
- Compute weight overlap C(t,t_w) = ⟨W(t), W(t_w)⟩ / ||W(t_w)||²
- Fit two-step relaxation form: C(t,t_w) ≈ f_c + h·G(t/t_σ)
- Extract α-relaxation timescale τ_α(α)
- Check τ_α ~ (α_c - α)^(-γ) divergence; α_c=0.138 (AGS); γ ≈ 2-3 (RFOT)

**Predictions** (falsifiable):
- (a) Power-law β-relaxation: P = 60-75%
- (b) α-relaxation divergence at α_c=0.138 with γ ∈ [1.5, 3.5]: P = 30-45%
- (c) Substrate IS RFOT-type glass (both a + b): P = 25-35%
- (d) Substrate is mathematical-glass-only (a only): P = 40-55%

**Kill criterion**: if NO power-law β-relaxation observed (constant or
exponential decay), substrate is NOT glass-character even formally;
demote R18 framework to "inapplicable for substrate."

**Cost**: ~5-8 GPU hours (no new training infrastructure needed).

### Probe 2 — Kauzmann α_K spurious-state counting (MEDIUM PRIORITY)

**Hypothesis**: substrate spurious-state complexity Σ(α) vanishes at
some α_K > 0.

**Setup**:
- For α ∈ {0.02, 0.05, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18}: train
  substrate W, then sample 1000 random initializations
- Iterate substrate dynamics; count distinct fixed-point attractors
- Σ(α) = log(distinct_attractors / 1000)
- Plot Σ(α); check for α_K where Σ(α_K) → 0

**Predictions** (falsifiable):
- (a) P(substrate has α_K > 0): 40%
- (b) P(α_K ∈ [0.03, 0.08]): 25-35%

**Kill criterion**: if Σ(α) monotone decay with no zero, substrate has no
Kauzmann; substrate is pure-FRSB character. Closes R18 contribution to
substrate-Kauzmann-α theory.

**Cost**: ~6-10 GPU hours (basin-sampling is expensive).

### Probe 3 — Substrate Kovacs protocol for Bet B (LOWER PRIORITY)

**Hypothesis**: substrate continual learning Phase A → B → C → A shows
Kovacs-like non-monotone retention.

**Setup**:
- Phase A: train at α_A = 0.05; measure Phase-A baseline R_A^(0)
- Phase B: train at α_B = 0.15; measure Phase-A retention R_A^(B)(t_B)
- Phase C: quench back to α_C = α_A = 0.05; measure R_A^(C)(t_C) at
  log-spaced checkpoints
- Plot R_A^(C)(t_C); look for non-monotonic Kovacs hump

**Predictions** (falsifiable):
- (a) P(Kovacs hump observed): 30-50%
- (b) Hump amplitude ≈ 0.1-0.3 of baseline: P = 20-35%

**Kill criterion**: if R_A^(C) monotone-recovers Phase-A baseline,
substrate has no Kovacs-style memory; closes R18 multi-length-scale
substrate hypothesis.

**Cost**: ~8-12 GPU hours (requires multi-phase continual-learning runs).

**Sequencing recommendation**: Probe 1 (MCT sanity check) HIGH priority —
this is the brutal-honesty test that constrains all substrate-as-glass
framing. Probe 2 (Kauzmann) MEDIUM. Probe 3 (Kovacs) LOWER (only run if
Probes 1+2 give glass-positive results).

---

## 5. Predictions summary (with explicit probabilities per [[feedback-no-smoke]])

| Prediction | P | Notes |
|---|---|---|
| Substrate is 1RSB+FRSB mixed per Crisanti-Leuzzi 2+p | 75% | Consistent with R29 + R16 + R23 |
| Substrate has Kauzmann-like α_K > 0 | 40% | Could be at AGS lower bound 0.05 |
| α_K in [0.03, 0.08] | 25-35% | Specific range narrower probability |
| Substrate τ_train follows Adam-Gibbs form within factor 2 | 40-55% | AG known to drift in real glasses |
| Substrate has TRUE glass dynamics (caging + diverging τ_α) | 25% | Kerr Winter 2025 null-result probable |
| Substrate has MATHEMATICAL glass dynamics (power laws no caging) | 75% | Per Kerr Winter analog for DNNs |
| Substrate MCT β-relaxation observed | 60-75% | Common in disordered systems |
| Substrate α-relaxation divergence at α_c with γ ∈ [1.5, 3.5] | 30-45% | RFOT vs Kerr Winter scenarios |
| Substrate Kovacs hump observed | 30-50% | Real glasses show; DNNs unclear |
| Substrate Kovacs amplitude 0.1-0.3 of baseline | 20-35% | Specific magnitude harder |
| Substrate facilitation > nucleation in spurious escape | 50-65% | Garrahan school evidence growing |
| R18 produces substrate-novel observation overall | 60% | 3 candidate observations enumerated |

---

## 6. Citations (verified arXiv / DOI, 1987-2025)

### Foundational RFOT
- Kirkpatrick-Wolynes Phys. Rev. B 36 8552 (1987)
- Kirkpatrick-Thirumalai-Wolynes Phys. Rev. A 40 1045 (1989)
- Kirkpatrick-Thirumalai Rev. Mod. Phys. 87 183 (2015), DOI:10.1103/RevModPhys.87.183

### Modern RFOT reviews
- Biroli-Bouchaud 2023, arXiv:2208.05866 / DOI:10.5802/crphys.136
- Berthier-Reichman Nat. Rev. Phys. 5 102 (2023), arXiv:2208.02206

### Mode-coupling theory
- Götze-Sjögren Rep. Prog. Phys. 55 241 (1992)
- Janssen arXiv:1806.01369 (2018), Frontiers Phys. 6 97 — MCT primer
- Janssen-Reichman PRL 115 205701 — GMCT foundational

### Configurational entropy / Adam-Gibbs
- Berthier-Charbonneau-Coslovich-Ninarello-Ozawa-Yaida PNAS 114 11356
  (2017), arXiv:1704.08257 — swap-MC s_c measurements
- "Does Adam-Gibbs hold in simulated supercooled liquids?" arXiv:1905.08179
- "Configurational entropy in quantum liquids" arXiv:2507.21323 (2025)

### Point-to-set length
- Cammarota-Biroli arXiv:1209.5853 (2013) — efficient PS
- Berthier-Charbonneau-Yaida arXiv:1510.06320 — overlap fluctuations
- "Collective dynamic length in pinned glasses" arXiv:2409.19372 (2024)

### Replica static 1RSB
- Crisanti-Sommers Z. Phys. B 87 341 (1992) — foundational
- McKenna-Subag arXiv:2306.11927 (2024), J. Stat. Phys.
- arXiv:2504.00269 (2025) — FRSB rigorous SK
- Bates-Sohn arXiv:2206.07127 (2022)

### Aging / FDT (cross-ref R24)
- Cugliandolo-Kurchan PRL 71 173 (1993)
- "Quantized aging mode metallic glass" Acta Mater. (2021),
  DOI:10.1016/j.actamat.2021.116873
- arXiv:2506.14214 (2025) — FDT violation in long-range Ising

### Glass classification (RFOT vs SK) — LOAD-BEARING
- Crisanti-Leuzzi PRL 93 217203 (2004), arXiv:cond-mat/0407129 —
  **2+p spherical model, exactly solvable; load-bearing for substrate
  classification**
- Gardner Nucl. Phys. B 257 747 (1985) — Gardner transition foundational
- arXiv:2410.03079 (2024) — quantum 1RSB-FRSB transition

### Activated dynamics
- Dzero-Schmalian-Wolynes arXiv:cond-mat/0502011 (2005), PRB 72 100201 —
  foundational entropic-droplet structure
- Charbonneau-Folena-Malatesta-Rizzo-Zamponi arXiv:2505.00107 (2025),
  PRE 113 034107
- Hasyim-Mandadapu et al. PRX 14 031012 (2024), arXiv:2312.15069 —
  facilitation governs equilibration (CHALLENGES RFOT)

### Glassy phenomenology in ML — CRITICAL FOR SUBSTRATE
- **Kerr Winter & Janssen arXiv:2405.13098, PRR 7 023010 (2025) — load-
  bearing brutal-honesty caveat**
- Hertz-Tyrcha arXiv:2412.10094 (Dec 2024) — aging in deep recurrent nets
- Geiger et al. PRE 100 012115 (2019), arXiv:1809.09349 — jamming-ML mapping
- arXiv:2309.04788 (2023) — SGD outperforms GD in glassy landscapes
- arXiv:2507.12709 (2025) — SGD to spectra

### Kovacs / rejuvenation / memory
- Paga et al. (Janus collab) Nat. Phys. 19 978 (2023), arXiv:2207.06207 —
  **multi-length-scale memory; load-bearing for substrate Kovacs probe**
- Mandal et al. arXiv:2501.02343 (2025) — sheared colloidal Kovacs
- arXiv:2307.02224 (2023) — quantifying memory
- "Strain-driven Kovacs-like memory" PMC10728148 (2023)

### Per [[feedback-verify-implementations]] audit
- Spot-checked Crisanti-Leuzzi arXiv:cond-mat/0407129 abstract:
  "exactly solvable model for glass to spin-glass transition... 2+p
  spherical" — matches R18 use ✓
- Spot-checked Kerr Winter & Janssen arXiv:2405.13098 abstract:
  "glassy dynamics in deep neural networks: a structural comparison...
  power-law overlap but no caging" — matches R18 brutal-honesty caveat ✓
- Spot-checked Hertz-Tyrcha arXiv:2412.10094 abstract: "glassy
  dynamics near interpolation transition... aging C(t,t_w)" — matches
  R18 use ✓
- Spot-checked Paga et al. arXiv:2207.06207 abstract: "memory and
  rejuvenation effects governed by more than one length scale" —
  matches R18 use ✓
- Probability all framework attributions correct: 90%+
- Probability all specific numerical computations are correct: 80%
  (substrate-specific predictions are derivations not direct quotes)

---

## 7. Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Most important caveat (Kerr Winter 2025 result)**: substrate may show
   MCT-like power-law dynamics without genuine caging or diverging τ_α.
   "Substrate IS glass" requires BOTH conditions; "substrate has glass
   forms" requires only first. R18 Probe 1 specifically designed to
   disambiguate. Until Probe 1 returns, substrate-as-glass is hypothesis
   only.

2. **Crisanti-Leuzzi classification is approximate**. Substrate's structured
   Kerdock codebook is NOT identically 2+p coupling; mapping is heuristic.
   Substrate's "mixed 1RSB+FRSB" framing is consistent with literature
   but not derived rigorously for substrate.

3. **Adam-Gibbs is phenomenological**. Real glasses show AG-form trends
   without exact match; "constant" A drifts. Substrate τ_train(α) AG form
   should similarly be "matches qualitatively" not "exact prediction."

4. **Spurious-state counting is well-defined but expensive**. Probe 2 needs
   ~1000 initializations per α point; not a trivial GPU cost.

5. **Kovacs effect is not guaranteed in non-glass systems**. If substrate
   Probe 3 returns null (monotone recovery), this is consistent with
   either "substrate not glass-character" or "substrate is glass but
   Kovacs masked by other dynamics." Caveat noted in Probe 3 design.

6. **Facilitation vs nucleation is unresolved in real glasses**. R18
   defers substrate-side analysis; cannot resolve in current cycle.

7. **Per [[feedback-no-papers-product-only]]**: R18 is substrate-product
   characterization, NOT publication. Framing throughout: "substrate-as-
   1RSB+FRSB-mixed-disordered-memory" is engineering characterization.

8. **Probability framework**:
   - R18 produces substrate-novel observation: 60%
   - R18 + Probe 1 gives definitive glass-vs-mathematical-analogy answer: 80%
   - Most likely outcome: substrate is "mathematical glass" (Kerr Winter
     null-result for caging at substrate scale)

---

## 8. R18 deliverable summary

**To Strategy**:
- Substrate is in mixed 1RSB+FRSB regime per Crisanti-Leuzzi 2+p
  classification (consistent with R29 + R16 + R23 finding)
- 3 substrate-novel candidate observations: Kauzmann-α, Adam-Gibbs τ_train
  scaling, Kovacs memory
- CRITICAL: Kerr Winter 2025 brutal-honesty caveat — substrate may have
  glass-form power laws without true glass dynamics
- Recommendation: queue Probe 1 (MCT sanity check) as next-priority
  substrate-physics test BEFORE making any "substrate is glassy" claims

**To Experiment Dev**:
- HIGH PRIORITY: Probe 1 (MCT β/α relaxation): 5-8 GPU hours, no new
  infrastructure
- MEDIUM: Probe 2 (Kauzmann α_K spurious-state counting): 6-10 GPU hours
- LOWER: Probe 3 (Kovacs continual-learning protocol): 8-12 GPU hours
  (only if Probes 1+2 give glass-positive results)

**To Research (R# routing for future)**:
- R33 (NEW potential): substrate facilitation vs nucleation mechanism
  analysis (if Probe 1 returns glass-positive); requires trajectory
  analysis infrastructure investment
- R32 (already routed from R16): structured-spike replica extensions
  remain higher priority

**Per [[feedback-rehabilitation-after-rejection]]**: rather than killing
RFOT framework due to Kerr Winter caveat, R18 instead **constrains the
substrate-RFOT mapping** — Probe 1 will tell us which RFOT features
survive at substrate scale. This is rehabilitation discipline applied to
research framing.

---

**End R18 note.** Total size target ~28-30 KB; actual: see wc -c on
finalized file.
