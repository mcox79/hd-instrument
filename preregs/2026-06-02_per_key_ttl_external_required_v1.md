# Pre-registration: per_key_ttl_external_required_v1

**Date:** 2026-06-02
**Anchor:** per_key_ttl_external_required_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_per_key_ttl_external_required_v1.py

## Scientific question (Caching-Policy Expressibility, Tier 2 NEGATIVE)
A single global decay parameter gamma cannot implement per-key TTL in the substrate.
Does the global gamma (0.90^t) apply uniformly to ALL stored patterns, confirming
that per-key TTL requires an external per-key expiry register?

## Pre-registered thresholds (Tier 2 NEGATIVE -- constraint confirmation)
- HARD-PASS (constraint confirmed): max_delta_retention <= 0.05 (global gamma applies equally; per-key TTL impossible natively)
- MIDDLE: max_delta_retention in (0.05, 0.15] (some per-key variation; may be noise)
- HARD-FAIL (constraint violated): max_delta_retention > 0.15 (substrate has native per-key expiry)

## Calibration note
For Tier 2 NEGATIVE cells, HARD-PASS = confirming the constraint. Formula:
gamma^t = 0.9^5 = 0.5905. All patterns should retain at same rate after t=5 decays.

## Smoke result
HARD_PASS (constraint confirmed): max_delta_retention=0.0000 (smoke N=1024, GAMMA=0.90, 2 seeds)
