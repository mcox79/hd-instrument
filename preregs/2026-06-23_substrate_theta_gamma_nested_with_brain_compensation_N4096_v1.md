# Prereg: substrate_theta_gamma_nested_with_brain_compensation_N4096_v1

**Filed:** 2026-06-23
**Filed-by:** exp_dev
**Source hand-off:** notes/exp_dev_handoff_research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md
**Strategy push (N-scale rationale):** notes/exp_dev_to_strategy_brain_comp_HARD_FAIL_2026-06-23.md

## N-suffix

No `_n<NUMBER>` (lowercase n) suffix in anchor name. Anchor name contains `_N4096_` (uppercase N)
which is NOT a PROT-018 trigger. Production N = 4096. Rationale: this is the production-scale
brain-compensation test cell; N is encoded in the human-readable name for clarity, not as a
PROT-018 suffix. Script production config: `N_DIM = 4096` in the else-branch of SMOKE block.

## Hypothesis

N=512 smoke HARD_FAILed because f=0.02 x N=512 = ~10 active dims, insufficient projection
overlap for cyclic-roll phase averaging. N=4096 x f=0.02 = 82 active dims is a qualitatively
different regime (Aso-Rubin sparsity threshold). Brain-canonical structural compensators
(sparse-bipolar codebook f=0.02, CERT 592; per-gamma-cycle Hopfield attractor cleanup) may
recover the structural SNR deficit of theta-gamma nested oscillation vs single-frequency
lock-in at N=4096.

## Arms (6)

1. ARM_SINGLE_LOCKIN:        single-frequency P=64 lock-in on dense bipolar (baseline)
2. ARM_NESTED_BASELINE:      theta-gamma nested on dense bipolar (v1 deficit reproduction)
3. ARM_NESTED_SPARSE:        theta-gamma on sparse-bipolar codebook (f=0.02, CERT 592)
4. ARM_NESTED_CLEANUP:       theta-gamma on dense codebook + per-gamma Hopfield cleanup (tau=0.3)
5. ARM_NESTED_BRAIN_FULL:    sparse codebook + cleanup (compose arms 3+4)
6. ARM_SINGLE_LOCKIN_SPARSE: single-freq on sparse codebook (control; negativity-check #3)

## Pre-registered HARD bands (immutable; from handoff)

### HARD_PASS (any one suffices):
- CRITERION_A: ARM_NESTED_BRAIN_FULL recall@1 at sigma=16 >= ARM_SINGLE_LOCKIN recall@1 - 0.02
- CRITERION_B: ARM_NESTED_BRAIN_FULL recall@1 at sigma=32 >= ARM_SINGLE_LOCKIN recall@1 + 0.05
- CRITERION_C: ARM_NESTED_SPARSE AND ARM_NESTED_CLEANUP each add >= 0.10 recall vs NESTED_BASELINE at sigma=16

  If A+B both pass: chain-grade-eligible (META = brain-compensated-nested recovers-and-exceeds).

### HARD_FAIL (any one triggers; route to TDM-gating Anchor 2):
- HARD_FAIL_1: ARM_NESTED_BRAIN_FULL <= ARM_NESTED_BASELINE + 0.03 at ALL sigmas
- HARD_FAIL_2: ARM_NESTED_SPARSE < ARM_NESTED_BASELINE at sigma=16
  (N=512 smoke already confirmed this; N=4096 = 82 active dims is the scale-gate test)
- HARD_FAIL_3: ARM_NESTED_CLEANUP degrades vs BASELINE at sigma=4 by > 0.05

### MIDDLE_BAND:
- ARM_NESTED_BRAIN_FULL exceeds NESTED_BASELINE by 0.05-0.10 but below single-frequency.
  Tune f-grid + tau-grid OR pivot to TDM-gating.

## Config (production; N=4096 direct-to-FULL; smoke SKIP justified)

N=4096, M=500, seeds=[7,17,23], sigmas=[4,8,16,32,64,128]
P_theta=8, P_gamma=7, P_single=64, k_theta=1, k_gamma=31
sparse_f=0.02 (82 active dims at N=4096), cleanup_tau=0.30, cleanup_temp=4.0
N_EVAL=200
Routing: remote_cpu_queue (~60-120min)

## Smoke skip justification

N=512 smoke of the 6-arm cell already ran and HARD_FAILed structurally on
ARM_NESTED_SPARSE (10 active dims, insufficient overlap). The science question
is whether N=4096 (82 active dims) escapes this failure mode. Running another
N=512 smoke would re-confirm the known failure, not gate the experiment.
USER explicit directive: skip local smoke; go direct to N=4096 remote_cpu_queue.

## Script location

experiments/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1.py
