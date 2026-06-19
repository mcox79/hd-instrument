# Week 8 Scaling Law Summary

**Date:** 2026-05-17
**Phase:** End of Week 8 -- the headline week of the research plan

## What was fit

Three exponents from three independent experiments at consistent protocols (10-30 trials per cell, FHRR seed = BSC seed = depth seed = 42 for reproducibility):

| Experiment | Quantity | Fitted scaling law | R^2 |
|---|---|---|---|
| FHRR capacity | `k_50%(N)` | `~ N^1.003` (`k_50% ~= N / 4.84` for pool=200) | 0.99999734 |
| BSC capacity | `k_50%(N)` | `~ N^1.004` (`k_50% ~= N / 12.2` for pool=200) | 0.9999 |
| Nesting depth | `depth_50%(N)` | `0.717 * log2(N) - 0.629` (pool=100) | 0.973 |

## What the exponents mean for HDC's reach

### Bundle capacity scales linearly with N (alpha ~ 1.0)

Both FHRR and BSC. No super-linear surprises (which would be publishable), no sub-linear surprises (which would also be publishable). The substrate is well-behaved: doubling N doubles the number of role-filler pairs that can be stored with 50% recovery against a 200-atom codebook.

The FHRR/BSC capacity ratio is **2.52x and constant across the 16x N range tested**, meaning BSC's binary representation costs only a fixed constant prefactor, not a scaling penalty.

### Nesting depth scales sub-linearly in log(N) (beta ~ 0.72)

Doubling N adds 0.72 levels of nesting, not 1.0 as naive signal-decay math predicts. Mechanism is some combination of compounded unbind noise, cross-level crosstalk, and bundle normalization distortion. Practical ceiling at modest N:

- N=1024:  depth ~6
- N=16384: depth ~9
- N=10^6:  depth ~13 (extrapolated)

HDC favors **wide-but-shallow** symbolic structures over **deep-but-narrow** ones.

## What this implies about Goal #1 (efficient scalable architecture)

The exponents are honest. Capacity grows linearly with substrate dimension; nesting depth grows logarithmically (sub-linearly). To compete with LLM context windows (millions of distinct items, deeply chained reasoning), N would need to be in the 10^7+ range -- feasible in raw RAM but expensive in compute.

The substrate is "scale-tame" at the tested dimensions: no cliffs, no saturation, just clean polynomial scaling. This is good news (no hidden barriers) and bad news (no hidden speedups either). It supports the hybrid-architecture conclusion from the project's earlier framing: HDC as a structured memory component of larger systems, not a standalone LLM replacement.

## What this implies about Goal #2 (hardware substrates)

The FHRR/BSC comparison is now backed by a real scaling fit, not a single data point:

| Metric | FHRR | BSC | Winner |
|---|---|---|---|
| Capacity at N | N / 4.84 | N / 12.2 | FHRR (2.52x) |
| Storage per atom | 8 bytes (complex64) | 1 byte (int8) | BSC (8x) |
| Bytes per stored capacity | 38.7 | 12.2 | BSC (3.2x) |
| Bind operations | ~6N FLOPs | ~N integer ops | BSC (~12x cheaper) |
| Capacity scaling exponent | 1.003 | 1.004 | Equal |

**Conclusion: BSC dominates for memory-bound or compute-bound deployments at every dimension tested, with no scaling-exponent penalty.** This is the strongest single hardware-substrate finding from the project so far.

For neuromorphic, in-memory, or edge-AI substrates where binary representations are native: BSC is the empirically-justified choice.

## What this implies about Goal #3 (what's not working / where to optimize)

Two specific places where the data suggests improvement is possible:

1. **Depth scaling has sub-linear loss not predicted by theory.** The 28% gap between predicted slope (1.0) and empirical slope (0.717) suggests a real mechanism that wasn't in the naive model. Investigating this could yield a better understanding -- or a substrate variant (e.g., normalized HRR, sparse VSA, learned binding) that pushes the exponent back to 1.0.

2. **Hebbian boost at high N is unmeasured.** M5 showed boost matters at N=256 in the brittle regime. At N=1024+ the substrate is too forgiving for boost to matter. The interesting scaling question: at very high N where plain cleanup is essentially perfect, what does Hebbian add? A scaling-law sweep with varying pool sizes (junk floor controls difficulty) could measure this.

## Pre-registration cleanup

- FHRR capacity exponent in [0.8, 1.2]: **confirmed** at 1.003.
- BSC capacity exponent equal to FHRR: **confirmed** at 1.004.
- FHRR/BSC ratio approximately constant across N: **confirmed** (2.46-2.52).
- Depth exponent in [0.7, 1.3]: **borderline confirmed** at 0.717 (right at the lower edge).

The only surprise: depth scaling is sub-linear. This is a real prediction that didn't survive contact with data. The underlying mechanism is identifiable (compounded noise across levels) and worth a follow-up investigation.

## Status of the original Week 8 deliverable

The PLAN.md called for fitted exponents, plots, and pre-vs-post comparison. **All three are now in this repo:**

- `data/exp_scaling_capacity/dashboard.pdf` (FHRR alpha = 1.003)
- `data/exp_scaling_bsc/dashboard.pdf` (BSC alpha = 1.004)
- `data/exp_scaling_depth/dashboard.pdf` (depth beta = 0.717)
- `notes/exp_scaling_capacity.md`, `notes/exp_scaling_bsc.md`, `notes/exp_scaling_depth.md`

This is the first body of work in the project that could plausibly stand on its own as a methods paper:

> "Empirical scaling laws for bundle capacity and nesting depth in FHRR and BSC vector-symbolic architectures, fitted from a unified observability instrument."

It's not a novelty result on its own -- the alphas confirm well-known theoretical predictions and the depth sub-linearity is a small refinement to known noise models. But the methodology (pre-registered, scaffold-free verification, reproducible harness) and the head-to-head comparison are valuable.

## Next: Week 9 (release) + Week 10+ (case study)

Per the original plan:
- **Week 9**: publish `hd-instrument` v0.1.0 to PyPI, MIT-licensed; MkDocs site with the cert report and these scaling laws embedded; quickstart notebook that runs the diagnostic and produces a PDF.
- **Week 10+**: continual learning on Split-CIFAR-10 case study. With substrate behaviour now empirically mapped, the case study has well-characterized building blocks to compose.
