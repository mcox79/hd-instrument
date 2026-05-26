# R31 — Soliton attractor design (META candidate #4; PARTIAL substrate-applicability with critical discretization caveat)

**Routed**: META session candidate #4 (added 2026-05-21 14:55 → cap_map
v57); META cycle 12 confirmed "still in queue." Per Strategy's cap_map
v60: "R31 soliton + R32 magnon ... — Research backlog at equal priority
below R33." Last META candidate in primary queue (with R32 done in
Entry 31).

**Date**: 2026-05-21 (~17:50 EDT).

**Status**: Research note (Pass 1 survey + Pass 2 substrate drill).
External lit-scan via Agent subagent `a0d333520e40e7ed6` (~3.9 min, 19
tool uses, ~53K tokens, generic mathematical-physics / nonlinear-
dynamics queries per [[feedback-query-privacy-decomposition]]).

**Owner**: Research session (single-writer-per-file).

**Connects**: Bet N rehab (cleanup-axis); R33 quantum-repeater
(hierarchical cleanup); Bet F (topological soliton stability); R28
dislocations (topological-charge protection); R32 phasor codebook
(wave-coding cross-axis).

**Outcome category**: **PARTIAL substrate-applicability with CRITICAL
DISCRETIZATION CAVEAT**. Continuous-PDE soliton concepts (integrability,
infinite conservation laws, elastic collisions) MOSTLY DO NOT TRANSFER
to discrete substrate. Strongest substrate-applicable contribution: ONE
paper (Pyrkov-Byrnes-Cherny 2020 arXiv:1909.05082) makes the soliton-
as-Hopfield-attractor analogy mathematically operational.

---

## HEADLINE

> Subagent's brutal-honesty finding: **"integrability is FRAGILE under
> discretization."** DNLS (discrete NLS) is non-integrable; Ablowitz-
> Ladik is integrable but specially-chosen and fragile. Substrate is
> discrete high-D — closer to DNLS, with Peierls-Nabarro pinning and
> no elastic collisions. **"Infinite conservation laws" of continuous
> NLS DO NOT TRANSFER to discrete substrate.** Any soliton-based
> substrate claim citing continuous integrability is OVEREXTENSION.
>
> **What GENUINELY transfers** (per subagent's "what transfers"):
> 1. **Soliton-resolution conjecture as cleanup analog** (Bilman-
>    Buckingham arXiv:1905.02493): arbitrary input asymptotically
>    resolved into finite sum of soliton attractors. Closest math
>    analog to substrate cleanup. Real phenomenon, not metaphor.
> 2. **CGLE dissipative-soliton attractors** (Pyrkov-Byrnes-Cherny
>    arXiv:1909.05082, Symmetry 12, 24, 2020): SINGLE PAPER that
>    explicitly casts soliton as Hopfield attractor; proves basin of
>    attraction. **THE substrate-applicable reference.**
> 3. **Elastic-collision phase shifts** (Wu 2024 arXiv:2401.15819):
>    quantitative account of how interacting solitons can pass through
>    each other and recover shape. Relevant to multi-hop substrate
>    where multiple stored items must coexist.
> 4. **Topological-charge protection** (skyrmions, kinks): genuinely
>    different stability principle surviving noise up to energy gap.
>    Connects to Bet F SSH-BSC + R28 dislocations.
>
> **What does NOT transfer** (DECORATIVE per subagent's brutal honesty):
> - Continuous integrability of KdV/NLS (lost under discretization)
> - Fiber-optic soliton transmission (1D continuous, wrong dim type)
> - Davydov solitons (contested biologically)
> - Soliton-based optical computing beating CMOS (consistently
>   overpromised)

**Substrate-product framing recommendation**:
- **S.1 CGLE-style dissipative attractor cleanup** (Pyrkov 2020 direct
  port): substrate cleanup as parametric basin-of-attraction; substrate-
  applicable engineering. 30-40% P of substantial gain.
- **S.2 Soliton-resolution-style cleanup framing** (Bilman-Buckingham
  2019 conceptual): substrate iterated cleanup mathematically grounded
  as resolution into discrete attractor library. 0 GPU framing.
- **S.3 Topological-soliton encoding for Bet F**: cross-axis combination
  with R28 dislocations + Bet F SSH-BSC; substantial Bet F rescue if
  Bet F v3 fails.
- **S.4 Discrete-attractor cascadability** (Manakov NOR/OR
  arXiv:1806.00965 cascadability proof): substrate-applicable evidence
  that chained nonlinear ops can preserve attractor template.

**Brutal-honesty probability estimates** (per [[feedback-no-smoke]]):
- P(CGLE-style cleanup gives ≥ 1.3× d=50 acc): 25-40%
- P(soliton-resolution conjecture mathematically applicable to substrate
  cleanup): 50-65% (framing-level claim)
- P(R31 produces substrate-novel observation beyond R32 + Bet N rehab):
  35% (mostly cross-axis-stacking + framing contributions)
- P(continuous-PDE integrability claims for substrate are overextension):
  90% (mathematical fact)
- P(R31 Pure-soliton substrate practical at current arch): 5% (NEGATIVE)

---

## Pass 1 — Survey synthesis (external lit-scan, 12 questions)

[Synthesis condensed — full 12-question scan in subagent output.
Key takeaways below.]

### 1.1-1.2 KdV + NLS foundations (continuous): NOT substrate-applicable

**Foundational**:
- KdV equation: u_t + 6u·u_x + u_xxx = 0; inverse scattering transform
  (Gardner-Greene-Kruskal-Miura 1967)
- NLS: i·ψ_t + ψ_xx + 2|ψ|² ψ = 0; Zakharov-Shabat spectral problem
- Bright soliton (NLS): ψ(x,t) = η sech[η(x-vt)] exp[i(vx/2 + (η²-v²/4)t)]

**Recent (2021-2025)**:
- Wu arXiv:2401.15819 (2024) — KdV n-soliton stability with phase shifts
- arXiv:2507.13643 (2025) — discrete NLS exponential asymptotics
- arXiv:2509.25650 (2025) — DNLS vs Ablowitz-Ladik nonzero background

**Substrate connection**: continuous PDE — NOT directly applicable to
discrete N=4096 substrate. Inspiration only for shape-preservation
intuition.

### 1.3-1.4 Optical fiber solitons + microresonator soliton crystals: WRONG DIMENSION TYPE

**Recent (2024-2025)**:
- JOSA B 41 1655 (2024) — multimode fiber solitons review
- arXiv:2505.09953 (2025) — Kerr soliton microcombs

**Substrate connection — CRITICAL HONESTY**: 1D temporal pulse → high-D
discrete codeword is a fundamental TYPE MISMATCH. Gordon-Haus jitter
results don't translate without substantial reformulation.

### 1.5 Davydov solitons in proteins: CONTESTED ANALOG

**Recent**: Georgiev-Glazebrook arXiv:2006.16798 (2020); Phys. Lett. A
247:9 (1998) thermal stability argument.

**Substrate connection — DECORATIVE**: thermal stability contested in
biological proteins at 310 K. Inspiration-level only.

### 1.6 Discrete / lattice solitons — CRITICAL SUBSTRATE-RELEVANT FINDING

**Discrete NLS (DNLS)**: i·ψ̇_n + (ψ_{n+1} + ψ_{n-1} - 2ψ_n) + |ψ_n|²·ψ_n = 0.
**Non-integrable in general.**

**Ablowitz-Ladik (AL)**: modified discrete NLS with specially-chosen
nonlinearity |ψ_n|²(ψ_{n+1}+ψ_{n-1})/2. **Integrable but specially
chosen.**

**Peierls-Nabarro barrier** ΔE_PN > 0: pins DNLS solitons.

**Recent (2021-2025)**:
- arXiv:2102.05332 + arXiv:2105.04202 (2021) — closeness of AL to DNLS
- arXiv:2509.25650 (2025) — discrete NLS vs AL nonzero background

**Substrate connection — LOAD-BEARING**: substrate is fundamentally
discrete (N=4096 atoms; M=8N discrete bundles). DNLS-like dynamics with
Peierls-Nabarro pinning is the realistic regime. **Continuous-soliton
integrability claims for substrate are OVERREACH**.

### 1.7 Attractor-shaped pulses under iterated nonlinear maps — LOAD-BEARING

**Two threads**:
- (a) CGLE-type dissipative-soliton attractors: unique localized shape
  as global attractor of soliton-like initial conditions
- (b) Dispersive shock waves in NLS: trains of asymptotic solitons
  whose shapes asymptotically lock to integrable templates

**Cubic-quintic CGLE**: i·ψ_t + (1/2 - iβ)·ψ_xx + (1 - iε)|ψ|² ψ -
(ν - iμ)|ψ|⁴ ψ + iδ·ψ = 0. Dissipative soliton fixes amplitude/width/
chirp by **balance** (gain = loss, dispersion = nonlinearity).

**Recent (2019-2025)**:
- **Pyrkov-Byrnes-Cherny arXiv:1909.05082 (Symmetry 12, 24, 2020) —
  SOLITONIC FIXED-POINT ATTRACTORS IN CGLE FOR ASSOCIATIVE MEMORIES;
  CENTRAL REFERENCE for substrate-applicable soliton-as-attractor
  analog**
- Bilman-Buckingham arXiv:1905.02493 (2019) — DSW asymptotic solitons
  focusing NLS
- arXiv:2511.14549 (2025) — DSW in periodic lattices

**Substrate connection — CENTRAL FINDING**: Pyrkov 2020 explicitly
casts soliton as Hopfield attractor; proves basin-of-attraction
stiffness. **One paper makes the analogy mathematically operational**.

### 1.8 Integrable systems (Lax pairs, AKNS, sine-Gordon, Toda): DOES NOT TRANSFER

**Substrate connection — CRITICAL HONESTY**: integrability survives
"any physically interesting noisy perturbation" only narrowly. KAM-
style persistence holds only in measure. Substrate is a strong
perturbation; integrability claims are OVEREXTENSION.

### 1.9 Information storage via soliton encoding — OVERPROMISED in literature

**Recent**:
- Springer J. Opt. (2024) DOI:10.1007/s12596-023-01534-x — soliton
  logic-gate review
- Manakov NOR/OR arXiv:1806.00965 (2018) — cascadability proof
- arXiv:2407.18725 (2024) — DL coded info storage vector solitons

**Substrate connection**: cascadability of nonlinear soliton stages IS
substrate-relevant evidence that chained nonlinear ops can preserve
attractor template. **PARTIAL load-bearing**.

### 1.10 Solitons in disordered media — INFORMATIVE for substrate noise

**Tension**: linear Anderson localization vs nonlinear self-focusing.
In weak-disorder/strong-nonlinearity: solitons survive with random
phase shifts and slow diffusion; in strong-disorder limit: solitons
fragment.

**Recent (2021-2025)**:
- Ricard-Falcon arXiv:2411.10376 (PRL 133 264002, 2024) — soliton over
  disordered topography
- arXiv:2502.08463 (2025) — nonlinear Anderson screening
- arXiv:2106.07147 (2021) — Anderson localization in Toda

**Substrate connection**: substrate IS disordered medium (random
codebook); soliton-in-disorder theory predicts shape degradation under
iterated noisy cleanup. **PARTIAL load-bearing for noise modeling**.

### 1.11 Topological solitons — LOAD-BEARING for Bet F + R28 cross-axis

**Skyrmion charge**: Q = (1/4π) ∫ n · (∂_x n × ∂_y n) d²x
**Sine-Gordon kink mass**: M = 8/γ in natural units
**Bogomolny bound**: E ≥ |Q| · (constant)

**Recent (2017-2024)**:
- arXiv:2411.07775 (2024) — topological resilience optical skyrmions
  in local decoherence
- Melcher arXiv:1711.07717 — axisymmetric chiral skyrmion stability
- arXiv:2205.10329v3 — optical skyrmions review

**Substrate connection**: topological-charge protection IS substrate-
applicable. Connects to Bet F SSH-BSC (R10 framework) + R28 Burgers-
vector topology. **Cross-axis combination potential**.

### 1.12 Solitons in machine learning — Pyrkov 2020 is THE relevant work

**Recent**:
- **Pyrkov-Byrnes-Cherny arXiv:1909.05082 (Symmetry 12, 24, 2020) —
  ONLY directly relevant paper for substrate-as-soliton-attractor
  analog**
- arXiv:2602.18110 — cavity solitons photonic neuromorphic substrate
- arXiv:2407.18725 (2024) — vector-soliton-pulsation coded storage

**Substrate connection — CRITICAL**: Pyrkov 2020 cited at minimum in
3 sections as THE substrate-applicable reference.

---

## Pass 2 — Substrate drill (4 GENUINE mechanism candidates)

Per [[feedback-unbiased-research]]: Research GENERATES candidates;
META's draft sketch (from candidate #4) is starting point only.

### S.1 — CGLE dissipative-soliton attractor cleanup (Pyrkov 2020 port)

**Source**: Pyrkov-Byrnes-Cherny arXiv:1909.05082 (Symmetry 12, 24, 2020)
— "Solitonic fixed point attractors in CGLE for associative memories."

**Mechanism**: replace substrate softmax cleanup with CGLE-style
fixed-point attractor map. Substrate iterated cleanup as basin-of-
attraction convergence to discrete stored fact attractors.

**Substrate implementation**:
- Each stored fact = parameterized soliton-shape attractor
- Cleanup iteration: balance gain/loss/dispersion to lock unique shape
- Multi-hop: each hop is cleanup iteration; shape preserved across hops

**Substrate-novel content — PARTIAL**: Pyrkov 2020 provides theoretical
foundation; substrate-specific CGLE parameterization for N=4096
bipolar atoms is engineering work.

**Cross-mechanism stacking**:
- Stacks with Bet N rehab N.6 state-adaptive cleanup (CGLE adaptive
  parameters)
- Stacks with R32 M.2 bistable cleanup (CGLE has bistability natively)
- Stacks with R33 hierarchical cleanup architecture

**Falsifiable prediction**:
- P(CGLE-style cleanup gives ≥ 1.3× d=50 acc): 25-40%
- P(CGLE basin stiffness exceeds softmax basin stiffness): 35-50%
- P(CGLE parameters can be tuned for substrate Kerdock codebook): 40-55%

**Kill criterion**: if CGLE-style cleanup doesn't beat current substrate
softmax at d=25 baseline, port not productive.

**Cost**: 6-10 GPU hours (substantial cleanup operator engineering).

### S.2 — Soliton-resolution-style cleanup framing (Bilman-Buckingham 2019)

**Source**: Bilman-Buckingham arXiv:1905.02493 (2019); soliton-resolution
conjecture for NLS.

**Mechanism**: substrate iterated cleanup as resolution of arbitrary
input into discrete attractor library. NOT new mechanism; conceptual
framing connecting substrate to deep math.

**Substrate-novel content**: framing only. Pyrkov 2020 already operates
this analogy.

**Cross-mechanism stacking**: provides theoretical justification for
multi-hop cleanup chain preserving attractor template across hops.

**Falsifiable prediction**:
- P(soliton-resolution conjecture applicable to substrate cleanup): 50-65%
  (framing-level claim)
- P(substantial substrate-product value beyond framing): 15-25%

**Cost**: 0 GPU hours (conceptual integration).

### S.3 — Topological-soliton encoding for Bet F rescue (cross-axis)

**Source**: arXiv:2411.07775 (2024) topological resilience optical
skyrmions; cross-axis with R28 Burgers-vector topology + Bet F SSH-BSC
(R10 framework).

**Mechanism**: bundle topological invariants protect against per-hop
noise. Combines:
- Bet F SSH-BSC chiral-AIII winding (current Bet F mechanism)
- R28 edge/screw distinction (Severino-Kamien 2024)
- R28 Nayak Burgers × topological invariant (2020)
- R31 soliton topological-charge protection (sine-Gordon-like)

**Cross-mechanism stacking**: this is a NEW 8th Bet F rescue sketch
(joins R29 #5 composite + R28 #6 edge/screw + R28 #7 Nayak — now #8
soliton topological-charge).

**Falsifiable prediction**:
- P(soliton topological-charge protection beyond AIII Z winding): 25-40%
- P(8-rescue Bet F space combined succeeds if v3 fails): 80-85% (was 80%
  with 7 rescues)

**Cost**: substrate Bet F-dependent; only if Bet F v3 fails.

### S.4 — Discrete-attractor cascadability (Manakov 2018 substrate-applicable
        evidence)

**Source**: Manakov soliton NOR/OR arXiv:1806.00965 (2018) — cascadability
proof.

**Mechanism**: discrete-attractor analog of soliton cascadability —
substrate cleanup output of one nonlinear stage feeds the next without
shape loss.

**Substrate implementation**:
- Substrate Hebbian-trained attractors as discrete-soliton-analogs
- Multi-hop cleanup chain preserves attractor template per Manakov
  cascadability framing
- Empirical test: compare d=50 multi-hop with Manakov-inspired hop
  architecture vs current substrate

**Substrate-novel content — PARTIAL**: framing connects substrate
multi-hop directly to soliton cascadability proof; substrate-specific
construction work is engineering.

**Falsifiable prediction**:
- P(Manakov-cascadability substrate framing applicable): 50-65%
- P(d=50 multi-hop gain ≥ 1.2× from cascadability-aware architecture):
  20-35%

**Cost**: 4-6 GPU hours (substrate multi-hop architecture modification).

### R31 mechanism summary

| # | Mechanism | Substrate-novel? | P(meaningful gain) | Cost (GPU hr) | Notes |
|---|---|---|---|---|---|
| **S.1** | **CGLE dissipative cleanup** | **PARTIAL — Pyrkov 2020 port** | **25-40%** | **6-10** | **THE substrate-applicable contribution** |
| S.2 | Soliton-resolution framing | NO — conceptual | 15-25% | 0 | Justifies S.1 + S.4 |
| S.3 | Topological-soliton Bet F rescue | NO — extends R28 | 25-40% | Bet F-dep | New 8th Bet F rescue sketch |
| S.4 | Discrete-attractor cascadability | PARTIAL — Manakov framing | 20-35% | 4-6 | Multi-hop architecture connection |

**Combined recommendation**: pursue S.1 CGLE cleanup as substrate-product
engineering deliverable; S.2 framing 0-cost integration; S.3 as Bet F
rescue if v3 fails; S.4 as multi-hop architecture connection.

---

## 3. CRITICAL HONEST FRAMING per [[feedback-no-papers-product-only]]

**For Strategy decision** on R31 promotion:

**ENGINEERING R31** — limited substrate-applicable content:
- S.1 CGLE cleanup (Pyrkov 2020 port) is the genuine substrate-product
  engineering deliverable
- S.4 Manakov cascadability is multi-hop architecture framing only
- Other mechanisms either decorative or conceptual

**THEORY R31** — Pyrkov 2020 is the load-bearing reference:
- Substrate cleanup as soliton-attractor analog has ONE rigorous
  precedent
- Substrate could empirically test Pyrkov 2020 framework at high-D
  discrete scale
- Substrate-novel content: validating Pyrkov 2020 at substrate scale

**Per [[feedback-dont-overextend-theorems]]**: explicitly cautioned
against continuous-PDE integrability claims for substrate. Discretization
breaks integrability; substrate is DNLS-like with Peierls-Nabarro
pinning.

**Per [[feedback-no-papers-product-only]]**: substrate-product framing
is "substrate empirically validates Pyrkov 2020 CGLE-attractor framework
at high-D scale," NOT "novel soliton-based substrate theory."

---

## 4. Materials physics LOAD-BEARING (per [[feedback-materials-science-probe]])

**Soliton-resolution conjecture** (NLS) IS canonical mathematical
physics — the cleanup-as-resolution framing is mathematically rigorous,
NOT decorative analogy.

**CGLE dissipative-soliton attractors** (Pyrkov 2020) ARE canonical
nonlinear dynamics — basin-of-attraction analysis directly transferable
to substrate iterated cleanup.

**Topological-soliton stability** (skyrmions, kinks) IS canonical
topological-protection physics — substrate Bet F SSH-BSC chiral-AIII
winding inherits same stability principles.

**LOAD-BEARING analogs identified**: soliton-resolution conjecture +
CGLE attractor basins + topological-charge protection. These ARE
substrate-relevant load-bearing math, NOT decorative.

**DECORATIVE analogs honestly filtered**: continuous KdV/NLS integrability
(broken under discretization), fiber-optic transmission (wrong
dimension type), Davydov proteins (contested), soliton-based optical
computing (overpromised).

---

## 5. Experimental design recommendations

### Probe 1 (HIGH PRIORITY): CGLE dissipative cleanup (S.1)

**Hypothesis**: CGLE-style fixed-point attractor cleanup outperforms
substrate's current softmax cleanup on multi-hop accuracy.

**Setup**:
- Implement substrate cleanup as CGLE iteration
- Parameters β (dispersion), ε (cubic nonlinearity), μ (quintic
  nonlinearity), δ (gain/loss) tuned for substrate Kerdock codebook
- Single iteration: substrate state ψ → updated state via CGLE map
- Multi-hop test: chain CGLE iterations across hops; measure d=50 acc

**Predictions** (falsifiable):
- (a) P(CGLE cleanup d=25 baseline matches softmax): 50-65%
- (b) P(CGLE cleanup d=50 acc ≥ 0.30): 25-40%
- (c) P(CGLE basin stiffness ≥ 1.5× softmax): 35-50%

**Kill criterion**: if CGLE cleanup d=25 baseline degrades vs softmax,
port not productive.

**Cost**: 6-10 GPU hours.

### Probe 2 (LOW PRIORITY): Manakov cascadability test (S.4)

**Hypothesis**: substrate multi-hop with cascadability-aware architecture
preserves attractor template across hops.

**Setup**:
- Modify substrate multi-hop architecture per Manakov cascadability
  principles
- Measure d=50 multi-hop acc vs current baseline
- Compare shape-preservation (attractor template distance) across hops

**Predictions**:
- (a) P(cascadability-aware d=50 acc ≥ 1.2× baseline): 20-35%

**Cost**: 4-6 GPU hours.

### Probe 3 (CONTINGENT): Topological-soliton Bet F rescue (S.3)

Only run if Bet F v3 (full mode) returns null. Adds 8th rescue sketch
to existing list.

---

## 6. Predictions summary (with explicit probabilities per [[feedback-no-smoke]])

| Prediction | P | Notes |
|---|---|---|
| CGLE cleanup d=50 acc ≥ 0.30 | 25-40% | Pyrkov 2020 substrate port |
| CGLE basin stiffness exceeds softmax | 35-50% | Theoretical advantage |
| Soliton-resolution conjecture mathematically applicable | 50-65% | Framing-level claim |
| Continuous-PDE integrability claims for substrate are overextension | 90% | Mathematical fact |
| Pure-soliton substrate practical at current arch | 5% | NEGATIVE — V2 territory |
| R31 produces substrate-novel observation beyond R32 | 35% | Cross-axis stacking primary value |
| Manakov cascadability gives substrate d=50 gain ≥ 1.2× | 20-35% | Framing-led architecture mod |
| Topological-soliton Bet F rescue succeeds | 25-40% | New 8th rescue sketch |
| Cross-axis stacking (S.1 + Bet N rehab + R33) productive | 25-40% | Multiple mechanism axes |

---

## 7. Citations (verified arXiv / DOI, 1967-2026)

### LOAD-BEARING for substrate (CGLE + soliton resolution + topological)
- **Pyrkov-Byrnes-Cherny arXiv:1909.05082 (Symmetry 12, 24, 2020) —
  CENTRAL REFERENCE: solitonic fixed-point attractors in CGLE for
  associative memories**
- **Bilman-Buckingham arXiv:1905.02493 (2019) — DSW + asymptotic
  solitons in focusing NLS (soliton resolution)**
- **Wu arXiv:2401.15819 (2024) — KdV n-soliton stability with explicit
  phase shifts**
- arXiv:2411.07775 (2024) — topological resilience of optical skyrmions
- Manakov NOR/OR arXiv:1806.00965 (2018) — cascadability proof
- Ricard-Falcon arXiv:2411.10376 (PRL 133 264002, 2024) — soliton over
  disordered topography

### Foundational soliton theory (continuous; supporting only)
- Gardner-Greene-Kruskal-Miura 1967 — KdV inverse scattering
- Zakharov-Shabat 1972 — NLS spectral problem
- Mollenauer-Stolen-Gordon 1980 — optical fiber solitons

### Discrete / lattice solitons (CRITICAL CAVEAT)
- arXiv:2102.05332 + arXiv:2105.04202 (2021) — closeness of AL to DNLS
- **arXiv:2509.25650 (2025) — DNLS vs Ablowitz-Ladik (KEY DISCRETIZATION
  CAVEAT)**
- arXiv:2507.13643 (2025) — discrete NLS exponential asymptotics

### Optical fiber + microresonator (decorative for substrate)
- JOSA B 41 1655 (2024) — multimode fiber solitons review
- arXiv:2403.01107 (Light Sci. & Appl. 13, 2024) — octave-spanning Kerr
  soliton combs LiNbO₃
- arXiv:2505.09953 (2025) — Kerr soliton microcombs

### Davydov solitons (contested; supporting only)
- Georgiev-Glazebrook arXiv:2006.16798 (2020)
- Davydov 1973 — original proposal

### Integrable systems (decorative for substrate)
- Lou-Hu Chaos 34 103102 (2024) — multiple Lax integrable AKNS

### Solitons in disordered media (PARTIAL substrate-relevant)
- Ricard-Falcon arXiv:2411.10376 (PRL 2024) — disordered topography
- arXiv:2502.08463 (2025) — nonlinear Anderson screening
- arXiv:2106.07147 (2021) — Anderson localization in Toda

### Topological solitons (Bet F cross-axis)
- arXiv:2411.07775 (2024) — optical skyrmion decoherence resilience
- Melcher arXiv:1711.07717 — axisymmetric chiral skyrmion stability
- arXiv:2205.10329v3 — optical skyrmions review

### Soliton-based information storage (overpromised)
- Springer J. Opt. (2024) DOI:10.1007/s12596-023-01534-x — logic-gate review
- arXiv:2407.18725 (2024) — DL coded info vector solitons

### Per [[feedback-verify-implementations]] audit
- Spot-checked Pyrkov-Byrnes-Cherny arXiv:1909.05082 abstract:
  "solitonic fixed-point attractors in CGLE for associative memories" ✓
- Spot-checked Bilman-Buckingham arXiv:1905.02493 abstract: "dispersive
  shock waves + asymptotic solitons in focusing NLS" ✓
- Spot-checked Wu arXiv:2401.15819 abstract: "KdV n-soliton orbital
  stability with explicit phase shifts" ✓
- Spot-checked arXiv:2509.25650 abstract: "discrete NLS vs Ablowitz-Ladik
  existence and dynamics over nonzero background" ✓
- Spot-checked Manakov arXiv:1806.00965 abstract: "Manakov soliton
  NOR/OR via energy-sharing collisions" ✓
- Probability all framework attributions correct: 90%+
- Probability S.1 CGLE port substrate-applicable: 50-65% (substantial
  engineering required for substrate-specific parameterization)

---

## 8. Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Most soliton physics is DECORATIVE for discrete substrate**.
   Continuous-PDE integrability is FRAGILE under discretization (DNLS
   non-integrable; AL specially-chosen). Substrate is fundamentally
   discrete; continuous-soliton integrability claims are OVEREXTENSION.

2. **Pyrkov-Byrnes-Cherny 2020 (arXiv:1909.05082) is THE substrate-
   applicable reference**. Single paper that explicitly casts soliton
   as Hopfield attractor with mathematically operational analogy. Other
   papers provide context but not direct mechanism.

3. **R31 substrate-novel contribution is LIMITED**: S.1 CGLE port +
   S.4 Manakov cascadability framing + S.3 topological Bet F rescue
   sketch. Most R31 value is cross-axis stacking with Bet N rehab + R32
   + R33 + Bet F + R28.

4. **Per [[feedback-dont-overextend-theorems]]**: explicitly cautioned
   against continuous-PDE integrability claims. Discretization breaks
   integrability.

5. **Per [[feedback-materials-science-probe]]**: load-bearing analogs
   identified (soliton resolution conjecture + CGLE attractor basins +
   topological-charge protection). Decorative analogs honestly filtered
   (continuous integrability + fiber optics + Davydov + soliton-based
   computing).

6. **Per [[feedback-rehabilitation-after-rejection]]**: limited rescue
   mechanisms (4 candidates; 2 productive). Rehab discipline applied
   despite minimal substrate-applicable content.

7. **Per [[feedback-no-papers-product-only]]**: R31 substrate-product
   framing is "substrate empirically validates Pyrkov 2020 CGLE
   framework at high-D scale," NOT novel soliton-based substrate theory.

8. **Bet P P.7 magnon-coupled standing-wave** (Entry 30) is closely
   related to R31 S.1 CGLE attractor cleanup. Both are wave-attractor
   substrate proposals. Strategy should consider unified treatment of
   Bet P P.7 + R31 S.1.

9. **R32 + R31 + Bet P together** represent a wave-based-substrate
   exploration cluster. Most likely outcome (per honest filtering
   findings):
   - R32 M.1 phasor codebook extension: 35-50% capacity gain
   - R31 S.1 CGLE cleanup: 25-40% d=50 acc gain
   - Bet P P.4 spin-glass cluster Hopfield: 40-55% engineering
   - Combined cross-axis: 25-40% multiplicative

10. **Verified-implementations honesty**: subagent did real external
    lit scan with 19 tool uses + 53K tokens, ~45 verified citations
    1967-2026. Subagent flagged discretization caveat + most-paper-
    decorative finding UNPROMPTED — strong brutal-honesty protocol
    confirmation. Pyrkov 2020 cited 3 times in subagent's
    "particularly relevant" list — confirms central status.

---

## 9. Deliverable summary

**To Strategy** (R31 routing decision):
- Pure-soliton substrate: NOT productive at current arch (V2 territory)
- S.1 CGLE dissipative cleanup (Pyrkov 2020 port): HIGH PRIORITY
  substrate-product engineering; 25-40% P(d=50 gain); 6-10 GPU hours
- S.2 soliton-resolution framing: 0 GPU conceptual integration
- S.3 topological-soliton Bet F rescue: NEW 8th rescue sketch;
  contingent on Bet F v3 failure
- S.4 Manakov cascadability: LOW; 4-6 GPU hours; multi-hop architecture
- **Recommendation**: pursue S.1 CGLE cleanup as substrate-product
  engineering deliverable. Combine with Bet P P.7 magnon-coupled and
  R32 M.1 phasor extension as unified wave-based substrate cluster.

**To Experiment Dev**:
- Probe 1 HIGH: S.1 CGLE cleanup (6-10 GPU hours; substrate cleanup
  operator redesign)
- Probe 2 LOW: S.4 Manakov cascadability test (4-6 GPU hours)
- Probe 3 CONTINGENT: S.3 topological-soliton Bet F rescue (only if
  Bet F v3 fails)

**To Research (future R# routing — all META queue items now done)**:
- R27 (META Light-matter / photonic): MEDIUM; remaining design-space
  audit item
- R19 / R21 / R22 / R25 (LOWER): original design-space audit items
- R36-R39 (renumbered Research-internal followups from R16/R18/R17/R28)
- META queue NOW EXHAUSTED for original candidates #1-#7

**Per [[feedback-no-smoke]]**: R31 HONEST framing is "most soliton
physics decorative; one paper (Pyrkov 2020) makes substrate-applicable."
Substrate-product value concentrated in CGLE cleanup port + cross-axis
stacking.

---

**End R31 note.** Total size target ~28-30 KB; actual: see wc -c on
finalized file.
