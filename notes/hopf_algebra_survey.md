# Three Hopf algebras for HDC: comparative survey

This doc compares three candidate Hopf algebras for HDC, ranked by
implementation tractability and expected research value. Each is a
distinct mathematical object with different capabilities — picking the
right one is half the research problem.

## At a glance

| Property | k[S_3] (Wave 13.1) | Sweedler H_4 (Wave 13.2) | D(S_3) (Wave 13.3) |
|---|---|---|---|
| Dimension | 6 | 4 | 36 |
| Algebra (mul) | Non-commutative ✓ | Non-commutative ✓ | Non-commutative ✓ |
| Coalgebra (Δ) | **Cocommutative (trivial)** | **Non-cocommutative ✓** | **Non-cocommutative ✓** |
| Δ rank | 1 (grouplike: Δ(g)=g⊗g) | **≤ 2 (genuinely non-trivial)** | **≤ |G|=6** |
| Antipode | g → g^{-1}, period 2 | period 4 | period 2 |
| R-matrix (braiding) | none | none | ✓ |
| Implementation cost | 1-2 days | 1-2 days | 3-5 days |
| Stacked for N=4096 | 682 copies | 1024 copies | 113 copies |
| Δ-cleanup useful? | NO (Δ is trivial) | **YES** | **YES** |
| Tests what | non-commutative bind | non-trivial Δ | full Hopf + R-matrix |

**Headline recommendation:** start with **Sweedler H_4** for Δ-cleanup
tests. k[S_3] only validates non-commutative binding (which is incremental
over our existing permutation-based VSA). D(S_3) is the most powerful but
also the most expensive.

## 1. k[S_3] — group algebra of the symmetric group

**Wave 13 Phase A (already implemented).**

**What it is:** Linear combinations of the 6 elements of S_3 (the
permutation group on 3 letters). Multiplication is group convolution.

**Hopf structure:**
- Algebra: group convolution (non-commutative because S_3 is non-abelian)
- Coalgebra: Δ(g) = g ⊗ g for each group element (**cocommutative** —
  same on both sides). Δ is "grouplike."
- Antipode: S(g) = g^{-1} (period 2: applying twice gives back g)

**What it tests:**
- Does non-commutative binding alone help at byte-LM scale?
- Is the simplest non-abelian case enough?

**What it CAN'T test:**
- Anything about comultiplication's value, because Δ here is trivial
  (cocommutative implies no structural decomposition benefit beyond
  what unbinding already gives).

**Why we still ran it:** establishes baseline for non-abelian binding.
If Phase A shows no advantage over FHRR/BSC, then the non-commutativity
of binding alone isn't doing useful work — and we should focus on
non-cocommutativity (the other two algebras) where the real Hopf benefits live.

## 2. Sweedler's H_4 — the smallest non-trivial Hopf algebra

**Wave 13.2 (recommended next).**

**What it is:** The unique 4-dimensional Hopf algebra that's neither a
group algebra nor a function algebra. It's the standard "first
non-trivial example" in Hopf algebra textbooks.

**Generators and relations:**
- g, x generate H_4
- g² = 1 (g is an involution)
- x² = 0 (x is nilpotent)
- g·x = -x·g (anticommutation)

**Basis:** {1, g, x, gx} (4-dim)

**Multiplication table (basis × basis):**
```
        1    g    x    gx
1     | 1    g    x    gx
g     | g    1   gx    x
x     | x   -gx   0    0
gx    | gx  -x    0    0
```

(Note: x·x = 0 and x·gx = 0 reflect x² = 0.)

**Comultiplication (THE KEY FEATURE):**
- Δ(1) = 1 ⊗ 1
- Δ(g) = g ⊗ g (grouplike, like in k[S_3])
- **Δ(x) = x ⊗ 1 + g ⊗ x** ← non-trivial, non-cocommutative
- Δ(gx) = gx ⊗ g + 1 ⊗ gx (derived from Δ(g)·Δ(x))

The Δ(x) formula is the genuinely new thing. It says: "if c contains
an x component, that x is a sum of (something-x bound to 1) plus
(g bound to something-x)." Reading Δ(c) tells you HOW x is distributed.

**Antipode:**
- S(1) = 1, S(g) = g, S(x) = -gx, S(gx) = x
- Period 4: S²(x) = -x, S⁴(x) = x. (Period 2 in the group case is
  insufficient for a Hopf to be a group algebra; H_4 is "twisted.")

**Why this matters for HDC:**

The rank of Δ on H_4 is at most 2 (Δ(x) has 2 terms, others have 1).
This means Δ-cleanup with SVD of Δ(c) (per the algorithm doc) needs
only rank-2 SVDs per slot — extremely cheap.

If we stack 1024 H_4 copies, total dim = 4096. Each slot's Δ is in
H_4 ⊗ H_4 = 16-dim space. Per-slot operations are tiny.

**Test design (Wave 13.2):**

1. **Verify non-cocommutativity:** Δ(x) ≠ σ·Δ(x) where σ swaps tensor
   factors. (Trivial check.)

2. **Δ recovery test:** generate a "bound" hypervector c = a*b where a
   and b are randomly chosen H_4 atoms. Compute Δ(c). SVD-decompose Δ(c)
   per slot. Top-rank components should reconstruct a, b (up to per-slot
   permutation).

3. **Constituent identification:** given a bundled c = sum_i a_i * b_i,
   does Δ-cleanup with SVD identify the (a_i, b_i) pairs better than
   exhaustive codebook search? Measure top-k pair recovery accuracy.

**If H_4 Δ-cleanup works:** validates the entire Hopf-VSA approach.
Move to Drinfeld double D(S_3) for the more powerful version.

**If it doesn't work:** the Δ structure is too small (only 4 dimensions
per slot). Drinfeld double's 36-dim slots may have enough capacity.

## 3. Drinfeld double D(S_3) — the "full" Hopf machinery

**Wave 13.3 (research-grade, deferred).**

**What it is:** The Drinfeld double construction D(G) is the
"quasi-triangular" Hopf algebra associated with G. It's the *quantum
double* — non-commutative AND non-cocommutative AND equipped with an
R-matrix (braiding structure).

**Dimension:** |G|² = 36 for G = S_3.

**Basis:** {(g, χ) : g ∈ S_3, χ ∈ Ĝ}, where Ĝ is the dual basis (linear
functionals on the group algebra).

**Multiplication (Drinfeld's twist):**
```
(g, χ) · (h, ψ) = (gh, χ_h · ψ)
```
where χ_h(x) = χ(h x h^{-1}) is the conjugation-shifted character.

**Comultiplication:**
```
Δ((g, χ)) = sum_{i+j=χ} (g, χ_i) ⊗ (g, χ_j)
```
where i+j=χ is the convolution decomposition of χ.

**R-matrix:** D(G) carries a canonical R ∈ D(G) ⊗ D(G) satisfying the
quantum Yang-Baxter equation R₁₂R₁₃R₂₃ = R₂₃R₁₃R₁₂. This R-matrix
gives **braided multiplication** — a stronger form of non-commutativity
where the order of operations is tracked algebraically.

**Why this is the "Cadillac" of Hopf-VSA:**

1. **All Hopf structure simultaneously.** Non-commutative bind,
   non-cocommutative Δ, well-defined antipode, AND R-matrix for braiding.
   Every Hopf-algebra property HDC could want.

2. **Topological quantum field theory connection.** D(G) defines
   topological invariants. If HDC operations respect this structure,
   our system is "topologically robust" — invariant under continuous
   deformations of the binding chain.

3. **Universal example.** Every modular Hopf algebra is a Drinfeld double.
   Whatever works for D(S_3) generalizes.

**Implementation complexity:**

Each (g, χ) requires tracking a group element AND a character. The
multiplication formula has a conjugation step (h x h^{-1}) which is
group-dependent. The R-matrix needs to be precomputed (it's a |G|² × |G|²
matrix). The Δ involves convolution of characters.

Honest estimate: 3-5 days for a working implementation, 1 more day for
test rig integration.

**Why we defer:** if Sweedler H_4 (Wave 13.2) doesn't show signal,
D(S_3) is unlikely to either — it has the same kind of non-cocommutative
Δ, just with more structure. Validate the simpler case first.

## Decision tree

```
Wave 13.1 (k[S_3]) result
├─ S_3 binds, non-commutativity gives signal (≥0.02 bpc advantage)
│  └─ Document as positive finding; non-commutative binding is real
└─ S_3 ≈ FHRR (no advantage)
   └─ Non-commutativity ALONE doesn't help; we need non-cocommutativity

Wave 13.2 (H_4) result (KEY DECISION POINT)
├─ H_4 Δ-cleanup outperforms naive (≥10% recovery improvement)
│  └─ Hopf approach is validated; push to Wave 13.3 for full power
├─ H_4 Δ works mathematically but no recovery advantage
│  └─ Δ is too small (4-dim); try D(S_3) for more structure (Wave 13.3)
└─ H_4 Δ implementation can't recover (algorithm issue)
   └─ Algorithm needs work; revisit Wave 13.2 design before D(S_3)

Wave 13.3 (D(S_3)) result
├─ D(S_3) Δ-cleanup substantially better
│  └─ Build full Hopf-VSA byte LM; this is publishable
└─ D(S_3) ≈ H_4 (no further advantage)
   └─ Hopf structure has hit its ceiling; document and move on
```

## What success looks like

Bare minimum (Wave 13.2): demonstrate that on a *toy* synthetic bind/
decompose task, Δ-cleanup recovers constituents at higher accuracy than
random-codebook search. This validates the entire premise.

Headline-worthy (Wave 13.3 + integration): byte-LM with Hopf-VSA
substrate matches or beats BSC baseline AND shows compositional-recall
advantage on a separate diagnostic task.

Both are 2-4 weeks out. The next 1-2 days deliver Wave 13.2.
