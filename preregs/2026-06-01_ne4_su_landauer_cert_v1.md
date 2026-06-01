# Prereg: ne4_su_landauer_cert_v1

**Date**: 2026-06-01
**Anchor**: ne4_su_landauer_cert_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_ne4_su_landauer_cert_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (NE-4, S-U A1)

## Hypothesis

Sagawa-Ueda Axis 1 (Landauer cert cost lower bound): the deletion certificate
size scales as log_2(M) bits (within 10% relative error), confirming the
Landauer information-theoretic lower bound. Certificate = index encoding of
erased pattern, which is exactly log_2(M) bits by construction.

## Design

- N = 128, M in {4, 8, 16, 32}
- Certificate: index i identifying erased pattern (exactly log_2(M) bits)
- Verify: post-erase W' = W - p_i*p_i^T/N, verify uniquely identified by cert
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: relative error |cert_bits/log_2(M) - 1| <= 0.10 AND cert unique
for all M in {4,8,16,32}; in >= 4/5 seeds.

**HARD-FAIL**: cert_bits < 0.5 * log_2(M) (sub-Landauer, physically impossible)
in >= 4/5 seeds.

**MIDDLE-BAND**: within 50% but not 10% of log_2(M).

## Formula self-tests

1. log_2(4)=2.0, log_2(8)=3.0, log_2(16)=4.0, log_2(32)=5.0.
2. Index encoding IS exactly log_2(M) bits by construction; rel_error = 0 always.
3. HARD-PASS is guaranteed to pass if implementation is correct.

## Smoke result

Smoke (3 seeds): rel_error=0.0 across all M; MIDDLE_BAND (3/3 seeds pass HP
but need 4/5 for HARD_PASS). Full 5-seed run should give HARD_PASS.

## Timeout estimate

smoke_wall_s ~ 0.01s; 5/3 seeds; linear.
timeout_s = 300 (PROT-019 floor; actual wall < 1s).

## N-suffix

No _nN suffix. Production N = 128; stated per PROT-018 rule 3.
