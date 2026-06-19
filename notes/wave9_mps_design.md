# Wave 9: Matrix Product States (MPS) VSA — Design

Reference: substrate audit, 2026-05-18. The audit's verdict on MPS:
"Highest upside-to-strangeness ratio in the list. Tensor-network /
condensed-matter machinery is the genuine materials-science analogue."

## What is an MPS?

A Matrix Product State (MPS) represents a high-dimensional tensor as a
product of smaller tensors along a chain. For a tensor with physical
indices `(i_1, i_2, ..., i_L)` over alphabet of size `d`, the MPS
factorizes:

```
T_{i_1, i_2, ..., i_L} = sum over bonds A^{i_1}_{a_0,a_1} · A^{i_2}_{a_1,a_2} · ... · A^{i_L}_{a_{L-1},a_L}
```

where each `A^i` is a small matrix of shape `(χ, χ)` (bond dim χ), and
the sum is contracted over the intermediate bond indices.

The full tensor has `d^L` elements; the MPS form has only
`L · d · χ²` parameters. For χ=16, L=12, d=4: 12·4·256 = 12,288 params
vs 4^12 = 16.7M dense.

## Why MPS for HDC

Three reasons the audit highlighted:

1. **Natural sequence encoding.** An MPS chain matches the 1D structure
   of byte sequences directly. Each site = one byte position.

2. **Controllable expressivity via bond dim χ.** Bigger χ = more
   expressive (closer to dense); smaller χ = more compressed (lossier).
   Direct knob on the bias-variance tradeoff.

3. **DMRG sweep training as a non-backprop alternative.** Density
   matrix renormalization group is the standard MPS optimization
   algorithm, sweeping left-right then right-left, updating one site at
   a time via SVD. Maps to layer-wise local updates → fits the
   brain-inspired no-backprop framing.

## Concrete substrate design (first prototype)

For our byte-LM at N_effective ≈ 4096 expressible features:

- **L = 12 sites, d = 4, χ = 16.** Per-atom params: 12 · 4 · 16² = 12,288.
  Full state space: 4^12 = 16.7M dimensional (much bigger than FHRR's
  4096, but compressed).

- **Atoms:** Each byte (256) and each position (K=4) is a random
  initial MPS with the above shape, normalized so total state has
  L2-norm 1.

- **Binding (MPS Hadamard product):** Element-wise multiplication of
  two MPS in the full state space. Implemented site-by-site: the bond
  dim of the product is χ² = 256. SVD-truncate back to χ' = 16 (or
  keep χ=32 for slightly better precision). This costs O(L · χ⁶) per
  bind, which for our params is ~100M flops — fine on CPU.

- **Bundling (sum + truncate):** Direct-sum of MPS bonds, doubling χ
  to 32, then SVD-truncate back to χ=16. For K=4 bound atoms, this
  truncates after each summed pair to keep cost bounded.

- **Cleanup / similarity:** MPS inner product
  `<atom_v | query> = scalar` computed by tracing the contracted chain.
  Cost: O(L · χ³ · d) ≈ 200K flops — negligible.

- **W matrix:** Two options:
  (a) **Dense W** in the (d^L)-dim space — but 16M × 16M is huge.
      Won't fit.
  (b) **MPO (Matrix Product Operator) W** — represent W as a chain of
      operator tensors with operator bond dim. This is the natural
      tensor-network choice.

  For first prototype: keep W as dense over flattened MPS feature
  space. But that requires flattening MPS to a low-dim summary
  (e.g., contract with a fixed projection MPS to get a single scalar
  per "logical feature"). Net effect: we project MPS-bundled ctx to
  a dense 4096-dim feature vector via some learnable or fixed
  projection MPS. Then standard W operates on the 4096-dim features.

  **Simpler first cut:** flatten MPS atom to its dense d^L vector
  (just for first prototype), use this as the "hypervector." Yes, this
  is 16M dim per atom, but as a prototype it shows whether the MPS
  structure helps. We then optimize storage in a follow-up.

  **Even simpler:** keep the small MPS shape (L=12, d=4, χ=16), use
  a flattened (L·d·χ²) = 12288-dim parameter vector as the atom in
  every step. Binding/bundling operate on the MPS parameters
  directly (treating them as a flat vector). This is "MPS-shape
  parameters but flat-vector operations" — not a true MPS-VSA but
  a useful intermediate.

  Let's go with the simplest first prototype: flat 12,288-dim vector
  with random init from MPS construction, FHRR-style binding (elementwise
  multiply), standard Hebbian update. This tests "does MPS-shape
  initialization help?" rather than the full MPS-VSA claim.

  Then iterate to full MPS-VSA with contraction-based binding in a
  follow-up.

## Falsification criterion

For the simplest prototype:
- Best MPS-shape FHRR-style variant within ±0.05 bpc of FHRR (2.4994):
  **reject** — MPS shape alone doesn't help.
- Best MPS-shape variant ≤ 2.44: **support** — there's signal in the
  shape, follow up with full MPS-VSA contraction.

## Implementation effort breakdown

| Stage | Effort | Deliverable |
|---|---|---|
| Simplest prototype (MPS-shape param vector + standard ops) | 1-2 days | Runnable bpc number |
| MPS contraction binding (proper) | 3-5 days | True MPS-VSA bind |
| DMRG-sweep W training | 1 week | Non-backprop training story |
| MPO W operator | 1 week | Full TN architecture |

Today's deliverable: simplest prototype only.

## Library choice

For full implementation: `quimb` (Python, MPS-first). For prototype:
PyTorch tensor ops directly. Stick with PyTorch for now (no library
dependency, matches all our other experiments).

## What this experiment answers

The audit's framing: **does the MPS / tensor-network shape of an HDC
substrate give us low-rank expressivity that helps at byte-LM scale?**

Concretely:
- If yes (≤ 2.44 bpc): the tensor-network approach is a real lever;
  push on full DMRG training.
- If no (~ 2.50 bpc): the FHRR substrate is already near-optimal at
  this scale, and we're chasing diminishing returns. Pivot to depth
  (Wave 10).
