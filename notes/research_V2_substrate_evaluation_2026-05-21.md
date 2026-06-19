# Research note: V2 substrate evaluation — gain/loss per candidate

**Date**: 2026-05-21 ~20:50 EDT
**Owner**: Research session (single-writer)
**Request**: `strategy_request_to_research_V2_substrate_evaluation_2026-05-21.md` (20:32, user-directed)
**Decision-log entry**: Entry 52
**Pass-1 honesty label**: REAL external lit scan via 3 parallel Agent (general-purpose) subagents; ~36 papers surveyed, 2020-2026 dominant; generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — executive verdict

**Order of substrate-product priority (highest → lowest expected value)**:

| Rank | Candidate | Mechanism class | P(5× capacity, 6 mo) | Substrate-product fit |
|---|---|---|---|---|
| 1 | **V2.D** modern dense AM | Energy function change | 0.55-0.65 | Native softmax(β=32) already β-large regime; replace with explicit exp; LIT SUPPORT STRONGEST |
| 2 | **V2.B** hybrid HRR+bipolar | Storage mechanism extension | 0.10 capacity / 0.20 depth | Bet X recommendation; lift d=25 cliff via parallel HRR pool |
| 3 | **V2.C** large-N + codebook opt | Scaling + Welch-bound | 0.20-0.25 | R36 deep-drill predicts M/N drops at N=65536; not free win |
| 4 | **V2.A** hyperbolic-tiling | Topology / lattice change | 0.10-0.15 | Mean-field exponents; boundary pathology; FRSB marginal stability |
| 5 | **V2.F** magnon/phasor | Codebook structure | 0.25 capacity / 0.05 depth | Physical magnon = reservoir computer (NOT AM); phasor gains trace to sparsity, not wave structure |
| 6 | **V2.E** operator-algebra QEC | Algebraic recovery framework | 0.05-0.10 | Zero classical benchmark; Harlow theorem warning |

**Recommended action**: promote V2.D to active V2 research-track (highest expected value AND best literature support). V2.B preserves current substrate while extending compositional depth — best "build-on-top" option per Bet X UNIFYING insight. V2.A/V2.E/V2.F defer (theoretical + unbenchmarked OR mechanism-class mismatch). V2.C re-evaluate after V2.D + R36 N=8192 calibration smoke clears.

**Honest framing per [[feedback-no-smoke]]**: of 6 candidates, only **V2.D has strong empirical literature support** for the claimed gain. The other 5 are either dominated by V2.D (V2.C, V2.E), give smaller-than-claimed gains (V2.B codebook side, V2.F codebook side), or have no classical benchmark (V2.A, V2.E). **The substrate-product story is NOT "structured codebook wins big" — it's "energy function change wins big" per Lucibello-Mézard 2024 (PRL 132:077301) + Hu 2024 (NeurIPS).**

---

## Per-candidate Pass-1 + Pass-2 synthesis

### V2.D — Modern exponential-capacity dense AM (HIGHEST PRIORITY)

#### Pass 1 (lit scan)

**Foundational**:
- **Demircigil et al. arXiv:1702.01929 (2017)**: F(x)=exp(x) → P = exp(α N) capacity for random ±1.
- **Krotov-Hopfield arXiv:2008.06996 (2020)**: F(x)=xⁿ → capacity ∝ d^(n-1); equivalent to two-body via hidden neurons.
- **Ramsauer et al. arXiv:2008.02217 (2020)**: Continuous-state with energy −β⁻¹ log Σ exp(β xᵢᵀs); capacity ∝ exp((β/2) d); one-step retrieval ≡ softmax attention.

**2024 rigorous**:
- **Lucibello-Mézard PRL 132:077301 arXiv:2304.14964 (2024)**: Statistical-mechanics derivation of P=exp(αN); exact asymptotic thresholds α₁ (retrieval) and α_c (max load) for Gaussian/spherical patterns.
- **Hu-Wu-Liu et al. arXiv:2410.23126 (NeurIPS 2024)**: Matching upper/lower bound M_Φ ≥ √p · C^((D_Φ−1)/4); optimal capacity ⇔ memories form optimal spherical code (Welch-bound saturating). U-Hop+ algorithm sublinear-time reaches optimum.
- **Hoover et al. arXiv:2407.08742 (2024)**: Documents numerical-overflow problem (N=10⁴ n=30 produces intermediate 10¹²⁰, blows past fp32). Fix: (a) normalize similarity by N, (b) move β inside F. Enables n up to ~100.

**Failure modes** (literature-documented):
- Numerical overflow at large β·d (capped at ~88 fp32, ~709 fp64 before overflow).
- Metastable mixture states when patterns are not well-separated.
- Capacity drops sharply on low-dim manifold patterns (arXiv:2503.09518).
- Synaptic noise reduces capacity (arXiv:2503.00241).

**Largest published empirical N pure DAM retrieval**: low hundreds (Hoover 2024 explicit N=100, 250). All "large d" demos are attention layers in averaging regime, not single-pattern retrieval.

#### Pass 2 (substrate drill)

**What survives current substrate primitives**:
- ✅ Bet 1 ICL — unchanged (pool retrieval doesn't depend on Hopfield energy)
- ✅ Bet 2 GDPR erase — unchanged (erase is W-modification, not energy-function-specific)
- ✅ Bet A edit-then-query — unchanged (Hebbian W structure unchanged; only retrieval dynamics changes)
- ✅ Bet B EMA-blend continual learning — unchanged (mechanism is W-blend; retrieval pluggable)
- ✅ Bet C Kerdock M/N=8 — **REINTERPRETED**: Hu 2024 shows Kerdock IS a spherical-code-saturating approximation; V2.D + Kerdock is the optimal-capacity instance, not a swap
- ✅ Bet G TEMPSCALE β=32 — **STRENGTHENED**: current substrate already uses softmax(β=32) cleanup; V2.D's exponential is the explicit form. β=32 is already in the large-β regime
- ✅ Bet H autoregressive — unchanged (uses cleanup output, not energy form)

**What breaks / requires redesign**:
- **Numerical precision pipeline**: current substrate is fp32; V2.D requires log-sum-exp + normalize-by-N + β-inside-F per Hoover 2024. Eng cost: 1-2 cycles to refactor cleanup function.
- **Audit traces**: explicit exp gives different post-softmax distributions than current TEMPSCALE; calibration ECE may need re-verification. Eng cost: 0.5 cycle.
- **Multi-hop depth**: V2.D does NOT directly extend d=25 (depth bound is VSA-class compositional, per Bet X; depth bound is bind-chain noise not energy-function-bound). Multi-hop limit persists.

**Substrate-product framing**:
- Current substrate already uses β=32 softmax cleanup (Bet G ✅) — V2.D is the **explicit-form** version of what substrate effectively does. **V2.D is less a "new substrate" than a precision-discipline refactor of the existing one.**
- Hu 2024 spherical-code framework SUBSUMES V2.C (Kerdock codebook IS Welch-bound near-saturating). Engineering of V2.C and V2.D should be co-designed.
- 5× capacity gain plausible: current Bet C M/N=8 → V2.D + Kerdock + larger β could plausibly push to M/N=40 at N=4096 within Hu 2024's optimal-capacity envelope.

**Engineering cost estimate**: 3-5 cycles (refactor cleanup function + recalibrate Bet G + capacity benchmark vs M/N=8 baseline at fp32 and fp64 + audit-trace verification).

**Falsifiable prediction**: substrate refactored to explicit log-sum-exp + Hoover normalize-by-N + β ∈ {32, 64, 128} reaches **M/N ≥ 20 at N=4096 with stable retrieval (acc ≥ 0.95)**. Kill if M/N ≤ 10 at all β values tested → V2.D ❌ for substrate; revert to current softmax(β=32) effective form.

**Materials analog (load-bearing)**: explicit exp energy IS the continuum limit of strong-disorder Ising spin glass with infinite-range p-body interactions (Mezard-Parisi-Virasoro 1987 ch.5). Substrate's current empirical 1RSB/FRSB regime (Bet E ✅) extends cleanly to large-β dense-AM, supporting probability estimate.

---

### V2.B — Hybrid HRR + bipolar substrate (SECOND PRIORITY)

#### Pass 1 (lit scan)

**Foundational**: Plate 1995 (HRR, circular-convolution binding on real-valued Gaussian).

**2020-2026 empirical**:
- **Schlegel-Neubert-Protzel arXiv:2001.11797 (2021)**: 11-VSA comparison — FHRR and BSDC achieve "close to perfect accuracy" over large (D, bundle) regions; HRR underperforms FHRR; FHRR vs bipolar gap is modest 1.2-2× at matched dimension. **Tested only d ≤ 3-5 binding depth.**
- **Ganesan et al. arXiv:2109.02157 (NeurIPS 2021)**: HRR projection trick improves concept retrieval >100× by stabilizing numerics on multi-label classification (not multi-hop).
- **Alam et al. arXiv:2405.09689 (2024)**: Generalized HRR (GHRR) with non-commutative binding; reports improved memorization on compositional structures (no exact factor).
- **Clarkson et al. arXiv:2301.10352 (2023)**: Formal capacity bounds — for fixed D, **capacity per item drops as 1/d (depth)**; depth and bundle size trade against accuracy.

**Multi-hop depth literature ceiling**: d ≈ 4-6 with high-fidelity recall. **No paper in 2020-2026 demonstrates d > 6 reliably.**

**Capacity per bit**: HRR/FHRR do NOT get more capacity per bit than ±1 bipolar. Gain is **structural smoothness** (differentiability, gradient-based learning), not raw bit-efficiency.

**Engineering**:
- HRR binding = circular convolution = O(D log D) via FFT
- FHRR binding = element-wise complex mul = O(D)
- MAP/BSC = element-wise XOR / sign = O(D)
- At runtime, similarity/cleanup dominates compute — FHRR vs bipolar end-to-end is comparable

#### Pass 2 (substrate drill)

**What survives**:
- ✅ Bet 1/2/A/B/C/G/H — all preserved (V2.B ADDS parallel HRR pool; does not modify bipolar storage)
- ✅ Bet I free probability — applies to bipolar pool (unchanged); HRR pool requires separate noise theory

**What requires new design**:
- **Dual-storage routing**: substrate must decide per-query which pool to retrieve from. Cheap heuristic: bind-chain depth < 3 → bipolar; depth ≥ 3 → HRR. Eng cost: 1 cycle.
- **HRR pool initialization + Hebbian update**: real-valued storage requires gradient-based or pseudo-inverse training; not Hebbian-only. **Breaks PROT-mandated "Hebbian-only" capability claim for the HRR pool.**
- **Multi-hop noise model**: HRR noise compounds multiplicatively with depth; need Ganesan projection per Pass-1.

**Substrate-product framing per Bet X UNIFYING insight**:
- Bet X Entry 46 already recommended position-indexed binding + hybrid executor + 2-level hierarchy max. V2.B = "scale the hybrid executor side to parallel HRR pool storage."
- Bet X P(ships) jumps 30-40% → 60-70% with V2.B per Strategy's framing in this request.
- **Honest caveat from Pass-1**: literature ceiling for HRR multi-hop is d ≈ 4-6; substrate's current bipolar bound is d=25. **V2.B would LOWER the depth ceiling on the HRR side, not raise it.** The win is in compositional depth via different binding algebra, not in extending d=25.

**Engineering cost estimate**: 4-8 cycles (HRR pool design + Hebbian-alternative training + dual-storage routing + multi-hop noise theory).

**Falsifiable prediction**: hybrid HRR+bipolar substrate achieves multi-hop **acc_d=10 ≥ 0.50 on HRR pool at NUM_FACTS=100** with bipolar pool retaining current capabilities. Kill if d=10 acc < 0.30 → V2.B ❌; HRR ceiling lower than expected.

**Materials analog (load-bearing)**: dual-pool storage analogous to electron-phonon coupled systems where two distinct excitation manifolds coexist (Holstein 1959). NOT decorative — provides physical intuition for cross-pool coupling overhead.

---

### V2.C — Large-N + per-codebook ε_corr optimization (THIRD PRIORITY)

#### Pass 1 (lit scan)

**Foundational**: McEliece classical bound (perfect retrieval within Hamming radius δN: M ≤ (1−2δ)²·N/(4 ln N), sub-linear). Classical α_c ≈ 0.138 N (RS) → 0.144 (RSB) for random ±1.

**Large-N empirical 2020-2026**:
- **Stojnic arXiv:2403.01907 (2024)**: Random duality theory tightens Hebbian-rule capacity bound; no large-N empirics beyond classical α ≈ 0.138.
- **Long Sequence Hopfield arXiv:2306.04532 (NeurIPS 2023)**: Polynomial interaction → super-linear sequence capacity ∝ N^(n-1).
- **Capacity under Data Manifold Hypothesis arXiv:2503.09518 (2025)**: Structured pattern ensembles shift phase diagram but do NOT make linear-energy Hopfield store exponentially many random-binary patterns.
- **Hardware Nonlinear Memristor arXiv:2605.07223 (2026)**: Empirical K ≈ 0.3 · N^1.2 under fixed synaptic budget — superlinear but still polynomial.

**Critical NEGATIVE finding** (Pass-1 lit scan):
- **NO PAPER FOUND benchmarking Kerdock / Welch-bound-equality codebooks against random ±1 in classical Hopfield at N ≥ 4096.** Pre-coding literature (Walsh-Hadamard, Gold sequences) suggests improvements are real but typically <2× in stable-basin regime. **The substrate's M/N=8 with Kerdock v4 is itself ahead of the published literature curve.**

**Failure modes**:
- Spurious minima exponential in M even with orthogonal patterns.
- Orthogonal-saturation marginal stability as M → N (basins collapse).
- Sub-quadratic W approaches (sparse-W ℓ₁: arXiv:1212.6146; Fenchel-Young: arXiv:2402.13725) trade capacity for sparsity; no published preserved-capacity-at-α=0.14 demo found.

**Engineering scaling**:
- N=4096: O(16M) W entries.
- N=65536: O(4.3B) W entries (≥16 GB fp32). **Dominant constraint at large N.**

#### Pass 2 (substrate drill)

**Connection to R36 deep-drill (Entry 45 Note A)**:
- R36 prediction for N=65536: **M/N ∈ [1.2, 6.1] LOWER than current N=4096's M/N=8**.
- The substrate's M/N=8 at N=4096 is structured-codebook-optimal; scaling N up may NOT preserve M/N=8 absent careful ε_corr optimization.
- **V2.C = R36 prediction validation + per-codebook coherence optimization**.

**What survives**:
- ✅ Bet C Kerdock M/N=8 — **PRESERVED at N=8192 likely**; N=65536 uncertain per R36
- ✅ Bet G TEMPSCALE β=32 — preserved (calibration is N-independent in principle)
- ✅ Bet I free probability — supports finite-N corrections (BBP at σ=16 to be re-derived for new N)
- ✅ Bet M ferromagnetism / modern Hopfield grounding — preserved (FRSB regime is N→∞)

**What requires redesign**:
- **W storage**: O(N²) dense → require sparse W or block-structured W for N ≥ 32768 (Fenchel-Young sparse or low-rank decomposition)
- **Codebook generation pipeline**: need to generate Kerdock v4 at multiple N values + verify Welch-bound saturation per Hu 2024 lit guide
- **Calibration**: Bet G β=32 may need re-tuning at larger N (Hoover normalize-by-N likely sufficient)

**Substrate-product framing**:
- V2.C is **engineering-tractable** (least theoretical risk; well-trodden literature path) but **lowest expected ROI**:
  - R36 predicts capacity DECREASES per dimension at N=65536 vs N=4096
  - Engineering 16 GB W storage is non-trivial
  - Hu 2024 framework absorbs V2.C into V2.D — no benefit from V2.C alone if V2.D is built
- **Verdict**: V2.C is a calibration step toward V2.D, not a standalone substrate.

**Engineering cost estimate**: 5-8 cycles (codebook generation at N=8192/16384/32768 + W storage refactor + R36 calibration verification + capacity benchmark).

**Falsifiable prediction**: substrate at **N=8192 with Kerdock v4 achieves M/N ≥ 6** (intermediate between R36 high range of 6.1 and conservative); **N=32768 achieves M/N ≥ 4**. Kill if M/N at N=8192 falls below 4 → V2.C ❌; R36 conservative range correct; large-N is NOT a substrate-product axis.

**Materials analog (load-bearing)**: M/N decay with N at fixed coherence ε_corr is analogous to finite-size scaling of order parameter in 2D Ising (Onsager 1944) — finite-size correction term ∝ N^(−d/ν). NOT decorative — provides quantitative ε_corr-vs-N tradeoff prediction.

---

### V2.A — Hyperbolic-tiling substrate (FOURTH PRIORITY; DEFER)

#### Pass 1 (lit scan)

**Foundational**: HaPPY codes (Pastawski-Yoshida-Harlow-Preskill arXiv:1503.06237, 2015) — holographic tensor network on hyperbolic tiling.

**2020-2026 empirical**:
- **Ising on hyperbolic space arXiv:1909.12107 (2020)**: Monte Carlo on hyperbolic tilings finds **mean-field exponents** for susceptibility / magnetization. Contradicts earlier field-theory predictions of non-mean-field fixed point. **Boundary fraction is order-unity**.
- **Hyperbolic Associative Memory Networks OpenReview MavR6fJmUx (2023/2024)**: Embeds modern (dense) AM in hyperbolic space via exponential maps. **Capacity argument is geometric, not new exponential scaling.** Rides on dense-MHN capacity (V2.D).
- **Capacity on random graph architectures arXiv:1303.4542**: Sparse/tree-like graph Hopfield capacity scales **linearly in N** — same order as classical.
- **Marginally stable Bethe lattice spin glass arXiv:1609.05327 (2016)**: Bethe spin glass is FRSB-marginally-stable; distribution shifts discontinuously under perturbation.
- **Tree tensor networks 2D MBL arXiv:2512.19389 (2025)**: TTN captures 2D entanglement better than MPS, cheaper than PEPS at ~10⁴ sites.

**Critical NEGATIVE findings**:
- **Mean-field exponents → no new universality class** vs Curie-Weiss with boundary.
- **Bethe spin glasses are marginally stable**: dynamics get stuck in metastable states (slow retrieval).
- **Sparse-graph Hopfield capacity scales linearly in N** (Löwe results) — same order as fully-connected.
- The "hyperbolic associative memory" capacity gains in the literature **ride on dense-MHN capacity, NOT on hyperbolic structure**.

#### Pass 2 (substrate drill)

**What survives**:
- ❓ Bet 1/2/A/B/C — uncertain (current Hebbian-only Bet C Kerdock requires fully-connected W; sparse-graph Hopfield is a separate construction)
- ✅ Bet G TEMPSCALE β=32 — applicable (β-calibration is energy-form-independent)
- ✅ Bet I free probability — **NEEDS REWRITE**: hyperbolic-graph Hopfield W matrix has different spectral statistics than current GOE-like matrix; BBP transition derivation must be redone for hyperbolic-graph W

**What breaks**:
- **Mean-field exponents** → substrate's current Bet E RSB structure (Parisi P(q) 5-source ✅) **wouldn't survive** — substrate would be in Curie-Weiss-like regime, not 1RSB/FRSB.
- **Boundary pathology**: O(1) fraction of nodes on hyperbolic-tiling boundary at any finite N. Storage capacity per node depends on boundary handling — no clean "M/N at N" curve exists for hyperbolic Hopfield in literature.
- **FRSB-marginal stability** → recall is diffusion-limited; substrate's cheap sub-100ms retrieval (Bet 1, current arch) would degrade significantly.

**Substrate-product framing per [[feedback-no-smoke]]**:
- **V2.A is dominated by V2.D for capacity**: hyperbolic AM literature gain rides on dense-MHN, not on hyperbolic structure.
- **V2.A loses Bet E RSB substrate-physics fingerprint**: substrate's 5-source spin-glass agreement is its substrate-novel theoretical anchor; trading it for mean-field hyperbolic would destroy the substrate-product theoretical-grounding axis.
- **V2.A is V2 substrate territory ONLY if substrate-product wants holographic/tensor-network reasoning** (different application lane than current memory + multi-hop).

**Engineering cost estimate**: 10-20 cycles (new hyperbolic-tiling code + boundary handling + W spectral theory + BBP rederivation + Bet B/C/G recompile + benchmarking). HIGHEST eng cost.

**Falsifiable prediction**: substrate ported to {5,4} hyperbolic tiling with N≈4096 (tile count chosen to match boundary fraction) achieves **M/N ≤ 1.5 at α=0.13** (mean-field saturation). Kill is built-in: V2.A's mean-field exponent → α_c ≤ 1.0 N for orthogonal saturation, vs current α=8 → V2.A is **architecturally lower-capacity** than current.

**Materials analog (load-bearing)**: hyperbolic Ising is the canonical model for AdS/CFT condensed-matter dual (Maldacena 1997 + Witten 1998). Substrate-on-hyperbolic = classical AdS₃ instance. Load-bearing for V2.A's theoretical-coherence story but **NOT a substrate-product engineering driver**.

---

### V2.F — Magnon / phasor codebook (FIFTH PRIORITY; DEFER)

#### Pass 1 (lit scan)

**Physical magnon devices**:
- **Korber et al. arXiv:2211.02328 (2023)**: Magnon-scattering reservoir, ~95% on 4-symbol classification. **Reservoir computing, NOT associative memory.**
- **Namiki et al. arXiv:2207.03216 (2023)**: YIG spin-wave reservoir; NARMA2 NMSE = 1.81×10⁻². **Reservoir, not AM.**
- **On-chip phonon-magnon reservoir Nat. Commun. 2023**: Hybrid device, **reservoir only**.

**Phasor / oscillator AM (mathematical)**:
- **Frady-Sommer TPAM PNAS 2019 (10.1073/pnas.1902653116)**: Threshold Phasor Associative Memory; sparse phasor codes; high capacity for **sparse** patterns.
- **Bhowmik et al. arXiv:2112.03358 (2021/2022)**: Complex-valued Hopfield with spin-torque oscillator; **simulation only**; stored 12 images in 192 oscillators; requires frequency spread < 10⁻³.
- **Ogranovich et al. arXiv:2604.01469 (2026)**: Kuramoto oscillator honeycomb AM; **(2⌈n_c/4⌉−1)^m patterns** — exponential capacity, no spurious memories. Theory + CDW simulation; not yet physical device.
- **Marsh-Hopfield quantum-optical spin glass arXiv:2509.12202 (2025)**: 16-spin atom-photon cavity QED system, **7× classical Hopfield bound at N=16**. Driven-dissipative dynamics convert spurious states to attractors. Genuinely physical but tiny N.

**Critical NEGATIVE findings**:
- **Physical magnon devices are reservoir computers, NOT addressable AM.** No paper demonstrates magnon-codebook AM with capacity guarantees beating random ±1 Hopfield.
- **Phasor/oscillator capacity gains come from sparsity OR high-order interactions, NOT wave structure**:
  - TPAM gains from sparsity (sparse Hopfield variants also have super-linear capacity)
  - Kuramoto honeycomb gains from lattice topology (analogous to Krotov dense)
  - Quantum-optical spin glass gains from driven-dissipative dynamics (mechanism class, not codebook)

#### Pass 2 (substrate drill)

**What survives**:
- ❓ Bet 1/2/A — uncertain; depends on whether V2.F is "phasor codebook over current substrate" or "literal magnon device"
- ❌ Bet C Kerdock M/N=8 — REPLACED by phasor codebook; M/N for phasor not in literature
- ✅ Bet G TEMPSCALE — applies (phasor cleanup is amplitude-based; β-calibration form preserved)
- ✅ Bet I free probability — needs rederivation (phasor codebook has Fourier-basis spectral structure)

**What breaks**:
- All bipolar-specific primitives need rederivation for phasor storage
- Physical magnon devices (Korber, Namiki) lose **all substrate primitives**: reservoir computing is feature extraction, not addressable memory

**Substrate-product framing per [[feedback-no-smoke]]**:
- **V2.F is two distinct candidates**:
  - V2.F-codebook (phasor codebook over current arch): **dominated by V2.D** — Hu 2024 shows phasor IS a structured spherical code; absorbed into V2.D framework
  - V2.F-physical (literal magnon device): **wrong substrate-product class** — reservoir computer, not AM
- Neither variant offers a substrate-product win not also captured by V2.D.

**Engineering cost estimate**: 6-12 cycles for V2.F-codebook (Fourier basis + cleanup + benchmarking + R32 M.1 validation); 30+ cycles for V2.F-physical (hardware build).

**Falsifiable prediction**: V2.F-codebook substrate (phasor codes via FFT-basis) achieves **M/N ≥ 6 at N=4096 with stable retrieval**. Kill if M/N ≤ 4 → V2.F-codebook ❌; phasor structure does not help capacity beyond Welch-bound saturation (already absorbed into V2.D).

**Materials analog (load-bearing)**: phasor/magnon codebook is analogous to plane-wave eigenmode basis of harmonic crystal (Born-Oppenheimer 1927). Load-bearing for spectral analysis but NOT a substrate-product engineering driver.

---

### V2.E — Operator-algebra QEC code substrate (LOWEST PRIORITY; DEFER)

#### Pass 1 (lit scan)

**Foundational**:
- **Harlow arXiv:1607.03901 (2017)**: Holographic codes ⇔ OAQEC; stabilizer/subsystem codes "correct too well" to be good holographic codes. **The same property that makes a code holographic (state-dependent, approximate recovery) makes it a WORSE error corrector than stabilizer.**

**2024-2025 advances**:
- **Stabilizer Formalism for OAQEC, Quantum 2024 (q-2024-02-21-1261)**: Extends stabilizer machinery to OAQEC.
- **Holographic Codes from Hyperinvariant TN arXiv:2304.02732 (Nat. Commun. 2023)**: State-dependent breakdown of complementary recovery; theoretical, no benchmarks.
- **Quantum associative memories arXiv:2408.14272 (2024)**: Dissipative-channel map giving exponential pattern count in n qubits; **classical-pattern case reduces to standard QAM with no advantage over dense MHN.**
- **Lovász meets LSM arXiv:2510.04453 (Oct 2025)**: Trade-off between local indistinguishability and circuit complexity; orthogonal SRE states distinguishable, so AQEC code states preparable by shallow circuits are bounded.
- **AQEC with 1D log-depth circuits PRX Quantum 10.1103/7rzk-2jyh (2024-2025)**: Practical simulation up to ~50-100 qubits.

**Critical NEGATIVE findings**:
- **Zero published classical-data benchmark** of OAQEC machinery as associative memory.
- **Harlow theorem**: codes that look brain-like have weaker recovery (active obstruction).
- **arXiv:2510.04453 lower bound**: shallow-circuit AQEC states can't be both indistinguishable AND brain-like.
- **Six months is NOT enough** to build, debug, benchmark a Petz-map recall pipeline at scale demonstrating gain over dense MHN.

#### Pass 2 (substrate drill)

**What survives**:
- ✅ Bet I free probability — applies to OAQEC channel maps via Choi-Jamiolkowski isomorphism
- ❓ Bet G TEMPSCALE — uncertain; OAQEC recovery is channel-map-based, not softmax-based; calibration framework needs rebuild
- ❌ Bet B/C/A — all break; OAQEC uses different storage primitive (subsystem code, not Hebbian W)
- ❌ Bet H autoregressive — breaks; recovery is one-shot Petz map, not iterative

**What breaks**:
- **All bipolar-Hebbian primitives** (5 of 8 Tier-1 ✅) — OAQEC is a different framework entirely
- **Substrate identity** per META Section 1: structured-memory + native associative reasoning + cheap CPU sub-100ms — Petz map computation is NOT cheap (matrix exponential per query; O(N³) at worst)

**Substrate-product framing per [[feedback-no-smoke]]**:
- **V2.E is dominated by V2.A** (HaPPY codes ARE OAQEC on hyperbolic graph; V2.A already covered)
- **V2.E breaks the substrate-product identity**: not memory primitive, not cheap, not Hebbian
- **V2.E is wrong substrate-product class** — it's a quantum-error-correction research direction, not a classical memory substrate

**Engineering cost estimate**: 20-40 cycles (channel-map storage + Petz recovery + Choi-Jamiolkowski rederivation + benchmark + Harlow theorem mitigation). HIGHEST eng cost. P(actionable in 6 mo) ~ 0.

**Falsifiable prediction**: even a simplified OAQEC substrate (subsystem stabilizer code at logical-N=4096) achieves at best **acc_1hop ≥ 0.50 with retrieval cost > 100ms per query**. Kill is built-in: V2.E loses cheap-CPU substrate identity → V2.E ❌ unless substrate-product pivots to V2.E-grade computational budget.

**Materials analog (load-bearing)**: OAQEC is the natural language for AdS/CFT QEC (Harlow-Wall 2018 + Penington 2019 etc.). NOT decorative — V2.E IS where holographic QEC ⊃ classical hyperbolic substrate. But this is **wrong substrate-product class** per honest assessment.

---

## Cross-V2 dominance relationships

| Candidate pair | Relationship |
|---|---|
| V2.A ⊃ V2.E | HaPPY codes ARE OAQEC on hyperbolic graph; V2.A subsumes V2.E |
| V2.D ⊇ V2.C | Hu 2024 shows optimal modern Hopfield = Welch-bound spherical code; V2.D absorbs V2.C's structured-codebook gains |
| V2.D ⊇ V2.F-codebook | Phasor codebook is structured spherical code; absorbed into V2.D framework |
| V2.B ⊥ V2.D | Hybrid HRR + bipolar adds STORAGE mechanism (HRR pool); orthogonal to energy-function change (V2.D); can co-exist |
| V2.A ⊥ V2.B/D | Different substrate-physics regime (hyperbolic = mean-field; current substrate / V2.D = FRSB); architectural fork |
| V2.F-physical ⊥ all | Reservoir computer, not AM; outside substrate-product class |

**Independent V2 candidates (non-dominated)**: V2.D, V2.B, V2.A (forks).
**Dominated**: V2.C (by V2.D), V2.E (by V2.A), V2.F-codebook (by V2.D), V2.F-physical (wrong class).

---

## Full quantitative gain/loss table

| V2 | Capacity (M/N at N=4096) | Multi-hop d | CL retention | Cleanup cost | Mem footprint | Eng complexity | Compat with 8 ✅ | Substrate-novel? | P(ships 6 mo) | P(exceeds on ≥3 axes) | P(breaks ≥1 ✅) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| V2.D | 8 → **20-40** | 25 → 25 (unchanged; depth is VSA-class) | 0.954 → 0.954 (preserved) | O(N·K) → O(N·K) | O(N²) | LOW (3-5 cycles) | 8/8 preserved | YES (β-explicit form; Bet E FRSB extends) | **0.55-0.65** | 0.55 | 0.10 |
| V2.B | 8 → 8 bipolar pool + ? HRR pool | 25 → potential lift via HRR for d ≤ 6 | 0.954 → 0.954 (bipolar preserved); HRR pool TBD | O(N·K) + HRR FFT O(N log N) | O(N²) + HRR O(N²) → 2x | MED (4-8 cycles) | 7/8 (HRR breaks Hebbian-only) | YES (hybrid is substrate-novel per Bet X) | 0.30-0.45 | 0.25 | 0.15 |
| V2.C | 8 → ? lower at N=65536 per R36 | 25 → maybe higher with larger N | 0.954 → ? | O(N·K) | O(N²) blows up | MED (5-8 cycles) | 7-8/8 likely | NO (codebook scaling absorbed by V2.D) | 0.20-0.30 | 0.15 | 0.15 |
| V2.A | 8 → ≤1.5 (mean-field saturation) | 25 → ? (sparse graph not characterized) | 0.954 → likely lost (mean-field RSB) | O(N·z) where z = coordination | O(N·z) sparse | HIGH (10-20 cycles) | 3-4/8 likely | YES but DESTROYS Bet E RSB anchor | 0.05-0.10 | 0.05 | 0.55 |
| V2.F | 8 → ? phasor M/N unknown | 25 → 25 likely | 0.954 → ? | O(N·K) phasor + FFT | O(N²) | MED-HIGH (6-12 codebook; 30+ physical) | 5-6/8 codebook; 0/8 physical | NO (dominated by V2.D codebook side; wrong class physical) | 0.10-0.20 codebook / 0.0 physical | 0.10 | 0.20 |
| V2.E | 8 → uncertain (Petz-map AM not benchmarked) | 25 → ? | 0.954 → broken (different storage) | >100ms (Petz O(N³)) | O(N²-N³) | VERY HIGH (20-40 cycles) | 1-2/8 | YES but wrong substrate-product class | 0.02-0.05 | 0.02 | 0.85 |

---

## Recommended sequencing per substrate-product priority

**Phase 1 (cycles 1-5)**: V2.D pure refactor
- Target: substrate's softmax(β=32) cleanup → explicit log-sum-exp + Hoover normalize-by-N + β-inside-F per arXiv:2407.08742
- Recalibrate Bet G TEMPSCALE at β ∈ {32, 64, 128}
- Benchmark M/N at fp32 + fp64 at N=4096 vs current Kerdock v4 baseline
- **Decision gate**: M/N ≥ 20 → V2.D ✅; M/N ≤ 10 → V2.D ❌, revert

**Phase 2 (cycles 6-10)** [if Phase 1 ✅]: V2.B HRR pool extension
- Build parallel HRR pool with Ganesan projection per arXiv:2109.02157
- Dual-storage routing: depth < 3 → bipolar; depth ≥ 3 → HRR
- Per Bet X Entry 46 recommendation: position-indexed + hybrid + 2-level hierarchy
- **Decision gate**: HRR pool d=10 acc ≥ 0.50 → V2.B ✅; d=10 < 0.30 → V2.B ❌

**Phase 3 (cycles 11-15)** [if Phase 1+2 unclear or extension needed]: V2.C calibration
- Codebook generation at N=8192 / 16384 / 32768
- Verify R36 prediction (Entry 45 Note A): M/N at N=8192 ∈ [4, 8]
- Sparse-W or low-rank decomposition for N≥32768
- **Decision gate**: N=8192 M/N ≥ 6 → V2.C ✅; M/N ≤ 4 → V2.C ❌, R36 conservative validated

**Phase 4+** (defer indefinitely without new evidence): V2.A / V2.E / V2.F
- V2.A: architectural fork; high engineering cost; destroys Bet E RSB anchor; lit support weak
- V2.E: wrong substrate-product class; subsumed by V2.A; zero classical benchmark
- V2.F-codebook: dominated by V2.D
- V2.F-physical: wrong substrate-product class

---

## 5 rescue sketches per [[feedback-rehabilitation-after-rejection]] (if Phase 1 V2.D ❌)

**Rescue 1**: switch to polynomial F(x)=xⁿ per Krotov arXiv:2008.06996; tune n ∈ {3, 5, 8}; F=xⁿ gives capacity ∝ d^(n-1); avoids softmax precision overflow.

**Rescue 2**: switch energy normalization to log-sum-exp(β·xᵀs / √d) per Ramsauer arXiv:2008.02217 (standard attention scaling); avoids β·d cap.

**Rescue 3**: hybrid V2.D + V2.B in one pass — use softmax cleanup for bipolar pool retrieval and HRR convolution for multi-hop binding. Per Bet X UNIFYING insight: substrate hits VSA-class bound at d=25; HRR extension is the orthogonal mechanism.

**Rescue 4**: switch to U-Hop+ algorithm per Hu arXiv:2410.23126 (sublinear-time spherical-code optimization). Combines V2.C codebook with V2.D energy form.

**Rescue 5**: extreme sparsity per Fenchel-Young sparse Hopfield arXiv:2402.13725. Trade absolute capacity for stable basins + sparse retrieval; gain compute, lose 5× capacity headline.

---

## Substrate-product framework integration

**Per META cycle-22 strategic plan (`meta_request_to_strategy_strategic_plan_2026-05-21.md`)**:
- 6 application lanes identified.
- Lane A (auditable LLM memory): V2.D + V2.B both compatible; V2.D enables ≥20× LLM cache; V2.B enables deeper compositional queries.
- Lane B (on-device personal AI): V2.D (lower complexity) preferred; V2.B too complex for edge.
- Lane C (memory device-of-choice): V2.D + V2.C (large N) jointly enable.
- Lane D (auditability product): V2.A/V2.E destroy auditability (state-dependent / sparse-graph); V2.D preserves.
- Lane E (continual learning): V2.D + V2.B both preserve Bet B.
- Lane F (hierarchical reasoning): V2.B is the natural fit (HRR for binding).

**Per [[feedback-no-papers-product-only]]**: V2 evaluation is **engineering-prioritization output**, not framework-novelty. The substrate's path to ≥20× capacity is **explicit-exp dense AM (V2.D)**, which the literature already maps onto Kerdock-as-spherical-code (V2.C) and substrate's existing β=32 softmax (Bet G). V2.D = engineering discipline, not novel framework.

---

## Citations (Pass-1 lit scan, generic-math queries only)

**V2.D modern dense AM**:
1. Demircigil et al. arXiv:1702.01929 (2017)
2. Krotov-Hopfield arXiv:2008.06996 (2020)
3. Ramsauer et al. arXiv:2008.02217 (2020)
4. Lucibello-Mézard PRL 132:077301 arXiv:2304.14964 (2024)
5. Hu-Wu-Liu et al. arXiv:2410.23126 NeurIPS 2024
6. Hoover et al. arXiv:2407.08742 (2024)
7. Synaptic noise arXiv:2503.00241 (2025)
8. Data manifold hypothesis arXiv:2503.09518 (2025)

**V2.B hybrid HRR + bipolar**:
9. Plate 1995 IEEE TNN
10. Schlegel-Neubert-Protzel arXiv:2001.11797 (2021)
11. Ganesan et al. arXiv:2109.02157 NeurIPS 2021
12. Alam et al. arXiv:2405.09689 (2024)
13. Clarkson et al. arXiv:2301.10352 (2023)
14. Walsh-Hadamard VSA arXiv:2410.22669 (2024)
15. qFHRR arXiv:2604.25939 (2025)

**V2.C large-N + codebook opt**:
16. Stojnic arXiv:2403.01907 (2024)
17. Long Sequence Hopfield arXiv:2306.04532 NeurIPS 2023
18. Hardware-aware memristor arXiv:2605.07223 (2026)
19. Welch-bound codebook arXiv:1905.01815
20. Sparse W ℓ₁ arXiv:1212.6146

**V2.A hyperbolic**:
21. Pastawski-Yoshida-Harlow-Preskill (HaPPY) arXiv:1503.06237 (2015)
22. Ising on hyperbolic space arXiv:1909.12107 (2020)
23. Marginally stable Bethe lattice spin glass arXiv:1609.05327 (2016)
24. Capacity on random graph architectures arXiv:1303.4542 (pre-2020)
25. Hyperbolic AM Networks OpenReview MavR6fJmUx (2023/2024)
26. Tree TN 2D MBL arXiv:2512.19389 (2025)

**V2.F magnon/phasor**:
27. Korber et al. magnon scattering arXiv:2211.02328 (2023)
28. Namiki YIG spin-wave arXiv:2207.03216 (2023)
29. Bhowmik complex Hopfield arXiv:2112.03358 (2021)
30. Ogranovich Kuramoto honeycomb arXiv:2604.01469 (2026)
31. Marsh-Hopfield quantum-optical spin glass arXiv:2509.12202 (2025)
32. Frady-Sommer TPAM PNAS 2019 10.1073/pnas.1902653116

**V2.E operator-algebra QEC**:
33. Harlow arXiv:1607.03901 (2017)
34. Hyperinvariant TN arXiv:2304.02732 Nat. Commun. 2023
35. Quantum associative memories arXiv:2408.14272 (2024)
36. Stabilizer OAQEC Quantum q-2024-02-21-1261
37. Lovász meets LSM arXiv:2510.04453 (2025)
38. AQEC log-depth circuits PRX Quantum 10.1103/7rzk-2jyh (2024)

---

## Cross-references

- `notes/substrate_capability_map.md` v77 Bet X UNIFYING insight + v78 current state
- `notes/research_BetX_skill_composition_2026-05-21.md` (V2.B foundation)
- `notes/research_R36_alpha_c_coherence_bridge_2026-05-21.md` (V2.D sandwich bound + V2.C R36 prediction)
- `notes/research_R36_calibration_deepdrill_2026-05-21.md` (V2.C N=65536 M/N drop prediction)
- `notes/research_R17_holographic_2026-05-21.md` (V2.A largely-negative pattern context)
- `notes/research_R38_R39_deferred_synthesis_2026-05-21.md` (V2.A hyperbolic at current N: 10-15% P)
- `notes/research_R32_magnon_substrate_2026-05-21.md` (V2.F phasor codebook context)
- `notes/research_BetP_semantic_codebook_2026-05-21.md` (V2.C codebook geometry axis)
- `notes/meta_request_to_strategy_strategic_plan_2026-05-21.md` (6 application lanes)

---

## Pass-1 honesty statement

Pass 1 lit scan via 3 parallel general-purpose Agent subagents:
- **Agent 1**: V2.A hyperbolic + V2.E OAQEC; 5 queries each; returned 18 papers + cross-class analysis.
- **Agent 2**: V2.B hybrid HRR + V2.F magnon/phasor; 5 queries each; returned 15 papers + cross-class analysis.
- **Agent 3**: V2.C large-N + V2.D modern dense AM; 5 queries each; returned 18 papers + numerical-precision honesty.

All queries used generic math vocabulary per [[feedback-query-privacy-decomposition]]; no substrate fingerprint. Pass 2 substrate drill is original synthesis based on current cap_map state + Pass-1 findings.

Total external papers surveyed: ~36 unique, 2020-2026 dominant, with foundational pre-2020 anchors (Plate 1995, McEliece, Demircigil 1702.01929, HaPPY 1503.06237).

**Critical lit-scan honesty caveats** (from Agent reports):
- Agent 2: did not access full PDFs for Schlegel + Clarkson (numerical claims abstract-level).
- Agent 2: TPAM PNAS paper 403-blocked; capacity numbers from secondary sources.
- Agent 3: largest published pure-DAM empirical N is **low hundreds** (Hoover 2024). All "large d" demos are attention layers in averaging regime, not single-pattern retrieval.
- Agent 1: zero published OAQEC classical-memory benchmark.

**These caveats are LOAD-BEARING for the probability estimates** — V2.D's 0.55-0.65 P assumes substrate refactor extends published-low-hundreds-N DAM results to substrate's N=4096 regime; this is empirically untested in literature.

EOF marker.
