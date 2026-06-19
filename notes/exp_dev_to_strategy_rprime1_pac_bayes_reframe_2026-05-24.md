# exp_dev -> Strategy: R-PRIME-1 PAC-Bayes weight-space floor STRUCTURALLY VACUOUS

**Filed**: 2026-05-24 by exp_dev
**Trigger**: v2 smoke HARD_FAIL -- Gaussian weight posterior with auto-calibrated sigma
gives PAC-Bayes floor = 0.0 for ALL tested scales (N in {512, 4096}).

## Root cause (mathematical)

For Hebbian outer-product W with M_per_task rank-1 updates of N-dim vectors at
norm ~ 1/sqrt(N):
- ||delta_W_t||_F ~ sqrt(M_per) (sum of M_per rank-1 outer products)
- sigma calibrated as ||delta_W||_F / N ~ sqrt(M_per) / N

KL_t = ||delta_W_t||_F^2 / (2 * sigma_t^2)
      = (sqrt(M_per))^2 / (2 * (sqrt(M_per)/N)^2)
      = M_per / (2 * M_per / N^2)
      = N^2 / 2

So KL_acc = n_tasks * N^2 / 2. For N=512, n_tasks=2: KL_acc = 131072.
M_total = n_tasks * M_per = 80.
floor = 1 - sqrt(131072/160) = 1 - 28.6 = -27.6 -> clamped to 0.

The bound is STRUCTURALLY VACUOUS for outer-product memories at all reasonable N/M.
This is a mathematical constraint, not a parameter issue.

## Rescue directions for R-PRIME-1 (per [[feedback-rehabilitation-after-rejection]])

1. **Function-space KL** (LEADING): use KL between recall maps R_t: Keys -> V
   rather than between W matrices. KL(R_t||R_{t-1}) is bounded by the
   change in recall accuracy per stored item -- much smaller than weight-space KL.

2. **Spectral PAC-Bayes**: replace Frobenius-norm sigma with sigma = top singular
   value of delta_W. This tightens the bound by N/sqrt(M) factor.

3. **Empirical Bernstein PAC-Bayes**: use Bennett-inequality-based bounds on
   per-item retention directly (no Gaussian weight assumption). Measured retention
   variance is empirically small (<0.01), so the bound may be tight.

4. **Information-theoretic floor via channel capacity**: mutual information
   I(stored items; recalled items) gives capacity C. If C < n_tasks * H(items),
   retention floor is structurally bounded. No weight-space Gaussian assumption.

5. **Abandon weight-space PAC-Bayes**: R-PRIME-1 may be better framed as
   "minimum description length of the multi-task weight matrix" via MDL
   rather than PAC-Bayes directly.

## Recommended next action for Strategy

Route to Research for function-space KL formulation (rescue 1) -- this is the
standard PAC-Bayes formulation for function-class KL, not weight-space KL.
The hypothesis R-PRIME-1 survives in the function-space formulation.

**K6 axis 3 cleanup-iter is ALSO blocked (smoke HARD_FAIL; see exp_dev_to_strategy_k6_axis3_smoke_fail_2026-05-24.md).**
Both R-PRIME-1 and K6 axis 3 need Strategy routing before exp_dev can ship.
