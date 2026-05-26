# Pre-registration: PAC-Bayes Laplace-Fisher self-test verifier

**Filed:** 2026-05-25
**Script:** experiments/exp_wave14_pac_bayes_laplace_selftests_v1.py
**Queue:** local_cpu_queue
**Estimated runtime:** <5s

## Hypothesis

The Laplace-Fisher KL formula from R-PRIME-1 handoff (commit 0140545) must pass all
4 self-test pairs (from the handoff doc) BEFORE the GPU v2 run proceeds. This probe
verifies the formula implementation is correct, independent of the GPU run.

Also tests whether the ALT3_LAPLACE_ASSUMPTION_VIOLATED diagnosis is structurally
expected (Hebbian outer-product always produces large ||Delta_W||/||W_A|| ratios),
which would validate the v2 remedy approach.

## Pre-registered outcomes

**SELF_TEST_PASS:** all 4 canonical handoff self-tests pass to stated tolerances.
Formula verified; GPU v2 run is safe.

**SELF_TEST_FAIL:** >= 1 self-test fails. Do NOT proceed with GPU v2 run until fixed.

## Self-test pairs (from R-PRIME-1 handoff)

1. W_A=W_B, f_A=f_B -> KL = 0 (|KL| < 1e-9) for N in {16, 64, 256}
2. W_A=0, W_B=1, f_A=4, f_B=1, ridge=0 -> KL = 2.8069 (residual < 1e-4)
3. N=4, single high-Fisher entry: f_A[0,0]=100, W_B[0,0]=1 -> KL = 50.0 (residual < 1e-4)
4. Monotonicity: f_A=f_B=ones, W_B = alpha*randn, KL proportional to alpha^2 (rel_err < 1e-6)
