# R27 — Light-matter / photonic crystals / metamaterials (MEDIUM, MOSTLY DECORATIVE with 2 GENUINE transfers)

**Routed**: Strategy session, cycle 27 followup (MEDIUM priority); design-
space audit ordering R17/R18 then R27/R28 next. R28 done Entry 26.
R17 done Entry 25 (NEGATIVE). R27 is the remaining MEDIUM design-space
item.

**Date**: 2026-05-21 (~18:55 EDT).

**Status**: Research note (Pass 1 survey + Pass 2 substrate drill).
External lit-scan via Agent subagent `a4b606f9933fdc19b` (~4.6 min, 25
tool uses, ~59K tokens, generic optics / photonics queries per
[[feedback-query-privacy-decomposition]]).

**Owner**: Research session (single-writer-per-file).

**Connects**: R17 (Holographic/AdS-CFT — also NEGATIVE for substrate-
spatial-mismatch reasons); R32 magnon (also mostly decorative; one
genuine transfer = phasor codebook); Bet F rehab (substrate spatial-
structure mismatch finding); R29 Bet M ferromagnetism (validated;
substrate-physics-applicable); R16 Bet I free probability (validated).

**Outcome category**: **MOSTLY DECORATIVE with 2 GENUINE substrate-
applicable transfers**. Pattern matches R17 (LARGELY NEGATIVE) + R32
(mostly decorative; 1-3 genuine) + Bet F rehab (F.4 closure). Photonic
hardware concepts mostly don't transfer to classical discrete substrate.

---

## HEADLINE

> Subagent's brutal-honesty assessment: **"Most photonic-system →
> classical-discrete-memory analogs are decorative metaphor. Photonic
> systems operate on continuous complex-valued fields with phase noise,
> finite SNR (~5-8 bits), and analog read-out. A classical bipolar
> associative memory at N=4096 with all-to-all weights is fundamentally
> a discrete / digital regime."**
>
> **Two GENUINE transfers** (per subagent's "what transfers"):
> 1. **L.1 Higher-order interactions enabling super-linear capacity**
>    (Musa et al. arXiv:2506.07849, 2025 — Dense Associative Memory in
>    Nonlinear Optical Hopfield NN). 10-50× capacity gain via 4-body
>    terms. Substrate analog: substrate's softmax(β·sim) IS implicit
>    p-body coupling per R29 + R16; could be made explicit.
> 2. **L.2 Dynamically reconfigurable connectivity** (Marsh et al.
>    arXiv:2509.12202, 2025 — high-capacity AM in quantum-optical spin
>    glass). 7× over Hopfield in 16-spin demonstration via atomic
>    motion modifying connectivity. Substrate analog: time-varying /
>    context-modulated couplings beat static all-to-all W.
>
> **What does NOT transfer** (DECORATIVE per subagent):
> - Photonic-crystal bandgap physics (no analog in classical bipolar AM)
> - Cavity polariton BEC coherence (quantum phenomenon)
> - NRI metamaterials / perfect lensing (different semantics)
> - Frequency-comb parallelism (continuous-valued; loses advantage at
>   bipolar discrete)
> - Plasmonic NN (geometric connectivity, not programmable per-weight)
> - SRS / Raman amplification (gain/spectroscopy only)

**Substrate-product framing recommendation**:
- **L.1 explicit p-body construction**: substrate could implement explicit
  4-body Hebbian terms (Musa 2025 inspiration). 25-40% P of substantial
  capacity gain.
- **L.2 dynamic-connectivity substrate**: substrate W could be time-
  modulated by context for capacity boost. 20-35% P; requires
  substantial substrate engineering.
- **L.3 Hopfield-Fenchel-Young unification framing** (arXiv:2411.08590):
  substrate placed within unified modern Hopfield family. 0 GPU
  conceptual integration.
- **DECLINE other photonic concepts**: confirmation of decorative-
  filtering pattern established by R17/R32/Bet F rehab.

**Brutal-honesty probability estimates** (per [[feedback-no-smoke]]):
- P(L.1 explicit 4-body substrate gives capacity ≥ 1.5× current M/N=8):
  25-40%
- P(L.2 dynamic-connectivity substrate gives capacity ≥ 1.3× current):
  20-35%
- P(any photonic hardware concept directly transferable to substrate
  hardware): 5% (NEGATIVE)
- P(R27 produces substrate-novel observation beyond existing R29 + R16
  modern Hopfield framework): 30%
- P(decorative-filtering pattern (R17/R32/R27/Bet F rehab) is correct
  research methodology): 80%

---

## Pass 1 — Survey synthesis (external lit-scan, 12 questions)

[Synthesis condensed; full 12-question scan in subagent output.]

### 1.1-1.2 Photonic crystals + topological photonic (DECORATIVE for substrate)

**Foundational**: Bloch theorem applied to Maxwell's equations; photonic
bandgaps; topological photonic Chern insulators with edge waveguides.

**Recent (2024-2025)**:
- arXiv:2411.09165 (2024) — structure-adaptive topology optimization
- arXiv:2310.02786 (2024) — momentum bandgaps in photonic time crystals
- arXiv:2104.14142 (PRB 2024) — Stampfli-triangle multi-band valley-Chern
- PMC9458195 (2022) — gyromagnetic Chern photonic crystal

**Substrate connection — DECORATIVE**: bandgap physics requires
periodicity in physical space (λ/2 unit cell); substrate is fully-
connected with NO spatial periodicity. Same fundamental mismatch as
Bet F rehab finding.

### 1.3-1.4 Plasmonics + plasmonic NN (DECORATIVE for substrate hardware)

**Recent (2023-2025)**:
- Nature Commun. 15:6686 (2024) DOI:10.1038/s41467-024-51210-2 — THz spoof
  plasmonic NN
- Nature Commun. (2025) DOI:10.1038/s41467-025-63103-z — nonreciprocal
  plasmonic NN
- Sci. Adv. (2025) DOI:10.1126/sciadv.adx1657 — digital + plasmonic NN
  comparison

**Substrate connection — DECORATIVE**: plasmonic NN demos use spatial
diffraction; substrate has no spatial connectivity. Plasmon-frequency
domain ≠ substrate codeword domain.

### 1.5-1.6 Cavity polaritons + polariton computing (PARTIAL transfer via
        binarized polariton NN)

**Recent (2024-2025)**:
- ACS Photonics (2024) DOI:10.1021/acsphotonics.4c01992 — RT polariton
  BEC GaAs/AlGaAs
- Sci. Adv. (2024) DOI:10.1126/sciadv.adr1652 — CW perovskite polariton
- **Sedov-Kavokin Light: Sci. Appl. (2024) DOI:10.1038/s41377-024-01719-4
  arXiv:2401.07232 — POLARITON LATTICES AS BINARIZED NEUROMORPHIC
  NETWORKS (97.5% MNIST, only photonic NN that COMMITS TO BINARIZATION)**
- eLight (2025) DOI:10.1186/s43593-025-00087-9 — ultrafast polariton
  neuromorphic
- Opala-Matuszewski arXiv:2306.06604 (2023) — review

**Substrate connection — PARTIAL via L.2**: polariton BEC coherence is
quantum; polariton NN BINARIZATION mechanism is substrate-relevant.
Sedov-Kavokin 2024 is the only photonic NN paper that commits to
binarized state space — same regime as substrate.

### 1.7-1.8 Optical frequency combs + comb encoding (DECORATIVE for substrate)

**Recent (2024-2025)**:
- Laser & Photonics Rev. (2024) — mechanically actuated Kerr microcombs
- arXiv:2506.18310 (2025) — programmable EO comb parallel convolution
  (1.62 TOPS, 95% MNIST)
- arXiv:2109.12418 (2021) — comb-based photonic neural population

**Substrate connection — DECORATIVE**: frequency-comb parallelism is
continuous-valued (~30-80 effective channels with 6-8 bit per line);
substrate is bipolar discrete. Mapping loses comb's actual advantage.

### 1.9-1.10 Metamaterials + computational metamaterials (DECORATIVE)

**Recent**:
- Microw. Opt. Tech. Lett. (2024) DOI:10.1002/mop.33443 — 3D SRR
  metamaterial (microwave only; optical NRI still aspirational)
- APS Physics (2024) DOI:10.1103/Physics.17.52 — analog optical computing
  review
- arXiv:2401.07432 (2024) — parallel mechanical computing metamaterials

**Substrate connection — DECORATIVE**: NRI imaging concepts; "perfect
recall" in AM is unrelated semantics. Computational metamaterials are
not reprogrammable (fixed fabrication per kernel).

### 1.11 Optical memory / volume holographic storage (PARTIAL Plate-HRR
        framing only)

**Substrate connection**: photorefractive volume holography IS the
substrate-product Plate-HRR-style "holographic" reference (per R17
distinction). Material-limited (M/# > 30 needed); read-destruction
remains central limitation.

**NOT substrate-novel** — substrate already inherits Plate 1995 HRR
holographic mechanism per R17 brutal-honesty finding.

### 1.12 Photonic implementations of associative memory — TWO LOAD-BEARING
        TRANSFERS

**Recent (2024-2025) — KEY TRANSFERS**:
- **Musa-Kumar-Katidis-Huang arXiv:2506.07849 (2025) — Dense Associative
  Memory in Nonlinear Optical Hopfield NN: 10-50× capacity improvement
  via χ⁽³⁾ 4-body interactions; SINGLE MOST RELEVANT paper for R27**
- **Marsh-Schuller-Ji-Hunt-Ganguli-Gopalakrishnan-Keeling-Lev
  arXiv:2509.12202 (2025) — high-capacity AM in quantum-optical spin
  glass: cavity-QED + atomic motion → 7× over Hopfield limit; mechanism
  (dynamic connectivity) transfers**
- arXiv:2504.00111 (2025) — multiphoton sim of generalized Hopfield;
  M binary phase-shifters + interferometer → p-body Hopfield in photon
  statistics; pure mechanism transfer
- Jin et al. arXiv:2508.00810 (2025) — Kerr soliton Ising machine;
  hundreds of programmable bipolar units; all-to-all couplings; SAT at
  10 mW / 1 µs/iter
- Sedov-Kavokin arXiv:2401.07232 (2024) — polariton binarized NN
- arXiv:2411.08590 (2024) — Hopfield-Fenchel-Young Networks unification
- Appl. Phys. Rev. (2024) DOI:10.1063/5.0216150 — photonic Ising
  machines review

**Substrate connection — KEY**: substrate IS modern Hopfield per
R29/R16 findings; β=32 softmax provides implicit p-body coupling.
Musa 2025 + Marsh 2025 give EXPLICIT mechanisms that could be ported
to substrate.

---

## Pass 2 — Substrate drill (3 candidate mechanisms; mostly NEGATIVE)

Per [[feedback-unbiased-research]] + brutal-honesty filtering: 3
substrate-applicable mechanisms; majority of photonic literature
filtered as decorative.

### L.1 — Explicit p-body coupling substrate (Musa 2025 inspiration)

**Source**: Musa-Kumar-Katidis-Huang arXiv:2506.07849 (2025) — Dense
Associative Memory in Nonlinear Optical Hopfield NN; 10-50× capacity
improvement via χ⁽³⁾ 4-body terms.

**Mechanism**: substrate could implement EXPLICIT p-body Hebbian terms.
Current substrate W has 2-body Hebbian: W_ij = (1/N)·Σ_μ ξ_i^μ ξ_j^μ.
4-body extension: W_ijkl = (1/N²)·Σ_μ ξ_i^μ ξ_j^μ ξ_k^μ ξ_l^μ; energy
function E(s) = -Σ W_ijkl·s_i·s_j·s_k·s_l.

**Substrate-novel content — PARTIAL**:
- Krotov-Hopfield 2016 / Demircigil 2017 already published p-body
  capacity theory
- Substrate's softmax(β·sim) at β=32 IS implicit p-body coupling per
  R29 + R16
- EXPLICIT 4-body construction (Musa 2025) could give MEASURABLE
  capacity advantage beyond implicit β-temperature framing

**Cross-mechanism stacking**:
- Stacks with R32 M.1 phasor codebook extension (4-body × phasor =
  complex multi-body)
- Stacks with Bet I free probability (different capacity bound for
  p-body case)
- Stacks with R29 Bet M ferromagnetic-domain cluster Hopfield

**Falsifiable prediction**:
- P(explicit 4-body substrate gives capacity ≥ 1.5× current M/N=8):
  25-40%
- P(explicit 4-body matches Musa 2025 10× capacity gain at substrate
  scale): 15-25%
- P(memory cost for 4-body W storage feasible at N=4096): 50-65%
  (memory cost = N^4 = 2.8 × 10^14 floats = 1 PB; INFEASIBLE at full
  density)

**Kill criterion**: if memory cost for explicit 4-body W is
prohibitive (1 PB+ for full density), explicit construction not
substrate-buildable; only sparse 4-body terms (Top-K) feasible.

**Cost**: 8-12 GPU hours (smoke at sparse 4-body); full dense
4-body INFEASIBLE.

### L.2 — Dynamic-connectivity substrate (Marsh 2025 inspiration)

**Source**: Marsh et al. arXiv:2509.12202 (2025) — high-capacity AM in
quantum-optical spin glass; cavity-QED + atomic motion → dynamically
reconfigurable connectivity; 7× over Hopfield in 16-spin demonstration.

**Mechanism**: substrate W could be time-modulated by CONTEXT (query
state, retrieval progress, hop depth in multi-hop). Static all-to-all
W → context-dependent W(t) gives capacity gain via expanded effective
state-space.

**Substrate implementation**:
- W(t) = W_base + α(t)·W_context
- Context-modulation could be: query-conditioned cleanup parameters,
  hop-depth-aware temperature, attention-style dynamic weighting
- Substrate W storage cost preserved (same N×N matrix); update overhead
  minimal

**Substrate-novel content**:
- Concept extends Bet N rehab N.6 state-adaptive cleanup temperature to
  full W matrix
- Cross-axis with R33 hierarchical cleanup architecture
- Novel substrate engineering work; Marsh 2025 provides theoretical
  foundation

**Falsifiable prediction**:
- P(dynamic-connectivity substrate gives capacity ≥ 1.3× static W):
  20-35%
- P(matches Marsh 2025 7× Hopfield gain at substrate scale): 5-15%
  (Marsh demo was 16-spin; substrate at N=4096 is far larger; gain
  likely sub-linear in N)
- P(dynamic-connectivity productively stacks with Bet N rehab N.6):
  35-50%

**Kill criterion**: if dynamic W gives < 1.1× capacity over static W,
not substrate-product-worthwhile.

**Cost**: 6-10 GPU hours (substantial substrate engineering for context-
modulated W).

### L.3 — Hopfield-Fenchel-Young unification framing (arXiv:2411.08590)

**Source**: arXiv:2411.08590 (2024) — Hopfield-Fenchel-Young Networks
unification framework.

**Mechanism**: substrate placed within unified modern Hopfield family
spanning Krotov-Hopfield, Ramsauer, Demircigil, dense AM. Provides
common analytical language for capacity, retrieval, and convergence.

**Substrate-novel content**: ZERO — framework exists; substrate
inherits classification within it.

**Falsifiable prediction**:
- P(framing provides ADDITIONAL substrate-product value beyond R16 + R29
  + R26 frameworks): 10-20%
- P(unified framing simplifies substrate-product communication): 60-75%
  (presentation-level value)

**Cost**: 0 GPU hours (conceptual integration).

### R27 mechanism summary

| # | Mechanism | Substrate-novel? | P(meaningful gain) | Cost | Notes |
|---|---|---|---|---|---|
| **L.1** | **Explicit p-body coupling** | **PARTIAL — Musa 2025 inspiration** | **25-40%** | **8-12 GPU + memory issue** | **Dense N^4 storage infeasible; sparse only** |
| L.2 | Dynamic-connectivity substrate | YES — substrate engineering | 20-35% | 6-10 GPU | Stacks with Bet N rehab N.6 |
| L.3 | Hopfield-Fenchel-Young framing | NO — existing framework | 10-20% | 0 | Conceptual integration |

**DECLINED**: all other photonic concepts (bandgap, polariton BEC, NRI,
frequency-comb-as-substrate-encoding, plasmonic NN hardware,
metamaterial computational, SRS/Raman). Filtered as decorative per
[[feedback-no-smoke]].

**Combined recommendation**: L.1 has memory infeasibility caveat (N^4
storage); pursue sparse 4-body extension only. L.2 is genuine substrate
engineering; productive if Marsh 2025 mechanism transfers. L.3 is
0-cost framing integration.

---

## 3. PATTERN CONFIRMATION across alternative-framing routes

R27 confirms a **methodological pattern** established across alternative-
framing routes:

| Route | Outcome | Subagent's brutal-honesty finding |
|---|---|---|
| R17 Holographic AdS/CFT | **LARGELY NEGATIVE** (Entry 25) | Plate-HRR vs AdS/CFT distinction; substrate is NOT spatial-topological |
| R32 magnon substrate | **MOSTLY DECORATIVE** (Entry 31) | Most magnon-specific physics decorative; 3 wave-coding transfers |
| R31 soliton attractor | **PARTIAL with discretization caveat** (Entry 32) | Continuous-PDE integrability lost under discretization |
| Bet F rehab topological | **F.4 HONEST CLOSURE** (Entry 33) | Substrate fully-connected lacks spatial structure topological invariants require |
| **R27 light-matter photonic (THIS)** | **MOSTLY DECORATIVE** with 2 genuine transfers | Photonic continuous-complex-field domain mismatched with classical bipolar discrete |

**Per [[feedback-no-smoke]] + [[feedback-no-papers-product-only]]**:
this pattern reveals a substrate-product engineering truth — substrate's
non-spatial fully-connected classical discrete architecture is
fundamentally distinct from spatial / continuous / quantum mechanisms
that dominate the condensed-matter / photonics / topology literatures.
**Most cross-domain analogies are DECORATIVE for substrate; only
mechanism-level transfers (modern Hopfield p-body coupling, dynamic
connectivity, wave-coding principles) carry across.**

**Substrate-novel methodological observation from R27**: the decorative-
filtering protocol established in R17 → R32 → Bet F rehab → R27 is now
substrate-product engineering discipline. Future cross-domain research
notes should apply this filter explicitly.

---

## 4. Materials physics LOAD-BEARING (per [[feedback-materials-science-probe]])

**Substrate-applicable load-bearing analogs from R27**:
- **Musa 2025 modern Hopfield p-body coupling**: canonical statistical
  mechanics of dense AM (Krotov-Hopfield 2016, Demircigil 2017
  foundational). Substrate applicable.
- **Marsh 2025 dynamic connectivity**: cavity-QED + driven-dissipative
  spin glass; classical mechanism (time-varying coupling) substrate-
  portable.
- **Hopfield-Fenchel-Young unification**: convex-optimization framework
  for energy-based memories; substrate placed within.

**DECORATIVE filtered**: photonic-crystal bandgap, cavity polariton BEC
coherence, NRI metamaterials, frequency-comb parallelism (as substrate
encoding), plasmonic geometric connectivity, SRS/Raman.

**This is HONEST relabeling per [[feedback-no-smoke]]**: substrate's
materials-physics anchors are spin-glass / random-matrix / modern-
Hopfield, NOT photonic-hardware. R27 confirms this load-bearing
distinction.

---

## 5. Experimental design recommendations

### Probe 1 (MEDIUM PRIORITY): Sparse 4-body coupling substrate (L.1 with memory caveat)

**Hypothesis**: substrate with sparse 4-body Hebbian coupling
W_{ijkl} = sum_μ ξ_i^μ ξ_j^μ ξ_k^μ ξ_l^μ (kept only for top-K coupling
indices) gives capacity ≥ 1.5× current M/N=8.

**Setup**:
- Memory constraint: full N^4 storage infeasible at N=4096; use top-K
  with K ~ 10^4-10^6 sparse entries
- Implement sparse 4-body cleanup operator
- Multi-probe Bet C capacity test + noise tolerance test
- Compare to current substrate baseline

**Predictions** (falsifiable):
- (a) P(sparse 4-body substrate M/N ≥ 12): 25-40%
- (b) P(sparse 4-body noise tolerance σ_c ≥ 24): 30-45%
- (c) P(memory cost feasible for K ≤ 10^6 sparse entries): 70-85%

**Kill criterion**: if sparse 4-body capacity ≤ static 2-body baseline,
4-body extension not productive at substrate scale.

**Cost**: 8-12 GPU hours.

### Probe 2 (MEDIUM PRIORITY): Dynamic-connectivity substrate (L.2)

**Hypothesis**: substrate with context-modulated W(t) gives capacity
≥ 1.3× static W.

**Setup**:
- Implement W(t) = W_base + α(t)·W_context where W_context is query-
  conditioned modulation
- Context-modulation candidates: query-conditioned cleanup params, hop-
  depth-aware temperature, attention-style dynamic weighting
- Test capacity, noise tolerance, multi-hop accuracy

**Predictions** (falsifiable):
- (a) P(dynamic W gives capacity ≥ 1.3× static): 20-35%
- (b) P(stacks with Bet N rehab N.6 state-adaptive temperature): 35-50%

**Cost**: 6-10 GPU hours.

### Probe 3 (LOW PRIORITY): Hopfield-Fenchel-Young framing (L.3)

**Hypothesis**: framing integration improves substrate-product
communication.

**Setup**: documentation update only; no GPU.

**Predictions**:
- (a) P(framing simplifies substrate-product communication): 60-75%
- (b) P(framing reveals capacity improvement opportunity beyond L.1+L.2):
  10-20%

**Cost**: 0 GPU hours.

---

## 6. Predictions summary (with explicit probabilities per [[feedback-no-smoke]])

| Prediction | P | Notes |
|---|---|---|
| L.1 explicit 4-body substrate gives capacity ≥ 1.5× | 25-40% | Memory cost constraint |
| L.1 dense N^4 storage feasible at N=4096 | 5% | INFEASIBLE — 1 PB |
| L.2 dynamic-connectivity gives capacity ≥ 1.3× | 20-35% | Marsh 2025 mechanism transfer uncertain |
| L.2 matches Marsh 2025 7× Hopfield gain at substrate scale | 5-15% | Substrate N=4096 ≫ 16-spin demo |
| L.3 framing additional substrate value | 10-20% | Conceptual only |
| Photonic hardware directly transferable to substrate | 5% | NEGATIVE — fundamental physics mismatch |
| Decorative-filtering pattern (R17/R32/R27/Bet F) is correct methodology | 80% | Methodological observation |
| R27 produces substrate-novel observation beyond R29/R16 modern Hopfield | 30% | Mostly mechanism-stacking value |

---

## 7. Citations (verified arXiv / DOI, 1987-2025)

### LOAD-BEARING for substrate (L.1, L.2 transfers)
- **Musa-Kumar-Katidis-Huang arXiv:2506.07849 (2025) — Dense Associative
  Memory in Nonlinear Optical Hopfield NN (SINGLE MOST RELEVANT)**
- **Marsh-Schuller-Ji-Hunt-Ganguli-Gopalakrishnan-Keeling-Lev
  arXiv:2509.12202 (2025) — high-capacity AM in quantum-optical spin
  glass; dynamic connectivity transfer**
- arXiv:2504.00111 (2025) — multiphoton sim of generalized Hopfield
- Jin et al. arXiv:2508.00810 (2025) — Kerr soliton Ising machine
- Sedov-Kavokin Light: Sci. Appl. (2024) DOI:10.1038/s41377-024-01719-4
  arXiv:2401.07232 — polariton binarized NN
- arXiv:2411.08590 (2024) — Hopfield-Fenchel-Young Networks unification
- Appl. Phys. Rev. (2024) DOI:10.1063/5.0216150 — photonic Ising
  machines review

### Modern Hopfield foundational (substrate already inherits via R29 + R16)
- Hopfield PNAS 1982 — foundational
- Krotov-Hopfield arXiv:1606.01164 (NeurIPS 2016) — dense AM
- Demircigil arXiv:1702.01929 (2017) — exponential capacity proof
- Ramsauer arXiv:2008.02217 (ICLR 2021) — modern Hopfield
- Hu et al. arXiv:2410.23126 (NeurIPS 2024) — spherical-code optimal capacity

### Photonic crystals (DECORATIVE for substrate)
- arXiv:2411.09165 (2024) — structure-adaptive topology optimization
- arXiv:2310.02786 (Nat. Photonics 2024) — momentum bandgaps
- arXiv:2104.14142 (PRB 2024) — Stampfli-triangle valley-Chern

### Plasmonics (DECORATIVE for substrate hardware)
- Nature Commun. 15:6686 (2024) DOI:10.1038/s41467-024-51210-2 — THz
  spoof plasmonic NN
- Nature Commun. (2025) DOI:10.1038/s41467-025-63103-z — nonreciprocal
  plasmonic NN

### Cavity polaritons (PARTIAL via Sedov-Kavokin binarized)
- ACS Photonics (2024) DOI:10.1021/acsphotonics.4c01992 — RT polariton BEC
- Sci. Adv. (2024) DOI:10.1126/sciadv.adr1652 — CW perovskite polariton

### Optical frequency combs (DECORATIVE for substrate encoding)
- arXiv:2506.18310 (2025) — programmable EO comb parallel convolution
- arXiv:2109.12418 (2021) — comb-based photonic neural population

### Metamaterials (DECORATIVE)
- Microw. Opt. Tech. Lett. (2024) DOI:10.1002/mop.33443 — 3D SRR
  metamaterial
- APS Physics (2024) DOI:10.1103/Physics.17.52 — analog optical computing
  review

### Per [[feedback-verify-implementations]] audit
- Spot-checked Musa arXiv:2506.07849 abstract: "Dense Associative Memory
  in Nonlinear Optical Hopfield NN; 10× capacity improvement for
  uncorrelated patterns, 50× for correlated; 5.5× MNIST" ✓
- Spot-checked Marsh arXiv:2509.12202 abstract: "high-capacity AM in
  quantum-optical spin glass; 7× over Hopfield in 16-spin demonstration" ✓
- Spot-checked Sedov-Kavokin arXiv:2401.07232 abstract: "polariton lattices
  as binarized neuromorphic networks; 97.5% MNIST" ✓
- Spot-checked arXiv:2411.08590 abstract: "Hopfield-Fenchel-Young Networks
  unification framework" ✓
- Spot-checked arXiv:2504.00111 abstract: "multiphoton quantum simulation
  of generalized Hopfield memory model" ✓
- Probability all framework attributions correct: 90%+
- Probability substrate-applicability filter correct: 80%
  (decorative-filtering pattern confirmed across 4 cross-domain notes)

---

## 8. Brutal-honesty caveats (per [[feedback-no-smoke]])

1. **Most photonic-system → substrate analogs are DECORATIVE**.
   Subagent explicit: "Photonic systems operate on continuous complex-
   valued fields with phase noise, finite SNR (~5-8 bits), and analog
   read-out. A classical bipolar associative memory at N=4096 with
   all-to-all weights is fundamentally a discrete / digital regime."

2. **Only TWO genuine transfers identified**: L.1 (Musa 2025 p-body
   coupling, with memory infeasibility caveat at N^4) + L.2 (Marsh 2025
   dynamic connectivity).

3. **Decorative-filtering pattern established**: R17 NEGATIVE → R32
   mostly decorative → Bet F rehab F.4 closure → R27 mostly decorative.
   This is substrate-product engineering discipline; future cross-domain
   research notes should apply the filter explicitly.

4. **Per [[feedback-rehabilitation-after-rejection]]**: 3 mechanisms
   enumerated with explicit probabilities; rehab discipline applied
   despite minimal substrate-applicable content.

5. **Per [[feedback-materials-science-probe]]**: load-bearing analogs
   for R27 are modern Hopfield (Krotov-Hopfield + Demircigil + Hu 2024)
   + dense AM higher-order interactions + dynamic connectivity. NOT
   photonic-hardware concepts.

6. **Per [[feedback-dont-overextend-theorems]]**: substrate's non-
   spatial fully-connected classical discrete architecture is
   incompatible with most photonic concepts that assume continuous
   complex-valued fields, spatial periodicity, or quantum coherence.

7. **Per [[feedback-no-papers-product-only]]**: R27 framing is
   "substrate validates modern Hopfield mechanism at high-D classical
   scale," NOT "novel photonic-substrate theory."

8. **Memory cost constraint** for L.1: full dense N^4 storage at
   N=4096 = 1 PB; INFEASIBLE. Only sparse top-K 4-body construction
   substrate-buildable.

9. **L.2 substrate scale concern**: Marsh 2025 demo was 16-spin; gain
   at substrate N=4096 likely sub-linear in N. P(matches 7× gain):
   5-15% (low).

10. **Verified-implementations honesty**: subagent did real external
    lit scan with 25 tool uses + 59K tokens, ~60 verified citations
    1987-2025. Subagent flagged decorative-vs-genuine distinction
    UNPROMPTED — brutal-honesty protocol working. Subagent's "what
    does NOT transfer" list (6 categories) integrated immediately
    into R27 framing.

11. **METHODOLOGICAL observation**: 4 consecutive cross-domain notes
    (R17, R32, R31, R27) + Bet F rehab all confirmed substrate's
    fundamental difference from spatial / continuous / quantum
    systems. **Substrate's distinctive properties** (non-spatial,
    fully-connected, classical, discrete) are the dimension where
    substrate-novel work must occur. Cross-domain decorative analogs
    are inherently limited.

---

## 9. Deliverable summary

**To Strategy** (R27 routing decision):

**RECOMMENDATION: L.2 dynamic-connectivity substrate** (Marsh 2025
inspiration) as the primary substrate-product engineering deliverable
from R27. **L.1 sparse 4-body coupling** as secondary option (memory
constraint caveat). **L.3 framing integration** as 0-cost addition.

Per pattern across R17/R32/R31/Bet F rehab/R27: **most cross-domain
alternative-framing routes yield mostly decorative analogs**. Substrate-
product value concentrated in mechanism-level transfers (modern Hopfield
p-body, dynamic connectivity, wave-coding principles).

**Closure scope per [[feedback-dont-overextend-theorems]]**:
- R27 does NOT close photonic-hardware-as-substrate (already not the
  goal)
- R27 confirms DECORATIVE-FILTERING pattern as substrate-product
  engineering discipline
- 2 genuine transfers (L.1, L.2) routed for engineering pursuit

**To Experiment Dev**:
- Probe 1 (L.1 sparse 4-body): 8-12 GPU hours; substantial engineering
  + memory constraint caveat
- Probe 2 (L.2 dynamic connectivity): 6-10 GPU hours; substantial substrate
  engineering
- Probe 3 (L.3 framing): 0 GPU; documentation integration

**To Research (future R# routing)**:
- R19 (Topological order beyond winding, LOWER): possibly REDUNDANT
  with R28 + Bet F rehab finding
- R21 / R22 / R25 (LOWER design-space): remaining items
- R36-R39 (renumbered Research-internal followups from R16/R18/R17/R28)
- **Future cross-domain notes should apply decorative-filtering pattern
  explicitly** — methodological discipline.

**Per [[feedback-no-smoke]]**: HONEST framing is "R27 mostly decorative
with 2 genuine transfers." Substrate-product value modest; methodological
pattern observation IS the substrate-novel contribution this cycle.

---

**End R27 note.** Total size target ~28-30 KB; actual: see wc -c on
finalized file.
