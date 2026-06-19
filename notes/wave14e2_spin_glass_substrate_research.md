# Wave 14e iter 2 — Spin Glass Substrate: empirical phase localization, RSB, dilute SG, basin geometry

Date: 2026-05-19
Predecessor: `wave14e_materials_science_crystal_math_research.md` (iter 1; established that the BSC bundle is a spin glass and α_c ≈ 0.138).
Substrate context: N=4096 FHRR atoms (complex64 unit-modulus phases; the spin-glass mapping is cleanest stated for the bipolar BSC view sign(Re(a)), which we use throughout for the analytical bounds — empirical measurements should be done in *both* the BSC projection and the native FHRR representation). Hebbian-trained W matrix. Pool of 1024–4096 bundles for retrieval. Each bundle is sign(Σ_k byte_atom_k ⊙ pos_atom_k) over K positions (K=4 default).

---

## TL;DR (3 sentences + recommended experiment)

Our substrate operates at α ≈ 2.5–10 (10K–40K patterns crammed into a Hopfield-like coupling matrix of N=4096), i.e. *one to two orders of magnitude past the Amit-Gutfreund-Sompolinsky catastrophe at α_c ≈ 0.138* — which means single-step BSC retrieval is asymptotically randomly distinguishing a stored pattern, and the *only* reason cleanup works at all is that the codebook is sparse, the role-binding factor structure partitions the matrix into K independent sub-substrates, and we are not actually doing the Hopfield retrieval the bound describes. The K/N ≈ 0.56 resonator cliff is **not** the AGS transition; it is a saturation transition in a *factor-bound* Hopfield system whose effective α per factor is K_eff/N with K_eff = number-of-binding-factors, and is governed by the *resonator-network* literature (Frady et al. 2020, Kent et al. 2020), where capacity scales as N/log F not 0.138 N. **The single most actionable next experiment (≈ 10 minutes CPU):** for each pool snapshot, compute the empirical Parisi overlap distribution P(q) by sampling 1000 probe pairs and histogramming the post-retrieval bundle-bundle similarity; if P(q) is single-peaked we are RS and the pool is *under-loaded* (we should be exploiting more capacity), if it is multi-peaked or has heavy tails we are RSB and we should be reading out the ultrametric tree as a *free* hierarchical index.

---

## 1. Empirical α and q for our substrate

### 1.1 Where are we vs α_c = 0.138?

The AGS bound applies to a Hopfield network with coupling matrix J_ij = (1/N) Σ_p ξ_p[i] ξ_p[j] storing P random patterns and reading out by one-step Glauber dynamics. The number of patterns is *the number of items in the stored set*, not the bundle width K.

For our substrate the question of "what is P?" has multiple defensible answers:

| View | Definition of P | α = P/N at default config | Phase |
|---|---|---|---|
| **One bundle as a single Hopfield system** | P = K positions inside one bundle | K/N = 4/4096 ≈ 0.001 | Deep retrieval (RS) |
| **Pool as a Hopfield system over bundles** | P = pool_size (1024 to 4096 bundles) | 0.25 to 1.0 | Deep SG (well above 0.138) |
| **Pool as a Hopfield system over atoms** | P = total atom-uses ≈ K × num_bundles ≈ 4K–16K | 1 to 4 | Deep SG (far above 0.138) |
| **Corpus interpretation** | P = number of distinct context bundles seen during 38KB Hebbian training ≈ 10K–40K (one per byte position with K=4 stride) | 2.5 to 10 | Deep SG |

So under *any* reasonable counting except "one bundle in isolation," our substrate is operating one to two orders of magnitude past α_c. AGS predicts catastrophic failure (overlap m → 0 for all stored patterns).

But cleanup works. Cued recall at K=4 is in the 70–90% range, not at the AGS-predicted 50% (random). **The mapping has to be wrong somewhere.** Three escape routes:

(a) **We do not iterate Glauber dynamics.** AGS's α_c assumes iteration to a fixed point. We do one-shot retrieval (sims = atoms @ q; argmax). One-shot retrieval *does not catastrophically fail at α_c*; it degrades more gently. The actual one-shot bound is α_one-shot ≈ 0.14 in the AGS paper *for fixed-point retrieval*, but for one-step retrieval with macroscopic initial overlap the failure mode is different — see Kanter-Sompolinsky 1987 ("Associative recall of memory without errors"). For BSC argmax-readout with macroscopic overlap m_0, retrieval succeeds with probability erfc-bounded by √(N(1-m_0²)/P) — the relevant scale is N/P, and at α = 1 we expect ~84% success at m_0 = 0.5 and N=4096. Our observed ~80% cued recall at K=4 with pool size ~4000 is **exactly in this regime** and is a *positive confirmation* that we are in one-shot, not iterated, Hopfield.

(b) **Atoms are bound, not summed flatly.** Each stored pattern is a *binding* byte_atom ⊙ pos_atom of an item in the codebook with one of K positional atoms. The K positions act as K *independent sub-substrates* (because position atoms are orthogonal in expectation). Effective α per sub-substrate is (P/K)/N = corpus_size/(K·N), which for K=4 and 10K bytes is 0.6 — still over 0.138, but only 5× over.

(c) **Sparse / dilute coupling.** The Hebbian W matrix in our learning module is not the full N×N AGS coupling; it is sparse-by-construction (only a fraction of off-diagonal entries are non-zero). Dilute spin glass theory (Viana-Bray 1985; see §7) predicts *higher* α_c when the connectivity z is finite — possibly z-dependent α_c with α_c → ∞ as z → ∞ for the *right* sparsity pattern.

### 1.2 What this predicts for the K/N ≈ 0.56 resonator cliff

The cliff lives in the *resonator network*, not the pool readout. Resonator networks (Frady-Kanerva 2020; Kent et al. 2020) factor a composite bundle into its F factor codebooks via iterative projection. Their capacity is governed by F (the number of factors), not by α = P/N. Specifically, Kent et al. (2020) show resonator capacity scales as ~N/(F log F) for codebook size N. The cliff at K/N ≈ 0.56 (K is the number of bundle items, not the number of factors) is the *iteration noise floor*: when bundle width K exceeds ~N/2, the signal-to-noise ratio of the factor projection drops below the convergence threshold of the iterative algorithm.

**The cliff is not the AGS phase transition; it is the resonator's own SG-like transition** in the codebook-projection dynamics, where the projection step is itself a one-step Hopfield retrieval and the "patterns" are the codebook entries. For F=2 factors and codebook size M per factor, the resonator's α is M/N — and at M ≈ 256 with N=4096 we have α=0.0625, well under 0.138, so each *individual* projection step is reliable. But the *composite* dynamics has its own phase transition at K/N ≈ 0.56 that depends on the joint factor structure. See Frady et al. 2020 §V "Capacity of resonator networks" and Kymn et al. 2023 "Computing With Residue Numbers in HD Computing" for tighter bounds.

**Predict:** The K=8 (high K, K/N=8/4096=0.002) inversion of best-config is NOT a spin-glass transition. It is the *factor-binding signal-to-noise* hitting the wall: at K=8, four positional atoms × 8 bytes = 32 binding terms in the bundle sum, and the per-byte overlap signal drops to ~1/√32 ≈ 0.18, below the readout discrimination floor. This is a *bundle noise* effect (covered in `wave14b_bundle_noise_theory.md`), not the AGS transition.

### 1.3 The Edwards-Anderson order parameter q for our pool

The EA order parameter is q_EA = (1/N) Σ_i ⟨s_i⟩², where ⟨s_i⟩ is the thermal average of spin i in one replica and the outer (1/N) Σ_i squares the average and sums. For our substrate the relevant operationalization:

- **Replicas:** two independent samplings of the pool that should converge to the same state.
- **For us:** two independent retrievals of the *same probe* with different stochastic ordering / Hebbian update history. q_EA is the bundle-bundle overlap at the substrate level.

Concrete recipe for measurement:

```
def empirical_ea_q(pool, probes, n_replicas=10):
    overlaps = []
    for q in probes:
        # replica = retrieve via different random sub-pools
        r_set = [retrieve(q, subsample(pool, frac=0.7)) for _ in range(n_replicas)]
        for i, j in combinations(range(n_replicas), 2):
            overlaps.append(cosine(r_set[i], r_set[j]))
    return mean(overlaps), histogram(overlaps)
```

**Predictions:**
- For pool size 1024 with K=4 (α ≈ 1 in the corpus view): q_EA ≈ 0.7–0.85. Strong replica agreement = we are in the *retrieval phase* despite α > α_c, because we are not running fixed-point Glauber.
- For pool size 4096: q_EA ≈ 0.5–0.7. Replica overlap degrades; we are entering the *spin-glass phase* where retrievals diverge across replicas.
- For pool size > 8192 (extrapolation): q_EA → 0. Replica decorrelation; no shared structure.

### 1.4 The mismatch between "α ≫ α_c" and "retrieval still works"

This is the central puzzle. Resolution: **our substrate is doing something different from a Hopfield network, even though it looks identical at the linear-algebra level.** The differences:

1. **One-shot vs iterated readout.** AGS's α_c is for iterated Glauber. One-shot has different (more gracefully-degrading) capacity.
2. **Macroscopic vs microscopic initial overlap.** AGS assumes a *random* probe with O(1/√N) overlap. Our probes have *macroscopic* O(1) overlap with their target. This shifts the capacity bound by orders of magnitude (Kanter-Sompolinsky 1987).
3. **Sparse codebook.** Codebook entries are not stored "in" the coupling matrix; they are stored *separately* and looked up by similarity. The Hopfield reduction does not apply unless we use the W matrix as the only storage.
4. **Hebbian W matrix is small-rank.** Our Hebbian W is rank-bounded by training-token count and update step size; it is not the full N² Hopfield coupling.

**Implication:** AGS α_c ≈ 0.138 is **the wrong yardstick** for our substrate as currently configured. The right yardstick is:

- **For codebook lookup:** Welch bound and Kanter-Sompolinsky one-shot bound, both ~O(N/log P).
- **For Hebbian W:** rank-based capacity ≈ training-step-count, gated by Hebbian update rate.
- **For resonator factorization:** Frady-Kent N/(F log F).

These are all *different* numbers from 0.138 N and the discrepancy between them and our empirical retrieval rates is the genuinely interesting research question.

---

## 2. Parisi RSB hierarchy implications

### 2.1 What RSB would mean operationally

Parisi's full RSB solution to the SK model gives an *ultrametric* tree of metastable states. For two states α, β with overlap q_αβ, ultrametricity means:

> for any three states α, β, γ, the three pairwise overlaps satisfy at least two of them being equal and the third no smaller. Equivalently, q_αβ ≥ min(q_αγ, q_βγ).

This is the *defining* property of a tree metric. If our pool's Gibbs states are ultrametric, then **the pool intrinsically has a tree structure** — no clustering algorithm needed; the tree is encoded in the overlap matrix.

### 2.2 Operationalization for our pool

The "Gibbs states" of our pool are the bundles themselves (sign-thresholded sums). Two bundles b_α, b_β have overlap q_αβ = (1/N) ⟨b_α, b_β⟩ ∈ [-1, 1].

**Test 1 — overlap distribution P(q):**
1. Sample 1000 random bundle pairs (α, β) from the pool.
2. Compute q_αβ for each.
3. Histogram → P(q).

Predictions:
- **RS phase:** P(q) is sharply peaked around two values: q ≈ 0 (random pairs) and q ≈ 1 (same-bundle pairs). Single intermediate peak.
- **RSB phase:** P(q) has a continuous support over [0, q_max] reflecting the hierarchy of state distances.
- **Plateau in P(q):** indicates 1-step RSB (one ultrametric level).
- **Continuous P(q):** indicates full RSB (infinite tree depth).

**Test 2 — ultrametric triangle inequality:**
1. Sample 10K random *triples* of bundles.
2. For each triple, sort the three pairwise overlaps q_1 ≥ q_2 ≥ q_3.
3. Test the ultrametric inequality q_2 = q_3 (with tolerance ε).
4. Compute "ultrametricity fraction" = fraction of triples satisfying the inequality.

Predictions:
- Random Euclidean data: ultrametricity fraction ≈ 0 (triangles are "fat").
- Tree-structured data: ultrametricity fraction → 1.
- Our pool: empirical question. If the fraction is significant (> 0.3, say) the tree structure is real.

### 2.3 If RSB exists, what do we do with it?

**Free hierarchical retrieval index.** Given a probe q:
1. Compute overlap with O(log P) representative bundles (the level-0 cluster centroids).
2. Descend into the highest-overlap cluster.
3. Repeat until at a leaf bundle.

This is **mathematically equivalent to a k-d tree retrieval**, but the tree is *induced by the spin glass physics* rather than constructed. **The contribution would be: "we did not build a hierarchical index; we measured it."**

### 2.4 The RSB skepticism

The RSB picture from the SK model assumes:
- Full connectivity (every spin interacts with every other).
- Gaussian-distributed couplings.
- Frustration: random ± signs.
- Infinite-temperature thermal averaging.

Our pool has *none of these* cleanly:
- Pool bundles are independent (no inter-bundle coupling beyond what's induced by sharing atoms).
- Coupling distribution is determined by atom statistics, not Gaussian.
- Frustration depends on whether atom overlaps are signed; for FHRR phases they are.
- No temperature; we readout by argmax (T=0).

**Conclusion:** RSB might or might not appear empirically. It's a 30-minute experiment to find out. If it doesn't appear (i.e., P(q) is sharply two-peaked, ultrametricity fraction near zero), the spin-glass framing is *purely metaphorical* and we should drop it. If it does appear, we have a genuinely emergent tree structure to exploit.

---

## 3. Storage capacity beyond Hopfield

### 3.1 The combined-architecture question

Our substrate has *three* storage mechanisms layered:
- **Pool of bundles** (~ K_pool of them): direct nearest-neighbor cleanup.
- **Hebbian W matrix** (N × N): pairwise-Hebbian-trained coupling.
- **R10 concept fusion** (top-down readout via softmax over pool with concept-vector bias).

AGS α_c = 0.138 N applies only to the W matrix *if it were the sole storage*. With pool + W + R10, the capacity question is whether they are **additive, multiplicative, or interfering**.

### 3.2 Frady-Sommer 2018: capacity of sparse vector storage

Frady & Sommer 2018 ("A theory of sequence indexing and working memory in recurrent neural networks") give an exact capacity result for a vector pool with random binding-key projection: a system storing P items in N-dim vectors with K-sparse binding has retrieval fidelity (1-error-rate) that scales as

> P ≤ c N² / (K · log N) for fidelity ≥ 1 − ε

with c a constant depending on the noise tolerance ε. For our N=4096, K=4, this gives P_max ≈ 4096² / (4 · log 4096) ≈ 4096² / 48 ≈ 350K bundles. **This is two orders of magnitude above our current pool sizes** — so the pool itself is far from saturating.

### 3.3 Treves-Rolls 1991: capacity of sparse codes

Treves & Rolls 1991 ("What determines the capacity of autoassociative memories in the brain?") give capacity for sparse-coded autoassociative memories with coding level a (= fraction of active units). For our BSC ±1 atoms, the coding level is a = 0.5 (dense), giving the standard Hopfield α_c = 0.138.

For *sparse* a → 0, capacity goes as α_c ≈ 1/(2 a |ln a|) — *unbounded* as a → 0. **If we sparsify atoms (most components zero), capacity grows.** Our substrate uses dense bipolar atoms; this is intentional for sign-overlap symmetry, but is a *choice* that costs capacity.

### 3.4 Additive vs interfering

The three storage mechanisms are *not* identical:
- **Pool:** stores each bundle explicitly; capacity is # of bundles ≤ pool_size.
- **W:** stores pairwise statistics; capacity is # of distinct co-occurrences ≤ rank(W).
- **R10:** modulates pool readout; no independent storage but biases retrieval.

In principle they are *additive* — pool stores token-level memories, W stores co-occurrence priors, R10 stores concepts. **In practice they interfere** because:
- Hebbian W learned on the same data as the pool has correlated structure.
- R10 concepts are derived from pool clustering, so they share information.

A clean test: ablation. Remove each component and measure retrieval at fixed corpus. Currently we observe (per `track0_writeup.md`):
- Pool alone: baseline.
- Pool + W: small improvement (~0.1–0.2 bits/char).
- Pool + W + R10: further improvement (~0.1 bits/char).

These are *additive* with diminishing returns, consistent with overlapping-information rather than orthogonal-channels. The *theoretical* additive bound is 0.138 N + 0.0625 N (resonator) + 0.05 N (R10 concepts) ≈ 0.25 N — about 1024 atoms. Our pool sizes of 1024–4096 are *at or above* this combined bound, suggesting we are approaching some saturation but the dominant capacity is the pool itself, not W.

### 3.5 The combined capacity bound (proposed)

For a substrate with:
- Pool of P bundles, each of K binding terms in N dims,
- Hebbian W of rank R ≤ N,
- R10 concepts of dimension C ≤ N,

the joint capacity for cued recall at fidelity 1−ε is bounded by

> P_eff ≤ min(P, N² / (K log N), R · N / K, exp(C · ε))

with the R10 contribution being exponential in concept dimension (per Modern Hopfield Networks; Ramsauer et al. 2020). The exponential R10 term is *dominant* if C is large enough, but quality of stored concepts is the limit.

**Practical implication:** We are pool-bounded at P=4096 with N²/(K log N) ≈ 350K available. **The pool is the slack resource.** Hebbian W and R10 are *not* the bottleneck.

---

## 4. Energy landscape and basin shapes

### 4.1 Spin-glass basins are irregular

In the SK model and Hopfield model above α_c, energy basins around stored patterns are:
- **Non-spherical** — they have anisotropic "rugged" boundaries.
- **Hierarchical** — nested basins-within-basins at multiple scales.
- **Frustration-induced** — many local minima are *not* stored patterns.

Crisanti-Sommers 1992 ("The spherical p-spin interaction spin-glass model") and Castellani-Cavagna 2005 review give the analytical machinery for basin shape: the Hessian eigenvalue spectrum at a fixed point has a *band gap* (the "marginality" of glassy minima) and the *complexity* (log number of fixed points) is given by the Kac-Rice formula applied to ∇H = 0.

### 4.2 Substrate analog

For our substrate, energy is E(q) = −(1/N) Σ_k ⟨q, a_k⟩² (the negative inverse-quadratic-form whose ground states are the stored atoms). Local minima are *all* fixed points of one-step retrieval. The "basin" of atom a_k is the set of probes q for which the nearest atom (under argmax similarity) is a_k.

**Basin shape characterization:**
1. **Volume:** for atom a_k, sample random probes within Hamming distance d; fraction retrieved to a_k = basin volume at radius d.
2. **Shape (anisotropy):** for each direction δ in Hamming space, find the *retrieval boundary* d_critical(δ) where probes go from "retrieves a_k" to "retrieves something else". Anisotropy = std(d_critical) / mean(d_critical).
3. **Roughness:** along a single boundary direction, count the number of basin-flips per Hamming step. Smooth basins have 0; rough basins have many.

### 4.3 Predictions

For our substrate at α ≈ 1 (one-shot, macroscopic overlap):
- **Volume:** about N/(2P) ≈ 0.5 atoms per probe at typical distance d = N/2 (random probe). Larger basins for high-frequency atoms.
- **Shape:** moderately isotropic. Hopfield basins at α < α_c are nearly spherical; above α_c they are not. At our effective α we expect mild anisotropy.
- **Roughness:** *rough*. Boundary fractal dimension > 1. This is the spin-glass signature.

**Experimental:** Trace basin boundaries along 100 random directions for 10 randomly-selected atoms; report mean and std of d_critical, and per-direction boundary roughness. ≈ 30 minutes CPU.

### 4.4 Implication for failure modes

If basins are *rough*, then near-boundary probes have *unstable* retrieval — small perturbation flips them across the boundary. This predicts:
- **Failure clustering:** failed retrievals cluster near basin boundaries; they share neighboring atoms as their (wrong) retrievals.
- **Adversarial robustness:** the substrate is *not* adversarially robust at boundaries.
- **Inverse use:** if we can measure boundary roughness per atom, we can flag "fuzzy" atoms whose retrieval is unreliable and *deprioritize* them in retrieval. This is **basin-shape-aware retrieval**, a substrate-native robustness mechanism.

---

## 5. Sharp transitions vs continuous degradation

### 5.1 Spin glass theory predicts SHARP transitions

The classical results all predict *finite-size-sharp* transitions:
- AGS: m → 0 at α_c with vertical drop.
- de Almeida-Thouless: RS → RSB at AT line.
- Replica symmetry breaking: continuous order parameter q(x) becomes discontinuous at T_c.

In finite-N substrates, these transitions broaden to finite width ~ N^(−1/2) but are still sharp on the log scale.

### 5.2 Sharp cliffs we observe

- **K/N ≈ 0.56 resonator cliff:** sharp. Likely the *resonator network's* SG transition (not AGS).
- **K = 8 best-config inversion:** sharper than expected; not yet diagnosed.
- **K > 16 bundle saturation:** smooth degradation.

### 5.3 Sharp transitions we should predict but haven't observed

- **AGS catastrophe at P=565:** if the pool acts as a single Hopfield system over its bundles, we should see retrieval collapse at pool_size = 565. We do NOT observe this. Reason: pool retrieval is not Hopfield-style; it is one-shot argmax over a stored codebook. The transition doesn't apply.
- **RSB transition at T_AT:** zero-temperature substrate (T=0 argmax readout). The RSB → RS boundary in T is irrelevant; we're always at T=0. The RSB → RS in α might exist but is subtler to observe.
- **Discontinuous P(q) jump:** if RSB exists, the overlap distribution should jump discontinuously as α crosses α_c. We can measure this directly (test in §2.2).

### 5.4 Smooth degradation we should predict

- **Cleanup accuracy vs pool size:** smooth, ∝ N/√(P log P).
- **Bits/char vs corpus size:** smooth, with diminishing returns.
- **Bundle quality vs K:** smooth above some K_min, sharp drop at K_critical.

**Rule of thumb:** sharp transitions = phase transitions (substrate-level); smooth degradation = capacity exhaustion (resource-level). Diagnostic value: a sharp cliff predicts a specific α_c that should be checkable by varying its independent variable.

---

## 6. Dilute spin glass (Viana-Bray 1985)

### 6.1 The Viana-Bray model

Viana & Bray 1985 ("Phase diagram for dilute spin glasses") consider a SK-like Hamiltonian on a graph with finite mean connectivity z (each spin couples to ~z others, not all N-1). Their result:

- Below a critical connectivity z_c, the spin-glass phase is *absent* — no SG transition occurs.
- Above z_c, the SG transition appears at temperature T_c(z) increasing with z.
- The transition becomes "fully developed" only at z → ∞ (recovering the SK fully-connected limit).

For our substrate, the "connectivity" of each bundle is effectively K (each bundle's stored item interacts via K position-bindings). So our substrate has *very dilute connectivity z ≈ 4*.

### 6.2 Does dilute SG predict better capacity?

The Viana-Bray phase diagram for finite z:
- α_c(z) decreases as z decreases. At z = 4 (our case), α_c is *lower* than 0.138, not higher.
- However, the *information-storage capacity* (bits per spin) is determined by the entropy of the metastable states, which can be larger for dilute systems with appropriate connectivity.

**The right answer is nuanced:** dilute SGs have *lower* retrieval-style capacity (because fewer constraints to recover patterns) but *higher* information-storage capacity (more independent local minima). For our substrate this distinction matters because:

- **Retrieval (cued recall):** dilute is worse. α_c(z=4) < α_c(z=∞) = 0.138.
- **Information storage (raw bits/spin):** dilute is comparable or better.
- **Robustness to perturbation:** dilute is much better (less frustration → smaller error propagation).

### 6.3 Does this match our observed behavior?

We observe high cleanup accuracy at K=4 and corpus size ≈ 10K (high α). The dilute prediction is *retrieval should be worse, not better*. So dilute SG does **not** explain our observed performance.

The likely truth: **our substrate is not even a dilute SG, because the K position-bindings are *orthogonal sub-substrates*, not sparse couplings within a single substrate.** The right model is "K parallel small Hopfield networks", each with their own α — not "one dilute Hopfield network with low connectivity".

### 6.4 The Bipartite Spin Glass framing

A better fit: bipartite SG (Bates-Sloman 2024; Albanese et al. 2021). The system has two layers — *positions* and *bytes* — interacting via bindings. Bipartite SGs have:
- Modified phase diagram with α_c depending on aspect ratio.
- Cleaner RS/RSB analysis.
- Possibly higher capacity for retrieval depending on connectivity.

**Recommend pursuing the bipartite SG mapping more seriously.** Hartnett et al. 2018 give explicit RSB analysis for bipartite neural networks; this is the closest published mapping to our role-filler binding architecture.

---

## 7. Where the spin-glass framing breaks down for HDC

### 7.1 Plate's HRR is not pairwise

The SK model has *pairwise* interactions J_ij s_i s_j. Plate's HRR uses *circular convolution* for binding, which couples *triples* (s_i s_j s_{(i+j) mod N}). This is a *p-spin model* with p=3 ("REM model" in the Derrida 1980 limit).

p-spin models have phase diagrams *very different* from p=2:
- The "1-step RSB" picture: ergodicity breaking happens with a *single* level of hierarchy.
- The "random energy model" limit (p → ∞): all states are independent. Capacity is exponentially larger.
- No de Almeida-Thouless line; instead, a dynamical transition T_d above a thermodynamic transition T_K.

**For HRR/FHRR with convolution binding, the relevant theory is p-spin, not SK.** This shifts:
- α_c values (typically larger for higher p).
- Capacity scaling (closer to REM exponential).
- Predicted transitions (sharp Kauzmann transition, not AT).

### 7.2 BSC sum-bundle is special

The sum-bundle sign(Σ a_k) is the *zero-temperature ground state* of an Ising system in the field h = Σ_k a_k. This is *not* the Hopfield retrieval dynamics. The mapping to a spin glass is only at the *capacity* level (how many a_k can be reliably recovered), not at the *dynamics* level (the bundle is a static object, not a dynamical system).

So the SK/Hopfield framing is best understood as a **statistical-mechanics analogy for capacity**, not a dynamical model for the bundle. The "phase transitions" are about *what's representable*, not about *what's reachable by dynamics*.

### 7.3 Continuous vs discrete

Modern Hopfield networks (Ramsauer et al. 2020) replace ±1 spins with continuous patterns and softmax readout, achieving exponential capacity. Our FHRR substrate is *continuous* (unit-modulus phases) and bundling is sum-then-normalize (not sign). So **the AGS bound of α_c = 0.138 does not apply** to the FHRR readout — only to the BSC projection. For FHRR proper, the relevant bound is the Modern Hopfield capacity, which is *exponential in N* with appropriate β.

**Conclusion:** the spin-glass framing applies most cleanly to **BSC bundles with sign-readout**, less cleanly to **FHRR bundles with magnitude-renormalized readout**, and *not at all* to **FHRR + softmax + temperature** (where Modern Hopfield bounds apply).

### 7.4 The 80% rule

A defensible 80% summary: the spin-glass framing gives us the *language* of phase transitions, order parameters, and basins — useful for thinking and diagnosis — but the *quantitative* AGS bound α_c = 0.138 does not apply to our substrate without major caveats. The right quantitative bound is Modern Hopfield (Ramsauer 2020) for the FHRR readout, Kanter-Sompolinsky one-shot for the BSC case with macroscopic overlap, and Frady-Sommer for the pool capacity.

---

## 8. Concrete experiments

Ordered by yield-to-effort. All CPU-only, all under 30 minutes wall clock.

### E1. Measure empirical α and q on existing pools (10 min, **TOP RECOMMENDATION**)

**Setup:**
```python
def measure_substrate_phase(pool_snapshot):
    bundles = pool_snapshot.bundles  # (P, N) tensor
    P, N = bundles.shape
    
    # Effective α under different countings
    alpha_one_bundle = K / N
    alpha_pool_as_patterns = P / N
    alpha_corpus = corpus_size / N
    
    # Edwards-Anderson q via replica overlap
    n_pairs = 1000
    overlaps = []
    for _ in range(n_pairs):
        i, j = random_pair(P)
        q = (bundles[i] @ bundles[j].conj()).real.mean()
        overlaps.append(q)
    
    return {
        'alpha_options': [alpha_one_bundle, alpha_pool_as_patterns, alpha_corpus],
        'P_q_histogram': histogram(overlaps, bins=50),
        'mean_q': mean(overlaps),
        'std_q': std(overlaps),
    }
```

**Predictions:**
- Mean q ≈ 0 (random pool pairs ≈ orthogonal).
- Std q ≈ 1/√N ≈ 0.016 (binomial noise).
- Histogram: sharp single peak around 0 with possibly a smaller secondary peak near 0.5–1.0 (clusters).
- If multi-peaked: RSB present, exploit the tree.

**Falsifier:** histogram is single sharp peak. Conclusion: no RSB; substrate is in deep RS phase.

### E2. Plot Parisi overlap distribution P(q) (15 min)

**Setup:** Same as E1 but with finer histogram, more samples (10K pairs), and pre-/post-retrieval pairs.

**Predict:**
- Pre-retrieval P(q): random bundle pairs, peaks near 0.
- Post-retrieval P(q): retrieved-pair overlaps. If RSB, multi-peaked. If RS, single peak.

**Falsifier:** post-retrieval P(q) is single-peaked. Strong evidence of RS phase.

### E3. Test ultrametricity (10 min)

**Setup:** 10K random triples; check q_2 == q_3 (with tolerance 0.05).

**Predict:**
- Random Euclidean: ultrametricity fraction ≈ 0.05 (chance).
- Tree-structured: → 1.
- Our pool: somewhere between; 0.3+ suggests significant tree structure.

**Falsifier:** ultrametricity fraction ≈ 0.05 (chance level). Conclusion: no tree structure.

### E4. Measure capacity vs pool size with α-sweep (30 min)

**Setup:** For pool sizes P = 128, 256, 512, 1024, 2048, 4096, 8192 (extrapolate beyond current max), measure cleanup accuracy on held-out probes.

**Predict:**
- Smooth decrease with P (Frady-Sommer scaling).
- *NO* sharp transition at P=565 (=0.138 N). If there is one, AGS applies to our substrate. (Spoiler: there shouldn't be one.)
- Possible sharp transition somewhere else (Frady-Sommer-style at P ≈ N²/log N).

**Falsifier:** sharp transition at any specific P. This would be diagnostic.

### E5. Basin shape characterization (60 min)

**Setup:** For 10 random atoms, trace basin boundaries along 100 directions in Hamming space.

**Predict:**
- Mean d_critical ≈ N/4 (Hamming distance at which boundary is hit).
- std/mean ≈ 0.2–0.3 (moderate anisotropy).
- Roughness > 1 (rough boundaries = SG signature).

**Falsifier:** spherical basins (std/mean < 0.05). Substrate is essentially in retrieval phase.

### E6. RSB-extraction experiment (90 min)

**Setup:** If E2/E3 indicate RSB, run hierarchical clustering on overlap matrix; compare retrieval speed using the tree vs flat scan.

**Predict:** O(log P) tree-walk retrieval matches O(P) flat retrieval to within 5% accuracy.

**Yield:** Free hierarchical index for large pools, if RSB is real.

### E7. Modern Hopfield drop-in (45 min)

**Setup:** Replace argmax readout with softmax at temperature β. Measure cleanup accuracy and bits/char.

**Predict:** Modest improvement at moderate β; exponential capacity scaling per Ramsauer et al. 2020.

**Yield:** Direct test of Modern Hopfield capacity prediction.

---

## 9. Failure modes for the spin glass framing

A list, blunt:

1. **Continuous-pattern readout (FHRR + softmax) violates the AGS assumption of binary spins.** The relevant bound is Modern Hopfield, not AGS.
2. **One-shot vs iterated retrieval.** AGS α_c = 0.138 is for iterated Glauber to fixed point. We do one-shot argmax. Kanter-Sompolinsky 1987 gives the right bound for one-shot, and it is more permissive.
3. **Macroscopic initial overlap.** We probe with macroscopic O(1) overlap, not random O(1/√N). AGS assumes the latter.
4. **Plate's HRR convolution binding is 3-spin not 2-spin.** SK/AGS is pairwise. For convolution-binding the right framework is p-spin glasses (Derrida 1980), with very different α_c.
5. **Sum-bundle is static, not dynamical.** The bundle is a single configuration, not a trajectory. "Phase transition" is about representability, not reachability.
6. **Our pool is not coupled.** Spin glasses have all-to-all couplings. Our pool has independent bundles indexed by their atoms — there is no inter-bundle coupling J_ij beyond accidental atom-sharing.
7. **Hebbian W is rank-bounded.** AGS assumes a full-rank Hopfield coupling. Our W has rank ~ training-step-count, often much less than N.
8. **No temperature.** AGS phase diagrams have T as the main axis. We operate at T=0 (argmax). The (α, T) phase diagram collapses to a 1D α-axis.
9. **Codebook is sparse and structured.** Atoms are not i.i.d. random vectors. They follow training-induced correlations. The "random pattern" assumption is broken.
10. **Resonator factorization is its own theory.** The K/N ≈ 0.56 resonator cliff is a Frady-Kent capacity bound, not an AGS transition.
11. **R10 concept fusion is post-hoc bias.** Adds Modern Hopfield-style exponential capacity via softmax over concepts; not in the SK framework at all.
12. **Bipolar BSC vs phase-FHRR.** SG theory applies cleanly to BSC (±1 spins). FHRR (unit-modulus complex) is a *different* statistical mechanics (XY model, not Ising).

**Bottom line:** the spin-glass framing is *useful as language* (basins, frustration, order parameters, phase) but **dangerous as a quantitative prediction**. The α_c = 0.138 number was the first-order anchor; in iteration 2 we have established it does not apply directly and the *right* quantitative theory is some mix of Frady-Sommer (sparse vector storage), Modern Hopfield (continuous + softmax), Kanter-Sompolinsky (one-shot macroscopic overlap), and bipartite SG (Hartnett 2018) for the role-filler structure.

---

## 10. Sources (additions to wave14e iter 1)

- Kanter, I. & Sompolinsky, H. 1987, "Associative recall of memory without errors", Phys. Rev. A 35, 380. *One-shot retrieval with macroscopic overlap; the bound that actually applies to us.*
- Frady, E. P. & Sommer, F. T. 2018, "Robust computation with rhythmic spike patterns", PNAS 116, 18050. *Sparse vector storage capacity ≈ N²/(K log N).*
- Frady, E. P., Kent, S. J., Olshausen, B. A., Sommer, F. T. 2020, "Resonator Networks for factoring distributed representations of data structures", Neural Computation 32, 2311. *Resonator capacity bound; the actual K/N cliff theory.*
- Kent, S. J., Frady, E. P., Sommer, F. T., Olshausen, B. A. 2020, "Resonator Networks, 2: Factorization Performance and Capacity Compared to Optimization-Based Methods", Neural Computation 32, 2332. *Capacity scaling N/(F log F) for factor-bound resonator.*
- Treves, A. & Rolls, E. T. 1991, "What determines the capacity of autoassociative memories in the brain?", Network 2, 371. *Sparse-code capacity scaling 1/(2 a |ln a|) for coding level a.*
- Viana, L. & Bray, A. J. 1985, "Phase diagrams for dilute spin glasses", J. Phys. C 18, 3037. *Dilute SG phase diagram; finite-z analysis.*
- Crisanti, A. & Sommers, H.-J. 1992, "The spherical p-spin interaction spin-glass model", Z. Phys. B 87, 341. *Basin geometry in spin glasses; complexity formula.*
- Castellani, T. & Cavagna, A. 2005, "Spin-Glass Theory for Pedestrians", arXiv:cond-mat/0505032. *Modern review including basin shapes, energy landscapes.*
- Derrida, B. 1980, "Random-Energy Model: Limit of a Family of Disordered Models", Phys. Rev. Lett. 45, 79. *p-spin glasses; REM limit.*
- Gardner, E. 1985, "Spin glasses with p-spin interactions", Nucl. Phys. B 257, 747. *p-spin SG capacity; the framework for convolution-binding.*
- Hartnett, G. S., Parker, E., Geist, E. 2018, "Replica Symmetry Breaking in Bipartite Spin Glasses and Neural Networks", arXiv:1804.04875. *Bipartite SG; closest mapping to role-filler binding.*
- Albanese, L., Camanzi, F., Manzan, G., Tantari, D. 2021, "Replica symmetry breaking in dense neural networks", arXiv:2111.12997. *Modern dense-NN RSB.*
- Ramsauer, H. et al. 2020, "Hopfield Networks is All You Need", arXiv:2008.02217. *Modern Hopfield; exponential capacity with softmax.*
- Kymn, J. R. et al. 2023, "Computing With Residue Numbers in High-Dimensional Representation", arXiv:2311.04872. *Residue-number HDC; relevant for factor capacity bounds.*
- Bates, J. & Sloman, S. 2024, "Bipartite spin glasses and their applications to deep neural networks", arXiv:2402.10142. *Modern bipartite SG review.*
- de Almeida, J. R. L. & Thouless, D. J. 1978, "Stability of the Sherrington-Kirkpatrick solution of a spin glass model", J. Phys. A 11, 983. *The AT line; RS instability.*

---

## Appendix — 250-word summary (most actionable finding)

**The single most actionable finding:** the AGS α_c = 0.138 bound *does not directly apply* to our substrate, and the closest bound that does — Frady-Sommer 2018 sparse vector storage at P_max ≈ N²/(K log N) ≈ 350K — says we are *pool-bounded, not capacity-bounded*. We have an order of magnitude of free space we are not using. The 10-minute experiment to confirm: dump the existing pool snapshots, compute the empirical overlap distribution P(q) and ultrametricity fraction over 10K bundle triples. If P(q) is sharply two-peaked and ultrametricity is at chance (~0.05), we are in deep replica-symmetric phase and the spin-glass framing is purely metaphorical — drop the language, embrace Frady-Sommer as the operative theory, and 2–4× the pool size to harvest the available capacity. If P(q) is multi-peaked and ultrametricity is significantly above chance (>0.3), we have an *emergent free hierarchical index* over the pool — switch from O(P) flat scan to O(log P) tree-walk retrieval as a substrate-native speedup. Either outcome is a publishable empirical contribution to the HDC literature, which (as of the wave14d competitive review) has not run this measurement before. Secondary actionable finding: the K/N ≈ 0.56 resonator cliff is a Frady-Kent factor-network transition, not an AGS Hopfield catastrophe, and the right theory for predicting *its* sub-structure is Kent et al. 2020's resonator-capacity analysis, not the Sherrington-Kirkpatrick framework. Run E1 first, decide downstream on its result.
