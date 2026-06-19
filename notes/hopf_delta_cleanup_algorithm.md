# Δ-based cleanup algorithm for Hopf-VSA

This doc designs the algorithm that makes Hopf comultiplication
Δ: H → H ⊗ H useful as a VSA primitive. Without an efficient cleanup
algorithm, Δ is mathematical structure without computational payoff.

## The asymmetry standard VSA can't fix

| Question | Standard VSA |
|---|---|
| Is atom X bound in this hypervector? | O(N) inner product with X |
| What is bound to a known key K? | O(N) unbind with K^{-1}, then identify |
| **What atoms are bound here?** | **O(V × N) — test every codebook entry** |
| **What's the compositional structure?** | **no native op; must reconstruct via search** |

The last two rows are O(vocabulary × dim). For our 256-byte vocab this is
manageable, but for natural language with V ≥ 10K vocabulary, it's
expensive. For full compositional decomposition (nested structures),
it's combinatorially explosive.

## What Δ gives us — and what it doesn't

Comultiplication Δ takes a hypervector c ∈ H and produces a tensor
Δ(c) ∈ H ⊗ H, which lives in a space of dimension dim(H)². The structure
of Δ(c) encodes **which factor pairs c "looks like a binding of."**

Critical caveat: Δ alone doesn't return the constituents. It returns a
*tensor* that *contains information about* the constituents. Extracting
them is the cleanup problem in a new geometry.

## Algorithm: Slot-wise SVD decomposition of Δ(c)

The key insight is that for STACKED Hopf algebra substrates (e.g., 1024
copies of H_4 = 4096 total dim), Δ acts independently per stack slot.
Each slot's Δ(c_s) lives in a small space (dim(H_local)² = 16 for H_4),
so SVD per slot is cheap.

```
def hopf_delta_cleanup(c, atoms_codebook, Δ, num_stacks, dim_H_local):
    """
    Inputs:
      c:               (num_stacks, dim_H_local) — the hypervector to decompose
      atoms_codebook:  (V, num_stacks, dim_H_local) — codebook of V atoms
      Δ:               function that maps H → H ⊗ H (per-slot operation)
      num_stacks:      number of stacked Hopf algebras (e.g., 1024)
      dim_H_local:     dimension of local Hopf algebra (e.g., 4 for H_4)

    Output:
      ranked list of (atom_i, atom_j) pairs that are likely constituents
      of c, with scores.
    """
    # Step 1: per-slot Δ
    # Δ_c_per_slot has shape (num_stacks, dim_H_local, dim_H_local)
    Δ_c_per_slot = stack([Δ(c[s]).reshape(dim_H_local, dim_H_local)
                          for s in range(num_stacks)])

    # Step 2: per-slot SVD → rank-k factor pairs (k bounded by algebra structure)
    # For H_4: Δ has rank ≤ 2 on any element, so k=2 is enough.
    # For D(S_3): Δ has rank ≤ |G|=6.
    # Returns per-slot (U_s, S_s, V_s) where U_s, V_s are (dim_H_local, k).
    factors = batch_svd(Δ_c_per_slot, top_k=ALGEBRA_MAX_RANK)

    # Step 3: aggregate slot-wise factor evidence into a global score matrix
    # For each candidate pair (atom_i, atom_j) of codebook entries:
    #   compatibility[i, j] = sum_s, top_k <U_s[:, k], atom_i[s]> · <V_s[:, k], atom_j[s]>
    # This is the score "how much does (atom_i, atom_j) look like a constituent
    # decomposition of c when projected through Δ?"

    V = atoms_codebook.shape[0]
    scores = zeros(V, V)
    for k in range(ALGEBRA_MAX_RANK):
        # left_proj[i, s] = <U_s[:, k], atom_i[s]>
        left_proj = einsum('vsa,ska->vs', atoms_codebook, factors.U[:, :, k])
        right_proj = einsum('wsa,ska->ws', atoms_codebook, factors.V[:, :, k])
        # weighted by singular values
        weighted = left_proj * factors.S[:, k].sqrt()
        weighted_r = right_proj * factors.S[:, k].sqrt()
        scores += weighted @ weighted_r.T

    # Step 4: top-k pair returned (with thresholding)
    return top_pairs(scores, threshold)
```

## Complexity analysis

- Step 1 (per-slot Δ): O(num_stacks · dim_H_local²) = O(1024 · 16) = 16K ops for H_4
- Step 2 (batched SVD): O(num_stacks · dim_H_local³) for batched 4×4 SVD = 64K ops
- Step 3 (codebook projection per rank): O(V · num_stacks · dim_H_local · top_k)
  = O(256 · 1024 · 4 · 2) = 2M ops per Hopf rank
- Step 4: O(V²) scoring with thresholding

**Total: ~2-5M ops per cleanup query.**

Compare to naive codebook search: O(V · N) = O(256 · 4096) = 1M ops per
query for finding the SINGLE best match. But naive can't decompose
compositions; Δ-cleanup returns the structural decomposition.

So Δ-cleanup is ~2-5× more expensive than naive cleanup at our vocab,
but returns much more information (full pair structure, not just
nearest-singleton). For large vocab (V=50K), naive scales as 5e8 vs
Δ-cleanup's ~4e8 with rank=2 → roughly comparable. For full
compositional decomposition (find ALL pair structures), naive needs
V² inner products (2.5e9) while Δ-cleanup naturally returns top pairs
in one pass.

## What problems Δ-cleanup actually solves

Three classes of problems where this matters:

1. **Variable binding queries.** "Given a representation of {position1: X,
   position2: Y, position3: Z}, retrieve everything that's at position2."
   Standard VSA can do this only if you know there are EXACTLY 3 bindings.
   Δ-cleanup retrieves the structure regardless.

2. **Compositional decomposition.** "Given a hypervector representing
   'red square', is it bound from 'red' ⊗ 'square'?" Δ-cleanup is the
   native way to ask "is c structurally a binding?"

3. **Symbolic-subsymbolic translation.** Take a continuous representation,
   apply Δ, extract the symbolic structure (which atoms are present).
   This is the *interpretability* angle — Δ gives a structural readout.

## When Δ-cleanup is the wrong tool

For language modeling specifically, naive cleanup is fine:
- We don't need compositional decomposition at every byte
- The W matrix learns the next-byte distribution directly
- We just need to predict 1 byte from a 256-byte codebook

Δ-cleanup is MORE relevant for:
- Question answering (compositional retrieval)
- Knowledge graph completion (find atoms compatible with constraints)
- Continual learning (decompose a learned hypervector into "old" and "new" parts)
- Few-shot ICL (figure out the binding structure of in-context examples)

This means Hopf-VSA's biggest payoff is in Wave 3a (continual learning),
Wave 3b (ICL), and future symbolic-reasoning tasks — NOT in raw perplexity
on byte-LM.

## Implementation phasing

| Phase | Deliverable | Cost |
|---|---|---|
| Δ-only test (verify Δ works) | Toy capacity tests like Wave 13 Phase A | 1 day each |
| SVD-cleanup unit test | Synthetic binding+decomposition recovery | 2 days |
| Compositional reasoning task | bAbI-style or simple toy | 1 week |
| Integration with byte-LM (limited use) | Use Δ at test time for capability test | 1 week |
| Full Hopf-VSA byte LM | Replace standard cleanup with Δ-cleanup | 2-3 weeks |

Phase ordering: validate at toy task → simple capability task → byte LM.
Don't jump to byte LM directly.
