# Substrate exploration designs (Waves 8-13)

Per the substrate audit (2026-05-18 deep-dive on alternative VSA
mathematical frameworks), we're adding 6 substrate waves. This doc
captures designs and implementation plans.

## Wave 8: Clifford / Geometric Algebra G(2,0) — IMPLEMENTED

File: [exp_wave8_clifford_g20.py](../experiments/exp_wave8_clifford_g20.py)

Stacked G(2,0) multivectors (1024 slots × 4-dim each = 4096 total).
Geometric product binding is non-commutative natively. Standard sum +
L2-normalize bundling. Hebbian delta-rule W update on flattened
representation.

Status: prototype written, queued to launch after Wave 3a.5.

Extensions planned (Wave 8.5, 8.6):
- **G(3,0)** — adds a third grade (volume element); 8-dim per slot; 512 slots
- **G(4,1) conformal** — adds null vectors for conformal geometry; 32-dim slot

## Wave 9: Matrix Product States (MPS) VSA — DESIGN

Atom representation: each hypervector is an MPS over L sites with
physical dim d=4 and bond dimension χ=16.

Total parameters per atom: L × d × χ² = L × 4 × 256.
For 4096 effective dim, pick L = 32 sites (giving d^L = 4^32 ≈ 10^19
expressible states with only 32 × 4 × 256 = 32K params per atom).

Operations:
- **Binding (MPS contraction):** A * B = MPS contraction site-by-site,
  bond dim grows to χ² = 256, then SVD-truncate back to χ=16.
- **Bundling:** direct-sum of MPS at each site (bond dim doubles), then
  SVD-truncate back. Or simpler: convert to dense, sum, re-MPS.
- **Cleanup:** nearest-MPS retrieval via overlap (compute <atom | query>
  via MPS contraction; closed form).
- **Training:** DMRG-style sweeps (left-right and right-left) on the W
  tensor as a non-backprop alternative.

Library: `quimb` (Python tensor-network library, MPS-first) or PyTorch's
manual implementation.

Implementation effort: 1-2 weeks. Tricky parts:
- Stable SVD truncation under repeated binding
- DMRG sweep loop convergence on the byte-prediction objective
- Numerical conditioning of bond dimensions

Falsification: if MPS at χ=16 doesn't beat FHRR by ≥0.1 bpc, the
low-rank tensor-network framing isn't helping at our scale.

Expected payoff: 0.1-0.4 bpc. The audit calls this the "highest
upside-to-strangeness ratio."

## Wave 10: RG-flow hierarchical HDC — DESIGN

Approach: keep FHRR substrate, add depth via learnable coarse-graining
maps K_i: HD_n → HD_{n/2} that merge pairs of context positions.

Architecture:
- Level 0: standard FHRR ctx vectors at N=4096
- K_1: HD_4096 → HD_4096 (learnable linear map; coarse-grains 2 positions
  into 1 hypervector)
- Level 1: predicted bundle at half the temporal resolution
- K_2: HD_4096 → HD_4096 (further coarse-graining)
- Level 2: at quarter resolution
- ... up to log2(K) levels

Training (non-backprop, layer-wise):
- Level 0: standard delta-rule W as we have now
- K_1: learn to maximize mutual information between level-0 features and
  level-1 features (Bayesian RG prescription, Berman/Klinger 2024
  arXiv:2405.17538). Approximate via covariance: I(X;Y) ≈ -log det(Σ_XY)
  / det(Σ_X Σ_Y), train K_1 to maximize this.
- W_1: delta-rule on level-1 features predicting level-1 targets
- Repeat for level 2, 3...

Implementation effort: 2 weeks. Key challenges:
- Defining "next byte target" at coarser resolutions (just bundle the
  two next bytes?)
- Picking the MI estimator (closed-form vs MINE-style)
- Stitching multi-resolution predictions back to byte-level bpc

Expected payoff: 0.2-0.5 bpc. Maps to cortical hierarchies and is
bio-plausible (only local + layer-wise updates, no backprop through
layers).

## Wave 11: LDPC-cleanup HDC — DESIGN

Approach: keep BSC substrate but replace flat random codebook with a
structured LDPC code's codeword space. Cleanup uses belief propagation
decoding to project noisy retrievals onto codewords.

Setup:
- Pick (n, k) LDPC code with n=4096 (or close), k chosen for desired
  rate (~3000 codewords)
- 256 byte atoms = 256 randomly-selected codewords
- 4 pos atoms = 4 more random codewords
- W update unchanged
- Cleanup at READ: use min-sum or sum-product belief propagation to
  decode the noisy W readout to nearest codeword

Library options:
- `pyldpc` (Python LDPC encoder/decoder)
- Custom belief-propagation in PyTorch (parallel over batches)

Implementation effort: 1 week.

Expected payoff: capacity guarantees from coding theory; perplexity
gain unclear (probably ≤0.05 bpc). The audit characterizes this as
"lower ceiling than #1-3 but cheap and unambiguous gain on
capacity-limited tasks."

Should pursue only if Wave 8/9/10 results suggest cleanup is the
bottleneck.

## Wave 13: Hopf algebra VSA — RESEARCH-GRADE

Per audit: "speculative; no ML/HDC literature." User explicitly
requested despite this.

Hopf algebras have:
- Algebra structure (multiplication μ: H⊗H → H) — like binding
- Coalgebra structure (comultiplication Δ: H → H⊗H) — could be a new
  primitive for "decomposing" a bound hypervector
- Antipode S: H → H — natural inverse, like unbinding
- Unit, counit — null elements

Concrete first choice: **Drinfeld double of a finite group D(G)**, with
G = small finite non-abelian group (S_3, A_4, Q_8 quaternion group, or
D_4 dihedral group).

For G = S_3 (smallest non-abelian, |G|=6):
- D(S_3) has dim 36 (= |G|²)
- Atom = element of D(S_3); 36-dim
- Binding = D(S_3) multiplication (non-commutative, non-cocommutative)
- Unbinding = antipode
- Cleanup = nearest element in D(S_3) basis

To reach N=4096, stack 4096/36 ≈ 113 copies. Or pick a larger group.

Alternative starting point: **quantum group U_q(sl_2) at q=root of
unity**. Has finite-dimensional representations and rich structure
(R-matrix gives non-commutative non-cocommutative binding).

Implementation effort: 2-4 weeks. Major risks:
- No ML library implements these operations directly
- Numerical conditioning of antipode under repeated operations is
  unknown
- The "right" cleanup metric isn't obvious
- May not be parameter-efficient (lots of basis elements)

Expected payoff: unclear. The math is elegant but the empirical case
is untested. The audit's recommendation was "wait until someone
publishes a first attempt" — user has opted to be that someone.

Plan: start with the smallest case (D(S_3)) on a TOY task (e.g., 4
classes of synthetic byte sequences) before scaling to byte-LM. This
de-risks the ~2-month timeline.

## Priority order and queue

Recommended execution order based on payoff/cost:

1. **Wave 12 (qFHRR)** — DONE; cheapest, runs in ~1 min × 4 variants
2. **Wave 8 (Clifford G(2,0))** — DONE; runnable prototype, ~5 min at N=4096
3. **Wave 9 (MPS)** — write next; ~2 weeks dev + 30 min run
4. **Wave 10 (RG-flow)** — write next; ~2 weeks dev + 1 hour run
5. **Wave 11 (LDPC)** — short dev; ~1 week + 5 min run
6. **Wave 13 (Hopf D(S_3))** — long tail; toy task first, then byte-LM

All of these are independent of the ongoing Wave 3a.5 / 4.5 / 4.6 /
6.5 backprop track, so they parallelize cleanly.

## What we expect to learn

Each substrate tests a specific axis:
- **Clifford**: does non-commutative geometric algebra give multi-head-like
  expressivity?
- **MPS**: does low-rank tensor-network structure help at our scale?
- **RG-flow**: does hierarchical coarse-graining give depth without
  backprop?
- **LDPC**: does coding-theory-grounded cleanup help with retrieval?
- **qFHRR**: cheap memory-efficiency check
- **Hopf**: does the "natural" algebra-of-binding structure pay off?

Combined, these decompose the question "what's the right algebra for
HDC?" into testable substrate variants. Most published HDC papers stay
within FHRR/HRR/BSC; this wave is a comprehensive expansion.
