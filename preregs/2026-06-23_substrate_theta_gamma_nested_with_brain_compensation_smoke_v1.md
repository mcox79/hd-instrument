# Prereg: substrate_theta_gamma_nested_with_brain_compensation_smoke_v1

**Filed:** 2026-06-23
**Filed-by:** exp_dev
**Source hand-off:** notes/exp_dev_handoff_research_theta_gamma_SNR_compensation_brain_mechanism_2026-06-23.md

## Hypothesis

Brain-canonical structural compensators (sparse-bipolar codebook f=0.02, CERT 592) plus
per-gamma-cycle Hopfield attractor cleanup recover the structural SNR deficit of theta-gamma
nested oscillation versus single-frequency lock-in. If HARD_PASS, substrate gains a
multi-item-per-gamma-cycle buffer (4-8 items at recall >= 0.95).

## Arms (6)

1. ARM_SINGLE_LOCKIN: single-frequency P=32 lock-in on dense bipolar codebook (baseline)
2. ARM_NESTED_BASELINE: theta-gamma nested on dense bipolar (v1 deficit reproduction)
3. ARM_NESTED_SPARSE: theta-gamma on sparse-bipolar codebook (f=0.02, CERT 592)
4. ARM_NESTED_CLEANUP: theta-gamma on dense codebook + per-gamma Hopfield cleanup (tau=0.3)
5. ARM_NESTED_BRAIN_FULL: sparse codebook + cleanup (compose arms 3+4)
6. ARM_SINGLE_LOCKIN_SPARSE: single-freq on sparse codebook (control; negativity-check #3)

## Pre-registered HARD bands (immutable; from handoff)

### HARD_PASS (any one suffices):
- CRITERION_A: ARM_NESTED_BRAIN_FULL recall@1 at sigma=16 >= ARM_SINGLE_LOCKIN recall@1 - 0.02
- CRITERION_B: ARM_NESTED_BRAIN_FULL recall@1 at sigma=32 >= ARM_SINGLE_LOCKIN recall@1 + 0.05
- CRITERION_C: ARM_NESTED_SPARSE AND ARM_NESTED_CLEANUP each add >= 0.10 recall vs NESTED_BASELINE at sigma=16

### HARD_FAIL (any one triggers; route to TDM-gating Anchor 2):
- HARD_FAIL_1: ARM_NESTED_BRAIN_FULL <= ARM_NESTED_BASELINE + 0.03 at ALL sigmas
- HARD_FAIL_2: ARM_NESTED_SPARSE < ARM_NESTED_BASELINE at sigma=16
- HARD_FAIL_3: ARM_NESTED_CLEANUP degrades vs BASELINE at sigma=4 by > 0.05

### MIDDLE_BAND:
- ARM_NESTED_BRAIN_FULL exceeds NESTED_BASELINE by 0.05-0.10 but below single-frequency.

## Config (smoke)

N=512, M=50, seeds=[7,17,23], sigmas=[4,8,16,32,64]
P_theta=4, P_gamma=7, P_single=32, k_theta=1, k_gamma=31
sparse_f=0.02, cleanup_tau=0.30, cleanup_temp=4.0 (scale_by_sqrt_d=True)
N_EVAL=80

## Config (full; gated on smoke HARD_PASS)

N=4096, M=500, seeds=[7,17,23], sigmas=[4,8,16,32,64,128]
P_theta=8, P_gamma=7, P_single=64
Routing: remote_cpu_queue (~45-90min)

## N-suffix note (PROT-018)

No _n<N> suffix in anchor name. Production N=4096 explicit. Rationale: mechanism-comparison
cell; N=4096 chosen for remote_cpu tractability.

## Smoke result (2026-06-23)

**VERDICT: HARD_FAIL** (smoke wall=1.53s)

Per-arm recall at sigma=16 (mean over 3 seeds):
- ARM_SINGLE_LOCKIN: 0.9958
- ARM_NESTED_BASELINE: 0.9125
- ARM_NESTED_SPARSE: 0.0375 (HARD_FAIL_2 triggers: < NESTED_BASELINE)
- ARM_NESTED_CLEANUP: 0.9042
- ARM_NESTED_BRAIN_FULL: 0.0625 (HARD_FAIL_1 triggers: not > BASELINE + 0.03)
- ARM_SINGLE_LOCKIN_SPARSE: 0.1000

### Root cause (structural; not instrumentation suspect)

N=512 * f=0.02 = ~10 active dimensions per sparse vector. The lock-in demod accumulates
phase-rotated projections; with only 10 active dims the per-phase overlap is ~10/512,
destroying SNR before phase averaging can compensate. Control arm ARM_SINGLE_LOCKIN_SPARSE
confirms: even single-freq recall collapses to 0.808 at sigma=4 on sparse codebook vs 1.000
on dense. The ARM_NESTED_CLEANUP (dense + cleanup) behaves normally (0.904 at sigma=16),
confirming cell instrumentation is correct.

At N=4096 with f=0.02: ~82 active dims -- qualitatively different regime. Sparse compensation
may be viable at full N. Reroute to Strategy for: (a) N-scaling gate-test of sparse arm OR
(b) pivot to TDM-gating Anchor 2.

## Timeout estimate

Not applicable (HARD_FAIL at smoke; full run not authorized).
If full run were authorized: smoke_wall=1.53s, N_full/N_smoke = 4096/512 = 8, seeds 3/3,
scaling_exp=1.5 (nested demod is O(N*P_theta*P_gamma) moderate super-linear):
timeout = ceil(1.5 * 1.53 * 8^1.5 * 1) = ceil(1.5 * 1.53 * 22.6) = ceil(52s) = 300s.
Very short; full run is CPU-tractable. But not authorized without Strategy review per HARD_FAIL gate.
