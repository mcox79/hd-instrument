# Wave 14e — Materials Science / Crystal Structure Math for HDC/VSA Substrates

Date: 2026-05-19
Substrate context: N=4096 BSC bipolar atoms (each dim in {+1,-1}); bundling = sum-then-sign; binding = element-wise product (XOR-equivalent). The substrate is mathematically an Ising spin system on N sites with a particular ensemble of "spin configurations" (atoms) and a sign-majority readout. This note works the materials-science / crystallography corner without assuming the mapping helps; the contribution we want is the *mapping itself*, audited.

---

## TL;DR — top 3 transferable insights

1. **The bundle is a spin glass; capacity is governed by Amit-Gutfreund-Sompolinsky physics, not by intuitive "how many atoms fit in N bits".** When we bundle K atoms by sum-then-sign and read out by sign-overlap, the bundle plays the role of a Hopfield network's coupling matrix evaluated on a probe, and the relevant capacity-vs-noise regime is α = K/N. The literature predicts a sharp transition at α_c ≈ 0.138 (for random ±1 patterns, finite-noise retrieval). Above that, retrieval collapses into a *spin-glass phase* with exponentially many spurious attractors — the same "mixture" regime modern (continuous) Hopfield networks escape by softmax temperature. This gives a *first-principles* capacity bound for the BSC bundle and predicts a phase transition that should be visible in our pool, not a soft falloff.

2. **The reciprocal-lattice / Fourier-dual structure already exists in HDC — it's called FHRR.** Bloch's theorem and the convolution theorem say: on a structure with translational symmetry, convolution in real space = pointwise multiplication in reciprocal space. Plate's Holographic Reduced Representation (HRR) bundles via addition and binds via *circular convolution* — and the Fourier-variant (FHRR) replaces circular convolution with element-wise complex multiplication on unit-modulus vectors. Our BSC binding (element-wise product on ±1) is *already in the reciprocal-lattice picture*: it's the FHRR restricted to {+1,-1} ⊂ S¹. The cost of "binding-as-multiplication" we already pay; the part we are *not* exploiting is that bundling (sum) is the dual of *convolution* — i.e., the BSC bundle is the reciprocal-space image of a HRR-style real-space convolution of cleanup-memory items. That observation makes the FFT-cleanup trick (Kanerva-style cleanup over a 4096-dim FFT) the most concretely transferable item.

3. **Topological defects give us a *naming scheme* for substrate edits, not a new operation.** Mermin (1979) classifies defects in an order-parameter manifold M by homotopy: point defects ↔ π_n(M), line defects ↔ π_{n-1}(M), etc. For BSC the order-parameter manifold of a single site is the discrete pair {+1,-1} = S⁰, whose homotopy is trivial — but the *order parameter of a bundle* (its sign overlap with each stored atom) lives on a (K-1)-simplex with non-trivial connectivity. This means substrate edits decompose naturally into a finite set of invariant classes (substitution, vacancy = bit drop, interstitial = bit flip into a new direction, dislocation = phase-shifted permutation of a stored atom). The math doesn't give us a new edit primitive; it gives us a *complete and disjoint taxonomy* for an audit log.

**Single most transferable insight (250-word version at end).**

---

## 1. Spin glass theory as substrate math

### The literal mapping

A BSC atom a ∈ {+1,-1}^N is a configuration of N Ising spins. Bundling K atoms a_1, ..., a_K by sign(Σ a_k) is precisely the *zero-temperature majority configuration* of a system whose local field at site i is h_i = Σ_k a_k[i]. The bundle vector b = sign(h) is the ground state of the Hamiltonian H(s) = -Σ_i s_i h_i — i.e., the trivial paramagnet given the field h. So far this is uninteresting, but: when we *retrieve* by computing sims = atoms @ q / N and pick argmax, we are computing 1-step Glauber dynamics on a Hopfield network whose coupling matrix is J_ij = (1/N) Σ_k a_k[i] a_k[j] applied to the probe q. The retrieval similarity to atom a_k is exactly the magnetization m_k = (1/N) Σ_i a_k[i] q[i], i.e. the **overlap order parameter** in spin-glass language.

### Capacity prediction (AGS / Hopfield)

The classical result (Amit-Gutfreund-Sompolinsky 1985; Hopfield 1982) is that for an N-site Hopfield network storing K random ±1 patterns, retrieval is reliable only for α = K/N below α_c ≈ 0.138. Above α_c, all magnetizations collapse and the system enters a spin-glass phase with exponentially many non-pattern minima. For our N = 4096 substrate this predicts a sharp falloff of cued-recall accuracy at K* ≈ 565 stored atoms in a single bundle. This is a *checkable, falsifiable, first-principles* number — and if our pool experiments deviate from it we learn something specific (e.g., our atoms are not i.i.d., our query is not at the right Hamming distance, or our readout temperature is implicit and nonzero).

### Replica symmetric vs. RSB phase

For the SK model with Gaussian couplings, the replica-symmetric (RS) ansatz is unstable below T_AT (the de Almeida-Thouless line); the true solution requires Parisi's full RSB. For the Hopfield model (Amit-Gutfreund-Sompolinsky), three phases coexist:

- **Retrieval (R)**: stored patterns are stable minima with O(1) overlap.
- **Spin-glass (SG)**: only spurious minima with vanishing overlap; α > α_c ≈ 0.138.
- **Paramagnetic (P)**: thermal noise dominates, m = 0.

The RS/RSB boundary maps to a property of our bundle: if RS holds, all retrieval errors are well-described by a *single* overlap variable (Hamming distance to nearest atom). If RSB holds, errors live in a hierarchy of meta-stable regions whose overlap distribution is *non-trivial* (multi-peaked Parisi distribution P(q)).

### What to compute

For each pool, measure:
- **Edwards-Anderson order parameter** q_EA = (1/N) Σ_i ⟨s_i⟩² over Monte Carlo of substrate "shake" perturbations. q_EA > 0 with vanishing magnetization = SG phase.
- **Parisi overlap distribution** P(q) — sample two independent retrievals of the same probe, compute their overlap, histogram. RS predicts a δ-function; RSB predicts a continuous distribution.

This is essentially free to compute on existing pool snapshots.

---

## 2. Crystallographic groups for hierarchical composition

The 230 space groups in 3D (and 17 wallpaper groups in 2D) classify all ways a discrete translational lattice can combine with point-group symmetries (rotations, reflections, glides, screws). Each space group provides a structured *finite group* G whose irreducible representations partition the lattice's function space into orthogonal sectors (Tinkham 1964).

### Analog for substrate

If we want a substrate with *structured* compositional binding — beyond "random atoms + element-wise product" — a crystallographic group gives a built-in hierarchy. Concretely: assign each substrate atom an index in a discrete translation orbit, and bind a "role" by applying a group element. The role bindings then carry the group's irreducible-representation structure for free, so a bundle automatically decomposes (Fourier-on-the-group) into orthogonal symmetry sectors.

### Downside

The honest assessment: this only buys us something if there's a *natural* group acting on our data. Random text tokens don't have a 17-wallpaper-group structure. Visual data sometimes does (translations, 90° rotations of patches). For our two-bets project the realistic application is for *positional* role bindings in sequences — and there the relevant group is just Z_N (cyclic, abelian), whose irreducible representations are precisely the Fourier basis, so we're back at FHRR.

**Verdict: pretty math, but the only useful crystallographic group for sequences IS the one that gives the FFT (item 3). Skip 230 space groups; chase the FFT.**

---

## 3. Reciprocal lattice / Fourier-dual structure (the most actionable item)

### The bridge

Bloch's theorem says eigenstates of a translation-invariant Hamiltonian factorize as ψ_k(r) = e^{ik·r} u_k(r) with u periodic. Equivalently: convolution in real space = pointwise multiplication in reciprocal (Fourier) space. The convolution theorem is the *same statement* without the periodic restriction.

Plate's HRR (1995) used circular convolution as the binding operation precisely because it inherits the convolution theorem: HRR binding has O(N log N) FFT implementation, and the *Fourier* variant (FHRR) uses element-wise complex multiplication directly on unit-modulus vectors — turning binding into O(N).

### What this means for BSC

Our BSC binding (element-wise ±1 product) is *already* element-wise multiplication in real space. The dual question is: what is the *real-space convolution operation* whose Fourier transform is our element-wise product? Answer: it's the operation that, if we represented atoms as FFT(atom), would map to bundling.

This suggests two concrete primitives we don't currently have:

(a) **FFT-cleanup memory.** Store each atom's FFT once. Given a noisy probe q, compute Q = FFT(q), then sims = real(Q† · A_FFT) where A_FFT is the matrix of stored FFTs. The result is mathematically identical to atoms @ q (by Parseval) but enables O(N log N) batched cleanup, sub-linear nearest-neighbour search via reciprocal-lattice indexing, and a natural notion of *bandlimited cleanup* (truncate high frequencies = denoising).

(b) **Reciprocal-bundle.** Define a *dual bundle* b̃ = FFT(b). In reciprocal space, the bundle is a *sum* of phases; per the convolution theorem, sign-thresholding the inverse transform of a *product* of stored FFTs yields a substrate where *retrieval becomes convolution-with-the-probe*. This is exactly the HRR cleanup memory: real-space binding by convolution, real-space cleanup via FFT.

### The big bet's leverage

For the big-bet Hebbian VSA-LM: if positional roles are encoded as *phase ramps* (unit-modulus vectors with linearly-increasing phase across positions), then **positional binding becomes a frequency shift in the FFT domain**. This is Bloch's theorem doing exactly what it does for crystals: making translation a pointwise phase. The big-bet consequence: a Hebbian update rule that operates in FFT-space treats positional shifts as ordinary multiplications, removing the need for a separate "position embedding" pipeline.

**Verdict: this is the single most concretely transferable insight.** It's also already half-built in the VSA literature (FHRR) — what we add is using it as the bridge between the BSC pool and a HRR-style cleanup memory.

---

## 4. Topological defects as audit primitives

### The Mermin classification

For an ordered medium with order-parameter manifold M, defects are classified by homotopy:
- point defects in d=3: π_2(M)
- line defects in d=3: π_1(M)
- planar defects: π_0(M)

A defect's "topological charge" is an element of the relevant homotopy group, and it is *invariant under local deformation* — only global (large) operations can remove it. This is the math that makes vortices in superfluid He robust and gives quantized magnetic flux in superconductors.

### Mapping to substrate edits

Our edits live in atom-space, not in 3D physical space, so we need to translate. For the BSC substrate the natural M is the order-parameter simplex of cued-overlap to stored atoms (a (K-1)-dimensional simplex). A substrate edit is any change to the pool that moves a probe's image in this simplex.

| Materials defect | Substrate analog | Order-param signature |
|---|---|---|
| Substitutional | Replace atom a_k with a new ±1 vector | Single column swap in atom matrix; overlap vector loses one peak, gains another |
| Vacancy | Drop atom a_k entirely | Overlap simplex dimension drops by 1 |
| Interstitial | Add new atom while keeping all existing | Simplex dimension grows; coverage redistributes |
| Edge dislocation | Insert one *extra position* in a positional roll-encoding | Phase-ramp discontinuity in FFT-domain |
| Screw dislocation | Cyclic shift applied to half the pool | π_1 winding number = shift magnitude |
| Stacking fault | Reorder a sub-bundle's internal sum order | None in BSC (commutative); becomes visible in MAP/binding-order-sensitive variants |
| Grain boundary | Two pool partitions with different role-keys | Cross-partition queries return mixture states |

### What's earned

We do NOT get a new operation. We DO get:
- a *complete and disjoint* taxonomy of edit classes (no edit is two of these at once unless it's a *composite*);
- topologically-invariant edit IDs (e.g., screw shift k_shift is invariant under post-shift permutations);
- a principled way to predict which edits *cannot* be locally undone (those carrying non-trivial homotopy charge);
- a target-of-opportunity for audit telemetry: each edit reports its defect class + charge.

### Honest negative

For BSC the order-parameter manifold of a single site is S⁰ (two points) with trivial higher homotopy — so the entire defect math degenerates unless we group sites into structured roles. For FHRR (unit-modulus per site) M = S¹ per site, and we get π_1(S¹) = Z winding numbers for free. **The defect math is interesting for FHRR; it's largely trivial for plain BSC.**

---

## 5. Quasicrystals and aperiodic order

Penrose tilings (1974) and Fibonacci sequences (1D) are aperiodic — no translational symmetry — yet possess *Bragg-sharp* diffraction patterns with forbidden symmetries (5-fold, 8-fold, 10-fold). The math: they are projections of higher-dimensional periodic lattices through an irrational "cut-and-project" window.

### Substrate application

(a) **Quasi-random atoms for collision-aware codebooks.** Instead of i.i.d. ±1 atoms, sample atoms via a Fibonacci low-discrepancy sequence on the hypercube. Predicted gain: lower variance of pairwise overlaps for the same number of atoms = sharper inner-product separation. This is the analog of *Quasi-Monte Carlo* — well-known to beat MC for integration; the analog for inner-product estimation is not commonly used in HDC.

(b) **Aperiodic role-keys for positional encoding.** Positional roles in sequences are typically obtained by repeated permutation (cyclic shift). A Fibonacci-like aperiodic permutation schedule has long-range *non-repeating* structure, mitigating the "wraparound collision" that cyclic role-keys suffer at sequence length = N.

(c) **5-fold forbidden symmetry as a non-collision guarantee.** Crystals can't have 5-fold rotational symmetry but quasicrystals can. The substrate analog: there are bundle configurations that are *guaranteed non-aliasing* under any 5-fold-symmetric role-key set. This is genuinely novel territory but speculative.

### Verdict

Item (a) is testable in one afternoon: replace random ±1 atoms with a Hadamard-or-Fibonacci-structured codebook and measure inner-product variance. Probable speedup is modest (factor of 2–3 in capacity at same noise). Item (c) is the "exciting longshot" — see §11.

---

## 6. Phonons and collective modes

In a harmonic crystal, the low-energy excitations are phonons — orthonormal eigenmodes of the dynamical matrix obtained by Fourier-transforming on the lattice. Each mode carries momentum k and frequency ω(k); the long-wavelength acoustic modes are gapless.

### Substrate analog

A small perturbation to a bundle b → b + ε δ that does NOT change retrieval is a *phonon-like mode* of the substrate. The set of such perturbations forms a vector space — explicitly, the kernel of the readout-overlap Jacobian. For BSC the readout is sign(atoms @ b / N), so the kernel is the set of δ whose sign-overlap with every atom is exactly preserved.

**Practical use:** the dimensionality of this kernel = *substrate redundancy* = noise margin. A bundle with K atoms in N dimensions has approximately N - K dimensions of "phonon space" — perturbations that are invisible to readout. This gives a quantitative bound on robustness: a perturbation of magnitude up to √(N-K) (in L2) can be absorbed without retrieval error.

**Equivalent existing thing:** this is just the kernel of a linear map. Calling it "phonons" buys us only the language of *modes* — useful for thinking about which dimensions of perturbation are absorbable vs. catastrophic.

### Mode hierarchy

In real crystals, low-energy (acoustic) modes are robust collective oscillations; high-energy (optical) modes are localized. For the substrate, this would correspond to *spectral* decomposition of perturbations: low-frequency components (in the FFT sense) are absorbed by the bundle's redundancy; high-frequency components localize on single atoms. This predicts a *frequency-band noise-injection test*: add ε δ_k where δ_k is a single-frequency perturbation, measure retrieval degradation. Predict: degradation increases with k (frequency).

---

## 7. Tight-binding models

Slater-Koster (1954) tight-binding gives electronic structure of a lattice by writing the Hamiltonian as on-site energies + hopping integrals between neighbouring orbitals. For a translationally-invariant lattice the Hamiltonian is diagonalized exactly by Fourier transform on the lattice — yielding band structure.

### Substrate analog

Each substrate site (dimension i ∈ 1..N) carries an "on-site energy" = its current ±1 value; "hopping" = correlation between sites induced by the atom ensemble (atoms[k,i] atoms[k,j] averaged over k). The *band structure* of the substrate is the spectrum of the empirical correlation matrix.

**Useful prediction:** for random ±1 atoms in the AGS regime, the correlation matrix is approximately Wishart with known spectrum (Marchenko-Pastur). Deviations from this spectrum in our pool indicate non-random structure — either useful (e.g., the pool has learned something) or pathological (e.g., a redundant subspace).

**Concretely actionable:** plot Marchenko-Pastur expected eigenvalue density vs. observed; outlier eigenvalues identify the "learned" sub-pools, which can be extracted as principal components for hierarchical retrieval.

---

## 8. Spin glass dynamics for retrieval (Glauber, iterated retrieval)

Our current readout is one step: sims = atoms @ q / N → softmax. A Hopfield network instead *iterates*: given a probe q, compute h = J q, then q' = sign(h); repeat until convergence. This is zero-temperature Glauber dynamics. The energy E(s) = -½ s^T J s decreases monotonically; convergence is to a local minimum.

### Iterated retrieval prediction

For α < α_c, iterating brings the probe to the nearest stored atom even when single-step retrieval is ambiguous (small initial overlap). For α > α_c, iteration falls into a spurious spin-glass minimum.

This predicts a concrete experiment: in our pool, iterate the retrieval map until convergence and measure (a) success rate, (b) number of iterations to converge, (c) probability of falling into a non-pattern attractor. Predicted curves: (a) increases with iterations below α_c, (b) plateaus at O(log N), (c) is zero below α_c, jumps to ~1 above α_c.

### Connection to Modern Hopfield Networks (Ramsauer-Hochreiter 2020)

The modern Hopfield network with continuous patterns and *softmax* readout has exponential capacity (it stores ~exp(N) patterns reliably) and converges in *one* step. The update rule is mathematically transformer attention: q' = X^T softmax(β X q). For our substrate, this means: **if we replace the sign-readout with a softmax at finite temperature β, capacity goes from 0.138 N to exp(c β N) for some c > 0.** The catch: stored patterns must remain in the continuous regime for the analytic capacity — once we threshold back to ±1 (BSC), we lose the exponential scaling.

**Implication:** keep the bundle continuous (Σ atoms, no sign) for retrieval; only sign-threshold for storage/transmission. The "soft" representation has dramatically larger capacity.

---

## 9. Edwards-Anderson order parameter, ultrametricity, RSB hierarchy

Parisi (1979, 1980) showed that the true solution of the SK model requires a hierarchical (ultrametric) replica symmetry breaking ansatz. The order-parameter function q(x), 0 ≤ x ≤ 1, is non-trivial: it encodes a *hierarchy* of overlaps between Gibbs states. Two states with overlap q(x) at level x have a most-recent-common-ancestor at "depth" x in a tree of states.

### Substrate implication

If our pool, viewed as a Hopfield network at α just below α_c, exhibits RSB, then **memories naturally cluster ultrametrically**: a given probe has not just one "nearest atom" but a *tree* of progressively-closer atoms, with the tree structure being an emergent property of the pool ensemble.

This is a *free hierarchical index*. We don't construct it; we *measure* it via the overlap distribution. Operationally:

1. Sample many probe-pairs (q, q') from a probe distribution.
2. Compute their respective retrievals and their post-retrieval overlap.
3. Histogram → P(q). Multi-peaked P(q) = ultrametric tree exists.
4. Tree extraction: hierarchical clustering on the overlap matrix gives the ultrametric tree.

**Practical value:** for a pool of K atoms, ultrametric clustering converts O(K) retrieval comparisons into O(log K) tree-walks. *If* the substrate is in the RSB phase.

### Honest gotcha

Plain random BSC atoms in the *retrieval phase* (α < α_c) are in RS, not RSB — the substrate is well-described by a single overlap parameter and there's no useful tree. RSB structure appears only above α_c or with structured (non-random) atoms. For our pool to benefit from ultrametricity, we'd need to *intentionally over-load* it or use atoms with correlations. This is a deliberate design choice, not a free lunch.

---

## 10. Material defects → memory edit operations (full table)

Crystals undergo a known set of structural changes; each has a topological-defect signature, a measurable cost, and known repair mechanisms. Mapping the table cleanly:

| Defect class | Topology | Substrate edit | Cost (Hamming) | Repair |
|---|---|---|---|---|
| Substitutional impurity | π_0 (discrete swap) | Replace atom a_k | O(N/2) per replaced atom on average | Re-insert original; idempotent |
| Vacancy | π_0 (atom absent) | Drop atom a_k | 0 on bundle if atom unused; full magnitude if used | Re-add atom from cleanup memory |
| Interstitial | π_0 (extra atom) | Insert atom a_{K+1} | O(√N) noise to existing readouts | Drop atom (vacancy) |
| Anti-site | π_0 (swap two atoms) | Permute a_k, a_l | 0 (atoms are unordered in BSC) | Trivial in BSC |
| Edge dislocation | π_1 (line defect) | Insert a position in role-encoding | Phase-ramp discontinuity in FFT | Realign role-key length |
| Screw dislocation | π_1 (line defect with winding) | Cyclic shift on a subset | Z-valued winding number | Inverse shift |
| Stacking fault | π_0 (planar) | Reorder sum within a sub-bundle | 0 in BSC (commutative) | Trivial |
| Twin boundary | π_0 (planar mirror) | Negate a sub-bundle | Equivalent to swapping atom polarity | Negate again |
| Grain boundary | π_0 (planar) | Two pool partitions | Cross-overlap = chance level | Map roles between pools |
| Frenkel pair | π_0 (paired vac + int) | Move atom from one slot to another | Cost = move distance | Reverse move |

### Repair as audit

The materials-science framing is most useful here as *what kind of repair*. For each edit class we have a canonical repair primitive (column 5). The substrate audit log can be classified into these classes and repair recipes attached. This is mostly a *taxonomy contribution*, not a new mechanism.

---

## 11. Minimal viable bridge experiments

Five concrete experiments, ordered by yield-to-effort:

### E1. FFT cleanup memory (highest yield)

**Why:** Item §3's transferable insight. Direct test of "reciprocal substrate."
**Setup:** Store FFT(atom) for each atom; retrieve via Q = FFT(q); sims = real(conj(Q) @ A_FFT).T / N.
**Predict:** Identical sims to current substrate (Parseval); enables O(N log N) batched cleanup, bandlimited denoising, sub-linear ANN search via reciprocal-lattice indexing.
**Falsifier:** sims diverge from baseline by more than floating-point error.
**Effort:** half-day.

### E2. Iterated Glauber retrieval

**Why:** Item §8 — test whether iteration helps in our retrieval regime.
**Setup:** For each probe q, iterate q ← sign(atoms.T @ atoms @ q) until fixed point or max 10 iters.
**Predict:** below α_c, accuracy increases with iteration; above α_c, accuracy collapses.
**Falsifier:** flat or decreasing accuracy curves at all loads.
**Effort:** half-day.

### E3. Edwards-Anderson / Parisi overlap measurement

**Why:** Items §1, §9 — phase diagnosis for our pool.
**Setup:** Sample many probe pairs; compute retrieval-pair overlap; histogram P(q).
**Predict:** RS pool (α small): single-peaked δ-like P(q). RSB pool (α near α_c or structured atoms): multi-peaked.
**Falsifier:** multi-peaked P(q) at very small α, or single-peaked at very large α — would invalidate the SK/Hopfield mapping.
**Effort:** half-day.

### E4. Quasi-random (Fibonacci/Hadamard) atom codebook

**Why:** Item §5(a). Lower-variance overlaps from low-discrepancy atoms.
**Setup:** Replace random ±1 atoms with Hadamard rows or a Fibonacci-low-discrepancy ±1 sequence; measure pairwise overlap variance and bundle capacity at fixed error.
**Predict:** Variance ↓ ~2–3×; effective capacity ↑ ~2×.
**Falsifier:** No measurable improvement (would suggest BSC randomness already saturates the inner-product separation).
**Effort:** one day.

### E5. Topological-defect-classified edit log

**Why:** Item §4. Audit taxonomy.
**Setup:** Wrap edit API to emit defect-class + topological-charge per edit; query log to ensure every observed edit fits exactly one class.
**Predict:** every edit fits; if not, we've discovered a *new* edit class — itself a finding.
**Falsifier:** edits that don't fit the taxonomy.
**Effort:** one day, mostly plumbing.

---

## 12. The big insight — emergent properties

Materials science routinely discovers *emergent* phenomena: topological insulators (Kane-Mele 2005) where the bulk is insulating but edges conduct; Majorana fermions at vortex cores; fractional quantum Hall states with anyonic statistics. The common pattern: **local rules + global topology = robustly-protected non-local properties**.

### What's the substrate analog?

A genuine substrate-analog of an emergent property would be: a quantity computed from the substrate that is (a) *not* directly stored, (b) *robust* to local perturbations, (c) *visible* to a measurement that doesn't know the storage protocol. Candidates:

1. **Edge-state retrieval.** If we arrange atoms with a sublattice structure (e.g., bipartite — atoms drawn from two orthogonal sub-codebooks A and B), then a "boundary" between A-bundle and B-bundle could host *edge atoms* that are not in either sub-pool but are retrievable. This would be analogous to topological-insulator edge modes — local rules on each side, but emergent retrievable states only on the boundary.

2. **Quantized retrieval invariants.** Construct a *winding-number* observable: for a probe encoded as a phase ramp around a cyclic role-key, the retrieved overlap pattern can carry an integer winding number (analogous to a Chern number). This is exactly invariant under local atom edits; it gives a *topologically protected memory*.

3. **Anyonic-like binding statistics.** Element-wise product is commutative (boson-like); but on a *braided* role-key structure (where role-keys are FHRR phase vectors that pick up phases when permuted), binding becomes order-dependent in a controlled way. This is the structure that yields *non-abelian* defect fusion (Mermin 1979's biaxial nematic). A substrate where role-binding is non-abelian would store *ordered tuples* without explicit position encoding.

4. **Bulk-edge correspondence for substrate ensembles.** If we have a *pool of pools*, the boundary between two pool-clusters can host atoms that aren't in either pool but emerge from the boundary's topology. This is genuinely speculative but is the substrate analog of bulk-boundary correspondence — and it would give us a principled way to discover new atoms by *examining boundaries between existing pools*.

### Honest assessment

These are the "exciting longshots". None is at a stage where it's worth building today. They are worth tracking because (a) they share substrate structure (high-dimensional bipolar + ensemble), and (b) the materials-science community has invested decades of theory effort into proving things are *robust to local perturbation* — which is exactly the property we want of substrate memories.

The biggest of these: **quantized retrieval invariants** (item 2). If realized, it gives us *integer-valued memory labels* that are immune to bit-flip noise — a categorically different kind of memory than the floating-point-fuzzy substrate we have today. This is the exciting longshot.

---

## 13. Sources

- Sherrington & Kirkpatrick 1975, "Solvable Model of a Spin-Glass", Phys. Rev. Lett. 35, 1792.
- Edwards & Anderson 1975, "Theory of spin glasses", J. Phys. F 5, 965.
- Parisi 1979, "Infinite Number of Order Parameters for Spin-Glasses", Phys. Rev. Lett. 43, 1754.
- Parisi 1980, "A sequence of approximated solutions to the SK model", J. Phys. A 13, L115.
- Mézard, Parisi & Virasoro 1987, *Spin Glass Theory and Beyond*, World Scientific.
- Hopfield 1982, "Neural networks and physical systems with emergent collective computational abilities", PNAS 79, 2554.
- Amit, Gutfreund & Sompolinsky 1985, "Spin-glass models of neural networks", Phys. Rev. A 32, 1007; and 1987, "Statistical Mechanics of Neural Networks Near Saturation", Ann. Phys. 173, 30.
- Ramsauer et al. 2020, "Hopfield Networks is All You Need", arXiv:2008.02217.
- Mermin 1979, "The topological theory of defects in ordered media", Rev. Mod. Phys. 51, 591.
- Kane & Mele 2005, "Quantum Spin Hall Effect in Graphene" / "Z2 Topological Order and the Quantum Spin Hall Effect", arXiv:cond-mat/0411737 and arXiv:cond-mat/0506581.
- Bloch 1929, "Über die Quantenmechanik der Elektronen in Kristallgittern", Z. Phys. 52, 555.
- Slater & Koster 1954, "Simplified LCAO Method for the Periodic Potential Problem", Phys. Rev. 94, 1498.
- Penrose 1974, "The role of aesthetics in pure and applied mathematical research", Bull. Inst. Math. Appl. 10, 266.
- Shechtman et al. 1984, "Metallic Phase with Long-Range Orientational Order and No Translational Symmetry", Phys. Rev. Lett. 53, 1951 (quasicrystal discovery).
- Tinkham 1964, *Group Theory and Quantum Mechanics*, McGraw-Hill.
- Glauber 1963, "Time-Dependent Statistics of the Ising Model", J. Math. Phys. 4, 294.
- Plate 1995, "Holographic Reduced Representations", IEEE Trans. Neural Networks 6, 623.
- Kanerva 2009, "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors", Cognitive Computation 1, 139.
- Aubry & André 1980, "Analyticity breaking and Anderson localization in incommensurate lattices" (1D quasicrystal physics).
- Hartnett et al. 2018, "Replica Symmetry Breaking in Bipartite Spin Glasses and Neural Networks", arXiv:1804.04875.
- Barra et al. 2020, "Replica symmetry breaking in neural networks: a few steps toward rigorous results", arXiv:2006.00256.
- Albanese et al. 2021, "Replica symmetry breaking in dense neural networks", arXiv:2111.12997.
- Marchenko & Pastur 1967, "Distribution of eigenvalues for some sets of random matrices", Math. USSR-Sbornik 1, 457.

---

## Appendix — the 250-word summary

The single most transferable insight from materials science to our BSC/VSA substrate is that **the bundle is a spin glass and the FFT is its reciprocal lattice**. Two consequences fall out: first, the classical Amit-Gutfreund-Sompolinsky result α_c ≈ 0.138 gives a first-principles, falsifiable capacity bound (≈565 atoms in N=4096), with a *sharp* phase transition between retrieval and spin-glass phases — not a soft falloff. Edwards-Anderson order parameter and Parisi overlap distribution are cheap to measure on our existing pool and diagnose which phase we're in. Second, Bloch's theorem and the convolution theorem identify a "reciprocal substrate" — exactly the FHRR variant of HRR — where binding becomes element-wise multiplication of unit-modulus complex vectors and bundling becomes a sum that is dual to convolution. We can implement an FFT-cleanup memory for our current pool with O(N log N) batched retrieval, bandlimited denoising, and a principled way to encode positional roles as Bloch phase ramps. This is the bridge to the big bet: positional shifts become pointwise phase multiplications in FFT-space, removing the need for separate positional embeddings.

The most exciting longshot is **quantized retrieval invariants** — substrate analogs of topological insulator edge modes and Chern numbers. If we structure role-keys with non-trivial winding, the retrieval output carries an integer topological charge immune to local bit-flip noise. This would give *categorically* noise-protected memories: integer-valued labels you can't fuzz with a perturbation. Materials science spent decades proving these things are robust; the math transfers if we encode roles with the right structure.
