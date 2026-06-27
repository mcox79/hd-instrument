# 3x Research Drill: Tonegawa v3 BUNDLED HARD_FAIL Revival

**Filed:** 2026-06-27 ~17:35 PDT (research)
**Trigger:** USER directive on v3 BUNDLED smoke HARD_FAIL — `recall@1_at_K25` tone=0.040, proto=0.836, diag=0.044; all collapsed to 0.0 at K=100
**Method:** 2x drill discipline + independent third angle (3x for HARD_FAIL recovery vs cosmetic 2x); generic-terms-only; lit-scan penalty applied; novel-synthesis P capped at 0.50

---

## Bottom-line up front

**Tonegawa v3 lost not because sparse-ensemble is wrong, but because XOR-bind is the wrong operator for k-WTA sparse codes.** XOR was designed for dense bipolar vectors where every position carries ±1; on a code where 99% of positions are 0, XOR with a dense schema_id FLOODS the sparse channel — the unbound query loses k-WTA structure entirely. Both prototype and diagnostic baselines also collapsed at K=100 (proto fell from 0.836 to 0.0), so the failure mode is structural to the BUNDLED-with-XOR architecture, not Tonegawa-specific. Diagnostic at 0.044 ≈ chance (1/25 = 0.04) confirms the unbinding produces noise.

The three angles converge on **two top revival cells**: (TOP-1) permutation-bind for sparse codes, (TOP-2) separate-attractor BUNDLED with content-addressable cleanup.

---

## ANGLE A — Pure math: Treves-Rolls and the XOR/sparse incompatibility

Treves-Rolls capacity for sparse codes at sparseness `a`:
```
C_sparse ≈ N / (a * log(1/a))    [Treves & Rolls 1991, signal-to-noise derivation]
```
At a = 0.01 (k=20, N=2000), C_sparse ≈ 2000 / (0.01 × 4.6) ≈ 43,000 patterns — orders of magnitude above dense (`C_dense ≈ 0.14 × N ≈ 280`). So the theory says sparse SHOULD dominate.

**Why it didn't in v3:** Treves-Rolls assumes Hebbian outer-product storage with a thresholded cleanup attractor. v3 used XOR-superposition, which is the WRONG storage mechanism for sparse codes:

- XOR(dense_id, sparse_code) where dense_id has Hamming weight N/2 produces an output with weight ≈ N/2 (dense). The sparse structure is destroyed in the bound representation.
- Sum over K=25 such dense vectors hits Gaussian-noise saturation by central limit theorem at small K.
- Query XOR(id_k, S) returns sparse_code_k buried in O(K·N/2) noise. SNR ≈ 1/sqrt(K-1) for dense bipolar, much worse for sparse where signal is k = 20 bits but noise is K·N/2 bits.

**Theoretical crossover:** for sparse code with k active bits, SNR at top-1 unbinding ≈ k / sqrt((K-1)·N·a·(1-a)). Setting SNR ≥ 3 for reliable retrieval:
```
K_max ≈ k² / (9 · N · a · (1-a)) + 1 = 400 / (9 · 2000 · 0.01) ≈ 2.2
```
**The theory predicts XOR-bind sparse-ensemble survives only K ≤ 2-3**, explaining total collapse at K=100 AND poor performance at K=25.

**Two mechanism fixes from math:**

1. **A1 — Sparse-XOR with thresholded reconstruction:** replace dense `schema_id` with sparse bipolar id (sparseness matched to code: a_id = a_code = 0.01). XOR of two sparse-bipolar vectors stays sparse. Then BUNDLED sum stays in the sparse signal manifold. Closed-form SNR boost ≈ 1/a ≈ 100x.

2. **A2 — Permutation-bind (no XOR at all):** bind by cyclic shift `S = sum_k roll(sparse_code_k, hash(schema_id_k))`. Unbind by reverse shift. This is the Plate-1995 BSC adaptation for sparse codes — no destruction of sparseness, no Gaussian-noise floor from dense superposition. Theory predicts capacity ≈ N/(k·log N) ≈ 13,000 for our regime.

**Falsifiable prediction:** at K=500 with A2 permutation-bind, Tonegawa should achieve `recall@1 ≥ 0.10` while prototype-centroid-bundled drops below 0.05 (centroid bundling has dense superposition noise too at K=500). Discriminator: PERM_TONEGAWA - PROTO_BUNDLED ≥ 0.05 at K=500, ≥ 0.20 at K=2000.

---

## ANGLE B — Biology: what Tonegawa engram cells actually do

Tonegawa's Nobel work (Liu et al. 2012 Nature; Ramirez et al. 2013 Science) characterized engram cells as:

1. **Sparse:** 1-5% of CA1/dentate gyrus neurons per memory
2. **Spatially overlapping but functionally distinct:** two memories share the same hippocampal volume but engage non-overlapping (≤10% intersection) cell subsets
3. **Independently reactivatable:** optogenetic stimulation of engram-cell-set for memory A retrieves A without contaminating B
4. **Reconsolidated by attractor dynamics:** cleanup is via recurrent CA3 collaterals, NOT by linear unbinding of a superposition

**Critical disanalogy with v3:** the brain does NOT bundle K memories into one substrate vector. CA3's recurrent attractor network maintains K SEPARATE attractors over a shared neural sheet. Retrieval is "which attractor does the cue fall into," not "subtract noise from a superposition."

Tonegawa's engram cells share substrate the way K stable points share a 2000-dim phase space — coexisting, not bundled.

**Two substrate-mappings closer to actual mechanism:**

1. **B1 — Separate-attractor BUNDLED with Hopfield-style cleanup:** instead of `S = sum XOR(...)`, store K sparse codes as K attractors in a Hopfield weight matrix `W = sum_k outer(c_k, c_k)`. Query `q` iterates `c_{t+1} = sign(W·c_t)` with k-WTA threshold. This is the Treves-Rolls regime where 43,000-pattern capacity is achievable. The "bundling" is in shared weights, not shared activation.

2. **B2 — Pattern-separated overlap-bundle:** explicitly construct sparse codes with controlled overlap (engram-cell biology has ~10% intersection, NOT orthogonal). Bundle via simple sum (no XOR): `S = sum_k c_k`. Recall a memory by reactivating its INDEX set and intersecting with S. This matches Tonegawa's optogenetic-reactivation protocol literally — addressing by cell-subset identity, not by binding key.

**Falsifiable prediction:** at K=500 with B1 Hopfield cleanup over k-WTA codes (3 cleanup iterations), Tonegawa should achieve `recall@1 ≥ 0.40` vs prototype < 0.10. The biological mechanism predicts ROBUST recall at high K — that's the whole point of why brains use this scheme. If B1 doesn't deliver, the substrate is missing an essential brain primitive.

---

## ANGLE C — Substrate-native: alternative bind operations for sparse codes

XOR is one of ~5 known binding operators in the HDC literature. The others were largely abandoned because XOR is fast and works for dense bipolar — but they're a better fit for sparse codes:

1. **Vector addition (HRR-additive):** `S = sum_k (id_k + code_k)`. Unbind: `code_k ≈ S - sum_{j≠k} id_j - sum_j code_j` (requires knowing other ids). NO clean unbinding; rejected.

2. **Circular convolution (Plate HRR):** `S = sum_k (id_k ⊛ code_k)`. Unbind: `code_k ≈ id_k* ⊛ S` where * is involution. Works for sparse codes IF id_k is approximately orthonormal. Capacity ≈ √N. Established mechanism; expensive O(N log N).

3. **Permutation-bind (Kanerva BSC for sparse, "Permutation HRR"):** `S = sum_k roll(code_k, shift(id_k))`. Unbind: `code_k ≈ roll(S, -shift(id_k))` then k-WTA cleanup. This is **the cheapest and cleanest** for sparse codes — preserves sparseness exactly, O(N), and the noise from other k-1 terms is k·(K-1) bits over N positions, with sparse k-WTA cleanup recovering signal up to K ≈ N/(k log N).

4. **Multiplicative bind (sparse-only):** if both id_k and code_k are sparse with disjoint supports (or one is a permutation matrix), `S = sum_k (id_k ⊙ code_k)` preserves sparsity. Recall requires id_k to be a sparse indicator vector. Equivalent to "named slots" — degenerate for our use case.

5. **Block-sparse bind (recent: Frady et al. 2020 "Variable Binding for Sparse Distributed Representations"):** partition N into blocks; each schema gets a block-permutation; binding is in-block permutation. Capacity = number of blocks; very clean isolation between schemas. Excellent fit but adds architectural complexity (block structure).

**Recommendation:** C1 permutation-bind (option 3) is the substrate-native sweet spot — minimal departure from current substrate primitives, mathematically clean for sparse, supported by 25+ years of HDC literature on permutation binding.

**Falsifiable prediction:** at K ∈ {100, 500, 2000} with N=2048 and k=20:
- C1 permutation-bind: recall@1 ≈ {0.95, 0.65, 0.20}
- v3 XOR-bind: recall@1 ≈ {0.0, 0.0, 0.0} (already observed at K=100)
- Prototype-centroid-bundled: recall@1 ≈ {0.50, 0.15, 0.02} (cosine noise scales with sqrt(K))

Discriminator at K=500: C1_TONEGAWA - PROTO_BUNDLED ≥ 0.40. (Larger margin than Angle A because permutation preserves sparseness exactly while centroid bundling dense-superposition-saturates.)

---

## Top-2 revival cells (ranked across angles)

### TOP-1: `tonegawa_v4_permutation_bundled` (Angle C1 + Angle A2 convergence)

**Mechanism:** bind via cyclic shift, not XOR.
```
S = sum_k roll(sparse_code_k, hash(schema_id_k) % N)
recall: cleanup(roll(S, -hash(schema_id_query)), k-WTA)
```

**Why ranked TOP-1:** two independent angles (math A2 + substrate-native C1) converge here. Cheapest implementation (O(N) per bind vs O(N²) for Hopfield cleanup). Preserves sparseness exactly through the bundle. No new substrate primitives needed — `roll` is already in hdlab/.

**Pre-reg sketch (envelope-fail-bands):**
- K sweep: {25, 100, 500, 2000}, N=2048, k=20
- Arms: PERM_TONEGAWA, XOR_TONEGAWA_v3 (reference for failure mode), PROTO_CENTROID_BUNDLED, DIAG_RANDOM_PERM
- HARD_PASS: PERM_TONEGAWA - PROTO_BUNDLED ≥ 0.20 at K=500 AND PERM_TONEGAWA ≥ 0.10 at K=2000
- MIDDLE_BAND: PERM_TONEGAWA - PROTO_BUNDLED ∈ [0.05, 0.20) at K=500
- HARD_FAIL: PERM_TONEGAWA - PROTO_BUNDLED < 0.05 at K=500 (theory wrong; pivot to TOP-2)
- CARDINALITY_OK: EXPECTED_N_UNITS per K (sweep cells need this per META_RULE_H)

**Compute:** K=2000, N=2048, 3 seeds, 4 arms ≈ 30 CPU-min, MAY benefit from GPU at K=2000. Route via hdi_orchestrator if K ≥ 500.

**Smoke discriminator (per "smoke fires discriminator" discipline):** smoke at K=500, single seed; if PERM_TONEGAWA - PROTO_BUNDLED < 0.10 at K=500 smoke, do NOT dispatch full sweep — pivot to TOP-2.

### TOP-2: `tonegawa_v5_hopfield_separate_attractor` (Angle B1)

**Mechanism:** K sparse codes stored as Hopfield attractors over shared weights, NOT bundled into one vector.
```
W = sum_k outer(c_k, c_k) / k_sparse
recall(q): iterate c_{t+1} = k-WTA(W · c_t, k) for 3-5 iters from q init
```

**Why ranked TOP-2:** highest biological fidelity (matches Tonegawa engram-cell mechanism literally). Theoretically capacity is 43,000 patterns (Treves-Rolls). BUT: substrate adds Hopfield primitive (not currently in hdlab/); higher compute cost (W matrix is 2048×2048 dense); cleanup iterations add latency. TOP-2 not TOP-1 only because of substrate-cost not theoretical merit.

**Pre-reg sketch:**
- K sweep: {25, 100, 500, 2000, 10000}, N=2048, k=20, 3 cleanup iters
- Arms: HOPFIELD_TONEGAWA, PERM_TONEGAWA (top-1 head-to-head), PROTO_BUNDLED
- HARD_PASS: HOPFIELD_TONEGAWA ≥ 0.40 at K=2000 AND ≥ 0.10 at K=10000 (Treves-Rolls regime)
- Compute: K=10000 requires GPU; W matrix 16 MB float32; ~2 GPU-hr. Route via hdi_orchestrator.

**Smoke discriminator:** smoke at K=500 with 3 cleanup iters; if HOPFIELD recall@1 < 0.30 at K=500 smoke, the cleanup attractor isn't catching — debug iteration count + k-WTA threshold before dispatch.

---

## What I'm NOT recommending

- Going back to v2 isolated-bank: USER directive was BUNDLED capacity test; isolated-bank doesn't address the question.
- Pushing XOR-bind to higher N: Angle A math says K_max ≤ 3 for sparse-XOR REGARDLESS of N. Scaling N won't fix it.
- Block-sparse bind (Frady 2020): more architectural complexity than substrate currently supports; revisit if TOP-1 + TOP-2 both fail.

---

## Falsifiable cross-angle prediction (single number)

**At K=500, N=2048, k=20, single seed, BUNDLED regime:**
- v3 XOR-bind: recall@1 ≤ 0.02 (already observed pattern)
- v4 PERM_TONEGAWA (TOP-1): recall@1 ≥ 0.55
- v5 HOPFIELD (TOP-2): recall@1 ≥ 0.40 (cleanup-limited)
- PROTO_BUNDLED: recall@1 ≤ 0.20 (dense bundle saturates)

If v4 PERM_TONEGAWA delivers < 0.30 at K=500: the substrate has a deeper sparse-code-handling gap than this drill identifies; escalate to USER.

If v4 delivers ≥ 0.55: chain-grade evidence for permutation-bind as the substrate's canonical sparse-code binder; deprecate XOR-bind for sparse regimes; update hdlab/ primitive.

---

## Self-test (lit-scan calibration penalty applied)

- Raw P(TOP-1 HARD_PASS at K=500): 0.65 (two independent angles converge + Plate-permutation 25-year track record)
- After calibration penalty (-0.20 for novel-synthesis combining permutation-bind + Tonegawa-style ensemble in our substrate): **P = 0.45**
- Capped at 0.50 per novel-synthesis ceiling: **P = 0.45 (final)**

- Raw P(TOP-2 HARD_PASS at K=2000): 0.55 (Treves-Rolls is solid theory but Hopfield cleanup adds implementation risk)
- After penalty (-0.20): **P = 0.35**

Combined P(at least one of TOP-1/TOP-2 HARD_PASS): ≈ 0.65 (independence assumption; correlated failures via shared sparse-code substrate would bring this to ≈ 0.55).

## Artifacts to ship next (research lane)

1. This drill (filed)
2. atomize 3-4 cert atoms: (a) XOR-bind incompatibility with k-WTA at K > 3, (b) permutation-bind as substrate canonical for sparse, (c) Hopfield attractor as biological-fidelity alternative, (d) Treves-Rolls crossover formula
3. update `data/director_plan.json` priority: TOP-1 v4_permutation_bundled cell-author handoff
4. spawn hdi_exp_dev for v4 cell-authoring with pre-reg sketch above
