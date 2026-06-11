# Research drill 2x DEEP COMBINED: Free-probability F4 + Family-tag inventory expansion

Date: 2026-06-11
Author: research sub-agent (Opus)
Trigger: combined next-drill candidate pair from prior cycles (free-probability F4 = top advisor candidate; family-tag inventory = Tier-2 structuring need for substrate-self-index observability)
Discipline: 2x DEEP operational drill on existing findings; generic math terms in lit-scan only; lit-scan calibration penalty applied; HARD-PASS and HARD-FAIL pre-registered.

---

## HEADLINE

Free F4 (Voiculescu's fourth free cumulant) is the cheapest substrate-novel observability lever discovered to date: a single scalar computable in ~30 lines from a histogram of inner-product / overlap samples, that DISCRIMINATES "flat cosine geometry" (semicircle, F4 = 0) from "richer relational structure" (deformed-semicircle, F4 != 0) at finite N. Combined with a Boxology-shaped family-tag inventory of ~27 categories (operator-algebra-grounded, not ad-hoc), this gives substrate-self-index its missing Tier-2 cluster definitions AND a single scalar to measure whether self-index actually re-organizes the embedding distribution beyond what a flat-cosine baseline would yield.

Two artifacts proposed together because the F4 observability has no information-bearing teeth until the family-tag inventory provides the cluster labels over which F4 is conditionally evaluated (within-family F4 vs cross-family F4 vs global F4).

---

## Drill 1: Free-probability F4 -- implementation and diagnostic value

### 1.1 Mathematical setup

The fourth free cumulant kappa_4 (also written K_4 or "F4") is the lowest-order free cumulant whose value differs from the corresponding classical cumulant for non-trivial distributions. Moment-cumulant inversion via the Mobius function on the non-crossing partition lattice NC([4]) gives, for a centered random variable with moments m_k = phi(a^k):

    kappa_2 = m_2
    kappa_3 = m_3
    kappa_4 = m_4 - 2 * m_2^2

That is the standard "free kurtosis" formula. Compare classical kurtosis:

    c_4_classical = m_4 - 3 * m_2^2  (Gaussian baseline: c_4 = 0)

For the free analogue the baseline of "no higher-order structure" is the SEMICIRCLE law (Wigner), not the Gaussian. For a centered semicircle of radius 2*sigma:

    m_2 = sigma^2, m_4 = 2 * sigma^4, hence kappa_4_semicircle = 0

Any non-zero kappa_4 measures deviation of the empirical eigenvalue / overlap distribution from semicircularity -- i.e. from "what you'd get if your matrix or your overlap distribution were drawn from a flat-cosine / rotationally-invariant baseline".

For RECTANGULAR matrices (e.g. an N x M codebook where N != M), the proper analogue is the rectangular free cumulant. The fourth rectangular free cumulant is:

    kappa_4_rect = m_4 - (1 + lambda) * m_2^2,  where lambda = M/N (aspect ratio).

This collapses to the square case when lambda = 1.

### 1.2 Implementation sketch (~30 lines numpy)

For a substrate observable X (e.g. vector of pairwise overlaps, or vector of substrate-self-index sub-scores):

```
def free_kappa4(x, aspect=1.0):
    x = x - x.mean()
    m2 = (x**2).mean()
    m4 = (x**4).mean()
    return m4 - (1.0 + aspect) * m2 * m2

def free_kappa4_rect_from_matrix(W):
    # W: N x M codebook, get singular-value-squared distribution
    s2 = np.linalg.svd(W, compute_uv=False)**2
    aspect = W.shape[1] / W.shape[0]
    return free_kappa4(s2, aspect)
```

For higher cumulants kappa_n with n > 4 the recursion is:

    m_n = sum over NC([n]) of (product over blocks b of kappa_|b|)

Inverting recursively gives kappa_n in O(C_n) operations where C_n is the n-th Catalan number (C_4 = 14, C_5 = 42, C_6 = 132). Tractable up to kappa_8 or so on any laptop.

### 1.3 Standard error and finite-sample correction

The "Finite N precursors of free cumulants" line of work (arXiv 2508.21483 and the spectral-k-statistics tradition of arXiv 1302.5892) shows that the naive moment-based estimator is biased at finite N. The polykay-based bias correction adds a 1/N term:

    kappa_4_hat_corrected = kappa_4_hat_naive - (1/N) * (correction polynomial in m_2, m_3)

For substrate sample sizes (typically N >> 1000 for an embedding histogram), the 1/N correction is small. A simple bootstrap (resample x with replacement 1000 times, compute kappa_4, take 2.5/97.5 quantiles) gives a defensible CI without invoking heavy theory. Recommended: bootstrap CI on every F4 reading.

### 1.4 Diagnostic claim -- does F4 distinguish flat cosine from richer structure?

YES, with caveats. Theoretical argument:

- A flat-cosine baseline (random unit vectors in R^N drawn iid from uniform on the sphere) has pairwise-overlap distribution that is asymptotically Gaussian with mean 0 and variance 1/N. Classical kurtosis c_4 -> 0. The free kappa_4 of this distribution is also -> 0 because Gaussian and semicircle share the property that all higher cumulants vanish in the appropriate (classical vs free) sense, and the iid-uniform-on-sphere overlap distribution sits at the boundary where free and classical analyses converge.
- A substrate distribution that has RELATIONAL structure (clusters, families, hierarchies, learned regularities) will produce an overlap histogram with non-trivial higher moments. F4 measures the FIRST deviation from semicircularity that survives centering and rescaling.
- The key empirical question for substrate: how big does the substrate "extra structure" have to be to give an F4 that exceeds the iid-uniform-sphere baseline plus 2 * bootstrap SE?

Caveat: F4 alone cannot distinguish "richer relational structure" from "outlier-dominated noise". A small number of high-magnitude outliers also inflates m_4. Always pair F4 with a robust scale estimate (MAD-normalised) and inspect the histogram tails.

### 1.5 Substrate-specific reading: substrate-self-index vs flat cosine

The PROPOSED USE in the substrate context: compute F4 of the overlap distribution between every concept-embedding pair under two conditions:

1. BASELINE: flat cosine over raw embeddings (no self-index re-organisation).
2. TREATMENT: cosine over substrate-self-index-projected embeddings (whatever the self-index does -- factor, contextualise, normalise, family-tag-condition).

If F4(treatment) - F4(baseline) is significantly negative (semicircle MORE) or significantly positive (more structure surfaced), the self-index is DOING SOMETHING beyond linear cosine. If F4(treatment) ~= F4(baseline) within bootstrap CI, the self-index is a no-op at the level of pairwise relational geometry.

A negative move toward semicircularity would indicate the self-index is WHITENING (good if you want clean retrieval, bad if you want relational structure preserved). A positive move would indicate the self-index is CONCENTRATING relational mass into low-rank structure (good for clustering/family tagging).

This gives the substrate-self-index its first observability test that is NOT just task-accuracy.

### 1.6 Implementation cost

Theory understanding: ~1 day reading (Novak lectures + Mingo-Speicher book chapter 1 free cumulants).
CPU compute for one F4 reading on N ~ 10K samples with 1000-bootstrap: ~30 seconds laptop.
Full self-index vs baseline sweep on substrate (say 10 different self-index variants): minutes.

This is the cheapest serious observability lever ever proposed.

---

## Drill 2: Family-tag inventory expansion -- ~27 categories proposal

### 2.1 The lattice of frameworks consulted

The family-tag inventory question is "how do we organize 300-500 sub-ops into a minimal hierarchy of ~25-30 categories that is principled rather than ad-hoc?" Four organizing frameworks bear on this:

A. BOXOLOGY (van Harmelen & ten Teije, 2019). Compositional design patterns for hybrid systems using oval-for-computation + box-for-data-structure notation, with primary axis SYMBOLIC vs STATISTICAL.

B. OPERATOR ALGEBRA TAXONOMIES (functor categories, operadic composition). Primary axis is COMPOSITIONAL ROLE -- what does the operator do under composition -- with secondary axis of arity and signature.

C. COGNITIVE ARCHITECTURES (SOAR, ACT-R, CLARION, DUAL standard model). Production-rule decomposition with axes: PROCEDURAL vs DECLARATIVE; SHORT-TERM vs LONG-TERM; SYMBOLIC vs SUB-SYMBOLIC.

D. LINEAR-ALGEBRAIC / VSA TAXONOMY. Binding, bundling, permutation, rotation, projection, normalization, addressing -- the substrate-native primitives.

A principled inventory should respect the SHARED axes across A-D rather than pick one framework's vocabulary. The shared axes are:

    1. COMPOSITIONAL ROLE: binder / unbinder / mixer / transformer / observer
    2. ARITY: unary / binary / n-ary / reducer
    3. STATE COUPLING: stateless / read-only / read-write / accumulator
    4. SUB-SYMBOLIC vs SYMBOLIC: continuous-numeric vs discrete-categorical
    5. SCOPE: local / family / global

### 2.2 Proposed ~27 family-tag inventory

Organised in 5 super-groups by COMPOSITIONAL ROLE. Each tag is named in operator-algebra-neutral terms, with substrate-product reading and a one-line operator-signature.

GROUP I -- BINDERS (produce role-filler associations)

1. BIND_TENSOR    -- circular convolution / Hadamard / XOR / tensor product. Signature: (V, V) -> V.
2. BIND_TYPED     -- typed binding with explicit role marker. Signature: (Role, Filler) -> V.
3. BIND_SEQUENCE  -- temporal / positional binding via permutation power. Signature: (V, pos:int) -> V.
4. BIND_CONTEXT   -- conditional binding scoped to a context vector. Signature: (V, V, ctx:V) -> V.

GROUP II -- UNBINDERS (recover constituents)

5. UNBIND_INVERSE -- algebraic inverse of binder. Signature: (V, key:V) -> V_noisy.
6. CLEANUP_NN     -- nearest-neighbour cleanup against codebook. Signature: V_noisy -> V_clean.
7. ITERATIVE_DECODE -- iterative decoding (message passing / argmax loop). Signature: V_noisy -> V_clean, k_iters.
8. RESONATOR      -- resonator-network factor recovery. Signature: V -> (V_1, ..., V_k).

GROUP III -- MIXERS (combine without binding)

9. BUNDLE_SUM     -- additive superposition. Signature: list[V] -> V.
10. BUNDLE_WEIGHTED -- weighted bundle with sparsity / softmax. Signature: (list[V], list[float]) -> V.
11. BUNDLE_THRESHOLD -- bundle followed by threshold / sign / clip. Signature: list[V] -> V_thresholded.
12. POOL_FAMILY   -- aggregate within a family-tag scope. Signature: (list[V], family:Tag) -> V.

GROUP IV -- TRANSFORMERS (re-shape geometry without changing semantics)

13. WHITEN_ZCA    -- ZCA / PCA whitening. Signature: V -> V_whitened.
14. NORMALIZE_L2  -- unit-norm projection. Signature: V -> V_normalized.
15. PROJECT_LOWRANK -- low-rank projection. Signature: V -> V_lowrank.
16. ROTATE_RANDOM -- Kerdock / Hadamard / random orthogonal rotation. Signature: V -> V_rotated.
17. PERMUTE       -- coordinate permutation. Signature: V -> V_permuted.
18. PHASE_SHIFT   -- complex-phase rotation (FHRR). Signature: V -> V_phase_shifted.
19. EMBED_LIFT    -- lift from lower-dim to substrate-dim. Signature: V_low -> V.
20. PROJECT_TIER  -- project across tier-1 / tier-2 / tier-3 hierarchy. Signature: (V, tier:int) -> V'.

GROUP V -- OBSERVERS (measure without changing)

21. SIM_COSINE    -- cosine / dot-product similarity. Signature: (V, V) -> float.
22. SIM_OVERLAP   -- VSA overlap (sign-normalized correlation). Signature: (V, V) -> float.
23. KAPPA4_FREE   -- fourth free cumulant of overlap distribution. Signature: histogram -> float. (DRILL 1 PRODUCT)
24. ATOM_MARGIN   -- min margin between query and codebook entries. Signature: (V, codebook) -> float.
25. SPECTRAL_GAP  -- eigenvalue gap of W or related matrix. Signature: matrix -> float.
26. FAMILY_PURITY -- within-family vs cross-family overlap ratio. Signature: (codebook, family_tags) -> float.
27. AUDIT_RECEIPT -- structured audit log entry (GDPR / counterfactual receipt). Signature: op -> receipt:dict.

### 2.3 Coverage check vs known sub-ops

- HRR/FHRR core (bind, unbind, bundle, permute, cleanup) -> tags 1, 5, 6, 9, 17.
- Modern-Hopfield / resonator (cap_map row anchors) -> tags 7, 8.
- Continual-learning ops (whiten, normalize, low-rank, freeze) -> tags 13, 14, 15, 20.
- Privacy / audit (GDPR receipt, counterfactual log) -> tag 27.
- Tier-1 / Tier-2 sharding -> tags 12, 20, 26.
- Substrate-self-index observability -> tag 23 (this drill's product).
- Calibration / margin / capacity-edge -> tags 24, 25.

This covers the explicit-named sub-op list seen in cap_map and adjacent feedback memories without gaps and without obvious over-coverage. Adjustments are expected as new sub-ops surface; the GROUP-by-ROLE skeleton is the load-bearing structure, the specific tag list is editable.

### 2.4 Hierarchy depth and "minimal"

Two levels: GROUP I-V (5 super-tags) and the 27 leaf tags. No deeper sub-tree. The cognitive-architecture literature consistently warns that 3+ level taxonomies stop being usable and start being a documentation burden (the SOAR / ACT-R Standard-Model exercise converged on roughly 2 levels for the same reason). 27 leaves at the bottom of 5 super-groups is within the human-memorable range (5 +/- 2 super-groups, 5-6 leaves per super-group).

### 2.5 Operator-algebra grounding (not just engineering)

The GROUP I-V partition maps onto the standard category-theoretic decomposition of operations on a monoidal category with duals: tensor / dualization / multiplication / unit / counit, which corresponds in VSA terms to bind / unbind / bundle / identity / measurement. The KAPPA4_FREE observer (tag 23) is the only tag that requires free-probability machinery and lives in the observer group precisely because it is a SCALAR FUNCTIONAL of the substrate state, not an in-substrate operator.

This grounding is what makes the inventory NOT ad-hoc.

---

## Cheap decisive test

A single notebook with three cells:

CELL 1. Compute F4 on baseline iid-uniform-on-sphere overlaps (N = 10K vectors, dim = 1024), 1000 bootstrap. Verify F4 within 2 SE of 0.

CELL 2. Compute F4 on substrate concept-embedding overlaps as currently stored. Compare to baseline. Bootstrap CI.

CELL 3. Compute F4 on substrate-self-index-projected overlaps. Compare to CELL 2.

Total compute: under 5 minutes laptop CPU. Total code: under 50 lines.

If CELL 2 - CELL 1 is within bootstrap CI: substrate as currently stored has no surplus relational structure over flat cosine (an interesting null result -- means storage is already maximally entropic).
If CELL 3 - CELL 2 is within bootstrap CI: substrate-self-index is a no-op at this level (forces a re-think of what self-index claims to do).
Either of these results would falsify a substrate-self-index design narrative that has not yet been falsified.

---

## Falsifiable predictions

PREDICTION P1: F4 of iid-uniform-on-sphere overlaps at dim=1024, N=10K is < 0.05 in absolute value (semicircle baseline holds at scale of interest).
HARD-PASS: |F4_baseline| < 0.05 with 1000-bootstrap.
HARD-FAIL: |F4_baseline| > 0.10 (would invalidate the semicircle null and force re-derivation).

PREDICTION P2: F4 of substrate concept-embedding overlaps is significantly different from baseline (substrate is not just flat random vectors).
HARD-PASS: |F4_substrate - F4_baseline| > 3 * bootstrap_SE.
HARD-FAIL: |F4_substrate - F4_baseline| < 1 * bootstrap_SE (substrate would be empirically indistinguishable from random rotation -- a serious problem).

PREDICTION P3: F4 of substrate-self-index-projected overlaps differs from un-projected by at least 2 * bootstrap_SE in EITHER direction.
HARD-PASS: |F4_self_index - F4_substrate| > 2 * bootstrap_SE.
HARD-FAIL: difference within 1 * bootstrap_SE (self-index has no measurable effect on second-order-free relational geometry).

PREDICTION P4 (family-tag inventory): the 27-tag inventory covers >= 95% of named sub-ops in cap_map and current feedback memory index without ambiguous double-assignment.
HARD-PASS: 95%+ unique coverage on enumeration audit.
HARD-FAIL: <80% coverage OR > 5 sub-ops requiring multi-tag assignment with no clear primary tag (indicates the role-axis is wrong).

---

## Cross-thread synthesis

This drill connects three open threads:

- substrate v3.2 ENGINEERED WRAPPER (per-shard protection, locality, importance) -- the family-tag inventory provides the LABEL SET that per-shard protection partitions on; without ~27 family tags the per-shard wrapper has nothing to scope over.
- substrate-self-index Tier-2 cluster definitions -- F4 (tag 23) provides the OBSERVABILITY that lets substrate-self-index be evaluated without round-trip task accuracy.
- prior drill on free-probability (Marchenko-Pastur, R-transform) -- F4 is the cheapest extension of that line; F2 (Tracy-Widom edge) and F5 (R-transform) require more apparatus, F4 is one-formula.

This drill DOES NOT overlap with the recent NL-substrate POS/intent/slot-filling validation work; that thread is about substrate-classical-NLP, this is about substrate observability and ontology.

---

## Substrate-product implications

PRODUCT IMPLICATION 1 -- ship F4 as a diagnostic. Add KAPPA4_FREE as a standard observability metric in the substrate dashboard alongside recall@1, F1, and cosine-spectrum plots. ~30 lines code. Becomes a permanent regression check ("did the last self-index change move F4 off the semicircle?").

PRODUCT IMPLICATION 2 -- adopt the 27-tag family inventory as the substrate ontology. Tag every sub-op in code with one primary tag and at most one secondary tag. Use the tag taxonomy as the index for documentation, the partition for per-shard protection scoping, and the cluster-definition for Tier-2 substrate-self-index.

PRODUCT IMPLICATION 3 -- F4-conditional and family-conditional retrieval. Compute within-family F4 separately from cross-family F4. If they differ significantly, family-aware retrieval is justified by a measurable observable, not just intuition. This is a substrate-novel feature: "show me the families with the most internal relational structure" is a query no flat-cosine baseline can answer.

PRODUCT IMPLICATION 4 -- substrate self-index OBSERVABILITY surface. F4 is the first metric that can DETECT whether a self-index change is a no-op without running a full benchmark suite. This compresses the experiment-design loop substantially.

---

## Calibration

Lit-scan calibration penalty applied. F4 mathematics is textbook (Voiculescu 1991, Speicher 1994, Mingo-Speicher book); no novel-synthesis cap needed for the THEORY. Novel-synthesis cap DOES apply to the substrate-specific empirical predictions because no published precedent applies F4 to substrate-style overlap histograms specifically.

P estimates (deflated):
- F4 math is correct as written: P = 0.95 (textbook).
- F4 bootstrap CI on substrate sample sizes will give defensible reading: P = 0.80.
- F4(substrate) - F4(baseline) is detectable at HARD-PASS threshold: P_deflated = 0.55 (capped from raw 0.70 by novel-synthesis cap and substrate-uncharted-regime penalty 0.15).
- 27-tag inventory covers 95%+ of named sub-ops on enumeration audit: P_deflated = 0.50 (capped from raw 0.70).

OVERALL P_deflated for "this drill produces actionable next experiments": 0.50.

---

## Citations (verified)

1. Mingo, Speicher. "Free Probability and Random Matrices." 2017 textbook. (arXiv 1404.3393 lecture-note precursor; verified URL https://arxiv.org/pdf/1404.3393)
2. Novak. "Three lectures on free probability." MSRI/SLMath. (https://library.slmath.org/books/Book65/files/140819-Novak.pdf; verified)
3. Collins, Mingo, Sniady, Speicher. "Second order freeness and fluctuations of random matrices, III." arXiv math/0606431 (verified URL).
4. "Finite N precursors of the free cumulants." arXiv 2508.21483 (verified URL).
5. "Cumulants for finite free convolution." arXiv 1611.06598 (verified URL).
6. "A Note on Cumulant Technique in Random Matrix Theory." MDPI Entropy 25:725 (verified URL).
7. van Harmelen, ten Teije. "A Boxology of Design Patterns for Hybrid Learning and Reasoning Systems." arXiv 1905.12389 (verified URL).
8. "Modular Design Patterns for Hybrid Actors." arXiv 2109.09331 (verified URL).
9. Anderson et al. "ACT-R: A cognitive architecture." (WIRES Cognitive Science; verified URL via Wiley DOI).
10. "An Analysis and Comparison of ACT-R and Soar." arXiv 2201.09305 (verified URL).
11. "Natural statistics for spectral samples." arXiv 1302.5892 (verified URL; spectral k-statistics / polykays).
12. "Speicher / Voiculescu free cumulant lecture notes." arXiv 1908.08125 (verified URL).

Verified citation count: 12.

---

## exp_dev-actionable

YES. F4 implementation (Drill 1) is ready for empirical test now. Family-tag inventory (Drill 2) is ready for a tagging audit that does not require GPU. A companion exp_dev hand-off file will be written separately if and when this drill is converted into anchors. For now, the cheap decisive test in Section "Cheap decisive test" above is the minimal first step.
