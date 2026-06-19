# Pre-registration: Semantic-A v2 Multi-field RRF

Date: 2026-06-12
Status: Pre-registered (prototype run complete; queued for dashboard-visible reproduction)
Experiment file: [exp_semantic_a_v2_multifield_rrf_gpu_v1.py](../experiments/exp_semantic_a_v2_multifield_rrf_gpu_v1.py)

## Hypothesis (H)

RRF over multiple atom-field bge rankings (description / id-token / name / serves_capability) lifts A-axis F1 over description-only.
Operationalized: `A_F1(RRF) - A_F1(desc) >= 0.04`. (Prototype finding: naive equal-weight RRF DILUTES; the name/id-token field alone
is the lever at ~0.41 -- this run reproduces that on the GPU runner.)

## Pre-registered outcomes
- HARD-PASS: RRF A-F1 >= 0.43 + lift >= +0.04 ; MIDDLE +0.02-0.04 ; HARD-FAIL < +0.02.
