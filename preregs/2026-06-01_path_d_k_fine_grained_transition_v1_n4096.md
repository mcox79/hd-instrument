# Pre-registration: path_d_k_fine_grained_transition_v1_n4096

Date: 2026-06-01
Anchor: path_d_k_fine_grained_transition_v1_n4096
Queue: remote_cpu_queue
Script: experiments/exp_path_d_k_fine_grained_transition_v1_n4096.py
HDLAB_EXP_NAME env: 7d39e13

## Hypothesis

At N=4096, M=16N=65536, depth=5, sweeping K_paths in {1, 2, 3, 5, 10, 100}:
the path_d_run accuracy (candidate-pool disambiguation) increases monotonically
from K=1 substrate-physics regime through intermediate K values to the
production-default K=10/100. The transition curve maps the K-safety-margin
lever and informs whether K=5 (5x latency reduction vs K=100) is a safe
operating point for production substrate deployments.

## Config

- N = 4096 (PROT-018: bound by _n4096 suffix)
- M = 16 * 4096 = 65536 (fixed per routing)
- depth = 5
- K_paths sweep: {1, 2, 3, 5, 10, 100}
- 5 seeds: [7, 17, 23, 42, 99]
- k_random_keys = 100 per cell
- device: cpu (PROT-022)

## Primary metric

path_d_kK_acc = accuracy from path_d_run(K_paths=K) for K in {2, 3, 5, 10, 100}
path_b_top1_acc = substrate phase-boundary probe (K=1 effective, no pool; K-independent)

## Pre-registered bands

### HARD-PASS
Monotone increase in mean accuracy across K AND:
- K=2 mean in [0.10, 0.30]
- K=3 mean in [0.40, 0.70]
- K=5 mean in [0.85, 0.99]
- K=10 mean >= 0.90 (matches v307 unanimous result)
Interpretation: smooth transition curve; substrate could safely operate at K=5.

### HARD-FAIL
K=2 mean <= 0.01 AND K=3 mean <= 0.01 AND K=5 mean <= 0.01
(all three intermediate K values at random-chance band)
Interpretation: substrate-physics signal scales worse than naive expectation;
K cliff is beyond K=10; K=5 unsafe operating point.

### MIDDLE-BAND
Discontinuous jump (cliff at specific K threshold) OR partial monotone:
- Some K values in HP band but not all
- Large gap between consecutive K values (cliff signature)
Interpretation: K-safety-margin lever is sharp at a specific K*; informs
minimum safe K for substrate deployments.

## Formula self-tests (verified at module scope in script)

1. HP: k2=0.20, k3=0.55, k5=0.90, k10=0.98, k100=1.0 (monotone + in bands) -> K_FINE_HARD_PASS CONFIRMED
2. HF: k2=0.005, k3=0.008, k5=0.009, k10=0.98 (all intermediate random-chance) -> K_FINE_HARD_FAIL CONFIRMED
3. MIDDLE: k2=0.20, k3=0.55, k5=0.70, k10=0.98 (cliff at k5->k10) -> K_FINE_MIDDLE_BAND CONFIRMED

## N-suffix note

_n4096: production N = 4096. Smoke runs at N_SMOKE=1024 (log2=10, even;
Kerdock codebook compatible). FULL config N=4096.

## Smoke gate result

Smoke: N=1024 M=512 1 seed wall=0.17s. All metrics non-null, n_eval=20. PASS.
Note: smoke at N=1024/M=512 gives acc=1.0 across all K (expected at small M).
Instrumentation self-test at N=1024/M=512/depth=3 confirms gates fire correctly
on injected HP/HF/MIDDLE synthetic data. Self-test at module scope: PASS.

## Timeout estimate

smoke_wall_s = 0.17s at N_smoke=1024/M=512.
Reference from v307 (same harness at N=4096/M=16N): ~60s/seed.
K-sweep is 6 K values per seed; each path_d_run call is independent.
Estimate per seed: ~60s (comparable to K=3 probe at FULL scale).
FULL: 5 seeds * ~60s = 300s. 1.5x safety = 450s.
PROT-019 floor: 14400s. timeout_s = 14400.

## Calibration note

Prior anchor v307 confirmed K=1 path_b_top1_acc=0.022 at M=16N.
v307 confirmed K=10/100 unanimous (>=0.90). The K=2/3/5 intermediate values
have no prior empirical anchor -- bands set from theoretical interpolation
(monotone expectation). Bands are wide (K=2: [0.10,0.30]; K=3: [0.40,0.70])
per calibration-probe policy for first measurement of intermediate K values.

## Strategic value

Maps production K operating-point selection. If K=5 lands in HP band
(mean 0.85-0.99), substrate could run at K=5 with 5x latency reduction
vs K=100. If MIDDLE-BAND (cliff), identifies minimum safe K precisely.

## Origin

R2 from cap_map v307 follow-on routing (notes/strategy_request_to_strategy_v307_followon_experiments_2026-06-01.md).
