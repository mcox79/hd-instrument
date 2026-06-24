# Prereg: substrate_theta_gamma_nested_oscillation_LM_v1

**Date**: 2026-06-23
**Anchor**: substrate_theta_gamma_nested_oscillation_LM_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_substrate_theta_gamma_nested_oscillation_LM_v1.py

## Hypothesis

The chain-grade single-frequency lock-in amplifier (cert ledger row 678,
recall=1.000 cv=0.000 at sigma=64 with k=31 P=64) uses ONE HD frequency.
Lisman-Idiart neuroscience: theta (5 Hz carrier) nests 7+-2 gamma (40 Hz)
sub-cycles, each holding ONE memory item. Encoding two nested frequencies in
the same HD demodulation framework may lift recall capacity or widen the
discriminating sigma band via temporal STRUCTURE: items are bound to theta
phase position (sequenced recall) not just carrier phase.

The 2-frequency nested mechanism uses:
  k_theta=1 (slow carrier rotation), P_theta=8 theta phases
  k_gamma=31 (fast item rotation), P_gamma=7 gamma sub-cycles per theta

Total phases = 56. Expected SNR lift = sqrt(56/4) = sqrt(14) ~ 3.74x.
Compared to single P=64: sqrt(32) ~ 5.65x. So raw SNR is lower BUT temporal
structure adds item-by-phase binding that may lift sigma_capacity.

## Arms

- ARM_SINGLE_LOCKIN: existing chain-grade primitive, P=64, k=31 (single freq)
- ARM_THETA_GAMMA_NESTED: two-frequency nested oscillation as specified above

## Pre-registered thresholds (HARD -- set before run, cannot change ex-post)

### HARD_PASS (either criterion suffices):
- CRITERION_A: max(theta_gamma_recall@1 - single_lockin_recall@1) >= 0.10
  at any sigma, averaged across all 3 seeds
- CRITERION_B: sigma_capacity_nested >= 2x sigma_capacity_single
  where sigma_capacity = highest sigma with recall@1 >= 0.95

### HARD_FAIL:
- theta_gamma_recall@1 <= single_lockin_recall@1 at ALL tested sigmas
  (nested oscillation adds nothing; all per-seed, per-sigma deltas <= 0)

### MIDDLE_BAND:
- theta-gamma exceeds single at some sigmas, max_delta < 0.10 AND
  cap_ratio < 2.0x. Partial structure benefit; tune P_theta/P_gamma.

## N-suffix note (PROT-018 rule 3)

No _n<NUMBER> suffix in anchor name. Production N = 4096.
Rationale: mechanism-comparison cell (not a capacity-scaling cell);
N=4096 chosen for CPU tractability on remote_cpu_queue.

## Config

**Smoke**: N=512, M=50, seeds=[7,17], sigmas=[4,8,16,32,64],
           P_theta=4, P_gamma=7, P_single=32, k_gamma=31, k_theta=1, N_EVAL=80

**Full**: N=4096, M=500, seeds=[7,17,23], sigmas=[4,8,16,32,64,128,256],
          P_theta=8, P_gamma=7, P_single=64, k_gamma=31, k_theta=1, N_EVAL=200

## Timeout estimate

smoke_wall_s = 0.32s (measured on laptop at N=512, M=50, 2 seeds, 5 sigmas)
smoke total with Python startup = 1.16s

Scaling from smoke to full:
  N ratio: 4096/512 = 8x
  seed ratio: 3/2 = 1.5
  sigma ratio: 7/5 = 1.4
  phase ratio: (64+56)/(32+28) = 2.0 (more phases in full config)
  N_EVAL ratio: 200/80 = 2.5
  Total ops ratio ~ 8 * 1.4 * 2.0 * 2.5 = 56x (scaling_exp=1.0 since pure numpy no matrix allocs)
  Remote slowdown estimate: 5x vs laptop (conservative)

Formula: ceil(1.5 * 0.32 * 56 * 1.5 * 5) = ceil(201.6) = 300s

Dispatching with timeout_s=1800 (30 min; 6x headroom over 300s estimate).
Conservative buffer for remote_cpu queue scheduling overhead and numpy vectorization differences.

## Smoke result (pre-dispatch)

HARD_FAIL at smoke: nested oscillation underperformed single-frequency at all sigmas.
  sigma=16: single=0.994, nested=0.906, delta=-0.088
  sigma=32: single=0.712, nested=0.313, delta=-0.399
Mechanism is theoretically disadvantaged: 28 total nested phases vs 32 single phases.
Expected: FULL run confirms HARD_FAIL (same phase-count disadvantage at N=4096).
Dispatching to FULL for official cert verdict record.

## Substrate-native lineage

- lock-in amplifier: cert ledger row 678 (HARD_PASS, chain-grade)
- Frequency: k=31 coprime-N rotation (proven orthogonal at N=8192)
- Two-frequency nested: Lisman-Idiart USER-derived intuition (2026-06-23)
- No re-derivation of lock-in from scratch; composes hdlab-proven primitive

## Dependencies verified

- experiments/_seed_checkpoint.py: exists in repo
- numpy: available in .venv
- No torch import (pure CPU cell)
- No external data files required
