# Pre-registration: query_dp_audit_eps_v1

**Date:** 2026-06-01
**Anchor:** query_dp_audit_eps_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_query_dp_audit_eps_v1.py
**Cap_map row:** PP-14 differential privacy -- Query-DP sub-property

## Scientific question
Q13: Does Query-DP noise variance M*c^2/eps^2/N stay negligible vs crosstalk for eps > 0.06?

## Pre-registered bands
- HARD-PASS: audit accuracy drop at eps=0.1 < 1.0pp AND eps=0.3 < 0.5pp AND eps=1.0 < 0.2pp;
  AND eps=0.06 shows visible degradation (drop >= 1.0pp vs eps=inf baseline).
- MIDDLE: drop at eps=0.1 in [1, 3]pp OR degradation not monotone in eps.
- HARD-FAIL: drop at eps=0.3 > 3pp (query-DP imposes non-negligible cost at moderate eps).

## Design
- N=4096, M=200, TAU=0.5
- Eps grid: [inf, 1.0, 0.3, 0.1, 0.06]
- 5 seeds, 200 queries per (seed, eps)
- DP noise on overlap score scalar: sigma^2 = M*c^2 / (eps^2 * N)

## Formula self-tests
1. eps=inf: sigma=0, accuracy = baseline.
2. eps=0.06: sigma = sqrt(200/(0.0036*4096)) = 3.68 -- large, expected accuracy drop.
3. eps=0.1: sigma = 2.21 -- intermediate.
4. eps=1.0: sigma = 0.22 -- negligible.

## Timeout estimate
smoke_wall_s=1.7s, FULL_N=smoke_N (same N), FULL_seeds=5, smoke_seeds=2.
timeout = ceil(1.5 * 1.7 * 1.0 * 2.5) = ceil(6.4) = 10. timeout=300 (floor).

## N-suffix note
No _nN suffix. Production N=4096 per PROT-018 rule 3.

## Smoke result
run_mode=smoke, verdict=MIDDLE_BAND, elapsed=1.7s. Metrics non-null. PASS gate.
