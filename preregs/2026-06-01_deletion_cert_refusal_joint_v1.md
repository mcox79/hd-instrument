# Pre-registration: deletion_cert_refusal_joint_v1

**Date:** 2026-06-01
**Anchor:** deletion_cert_refusal_joint_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_deletion_cert_refusal_joint_v1.py
**Cap_map row:** PP-9 deletion-cert x PP-31 refusal-cert joint (GDPR erasure-audit pair)

## Scientific question
Q14: Does delete+refusal joint composition work? Post-delete refusal precision >= 0.95
AND recall >= 0.90. Joint reliability >= product of individual reliabilities.

## Pre-registered bands
- HARD-PASS: post_del_precision >= 0.95 AND post_ret_recall >= 0.90 AND
             joint_reliability >= individual_product * 0.95 (within 5%).
- MIDDLE: precision in [0.85, 0.95) OR recall in [0.80, 0.90).
- HARD-FAIL: precision < 0.80 OR recall < 0.75.

## Design
- N=4096, M=100, K_DELETE=10, TAU=0.5
- 5 seeds, 200 probes per condition
- Two conditions: deleted-pattern probes (should be refused), retained-pattern probes (should not be refused)

## Formula self-tests
1. Pre-delete: overlap ~ 1 - (M-1)/N ~ 0.976. Above tau=0.5: passes (not refused).
2. Post-delete: residual overlap ~ (M-k)/N = 0.022 < 0.5: refused correctly.
3. Crosstalk floor: 1/sqrt(N) = 0.0156.

## Timeout estimate
smoke_wall_s=2.6s, FULL: ceil(1.5 * 2.6 * 1.0 * 2.5) = ceil(9.75) = 10. timeout=300 (floor).

## N-suffix note
No _nN suffix. Production N=4096 per PROT-018 rule 3.

## Smoke result
run_mode=smoke, verdict=HARD_PASS precision=1.0 recall=1.0 elapsed=2.6s. PASS gate.
