# Prereg: wave14_rprime1_pac_bayes_v2

**Filed**: 2026-05-24 exp_dev
**Anchor**: R-PRIME-1 PAC-Bayes KL-accumulation retention floor v2 (calibrated sigma)
**v1 root cause**: sigma=0.10 made KL >> M for all N; floor clamped to 0 in smoke.
**v2 fix**: sigma auto-calibrated per task as sigma = ||delta_W||_F / N (RMS amplitude); KL_t becomes O(N^2/2) per task.

## Hypothesis

Multi-task retention has an information-theoretic lower bound via PAC-Bayes
KL accumulation across task switches: retention(t) >= 1 - sqrt(KL_acc/(2*M)).
Tested across 5 phase-A norm regimes (norm in {0.5, 1.0, 2.0, 4.0, 8.0});
if measured retention tracks predicted floor within +/-20%, PAC-Bayes is
the binding mechanism.

## Design (exp_dev autonomy)

- N = 4096 (FULL), 512 (smoke)
- M per task = 200 (FULL), 40 (smoke)
- N tasks = 4 (FULL), 2 (smoke)
- Norm regimes: {0.5, 1.0, 2.0, 4.0, 8.0} (FULL)
- Seeds: {7, 17, 23, 31, 41} (FULL)
- sigma auto-calibrated: sigma_t = ||delta_W_t||_F / N (calibration_factor=1.0)
- Queue: remote_cpu_queue (pure numpy; multi-regime; ~5-15 min CPU)

## Pre-registered falsifier bands

- **HARD-PASS**: measured retention tracks floor within +/-20% on >=3 of 5 norm
  regimes AND Pearson r >= 0.60. -> R-PRIME-1 PAC-Bayes row 🔬 -> 🟡 candidate.
- **HARD-FAIL**: max abs error > 0.40 on every regime OR Pearson r < 0.20.
  -> PAC-Bayes floor REJECTED as Bet B mechanism.
- **MIDDLE**: any intermediate.

## Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

- pac_bayes_floor(50, 200) = 1 - sqrt(50/400) = 0.646 (formula check)
- pac_bayes_floor(0, 100) = 1.0
- pac_bayes_floor(200, 100) = max(0, 1 - 1.0) = 0.0
- Verdict: tight tracking -> PAC_BAYES_V2_HARD_PASS; all errors >0.40 + r<0.20 -> PAC_BAYES_V2_HARD_FAIL.
All 4/4 verdict + 3 formula self-test cases pass.

## Smoke outcome

v2 smoke still shows predicted floor = 0.0 at N=512 (KL_acc = N^2/2 per task >> M_total).
Root cause: KL scales as N^2/2 per task; for sigma = ||dW||_F/N, KL_t = N^2/2 structurally.
For N=512, KL_acc = 512^2 * n_tasks / 2 = 262144; M_total = 80; floor = 1-sqrt(1638) = -39 -> clamped to 0.
This is a STRUCTURAL mathematical hard-fail: the Gaussian weight posterior with per-task sigma calibration
produces a vacuously loose PAC-Bayes bound for outer-product memories at any tested scale.

## Smoke verdict: HARD_FAIL -> upstream-push to Strategy

This is NOT a retriable parameter issue; it is the geometry of outer-product memory updates:
||W_t - W_{t-1}||_F ~ sqrt(M) * N (via Frobenius of sum of M outer products of N-dim vectors),
so KL / M ~ N^2 / (2 * sigma^2 * M) -> requires sigma >> N/sqrt(M) for non-vacuous bound,
which grows as N/sqrt(M_per) and is not calibratable away without reframing.

R-PRIME-1 rescue: use task-level KL in function-space (information geometry on the recall map,
not weight space). See notes/exp_dev_to_strategy_rprime1_pac_bayes_reframe_2026-05-24.md.
