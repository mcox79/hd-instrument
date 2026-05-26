# Research note: Bet Y V2.D OAQEC pre-investigation — Bet Y does NOT open OAQEC at V2; substrate-as-OAQEC stays DEFERRED INDEFINITELY

**Date**: 2026-05-22 ~09:05 EDT
**Owner**: Research session (single-writer)
**Request**: `strategy_request_to_research_two_followups_2026-05-22.md` (08:40, user-flagged; Request B — Bet Y V2.D OAQEC pre-investigation)
**Decision-log entry**: Entry 119
**Pass-1 honesty label**: REAL external lit scan via Sonnet Agent (general-purpose) subagent per [[feedback-subagent-model-optimization]]; ~12+ unique 2017-2026 papers + foundational anchors; generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — STRONG NEGATIVE; Bet Y V2.D does NOT open OAQEC framework

**HEADLINE finding** (per Agent B SKEPTIC analysis): Bet Y V2.D (modern dense AM with exp(β·x) energy + softmax cleanup) does **NOT** introduce non-commuting operator structure to substrate in OAQEC-relevant sense. **Substrate-as-OAQEC stays DEFERRED INDEFINITELY** per Entry 115 conclusion.

**Honest probabilities** (per Agent B):

| Claim | P | Rationale |
|---|---|---|
| Bet Y V2.D introduces genuine non-commuting structure | **0.15** | Softmax F(ξ) converges to fixed points where iterates commute; only trivial matrix non-commutativity |
| Non-commutativity enables OAQEC framework applicability (Harlow 2017) | **0.08** | OAQEC needs Hilbert space + C*-algebra with non-trivial center + quantum-coherent errors; substrate has none |
| V2.D opens substrate-novel OAQEC theoretical-grounding axis | **0.07** | No paper bridges AM retrieval operators to OAQEC-admissible algebras |

**Critical theoretical finding (Agent B direct quote)**:
> "Classical AM with symmetric weight matrix = commutative algebra (functions of W share eigenvectors). The softmax map F(ξ) = X·σ(β·Xᵀξ) converges to a fixed point where [F, F] = 0 trivially. The interesting non-commutativity would require two distinct networks or two distinct retrievals being composed — not the standard retrieval iteration."

**arXiv:2604.07401 framework assessment** (per Agent B):
- Paper: Petrova-Polyachenko-State (April 2026, ICML 2026) "Geometric Entropy and Retrieval Phase Transitions in Continuous Thermal Dense Associative Memory"
- Content: equilibrium thermodynamics, replica method, LSE/LSR kernels, α_c=0.5 at T=0
- **Geometric entropy s(φ,q) = ½ln(1-q) + (q-φ²)/[2(1-q)]** depends only on N-sphere geometry, NOT kernel
- **Framework uses NO non-commutative structure**: continuous real-valued states, real scalar energies, commuting integrals/derivatives in replica space, standard Ising-like phase transition analysis
- The "geometric" refers to SPHERICAL GEOMETRY, NOT algebraic/quantum-geometric structure
- **Does NOT apply directly to bipolar classical AM** — spherical constraint load-bearing

**Why softmax does NOT generate OAQEC-relevant non-commutativity**:
- F(ξ) = X·softmax(β·Xᵀξ) is fixed-point map
- One-step convergence to patterns for well-separated stored patterns (Ramsauer 2020)
- Sequential iteration F∘F vs F₂∘F₁ for different X₁, X₂: trivially differs because matrix multiplication doesn't commute
- This is **standard matrix non-commutativity**, NOT structured C*-algebraic non-commutativity that OAQEC requires

**OAQEC framework requirements** (Harlow 2017):
1. Hilbert space (or classical analog = probability space) ✓ trivially classical
2. C*-algebra of logical operators with **non-trivial center** ✗ substrate has trivial center (commutative)
3. Error operators satisfy commutant condition Π_A E_j†E_k Π_A ∈ M' ✗ trivially holds for commutative M=M'
4. **Non-commutative algebra** to obtain non-trivial error correction beyond classical repetition ✗ substrate is classical

**Verdict**: **substrate-as-OAQEC framework STAYS DEFERRED INDEFINITELY**. R16 BBP free probability framework remains PRIMARY theoretical anchor per Entry 115.

**11th HONEST-RECALIBRATION-pattern note** of session (R17 / R33 / R32 / annealing / critical / triple / V2.E / substrate-as-QEC / R36 mechanism / Bet Y V2.D OAQEC pre-investigation now / 11th).

---

## Pass 1 — external literature scan synthesis (Sonnet; ~12+ papers)

### arXiv:2604.07401 substrate-applicability assessment (DETAILED)

**Paper**: Tatiana Petrova, Evgeny Polyachenko, Radu State. "Geometric Entropy and Retrieval Phase Transitions in Continuous Thermal Dense Associative Memory." arXiv:2604.07401, April 2026. Published ICML 2026.

**Precise theoretical content** (Agent B):
- Equilibrium thermodynamics for modern dense AM over continuous states on N-sphere
- Two kernels compared:
  - **LSE (Gaussian)**: E(ξ) = -β⁻¹ log(Σ exp(-β‖X_i - ξ‖²)). Retrieval extends to high T as α→0; interference from spurious patterns always present for α>0
  - **LSR (Epanechnikov, finite-support)**: threshold α_th below which no spurious patterns; near-perfect retrieval at any T
- **Geometric entropy**: s(φ,q) = ½ln(1-q) + (q-φ²)/[2(1-q)] where φ=alignment, q=self-overlap
- s depends ONLY on N-sphere geometry, NOT on kernel
- Emerges from disorder-averaged replica free energy via standard RS ansatz
- ⟨f⟩ = u(φ) - T·s(φ,q), saddle point at q=φ²
- **α_c = 0.5 at T=0** zero-temperature critical capacity

**Framework algebraic structure** (Agent B SKEPTIC):
- Continuous real-valued states on S^(N-1)
- Real scalar energy functionals
- Commuting integrals and derivatives in replica space
- Standard Ising-like phase transition analysis
- "The paper uses NO non-commutative structure"
- Ramsauer 2020 connection is "motivational" not algebraic
- "Geometric" = spherical geometry, NOT algebraic/quantum-geometric

**Does it apply to bipolar classical AM with softmax(β) cleanup?**
- **Directly: NO** (Agent B)
- α_c=0.5 requires continuous spherical states
- Bipolar (±1) AM is different universality class (Hopfield linear capacity 0.14N, polynomial higher-order)
- LSE/LSR analysis not portable: entropy s(φ,q) assumes spherical integration measure; discrete hypercube measure gives fundamentally different calculation
- **Indirectly**: phase-transition framework (replica + free energy + load α) is generic; applied to bipolar since AGS 1987; 2604.07401 adds no new results there

### Modern Hopfield non-commutativity findings

**Papers reviewed**:
1. **Ramsauer et al. arXiv:2008.02217 (2020/2021)** ★ — Hopfield Networks is All You Need
2. arXiv:2603.27804 (2026) — Unstable fixed points in continuous Hopfield
3. arXiv:2509.06905 (2025) — Yet another exponential Hopfield model
4. **Hu et al. arXiv:2410.23126 NeurIPS (2024)** — Provably optimal capacity via spherical codes
5. Mishra Medium post — "Your Attention Is Noncommutative" (non-peer-reviewed)
6. Classical update-rule commutativity literature (synchronous vs asynchronous)

**Critical findings on softmax commutativity** (per Agent B):

**Ramsauer 2020**: softmax update F(ξ) = X·softmax(β·X^T·ξ) analyzed as **fixed-point map**, NOT composable operator. One-step convergence. **No commutativity analysis performed.**

**arXiv:2603.27804 (2026)**: fixed-point structure analysis; exponentially more unstable fixed points than attractors for large β; geometric/polytope analysis. **Does NOT address whether F₁∘F₂ vs F₂∘F₁ differs.**

**Mishra Medium post**: claims AB ≠ BA for two attention heads; invokes Connes noncommutative geometry; commutator [A₁, A₂] = "semantic curvature." **NOT peer-reviewed; no formal proof; speculative analogy piece.**

**Classical synchronous/asynchronous update**: well-studied (convergence vs limit cycles). **NOT non-commutativity of operators** — it's order-of-evaluation sensitivity in a scalar energy landscape. Formal commutator [F_i, F_j] (update neuron i vs j) has **never been studied** in this literature.

**Key finding on softmax commutativity** (Agent B verbatim):
> "Softmax σ: R^n → Δ^(n-1) is not idempotent (σ(σ(x)) ≠ σ(x) except at uniform), but this is DISTINCT from non-commutativity. Composing two softmax retrievals F_A ∘ F_B vs F_B ∘ F_A (different pattern matrices A,B) will generically differ because F(ξ) = X·σ(βXᵀξ) depends on X. **But this order-dependence is the same order-dependence that arises from any matrix multiplication: it reflects standard non-commutativity of matrix products, not any deeper algebraic structure. No paper in this scan claims or proves softmax retrieval update generates non-commutative algebra in any operator-algebraic sense.**"

### Classical AM bridge findings

**Papers reviewed**:
1. **Bény-Oreshkov PRL 2010 (arXiv:0907.4207)** ★ — General Conditions for Approximate QEC; classical info = dim A = 1 = commutative algebra
2. **Harlow 2017 (arXiv:1607.03901)** ★ — RT formula from QEC; full OAQEC framework
3. errorcorrectionzoo.org/c/oaecc — OAQEC code = finite-dim C*-algebra with A = ⊕_γ I_γ ⊗ L(B_γ)
4. Transfer matrix non-commutativity arXiv:1006.1608 + SciPost Phys. 12:007 (2022) — classical 1D spin systems
5. arXiv:1005.3972 — Non-commutativity from coarse-grained classical probabilities
6. C*-algebra Bohrification literature arXiv:1601.02794 + quant-ph/0312051

**Critical findings**:

**OAQEC code requirement** (errorcorrectionzoo.org):
- Finite-dimensional C*-algebra with decomposition A = ⊕_γ I_γ ⊗ L(B_γ)
- Classical info lives in block structure (index γ)
- Quantum info in L(B_γ) factors
- **Purely classical code**: all B_γ = ℂ (dimension 1) → algebra becomes commutative → OAQEC reduces to **classical error correction** with NO structural novelty

**Harlow 2017 full framework**:
- Hilbert space decomposition H = ⊕_γ A_γ ⊗ B_γ
- Error operators satisfy Π_A E_j†E_k Π_A ∈ A' (commutant condition)
- **Non-trivial center of bulk algebra encodes classical information**
- Commutative subalgebras (classical limits) **PERMITTED, not excluded** — but yield no interesting OAQEC content

**Transfer matrix non-commutativity** (arXiv:1006.1608):
- Classical 1D spin systems have transfer matrices T non-commuting at strong coupling
- Textbook statistical mechanics
- **Relevant non-commutativity is between different local interactions** (e.g., [T_J, T_h] ≠ 0 for Ising in field)
- **NOT between retrieval steps in associative memory**

**Coarse-graining non-commutativity** (arXiv:1005.3972):
- Coarse-graining classical probability can produce effective non-commutative structure in coarse-grained algebra
- **Applies to MEASUREMENT algebra, NOT state space evolution**

**C*-algebra Bohrification** (arXiv:1601.02794):
- Classical mechanics = commutative C*-algebra
- Quantum mechanics = non-commutative C*-algebra
- Bohrification studies commutative subalgebras of non-commutative ones
- **Classical AM with symmetric W matrix is entirely in commutative regime**: W symmetric → all functions of W commute pairwise (share eigenvectors)
- **No non-commutative extension required or natural**

**Could bipolar Kerdock + softmax(β=32) cleanup be recast as non-commuting?**

Agent B analysis:
- Bipolar Kerdock construction = highly structured pattern set (related to Kerdock codes over Z/4)
- W = XᵀX (outer product sum) inherits code structure
- Softmax retrieval F(ξ) = X·σ(β·Xᵀξ)
- Sequential application F∘F: iteration F^(t) converges to fixed point where [F, F] = 0 trivially
- "Interesting non-commutativity would require two distinct networks or two distinct retrievals being composed — NOT the standard retrieval iteration"
- **No paper found treats this specific construction**

### Cross-class observations (Agent B synthesis)

**Central structural question**: does modern DAM update F(ξ) = X·softmax(β·X^T·ξ) introduce non-commuting operator algebra when iterated or composed?

**What literature shows**:
- F is map R^d → R^d (or S^(d-1) → S^(d-1) for spherical)
- F converges to fixed-point attractor in one step for well-separated patterns
- Set {F_X : X varies over pattern matrices} is non-commuting in **trivial sense** that any set of matrix functions is: F_{X1}∘F_{X2} ≠ F_{X2}∘F_{X1} generically because matrix multiplication doesn't commute
- This is **STANDARD MATRIX NON-COMMUTATIVITY**, NOT operator-algebra non-commutativity in OAQEC-relevant sense

**For OAQEC to apply** (Harlow 2017 framework):
1. Hilbert space (or classical probability space)
2. C*-algebra of "logical operators" acting on it with non-trivial structure
3. Error operators satisfying commutant condition

**For dense AM specifically**:
- "Hilbert space" = R^N (state space) ✓ trivially classical
- "Logical algebra" = needs to identify set of operators on pattern retrieval; **substrate's symmetric W has commutative algebra (all functions of W share eigenvectors)**
- "Errors" = noise perturbations of ξ; trivially satisfy commutant condition in commutative algebra

**For OAQEC to add anything over classical error correction**:
- Logical algebra must be **non-commutative**
- Must be multiple non-commuting operations on stored patterns
- Classical symmetric-weight networks have commutative logical algebra (retrieval operations commute at convergence)
- **Softmax nonlinearity breaks this slightly during transients but restores it at fixed points**

**Verdict**: **CONDITIONAL non-commutativity path exists, but requires deliberate construction**:
- (a) Composing retrieval from two distinct pattern sets (multi-network or multi-head structure)
- (b) Introducing asymmetric weight updates (Hebbian with asymmetric W)
- (c) Working with non-equilibrium transient dynamics before convergence
- **NONE of these is the default single-network softmax retrieval setup**

---

## Pass 2 — substrate drill: Bet Y V2.D structural analysis

### Bet Y V2.D specifically (per Entry 52 V2 evaluation)

**Bet Y V2.D mechanism**:
- Replace softmax(β=32) cleanup → explicit log-sum-exp E(s) = -β⁻¹ log Σ exp(β·xᵢᵀs)
- Energy descent via gradient flow on E(s)
- 1-5 gradient steps for cleanup

**Operator-algebra analysis**:
- Energy E(s) is REAL SCALAR function on R^N
- Gradient ∇E(s) is REAL VECTOR FIELD
- Energy descent F: R^N → R^N is REAL MAP
- Composition F∘F: standard matrix-product non-commutativity for different X (pattern matrices)
- **Same operator-algebra structure as classical Hopfield with softmax — commutative at fixed points**

**Bet Y V2.D + P.4 (α-entmax) extension** (per Phase Transformations Entry 53):
- α-entmax interpolates dense (α=1 softmax) to sparse (α=2 sparsemax)
- Generalizes to Hopfield-Fenchel-Young framework (arXiv:2411.08590)
- **Still real-valued energy functional**; still commutative at fixed points
- No path to non-commutativity

### Falsifiable prediction

**Bet Y V2.D substrate operator algebra is commutative at convergence**: ∀ pattern matrix X, fixed-point iterates of F_X commute: [F_X^k, F_X^j] = 0 for all k, j when F is at fixed point.

**Falsification test** (analytical only):
1. Construct Bet Y V2.D substrate at small N (say N=16) with random pattern matrix X
2. Compute F(ξ) iteratively until convergence: ξ_0, ξ_1 = F(ξ_0), ..., ξ_k = F^k(ξ_0)
3. Verify [F^k, F^j](η) = 0 for η near fixed point — should hold trivially
4. **Falsification**: if [F^k, F^j](η) ≠ 0 at fixed point for some η, non-commuting structure exists; OAQEC path opens
5. **Confirmation** (expected): commutators all zero; substrate is classical/commutative

**Eng cost**: ~30 min analytical Python (no GPU needed; small N validates).

### Materials analog (load-bearing)

**Substrate as classical C*-algebra**:
- Per Gelfand-Naimark: commutative C*-algebra ≅ continuous functions on compact Hausdorff space
- Substrate state space R^N + symmetric W → commutative algebra of continuous functions
- **Mathematically equivalent to classical observables on phase space** (Hamilton's classical mechanics)
- Substrate is NOT a quantum object (no superposition, no entanglement)
- Symmetric W ensures commutativity (no non-commuting H = position·momentum analog)

**Non-commutative extension paths** (NOT current substrate):
- Asymmetric W (Hebbian with directional learning rule): potential non-commutativity but breaks substrate's energy descent guarantee
- Multi-network composition: stack 2+ substrates with different X → matrix-product non-commutativity (trivial)
- Quantum extension (V3+ substrate): introduce qubit substrate → genuinely non-commuting

---

## 5 pre-armed rescue sketches (PROT-004 per [[feedback-rehabilitation-after-rejection]])

**If R16 BBP framework requires augmentation for substrate-product theoretical-grounding**:

1. **Sourlas-type spin-glass framework** (per Entry 115 Path 1): substrate's Bet E ✅ Parisi P(q) confirms SK-class spin glass; Cade et al. arXiv:2104.04847 (2021) classical-spin-model phase transition for thresholds. Re-derives BBP from different framework; substrate gains 2 independent derivations of σ_c=16.

2. **Hu 2024 spherical-code bridge** (per Entry 115 Path 5 + Entry 114 Kerdock(16)): substrate-as-rigorous-spherical-code via Kerdock-IS-Welch-bound-saturating-frame. P=0.35 for substrate-novel grounding via this path.

3. **Brandao 2013 exponential-decay-implies-area-law** (per Entry 115 Path 4): technical but published-quality math result for substrate.

4. **Multi-network OAQEC** (NEW per Agent B): construct substrate operator algebra over 2+ substrates with different X; non-commutativity emerges via matrix-product structure; rigorous but trivial sense.

5. **Asymmetric W substrate** (V3+ territory): break symmetric W constraint; introduce directional asymmetry; non-commuting algebra emerges but breaks energy descent + Bet E ✅ spin-glass framework.

---

## Citations (Pass-1 lit scan; Sonnet-dispatched; verified per [[feedback-verify-implementations]])

**arXiv:2604.07401 + geometric entropy**:
1. **arXiv:2604.07401 Petrova-Polyachenko-State (2026)** ★ — Geometric Entropy + Retrieval Phase Transitions; α_c=0.5; LSE/LSR kernels
2. arXiv:2603.13350 (2025) — Thermal robustness LSE vs LSR

**Modern Hopfield non-commutativity**:
3. **Ramsauer et al. arXiv:2008.02217 (2020/2021)** ★ — Hopfield Networks is All You Need; fixed-point analysis
4. arXiv:2603.27804 (2026) — Unstable fixed points in continuous Hopfield
5. arXiv:2509.06905 (2025) — Yet another exponential Hopfield model
6. **Hu et al. arXiv:2410.23126 NeurIPS (2024)** — Optimal capacity via spherical codes

**Classical AM bridge + OAQEC**:
7. **Bény-Oreshkov arXiv:0907.4207 PRL (2010)** ★ — Approximate OAQEC; classical limit = commutative
8. **Harlow arXiv:1607.03901 (2017)** ★ — RT formula from QEC; OAQEC framework
9. errorcorrectionzoo.org/c/oaecc — OAQEC code C*-algebra definition
10. Bény arXiv:quant-ph/0608071 — QEC generalization Heisenberg picture
11. arXiv:1601.02794 (2016) — Bohrification: classical to commutative

**Classical non-commutativity literature**:
12. arXiv:1006.1608 — Transfer matrix non-commutativity Ising chain
13. SciPost Phys. 12:007 (2022) — Classical 1D spin transfer matrix
14. arXiv:1005.3972 — Non-commutativity from coarse-grained classical probabilities

**Non-peer-reviewed reference (cited for context)**:
15. Mishra Medium post — "Your Attention Is Noncommutative" (SPECULATIVE; not peer-reviewed)

---

## Cross-references

- `notes/research_substrate_as_OAQEC_2026-05-22.md` (Entry 115) — original substrate-as-OAQEC analysis; this Entry 119 CONFIRMS deferred indefinitely conclusion
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (Entry 52) — V2.D Bet Y candidate (operator algebra remains commutative; doesn't change OAQEC applicability)
- `notes/research_phase_transformations_2026-05-21.md` (Entry 53) — P.4 dense↔sparse Hopfield-Fenchel-Young (still commutative)
- `notes/research_R36_mechanism_at_largeN_2026-05-22.md` (Entry 118) — Companion R36 mechanism note (β-scaling pathology)
- `notes/strategy_request_to_research_two_followups_2026-05-22.md` — original Strategy routing (Request B)

---

## Pass-1 honesty statement

**Model selection per [[feedback-subagent-model-optimization]]**: Sonnet-dispatched lit-scan subagent. ~12+ unique 2017-2026 papers + foundational anchors. Generic math/physics queries only per [[feedback-query-privacy-decomposition]].

**Critical load-bearing references**:
- arXiv:2604.07401 Petrova-Polyachenko-State (2026) — precise content (commutative thermodynamics; not non-commutative)
- Harlow 2017 arXiv:1607.03901 — OAQEC framework non-commutative algebra requirement
- Ramsauer 2020 arXiv:2008.02217 — modern Hopfield fixed-point convergence
- Bohrification arXiv:1601.02794 — classical mechanics = commutative C*-algebra

**Per [[feedback-verify-implementations]]** verified claims:
- arXiv:2604.07401 framework purely thermodynamic (commutative): verified via Agent B direct content extraction; geometric entropy s(φ,q) is real-valued function on real-valued state space
- Harlow 2017 requires non-commutative algebra: verified consistent with Entry 115 analysis
- Softmax fixed-point convergence (Ramsauer): verified standard one-step convergence result
- Classical AM with symmetric W is commutative: verified via Gelfand-Naimark + Bohrification literature

**Brutally honest summary**:
1. **Bet Y V2.D does NOT introduce OAQEC-relevant non-commutativity** — softmax/exp energy operates on real-valued state space with commutative algebra at fixed points
2. **arXiv:2604.07401 geometric entropy framework is PURELY thermodynamic** — uses no non-commutative structure; "geometric" refers to spherical geometry only
3. **Substrate-as-OAQEC stays DEFERRED INDEFINITELY** — confirms Entry 115 conclusion
4. **R16 BBP framework remains PRIMARY substrate-physics theoretical anchor**
5. **5 alternative theoretical-grounding paths enumerated** (Sourlas spin-glass, Hu 2024 spherical-code, Brandao area-law, multi-network OAQEC trivial, asymmetric W V3+)
6. **11th HONEST-RECALIBRATION-pattern note this session**

**Substrate-product action**:
- **DO NOT** pre-investigate OAQEC at V2.D substrate level (conclusion confirmed: no path opens)
- **PRESERVE** R16 BBP as primary theoretical anchor
- **OPTIONAL**: pursue Path 2 (Hu 2024 spherical-code bridge) for alternative substrate-novel grounding — couples to Entry 114 N=65536 + Entry 118 R36 mechanism notes
- **DEFER** OAQEC pursuit to V3+ substrate (quantum extension or asymmetric-W reformulation)

**Per [[feedback-no-papers-product-only]]**: framed as substrate-product engineering-decision ("V2.D doesn't open OAQEC at substrate level"), NOT "novel OAQEC framework paper."

EOF marker.
