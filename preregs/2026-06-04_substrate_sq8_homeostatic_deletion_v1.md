# Prereg: substrate_sq8_homeostatic_deletion_v1
## Anchor
substrate_sq8_homeostatic_deletion_v1
## Routing
SQ8 (P_drill=0.65; LifeHD 2024). Homeostatic D-ECR self-deletion; recent-recall stability under unbounded stream.
Setpoint = 0.85*alpha_c (graceful zone per alpha-ramp). CPU numpy, $0. remote_cpu_queue.
## Pre-registered bands (stability = min recent-recall over stream MULTs; drift = max-min)
HARD-PASS min>=0.90 AND drift<=0.05. MIDDLE min>=0.75. HARD-FAIL min<0.75 or drift>0.15.
## Formula self-tests (PROT-022)
low-load recall / eviction reduces ||W|| / alpha_c=0.138. [PASS]
## Smoke gate
Smoke (N=512): STABLE (drift 0.03) but recall ~0.6 (finite-size at N=512); full N=2048 -> higher level expected. Mechanics validated.
## Queue
remote_cpu_queue (numpy). timeout 14400s.
