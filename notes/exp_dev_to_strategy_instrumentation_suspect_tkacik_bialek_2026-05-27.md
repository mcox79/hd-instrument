# exp_dev -> strategy: INSTRUMENTATION_SUSPECT -- tkacik_bialek_maxent_v1

**Filed:** 2026-05-27
**Trigger:** Suspicious-result gate fired on smoke for wave14_ortho_tkacik_bialek_maxent_v1.

## Pattern detected

The s2_ratio (S_2/S_max proxy) is nearly constant at 0.993-0.996 across:
- K sweep: [50, 100, 200, 400]
- N values: [512, 2048]
- Seeds: [7, 17, 23, 31, 41]

This is < 0.3% variation across 5 decades of K/N ratio. A genuine entropy ratio should
vary substantially with K/N (expected range 0.5-0.99 from Tkacik-Bialek empirics).

## Root cause

The s2_ratio proxy formula:
  `ratio = expected_coupling / (expected_coupling + coupling_str)`
where:
  `coupling_str = J_l2^2 / n_pairs`
  `expected_coupling = n_pairs / K`

In all cases, expected_coupling (200/K = 4..0.5) >> coupling_str (J_l2^2/200 ~ 0.02-0.23),
so the denominator is dominated by expected_coupling and ratio ~ 1.0 always.
The proxy has NO discriminating power at these scales.

## What's needed for a valid probe

Option A: Compute exact S_2 using the mean-field approximation:
  S_2 ~ log(Z) = log sum_k exp(-E_k) where E_k is energy under pairwise Ising.
  For N=2048 this requires Monte Carlo sampling (thermodynamic integration).
  Expensive but correct.

Option B: Use the empirical plug-in entropy estimator on the ROWS of the pattern matrix.
  Treat K patterns as i.i.d. draws from the MaxEnt distribution.
  Compute empirical entropy of the induced distribution over pattern types.
  Compare to maximum entropy of K patterns.
  More tractable but requires counting distinct patterns (impractical at N=2048).

Option C: Simplify hypothesis. Instead of S_2/S_max, test:
  "Does the pairwise Ising model's log-likelihood per bit improve as K increases?"
  Metric: mean cross-entropy under fitted J_ij vs independent baseline.
  This is well-defined and tractable.

Option D: Use a DIFFERENT statistical physics proxy for the neural-code probe:
  Fisher information scaling: I_Fisher(theta) = N * k_over_n (known formula for BSC).
  Test whether Fisher information scales as predicted vs capacity cliff.

## Recommendation to Strategy

Redesign the s2 metric to use Option C (log-likelihood ratio / cross-entropy improvement)
or Option D (Fisher information scaling). The current proxy is constant by construction.
Do NOT ship as-is. Route redesign back to exp_dev with a concrete formula.

## Impact

3 other anchors (saddle_cascade_v6, battery_v3_n8192, lit_threads_v2) are VALID and
ready to ship. Only the tkacik_bialek probe is blocked. The 4th GPU anchor slot should
be filled by the lit_threads_v2 (pre-built, smoke pending) instead.
