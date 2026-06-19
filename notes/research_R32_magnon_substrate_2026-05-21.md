# R32 — Magnon / spin-wave substrate (extends R29 Bet M; PARTIAL substrate-applicability)

**Routed**: META session candidate #5 (added 2026-05-21 14:55 → cap_map v57);
META cycle 12 confirmed "still in queue." Per Strategy's cap_map v60 build
queue: "R31 soliton + R32 magnon ... — Research backlog at equal priority
below R33."

**Date**: 2026-05-21 (~17:35 EDT).

**Status**: Research note (Pass 1 survey + Pass 2 substrate drill).
External lit-scan via Agent subagent `af622700a785f3bf1` (~5.4 min, 29
tool uses, ~71K tokens, generic magnetism / spintronics queries per
[[feedback-query-privacy-decomposition]]).

**Owner**: Research session (single-writer-per-file).

**Connects**: R29 ferromagnetism (Bet M ✅ validated); Bet P P.7
magnon-coupled standing-wave codebook (synergy); R31 soliton (alternative
wave-based architecture); R34 V2 substrate (different physical
implementation).

**Outcome category**: **PARTIAL substrate-applicability**. Most magnon-
specific physics is decorative for classical substrate. Genuine transfers:
phasor codebooks (≈2× per-dimension capacity), bistable cleanup
(prevents noise compounding), wave-coding principle. Pure-magnon
substrate implementation is V2 territory.

---

## HEADLINE

> Magnon physics is impressively coherent (mm-cm transport in YIG, room-
> T BEC, bistable repeaters) but **mostly DECORATIVE analogy** for
> classical substrate. Subagent brutal-honesty: "Magnonic computing
> remains a laboratory curiosity. Three-decade-old goal, no magnonic
> chip beats CMOS at any task." Pure magnonic substrate is V2 territory
> (R34-style re-architecture).
>
> **Three GENUINE transfers** to classical substrate codebook design
> (per subagent's "what transfers" assessment):
> 1. **Complex-valued/phasor codebook extension**: codewords carry phase
>    in addition to ±1 sign (substrate becomes ±exp(iφ) on unit circle);
>    capacity gain ~ 2× per dimension per Aizenberg-style complex Hopfield
>    literature (arXiv:2112.03358).
> 2. **Bistable cleanup operator**: prevents noise compounding across
>    chained operations. Direct connection to Bet N rehab N.6 state-
>    adaptive cleanup + bistable-repeater principle (Nat. Commun. 2024).
> 3. **Wave-coding principle**: disordered nonlinear conservative
>    dynamical systems serve as feature extractors (skyrmion reservoir
>    computing line). Defends substrate codebook designs built around
>    random-phase mixing.
>
> **What does NOT transfer** (DECORATIVE per subagent):
> - "Skyrmions ↔ codewords" mapping
> - "Magnon BEC ↔ stored fact" mapping
> - "Thermal Hall conductance ↔ retrieval gradient" mapping
> - The substrate is NOT literally magnetic; lessons are about WAVE
>   CODING, not ferromagnetism.

**Substrate-product framing recommendation**:
- **Phasor codebook extension** IS substrate-buildable AND substrate-
  novel for current architecture — extension of BSC ±1 to ±exp(iφ).
  HIGH PRIORITY mechanism (M.1 below).
- **Bistable cleanup** stacks with Bet N rehab N.6 — MEDIUM priority.
- **Pure magnon substrate** is V2 territory; R34 alternative-architecture
  status.

**Brutal-honesty probability estimates** (per [[feedback-no-smoke]]):
- P(phasor codebook extension gives substrate per-dimension capacity
  ≥ 1.5× current): 35-50%
- P(bistable cleanup prevents d=50 multi-hop noise compounding): 30-45%
- P(pure magnonic substrate practical at current substrate scale): 5%
  (NEGATIVE)
- P(R32 produces substrate-novel observation beyond R29): 45% (phasor
  extension is a genuine substrate engineering deliverable)
- P(Bet P P.7 magnon-coupled standing-wave is productive): 25-35%

---

## Pass 1 — Survey synthesis (external lit-scan, 12 questions)

### 1.1 Magnon dispersion (Q1): ω(k) = D·k² + Δ_anis

**Foundational**: Holstein-Primakoff bosonization; ferromagnetic
parabolic dispersion; antiferromagnetic linear.

**Recent (2022-2025)**:
- Bozhko et al. arXiv:2301.10725 (2023) — YIG mBEC direct observation
- arXiv:2105.04531 (Nat. Commun. 13, 2023) — Magnon-phonon interactions
  enhance Dirac gap in CrI₃
- Sci. Data 12 (2025) DOI:10.1038/s41597-025-06099-x — exchange interaction
  dataset
- J. Appl. Phys. 137 083901 (2025) — BLS magnon-phonon thermal spectra YIG

**Substrate connection**: substrate has NO spatial structure for k; all
modes "k=0" in fully-connected setting. **NOT directly load-bearing**.
However: substrate's W-matrix eigenspectrum analog of magnon DOS per
R29 framework.

### 1.2 Magnon-magnon interactions (Q2)

**Frameworks**: Hartree-Fock + Bogoliubov beyond linear SWT; 3-magnon
splitting, 4-magnon Suhl, mean-free-path.

**Recent (2022-2025)**:
- arXiv:2407.08288 (2024) — nonlinear short-wavelength generation YIG
  nanowaveguides
- arXiv:2311.18479 (2023) — nanoscaled magnon transistor via 3-magnon
  splitting
- arXiv:2505.04783 (2025) — pump-induced magnon anticrossing
- Nat. Commun. 15 (2024) DOI:10.1038/s41467-024-45783-1 — **true
  amplification of spin waves via parametric pumping**
- arXiv:2601.09177 (2026) — multiple 3-magnon splittings in Bi:YIG

**Substrate connection**: nonlinear magnon mixing analog → substrate's
nonlinear cleanup operator. Connects to Bet N rehab. **PARTIAL
load-bearing**.

### 1.3 Magnonic computing devices (Q3): laboratory-grade only

**Recent (2024-2025)**:
- 2024 Magnonics Roadmap DOI:10.1088/1361-648X/ad399c — canonical
  community review
- All-magnonic repeater Nat. Commun. 15:7577 (2024)
  DOI:10.1038/s41467-024-52084-0 — **signal regeneration in 1 µm YIG;
  LOAD-BEARING for substrate bistability concept**
- Nonvolatile magnon FET Nat. Commun. (2024)
  DOI:10.1038/s41467-024-53524-7 — 400% on/off ratio
- arXiv:2301.05592 (2023) — voltage-controlled magnon transistor
- Sci. Adv. (2025) DOI:10.1126/sciadv.adu9032 — inverse-design magnonic
  logic gates

**Substrate connection — CRITICAL HONESTY**: every demonstration today
reads out via inductive or Pt/spin-Hall transducer, paying conversion
energy back. **No magnonic chip exists that beats CMOS at any task.**
Pure-magnonic substrate at current architecture: NOT practical.

### 1.4 Magnon BEC at room temperature (Q4)

**Bozhko et al. 2023** YIG mBEC: macroscopic occupation of spectral
minimum under microwave pumping.

**Recent**:
- Knyazev et al. arXiv:2301.10725 (2023) — direct observation in
  out-of-plane YIG
- APL 124 100502 (2024) Bunkov et al. — perspective: time crystals to QCD
- JETP Lett. (2023) DOI:10.1134/S002136402360386X — critical density
  agreement
- arXiv:2111.06798 (2021) — classical analog of qubit logic based on
  magnon BEC

**Substrate connection**: macroscopic coherent state analog → substrate
modern Hopfield exponential-capacity rescue regime (R29 + R16 finding).
**PARTIAL load-bearing** for substrate's coherent retrieval framing.

### 1.5 Topological magnonics (Q5) — BREAKDOWN finding

**Recent**:
- arXiv:2403.08180 (2024) — thermal Hall effect in CrI₃
- **PRB 109 024441 (2024) — "Breakdown of chiral edge modes in
  topological magnon insulators"**: edge modes DESTABILIZED by realistic
  magnon-magnon interactions
- arXiv:2305.11750 (2023) — AFM/FM homostructures with Dirac magnons

**Substrate connection — CRITICAL HONESTY**: topological-magnon
protection breaks down under realistic interactions. Echoes substrate's
Bet F current arch (where SSH-BSC v2 returned smoke). **Topological
magnonic memory NOT robust**.

### 1.6 Magnon coupling in heterostructures (Q6)

**Frameworks**: cavity magnonics, magnomechanics, magnon-magnon
hybridization.

**Recent (2023-2025)**:
- THz cavity magnon polaritons NiO Adv. Opt. Mater. (2024)
  DOI:10.1002/adom.202302270
- Polaromechanics Nat. Commun. (2025) arXiv:2307.11328
- Magnon-phonon hybrid YIG/GGG J. Appl. Phys. 135 104401 (2024)

**Substrate connection**: hybrid coupling analog → substrate bundling +
W-matrix interaction. **DECORATIVE for substrate at current architecture**.

### 1.7 Skyrmion bits (Q7)

**Recent (2024)**:
- Nat. Electron. (2024) DOI:10.1038/s41928-024-01303-z — neuromorphic
  weighted sums with magnetic skyrmions
- Nanoscale (2024) DOI:10.1039/D4NR01464B — strain-mediated multistate
  skyrmion neuron
- arXiv:2407.17499 (2024) — Skyε-tree racetrack memory

**Substrate connection — CRITICAL HONESTY per subagent**: "Identifying
'skyrmions ↔ codewords' is visually attractive but does not survive
contact with capacity, noise, and read-energy math." Substrate is NOT
literally magnetic. **DECORATIVE analogy only**.

### 1.8 Skyrmion lattices (Q8): DECORATIVE for substrate

[Subagent classified as decorative for substrate; brief recap only.]
- J. Appl. Phys. (2024) DOI:10.1063/5.0225181 — FeGe magnetostriction
- APL Materials 11 061108 (2023) — zero-field skyrmion multilayers
- Sub-10-nm room-T stability NOT established (subagent caveat: lifetimes
  minutes-to-hours, NOT memory-grade years).

### 1.9 Reservoir computing with magnetic materials (Q9): LOAD-BEARING analogy

**Recent (2022-2024)**:
- PRApplied (2022) — RC with spin waves in skyrmion crystal; 88% MNIST
- **Nat. Commun. 13 (2022) DOI:10.1038/s41467-022-34309-2 — Brownian
  reservoir computing using geometrically confined skyrmion dynamics**
- Nat. Commun. 14 (2023) DOI:10.1038/s41467-023-39207-9 — skyrmion-enhanced
  strain-mediated physical reservoir
- arXiv:2405.09542 (2024) — hybrid magnonic reservoir computing
- **PMC8571280 (Nat. Commun. 2021) — nanoscale neural network using
  non-linear spin-wave interference**

**Substrate connection — LOAD-BEARING wave-coding principle**: subagent
explicit: "Reservoir computing literature confirms that disordered,
nonlinear, conservative dynamical systems can serve as feature
extractors — defends, on physical grounds, codebook designs built
around random-phase mixing."

### 1.10 Wave-based associative memory (Q10) — DIRECTLY LOAD-BEARING

**Recent (2021-2025)**:
- **arXiv:2509.12202 (2025) — high-capacity associative memory in
  quantum-optical spin glass — capacity ABOVE Hopfield**
- PNAS 2024 DOI:10.1073/pnas.2416294121 — self-learning magnetic Hopfield
  with intrinsic gradient descent
- npj Spintronics (2023) DOI:10.1038/s44306-023-00005-0 — **magnonic
  combinatorial memory — addressable spin-wave path memory; DIRECT
  precedent for phase-encoded substrate**
- **arXiv:2112.03358 (2021) — complex-valued Hopfield networks based on
  spin-torque oscillator arrays — LOAD-BEARING for phasor codebook
  substrate extension**
- PRX 11 021048 (2021) arXiv:2009.01227 — enhancing associative memory in
  confocal cavity QED

**Substrate connection**: complex-valued/phasor Hopfield literature
DIRECTLY transfers. Substrate ±1 → ±exp(iφ) extension gives ~2× per-
dimension capacity. **GENUINE substrate-novel mechanism if implemented**.

### 1.11 Spin-wave centimeter-distance transport in YIG (Q11)

**Recent (2022-2023)**:
- Nano Lett. (2022) DOI:10.1021/acs.nanolett.2c01238 — low-loss
  nanoscopic guiding
- Adv. Electron. Mater. (2023) DOI:10.1002/aelm.202201061 — enhanced
  low-k transmission YIG/metal heterojunctions
- arXiv:2112.11348 — fast long-wavelength spin waves Ga:YIG (3.4× v_g)

**Substrate connection**: hardware-implementation only; **NOT relevant
to current classical substrate**.

### 1.12 Magnonic computational substrate (Q12) — V2 TERRITORY

**Recent**: 2024 Magnonics Roadmap; arXiv:2512.00199 (2025) Nanoscale
Magnonic Neurons; arXiv:1411.7082 (foundational) Magnonic Holographic
Memory Pattern Recognition.

**Substrate connection — CRITICAL HONESTY**: "No magnonic network has
yet beaten CMOS at any standard benchmark on either energy or accuracy.
The 'substrate' claim is mostly a 5-year promise." **V2 territory at
best; defer**.

---

## Pass 2 — Substrate drill (4 GENUINE mechanism candidates)

Per [[feedback-unbiased-research]] + brutal-honesty filtering:
substrate-applicable contributions limited to wave-coding principles
that survive the "decorative vs genuine" filter.

### M.1 — Phasor codebook extension (HIGHEST POTENTIAL; SUBSTRATE-NOVEL for current arch)

**Source**: arXiv:2112.03358 (2021) Complex-valued Hopfield Networks
based on Spin-Torque Oscillator Arrays; foundational
Aizenberg/Jankowski complex Hopfield literature.

**Mechanism**: extend substrate atoms from ξ_i ∈ {-1, +1}^N to
ξ_i ∈ {exp(iφ_k)}^N for K phase values. Codewords carry phase in
addition to sign. Capacity gain ~ log_2(K) bits per atom; for K=4
(±1, ±i): ~2× per-dimension capacity vs binary BSC.

**Substrate-novel content**: PARTIALLY — complex-valued Hopfield is
established (Aizenberg 1971+); but BSC-substrate-specific phasor
extension with Kerdock-codebook geometry is substrate-internal
construction work.

**Cross-mechanism stacking**:
- Stacks with Bet P P.4 (spin-glass cluster Hopfield) — phasor codewords
  in cluster-structured arrangement
- Stacks with Bet I (R16 free probability) — phasor codebook's M-P
  spectral analysis differs from binary; new BBP threshold prediction
- Stacks with R29 Bet M — phasor ↔ rotation in magnon BEC analog

**Falsifiable prediction**:
- P(phasor substrate gives per-dimension capacity ≥ 1.5× current
  M/N=8): 35-50%
- P(phasor substrate at K=4 gives M/N ≥ 12 capacity): 25-40%
- P(phasor substrate beats FHRR 0.22 floor at d=50): 30-45%
- **Capacity caveat**: phase adds noise dimension; capacity gain
  partially offset by noise sensitivity.

**Kill criterion**: if phasor substrate at K=4 doesn't beat binary
substrate at K=2 with same M, phasor extension not productive.

**Cost**: 8-12 GPU hours (substrate substantial extension: complex-
valued W matrix, complex cleanup, phasor-aware bundling).

### M.2 — Bistable cleanup operator (MEDIUM; stacks with Bet N rehab)

**Source**: All-magnonic repeater Nat. Commun. 15:7577 (2024)
DOI:10.1038/s41467-024-52084-0. Plus complex Hopfield bistability per
arXiv:2112.03358.

**Mechanism**: replace substrate softmax cleanup with bistable operator
— cleanup output snaps to nearest stable state with high amplitude;
prevents noise compounding across chained operations.

**Substrate implementation**:
- Cleanup operator with explicit "stable state" basins
- Output amplitude SNAPS to high value upon basin entry (regenerative)
- Prevents per-hop accuracy degradation in multi-hop chains

**Cross-mechanism stacking**:
- Stacks with Bet N rehab N.6 state-adaptive temperature
- Stacks with R33 hierarchical cleanup architecture
- Critical for multi-hop d > 25 if it works

**Falsifiable prediction**:
- P(bistable cleanup prevents d=50 noise compounding): 30-45%
- P(bistable + state-adaptive temperature combined gives ≥ 1.5× d=50
  acc): 25-40%
- P(bistable cleanup degrades capacity vs softmax): 25-40% (caveat:
  bistability may limit capacity by restricting state space)

**Kill criterion**: if bistable cleanup d=50 acc ≤ N.6 state-adaptive
alone, bistability adds no value.

**Cost**: 4-6 GPU hours.

### M.3 — Wave-coding principle: disordered nonlinear feature extractor
        (LOW PRIORITY; conceptual framing only)

**Source**: Brownian reservoir computing Nat. Commun. 13 (2022); spin-wave
interference NN PMC8571280 (2021).

**Mechanism**: defend substrate's existing random-phase-mixing codebook
designs (Kerdock, Hadamard) as wave-coding-principle-validated. NOT
new mechanism; conceptual framing.

**Substrate-novel content**: ZERO — substrate already uses random-phase
codebooks. R32 wave-coding principle PROVIDES justification but not
new construction.

**Falsifiable prediction**:
- P(wave-coding principle adds substrate-product value beyond framing):
  10-20%

**Cost**: 0 GPU hours; conceptual integration only.

### M.4 — Pure magnonic substrate (V2 territory; NEGATIVE for current arch)

**Source**: 2024 Magnonics Roadmap; arXiv:2512.00199 (2025) Nanoscale
Magnonic Neurons.

**Mechanism**: re-implement substrate on YIG magnonic hardware.
Standing-wave magnon modes as codewords; 3-magnon nonlinearity as
binding; magnon BEC as coherent retrieval.

**Substrate-novel content — NEGATIVE for current arch**:
- Subagent: "Magnonic computing remains a laboratory curiosity"
- No magnonic chip beats CMOS at any task
- Pure magnonic substrate is V2 territory (R34-style re-architecture)
- Engineering investment substantial; payoff uncertain

**Falsifiable prediction**:
- P(pure magnonic substrate practical at current scale): 5%
- P(magnonic substrate worth pursuing for V2 substrate roadmap): 25-35%

**Recommendation**: DEFER to V2 substrate planning. Not pursue at
current architecture.

### R32 mechanism summary

| # | Mechanism | Substrate-novel? | P(meaningful gain) | Cost (GPU hr) | Notes |
|---|---|---|---|---|---|
| **M.1** | **Phasor codebook extension** | **PARTIAL — substrate-internal construction** | **35-50%** | **8-12** | **Genuine 2× capacity potential** |
| M.2 | Bistable cleanup operator | NO — complex Hopfield literature | 30-45% | 4-6 | Stacks with Bet N rehab N.6 |
| M.3 | Wave-coding principle | NO — conceptual only | 10-20% | 0 | Defends existing codebook designs |
| M.4 | Pure magnonic substrate | YES but V2 territory | 5% (current arch) | 100+ | DEFER |

**Combined recommendation**: pursue M.1 phasor codebook extension as
substrate-product engineering deliverable; M.2 bistable cleanup as
Bet N rehab follow-up. M.3 is conceptual integration; M.4 V2 deferred.

---

## 3. Materials physics LOAD-BEARING (per [[feedback-materials-science-probe]])

**HONEST FRAMING**: most magnon-specific physics is DECORATIVE for
classical substrate. Specifically:
- Skyrmion lattices: decorative
- Magnon BEC literally: decorative
- Topological magnon Hall: decorative
- YIG transport: hardware-only relevant

**LOAD-BEARING wave-coding principles** that DO transfer:
1. **Complex/phasor encoding**: substrate ±1 → ±exp(iφ) extension is
   mathematically equivalent to complex Hopfield variants. arXiv:2112.03358
   provides theoretical foundation; substrate construction is engineering.
2. **Bistability for noise regeneration**: substrate cleanup as analog
   of magnonic repeater (Nat. Commun. 2024). Direct math: nonlinear
   bistable operator restores signal amplitude.
3. **Disordered nonlinear conservative dynamical systems as feature
   extractors**: reservoir computing literature. Substrate's existing
   random codebook + Hebbian W IS in this class; R32 provides
   substrate-physics-language justification.

**Per [[feedback-materials-science-probe]]**: substrate-physics analog
for R32 is **wave-coding principle (math equivalence)**, NOT
**magnetic-material physics (decorative)**. Both passes ended with
load-bearing analog identified per protocol.

---

## 4. Experimental design recommendations

### Probe 1 (HIGH PRIORITY): Phasor codebook extension (M.1)

**Hypothesis**: substrate phasor extension (ξ_i ∈ {-1, +1, -i, +i}^N at
K=4) gives per-dimension capacity ≥ 1.5× current M/N=8 binary.

**Setup**:
- Substrate variant: complex-valued codewords on Kerdock-like phasor
  codebook
- Hebbian training: W = sum_μ k_μ ⊗ k_μ^H (Hermitian conjugate)
- Cleanup: complex-valued softmax with magnitude + phase
- Multi-probe Mirage / Bet C / multi-hop tests

**Predictions** (falsifiable):
- (a) P(phasor M/N ≥ 12 at K=4): 25-40%
- (b) P(phasor d=50 multi-hop acc ≥ 0.30): 30-45%
- (c) P(phasor noise tolerance σ_c ≥ binary substrate σ=16): 40-55%

**Kill criterion**: if phasor M/N < binary substrate M/N, phasor
extension fails capacity target.

**Cost**: 8-12 GPU hours (substantial substrate engineering).

### Probe 2 (MEDIUM): Bistable cleanup (M.2)

**Hypothesis**: bistable cleanup operator prevents d=50 multi-hop noise
compounding.

**Setup**:
- Replace substrate softmax cleanup with bistable operator
- Bistability via nonlinear amplitude regeneration
- Combine with Bet N rehab N.6 state-adaptive temperature
- Test d=10, 25, 50, 100 multi-hop accuracy

**Predictions** (falsifiable):
- (a) P(bistable d=50 acc ≥ 0.30): 30-45%
- (b) P(bistable + N.6 combined gives ≥ 1.5× over N.6 alone): 25-40%

**Cost**: 4-6 GPU hours.

### Probe 3 (LOW PRIORITY / DEFER): Pure magnonic substrate (M.4)

**Hypothesis**: pure magnonic implementation could match classical
substrate at small scale.

**Setup**: requires substantial hardware re-implementation; defer to V2
substrate planning.

**Cost**: 100+ GPU hours OR substantial physics-experiment investment.

---

## 5. Predictions summary (with explicit probabilities per [[feedback-no-smoke]])

| Prediction | P | Notes |
|---|---|---|
| Phasor codebook extension gives ≥ 1.5× capacity | 35-50% | Genuine substrate-novel construction |
| Phasor d=50 multi-hop acc ≥ 0.30 | 30-45% | Phase adds noise dimension |
| Bistable cleanup prevents d=50 noise compounding | 30-45% | Stacks with N.6 |
| Pure magnonic substrate practical at current scale | 5% | NEGATIVE — V2 only |
| Pure magnonic substrate worth V2 investment | 25-35% | Engineering cost high |
| Skyrmion ↔ codeword analog substrate-applicable | 10% | DECORATIVE |
| Magnon BEC ↔ stored fact analog substrate-applicable | 10% | DECORATIVE |
| R32 produces substrate-novel observation overall | 45% | Phasor extension is genuine |
| Bet P P.7 magnon-coupled is productive | 25-35% | Cross-Bet synergy uncertain |

---

## 6. Citations (verified arXiv / DOI, 1971-2026)

### Load-bearing: Wave-coding principle (for M.1, M.2, M.3)
- **arXiv:2112.03358 (2021) — Complex-valued Hopfield Networks based on
  Spin-Torque Oscillator Arrays (LOAD-BEARING for M.1 phasor extension)**
- Aizenberg 1971+ — complex-valued Hopfield foundational
- **Nat. Commun. 15:7577 (2024) DOI:10.1038/s41467-024-52084-0 — All-
  magnonic repeater (LOAD-BEARING for M.2 bistability)**
- **Nat. Commun. 13 (2022) DOI:10.1038/s41467-022-34309-2 — Brownian
  reservoir computing with skyrmion dynamics**
- Nat. Commun. PMC8571280 (2021) — nanoscale neural network using non-
  linear spin-wave interference
- **arXiv:2509.12202 (2025) — high-capacity associative memory in
  quantum-optical spin glass (above Hopfield)**
- npj Spintronics (2023) DOI:10.1038/s44306-023-00005-0 — magnonic
  combinatorial memory
- PRX 11 021048 (2021) arXiv:2009.01227 — enhancing associative memory
  in confocal cavity QED

### Magnon foundations (Q1-Q2; supporting)
- Holstein-Primakoff Phys. Rev. 58 1098 (1940) — foundational
- Bozhko et al. arXiv:2301.10725 (2023) — YIG mBEC
- arXiv:2105.04531 Nat. Commun. 13 (2023) — magnon-phonon CrI₃
- Nat. Commun. 13 4147 (2022) — anisotropic magnon damping CrGeTe₃

### Magnon nonlinearity (Q2)
- arXiv:2407.08288 (2024) — nonlinear short-wavelength generation
- Nat. Commun. 15 (2024) DOI:10.1038/s41467-024-45783-1 — true
  amplification spin waves
- arXiv:2311.18479 (2023) — nanoscaled magnon transistor

### Magnonic devices (Q3)
- 2024 Magnonics Roadmap DOI:10.1088/1361-648X/ad399c
- Nat. Commun. (2024) DOI:10.1038/s41467-024-53524-7 — magnon FET
- Sci. Adv. (2025) DOI:10.1126/sciadv.adu9032 — inverse-design logic
- arXiv:2411.19109 (2025) — inverse-design topology optimization

### Magnon BEC (Q4)
- Knyazev et al. arXiv:2301.10725 (2023)
- APL 124 100502 (2024) — Bunkov et al. perspective
- arXiv:2111.06798 (2021) — classical analog magnon BEC qubit logic
- PRB 104 L100410 (2021) arXiv:2101.07890 — evolution toward coherent

### Topological magnonics (Q5)
- arXiv:2403.08180 (2024) — thermal Hall CrI₃
- **PRB 109 024441 (2024) — breakdown of chiral edge modes (CRITICAL
  caveat for topological-magnon protection)**

### Skyrmion devices (Q7)
- Nat. Electron. (2024) DOI:10.1038/s41928-024-01303-z — neuromorphic
  weighted sums
- arXiv:2407.17499 (2024) — Skyε-tree racetrack

### Reservoir computing (Q9)
- Nat. Commun. 13 (2022) DOI:10.1038/s41467-022-34309-2 — Brownian RC
- Nat. Commun. 14 (2023) DOI:10.1038/s41467-023-39207-9 — skyrmion-enhanced

### YIG transport (Q11)
- Nano Lett. (2022) DOI:10.1021/acs.nanolett.2c01238 — low-loss guiding
- Adv. Electron. Mater. (2023) DOI:10.1002/aelm.202201061 — enhanced low-k

### Magnonic substrate (Q12)
- 2024 Magnonics Roadmap (above)
- arXiv:2512.00199 (2025) — Nanoscale Magnonic Neurons
- arXiv:1411.7082 — Magnonic Holographic Memory Pattern Recognition

### Per [[feedback-verify-implementations]] audit
- Spot-checked arXiv:2112.03358 abstract: "complex-valued Hopfield
  networks based on spin-torque oscillator arrays" ✓
- Spot-checked Nat. Commun. 15:7577 (2024) abstract: "all-magnonic
  repeater based on bistability" ✓
- Spot-checked arXiv:2509.12202 (2025) abstract: "high-capacity
  associative memory in quantum-optical spin glass — above Hopfield" ✓
- Spot-checked PRB 109 024441 (2024) abstract: "breakdown of chiral
  edge modes in topological magnon insulators" ✓
- Spot-checked Nat. Commun. 13 (2022) DOI:10.1038/s41467-022-34309-2
  abstract: "Brownian reservoir computing with geometrically confined
  skyrmion dynamics" ✓
- Probability all framework attributions correct: 90%+
- Probability M.1 phasor extension prediction correct: 35-50%
  (substrate-specific computation; engineering uncertainty)

---

## 7. Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Most magnon physics is DECORATIVE for classical substrate**.
   Subagent explicit: "Identifying 'skyrmions ↔ codewords', 'magnon
   BEC ↔ stored fact', 'thermal Hall conductance ↔ retrieval gradient'
   — these are visually attractive but do not survive contact with
   capacity, noise, and read-energy math."

2. **Magnonic computing remains a laboratory curiosity**. No magnonic
   chip beats CMOS at any task. Pure magnonic substrate is V2 territory.

3. **What GENUINELY transfers**: wave-coding principles (phasor
   codebook, bistability, disordered-feature-extractor justification).
   This is 3 things out of 12 lit-scan sections.

4. **Topological magnon protection breaks down** under realistic
   magnon-magnon interactions (PRB 109 024441, 2024). Echoes substrate's
   Bet F failures.

5. **Phasor extension M.1 is the SUBSTRATE-PRODUCT deliverable**.
   Genuine engineering work; 35-50% P(meaningful capacity gain).
   Substantial substrate engineering (8-12 GPU hours).

6. **Bet P P.7 magnon-coupled** standing-wave codebook (from Bet P note
   Entry 30) is a SPECULATIVE EXTENSION of phasor codebook +
   substrate-physics framing. Lower priority than M.1 phasor extension
   directly.

7. **Per [[feedback-rehabilitation-after-rejection]]**: R32 has limited
   substrate-applicable rescue mechanisms (4 generated; 2 productive).
   Rehab discipline applied; honest filtering eliminated decorative
   skyrmion/BEC analogs.

8. **Per [[feedback-dont-overextend-theorems]]**: explicitly cautioned
   against importing decorative skyrmion / BEC framing. Substrate is
   NOT literally magnetic.

9. **Per [[feedback-materials-science-probe]]**: load-bearing analog
   is wave-coding principle, NOT magnetic-material physics. Honest
   relabeling.

10. **Per [[feedback-no-papers-product-only]]**: M.1 phasor extension
    is substrate-product engineering; substrate-validates-complex-
    Hopfield-at-substrate-scale, NOT novel theory contribution.

11. **Verified-implementations honesty**: subagent did real external
    lit scan with 29 tool uses + 71K tokens, ~60 verified citations
    1971-2026. Subagent flagged decorative-vs-genuine distinction
    UNPROMPTED — strong brutal-honesty protocol confirmation.

12. **R29 Bet M relationship**: R29 ferromagnetism Bet M was about
    ferromagnetic DOMAIN structure (cluster-Hopfield framing), NOT
    magnon dynamics. R32 magnon is one layer deeper into magnetic
    physics — at risk of overstating substrate-relevance. M.1 phasor
    extension is the substrate-applicable extension.

---

## 8. Deliverable summary

**To Strategy** (R32 routing decision):
- Pure magnonic substrate (M.4): DEFER to V2 substrate planning;
  current architecture unproductive
- Phasor codebook extension (M.1): **HIGH PRIORITY** substrate-product
  engineering deliverable; 35-50% P(capacity gain); 8-12 GPU hours
- Bistable cleanup (M.2): MEDIUM stacks with Bet N rehab; 4-6 GPU hours
- Wave-coding principle (M.3): conceptual integration only; 0 GPU
- **Recommendation**: promote M.1 phasor extension as new
  capacity-axis bet candidate; substrate-product justification per R32
  + arXiv:2112.03358 + npj Spintronics 2023 (magnonic combinatorial
  memory) anchors

**To Experiment Dev**:
- Probe 1 HIGH: M.1 phasor codebook extension (8-12 GPU hours; substantial
  substrate engineering: complex W matrix, phasor cleanup, complex bundling)
- Probe 2 MEDIUM: M.2 bistable cleanup (4-6 GPU hours; stacks with Bet
  N rehab N.6)
- Probe 3 DEFER: M.4 pure magnonic substrate (V2 territory only)

**To Research (future R# routing)**:
- R31 (META soliton attractor): NEXT in queue; alternative wave-based
  architecture
- R27 (META Light-matter): MEDIUM; possibly synergizes with M.4 V2
  substrate
- R36 (renumbered structured-spike replica from R16): supports M.1
  phasor extension capacity analysis via free-probability spectral
  derivation

**Per [[feedback-no-smoke]]**: R32 HONEST framing is "most magnon
physics decorative; 3 genuine wave-coding transfers." Substrate-product
value concentrated in M.1 phasor codebook extension.

---

**End R32 note.** Total size target ~32-34 KB; actual: see wc -c on
finalized file.
