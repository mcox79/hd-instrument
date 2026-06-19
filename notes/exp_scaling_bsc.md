# Experiment: BSC bundle-capacity scaling exponent vs N

**Date:** 2026-05-17
**Phase:** Week 8 scaling-law experiment (part 2)

## Goal

Fit the BSC analogue of the FHRR scaling law from `exp_scaling_capacity.md`. Confirm or falsify whether the binary substrate has the same alpha = 1.0 exponent as FHRR, distinguishing whether BSC's lower capacity at fixed N is a constant-factor penalty (best case for hardware-substrate goal) or a scaling-exponent penalty (worse).

## Setup

Same as FHRR scaling experiment:
- Sweep N in {1024, 4096, 8192, 16384}
- Sweep k in {10, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400}
- Pool size 200, 10 trials per cell
- Substrate: BSC (+/-1 with elementwise mul / sign-of-sum / normalized dot product)

## Pre-registered prediction

- alpha_BSC = 1.0 (same scaling shape as FHRR -- both are random-vector substrates with crosstalk dominating capacity).
- Constant offset (intercept) lower than FHRR's, consistent with M6's observation that BSC at N=1024 has ~2.5x lower k_50% than FHRR.

## Result (2026-05-17)

| N | empirical k_50% | FHRR k_50% (reference) | FHRR/BSC ratio |
|---|---|---|---|
| 1024 | 86 | 217 | 2.52 |
| 4096 | 355 | 874 | 2.46 |
| 8192 | 698 | 1745 | 2.50 |
| 16384 | 1394 | 3509 | 2.52 |

Fitted scaling law:
- **alpha_BSC = 1.004**
- intercept = -2.495 (so prefactor = exp(-2.495) = 0.082; `k_50% ~ N / 12.2`)
- **R^2 = 0.9999**

## Takeaway: BSC scales identically to FHRR (alpha-equivalent); the cost is purely a constant prefactor

The 2.5x FHRR/BSC capacity ratio is essentially constant across N (between 2.46 and 2.52 across the 16x N range tested). Combined with FHRR's 8x storage cost per atom (8 bytes vs 1 byte), the **bytes-per-stored-capacity** ratio remains the same FHRR/BSC = 8/2.5 = 3.2x at every N tested.

This is a strong positive result for the hardware-substrate goal: BSC's binary representation gives 3.2x more storage efficiency without paying a scaling-exponent penalty. The substrates' scaling laws differ only in the constant prefactor.

## Pre-registration check

- alpha_BSC predicted to be 1.0: confirmed (1.004 within fit noise).
- BSC at N=1024 should be near M6's ~85 (50% recovery): confirmed (86.1).
- FHRR/BSC ratio approximately constant across N: confirmed (2.46-2.52 across 16x N range).

No falsification threshold tripped. The prediction held with high precision.

## Implications

For hardware deployment of HDC:
- **Memory-bound workloads** (edge devices, neuromorphic, in-memory compute): BSC wins by 3.2x at every dimension, with no scaling penalty as you go larger.
- **Capacity-bound workloads** (need k stored items): FHRR wins by 2.5x at every N. To match BSC's capacity at N=1024, FHRR needs only N=410.
- **The exponents are equal** (both ~1.0), so the choice between substrates is purely "which prefactor matters more for your use case."

The fact that the exponent is exactly 1.0 for both substrates (within fit noise across 16x of N) is reassurance that no scaling cliff exists in this regime. The substrates are "scale-equivalent" up to a constant.

## What this implies for Week 8's overall framing

The Week 8 plan asked: "could high connectivity scale HDC to LLM-like capabilities?" The exponents from FHRR and BSC are both pinned at alpha ~ 1.0. To match an LLM context window (say 1M discrete tokens at modest similarity), the substrate needs N ~ 5M for FHRR or N ~ 12M for BSC. These are big but feasible at modern compute (RAM and matmul speed both scale).

The honest takeaway: capacity DOES scale with N as predicted, with NO super-linear or sub-linear surprises. The substrate is a tame, well-behaved scaling system at the dimensions tested. To reach LLM-scale you'd need 6-7 orders of magnitude more atoms; nothing in the substrate physics breaks if you do, but the engineering challenge is real and orthogonal to the algebraic substrate question.
