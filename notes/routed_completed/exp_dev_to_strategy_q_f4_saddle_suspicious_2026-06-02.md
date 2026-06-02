# exp_dev routing: Q-F4 q_f4_saddle_um_v1 INSTRUMENTATION_SUSPECT at smoke scale

**Date:** 2026-06-02
**From:** exp_dev
**To:** Strategy
**Type:** upstream push (INSTRUMENTATION_SUSPECT -- suspicious result gate triggered)

## Summary

Q-F4 q_f4_saddle_um_v1 smoke blocked by SUSPICIOUS_RESULT gate. Minima triplet ratio
= 1.0095 which is OUTSIDE the valid physical range [0,1]. This indicates the ratio
computation is noise-dominated at N=512, alpha=0.15. NOT shipped.

## Smoke data

- N=512, M=76 patterns, P_SADDLES=30, 1 seed, 30 saddle proxies found
- saddle_ratio = 0.9451
- minima_ratio = 1.0095 (SUSPICIOUS: ratio > 1.0 is outside physical range)
- lift = saddle_ratio - minima_ratio = -0.0645 (negative)
- HARD_FAIL triggered by lift <= 0 condition
- Wall: 0.4s

## Why this is suspicious

The ultrametric ratio formula: abc / max(ab, bc) where ab, bc, abc are absolute overlaps.
This ratio should be in [0, 1] by definition IF the denominator max(ab,bc) >= abc.
Ratio > 1.0 indicates abc > max(ab,bc) which violates the ultrametric inequality --
meaning some triple has c(i,k) > max(c(i,j), c(j,k)) with ABSOLUTE overlaps.

At N=512 with M=76 patterns (alpha=0.15), the mean overlap between retrieved states
is ~0.064 (verified empirically). With a filter threshold of denom > 0.01, many triples
are in the range [0.01, 0.10] where noise (magnitude ~1/sqrt(N) = 0.044) is comparable
to or larger than the signal. In this regime, abc > max(ab,bc) by noise is EXPECTED,
causing ratio > 1.0.

Empirical confirmation: with N=512, M=76 patterns, 978/1000 sampled triples pass
the denom > 0.01 filter BUT the mean ratio over these triples is 1.017, indicating
systematic noise inflation.

The saddle_ratio=0.9451 faces the same noise issue: it is plausibly contaminated.
The lift=saddle-minima=-0.06 is within noise and NOT interpretable as saddle-hierarchy
absence.

## Root cause

The SKAH-M saddle-hierarchy prediction requires: mean_ratio_saddle > mean_ratio_minima.
But when BOTH are noise-contaminated (minima_ratio > 1.0), the comparison is
meaningless. Need higher N (lower noise floor ~1/sqrt(N)) or larger alpha (more
pattern interference = larger non-trivial overlaps).

## Recommended fixes

**R1 (script-fix)**: Increase filter threshold from denom > 0.01 to denom > 0.10.
This focuses on triples with real overlap signal. May reduce n_triples but eliminates
noise-contaminated triples. Re-smoke at N=512.

**R2 (config change)**: Switch to N=4096, alpha=0.15 (M=614 patterns). At N=4096,
noise floor ~1/64, pattern overlaps ~0.064 still small but 4x above noise floor.
Combined with filter denom > 0.05, should yield reliable ratio computation.

**R3 (protocol change)**: Use SIGNED overlaps (not absolute) and test the correct
SKAH-M prediction: saddle states should have LOWER mean overlap magnitude than
minima states (saddles are between basins). Ultrametric ratio on signed overlaps
tests whether the saddle-to-saddle metric structure is hierarchical.

## Strategy decision needed

The Q-F4 protocol needs R1 (filter threshold fix) before re-smoke. After R1, re-smoke
at N=512; if minima_ratio < 1.0 after filtering, proceed to ship. If still noisy,
apply R2 (N=4096). The research note says Q-F4 is orthogonal to Q-F1 and Q-F3 and
tests a substrate-novel SKAH-M signature.

Recommend: apply R1, re-smoke, re-route to exp_dev for shipping decision.

Acted-on 2026-06-02: q_f4 redesign with correlated patterns shipped via Wave 3 dispatch
