# Pre-registration: wave14_S_transform_kerdock_v1

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_S_transform_kerdock_v1.py
**Companion to**: wave14_free_cumulants_kerdock_v1 (GPU running)

## Why this experiment

The AMP_SE_DIVERGES verdict (2026-05-23) established that the substrate's
4-coset Kerdock matrix is outside the standard AMP universality class. The
free cumulants probe (running on GPU) tests ADDITIVE free convolution
structure (R-transform). The S-transform tests MULTIPLICATIVE free
convolution -- a distinct, complementary algebraic-free-probability axis.

S-transform is a genuinely independent probe: a free measure can have one
non-trivial transform and the other trivial (Nica-Speicher 2006 examples).
Two independent algebraic axes detecting non-MP-ness is doubly informative.

## Hypothesis

The first 5 coefficients of the S-transform power series for the Kerdock
spectrum, computed via psi-inversion from empirical moments m_1..m_5,
deviate by > 20% from the MP closed form
  S_{MP(c)}(z) = 1/(c+z) = sum_{k>=0} (-1)^k z^k / c^{k+1}
at some c = M/N in the sweep {0.25, 0.5, 1.0, 2.0, 4.0}.

Brutal-honesty P estimates (updated after smoke):
- P(DIVERGE): **0.95** -- smoke at N=1024 alpha={0.5, 1.0} shows huge
  deviation (50-99% across coefficient orders); FULL at N=4096 will only
  reinforce.
- P(MATCH): **0.02**
- P(INCONCLUSIVE): **0.03**

This is now near-certain. The science question shifts: it's not "does
Kerdock depart from MP" but "by HOW MUCH on each free-prob axis, and what
is the deviation profile shape vs alpha?"

## Predictions

Per-alpha relative deviation S_emp[k] / S_mp[k] - 1 for k in {1..4}.

- **DIVERGE**: at least half cells have worst |dev| > 0.20
- **MATCH**: all cells have worst |dev| < 0.10
- **INCONCLUSIVE**: mixed

Hard-fail:
- Self-test must give exact MP(c=0.25,0.5,1.0,2.0) coefficients
  (1e-6 tolerance) -- PASSED
- If empirical S coefficients are NaN / Inf (zero leading moment): halt
- Runtime > 5 min at N=4096: re-estimate

## Runtime / queue routing

- Pure numpy + recursive series inversion (O(n_max^3) coefficient bootstrap).
  N=4096 SVD is the dominant cost: 5 alpha values x 5 seeds = 25 SVDs at
  N=4096. ~30-60s per SVD on remote CPU -> ~15-25 min total.
- Route: **remote_cpu_queue** (Rule 2)
- Timeout = 1800 s (2x headroom)

## Smoke result

Self-test 5/5 PASS:
- Compositional inverse of z+z^2 gives Catalan-1 sequence (1,-1,2,-5,14)
- MP(c=0.25, 0.5, 1.0, 2.0) S-transforms match 1/(c+z) closed form to 1e-6
- Verdict DIVERGE / MATCH branches both fire correctly

Smoke (N=1024, alpha in {0.5, 1.0}, 2 seeds):
- alpha=0.5: S_emp = (1, -0.37, 0.19, -0.09, 0.05); S_MP = (2, -4, 8, -16, 32)
  -> dev_rel = (-0.50, +0.91, -0.98, +0.99, -1.00) -- ALL coefficients diverge
- alpha=1.0: S_emp = (1, -0.75, 0.75, -0.75, 0.75); S_MP = (1, -1, 1, -1, 1)
  -> dev_rel = (0, +0.25, -0.25, +0.25, -0.25) -- 25% deviation across orders
- Verdict: S_TRANSFORM_DIVERGE

Interpretation: Kerdock 4-coset spectrum is *strongly* non-MP on the
multiplicative free-convolution axis, even more dramatically than on the
free cumulants axis. The deviation has a distinct pattern (geometric, not
random) -- coefficients are systematically suppressed relative to MP.

## Linkage

If FULL also DIVERGE: pair with free_cumulants DIVERGE for two-axis
confirmation that Kerdock departs MP universality. Substrate observability
metric: "S-transform deviation profile" becomes a Cap-4 (observability)
diagnostic.

If FULL MATCH after smoke DIVERGE: would indicate finite-N artifact -- but
unlikely given the magnitude of the smoke deviation.
