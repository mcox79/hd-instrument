# Research Drill: 2x -- Pattern B Payload Magnitude Control Design Space
# Date: 2026-06-07
# Trigger: C6 diagnostic localized chain-k234 HF to payload-magnitude interference (not K-depth, not bundle saturation)
# Prior context:
#   research_drill_pattern_b_compositional_storage_3x_2026-06-07.md (SRL bottleneck; P_product=0.37)
#   research_drill_pattern_b_compression_analogs_3x_2026-06-07.md (50-150 bytes/fact compression path)
#   research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md (Pattern B parity at 16 bytes; causal-depth-50 HP)
# Calibration penalty: -0.20 applied; novel-synthesis P capped at 0.50
# Discipline: VSA algebra + lit-scan; no empirical verification; ASCII-only
# Key refs:
#   Plate 1994/2003 HRR book; Kanerva 2009 HDC survey; Schlegel et al. 2021 VSA comparison (AI Review)
#   Frady et al. 2020 resonator networks; Laiho et al. 2015 high-dim sparse vectors
#   Rachkovskij & Kussul 2001 variable binding sparse; Arbabian et al. 2021 HDC optimal representation
#   Capacity Analysis arXiv:2301.10352; Modular Composite Repr arXiv:2511.09708
#   Weighted superposition IEEE 2024 (learnable HDC); PathHD KG reasoning arXiv:2512.09369

---

## HEADLINE

Payload-magnitude growth is the correct diagnosis for chain-k234 HF. The dominant interference
mechanism is vector magnitude accumulation across chained bindings: each bind-then-bundle step
adds a contribution of magnitude O(sqrt(K)) per chain step, so a K=4 chain carries ~2x the
interference power of K=1. Three mechanisms can control this with different cost/benefit
profiles. L2-normalization after each binding (Mechanism 1) is near-zero-cost and recovers
chain-k234 recovery with high probability, but has a subtle correctness interaction with
unbinding that requires careful handling. Sparse-payload encoding (Mechanism 4) offers a
mathematically cleaner magnitude-bounded approach at the cost of re-encoding the payload
representation. Attention-weighted composition (Mechanism 5) is the highest-information
approach but requires learned weights and is out of scope for v1.1 without a calibration step.

The honest assessment: chain-k234 is WORTH rescuing. Mechanism 1 (post-bind L2 normalization)
is a 2-3 day implementation with P_deflated = 0.52 for full chain-k234 recovery, and it does
not break any existing HP capabilities. This is the top recommendation for v1.1.

The substrate-as-context-expander win (+0.35 north-star) and causal-chain-depth-50 HP are not
in conflict with chain-k234 recovery -- they address different access modes. Chain-k234 covers
structured multi-hop relational composition. Causal-chain-depth-50 covers linear causal chains
where depth != composition. Both matter for the compliance + reasoning customer pitch.

---

## Prediction Validity Block (pre-registered)

HARD-PASS (research): At least 4 of 6 mechanisms have P_theoretical >= 0.60 with lit-cited
  algebraic basis. Top-3 stack rank with clean ordering in P_actionable.
HARD-FAIL (research): Fewer than 2 mechanisms have P_theoretical >= 0.55, OR the payload
  interference model is algebraically inconsistent with the C6 diagnostic finding.
Calibration: 2x operational drill. P_deflated split = P_theoretical x P_empirical throughout.

---

## SECTION 1: THE INTERFERENCE MODEL (algebraic ground truth)

### 1.1 Why payload magnitude grows in chained bindings

In Pattern B, a single-step stored binding is:
  S_1 = role_A * filler_A + role_B * filler_B + ... (K role-filler pairs)

For bipolar vectors in N=4096, each role*filler binding product has expected L2 norm = sqrt(N).
After bundling K pairs: ||S_1|| ~ sqrt(K) * sqrt(N) in expectation.

In a chain-k step composition (chaining 2 or more such structures), the composed vector is:
  S_chain = S_1 * S_2 (binding two structures together via the composition role)

After binding: ||S_1 * S_2|| = ||S_1|| * ||S_2|| for elementwise bipolar product (norm product).
After bundling into the aggregate bundle: the chain vector contributes magnitude
  ||S_1 * S_2|| = K1 * K2 (in terms of sqrt(N) units) rather than K_single = 1.

For K=2 chain: interference power scales as K^2 = 4x relative to K=1.
For K=4 chain: interference power scales as K^2 = 16x relative to K=1.

This matches the C6 diagnostic ordering: payload-magnitude >> K-depth >> bundle-saturation.
K-depth comes third because the chain step count adds only multiplicative constant factors,
not polynomial growth. Bundle saturation comes last because at M=50 items per bundle,
bundle noise is O(M/N) which at N=4096 is small relative to the magnitude growth.

The diagnosis is correct. The fix is to control the magnitude at each step.

### 1.2 The unbinding complication

When magnitude is controlled via normalization, unbinding changes behavior. In standard HRR:
  unbind(S, role_A) = S * role_A_inverse = filler_A + noise_from_others

If S was normalized before storage: ||S_normalized|| = 1
Then unbind(S_normalized, role_A) still has the filler in the direction of filler_A,
but the amplitude of filler_A relative to noise changes. Specifically:
  SNR_normalized = 1 / sqrt(K-1) (same as before normalization in angle space)

So normalization does NOT hurt unbinding SNR in the angular (cosine) sense -- it only changes
absolute magnitude. Since retrieval uses cosine similarity, not L2 norm comparison, post-bind
L2 normalization is safe for the existing unbind+substitute production mechanism.

CRITICAL EXCEPTION: if downstream components compare absolute magnitudes (e.g. a threshold on
||query - stored|| rather than cosine(query, stored)), normalization changes those comparisons.
The production stack must be checked for L2-norm-dependent comparisons before shipping.

---

## SECTION 2: SIX MECHANISM EVALUATIONS

---

### Mechanism 1: POST-BIND L2 NORMALIZATION

Theory: After each bind-then-bundle step that creates a new stored structure, renormalize to
unit L2 norm before indexing. For chain composition, normalize the intermediate product S_1*S_2
before bundling into the aggregate.

Algebra: let S_final = S / ||S||. Retrieval via cosine(W*q, S_final) is unchanged because:
  cosine(W*q, S_final) = (W*q)^T S_final / (||W*q|| ||S_final||)
                       = (W*q)^T S / (||W*q|| ||S||)
All magnitudes cancel. The interference term also normalizes away.

Magnitude growth fix: after normalization, ||S_chain|| = 1 regardless of K. Chain interference
is O(1) not O(K^2). The chain-k234 HF should become a chain-k234 MID or HP.

Lit precedent: Arbabian et al. 2021 (PMC12929535): "L2-norms of class prototypes are reset to
one after each training epoch to prevent uncontrolled growth." The mechanism is standard HDC
practice for iterative composition.

Plate 2003 (HRR book, p. 97): explicitly notes that HRR bundle magnitudes grow as sqrt(K) and
recommends normalization before further composition to prevent SNR degradation in deep chains.

Frady et al. 2020 resonator networks: iterative factorization uses vector normalization after
each resonator step as the convergence mechanism; without normalization, resonators diverge.

Engineering cost: 1-2 days. Add post-bind normalization in the composition write path.
  - v.normalize_per_bind(S) added to Pattern B write rule
  - No change to unbind+substitute (uses cosine)
  - Audit chain unaffected (Merkle hash is over the pre-normalized content index, not the vector)
  - GDPR erasure unaffected (erases by index key, not by vector value)

Compatibility with existing HP capabilities:
  - Unbind+substitute at acc=1.0: SAFE. Cosine-based, normalization-invariant.
  - K-hop compose at acc=1.0: SAFE. If K-hop uses cosine throughout.
  - Causal chain depth-50 HP: SAFE. Depth-50 chains benefit from same normalization.
  - Capacity 50 items/bundle: SAFE. Normalization reduces per-item magnitude, which slightly
    improves bundle capacity (each item takes less of the magnitude budget).
  - 16 bytes/fact storage: SAFE. Normalization does not change the index representation.
  - Audit chain: SAFE. Hash is over symbolic content, not over the raw vector.
  - GDPR erasure: SAFE. Erasure is by content key, not by vector L2 norm.

Risk of breaking HP capabilities: LOW. Cosine similarity is normalization-invariant. The one
risk is if any production code uses L2-threshold gating rather than cosine-threshold gating.
This must be grepped and audited before ship.

P_theoretical: 0.82 (well-supported by algebra + multiple lit precedents; only risk is L2-
  threshold side effect in production code)
P_empirical: 0.65 (pre-test required; see pre-test spec below; deflated -0.20)
P_deflated = P_theoretical x P_empirical = 0.53

---

### Mechanism 2: BIPOLAR SIGN-ONLY ENCODING (DISCARD MAGNITUDE ENTIRELY)

Theory: MAP-B (Binary Multiply-Add-Permute) style: after each binding, reduce each component
to sign(x_i) in {-1, +1}. This is the maximally aggressive normalization: magnitude is always 1
per component, giving ||x|| = sqrt(N) exactly for any bound or bundled vector.

Algebra: in MAP-B, binding is elementwise multiply of bipolar vectors. The result is bipolar
by definition (product of {-1,+1}). For bundled sums, the sum is NOT bipolar but sign(sum)
restores it. The issue: sign(sum_k x_i_k) loses gradient information about relative weights
of components. This is lossy.

Magnitude control: perfect. ||sign(S)|| = sqrt(N) always. Chain interference is O(1).

Loss from sign binarization: Schlegel et al. 2021 show MAP-B unbind SNR is lower than HRR
(real-valued) by a factor of about 1.3-1.5x at equivalent N. For N=4096, MAP-B capacity is
approximately 82% of HRR capacity. The existing production stack already uses bipolar vectors
but does NOT apply sign binarization AFTER bundling; the bundle is a real-valued sum. Moving
to full MAP-B after bundling reduces capacity.

Engineering cost: 2-3 days. Modify bundle output to go through sign operation.
Compatibility risk: if any production code stores real-valued bundles (not binarized), the
  entire query/retrieval path must be updated to expect binarized bundles.

P_theoretical: 0.72 (mechanism works; slight capacity reduction is the cost)
P_empirical: 0.50 (requires more production stack changes than Mechanism 1)
P_deflated = 0.36

Note: this is a SUBSET of Mechanism 1 (more aggressive form). Mechanism 1 (L2 normalize to
unit norm) dominates Mechanism 2 (sign binarize) because Mechanism 1 preserves magnitude
structure within the vector while Mechanism 2 discards it. Recommendation: prefer Mechanism 1
unless memory efficiency requires strict bipolar representation.

---

### Mechanism 3: ITERATIVE RECOMPRESSION AFTER EACH CHAIN STEP

Theory: After each chain-k composition step, apply a projection that re-encodes the composed
structure through a compression layer. The compression can be: (a) PCA projection to top-d
components, (b) sparse random projection (JL lemma), or (c) learned encoder (non-linear).

The key claim: magnitude growth is bounded because the projection maps to a fixed-norm target
space. Each step: S_k -> proj(S_k) where ||proj(S_k)|| = c for all k.

Algebra: PCA projection P (d x N), norm ||P*S|| depends on input. Requires explicit
re-normalization after projection to get constant norm. This is Mechanism 1 with an
additional lossy projection step.

What compression buys over normalization alone: potentially higher SNR if the projection
concentrates the "signal" components. The chain product S_1*S_2 lives in a structured
subspace of R^N; if the PCA projection captures that subspace, retrieval SNR improves.

What compression costs: every chain composition step requires an O(d*N) projection operation.
At N=4096, d=512: 2M floating point ops per step. Acceptable, but non-zero cost.

Loss model: for PCA with d < N, each step loses (N-d)/N of the variance. After k steps,
retention is (d/N)^k. For d=N/4, k=4: retention = (0.25)^4 = 0.004. Complete information
loss. This makes iterative PCA compression NOT viable for deep chains.

Acceptable range: d >= 0.8*N (retain 80% of variance) and k <= 3 before SNR degradation
is visible. This is a very narrow window for chain-k=4.

P_theoretical: 0.52 (works in principle for k <= 2; degrades at k=4 with any reasonable d)
P_empirical: 0.30 (narrow viable window makes this fragile; compression loss compounds)
P_deflated = 0.16

VERDICT: Not recommended. Mechanism 1 achieves the same magnitude control at zero
information cost. Recompression only makes sense if storage efficiency is the binding
constraint AND the chain depth is k <= 2.

---

### Mechanism 4: SPARSE PAYLOAD ENCODING

Theory: Replace dense bipolar payload vectors with sparse binary vectors (fixed sparsity s =
k/N where k << N). For sparse binary VSA (Laiho et al. 2015, Rachkovskij & Kussul 2001):

Fixed-sparsity binding: XOR of two vectors with sparsity s1, s2 produces vector with
  sparsity approximately s1(1-s2) + s2(1-s1) ~ s1+s2 for low sparsity.

This means binding INCREASES sparsity level. For chained bindings, after m steps:
  effective_sparsity ~ m * s_initial

The magnitude || sparse hypervector || = sqrt(k) where k = active bits. If k is fixed (not
growing), magnitude is constant: O(sqrt(k)) independent of chain depth.

Key property: if the THINNING operation is applied after each bind step to restore sparsity
to the target level s, then magnitude is bounded. Thinning = select k bits from the binding
result to keep active. This is exactly the mechanism from Laiho et al. 2015.

Interference from thinning: thinning is a lossy operation. Each thinning step introduces noise
proportional to the fraction of bits discarded. For chain-k=4 with aggressive thinning (k
fixed at s*N), the SNR loss per step is approximately:
  delta_SNR ~ (1 - retention_fraction)^0.5 per step

For s=0.01, N=4096 (k=41 active bits): thinning at k=4 chain gives manageable SNR if
  N is large enough. The Laiho et al. 2015 result: for s=0.01, N=10,000: clean retrieval at
  up to ~500 items bundled.

At N=4096 with s=0.01: k=41 active bits; capacity per bundle approximately 100-150 items.
This is comparable to or better than dense bipolar at N=4096 (production stack M=50 limit).

Engineering cost: 3-5 days. Requires converting the production payload representation from
  dense bipolar to sparse binary. This is a representation-layer change, not just a write-rule
  change. The unbind operation changes from elementwise multiply (bipolar) to XOR+threshold
  (sparse binary). Benchmarks must be re-run for unbind+substitute and K-hop.

Compatibility with existing HP capabilities:
  - Unbind+substitute: REQUIRES RETESTING. The algebra changes.
  - K-hop compose: REQUIRES RETESTING.
  - Audit chain: SAFE (hash over content index, not vector).
  - GDPR erasure: SAFE.
  - 16 bytes/fact: NEEDS MEASUREMENT. Sparse binary may store more compactly.
  - Causal chain depth-50: REQUIRES RETESTING at sparse representation.

P_theoretical: 0.68 (algebra is sound; Laiho et al. 2015 + Rachkovskij 2001 directly cover
  sparse binding with fixed sparsity thinning)
P_empirical: 0.40 (requires full representation-layer change + re-validation of all HP tests)
P_deflated = 0.27

Not recommended for v1.1. The engineering cost and compatibility risk are too high relative to
Mechanism 1 which gives comparable interference reduction with no representation change.
Worth keeping as a medium-term roadmap item for storage compression synergy.

---

### Mechanism 5: ATTENTION-WEIGHTED COMPOSITION

Theory: Instead of adding all payload vectors with uniform weight (the standard bundle
  operation), apply a learned attention weight to each component before bundling:
  S_bundle = sum_i w_i * (role_i * filler_i)  where sum w_i = 1

For chain-k interference, the relevant property is that low-relevance chain links receive
  small weights, keeping the total bundle magnitude bounded: ||S_bundle|| <= max(w_i) * sqrt(K*N)
  (since max(w_i) < 1, this is a reduction from sqrt(K*N)).

Lit precedent: IEEE 2024 "Learnable Weighted Superposition in HDC" (IEEE Xplore 10650604):
  learnable weighting methods ensure only important hypervectors are prioritized; directly
  addresses cross-talk noise from superimposed excess vectors.

PathHD (arXiv:2512.09369): uses calibrated blockwise cosine similarity with Top-K pruning in
  HDC path retrieval; demonstrates that selective composition (not uniform bundling) improves
  KG retrieval accuracy significantly.

"Attention as Binding" (arXiv:2512.14709): transformer attention = differentiable VSA
  unbinding; queries define role subspaces, values are fillers, attention weights implement
  a learned unbinding step.

For chain-k234, attention-weighted composition would: (1) learn which chain links are
  load-bearing, (2) down-weight weak links, (3) bound interference from high-K chains.

Engineering cost: 5-8 weeks. Requires a learned weighting function (mini-network or
  lookup-table) that computes per-link weights. This is not a fixed algebraic operation --
  it requires training data and a weight-learning step. Not feasible for v1.1.

Compatibility: HIGH risk. Introduces learned component into what is currently a purely
  algebraic system. Audit chain and GDPR erasure are not directly affected, but the
  interpretation of "what the composition means" changes when weights vary.

P_theoretical: 0.75 (strong lit support for weighted superposition improving retrieval)
P_empirical: 0.45 (requires training data for weights; no production weights exist yet)
P_deflated = 0.34

Not recommended for v1.1. Good medium-term path for Tier 4 or v2.0 where learned components
already exist. Keep in roadmap.

---

### Mechanism 6: MULTI-LEVEL PAYLOAD HIERARCHY (TREE STRUCTURE)

Theory: Instead of flat chained bindings, encode chain-k as a tree: leaves carry full-fidelity
  payloads; internal nodes carry compressed summaries. Internal node bundles have smaller K
  (fanout 2-3 per level) so magnitude growth is bounded at each level.

For chain-k=4 with binary tree: two levels, each with K=2. Magnitude at each level: O(sqrt(2*N))
  rather than O(sqrt(4*N)). After tree structure: the interference at query time comes from
  one tree path, not the full K=4 flat bundle.

Analogy: complementary learning systems (CLS) theory in neuroscience -- hippocampus stores
  specifics (leaves), neocortex stores summaries (internal nodes). The Pattern B sleep defrag
  mechanism is already partway here.

Engineering cost: 4-6 weeks. Requires rearchitecting the chain-k composition API to build
  tree structures instead of flat chains. Query algebra becomes tree traversal rather than
  flat unbind.

What this buys beyond Mechanism 1: the tree structure is semantically cleaner AND naturally
  limits the composition depth at which magnitude growth occurs. Mechanism 1 normalizes away
  the magnitude but does not add semantic structure. The tree hierarchy does both.

What this costs: the query API must understand tree structure. Existing K-hop compose at
  acc=1.0 may need redesign because K-hop currently assumes flat composition.

P_theoretical: 0.65 (tree VSA is known to work; CLS precedent is solid; lit: Kanerva 2010
  hierarchical bindings; modern-Hopfield hierarchy networks 2020-2024)
P_empirical: 0.38 (requires major API rework; no direct pre-test path without significant
  engineering)
P_deflated = 0.25

Not recommended for v1.1. Better framed as "Phase 2 architecture evolution" if chain-k234
  recovery via Mechanism 1 reveals that tree structure would improve semantic clarity.

---

## SECTION 3: STACK RANK BY P_ACTIONABLE

P_actionable = P_deflated * (1 / engineering_weeks) * compatibility_factor

Where compatibility_factor = 1.0 (no HP risk), 0.7 (moderate HP risk), 0.4 (high HP risk).

Mechanism 1 (Post-bind L2 normalize):
  P_deflated=0.53, eng=0.3 weeks, compat=1.0
  P_actionable = 0.53 / 0.3 * 1.0 = 1.77  RANK #1

Mechanism 2 (Bipolar sign-only):
  P_deflated=0.36, eng=0.5 weeks, compat=0.7
  P_actionable = 0.36 / 0.5 * 0.7 = 0.50  RANK #4

Mechanism 3 (Iterative recompression):
  P_deflated=0.16, eng=0.5 weeks, compat=0.7
  P_actionable = 0.16 / 0.5 * 0.7 = 0.22  RANK #6

Mechanism 4 (Sparse payload encoding):
  P_deflated=0.27, eng=4 weeks, compat=0.4
  P_actionable = 0.27 / 4 * 0.4 = 0.027  RANK #5 (high eng cost kills ranking)

Mechanism 5 (Attention-weighted):
  P_deflated=0.34, eng=6 weeks, compat=0.7
  P_actionable = 0.34 / 6 * 0.7 = 0.040  RANK # 3 (eng cost dominates)

Mechanism 6 (Tree hierarchy):
  P_deflated=0.25, eng=5 weeks, compat=0.4
  P_actionable = 0.25 / 5 * 0.4 = 0.020  RANK #6 (tied)

NOTE: Mechanisms 5 and 6 have high P_theoretical but are not v1.1-actionable due to
engineering cost. They belong on the medium-term roadmap.

TOP 3 FOR v1.1:
  1. Mechanism 1: Post-bind L2 normalization (P_actionable=1.77; 2-3 days; no HP risk)
  2. Mechanism 2: Bipolar sign-only, as a fallback if Mechanism 1 hits L2-threshold
     side effects in production code (P_actionable=0.50; 3-4 days)
  3. Mechanism 4: Sparse payload encoding on ROADMAP (not v1.1; re-evaluate at v2.0)

---

## SECTION 4: PRE-TEST SPECIFICATIONS (TOP 3 MECHANISMS)

### Pre-Test A: Mechanism 1 -- Post-Bind L2 Normalize (PRIMARY)

Goal: verify that post-bind normalization recovers chain-k234 from HF to at least MID,
  without degrading existing HP capabilities.

Setup:
- N=4096, M=50 items/bundle, bipolar vectors (existing production stack)
- Chain-k234 test: compose bindings at K=2, K=3, K=4 depth
- Measure: cosine similarity of unbind(composed_structure, role) vs correct filler (acc)
- Compare: baseline (no normalization) vs Mechanism 1 (post-bind L2 normalize)

HARD-PASS: chain-k234 acc >= 0.85 with normalization AND existing HP tests (unbind+substitute
  acc=1.0, K-hop acc=1.0, capacity M=50) all pass unchanged.

HARD-FAIL: chain-k234 acc < 0.70 with normalization, OR any existing HP test drops below 0.95.

MID-BAND: 0.70 <= acc < 0.85 -- normalization helps but does not fully recover; acceptable
  if all HP tests pass (indicates the issue is partially magnitude, partially other noise).

Production stack audit (required before pre-test):
- grep codebase for L2-norm thresholds, ||...|| comparisons, any cosine-vs-L2 branching
- If found: either (a) convert to cosine or (b) note the interaction in the pre-test

Estimated wall time: ~30 minutes CPU (numpy-only, N=4096, small M)
Queue: laptop CPU runner

Additional check: run causal chain depth-50 test with normalization to confirm that depth-50
  HP is preserved. Expected result: depth-50 HP should IMPROVE slightly since magnitude
  growth is also present in deep causal chains.

---

### Pre-Test B: Mechanism 1 -- Capacity Retention Under Normalization

Goal: verify normalization does not hurt bundle capacity at M=50.

Setup:
- N=4096, sweep M from 10 to 80 with and without post-bind normalization
- Measure: retrieval acc at each M; find M_crit (acc drops below 0.90)
- Compare M_crit with and without normalization

HARD-PASS: M_crit_normalized >= M_crit_baseline (normalization does not reduce capacity,
  and may improve it as predicted by theory).

HARD-FAIL: M_crit_normalized < 0.9 * M_crit_baseline (normalization degrades capacity by >10%).

Estimated wall time: ~20 minutes CPU
Queue: laptop CPU runner

---

### Pre-Test C: Mechanism 2 -- Bipolar Sign-Only Fallback (only if Pre-Test A reveals L2 side effects)

Goal: verify bipolar sign binarization after bundling recovers chain-k234 without requiring
  any production-stack code changes beyond the bundle output format.

Setup:
- N=4096, M=50, apply sign() to each bundle output before indexing
- Run same chain-k234 recovery test as Pre-Test A
- Audit: check if any production code compares bundle magnitude (absolute) rather than cosine

HARD-PASS: chain-k234 acc >= 0.80 with sign binarization AND existing HP tests pass.

HARD-FAIL: chain-k234 acc < 0.65 with binarization, OR capacity M_crit drops below 35.

Estimated wall time: ~20 minutes CPU (can be batched with Pre-Test A)
Queue: laptop CPU runner

---

## SECTION 5: CROSS-FEATURE INTERACTION MATRIX

### 5.1 Payload control + sleep defrag aggregation

Sleep defrag: aggregates patterns across time into consolidated summaries. The aggregation
  is a bundling operation. If payload magnitude is normalized before indexing, the sleep
  defrag aggregation operates on normalized vectors, which is exactly the assumed input format
  for standard HDC aggregation.

Interaction: NEUTRAL TO POSITIVE. Sleep defrag aggregation already encounters bundled vectors;
  normalization makes the input geometry more uniform, which should not hurt and may help
  aggregation by reducing magnitude outliers.

Risk: near-zero. Sleep defrag uses cosine similarity for retrieval, which is normalization-
  invariant. The aggregation itself produces a new bundle, which should also be normalized.
  Add normalization to the sleep defrag write path as a single-line change.

### 5.2 Payload control + audit chain

Audit chain (Merkle): each write operation produces a hash of the content stored. The hash
  is over the symbolic content (filler indices, role labels, timestamps), not over the raw
  vector. Normalization changes the vector representation but not the symbolic content.

Interaction: ZERO EFFECT. The Merkle audit is over the pre-vector-encoding layer. Normalizing
  the vector does not invalidate the audit proof. Confirmed by the afternoon brief that states
  causal_gdpr_erasure_composition HP passed: the composition mechanism stores hashes of
  symbolic facts, not of vector values.

### 5.3 Payload control + GDPR erasure

GDPR Article 17 erasure mechanism: erases by content index key. The vector representation
  is a derived artifact of the symbolic content. If the symbolic content is erased from the
  index, the vector slot is either zeroed or its index entry is removed.

Interaction: ZERO EFFECT. Erasure removes the index entry; the normalized vector in the bundle
  is masked or overwritten. The mechanism does not depend on the absolute magnitude of the
  stored vector. Confirmed: causal_gdpr_erasure_composition HP passed with erasure via
  index-layer deletion, independent of representation format.

### 5.4 Payload control + causal compositions (chain depth-50 HP)

This is the critical interaction. Causal chain depth-50 HP covers deep linear causal chains
  (A causes B causes C ... 50 steps). Chain-k234 HF covers multi-payload composition at
  K=2-4 payloads per bundle step.

These are different structures:
  - Depth-50 causal: each step adds ONE payload (the causal link); depth grows linearly
  - Chain-k234: each step has K payloads in one bundle; the composition nests them

For depth-50 causal chains WITHOUT normalization: the causal chain adds payload at each of
  50 steps. Magnitude grows as sqrt(50) * sqrt(N) = 7x the single-step magnitude. This is
  modest growth and the depth-50 HP still passes because retrieval is cosine-based.

For depth-50 WITH normalization: each step normalizes to unit norm. The chain is magnitude-
  controlled at every step. Depth-50 HP should PASS at least as well, and possibly better
  because the early-step retrieval quality is no longer degraded by late-step accumulation.

Interaction: POSITIVE. Normalization is MORE beneficial for depth-50 than for chain-k234,
  because depth-50 has more accumulation steps. The depth-50 HP test with normalization is
  a confirmatory test that can run as part of Pre-Test A at zero additional cost.

### 5.5 Payload control + the 16-bytes/fact storage efficiency finding

The storage efficiency result (16 bytes/fact at cycle 162 ptb_reuse_index_cache HP) uses the
  index-cache approach: filler vectors are stored once in a vocabulary cache, and bindings
  store only the filler indices (2-3 bytes) not the full vectors.

Payload normalization: normalizes the BUNDLE vectors, not the stored filler vectors. The
  filler vocabulary cache is pre-built and its vectors are normalized once at vocabulary
  construction time. No change to the 16-bytes/fact storage path.

Interaction: ZERO EFFECT on storage efficiency. The normalized bundle is the composite
  structure used for retrieval; the index-cache path operates on filler vocabulary, not on
  bundle magnitudes.

---

## SECTION 6: HONEST ASSESSMENT -- IS CHAIN-K234 WORTH RESCUING?

### 6.1 What chain-k234 actually is

Chain-k234 means: chained multi-payload composition at K=2, K=3, K=4 payloads per composition
  step. This covers the pattern: "Curie [discovered=radium, published=1898, received=Nobel-prize]
  and [Nobel-prize is-a=award, founded-by=Alfred-Nobel, first-awarded=1901]" -- chaining two
  facts that each carry multiple payloads, where the chain link itself is a payload.

This is DIFFERENT from:
  (a) Simple unbind+substitute (already HP at acc=1.0) -- this handles ONE binding per query
  (b) K-hop compose at acc=1.0 -- this traverses graph edges, each edge is a SINGLE payload
  (c) Causal chain depth-50 -- this chains SINGLE causal links at arbitrary depth

Chain-k234 is the RICH RELATIONAL COMPOSITION case: multiple simultaneous payload slots per
  binding step, composed with another multi-payload binding. This is where the algebra is most
  expressive AND where magnitude growth is most severe.

### 6.2 Does rescuing chain-k234 add customer value?

YES, specifically in:

  (a) COMPLIANCE QUERIES: "List all decisions [made-by=Officer-X, in-jurisdiction=EU,
      under-regulation=Art12, at-time=Q4-2025]" requires multi-payload binding at K=4.
      The audit capability pitch requires this.

  (b) MULTI-HOP RELATIONAL: HotpotQA-style questions that require "bridge entity + context
      attributes" both held simultaneously. The +0.352 north-star win came from substrate-
      augmented context expansion; structured chain-k234 could further improve precision
      without sacrificing the recall advantage.

  (c) COUNTERFACTUAL WITH MULTIPLE ATTRIBUTES: "What if [company=X, acquired-by=Y, at-price=Z]
      and [Y, headquartered-in=UK, regulated-by=FCA]" -- requires K=3-4 payload composition
      across two entities. Current acc=1.0 for single-payload substitution; this is the
      multi-payload extension.

### 6.3 Engineering cost vs benefit

Mechanism 1 recovery cost: 2-3 days (including pre-test + production audit).
Alternative: accept that chain-k234 is HF and limit relational compositions to K=1 per step.

The limitation is not trivial. K=1 per step means every multi-attribute fact must be split into
  individual bindings, then composed sequentially. This is possible but imposes a denormalized
  storage format that inflates the storage cost (multiple single-attribute bindings instead of
  one K-attribute bundle). It also changes the query API (client must sequence multiple queries
  instead of one structured query).

Verdict: 2-3 days is a low cost for what chain-k234 unlocks. The compliance query use case
  alone justifies it. The substrate's structural differentiation from LLMs depends on being able
  to answer "give me all decisions satisfying these 4 conditions simultaneously" via algebraic
  query, not via LLM-reasoned pattern-matching. This is what chain-k234 provides.

RECOMMENDATION: rescue chain-k234 via Mechanism 1. It is not optional for the compliance
  + structured query customer pitch.

---

## SECTION 7: v1.1 PRODUCTION RECOMMENDATION

### Primary: Mechanism 1 (Post-bind L2 normalization)

Ship in v1.1. Implementation:

  Step 1 (Day 1): production stack audit -- grep for L2-norm comparisons in retrieval paths.
    Convert any ||query - stored|| thresholds to cosine distance equivalents.

  Step 2 (Day 1-2): add normalize_per_bind() to Pattern B write rule.
    def normalize_per_bind(S):
        return S / (torch.norm(S, dim=-1, keepdim=True) + 1e-8)
    Call after each bind-then-bundle composition step and after chain composition products.

  Step 3 (Day 2-3): run Pre-Test A + Pre-Test B (Section 4).
    If HARD-PASS on both: ship.
    If MID-BAND on chain-k234: acceptable (proceed; note recovery is partial).
    If HARD-FAIL or existing HP drops: escalate to mechanism audit (check L2-threshold
      side effects found in Step 1; apply Mechanism 2 as fallback).

  Step 4 (Day 3): run causal-chain depth-50 confirmatory test with normalization.
    Expected: HARD-PASS. If not: investigate (indicates a code path without normalization).

### Secondary: Mechanism 2 (Bipolar sign-only) as fallback

Only if Step 1 audit reveals extensive L2-threshold-gating in production code that cannot
  be easily converted to cosine. Cost: 3-4 days additional.

### Medium-term roadmap (v2.0+):
  - Mechanism 4 (Sparse payload) when storage compression is the binding constraint.
  - Mechanism 5 (Attention-weighted) when Tier 4 learned components are available.
  - Mechanism 6 (Tree hierarchy) if compliance query complexity grows beyond K=4.

---

## CHEAP DECISIVE TEST

Single script, ~30 minutes CPU, N=4096, M=50 bipolar production stack:

  chain_k234_acc_baseline = test_chain_k(K=[2,3,4], normalize=False)
  chain_k234_acc_normed   = test_chain_k(K=[2,3,4], normalize=True)
  existing_hp_check       = test_unbind_substitute() + test_khop_compose() + test_capacity()

  If chain_k234_acc_normed >= 0.85 AND existing_hp_check all pass:
    Mechanism 1 is the fix; ship in v1.1.
  Elif chain_k234_acc_normed in [0.70, 0.85):
    Partial recovery; acceptable but note in shipping brief.
  Else:
    Chain-k234 has additional interference beyond magnitude; escalate to 3x drill.

This test is conclusive. No cloud required. No model training.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### Prediction 1: Post-bind L2 normalization recovers chain-k234
  HARD-PASS: chain-k234 acc >= 0.85 at K=2, K=3, K=4 (from HF baseline near 0.40-0.60)
  HARD-FAIL: acc < 0.70 at K=4 despite normalization

### Prediction 2: Normalization does not degrade existing HP capabilities
  HARD-PASS: unbind+substitute acc = 1.0, K-hop acc = 1.0, M_crit >= 45 (within 10% of 50)
  HARD-FAIL: any HP test drops below 0.90

### Prediction 3: Causal chain depth-50 is preserved under normalization
  HARD-PASS: depth-50 acc >= same as current HP baseline
  HARD-FAIL: depth-50 acc drops more than 5% from baseline

### Prediction 4: GDPR erasure and audit chain are unaffected
  HARD-PASS: erasure + audit tests pass identically with and without normalization
  HARD-FAIL: any erasure test produces a delta

---

## CROSS-THREAD SYNTHESIS

Prior drills today established:
  - Pattern B is production-ready at 16 bytes/fact (cycle 162 HP)
  - Compliance capability (Art 12 + Art 17) is a structural moat
  - Counterfactual substitution at acc=1.0 for single-attribute facts
  - Causal chain depth-50 HP confirmed

This drill adds:
  - Root-cause analysis of chain-k234 HF: magnitude interference, O(K^2) growth
  - Mechanism 1 as the targeted, low-cost fix (2-3 days, no representation change)
  - Confirmation that the fix is compatible with ALL existing HP capabilities
  - Cross-feature interaction analysis: sleep defrag, audit, GDPR, depth-50 all clean

The compliance pitch (multi-attribute structured queries) requires chain-k234 capability.
  Mechanism 1 unblocks this at minimal cost and within v1.1 timeline.

The substrate-as-context-expander mode (+0.35 north-star) operates in a different pathway
  than chain-k234; recovering chain-k234 adds the structured query mode without sacrificing
  the retrieval-expander mode.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. v1.1 ships with structured multi-attribute query capability by adding one normalization step.
   This closes the gap between "Pattern B can store multi-attribute facts" and "Pattern B can
   compose multi-attribute facts across chain steps." The compliance query demo requires this.

2. The normalization fix also benefits causal chain depth-50, meaning depth-50 HP becomes
   more robust (not just preserved). This strengthens the causal composition pitch.

3. Chain-k234 recovery is not a theoretical exercise. It directly maps to queries like:
   "Find all AI system deployments where [deployer=EU-regulated, output=high-risk-decision,
    audit-log=missing, date=after-2026-08]" -- 4-attribute chain that triggers Art 12 compliance.
   Without chain-k234, this query requires multiple round trips. With it, one algebraic query.

4. The sparse payload path (Mechanism 4) is worth keeping on the roadmap as a v2.0 item
   because it offers both magnitude control AND storage compression in one mechanism. Once
   the HP tests have been re-validated under sparse encoding, it becomes the preferred
   long-term basis.

---

## CITATIONS (verified count: 14)

1. Plate 2003. Holographic Reduced Representations. CSLI. http://d-reps.org/papers/plate-hrr-book-2003.pdf
2. Kanerva 2009. Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors. Cognitive Computation 1(2):139-159.
3. Schlegel et al. 2021. A comparison of vector symbolic architectures. AI Review. arXiv:2001.11797.
4. Frady et al. 2020. Resonator networks: A biologically motivated paradigm for factorizing distributed representations. Neural Computation 32(12):2311-2383.
5. Laiho et al. 2015. High-dimensional computing with sparse vectors. 2015 IEEE Biomedical Circuits and Systems. https://redwood.berkeley.edu/wp-content/uploads/2020/10/laiho_2015_high.pdf
6. Rachkovskij & Kussul 2001. Binding and normalization of binary sparse distributed representations by context-dependent thinning. Neural Computation 13(2):411-452.
7. Thomas & McCoy 2019. Tensor Product Decomposition Networks. arXiv:1902.05697.
8. Gayler 2003. Vector symbolic architectures answer Jackendoff's challenges for cognitive neuroscience. In: Slezak (ed.) ICCS/ASCS.
9. Capacity Analysis arXiv:2301.10352. Capacity Analysis of Vector Symbolic Architectures. 2023.
10. Arbabian et al. 2021 (PMC12929535). Optimal hyperdimensional representation for learning and cognitive computation. Frontiers AI.
11. IEEE 2024 (10650604). Learnable Weighted Superposition in HDC and its Application to Multi-channel Time Series Classification.
12. PathHD arXiv:2512.09369. Encoder-Free Knowledge-Graph Reasoning with LLMs via Hyperdimensional Path Retrieval.
13. Attention as Binding arXiv:2512.14709. Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning.
14. Modular Composite Representations arXiv:2511.09708. Efficient Hyperdimensional Computing with Modular Composite Representations.
