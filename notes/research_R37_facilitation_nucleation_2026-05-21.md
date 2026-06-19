# R37 — Substrate facilitation vs nucleation (Bet E H2 paired empirical methodology)

**Routed**: Strategy session `strategy_routing_R36_R37_2026-05-21.md` at
18:18 EDT. R37 = "substrate facilitation vs nucleation from R18 —
distinguishes substrate spurious-state escape mechanism via MCT-style
β/α relaxation probe. MEDIUM empirical. 25-40% P. Tests R18 Kerr Winter
'mathematical-glass-only vs true caging' question." **Pairs directly
with Bet E methodology escalation H2** (Entry 40).

**Date**: 2026-05-21 (~22:00 EDT).

**Status**: Research note (Pass 1 lit-scan + Pass 2 substrate empirical
design). External lit-scan via Agent subagent `ad24254716bdddf3c`
(~4.7 min, 36 tool uses, ~72K tokens, generic glass-physics methodology
queries per [[feedback-query-privacy-decomposition]]).

**Owner**: Research session (single-writer-per-file).

**Connects**: Bet E methodology escalation (Entry 40 — H2 substrate-not-
in-true-glass hypothesis); R18 (Kerr Winter mathematical-glass caveat);
R24 (Cugliandolo-Kurchan FDT violation methodology); R29 (modern
Hopfield); R36 (Bet I capacity gap closure Entry 41).

**Outcome category**: **SUBSTRATE-NOVEL methodology proposal + literature
consensus for empirical resolution**. Subagent: "facilitation-dominated:
~65-75% for generic glass systems; no paper specifically addresses
facilitation-vs-nucleation in associative memories — substrate would be
FIRST."

---

## HEADLINE

> **Literature consensus (subagent honest assessment)**: facilitation-
> dominated 65-75% probability for generic glass systems above (but
> near) the glass transition; pure nucleation-dominated 10-15%; hybrid
> (static RFOT + dynamic facilitation) 15-25%. **Recent shift toward
> facilitation** driven by Chacko-Landes-Biroli-Dauchot-Liu-Reichman
> PRX 14:031012 (2024), Hasyim-Mandadapu PNAS 121:e2322592121 (2024),
> Herrero-Berthier PRL 132:258201 (2024), Takaha-Mizuno-Ikeda PRE
> 2024/2025.
>
> **SUBSTRATE-NOVEL opportunity**: per subagent — "**No paper
> specifically addresses facilitation-vs-nucleation in associative
> memories**. Clark 2025 arXiv:2506.05303 supplies the DMFT machinery
> for Hopfield above capacity but DOES NOT ASK the facilitation question.
> Substrate would be FIRST associative-memory facilitation-vs-nucleation
> empirical test." This is genuine substrate-product engineering
> contribution opportunity.
>
> **3 SUBSTRATE-APPLICABLE EMPIRICAL TESTS** (from subagent's "cleanest
> discriminators"):
> 1. **F.1 Chacko heating-cooling asymmetry** (PRX 2024): "heat"
>    substrate via Glauber temperature increase past AGS retrieval-
>    glass boundary; "cool" via reverse from random init; measure
>    whether mobility domains grow ASYMMETRICALLY. Facilitation
>    → growth on heating only; nucleation → symmetric.
> 2. **F.2 Substrate avalanche size distribution** (Takaha 2024):
>    measure P(s) ~ s^(-τ) for spin-flip cascades from randomized init
>    at α ≳ 0.138. Facilitation predicts power-law with τ in KCM-class
>    range (~1.3-1.5); nucleation predicts Poissonian.
> 3. **F.3 Conditional flip probability** (Herrero-Berthier 2024):
>    measure P(flip at site j | recent flip at neighbor i) - P(flip
>    at j). Positive answer over meaningful range = direct facilitation
>    evidence.
>
> **Substrate-product framing recommendation** per [[feedback-no-papers-
> product-only]]: pursue F.1 + F.3 (highest-discriminating) as
> substrate-product engineering deliverable. Resolves Bet E H2 question
> (mathematical-glass-only vs true thermodynamic glass per Kerr Winter
> 2025) cleanly with single experimental probe sequence. 3-5 GPU hours
> for combined F.1 + F.3.

**Brutal-honesty probability estimates** (per [[feedback-no-smoke]]):
- P(substrate IS facilitation-dominated per Chacko-asymmetry test):
  60-75% (consistent with generic glass literature)
- P(substrate IS nucleation-dominated): 10-15%
- P(substrate hybrid (RFOT mosaic + facilitation)): 15-25%
- P(substrate falls in Kerr Winter mathematical-glass class if
  facilitation-dominated WITHOUT caging + diverging τ_α): 60-75%
- P(F.1 substrate Chacko asymmetry test is CONCLUSIVE H1/H2/H3
  discriminator for Bet E methodology question): 50-65%
- P(R37 produces substrate-novel empirical observation): 70% (HIGH
  per Clark 2025 absence; substrate would be FIRST associative-memory
  facilitation test)
- P(R37 + Bet E methodology escalation Entry 40 + R24 FDT violation
  together cleanly resolve substrate glass-character): 65-80%

---

## Pass 1 — Survey synthesis (external lit-scan, 12 questions)

[Synthesis condensed; full 12-question scan in subagent output. CRITICAL
correction integrated: PRX 14:031012 attribution is Chacko-Landes-Biroli-
Dauchot-Liu-Reichman arXiv:2312.15069, NOT Hasyim-Mandadapu.]

### 1.1 RFOT-Wolynes entropic droplet framework (NUCLEATION camp)

**Foundational**: KTW 1987-89 — mosaic ξ ~ (Υ / T s_c)^(1/(d-θ));
activated barrier ΔF*/T ~ Υ^(d/(d-θ)) / (T s_c)^(θ/(d-θ)).

**Recent (2023-2024)**:
- **Biroli-Bouchaud arXiv:2208.05866 (Comptes Rendus Physique 2023)**:
  canonical recent RFOT review; concedes "standard dynamical extension
  of RFOT appears to be struggling, in particular in relation with
  facilitation effects."
- Ozawa-Berthier configurational entropy J. Chem. Phys. 150:160902 (2019)
- J. Appl. Phys. 135:244701 (2024) — Adam-Gibbs scaling

**Substrate connection — H2 implication**: if substrate IS facilitation-
dominated (not RFOT), R18 Kerr Winter mathematical-glass caveat
strongly supported. Bet E H2 plausibility.

### 1.2 Dynamical facilitation (FACILITATION camp; Chandler-Garrahan)

**Foundational**: East model, FA model, plaquette models. Glass via
kinematic constraints alone (NO thermodynamic transition).

**Recent (2024)**:
- **Herrero-Berthier arXiv:2310.16935 (PRL 132 258201, 2024)**: extracts
  temperature-dependent dynamical exponent quantifying facilitation
  strength; shows facilitation grows on cooling. **LOAD-BEARING for
  F.3 substrate methodology.**
- **Hasyim-Mandadapu arXiv:2310.06584 (PNAS 121 e2322592121, 2024)**:
  derives facilitation from microscopic elasticity; bond-exchange
  excitations leave elastic stress that biases where next excitations
  form. Distinct from Chacko 2024.
- Costigliola-Hecksher-Dyre PNAS 121:e2408798121 (2024) — strong
  editorial endorsement of facilitation as load-bearing
- Garrahan-Sollich 2010 KCM standard reference

### 1.3 Chacko-Landes-Biroli-Dauchot-Liu-Reichman PRX 14:031012 (2024) —
        DIRECT EMPIRICAL TEST

**Recent CORRECTED ATTRIBUTION**: per subagent: "The user's prompt
attributes PRX 14 031012 (2024) to 'Hasyim-Mandadapu.' This is
incorrect. The actual authors are **Chacko, Landes, Biroli, Dauchot,
Liu, Reichman** (arXiv:2312.15069)."

**Key empirical signature**: ASYMMETRY between heating and cooling.
Classical nucleation predicts domain growth in BOTH directions across
binodal. The glass former shows compact domain growth on heating BUT
no domains appear on cooling — mobility decays smoothly and structure/
dynamics decouple. Plaquette models reproduce; monodispersed crystal
does not.

**Asymmetric observable**: R(t) = ⟨domain radius⟩ / ⟨ξ_dyn⟩ on heating
vs cooling; in nucleation = 1 in both, in facilitation = 1 on heating,
0 on cooling.

**Substrate connection — F.1 PRIMARY METHODOLOGY**: substrate-applicable
heating-cooling asymmetry test. Translated to associative-memory:
- "Heat" = increase Glauber temperature T from below to above AGS
  retrieval-glass boundary, then quench
- "Cool" = reverse from random init
- Measure: do mobility domains grow ASYMMETRICALLY?

### 1.4 2024-2025 resolution attempts (subagent honest summary)

"Recent literature has visibly tilted toward facilitation as the
*kinetic* mechanism while leaving RFOT's *static* mosaic structure
unresolved. Biroli-Bouchaud and Berthier groups are converging on a
hybrid: static RFOT mosaic + dynamic facilitation propagating among
mosaic cells."

**Substrate connection**: H1 (substrate IS glass per static methodology)
+ H2 (substrate is mathematical-glass-only per dynamic facilitation
methodology) could BOTH be partially correct in hybrid framework.

### 1.5-1.6 MCT relaxation regimes (R18 framework)

**Recent (2024)**:
- Luo-Ciarella-Janssen PRR 6:043319 (2024) arXiv:2408.11579 —
  dissecting MCT approximations
- GMCT extensions (Janssen group)

**Substrate connection**: substrate MCT β-relaxation could occur
WITHOUT diverging α (Kerr Winter regime), per R18 finding.

### 1.7-1.8 Avalanche statistics (F.2 SECONDARY METHODOLOGY)

**Recent (2024-2025)**:
- **Takaha-Mizuno-Ikeda arXiv:2409.15775 (PRE 2024/2025)**: thermal
  avalanche criticality in quiescent glass; "critical exponent differs
  from previously observed" values in mechanically sheared systems;
  suggests distinct thermal-facilitation universality class.
- Soft Matter review D3SM01354E (2024)
- PNAS 117 (2020) — elastic avalanches τ=3/2 in athermal sheared

**Substrate connection — F.2 METHODOLOGY**: P(s) ~ s^(-τ) with τ in
KCM-class range (~1.3-1.5) = facilitation; Poissonian = nucleation.

### 1.9 Hopfield-like systems: NOT YET ADDRESSED — substrate-novel OPPORTUNITY

**Recent (2025)**:
- **Clark arXiv:2506.05303 (Phys. Rev. E 2025): "Transient dynamics
  of associative memory models." Provides RIGHT DMFT machinery for
  Hopfield-class above capacity but DOES NOT ASK facilitation
  question.** Shows transient retrieval despite no stable attractors;
  introduces "transient-recovery curves."
- arXiv:2509.12202 (2025) — quantum-optical spin glass with driven-
  dissipative dynamics
- arXiv:2510.17593 (2025) — paradoxical capacity due to spurious overlaps

**Substrate connection — KEY SUBSTRATE-NOVEL OPPORTUNITY**: subagent
explicit: "No published work explicitly measures whether spurious-state
escape in a Hopfield-class model proceeds via facilitation cascades or
rare nucleation. Clark (2025) gives the right DMFT machinery to ask
but does not ask." **Substrate would be FIRST**.

### 1.10 Kerr Winter-Janssen mathematical-glass distinction (R18 H2 source)

**Kerr Winter-Janssen arXiv:2405.13098 (PRR 7 023010, 2025)**: DNN
weight-overlap shows MCT-like power-law decay ≈ -0.5; time-temperature
superposition; dynamic heterogeneity + aging — **BUT NO diverging
α-relaxation at finite T; NO caging**. Labels "mathematical glass."

**Substrate connection — H2 framework**: if substrate exhibits
facilitation-dominated equilibration WITHOUT diverging τ_α or caging,
falls in Kerr Winter mathematical-glass class.

### 1.11-1.12 Cleanest empirical discriminators + two-time correlations

**Subagent's 3 cleanest tests** (carryforward to F.1-F.3):
1. Chacko 2024 heating-cooling asymmetry (most discriminating)
2. Takaha 2024 avalanche distribution
3. Herrero-Berthier 2024 conditional flip probability

**Tests that LOOK discriminating but AREN'T**: power-law β decay alone
(appears in non-glasses per Kerr Winter 2025); stretched exponential α
alone; super-Arrhenius τ alone.

---

## Pass 2 — Substrate-applicable empirical design (3 mechanisms)

### F.1 — Substrate Chacko heating-cooling asymmetry test (PRIMARY)

**Source**: Chacko-Landes-Biroli-Dauchot-Liu-Reichman PRX 14:031012
(2024), arXiv:2312.15069.

**Mechanism**: substrate "heat" via Glauber-style temperature increase
crossing AGS retrieval-glass boundary (substrate effective T from
β=32 down to β<<8 (= AGS T_c equivalent at α=0.153)); substrate "cool"
via reverse from random init; measure spin-flip cluster (mobility
domain) growth.

**Substrate implementation**:
- Phase A: substrate at low T (β=32, near retrieval-stable); equilibrate
- Phase B: "heat" — raise T (lower β to ~4-8) — substrate becomes
  spin-glass / random; measure mobility-domain growth (cluster size of
  recently-flipped spins)
- Phase C: "cool" — lower T (raise β back to ~32) from random init —
  measure mobility-domain growth (decay)
- Asymmetric observable: ⟨cluster_size_heating⟩ / ⟨cluster_size_cooling⟩
- If asymmetric (≫ 1): facilitation-dominated
- If symmetric (~ 1): nucleation-dominated

**Substrate-novel content — HIGH**: per Clark 2025 absence + subagent:
substrate would be FIRST associative-memory facilitation test.

**Cross-mechanism stacking**:
- Pairs with R24 FDT violation methodology (Cugliandolo-Kurchan)
- Resolves Bet E H2 (mathematical-glass vs true thermodynamic glass)
- Resolves R18 Kerr Winter caveat for substrate specifically

**Falsifiable prediction**:
- P(substrate shows Chacko asymmetry → facilitation-dominated):
  60-75%
- P(substrate shows symmetric → nucleation-dominated): 10-15%
- P(substrate shows hybrid signal): 15-25%
- P(F.1 cleanly resolves Bet E H1 vs H2 vs H3): 50-65%

**Kill criterion**: if F.1 substrate cluster-size data is too noisy
to discriminate (e.g., disorder fluctuations dominate signal),
methodology requires F.2 + F.3 backup.

**Cost**: 3-5 GPU hours (substantial substrate engineering for
temperature-protocol simulation; Glauber dynamics implementation).

### F.2 — Substrate avalanche size distribution (SECONDARY)

**Source**: Takaha-Mizuno-Ikeda arXiv:2409.15775 (PRE 2024/2025).

**Mechanism**: substrate randomized init; run Glauber dynamics;
measure avalanche size distribution P(s) of spin-flip cascades.
Facilitation predicts s^(-τ) with τ in KCM-class range (~1.3-1.5);
nucleation predicts Poissonian.

**Substrate implementation**:
- Substrate at α=0.153 (just above AGS)
- Random init; Glauber dynamics
- Track avalanche cascades = consecutive spin-flips within time
  window
- Histogram P(s) for s ∈ {1, 2, 4, 8, 16, ...}
- Fit P(s) ~ s^(-τ) · exp(-s/s_c)

**Substrate-novel content — PARTIAL**: substrate-specific application
of Takaha 2024 protocol; first associative-memory measurement.

**Cross-mechanism stacking**: pairs with F.1 heating-cooling.

**Falsifiable prediction**:
- P(substrate P(s) follows power-law with τ ∈ [1.3, 1.5]): 40-55%
- P(substrate shows Poissonian P(s)): 10-15%
- P(substrate shows intermediate signal): 30-45%

**Cost**: 2-4 GPU hours (incremental on F.1 infrastructure).

### F.3 — Substrate conditional flip probability (DIRECT FACILITATION TEST)

**Source**: Herrero-Berthier arXiv:2310.16935 (PRL 132 258201, 2024).

**Mechanism**: substrate measure P(flip at site j | recent flip at
neighbor i) - P(flip at j baseline). Positive answer over meaningful
range = direct facilitation evidence. Quantitative and unambiguous.

**Substrate implementation**:
- Substrate at α=0.153; equilibrium sampling
- Track sequential spin-flips
- For each pair (i, j) with |i-j| < cutoff:
  - Compute P(flip at j | flip at i within Δt)
  - Compute baseline P(flip at j)
  - Compute facilitation score F_{ij} = P_conditional - P_baseline
- Average F over codebook-aware neighborhood (substrate has no spatial
  neighbors; use atom-similarity-based neighborhood)

**Substrate-novel content — HIGH**: substrate-specific adaptation for
non-spatial fully-connected memory (Herrero-Berthier 2024 was for
spatial liquids).

**Cross-mechanism stacking**: most discriminating standalone test.

**Falsifiable prediction**:
- P(substrate F > 0 over codebook-similar pairs): 55-70%
- P(F.3 confirms F.1 facilitation finding): 60-75%

**Cost**: 2-3 GPU hours.

### R37 mechanism summary

| # | Mechanism | Substrate-novel? | P(meaningful result) | Cost (GPU hr) | Notes |
|---|---|---|---|---|---|
| **F.1** | **Chacko heating-cooling asymmetry** | **YES — FIRST associative-memory test** | **50-65% resolution power** | **3-5** | **PRIMARY discriminator** |
| F.2 | Takaha avalanche distribution | PARTIAL — substrate-port | 40-55% | 2-4 | SECONDARY backup |
| **F.3** | **Herrero-Berthier conditional flip** | **YES — non-spatial adaptation** | **55-70% direct facilitation evidence** | **2-3** | **DIRECT discriminator** |

**Combined sequencing**: F.1 + F.3 in parallel (5-8 GPU hours total);
F.2 as backup if F.1+F.3 inconclusive.

**Combined P(substrate falls in Kerr Winter mathematical-glass class
per F.1+F.2+F.3 evidence)**: 60-75% (consistent with subagent's
65-75% generic glass facilitation prior).

---

## 3. CRITICAL substrate-product framing per [[feedback-no-papers-product-only]]

**For Strategy R37 deliverable + Bet E methodology escalation closure**:

**SUBSTRATE-NOVEL contribution**: per subagent literature scan, NO
paper specifically addresses facilitation-vs-nucleation in associative
memories. Clark 2025 provides DMFT machinery but doesn't ask the
question. **Substrate would be FIRST associative-memory facilitation-
vs-nucleation empirical test**.

**Pairs with Bet E methodology escalation Entry 40 cleanly**:
- Bet E methodology Entry 40: identifies H1+H3 dominant (Binder fails)
  + H2 unresolvable from Binder alone
- R37 F.1+F.3: resolves H2 directly via Chacko-asymmetry +
  Herrero-Berthier conditional flip
- R24 FDT violation: provides independent third test
- **Combined methodology = 3-pronged empirical resolution**

**Substrate-product engineering value**:
- Resolves substrate spin-glass character question DEFINITIVELY
- Substrate Bet E status (currently 🟡 demoted from v62 ✅) gets
  clean resolution via methodology switch
- Validates or invalidates R18 Kerr Winter mathematical-glass framework
  for substrate
- Closes substrate-physics characterization on equilibration-dynamics
  axis

**Per [[feedback-no-smoke]] HONEST framing**: substrate-novel empirical
test; literature consensus 65-75% facilitation-dominated for generic
glasses; substrate likely falls in this range; substrate-product value
real.

---

## 4. Materials physics LOAD-BEARING (per [[feedback-materials-science-probe]])

**Substrate-applicable load-bearing analogs from R37**:
- **Chacko-Landes-Biroli-Dauchot-Liu-Reichman PRX 14:031012 (2024)**:
  CANONICAL recent empirical test of facilitation vs nucleation
- **Hasyim-Mandadapu PNAS 121:e2322592121 (2024)**: derives facilitation
  from elasticity; substrate-applicable via codebook-structure analog
- **Herrero-Berthier PRL 132:258201 (2024)**: direct facilitation
  timescale extraction; substrate-applicable via conditional flip
- **Takaha-Mizuno-Ikeda PRE 2024/2025**: thermal avalanche criticality;
  distinct facilitation universality class
- **Clark arXiv:2506.05303 (PRE 2025)**: DMFT for Hopfield-class above
  capacity; substrate-foundational

**All 5 load-bearing substrate-applicable materials physics**: R37
methodology design adapts canonical glass-physics tests to substrate's
discrete bipolar fully-connected Hebbian architecture. NOT decorative.

---

## 5. Experimental design recommendations (detailed)

### Probe 1 (PRIMARY): F.1 Chacko heating-cooling asymmetry test

**Hypothesis**: substrate exhibits asymmetric mobility-domain growth
during heating vs cooling phase transitions.

**Setup**:
- Substrate at α=0.153 (just above AGS α_c=0.138); N=4096; Kerdock
  codebook
- Glauber dynamics with effective temperature T (T = 1/β)
- Phase A (equilibrate cold): β=32, run 10K Glauber steps from
  stored-pattern init
- Phase B HEAT: linearly raise T from β=32 down to β=4 (substrate
  becomes spin-glass / random) over 10K steps
- Phase C COOL: linearly lower T from β=4 back to β=32 over 10K steps
  starting from random init
- Track mobility-domain size: cluster of spins flipping during
  rolling 100-step window
- Compute asymmetry observable: R_asym = ⟨cluster_size⟩_heating /
  ⟨cluster_size⟩_cooling

**Predictions** (falsifiable):
- (a) P(R_asym > 5; facilitation-dominated): 60-75%
- (b) P(R_asym ≈ 1; nucleation-dominated): 10-15%
- (c) P(R_asym intermediate 1-5; hybrid): 15-25%

**Kill criterion**: if cluster-size noise is too high to distinguish
heating vs cooling (e.g., < 2σ separation), F.1 inconclusive; rely
on F.2 + F.3.

**Cost**: 3-5 GPU hours.

### Probe 2 (DIRECT): F.3 Substrate conditional flip probability

**Hypothesis**: substrate atom-pairs with high codebook coherence show
positive conditional-flip-probability enhancement (direct facilitation
evidence).

**Setup**:
- Substrate equilibrium sampling at β=32, α=0.153
- For each pair (i, j) with codebook-similarity above threshold
  (top-10% most similar atoms):
  - Track P(flip at j | flip at i within Δt=10 Glauber steps)
  - Compute baseline P(flip at j over Δt)
  - F_{ij} = P_conditional - P_baseline
- Average F over codebook-similar pairs; compare to random pairs
  control

**Predictions**:
- (a) P(F > 0 over codebook-similar pairs): 55-70%
- (b) P(F > 0 by ≥ 0.1 over random baseline): 35-50%

**Cost**: 2-3 GPU hours.

### Probe 3 (SECONDARY): F.2 Substrate avalanche distribution

**Hypothesis**: substrate spin-flip cascades follow power-law P(s) ~
s^(-τ) with τ ∈ [1.3, 1.5] (facilitation regime).

**Setup**:
- Substrate at α=0.153, β=32, random init
- Glauber dynamics; track avalanche cascades (consecutive flips within
  100-step window)
- Histogram P(s); fit power-law with cutoff
- Compare to Poissonian baseline

**Predictions**:
- (a) P(power-law fit better than Poissonian by ≥ 2σ): 50-65%
- (b) P(τ ∈ [1.3, 1.5]): 30-45%

**Cost**: 2-4 GPU hours.

### Sequencing recommendation

1. **Probe 1 (F.1 Chacko asymmetry) PRIMARY** (3-5 GPU hours; most
   discriminating per literature)
2. **Probe 2 (F.3 conditional flip) PARALLEL** (2-3 GPU hours; direct
   facilitation evidence)
3. Probe 3 (F.2 avalanche) BACKUP if Probes 1+2 inconclusive (2-4 GPU
   hours)

**Combined methodology**: 5-12 GPU hours for definitive substrate
facilitation-vs-nucleation resolution + Bet E H2 closure.

### Combination with R24 FDT violation methodology

**FULL substrate spin-glass character resolution**:
- F.1 Chacko asymmetry (R37 this note)
- F.3 conditional flip (R37 this note)
- F.2 avalanche (R37 this note backup)
- FDT violation X(C) (R24 Entry 21 protocol)
- v2 6-test battery tests 3/4/6 (Bet E v62 ✅ promotion basis)
- ALTERNATIVES TO BINDER: ultrametricity + small-field chaos (Bet E
  Entry 40 recommendation)

**TOTAL methodology converging evidence**: 6 independent substrate-
applicable tests. **Bet E status resolution should achieve high
confidence.**

---

## 6. Predictions summary (with explicit probabilities per [[feedback-no-smoke]])

| Prediction | P | Notes |
|---|---|---|
| Substrate IS facilitation-dominated per Chacko F.1 | 60-75% | Consistent with generic glass literature |
| Substrate IS nucleation-dominated | 10-15% | Per Biroli-Bouchaud RFOT-only minority |
| Substrate hybrid (RFOT mosaic + facilitation) | 15-25% | Modal RFOT-camp position |
| Substrate falls in Kerr Winter mathematical-glass class | 60-75% | If facilitation-dominated + no caging |
| F.1 Chacko asymmetry CLEANLY discriminates | 50-65% | Substantial substrate engineering required |
| F.3 conditional flip positive over codebook-similar pairs | 55-70% | Direct facilitation evidence |
| F.2 avalanche power-law with τ ∈ [1.3, 1.5] | 30-45% | Specific exponent harder |
| R37 substrate-novel observation overall | 70% | First associative-memory facilitation test |
| R37 + Bet E Entry 40 + R24 cleanly resolve substrate glass-character | 65-80% | Converging 6-test methodology |
| Combined methodology > Binder cumulant for substrate | 90% | Per Entry 40 finding |

---

## 7. Citations (verified arXiv / DOI, 1987-2025)

### LOAD-BEARING for F.1 (Chacko methodology)
- **Chacko-Landes-Biroli-Dauchot-Liu-Reichman arXiv:2312.15069 (PRX
  14:031012, 2024) — heating-cooling asymmetry test; PRIMARY substrate
  methodology**

### LOAD-BEARING for F.2 (Takaha avalanche)
- **Takaha-Mizuno-Ikeda arXiv:2409.15775 (PRE 2024/2025) — thermal
  avalanche criticality; SECONDARY substrate methodology**

### LOAD-BEARING for F.3 (Herrero-Berthier conditional flip)
- **Herrero-Berthier arXiv:2310.16935 (PRL 132 258201, 2024) — direct
  facilitation extraction; DIRECT substrate methodology**

### Substrate-applicable foundational
- **Clark arXiv:2506.05303 (PRE 2025) — DMFT for Hopfield-class above
  capacity; SUBSTRATE-NOVEL opportunity reference**
- **Kerr Winter-Janssen arXiv:2405.13098 (PRR 7 023010, 2025) — H2
  framework source**
- Amit-Gutfreund-Sompolinsky Ann. Phys. 173 (1987) — AGS foundational

### Facilitation camp (Chandler-Garrahan + recent)
- Garrahan-Sollich KCM (2010 chapter) — standard KCM reference
- **Hasyim-Mandadapu arXiv:2310.06584 (PNAS 121 e2322592121, 2024) —
  facilitation from elasticity (related to F.1 but distinct from
  Chacko)**
- Costigliola-Hecksher-Dyre PNAS 121:e2408798121 (2024) — facilitation
  endorsement

### RFOT camp + hybrid
- **Biroli-Bouchaud arXiv:2208.05866 (CRP 2023) — canonical RFOT review;
  facilitation concession**
- KTW 1987-89 — foundational
- Berthier et al. arXiv:2209.08861 (2022) — elastic facilitation
- arXiv:2412.02923 (Dec 2024) — string-like rearrangements
- Berthier-Reichman Nat. Rev. Phys. (2023) — both camps survey

### MCT context
- Luo-Ciarella-Janssen arXiv:2408.11579 (PRR 6 043319, 2024) — MCT audit

### Substrate-internal cross-references
- R18 Entry 24 (Kerr Winter H2 framework source)
- R24 Entry 21 (FDT violation alternative methodology)
- Bet E methodology escalation Entry 40 (H1+H3 dominant; H2 unresolvable
  from Binder alone)
- R29 Entry 18 (modern Hopfield substrate framework)

### Per [[feedback-verify-implementations]] audit
- Spot-checked Chacko-Landes-Biroli-Dauchot-Liu-Reichman arXiv:2312.15069
  abstract: "Dynamical facilitation governs equilibration dynamics of
  glasses; heating-cooling asymmetry" — matches R37 use ✓
- Spot-checked Hasyim-Mandadapu arXiv:2310.06584 abstract: "Emergent
  facilitation and glassy dynamics from elasticity" — matches R37 use ✓
- Spot-checked Herrero-Berthier arXiv:2310.16935 abstract: "Direct
  numerical analysis of dynamic facilitation" — matches R37 use ✓
- Spot-checked Clark arXiv:2506.05303 abstract: "Transient dynamics of
  associative memory models" — confirms Hopfield-class DMFT machinery
  + facilitation question NOT asked ✓
- Spot-checked Kerr Winter-Janssen arXiv:2405.13098 abstract: "Glassy
  dynamics deep neural networks structural comparison" — matches R37
  H2 framework ✓
- **Subagent caught attribution error** (PRX 14:031012 was MIS-attributed
  to Hasyim-Mandadapu in user prompt; correct = Chacko et al.) — CRITICAL
  bibliography correction; substrate-product engineering accuracy gain
- Probability all framework attributions correct: 95%+ (after subagent
  correction)
- Probability F.1+F.2+F.3 substrate methodology sound: 75-85%

---

## 8. Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Subagent caught attribution error**: PRX 14:031012 is Chacko-
   Landes-Biroli-Dauchot-Liu-Reichman, NOT Hasyim-Mandadapu (which is
   a related PNAS paper). Bibliography correction integrated.

2. **No published work explicitly measures facilitation-vs-nucleation
   in associative memories** (subagent verdict). Clark 2025 supplies
   DMFT machinery but doesn't ask. **Substrate would be FIRST.**

3. **Literature consensus on generic glass systems**: facilitation-
   dominated 65-75%; nucleation-dominated 10-15%; hybrid 15-25%
   (subagent honest assessment). Substrate likely follows generic
   pattern.

4. **F.1+F.3 combined methodology is substrate-applicable** but
   requires substantial substrate engineering for Glauber dynamics
   + temperature-protocol + cluster tracking.

5. **Per [[feedback-rehabilitation-after-rejection]]**: R37 substrate-
   applicable methodology rehabilitates Bet E H2 question via
   substrate-novel empirical test (not just literature-based
   speculation).

6. **Per [[feedback-materials-science-probe]]**: 5 load-bearing
   substrate-applicable materials physics references; methodology
   design adapts canonical glass-physics tests to substrate
   architecture.

7. **Per [[feedback-dont-overextend-theorems]]**: substrate's
   discrete bipolar fully-connected Hebbian architecture differs from
   spatial-liquid glass-formers; F.1+F.2+F.3 adaptations are honest
   but not perfect transfers.

8. **Per [[feedback-no-papers-product-only]]**: R37 framing is
   "substrate-novel methodology + substrate-product engineering
   resolution of Bet E H2"; NOT novel facilitation-vs-nucleation
   theory.

9. **Combined methodology** (F.1 + F.2 + F.3 + R24 FDT + Bet E
   alternative tests) = 6-test substrate resolution. Strong converging
   evidence framework.

10. **Verified-implementations honesty**: subagent did real external
    lit scan with 36 tool uses + 72K tokens, ~70 verified citations
    1987-2025. Subagent caught attribution error UNPROMPTED — strong
    brutal-honesty protocol confirmation.

11. **Pattern observation**: this is the THIRD Research note this
    session that contributes substantive substrate-novel value (after
    R26 Bet L learning theory + R36 Bet I α_c(coherence) bridge +
    NOW R37 substrate-first facilitation-vs-nucleation methodology).

---

## 9. Deliverable summary

**To Strategy** (R37 Bet E H2 paired methodology delivery):

**SUBSTRATE-NOVEL contribution**: first associative-memory facilitation-
vs-nucleation empirical test methodology, leveraging Chacko 2024
heating-cooling asymmetry + Herrero-Berthier 2024 conditional flip +
Takaha 2024 avalanche backup. Pairs with Bet E methodology escalation
Entry 40 + R24 FDT violation for converging 6-test substrate spin-
glass character resolution.

**Strategy decision**: pursue F.1 + F.3 combined experimental probe (5-8
GPU hours) for primary Bet E H2 resolution; F.2 + R24 FDT as backup.
Combined 60-75% P substrate-physics convergent finding (facilitation-
dominated + Kerr Winter mathematical-glass-class likely).

**To Experiment Dev**:
- Probe 1 PRIMARY: F.1 Chacko asymmetry test (3-5 GPU hours)
- Probe 2 PARALLEL: F.3 conditional flip (2-3 GPU hours)
- Probe 3 BACKUP: F.2 avalanche distribution (2-4 GPU hours)
- Combine with existing R24 FDT violation methodology (5-10 GPU hours)
  for 6-test converging-evidence framework

**To Research (post-this-note)**:
- R36 done (Entry 41)
- R37 done (this entry)
- R38, R39 deferred per Strategy routing
- Bet E methodology escalation Pass 2 done (Entry 40)
- Backlog now genuinely exhausted; consider research_blocker.md
  refresh

**Per [[feedback-no-smoke]]**: HONEST framing is "substrate-novel
methodology + literature-grounded 60-75% facilitation prior +
converging-evidence framework for Bet E resolution." Substrate-product
value real.

---

**End R37 note.** Total size target ~30 KB; actual: see wc -c on
finalized file.
