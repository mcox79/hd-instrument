# Research R13 — Drinfeld double D(H) construction for substrate binding

**Topic.** Strategy's R13 (NEW cycle 19 forward-routing): does the Drinfeld
double D(H) construction provide a binding algebra superior to FHRR/Clifford
for chained associative-memory retrieval? Connects to R8's multi-hop
rescue (binding-algebra swap candidate #4) and existing Hopf-algebra work
(wave13). R13 is forward-routing (low urgency vs Bet B / multi-hop / Bet F);
slots in after top-priority queue drains.

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 30 tool uses,
25+ verified citations 1986-2026). Tenth consecutive cycle following
post-audit protocol.

**HEADLINE finding (per [[feedback-no-smoke]])**: D(H) is mathematically
rich and **substrate-novel (no published VSA work)** — but for **finite**
H, the braid representation has **FINITE IMAGE**, recreating the same
collapse problem R8 was trying to escape. The genuinely depth-unlimited
direction is **q-deformed U_q(g)** which is infinite-dimensional and
doesn't fit fixed-N substrate without truncation. R13 may produce
substrate-novel publishable math (no prior VSA work) without delivering a
shipping capability. Honest probability: substrate-shipping capability
20–35%; publishable substrate-novel math finding 60–80%.

---

## Pass 1 — External literature scan (verified)

Generic pure-math queries via subagent: "Drinfeld double Hopf algebra
construction," "Yetter-Drinfeld category braided structure," "R-matrix
Yang-Baxter equation quantum group," "quantum double D(G) finite group,"
"braided monoidal category Joyal-Street," etc. No substrate fingerprint.

### 1.1 The Drinfeld double D(H) construction

**Drinfeld 1986** ICM Berkeley (AMS 1987, pp. 798–820): given any finite-
dimensional Hopf algebra H with invertible antipode, the quantum double
D(H) is built on vector space H* ⊗ H with cross-multiplication structure
that makes H and H* sub-Hopf-algebras, forcing a specific commutation
relation between them via the coproduct.

**Universal R-matrix**: R = Σ (e_i ⊗ 1) ⊗ (1 ⊗ e^i) ∈ D(H) ⊗ D(H),
where {e_i}, {e^i} are dual bases of H, H*. Satisfies:
- R Δ(x) = Δ^op(x) R for all x ∈ D(H)
- Yang–Baxter equation: **R_{12} R_{13} R_{23} = R_{23} R_{13} R_{12}**
- Hexagon identities (Joyal-Street)

For H = k[G] (G finite group): D(k[G]) is the group quantum double;
underlying algebra is smash product k^G # k[G]. Dimension **|G|²**.

Textbook references: **Kassel** *Quantum Groups* (GTM 155, Springer 1995);
**Majid** *Foundations of Quantum Group Theory* (CUP 1995), Ch. 7 on
quantum doubles.

### 1.2 Yetter-Drinfeld categories — representation theory

A left-left Yetter-Drinfeld module M over H: left H-module (action ▸) AND
left H-comodule (coaction δ: M → H ⊗ M) with compatibility
**δ(h ▸ m) = h_1 m_{-1} S(h_3) ⊗ (h_2 ▸ m_0)**.

Category ^H_H YD of YD modules is **braided monoidal**.

**Fundamental theorem** (Majid; Yetter): **^H_H YD ≅ Rep(D(H))** as
braided monoidal categories. Braiding **c_{M,N}: M⊗N → N⊗M** given by
**c(m ⊗ n) = (m_{-1} ▸ n) ⊗ m_0**.

Equivalently: **^H_H YD ≅ Z(Rep H)**, the Drinfeld center of the tensor
category of H-modules — deep connection to TQFT data via Müger 2003 +
Etingof-Nikshych-Ostrik 2005.

### 1.3 Universal R-matrix → braid group action

For V ∈ Rep(D(H)), assignment σ_i ↦ id^(i-1) ⊗ c_{V,V} ⊗ id^(n-i-1)
extends to representation of the **n-strand Artin braid group B_n** on
V^⊗n, satisfying Artin relations:
- **σ_i σ_j = σ_j σ_i** when |i-j| ≥ 2
- **σ_i σ_{i+1} σ_i = σ_{i+1} σ_i σ_{i+1}**

**B_n is INFINITE for n ≥ 2** (no torsion, Dehornoy ordering). This is
the structural property substrate would want — chained bindings cannot
collapse to a finite alphabet.

**Joyal-Street 1993** (*Adv. Math.* 102) formalized braided tensor
categories.

### 1.4 Concrete finite-group examples

**Dijkgraaf-Pasquier-Roche 1990**: irreps of D(k[G]) classified by pairs
(C, ρ) where C is conjugacy class of G and ρ is irrep of centralizer
C_G(g) for any g ∈ C. Dimension = |C| · dim ρ. Sum of dim² = |G|².

- **Abelian G**: every conjugacy class is singleton; irreps are
  G × Ĝ, all 1-dimensional. "Pointed" modular category.
- **(Z/2)^m**: irreps of D(k[(Z/2)^m]) are pairs (a, χ) with a ∈ (Z/2)^m
  and χ a character — 2^m × 2^m = **4^m** of them; R-matrix valued in ±1.
  **Strictly richer than Walsh** (which only sees ±1 pairing once)
  because YD modules carry two labels (module + coaction grading).
- **Dihedral D_n**: irreps of D(D_n) dimensions 1 or 2; sum to 4n².
- **Symmetric S_n**: rich Frobenius-Schur structure (Iovanov-Mason-Ng
  arXiv:1604.02378).
- **S_3 (smallest non-abelian)**: D(k[S_3]) is 36-dim algebra with 8
  irreps of dimensions {1,1,2,2,3,3,2,2}.

### 1.5 VSA literature on Hopf-algebraic / Drinfeld-double binding

**The most important meta-finding from lit scan**: VSA literature has
**ESSENTIALLY NO Drinfeld double work**.

- **Plate HRR** (1995): circular convolution on R^n; underlying algebra
  k[Z_n] commutative cocommutative. D(k[Z_n]) ≅ k[Z_n × Z_n] still
  commutative — HRR is sub-structure of abelian quantum double, gains
  NOTHING braided from doubling.
- **Aerts-Czachor-De Moor** (arXiv:0710.2611): HRR-style binding in
  Clifford / geometric algebra. Notes: "Variable bindings correspond to
  two different representations of (Z/2)^n." — exactly the Walsh-closure
  problem.
- **Schlegel-Neubert-Protzel 2022** (arXiv:2001.11797): VSA comparison.
  None of the 11 binding operators are Hopf-algebraic in the
  quasitriangular sense.
- **Shaw-Spivak 2025** (arXiv:2501.05368): "Developing a Foundation of
  VSAs Using Category Theory." Only ~12 hits for "category theory + VSA"
  on Google Scholar. **Confirms Drinfeld-double approaches to VSA
  binding are essentially unexplored.**
- **Raff et al. NeurIPS 2024** (arXiv:2410.22669): Walsh-Hadamard linear
  VSA — stays in (Z/2)^d world.

**This is a substrate-novel research direction**, mathematically legitimate
and unexplored in the VSA literature.

### 1.6 Multi-hop reasoning — the critical caveat

The lit scan's CRITICAL FINDING for substrate (per [[feedback-no-smoke]]):

> "Concrete *unitary* braid representations from finite-group quantum
> doubles (D(k[G]) with G finite) have **FINITE IMAGE** in U(V^⊗n) for
> many G, because k[G] is finite-dimensional. E.g., for G = (Z/2)^m the
> R-matrix gives a representation of B_n through the symmetric group up
> to ±1 phases — **depth growth is logarithmic at best**."

**This is the substrate-relevant catch.** R13's premise was that braided
binding gives depth-unlimited chains because B_n is infinite. But for
D(k[G]) with FINITE G, the action factors through a finite quotient.
**Substrate still hits finite-depth collapse**, just at a different
boundary than XOR.

To get genuinely infinite-order monodromy, lit scan recommends:
- **q-deformed U_q(g)** (infinite-dimensional; doesn't fit fixed N)
- **Twisted D^ω(k[G])** with nontrivial 3-cocycle ω (Dijkgraaf-Pasquier-
  Roche): adds nontriviality without leaving bipolar habitat
- **Modular categories from non-semisimple D(H)**: R-matrix has
  continuous q-parameters

### 1.7 Anyonic / topological connections (foundational materials analog)

**Kitaev 1997/2003** (arXiv:quant-ph/9707021): the **quantum-double
lattice model D(G)** on a lattice. For G = Z/2 this is the **toric code**;
for non-abelian G one gets universal-for-quantum-computation anyon models
(G = S_3 rich but non-universal; G = S_5 universal).

**Anyonic charges of D(G)-lattice model are exactly irreps of D(k[G])** —
the (conjugacy class, centralizer-irrep) pairs from §1.4.

**Rowell-Wang 2017** (arXiv:1705.06206) "Mathematics of Topological
Quantum Computing": ribbon and modular categories give computational
substrate; Reshetikhin-Turaev 1991 gives 3-manifold invariants.

**Substrate-relevance**: anyon braiding is **topologically protected** —
small geometric perturbations of braid path don't change the unitary.
For a software substrate, "protection is symbolic, not geometric":
preserve braid word → get exact unitary action. Structurally different
from FHRR / Clifford where result depends on continuous phases.

### 1.8 Implementation considerations

**Storage at N=4096**:
- D(k[G]) algebra dimension |G|² ≤ 4096 → |G| ≤ 64
- R-matrix has |G|⁴ entries; for strict embedding |G|⁴ ≤ 4096² gives
  |G| ≤ 8
- D(k[S_3]) (G=S_3, |G|=6): algebra 36-dim, R-matrix 1296 entries —
  comfortably substrate-embedded
- D(k[(Z/2)^3]) (G=(Z/2)^3, |G|=8): algebra 64-dim, R-matrix exactly
  **4096 entries = substrate-sized**

**R-matrix computation**: for group-like H sparse explicit tensor;
for non-group-like H generally hard (cf. arXiv:math/0005049 on
automated R-matrix construction in Mathematica).

### 1.9 The honest research-direction question

Lit scan's bottom line:

> "The mathematics is rich, the substrate connection through D(k[G]) is
> mechanically plausible but technically constrained, and the **genuinely
> interesting direction — q-deformed U_q(g) bindings — may be a better
> next probe than D(H) for finite H**."

So R13 as posed (D(H) for finite H) has structural limitations. The
substrate-relevant question is more like R13-prime: **q-deformed
U_q(sl_2) at generic q for substrate binding**. This is research that
hasn't been done in the VSA literature AT ALL.

---

## Pass 2 — Substrate-specific drill

### 2.1 The minimal D(H) upgrade for substrate

The lit scan identified two candidate D(H) constructions that fit
substrate at N=4096:

**Candidate A: D(k[S_3])** — smallest non-abelian case
- Algebra dim: 36; embed as 36 × 113-dim blocks in N=4096
- Irreps: {1,1,2,2,3,3,2,2}, total 36 (=|G|²)
- R-matrix: 36 × 36 = 1296 entries
- Braiding has nontrivial 2-dim and 3-dim irreps; non-finite image more
  likely than D(k[(Z/2)^m])
- Substrate-novel synthesis: never tried in VSA literature

**Candidate B: D(k[(Z/2)^3])** — substrate-sized abelian double
- Algebra dim: 64; embed directly
- Irreps: 4^3 = 64, all 1-dim (abelian)
- R-matrix: 4096 entries = **exactly N**
- Braiding has finite image (abelian; ±1 phases at best)
- Substrate-coherent (preserves bipolar ±1 habitat) but with finite
  image — UNLIKELY to solve depth collapse

**Candidate C: D^ω(k[(Z/2)^3]) twisted by 3-cocycle ω**
- Twist by ω ∈ H³((Z/2)^3, U(1)) introduces phase nontriviality
- Same dimension as Candidate B but richer braiding
- Lit scan suggested as bipolar-habitat-preserving non-abelian-like
  construction

**Top recommendation per lit scan**: **Candidate A (D(k[S_3]))** as the
smallest non-trivially-nonabelian quantum-double; produces non-modular
but braided category; "minimum viable substrate primitive."

### 2.2 The depth-collapse honest assessment

For D(k[S_3]) braid representation:
- B_n maps to U(V^⊗n) via R-matrix action
- V = 36-dim regular rep of D(k[S_3])
- Image is contained in the symmetric group on certain orbits times
  signs — **finite quotient of B_n**

**Quantitative depth-collapse prediction**:
- For abelian D(k[(Z/2)^3]): finite image of order ~2^k → collapse at
  depth O(k) ≈ O(log |G|) = O(3)
- For non-abelian D(k[S_3]): finite image of larger order, but still
  finite → collapse at depth perhaps 20-50
- For genuinely infinite image: need q-deformed U_q(sl_2)

**Honest read**: D(k[S_3]) might extend multi-hop depth from current
~25 (R8 finding) to ~50-100. Modest improvement, not the unlimited-
depth substrate fantasy.

### 2.3 The q-deformed direction (substrate-novel R13-prime)

Per lit scan's bottom-line recommendation: **U_q(sl_2) at generic q
(not a root of unity) gives infinite-order braid representations**.
This is the genuinely depth-unlimited binding.

**Substrate-applicable U_q(sl_2)**:
- Infinite-dimensional algebra; needs truncation to fit N=4096
- Standard truncation: take spin-j representation at j = N/4 - 1 → fits
- R-matrix becomes a continuous unitary depending on q parameter
- Braid representations are now in U(V^⊗n) with continuous parameters

**This is a substrate-novel research direction**. The lit scan flagged
ZERO published VSA work on q-deformed binding.

**Substrate-prediction**: depth-collapse pushed from O(log |G|) (finite D)
to **continuous (no finite collapse)**. But noise behavior matches
Clifford / FHRR — the depth improvement comes from algebraic structure,
not noise resilience.

### 2.4 Independent rescue ranking for R13

| Rank | Candidate | Mechanism | P(substrate gains) | Implementation |
|---|---|---|---|---|
| **1** | **D(k[S_3])** — smallest non-abelian double | Braided binding via S_3 quantum double | **30-45%** | 36-dim algebra in N=4096; R-matrix 1296 entries |
| **2** | **D^ω(k[(Z/2)^3])** twisted by 3-cocycle | Substrate-coherent (bipolar) with phase nontriviality | **20-35%** | 64-dim algebra; same scale as untwisted |
| **3** | **U_q(sl_2) truncated** — q-deformed (substrate-novel) | Continuous q gives infinite-order braid | **40-55%** | spin-j truncation at j=N/4-1 |
| **4** | **D(k[Q_8])** — quaternion group double | Smallest non-abelian non-symmetric | **25-40%** | |Q_8|²=64-dim |
| **5** | **D(k[D_4])** — dihedral group double | Mid-complexity non-abelian | **25-40%** | 64-dim |
| 6 | D(k[(Z/2)^3]) untwisted | Abelian (collapse-bound) | 5-15% | Substrate-sized R-matrix |
| 7 | RSP-equivalent finite-image variants | All finite-image equivalent at depth | similar to #6 | |
| 8 | Twisted U_q at root of unity | Modular category, finite | 30-50% but smaller scale | |

**Top recommendation: Candidate 3 (U_q(sl_2) at generic q)** because it
genuinely escapes finite-image collapse, with **Candidate 1 (D(k[S_3]))**
as the substrate-coherent fallback if q-deformation proves too
implementation-heavy.

---

## Specific experimental design (pseudocode)

**Note**: this is forward-routing research; the experimental design is a
PROPOSAL for if/when substrate's multi-hop work moves beyond R8 candidates.

**Experiment**: `wave14r_R13_drinfeld_v1` — minimal D(H) binding test

```text
config:
  N = 4096
  num_facts = 100
  chain_depth_sweep = [5, 10, 25, 50, 100]
  seeds = [7, 17, 23, 31, 41]
  candidates = ['D_S3', 'Dω_Z2_3', 'U_q_sl2']

setup_per_seed(seed, candidate):
  # Construct D(H) algebra + R-matrix
  if candidate == 'D_S3':
    G = S_3  # symmetric group on 3 elements
    algebra = D_k_G(G)  # 36-dim
    R = drinfeld_R_matrix(G)  # 36 × 36 dense
    embed_in_N = block_diagonal_embed(algebra, N=4096, blocks=113)
  elif candidate == 'Dω_Z2_3':
    G = (Z/2)^3
    cocycle_omega = nontrivial_3_cocycle(G)  # H^3(G, U(1))
    algebra = D_omega_k_G(G, omega)  # 64-dim twisted
    R = drinfeld_R_omega(G, omega)  # 64 × 64
    embed_in_N = block_diagonal_embed(algebra, N=4096, blocks=64)
  elif candidate == 'U_q_sl2':
    j_max = N // 4 - 1  # spin-j truncation
    q = exp(i * pi / 5)  # generic q (not root of unity)
    algebra = U_q_sl2_truncated(j_max, q)
    R = R_matrix_U_q_sl2(j_max, q)

storage_construction:
  # Encode facts using braided binding via R-matrix
  for fact_idx in range(num_facts):
    entity = sample_entity_from_algebra()
    relation = sample_relation_from_algebra()
    binding = R_braid(entity, relation, R_matrix)
    pool.append((fact_idx, binding))

multi_hop_chain(start, chain_length, R_matrix):
  current = start
  for step in range(chain_length):
    next_relation = pick_relation(step)
    current = R_braid(current, next_relation, R_matrix)
  return current

evaluate_chain_recovery(chain_target, retrieved):
  # Use Drinfeld-double cleanup operator (or fallback to Hopf-algebra
  # inner product if D-specific cleanup unavailable)
  return cleanup_accuracy(retrieved, expected=chain_target)

per_seed_per_depth(seed, candidate, depth):
  W, R_matrix = setup_per_seed(seed, candidate)
  accuracies = []
  for trial in range(100):
    start = random_fact_in_pool()
    chain_target = simulate_correct_chain(start, depth)
    retrieved = multi_hop_chain(start, depth, R_matrix)
    accuracies.append(evaluate_chain_recovery(chain_target, retrieved))
  return mean(accuracies)

main:
  results = {}
  for candidate in candidates:
    for depth in chain_depth_sweep:
      acc_per_seed = [per_seed_per_depth(seed, candidate, depth)
                      for seed in seeds]
      results[(candidate, depth)] = (mean(acc_per_seed), std(acc_per_seed))

verdict_logic:
  PASS iff (any candidate clears depth-25 threshold):
    accuracy[depth=25] >= 0.40 (substrate's current R8 prediction)
    AND accuracy[depth=50] >= 0.20

  STRONG PASS iff (candidate gives >25 depth without collapse):
    accuracy[depth=50] >= 0.40 AND accuracy[depth=100] >= 0.20

  KILL iff: all candidates collapse before depth=25 (no improvement
    over current substrate binding)
```

**Smoke test**: N=512, S_3 only, depth=10, 1 seed. Target ~30s. Oracle:
algebra construction succeeds; R-matrix satisfies YBE numerically.

**Self-test (4 synthetic cases)**:
- Trivial binding (R=identity): predict collapse at depth 1.
- Pure XOR baseline: predict collapse at substrate's known boundary.
- Idealized D(k[S_3]): predict modest improvement to ~50.
- Theoretical infinite-depth (perfect U_q): predict accuracy preserved
  through depth=100+.

**Wall budget**: ~30 min per candidate at full scale; 3 candidates =
1.5 hr total. Smoke ~5 min total.

---

## Materials analog (load-bearing — Kitaev's toric code IS D(Z/2))

**The mapping is direct and physically realized**:

**Kitaev 2003** (arXiv:quant-ph/9707021) showed that the quantum-double
model **D(G) on a 2D lattice** has:
- Ground states = topological subspaces protected against local
  perturbations
- Excitations = anyons whose types are exactly irreps of D(k[G])
- Braiding of anyons = R-matrix action on excitation subspace

For G = Z/2: this is the **toric code**, the canonical topological
quantum error-correcting code.

For non-abelian G: braiding anyons performs **topological quantum
computation** — gates are unitaries determined by braid word, not by
geometric path.

**Substrate-prediction consequence (load-bearing)**:

If substrate adopts D(k[S_3]) binding, the substrate IS a software
simulation of an S_3 quantum-double lattice model. Stored facts =
anyonic excitations; chained binding = anyon braiding; chain depth =
braid word length.

**Predicted topological protection**: in the physical anyon model,
braid-word preservation is topologically guaranteed (small geometric
perturbations don't change result). For software substrate, the
analog is: as long as the **symbolic braid word** is preserved across
noisy operations, the result is exact. This is QUALITATIVELY
DIFFERENT from FHRR / Clifford where small phase perturbations
accumulate over depth.

**However, the honest caveat**: substrate's noise is NOT geometric
(it's value-level). The topological protection argument transfers
only if substrate operations preserve braid words symbolically — a
condition stricter than continuous noise tolerance.

**Spin-glass Z/2 gauge theory analog**: BSC bipolar substrate maps
to Z/2 spins → quantum-double upgrade to D(k[(Z/2)^m]) gives
**Z/2 gauge theory on top of substrate**. The gauge fields are
the additional D(H) generators; their nontrivial commutation
relations are precisely the braided structure.

---

## Falsifiable prediction

**Primary prediction (Candidate 1, D(k[S_3])):**

At N=4096, num_facts=100, chain_depth_sweep through 100, 5 seeds:

- **Depth 25**: accuracy ≈ 0.40 (matches R8 FHRR/hybrid prediction;
  small improvement)
- **Depth 50**: accuracy **0.15-0.30** (modest extension via braided
  binding; finite image still kicks in)
- **Depth 100**: accuracy < 0.10 (finite-image collapse)
- **Honest read**: D(k[S_3]) extends multi-hop depth modestly (×1.5-2)
  but does NOT solve the depth problem.

**Stress prediction (Candidate 3, U_q(sl_2)):**

If implementable at substrate scale:
- **Depth 25**: accuracy ≈ 0.50 (cleaner algebra than D(k[S_3]))
- **Depth 50**: accuracy **0.35-0.50** (continuous q escapes finite
  image)
- **Depth 100**: accuracy **0.20-0.35**
- **Honest read**: U_q(sl_2) at generic q gives the genuinely
  depth-unlimited binding R13 hoped for. But implementation is
  substantially harder than D(k[S_3]).

**Kill criterion**: if D(k[S_3]) and U_q(sl_2) both collapse before
depth=25 across 3 of 5 seeds, **D(H)-based binding is NOT productive
for substrate**. R13 closes ❌; multi-hop rescue stays with R8's
FHRR/hybrid recommendations.

**Falsifier for substrate-novel claim**: if a published VSA paper
emerges using D(H) binding before substrate's experiment lands,
substrate's novelty claim weakens. Lit scan said zero such papers
exist as of 2026-05-21.

**Honest probability estimates**:
- P(D(k[S_3]) gives any improvement over R8's FHRR baseline) ≈
  **30-45%**
- P(U_q(sl_2) implementable in substrate at N=4096) ≈ **40-60%**
- P(U_q(sl_2) gives depth-100 viable multi-hop) ≈ **20-35%**
- P(R13 produces substrate-shipping capability) ≈ **20-35%**
- P(R13 produces substrate-novel publishable math finding) ≈ **60-80%**
  (no prior VSA-Drinfeld-double work; the bridge itself is publishable)

---

## Citations

1. **Drinfeld (1986). "Quantum Groups."** *Proc. ICM Berkeley 1986*,
   AMS 1987, pp. 798-820.
   — Original D(H) construction.

2. **Joyal, Street (1993). "Braided tensor categories."** *Adv. Math.*
   102:20-78.
   — Foundational braided monoidal category paper.

3. **Majid (1995). *Foundations of Quantum Group Theory.* CUP.**
   — Standard textbook; Ch. 7 on quantum doubles.

4. **Kassel (1995). *Quantum Groups.* Springer GTM 155.**
   — Textbook proof of YD ≅ Rep(D(H)).

5. **Dijkgraaf, Pasquier, Roche (1990). "Quasi Hopf algebras, group
   cohomology, and orbifold models."** *Nucl. Phys. B Proc. Suppl.*
   18B:60-72.
   — Twisted D^ω(G) and irrep classification.

6. **Kitaev (1997, published 2003). "Fault-tolerant quantum computation
   by anyons."** arXiv:quant-ph/9707021.
   — **Load-bearing materials analog**: D(G) lattice model / toric
   code; anyonic charges = irreps of D(k[G]).

7. **Reshetikhin, Turaev (1991). "Invariants of 3-manifolds via link
   polynomials and quantum groups."** *Invent. Math.* 103:547-597.
   — Topological invariants from quantum groups; foundational for
   modular category.

8. **Mason, Ng (2005). "Representations of quantum doubles of finite
   group algebras and the Yang-Baxter equation."** arXiv:math/0511072.
   — Concrete computations for substrate-applicable G.

9. **Rowell, Wang (2017). "Mathematics of topological quantum
   computing."** arXiv:1705.06206.
   — Modern survey; modular categories for computation.

10. **Schlegel, Neubert, Protzel (2022). "A comparison of vector
    symbolic architectures."** AI Review 55:4523-4555.
    arXiv:2001.11797.
    — Confirms VSA literature has NO Drinfeld-double binding work.

11. **Shaw, Spivak et al. (2025). "Developing a Foundation of Vector
    Symbolic Architectures Using Category Theory."** arXiv:2501.05368.
    — Category-theoretic VSA foundation; flags Drinfeld doubles as
    unexplored.

---

## Routing

- **Experiment Dev**: R13 is **forward-routing, low urgency** vs
  Bet B / multi-hop / Bet F. Substrate-novel territory. Recommended
  experimental design (Candidate 1 D(k[S_3]) + Candidate 3 U_q(sl_2))
  is ready but should NOT be queued until top-priority experiments
  complete. **No immediate action required.**

- **Strategy**: this note proposes:
  - cap_map row addition (forward-routing): "Drinfeld-double / quantum-
    group binding for multi-hop reasoning" at 🔬 with substrate-novel
    math caveat
  - HONEST framing on the finite-image limitation: D(H) for finite H
    does NOT escape finite-image collapse; the genuinely depth-unlimited
    direction is U_q(g) which is implementation-heavy
  - Connection to existing wave13 Hopf-algebra work: D(H) is the
    quantum-group extension; wave13's framework already considered
    this direction at some level
  - The materials analog (Kitaev D(G) lattice = toric code) is
    load-bearing for any future substrate work on topologically
    protected memory primitives

- **Research (this session, future cycles)**: R13 closes ✅ with the
  honest substrate-novel-math + finite-image-caveat finding. If
  Strategy wants to pursue R13-prime (U_q(sl_2) substrate binding),
  that's a follow-up research question. **R14 (Tomita-Takesaki) and
  R15 (Steenrod) remain open** for future cycles.

**HONEST FINAL NOTE**: R13's substrate-applicability is **20-35%** —
the math is rich and substrate-novel, but the structural limitation
(finite-image braiding from finite-G doubles) means D(k[G]) doesn't
deliver the depth-unlimited binding R13 was hoping for. The genuinely
exciting direction (U_q(g) infinite-dimensional quantum groups) is
research-grade, not engineering-grade. R13 has value as a published
substrate-novel-math bridge (60-80% probability of publishable
finding), but should NOT be prioritized over Bet B / Bet F / multi-hop
FHRR experiments per [[feedback-no-papers-product-only]] — substrate's
focus is product, not papers.
