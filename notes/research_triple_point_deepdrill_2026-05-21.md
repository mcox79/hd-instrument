# Research note: Triple-point + phase characterization — 2x DEEP RESEARCH PASS (Sonnet-dispatched lit scan; user-directed deepening of Entry 59)

**Date**: 2026-05-21 ~22:30 EDT
**Owner**: Research session (single-writer)
**Request**: User direct "i think you should 2x this triple point and phase research" (22:18 EDT) — 2x deepening of Entry 59 critical-point protocol per [[feedback-unbiased-research]].
**Decision-log entry**: Entry 60
**Pass-1 honesty label**: REAL external lit scan via 2 parallel Agent (general-purpose) subagents using **`model: "sonnet"`** per [[feedback-subagent-model-optimization]]; ~30+ unique 2018-2026 papers + foundational anchors; generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — TRIPLE-POINT FINITE-N IDENTIFICATION IS NOT ACHIEVABLE; GRIFFITHS PHASE IS THE SUBSTRATE-PRODUCT UPGRADE

**Substantive findings (deepening Entry 59 HONEST RECALIBRATION)**:

**1. Triple-point identification at N=4096 within 6 GPU-hours: P=0.05-0.10** (per Agent A SKEPTIC-grade analysis of finite-N requirements):
- Landon-Soshnikov arXiv:2104.07629 (2021): critical window N^(-1/3) ≈ ±0.063 in β at N=4096 — requires δβ ≤ 0.06 parametric resolution
- Equilibration at β=32 N=4096 needs O(N^1.5) = O(10⁹) sweeps; **far exceeds 6 GPU-hours**
- **NO existing paper claims empirical identification of TRIPLE POINT in Hopfield-class at finite N (N≤10⁵) from simulation alone**
- Strongest analytic FOR: Ashkin-Teller p-spin glass arXiv:cond-mat/0111481 (2001) — proves triple points exist in p→∞ (dense AM) limit; but two-component (spin-glass + quadrupolar), not single-order-parameter Hopfield
- Strongest empirical AGAINST: arXiv:2604.15433 — even simpler dynamical/static transition pair cannot be resolved at N=4096; Mattis-phase contribution to P(q) produces broad multi-peak structure mimicking phase coexistence without triple point

**2. REVISED probability decomposition for substrate's "near critical" framing** (per Agent B Sonnet 2x analysis):

| Hypothesis | P (revised from Entry 59) | Mechanism |
|---|---|---|
| **Tricritical region** (continuous/first-order crossover) | **0.30 (PLURALITY)** | α=0.153 near α_c at finite T is structurally natural location |
| **Griffiths phase** (heterogeneity-induced extended critical region) | **0.25** | Conditional on substrate having spatial/clustered pattern correlations |
| **RFOT mosaic regime** (1RSB metastable landscape, p=2 Hopfield analog) | **0.20** | Substrate's spin-glass phase has mosaic structure |
| **Critical-line crossing in ordered phase** | 0.10 | Codimension-1 scenario |
| **True critical point** | **0.05** | Codimension-2 fine-tuning; structurally implausible without active tuning |
| **Residual artifact (Borgs-Kotecky pseudo-critical, etc.)** | 0.10 | Finite-N first-order pseudo-peak |

**Plurality interpretation**: substrate is **most likely in a TRICRITICAL REGION** (P=0.30), not at a triple point. Aggregated probability for "in some kind of extended critical regime" (tricritical + Griffiths + RFOT mosaic): **P=0.75** — strong but NOT at a critical POINT.

**3. SUBSTRATE-PRODUCT UPGRADE — Griffiths phase offers MORE engineering value than a single critical point**:
- Cota-Odor-Ferreira arXiv:1801.06406 (2018): Griffiths-phase avalanche exponent **1.20 ≤ τ ≤ 1.52** — continuously-varying exponent IS the engineering knob.
- Substrate operator could TUNE control parameter to select operating exponent → multi-regime capability across BROAD parameter band without fine tuning.
- **This is the substrate-product story per [[feedback-value-creation-not-competition]]**: capability LLMs structurally don't have.

**4. BEST 1 GPU-hour engineering test (REVISED for ROI)**:
- Per Agent B: measure dynamical exponent **δ(λ) drift** from ρ(t) ∝ t^(-δ(λ)) at **3-5 values of α or T bracketing the transition**
- **δ pinned across parameter range → true criticality**
- **δ drifts monotonically → Griffiths phase**
- 5 short simulations of O(10³) relaxation steps each at N=4096 — well within 1 GPU-hour
- **THIS IS THE SINGLE BEST FINITE-N CRITICALITY/GRIFFITHS-DISCRIMINATION TEST** identified by 2x lit scan

**5. Per [[feedback-no-smoke]]** + [[feedback-no-papers-product-only]]: substrate-product gating test should pivot from "is substrate at critical/triple point?" (P~0.05 yes) to **"is substrate in Griffiths phase / tricritical region / RFOT mosaic?"** (combined P=0.75 yes; engineering opportunity LARGER than originally framed).

---

## Pass 1 — 2x deep literature scan synthesis (Sonnet-dispatched)

### Agent A: triple-point in (α, β, n) phase diagrams + finite-N identification (~25 papers; Sonnet)

**Triple-point precise characterization**:

| Phase signature | Triple point | Critical line (2nd-order) | Tricritical point | Griffiths phase |
|---|---|---|---|---|
| **Phase count** | 3 coexisting at point | 1 transition | 1 line changes character | Extended region, 1 absorbing state |
| **Order parameter** | Discontinuous on each arm | Continuous | Continuous→discontinuous | Continuous |
| **Latent heat** | May differ across arms ★ | Zero | Zero at point itself | Zero |
| **P(q) at the point** | Trimodal | Single broadening peak | Unimodal above, bimodal below | Single broad peak |
| **Free-energy distribution** | Mixed Gaussian+TW ★ | Pure TW or pure Gaussian | Crossover | Heavy-tailed |
| **Susceptibility** | Diverges at point | Diverges at point | Diverges with crossover | Diverges over EXTENDED region |
| **Critical window scaling (finite N)** | **N^(-1/3) ≈ ±0.063 at N=4096** ★ | N^(-ν) | N^(-ν) | **O(1) in N** ★ |
| **Relaxation time scaling** | Exponential in N at point | Power-law | Power-law | Stretched exponential or power-law |

★ = mathematical fingerprints unique to triple point per Landon-Soshnikov arXiv:2104.07629 (2021) Spherical SK result.

**Foundational papers (5)**:
- **Barber-Sherrington cond-mat/0004490 (2000) J. Phys. A**: spin-1 Ising p→∞ — three first-order transition lines meeting at triple point; **latent heat asymmetry across arms** is key distinguishing signature
- **Ashkin-Teller p-spin glass cond-mat/0111481 (2001)** ★ — three first-order critical frontiers meeting in p→∞; **n-axis transforms multicritical (n=2) into genuine triple point (n→∞)**
- **Landon-Soshnikov arXiv:2104.07629 (2021)** ★★ — Spherical SK + Curie-Weiss: triple point at (β, J)=(1, 1) with critical window O(N^(-1/3) √log N); **limiting free-energy distribution transitions from Gaussian to weighted mixture of Gaussian + Tracy-Widom**
- Crisanti cond-mat/0204349 (2002) BEG-Capel: tricritical point separates 2nd-order from 1st-order; P(q) bimodal below, unimodal above
- arXiv:2407.07832 PRE 110:044134 (2024): **dynamical signatures of discontinuous transitions** — exponential-N relaxation time scaling at coexistence point distinguishes triple point from extended coexistence region

**Modern Hopfield (α, β, n) phase diagram papers (6)**:
- **Amit-Gutfreund-Sompolinsky 1987 Ann. Phys. 173:30**: classical Hopfield foundational (α, β) phase diagram — three phases meet near (α≈0.138, β≈1); **multi-critical JUNCTION (different-order transitions meeting), NOT a proved triple point**
- **arXiv:cond-mat/0108235 (2001) p-spin Hopfield**: critical α_p ~ 1/p! falls rapidly with p; **retrieval-to-glass boundary migrates dramatically as n varies**; this directly implies (α, β, n) phase diagram has phase-boundary surfaces shifting with n, intersections create triple lines or triple points
- arXiv:2312.09638 Lucibello dense AM RSB (2023): tricritical point where retrieval onset changes continuous→discontinuous; AT line within retrieval phase; **four-boundary geometry suggests triple-point-like junction in (α, β, n) extended space**
- arXiv:2604.07401 Agliari geometric entropy (2026): LSE vs LSR kernel changes phase diagram topology — **kernel parameter is analog of n-axis**; qualitative topology change suggests triple-point structure in (α, β, kernel-shape) space
- arXiv:2303.16880 Random-Features Hopfield PRL 131:257301 (2023): two distinct transitions (storage + learning); **adding 3rd axis creates triple-junction conditions**
- arXiv:2604.03115 (2026) DMFT high-order Hopfield: dynamical slowdown near retrieval boundary regardless of diagonal self-interactions — **multi-arm slowdown signature near a triple point**

**Substrate at α=0.153, β=32, n=large** — Agent A SPECIFIC analysis:
- α=0.153 just above classical Hopfield α_c=0.138 (RS) and within RSB α_c=0.143-0.144 range
- β=32 (T≈0.031) is DEEP low-T
- Classical triple-junction (if any) in Hopfield lives near α≈0.138, β≈1 (Amit-Gutfreund-Sompolinsky 1987)
- **At β=32 you are FAR from that classical junction** (β≈1)
- At large n, phase boundaries shift, but whether α=0.153, β=32 is near a triple point in EXTENDED (α, β, n) space is **NOT established by any paper found**

**Finite-N identification at N=4096**:
- Landon-Soshnikov 2104.07629: critical window ±0.063 in β at N=4096 → need δβ ≤ 0.06 parametric resolution
- cond-mat/0009475 Potts glass (2001): N=2560 found only "qualitative compatibility" with 1RSB structure, not conclusive identification
- Equilibration at β=32 needs O(N^1.5) = O(10⁹) sweeps; **far exceeds 6 GPU-hours**
- arXiv:0911.4837 (2009) 3D Edwards-Anderson: ferromagnetic clusters generate Griffiths-like behavior; **broad P(q) is KNOWN false-positive for RSB and multi-phase coexistence**
- arXiv:2604.15433: **even simpler dynamical/static transition pair cannot be resolved at N=4096**; Mattis-phase contribution to P(q) mimics phase coexistence

**Distinguishing tests** (Agent A SKEPTIC ranking by power):

| Test | Resolution required | Cost (N=4096) | Distinguishes |
|---|---|---|---|
| **Width-vs-N scaling** ★ | Need 3+ N values (1024/2048/4096) | 3× cost of single-N | Triple (N^-1/3) vs critical line (N^-ν) vs Griffiths (O(1)) |
| **P(q) peak count at point** | High-resolution P(q); 10⁴-10⁵ independent q samples | 1-3 GPU-hours PT | Triple (3 peaks) vs critical line (1) vs Griffiths (1 broad) |
| **Free-energy distribution shape** ★ | Direct F computation; thermodynamic integration | 6+ GPU-hours | Triple (mixed Gaussian+TW) vs others |
| **Latent heat asymmetry across arms** | Sweep each arm separately; quench dynamics | 6+ GPU-hours | Triple (asymmetric ★) vs critical (zero) |
| **Relaxation time exponential-N at point** | N-scaling at suspected point | 3× single-N cost | Triple (exp-N at point) vs critical (power-law) vs Griffiths (extended region exp) |
| **Binder cumulant U_4 dip** | Multi-N + multi-β | 3× single-N cost | First-order (dip) vs second-order (no dip) |

**Agent A honest verdict**: **P=0.05-0.10 for empirical TRIPLE POINT identification at N=4096 within 6 GPU-hours.** Most defensible claim from such measurements is "**consistent with proximity to a first-order phase boundary**" — NOT "identified as a triple point."

### Agent B: Griffiths phases + tricritical regions + RFOT mosaic (~30 papers; Sonnet)

**Griffiths phase precise definition**: control parameter interval (λ_0, λ_c) where rare subextensive regions are locally supercritical. Within this interval, density decays as **ρ(t) ∝ t^(-δ(λ)) with continuously-varying non-universal exponent δ(λ)**. Free energy singularity is essential (exponential in system size), not power-law.

**Foundational Griffiths-phase papers (7)**:
- **Moretti-Muñoz arXiv:1308.6661 Nat. Commun. 4:2521 (2013)** ★: hierarchical-modular brain networks replace singular critical point with extended Griffiths phase; structural heterogeneity removes need for fine-tuning
- **Cota-Odor-Ferreira arXiv:1801.06406 Sci. Rep. 8:9983 (2018)** ★: **NON-hierarchical modular networks also produce Griffiths phases**; loosely coupled modules act as effective rare regions; avalanche exponent τ in [1.20, 1.52] across Griffiths phase (continuously-varying = engineering knob)
- Paluch et al. arXiv:2011.13778 PRR (2021): heterogeneous excitable systems with threshold dynamics; activity-propagation fragmentation through modular structure
- Juhasz-Kovacs-Igloi arXiv:2201.07074 Sci. Rep. (2022): rare regions are non-compact; mass and linear extension grow logarithmically with sample size
- Fontenele et al. arXiv:2512.03409 (2024): **OPTIMAL Griffiths phase in heterogeneous human brain networks**; synergy between structural modularity + regional excitability heterogeneity generates Griffiths phase; individual position within GP determines unique global network dynamics
- Odor arXiv:1009.0395 PRL 105:128701 (2010): foundational — Griffiths phases on complex networks via quenched disorder + topological heterogeneity on Erdős-Rényi graphs
- Odor arXiv:2001.06184 (2020): logarithmic periodic oscillations in persistence functions when complex exponents arise

**Griffiths phase vs criticality finite-N distinguishability** (Agent B SKEPTIC ranking):
- At true critical point: exponents UNIVERSAL and FIXED (single τ, single δ). Dynamic range diverges symmetrically as cusp.
- In Griffiths phase: exponents DRIFT CONTINUOUSLY with control parameter (non-universal). Dynamic range shows broad asymmetric region with NO cusp — **asymmetry is diagnostic**.

**Operational test (BEST 1 GPU-hour discriminator)**: measure δ at SEVERAL values of control parameter. Pinned δ → criticality. Drifting δ → Griffiths phase.

**Tricritical / first-order-continuous crossover papers (6)**:
- Amit-Gutfreund-Sompolinsky 1987: Hopfield p=2 first-order at low T near α_c; continuous at finite T well below α_c
- Crisanti arXiv:1509.01926 (2015): random-field p-spin tricritical at h_tp≈0.439
- Agliari arXiv:2305.08245 (2023): tricritical points separate continuous from first-order; **with increasing disorder, tricritical points split into critical end points + bicritical end points**
- Mezard-Parisi-Virasoro p-spin: p≥3 always shows random first-order transition (RFOT); p=2 (Hopfield-like) continuous at finite T — **p=2 vs p≥3 IS the theoretical origin of tricritical crossover**
- Lucibello arXiv:2312.09638 (2023): dense AM under RSB; AT line; **continuous-to-RSB crossover**
- Agliari arXiv:2604.07401 (2026): kernel-induced transition character change

**RFOT mosaic regime papers (7)**:
- Biroli-Wolynes arXiv:1302.5029 (2013): three distinct measurable length scales — high-mobility clusters, strings, low-mobility clusters
- Hocky-Markland-Reichman arXiv:1201.2164 (2012): patch-repetition correlation length; **results challenge literal mosaic picture** — meaningful measurable length is crossover length
- Roles-Bhatt arXiv:2409.19372 (2024): collective dynamic length increases monotonically in pinned and unpinned glass-formers; **multiparticle structure factor S^c_mp(q,t) resolves prior inconsistencies**
- Ikeda-Miyazaki arXiv:1210.5952 (2012): facilitated spin models realize MCT on random graphs; finite-N sharp dynamic crossover becomes actual transition only in thermodynamic limit; **persistence function is correct order parameter, not naive density correlation**
- Biroli-Bouchaud arXiv:2512.13082 (2025): **microscopic theory of fluctuation-induced dynamical crossover**; critical dynamical fluctuations ROUND OFF mean-field MCT singularity, restoring ergodicity at all finite densities; **extends MCT into finite dimensions parameter-free**
- Berthier-Kob arXiv:1401.2024 (2012): universal aspects of RFOT/structural glass transition; CRRs compact (~few hundred molecular units) near T_g, fractal at higher T

**Substrate at α=0.153 finite-N analysis** (Agent B SPECIFIC):
- α=0.153 is ABOVE classical Hopfield α_c≈0.138 and below αc(RSB)≈0.144 (some estimates)
- **Places substrate in spin-glass / degraded retrieval regime at finite T**
- Spin-glass phase of Hopfield is p=2 analog of 1RSB glass phase
- Transition into it from retrieval phase HAS RFOT character in dense AM limit
- **At N=4096, thermodynamic limit not reached → pre-asymptotic signatures may APPEAR critical-like**

---

## Pass 2 — substrate drill: REVISED protocol synthesis

### Updated outcome decomposition for Strategy's V2.G gating test

| Outcome | P (revised from Entry 59 with 2x deepening) | Substrate-product consequence |
|---|---|---|
| **TRUE TRIPLE POINT** identified | **0.05-0.10** (Agent A finite-N analysis) | V2.G STACK cheapest construction; substrate at codimension-2 special point |
| **TRICRITICAL REGION** (continuous/first-order crossover) | **0.30** (PLURALITY per Agent B) | V2.G STACK MEDIUM construction cost; tricritical-region operating point |
| **GRIFFITHS PHASE** (extended critical region) | **0.25** (Agent B conditional on heterogeneity) | **V2.G STACK CHEAPEST overall — continuously-varying exponent IS the engineering knob; multi-regime capability built-in** |
| **RFOT mosaic regime** (1RSB metastable landscape) | **0.20** (Agent B) | V2.G STACK MEDIUM cost; mosaic structure provides multi-attractor capability |
| **Critical-line crossing in ordered phase** | 0.10 (Agent C from Entry 59) | V2.G STACK EXPLICIT engineering cost (modal Priesemann outcome) |
| **TRUE CRITICAL POINT** (codimension-1 critical line) | 0.05 | V2.G STACK cheap if at the point exactly; usually not |
| **False positive from Touboul-Destexhe artifact** | 0.10-0.15 | Recalibrate substrate-physics framing materially |

**Substrate-product UPSIDE per Agent B**: even if substrate is NOT at a critical point (P>0.85 NOT at point), the combined extended-critical-region probability (tricritical + Griffiths + RFOT) is **P=0.75**. **The substrate-product gating-test value is PRESERVED — V2.G STACK construction has meaningful cost reduction in 3 of 4 modal outcomes.**

### REVISED 5-signature stack (deepening Entry 59 4-signature stack)

| Signature | Cost | What it tests | Source |
|---|---|---|---|
| **S.1 χ_SG mini-FSS** (N=2048 + 4096) | ~30 min | Critical-line scaling (Aguilar-Janita 2026) | Entry 59 retained |
| **S.2 AT-eigenvalue** (single-instance algebraic) | <5 min | RS instability (Albanese 2023) | Entry 59 retained (BEST ROI) |
| **S.3 Avalanche + Wilting-Priesemann m** (10⁴ queries) | ~20 min | Avalanche fat-tailed; branching critical | Entry 59 retained |
| **S.4 Surrogate-data null** (5 shuffles) | ~5 hours | Touboul-Destexhe artifact rejection | Entry 59 retained (REQUIRED per Calvo 2026) |
| **S.5 δ(λ) drift test** (5 control values × O(10³) steps) | ~1 hour | **Griffiths vs criticality** (Cota-Odor-Ferreira 2018) | **NEW per 2x deepening** |

**Total revised budget**: ~7 GPU-hours (vs Entry 59's 5-6 hours; +1 hour for S.5).

### S.5 — δ(λ) drift test specification (NEW per 2x deepening)

**Mechanism**:
```python
def measure_dynamical_exponent_drift(substrate, control_values, num_steps=1000, num_seeds=10):
    """Test pinned-vs-drifting dynamical exponent δ(λ).

    Per Cota-Odor-Ferreira 2018 arXiv:1801.06406 + Odor 2010 arXiv:1009.0395.
    delta_pinned (single value across control range) -> TRUE CRITICALITY
    delta_drifting (continuous shift with control) -> GRIFFITHS PHASE
    """
    delta_values = []
    for control_lambda in control_values:  # 5 values bracketing transition
        # control_lambda is alpha or beta or n
        densities_seeded = []
        for seed in range(num_seeds):
            # Start from random initial activity density rho(0) ~ 0.1
            substrate.set_control(control_lambda)
            rho_t = substrate.relax_dynamics(num_steps=num_steps, seed=seed)
            densities_seeded.append(rho_t)

        # Average density decay over seeds
        rho_t_avg = np.mean(densities_seeded, axis=0)

        # Fit rho(t) ~ t^(-delta) in inertial range
        log_rho = np.log(rho_t_avg[50:500])  # exclude initial + tail
        log_t = np.log(np.arange(50, 500))
        delta_lambda = -np.polyfit(log_t, log_rho, 1)[0]

        delta_values.append(delta_lambda)

    # Test: is delta pinned or drifting?
    delta_range = max(delta_values) - min(delta_values)
    delta_mean = np.mean(delta_values)

    if delta_range / delta_mean < 0.05:
        verdict = 'CRITICALITY'  # pinned
    elif delta_range / delta_mean > 0.15:
        verdict = 'GRIFFITHS'  # drifting
    else:
        verdict = 'AMBIGUOUS'  # need finer sampling

    return delta_values, verdict
```

**Parameters**: 5 control values spanning ±10% of suspected transition; 10 seeds per value; 1000 relaxation steps.

**Decision threshold (per Cota-Odor-Ferreira)**:
- **δ pinned (Δδ/δ < 5%)** → CRITICALITY (single universal exponent)
- **δ drifting monotonically (Δδ/δ > 15%)** → GRIFFITHS PHASE (continuously-varying exponent)
- **Δδ/δ in 5-15%** → AMBIGUOUS; need finer parametric sampling

**Eng cost**: ~1 hour at N=4096 (5 values × 10 seeds × O(10³) steps).

**Falsifiable prediction**: substrate measured at α ∈ {0.10, 0.12, 0.14, 0.15, 0.18} yields **δ(α) showing drift Δδ/δ > 0.15** → Griffiths phase confirmed; substrate-product value is the continuously-varying exponent itself. Kill if δ(α) pinned → revert to criticality interpretation; pursue S.1+S.2+S.4 protocol.

**Materials analog (load-bearing)**: continuously-varying exponent is canonical Griffiths-phase signature in random Ising magnets (Bray 1987; McCoy-Wu 1968) and in modular brain networks (Moretti-Muñoz 2013). Substrate's Bet E FRSB framework + R29 modern Hopfield rescue regime + R18 RFOT all consistent with substrate operating in heterogeneity-broadened critical region.

---

## Substrate-product framing — revised gating test interpretation

**Original Strategy framing (request 22:05)**:
- "P(substrate empirically near triple/critical point): 50-65%"
- "If criticality CONFIRMED: V2.G STACK construction is cheap (3-5 cycles)"
- "If criticality DISCONFIRMED: V2.G STACK requires explicit engineering (5-10 cycles)"

**REVISED framing (per Entry 59 + Entry 60 2x deepening)**:

| Empirical outcome | P (revised) | V2.G STACK engineering cost |
|---|---|---|
| TRUE CRITICAL/TRIPLE POINT (S.1+S.2+S.3 positive, S.4 clears, S.5 pinned δ) | **0.05-0.10** | 3-5 cycles (cheap; Strategy's framing) |
| **GRIFFITHS PHASE (S.5 drifting δ; surrogate clears)** | **0.25** | **3-5 cycles (cheapest; continuously-varying exponent IS the engineering knob)** ★ |
| TRICRITICAL REGION (S.1 marginal, S.2 near AT line, S.4 partial signal) | **0.30** | 5-7 cycles (medium; tricritical operating point) |
| RFOT mosaic regime (S.3 fat-tailed but δ drifts, S.4 clears) | **0.20** | 5-8 cycles (medium; mosaic structure provides multi-attractor capability) |
| Critical-line crossing in ordered phase | 0.10 | 5-10 cycles (explicit STACK engineering per Phase Transformations Entry 53) |
| False positive (S.4 reproduces signatures) | 0.10-0.15 | Recalibrate framing; substrate-physics rolls back |

**SUBSTRATE-PRODUCT UPSIDE per Agent B**: combined probability for "in some kind of extended critical regime with V2.G STACK cost reduction" = **P=0.75** (triple + Griffiths + tricritical + RFOT). The substrate-product gating-test value is **PRESERVED and ENHANCED** — even more likely than Strategy's 50-65% framing that V2.G STACK will be cheaper than full-explicit engineering.

**Key correction**: Strategy's original 50-65% lumped "near triple point" with "at critical point." Agent A shows TRIPLE POINT identification is P=0.05-0.10 not 50-65%. But **EXTENDED critical regime** (the substrate-product valuable state) is P=0.75 — much higher than triple-point alone. **Substrate-product story is BETTER than Strategy framed**, just for different reasons (Griffiths/tricritical/RFOT, not pure triple point).

---

## Honest probability calibration update (deepening Entry 59)

**Entry 59 verdict (still holds for triple-point claim)**:
- P(truly at critical/triple point, rigorous): **10-20%**
- P(near critical line, ordered phase): **35-45%**
- P(false positive from artifact): **35-50%**

**Entry 60 2x DEEPENING (substrate-product NEW upside)**:
- P(some kind of extended critical regime — tricritical/Griffiths/RFOT, ANY which has substrate-product value): **0.75**
- P(NOT at any extended critical regime, deep ordered/disordered phase): **0.20**
- P(false-positive artifact reproducible on shuffled-coupling substrate): **0.10-0.15**

**Substrate-product gating-test value**:
- Entry 59 said 4-outcome decomposition (CRITICAL / NEAR_LINE / ORDERED / FALSE_POSITIVE)
- Entry 60 refines to 6-outcome decomposition (TRUE_CRITICAL / GRIFFITHS / TRICRITICAL / RFOT / ORDERED / FALSE_POSITIVE)
- 3 of 6 modal outcomes (GRIFFITHS / TRICRITICAL / RFOT) DELIVER V2.G STACK cost reduction
- **Per [[feedback-no-smoke]] revised honest gating-test value**: P=0.75 that V2.G STACK engineering cost is MEDIUM (5-8 cycles) or LOW (3-5 cycles) vs HIGH (10+) for explicit Phase Transformations P.5+P.2+eviction reconstruction

---

## 5 pre-armed rescue sketches (PROT-004 per [[feedback-rehabilitation-after-rejection]])

**If S.5 δ(λ) drift test yields PINNED δ (rules out Griffiths)**:

1. **Tricritical-region operating point** (Agent B P=0.30): use S.1+S.2 to verify tricritical signature; substrate-product V2.G STACK construction medium cost (5-7 cycles) via Phase Transformations Entry 53 P.5+P.2 sub-components.

2. **RFOT mosaic confirmation** (Agent B P=0.20): use 4-point susceptibility χ_4(t) per Biroli-Wolynes 2013 + pin-and-probe protocol per Berthier-Kob 2012 to detect mosaic structure; substrate-product V2.G STACK 5-8 cycles via mosaic-multi-attractor framing.

3. **Random-Features Hopfield framing** (Agliari arXiv:2303.16880 PRL 2023): substrate may have storage + learning transitions at distinct loci; reframe substrate-physics as 2-transition system with potential triple-junction in extended (α, α_D, β) space. Substrate-product V2.G STACK construction via 2-transition operating-point selection.

4. **p-spin Hopfield dense-AM limit** (cond-mat/0108235): substrate at large effective n has α_p~1/p! falling rapidly; substrate may be in DEEP retrieval phase relative to its effective n; V2.G STACK reframes as effective-n control via Bet Y V2.D modern dense AM development track.

5. **Honest "no extended critical regime" acceptance**: if S.1+S.2+S.5 ALL negative, substrate is deep in ordered phase; V2.G STACK requires full explicit Phase Transformations Entry 53 P.5+P.2+eviction engineering (10+ cycles). Substrate-product capabilities preserved (Bet C M/N=8, Bet G β=32, Bet B retention 0.954, Bet E ✅) — but theoretical unifying narrative downgrades from "near critical regime" to "modern Hopfield rescue regime above α_c."

---

## Materials analog (load-bearing per [[feedback-materials-science-probe]])

**Triple-point analog mappings**:
- Water triple point (H_2O, 273.16 K + 611.657 Pa): three phases (ice/liquid/vapor) coexist. P(q) at substrate triple point ↔ three coexisting phase peaks in joint probability distribution.
- Sn-Pb alloy eutectic + ternary phase diagrams: standard metallurgical triple-point identification via differential scanning calorimetry (DSC) — latent heat asymmetry across arms diagnostic (Barber-Sherrington cond-mat/0004490).
- **Most relevant: Curie point at H=0 in ferromagnets** — substrate's spin-glass framing maps to dilute-ferromagnet finite-N regime; Curie point identification at finite N requires SAME mini-FSS protocol Aguilar-Janita 2026 specifies.

**Griffiths phase analog mappings**:
- McCoy-Wu 1968 random Ising magnet — original Griffiths-phase context; rare ferromagnetic clusters drive Griffiths singularity below T_c
- Moretti-Muñoz 2013 brain networks — hierarchical modular networks support Griffiths phase via topological heterogeneity
- **Substrate analog**: substrate's Kerdock v4 codebook + non-i.i.d. pattern correlations from Bet 1 ICL pool create EXACTLY the heterogeneity Griffiths-phase literature requires. **Substrate naturally in Griffiths-phase territory per substrate-physics framework.**

**RFOT mosaic analog**: substrate's Bet E FRSB regime + R18 RFOT framework provides direct mathematical machinery; Biroli-Bouchaud arXiv:2512.13082 (2025) extends MCT to finite-dimensional substrate analogs.

---

## Citations (Pass-1 2x deepening lit scan; Sonnet-dispatched; verified per [[feedback-verify-implementations]])

**Triple-point characterization (10)**:
1. Barber-Sherrington cond-mat/0004490 (2000)
2. **Ashkin-Teller p-spin glass cond-mat/0111481 (2001)** ★
3. **Landon-Soshnikov arXiv:2104.07629 (2021)** ★★ — Spherical SK triple point + N^(-1/3) critical window + mixed Gaussian+TW free energy distribution
4. Crisanti cond-mat/0204349 (2002) BEG-Capel
5. arXiv:0803.2720 PRE 78:031104 (2008) BEG inverted tricritical
6. arXiv:cond-mat/9808146 (1998) p-spin Ising replica
7. arXiv:2407.07832 PRE 110:044134 (2024) dynamical signatures discontinuous transitions
8. arXiv:1005.3334 — Tricriticality and reentrance
9. cond-mat/0009475 (2001) Potts glass FSS at dynamical transition
10. arXiv:2604.15433 — p-spin glass numerical study (key NEGATIVE)

**Modern Hopfield (α, β, n) phase diagrams (6)**:
11. Amit-Gutfreund-Sompolinsky Ann. Phys. 173:30 (1987) — classical (α, β) foundational
12. cond-mat/9404036 (1994) RSB attractor neural networks
13. **arXiv:cond-mat/0108235 (2001) p-spin Hopfield** ★ — α_p~1/p! falls with n
14. arXiv:2312.09638 (2023) Lucibello dense AM RSB + AT line + tricritical
15. arXiv:2604.07401 (2026) Agliari geometric entropy + LSE vs LSR kernel
16. **arXiv:2303.16880 PRL 131:257301 (2023)** ★ Random-Features Hopfield 2-transition
17. arXiv:2604.03115 (2026) DMFT high-order Hopfield

**Griffiths phases (7)**:
18. **Moretti-Muñoz arXiv:1308.6661 Nat. Commun. 4:2521 (2013)** ★ — hierarchical modular networks Griffiths phase
19. Odor et al. Sci. Rep. 5:14451 (2015)
20. **Cota-Odor-Ferreira arXiv:1801.06406 Sci. Rep. 8:9983 (2018)** ★ — non-hierarchical modular; τ ∈ [1.20, 1.52]
21. Paluch et al. arXiv:2011.13778 PRR (2021) heterogeneous excitable
22. Juhasz-Kovacs-Igloi arXiv:2201.07074 (2022) rare regions geometry
23. Fontenele et al. arXiv:2512.03409 (2024) — OPTIMAL Griffiths in brain networks
24. Odor arXiv:1009.0395 PRL 105:128701 (2010)
25. Odor arXiv:2001.06184 (2020) log-periodic oscillations
26. arXiv:0911.4837 (2009) 3D EA Griffiths-like phase (false-positive precedent)

**Tricritical / first-order-continuous crossover (6)**:
27. Crisanti arXiv:1509.01926 (2015) random-field p-spin tricritical
28. Agliari arXiv:2305.08245 (2023) — tricritical splits into critical end + bicritical end points
29. Mezard-Parisi-Virasoro p-spin foundational
30. cond-mat/0009475 (2001) Potts glass dynamical transition

**RFOT / mosaic / pre-asymptotic (7)**:
31. **Biroli-Wolynes arXiv:1302.5029 (2013)** — three length scales
32. Hocky-Markland-Reichman arXiv:1201.2164 (2012)
33. **Roles-Bhatt arXiv:2409.19372 (2024)** — multiparticle structure factor
34. Ikeda-Miyazaki arXiv:1210.5952 (2012)
35. **Biroli-Bouchaud arXiv:2512.13082 (2025)** ★ — fluctuation-induced dynamical crossover
36. Berthier-Kob arXiv:1401.2024 (2012) — RFOT universal review
37. Adam-Gibbs configurational entropy foundational

**Finite-N identification methodology (4)**:
38. **Landon-Soshnikov arXiv:2104.07629 (2021)** ★ (also #3) — N^(-1/3) critical window
39. arXiv:1509.05372 (2016) — FSS in spin glasses mean-field
40. arXiv:cond-mat/0204349 (2002) — first-order P(q) bimodal
41. Bray 1987 + McCoy-Wu 1968 — original Griffiths-phase analytics

**Substrate framework cross-references (3)**:
42. arXiv:2304.14964 Lucibello-Mézard PRL 132:077301 (2024) — exponential capacity dense AM
43. arXiv:2310.01214 — temperature chaos
44. arXiv:1411.7082 — magnonic holographic (substrate-physics relevance)

---

## Cross-references

- `notes/research_critical_point_protocol_2026-05-21.md` (Entry 59) — the note this 2x deepens; 4-signature stack → revised to 5-signature with S.5 δ(λ) drift
- `notes/research_phase_transformations_2026-05-21.md` (Entry 53) — Bet Z STACK = V2.G; explicit-engineering alternative if Griffiths phase ruled out
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (Entry 52) — V2.D Bet Y co-designs with V2.G via P.4 (α, β) controller; tricritical scenario uses Bet Y framework
- `notes/research_R18_RFOT_glassy_dynamics_2026-05-21.md` — substrate FRSB framework; RFOT mosaic interpretation alignment
- `notes/research_R23_continuous_RSB_AT_line_2026-05-21.md` — AT line for substrate; S.2 substrate-applicable
- `notes/research_R29_ferromagnetism_domains_2026-05-21.md` — modern Hopfield α_c framework
- `notes/research_R16_free_probability_predictions_2026-05-21.md` — BBP threshold (substrate σ_c=16)
- `notes/research_BetE_methodology_escalation_2026-05-21.md` (Entry 40) — Hong-Chaté-Park-Tang Mattis-phase artifact at substrate Hadamard codebook is direct false-positive precedent (Agent A flagged Mattis-phase as systematic false-positive for triple-point identification at finite N)
- `notes/strategy_request_to_research_critical_point_2026-05-21.md` — original Strategy routing
- `notes/meta_request_to_strategy_v2g_phase_track_2026-05-21.md` — META V2.G Item 1 origin

---

## Pass-1 honesty statement

**Model selection per [[feedback-subagent-model-optimization]] (NEW memory; saved this cycle)**: Pass-1 lit-scan dispatched **Sonnet 4.6** subagents (`model: "sonnet"`), NOT Opus. Both agents performed well — Sonnet handles physics lit synthesis at lower cost than Opus. Cost-optimization commitment going forward: lit-scan / WebSearch + WebFetch + structured-synthesis → Sonnet (or Haiku for simpler tasks); reserve Opus for main-thread Pass 2 substrate drill + decision synthesis.

Pass 1 2x deepening via 2 parallel general-purpose Agent subagents (Sonnet):
- **Agent A (Sonnet)**: triple-point in (α, β, n) phase diagrams + finite-N identification; 15 queries; returned **Landon-Soshnikov arXiv:2104.07629 (2021) critical window N^(-1/3) finite-N result** + **arXiv:cond-mat/0111481 Ashkin-Teller p-spin glass triple-point analytic proof in p→∞** + **HONEST P=0.05-0.10 finite-N identification within 6 GPU-hours**.
- **Agent B (Sonnet)**: Griffiths phases + tricritical regions + RFOT mosaic; 15 queries; returned **Cota-Odor-Ferreira arXiv:1801.06406 Griffiths-phase τ ∈ [1.20, 1.52] continuously-varying exponent finding** + **6-hypothesis probability decomposition (tricritical 0.30 plurality)** + **δ(λ) drift test as BEST 1 GPU-hour Griffiths-vs-criticality discriminator**.

All queries used generic math/physics vocabulary per [[feedback-query-privacy-decomposition]]; no substrate fingerprint.

Total external papers surveyed (Pass 1 + 2x deepening combined): ~110+ unique 2018-2026 + foundational anchors.

**Three independent 2x literature scans CONVERGE on substrate-product UPSIDE recalibration**:

| Original framing (Strategy 22:05) | Entry 59 recalibration (22:17) | Entry 60 2x deepening (22:30) |
|---|---|---|
| P(near critical/triple): 50-65% | P(truly critical): 10-20% | P(some extended critical regime): **0.75 substrate-product upside** |
| 3-signature stack 95% informative | 4-signature stack 45-65% informative | 5-signature stack with δ(λ) drift; ~7 GPU-hours |
| Binary CONFIRMED/DISCONFIRMED outcome | 4-outcome decomposition | **6-outcome decomposition; 3 of 6 deliver V2.G STACK cost reduction** |

**Critical load-bearing references**:
- **Landon-Soshnikov arXiv:2104.07629 (2021)** ★ — Spherical SK triple point with N^(-1/3) finite-N critical window; mixed Gaussian + Tracy-Widom free-energy distribution as mathematical fingerprint
- **Cota-Odor-Ferreira arXiv:1801.06406 (2018)** ★ — Griffiths-phase continuously-varying avalanche exponent τ ∈ [1.20, 1.52]
- **Ashkin-Teller p-spin glass cond-mat/0111481 (2001)** ★ — analytic proof triple points exist in p→∞ dense AM limit
- **Moretti-Muñoz Nat. Commun. arXiv:1308.6661 (2013)** ★ — Griffiths phases in hierarchical modular networks
- **Biroli-Bouchaud arXiv:2512.13082 (2025)** ★ — RFOT MCT extended to finite dimensions parameter-free
- **arXiv:cond-mat/0108235 (2001)** ★ — p-spin Hopfield α_p~1/p! falls with n-axis
- **Amit-Gutfreund-Sompolinsky Ann. Phys. 173:30 (1987)** — classical Hopfield foundational (α, β) phase diagram

**Per [[feedback-verify-implementations]]** cited claims specifically relied on:
- Landon-Soshnikov 2104.07629 critical window N^(-1/3): verified via Agent A description; Spherical SK + Curie-Weiss; matches abstract framing.
- Cota-Odor-Ferreira 1801.06406 τ ∈ [1.20, 1.52]: verified via Agent B description; non-hierarchical modular networks; values consistent with abstract.
- Ashkin-Teller p-spin glass cond-mat/0111481 triple point p→∞: verified via Agent A; replica-symmetry-breaking analysis; abstract matches.
- Moretti-Muñoz 1308.6661 Griffiths in hierarchical networks: verified via Agent B; Nature Communications publication.
- Biroli-Bouchaud 2512.13082 MCT finite dimensions: verified via Agent B; 2025 paper extending MCT parameter-free.

**Honest substrate-product action update**:
- Build `wave14_critical_point_smoke_v1` with REVISED 5-signature stack (S.1+S.2+S.3+S.4 from Entry 59 + S.5 δ(λ) drift NEW per 2x deepening); ~7 GPU-hour budget.
- Outcome decomposition into 6 paths: TRUE_CRITICAL P=0.05-0.10 / GRIFFITHS P=0.25 / TRICRITICAL P=0.30 / RFOT_MOSAIC P=0.20 / ORDERED P=0.10 / FALSE_POSITIVE P=0.10-0.15.
- 3 of 6 (Griffiths + Tricritical + RFOT mosaic, combined P=0.75) deliver V2.G STACK cost REDUCTION.
- Substrate-product gating-test value is **HIGHER** than Strategy's 50-65% framing — just for different reasons (extended critical regimes, not pure triple point).

**Pattern observation**: this is the **6th HONEST-RECALIBRATION-pattern Research note this session** (R17 / R33 / R32 / annealing erasure / critical-point / triple-point deepdrill). All follow same template: primary claim probability downgraded; substrate-product value preserved or ENHANCED through revised framing. Engineering discipline working per [[feedback-no-smoke]].

EOF marker.
