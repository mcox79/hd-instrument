# Alt-basis substrates that enable M2 — research agent synthesis

Returned 2026-05-19. Survey of alternative VSA carriers whose structure
provides concept-extraction signals independent of bilinear retrieval,
while preserving our pros.

## Six levers for escape

(A) Non-bilinear binding
(B) Non-commutative algebra carrying order/grade invariants
(C) Topological/valuation structure (ultrametric)
(D) Idempotent/extremal structure
(E) Equivariance group with invariants beyond inner product
(F) Spectral/modular canonical flow

## Top 3 recommendations (priority order)

### Rank 1 — Connes-Kreimer / shuffle Hopf carriers (Wave 14.B-style with prefix/suffix M2 channel)

Already in queue. Math is cleanest demonstration of structure orthogonal
to bilinear retrieval; decomposition provably 100%; CL unchanged.
The M2 feature is "prefix-bundle of episode" extracted by the
antipode-driven decomposition — structurally non-bilinear.

**Status:** Wave 14.A symbolic toy validated 100%. Wave 14.C
(hierarchical with proper resonator on graded Hopf) is a multi-day
implementation.

### Rank 2 — VTB (Gosmann-Eliasmith 2019) with non-commutator concept channel

bind(x,y) = M(y) x where M(y) is a deterministic block permutation-
and-rotation matrix from y. Non-commutative. **Exact unbinding.**
Resonator-compatible. ~2x BSC cost.

**M2 feature:** bind in both orders; M2 reads commutator-residual
norm and direction. Pure non-commutativity test.

**Test (~30 min GPU):** swap binding from elementwise · to VTB M(y) x
in `train_phase_a` of one of our scripts. Compare bpc and add
commutator features to M2 fusion. Falsifier: |delta| < 0.05.

### Rank 3 — FHRR with phase-statistic M2 channel (NOT phase-as-retrieval)

We've tested FHRR as retrieval. We have NOT tested FHRR **phase
histograms / circular variances** as a SEPARATE concept channel.

**M2 feature f(b) in R^k, k~30:**
- resultant length |sum exp(i phase)|
- phase-histogram entropy over 8 bins
- circular variance at offsets {1, 4, 16}

**Test (~1h GPU):** load existing FHRR Phase A state if available;
compute phase statistics per bundle; use as additive logit to retrieval.
&gt;= 0.05 bpc threshold.

## Other strong-but-deferred candidates

### GHRR (Alam 2024 non-commutative HRR)
Lever (B) clean. Requires per-atom unitary U_x. ~5-10x BSC cost on
dense matrices; needs block-diagonal/sparse U_x for tractability.

### Clifford G(3,1) — not G(2,0)
Wave 8 tested G(2,0); 4-dim slot too small. G(3,1) has 16 grades
(8.4M dims naive; restrict to grade-1 + sparse grade-2 PPMI pairs
~tractable). Grade-2 captures oriented pairwise relations provably
absent from sum-bundling. Salvageable but negative prior from Wave 8.

### MPS / tree tensor networks (NOT Wave 9's flat-MPS)
Wave 9 failed because flat-MPS shape, no real contractions. Proper
test: TT contraction binding with chi=8, L=16, d=8. f(b) =
entanglement entropy across cuts. ~1 day engineering.

### p-adic / non-Archimedean carriers
Cleanest example of "kernel-independent structure" — p-adic ultrametric
and Euclidean cosine measure different things by construction.
Resonator at HDC scale unstudied. Speculative but mathematically
unique.

### Sparse block codes (Laiho 2015 / SLOT)
Lever (D). Block-coactivation patterns are combinatorial invariants.
Frady-Sommer 2021 SLOT extension gives resonator. Cheaper than BSC.
Worth parallel-feature trial.

### Tomita-Takesaki / KMS carriers
Lever (F). Pick small matrix algebra M_n(C), n=64, total dim 4096.
Modular flow sigma_t canonical. **Highest novelty** — no prior art
on Tomita-Takesaki for HDC. Risk: matrix binding more expensive,
decomposition unproven at scale.

## Skip list

- **HLB / Walsh-Hadamard** (Kazemi NeurIPS 2024): designed for backprop;
  no new lever for our redundancy axis.
- **Sweedler H_4**: dominated by graded combinatorial class.
- **Clifford G(2,0)**: already tested, failed.
- **Tropical/max-plus**: no scale-decomposition story.
- **Hyperbolic**: mismatched to byte-LM (which isn't strongly hierarchical
  at K=4 granularity).
- **Wave 9 flat-MPS**: proven failed; real MPS-TT is multi-week build.

## The 2-hour GPU decision experiment

Run all three top candidates in a single experiment at N=4096:
- One shared pool of K=1024 byte-position bundles
- Encode three ways: (i) BSC baseline, (ii) VTB binding,
  (iii) CK prefix-suffix pre-extracted, (iv) FHRR phase-stats pre-extracted
- Train delta-rule W on each; freeze
- M2 fusion head reads [retrieval_score, concept_feature] for each
- Headline: byte-LM bpc post-shift vs A_only baseline
- Decision rule: any variant with >=0.05 bpc post-shift win is promoted

**If none win:** the narrow Lippl-Stachenfeld redundancy class extends
beyond bipolar BSC — publishable observation; the fix lives in the
readout architecture, not the carrier.

## Sources

- [Alam GHRR 2024](https://arxiv.org/abs/2405.09689)
- [Gosmann-Eliasmith VTB](https://compneuro.uwaterloo.ca/files/publications/gosmann.2019b.pdf)
- [Frady-Sommer Sparse VSA Binding](https://arxiv.org/pdf/2009.06734)
- [Kazemi Walsh-Hadamard linear VSA NeurIPS 2024](https://arxiv.org/abs/2410.22669)
- [Kent-Frady-Olshausen-Sommer Resonator Networks 2](https://arxiv.org/pdf/1906.11684)
- [Clifford Group Equivariant Networks](https://arxiv.org/pdf/2305.11141)
- [Maragos-Gaubert Tropical Geometry and ML](http://www.cmap.polytechnique.fr/~gaubert/COURSM2/TROPICALANDLEARNING/Tropical_Geometry_and_Machine_Learning.pdf)
- [Nickel-Kiela Poincare embeddings](https://arxiv.org/pdf/1705.08039)
- [Nickel Lorentz hyperbolic 2018](https://arxiv.org/pdf/1806.03417)
- [Zuniga p-adic NNs 2024](https://arxiv.org/pdf/2402.00094)
- [Tomita-Takesaki modular theory](https://arxiv.org/pdf/math-ph/0511034)
- [Sorce 2023 modular flow intuitive construction](https://arxiv.org/pdf/2309.16766)
- [Kleyko HDC/VSA survey Part I](https://arxiv.org/pdf/2111.06077)
