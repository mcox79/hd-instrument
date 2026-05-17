# Experiment: nested-structure depth-recovery scaling vs N

**Date:** 2026-05-17
**Phase:** Week 8 scaling-law experiment (part 3)

## Goal

Fit the exponent for `depth_50%(N) = beta * log2(N) + intercept`, where depth_50%(N) is the maximum nesting depth (fan-out 2 per level) at which the innermost leaf atom is recovered correctly 50% of the time via cleanup against a 100-atom pool.

## Naive prediction

Per-level signal decays as `(1/sqrt(2))^d` for fan-out 2. Junk floor at pool size 100 is `sqrt(ln(100) / N)`. Setting signal = junk for the 50% boundary:

    2^(-d/2) = sqrt(ln(100) / N)
    d = log2(N) - log2(ln(100)) = log2(N) - 2.2

So predicted slope `beta = 1.0` on a log2(N) x-axis with intercept ~ -2.2.

## Setup

- N in {1024, 2048, 4096, 8192, 16384} (5 points for the fit).
- depth in {1, 2, ..., 8, 9, 10, 12}.
- 100-atom filler pool, 4 shared role atoms (AGENT, PATIENT, BELIEVER, CONTENT).
- 30 trials per cell.

## Result (2026-05-17)

| N | empirical depth_50% | predicted (beta=1) |
|---|---|---|
| 1024 | 6.44 | 7.8 |
| 2048 | 7.54 | 8.8 |
| 4096 | 7.75 | 9.8 |
| 8192 | 8.69 | 10.8 |
| 16384 | 9.44 | 11.8 |

Fitted scaling law:
- **beta = 0.717** (vs predicted 1.0)
- **intercept = -0.629** (vs predicted -2.2)
- **R^2 = 0.973**

## Takeaway: depth scales sub-linearly in log2(N)

The naive signal-decay model overpredicts depth by ~1-2 levels at every N. Empirical depth scaling is **0.72 levels per doubling of N**, not 1.0.

This means: to double the achievable nesting depth, the substrate dimension must grow by `2^(1/0.717) ~ 2.6x` -- not 2x as naive theory says.

Possible mechanisms for the sub-linear scaling (each adds noise beyond the simple geometric decay):
1. **Compounded unbind noise**: each unbind operation introduces small numerical noise that compounds across levels.
2. **Bundle normalization isn't lossless**: per-component magnitude renormalization of a sum of complex numbers does preserve unit magnitude but distorts the phase distribution in ways that aren't captured by the simple sqrt(2) model.
3. **Cross-level crosstalk**: at depth d, the outer bundling combines (BELIEVER, X) with (CONTENT, inner). The inner has its own internal structure that interferes additively with the outer's components, beyond the multiplicative decay.

These mechanisms together yield the **empirical scaling law `depth_50%(N) ~ 0.72 * log2(N) - 0.63`**.

## Pre-registration check

- beta predicted = 1.0; empirical = 0.717. **Falsified at the 0.7-1.3 tolerance band... barely outside (0.717 is on the boundary).**
- Intercept predicted = -2.2; empirical = -0.629. Way off — the empirical depth at small N is much lower than predicted, so the constant offset adjusts.

This is the first scaling-law experiment where the **pre-registered prediction was falsified** by the data (slope is 30% lower than expected). The R^2 = 0.973 fit is solid though, so the discrepancy is in the model, not in the data. The empirical law replaces the naive theoretical one.

## Resolution (2026-05-17, see notes/week8_depth_mechanism.md)

Follow-up investigation tested two hypotheses for the sub-linearity:

1. **Shared-role coherent cross-talk** -- falsified. Fresh roles per level gave beta = 0.657, essentially identical.
2. **FHRR per-component renormalization** -- confirmed. HRR (whole-vector L2 norm) gave beta = **1.273**, super-linear.

The depth ceiling is a property of the FHRR bundle operator, not of HDC. HRR scales depth much more favorably and is the production substrate of choice for compositional workloads.

## Implications

For LLM-comparable nesting capacity: at N=16384, depth_50% ~ 9.4. To reach depth ~ 100 (analogous to deeply-nested function calls or 100-step reasoning), the required N is `2^((100 + 0.629) / 0.717) ~ 2^140 ~ 10^42` -- not feasible.

Practical depth ceiling per dimension:
- N=1024: depth ~ 6 reliably
- N=16384: depth ~ 9 reliably
- N=1M (predicted): depth ~ 13 (still useful for typical compositional structures)

The exponent is the more honest scaling story than the prefactor: HDC can hold short-to-moderate nested structures, but cannot indefinitely deepen them by adding dimensions. There's diminishing return on N for nesting depth, in contrast to bundle capacity which scales linearly with N.

This is consistent with the empirical observation that HDC works best for "wide-but-shallow" symbolic structures, less well for "deep-but-narrow" ones.
