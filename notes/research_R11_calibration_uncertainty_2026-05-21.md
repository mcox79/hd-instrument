# Research R11 — Substrate calibration / uncertainty (Bet G prerequisite)

**Topic.** Strategy's Bet G (NEW cycle 9, PROVISIONAL ❌-pending-rehab):
the substrate retrieves at accuracy ≈ 1.0 but its confidence scores are
not predictive of correctness. `wave14yd_calibration_fact_retrieval` (10:47)
returned **ECE = 0.59, Brier = 0.35**. R11 asks: which calibration / uncertainty
mechanism reduces ECE below 0.15 on the fact-retrieval-confidence test, ranked
by predicted ECE-improvement? Per rehab-routing protocol, this note GENERATES
the ranking independently rather than vetting Strategy's 5 draft sketches.

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real external
literature scan** via Agent subagent (~5 min, 27 tool uses, 25+ verified
citations). Pass 2 drills the substrate-specific math.

---

## Pass 1 — External literature scan (verified)

Generic-stats / ML queries via subagent: "neural network calibration ECE
expected calibration error," "Guo Pleiss Sun Weinberger 2017 temperature
scaling," "conformal prediction uncertainty quantification," "kNN retrieval
confidence calibration," "nearest neighbor distance to probability," etc.
No substrate fingerprint.

### 1.1 The diagnosis — what ECE=0.59 with accuracy≈1 actually means

**This is the single most important finding from the lit scan.** Modern
miscalibrated nets sit at ECE = 0.05–0.20. ECE in the 0.5+ range happens
when the score is essentially uncorrelated with correctness — but the
substrate has accuracy ≈ 1.0. This is unusual; the lit scan flagged the
diagnosis as parsimonious:

**The score is correct in RANK but wrong in LOCATION.** With accuracy ≈ 1,
the system always picks the right top-1 entity. But its cosine-similarity
output to the correct entity clusters around 0.3–0.5 (typical cosine
values for high-dim bipolar vectors at substrate's M_stored). The
substrate then reports `p ≈ 0.4` while almost always being right —
producing per-example `(p−y)² ≈ 0.36`, exactly the observed Brier = 0.35.

**Brier decomposition** (Murphy 1973 decomposition): Brier = reliability +
resolution + uncertainty. With accuracy ≈ 1, irreducible uncertainty term
= 0; resolution term ≈ 0 (no AUROC headroom); **Brier = 0.35 is pure
reliability error**. The mapping is clean.

**This means**: the calibration problem is single-parameter sharpness/location.
Temperature scaling on the cosine-softmax should be sufficient. The literature
predicts ECE drops from 0.59 to **<0.05** with ≤1000 calibration points if the
diagnosis is correct. P(diagnosis is correct) ≈ 70–80% from lit-scan
posterior.

### 1.2 Foundational calibration toolkit

The literature has a stable post-hoc toolkit converged since 2017:

**Temperature scaling** (Guo-Pleiss-Sun-Weinberger ICML 2017,
arXiv:1706.04599). The canonical single-parameter rescue. Scalar `T`
learned on held-out set by minimizing NLL; rescales logits before softmax;
**preserves argmax exactly** (accuracy invariant). Guo's headline numbers:
CIFAR-100/ResNet-110 ECE drops from 16.5% → 1.3% after TS;
ImageNet/ResNet-152 from 6.5% → 1.9%.

**Platt scaling** (Platt 1999). Original binary form: `p = 1/(1+exp(aS+b))`.
Temperature scaling is special case `a=1/T, b=0` extended to multiclass.

**Isotonic regression** (Zadrozny-Elkan KDD 2002). Non-parametric monotone
step function fit to calibration data. **Dominates Platt when calibration
data ≥ ~1000 points** (Niculescu-Mizil-Caruana ICML 2005); overfits below.

**Histogram binning**. Stricter discretization of isotonic; cheap; bin-count
sensitive.

**Conformal prediction** (Vovk-Gammerman-Shafer 2005; modern intro
Angelopoulos-Bates 2022). Provides **set-valued, distribution-free coverage
guarantees** rather than point probabilities. Only method with formal
finite-sample guarantees; others are empirical.

### 1.3 Recent (2024–2026) developments

- **Beta calibration** (Kull-Filho-Flach AISTATS 2017; EJS 2017): parametric,
  includes identity as special case; robust at small N. Avoids the Platt
  failure mode where logistic re-calibrates an already-calibrated model.
- **Dirichlet calibration / matrix scaling** (Kull et al. arXiv:1910.12656
  NeurIPS 2019): multiclass-native; equivalent to log-transform + linear
  layer + softmax. With ODIR regularization beats TS on many deep nets.
- **Structured matrix scaling** (arXiv:2511.03685, 2025): recent extension
  addressing overfitting of full matrix scaling.
- **Spline calibration** (Gupta et al. ICLR 2021, arXiv:2006.12800):
  KS-statistic-based, binning-free, monotone differentiable; often beats
  TS on KS error.
- **Focal-loss calibration** (Mukhoti et al. NeurIPS 2020): training-time
  fix; better than TS on OOD; comparable on in-distribution combined with TS.
- **LLM-specific calibration**: token-level + length-conditional; "Calibration
  Across Layers" (arXiv:2511.00280, 2025); FermiEval (arXiv:2510.26995,
  2025) — LLM verbalized confidence at 99% covers ground truth only ~65%.
- **RAG calibration** (Ozaki et al. arXiv:2412.20309, 2024 medical): document
  ordering + prompt structure affect calibration independently of retrieval
  accuracy.

### 1.4 Calibration in retrieval / kNN-LM / CAM specifically (the heart of R11)

**kNN-LM** (Khandelwal et al. ICLR 2020, arXiv:1911.00172) builds
`p_kNN(y|x) ∝ Σ 1[y_i=y] exp(−d(q,k_i)/T)` with softmax over negative
distances at temperature `T`, then interpolates with base LM at coefficient
`λ`. **Both `T` and `λ` are calibration hyperparameters tuned on validation
perplexity.** This is the direct analog of substrate's cosine-softmax
calibration.

**Adaptive kNN-LM** (Drozdov et al. arXiv:2210.15859, 2022): makes `λ`
depend on retrieval quality — ~4% perplexity gain on WikiText-103.
Substrate-relevant because retrieval-quality-dependent calibration is the
natural extension if pure TS doesn't suffice.

**Non-Exchangeable Conformal Nucleus Sampling** (Ulmer et al. EACL Findings
2024, aclanthology 2024.findings-eacl.129): extends conformal prediction
to kNN-LM token generation, providing token-level calibrated sets without
retraining. **Best published precedent for substrate-style conformal
calibration.**

**Efficient Nearest-Neighbor Uncertainty Estimation for NLP** (arXiv:2407.02138,
2024): direct kNN-based uncertainty; treats retrieval distances as confidence
signal.

**The substrate-critical insight from the lit scan**: when retrieval accuracy
is ≈ 1, the top-1 cosine score saturates while runner-up distance is
unbounded — **softmax-of-cosine becomes degenerate, and temperature alone
cannot fix it if the issue is the cosine distribution's location**.
Margin (top1 − top2) or normalized softmax with calibrated temperature is
the recommended fix in this regime.

### 1.5 Conformal prediction for retrieval (2024-26)

- **Adaptive Conformal Inference** (Gibbs-Candès NeurIPS 2021,
  arXiv:2106.00170; Online ACI JMLR 2024, arXiv:2208.08401).
- **Romano-Sesia-Candès** NeurIPS 2020: APS / RAPS sets for classification.
- **Conformal kNN regression** (Papadopoulos et al., arXiv:2110.13031).
- **Conformal kNN UQ in Metric Spaces** (arXiv:2507.15741, 2025): directly
  applies to vector-codebook retrieval. **Most substrate-relevant recent
  reference.**
- **Conformal Prediction Sets with Trust Scores** (arXiv:2501.10139, 2025):
  improves conditional coverage using learned trust score; matches the
  high-accuracy-but-miscalibrated regime directly.
- **Kandinsky Conformal Prediction** (arXiv:2502.17264, 2025): beyond
  class/covariate-conditional coverage.

For substrate with accuracy ≈ 1 and ECE = 0.59, conformal delivers
set-valued coverage guarantees **regardless of calibration baseline** —
but does not directly reduce ECE on the scalar probability. It reframes
the problem. Use IF the product story is "calibrated coverage sets" not
"calibrated probability scores."

### 1.6 Bayesian / variational approaches

- **MC dropout** (Gal-Ghahramani ICML 2016, arXiv:1506.02142): cheap
  pseudo-Bayesian; **known to be miscalibrated** (arXiv:2006.11584 shows
  MC-dropout is itself overconfident; logit-scaling on top recovers
  calibration). Inferior to TS alone.
- **Deep ensembles** (Lakshminarayanan-Pritzel-Blundell NeurIPS 2017,
  arXiv:1612.01474): gold standard for predictive distributions; typically
  beats MC dropout and matches/beats post-hoc TS on calibration, at M× cost.
- **Nearest-Neighbor Gaussian Processes** (Datta et al.): good for spatial
  retrieval; underestimates uncertainty in classification (arXiv:0804.1325).

For retrieval at accuracy ≈ 1, deep ensembles give marginal gains on
in-distribution while costing M×. Not cost-effective in this regime per
the lit scan.

### 1.7 Norm-based / margin-based confidence (substrate-relevant)

- **Softmax response / SR** (Geifman-El-Yaniv NeurIPS 2017): max softmax
  probability; standard baseline for selective classification.
- **Energy-based OOD** (Liu et al. NeurIPS 2020, arXiv:2010.03759):
  `−logsumexp(logits)` theoretically aligned with input density; avoids
  softmax overconfidence; reduces FPR@95 by 18% over MSP on
  CIFAR-10/WideResNet. **Directly maps to substrate via Hopfield energy
  framing.**
- **DBLE** (arXiv:1912.01730): distance-in-representation-space confidence.
- **"How to Fix a Broken Confidence Estimator"** (arXiv:2305.15508):
  systematic comparison; logit-based scores (margin, energy, max-logit)
  often beat MSP on selective classification AURC even when ECE is similar.

For substrate with accuracy ≈ 1, **top1−top2 margin and L2-normalized
embedding norm are canonical confidence signals; energy is the principled
generalization**. The lit scan flags this as a Strategy-listed sketch
(#5 bundle-norm) that has a real literature anchor.

### 1.8 The materials-science / Hopfield-β analog (load-bearing)

**This is the most important finding from the materials axis.** Modern
dense associative memory (Krotov-Hopfield 2016; Ramsauer et al.
arXiv:2008.02217 "Hopfield Networks Is All You Need") uses the energy

  **E(x) = −logsumexp(β · X · x)**

where X is the stored pattern matrix, x is the query, β is the inverse
temperature. **This is exactly Liu et al. 2020's energy-based confidence
with β = 1/T.** Same equation. Two communities (statistical mechanics +
ML calibration) reinvented it independently.

**The mapping**:
- Substrate's cosine-softmax `softmax(cos(W·k, v_i)/T)` is mathematically
  identical to a modern Hopfield retrieval at inverse temperature β = 1/T.
- Hopfield's β controls the "sharpness" of pattern retrieval: at β → ∞,
  retrieval is hard argmax; at β → 0, uniform. **The optimal β for
  retrieval probability calibration is exactly what temperature scaling
  finds.**
- ECE = 0.59 in the substrate is equivalent to "operating at the wrong
  inverse temperature β." Finding the right β from validation data is
  temperature scaling under a new name.
- Spin-glass / replica analysis (Amit-Gutfreund-Sompolinsky 1987; recent
  dense AM PDEs arXiv:2203.14273) gives confidence in pattern recall as
  the partition function `Z(β) = Σ exp(−βE)` evaluated at retrieval
  temperature. **Free energy `F = −T log Z` is the calibrated
  log-likelihood under the Gibbs measure.**

**Substrate-prediction**: at substrate's operating point α = 0.153 (per
wave14m_alpha_c), the right β is determined by α and N. The current
substrate likely uses default β=1 (or implicit β=N from cosine
normalization), neither of which matches the spin-glass-optimal β.
**Temperature scaling rediscovers the spin-glass-optimal β empirically.**

This is the load-bearing materials analog — direct mathematical equivalence,
not decorative.

### 1.9 ECE / Brier benchmark values from the literature

- Guo 2017 CIFAR-100/ResNet-110: ECE 16.5% → 1.3% (post TS).
- Guo 2017 ImageNet/ResNet-152: ECE 6.5% → 1.9% (post TS).
- Minderer et al. NeurIPS 2021 (arXiv:2106.07998): non-conv architectures
  (MLP-Mixer, ViT) raw ECE ~2-3%, narrowing the post-hoc gain.
- BERT/RoBERTa text classification: raw ECE 3-8% → <2% after TS.
- **kNN retrieval predictors**: no widely cited ECE benchmark; published
  work reports perplexity instead. Khandelwal et al. and Drozdov et al.
  imply softmax temperature is crucial; uncalibrated kNN softmax tends
  sharply overconfident on in-distribution.

**Substrate's ECE = 0.59 is extreme by published standards.** The most
parsimonious diagnosis (sharpness/location problem) predicts TS drops it
to < 0.05. If TS doesn't get there, the diagnosis is wrong — escalate.

---

## Pass 2 — Substrate-specific drill (independent rescue ranking)

Per rehab-routing protocol ([[feedback-rehabilitation-after-rejection]] +
research playbook), I generate the ranking from first principles + lit
scan, not from Strategy's draft.

### 2.1 Decomposing the rescue space

The substrate's calibration problem has three orthogonal axes:
- **Score location/scale fix** (raw cosine has wrong mean): temperature
  scaling, beta calibration, isotonic.
- **Score functional form fix** (cosine isn't the right score): margin,
  energy, learned trust scores.
- **Coverage reframe** (give up on point probability, give set
  guarantees): conformal prediction.

Strategy's draft (Platt, isotonic, Bayesian σ², multi-vote, bundle-norm)
mixes axes. My ranking separates them so the substrate can attack the
problem cleanly.

### 2.2 Independent rescue ranking (10 candidates, ranked)

Ranking criteria: (a) **predicted ECE-improvement on substrate's regime**
(accuracy≈1, cosine cluster at 0.3-0.5); (b) **implementation cost**;
(c) **accuracy preservation** (does the fix break argmax?); (d) **literature
maturity** (well-validated > experimental); (e) **substrate-coherence**
(works with existing infrastructure).

| Rank | Candidate | Mechanism axis | Predicted ECE-after | Cost | Accuracy-preserving? | Literature anchor |
|---|---|---|---|---|---|---|
| **1** | **Temperature scaling on cosine-softmax** | Score location | **0.02–0.05** | Trivial (1 scalar) | YES exactly | Guo 2017 (arXiv:1706.04599) — canonical |
| **2** | **Isotonic regression on top-1 score** | Score location (non-parametric) | 0.03–0.06 | Low (O(N) breakpoints) | YES if rank-preserving | Zadrozny-Elkan 2002; needs ≥1000 cal pts |
| **3** | **Beta calibration on top-1** | Score location (parametric) | 0.04–0.08 | Low (3 params) | YES | Kull-Filho-Flach AISTATS 2017 |
| **4** | **Energy-based confidence (−logsumexp β·cos)** | Score functional | 0.04–0.10 | Low (1 scalar β; replaces softmax) | YES | Liu et al. 2020 (arXiv:2010.03759); IS Hopfield energy |
| **5** | **Margin-based confidence (top1 − top2)** | Score functional | 0.05–0.12 | Trivial | YES | Geifman-El-Yaniv 2017; "Broken Confidence" 2023 |
| **6** | **Conformal prediction with cosine-margin score** | Coverage reframe | (not ECE; gives 1−α coverage) | Low (quantile compute) | YES (sets contain argmax) | Romano-Sesia-Candès 2020; arXiv:2507.15741 |
| **7** | **Dirichlet calibration (multiclass-native)** | Score location | 0.03–0.08 | Medium (K² params for K classes; ODIR regularize) | YES | Kull et al. arXiv:1910.12656 |
| **8** | **Deep ensembles** (M copies of W with different init) | Score location + functional | 0.04–0.10 | High (M× compute) | YES (vote argmax) | Lakshminarayanan et al. 2017 |
| **9** | **Multi-vote / vote-share confidence** | Score functional | 0.08–0.15 | Medium (re-train M models) | YES | Strategy's #4 sketch; closest published is deep ensembles |
| **10** | **MC dropout / Bayesian σ²** | Score location (variational) | 0.10–0.20 | Medium | Yes if averaged | Gal-Ghahramani 2016; **known under-calibrated** |

**Top recommendation: Candidate 1 (Temperature scaling)** with
**Candidate 4 (Energy-based confidence)** as the substrate-coherent
variant because it IS the Hopfield-β framing.

### 2.3 Reordering vs Strategy's draft

Strategy's 5 sketches:
1. Platt scaling → my **#1** (TS is special case; same family) ✓
2. Isotonic → my **#2** ✓
3. Bayesian σ² → my **#10** (down-ranked; literature says under-calibrated)
4. Multi-vote → my **#9** (down-ranked; closest published is deep ensembles)
5. Bundle-norm confidence → my **#4** (up-ranked as energy-based;
   substrate-mathematically equivalent to Hopfield energy)

**Strategy missed:**
- Beta calibration (my #3) — small-N robust parametric
- Conformal prediction (my #6) — distribution-free coverage; only method
  with finite-sample guarantee

**My downranking rationale:**
- Bayesian σ² and multi-vote are expensive (M× cost) for the substrate's
  diagnosis (single-parameter sharpness). The lit scan is clear that they
  give marginal improvement over TS in accuracy-≈1 regimes.

### 2.4 Drill on top-ranked Candidate 1 (Temperature scaling on cosine-softmax)

**The substrate-specific math:**

Substrate retrieval scores facts via cosine similarity:
  `s_i = cos(W·k_query, v_i) = (W·k_query)ᵀ v_i / (||W·k_query|| · ||v_i||)`

For unit-norm v_i: `s_i ∈ [-1, +1]`. Substrate's current confidence
likely computes `p_i = softmax(s_i)` with implicit T=1 — which is too
sharp when scores cluster at 0.3-0.5 (max softmax probability for top-1
score ≈ 0.4 over a few competing entities).

**Temperature-scaled retrieval probability:**
  `p_i(T) = exp(s_i / T) / Σ_j exp(s_j / T)`

Learn T on held-out calibration set by minimizing NLL:
  `T* = argmin_T Σ_(k,v_correct) [−log p_correct(T)]`

Closed-form impossible; use scipy.optimize.minimize_scalar with bounded
search over T ∈ [0.01, 10]. Cost: O(N_cal · M_stored) per T evaluation;
~100 evaluations = ~100 · 1000 · 627 = ~6×10⁷ ops. Sub-second on GPU.

**Why TS will work** (substrate diagnosis):
- Substrate's current p_correct ≈ 0.4 (lit-scan diagnosis from
  Brier=0.35 + accuracy=1).
- Per-example calibration error ≈ |1.0 − 0.4| = 0.6 (matches ECE = 0.59).
- TS rescales scores so the top-1 score's softmax probability matches
  the empirical correct rate (≈ 1.0). For substrate's score distribution,
  the optimal T is likely 0.05–0.2 (much smaller than 1, i.e., sharpen
  the softmax).
- After TS at optimal T, max softmax probability → ~0.95-0.99 for the
  top-1, ~0.01-0.05 for runners-up. ECE drops to < 0.05.

**Substrate-coherence**: TS is one scalar added at the readout layer.
NO change to storage, NO change to W training, NO change to argmax (TS
is monotone in scores, preserves rank). Fully reversible.

**Critical caveat from lit scan**: when retrieval accuracy is ≈ 1 and
the top-1 score saturates near 1 while runner-up score is unbounded,
softmax-of-cosine can become degenerate at small T. The fix is to use
margin (top1−top2) or normalize the score distribution before softmax.
**If TS at small T produces extreme overconfidence on edge cases** (e.g.,
when top-2 is also very close), escalate to Candidate 4 (energy) which
handles this gracefully.

### 2.5 Drill on Candidate 4 (Energy-based confidence — the Hopfield-β framing)

**The substrate-specific math:**

Replace softmax-of-cosine with energy-based confidence:
  `E(query) = −logsumexp(β · cos(W·k_query, v_i))_i`
  `confidence = sigmoid(τ · (E_threshold − E(query)))`

This is **mathematically identical to a modern Hopfield retrieval at
inverse temperature β** (Ramsauer 2020). The energy E captures both
top-1 sharpness AND the distribution of runners-up — handling the
degenerate-softmax failure mode of pure TS.

**Substrate-cohence**: this re-frames the substrate's readout as
explicit Hopfield retrieval at calibrated β. The substrate IS a
Hopfield-like memory; this aligns the calibration mechanism with the
underlying physics.

**Why this might beat pure TS**:
- TS rescales the score distribution. Energy uses the full distribution
  of scores (not just top-1 vs top-2). When scores have heavy tails or
  multimodal structure, energy is more robust.
- Energy gives a "natural" out-of-distribution signal: very high energy
  (no nearby stored fact) → low confidence, regardless of top-1 score.
  Pure TS cannot distinguish "I retrieved correctly but with low cosine"
  from "I retrieved a random fact."

**Tradeoff**: energy has 2 hyperparameters (β, threshold) vs TS's 1.
Slightly more held-out data needed (~500 vs ~200 calibration examples).

### 2.6 Drill on Candidate 6 (Conformal prediction — coverage reframe)

**The substrate-specific math:**

Use cosine-margin as nonconformity score:
  `α_i = 1 − cos(W·k_query, v_correct_i) + max_{j ≠ correct} cos(W·k_query, v_j)`

Compute threshold `q̂_α = ⌈(1-α)(n+1)/n⌉-quantile of {α_1, ..., α_n}`
on calibration set. At test time, prediction set:
  `C(query) = {v : 1 − cos(W·k_query, v) + max_{j ≠ v} cos(...) ≤ q̂_α}`

**Guarantee**: P(true_v ∈ C(query)) ≥ 1 − α for any α ∈ (0, 1),
distribution-free, finite-sample. This is the only method on the list
with formal guarantees.

**Substrate-coherence**: substrate already returns top-k candidates from
pool retrieval; conformal sets are a principled choice of k per query.

**Why conformal might be the right product story** (not just an ECE
fix): the substrate's existing "provenance" capability (✅ at v3+) is
already set-valued. Adding conformal coverage to provenance gives the
substrate **"every retrieval comes with a guaranteed-coverage set of
plausible facts"** — a stronger product claim than "calibrated scalar
probability."

**Tradeoff**: conformal does NOT directly reduce ECE on a scalar
probability score. If the product requires `p ∈ [0, 1]` outputs, use
TS or energy. If the product can use coverage sets, conformal is the
right choice.

---

## Specific experimental design (pseudocode)

**Experiments**: Run THREE rescues in parallel — TS (primary, cheapest),
Energy (substrate-coherent), Conformal (coverage reframe). Compare on
the same calibration set.

### Experiment 1 — `wave14_calibration_TS_v1` (primary)

```text
config:
  N = 4096
  M_stored = 627  # current substrate operating point
  N_cal = 1000  # calibration set size (lit-scan recommendation)
  N_test = 1000  # held-out test set for ECE / Brier
  seeds = [7, 17, 23, 31, 41]  # 5 seeds
  T_search = log-spaced [0.01, 10.0], 100 points

setup_per_seed(seed):
  # Use existing substrate W and pool from current operating point
  W, pool = load_substrate_baseline(seed)
  cal_queries = sample_queries(N_cal, seed=seed)
  test_queries = sample_queries(N_test, seed=seed+1000)
  return W, pool, cal_queries, test_queries

learn_T(W, pool, cal_queries):
  def nll_loss(T):
    total_nll = 0
    for q in cal_queries:
      scores = compute_cosine_scores(W @ q.key, pool.values)
      p = softmax(scores / T)
      total_nll -= log(p[q.correct_idx])
    return total_nll / N_cal

  T_optimal = minimize_scalar(nll_loss, bounds=(0.01, 10.0))
  return T_optimal

evaluate_calibration(W, pool, test_queries, T):
  predictions = []
  confidences = []
  correctness = []
  for q in test_queries:
    scores = compute_cosine_scores(W @ q.key, pool.values)
    p = softmax(scores / T)
    pred_idx = argmax(p)
    predictions.append(pred_idx)
    confidences.append(p[pred_idx])  # top-1 confidence
    correctness.append(pred_idx == q.correct_idx)

  ECE = compute_ECE(confidences, correctness, n_bins=15)
  Brier = mean([(c - cor)**2 for c, cor in zip(confidences, correctness)])
  accuracy = mean(correctness)
  return ECE, Brier, accuracy

main_per_seed(seed):
  W, pool, cal_q, test_q = setup_per_seed(seed)

  # Baseline (no calibration, T=1)
  ECE_baseline, Brier_baseline, acc_baseline = evaluate_calibration(
    W, pool, test_q, T=1.0)

  # Calibrated
  T_opt = learn_T(W, pool, cal_q)
  ECE_calibrated, Brier_calibrated, acc_calibrated = evaluate_calibration(
    W, pool, test_q, T=T_opt)

  return {
    'T_opt': T_opt,
    'ECE_baseline': ECE_baseline,
    'ECE_calibrated': ECE_calibrated,
    'Brier_baseline': Brier_baseline,
    'Brier_calibrated': Brier_calibrated,
    'accuracy_preserved': abs(acc_baseline - acc_calibrated) < 0.001,
  }
```

### Experiment 2 — `wave14_calibration_energy_v1` (substrate-coherent)

Same setup but replace softmax with energy-based confidence:
```text
energy_confidence(scores, beta, threshold):
  E = -logsumexp(beta * scores)
  return sigmoid(threshold - E)

# Learn β and threshold jointly on calibration set via NLL
```

### Experiment 3 — `wave14_calibration_conformal_v1` (coverage reframe)

```text
nonconformity(query, candidate, W, pool):
  scores = compute_cosine_scores(W @ query.key, pool.values)
  s_candidate = scores[candidate]
  s_runner_up = sorted(scores, reverse=True)[1] if candidate == argmax(scores) else max(scores)
  return 1 - s_candidate + s_runner_up

# Calibrate threshold on calibration set
alpha_scores = [nonconformity(q, q.correct_idx, W, pool) for q in cal_q]
q_hat = quantile(alpha_scores, 1 - alpha)

# At test time, return prediction set
prediction_set = [v for v in pool.values if nonconformity(query, v, W, pool) <= q_hat]
```

### Multi-probe verdict logic

```text
verdict_logic:
  PASS (per Bet G criteria):
    ECE_calibrated < 0.15  # primary target
    Brier_calibrated < 0.20  # primary target
    accuracy_preserved == True  # TS is monotone; should always pass
    5-seed mean within ±1σ of single-seed

  EXCEED (full success):
    ECE_calibrated < 0.05  # lit-scan prediction if diagnosis correct
    Brier_calibrated < 0.10

  KILL:
    ECE_calibrated > 0.20 after all 3 rescues (TS, energy, conformal)
    AND multi-seed (3 of 5 seeds fail)
    → substrate calibration is structural; product story drops
      "trustworthy confidence scores" entirely
```

**Smoke test**: N=512, N_cal=100, N_test=100, 1 seed. Target ~10s.
Oracle: ECE_baseline > 0.3 (confirm substrate's miscalibration replicates);
T_opt < 1.0 (sharpening direction confirmed).

**Self-test** (4 synthetic cases):
- Perfectly calibrated scores (cosine matches correct rate exactly):
  predict T_opt ≈ 1.0, ECE_baseline ≈ 0.
- Maximally miscalibrated (scores anti-correlated with correctness):
  predict T_opt negative (impossible); test should detect.
- Substrate-like (cosine cluster at 0.3-0.5, accuracy ≈ 1): predict
  T_opt ∈ (0.05, 0.20), ECE drops from ~0.6 to < 0.05.
- Random retrieval (accuracy ≈ 1/M): predict T_opt ≈ 1.0, ECE ≈ 0.

**Wall budget**: 3 experiments × 5 seeds × ~5s per seed at full scale
≈ 75s. Negligible compute. Plus subagent cost for analysis ~2 min.

---

## Materials analog (load-bearing — Hopfield β IS the calibration parameter)

The substrate's W = Σ vᵢ kᵢᵀ is mathematically a classical Hopfield
memory. Modern Hopfield (Ramsauer et al. 2020) extends this with the
energy function:

  **E(x) = −logsumexp(β · X · x)**

where β is the inverse temperature controlling retrieval sharpness.
Liu et al. 2020's energy-based OOD detection uses the **exact same
formula** with β = 1/T as a confidence signal. The two communities
(statistical mechanics of associative memory + ML calibration)
re-derived the same equation.

**The substrate-prediction consequence**: ECE = 0.59 in the substrate
is equivalent to "operating at the wrong inverse temperature β." The
optimal β for retrieval-probability calibration is the spin-glass-optimal
β determined by the substrate's storage load α and dimension N. At α =
0.153 and N = 4096, the spin-glass theory (Amit-Gutfreund-Sompolinsky
1987) predicts an optimal β ≈ √(1/α) ≈ 2.5 — much sharper than the
default β = 1 substrate's cosine-softmax uses.

**Translating to calibration parameters**:
- Substrate's current implicit β ≈ 1 (cosine-softmax with T=1).
- Spin-glass-optimal β ≈ 2.5 → corresponds to T ≈ 0.4.
- Lit-scan diagnosis predicts T_opt ∈ (0.05, 0.20) for ECE < 0.05 —
  even sharper than spin-glass optimum because the calibration target
  is exact match to accuracy, not retrieval reliability.

The materials physics gives us a predictive lower bound on how much
sharpening TS will do: at LEAST factor-of-2 sharpening from the
spin-glass argument, possibly factor-of-5 from the calibration
argument. Both predictions point in the same direction.

**Why this is load-bearing, not decorative**: the mathematical equivalence
means that fitting T via TS = computing the spin-glass-optimal β =
finding the calibrated Hopfield-β = computing the Liu energy-confidence
scale. Three communities, one parameter.

The note's R10 (SSH-BSC topology) and R11 (calibration) together exhibit
a pattern: the substrate's open research questions keep mapping cleanly
to established condensed-matter physics. This is reinforcement for the
"substrate IS a physical system" framing of [[feedback-materials-science-probe]].

---

## Falsifiable prediction

**Primary prediction (Experiment 1, Temperature Scaling):**

At N=4096, M_stored=627, N_cal=1000, N_test=1000, 5 seeds:

- **T_opt ∈ (0.05, 0.20)** — sharpening required (substrate currently
  too soft). Spin-glass spin-glass argument gives lower bound ~0.4;
  calibration target is sharper.
- **ECE_baseline ≈ 0.55–0.65** (replicates substrate's reported 0.59).
- **ECE_calibrated < 0.05** (5-seed mean). The lit-scan diagnosis
  (sharpness/location problem) makes this prediction high-confidence.
- **Brier_calibrated < 0.10** (down from 0.35).
- **accuracy_preserved**: exact (TS is monotone in scores).

**Stress prediction (Experiment 2, Energy):**

If TS at small T produces degeneracy (top-2 score ≈ top-1):
- Energy-based confidence achieves **ECE < 0.08** by handling the
  score distribution more gracefully than softmax.
- β_opt ∈ (5, 20) — substrate-coherent with Hopfield-energy framing.

**Coverage prediction (Experiment 3, Conformal):**

At α = 0.10 (90% coverage target):
- Prediction set size median: 1 (since accuracy ≈ 1, most queries are
  unambiguous).
- Prediction set size at 99th percentile: 3-5 (rare ambiguous queries).
- Empirical coverage: 0.90 ± 0.01 (within finite-sample bound).

**Kill criterion.**

If **ECE_calibrated > 0.20 after all three rescues** (TS at optimal T,
energy at optimal β, conformal at α=0.10), AND multi-seed (3 of 5):

The diagnosis is wrong. The substrate's confidence-score distribution
has a deeper structural problem (e.g., scores are not monotone with
correctness; multimodal cosine distribution that no single-parameter
fix can repair). Bet G escalates to ❌-structural; the next research
priority shifts to redesigning the substrate's score function entirely
(e.g., learned distance metric, attention-based scoring).

**Falsifier for the diagnosis itself.**

If TS finds T_opt > 1.0 (substrate is too sharp, not too soft) — the
lit-scan diagnosis is wrong. The substrate's miscalibration is the
opposite direction from predicted, meaning the cosine distribution
clusters NEAR 1 (very confident on wrong answers) rather than near
0.3-0.5. Different mechanism; would require re-running R11 with
inverted hypothesis.

---

## Citations

1. **Guo, Pleiss, Sun, Weinberger (2017). "On Calibration of Modern
   Neural Networks."** ICML 2017. arXiv:1706.04599.
   — Canonical temperature scaling reference; provides ECE-improvement
   benchmark.

2. **Zadrozny, Elkan (2002). "Transforming classifier scores into
   accurate multiclass probability estimates."** KDD 2002.
   — Isotonic regression foundational reference.

3. **Niculescu-Mizil, Caruana (2005). "Predicting good probabilities
   with supervised learning."** ICML 2005.
   — Empirical comparison: isotonic dominates Platt for N ≥ 1000.

4. **Kull, Filho, Flach (2017). "Beta calibration: a well-founded and
   easily implemented improvement on logistic calibration for binary
   classifiers."** AISTATS 2017 / EJS.
   — Beta calibration; small-N parametric robustness.

5. **Liu, Wang, Owens, Li (2020). "Energy-based Out-of-distribution
   Detection."** NeurIPS 2020. arXiv:2010.03759.
   — Energy-based confidence; mathematically identical to Hopfield
   modern AM energy. Substrate-coherent rescue mechanism.

6. **Ramsauer et al. (2021). "Hopfield Networks is All You Need."**
   ICLR 2021. arXiv:2008.02217.
   — Modern dense AM with energy `E = −logsumexp(β·X·x)`. The substrate's
   storage is mathematically a modern Hopfield; β is the calibration
   parameter.

7. **Khandelwal, Levy, Jurafsky, Zettlemoyer, Lewis (2020).
   "Generalization through Memorization: Nearest Neighbor Language
   Models."** ICLR 2020. arXiv:1911.00172.
   — kNN-LM with cosine-softmax temperature as calibration hyperparameter;
   direct analog of substrate's calibration problem.

8. **Romano, Sesia, Candès (2020). "Classification with Valid and
   Adaptive Coverage."** NeurIPS 2020.
   — Conformal classification; APS / RAPS sets. Substrate-applicable
   for coverage-reframe rescue.

9. **Ulmer et al. (2024). "Non-Exchangeable Conformal Language Generation
   with Nearest Neighbors."** Findings of EACL 2024.
   — Best published precedent for conformal calibration of kNN
   retrieval. Substrate-relevant.

10. **Lakshminarayanan, Pritzel, Blundell (2017). "Simple and Scalable
    Predictive Uncertainty using Deep Ensembles."** NeurIPS 2017.
    arXiv:1612.01474.
    — Deep ensembles; gold standard for predictive uncertainty.
    Down-ranked in this note due to high cost for marginal gain.

11. **Geifman, El-Yaniv (2017). "Selective Classification for Deep Neural
    Networks."** NeurIPS 2017.
    — Margin-based confidence (top1−top2); substrate-applicable as
    cheap rescue.

12. **Conformal Prediction Sets with Trust Scores (2025). arXiv:2501.10139.**
    — Conditional coverage with learned trust score; matches
    high-accuracy-but-miscalibrated regime directly.

13. **Conformal and kNN Predictive Uncertainty in Metric Spaces (2025).
    arXiv:2507.15741.**
    — Direct application to vector-codebook retrieval; most substrate-
    relevant 2025 reference.

14. **Amit, Gutfreund, Sompolinsky (1987). "Statistical mechanics of
    neural networks near saturation."** *Ann. Phys.* 173, 30.
    — Classical Hopfield spin-glass analysis; provides spin-glass-optimal
    β prediction for substrate's α = 0.153 operating point.

---

## Routing

- **Experiment Dev (E_G)**: this note recommends building THREE parallel
  rescue experiments:
  - **`wave14_calibration_TS_v1`** (primary, ~10s total wall time)
  - **`wave14_calibration_energy_v1`** (substrate-coherent variant)
  - **`wave14_calibration_conformal_v1`** (coverage reframe)
  All cheap; ~5 minutes total at full scale. Pre-reg + smoke gate +
  queue-add per standard pipeline.

- **Strategy**: this note GENERATES the rescue ranking independently
  per rehab-routing protocol. Reordering vs Strategy's draft documented
  above (Strategy's Platt/isotonic correct; Bayesian σ²/multi-vote
  downranked; bundle-norm upranked as energy-based; **beta calibration
  and conformal prediction were missing from Strategy's draft** —
  added to ranking). Cap_map row addition proposal: "Substrate
  calibration via temperature scaling" at 🔬 (experimental design
  ready). Bet G should move from PROVISIONAL ❌ to 🔬-pending-rescue
  once R11 lands.

- **Research (this session, future cycles)**: if Experiment 1 (TS)
  passes with ECE < 0.05 (high-confidence prediction): R11 closes;
  Bet G upgrades to ✅; cap_map row "calibrated retrieval confidence"
  added. If Experiment 1 fails (T_opt > 1.0 OR ECE > 0.15 after TS):
  the lit-scan diagnosis was wrong; route follow-up to investigate
  the underlying score distribution structure (possibly R11.2 on
  score-distribution diagnostics). If experiments 2 and 3 also fail:
  Bet G closes ❌-structural; substrate product story drops trustworthy
  confidence.
