# Prereg: pp31_2d_refusal_cert_v1

**Date**: 2026-06-01
**Anchor**: pp31_2d_refusal_cert_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_pp31_2d_refusal_cert_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (PP-31 Sub-cap 2-D)

## Hypothesis

Refusal audit certificate: a 2-field certificate (refusal_type, confidence_score,
threshold) correctly distinguishes confidence-based refusal (score < tau, healthy W)
from system failure (score < tau, overloaded W) in 5/5 trials per seed. Certificate
generation time < 1ms (no matrix ops, just field assignment).

Compliance differentiator: satisfies FDA SaMD, EU AI Act Art 14, SR 11-7 audit
requirements for auditable refusal records.

## Design

- N = 512, TAU = 0.50
- M_HEALTHY = 40 (alpha = 0.078 << alpha_c = 0.138)
- M_OVERLOAD = 96 (alpha = 0.188 > alpha_c * 1.20)
- 5 confidence-refusal trials (40% noise -> score < TAU)
- 5 system-failure trials (same noise, overloaded W)
- Certificate: overloaded iff alpha > 1.20 * alpha_c

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: cert correct (right refusal_type) for all trials when score < TAU
AND cert generation <= 1ms per trial.

**HARD-FAIL**: >= 2 misclassifications OR cert generation > 10ms.

**MIDDLE-BAND**: 1 misclassification (4/5) OR 1-10ms generation.

## Smoke result

Smoke (3 seeds, 30 trials): HARD_PASS. correct=30/30, max_cert_time=0.004ms.
Full run expected to confirm.

## Timeout estimate

smoke_wall_s ~ 0.01s. timeout_s = 300 (PROT-019 floor).

## N-suffix

No _nN suffix. Production N = 512; stated per PROT-018 rule 3.
