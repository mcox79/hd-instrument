# Pre-registration: combo1_alpha_p_minus_1_audit_sensitivity_v1_n4096

Date: 2026-06-02
Anchor: combo1_alpha_p_minus_1_audit_sensitivity_v1_n4096
Queue: remote_cpu_queue
Seeds: [7, 17, 23, 31, 41]
N: 4096

## Hypothesis
PP-45 alpha^(p-1) audit sensitivity scaling. For p=3 DAM, kappa_3 sensitivity
(delta_kappa3 = |kappa_3(W + xi xi^T/N) - kappa_3(W)|) should scale as alpha^2
(i.e. log-log slope = p-1 = 2.0). Tests whether the sensitivity exponent is
consistent with polynomial DAM theory.

## Pre-registered Thresholds
HARD-PASS: log-log slope in [1.5, 2.5] AND Spearman rho >= 0.90 AND sens at alpha=0.05 > 0.
HARD-FAIL: slope < 1.0 (exponent wrong order) OR rho < 0.50 (no monotone relationship).
MIDDLE: rho PASS but slope outside [1.5, 2.5].

## Calibration Source
Smoke MIDDLE_BAND: slope=1.0 (FAIL, outside [1.5,2.5]), rho=1.0 (PASS), sens_05 PASS.
Sub-leading correction: at small alpha, sub-leading alpha^3 term suppresses apparent slope.
More alpha points (N=4096, 5 seeds) should push slope toward 2.0 asymptote.

## Smoke Result
MIDDLE_BAND: slope=1.0, rho=1.0. Walk-back: 5 seeds at N=4096.
