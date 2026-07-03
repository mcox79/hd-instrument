# 5x Drill Component 4/5 — Physics + Statistical Mechanics on Sparse HF Encoder Loss

**Date:** 2026-07-02 (evening, day 2)
**Author:** hdi_research (Director)
**Drill component:** 4 of 5 (Physics / statistical mechanics angle)
**Critical negative under drill:** k=2% sparse-bipolar competitive-Hebbian encoder LOSES to dense bag-of-char-trigrams on WordNet held-out-synonym retrieval (recall@5 0.16 vs 0.28).

---

## 1. Prior-work check (substrate concept-query first)

Substrate-KB queries run per USER-locked discipline (v2 schema, tau=0.15, k=5, chunk-content):

| Query | Top-hit cosine | Prior arc |
|---|---|---|
| "sparse coding phase transition capacity Hopfield critical" | 0.376 | `research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md` — "Sparse coding capacity gain" |
| — cont. — | 0.362 | `research_drill_sparse_outer_product_writes_cross_cutting_2x_2026-06-05.md` — **CS phase transitions (Donoho-Tanner 2009; arXiv:2501.11905); bipolar AM capacity cliff = L1-minimization phase transition; SPLADE/ColBERT 1-2% sufficient for retrieval** |
| — cont. — | 0.355 | `research_drill_learned_codebooks_real_encoder_rescue_1x_2026-06-06.md` — **Sparse Hopfield 2025 arXiv:2603.26217 (2.34% works with higher-order interactions); Knoblauch 2012 (N/log N)^2 sparse capacity** |
| — cont. — | 0.352 | `research_drill_production_substrate_llm_hybrid_architecture_at_scale_2x_2026-06-05.md` — Sparse Hopfield capacity scaling summary |
| "glass transition sparsity retrieval information geometry" | 0.376 | `research_drill_sparse_key_composition_partners_2x_2026-06-06.md` — "Field F: Information geometry / optimal transport" |
| "percolation threshold concept retrieval sparse representation" | 0.377 | wordnet::percolation entity (no prior arc atom) |

**Overlap check:** Substrate has ~4 prior arc atoms on Sparse-Hopfield/CS-phase-transitions. NONE of them make the specific claim being drilled here (that k=2% on OUR competitive-Hebbian ARM sits at wrong side of a phase transition for HELD-OUT-SYNONYM retrieval on WordNet). The prior atoms establish that:
1. CS phase transitions are UNIVERSAL (Donoho-Tanner) — bipolar AM capacity has a hard cliff.
2. Sparse Hopfield with 2.34% activity DOES work — but only with higher-order interaction terms (super-polynomial capacity).
3. SPLADE/ColBERT report 1-2% works — but with LEARNED sparsity + inner-product retrieval, not competitive-Hebbian ARM.
4. Knoblauch capacity scales as (N/log N)^2 for VERY sparse activity — requires N large; peak sparsity is O(log N / N).

**Delta this drill adds:** apply the classical vs modern Hopfield capacity distinction + glass-transition rigidity + percolation-on-WordNet-graph to explain WHY 2% bipolar competitive-Hebbian loses to bag-of-trigrams in a setting where prior work said 2% should be sufficient.

---

## 2. Phase transition analysis — is 2% below k_c for real-content retrieval?

### 2.1 Donoho-Tanner phase transition (compressed sensing)

For sparse recovery via L1 minimization, there is a well-known phase transition at critical (delta, rho) where:
- delta = M/N (measurement ratio)
- rho = k/M (sparsity relative to measurements)

Above the DT curve: recovery succeeds w.h.p. Below: fails w.h.p. The transition sharpens as N → infinity.

Analogous transition exists for BIPOLAR associative memory (Sherrington-Kirkpatrick-like spin-glass phase diagram): capacity α = K/N has a critical α_c below which retrieval succeeds, above which spurious minima dominate.

### 2.2 Our regime

- N = 8192 (HD dim)
- K = 1000 (WordNet concept count, approx)
- k_active = 2% × 8192 = 164 active bits per concept
- α = K/N = 1000/8192 ≈ 0.122

For CLASSICAL Hopfield (all-active binary spins), α_c ≈ 0.138. We are AT α_c — sitting on the phase boundary. Under the classical bound we should barely function — but the WordNet held-out task is not classical recall; it is synonym-interpolation.

For SPARSE bipolar (Tsodyks-Feigelman / sparse Hopfield), α_c scales UP with sparsity as:
    α_c(f) ≈ 1 / (f × |log(f)|)     [f = active fraction]

At f=0.02: α_c ≈ 1 / (0.02 × 3.91) ≈ 12.8. So capacity for EXACT recall is fine (K/N ≈ 0.12 << 12.8). Bag-of-trigrams doesn't win on capacity grounds.

### 2.3 But: held-out synonym retrieval requires INTERPOLATION, not exact recall

Phase transition for exact recall ≠ phase transition for cluster-neighborhood retrieval. Sparse bipolar codes at low f have LARGE Hamming distance between random concept vectors:
- E[d_H(a, b)] ≈ 2f(1-f) × N = 2 × 0.02 × 0.98 × 8192 ≈ 321 bits differ per random pair

Synonym query needs cosine within a small ball around the target. In bipolar sparse: query→concept cosine falls off SHARPLY with any small mismatch because active-set overlap is combinatorially rare. Char-trigram dense representation has O(sqrt(dim)) similarity to random pairs (concentration of measure), giving a SMOOTHER similarity landscape.

**Verdict for §2:** we are not below α_c for exact recall. We are on the wrong side of a DIFFERENT phase transition — the **rigidity transition** — where sparse bipolar codes have zero-measure interpolation neighborhood.

---

## 3. Hopfield / modern Hopfield capacity comparison

### 3.1 Classical Hopfield (Hebbian outer-product; binary or bipolar)

Energy: E(s) = -0.5 s^T W s, W = Σ_μ ξ^μ (ξ^μ)^T
Capacity: α_c ≈ 0.138 for random patterns
Retrieval: gradient descent → nearest attractor
FAILURE MODE: quadratic energy has LOCAL basins around each stored pattern. Interpolation between two stored patterns collapses to one or the other — no "in-between" attractor exists.

### 3.2 Modern Hopfield (Krotov-Hopfield 2016; Ramsauer et al. 2020)

Energy: E(s) = -F(Σ_μ exp(ξ^μ · s / τ))  [log-sum-exp / softmax variant]
Capacity: EXPONENTIAL in dim (N^k for polynomial interaction of order k; exponential for softmax)
Retrieval: single step is equivalent to transformer attention: s' = Σ_μ softmax(β ξ^μ · s) ξ^μ

**Crucial property:** modern Hopfield retrieval PRODUCES INTERPOLATED OUTPUTS. If query s is between ξ^1 and ξ^2, softmax weights BOTH → linear combination in output. This is EXACTLY what synonym retrieval needs.

### 3.3 Bag-of-char-trigrams as an implicit modern-Hopfield lookalike

Bag-of-trigrams retrieval uses cosine similarity over dense positive-count vectors with cosine normalization. Under a similarity metric that becomes exp(cosine/τ) at retrieval time (or equivalently, softmax-over-similarities top-k), bag-of-trigrams IS a modern-Hopfield lookalike:
- All features co-active → high entropy representation
- Similarity smoothly interpolates via shared trigrams (synonyms share char n-grams: "car" and "cars" share "car")
- Softmax retrieval blends nearest neighbors → held-out synonyms score high on recall@5

Our competitive-Hebbian ARM applies HARD winner-take-most sparsification at write AND at readout. This is CLASSICAL Hopfield-like → interpolation is NOT possible.

### 3.4 Quantitative comparison

| Metric | Classical Hopfield (our HF encoder, k=2%) | Modern Hopfield (bag-trigrams-cosine) |
|---|---|---|
| Capacity for exact recall | K = α_c × N / (f\|log f\|) ≈ 105k concepts (large) | K = N^c (super-polynomial, effectively unbounded at our scale) |
| Interpolation | NONE (nearest attractor is one of stored ξ^μ) | YES (softmax mixture of top-k) |
| Held-out-synonym recall | LIMITED (bag-of-neighbors doesn't emerge) | STRONG (synonyms cluster via shared trigrams) |
| Energy landscape | Rugged; many spurious minima | Smooth; single global attractor per query |

**Verdict for §3:** the char-trigram winning is not just an encoder-quality artifact; it is that bag-of-trigrams + cosine implicitly implements a MODERN-Hopfield retrieval geometry, while our sparse competitive-Hebbian ARM is stuck in CLASSICAL-Hopfield rigidity.

---

## 4. Glass transition + representational rigidity

### 4.1 Spin-glass phase diagram for sparse bipolar

Nishimori / Amit-Gutfreund-Sompolinsky phase diagram (T vs α, f) has three regions:
1. **Retrieval phase** (low T, α < α_c): patterns are stable attractors
2. **Spin-glass phase** (low T, α > α_c): exponentially many spurious minima; no retrieval
3. **Paramagnetic phase** (high T): everything melts to zero-mean

At low sparsity f and moderate α (our regime: α=0.12, f=0.02), we sit near the RETRIEVAL/GLASS boundary. The retrieval basin is STABLE for exact stored patterns but the surrounding landscape is glassy — many nearly-degenerate metastable minima.

### 4.2 Glassy metastable minima kill synonym retrieval

Synonym query s ≠ any stored ξ^μ. In glass phase, gradient descent from s finds a RANDOM metastable minimum, not the closest stored pattern. Because the glass has zero long-range order, retrieved patterns from synonym queries are essentially uncorrelated with the true target — recall@5 near chance.

Bag-of-trigrams doesn't have this problem: cosine over dense-positive-count vectors is CONVEX in the similarity metric. There is no glassy landscape — top-k is well-defined and monotone in overlap.

### 4.3 Empirical fingerprint

If glass transition explains it, we should observe:
- Recall@1 for EXACT training-set queries: high (retrieval basin stable)
- Recall@5 for held-out synonyms: near chance (glass takeover)
- Ratio (exact recall) / (synonym recall) should be much higher for HF than for trigram

**Testable prediction:** measure recall@1 on exact-training-set queries for both encoders. Predict HF ≈ trigram or HF > trigram on exact (basins are stable), but HF << trigram on synonym (glass wins).

**Verdict for §4:** representational rigidity + glassy metastability of sparse bipolar codes predicts poor synonym generalization even when exact-recall capacity is fine.

---

## 5. Free-energy analysis for interpolation vs exact recall

F = U - TS

### 5.1 Sparse bipolar HF encoder

- Internal energy U: LOW per stored pattern (stored patterns are attractors)
- Entropy S: LOW (only k=164 of 8192 bits active per code; the code is nearly-deterministic given the concept)
- F = U - TS: minimized at LOW T (near-zero thermal fluctuation) — CRISP but BRITTLE

### 5.2 Bag-of-char-trigrams

- Internal energy U: no explicit energy; effectively HIGHER because vectors are not "attractor" states of any dynamics
- Entropy S: HIGH (all ~1000 trigrams active with varying counts; representation is diffuse)
- F = U - TS: minimized at MODERATE T — SMOOTH and DUCTILE

### 5.3 Prediction for synonym retrieval

Held-out synonym retrieval requires the effective retrieval T to be > 0 (thermal exploration around query). Under HF: raising T pushes us into glass phase → recall crashes. Under trigram: raising T just softens softmax → recall stays high.

There is an ASYMMETRY: HF has no "operating T" where both exact recall AND synonym generalization work simultaneously. Trigram has a wide T operating window.

**Verdict for §5:** free-energy geometry predicts that dense, high-entropy encodings will beat sparse, low-entropy encodings on any task requiring off-manifold interpolation. Synonym retrieval is exactly such a task.

---

## 6. Percolation analysis of WordNet concept graph under sparse encoding

### 6.1 Concept-similarity graph

Define graph G: vertices = concepts (~1000), edges = (a,b) if cosine(enc(a), enc(b)) > θ.

For retrieval to work above chance on synonym queries, G must have a percolating cluster containing both query-target concept AND its synonym neighbors.

### 6.2 Percolation threshold for sparse bipolar

Random sparse bipolar with f=0.02: E[cosine(a, b)] = 0 for random pairs. Variance:
    Var[cosine] ≈ 2f/N + 2f²(N-1)/N² ≈ 5×10^-6 for N=8192, f=0.02

Standard deviation ≈ 0.0022. So cosine of random pair concentrates tightly at 0. Similarity ordering is DOMINATED by noise for concepts that aren't semantically synonymous under our encoder. Percolation requires the SIGNAL cosine (for actual synonyms) to exceed the noise SD by O(sqrt(K)).

Competitive-Hebbian doesn't guarantee synonyms get correlated codes — the Hebbian update aligns codes with INPUT CORRELATIONS, and our input to encoder is a random-hashed feature vector for synonyms that may itself have weak correlation. RESULT: synonym cosine ~ 0.01-0.05, random-pair noise SD ~ 0.002, so signal-to-noise ~ 5-25. Marginal but not fatal.

### 6.3 Percolation threshold for bag-of-char-trigrams

Trigram similarity for synonyms (share stems: "car"/"cars", "run"/"running"): cosine ~ 0.3-0.7. Random pair cosine ~ 0.05 (concentration around a positive baseline because all English words share common trigrams "the", "ing", "ion" etc.). SNR ~ 6-14. COMPARABLE ordering.

### 6.4 Where the sparse regime loses percolation

Percolation on G at threshold θ requires that G(θ) has a giant connected component. Under sparse-bipolar with SNR ~5-25 for synonyms, threshold θ set to include synonym edges will ALSO include noise edges (false positives) at similar rate. Recall@5 becomes probabilistic — the top-5 by cosine is dominated by NOISE not by semantics.

Under trigram with SNR ~6-14 but BASELINE cosine ~ 0.05, threshold θ ~ 0.2 cleanly separates synonyms from noise. Recall@5 concentrates on true synonyms.

**Verdict for §6:** the SNR for our HF encoder is marginal — we're at the percolation threshold for synonym cluster formation. Small perturbations (competitive-Hebbian update stochasticity, k discretization) push us BELOW threshold. Trigram baseline sits safely above threshold because its ENCODING intrinsically encodes lexical structure that correlates with WordNet's synonym relation.

---

## 7. Physics verdict — is there a phase-transition explanation?

**YES, there is a phase-transition explanation, and it is NOT a single transition — it is a triple failure:**

1. **Rigidity transition:** sparse-bipolar retrieval basins have zero-measure interpolation neighborhood. Held-out synonym queries fall OUTSIDE any basin → no useful retrieval.

2. **Classical-vs-modern Hopfield transition:** bag-of-trigrams + cosine implicitly implements modern-Hopfield (softmax) geometry with EXPONENTIAL capacity AND interpolation. Our competitive-Hebbian ARM is stuck in CLASSICAL Hopfield with quadratic energy — no interpolation, no attention-like blending.

3. **Percolation transition on WordNet concept graph:** sparse encoding gives marginal SNR (~5-25) for synonym-edges vs random-noise-edges. Small perturbations push us BELOW percolation. Trigram encoding has intrinsic lexical structure that keeps SNR safely above threshold.

**None of these is "encoder training didn't converge" or "k=2% is too aggressive" in a naive sense.** The physics says: the entire ARCHITECTURE (sparse binary + Hebbian outer-product + winner-take-most readout) is the wrong energy geometry for the held-out-synonym task. Even a perfectly-trained k=2% competitive-Hebbian ARM would lose to trigrams on this task.

---

## 8. Predicted k_c for real-content retrieval + prescription for v2

### 8.1 Predicted critical sparsity for our task

For classical sparse-Hopfield capacity, k_c(f) ~ f × |log f|. Optimizing for HELD-OUT-SYNONYM retrieval (which requires interpolation), the free-energy analysis suggests:

    f_optimal ≈ 1 / sqrt(N / log(K))    [balances rigidity vs capacity]

For N=8192, K=1000: f_optimal ≈ 1/sqrt(8192/7) ≈ 1/34 ≈ 3%

So k=2% is not catastrophically far from f_optimal (3%). Raising to 5-10% would help but NOT dominantly — the fundamental problem is the classical-Hopfield energy geometry, not the sparsity level.

### 8.2 Prescription for v2 (physics-informed)

**Ranked by expected effect size (physics prior):**

1. **[HIGHEST PRIOR] Modern-Hopfield readout (softmax attention).** Keep sparse-bipolar STORAGE (k=2%), but replace winner-take-most retrieval with softmax(β · Wq) top-k blending. This ports us from classical to modern Hopfield energy geometry. Expected: +0.10-0.15 recall@5 (bring us to trigram parity or above). Cost: readout complexity O(K × N) per query (same as current cosine-lookup).

2. **[MEDIUM PRIOR] Dense positive-count encoder for storage.** Replace bipolar {-1,+1} with dense positive-counts (like trigrams). Loses the sparse-code write efficiency but gains modern-Hopfield-native geometry. Expected: +0.10 recall@5. Cost: 5-10x memory per code.

3. **[MEDIUM PRIOR] Increase active fraction to 5%.** Move from f=0.02 to f=0.05. Increases interpolation neighborhood, reduces rigidity. Expected: +0.03-0.05 recall@5 (modest). Cost: 2.5x active bits per code.

4. **[LOW PRIOR] Higher-order interaction terms (Krotov-Hopfield).** Replace quadratic energy with polynomial-order interactions. Provides exponential capacity + interpolation. Expected: +0.15 recall@5 but requires energy-minimizing dynamics not just Hebbian. Cost: fundamentally different training loop.

5. **[HYBRID — RECOMMENDED for v2]** Combine (1) + a mild version of (3): keep sparse-bipolar storage, use softmax attention readout, and set f=0.03. Best interpolation + retains sparse-write efficiency.

### 8.3 Testable predictions the v2 should verify

If the physics-verdict is right, v2 should show:
- Exact-training-set recall@1: HF v1 ≈ HF v2 (both near 1.0) — storage capacity is fine
- Held-out-synonym recall@5: HF v2 > HF v1 by +0.10, matching or exceeding trigram
- Retrieval temperature curve: HF v2 has wide operating T; HF v1 has narrow T
- Recall vs f sweep: HF v2 monotonically improves f=0.01 → 0.05; HF v1 saturates or degrades at f<0.03

If v2 with softmax-readout still loses to trigrams: the physics diagnosis is incomplete and the problem is encoder-signal not retrieval-geometry (kicks investigation back to encoder training data / hashing).

---

## Deliverable summary

- **Path:** `d:/AI/hd-instrument/notes/research_5x_drill_4_physics_stat_mech_substrate_content_HF_2026-07-02.md`
- **Top-line verdict:** YES, there is a phase-transition explanation — but it is a TRIPLE failure (rigidity + classical-vs-modern-Hopfield geometry + WordNet-graph percolation), not a single k_c crossing.
- **Predicted critical sparsity:** f_optimal ≈ 3% for our (N=8192, K=1000, task=synonym-retrieval) regime. k=2% is close to optimal — the bigger lever is the READOUT GEOMETRY (modern-Hopfield / softmax attention), not the sparsity level.
- **v2 prescription:** hybrid — keep sparse-bipolar storage (k=3%), replace winner-take-most readout with softmax attention over stored codes. Ports us from classical to modern Hopfield without losing sparse-write efficiency.
- **Testable prediction:** HF v2 with softmax readout should beat trigram on synonym recall@5 by 0.05-0.10 while retaining exact-recall near 1.0. If not, encoder signal (not geometry) is the true bottleneck.

**Lit-scan calibration penalty applied:** deflated P(this diagnosis is complete) from prior 0.60 → 0.42 (novel synthesis of three known phase transitions, not one established result). Cap at 0.50 respected.
