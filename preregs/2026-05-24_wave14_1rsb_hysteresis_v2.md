# Prereg: wave14_1rsb_hysteresis_v2

**Filed**: 2026-05-24 exp_dev (re-ship after TypeError fix)
**Anchor**: Pred-4 (1-RSB diagnostic) -- Hysteresis under capacity sweep [v2]
**Trigger**: wave14_1rsb_hysteresis_v1 INSTRUMENTATION_FAIL (TypeError at base.evaluate_bpc --
             called with 6 args instead of required 10; missing pool_vecs/pool_labels/pool_used/batch_size).
**Design unchanged**: same hypothesis, thresholds, M sweep, seeds as v1.

## Root cause of v1 failure

`run_4stage_get_retA` called `base.evaluate_bpc(W_ABCD, byte_atoms, pos_atoms, test_a_idx, test_a_tgt, device)`
but the function signature is `evaluate_bpc(W, pool_vecs, pool_labels, pool_used, byte_atoms, pos_atoms, eval_bytes, eval_targets, batch_size, device)`.
v2 fix: `base.evaluate_bpc(W_ABCD, pool_D_v, pool_D_l, pool_D_u, byte_atoms, pos_atoms, test_a_idx, test_a_tgt, batch_size, device)`.

## Hypothesis (unchanged from v1)

First-order phase transition (1-RSB) prediction: the substrate shows hysteresis
when capacity is swept through alpha_c. Loading from BELOW alpha_c (low -> high M)
vs from ABOVE (high -> low M) produces different retA curves at the same M cells.
Hysteresis gap = |retA_forward - retA_reverse| >= 0.10 at some M.

RS / continuous transition prediction: both trajectories give the same retA within
seed-variance. Max hysteresis gap < 0.03 everywhere.

## Design (unchanged from v1)

- N = 2048 (FULL), 512 (smoke) [CPU-feasible]
- Batch = 32 (FULL), 16 (smoke)
- Epochs = 5 (FULL), 1 (smoke)
- Phase-A epochs = 8 (FULL), 1 (smoke)
- M sweep = {25k, 50k, 100k, 150k, 200k, 300k, 400k} bytes (FULL),
            {25k, 100k, 400k} (smoke)
- Seeds = {7, 17, 23} (FULL, 3 seeds), {17} (smoke)
- Trajectories: Forward (low->high M) + Reverse (high->low M)
- Queue: remote_cpu_queue (CPU; no GPU needed)
- ETA: ~30-45 min CPU (7 M x 2 traj x 3 seeds x 4 stages)

## Pre-registered bands (unchanged from v1)

HARD-PASS: max hysteresis gap >= 0.10 at any M cell.
  Interpretation: first-order transition; 1-RSB framing supported.

RS-HARD-FAIL: max hysteresis gap < 0.03 everywhere.
  Interpretation: continuous transition; 1-RSB NOT supported at capacity axis.
  Rehab: check 1-RSB at OTHER axes (temperature, learning rate, sparse noise).

MIDDLE-BAND: max gap in [0.03, 0.10).
  Interpretation: inconclusive; run with larger N or more seeds.

## Self-test verification (exp_dev pre-checks before smoke gate)

Self-test cells from v1 (all passed in v1 gate run):
- ({"max_hysteresis_gap": 0.12}, "HYSTERESIS_1RSB_CONFIRMED")
- ({"max_hysteresis_gap": 0.02}, "HYSTERESIS_RS_SMOOTH")
- ({"max_hysteresis_gap": 0.06}, "HYSTERESIS_MIDDLE")
- ({"max_hysteresis_gap": 0.10}, "HYSTERESIS_1RSB_CONFIRMED")   # boundary: >= threshold
- ({"max_hysteresis_gap": 0.03}, "HYSTERESIS_MIDDLE")            # boundary: >= lower
- ({}, "HYSTERESIS_RS_SMOOTH")                                    # missing key -> 0.0 < 0.03

v2 ADDITIONAL self-test: verify evaluate_bpc accepts 10-arg call with dummy tensors at N=8:
  W = zeros(8,8); pool_v = zeros(16,8); pool_l = zeros(16,dtype=long); pool_u=0
  byte_atoms = randn(256,8); pos_atoms = randn(4,8)
  eval_bytes = zeros(10,4,dtype=long); eval_tgt = zeros(10,dtype=long)
  Result should not raise TypeError.

## No design changes needed

The 1-RSB hysteresis hypothesis is intact. The v1 script bug was in retA measurement
only, not in training or sweep design. Same pre-registered bands apply.
