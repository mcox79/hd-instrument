# Wave 14e: Multi-hop compositional reasoning across HDC/VSA bundles

Date: 2026-05-19
Substrate: N=4096 BSC bipolar (atoms in {-1,+1}^4096), bind = element-wise product (equivalent to XOR on bits), bundle = sign(sum).
Goal: given B1 (encoding relation A->B) and B2 (encoding relation B->C), derive a bundle/relation that supports the query "A->?" or "A composed with R1 and R2 yields what?" with > 80% accuracy at 2-hop.

---

## TL;DR (recommended primitive design)

The clean, brain-aligned primitive for multi-hop chaining in BSC is the **triple bundle with self-inverse algebra cancellation**:

1. Encode each fact as a triple-bound atom: `e_i = subj_i * rel_i * obj_i` (single bound vector, not a bundle).
2. Store the fact base as a superposition: `M = sign(sum_i e_i)`.
3. For a 2-hop query `(A, R1) -> ? -> (?, R2) -> ?`, form `q = A * R1`, probe `M` to recover the intermediate object atom `B_hat = clean(M * q)`, then re-probe with `q' = B_hat * R2` to get `C_hat = clean(M * q')`.
4. Chaining works because BSC binding is its own inverse: `(A * R1) * (A * R1 * B) = B`. The cleanup step (item-memory nearest-neighbor) is what truncates noise between hops.

This is **bound triples + cleanup-between-hops**, not bundle-of-bundles. The literature converges here: HRR (Plate 1995 §6), SPA/Spaun (Eliasmith 2012), and the TEM (Whittington 2020) all factor "structural relation" from "sensory content" and apply the relation to a clean content vector each step. Direct bundle * bundle chaining (without cleanup) collapses after roughly **log(N)/log(K)** hops because noise is multiplicative across the chain.

**Predicted hop ceiling** for N=4096, fact-base size F=100, atoms-per-bundle k=3 (subject, relation, object): single-hop SNR ~ sqrt(N/F) ~ 6.4, hop-k cleanup-gated SNR decays as (1 - epsilon)^k where epsilon ~ 0.5*erfc(sqrt(N/(2F))/sqrt(2)). For F=100, single-hop error < 1e-6 -> 5-7 hops feasible; for F=1000, 3-4 hops; for F=10000, 2 hops marginal. Without cleanup, 1 hop is the practical ceiling.

---

## 1. Formal math for compositional binding (HRR / TPR / BSC compared)

Three formalisms support chained inference. They differ in algebra, decoding cost, and capacity.

### 1.1 Smolensky 1990 Tensor Product Representations (TPR)
Binding: `r * f = r tensor f`, an outer product. Composition: `S = sum_i r_i tensor f_i`. Decoding by inner product: `S r_i ~ f_i`.
- **Pro:** exact decoding when role vectors are orthonormal; chains as repeated tensor contractions.
- **Con:** dimensionality **grows multiplicatively per binding** (N^k for k-deep). Not fixed-width. Unusable as a long-term substrate.
- **Chained inference:** S1 = A tensor R1 tensor B, S2 = B tensor R2 tensor C. Contracting along the shared B axis yields A tensor R1 tensor R2 tensor C. Clean but expensive (rank-4 tensors at depth 2; rank-2k at depth k).

### 1.2 Plate 1995 HRR
Binding: circular convolution `a circle-conv b` (FFT(a)*FFT(b), IFFT). Inverse: approximate inverse `a^# = a` reversed (involution under unitary vectors). Composition: superposition (sum) followed by normalization.
- **Pro:** fixed dimension N; compositional structure chunks recursively (§6: a sentence is a vector that can be re-bound). Capacity formula: roughly `K ~ N / (4 ln(M))` bound pairs for M-vocabulary cleanup (Plate ch.7).
- **Con:** decoding is **noisy** -> requires associative cleanup memory. Inverse is approximate.
- **Chained inference:** standard pattern is `S = role_1 \circ filler_1 + role_2 \circ filler_2 + ...`. To traverse a chain, you bind with the role, get a noisy filler, clean it, repeat. Plate explicitly demonstrates this for frame chaining (`mother-of(father-of(x))`) but reports degradation after ~3-4 levels of recursion at N=512.

### 1.3 BSC / MAP (Kanerva 1997; Gayler 1998)
Binding: element-wise product on {-1,+1}^N (equivalent to XOR on {0,1}^N after a mapping). Bundle: `sign(sum)`. **Self-inverse:** `x * x = 1` (vector of ones). Inverse-of-binding equals binding (involutive).
- **Pro:** O(N) operations; hardware-cheap (XOR + popcount); same fixed dimension; self-inverse algebra is the cleanest for chained queries.
- **Con:** the sign() bundling discards magnitude, so the SNR per term drops; binding two bundles produces a bundle of all cross-products (combinatorial blowup before cleanup).
- **Chained inference:** since `x * x = 1`, you get clean cancellation if the same atom appears bound on both sides: `(A*R1*B) * (B*R2*C) = A*R1*R2*C`. This is the key algebraic trick for 2-hop.

### 1.4 Recent extensions worth noting
- **GHRR** (Generalized HRR, arxiv:2405.09689): block-diagonal projection variants that recover Plate's linear capacity scaling that the naive HRR lost in practice. Used in PathHD for KG-reasoning. Relevant if we ever want continuous similarity at scale.
- **MAP-C / MBAT** (Gayler & Levy): map-and-permute variants that combine BSC with a random permutation so binding is non-commutative (`a # b != b # a` after permutation). This matters when relations are directional (`father_of != child_of`). We should plan for permutation-based directionality from the start.
- **Sparse Block Codes** (Hersche 2024, IBM): each factor occupies a dedicated index block; binding is per-block element-wise, factorization is independent per block. Reduces cross-factor noise from O(F^2) to O(F) and lifts the factor-count ceiling from ~3 to ~10+.

### Verdict
For **chained inference under a fixed-width, neuro-plausible substrate**, BSC wins on cost and algebraic cleanliness (self-inverse). HRR is the right reference when you need a continuous similarity metric and a graceful capacity bound. TPR is the right reference when you want exact symbolic decoding and don't care about width. Our substrate (N=4096 BSC bipolar) is committed to BSC; the formal capacity tools we should port from Plate are the **superposition capacity bound** and the **cleanup-error model** (HRR appendix on capacity of superposition memory), which translate to BSC with the obvious substitutions (dot product -> normalized Hamming, Gaussian noise model -> binomial).

Concrete capacity translation (BSC at N, bundle of F bound terms):
- Hamming similarity of M to any constituent term: `mean = 1/sqrt(F)` (for odd F; for even F, the sign() majority is unbiased and similarity is `~sqrt(2/(pi F))`).
- Variance per bit: `~1/N` (independent coin flips).
- Detection margin (per cleanup against one distractor): `sqrt(N/F)` in standard-deviation units. This is the master formula that drives all downstream predictions.

---

## 2. BSC-specific implementation

### 2.1 Encoding facts
Each fact `(s_i, r_i, o_i)` becomes a single bound triple atom:
```
e_i = s_i * r_i * o_i   # element-wise product, in {-1,+1}^N
```
This is **not a bundle** of three things; it is a single bound vector that carries all three identities multiplicatively. Bundling enters only when superposing many facts:
```
M = sign( sum_i e_i )   # in {-1,+1}^N
```
This is the "fact base hypervector". For F facts at N=4096, M faithfully stores roughly N/(4 log F) facts before queries become unreliable.

### 2.2 Single-hop query
"What is A connected to via R1?" Form probe `q = A * R1`. Compute `q * M`. The component corresponding to fact `e_i = A * R1 * B` cancels to `B`; all other facts contribute random sign-vectors. So:
```
B_hat = sign( q * M )    ## a bipolar vector noisy around B
B_recovered = nearest_atom_in_codebook(B_hat)
```
This is the **clean-up** step. Without a codebook, B_hat sits at Hamming-distance roughly `0.5 - 0.5*sqrt(1/(F-1))` from B in the worst case. With the codebook (item memory), nearest-neighbor recovers B exactly when SNR > 1.

### 2.3 Two-hop query
"A through R1 to ? through R2 to ?". Two equivalent paths:

**Path A: chained cleanup (RECOMMENDED).**
```
q1 = A * R1
B_hat = cleanup( q1 * M )
q2 = B_hat * R2
C_hat = cleanup( q2 * M )
```
Cleanup re-snaps the intermediate to a clean codebook atom, removing accumulated noise. Per-hop error compounds *only at the cleanup decision boundary*, not in the vector.

**Path B: composed-relation probe (FASTER, NOISIER).**
Form a composed relation `R12 = R1 * R2`. Probe `M * (A * R12)`. This works **only if** the substrate has stored a derived bundle that explicitly encodes the 2-hop path, OR if you can construct a "composed M" from M itself via `M * M`. The latter gives a sum of all pairwise cross-products of facts, of which the desired `e_AB * e_BC = A*R1*R2*C` is one term — but it is buried in O(F^2) noise terms. Path B is therefore useless beyond F ~ sqrt(N/4 log F), i.e. ~25 facts at N=4096. **Stick with Path A.**

### 2.4 Composing relations directly
The query `R = R1 \circ R2` such that `A * R = C` becomes `R_hat = (A^{-1}) * C = A * C` (BSC inverse is self). Useful when you have observed A->C empirically and want to extract the implicit relation; not a chaining primitive.

### 2.5 Directional relations via permutation
BSC binding is commutative, so `A * R` and `R * A` are the same. For directional edges (`A is_father_of B` is not `B is_father_of A`), introduce a permutation `pi` and define:
```
e_i = subj_i * rel_i * pi(obj_i)
```
Now the probe is `q = A * R1`, recovery is `B_hat = pi^{-1}(q * M)`. This is the same trick used in HRR (circular shift) and in TEM (action operator). It costs nothing — pi is a fixed random permutation on N indices, O(N) to apply, O(N) memory.

### 2.6 What about bundles-of-bundles (i.e. composing M's)?
If we wanted to combine two fact bases M1 and M2 (e.g. one per relation type), the legitimate operation is **superposition**: `M = sign(M1 + M2)` — preserves the per-fact recovery margin in the union if the codebooks are disjoint. The illegitimate operation is **binding**: `M1 * M2` gives a sum of O(F1 * F2) cross-terms with no useful structure unless we are exploiting a specific cancellation (as in §3's joint resonator).

---

## 3. Resonator network for multi-bundle decomposition

Frady-Sommer 2020 (arxiv:1906.11684) defines a resonator for a single bound product `s = a * b * c` over factor codebooks A, B, C. Dynamics:
```
a_hat <- g( A * (A^T (s * (b_hat * c_hat))) )    # ditto for b_hat, c_hat
```
where g is sign() for BSC. It works because each iteration projects the residual onto the codebook and the cross-factor noise self-cancels.

**Extension to two bundles** (this is the novel piece for our wave):
We want to factor a *pair* `(B1, B2)` jointly, where B1 = A*R1*B and B2 = B*R2*C, exploiting that **B is shared**. Construct the joint quantity:
```
J = B1 * B2 = (A * R1 * B) * (B * R2 * C) = A * R1 * R2 * C
```
Now run a 4-factor resonator over codebooks (atoms, relations, relations, atoms) on J. This recovers (A, R1, R2, C) jointly — and the shared B is invisible in J, which is exactly what we want for transitive chaining. **Key insight:** the BSC self-inverse property turns the multi-bundle decomposition into a *single-bundle* problem of higher factor count. No need to extend the resonator dynamics; only the codebook product.

Kent et al. 2020 (sparse VSA) and Hersche et al. 2024 (sparse block-code factorizer) make the resonator scale to higher factor counts by using **block-sparse codes** where each factor lives in its own block — this is directly the right tool when you need to factor 4+ factors per query. Adopt their factorizer when extending beyond 3-factor.

### Cost per resonator hop
- Inner loop: O(F * N) per iteration (F = codebook size, N = dimension), typically 10-50 iterations to converge.
- For N=4096, F=100 atoms, that is ~2-20 MFLOPs per joint factorization. Cheap.

### Failure mode
Resonator fails (does not converge) when the codebook size F per factor exceeds the operational capacity `F_max ~ N / (log F)^2`-ish (Frady-Sommer 2020 §IV). For N=4096 you get F_max ~ a few hundred per factor before convergence becomes unreliable. **This is the hard ceiling, not the noise-accumulation ceiling.**

---

## 4. Graph-as-VSA: cost and failure mode

Treat atoms as graph nodes, relations as edge-type atoms, edges as bound triples `s*r*o`, graph M as the sum. Multi-hop traversal = repeated probe-cleanup. This is exactly the schema PathHD (arxiv:2512.09369) uses for knowledge-graph reasoning with hyperdimensional vectors.

### Cost per hop
| Operation | Cost |
|---|---|
| Form probe `q = atom * rel` | O(N) |
| Bind with M `q * M` | O(N) |
| Cleanup (nearest atom over F-codebook) | O(F * N) |
| **Total per hop** | **O(F * N)** |

For F=100, N=4096: ~400k ops per hop -> ~microseconds. Multi-hop is essentially free until codebook grows.

### Failure modes
1. **Cleanup mis-snap:** at low SNR, cleanup snaps to wrong atom; subsequent hops are then on the wrong manifold. Error is **categorical** not graceful.
2. **Branching factor:** if a node has b outgoing edges of the same relation, the probe returns a *bundle* of b destinations, and cleanup picks one arbitrarily. Requires a different primitive ("expand all branches" rather than "find the one branch"). Spaun handles this with a "controller" gating signal that decides whether to expand or commit.
3. **Spurious self-loops:** any pair of facts that share two atoms creates a phantom edge in M*M. Mitigation: never use Path B; always use chained cleanup.
4. **Noise accumulation without cleanup:** Per-hop SNR decays geometrically. With cleanup, decay halts at the cleanup decision boundary.
5. **Codebook overlap:** if two atoms are accidentally close (`|<a_i, a_j>| > 3/sqrt(N)`), cleanup is biased. For random atoms in N=4096, pairwise overlap ~ 0.015 stdev, so probability of two atoms within margin 0.05 is `~erfc(0.05*sqrt(4096)/sqrt(2)) ~ 0.026`. Across a codebook of 100 atoms, ~130 pairs are at risk; one or two will be the bottleneck. Mitigation: orthogonalize the codebook (Gram-Schmidt on bipolar approximation, or use a coded set).

---

## 5. Predicted hop-count ceiling (math from HRR capacity)

Plate's HRR capacity result (Plate 1995, appendix; generalizing to BSC):
- Single bundle of F bound atoms in dimension N, querying for one constituent, gives Hamming similarity `mu ~ 1/sqrt(F)` between query result and target.
- Probability of correct cleanup against a codebook of C distractors:
  `P_correct ~ 1 - C * Phi(-mu * sqrt(N))`  (Phi is normal CDF)
- For N=4096, F=100, C=100: mu = 0.1, mu*sqrt(N) = 6.4 -> Phi(-6.4) < 1e-10 -> per-hop error < 1e-8.
- Hop-k success probability: `(1 - per_hop_error)^k`. For k=10 hops: still > 0.9999.

For F=1000, mu = 0.032, mu*sqrt(N) = 2.0, Phi(-2.0) = 0.023 -> per-hop error ~ 2.3 (with 100 distractors), **collapses immediately**. At F=300, mu*sqrt(N) = 3.7, Phi(-3.7) ~ 1e-4 -> 4 hops at >99%.

**The dominant scaling is `mu*sqrt(N) = sqrt(N/F)`.** Hop ceiling is set by F (fact-base size relative to N), not by k. *If cleanup succeeds at hop 1, it succeeds at hop k for the same M.* Multi-hop "noise accumulation" is a red herring **iff cleanup is applied at every hop**. Without cleanup, SNR falls as `1/sqrt(F)^k` and ceiling is `k_max ~ log(N) / log(F)`.

### Practical ceilings at N=4096
| F (facts) | with cleanup | without cleanup |
|---|---|---|
| 100 | > 50 hops (limited by cleanup decision boundary) | ~1 hop |
| 300 | ~10 hops | 1 hop |
| 1000 | 2-3 hops | <1 hop reliable |
| 10000 | substrate insufficient at N=4096 | n/a |

**Recommendation:** never operate without cleanup between hops. Treat cleanup as the analog of synaptic re-stabilization in HC — the system *must* re-snap to a discrete attractor each step.

---

## 6. Experiment design (minimal viable test)

### 6.1 Setup
- N = 4096, BSC bipolar.
- Generate F = 100 random atoms as entities A_1..A_100 and R = 20 relation atoms.
- Sample a random directed graph G of 200 edges over (entity, relation, entity). Ensure 50+ 2-hop paths and 20+ 3-hop paths exist by construction.
- Encode M = sign(sum_e e), where each e = subj * rel * obj.
- Cleanup codebook = the 100 entity atoms.

### 6.2 Queries
- **1-hop baseline:** 100 queries `(s, r) -> o?`. Expected accuracy ~ 100%.
- **2-hop test:** 50 queries `(s, r1, r2) -> o?` where ground-truth path s -r1-> x -r2-> o exists in G. Run path A (chained cleanup). Pass criterion: accuracy > 80%.
- **3-hop test:** 20 queries `(s, r1, r2, r3) -> o?`. Pass criterion: > 50% (and > 1% random baseline).
- **Capacity stress:** repeat at F = 200, 500, 1000 entities, 50, 100, 200 relations, edges scaled proportionally. Plot accuracy vs. F to confirm sqrt(N/F) curve.

### 6.3 Confounds to control
- Branching: ensure each (subject, relation) pair has exactly one object in ground-truth set (or test the branching-aware primitive separately).
- Cycles: 2-hop paths that loop back to subject — exclude or test separately (different math).
- Distractor density: 100 cleanup distractors is the published worst case; report at 100, 500, 1000.

### 6.4 Predicted outcomes (pre-registered)
- 1-hop > 99%; if not, substrate is broken.
- 2-hop > 95% at F=100, > 80% at F=300; if not, cleanup is the failure point — instrument the cleanup margin.
- 3-hop > 90% at F=100. The "noise accumulates per hop" hypothesis predicts much lower; if 3-hop is high, that hypothesis is falsified for our substrate and we should publish that result.

### 6.5 Compare against
- Random baseline: 1/100 = 1%.
- Bundle-of-relations (path B): predict < 5% at F=100 due to F^2 noise.
- TPR-equivalent exact symbolic: 100% by construction (sanity oracle).

---

## 7. Brain mapping: mathematical structure of relational memory in HC

Don't ask "is HDC like the brain"; describe what the brain computes and read off the mathematical form.

### 7.1 What HC does (Eichenbaum 2017, Whittington 2020)
- HC stores **relational** structure: edges between entities, not entities themselves. CA1/CA3 place cells remap between environments while preserving the *relational graph*. The same place cell can represent "northwest corner" in two different rooms — it codes the relation, not the absolute location.
- Medial entorhinal cortex (mEC) provides a **structural basis**: grid cells, band cells, object-vector cells. Whittington 2020 formalize mEC as encoding a graph Laplacian / transition operator that is *content-independent*.
- Hippocampus binds mEC structural codes with lateral entorhinal (LEC) sensory codes: `place_cell = bind(structural, sensory)`. This is **literally** a VSA bind operation — Hadamard-like in the TEM model.

### 7.2 The mathematical form
TEM's update rule (Whittington 2020, eqs. 1-3 of their model section):
- Latent structural state `g_t` evolves under an action operator: `g_{t+1} = T(a_t) g_t`. T is a learned linear operator per action a.
- Sensory state `x_t` is bound with structure to give the HC code: `p_t = g_t bind x_t`.
- Episodic memory: `M += p_t outer p_t^T` (Hopfield-like).
- Retrieval: `p_query = (g_query bind x_partial); p_recovered = M p_query / cleanup`.

This is **identical in form** to our BSC chained-query design:
| BSC chained query | TEM operation |
|---|---|
| q1 = A * R1 | p_query = g_A bind x_R1 |
| q1 * M | M p_query |
| cleanup -> B | attractor dynamics in CA3 |
| q2 = B * R2 -> cleanup -> C | next step of mEC-driven action transition |

### 7.3 What this buys us
- The *structural-content factorization* (mEC structure x LEC content) gives a principled answer to "why bind at all?" It is **not** so atoms compose; it is so the same relation can apply to many contents. Our R1, R2 atoms are the analog of mEC's transition operators.
- The *attractor cleanup* in CA3 is the biological cleanup-between-hops. No-cleanup variants are not just engineering oversights — they are biologically implausible.
- The *Hopfield-style M* is the substrate-level analog of our bundle M = sign(sum e_i). The associative cleanup is a separate Hopfield network operating on the codebook, also biologically plausible (CA3 recurrence).

### 7.4 What it predicts for our substrate
- 2-hop with cleanup should work as well as 1-hop, up to the codebook-capacity ceiling. (Matches HRR/BSC math.)
- The "neuromodulator" role is plausibly **gating cleanup vs. continue-noisy** — a global signal that says "snap to the attractor now" vs. "hold the superposition". This is testable: in our substrate, expose cleanup as a gated operation and study which task structures benefit from delayed cleanup.

---

## Sources

### Primary VSA / HDC
- Plate, T.A. (1995). Holographic Reduced Representations. IEEE TNN 6(3). https://www.semanticscholar.org/paper/Holographic-reduced-representations-Plate/0c4d193b4e8520dbc583cc7ee59c8417869f67ce — chunking ch.6, capacity appendix.
- Plate, T.A. (2003). Holographic Reduced Representation: Distributed Representation for Cognitive Structures. CSLI. https://press.uchicago.edu/ucp/books/book/distributed/H/bo3643252.html
- Kanerva, P. (1997). Fully Distributed Representation. http://www.cap-lore.com/RWC97-kanerva.pdf — BSC, XOR binding.
- Kanerva, P. (2009). Hyperdimensional computing. https://www.diva-portal.org/smash/get/diva2:1014251/FULLTEXT01.pdf — BSC analogical mapping.
- Smolensky, P. (1990). Tensor Product Representations. Artificial Intelligence 46.
- Gayler, R. (1998). Multiplicative Binding, Representation Operators & Analogy.
- Frady, E.P., Kent, S., Olshausen, B., Sommer, F.T. (2020). Resonator Networks 1 & 2. Neural Computation 32(12). arxiv:1906.11684. https://arxiv.org/pdf/1906.11684 — single-bundle factorization.
- Kent, S. et al. (2020). Resonator networks for sparse VSAs. https://rctn.org/bruno/papers/resonator1.pdf
- Hersche, M. et al. (2024). Factorizers for distributed sparse block codes. arxiv:2303.13957. https://arxiv.org/abs/2303.13957 — sparse block factorizer for higher factor count.

### Recent graph / multi-hop in VSA
- PathHD: Encoder-Free Knowledge-Graph Reasoning with HD Path Retrieval (2025). https://arxiv.org/html/2512.09369 — knowledge-graph multi-hop in HDC.
- VS-Graph (2025). https://arxiv.org/abs/2512.03394 — multi-hop neighborhood aggregation in HDC.

### Brain / cognitive
- Eichenbaum, H. (2017). The role of the hippocampus in navigation is memory. J Neurophysiol. https://pmc.ncbi.nlm.nih.gov/articles/PMC5384971/
- Eichenbaum, H. (2017). Memory, Relational Representations, and the Long Reach of the Hippocampus.
- Whittington, J.C.R. et al. (2020). The Tolman-Eichenbaum Machine. Cell. https://www.cell.com/cell/fulltext/S0092-8674(20)31388-X
- Eliasmith, C. et al. (2012). Spaun: A Large-Scale Model of the Functioning Brain. Science 338. https://en.wikipedia.org/wiki/Spaun_(Semantic_Pointer_Architecture_Unified_Network)

---

## Step-back assessment

Before committing, list what could rescue this approach if 2-hop fails the > 80% bar:

1. **Increase N** to 8192 or 16384 — doubles SNR per hop, cheap.
2. **Sparse block codes** (Hersche 2024) — per-factor blocks reduce cross-factor noise; especially helpful at F > 300.
3. **Multiple Ms** (partition the fact base by relation type) — F per M drops, capacity rises; explicit relation-typed memory.
4. **Cleanup over learned embeddings** instead of random atoms — Hebbian/SDM-style codebook with sub-linear distractor effects.
5. **Holographic chunking** (Plate ch.6) — collapse a 3-hop chain into a single bound chunk after first traversal; reduces future hop count.

If the substrate fails all five, the bet shifts: BSC at N=4096 cannot support graph reasoning over F > 100 entities, and we either move to HRR or go to N > 8192. **That is a real and decidable outcome of the wave14e experiment, not a hedge.**
