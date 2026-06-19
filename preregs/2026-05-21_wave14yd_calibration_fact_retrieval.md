# Pre-registration: wave14yd_calibration_fact_retrieval

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14yd_calibration_fact_retrieval.py](../experiments/exp_wave14yd_calibration_fact_retrieval.py)
Priority source: cap_map Tier-3 KILLER "Calibration / uncertainty"
(UNSURE) — does the substrate know when it doesn't know?
Author: experiment_dev session, pipeline tick 15

## Why

Critical product question: when the substrate's argmax cleanup returns
a fact, can we trust the **max softmax probability** as a calibrated
confidence? If yes, the substrate "knows when it doesn't know" and can
abstain or hedge on low-confidence predictions. If no, all outputs come
with equal apparent confidence and the user can't tell good from bad.

The earlier `wave14calibration_v2` tested soft-trace bundle calibration
(`Brier_soft=0.294 > Brier_clipped=0.212`, verdict `CAL_NO_GAIN`). That
was a different question: bundle-side calibration of HRR-style soft
counting. This experiment tests **fact-retrieval-side calibration**: when
we probe a stored key, does the softmax confidence on the cleanup output
correlate with whether the retrieved value is correct?

Test design: build M facts (Kerdock keys, since Kerdock is the validated
config). For each fact i, probe with k_i (exact) or with k_i + Hamming
perturbation (paraphrase). Compute softmax over value codebook; record
(max_softmax, argmax_correct) pairs. Bin by confidence, compute
calibration metrics.

## Hypothesis

At N=4096, M_stored=N=4096 Kerdock keys, 3 seeds, with mixed exact and
paraphrase queries (varying Hamming radii to spread the confidence
distribution):

- Substrate softmax confidence is **at least somewhat calibrated** —
  ECE < 0.15 (mildly miscalibrated or better).
- Confidence and accuracy positively correlate (slope of accuracy vs
  confidence bin > 0).
- High-confidence predictions (max_softmax > 0.9) are mostly correct
  (accuracy in top bin > 0.95).

## Multi-probe success criteria

Three calibration metrics:
1. **ECE (Expected Calibration Error)** with 10 equal-width bins on [0, 1]
2. **Brier score** = mean (predicted_probability - one_hot_true)²
3. **Top-bin accuracy** — fraction correct among predictions with
   max_softmax > 0.9

Verdict thresholds:
- ECE < 0.05 AND top-bin > 0.95: WELL_CALIBRATED
- 0.05 ≤ ECE < 0.15: MARGINAL
- ECE ≥ 0.15: POOR

## Kill criterion

If confidence is anti-correlated with accuracy (low-confidence
predictions are MORE correct than high-confidence) — verdict
`CALIBRATION_INVERTED`. Indicates a fundamental bug or surprising
substrate property.

## Verdict labels (5)

- `CALIBRATION_WELL` — ECE < 0.05, substrate confidence tracks accuracy
- `CALIBRATION_MARGINAL` — 0.05 ≤ ECE < 0.15
- `CALIBRATION_POOR` — ECE ≥ 0.15
- `CALIBRATION_INVERTED` — accuracy DROPS with confidence (kill)
- `CALIBRATION_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. At smoke scale, mean accuracy over all probes ≥ 0.70 (substrate
   actually stores facts)
2. Confidence distribution spans a meaningful range (max − min > 0.1)
   so binning is informative
3. ECE in valid range [0, 1]

## Pre-mortem (3 failure causes)

1. **Confidence distribution is too narrow** — if every probe gives
   nearly identical softmax confidence, calibration metrics are
   meaningless. With exact-key probes: confidence likely high and
   tight. With paraphrase probes at varying h: confidence spread.
   Use a mix: half exact, half h=8 paraphrase, half h=16 paraphrase.

2. **BETA scaling masks true confidence** — softmax(BETA * sims) at
   high BETA collapses to argmax-one-hot regardless of similarity gap.
   At BETA=1, softmax is closer to actual confidence. Test at BETA=1
   (no scaling) vs BETA=8 (substrate default). Report both.

3. **Binning artifacts at high accuracy** — if substrate is very
   accurate (95%+) most bins are empty; ECE dominated by one bin.
   Mitigation: report bin counts; if low-confidence bin has < 10
   samples, note in verdict_msg.

## Operational definition

- N = 4096
- M_stored = 4096 Kerdock keys (from v3 4-coset codebook)
- 3 seeds
- For each seed: M facts, probe each with:
  - exact key (k_i)
  - h=4 paraphrase
  - h=8 paraphrase
  - h=16 paraphrase
- Total per seed: 4M = 16384 probes
- BETA = 8.0 (substrate's operating value; matches wave14d_icl_via_pool, etc.)
  At BETA=1 the softmax over M values is too flat for meaningful confidence
  spread (max softmax ~ 1/M); BETA=8 gives the substrate's actual confidence
  distribution as used in production.
- ECE with 10 bins on [0, 1] of max_softmax
- Brier score with one-hot true label

For each probe:
  sims_i = (W @ k_i) @ values.T  # (M,) similarities
  probs_i = softmax(BETA * sims_i / N)  # probability distribution
  confidence = max(probs_i)
  prediction = argmax(probs_i)
  correct = (prediction == true_idx)

ECE = Σ_b |confidence_b - accuracy_b| * (n_b / total)
Brier = mean_i (probs_i - one_hot_i)²

## Cited mechanism / sources

- wave14calibration_v2 (own work, prior): tested DIFFERENT calibration
  question (bundle-side, soft-vs-clip); got CAL_NO_GAIN
- Standard ECE / Brier definitions: Guo et al. 2017 "On Calibration of
  Modern Neural Networks"; Brier 1950

## Expected runtime

- Smoke (N=1024, M=256, 1 seed): ~3-5 s
- Full (N=4096, M=4096, 3 seeds, 4 probe types): ~1-3 min on GPU

## What product decision this enables

- `WELL_CALIBRATED` → cap_map "Calibration / uncertainty" moves UNSURE
  → 🟢; product can offer "confidence scores" with each retrieval.
- `MARGINAL` → cap_map row stays 🟡 with note "fact-retrieval somewhat
  calibrated; would benefit from temperature scaling or post-hoc
  calibration."
- `POOR` → cap_map row stays UNSURE → ❌; would need post-hoc
  calibration (Platt, temperature scaling, isotonic regression) before
  shipping confidence as a product feature.
- `INVERTED` → audit bug.
