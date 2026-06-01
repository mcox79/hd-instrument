# Prereg: kf45_pre_argmax_joint_probe_v1_n4096

Filed: 2026-05-29
Source: research_surge_synthesis_v276_2026-05-29.md Agent 5 / exp_dev_handoff_research_kf4_kf5_rescue_paths_v276_2026-05-29.md

## Hypothesis
KF-4 (drift detection) and KF-5 (steerability) share the argmax-bottleneck root cause.
Pre-argmax layer signals (W spectral gap shift, logit entropy, top-k JSD) can jointly
rescue both capabilities.

## N-suffix
_n4096 binding: production N = 4096. Anchor: kf45_pre_argmax_joint_probe_v1_n4096.

## Pre-registered bands

### Signal 1: Spectral gap shift (KF-4)
HARD_PASS: mean |spectral_gap_shift| >= 0.05 (5% fractional shift).
HARD_FAIL: mean |spectral_gap_shift| < 0.005 (< 0.5%, noise floor).

### Signal 2: Logit entropy range (KF-5)
HARD_PASS: logit_entropy range > 1.0 bit AND monotone decreasing with beta in >= 3/3 seeds.
HARD_FAIL: logit_entropy_range < 0.1 bit across all beta values.

### Signal 3: Top-k JSD (KF-5)
HARD_PASS: mean_jsd(beta=2 vs beta=128) >= 0.10.
HARD_FAIL: mean_jsd < 0.01.

### Joint outcome
JOINT_HARD_PASS: >= 2 of 3 signals HARD_PASS.
JOINT_MIDDLE_BAND: exactly 1 signal HARD_PASS, OR all 3 MIDDLE_BAND.
JOINT_HARD_FAIL: all 3 signals HARD_FAIL.

## Timeout estimate
Smoke: N=1024, 2 M_fracs, 3 betas, 1 seed: ~0.5s CPU. GPU: ~0.1s.
FULL: N=4096, 2 M_fracs, 6 betas, 3 seeds.
scale = (4096/1024)^1.5 * 3 * 2 = 8 * 6 = 48. Est: 1.5 * 0.5 * 48 = 36s GPU.
Safety 8x: 288s. timeout_s = 900.

## Middle-band outcome plan
If JOINT_MIDDLE_BAND: retain the passing signal, file upstream note to Strategy for
focused drill on the passing mechanism. Do not re-run with same params.
