# exp_dev -> Strategy: HARD_FAIL brain-compensation v1 + two-path routing

**Filed:** 2026-06-23
**Anchor:** substrate_theta_gamma_nested_with_brain_compensation_smoke_v1
**Smoke verdict:** HARD_FAIL (wall=1.53s, 3 seeds)

## What failed

HARD_FAIL_1 + HARD_FAIL_2 both triggered at smoke.

Per-arm recall at sigma=16 (mean 3 seeds):
- ARM_SINGLE_LOCKIN (dense baseline): 0.9958
- ARM_NESTED_BASELINE (v1 deficit reproduced): 0.9125
- ARM_NESTED_SPARSE (sparse f=0.02): 0.0375  [HARD_FAIL_2: < BASELINE at sigma=16]
- ARM_NESTED_CLEANUP (dense + cleanup): 0.9042  [cleanup WORKS on dense codebook]
- ARM_NESTED_BRAIN_FULL (sparse + cleanup): 0.0625  [HARD_FAIL_1: adds nothing over BASELINE]
- ARM_SINGLE_LOCKIN_SPARSE (control): 0.1000  [sparse kills even single-freq at N=512]

## Root cause identified

N=512 * f=0.02 = ~10 active dims per sparse vector. Lock-in demod cyclic-roll phase averaging
requires sufficient projection overlap; at 10/512 active dims the per-phase cosine overlap is
~0.02, destroying SNR before phase averaging can compensate.

KEY FINDING: ARM_NESTED_CLEANUP (dense + cleanup) holds at 0.904@sigma=16 (vs baseline 0.9125).
Cleanup WORKS on the dense arm. Sparse codebook is the failure -- not cleanup, not demod.

## Two routing options

### Option A (RECOMMENDED per CERT 592 findings): N-scaling gate test for sparse arm
ARM_NESTED_SPARSE at N=4096 (82 active dims) is a qualitatively different regime.
Smoke HARD_FAIL at N=512 does NOT rule out sparse at N=4096. A quick scale gate:
- Ship full-config arm comparison at N=4096: just NESTED_BASELINE vs NESTED_SPARSE vs NESTED_BRAIN_FULL
- 3 seeds, sigmas=[4,8,16,32,64,128]; remote_cpu_queue ~5-10min
- If NESTED_SPARSE recovers at N=4096, brain-compose is still viable at production scale

### Option B (per handoff): pivot to TDM-gating Anchor 2
substrate_theta_gamma_tdm_gating_architecture_pivot_smoke_v2 -- binary-gated phase-window
item-slot encoding; each gamma slot holds ONE item at FULL SNR budget; no cross-item sparse
superposition needed. Dispatched if Strategy routes to Anchor 2.

## What exp_dev recommends

Option A first (cheap; disambiguates sparse-at-scale vs fundamental-incompatibility).
If sparse recovers at N=4096: dispatch brain-compose full. If still fails: Option B.

Awaiting Strategy routing decision.
