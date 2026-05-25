# Prereg: wave14_1rsb_hysteresis_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Pred-4 (1-RSB diagnostic) -- Hysteresis under capacity sweep
**Trigger**: pq_retained_v1 MIDDLE (Pred-2 inconclusive); Pred-4 is the sole remaining
             CPU-targeted diagnostic from the 1-RSB battery. Distinguishes first-order
             (discontinuous, hysteretic) from continuous transition at capacity boundary.

## Hypothesis

First-order phase transition (1-RSB) prediction: the substrate shows hysteresis
when capacity is swept through alpha_c. Loading from BELOW alpha_c (low -> high M)
vs from ABOVE (high -> low M) produces different retA curves at the same M cells.
Hysteresis gap = |retA_forward - retA_reverse| >= 0.10 at some M.

RS / continuous transition prediction: both trajectories give the same retA within
seed-variance. Max hysteresis gap < 0.03 everywhere.

## Design (exp_dev autonomy)

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

## Pre-registered falsifier bands (before FULL run)

- **HARD-PASS (1-RSB first-order)**: max hysteresis gap >= 0.10 at any M cell.
  -> HYSTERESIS_1RSB_CONFIRMED: first-order transition signature; 1-RSB framing supported.

- **HARD-FAIL (RS continuous)**: max hysteresis gap < 0.03 everywhere.
  -> HYSTERESIS_RS_SMOOTH: no hysteresis; continuous transition; 1-RSB NOT supported at capacity axis.

- **MIDDLE**: max gap in [0.03, 0.10).
  -> HYSTERESIS_MIDDLE: inconclusive; partial hysteresis may indicate finite-size artifact.

## Self-test cells

({"max_hysteresis_gap": 0.12}) -> HYSTERESIS_1RSB_CONFIRMED
({"max_hysteresis_gap": 0.02}) -> HYSTERESIS_RS_SMOOTH
({"max_hysteresis_gap": 0.06}) -> HYSTERESIS_MIDDLE
({"max_hysteresis_gap": 0.10}) -> HYSTERESIS_1RSB_CONFIRMED  [boundary: >= threshold]
({"max_hysteresis_gap": 0.03}) -> HYSTERESIS_MIDDLE           [boundary: >= lower threshold]
({})                           -> HYSTERESIS_RS_SMOOTH         [missing key -> 0.0 < 0.03]

All 6/6 self-test cases verified in script self_test_verdict().

## Queue entry

`queue=remote_cpu_queue name=wave14_1rsb_hysteresis_v1 script=experiments/exp_wave14_1rsb_hysteresis_v1.py prereg=preregs/2026-05-24_wave14_1rsb_hysteresis_v1.md timeout=5400`
