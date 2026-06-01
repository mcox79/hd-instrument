# exp_dev -> Strategy: KF-4 drift detect v4 blocked

**Filed:** 2026-05-29
**Blocking reason:** INSTRUMENTATION_SUSPECT - structural acc_drop=0 at all scales

## What was attempted

kf4_drift_detect_v4_n4096: rescue of KF-4 drift detection via calibrated-noise accuracy
drop (acc_base - acc_drifted after 200 spurious outer products of scale 1/N).

## What was found

At N=1024 (smoke): acc_base=1.0, acc_drifted=1.0, acc_drop=0.0 (SMOKE_FAIL).
At N=4096 (4x smoke): acc_base=1.0, acc_drifted=1.0, acc_drop=0.0.
Noise fraction = 200/M_full = 0.024 at M_frac=2.0.

## Root cause

Kerdock codebook substrates are perfectly error-correcting (argmax over Kerdock
codewords de-noises any linear perturbation). The retrieval step is:
  output = W @ k / N -> project onto Kerdock codebook via argmax
This argmax step creates a hard decision boundary. Small additive noise to W (200 outer
products of scale 1/N total perturbation = 0.05 fractional) is completely absorbed by
the argmax de-noising step. acc_drop=0 is a GENUINE result, not instrumentation failure.

## Attempted mechanisms

1. v3: margin-based (cosine similarity gap). HARD_FAIL gap=0.0.
2. v4 attempt 1: OOS posterior entropy (H_drifted - H_base). Both H_base=H_drifted=0.0
   because BETA=32 causes one-hot softmax for stored keys. Entropy always 0.
3. v4 attempt 2: OOS max-confidence ratio (ratio_drifted/ratio_base). ratio_base already
   at 1663x uniform (substrate fully associative for ANY query). Signal ratio=1.000.
4. v4 attempt 3: calibrated accuracy drop (acc_base - acc_drifted). Always 0.0.

## What this means scientifically

The Kerdock substrate is structurally ROBUST to drift at this perturbation level.
This is a POSITIVE property (robustness) but makes drift detection via retrieval
accuracy or output confidence impossible at practical noise levels.

## Proposed paths forward

1. MUCH LARGER DRIFT: test acc_drop with N_DRIFT_STEPS=C (one spurious pattern per
   codebook atom = total noise = 1.0 per W entry). At this scale, acc_drop should
   be measurable. But this is not "drift" -- it's complete rewrite.

2. DIFFERENT DETECTION SIGNAL: instead of probing with the original stored keys,
   use a MONITOR SET (fresh keys stored AFTER drift) and measure their retention
   vs a pre-drift monitor set. Drift affects new patterns stored post-drift.

3. CAPACITY-BASED DETECTION: measure maximum M before acc drops below threshold.
   Drifted substrate has lower effective capacity. Compare M_c_base vs M_c_drifted.

4. SPECTRAL SIGNAL: measure eigenvalue distribution of W (singular values of W-I).
   Drift adds noise to singular values. Compare spectral gap before vs after drift.
   This would be observable even at small perturbation levels.

## Recommendation to Strategy

KF-4 drift detection via retrieval accuracy is not viable for Kerdock substrates
because of perfect error-correction. Route to exp_dev with:
- Option A: spectral detection mechanism (W singular value drift)
- Option B: capacity monitoring (M_c shift before/after drift)
- Option C: abandon KF-4 and note structural robustness as positive KF-4 property

Routing: notes/exp_dev_to_strategy_kf4_v4_blocked_2026-05-29.md
