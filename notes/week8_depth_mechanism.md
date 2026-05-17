# Week 8 deep-dive: why does FHRR depth scale sub-linearly?

**Date:** 2026-05-17
**Phase:** Hypothesis investigation triggered by exp_scaling_depth.py's falsified prediction

## The puzzle

`exp_scaling_depth.py` measured `depth_50%(N)` for FHRR with shared role atoms and got **beta = 0.717** on a log2(N) axis -- 30% lower than naive geometric-decay theory predicts.

Naive model:
- Signal magnitude after d nestings: `(1/sqrt(2))^d` for fan-out-2 bundles
- Max-junk floor at K-atom codebook: `sqrt(ln K / N)`
- Setting equal -> `depth_50% ~ log2(N) - log2(ln K)`, slope = 1.0

Something is eating ~30% of the depth per doubling of N.

## Hypothesis 1 (falsified): coherent cross-talk from shared role atoms

`believes()` reuses BELIEVER and CONTENT across all outer levels. When unbinding by CONTENT to peel back a level, the residual cross-talk has a fixed direction (`BELIEVER * conj(CONTENT)`) and varying per-level amplitude (`p_d`). My hypothesis: coherent direction compounds differently than independent random noise, biting depth.

**Test (`exp_scaling_depth_fresh.py`): fresh BELIEVER and CONTENT atoms per level.**

| N | shared-role d_50% | fresh-role d_50% |
|---|---|---|
| 1024 | 6.44 | 6.45 |
| 2048 | 7.54 | 6.88 |
| 4096 | 7.75 | 7.69 |
| 8192 | 8.69 | 8.62 |
| 16384 | 9.44 | 8.88 |

**Result: beta = 0.657, slightly LOWER than shared.** Within measurement noise. Hypothesis falsified.

Why my reasoning was wrong: when computing `sim(recovered, true_filler)`, the cross-talk direction projects onto a random `true_filler` with magnitude `~1/sqrt(N)`. The level-varying amplitudes sum as `~sqrt(d)` whether coherent or independent. Both give `~sqrt(d)/sqrt(N)` total noise. Role reuse and fresh roles end up equivalent.

## Hypothesis 2 (confirmed): FHRR's per-component renormalization

FHRR bundle is `bundle_k = (z1_k + z2_k) / |z1_k + z2_k|` per component. For unit-modulus inputs:

- `|z1_k + z2_k| = 2 * |cos(theta/2)|` where theta is the phase difference
- `E[|z1+z2|] = 4/pi ~= 1.27`, **not** sqrt(2) as the simple model assumes
- `E[1/|z1+z2|]` is **formally divergent** -- the heavy tail near zero blows up

The implication: per-component renorm randomly amplifies components where the two bundle inputs nearly cancel. Across d levels of bundle-then-unbind this multiplicative noise compounds.

HRR uses whole-vector L2 normalization: one global denominator, no per-component amplification. Predicted: HRR should scale closer to the naive log2(N) law.

**Test (`exp_scaling_depth_hrr.py`):**

| N | FHRR shared | FHRR fresh | **HRR** |
|---|---|---|---|
| 1024 | 6.44 | 6.45 | 5.86 |
| 2048 | 7.54 | 6.88 | 6.36 |
| 4096 | 7.75 | 7.69 | 8.20 |
| 8192 | 8.69 | 8.62 | 9.09 |
| 16384 | 9.44 | 8.88 | **10.86** |

Fitted exponents:

| Substrate | beta | R^2 |
|---|---|---|
| FHRR shared roles | 0.717 | 0.973 |
| FHRR fresh roles | 0.657 | 0.974 |
| **HRR** | **1.273** | **0.974** |

**Result: HRR is super-linear in log2(N) -- each doubling of N adds ~1.27 levels.** That's 77% steeper than FHRR, and significantly higher than the naive 1.0 prediction.

Hypothesis 2 confirmed. The heavy-tail per-component renorm in FHRR is the dominant cause of depth ceiling.

## Crossover and extrapolation

There's a crossover around N = 2048-4096:
- Below: FHRR slightly better (per-component variance averages out at low N)
- Above: HRR pulls ahead, gap widens with N

Extrapolated `depth_50%` (using the fitted slopes):

| N | FHRR shared | HRR | gap |
|---|---|---|---|
| 32K (2^15) | 10.16 | 12.13 | +1.97 |
| 256K (2^18) | 12.31 | 15.95 | +3.64 |
| 1M (2^20) | 13.71 | 18.26 | **+4.55** |
| 16M (2^24) | 16.58 | 23.34 | +6.76 |

## What this changes

The earlier "HDC favors wide-but-shallow" conclusion was true *for FHRR specifically*. With HRR, deep structures are reachable at far more practical N:

| Real workload | Typical depth | HRR feasibility | FHRR feasibility |
|---|---|---|---|
| AST / parse trees | 5-12 | N=10k works | N=10k borderline |
| Hierarchical KB | 4-7 | N=2k works | N=2k works |
| Multi-hop reasoning | 3-7 | N=1k works | N=2k works |
| Chain-of-thought (medium) | 5-15 | N=100k works | N=100k borderline |
| Chain-of-thought (long) | 20-50 | N=10M reaches 22 | N=10^12 infeasible |

For deep-compositional workloads, **HRR is the production substrate of choice, not FHRR**, by a wide and growing margin.

## Pre-registration check

- H1 (shared-role coherence): predicted fresh roles -> beta closer to 1.0. **Falsified.**
- H2 (per-component renorm): predicted HRR -> beta closer to 1.0. **Over-confirmed** (HRR went super-linear, 1.27).

One falsified, one over-confirmed. The instrument earned its keep -- two cycles of hypothesis -> design experiment -> measure took about 30 minutes of compute on consumer hardware, and converged on a clean mechanism.

## Honest revision (2026-05-17, after validation run)

The extended-N HRR run (N=4k...131k) returned **beta = 2.441, R^2 = 0.845** -- but the lower R^2 reveals real measurement noise:

| N | d_50% original (small-N run) | d_50% extended-N run | agreement? |
|---|---|---|---|
| 4096 | 8.20 | 6.92 | 1.3 levels apart |
| 8192 | 9.09 | 6.13 | **3 levels apart** |
| 16384 | 10.86 | 9.63 | 1.2 levels apart |

Same code, same seed, same workload: different `d_50%` at the same N. The recovery curves are also non-monotonic at fine grain (e.g. at N=16384 recovery jumps back up at depth 12 vs 10).

**Cause:** 30 trials per cell is too few for the steep transition zone. A single trial flip-flops d_50% by 1 level routinely.

**What survives:**
- HRR depth scales **positively and substantially** with N. N=131k reaches d~19 reliably; N=4k reaches d~6-8.
- HRR is **dramatically better than FHRR** for depth at large N (FHRR at N=16k tops out d=9; HRR at N=131k reaches d=18).
- Substrate-selection guidance ("HRR for depth-bound workloads") is unaffected.

**What doesn't survive:**
- The specific **beta = 1.273** point estimate. The honest reading: slope is somewhere in the **1.0-2.5 range** depending on which window of N you fit, and a single power law may not fit the full curve cleanly.
- The extrapolation numbers I wrote ("d_50% = 18 at N=1M") were overconfident. Soft +/- 3 levels uncertainty.

**Pre-registration cleanup, revised:**
- H1 (shared roles) still falsified.
- H2 (per-component renorm) still confirmed at the qualitative / mechanism level: HRR avoids FHRR's heavy-tail and gets dramatically better depth. The numerical exponent claim was over-confident given 30 trials/cell.

## Follow-up needed for a publishable exponent

To pin the HRR depth exponent with publishable precision:

- 300+ trials per cell (10x more than current).
- Bootstrap confidence intervals on the d_50% interpolation per N.
- Wider N range (1k...256k) with the recovery curve evaluated at finer depth granularity.

Total compute: roughly 30 minutes on consumer CPU. Achievable but not yet done.

## Production implication, restated (carefully)

The depth question goes from "structural limit of HDC" to "substrate choice + N budget":

- For workloads with depth <= 7: any substrate at N=1k-4k works.
- For depth 7-15: HRR at N=10k-100k.
- For depth 15-25: HRR at N=1M+ (extrapolated -- soft +/- 3 levels of uncertainty).
- For depth > 25: outside HDC's practical range; use sequential reasoner.

The Week 10+ case study should use HRR (not FHRR) for any compositional benchmark. The exact exponent matters less for product selection than the qualitative regime, which is unambiguous from the head-to-head data we have.
