# Prereg — R-PRIME-1 PAC-Bayes KL-accumulation retention floor

**Anchor**: `wave14_rprime1_pac_bayes_floor_v1`
**Queue**: overnight_queue (GPU; multi-task, multi-N, multi-seed depth probe)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

Multi-task substrate retention has an information-theoretic LOWER BOUND set by
KL divergence accumulation across task switches per PAC-Bayes theory. Model
substrate's outer-product Hebbian W as Gaussian posterior N(W, sigma^2 I);
KL between consecutive task posteriors is `||W_t - W_{t-1}||_F^2 / (2 sigma^2)`;
retention >= `1 - sqrt(KL_acc / (2 M))`.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: measured retention tracks PAC-Bayes predicted floor within
  +/-20% on >=3 of 5 phase-A norm regimes AND Pearson r(predicted, measured) >= 0.60.
  -> R-PRIME-1 PAC-Bayes row promoted from 🔬 to 🟡 (PAC-Bayes is the
  retention-mechanism candidate; closed-form floor predictor available).
- **HARD-FAIL**: max abs error |measured - predicted| > 0.40 across all
  regimes AND Pearson r < 0.20. -> PAC-Bayes floor REJECTED as Bet B mechanism.
- **MIDDLE-BAND**: any intermediate; report bands; consider sigma_pac_bayes
  re-tuning as R1 rescue.

## Parameters (exp_dev autonomy)

- N (substrate dim) = 4096 FULL / 512 smoke
- M per task = 200 FULL / 40 smoke
- N_tasks = 4 FULL / 2 smoke
- Norm regimes = {0.5, 1.0, 2.0, 4.0, 8.0} FULL
- Seeds = {7, 17, 23, 31, 41} FULL
- sigma_pac_bayes = 0.10 (Gaussian-posterior std assumed for KL calc)

## Calibration penalty

Per [[feedback-lit-scan-calibration-penalty]]: PAC-Bayes for Hebbian
outer-product memories is uncharted regime; P(HARD-PASS) deflated by 0.20.
Smoke at N=512 sigma=0.1 shows pred_floor saturates to 0 (KL >> 2M); FULL at
N=4096 with longer training is needed to see whether the floor lifts into
non-trivial range — this is informative behaviour, not a script bug.

## ETA

GPU FULL ~30-60 min.
