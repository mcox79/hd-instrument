# R1 iterative Hopfield negative — research agent synthesis

Returned 2026-05-19. Deep research on why iterative Modern Hopfield
(Ramsauer 2021) gave monotonically-worse bpc at every beta for steps>=2.

## TL;DR

**Iterative modern Hopfield is dead for byte-LM label-prediction at
our scale, and the literature predicts this.** The reason converges
on one explanation:

> Ramsauer iteration recovers the **nearest stored pattern** (or its
> cluster mean when patterns are correlated). Our task is **label
> prediction**, where the cluster mean's label is not the nearest
> pattern's label. At beta=16, P=1024, one-shot softmax already
> concentrates correctly; iteration then drifts toward the metastable
> cluster centroid, smearing the label distribution.

This is over-determined negative against a **protocol mismatch**.

## Ramsauer 2021 theorem restated

Theorem 4 ("one update step is enough"): if a query lies in x_i's
basin and the separation Delta_i = <x_i, x_i> - max_{j!=i} <x_i, x_j>
is large relative to 1/beta, then `||xi_1 - x_i|| <= 2N exp(-beta *
(Delta_i - 2 max_k ||x_k||^2 / sqrt(d)))`. Retrieval error decays
exponentially in beta * Delta_i AFTER A SINGLE STEP.

The theorem **does not say** iteration is better than one-shot. It
says one step suffices under separation, and that if separation
fails (clustered patterns), iteration converges to **cluster average**.

## Why iteration is monotone-worse for our setup

1. **Target is a label, not a bundle.** Ramsauer iterates xi in
   bundle space. We then softmax-weight a 256-d label distribution.
   If query is already near x_i after one step, label has near-delta.
   Iterating further drifts toward metastable cluster centroid whose
   constituent patterns have **different labels**.

2. **Clustered memories with disagreeing labels.** With 256-byte
   alphabet and K=4, many 4-grams reoccur with different next bytes.
   Same byte_atom*pos_atom factors → similar bundles → small Delta_i
   → metastable cluster → cluster-mean label is a mixture.

3. **Softmax at beta=16 over P=1024 is already near-delta.** One-shot
   already saturates; iteration has no headroom.

4. **Bipolar BSC bundles have high baseline correlation** for
   overlapping prefixes (which dominate byte-LM data!).

## Known iteration failure modes (literature)

- **Metastable mixture states** (Ramsauer §A.4; Gayrard 2024)
- **Pattern-correlation breakdown** (Schaeffer 2024)
- **Beta-step interaction** — when one step already converges, extra
  steps accumulate noise (Ramsauer Thm 4; Millidge 2022)
- **Initial-condition sensitivity** — iteration LOCKS IN wrong choices
- **Saddle/spin-glass attractors** (Schaeffer 2025)
- **Label-readout vs bundle-readout** — our specific protocol failure

## Implementation review

`experiments/exp_wave14b_r1_modern_hopfield.py` is correct Ramsauer
modulo BSC-style /N normalization (standard in HDC). No bug. The
negative result is real, not a coding artifact.

The label-readout (`scatter_add` of final weights to 256-d labels)
is the **protocol mismatch** with Ramsauer's bundle-prediction task.

## Three falsifiable rescue experiments (<1h GPU each)

### R1.B (STRONGEST RESCUE) — Native bundle-readout protocol

Replace label-pool readout with bundle-pool readout: the iterate xi_t
itself, decoded via cosine against the byte codebook, gives P_retr.
This is Ramsauer's ORIGINAL prediction task.

**Decision rule:**
- If iteration helps bundle-readout but not label-readout: protocol
  mismatch is the cause
- If iteration also hurts bundle-readout: iteration is genuinely dead
- Threshold: >=0.01 bpc bundle-readout improvement from steps>=2

### R1.A — Harder retrieval problem

Increase K=4→16 (more byte history); reduce N=4096→1024 so
beta*Delta isn't saturated; increase pool to P=8192 with overlapping
contexts. If iteration ever helps anywhere in this grid, R1 was
setup-specific.

### R1.C — Beta annealing during iteration (SDS schedule)

Start beta_0=4, anneal beta_t = beta_0 * 2^t over T=4 steps. Graduated
non-convexity: escape early metastable basins, then sharpen. If any
schedule beats steps=1 beta=16 by >=0.02 bpc, iteration is rescuable.

## Honest bottom line

**Single strongest rescue: R1.B.** If iteration cannot help even when
we play by Ramsauer's rules (predict bundles, not labels), iterative
branch CLOSES definitively.

If R1.B also fails: keep `steps=1, beta=16, bpc=4.2478` as the lone
Ramsauer-flavored win and treat it as **high-beta one-shot
calibration** (Velickovic "softmax-is-not-enough" prescription), not
a Hopfield-iteration win. Re-frame the negative as a successful
**falsification** of iterative refinement, not a failure of the
underlying retrieval idea.

## Sources

- [Ramsauer NeurIPS 2021 arXiv:2008.02217](https://arxiv.org/pdf/2008.02217)
- [Krotov-Hopfield Dense Associative Memory](https://link.springer.com/article/10.1007/s10955-017-1806-y)
- [Millidge Universal Hopfield Networks](https://pmc.ncbi.nlm.nih.gov/articles/PMC7614148/)
- [Bricken-Pehlevan Attention Approximates SDM](https://arxiv.org/abs/2111.05498)
- [Velickovic Softmax is not Enough](https://arxiv.org/abs/2410.01104)
- [Schaeffer Modern Hopfield meets Encoded Reps 2024](https://arxiv.org/html/2409.16408v2)
- [Schaeffer Transient dynamics 2025](https://arxiv.org/pdf/2506.05303)
- [Gayrard Mixed Memories Hopfield 2025](https://arxiv.org/pdf/2504.04879)
- [Martins Sparse Modern Hopfield](https://openreview.net/pdf?id=zwqlV7HoaT)
