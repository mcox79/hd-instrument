# Wave 14f — Scaling laws for non-parametric retrieval-based ICL

Date: 2026-05-20
Status: external-literature synthesis (no project numbers used as input)

This note synthesizes published results on how non-parametric, retrieval-augmented in-context-learning gain scales with (a) memory size P and (b) representation dimension d. The goal is pre-registered predictions and a clean experimental design.

---

## TL;DR — predicted curves

We model the retrieval system as a pool of P stored entries, each a random vector in dimension d, and a cosine-style nearest-neighbor read. Two regimes dominate:

1. **Memory size P (at fixed d).** Empirically, retrieval-LM perplexity drops roughly log-linearly in datastore size with no saturation through several orders of magnitude (Khandelwal 2020, Borgeaud 2022, Shao 2024). The implied ICL gain (negative log-loss reduction) grows like
   - ΔICL(P) ≈ a · log(P) + b
   over the practical range, with **no saturation** observed below ~10^9–10^12 entries when d ≳ 1024.

2. **Dimension d (at fixed P, P ≪ exp(d)).** VSA capacity theory (Frady-Kleyko-Sommer 2018; Clarkson et al. 2023) says the signal-to-noise ratio of a cosine read from a bundle of M random items is
   - SNR ≈ d / M (linear in d, inverse in M)
   - reliable retrieval requires d = Ω(M · log(1/δ)) for failure prob δ.
   So when P ≪ d / log d we are **under-filled** and ICL gain is dimension-limited only insofar as it sets the floor on retrieval error; further doubling d gives **sub-logarithmic** ICL gain. When P ≳ d / log d we are **overfilled** and retrieval finds noise; gain collapses.

**Predicted gains for the sweeps (pre-registered):**

| Sweep | Predicted ΔICL change |
|---|---|
| P: 1024 → 8192 (3 doublings) at d=4096 | +3 · a units, with a ≈ 5–15% of the d=4096 baseline gain per doubling. Total ≈ 15–45% gain over P=1024. |
| d: 2048 → 8192 (2 doublings) at P=4096 | Small (≤10%) total improvement. At d=2048, P=4096 we are near the overfill knee (P > d) — expect gain *jump* from d=2048 to d=4096, then near-flat from d=4096 to d=8192. |

These are the bets we will hold ourselves to in `exp_scaling_capacity.md` follow-ups.

---

## 1. kNN-LM scaling math

### 1.0 Setup and notation

Throughout this section, P denotes the number of stored (key, value) pairs in the retrieval datastore, d denotes the dimension of the key vector, and ICL gain is the reduction in negative-log-likelihood (equivalently, log-perplexity) attributable to the retrieval branch versus an LM-only baseline:
- ICL gain = log PPL(LM only) − log PPL(LM + retrieval).
- Equivalently, ICL gain is the expected log-likelihood improvement per token. Positive values mean retrieval helps.

The retrieval distribution is a softmax over cosine (or negative-L2) similarities between the query key and the P stored keys, with temperature τ. The final next-token distribution is a convex combination with parameter λ ∈ [0,1] between the parametric branch and the retrieval branch. We hold λ at its per-cell-optimal value to remove a confound.

### 1.1 Khandelwal 2020 (kNN-LM, arxiv:1911.00172)

The kNN-LM interpolates a parametric LM with a non-parametric retrieval distribution computed by k-NN over a datastore of P cached (key, next-token) pairs. The empirical scaling result (Section 4.2, Figure 2a, Wikitext-103):

- 100M-token LM alone: perplexity 19.59
- 100M-token LM + 1.6B-token datastore: outperforms 3B-token-trained LM (PPL 15.17)
- 100M-token LM + 3B-token datastore: PPL 13.73

Two observations matter for our scaling story:

1. **Monotone, no saturation.** The authors explicitly state "increasing the datastore size monotonically improves performance, and has not saturated even at about 3B tokens." This is the dominant published statement on the functional form.
2. **Sub-log decay of perplexity, equivalently log-linear gain in log-likelihood.** Three doublings of the datastore (≈ 400M → 3B) shrink PPL from ~17 to ~13.7. In log-loss units (ICL gain = −Δ log p), gains across the curve are approximately constant per doubling — i.e. ΔICL ≈ a · log₂(P). This is the empirical regularity we will rely on for our predictions.

The optimal interpolation parameter λ also rises with P (Figure 2b), meaning the retrieval component absorbs more responsibility as the pool grows — consistent with retrieval SNR improving.

### 1.2 Borgeaud RETRO 2022 (arxiv:2112.04426)

RETRO scales the retrieval database from Wikipedia-scale (~4B) to MassiveText scale (~1.7T). Headline finding: retrieval performance gain is **roughly constant per decade of database size** and is comparable to multiplying the parametric model size by ~10× — a strong log-linear claim. The gain does not vanish through 1.7T tokens.

### 1.3 Shao 2024 (arxiv:2407.12854, MassiveDS / 1.4T datastore)

Explicitly titled "Scaling Retrieval-Based Language Models with a Trillion-Token Datastore." Reports that "datastore scaling reduces perplexity without signs of saturation" on RedPajama and S2ORC. A Llama-2 7B with the 1.4T datastore outperforms Llama-2 13B LM-only. They do **not** publish a fitted power-law exponent — they report Pareto-frontier curves on a log-x axis showing approximately linear loss reduction per decade of datastore.

### 1.3b Why log-linear and not a power law?

A first-principles reason for the log-linear form: as the datastore grows, the expected distance from a random query to its k-th nearest neighbor shrinks like (P)^(−1/d_eff), where d_eff is the *intrinsic* dimension of the key manifold. The corresponding probability-mass concentration of the retrieval softmax improves like 1 − exp(−c · (P)^(1/d_eff)). For d_eff ≫ 1 this is approximately linear in log P over many orders of magnitude — exactly the regime where the published curves live. The log-linear law is thus a manifestation of the curse-of-dimensionality eating an otherwise polynomial gain.

This also explains why **higher intrinsic dimension flattens the curve**: for very high-d_eff keys (random vectors), retrieval gain per log-doubling is small; for low-d_eff keys (well-clustered semantic embeddings), retrieval gain per log-doubling is large. In our setting, where keys may be closer to random, we should expect a *small* slope `a`.

### 1.4 Functional-form summary

Across three independent retrieval-LM studies (kNN-LM, RETRO, MassiveDS):
- ΔICL(P) ≈ a · log P + b over the practical regime
- No saturation observed below ~10^12 tokens (when d is the embedding dim, typically 768–4096)

Caveats:
- The constant `a` depends on dataset diversity and key-encoder quality — it is *not* a universal constant.
- The log-linear law must eventually fail (information-theoretically), but the published curves do not show the knee.
- These studies use realistic LM embeddings; for random / HDC keys the *coefficient* will be smaller because random keys carry less semantic signal per dimension.

---

## 2. HDC capacity bounds

### 2.1 Frady-Kleyko-Sommer 2018 (arxiv:1803.00412)

Classical result for VSA bundling with bipolar / Rademacher random hypervectors. Bundle M random items into a single vector s = sum xᵢ; read out item j by cosine with xⱼ. The readout statistic has:

- Signal mean ≈ d (or 1 after normalization)
- Noise variance ≈ d · (M − 1)
- SNR ≈ d / (M − 1) ≈ d / M

Reliable winner-take-all readout (probability ≥ 1 − δ) requires SNR ≳ 2 log(K/δ) where K is the codebook size, giving
- **M_max = O(d / log K)** items per bundle, **linear in d** modulo log factors.

This is the canonical "capacity is linear in d" statement.

### 2.2 Clarkson, Ubaru, Yang 2023 (arxiv:2301.10352, "Capacity Analysis of VSAs")

Re-derives bundling and binding capacities for four common VSAs (MAP-I, MAP-B, sparse-binary, Bloom-style). Key results:

- **MAP-I bundling (Theorem 6):** dimension m = O(N · log(M / δ)) to represent N items with failure δ — same linear-in-N (equivalently linear-in-d for fixed N) capacity, with explicit log factors.
- **MAP-B bundling (Theorem 16):** m = O(n · log(d / δ)) for membership testing in a bundle of size n drawn from universe d.
- Reliable retrieval with relative error ε needs m = O(ε⁻² log(1/δ)) — a Johnson-Lindenstrauss-flavored bound.

### 2.2b Why the read is cosine, and why it matters

For Rademacher (±1) keys of dim d, the inner product of a key with the bundled sum-of-M-keys is the signal (mean d / sqrt(d) = sqrt(d) after normalization); inner products of *other* keys with the bundle are the noise, each with variance ≈ M/d after normalization. The sum-of-noises distribution has variance ≈ M/d. So the readout statistic is approximately N(sqrt(d), M/d) for the correct key versus N(0, M/d) for a foil. Pick-the-max over K foils succeeds with probability → 1 iff d/M ≫ log K. This is exactly the SNR = d/M law and it says the right thing about both axes: the gain from doubling d is multiplicative on SNR, but only matters near the knee; below the knee the win-margin is already huge and an extra factor of 2 on SNR is invisible at the task level.

### 2.3 Hopfield reference point

Classical Hopfield (Hertz-Krogh-Palmer): capacity ≈ 0.15 n storable patterns for n neurons (correlated retrieval). With strict exact-recovery, n / (4 log n). Same family: **linear in n with log shaving.**

### 2.4 What this means for our pool

Treat the pool as a bundle/codebook of P random keys in dimension d, with cosine readout against a query. Then:
- For random keys, retrieval is reliable iff d ≳ P · log(1/δ).
- ICL gain via pool retrieval grows in d only insofar as d crosses the threshold d ≈ P · log(1/δ). Once d ≫ P log(1/δ), additional d gives diminishing returns (the noise is already buried).
- The realistic gradient w.r.t. d is therefore **non-monotone in slope**: large near the knee, near-zero deep into the under-filled regime.

---

## 3. The two limits and the transition regime

The capacity literature defines the load factor
- α = P / d (number of items per dimension)

Three regimes:

| Regime | Condition | Behavior |
|---|---|---|
| Under-filled | α ≪ 1 / log K | SNR ≫ 1; cosine retrieval finds correct neighbor with probability → 1; ICL gain limited only by *semantic* signal in keys, not by retrieval noise. |
| Knee | α ≈ 1 / log K | SNR ≈ O(1); retrieval succeeds only on the easiest cases; sharp transition. |
| Overfilled | α ≫ 1 / log K | SNR < 1; retrieval finds noise; ICL gain collapses toward zero (or, in interpolated systems, the parametric branch dominates). |

For the planned sweeps (POOL_SIZE ∈ {1024, 2048, 4096, 8192}, d ∈ {2048, 4096, 8192}, with log K ≈ 8–12 for realistic codebooks):

| (P, d) | α = P/d | Regime |
|---|---|---|
| (1024, 4096) | 0.25 | well under-filled |
| (2048, 4096) | 0.5 | under-filled, approaching knee |
| (4096, 4096) | 1.0 | **at the knee** |
| (8192, 4096) | 2.0 | **overfilled** for random keys; only semantic structure can save us |
| (4096, 2048) | 2.0 | overfilled |
| (4096, 8192) | 0.5 | under-filled |

So the d-sweep at fixed P=4096 walks across the knee, and the P-sweep at fixed d=4096 also walks across the knee. **Both sweeps are well-positioned to expose the transition** rather than living entirely in one regime — that is the design property we want.

Important asymmetry: published retrieval-LM systems (kNN-LM, RETRO) use *learned* embeddings whose intrinsic dimension is ≪ d, so they sit deep in the under-filled regime and see only the log-linear gain phase. Systems with random / HDC keys (our setting) will hit the knee much sooner. **Predicted curves below assume our keys are closer to random than to LM-trained.**

---

## 4. Experimental design — pre-registered predictions

### 4.1 Sweeps

- **Sweep A (memory size):** POOL_SIZE ∈ {1024, 2048, 4096, 8192}, fixed d = 4096, fixed N = 64 (context length), all other settings frozen.
- **Sweep B (dimension):** d ∈ {2048, 4096, 8192}, fixed POOL_SIZE = 4096, fixed N = 64.

Each cell: 5 seeds, BF-style aggregation per the standing playbook.

### 4.2 Predictions (pre-registered)

**Sweep A — ICL gain vs P at d=4096:**
- Monotone increase across {1024, 2048, 4096}.
- **Knee at P ≈ d / log K ≈ 4096 / 10 ≈ 400** is well below our smallest cell — so for random keys we are *already overfilled* even at P=1024 and we should expect **flat or decreasing** gain across the sweep.
- For semantically-structured keys, sit further left: expect log-linear rise, with ΔICL(P=8192) − ΔICL(P=1024) ≈ 3 · a units, a ≈ 5–15% of the P=1024 baseline.
- **Decision rule:** if the curve is flat from P=1024 onward → our keys behave like random vectors (overfilled regime); if the curve rises log-linearly → keys carry semantic signal that survives the load.

**Sweep B — ICL gain vs d at P=4096:**
- α = P/d crosses 2.0 → 1.0 → 0.5 across the sweep.
- Predicted **largest jump between d=2048 and d=4096** (crossing the knee).
- Predicted **near-flat from d=4096 to d=8192** (deep under-filled).
- Quantitatively: ΔICL(d=4096) − ΔICL(d=2048) should be ≥ 2× larger than ΔICL(d=8192) − ΔICL(d=4096).
- **Decision rule:** if d=2048 → d=4096 jump dominates and d=4096 → d=8192 is flat → capacity-limited story confirmed. If both increments are similar → ICL gain is *not* capacity-limited and we are paying for dimension for other reasons (e.g., expressivity of the encoder).

### 4.3 What would falsify the framing

- ICL gain rises sub-logarithmically with P but *also* rises sharply with d above the knee → suggests gain is driven by encoder expressivity, not retrieval SNR. (Rescue: re-frame as encoder-scaling, not memory-scaling.)
- ICL gain decreases with P everywhere → keys are pure noise, semantic story fails. (Rescue: improve key encoder before any further capacity work.)
- ICL gain is independent of both P and d → ICL is being delivered by the parametric branch, not retrieval at all. (This would be the most damaging outcome — kills the small bet.)

### 4.3b Secondary readouts to collect

For each cell, log not just ICL gain but also:
- Retrieval entropy (entropy of the softmax over the P keys, averaged over queries). Low entropy → confident retrieval; high entropy → noise-floor retrieval.
- Top-1 retrieval margin: similarity gap between the top neighbor and the runner-up.
- Effective λ (interpolation weight chosen per cell).
- Fraction of queries whose top retrieved value matches the gold label.

These let us distinguish "retrieval works but the value tokens aren't useful" from "retrieval is finding noise."

### 4.4 Cost

- Sweep A: 4 cells × 5 seeds = 20 runs.
- Sweep B: 3 cells × 5 seeds = 15 runs. (cell (P=4096, d=4096) shared with Sweep A → 14 new runs.)
- Total ≈ 34 runs. Background queue per the no-blocking rule.

---

## 5. Sources

- Khandelwal et al. 2020, "Generalization through Memorization: Nearest Neighbor Language Models," [arxiv:1911.00172](https://arxiv.org/abs/1911.00172) — datastore-size scaling, monotone-no-saturation finding, λ-vs-P observation.
- Borgeaud et al. 2022, "Improving Language Models by Retrieving from Trillions of Tokens" (RETRO), [arxiv:2112.04426](https://arxiv.org/abs/2112.04426) — retrieval gain ≈ constant per decade of database size; ~10× effective parameter equivalence.
- Shao et al. 2024, "Scaling Retrieval-Based Language Models with a Trillion-Token Datastore" (MassiveDS), [arxiv:2407.12854](https://arxiv.org/abs/2407.12854) — datastore scaling without saturation up to 1.4T tokens.
- Frady, Kleyko, Sommer 2018, "A Theory of Sequence Indexing and Working Memory in Recurrent Neural Networks," [arxiv:1803.00412](https://arxiv.org/abs/1803.00412) — VSA bundling capacity, SNR ≈ d/M.
- Clarkson, Ubaru, Yang 2023, "Capacity Analysis of Vector Symbolic Architectures," [arxiv:2301.10352](https://arxiv.org/abs/2301.10352) — formal capacity bounds for MAP-I, MAP-B, sparse-binary, Bloom-style VSAs; m = O(N log(M/δ)) etc.
- McEliece, Posner, Rodemich, Venkatesh 1987, "The Capacity of the Hopfield Associative Memory," IEEE Trans. Info. Theory 33(4):461–482 — classical n/(2 log n) and n/(4 log n) capacities for Hopfield nets; reference point for "linear-in-dimension" capacity.
- Xu, Alon, Diao, Neubig 2023, "Why do Nearest Neighbor Language Models Work?", [arxiv:2301.02828](https://arxiv.org/abs/2301.02828) — ensembling of input representations recovers ~55% of kNN-LM gain even without retrieval; useful sanity for distinguishing retrieval-driven vs encoder-driven ICL.
- Geng, Cai et al. 2024, "Great Memory, Shallow Reasoning: Limits of kNN-LMs," [arxiv:2408.11815](https://arxiv.org/abs/2408.11815) — kNN-LMs excel at memorization-style tasks, fail on multi-hop reasoning; bounds the kind of ICL gain we should expect from pure retrieval.

---

## 5b. Cross-check: distinguishing retrieval-driven ICL from encoder-driven ICL

Xu et al. 2023 ("Why do Nearest Neighbor Language Models Work?", arxiv:2301.02828) is load-bearing here. They show that **~55% of the kNN-LM gain is recoverable from ensembling input representations alone, with no actual retrieval**. So when we measure ICL gain in our system, we have to be careful: a positive gain does not automatically mean retrieval is helping. It could mean the encoder branch is doing the work and retrieval is a no-op or even a small drag.

The two diagnostic interventions we can do cheaply, *in addition* to the main sweeps:

1. **Shuffled-pool control.** Re-run each cell with the values shuffled (keys preserved, but each key now points to a random value from elsewhere in the pool). If ICL gain is unchanged → retrieval contributes nothing; the effect is encoder-side. If ICL gain drops to baseline → retrieval is the mechanism.
2. **Random-key control.** Re-run with the keys replaced by Gaussian noise (values preserved). If gain is unchanged → values are being delivered via a non-retrieval path. If gain drops → key quality matters, which is the prediction under the retrieval story.

We don't need these for the first pass, but they should be queued immediately if Sweep A comes back flat.

## 5c. Where this fits in the bigger picture

For the **small bet** (HDC memory for an LLM), this experiment is a clean test of whether non-parametric retrieval *into a fixed-d, fixed-P pool* can deliver meaningful ICL gain at the operating point we care about (N=64). If both sweeps cross the knee as predicted, we have a recipe: pick P just under the knee, hold d there, and the dial moves predictably.

For the **big bet** (Hebbian-trained VSA-LM), the same scaling story applies in reverse: a Hebbian-trained pool has *learned* keys, which lower the effective intrinsic dimension and push the knee out (more P fits in the same d). Measuring how much the knee moves between random and Hebbian-trained keys at fixed (P, d) is the next experiment after this one — and we cannot interpret that experiment without first nailing down the random-key baseline here.

In neuromodulator framing: retrieval gain is the *cortical-thalamic relay* story — sparse, high-precision recall from a content-addressable store. Capacity-linear-in-d corresponds biologically to the cortical area / synapse-budget tradeoff. The knee at P ≈ d / log K is the analogue of pattern-separation breaking down when too many memories are crammed into the same dentate gyrus volume — the same overcrowding failure mode, different substrate.

## 6. Plain-language status

The literature says the same thing three ways:

- **kNN-LM / RETRO / MassiveDS:** "more memory monotonically helps, log-linearly, no ceiling we have seen."
- **VSA capacity:** "you can store about d items in a d-dimensional bundle before the noise eats you; the knee is sharp."
- **Hopfield:** "same thing, in 1980s clothes — capacity is linear in dimension up to log shaving."

So the right experiment is the one that walks **across the knee** in both directions: P-sweep at fixed d, d-sweep at fixed P. The two pre-registered predictions above tell us, before we look at the data, what each outcome means.

The biggest risk is the boring one: if both sweeps come back flat, ICL isn't actually being delivered by retrieval — it is being delivered by something else in the stack — and we will have to chase down what.

## 7. Open questions we are *not* answering here

- How does the slope `a` in ΔICL ≈ a · log P depend on the task distribution? Khandelwal saw a big slope on Wikitext-103; we don't know what slope we will see on our eval.
- How does the knee move with k (number of neighbors retrieved, not just the top-1)? Larger k smooths the readout and effectively raises capacity by a factor like sqrt(k), but only if the top-k actually contain the correct neighbor.
- What happens when values are *programs* rather than tokens (i.e. retrieved tools or skills)? The capacity bounds still apply to keys, but the gain function over values is task-dependent and unrelated to the scaling laws above.

These are explicit non-goals for Wave 14f. They become Wave 15 candidates if the present sweeps land cleanly.

## 8. One-line take

**Capacity is linear in d, gain is logarithmic in P, and the knee is at P ≈ d / log K — the experiments are designed to walk across that knee in both directions and report what happens.**

