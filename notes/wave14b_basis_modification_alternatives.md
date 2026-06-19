# Basis modification alternatives — research agent synthesis

Returned 2026-05-19. Unbiased math survey on operations that GENUINELY
extend the representational basis of a VSA substrate, where our prior
attempts (PPMI-derived atoms; independent random atoms) produced null.

## Reframe the question

"Extending the basis" is a category error in flat R^N: there is no
extension of R^N beyond itself. The only genuinely new representational
dimensions come from one of three structural moves:

- **(M1) Lifting to a higher tensor degree** — go from linear span
  of byte ⊗ pos to bilinear/cubic spans `byte_a ⊗ byte_b ⊗ pos` that
  are provably outside the original additive span.
- **(M2) Carrier with built-in stratification** — change the algebraic
  carrier from R^N to a graded/filtered object (Clifford, Hopf, MPS,
  sheaf) whose dimension count grows monotonically.
- **(M3) Coding-theoretic capacity slack** — keep R^N but use a sparser
  code so the bundle operates *below* capacity, reserving a genuinely
  unused subspace.

Our two failures are **diagnostic**: attempt #1 (PPMI bundle) is in M1's
image collapsed back to degree-1 — that is why it failed. Attempt #2
(independent random atoms) is in M3 but at K=4 the bundle is so far
below capacity that adding mass changes nothing measurable.

The failures confirm: M3 alone is exhausted. We need M1 (degree lift)
or M2 (carrier change).

## Top 3 candidates (priority order)

### Rank 1 — B1. Direct-sum / block-coded VSA [CLEANEST DISAMBIGUATOR, 45 min CPU]

**Def.** Split R^N into R^N_byte ⊕ R^N_concept (N = N_byte + N_concept).
Bytes only bind into N_byte block, concepts only into N_concept block.
Concatenation, not summation.

**Why new.** Adding a concept extends the concept block monotonically
without redistributing mass in the byte block. True orthogonal extension:
byte SNR is *literally untouched* when concept atoms are added.

**Pros check.** Decompose per-block (resonator runs independently);
W_frozen becomes block-diagonal; per-block W_byte unchanged. Editing yes.
Same total flops, partitioned.

**Test:** re-run basis_modification_indep with concept_atoms placed in
coords [N_byte..N] (zero in [0..N_byte]) and byte atoms zero in
[N_byte..N]. **Cleanest experiment to disambiguate "concept signal
exists but is being clobbered" vs "concept signal doesn't add
information."**

### Rank 2 — A1. Cubic byte_a · byte_b · pos binding [30 min CPU]

**Def.** Add to ctx a second additive component
`sum_{(a,b) in pairs} byte_atom[b_a] · byte_atom[b_b] · pos_atom[r] · pair_pos`
where pair_pos is a fresh random vector and · is BSC binding.

**Why genuinely new.** Triple product is cubic in original atoms. In
BSC algebra, span{byte_i · pos_r} and span{byte_i · byte_j · pos_r} are
orthogonal in expectation. This lift adds capacity OUTSIDE the existing
linear span — exactly what attempt #1 mistakenly thought it was doing.
Smolensky 1990 TPR grade-counting gives the formal argument.

**Pros check.** Decompose via resonator at arbitrary product orders
(Frady-Sommer 2020). Continual learning + editing unchanged. CPU cost
O(#pairs · N) per ctx; cap at <=32 PPMI pairs/K=4 window → 130K mults
per token = fine.

**Predicted gain:** 0.05-0.15 bpc on byte-LM pre-shift, scaling with
PPMI mass. Falsifier: |Δbpc| < 0.01.

### Rank 3 — B3. Clifford grade-2 bivectors for concepts [~2h GPU]

**Def.** Use Clifford algebra Cl(N). Concepts get assigned to grade-2
(bivector = pairwise antisymmetric). Bind to ctx via Clifford geometric
product against a grade-2 pos slot.

**Why new.** Grades are LITERALLY orthogonal subspaces of the multivector
algebra. Bivectors encode the *antisymmetric/oriented* part of byte
pairs — provably absent from grade-1 sum-bundling.

**Pros check.** Resonator extends (Frady-Sommer machinery generalizes
to grade-projection). Restrict to grade-1 + sparse grade-2 (only
PPMI-active pairs ~50): tractable.

**Signal added.** Grade-2 captures handed/oriented pairwise relations;
grade-3 captures handed triples. Higher PPMI structure naturally lives
there.

## Other candidates surveyed

### A3. Concept atoms via coherence regularization (medium)
Top-K SVD of pool_residual after projection orthogonal to byte·pos span.
Data-driven counterpart to A1. Test: ~1h GPU.

### A2 / A4 / A5
- A2 (random pos lattice extension): equivalent to attempt #2, skip.
- A4 (sparse coding on residual): equivalent to A3 with L1 prior.
- A5 (Plate fractional power positions): requires carrier change, see B group.

### B2. MPS with growable bond dimension (long-term)
Stoudenmire-Schwab; χ grows monotonically with new entanglement
discovered. Requires re-orthogonalization on each update (expensive).
~1 day engineering, defer.

### B4-B6. Hopf algebra / sheaf / operator algebra
Mathematically elegant but no concrete 2h test. Defer.

### C1. Sparsified block-sparse VSA (Hersche 2024) — strong candidate

Block-sparse codes: divide R^N into B blocks; each codeword has exactly
1 active position per block. New concepts → new blocks. Capacity
log(N/B)·B with much higher named-entity resolution. Resonator exists
(Hersche 2024). Faster than dense BSC (sparsity).

**Test (~1h CPU):** B=64, blocks of width 64 (N=4096), append 4 blocks
for concept slots. Predicted: clean yes/no on "does concept information
exist at this resolution".

## Honest assessment

Most VSA "extensions" in the literature add complexity without bpc gain
because the substrate operates below capacity. Our null results confirm
this regime: with K=4 in N=4096, the bundle has SNR slack, so any
uncorrelated addition just shifts mass.

The only candidates that escape this trap **place new signal in a
provably orthogonal substructure** (A1 cubic, B1 direct sum, B3 Clifford
grade-2, C1 sparse blocks) or **change the carrier so capacity is
defined differently** (B2 MPS).

Each carries a *grading* that BSC doesn't have. **In each case the new
dimension is not in the original additive span by construction, not by
hope.**

## If all top-3 still null

The honest conclusion would be that *byte-LM at K=4 on this corpus is
bottlenecked by W's learning rate or pool capacity*, not basis dimension,
and the codebook-growth program should be paused in favor of fixing
whichever of those is the actual binding constraint.

## Sources

- [Frady-Sommer Resonator Networks for VSA factorization (arXiv:1906.11684)](https://arxiv.org/abs/1906.11684)
- [Factorizers for Distributed Sparse Block Codes (arXiv:2303.13957)](https://arxiv.org/html/2303.13957v2)
- [Capacity Analysis of VSA (arXiv:2301.10352)](https://arxiv.org/pdf/2301.10352)
- [Smolensky 1990 — Tensor Product Variable Binding](http://www.lscp.net/persons/dupoux/teaching/AT1_2014/papers/Smolensky_1990_TensorProductVariableBinding.AI.pdf)
- [Geometric Clifford Algebra Networks (arXiv:2302.06594)](https://arxiv.org/pdf/2302.06594)
- [Plate HRR — Holographic Reduced Representations](https://www.researchgate.net/publication/5589577_Holographic_Reduced_Representations)
- [Compositional Factorization of Visual Scenes (arXiv:2404.19126)](https://arxiv.org/html/2404.19126)
- [Improved cleanup of fractional power encodings (arXiv:2412.00488)](https://arxiv.org/html/2412.00488)
- [Stoudenmire-Schwab Tensor Networks for Supervised Learning](http://papers.neurips.cc/paper/6211-supervised-learning-with-tensor-networks.pdf)
