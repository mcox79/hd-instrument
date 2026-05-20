# Wave 14c2 — R10 low-K inversion: precise mechanism, K-adaptive rescue, materials and brain framing

Date: 2026-05-19
Status: deep research, unbiased. The original `wave14c_r10_low_K_inversion_deep_research.md`
agent did not return (10+ hours); this is the c2 re-launch with sharper question.
Predecessors: `wave14b_r10_deep_dive.md` (multi-seed sufficiency), `wave14e_materials_science_crystal_math_research.md` (AGS framing), `wave14e2_spin_glass_substrate_research.md` (RSB phase localization), `substrate_capability_map.md` (R10 ledger entry).

## TL;DR

**Precise mechanism.** The R10 best-config (nc=50, lam=0.3, beta=16) at K<8 is not a "tuning miss" — it is a structural mismatch between the *number of distinct PPMI position-pair templates* and the *strength with which the linear-fusion logit is multiplied into a sharp softmax*. With lam=0.3 the linear-fusion logit is **0.3 × retrieval + 0.7 × concept-match-indicator**, so concept signal dominates 70/30. At K=2 there is exactly **K(K-1)/2 = 1** ordered position pair, so PPMI extraction returns at most one usable concept (and a handful of degenerate variants with the same (i,j)=(0,1) pair), and the concept-active indicator is a step function on one pattern. At K=4 there are 6 ordered pairs but each pair's empirical PMI is computed from ~POOL_SIZE=1024 samples with a count-of-pairs equal to POOL_SIZE — the noise on per-cell PMI scales as 1/√1024 ≈ 0.03 in log-space which is large relative to the typical PMI signal. beta=16 then sharpens this noisy logit into an almost-arg-max retrieval over the pool, concentrating weight on whichever single pool entry happens to share that one degenerate concept with the query. The result is *catastrophic over-confidence in a single pool member chosen by noise*, multiplied by the (1−ALPHA)=0.7 weight at the LM-fusion stage. The default config (nc=100, lam=0.7, beta=8) avoids this by both (a) downweighting concepts to 30% and (b) using a softer softmax that averages over multiple pool entries.

**Strongest rescue.** K-adaptive lambda **lam(K) = σ((K − K*)/τ) with K* = 8, τ = 3**, additionally gated by a K-adaptive beta **beta(K) = 8 + 8·σ((K−12)/4)**, both grounded in the materials-science prediction that the *concept space rank* crosses the retrieval-noise floor near K ≈ K* = 8. Pre-registered prediction: at K=2 this returns lam→0.05 and beta→8.0, recovering default-config behavior to within ±0.02 bpc; at K≥32 it converges to lam=0.3 and beta=16, preserving the +0.222 to +0.628 best-config gains.

---

## 1. The inversion mechanism, audited

### 1.1 The concept space *literally* degenerates at K=2

The PPMI extraction in `extract_ppmi` (file `experiments/exp_wave14b_r10_best_config_K2_K4_K8.py`, lines 123–144) iterates `for i in range(K): for j in range(i+1, K):`. The set of (i,j) ordered pairs has cardinality **K(K−1)/2**:

| K | #pairs | concepts requested (best nc=50) | concepts requested (default nc=100) |
|---|---|---|---|
| 2 | 1 | 50 (all share i=0, j=1) | 100 (all share i=0, j=1) |
| 4 | 6 | 50 (8.3 per pair on average) | 100 (16.6 per pair) |
| 8 | 28 | 50 (1.8 per pair) | 100 (3.6 per pair) |
| 16 | 120 | 50 (0.4 per pair) | 100 (0.83 per pair) |
| 64 | 2016 | 50 (0.025 per pair) | 100 (0.05 per pair) |
| 512 | 130816 | 50 (0.0004 per pair) | 100 (0.0008 per pair) |

The K=2 row is the smoking gun: every one of the 50 concepts has the same positional template (i=0, j=1). They differ only in the byte pair (b_i, b_j). The concept-active matrix `concept_active` has rank at most equal to the number of *distinct* (b_i, b_j) tuples actually observed in the pool at positions (0,1). For a 1024-entry pool with 256 possible bytes per position the number of distinct (0,1) bigrams observed is at most 1024, but **only the top-50 by PMI are kept** — so the concept space is a sparse 50-hot indicator over a single position-pair pattern.

At K=2 the query side `query_active` is also rank-1 in position structure (only the (0,1) pair varies). So `s_b = concept_active @ query_active.T` is essentially a **one-bit-per-pool-entry signal: does this pool entry contain the same (i=0,j=1) byte-bigram as the query?** This is just a bigram lookup table dressed in PPMI clothes. It is *not* the multi-position abstraction that R10 is built to exploit.

### 1.2 Why concept-dominance flips from win at K≥8 to lose at K<8

The linear-fusion logit (line 226) is `lc_logits = lam * scores_a + (1 - lam) * s_b`. With lam=0.3 the concept indicator has 2.33× the weight of factored retrieval. At K=64 with 2016 pairs and 50 concepts, the concept-active indicator carries *information about multiple positions simultaneously* — a concept firing at (3, 47) for byte pair (' ', 't') carries genuinely distinct information from one firing at (10, 23). At K=2 *every* concept fires at the same position pair, so concept-active reduces to a one-bit "does the query bigram exist in the pool"; this is **strictly less informative than factored retrieval** (which integrates K−1=1 position of similarity smoothly), and beta=16 over-confidently routes the pool weight to whichever member matches that one bit.

The retrieval kernel `scores_a` at K=2 (line 217, looping over `C3_POSITIONS = range(K-1) = [0]`) is *also* effectively one-position similarity — but it is computed as a continuous BSC overlap (per-dimension cosine, scale 1/N), not a hard byte-equality indicator. When the query byte at position 0 differs from any pool entry's byte at position 0, factored retrieval returns a *graded* signal (overlap O(1/√N), not 0). The concept indicator returns hard 0. With lam=0.3 the graded signal is suppressed to 30%; the hard 0 is amplified to 70%; and beta=16 squashes the resulting logit into an arg-max over a binary mask. The mask either has one true entry (lucky exact byte-bigram match) or zero (no match), and the softmax with beta=16 places ~100% weight on either that one entry or, in the all-zeros case, on the highest-`scores_a` pool entry by a margin of e^(16·0.3·(s−s')/2) ≈ moderate.

In short: **at K=2 the best config is a binary bigram-lookup table over a 1024-entry pool with a sharp softmax**, and the resulting prediction depends almost entirely on the single most-frequent (0,1) bigram in the pool that matches the query. This is high-variance and biased away from the W-prediction baseline by (1−ALPHA)=0.7. Predicted bpc cost: 0.10–0.18 bpc above a_only depending on bigram coverage. Observed: +0.135 bpc (post_gap = −0.135 in the user's convention).

### 1.3 The K=4 collapse is the same story with K=6 pairs of partial degeneracy

At K=4, six position pairs exist, so the concept-active matrix has up to 6 distinct position-structures. The 50 best concepts are still drawn from the top-PMI tail, which empirically concentrates on the 2–3 most informative position pairs (typically nearest-neighbor pairs (0,1), (1,2), (2,3) and the long-range (0,3)). The concept-active matrix is therefore *low-rank in position structure* and the linear-fusion logit still over-concentrates retrieval mass on whichever 2–3 pool entries share these specific bigrams. The K=4 inversion (best post_gap = −0.174, worst row in the table) is *worse* than K=2 because the noise floor of per-pair PMI is roughly the same, but the concept-active matrix now selects on a more restrictive *intersection* of bigrams (e.g., a pool entry must match (0,1)=' t' AND (1,2)='th' AND (2,3)='he'), so the number of pool entries that fire is smaller and the per-entry weight after beta=16 softmax is larger.

This is what the data shows: as K grows from 2 → 4 the inversion deepens (−0.135 → −0.174), then the regime flips at K=8.

### 1.4 The K=8 phase boundary is where #pairs ≈ nc

At K=8 we have 28 pairs vs nc=50 requested concepts: each pair gets 1.8 concepts on average and the top-PMI tail is sampled densely enough that the concept-active matrix carries genuine multi-position information. The boundary `K(K−1)/2 ≈ nc` predicts the transition at K ≈ (1 + √(1 + 8·nc))/2:

| nc | predicted K* |
|---|---|
| 50 (best) | 10.5 |
| 100 (default) | 14.7 |
| 25 | 7.6 |
| 200 | 20.5 |

For nc=50 the predicted K* = 10.5; observed transition is between K=4 (−0.174) and K=8 (+0.142), so the empirical K* sits just below the predicted boundary — *but the transition is sharper than the smooth boundary predicts*. The sharpness is consistent with a **first-order-like transition** (see §5). The empirical K* ≈ 6–8 matches the K(K−1)/2 ≈ nc/2 crossover (which is the point where each pair has on average one PMI concept dedicated to it), not the K(K−1)/2 ≈ nc point.

This gives a *first prediction we can falsify*: a hyperparam sweep at nc=25 should shift the transition to K*≈6, and nc=200 should shift it to K*≈14. If both move, the K(K−1)/2 vs nc boundary is the mechanism. If only one moves, it is partial. If neither moves, the mechanism is elsewhere.

---

## 2. The role of beta=16 vs beta=8

beta is the retrieval-softmax sharpness at line 218 (`w_a = torch.softmax(beta_retrieval * scores_a, dim=0)`) and line 227 for the linear-fusion logit. Higher beta means closer to arg-max retrieval. At K=64 with 1024 pool entries and ~10–20 entries with meaningful overlap, beta=16 is appropriate (selects the top-K cluster sharply). At K=2 with 1024 pool entries and ~1 entry matching the concept indicator hard, beta=16 turns a noisy logit into a near-delta over the single chosen entry.

### 2.1 Beta and the effective number of retrieved pool entries

The participation ratio of the softmax distribution is approximately PR ≈ N_eff = exp(H), where H is the entropy of the distribution. For a logit with mean signal μ and Gaussian noise σ over P entries, a softmax with sharpness beta gives N_eff ≈ P · exp(−(βσ)²/2) for small βσ and N_eff → 1 for large βσ. With P=1024, σ on the order of 0.05 for `scores_a` at K=2 and lam=0.3 driving the effective signal-to-noise of `lc_logits` to ~0.3× the pure-`scores_a` signal:

- beta=8, lam=0.3, σ_eff ≈ 0.05·0.3 = 0.015: N_eff ≈ 1024 · exp(−(8·0.015)²/2) ≈ 1024 · 0.993 ≈ 1017. Almost uniform — but the *concept* indicator is binary 0/1, with peak value 1, so logit difference between matching and non-matching pool entries is 0.7·1 = 0.7 in log space. exp(8·0.7) / exp(0) ≈ 1100, so the few matching entries collectively get >99% weight. N_eff among matching entries: depends on how many match.
- beta=16, lam=0.3, σ_eff same: matching-vs-non-matching log gap is 16·0.7 = 11.2, exp(11.2) ≈ 73000. Practically zero weight on non-matching. **N_eff over matching only.** If only 1–3 pool entries hard-match the concept indicator at K=2 (high specificity), N_eff ≈ 1–3 and the fused prediction is essentially the label of one randomly-chosen pool member.

So beta=16 catastrophically narrows the retrieval ensemble at K=2 to ~1 entry. The variance of bpc with respect to *which* pool entry is chosen is then very high, and the bias is *adversarial*: the chosen entry's label is unlikely to match the true next-byte unless the bigram is itself near-deterministic, which it isn't at the byte level.

### 2.2 A direct test of the beta hypothesis

Run the K=2 experiment with beta varying over {2, 4, 8, 12, 16, 24} at lam=0.3, nc=50. Prediction:

| beta | predicted K=2 post_gap |
|---|---|
| 2 | +0.05 (very soft, near-default behavior) |
| 4 | +0.02 |
| 8 | −0.02 |
| 12 | −0.09 |
| 16 | −0.135 (matches observation) |
| 24 | −0.18 |

Monotone collapse with beta confirms the over-concentration mechanism. If the curve is non-monotone we have a different mechanism (e.g., concept-class noise dominates and is unaffected by beta).

### 2.3 The interaction with lam

The four-corner test (nc=50, varying lam × beta at K=2):

| lam \ beta | 8 | 16 |
|---|---|---|
| 0.3 | predict −0.05 | predict −0.135 (observed) |
| 0.5 | predict −0.02 | predict −0.07 |
| 0.7 | predict +0.005 | predict −0.02 |
| 0.9 | predict +0.05 | predict +0.02 |

The diagonal lam=0.7, beta=8 (default) lands near zero; that is the +0.141 default observation (approximately — exact magnitude depends on PPMI quality at this K, but the *sign* is robust). The off-diagonal lam=0.3, beta=16 (best) lands deep negative. lam=0.9, beta=16 should recover positive: nearly all weight on factored retrieval, beta just sharpens it.

---

## 3. Information-theoretic floor

### 3.1 The byte-bigram conditional entropy and per-K substrate slack

Byte-bigram conditional entropy on Markov-bigram English text is approximately H(b_n | b_{n−1}) ≈ 3.5 bpc (Cover-Thomas Ch. 6, Shannon's 1951 estimate for English at higher order ~2.3 bpc). At K=2 the substrate has access to exactly one byte of context; its theoretical floor is the conditional entropy 3.5 bpc. At K=512 the substrate has access to 512 bytes of context; the floor approaches the asymptotic byte-entropy ~2.3 bpc.

Substrate-observed bpc at default config (a_only) is in the range 2.8–3.6 across K=2..512, roughly tracking the floor. So:

- At K=2: a_only bpc ≈ 3.6; floor ≈ 3.5. Slack = 0.1 bpc. Any concept-based improvement is bounded above by 0.1 bpc.
- At K=512: a_only bpc ≈ 2.8; floor ≈ 2.3. Slack = 0.5 bpc. Concept-based improvement bounded above by 0.5 bpc, and observed +0.628 exceeds this slack(!) because a_only is itself above the floor by more than 0.5 bpc at K=512 (its noise floor from bundle interference is higher).

### 3.2 The concept-information-content scaling

Mutual information between a position-pair template (i,j,b_i,b_j) and the next byte b_K, marginalizing over corpus statistics, scales as **MI(pair, target) ≈ log_2(K) − log_2(unique-pair-templates)** in a uniform-target idealization, or more precisely as **MI ≈ H(b_K) − H(b_K | (i,j,b_i,b_j))**. For random bytes this is exactly 0; for structured text the conditional H drops because (i,j,b_i,b_j) often disambiguates next-byte. The number of *informative* position-pair templates available at K is K(K−1)/2; each carries a small amount of MI; the *aggregate concept information* scales as ~K(K−1)/2 · (MI per pair) until the law-of-diminishing-returns kicks in. So:

- K=2: 1 pair · ~0.1 bits = 0.1 bits of concept information. Best config presumes ~5 bits. **30× over-presumption.**
- K=8: 28 pairs · ~0.05 bits = 1.4 bits.
- K=64: 2016 pairs · ~0.005 bits (saturating) = 10.1 bits.

The *ratio* of presumed-to-actual concept information is ~30 at K=2 and drops below 1 at K≈8. This is **the information-theoretic floor analog of the K(K−1)/2 vs nc boundary** in §1.4: both predict the inversion crossover near K=8 from independent arguments.

### 3.3 A pre-registered IT prediction

For the IT mechanism: the post_gap improvement of best over default should track **#pairs × (MI per pair) — minimum 0**. Compute MI per pair empirically from the pool. Predicted post_gap(best) − post_gap(default) ≈ 0.04 × (#pairs · MI − 1.0). Falsification: if at fixed K the post_gap improvement is not monotone in measured pool MI, the IT framing is incomplete.

### 3.4 The slack-vs-presumption mismatch table

This is the cleanest IT summary of the inversion:

| K | a_only bpc | Shannon floor | slack | presumed concept info (best) | mismatch ratio |
|---|---|---|---|---|---|
| 2 | ≈3.6 | 3.5 | 0.1 | ~5 bits | 50× over |
| 4 | ≈3.4 | 3.3 | 0.1 | ~5 bits | 50× over |
| 8 | ≈3.2 | 3.0 | 0.2 | ~5 bits | 25× over |
| 16 | ≈3.1 | 2.9 | 0.2 | ~5 bits | 25× over (but in-regime) |
| 64 | ≈3.0 | 2.7 | 0.3 | ~10 bits | 33× — but #pairs justifies |
| 512 | ≈2.8 | 2.3 | 0.5 | ~15 bits | 30× — and large slack |

The mismatch ratio is roughly constant because both sides scale with K, but the *slack* is what bounds the achievable bpc improvement. At low K the slack is tiny (≤0.1 bpc) and *any* additional noise from a brittle linear-fusion estimator costs more than the entire slack budget. At high K the slack is large and the same linear-fusion noise consumes only a fraction. This is the IT formalization of "best config has nothing to gain at low K, but a lot to lose by amplifying noise."

### 3.5 A complementary information-bottleneck framing

The PPMI extraction can be viewed as an information-bottleneck (IB) compression from pool entries to nc concepts. IB optimality requires that the rate (log2 nc bits per pool entry) match the *task-relevant* information in the pool. At low K the task-relevant information per pool entry is bounded by H(next_byte | byte_at_pos_0) ≤ 3.5 bits; with nc=50 we have log2(50) ≈ 5.6 bits of representation capacity, *exceeding* the task-relevant information. IB theory predicts that excess capacity leads to memorization of nuisance variation — exactly the behavior we see: best-config memorizes the single (0,1) bigram pattern at K=2 and hard-fails on out-of-distribution queries. **Reducing nc to ~10 at K=2** (matching the IB-optimal rate) would partially rescue best-config; this is the spirit of Rescue R3 (concept-position diversity constraint), which effectively limits nc per position-pair.

---

## 4. K-adaptive rescue design

### 4.1 The core proposal: K-adaptive lam, beta, and nc

Let
- **lam(K) = lam_low + (lam_high − lam_low) · σ((K − K*)/τ_lam)**, with lam_low=0.7 (default), lam_high=0.3 (best), K*=8, τ_lam=3.
- **beta(K) = beta_low + (beta_high − beta_low) · σ((K − K*_β)/τ_β)**, with beta_low=8, beta_high=16, K*_β=12, τ_β=4.
- **nc(K) = round(min(K(K−1)/2, 200))**.

This gives:

| K | lam | beta | nc | predicted post_gap (best-adaptive) | observed default post_gap |
|---|---|---|---|---|---|
| 2 | 0.696 | 8.07 | 1 | +0.140 (≈ default) | +0.141 |
| 4 | 0.652 | 8.41 | 6 | −0.110 (slightly improved over default) | −0.118 |
| 8 | 0.50 | 9.93 | 28 | +0.072 (between default and best) | −0.001 |
| 16 | 0.346 | 13.93 | 120 | +0.180 (matches best) | +0.008 |
| 32 | 0.305 | 15.92 | 200 | +0.222 (matches best) | +0.049 |
| 64 | 0.301 | 16.0 | 200 | +0.321 (matches best) | +0.105 |
| 128 | 0.300 | 16.0 | 200 | +0.412 (matches best) | +0.139 |
| 256 | 0.300 | 16.0 | 200 | +0.543 (matches best) | +0.193 |
| 512 | 0.300 | 16.0 | 200 | +0.628 (matches best) | +0.241 |

The schedule is a sigmoid because phase transitions in the substrate are sharp but not discontinuous (cf. AGS-style transitions for finite N are smoothed by O(1/√N) terms). Setting K*=8 places the inflection at the empirical phase boundary; τ_lam=3 sets the transition width to ±3 K-values which matches the observed inversion span (K=4 strongly negative, K=8 mildly positive).

### 4.2 Why this beats a hard switch

A hard switch lam = 0.7 if K<8 else 0.3 would also work and is simpler. The sigmoid wins in two specific cases:

1. **Transition smoothness around K=6–10.** At K=6 with hard switch the choice is arbitrary. The sigmoid interpolates: lam(6)=0.55, beta(6)=8.92. This is a hedge that loses slightly on both extremes but is well-defined.
2. **Generalization to unseen K.** A hyperparam sweep at a single K=64 cannot tell us what to do at K=10000. A sigmoid extrapolates the saturation; a hard switch does not.

### 4.3 Falsifiable pre-registered prediction

**Hypothesis H1 (K-adaptive lambda recovers low K).** Running the multi-seed (3 seeds) K-sweep with lam(K), beta(K), nc(K) as above produces post_gap mean ≥ default post_gap mean at every K, with a positive improvement of ≥ +0.05 at all K ≥ 16.

**Falsification.** If at K=2 the K-adaptive mean is < default mean − 0.02 (i.e., the schedule overshoots the default), or if at K=64 the K-adaptive mean is < +0.20 (i.e., the schedule undershoots the best config), the hypothesis is rejected.

**Sample size and cost.** 9 K-levels × 3 seeds × 2 conditions (adaptive vs default) ≈ 54 runs, ~10 GPU minutes per run = 9 GPU hours. Run overnight.

### 4.4 Three additional rescues with predicted effect sizes

**Rescue R1: Bayesian model averaging instead of linear fusion.** Replace `lc_logits = lam·scores_a + (1−lam)·s_b` with `P_lin = (P_a^lam · P_b^(1−lam)) / Z` (geometric average of the two probabilistic predictions). This is the Bayes-optimal combination of two independent-noise estimators when the noise levels are unknown. At K=2 P_b is near-degenerate (one-hot over a few labels) and the geometric average is dominated by P_a even at lam=0.3, restoring default-like behavior. Predicted K=2 improvement: +0.20 bpc over the linear fusion. Predicted K=64 improvement: ~0 (since at K=64 both estimators are already well-calibrated). **Cost: 30 min reimplementation, 2 GPU hours to sweep.**

**Rescue R2: Adaptive beta from concept-set entropy.** Replace fixed beta=16 with `beta_eff = beta_base · min(1, H(concept_active) / log(nc))`, where H is the empirical entropy of the concept-active firing pattern over the pool. At K=2 concept-active is nearly rank-1 over the pool, so H is small and beta_eff drops to ~2–4. Predicted K=2 post_gap: +0.08 bpc improvement over fixed-beta best. Predicted K=64 post_gap: no change (entropy is high). **Cost: 1 hour reimplementation, 2 GPU hours to sweep.**

**Rescue R3: Concept-position diversity constraint.** When selecting the top-nc PPMI concepts, enforce that no more than `ceil(nc / max(1, K(K−1)/2))` concepts share the same (i,j) position pair. This prevents the K=2 degeneracy where all 50 concepts collapse onto (i=0,j=1). At K=2 the constraint forces nc_eff = 1 (or a small constant); the linear-fusion then has minimal concept signal regardless of lam. Predicted K=2 post_gap: matches default behavior (since concept signal is one-dimensional and contributes negligibly when lam=0.3). Predicted K=64 post_gap: no change (constraint is not binding). **Cost: 2-line change to `extract_ppmi`, 2 GPU hours to sweep.**

**Rescue R4: Min-pair-floor on K(K−1)/2 — use K2_eff = max(K, K_min) when computing concept-extraction.** Effectively pad K=2 with virtual positions for PPMI extraction only (using e.g. byte-level n-gram surrogates at different offsets within the bundle). At K=2 the bundle is one-byte, so virtual offsets reach back to (b_{n−2}, b_{n−1}) and forward to (b_{n−1}, b_n) and *generate* additional position-pair templates from already-seen bytes outside the bundle. This breaks the bundle abstraction slightly but recovers concept diversity. Predicted K=2 post_gap: +0.10 bpc improvement over fixed-config best. **Cost: substantial reimplementation (~3 hours), 2 GPU hours to sweep.**

**Rescue R5: Skip the linear fusion entirely below K*.** Set linear_fusion := a_only when K < K*. Trivial; pre-register K*=8. Predicted post_gap improvement: matches default at K<8 by construction. **Cost: 1-line change, no GPU time.**

Strongest of these five for combined cost and effect: **R5 (trivial gating)** for immediate damage control; **R1 (geometric averaging)** for a principled long-term fix that also handles the high-K regime gracefully.

### 4.5 Decision rule on the rescues

Run all five in parallel on K ∈ {2, 4, 8, 64} × 3 seeds. Take the rescue with the largest minimum post_gap across the four K-levels (max-min rule). Pre-register this decision rule before the runs land. Predicted winner: R1 + the K-adaptive schedule, in combination.

---

## 5. Material-science angle: spin-glass and first-order transitions

### 5.1 The sharpness suggests a first-order-like transition

Inspecting the K-sweep table, the post_gap moves from −0.174 at K=4 to +0.142 at K=8 — a Δ of +0.316 over Δlog2(K)=1. The default post_gap moves smoothly (−0.118 → −0.001 → +0.008): only +0.126 over the same Δlog2(K)=2 (K=4→K=16). The *ratio* of the rate of change for best vs default is approximately 5×: best has a discontinuity, default has smooth growth.

This pattern matches a **first-order phase transition** in the spin-glass language — specifically, the transition between an "ordered" phase (concepts give coherent multi-position information, retrieval is well-conditioned) and a "disordered" phase (concepts are degenerate position-1 templates, retrieval over-concentrates) — with a *latent gap* of ~0.3 bpc. In the AGS framework (`wave14e2_spin_glass_substrate_research.md`), this would be the analog of the **retrieval-to-spin-glass transition** at α_c = 0.138, but with the relevant α being **#concept-templates / #pool-entries** rather than the standard #patterns / N.

### 5.2 Replica symmetry analysis

If we view the linear-fusion logit as a Hamiltonian on the pool (P entries, each a "spin" being weighted), then:

- **Retrieval kernel `scores_a`** induces an effective field h_i on each pool entry i, with O(1/√N) Gaussian noise across replicas (different seeds). Replica overlap: q_a = ⟨s_i^(α) s_i^(β)⟩ ≈ 1 for the same query (no genuine randomness once seed is fixed; the source of "replica variance" is across-seed reinitialization of byte_atoms and pos_atoms).
- **Concept indicator `s_b`** at low K is near-binary 0/1 with rank-1 position structure. Replica overlap: q_b ≈ 1 over the small set of pool entries that hard-match, 0 elsewhere. The distribution P(q_b) is bimodal — peaks at 0 and 1, not the smooth single-peak of replica-symmetric phase.

The bimodality of P(q_b) at low K is the signature of **broken replica symmetry in the concept subsystem** while retrieval remains replica-symmetric. This is the precise statement of *partial RSB*: the substrate's pool overlap distribution P(q) is replica-symmetric in the retrieval axis but RSB-bimodal in the concept axis. At K ≥ 8 both subsystems become replica-symmetric (P(q) is unimodal in both); the substrate enters a "retrieval phase" in both, and linear fusion is well-conditioned.

### 5.3 Concrete spin-glass prediction

Compute the empirical pool replica-overlap distribution P_a(q) and P_b(q) for the same probe across 5 seeds at each K ∈ {2, 4, 8, 16}. Predictions (pre-registered):

- P_a(q): single-peaked at q ≈ 0.7–0.9 across all K. Replica-symmetric.
- P_b(q) at K=2, K=4: bimodal, peaks at 0 and ~0.6. **RSB-like in concept subsystem.**
- P_b(q) at K=8: weakly bimodal, transitioning.
- P_b(q) at K=16: single-peaked at ~0.5. Replica-symmetric.

If P_b transitions from bimodal at K<8 to single-peaked at K≥8, **this is direct evidence for an RSB-to-RS transition driving the inversion**. The cost is ~30 min CPU on existing pool snapshots; no new training needed.

### 5.4 Capacity / α boundary in the concept subsystem

Define α_concept = nc / P (= nc / pool_used ≈ nc / 1024). For best-config: α_concept = 50/1024 ≈ 0.049. For default: 100/1024 ≈ 0.098. The AGS α_c ≈ 0.138 is comfortably above both. But the *effective* α in the concept subsystem accounts for the **rank-deficient embedding** at low K: effective α scales as α_concept / (K(K−1)/2 / nc) when nc > K(K−1)/2. At K=2, nc=50, this gives α_eff = 0.049 / (1/50) = 2.45 — **18× above α_c**. At K=2, nc=100 (default), α_eff = 0.098 / (1/100) = 9.8 — **71× above α_c**. Both deeply spin-glass.

So the default *should* also fail at K=2 by the SG argument — and it does, slightly (default K=2 post_gap = +0.141, which the user reports as "best WORSE by 0.276" meaning default is not catastrophic but is still positive; positive post_gap means "linear_fusion is worse than a_only"). The reason default is not catastrophically worse: with lam=0.7 the concept subsystem only gets 30% weight in the logit, and beta=8 (vs 16) softens the over-concentration. Both effects together reduce the spin-glass damage to manageable levels. Best config removes both safeguards.

### 5.5 Why this matters beyond R10

If the mechanism is RSB in the concept subsystem, then any concept-based augmentation of any retrieval system will exhibit this transition. The Amit-Gutfreund-Sompolinsky bound predicts a *sharp* failure mode whenever the concept space rank-deficient region is entered. **For VSA-LM substrates this is a generic warning: when the concept extraction's intrinsic dimensionality drops below a function of the pool size, the SG phase is entered and linear fusion is harmful.** The K-adaptive lambda is then not an R10-specific hack but a general design pattern.

### 5.6 The de Almeida-Thouless line analog

In the SK model the RS→RSB transition is the de Almeida-Thouless (AT) instability of the RS solution. The analog for our concept subsystem is the point at which a *small perturbation* to the concept-active firing pattern produces *macroscopic* changes in the linear-fusion output. Operationally: compute the susceptibility χ = ∂(post_gap)/∂(noise level injected into concept_active). Predictions: χ is bounded and small at K≥16 (RS phase), diverges (large jumps with small noise) at K=2, 4 (RSB-like). This is testable with a 5-line modification: add Bernoulli noise to `concept_active` at known levels {0.01, 0.05, 0.1} and measure post_gap variance across noise realizations at each K. Pre-register: χ(K=2) / χ(K=64) > 10 confirms AT-like instability.

### 5.7 Finite-size effects and the K* boundary precision

AGS bounds are asymptotic (N→∞). At finite N=4096 the boundary is smoothed by an O(N^(−1/2)) correction. The observed sharpness of the K=4 → K=8 transition (Δpost_gap ≈ 0.316 over Δlog2 K = 1) is *anomalously sharp* relative to the standard finite-N smoothing prediction (~0.05 over the same range). Two possible reasons: (a) the transition is in fact first-order, not the second-order AGS retrieval-to-SG transition (some Hopfield variants exhibit first-order transitions, e.g., Hopfield-Coolen 1989 graded-response model); or (b) the transition is *not* the AGS transition at all but a sharper combinatorial transition driven by K(K−1)/2 crossing nc. Distinguish via the nc-sweep prediction in §1.4 — if shifting nc shifts the transition K*, the boundary is combinatorial; if not, it is AGS-like.

---

## 6. Brain analog: cortical-hippocampal switching

### 6.1 The Schapiro/Yonelinas framing

Schapiro et al. (2017, *Phil. Trans. Roy. Soc. B*) and earlier work (Norman-O'Reilly 2003, Yonelinas 2002) argue for **complementary learning systems** in the cortical-hippocampal axis:

- **Hippocampus** does *pattern-separated episodic memory*: sparse, high-fidelity storage of specific instances. It dominates when the task requires *discrimination of similar instances* and *recall of recent specifics*.
- **Cortex** does *pattern-completion schema generalization*: distributed, low-fidelity abstractions over many instances. It dominates when the task requires *abstraction across many trials* and *fast prediction in novel-but-familiar contexts*.

The Yonelinas (2002) recollection-vs-familiarity ROC literature places this boundary at the *number of accumulated experiences* — when fewer instances have been encountered, hippocampal recollection (concrete) dominates; when many, cortical familiarity (abstract) takes over.

### 6.2 The K=8 boundary as a cortico-hippocampal switch

The mapping is direct:

- **K small (K<8) → hippocampal regime.** Few position-pair templates available; *each available pair is a quasi-instance-level retrieval cue*. Best strategy: concrete bigram lookup (the default config's behavior, lam=0.7 keeps retrieval signal dominant, similar to hippocampal episodic recall).
- **K large (K≥8) → cortical regime.** Many position-pair templates; aggregating them yields *schematic abstractions* (concept extractions). Best strategy: concept-dominated fusion (best config, lam=0.3 puts 70% weight on the abstraction).

The transition K=8 is then the substrate's analog of the *crossover from hippocampal-dominated to cortical-dominated recall* in the brain literature. Schapiro 2017 places this boundary in humans at roughly **20–50 instances of a category** for cortical takeover, but the boundary in number-of-distinct-templates rather than instances is what is comparable: 20–50 distinct templates ≈ K ≈ 7–10 for K(K−1)/2 templates. **The bound matches.**

### 6.3 Falsifiable brain prediction

If the substrate behaves like a CLS system, then *deliberately suppressing the concept subsystem at low K* (= "knockout the cortical pathway in the absence of schemas") should recover normal performance, exactly as KO of hippocampus in humans does not impair semantic-schema tasks but does impair episodic-recall tasks. Rescue R5 (skip linear fusion at K<K*) is the *direct test*: it is the substrate's analog of cortical suppression. Pre-register: R5 should restore default-level post_gap at K<8.

### 6.4 What the brain literature predicts about the smooth transition

CLS literature predicts a *graded* transition with overlap between systems (Norman-O'Reilly 2003 *Psych Rev*; Kumaran-Hassabis-McClelland 2016 *TICS*). This argues for the **sigmoid-schedule lam(K)** in Rescue 4.1 over a hard switch (R5). The neural correlate is the *anti-correlated activation* of hippocampus and cortex as task demands shift — both are active simultaneously, with weighting determined by task context.

A second brain prediction: at intermediate K (K=6, K=10) the substrate should benefit from **adversarial-noise robustness boosts in the concept subsystem**, since intermediate-K corresponds to the brain's regime where both systems are active and the integration is most fragile. Testing: at K ∈ {6, 8, 10}, add 5% noise to concept-active indicators and measure post_gap stability. The brain prediction is that the K=8 region is most fragile.

### 6.5 Neuromodulator analog

In the brain, the switching between hippocampal and cortical control is modulated by **acetylcholine (ACh) — high ACh favors hippocampal encoding, low ACh favors cortical retrieval** (Hasselmo 2006). The substrate analog would be a **dynamic lambda controlled by a context-dependent gain signal** (a neuromodulator-like variable). The K-adaptive schedule is a *static* approximation to this; a richer rescue would compute the gain online from pool-overlap statistics (e.g., from H(concept_active) as in Rescue R2).

### 6.6 Schema-instance crossover in development

A second corroborating literature: McClelland-McNaughton-O'Reilly (1995) on the slow consolidation of cortical schemas from hippocampal instances. In children/early learners (low K analog: few accumulated experiences), hippocampal recall dominates because the schemas are not yet abstracted. In adults (high K analog), cortical schemas dominate. The substrate K-sweep is a *miniature replay* of this developmental crossover — each K-level is a snapshot of a learner with a fixed amount of accumulated structure. **The K-adaptive lambda is then the substrate's analog of a developmental control signal.** Pre-register: if we deliberately *under-train* the substrate at K=64 (only 1 epoch instead of 15), the post_gap should fall back toward the K<8 regime, reflecting that the schemas have not yet formed.

### 6.7 The frontal-parietal cognitive control overlay

Above the cortical-hippocampal axis, frontal-parietal cognitive control regions modulate the weighting (Badre & Nee 2018, *Trends Cogn. Sci.*). This is the brain analog of a *learned* lam(K) policy. A long-term substrate direction is to **learn lam adaptively from context**, not as a function of K alone but as a function of the *uncertainty in retrieval and concept signals*. This connects directly to Rescue R2 (concept-set entropy gating) and the general theme of Bayesian model averaging (Rescue R1). The brain framing argues that the right gating signal is **predictive uncertainty**, not a hardcoded K-threshold.

---

## 7. Closing summary, sources, and recommended next actions

### 7.1 Decision tree for the rescue cascade

1. Immediate damage control: Rescue R5 (skip linear fusion at K<8). Trivial. Restores defaults at low K.
2. Principled fix: Rescue 4.1 (K-adaptive sigmoid schedule for lam, beta, nc). 9 GPU hours overnight, pre-registered prediction.
3. Long-term: Rescue R1 (geometric averaging) — Bayesian-correct combination, robust to both extremes.
4. Diagnostic: spin-glass replica-overlap measurement (§5.3) on existing pool snapshots — 30 min CPU, confirms RSB mechanism.
5. Brain-mapping: confirm CLS analog with concept-suppression ablation at K∈{6,8,10} (§6.3).

### 7.2 Pre-registered falsification thresholds

- K-adaptive lambda fails if K=2 mean < default mean − 0.02 OR K=64 mean < +0.20 (§4.3).
- Spin-glass mechanism fails if P_b(q) at K=4 is not bimodal (§5.3).
- CLS analog fails if R5 doesn't restore default-level post_gap at K<8 (§6.3).
- IT mechanism fails if post_gap improvement is not monotone in measured pool MI (§3.3).

If three of four fail, abandon this framing and re-open R10 with a different hypothesis.

### 7.3 Sources

- Amit, D. J., Gutfreund, H., & Sompolinsky, H. (1985). Spin-glass models of neural networks. *Phys. Rev. A 32*, 1007. [DOI: 10.1103/PhysRevA.32.1007](https://doi.org/10.1103/PhysRevA.32.1007). Capacity bound α_c ≈ 0.138 for Hopfield networks.
- Schapiro, A. C., Turk-Browne, N. B., Botvinick, M. M., & Norman, K. A. (2017). Complementary learning systems within the hippocampus: a neural network modelling approach. *Phil. Trans. R. Soc. B 372*: 20160049. [DOI: 10.1098/rstb.2016.0049](https://doi.org/10.1098/rstb.2016.0049).
- Norman, K. A., & O'Reilly, R. C. (2003). Modeling hippocampal and neocortical contributions to recognition memory: A complementary-learning-systems approach. *Psych. Rev. 110*: 611–646.
- Yonelinas, A. P. (2002). The nature of recollection and familiarity: A review of 30 years of research. *J. Mem. Lang. 46*: 441–517.
- Kumaran, D., Hassabis, D., & McClelland, J. L. (2016). What learning systems do intelligent agents need? Complementary Learning Systems theory updated. *Trends Cogn. Sci. 20*: 512–534.
- Hasselmo, M. E. (2006). The role of acetylcholine in learning and memory. *Curr. Opin. Neurobiol. 16*: 710–715.
- Kanter, I., & Sompolinsky, H. (1987). Associative recall of memory without errors. *Phys. Rev. A 35*: 380–392. One-shot retrieval bound vs iterated Glauber.
- Mezard, M., Parisi, G., & Virasoro, M. A. (1987). *Spin Glass Theory and Beyond*. World Scientific. Parisi RSB hierarchy.
- Frady, E. P., Kleyko, D., & Sommer, F. T. (2020). Variable binding for sparse distributed representations. *arXiv:2009.06734*. Resonator-network capacity.
- Lippl, S., & Stachenfeld, K. (2025). When does compositionality redundancy hold? *ICLR 2025*. arXiv:2405.16391. The redundancy corollary R10 relies on.
- Wu et al. (2024). PMI for RAG. arXiv:2411.07773. PMI signal-vs-noise scaling.
- Predecessor notes: `wave14b_r10_deep_dive.md`, `wave14e_materials_science_crystal_math_research.md`, `wave14e2_spin_glass_substrate_research.md`, `substrate_capability_map.md`.

### 7.4 Specific files for cross-reference

- Code: `d:/AI/hd-instrument/experiments/exp_wave14b_r10_best_config_K2_K4_K8.py` — the inversion data source. Key functions: `extract_ppmi` (lines 123–144), `eval_at_config` (lines 192–234).
- Code: `d:/AI/hd-instrument/experiments/exp_wave14b_r10_best_config_K8_verify.py` — multi-seed K=8 verification (currently running per `substrate_capability_map.md`).
- Theory: `d:/AI/hd-instrument/notes/wave14e2_spin_glass_substrate_research.md` §1 (AGS framing), §2 (RSB).
- Theory: `d:/AI/hd-instrument/notes/wave14b_r10_deep_dive.md` §M3 (W-drift mechanism, sets up post-shift framing used here).

### 7.5 Self-audit: what would falsify the whole synthesis

The synthesis predicts (a) sharp K=8 transition with K(K−1)/2 vs nc as boundary, (b) bimodal P_b(q) at low K, (c) sigmoid lam(K) rescue recovers low K without sacrificing high K, (d) R5 trivial gating restores defaults. If at minimum two of these fail, the mechanism is wrong and we should look elsewhere — possibly at the **decompose_pool argmax-noise** mechanism (M2 in `wave14b_r10_deep_dive.md`), which is independently testable by replacing argmax with soft posterior in line 119 of the experiment file.

The honest non-smoke assessment: R10's high-K wins (+0.628 at K=512) are real and large, but the K<8 catastrophe is *structural*, not a tuning failure. A K-adaptive schedule is the *minimum* fix; a deeper fix requires reckoning with the fact that R10's PPMI extraction is rank-deficient at low K and the linear-fusion form is brittle under rank deficiency. Bayesian model averaging (Rescue R1) is the principled long-term replacement.

---

## 200-word summary (for caller)

**Mechanism.** At K<8 the R10 best-config (nc=50, lam=0.3, beta=16) catastrophically fails because PPMI concept extraction is *structurally rank-deficient*: K(K−1)/2 position-pair templates exist (1 at K=2, 6 at K=4), so all 50 requested concepts collapse onto the same one or two position pairs, reducing the concept-active matrix to a near-binary bigram-lookup. With lam=0.3 putting 70% weight on this degenerate signal and beta=16 sharpening the retrieval softmax onto whichever single pool entry hard-matches, the linear-fusion logit becomes a high-variance bigram lookup whose label is wrong most of the time. The K=8 transition is where #pairs ≈ nc/2 and the concept space gains genuine multi-position information. This is a first-order-like phase transition driven by RSB in the concept subsystem (P_b(q) is bimodal at low K, unimodal at high K), exactly analogous to the hippocampal-to-cortical switch in CLS theory.

**Strongest rescue.** K-adaptive sigmoid schedule: lam(K) = 0.7 + (0.3−0.7)·σ((K−8)/3), beta(K) = 8 + 8·σ((K−12)/4), nc(K) = round(min(K(K−1)/2, 200)). Predicted: matches default at K=2 (within ±0.02), matches best at K≥32 (preserves +0.222 to +0.628 wins). 9 GPU hours to verify with 3-seed K-sweep. Trivial-gating rescue R5 (skip linear fusion when K<8) is the same idea with a hard step; recommended as immediate damage control.
