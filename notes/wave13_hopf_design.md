# Wave 13: Hopf algebra VSA — Design

Reference: substrate audit, 2026-05-18. Verdict:
"Speculative; no ML/HDC literature. Cost: very high (research-grade;
weeks-to-months just to formalize). Don't pursue yet — wait until
someone publishes a first attempt."

User explicitly requested this despite the audit warning. The user
will be that someone.

## Why Hopf algebras for HDC

A Hopf algebra H is exactly the algebraic structure for "operations
that can both combine and decompose":

- **Algebra structure** (multiplication μ: H⊗H → H): the natural BIND
- **Coalgebra structure** (comultiplication Δ: H → H⊗H): the natural
  DECOMPOSE — a brand-new VSA primitive that says "this hypervector
  encodes things bound from these pieces"
- **Antipode** (S: H → H): the natural INVERSE — perfect unbinding
- **Unit (1)** and **counit (ε)**: identity elements

VSA's commutative substrates (FHRR, BSC, HRR) handle binding fine but
have NO native decompose operation. Hopf algebras give us this for free.

## Simplest concrete instance: group algebra k[G]

For a finite group G, the group algebra k[G] is a Hopf algebra:
- Elements: formal linear combinations of group elements, sum_g c_g · g
- μ(a, b) = group convolution: (a * b)[g] = sum_h a[h] · b[h^{-1}g]
- Δ(g) = g ⊗ g (each group element is "grouplike")
- S(g) = g^{-1}
- ε(g) = 1
- 1 = e (group identity)

For abelian G (e.g., Z_n cyclic), this is COMMUTATIVE → reduces to HRR
(circular convolution). For NON-ABELIAN G, the group convolution is
NON-COMMUTATIVE → genuinely new.

**Smallest non-abelian group: S_3 (symmetric group on 3 letters),
|S_3| = 6.** Six elements: e, (12), (13), (23), (123), (132).
Multiplication table is 6×6 fixed.

## Wave 13 Phase A: S_3 group algebra VSA (this commit)

Substrate:
- N_total = 4096 effective dim, decomposed as 682 stacked S_3 group
  algebras, each 6-dim → 4092 ≈ 4096
- Atom = (682, 6) real tensor
- Per-site: 6-element coefficient vector in k[S_3]

Operations:
- **Binding (per-site group convolution):** for each of the 682 stack
  slots, compute group convolution. Cost: O(|G|²) per slot per atom
  pair = 36 mults per slot.
- **Bundling:** sum across K bound atoms, per-site L2-normalize
- **Antipode:** per-site permutation a → a' where a'[g] = a[g^{-1}]
- **Similarity:** flat inner product on (682, 6) → real number
- **Cleanup:** standard codebook nearest-neighbor

This is the SIMPLEST Hopf algebra VSA. It uses only the group-algebra
structure, not the full Drinfeld double. But it's a complete,
runnable prototype.

## Wave 13 Phase B: Drinfeld double D(S_3) (future)

D(S_3) has dimension |S_3|² = 36 (vs |S_3|=6 for plain group algebra).
Non-commutative AND non-cocommutative. Effort: ~1-2 weeks after
Phase A is validated.

If Phase A shows non-trivial signal (≤ 2.49 bpc on byte-LM with full
integration), Phase B is justified. If Phase A shows ≈ baseline, then
non-abelian group convolution doesn't help and the more elaborate
Drinfeld machinery probably won't either.

## Wave 13 Phase C: Quantum groups U_q(sl_2) (research-grade)

The "deepest" Hopf algebra. Has R-matrix structure giving braided
operations. Used in topological quantum field theory. **Probably
beyond what we can usefully implement at this scale.** Document as
future direction; don't commit to.

## Falsification (Phase A toy task)

Before committing to byte-LM integration:

1. **Atom recovery test:** generate 256 random atoms in k[S_3]^682, bind
   each with K=4 random "position" atoms, bundle, then unbind via antipode.
   Measure cleanup accuracy (top-1 byte recovery). Compare to FHRR at
   matched dim.

2. **Non-commutativity check:** verify that bind(a, b) ≠ bind(b, a) for
   random a, b (otherwise the algebra collapses to commutative and we
   gain nothing over HRR).

3. **Capacity scaling:** plot recovery accuracy vs number of items
   bundled (K=1, 4, 8, 16). If non-abelian binding has capacity
   advantage over commutative FHRR, this is where it should show.

## Phase A toy implementation (this commit)

The S_3 multiplication table:
```
        e    (12)  (13)  (23)  (123) (132)
e     | e    (12)  (13)  (23)  (123) (132)
(12)  | (12) e     (123) (132) (13)  (23)
(13)  | (13) (132) e     (123) (23)  (12)
(23)  | (23) (123) (132) e     (12)  (13)
(123) | (123)(23)  (12)  (13)  (132) e
(132) | (132)(13)  (23)  (12)  e     (123)
```

Indexed as [g_left][g_right] = g_result.

Convolution: (a * b)[g] = sum over (h, h') with h·h' = g of a[h] · b[h']

For per-site implementation, we precompute the convolution as a tensor
contraction.

## What the toy test answers

If S_3 group algebra binding has capacity advantage over FHRR at
matched dim:
- Phase B (Drinfeld double) becomes the obvious next step
- Phase B might give us the "decompose" operation we couldn't get otherwise
- Long-term: full Hopf VSA is a paper

If no advantage:
- Plain non-abelian binding isn't the source of any gap
- Either Drinfeld's twist matters specifically (test in Phase B)
- Or Hopf algebras don't help at our scale (move on)

Cost for Phase A toy: 1-2 days. This commit.
