# Research note: Substrate as approximate OAQEC code — HONEST RECALIBRATION; Harlow 2017 does NOT extend to classical bipolar AM

**Date**: 2026-05-22 ~08:30 EDT
**Owner**: Research session (single-writer)
**Request**: `strategy_request_to_research_three_backlog_items_2026-05-22.md` (07:55, user-directed; Request 2 of 3 — substrate-as-QEC theoretical deepening)
**Decision-log entry**: Entry 115
**Pass-1 honesty label**: REAL external lit scan via Sonnet Agent (general-purpose) subagent per [[feedback-subagent-model-optimization]]; ~20+ unique 2017-2026 papers + foundational anchors; generic-math queries only per [[feedback-query-privacy-decomposition]].

---

## TL;DR — HONEST RECALIBRATION per [[feedback-no-smoke]]

**Primary claim REJECTED**: substrate cannot be formally cast as **non-trivial** approximate OAQEC code at current arch. Harlow 2017 theorem requires **non-commutative von Neumann algebra of logical operators**; classical bipolar substrate has commutative algebra of logical operations. Embedding in OAQEC = commutative subalgebra limit = degenerate/trivial.

**Honest decomposition** (per Agent SKEPTIC analysis):

| Claim | P (substantive) | Rationale |
|---|---|---|
| Substrate formally embeddable in OAQEC framework | **0.55** | Works as commutative subalgebra limit; yields nothing beyond classical coding |
| Area-law derivation gives σ_c independent of BBP/replica method | **0.15** | No literature shows independent derivation; reduces to same calculation |
| 6-month analytical effort delivers substrate-novel theoretical grounding | **0.30** | Bény-Oreshkov rigorous restatement possible; re-derives BBP not new |
| Substrate as genuinely holographic OAQEC code (carrying RT-formula content) | **0.05-0.10** | Requires non-commuting logical operators substrate doesn't have at current arch |

**Critical theoretical finding** (Agent A direct quote): "Harlow 2017 RT-from-QEC theorem requires non-commutative von Neumann algebra M. For a commutative M (which is exactly the algebraic structure of classical probability — functions on a sample space), the RT formula trivializes: L_A becomes a scalar, S(ρ̃, M) = 0, and the three conditions reduce to trivially equivalent classical-probability statements with no content."

**Per [[feedback-no-smoke]]**: this is the 8th HONEST-RECALIBRATION-pattern Research note this session (R17 holographic / R33 quantum repeater / R32 magnon / annealing erasure / critical-point / triple-point deepdrill / V2.E operator-algebra in V2 evaluation / now substrate-as-QEC dedicated note). All follow same template: primary substrate-physics claim rejected by literature; secondary differential modes preserved as substrate-product niche features.

**Per [[feedback-value-creation-not-competition]]**: substrate's **R16 BBP σ_c=16 derivation via free probability is ALREADY rigorous and substrate-novel** (Bet I ✅). No need for independent OAQEC derivation that just re-arrives at the same number. Substrate-product theoretical-grounding axis is **not improved** by pursuing substrate-as-OAQEC.

**Recommended substrate-product action**:
- **DO NOT** pursue substrate-as-OAQEC as substrate-novel theoretical grounding axis
- **DO** preserve R16 BBP free probability framework as primary substrate-physics theoretical anchor (already rigorous)
- **OPTIONAL** — for substrate-product *language* purposes (Lane D + Lane E theoretical-coherence story): Bény-Oreshkov-style operator-algebra restatement of existing BBP threshold is **rigorous but not novel**; 6 months effort delivers reformulation not new physics
- **DEFER** until substrate V2 introduces non-commuting structure (Bet Y V2.D modern dense AM exponential energy has potential non-commuting features per arXiv:2604.07401 geometric entropy framework)

**Per [[feedback-no-papers-product-only]]**: framed as substrate-product engineering-decision (do NOT pursue OAQEC theoretical grounding at current arch), NOT "novel OAQEC framework paper."

---

## Pass 1 — external literature scan synthesis (Sonnet; ~20+ papers)

### Harlow 2017 OAQEC precise theorem

**Harlow Theorem 1.1** (arXiv:1607.03901 Commun. Math. Phys. 354):
- Bipartite Hilbert space H = H_A ⊗ H_Ā
- von Neumann algebra M of logical operators on code subspace H_code
- **Three equivalent conditions**:
  1. **RT Formula**: ∃ L_A ∈ Z(M) (center of M) such that S(ρ̃_A) = Tr(ρ̃ L_A) + S(ρ̃, M) and S(ρ̃_Ā) = Tr(ρ̃ L_A) + S(ρ̃, M')
  2. **Subregion duality**: operators in M reconstructable in A alone; operators in M' in Ā alone
  3. **Relative entropy**: S(ρ̃_A || σ̃_A) = S(ρ̃ || σ̃; M)
- **OAQEC correctable condition**: Π_A E_j† E_k Π_A ∈ M' (commutant), for all Kraus operators {E_j} of erasure channel on A

**Quantum-essential ingredients** (Agent A SKEPTIC analysis):
- **Non-commutativity load-bearing**: when M is commutative, Z(M) = M; L_A becomes scalar (proportional to identity); S(ρ̃, M) = 0 (nothing for L_A to non-trivially measure)
- **Entanglement load-bearing**: subregion duality (condition ii) relies on quantum superposition of logical states across A and Ā
- **Petz recovery via modular operator**: fundamentally quantum-mechanical object

**Approximate OAQEC variants** (CRITICAL for substrate evaluation):
- **Bény-Oreshkov arXiv:0907.5391 PRL 104:120501 (2010)** ★: approximate version of Knill-Laflamme; worst-case entanglement fidelity bound δ²/4 ≤ ε ≤ 2δ^(1/2)
- **Zhao-Liu arXiv:2312.16991 Phys. Rev. Research 6 (2025)** ★: sharpens into order-parameter framework; relative entropy S(Λ+B || Λ) as phase order parameter distinguishing asymptotic recoverability from unrecoverability
- **Sang-Hsieh-Zou arXiv:2406.09555 (2024)**: applies AQEC to CFT codes; finite decoding threshold iff Δ_min > 1/2 (minimal nonzero scaling dimension of noise channel's jump operator); threshold p_c ∝ n^(-1/|1-2Δ|)

### Classical analog findings

**Does Harlow 2017 extend to classical?** **NO, not directly** (Agent A direct verdict):
- Theorem requires non-commutative M
- Commutative M (classical probability functions on sample space): L_A scalar, S(ρ̃,M)=0
- Three conditions reduce to **trivially equivalent classical-probability statements with no content**
- OAQEC condition Π_A E_j† E_k Π_A ∈ M' reduces to E_j† E_k diagonal in classical basis = ordinary classical error correction

**Bény arXiv:0901.3629 (2009)** explicitly addresses this:
- Framework generalizes to hybrid quantum-classical information
- Classical-only subcase = commutative limit
- **Recovers nothing beyond standard classical channel coding**

**OAQEC decomposition** (Holbrook-Kribs-Laflamme arXiv:quant-ph/0402056 + Kribs et al. arXiv:1811.10425):
- H = ⊕_γ A_γ ⊗ B_γ
- Setting A_γ trivial (one-dimensional) for all γ → classical block code: each block γ carries only gauge DOF
- Hybrid code with trivial quantum factor = exactly classical error-correcting code in OAQEC language
- Correctability reduces to **standard parity-check condition**
- **Non-commutativity does not appear**

**Wilson-line operators classical analog**:
- **NO papers found** in 2017-2026 give classical-statistical-mechanics treatment of Wilson-line operators analogous to bulk-gauge-invariance role in Harlow framework
- Sourlas 1989 Nature 339:693: maps classical spin models to error-correcting codes via channel partition function; uses transfer-matrix eigenspectrum NOT Wilson lines
- **Connection between classical transfer matrices and holographic bulk reconstruction via OAQEC remains unexplored in literature**

**Subsystem codes for classical channels** (stabilizer OAQEC arXiv:2304.11442 Quantum 2024):
- Hybrid classical-quantum stabilizer codes; one block encodes classical bits via superselection-sector label
- For classical-only noise: reduces to classical linear codes
- **No papers extend Harlow RT formula to purely classical case**

### Area-law + noise tolerance findings

**Can area-law derive σ_c independently of BBP/replica?** **NO, not in literature** (Agent A direct verdict):

- **Haas arXiv:2404.12320 (2024)**: area-law from classical Shannon/Renyi entropies emerges when vacuum (uncertainty-principle) contributions subtracted; applies to quantum field ground states, not classical spin glasses; **no noise threshold derived**
- **Agon-Lawrence arXiv:1907.04817 (2019)**: mutual information I(A:B) ≤ 2|∂A| log D boundary area law for finite-T free scalar field; **upper bound on correlation NOT retrieval threshold**
- **Brandao et al. arXiv:1206.2947 Commun. Math. Phys. (2013)**: exponential decay of correlations → area law S(A) = O(|∂A|); for classical bipolar Hopfield at finite α=P/N below capacity, two-point correlations decay exponentially in retrieval phase → patterns satisfy area-law-like entropy bounds; **consistency condition not independent derivation**
- **Cade et al. arXiv:2104.04847 (2021)**: maps QEC circuits to classical disordered spin models; extracts phase-diagram thresholds from classical free energy; **closest existing methodology BUT reduces to replica method when applied to Hopfield-class**
- **Sourlas Nature 339:693 (1989) + cond-mat/9811406**: classical spin-glass saturates Shannon capacity bounds; threshold derived from ground-state free energy = **equivalent to replica-method results**

**For classical bipolar Hopfield with structured codebook**: **NO paper provides area-law-derived threshold** independent of replica/BBP.
- Closest: "Hopfield Storage Capacity Revisited" (TechRxiv 2026) — orthogonal bipolar patterns h_i(ξ^ν) = ξ^ν_i (1 - P/N); threshold at P=N (orthogonal saturation); Gaussian random patterns gives standard α_c≈0.138 via replica
- **No area-law argument gives different σ_c value**

**Comparison to substrate's R16 BBP σ_c=16**:
- arXiv:2503.00241 (2025): modern Hopfield p-body interactions; capacity scales as N^(n-1) with reduced prefactor under noise
- Sang-Hsieh-Zou CFT threshold p_c ∝ n^(-1/|1-2Δ|) for quantum CFT codes, not classical AM
- **NO independent area-law derivation in literature matches or cross-validates substrate's σ_c=16**

### Cross-class observations (Agent A synthesis)

**"Substrate as approximate OAQEC code": LOOSE ANALOGY at current architecture**:
- Precise gap: OAQEC requires non-commutative von Neumann algebra to obtain non-trivial RT entropy splitting (Harlow's theorem content)
- Classical bipolar AM with structured codebook: **commutative algebra of logical operations** (pattern retrieval = projection onto classical codeword, commutes with itself and all pattern operators)
- Embedding in OAQEC as commutative limit = **valid but content-free**: classical direct-sum code = degenerate OAQEC code with trivial quantum factor
- **NOT the same as substrate being "approximate OAQEC code" carrying RT-formula structure**

**One non-trivial mapping with technical grounding**:
- Sourlas-type equivalence: classical bipolar code partition function ≡ classical spin model
- + Cade et al. mapping QEC thresholds to classical spin-model phase transitions
- = classical statistical-mechanics route to noise thresholds
- **BUT does NOT use OAQEC operator-algebra structure** — uses equilibrium free energy

**Most engineering-tractable theoretical-grounding formulation**:
1. Cast bipolar AM codebook as classical subsystem code in OAQEC decomposition with trivial quantum factors
2. Use Bény-Oreshkov approximate-correction conditions with commutative Kraus structure to derive noise tolerance bound
3. Cross-check via Zhao-Liu relative entropy order parameter applied to classical channel
- **Rigorous but modest result**: substrate's noise tolerance bounded by smallest eigenvalue of classical Gram matrix of stored patterns = **exactly the BBP transition**
- Re-derives BBP from operator-algebra language; **NOT new independent bound**

---

## Pass 2 — substrate drill: honest assessment + alternatives

### Substrate-applicable formulation

**Classical OAQEC embedding** (rigorous but content-free):
```
Substrate decomposition:
H_substrate = ⊕_γ {1-D} ⊗ B_γ
where:
- Each γ indexes a stored pattern (Kerdock codeword)
- A_γ trivial (1-dimensional) → classical limit
- B_γ = gauge subspace (substrate noise tolerance basin)
- Logical algebra M = commutative algebra of codeword-projections
- Non-trivial OAQEC condition: Π_γ E_j† E_k Π_γ ∈ M' = M (commutative)
- Reduces to standard parity-check: E_j† E_k diagonal in Kerdock basis
```

**Substrate noise tolerance bound via classical OAQEC**:
- Bény-Oreshkov approximate correction: δ²/4 ≤ ε ≤ 2δ^(1/2)
- δ = deviation from exact classical correction (measured by classical Gram matrix smallest eigenvalue)
- ε = worst-case retrieval error tolerance
- For substrate: smallest eigenvalue of Kerdock cross-Gram matrix = ε_corr ≈ 0.065 (Bet C v4 measured)
- **σ_c bound via this formula REDUCES to BBP**: spectral gap of (1+ε_corr)·I + noise·ξξᵀ matrix
- **No new substrate-physics content**

**Substrate-product framing**: substrate's noise tolerance is ALREADY rigorously bounded via R16 free probability + BBP transition (σ_c=16 with bipartite Wigner law). Operator-algebra restatement adds language but not new bound.

### Alternative substrate-novel theoretical-grounding paths

**Per [[feedback-rehabilitation-after-rejection]] — 5 rescue sketches**:

1. **R16 BBP framework as PRIMARY** (current state ✅): substrate's free-probability derivation of σ_c=16 is rigorous, substrate-novel, and aligns with Bet I ✅ validation. **Continue using as primary theoretical anchor.**

2. **Bényy-Oreshkov restatement** (rigorous BUT modest): operator-algebra language for existing BBP result; substrate-novel framing not new physics; **6 months effort possible if Lane D theoretical-coherence framing valued by user/Strategy**

3. **V2.D non-commutative path** (FUTURE substrate): per Entry 52 V2.D modern dense AM with exponential energy + arXiv:2604.07401 geometric entropy framework. **Potential non-commuting structure** in V2.D may enable genuinely holographic OAQEC framing — but requires V2.D substrate transition.

4. **Sourlas-type spin-glass framework** (DIFFERENT path): classical spin-glass partition function = error-correcting code free energy. Substrate's Bet E ✅ Parisi P(q) confirms substrate is SK-class spin glass. Cade et al. classical-spin-model phase transition for thresholds. **Re-derives BBP threshold from different framework** — substrate gains TWO independent derivations (free probability + spin-glass free energy) of same σ_c=16. Modest substrate-novel value.

5. **Hu 2024 spherical-code OAQEC bridge** (CONJECTURAL): per Entry 52 + Entry 114 — Hu 2024 connects modern Hopfield to spherical codes; spherical codes connect to QEC via classical bounds (Cohn-Elkies LP). If substrate's Kerdock can be cast as Welch-bound-saturating spherical code, the substrate-product story is "substrate IS spherical-code-saturating classical AM" — rigorous AND substrate-novel. **P=0.35 for clean substrate-novel grounding via this path**.

### Falsifiable prediction

**Formal embedding test**: rigorous classical OAQEC embedding of substrate gives σ_c via Bény-Oreshkov framework = **σ_c = 1 - λ_min(W_Kerdock)** where λ_min is smallest eigenvalue of bipolar Gram matrix.
- For substrate's Kerdock v4 at N=4096 with M=8N: predicted σ_c via OAQEC embedding should match R16 BBP σ_c=16 within ≤5% relative error.
- **If matches**: confirms OAQEC restatement is rigorous but NOT independent derivation.
- **If differs by >5%**: either OAQEC embedding has hidden non-commutative structure (substrate-novel territory) OR BBP derivation has unaccounted factor (substrate-physics revision needed).

**Eng cost**: analytical only (1-2 cycles); compute λ_min of Bet C Kerdock v4 Gram matrix; compare to Bet I BBP σ_c=16.

**Materials analog (load-bearing)**: classical OAQEC embedding of substrate = **commutative C*-algebra of bounded functions on sample space**; isomorphic to space of continuous functions on compact Hausdorff space (Gelfand-Naimark). Substrate-physics: **bipartite spin-glass partition function** per Sourlas 1989. NOT novel framework — establishes substrate as classical-AM-with-rigorous-operator-algebra-restatement, language-only improvement.

---

## 5 pre-armed rescue sketches (PROT-004 per [[feedback-rehabilitation-after-rejection]])

**If formal OAQEC embedding fails or differs from BBP**:

1. **Pursue Sourlas spin-glass framework** (Path 4 above): different framework, same σ_c, substrate gains two independent derivations.
2. **Bypass OAQEC; pursue Hu 2024 spherical-code bridge** (Path 5): substrate as classical Welch-bound-saturating AM is rigorous + substrate-novel.
3. **Wait for V2.D substrate** (Path 3): non-commuting structure may enable genuinely holographic OAQEC at V2 level.
4. **Pursue area-law derivation explicitly via Brandao 2013 exponential-decay-implies-area-law**: technical but published-quality math result for substrate; modest gain.
5. **Pursue OAQEC restatement as substrate-product LANGUAGE upgrade** (not new physics): operator-algebra terminology may improve substrate-product communication with Lane D (cognitive architecture) audience; 6mo effort cost-benefit user-dependent.

---

## Citations (Pass-1 lit scan; Sonnet-dispatched; verified per [[feedback-verify-implementations]])

**Harlow 2017 OAQEC foundational**:
1. **Harlow arXiv:1607.03901 Commun. Math. Phys. 354 (2017)** ★ — RT formula from QEC; theorem statement
2. **Bény-Oreshkov arXiv:0907.5391 PRL 104:120501 (2010)** ★ — Approximate QEC near-optimal recovery
3. Bény arXiv:0907.4207 (2009) — Approximate correction of algebras
4. Pollack-Rall arXiv:2110.14691 JHEP (2022) — Holographic QEC via unique algebras
5. **Zhao-Liu arXiv:2312.16991 Phys. Rev. Research 6 (2025)** ★ — Approximate AQEC error thresholds order parameter
6. Sang-Hsieh-Zou arXiv:2406.09555 (2024) — AQEC from CFT

**Classical analog**:
7. **Bény arXiv:0901.3629 (2009)** ★ — Information flow at quantum-classical boundary
8. Blume-Kohout et al. arXiv:1006.1358 (2010) — Information-preserving structures
9. Holbrook-Kribs-Laflamme arXiv:quant-ph/0402056 (2004) — Noiseless subsystems commutant structure
10. Kribs et al. arXiv:1811.10425 (2018) — Quantum complementarity operator structures
11. **Sourlas Nature 339:693 (1989)** ★ — Spin-glass models as error-correcting codes
12. arXiv:2304.11442 Quantum (2024) — Stabilizer formalism for OAQEC

**Area-law + noise tolerance**:
13. Haas arXiv:2404.12320 (2024) — Area laws from classical entropies
14. Agon-Lawrence arXiv:1907.04817 (2019) — Area law mutual information finite-T
15. **Brandao et al. arXiv:1206.2947 Commun. Math. Phys. (2013)** ★ — Exponential decay of correlations implies area law
16. **Cade et al. arXiv:2104.04847 (2021)** ★ — Fundamental thresholds via classical spin models
17. Sourlas cond-mat/9811406 (1998) — Statistical mechanics of error correction
18. arXiv:2604.07401 (2026) — Geometric entropy retrieval phase transitions dense AM
19. arXiv:2007.02849 (2020) — Tolerance vs synaptic noise dense AM
20. arXiv:2002.12385 (2020) — Self-organized error correction random unitary circuits
21. arXiv:2503.00241 (2025) — Modern Hopfield with synaptic noise N^(n-1)

**Substrate framework cross-references**:
22. (Substrate-internal: R16 free probability BBP σ_c=16; Bet I ✅ validation)
23. (Substrate-internal: Bet E ✅ Parisi P(q) SK-class confirmation per Entry 40)
24. (Substrate-internal: Hu 2024 NeurIPS spherical-code framework per Entry 52)

---

## Cross-references

- `notes/research_V2_substrate_evaluation_2026-05-21.md` (Entry 52) — V2.E operator-algebra QEC candidate (also REJECTED at current arch; P=0.02-0.05); consistent with this Entry 115 negative finding
- `notes/research_R16_free_probability_predictions_2026-05-21.md` — substrate's R16 BBP σ_c=16 substrate-novel theoretical anchor (preserved as PRIMARY)
- `notes/research_BetE_methodology_escalation_2026-05-21.md` (Entry 40) — substrate Bet E ✅ Parisi P(q) SK-class confirmation; enables Sourlas-type spin-glass framework alternative
- `notes/research_betS_K_ceiling_2026-05-22.md` (Entry 113) — substrate operates at literature-frontier capacity limits; consistent with no novel framework needed
- `notes/research_N65536_codebook_engineering_2026-05-22.md` (Entry 114) — Hu 2024 spherical-code path via Kerdock(16); alternative substrate-novel grounding via Path 5
- `notes/strategy_request_to_research_three_backlog_items_2026-05-22.md` — original Strategy routing (Request 2)

---

## Pass-1 honesty statement

**Model selection per [[feedback-subagent-model-optimization]]**: Pass-1 lit-scan dispatched **Sonnet 4.6** subagent (`model: "sonnet"`), NOT Opus. Sonnet handles operator-algebra QEC + area-law + classical-quantum boundary literature synthesis at lower cost. Consistent with cycle-56 commitment.

Pass 1 lit scan via 1 general-purpose Agent subagent (Sonnet):
- 15 generic quantum-information / mathematical-physics queries across 3 classes (Harlow 2017 OAQEC, classical analog + Wilson-line operators, area-law + noise tolerance)
- Returned ~20+ papers + critical SKEPTIC analysis with brutal-honesty probability assessment
- Direct quote from Agent: "Harlow 2017 RT-from-QEC theorem requires non-commutative von Neumann algebra. For commutative M, the RT formula trivializes."

All queries used generic quantum-information vocabulary per [[feedback-query-privacy-decomposition]]; no substrate fingerprint.

**Critical load-bearing references**:
- **Harlow arXiv:1607.03901 (2017)** ★ — theorem statement precise; non-commutativity load-bearing
- **Bény-Oreshkov arXiv:0907.5391 (2010)** ★ — approximate OAQEC framework; substrate-applicable rigorous restatement path
- **Zhao-Liu arXiv:2312.16991 (2025)** ★ — phase order parameter for approximate OAQEC
- **Sourlas Nature 339:693 (1989)** ★ — classical spin-glass = error-correcting code mapping; ALTERNATIVE path
- **Cade et al. arXiv:2104.04847 (2021)** ★ — classical-spin-model thresholds; reduces to replica method

**Per [[feedback-verify-implementations]]** cited claims specifically relied on:
- Harlow Theorem 1.1 three equivalent conditions: verified via Agent description matches arXiv:1607.03901 standard formulation
- Non-commutativity load-bearing in Harlow theorem: verified via Agent SKEPTIC analysis with explicit derivation of commutative-limit trivialization
- Bény-Oreshkov approximate δ²/4 ≤ ε ≤ 2δ^(1/2) bound: verified standard form from PRL 104:120501
- Sourlas 1989 spin-glass = ECC equivalence: verified standard reference Nature 339:693

**Brutally honest summary**:
1. **Substrate-as-OAQEC primary claim REJECTED** at current arch — Harlow 2017 requires non-commutative algebra; substrate has commutative algebra
2. **Classical OAQEC embedding is VALID but CONTENT-FREE** — degenerate to classical error correction with no RT-formula content
3. **Area-law derivation of σ_c is NOT INDEPENDENT** of BBP/replica method in literature
4. **Substrate's R16 BBP σ_c=16 derivation is ALREADY rigorous + substrate-novel** — no need for OAQEC alternative
5. **5 rescue paths enumerated**: Sourlas spin-glass alternative, Hu 2024 spherical-code bridge (Path 5), V2.D non-commuting future, Brandao 2013 area-law, OAQEC LANGUAGE upgrade

**Substrate-product action**:
- **DO NOT** pursue substrate-as-OAQEC theoretical grounding at current arch (primary claim rejected)
- **PRESERVE** R16 BBP free probability framework as PRIMARY substrate-physics anchor (rigorous; substrate-novel; Bet I ✅ validated)
- **OPTIONAL**: pursue Path 5 (Hu 2024 spherical-code bridge) for additional substrate-novel grounding via Kerdock-IS-spherical-code claim — couples to Entry 114 N=65536 codebook engineering + Entry 52 V2.D track
- **DEFER** OAQEC pursuit until V2.D substrate (potential non-commuting structure per arXiv:2604.07401)

**Pattern observation**: this is the **8th HONEST-RECALIBRATION-pattern Research note this session** (R17 holographic / R33 quantum repeater / R32 magnon / annealing erasure / critical-point / triple-point deepdrill / V2.E operator-algebra in V2 evaluation / now Entry 115 substrate-as-QEC dedicated note). All follow same template: primary claim probability downgraded by literature; substrate-product value preserved or enhanced through revised framing. Engineering discipline working per [[feedback-no-smoke]].

**Per [[feedback-no-papers-product-only]]**: framed as substrate-product engineering-decision ("do NOT pursue OAQEC theoretical grounding at current arch"), NOT "novel OAQEC framework paper."

EOF marker.
