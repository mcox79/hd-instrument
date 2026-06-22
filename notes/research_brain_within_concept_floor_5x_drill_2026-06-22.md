# RESEARCH 5x DEEPER DRILL: Within-concept token-entropy floor — brain/biology/nature mechanisms for substrate-native LMs

**Date:** 2026-06-22
**Requestor:** Skunkworks (USER-directed novel-synthesis drill)
**Empirical driver:** n2 capacity_scaling MIDDLE_BAND + n3 SimVQ MVP HONEST_NEGATIVE → bigram-gap (1.12 bits) confirmed DECODE-SIDE; substrate-vs-ceiling gap ~2.9 bits at every PROJ_DIM. MKN smoothing + Path A V_C=4096 are live shots; if both miss, NEW mechanism intuition needed from neuroscience.
**Lit-scan calibration:** deflate P 0.15–0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE

**The substrate is operating at the WRONG coding sparsity for biological-analogue pattern completion.** Cerebellum and mushroom body use **expansion-coding sparse readout at f ≈ 0.05–0.10** (Marr-Albus, Litwin-Kumar 2017). The substrate uses **hard one-hot VQ at f = 1/V_C ≈ 1/1024 ≈ 0.001** — 50–100× sparser than the optimum that biological circuits converged on for high-fidelity decode under energy constraints. Hard one-hot VQ destroys the **pattern-completion** structure CA3 uses to lower conditional entropy: instead of asking "what token follows concept-c?" the brain asks "what token follows {c1, c2, c3, ... ck}" — a soft top-k overlapping code.

**The novel mechanism: TOP-K SOFT CONCEPT READOUT (kWTA-VQ) with overlap-decode at INGEST time.** Replace the hard `km.predict()` → single-concept assignment with **top-k softmax assignment** (k=8–32) and accumulate the decode matrix D over the top-k concepts (Hebbian-weighted by similarity). At test time, decode reads from the top-k concept rows (same kWTA), summed and renormalized. **No backprop. No new architecture. Same V_C, same N_DIM. Just a `k > 1` knob on both write and read paths.**

| Mechanism | Source | Substrate-applicability | Cost | Expected gain | P(HARD-PASS) |
|-----------|--------|--------------------------|------|---------------|--------------|
| **kWTA-VQ top-k soft assignment (novel synthesis)** | Cerebellum granule cell expansion (Marr/Albus/Litwin-Kumar); CA3 pattern completion (Rolls); mushroom body sparse Kenyon (Modi/Stevens) | **HIGHEST** — forward-only Hebbian, fits hd-instrument decode pipeline as a 2-line change | ~1.05× wall (k-fold accumulate) | 0.3–0.7 BPC | **0.40** (cap @ novel-synthesis) |
| Hippocampal episodic trace (CA1-style 2nd-pass lookup) | McClelland/O'Reilly/Norman CLS; Rolls CA3 pattern completion | MEDIUM — needs episodic-store mode (additive to substrate) | ~1.5× wall (test-set NN lookup) | 0.1–0.4 BPC | 0.30 |
| Conditional-entropy-regularized VQ (EM soft assign) | Variational IB on VQ-VAE (1808.01048); information bottleneck (Tishby) | MEDIUM-LOW — soft EM is slower; not a 2-line drop-in | ~2× wall | 0.2–0.5 BPC | 0.30 |
| Predictive-coding hierarchical decode | Rao-Ballard, Bastos, Friston | LOW — requires backprop / iterative gradient descent over decode-layer | infeasible without backprop | n/a | rejected |

**Cheap decisive test:** `n4_kwta_soft_decode_v1` — Sweep k ∈ {1, 4, 8, 16, 32} at V_C=1024, N_DIM=16384, K=1. **HARD-PASS bar: ceiling_bpc ≤ 1.75 AND substrate_bpc ≤ 4.75 at some k ∈ [4, 32]. HARD-FAIL: best ceiling change < 0.05 bits across all k.**

---

## L1 — LITERATURE BROAD SCAN (4 parallel streams)

### Stream A: Predictive coding (hierarchical inference)
- **Rao & Ballard 1999 + Friston 2005 + Bastos 2012:** cortex implements hierarchical variational inference; top-down predictions, bottom-up errors. Mathematically equivalent to backprop along arbitrary graphs (arxiv 2006.04182). **Verdict:** requires iterative gradient propagation — incompatible with substrate's forward-only Hebbian write-once design.
- **2024–2026 extensions:** spiking + gist signaling (Frontiers 2024.1338280); semantic+episodic memory in PC model (arxiv 2509.01987). **Verdict:** still backprop-adjacent.

### Stream B: Complementary Learning Systems (CLS)
- **McClelland/McNaughton/O'Reilly 1995, O'Reilly 2014:** brain factors learning into TWO systems — hippocampus (sparse, pattern-separated, fast, episodic) + cortex (distributed, slow, semantic). Wake-sleep replay consolidates hippocampus → cortex (arxiv 2401.08623, 2104.04132).
- **Key insight for substrate:** the substrate is currently a PURE cortex (slow distributed Hebbian write into D). Adding a hippocampus-style episodic side-channel at decode time could lower within-concept entropy WITHOUT touching the cortex side.
- **Mechanism for substrate:** at test time, on top of the existing concept-based decode, ALSO look up the K-nearest TRAINING residuals (not concepts — actual stored residuals) and use their direct next-token observations as an extra evidence stream. Combine via log-linear or learned weight.

### Stream C: Sparse distributed representations (cerebellum / Kenyon / dentate gyrus)
- **Marr 1969 / Albus 1971:** cerebellum granule cells are an EXPANSION CODE — M=209k mossy fibers → N=7M granule cells, K=4 sparse inputs per granule, **coding level f ≈ 0.05–0.10** (5–10% active).
- **Litwin-Kumar 2017 (Neuron):** OPTIMAL synaptic input degree K=4; representation DIMENSION (Schur-Hadamard expansion of input correlation) saturates at expansion ratio ~30 with f≈0.1. **Sparser than f≈0.05 introduces noise; denser destroys separability.**
- **Mushroom body (Modi/Stevens 2020):** Kenyon cells 5–10% active per odor, ~7 random PN inputs, deterministic kWTA via anterior paired lateral (APL) inhibition.
- **Dentate gyrus (Cayco-Gajic & Silver 2019):** granule cells implement pattern separation via sparse + expansion; CA3 then pattern-COMPLETES via recurrent collaterals.
- **Verdict:** the substrate is at f ≈ 1/V_C ≈ 0.001 (HARD one-hot) — 50–100× too sparse. The optimum coding level for high-fidelity pattern-completion decode is f ≈ 0.05–0.10, which translates to top-k = f·V_C ≈ 50–100 of 1024 concepts active per residual.

### Stream D: Information bottleneck for VQ
- **Tishby 2000, Achille-Soatto 2018:** the IB objective is min I(X;Z) − β·I(Z;Y). For substrate, X=residual, Z=concept, Y=next-token. Hard one-hot VQ has H(Z|X)=0; the **soft assignment EM-VQ (arxiv 1808.01048) INJECTS conditional entropy H(Z|X)** and provably improves the IB tradeoff.
- **Direct relevance:** the n3 SimVQ HONEST_NEGATIVE used PCA-init linear projection but KEPT hard nearest-neighbor assignment. The actual lever is the **assignment softness**, not the projection.

---

## L2 — FILTER TO SUBSTRATE-APPLICABLE

| Mechanism | Forward-only? | Composes with V_C × N_DIM? | Same Hebbian-write semantics? | Verdict |
|-----------|---------------|----------------------------|-------------------------------|---------|
| **Top-k soft kWTA-VQ (cerebellum/Kenyon analogue)** | YES | YES (knob on existing pipeline) | YES (just write to top-k rows of D, similarity-weighted) | **ACCEPT — top candidate** |
| Hippocampal episodic 2nd-pass lookup | YES (NN search) | YES (additive at decode) | NO (new memory store but Hebbian-compatible) | ACCEPT — secondary |
| Conditional-entropy-regularized EM VQ | YES (EM converges by iteration; no backprop) | YES | NO (EM at ingest; rewrites D) | ACCEPT — tertiary |
| Predictive coding hierarchical decode | NO (gradient needed) | n/a | n/a | REJECT |
| Wake-sleep replay / consolidation | YES but EXPENSIVE | needs second pass over data | NO | DEFER (composition not enabling) |

---

## L3 — DEEP DRILL ON TOP 1–2 MECHANISMS

### 3.1 Top-K soft kWTA-VQ (PRIMARY)

**Biological capacity bound (Litwin-Kumar 2017, Neuron):** for an expansion code with M inputs, N output cells, K synapses per cell, coding level f, the EFFECTIVE DIMENSION (which bounds linear separability and downstream learning capacity) follows roughly:
```
dim_eff ≈ N · f · (1−f) · g(K, input_correlation)
```
where g(K, ·) saturates around K=4 for typical biological correlation. The **optimum is at the f that maximizes f·(1−f) given the constraint that f·N ≥ k_active is feasible** — empirically f ≈ 0.05–0.10.

**Mapping to substrate:**
- Substrate's "output cells" = V_C = 1024 concepts.
- Current "coding level" = 1/1024 ≈ 0.001 (one concept active per residual).
- **Litwin-Kumar predicts optimum coding level f* ≈ 0.05–0.10 → k_active ≈ 50–100 of 1024 concepts active per residual.**
- The dimension boost is roughly proportional to f·(1−f) increase from 0.001·0.999 ≈ 0.001 to 0.10·0.90 = 0.09 → **~90× effective-dimension gain at the soft-readout layer.**

**Why this lowers ceiling_bpc:**
- Ceiling_bpc = H(token | concept) where concept is a single hard cluster ID.
- Under top-k soft readout, the per-position decode is H(token | top-k concepts, weights). By data-processing inequality this is ≤ ceiling_bpc (no information lost; more conditioning).
- The within-set token distribution SHARPENS because tokens that are FREQUENT in one nearby concept get supporting evidence from neighbors; tokens that are CONCEPT-SPECIFIC get reinforced; tokens that are ARTIFACTS of single-cluster overfitting get washed out.
- This is mechanically the SAME math as **Modified Kneser-Ney's continuation distribution** but built into the assignment layer instead of the smoothing layer — and the two compose.

**Mechanism detail — write path:**
```python
# Current (one-hot)
c = km.predict(residual)          # int in [0, V_C)
D[c, token] += 1                  # Hebbian write to one row

# Proposed (top-k soft)
dists = ((centroids - residual)**2).sum(-1)
top_k = np.argsort(dists)[:k]                          # k nearest concepts
w = softmax(-dists[top_k] / tau)                       # similarity weights, sum to 1
for ci, wi in zip(top_k, w):
    D[ci, token] += wi                                 # Hebbian write, similarity-weighted
```

**Mechanism detail — read path:**
```python
# Current (one-hot)
c = km.predict(query_residual)
logp = log(D[c] / D[c].sum() + eps)

# Proposed (top-k soft, same as write)
top_k, w = soft_assign(query_residual, centroids, k, tau)
pooled = (D[top_k] * w[:, None]).sum(axis=0)           # weighted sum of k rows
logp = log(pooled / pooled.sum() + eps)
```

Substrate-only-decode gate: PRESERVED. Zero LLM forward calls. Pure numpy. Wall-time overhead ≈ k× the matmul (negligible at k=32 against the 768-dim residual cost).

### 3.2 Hippocampal episodic 2nd-pass lookup (SECONDARY)

**CLS mechanism (McClelland 1995, O'Reilly 2014, Rolls CA3 review 2013):**
- Cortex (slow, distributed) = the current substrate concept-decode (D matrix).
- Hippocampus (fast, episodic) = a separate KEY-VALUE store of `(residual_train, next_token)` pairs.
- At decode: query the cortex (D row for concept-c) AND query the hippocampus (k nearest train residuals; their direct next-token observations); combine.

**Why this works:** when a residual lands in a high-entropy concept cluster, the cortical decode is near-flat → no information. But the K nearest training residuals (in raw space) often have a much sharper next-token distribution — they're "this exact context appeared in training, the next-token was X". This is RAG for substrate decode.

**Capacity:** episodic store size = N_train tokens; at decode, k-NN over residuals_per_token. Compute: brute-force on ~35k × 768 = fast (sub-second per query batch on CPU); FAISS for scale.

**Caveat:** this is closer to LLM-style retrieval than substrate-native; it adds memory cost (store all train residuals + tokens). Substrate-only-decode gate still passes (no LLM forward calls).

---

## L4 — CELL-DESIGN IMPLICATIONS + PRE-REG

### Primary cell: `n4_kwta_soft_decode_v1` (top-k soft kWTA-VQ)

**Scope:** Replace hard `km.predict()` with top-k softmax assignment. Apply to BOTH write (D accumulation at ingest) and read (D row pooling at decode). Sweep k.

**Independent variable:** k ∈ {1, 4, 8, 16, 32, 64}; tau ∈ {0.5, 1.0, 2.0} (softmax temperature; secondary sweep at best-k).

**Fixed:** V_C=1024, N_DIM=16384, K=1 (depth), residuals_per_token corpus (same as N2/n3), 3 seeds (7, 17, 23).

**Anchor:** k=1 case must reproduce N2 V_C=1024/N=16384/K=1 baseline ceiling=2.0491 ± 0.02 → if not, harness is corrupt.

**Primary metric:** ceiling_bpc (oracle decode floor) — same as n3.

**Secondary metrics:** substrate_bpc; codebook_utilization (now soft — measure effective entropy of the WRITE accumulator); per-concept token-distribution entropy; depth_token_gain at K=2 (composed in a follow-on).

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade, mechanism validated):**
- ceiling_bpc(best-k) ≤ 1.75 (≥ 0.30 bits improvement from 2.049)
- substrate_bpc(best-k) ≤ 4.75 (≥ 0.21 bits improvement from 4.959)
- cv ≤ 0.05 across seeds
- substrate-only-decode gate: zero LLM calls (grep audit + counter assertion)
- monotonic-in-k OR clear plateau: best-k must be in [8, 64], NOT k=1 (else it's a noise-only effect)

**HARD-PASS-PLUS (super-pass):** substrate_bpc < bigram_bpc = 3.844 at some k.

**MIDDLE_BAND (proven bound, partial mechanism):**
- ceiling_bpc drop ∈ [0.10, 0.30] bits at some k

**HARD-FAIL (mechanism wrong):**
- best ceiling_bpc change across all k < 0.05 bits → kWTA-VQ is NOT the decode-side mechanism; route to Path A or hippocampal lookup
- OR ceiling_bpc gets WORSE monotonically with k → soft averaging is destructive at this V_C (analogous to f >> 0.1 regime)

**Discriminating-regime requirement (C5):** the CAN-fail regime is k=1 (= current N2 baseline, must replicate exactly) AND k=V_C=1024 (= uniform pooling, should be near-unigram entropy). Both endpoints provide a sanity bracket.

**Version-marker requirement:** metrics.json must include `assignment_mode: 'top_k_soft'`, `k_value`, `tau`, `effective_coding_level = k/V_C` — to prevent the n3-class anchor-confusion (a different cell mis-cited as the baseline).

### Compute cost
- ~35–45 min on remote_cpu_queue per k value (similar to n3; the extra cost is k× row writes + k× row reads at decode).
- 6 k values × 3 seeds = 18 runs ≈ 12–14 hr remote_cpu. Or do {1, 8, 32} = 3 k values × 3 seeds = ~3.5 hr.
- **Recommend phased:** Phase 1 ship k ∈ {1, 8, 32} (3 k values × 3 seeds, ~3.5 hr) → if any k beats HARD-PASS bar, Phase 2 ships {4, 16, 64} for resolution.

### Composable follow-on (after n4 lands)
1. **n4 + MKN compose:** apply MKN smoothing on top of soft-kWTA decode. P(additional 0.05–0.15 BPC) ≈ 0.45 if n4 lands HARD-PASS.
2. **n4 + K=2 depth compose:** verify the n2-discovered "floor-masked depth gain" surfaces once the floor drops. Free piggyback (no extra cell).

### Secondary cell (CONDITIONAL on n4 HARD-FAIL): `n5_hippocampal_episodic_v1`
**Scope:** keep substrate decode unchanged; ADD a k-NN lookup over training residuals at decode time; combine via log-linear weight λ.
**Independent variable:** λ ∈ {0.0, 0.25, 0.5, 0.75, 1.0}; k_NN ∈ {8, 32, 128}.
**Pre-reg HARD-PASS:** substrate_bpc drop ≥ 0.30 bits at some (λ, k_NN).
**Pre-reg HARD-FAIL:** drop < 0.05 across all.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — kWTA-VQ lowers ceiling_bpc
**Hypothesis:** top-k soft kWTA-VQ at k* ≈ 50–100 (coding level f* ≈ 0.05–0.10) lowers ceiling_bpc by ≥ 0.30 bits at V_C=1024, N_DIM=16384, K=1.
**Mechanism:** soft assignment lifts the substrate from f=0.001 (hard one-hot, sub-optimal per Litwin-Kumar) to f≈0.05 (cerebellum/Kenyon optimum), expanding effective decode dimension ~90× and lowering H(token | top-k concepts) by data-processing inequality + sharpening of pooled distribution.
**HARD-PASS:** ceiling_bpc(best-k) ≤ 1.75.
**HARD-FAIL:** ceiling_bpc(best-k) change < 0.05.
**Calibrated P(HARD-PASS): 0.40** (capped at novel-synthesis ceiling 0.50; deflated 0.10 because: novel combination of biological mechanism + substrate primitive; the Litwin-Kumar optimum was derived for sensorimotor inputs, not LM-residual inputs; unsupervised k-means centroids may not be the right "granule cells" — but the directionality (f=0.001 too sparse) is robust).

### Prediction 2 (SECONDARY) — Optimal k is in the f≈0.05–0.10 band
**Hypothesis:** the best-k will land in k ∈ [32, 128] (f ∈ [0.03, 0.125]), bracketing the cerebellum/Kenyon biological optimum, NOT at k=1 (current) or k=V_C (uniform).
**HARD-PASS:** best-k ∈ [32, 128] AND ceiling improves over k=1 by ≥ 0.10.
**HARD-FAIL:** best-k = 1 (i.e., hard VQ is optimal — biological mapping fails).
**Calibrated P: 0.35** (independent prediction; bracketed by k=4 too-sparse + k=512+ too-dense; the SIGN of the effect — softer is better — is more confident than the exact optimum).

### Prediction 3 (CONDITIONAL on Prediction 1 PASSES) — depth K=2 surfaces post-floor-drop
**Hypothesis:** with floor dropped to ceiling_bpc ≤ 1.75, the n2-observed "floor-masked depth concept-gain" (+0.008 to +0.031) will propagate into a positive depth_token_gain at K=2.
**HARD-PASS:** depth_token_gain(K=2, best-k) ≥ +0.05 bits (currently −0.03 to −0.12).
**HARD-FAIL:** depth_token_gain still ≤ 0 (then depth mystery is not just floor-masking; investigate concept-prediction quality at K=2).
**Calibrated P: 0.45.**

### Prediction 4 (NULLABILITY CHECK) — bracket sanity at k=V_C
**Hypothesis:** at k = V_C = 1024 with uniform weights, ceiling_bpc ≈ log2(V_TOK) − unigram_bpc + ε, i.e., recovers unigram-level entropy.
**Purpose:** confirms the math is right; if k=1024 doesn't degrade to unigram, the implementation is buggy and the whole cell is INCONCLUSIVE.

### Prediction 5 (REVIVAL ROUTE if HARD-FAIL) — hippocampal episodic
**Hypothesis:** if n4 HARD-FAILs, the bottleneck is concept-PREDICTION (not within-concept entropy); then hippocampal 2nd-pass lookup (n5) becomes the evidence-warranted next mechanism.
**Pre-registered routing:** SAME-CYCLE Director note routing the negative (per USER STANDING rule) with revival angle "hippocampal episodic + Path A V_C scaling".

---

## CROSS-THREAD SYNTHESIS

### Composes with n3 SimVQ HONEST_NEGATIVE
- **n3 finding:** PCA-init projection BEFORE hard-VQ hurts (PD=64: −0.231 bits; PD=32: −0.426 bits). Linear projection threw away token-discriminating signal.
- **n4 distinction:** keeps the SAME 768-dim centroid space; only changes the ASSIGNMENT softness. There's no information-discarding projection. **The n3 negative does NOT bear on n4** — the levers are orthogonal.
- **n3 lesson absorbed:** unsupervised PCA-init projection has no LM-supervision signal. n4 also has no LM-supervision but uses MULTIPLICITY (k>1) instead of DIMENSIONALITY REDUCTION (d<768).

### Composes with n2 3-way knot
- n2 confirmed depth(K=2) doesn't surface in token-BPC because the floor masks it.
- n4 directly attacks the floor — if it works, the masked depth-gain surfaces "for free" (Prediction 3).
- This means n4 + K=2 is the **first joint-enabling composition** identified for the bigram-gap: VQ readout × depth coupling.

### Composes with Path A (V_C × N joint)
- Path A attacks within-concept entropy by SHRINKING clusters (more concepts).
- n4 attacks the same entropy by SOFTENING readout (overlapping clusters).
- These are MULTIPLICATIVE, not redundant: at V_C=4096 with k=8, effective coding level f = 8/4096 ≈ 0.002 — still in the sparse regime; the Litwin-Kumar optimum prescribes scaling k WITH V_C to maintain f ≈ 0.05–0.10. **At V_C=4096, optimal k ≈ 200; at V_C=16384, k ≈ 800.**
- **This reframes Path A entirely:** Path A is not "more concepts" — it's "more concepts AT THE SAME EFFECTIVE CODING LEVEL", which requires the kWTA framework first.

### Composes with MKN smoothing (n3 follow-on)
- MKN smooths the WITHIN-concept token distribution (one row of D at a time).
- n4 smooths ACROSS concepts (pooled rows of D, similarity-weighted).
- These are orthogonal smoothing axes. Both can compose multiplicatively.
- **Composition order:** n4 first (mechanistic floor drop), then MKN on top of pooled distribution (final residual entropy reduction).

### Composes with Hebbian-superposition #7 substrate-KV (CERT 591)
- The Hebbian-superposition value-cue→key alignment (CERT 591) operates in the **CONCEPT** layer, not the TOKEN layer.
- kWTA-VQ extends the same principle to the DECODE layer: instead of a hard concept-to-token map, a soft concept-cluster-to-token map.
- **Substrate principle emerging:** at EVERY layer (write, recall, decode), SOFT-OVERLAPPING readout beats HARD-DISJOINT readout, consistent with both the biological evidence (sparse-but-not-too-sparse) and the substrate's own internal mechanism (Hebbian superposition is by construction overlapping).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **kWTA-VQ is a substrate-wide PRIMITIVE, not just a decode lever.** Any place the substrate currently does hard one-hot VQ (concept assignment, intermediate clustering) is a candidate for soft top-k upgrade. If n4 lands, this becomes a refactoring opportunity across the substrate stack.

2. **Biological-coding-level is the new design rule.** Replace "V_C is the parameter" with "effective coding level f = k/V_C is the parameter, where f* ∈ [0.05, 0.10]". This unifies Path A (V_C×N) and Path B (decode-side k-sweep) under one knob.

3. **The cerebellum/Kenyon analogue is the substrate's natural prior.** The substrate IS an expansion-coding circuit (high-dim N_DIM W matrix, sparse hyperdimensional binding). Its decode layer should be expansion-coding-compatible too. Hard one-hot VQ violates this — a deviation from biology that has empirical cost.

4. **The CLS factorization opens a second axis.** If kWTA-VQ doesn't fully bridge the gap, the substrate can add a hippocampal episodic side-channel (n5). Either way, both mechanisms cite the SAME underlying biology, and both are forward-only and substrate-only-decode compatible.

5. **Re-framing of the depth mystery:** depth(K=2) WAS doing real work all along; the floor was just preventing it from showing. n4 closes the loop on the n2 finding — depth IS a valid lever, contingent on a soft-readout floor.

6. **Falsification value:** if n4 HARD-FAILs at the cerebellum-optimum k, it is genuine evidence that LM-residual VQ has DIFFERENT optimal sparsity than sensorimotor expansion coding. That itself is publishable-internal substrate knowledge — the biology analogue has limits.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (the path-forward map)

```
                            DECODE-SIDE GAP (1.12 bits, ~2.9 bits to ceiling)
                                            │
                ┌───────────────────────────┼───────────────────────────┐
                ▼                           ▼                           ▼
       n4 kWTA-VQ (NEW)              n3 SimVQ (DONE: NEG)        Path A V_C=4096
       coding-level lever            projection lever            granularity lever
       P(HARD-PASS) = 0.40           HONEST_NEGATIVE             P unknown (GPU)
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
   k=8 cheap  k=32     k=128 (probe Litwin-Kumar optimum)
        │
        ▼ (if HARD-PASS)
   ┌─────────────┴─────────────┐
   ▼                           ▼
n4 + K=2 depth         n4 + MKN smoothing
(free piggyback)       (orthogonal smoothing axis)
   │                           │
   └─────────────┬─────────────┘
                 ▼
        n4 + Path A (V_C=4096, k≈200)
        (the joint-enabling configuration; the cerebellum-scaled substrate)
                 │
                 ▼ (if HARD-PASS)
        FIRST BIGRAM-BEATING SUBSTRATE LM
        (HARD-PASS-PLUS bar at substrate_bpc < 3.844)
                 │
                 ▼
        Compose with Hebbian-superposition #7 (CERT 591)
        ⇒ glass-box-LLM foundation
```

**If n4 HARD-FAIL:**
```
n4 HARD-FAIL (kWTA-VQ not the mechanism)
    │
    └─→ ROUTE TO RESEARCH (USER STANDING rule)
        revival angle: n5 hippocampal episodic + Path A coupling
        + investigate WHY (concept-prediction layer, not decode)
```

---

## CITATIONS (verified, count = 14)

1. Marr, D. (1969). "A theory of cerebellar cortex." J. Physiol. 202(2): 437–470. (Foundational expansion-coding theory.)

2. Albus, J.S. (1971). "A theory of cerebellar function." Mathematical Biosciences 10: 25–61. (Independent rediscovery; sparse expansion + supervised readout.)

3. Litwin-Kumar, A., et al. (2017). "Optimal Degrees of Synaptic Connectivity." Neuron 93(5): 1153–1164. [Cell pdf](https://www.cell.com/neuron/pdf/S0896-6273(17)30054-5.pdf) [Semantic Scholar](https://www.semanticscholar.org/paper/Optimal-Degrees-of-Synaptic-Connectivity-Litwin-Kumar-Harris/24b82421b9337b1be267976733cefba7ab1ecca3). (K=4 optimal synapses; f≈0.1 optimal coding level; saturation curves.)

4. Xie, et al. (2023). "Task-dependent optimal representations for cerebellar learning." eLife 12:e82914. [eLife](https://elifesciences.org/articles/82914) [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10541175/). (Coding-level optimum is task-dependent; relevant for substrate's LM-task.)

5. Cayco-Gajic, N.A., Silver, R.A. (2019). "Re-evaluating Circuit Mechanisms Underlying Pattern Separation." Neuron. (Sparse + expansion + threshold for pattern separation across cerebellum/DG/MB.)

6. Modi, M.N., Shuai, Y., Turner, G.C. (2020). "The Drosophila Mushroom Body: From Architecture to Algorithm in a Learning Circuit." Annu. Rev. Neurosci. (Kenyon cell sparse 5–10% coding; APL inhibition implements kWTA.)

7. Rolls, E.T. (2013). "The mechanisms for pattern completion and pattern separation in the hippocampus." Frontiers in Systems Neuroscience 7:74. [Frontiers](https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2013.00074/full) [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3812781/). (CA3 autoassociative pattern completion; sparse distributed representation requirement.)

8. McClelland, J.L., McNaughton, B.L., O'Reilly, R.C. (1995). "Why there are complementary learning systems in the hippocampus and neocortex." Psychological Review 102(3): 419–457. (CLS foundational paper.)

9. O'Reilly, R.C. (2014). "Complementary Learning Systems." Cognitive Science. [CBMM](https://cbmm.mit.edu/sites/default/files/documents/Week3_O-Reilly2014.pdf) [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1551-6709.2011.01214.x). (Modern restatement; fast hippocampus + slow cortex factorization.)

10. Wu, H., et al. (2018). "Variational Information Bottleneck on Vector Quantized Autoencoders." arxiv 1808.01048. [arxiv](https://arxiv.org/pdf/1808.01048). (EM soft-VQ injects H(Z|X) > 0; provably improves IB tradeoff; direct relevance to kWTA-VQ.)

11. Tishby, N., Pereira, F.C., Bialek, W. (2000). "The information bottleneck method." arxiv physics/0004057. [arxiv](https://arxiv.org/abs/physics/0004057). (IB foundational.)

12. Achille, A., Soatto, S. (2018). "Information Dropout: Learning Optimal Representations Through Noisy Computation." IEEE TPAMI. (IB applied to representation learning; conditional entropy as a controllable knob.)

13. Maass, W. (2000). "On the Computational Power of Winner-Take-All." Neural Computation 12(11): 2519–2535. [ResearchGate](https://www.researchgate.net/publication/2457710_Neural_Computation_with_Winner-Take-All_as_the_only_Nonlinear_Operation). (kWTA universality; capacity bounds.)

14. Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction." Cognitive Computation 1: 139–159. (HDC binding/superposition primitives; foundation for the substrate's design.)

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15–0.25 from raw LM-based confidence.
- **Novel-synthesis cap at 0.50 applied:** kWTA-VQ as a SPECIFIC composition of biological-coding-level + soft-EM-VQ-IB has no prior empirical validation on LM-residual VQ tasks. P(HARD-PASS) = 0.40 reflects this cap + deflation.
- **HARD-FAIL thresholds mandatory and listed for every prediction.**
- The DIRECTIONALITY (softer-readout-is-better) is more confident (P ≈ 0.65–0.75 raw) than the MAGNITUDE (≥0.30 bits) — that is where the deflation hits.
- Biological optimum coding level (f ≈ 0.05–0.10) is robust across THREE independent biological circuits (cerebellum, mushroom body, dentate gyrus) — this is the load-bearing prior. The deflation accounts for cross-domain applicability uncertainty, not for the biology itself.

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev next cell after MKN):** `n4_kwta_soft_decode_v1`
- Same harness scaffold as n3, modified at the assignment step (write + read).
- Phase 1: k ∈ {1, 8, 32}, tau=1.0, 3 seeds, V_C=1024, N_DIM=16384, K=1. ~3.5 hr remote_cpu_queue.
- Phase 2 (conditional on Phase 1 ceiling drop ≥ 0.10): k ∈ {4, 16, 64, 128} for finer resolution + tau∈{0.5, 2.0} at best-k.
- Anchor: k=1 must reproduce n2 anchor 2.0491 ± 0.02.
- Version-marker: `assignment_mode='top_k_soft'`, `k_value`, `tau`, `effective_coding_level`.

**Composition prep (free piggyback once n4 ships):**
- Include K=2 arm at best-k (verifies Prediction 3 at no extra cell cost).

**Conditional next (only if n4 HARD-FAIL):** `n5_hippocampal_episodic_v1` — covered in L4 secondary cell section.

**Ordering vs MKN and Path A:**
- **n4 should ship BEFORE MKN.** MKN smooths within a row; if n4 changes the rows materially, MKN's optimal hyperparameters shift. Run them in sequence, not parallel.
- **n4 should ship BEFORE Path A.** Path A is GPU-expensive and Litwin-Kumar predicts it interacts multiplicatively with k. Knowing the optimal k at V_C=1024 saves wasted Path A GPU.

---

-- Research (Opus synthesis, 2x lit-scan via 6 parallel sub-agents, deflated per calibration)
