# Buried-treasure research directions (post pure-math audit)

The unbiased pure-math survey on 2026-05-18 returned 5 buried-treasure
candidates — mathematical structures that have closed-form operations
no one has wired into HDC/VSA but that look algorithmically tractable.
This doc captures them all so we don't lose context.

The framing rule (now in memory as `feedback-unbiased-research`):
*describe what the math does first, AI mapping is OUR synthesis.*

## 1. Connes-Kreimer rooted-tree Hopf algebra → **Wave 14**

See dedicated design doc: [wave14_connes_kreimer_design.md](wave14_connes_kreimer_design.md).

Native tree decomposition via coproduct that cuts trees into (subtree-above,
subtree-below) pairs with closed-form combinatorial rules. The Hopf
algebra I should have started with for the decomposition question; H_4
was the wrong Hopf algebra.

Status: design doc written, prototype pending. Estimated 1-2 weeks for
Phase A toy.

## 2. Free probability transforms → **Wave 15** (proposed)

The R-transform R_a(z) and S-transform S_a(z) linearize free additive
and multiplicative convolution respectively:
- R_{a+b}(z) = R_a(z) + R_b(z) for free additive convolution
- S_{ab}(z) = S_a(z) · S_b(z) for free multiplicative convolution

Computed via Cauchy transform G(z), then R(z) = G^{-1}(z) − 1/z.

**Why this might matter for HDC:** modern HDC uses high-dim random
vectors as atoms. As N → ∞, these are LITERALLY "free" in Voiculescu's
sense (this is the central limit theorem of free probability). So
operations on HDC hypervectors at large N ARE non-commutative free
random variable operations.

**Concrete capabilities to chase:**
- Theoretical bound on bundle capacity (how many atoms can be bundled
  before retrieval fails) — currently empirical (Frady-Kleyko-Sommer
  gives N/(2·SNR) bound; free probability could give a tighter one)
- Optimal weight decay schedules derived from spectral analysis
- Closed-form interference predictions for arbitrary substrate
  + binding combinations

**Design sketch:**
1. Pick FHRR or BSC substrate.
2. Apply Voiculescu's R-transform machinery to compute the spectral
   distribution of bundled atoms.
3. Derive analytic prediction of retrieval accuracy vs K (number bundled).
4. Compare to empirical retrieval curve.
5. If theory matches: extend to predict optimal hyperparameters for
   our other waves.

**Cost:** 1-2 weeks. Requires implementing R-transform numerically
(Cauchy transform inverse) but the math is standard. References:
Voiculescu 1991, Speicher 1998, Mingo-Speicher "Free Probability and
Random Matrices" 2017.

**Why it's exciting:** we'd have THEORETICAL guarantees on HDC
operations for the first time, not just empirical curves.

## 3. Tomita-Takesaki modular flow → **Wave 16** (proposed)

For any finite-dimensional algebra A with a faithful state ω, you get
a CANONICAL one-parameter automorphism group σ_t = Δ^{it} (·) Δ^{-it}
where Δ comes from polar decomposition of the involution S(a) Ω = a* Ω.
Plus an anti-linear duality J: A → A' that maps the algebra to its
commutant.

**Why this might matter:** the modular flow is "intrinsic time / intrinsic
ordering" extracted from algebra + state alone. No learned positional
embeddings needed — the algebra structure itself defines a canonical
flow.

**Concrete capabilities to chase:**
- Replace learned positional encoding in a sequence model with
  modular flow
- Use J to define "dual hypervectors" — observables and their dual
  observables form pairs naturally
- KMS condition gives a thermodynamic-like "equilibrium" for HDC
  representations

**Design sketch:**
1. Pick a small finite-dim algebra (e.g., matrix algebra M_n(C)).
2. Define a faithful state ω (a vector ψ such that ⟨ψ|·|ψ⟩ is positive
   on positive elements).
3. Compute the modular operator Δ and involution J.
4. Apply σ_t for various t — get a continuous family of "time-shifted"
   automorphisms.
5. Test: does σ_t replace positional encoding usefully in a sequence
   prediction task?

**Cost:** 2-3 weeks. Tomita-Takesaki for finite-dim algebras is
mechanical but the engineering wrappers are real. References: Bratteli-
Robinson "Operator Algebras and Quantum Statistical Mechanics" 1979;
Takesaki "Theory of Operator Algebras" vol. II.

**Why it's exciting:** "canonical time from data" is a Real Thing
that's never been exported from physics to AI.

## 4. Steenrod operations → **Wave 17** (proposed, lower priority)

The Steenrod algebra acts on mod-p cohomology by unary stable
operations Sq^i (and P^i, β) satisfying Adem relations. These are
non-trivial unary operations beyond ring multiplication; they
distinguish topological spaces that have the same cohomology ring.

**Why this might matter:** HDC has bind (binary), bundle (n-ary), and
unbind/cleanup. We have NO unary refining operations. Steenrod is a
class of unary operations whose existence we don't currently exploit.

**Concrete capabilities to chase:**
- Refine HDC representations beyond what binding/bundling captures
- Detect hidden structure in hypervectors that ring multiplication
  doesn't see

**Honest assessment:** the mapping to HDC is the LEAST obvious of the
five. Steenrod operations are deeply tied to topology and mod-p
arithmetic. Could be hugely valuable or a complete miss.

**Cost:** research-grade (4-8 weeks just to find the right HDC
analog). References: Hatcher "Algebraic Topology" Ch. 4; Steenrod
1962 monograph.

**Priority:** Wave 17 (after CK and Free Probability prove out).

## 5. R-matrices / Yang-Baxter braiding → **already covered**

The 2024 Renner et al. Nature MI paper extends resonator networks to
non-commutative bindings. Our Wave 13.3 already uses resonator network
machinery for H_4. The R-matrix approach is a special case of "binding
that doesn't commute"; quantum groups at root of unity give explicit
finite-dim R-matrices.

This is the SAME treasure as Wave 13.3, just with explicit R-matrix
parameterization. Status: subsumed into Wave 13.3 + future Wave 13.4
(D(S_3) Drinfeld double will have an explicit R-matrix).

## Priority order (proposed for next session(s))

1. **Wave 14: Connes-Kreimer trees.** Most concrete, addresses the
   problem H_4 didn't solve. 1-2 weeks Phase A.
2. **Wave 15: Free probability transforms.** Gives THEORETICAL
   foundations to HDC for the first time. 1-2 weeks.
3. **Wave 13.4: Drinfeld double D(S_3) with explicit R-matrix.**
   Continuation of the Hopf line; uses Wave 13.3's resonator
   infrastructure.
4. **Wave 16: Tomita-Takesaki modular flow.** Canonical positional
   encoding. 2-3 weeks.
5. **Wave 17: Steenrod-style unary operations.** Speculative;
   research-grade.

## What we've now uncovered

Going into this session, we had FHRR/BSC/SBC + standard binding/bundling
/cleanup. We're now planning:

- Wave 8 (Clifford G(2,0)) — non-commutative geometric algebra
- Wave 9 (MPS-shape) — tensor networks
- Wave 10 (RG-flow) — hierarchical depth without backprop
- Wave 11 (LDPC cleanup) — coding-theoretic capacity
- Wave 12 (qFHRR) — quantization
- Wave 13 (Hopf S_3 + H_4 + resonator) — non-commutative + non-cocommutative binding with working cleanup
- Wave 14 (Connes-Kreimer) — tree decomposition
- Wave 15 (Free probability) — theoretical foundations
- Wave 16 (Tomita-Takesaki) — canonical positional encoding
- Wave 17 (Steenrod operations) — unary refining operations

This is a comprehensive substrate exploration that would be unusual
for any HDC research program. Most published work covers 1-2 substrates;
we'll have 10+ tested at varying depth.
