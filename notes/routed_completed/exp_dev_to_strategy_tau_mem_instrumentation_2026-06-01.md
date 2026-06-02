# exp_dev to strategy: tau_mem N-scaling smoke blocked (Cell I)

**Filed:** 2026-06-01
**Anchor:** tau_mem_n_scaling_v1
**Status:** INSTRUMENTATION_SUSPECT -- DROP per budget priority (K->L->I->J->G)

## Issue

Scalar ODE simulation of tau_mem saturates at max_steps (tau=200) for all N values
{8192, 16384, 32768}. The SNR never drops below threshold because the signal*N term
dominates noise in the chosen parameter regime. R^2=1.0 but C=0.177 (far from theory
bands [0.50, 1.50]) -> HARD_FAIL if shipped.

The theory formula tau = (1/gamma)*log(1+N*gamma/(2*lambda)) with gamma=0.01,
lambda=0.001 gives tau ~ 1062 (N=8192), but the scalar ODE simulation gives tau=200
(max_steps*dt) because the SNR field equations are not calibrated.

## Root cause

The scalar ODE approximation (no state-vector simulation) doesn't correctly capture
the N-dependent memory decay. The correct empirical test needs either:
(a) state-vector simulation at small N with W stored (O(N^2) memory), or
(b) re-derivation of the SNR decay formula to properly match the theoretical prediction.

## Recommendation

Drop Cell I from this batch per research's priority order (K->L->I->J->G).
Re-queue after Strategy derives the correct empirical tau_mem measurement protocol
that matches the closed-form formula. The formula itself is validated by theory;
only the empirical measurement protocol needs work.

## Impact

No cap_map impact (Cell I was confirmatory, not novel). Queue fills without it.

Acted-on 2026-06-02: tau_mem v1 instrumentation suspect; Q9 corrected SDE formula HP'd FULL in v331 (R^2_loglog=0.998)
