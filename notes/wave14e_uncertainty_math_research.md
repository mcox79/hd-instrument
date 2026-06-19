# Wave 14e: Substrate-Native Uncertainty Quantification — Math Research

Drafted 2026-05-19. Unbiased math survey: what mathematical objects give
substrate-native uncertainty quantification, given the actual signal
geometry of our predictor?

Substrate setup recap:
- `P(byte | context) = α·P_pool + (1-α)·P_W`, both softmax distributions over 256 bytes.
- `P_W = softmax(β · ⟨readout(context), code_b⟩)`, β=8 by default.
- `P_pool = Σ_i w_i · onehot(target_i)`, where `w_i = softmax(β_pool · sim(query, key_i))`.
- Pool retrieval weights are themselves softmax over the cosine similarities.

So there are two softmaxes in series. That double-softmax structure is
the actual object the calibration math has to digest.

---

## TL;DR — best substrate-internal signal

Predicted ranking by likely correlation with byte accuracy, before any
empirical test:

1. **Top-1 margin of the final mixed P** (`P[top1] − P[top2]`). Bounded
   in [0,1], well-behaved at both temperature extremes, monotone in
   confidence by construction. This is the single most reliable single
   scalar for selective prediction and lines up with Chow's rule
   directly. Expected `r ≈ 0.5–0.7` against per-byte 0/1 correctness.

2. **Pool top-K similarity gap** (`max sim − mean of next K−1 sims`).
   Pre-softmax. Captures whether the pool has a *witness* — a key it
   actually matches. At β_pool=8, a similarity gap of 0.1 already
   dominates the softmax. Gap < 0.02 is essentially "no match". This is
   the right signal for **hard** abstention (pool-as-evidence; see §5).

3. **W-pool agreement** (`argmax P_W == argmax P_pool`). Binary, but
   when it fires the two independent sub-predictors confirm each other
   — empirically the strongest correctness flag in ensemble literature
   (Lakshminarayanan 2017). Expected lift in conditional accuracy of
   10–20 absolute points.

4. **Softmax entropy** `H(P) = −Σ p log p`. Classical but **degraded by
   high β**. At β=8 over 256 bytes the entropy is squashed toward 0
   regardless of true confidence (the temperature collapses it before
   the data does). Use top-1 margin instead.

5. **Pool retrieval entropy** `H(w)`. Better signal than `H(P)` because
   β_pool acts on raw cosine similarities (typically 0.0–0.6), not on
   readout logits. Captures "the pool is split across candidates" vs
   "the pool concentrates on one match". Worth tracking but redundant
   with the top-K gap.

The minimal viable bet (§6) is: top-1 margin **plus** W-pool agreement
covers selective prediction; pool top-K gap covers hard abstention.

---

## Calibration math

### What "calibrated" means

For a probabilistic classifier `f` outputting confidence `p̂ = max_c f(x)_c`
and predicted class `ŷ = argmax_c f(x)_c`, perfect calibration means

```
P( ŷ = y  |  p̂ = p ) = p     for all p ∈ [0,1].
```

When the model says "0.8", it is right 80% of the time. This is
**marginal** calibration in confidence; stronger notions (class-wise,
multicalibration) require more events to estimate.

### Why softmax DNNs are miscalibrated (Guo et al. 2017, arXiv:1706.04599)

Guo et al. measure calibration on modern CNNs and show the
distinctive failure: high-confidence predictions overshoot truth (the
reliability curve sags below the diagonal at p̂ ≈ 0.9–0.99). The
proximate cause is the softmax temperature: cross-entropy training
sharpens logits past the point that matches base-rate frequencies.

Our substrate inherits *exactly* this pathology by construction: β=8
on cos≈1 atoms pushes `P_W[top1]` above 0.99 routinely. The expected
calibration curve will be sag-below-diagonal at the high end. Guo's
fix — single-scalar **temperature scaling** — applies here directly,
because both our sub-distributions are already softmax.

### Expected Calibration Error (ECE)

Partition the test set into M equal-width confidence bins `B_m`:

```
ECE = Σ_m (|B_m| / n) · | acc(B_m) − conf(B_m) |.
```

- `acc(B_m)` = empirical accuracy in bin m,
- `conf(B_m)` = mean predicted confidence in bin m.

Standard M = 15 bins. ECE has no proper-scoring-rule status (it's a
diagnostic, not a loss to optimise), but it's the field default for
*reporting*. Watch the failure mode: with very peaky softmax most
predictions pile into the [0.95, 1.0] bin, hiding miscalibration in
low-density bins; report **adaptive-bin ECE** (equal-count bins) as well.

### Brier score (Brier 1950)

```
Brier = (1/n) Σ_i Σ_c ( f(x_i)_c − 1[y_i = c] )^2.
```

For a 256-way classifier with one-hot label this is
`Σ_c f(x)_c^2 − 2·f(x)_{y} + 1`. Brier is a **proper** scoring rule
(minimized in expectation by the true conditional), decomposes into
calibration + refinement + uncertainty (Murphy 1973), and is bounded.
Brier is the right scalar loss to optimize when tuning calibration
parameters on a held-out set.

### Negative log-likelihood

`NLL = −(1/n) Σ_i log f(x_i)_{y_i}`. Also proper. Sensitive to
overconfidence in a way Brier is not — one badly miscalibrated
prediction at p̂≈1 on a wrong label sends NLL to ∞ (clip to ε to keep
finite). For our substrate, where wrong-byte overshoot is the failure
mode, NLL is the **harshest** loss and the right one for tuning β
post-hoc.

### Temperature scaling — the recommended calibration knob

Holding W and pool fixed, learn a single scalar `T > 0` on a held-out
calibration set by minimizing NLL of

```
P̃(byte) ∝ exp( log(P_mix) / T ).
```

Equivalently, scale our effective β by 1/T. Two big virtues:
- it does not change argmax (selective prediction is unaffected),
- only one parameter, so won't overfit on small calibration sets.

For our setup specifically: temperature scaling will almost certainly
push effective β below 8. Phase B.2 BYTE_BETA sweep already showed the
floor sits around β≈8–16 for *log-loss*, but calibration optimum is
typically lower than likelihood optimum because the latter rewards
overconfidence on correct calls more than it punishes overconfidence
on wrong ones. Expect calibrated T ≈ 1.2–1.8 (i.e. effective β ≈ 4.5–6.6).

### Two-knob alternative — calibrate α and β jointly

Because we have the mixing coefficient α already, calibration can be a
two-parameter fit: pick `(α, T)` minimizing NLL on held-out. This
respects the substrate's structure: α controls *which evidence source*
to weight, T controls *how peaky* the result is. Expect this to
dominate single-T scaling by 5–15% NLL on tasks where one source is
clearly stronger.

---

## Conformal prediction adaptation

### What conformal gives (Vovk–Shafer 2005; Angelopoulos–Bates 2023, arXiv:2107.07511)

Split-conformal prediction takes any black-box predictor `f` and a
held-out calibration set `(X_i, y_i)_{i=1..n}` and returns, for each
new query x, a **prediction set** `C(x) ⊆ {1..256}` such that

```
P( y_new ∈ C(x_new) ) ≥ 1 − α.
```

The guarantee holds **finite-sample**, **distribution-free**, under
exchangeability of calibration and test points. No iid required, just
swap-symmetry.

### Recipe for our substrate

Use the natural conformal score for softmax classifiers
(Angelopoulos–Bates §2.2):

```
s(x, y) = 1 − P̂(y | x).
```

1. Compute `s_i = 1 − P̂(y_i | x_i)` for each calibration point.
2. Let `q̂ = ⌈(n+1)(1−α)⌉ / n` quantile of `{s_i}`.
3. For new x, output `C(x) = { c : P̂(c | x) ≥ 1 − q̂ }`.

That's all. Marginal coverage `≥ 1 − α` is guaranteed.

For α=0.1 and n=1000 calibration bytes: q̂ is roughly the 90th
percentile of calibration scores. If the substrate is well-fitted, q̂
will be small (< 0.3) and most prediction sets will be singletons or
doubletons. If q̂ is large (> 0.7), prediction sets blow up to many
bytes and the substrate is signalling deep uncertainty — that is *the*
informative output.

### Adaptive prediction sets — APS / RAPS

The naive score above gives marginal coverage but **conditional** coverage
can fail (Romano et al. 2020). APS (Romano-Sesia-Candès 2020) and RAPS
(Angelopoulos et al. 2021, arXiv:2009.14193) accumulate the sorted
softmax mass until the true class is included:

```
s_APS(x, y) = Σ_{c : P̂(c|x) ≥ P̂(y|x)} P̂(c|x).
```

This adapts set size to input difficulty: easy x get singletons, hard x
get larger sets *without* losing the coverage guarantee. For our
substrate, where difficulty varies enormously by context, APS is the
better fit.

### Cost

One held-out calibration set. We already split `test_a` / `test_b`;
reserve a third slice (`calib`, ~5–10% of held-out) and the cost is
zero engineering after that. Recompute q̂ whenever W or pool changes
materially.

---

## Selective prediction / abstention

### Chow's rule (Chow 1957, IRE Trans IT-3:3)

Optimal reject rule under a cost model: pay loss 1 for misclassification,
loss `c` for rejection (`0 < c < 1`). The Bayes-optimal action is

```
predict  if  max_c P(c|x) ≥ 1 − c,
reject   otherwise.
```

So with rejection cost c=0.2, accept only when top-1 confidence ≥ 0.8.
This is the cleanest theoretical anchor and what every modern
abstention rule reduces to under a linear cost.

### Geifman-El-Yaniv 2017 (arXiv:1705.08500) — Selection at target risk

Given a target accuracy `1 − ε` among accepted predictions, find the
**lowest** threshold τ on confidence κ(x) such that

```
risk_accepted(τ) = E[ loss · 1{κ(x) ≥ τ} ] / P(κ(x) ≥ τ) ≤ ε,
```

with `risk_accepted` estimated on a held-out set with a Hoeffding-style
upper bound to control finite-sample slack. Their SR algorithm
(Selection with guaranteed Risk) picks τ via binary search and
guarantees `P(risk_accepted ≤ ε) ≥ 1 − δ`.

Direct fit to our substrate: pick κ(x) = `P[top1] − P[top2]`, run SR
on `calib` slice with target ε=0.05, get threshold τ. At inference,
emit prediction iff margin ≥ τ; abstain otherwise. Reportable metrics:
**coverage** (fraction of inputs answered) and **selective accuracy**
(accuracy on the answered subset).

### AUROC for refuse-if-confidence-below-threshold

The signal-quality summary statistic: treat κ(x) as a score, label each
test point by correctness, compute AUROC. AUROC of 0.5 = κ uninformative;
AUROC > 0.8 = κ strongly predicts correctness; AUROC = 1 = perfect
separation. This is the right *signal-quality* metric independent of
threshold choice. Geifman-El-Yaniv use risk-coverage curves but AUROC
is the more standard reporting object.

### Practical threshold structure

Two-stage gate is the cleanest for our setup:
1. **Hard gate** (pool-as-evidence): require `max sim_pool ≥ τ_hard`.
   No pool witness ⇒ abstain regardless of W. Set τ_hard from training
   distribution of `max sim_pool` on correctly-predicted points (e.g.
   5th percentile).
2. **Soft gate** (Chow/Geifman): given pool witness, require
   `P[top1] − P[top2] ≥ τ_soft`. Calibrate τ_soft for target ε.

This is mathematically a conjunction; if either gate fails we abstain.

---

## Pool-as-evidence

### Idea

Every prediction is backed by retrieval weights `(w_i)` over pool
entries. If `max_i w_i < threshold` (no entry dominates) **or**
`max_i sim_i < threshold_sim` (no entry is similar enough), the pool
has not supplied evidence and we should refuse to predict.

This is **not** the same as confidence-based abstention. Confidence
asks "is the model sure?". Evidence asks "did the model see anything
relevant?". For an HDC pool these come apart sharply: at β_pool=8 the
softmax can pile mass on a single pool entry with sim=0.1 (essentially
noise) just because the others are all at sim=0.05. Looking at `w_i`
alone hides that.

### Two distinct thresholds

- **Pre-softmax (hard) threshold τ_sim**: refuse if `max sim_i < τ_sim`.
  This is a **hard** guarantee: no pool entry matches, full stop. We
  control this by the geometry of the HD space — for N=1024 FHRR,
  random vectors have cosine ≈ 1/√1024 ≈ 0.031 with stdev ≈ 0.031. So
  sim_max < 0.1 is statistically indistinguishable from "no match".
  τ_sim = 0.15 gives an effective false-witness rate < 1e-4.

- **Post-softmax (soft) threshold τ_w**: refuse if `max w_i < τ_w`.
  This catches "the pool is split between competing matches". τ_w = 0.5
  means "at least half the mass concentrates on one entry".

Use the conjunction. The pre-softmax threshold is the load-bearing one
for hard guarantees because it operates on the raw geometric witness,
not on a temperature-distorted aggregate.

### Why this is special for HDC

Random-vector substrates give us something that softmax DNNs do not:
**a closed-form null distribution**. For an N=1024 FHRR pool of size M,
the cosine of a query against a random key is approximately Gaussian
with mean 0 and variance 1/N. A single sim of 0.15 has z-score ≈ 4.8,
giving p ≈ 1.5e-6. With M = 10^4 keys and a Bonferroni correction the
adjusted p ≈ 0.015. So `max sim < 0.15` *literally* means "no key in
the pool is detectable above random".

This is sharper than anything dropout-MC or deep-ensemble UQ can give.
It exploits the HDC measure concentration directly.

### Threshold structure summary

```
abstain  if  max sim_pool < τ_sim          # hard, pool empty
       OR  max w_pool  < τ_w             # soft, pool ambivalent
       OR  P[top1] − P[top2] < τ_margin  # soft, mixed predictor ambivalent
```

τ_sim from null distribution; τ_w and τ_margin calibrated on `calib`.

---

## Minimal viable test

### Pipeline

1. Train substrate to standard checkpoint on `train`.
2. Hold out `calib` (1000–5000 bytes) and `test_a` (~50k bytes).
3. For each byte in test_a, log:
   - `entropy_P` = H(final mixed P),
   - `top1_margin` = P[top1] − P[top2],
   - `pool_entropy` = H(w),
   - `topK_gap` = max sim − mean of next K−1 sims (K=4),
   - `wp_agree` = 1[argmax P_W == argmax P_pool],
   - `correct` = 1[argmax P == y].
4. Compute Pearson `r(signal, correct)` and AUROC for each signal.
5. Compute ECE-15 and Brier on the final mixed P; compute again after
   single-T scaling on calib.
6. Compute split-conformal q̂ at α=0.1 on calib; report mean set size and
   empirical coverage on test_a.
7. Pick best signal κ(x). Run Geifman-El-Yaniv SR at ε=0.05 on calib;
   report coverage and selective accuracy on test_a.

### Pass conditions

- Any single signal with `r > 0.5` and `AUROC > 0.75` against per-byte
  correctness.
- Temperature scaling reduces ECE by ≥ 40%.
- Conformal coverage on test_a within ±2% of nominal 90%.
- Selective accuracy at 50% coverage ≥ 10 points above unconditional
  accuracy.

If all four pass, ship as the Wave 14e deliverable. If only signal-r
passes, document and continue — selective prediction works even when
calibration is poor.

### Failure modes to watch

- **Softmax saturation**: if 90%+ of P[top1] values are > 0.99, entropy
  and margin both lose discriminative power. Mitigation: report metrics
  on **logit margin** (pre-softmax) as well as post-softmax margin.
- **Pool zero-shot bytes**: bytes whose context-token has no pool keys.
  Pool entropy is meaningless there; gate on `pool_keys_present`.
- **Calibration set drift**: if `calib` and `test_a` come from
  different distributions (e.g. different text sources), conformal
  coverage misses nominal. Document split provenance.

---

## Hard vs soft guarantees

### Soft (conformal, Chow, Geifman)

- **Statement**: `P(y ∈ C(x)) ≥ 1 − α` *over the random draw of
  calibration + test*.
- **Strength**: distribution-free, finite-sample.
- **Cost**: one held-out set.
- **Failure mode**: exchangeability violation (distribution shift). The
  guarantee silently degrades and you discover it only by external
  audit.

### Hard (pool-as-evidence)

- **Statement**: "Substrate never predicts unless at least one pool key
  has cos similarity ≥ τ_sim with the query." This is a *deterministic*
  property of the predict-or-abstain function, not a probabilistic
  guarantee about outputs.
- **Strength**: holds with probability 1 over any test distribution, no
  exchangeability needed.
- **Cost**: zero, just gate on max sim_pool.
- **Limitation**: doesn't guarantee accuracy when it does predict — only
  that it predicted *for a reason*. To combine with accuracy, stack
  conformal on top of the gated predictor.

### Comparison

The hard guarantee is qualitatively different. Conformal protects
*coverage* (the true label is in the set). Pool-as-evidence protects
*epistemology* (the prediction is grounded in retrieved memory).
Conformal can fail silently under shift; pool-as-evidence can't, because
the geometric null distribution is intrinsic to the substrate.

For a brain-inspired substrate the pool-as-evidence guarantee is
arguably the *more biologically faithful* one: real associative memory
also has a "no recall" mode (you don't make up an answer when the
hippocampus is silent), and that mode is what makes the system
trustworthy under novelty. Conformal alone gives you a coverage
contract but lets the substrate fabricate when retrieval is empty.

### Recommended stack

```
1. Hard gate: refuse if max sim_pool < τ_sim. (hard, pool-as-evidence)
2. Soft gate: refuse if confidence/margin below Geifman τ. (soft, Chow-style)
3. Set output: APS conformal set with α=0.1.       (soft, coverage)
4. Calibration: temperature-scale P̂ pre-conformal.  (proper-scoring)
```

Hard then soft then set. Each layer fixes what the previous can't.

---

## Sources

- Brier (1950), "Verification of forecasts expressed in terms of
  probability", *Monthly Weather Review* 78:1.
- Chow (1957), "An optimum character recognition system using decision
  functions", *IRE Trans IT-3*.
- Murphy (1973), "A new vector partition of the probability score",
  *J. Applied Meteorology* 12.
- Vovk, Gammerman, Shafer (2005), *Algorithmic Learning in a Random
  World*, Springer.
- Guo, Pleiss, Sun, Weinberger (2017), "On Calibration of Modern Neural
  Networks", arXiv:1706.04599.
- Lakshminarayanan, Pritzel, Blundell (2017), "Simple and scalable
  predictive uncertainty using deep ensembles", arXiv:1612.01474.
- Geifman, El-Yaniv (2017), "Selective Classification for Deep Neural
  Networks", arXiv:1705.08500.
- Romano, Sesia, Candès (2020), "Classification with Valid and Adaptive
  Coverage", arXiv:2006.02544.
- Angelopoulos, Bates, Jordan, Malik (2021), "Uncertainty Sets for
  Image Classifiers using Conformal Prediction", arXiv:2009.14193.
- Angelopoulos, Bates (2023), "A Gentle Introduction to Conformal
  Prediction and Distribution-Free Uncertainty Quantification",
  arXiv:2107.07511.
- Naeini, Cooper, Hauskrecht (2015), "Obtaining Well Calibrated
  Probabilities Using Bayesian Binning", AAAI — origin of ECE.
- Kahneman et al. (1982), *Judgment under Uncertainty* — general
  reference for calibration as cognitive primitive.

Substrate-side priors:
- `wave14b_softmax_temperature_theory.md` — derivation of saturation
  knee β_knee ≈ log(M−1)/cos_true; relevant to expected ECE shape.
- `exp_alpha_sweep_charlm.py` — α=0.3 optimum, baseline 2.4994 bpc;
  natural anchor for joint (α, T) calibration sweep.
