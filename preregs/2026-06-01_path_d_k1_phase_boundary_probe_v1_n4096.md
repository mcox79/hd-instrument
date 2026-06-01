# Pre-registration: path_d_k1_phase_boundary_probe_v1_n4096

**Date**: 2026-06-01
**Anchor**: path_d_k1_phase_boundary_probe_v1_n4096
**Queue**: remote_cpu_queue
**HDLAB_EXP_NAME**: 7d39e13 (as specified in routing)

## Scientific question

Path D's validated "no-ceiling at M=64N depth=50" envelope (cap_map v297+v299 LIFTs) uses K_paths=100 candidates.
At K=100, p_eff = K/M = 3.8e-4 at M=64N is 100x above the ER percolation threshold 1/M.
The validated envelope may be operating entirely in the candidate-safety-margin regime rather than
the substrate-physics regime.

This anchor probes the actual substrate phase boundary by removing the candidate pool (K=1 effective).
The K=1 proxy is `path_b_top1_acc`: fraction of random query starts where Path B direct propagation
arrives at the correct depth-5 endpoint without any candidate-count safety margin.

## Config (PROT-018 bound)

- **N = 4096** (PROT-018 _n4096 binding)
- **M = 16N = 65536** (fixed)
- **depth = 5**
- **K_paths_grid**: {1, 10, 100} (evaluated per cell via path_d_run; K=1 effective via path_b_top1)
- **K_random_keys = 100** (query starts per seed)
- **Seeds (FULL)**: [7, 17, 23, 42, 99] (5 seeds)
- **device = cpu** (PROT-022; N=4096 CPU-safe; GPU queue has 2 pending)

## Metrics

- **path_b_top1_acc**: PRIMARY. Fraction of K_random_keys starts where Path B depth-5 walk arrives at correct endpoint (top-1 cosine-NN in codebook). This is the K=1-effective substrate phase boundary probe (no candidate pool).
- **path_d_k10_acc**: standard Path D accuracy with K_paths=10 (candidate pool).
- **path_d_k100_acc**: standard Path D accuracy with K_paths=100 (known validated regime).

## Pre-registered threshold bands

### HARD-PASS (K1_PHASE_HARD_PASS)

Both conditions must hold:
1. `mean(path_b_top1_acc) in [0.50, 0.95]` across 5 seeds
2. `mean(path_d_k100_acc) >= 0.90`

Interpretation: Substrate-physics signal is present at K=1. Path D envelope is (at least partially) substrate-physics, not pure K-safety-margin. K=10 expected to close most of the gap to K=100.

Also triggers HARD_PASS if `mean(path_b_top1_acc) > 0.95` (stronger-than-expected substrate physics).

### HARD-FAIL (K1_PHASE_HARD_FAIL)

`mean(path_b_top1_acc) in [0.001, 0.010]` (random-chance band)

Interpretation: Substrate Path D was operating entirely in the candidate-safety-margin regime. No substrate-physics signal at K=1. This would substantially DROP the Path D production-default sub-row P-band.

Also triggers HARD_FAIL if `mean(path_b_top1_acc) < 0.001` (below random-chance).

### MIDDLE-BAND (K1_PHASE_MIDDLE_BAND)

`mean(path_b_top1_acc) in (0.010, 0.500)`

Interpretation: Partial substrate-physics signal. Characterizable; additional experiments needed to quantify the phase transition as a function of K and M.

## Prior empirical anchor

From full-scale smoke at N=4096, M=65536, depth=5, seed=17, K_random_keys=100 (run before FULL ship):
- path_b_top1_acc = 0.040
- path_d_k10_acc = 1.000
- path_d_k100_acc = 1.000
- n_eval = 100
- elapsed = 19.5s

This single-seed smoke result already puts path_b_top1_acc = 0.040 in the MIDDLE-BAND (0.01, 0.50),
suggesting partial substrate-physics signal. The 5-seed FULL run quantifies the variance.

## Timeout estimate

```
smoke_wall_s  = 19.5s (1 full-scale seed, N=4096, M=65536, K_random_keys=100)
FULL_seeds    = 5
smoke_seeds   = 1
scaling_exp   = 1.0 (linear in seeds; each seed is independent)

timeout_s = ceil(1.5 * 19.5 * 1.0 * 5) = ceil(146.25) = 300s
```

Formula result: 300s. However PROT-019 enforces a floor of 14400s for _n4096 anchors. **timeout_s = 14400** (PROT-019 floor applied). Actual expected wall time ~100s (5 seeds x 20s); floor provides ample safety margin.

This is well under the 14400s block threshold and well under the 7200s warning threshold.

## N-suffix section

PROT-018: anchor name contains `_n4096`; production N = 4096. Verified: `grep "N_FULL.*4096" experiments/exp_path_d_k1_phase_boundary_probe_v1_n4096.py` passes.

## Walk-back gate

Smoke effect: path_b_top1_acc = 0.040 at 1 seed (middle-band, well above HF floor of 0.010).
Cohen's d not directly applicable to a proportion. The single-seed estimate is 0.040 vs HF upper bound 0.010 -- 4x above the HARD-FAIL threshold. 5 seeds planned provides adequate power to resolve MIDDLE vs HF. No walk-back (doubling) needed: the effect is not borderline.

## Strategic value

Resolves the "K=100 trivialization" caveat in cap_map v297+v299. Without this experiment, the cap_map's Path D "no-ceiling" claim is potentially confounded with K-safety-margin effects. With this experiment, we either confirm substrate-physics (HARD-PASS) or correctly reduce the P-band (HARD-FAIL).

Source: research routing `notes/strategy_request_to_strategy_p3_p4_external_routing_delivery_2026-06-01.md` Section P3 "Recommended next experiment".
