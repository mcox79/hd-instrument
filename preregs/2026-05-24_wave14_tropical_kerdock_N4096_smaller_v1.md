# Prereg — wave14_tropical_kerdock_N4096_smaller_v1

## Hypothesis

The empirical bit-flip margin distribution for the substrate's 4-coset MM
Kerdock codebook at smaller N (N=1024, 4096 codewords) is **well-defined**
in the same sense as v1's N=4096 measurement: low coefficient of variation
(cv) and low degenerate-trial fraction.

## Pre-registered bands (verbatim from v1 companion)

- **HARD PASS** (`EMP_MARGIN_WELL_DEFINED`):
  - cv (std / mean) <= 0.30
  - p25 (25th-percentile margin) > 0
  - deg_frac <= 0.20

- **HARD FAIL** (`EMP_MARGIN_DEGENERATE`):
  - cv > 0.80 OR deg_frac > 0.20

- **MIDDLE** (`EMP_MARGIN_NOISY_BASELINE`):
  - cv in (0.30, 0.80] with deg_frac <= 0.20.

## Design

- N = 1024 (4-coset MM Kerdock, 4096 codewords).
- eps in {0.1, 0.3, 0.5, 0.7, 0.9}.
- 10 seeds * 5 codewords per eps = 50 trials per cell * 5 cells = 250
  margin measurements.
- max_competitors = 64.
- GPU-vectorized top-k coordinate selection per candidate competitor.

ETA: 30 min on GPU (each N=1024 measurement ~16x cheaper than N=4096).

## Citations / context

- v1 companion: `wave14_tropical_kerdock_N4096_emp_margin_v1` (PASSed
  EMP_MARGIN_WELL_DEFINED at N=4096 smoke).
- Tropical Decision Boundaries 2024 (closed-form margin formula referenced
  by Cap-13 candidate).

## Routing

- Queue: `overnight_queue` (GPU).
- Timeout: 1800 s.
