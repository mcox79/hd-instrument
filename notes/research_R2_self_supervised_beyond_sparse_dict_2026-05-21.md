# Research R2 — Self-supervised concept discovery beyond sparse dictionary learning

**Topic.** Sparse dictionary learning (Mairal 2009 online algorithm) was the
2026-05-19 wave14d recommendation for replacing PPMI. The wave14d_sparse_vs_ppmi
experiment failed at runtime: Python-loop bottleneck in `learn_sparse_dictionary`
(~150K iterations per run, not vectorized). E5 in `active_priorities.md` is the
infra task to vectorize that. R2 asks the parallel question: what
substrate-compatible self-supervised concept-discovery alternatives exist that
**avoid the inner-loop bottleneck entirely** — i.e., closed-form,
already-vectorized, or end-to-end-differentiable without a sparse-code subproblem?

**Date.** 2026-05-21

**Status.** Research note, two passes complete. Routes to Strategy (cap_map
proposal) and Experiment Dev (E-candidate proposal). This is *parallel* to
E5 — if Hebbian Oja/Sanger or similar produces a credible signal at a
fraction of E5's infra cost, the sparse-coding path can be deprioritized.

**Scope note.** The 2026-05-19 note already ruled out PCA (loses position
structure), NMF (substrate is bipolar, not non-negative), k-means (no
high-dim cluster structure), LDA (corpus too short), and resonator-without-
codebook (no fixed point). This R2 note does NOT re-litigate those; it
drills the candidates the prior note flagged as plausible but did not
investigate beyond a paragraph, AND adds three candidate families not
considered there.

---

## Pass 1 — Survey of candidates that avoid the sparse-coding inner loop

### What "the inner-loop bottleneck" actually is

Online sparse dictionary learning (Mairal et al. 2009) alternates between
two steps per minibatch:
1. **Sparse code step** — for each pool vector x, solve
   `a = argmin (||x - D a||² + λ ||a||_1)`. This is LASSO; standard solvers
   (LARS, coordinate descent, FISTA) iterate to convergence over a's
   support, which is what generates the Python loop the substrate hit.
2. **Dictionary update step** — update D = D + stochastic gradient. This
   step IS vectorizable; the bottleneck is step 1.

The bottleneck is not specific to Mairal's algorithm — it's specific to
*any* method that requires solving a sparse-code subproblem per sample.
K-SVD has the same property. SAE (sparse autoencoder) avoids it by
replacing the LASSO with a ReLU+L1 penalty learned via autograd —
which is *one* of the ways out. There are others.

### Candidate F1: Hebbian Oja/Sanger rule (Generalized Hebbian Algorithm)

**Reference.** Sanger 1989 ("Optimal unsupervised learning in a
single-layer linear feedforward neural network," *Neural Networks* 2,
459–473); precursor: Oja 1982 ("A simplified neuron model as a
principal component analyzer," *J. Math. Biol.* 15, 267–273).

**Mechanism.** Online streaming algorithm that recovers the top-k
principal components of the input stream via a Hebbian rule with
Gram-Schmidt-style decorrelation. For input x_t and weights W ∈ R^{k×N}:

  y_t = W · x_t
  W ← W + η (y_t x_tᵀ − LT(y_t y_tᵀ) W)

where LT is the lower-triangular operator. Pure outer products and matrix
multiplies; **no inner-loop sparse code**. Substrate already runs Hebbian
delta-rule updates, so this is the same compute pattern reused for a
different purpose.

**Substrate fit.** Operates on bundle vectors directly, just like sparse
coding wanted to. Extracts the top-k principal components of the pool
distribution as concepts. Important caveat: the 2026-05-19 note ruled
out PCA because "PCA throws away byte-position structure by mixing
across positions." Sanger's algorithm has the same failure mode in its
vanilla form — but the rescue is **block-Sanger**: run k separate Sanger
processes, one per position p, recovering position-conditional principal
directions. The substrate's bundle = Σ_p bind(pos_p, byte_p), and
position-conditional concepts naturally preserve the (pos, byte) tensor
structure that vanilla PCA destroys.

**Why this might beat PPMI.** PPMI on argmax-decoded bytes sees only the
pair statistics of bytes that win argmax. Block-Sanger sees the *full*
bundle including the interference mass. That's the same advantage sparse
coding has — without the inner-loop cost.

**Honest limits.** Recovers principal components, which are *linear*
combinations of input directions. Sparse coding recovers an
over-complete frame, which can pick up structure linear methods miss
(parts-based, multi-modal). Sanger is strictly less expressive but
strictly cheaper.

### Candidate F2: Tensor CP decomposition of the W matrix

**References.** Carroll-Chang 1970 ("Analysis of individual differences
in multidimensional scaling via an N-way generalization of
'Eckart-Young' decomposition," *Psychometrika* 35, 283–319);
Harshman 1970 (PARAFAC, UCLA Working Papers in Phonetics 16); Kolda-Bader
2009 ("Tensor decompositions and applications," *SIAM Review* 51,
455–500, arXiv:0810.4408 — the modern survey).

**Mechanism.** The substrate's W = Σᵢ vᵢ kᵢᵀ is already a rank-K
matrix decomposition. CP decomposition of W into a different basis
{(uⱼ, wⱼ)} via ALS (alternating least squares):

  W ≈ Σⱼ σⱼ uⱼ wⱼᵀ,  optimize over σ, u, w with fixed rank J

For W with i.i.d. (vᵢ, kᵢ), ALS recovers σⱼ ≈ ||vᵢ|| ||kᵢ|| and (uⱼ, wⱼ) ≈
(vᵢ/||vᵢ||, kᵢ/||kᵢ||) up to permutation — same atoms back. Useful when J <
K and we want a *compressed* representation, or when W carries structure
beyond the random outer products (which it does after Hebbian training
on a corpus — co-occurring (k, v) pairs reinforce each other and produce
detectable structure beyond random rank-K).

**Substrate fit.** Closed-form ALS step: every update is a batched least-
squares solve, fully vectorized. No inner loop. PyTorch's
`torch.linalg.lstsq` handles it.

**Honest limits.** CP recovers what's *in* W after Hebbian training,
which is dominated by the random codebook atoms unless co-occurrence
structure is strong enough to lift the corresponding rank-1 atoms out of
the noise floor. At α = 0.153 (substrate operating point per
wave14m_alpha_c), the signal-to-noise at the top-K eigenvalues is
favorable; below the Marchenko-Pastur edge, ALS won't recover anything.
This is the same MP-edge story already explored in wave14mp_edge_detector.

**Where it differs from Sanger.** CP recovers the *bilinear* (v, k)
structure; Sanger recovers principal directions of the input
distribution. CP is the natural recipe for "what concept atoms are
currently STORED in W"; Sanger is the natural recipe for "what concept
atoms WOULD pool vectors prefer to be expressed in." Different questions.

### Candidate F3: InfoNCE / contrastive predictive coding (CPC) with linear projector

**References.** van den Oord-Li-Vinyals 2018 ("Representation learning
with contrastive predictive coding," arXiv:1807.03748); Chen-Kornblith-
Norouzi-Hinton 2020 (SimCLR, arXiv:2002.05709). Specific to the linear
form: Wang-Isola 2020 ("Understanding contrastive representation
learning through alignment and uniformity on the hypersphere,"
arXiv:2005.10242) shows that contrastive learning with a linear projector
recovers the top-k eigenvectors of the alignment-uniformity Gram matrix
— in expectation, the principal components of the "positive-pair"
distribution.

**Mechanism.** Define positives as nearby pool entries (same context
window); negatives as random pool entries. Learn a linear projector P
∈ R^{k×N} via the InfoNCE loss:

  L = − log [exp(sim(P x, P x⁺) / τ) /
             (exp(sim(P x, P x⁺) / τ) + Σ_neg exp(sim(P x, P x⁻) / τ))]

Concepts = columns of P. Gradients are vectorizable; no inner LASSO.

**Substrate fit.** Substrate already does pool retrieval via cosine, so
the cosine sim in InfoNCE is the substrate's native readout. The
positive-pair definition (nearby pool entries) maps cleanly to the
substrate's local-context structure. The linear projector is one matrix
multiply at inference.

**Why this might add value over Sanger.** InfoNCE optimizes for
*contrastive* discriminability between positive and negative pairs,
which is closer to the downstream R10 objective (concept atoms that
help predict the next byte). Sanger optimizes for *reconstruction*
variance, which is closer to the sparse-coding objective but doesn't
explicitly weight by predictive utility.

**Honest limits.** Requires autograd (PyTorch) and a backward pass per
batch, vs Sanger's pure outer-product update. ~3–5× more compute per
sample than Sanger, but still no inner sparse-code loop. Also requires
designing the negative-sampling distribution carefully; the wave14d
2026-05-19 note flagged this as the engineering tax.

### Candidate F4: Slow Feature Analysis (SFA)

**References.** Wiskott-Sejnowski 2002 ("Slow feature analysis:
unsupervised learning of invariances," *Neural Computation* 14,
715–770). Closed-form via generalized eigenvalue decomposition of
(input covariance, input-derivative covariance) pair.

**Mechanism.** Find a linear projection y = W · x that minimizes
variance of dy/dt subject to y being unit-variance and decorrelated
from previous outputs. Closed-form solution: generalized eigenvectors
of `Cov(x, x)` and `Cov(ẋ, ẋ)`. For byte streams, ẋ ≈ x_{t+1} − x_t.

**Substrate fit.** The substrate's pool is a temporal stream of bundles
indexed by training position. SFA's "slow features" would be concept
atoms that **change slowly across context**, i.e., topic-like or
genre-like atoms (longer than a byte trigram). This is a different cut
of the concept space than PPMI (pair frequencies) or sparse coding
(reconstruction of single bundles).

**Why interesting.** SFA's "slow" prior is a substrate-relevant
inductive bias: the substrate IS sequential and concepts that span many
bundles are exactly the long-range structure PPMI can't reach. Closed-
form via two SVDs; no inner loop.

**Honest limits.** SFA's vanilla form gives k ≤ N features (not over-
complete); recovers a basis, not a frame. May be a *complement* to
sparse coding rather than a replacement, capturing the slow-component
direction while sparse coding captures the fast-component. The
2026-05-19 note didn't consider this; worth surfacing.

### Candidate F5: Energy-based Hopfield concept emergence (Krotov-Hopfield dense associative memory)

**References.** Krotov-Hopfield 2016 ("Dense associative memory for
pattern recognition," arXiv:1606.01164); Ramsauer et al. 2020 ("Hopfield
networks is all you need," arXiv:2008.02217).

**Mechanism.** Modern Hopfield networks with polynomial or exponential
energy functions admit *attractor states* that emerge from the stored
pattern set. Concepts = stable attractor modes of the energy landscape.

**Substrate fit.** Subtly different — these are not "concept atoms
extracted from pool" but "stable retrieval states the substrate converges
to." For the substrate's classical-Hopfield regime (W = Σ vᵢ kᵢᵀ at α
= 0.153), the attractors ARE the stored patterns. So this candidate is
"what's stored" not "what could be extracted as a basis."

**Why honesty rules this out for R2.** Krotov-Hopfield-style concept
emergence requires *modified energy* (exponential or polynomial in pattern
overlaps), not the substrate's vanilla classical Hopfield. To use this,
we'd have to switch substrates (cap_map already notes this category
error: "Decoder swap to sparse Hopfield gives exp(N) capacity" was
retracted because substrate is W=Σvkᵀ not modern-Hopfield Ξ-matrix
storage). Not a viable R2 candidate without substrate redesign.

**Probability of being R2's right answer**: < 10%. Listed for
completeness; rejected on substrate-coherence grounds.

---

## Pass 2 — Drill the top three substrate-compatible candidates

Pass 1 narrowed to three viable families: F1 (Hebbian Oja/Sanger), F2
(Tensor CP of W), F3 (InfoNCE with linear projector). F4 (SFA) is a
complement, not a replacement. F5 (Krotov-Hopfield) requires substrate
redesign.

### Drill F1: Block-Sanger as the substrate-native concept extractor

**Algorithm.** For position p ∈ {0, ..., K−1}, maintain a per-position
weight matrix W_p ∈ R^{k×N}, k = concept count (e.g., k = 50 to match
current PPMI scale). On each pool entry x of length K, the per-position
input is x_p = (the bundle's contribution at position p, recovered by
unbinding with the position atom):

  x_p = x ⊙ pos_p

Per-position Sanger update:

  y_p = W_p · x_p
  W_p ← W_p + η (y_p x_pᵀ − LT(y_p y_pᵀ) W_p)

After T pool entries, W_p has rows = top-k principal components of the
**unbound-by-position-p** bundle distribution. Concepts at retrieval
time: for query bundle q, compute c_p = W_p · (q ⊙ pos_p) for each p,
then the concept activation vector is c = [c_0, c_1, ..., c_{K−1}],
length k·K. Fuse into R10-style linear correction.

**Substrate-specific math.** The unbinding `x ⊙ pos_p` recovers the
byte_p contribution plus interference from other positions. The
expectation of x_p over the pool is E[byte_p · pos_p · pos_p] = E[byte_p]
because pos_p ⊙ pos_p = 1 (BSC self-inverse). Each position's Sanger
process sees E[byte_p] + cross-position interference of magnitude
√((K-1)/N) per Frady-Sommer SNR analysis. For K=512, N=4096: σ_noise =
√(511/4096) ≈ 0.353, σ_signal = depends on byte frequency, but for
high-frequency bytes ('e', ' ', etc.) signal ≈ 0.1–0.3 — comparable to
noise, *not* drowned. The per-position Sanger process should converge
to high-variance directions in the byte distribution, conditional on
position.

**Why this might match or beat sparse coding's predicted gain.** Sparse
coding's mechanism for gain (per the 2026-05-19 note) was: "captures
non-Borel structure; over-complete; sees interference mass argmax
discards." Block-Sanger also operates on the full bundle (not argmax
output) and also sees the interference mass. The over-complete-frame
advantage that distinguishes sparse coding from PCA *is* lost in
Sanger's basis form — but it can be partially recovered by *non-linear
post-processing* of Sanger's outputs (a small MLP head, ReLU + linear
fuse, etc.). The cheap version doesn't do this and probably matches
basic sparse coding within noise.

**Predicted bpc gain at K=512** (calibrating against the 2026-05-19
prediction of +0.05 to +0.15 for sparse coding): **+0.03 to +0.10 bpc**
over the +0.628 baseline. The reduction from sparse coding's range
reflects the over-complete-frame disadvantage; the floor reflects
substrate-coherence (it's all bundle-space linear algebra) and the
fact that block-conditional structure handles the position-mixing
failure mode of vanilla PCA.

**Cost.** Per-position Sanger update: k · N matrix multiply per sample
× K positions = K · k · N ops/sample. For K=512, k=50, N=4096: ≈ 10⁸
ops/sample, fully GPU-vectorized. Whole-pool pass at P=50K: ~5×10¹²
ops, **fraction of a second on the 4060 Ti.** Total: a few minutes for
a hyperparameter sweep over k and η. Vs sparse coding's hours-blocked-
on-Python-loop.

### Drill F2: CP decomposition of W as a stored-concept extractor

**Algorithm.** W = Σᵢ vᵢ kᵢᵀ after Hebbian training. Solve

  min over (U, V, σ) : ||W − Σⱼ σⱼ uⱼ vⱼᵀ||_F²,  rank J

via ALS:
  fix V, σ → solve for U (least squares; closed form)
  fix U, σ → solve for V (least squares; closed form)
  fix U, V → solve for σ (singular value rescale)
  repeat to convergence (typically <50 iterations).

**Substrate-specific math.** After Hebbian training on a corpus, W's
spectrum has a high-rank random component (codebook atoms) plus a low-
rank corpus-structure component (frequent (k, v) co-occurrence pairs
lifted above the MP-edge). CP with rank J ≤ K extracts the J most
significant outer products. If J = α·N ≈ 627 (Hopfield capacity),
CP recovers all stored patterns. If J << α·N, CP recovers the
**most-reinforced** patterns — which correspond to high-frequency
content in the corpus.

**Why this might be a substrate-natural concept extractor.** "Concepts"
in the substrate are exactly "patterns that the corpus repeatedly
co-occurred." CP gives them to us by construction, and they're in the
substrate's native (v, k) form. No basis change, no interpretive layer.

**Honest assessment.** This is a *baseline* candidate, not a *novel*
one. It tells us what's stored. The PPMI-replacement question wants to
know what concepts WOULD HELP, not what concepts ARE PRESENT. CP can't
discover concepts the substrate doesn't already have in W.

**Probability that this is R2's right answer**: 20–30%. Useful as a
diagnostic (does the substrate's W after training contain corpus-aligned
structure beyond random?) but not transformative as a concept-extraction
mechanism.

### Drill F3: InfoNCE with linear projector on pool

**Algorithm.** Define positive pairs as pool entries from the same
training-stream window (within W tokens of each other in the source
text). Define negatives as random pool entries from elsewhere in the
training stream. Linear projector P ∈ R^{k×N}; learn via SGD on:

  L = − E_{(x, x⁺, {x⁻})} log[ exp((Px)·(Px⁺)/τ) /
                                Σ exp((Px)·(Px⁻_j)/τ) ]

**Substrate-specific math.** The InfoNCE loss with linear P converges
(per Wang-Isola 2020) to the top-k generalized eigenvectors of the
positive-pair covariance against the marginal covariance. This is
exactly the substrate's "what makes two bundles co-occur in
context" — a more refined cut than Sanger's marginal-PCA, because it
upweights directions where positive-pair similarity exceeds chance.

**Why InfoNCE might genuinely beat Sanger.** Sanger optimizes for
reconstruction; InfoNCE for *discriminability* between positives and
negatives. The latter is closer to the R10 use of concepts (predict
next byte given context), so the concepts InfoNCE finds are tuned to
the downstream task in a way Sanger's are not. Expected effect: +0.02
to +0.05 bpc above Sanger.

**Cost.** PyTorch autograd, ~3–5× Sanger per sample. For pool P=50K,
batch size 256, 10 epochs: ~30 minutes GPU. Still vastly cheaper than
the blocked sparse-coding path (which couldn't even finish smoke at
60s).

**Honest limits.** Negative-sampling choice matters; bad negative
distributions give degenerate solutions (the "uniformity" failure mode
in Wang-Isola). Substrate-aware fix: use *hard* negatives drawn from
nearby-but-not-positive pool entries; literature anchor for hard-
negative mining is Robinson-Chuang-Sra-Jegelka 2021 (arXiv:2010.04592,
"Contrastive learning with hard negative samples").

---

## Specific experimental design (pseudocode)

**Experiment**: `wave14r_block_sanger_vs_ppmi`. Pre-registered at
`preregs/2026-05-21_wave14r_block_sanger.md` (Experiment Dev to
author). Head-to-head against PPMI at the same R10 fusion budget.

**Why Sanger first (not InfoNCE).** Sanger is the simplest substrate-
coherent option — pure outer products, no autograd dependency, no
hyperparameter for negative sampling. If Sanger lands the predicted
+0.03–0.10 bpc, it's the answer with minimum infrastructure work. If
Sanger lands flat, the next experiment is InfoNCE — same hypothesis,
more sophisticated discriminative loss. CP decomposition is a third
priority, mostly as a diagnostic.

```text
config:
  N = 4096
  K = 512  # match R10 best-config K
  k_concepts = 50  # match PPMI's nc=50 used in R10 best-config
  pool_size = 4096  # match substrate operating point
  eta = 0.01  # Sanger learning rate; sweep {0.001, 0.01, 0.1}
  seeds = [7, 17, 23, 31, 41]  # 5-seed standard
  T_pool_passes = 3  # passes through pool for Sanger convergence
  pos_atoms = standard substrate position atoms, K=512 instances

storage_phase:
  # Use existing substrate Hebbian pipeline; no changes here.
  W, pool = train_substrate(corpus, K=K, N=N, ...)

block_sanger_concept_extraction:
  W_sanger = zeros(K, k_concepts, N)  # one per position
  for t in range(T_pool_passes):
    for x in pool:  # x is bundle of shape (N,)
      for p in range(K):
        x_p = x * pos_atoms[p]  # unbind position p
        y_p = W_sanger[p] @ x_p  # (k_concepts,)
        # Sanger update with lower-triangular decorrelation
        outer = y_p[:, None] * x_p[None, :]  # (k_concepts, N)
        decorr = lower_tri(y_p[:, None] * y_p[None, :]) @ W_sanger[p]
        W_sanger[p] += eta * (outer - decorr)
  # All vectorized: torch.einsum and torch.tril, no Python loop over k.

retrieval_phase:
  # R10-style fusion with sanger concepts replacing PPMI concepts.
  for query in test_set:
    # standard substrate retrieval
    pred_substrate = cleanup(W @ query)
    # sanger concept activations per position
    concept_acts = zeros(K, k_concepts)
    for p in range(K):
      q_p = query * pos_atoms[p]
      concept_acts[p] = W_sanger[p] @ q_p
    # R10 linear fusion (use same alpha, beta as R10 best-config)
    correction = concept_fusion_R10(concept_acts, alpha=alpha_best, beta=beta_best)
    pred_final = pred_substrate + correction
    record bpc

verdict_logic:
  PASS iff:
    mean(bpc_sanger - bpc_ppmi_baseline) > 0.02 across 5 seeds
    AND t-statistic > 2.0
    AND mean(bpc_sanger) > 0.628 + 0.02 (over R10 best-config baseline)
  KILL iff:
    mean(bpc_sanger - bpc_ppmi_baseline) < 0 across 5 seeds
    OR mean(bpc_sanger) within noise of byte-only baseline (no concept signal)
```

**Smoke test (queue_add gate)**: K=32, N=512, pool=64, k_concepts=8,
T_pool_passes=1. Target runtime ~10s. Pre-registered oracle assertion:
sanger should produce a W_sanger with bounded operator norm
(||W_sanger||_op < 10) — diverging Sanger fails fast.

**Self-test**: 4 synthetic cases:
- Pure Gaussian noise pool with no structure: predict Sanger components
  match top-k PCA of pool; no R10 gain.
- Pool with one strong concept (one bundle direction repeated): predict
  Sanger picks up that direction as first component; gain proportional
  to frequency.
- Pool with K=8 position-conditional concepts (high-freq bytes per
  position): predict block-Sanger recovers position-conditional means.
- Adversarial: pool with concept structure orthogonal to byte atoms —
  predict Sanger recovers it but R10 fusion can't use it (concept
  basis ≠ output basis); useful negative control.

**Wall budget.** ~5–10 GPU minutes at full scale; smoke <30s. Vs
the wave14d_sparse_vs_ppmi >5400s timeout. Two orders of magnitude
cheaper.

**Phase 2 (if Sanger lands positive).** Run InfoNCE-linear with same
config and same R10 fusion. If InfoNCE beats Sanger by ≥0.02 bpc with
t > 2, escalate to "concept extraction needs discriminative loss";
else, stay with Sanger as the substrate's native choice.

---

## Materials analog (load-bearing)

**The PCA / spectral framing.** A self-supervised concept-discovery
algorithm is a **spectral analyzer of the substrate's free energy
landscape**. The substrate's bundle distribution induces a covariance
matrix Σ = E[x xᵀ]; the eigenstructure of Σ is the substrate's
**ordered modes**, the same way a phonon spectrum is a solid's ordered
vibrational modes.

In materials terms, the four candidate families correspond to:
- **Sanger / PCA / block-PCA**: the **phonon spectrum** of the
  substrate. Each principal component is a collective excitation of
  bundle coordinates. Block-Sanger is per-position phonons — the
  substrate's analog of optical-vs-acoustic phonon separation by
  position in a unit cell.
- **InfoNCE**: a **contrastive free energy** that pulls together
  pool-pair similarities and pushes apart dissimilar ones. Materials
  analog: ferromagnetic vs anti-ferromagnetic ordering of pool
  alignments. The substrate's ordered phase under InfoNCE is exactly
  the alignment-uniformity tradeoff identified by Wang-Isola.
- **Tensor CP of W**: **mode decomposition of the stored Hamiltonian**.
  Stored memories are the substrate's energy minima; CP factors out
  the rank-1 outer products that compose the Hamiltonian into a sum
  of pure-state operators.
- **SFA** (the complement candidate): **slow modes near critical
  points**. In condensed matter, slow modes are the universal
  long-wavelength behavior near a phase transition (hydrodynamic
  modes, Goldstone modes). SFA's "slow features" are the substrate's
  analog: directions in bundle space that vary slowly across context,
  which would be the substrate's analog of long-wavelength phonons or
  Goldstone modes if there are any.

**Predictive consequence.** The substrate's α = 0.153 operating point
places it in the Hopfield ordered phase (AGS classical regime, per
wave14m_alpha_c). In ordered phases, the phonon spectrum has well-
defined modes that can be extracted spectrally. Block-Sanger should
work well *because* the substrate is in the ordered phase.

If the substrate's α were pushed toward α_c (≈ 0.138 for classical
random-key Hopfield; we measured 0.153 — slightly above), Sanger's
output would become noisy as the eigenvalue spectrum loses gap and
the modes mix. This is the substrate's analog of the spin-glass
transition; the cap_map's MP-edge phase detector
(wave14mp_edge_detector) tracks exactly this. Block-Sanger should
work below the spin-glass transition (α < α_c) and fail above it. We
operate below, so it should work.

---

## Falsifiable prediction

**Primary prediction (block-Sanger experiment):**

At N=4096, K=512, k_concepts=50, pool_size=4096, η=0.01, 3 pool passes
over a corpus where R10 best-config baseline is +0.628 bpc:

- bpc gain of block-Sanger + R10 fusion vs PPMI + R10 fusion at the
  same nc, alpha, beta: **+0.03 to +0.10 bpc** (5-seed mean, expect
  s.d. ≤ 0.02).
- Total bpc improvement over substrate-only baseline (no concepts):
  ≥ +0.65 (i.e., matches or exceeds R10 best-config + PPMI).
- Sanger weight matrix operator norm: bounded by O(1), no divergence.
- Per-position component diversity: at least 30 of 50 components per
  position carry > 5% of explained variance (not all variance in top-5).

**Secondary prediction (sanity check).**

If the per-position structure is dropped (vanilla Sanger on full
bundles without position unbinding): expected gain reverts to the
2026-05-19 PCA-on-pool prediction of 0 to +0.02 bpc. This is the
falsifier for the "block decomposition is necessary" hypothesis: if
vanilla Sanger lands inside the per-position Sanger's noise band,
the block structure isn't doing the work.

**Kill criterion.**

Block-Sanger lands at < +0.01 bpc above PPMI baseline across 5 seeds
AND vanilla Sanger lands ≥ +0.005 above block-Sanger. Either signal
kills the candidate family for substrate concept discovery; the next
research priority shifts to F3 (InfoNCE) with the same R10 fusion
harness.

If both Sanger variants AND InfoNCE land at ≤ +0.01 bpc above PPMI,
then PPMI on argmax is **information-equivalent** to the full bundle
distribution at this corpus and substrate size. That would be a real
substrate-capability finding: "the substrate's concept-discovery
ceiling is the byte K-gram statistics, regardless of which
self-supervised algorithm extracts them." Worth noting; not a failure
mode.

---

## Citations

1. Sanger (1989). "Optimal unsupervised learning in a single-layer
   linear feedforward neural network." *Neural Networks* 2, 459–473.
   DOI: 10.1016/0893-6080(89)90044-0.
   — Foundational; the Generalized Hebbian Algorithm that block-Sanger
   extends. Provides convergence proof to principal components.

2. Oja (1982). "A simplified neuron model as a principal component
   analyzer." *J. Math. Biol.* 15, 267–273.
   — The substrate-natural Hebbian PCA rule; precursor to Sanger.

3. Mairal, Bach, Ponce, Sapiro (2009). "Online learning for matrix
   factorization and sparse coding." *J. Machine Learning Research* 11,
   19–60. arXiv:0908.0050.
   — The sparse-coding algorithm wave14d_sparse_vs_ppmi was implementing
   when it hit the Python-loop block. Defines the inner-loop cost
   structure that this note's candidates avoid.

4. Kolda, Bader (2009). "Tensor decompositions and applications."
   *SIAM Review* 51, 455–500. arXiv:0810.4408.
   — Survey of tensor CP and Tucker. Closed-form ALS for the F2
   candidate.

5. van den Oord, Li, Vinyals (2018). "Representation learning with
   contrastive predictive coding." arXiv:1807.03748.
   — InfoNCE foundational paper; defines the contrastive loss for the
   F3 candidate.

6. Wang, Isola (2020). "Understanding contrastive representation
   learning through alignment and uniformity on the hypersphere."
   arXiv:2005.10242.
   — Proves InfoNCE with linear projector recovers top-k eigenvectors
   of the positive-pair covariance against marginal covariance. Key
   theoretical anchor for predicted F3 gain.

7. Robinson, Chuang, Sra, Jegelka (2021). "Contrastive learning with
   hard negative samples." arXiv:2010.04592.
   — Hard-negative-mining literature for the F3 InfoNCE engineering
   tax called out in pass 2.

8. Wiskott, Sejnowski (2002). "Slow feature analysis: unsupervised
   learning of invariances." *Neural Computation* 14, 715–770.
   DOI: 10.1162/089976602317318938.
   — Defines SFA; closed-form generalized eigendecomposition for the F4
   complement candidate.

9. Frady, Kleyko, Sommer (2018). "A theory of sequence indexing and
   working memory in recurrent neural networks." arXiv:1812.01087.
   — Substrate-foundation for the position-unbinding step in
   block-Sanger; provides the SNR analysis that lets us predict
   gain magnitude.

---

## Routing

- **Strategy**: this note proposes adding three new rows under
  "Concept structure" → research-only (🔬):
  - Block-Sanger self-supervised concept extraction (substrate-native,
    closed-loop Hebbian)
  - InfoNCE with linear projector (autograd, contrastive)
  - CP decomposition of W (closed-form ALS, diagnostic-only)
  Strategy keeps writer exclusivity; this is read-only input. Also
  proposes that E5 (vectorize learn_sparse_dictionary) can be
  **deprioritized** if block-Sanger lands the predicted gain — the
  sparse-coding path becomes redundant.

- **Experiment Dev**: this note recommends `wave14r_block_sanger_vs_ppmi`
  as a new E-candidate at higher priority than E5 (infra). Reasoning:
  block-Sanger is fully vectorized substrate-native math and tests the
  same PPMI-replacement hypothesis that sparse-coding was meant to,
  at <1% the infra cost. Smoke + multi-seed run takes ~10 GPU min total.

- **Research (this session, future cycles)**: if block-Sanger lands
  positive, R2 closes with Sanger as the answer. If block-Sanger lands
  flat, next cycle drills F3 (InfoNCE) with the same harness. If both
  flat, the substrate-capability finding is that "PPMI is
  information-equivalent to the bundle distribution at our K and N,"
  which is itself a useful cap_map row addition.
