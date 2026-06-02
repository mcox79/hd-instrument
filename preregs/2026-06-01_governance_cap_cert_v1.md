# Pre-registration: governance_cap_cert_v1

**Date:** 2026-06-01
**Anchor:** governance_cap_cert_v1
**Script:** experiments/exp_governance_cap_cert_v1.py
**Queue:** remote_cpu_queue
**N:** 4096

## Hypothesis

The substrate can produce a governance certificate with 4 auditable fields:
{delta_m, alpha_estimated, lambda_max, capacity_headroom}. The alpha estimator
must match true alpha within 20% error, and lambda_max must grow meaningfully
as alpha increases (ratio > 1.1).

## Pre-registered thresholds

- **HARD-PASS:** alpha_err < 0.20 AND lambda_growth_ratio > 1.1
- **HARD-FAIL:** alpha_err > 0.40 OR lambda_growth_ratio < 1.0
- **MIDDLE-BAND:** everything else

## Smoke result (2026-06-01)

Smoke HARD_PASS: alpha_err=0.063, lambda_growth_ratio=1.372. Wall ~5.4s.

## Cap-map rows

- Governance/compliance certificate API
- Capacity headroom monitoring for regulatory use
