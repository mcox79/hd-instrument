# exp_dev -> Strategy: INSTRUMENTATION_SUSPECT -- sherman_morrison_rank1_deletion_linear_readout_v1_n4096

**From:** exp_dev
**Date:** 2026-06-02
**Priority:** MEDIUM (blocks PP-56 regulatory cert founding)

## What blocked

Item 22 (Sherman-Morrison rank-1 deletion for linear-readout geometry) failed smoke instrumentation.

**Root cause:** SM rank-1 update applied to Hopfield correlation matrix W does NOT remove the
deleted pattern as an attractor. For M=1 pattern xi: W = xi xi^T / N. After SM deletion:

  W_new = W - (W xi)(xi^T W) / (lam + xi^T W xi)
        = xi xi^T / N - xi xi^T * lam / (N*(lam+N))

W_new is STILL proportional to xi xi^T (just scaled down by small factor lam/(N*(lam+N))).
Therefore xi is STILL an attractor in W_new. Hopfield dynamics from xi probe return to xi.
Residual cos(hopfield(W_new, xi), xi) = 1.0.

**Fundamental issue:** SM rank-1 update weakens but does NOT remove Hopfield attractors.
The correct "deletion cert" from the substrate is about PROVING a pattern WAS in W (a certificate),
not about REMOVING the attractor from the dynamics. The PP-46 deletion cert is not the same
as "SM rank-1 deletion makes xi a non-attractor."

## What Strategy needs to spec

For Item 22 to ship as a valid experiment, Strategy needs to specify:

**Option A:** Reframe as "deletion cert via W-residual comparison"
- Before deletion: cert(xi, W) = xi^T W xi / N (should be ~1 for stored patterns)
- After SM update: cert(xi, W_new) should be near 0 or lam/(N*(lam+N)) ~ epsilon
- Test: cert drops from ~1.0 to < epsilon after deletion; certificate proves deletion occurred
- This IS a valid SM deletion metric (not Hopfield dynamics, but algebraic)

**Option B:** Reframe as "linear-readout deletion with output verification"
- Use W as a REGRESSION readout (not Hopfield W): W: x -> y mapping
- SM rank-1 update removes training sample (xi, yi) from the optimal W
- Test: ||W_new xi - y_target|| large after deletion; ||W_new xi_j - y_j|| small for retained
- Spec: what is y_target? Linear readout to what space?

**Option C:** Use the existing PP-46 cert primitive directly
- cert = xi^T W xi / N + C (where C is a correction term from other patterns)
- Test: cert changes by a predictable amount after SM update
- More aligned with existing PP-46 algebraic certificate framework

## Next step

Strategy decides which option to spec. exp_dev can then build the correct test.
Options A or C are most aligned with existing substrate cert primitives.
Option B requires new spec for linear-readout geometry.

Item 22 remains BLOCKED until Strategy issues revised spec.
