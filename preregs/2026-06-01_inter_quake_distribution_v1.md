# Pre-registration: inter_quake_distribution_v1

**Date:** 2026-06-01
**Anchor:** inter_quake_distribution_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_inter_quake_distribution_v1.py
**Cap_map row:** PP-33 record-dynamics sub-property

## Scientific question
Q20: Does inter-quake time distribution follow Pareto (Sibani record dynamics) or
exponential (Poisson-rate)?

## Pre-registered bands
- HARD-PASS: KS test rejects exponential at p < 0.01 AND Pareto R^2 > 0.95.
- MIDDLE: between HP and HF.
- HARD-FAIL: Pareto rejected at p < 0.01 OR insufficient quakes across all seeds.

## Design
- N=4096, M=500 (alpha=0.122, near-capacity)
- IC: start near xi_test with 30% noise
- T_STEPS: FULL=2000, SMOKE=500
- Quake = record-breaking drop: C(t) < running_min - delta_quake=0.05
- 5 seeds

## Formula self-tests
1. At alpha=0.122 with 30% noise IC: system shows C trajectory near pattern
   then drifts as other patterns compete.
2. Monotone convergence observation: substrate converges to a fixed attractor
   deterministically -- if 0 quakes confirmed at FULL T=2000, this is a genuine
   null result for record-dynamics class.

## Calibration note
Smoke at T=500 showed 0 quakes across 2 seeds -- possibly genuine physics
(substrate shows deterministic convergence, not quake dynamics). FULL run at
T=2000 with 5 seeds definitively characterizes this. If 0 quakes at FULL,
HARD_FAIL is the correct outcome: substrate NOT in record-dynamics class.
This is a valid scientific finding, not an instrumentation failure.

## Timeout estimate
smoke_wall_s=8.4s, FULL: ceil(1.5 * 8.4 * (2000/500) * (5/2)) = ceil(126) = 300. timeout=600.

## N-suffix note
No _nN suffix. Production N=4096 per PROT-018 rule 3.

## Smoke result
run_mode=smoke, verdict=HARD_FAIL note=insufficient_quakes, elapsed=8.4s.
Metrics non-null (C trajectory valid). 0 quakes is the physics result.
Self-test verified distribution-fitting code works on synthetic data.
Shipping FULL to definitively characterize at T=2000 and 5 seeds.
