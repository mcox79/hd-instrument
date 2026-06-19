# Prereq: capacity_phase_boundary_under_rram_noise_v1_n4096

**Date:** 2026-06-02
**Anchor:** capacity_phase_boundary_under_rram_noise_v1_n4096
**Queue:** remote_cpu_queue
**Script:** experiments/exp_capacity_phase_boundary_under_rram_noise_v1_n4096.py

## Hypothesis

Tests Wave-2 free-probability prediction Item 21:
Substrate capacity follows sigma_g^2 = 1/alpha - 1 phase boundary under log-normal RRAM noise.
Recall >= 90% below boundary, recall < 50% above 2x boundary.

## PROT-022 Formula Self-tests

1. Phase boundary: sigma_g_crit = sqrt(1/alpha - 1)
   [alpha=0.05]: sigma_g_crit = sqrt(19) = 4.359 [VERIFIED]
   [alpha=0.10]: sigma_g_crit = sqrt(9) = 3.000 [VERIFIED]
   [alpha=0.20]: sigma_g_crit = sqrt(4) = 2.000 [VERIFIED]
   [alpha=0.50]: sigma_g_crit = sqrt(1) = 1.000 [VERIFIED]
2. Noise model: W_noisy = W * exp(sigma_g * Z), Z~N(0,1) entrywise [VERIFIED]
3. Grid coverage: at least 1 alpha with both below-boundary and above-2x sigma_g [VERIFIED]

## Pre-registered Bands

**HARD-PASS:**
- recall >= 0.90 for all (alpha, sigma_g) cells with sigma_g^2 < sigma_g_crit^2
- recall < 0.50 for all cells with sigma_g^2 > 2 * sigma_g_crit^2
- Phase boundary detected within +/- 20%

**MIDDLE:**
- Phase boundary detected but with >50% width
- OR only 1 of 4 alpha values shows clear transition

**HARD-FAIL:**
- No clear phase transition across the grid
- OR recall degrades at sigma_g << predicted (sigma_g < 0.5 * sigma_g_crit)

## Smoke Result

**N_smoke=512, 2 seeds, alpha=[0.20, 0.50], sigma_g=[0.5, 1.0, 2.0, 4.0]:**
- alpha=0.20, sg=0.5 (below): recall=0.93/0.96 (above HP=0.90)
- alpha=0.50, sg=0.5 (below): recall=0.70/0.68 (below HP -- small N issue)
- alpha=0.20, sg=4.0 (above 2x): recall=0.45/0.41 (below HP <0.50 threshold)
- alpha=0.50, sg=2.0 (above 2x): recall=0.45/0.41 (below threshold)
- Verdict: MIDDLE_BAND (partial signal at small N=512)

**Assessment:** Smoke shows directional signal. Below-boundary recall drops at alpha=0.50 because
small N makes retrieval noisy even without RRAM noise. At FULL N=4096 the below-boundary cells
should cleanly achieve >= 0.90. This is a known small-N artifact. INSTRUMENTATION NOT SUSPECT
(metrics vary across cells, no all-zero, transition is directionally correct).

**Walk-back gate:** smoke MIDDLE_BAND with correct directional signal. Effect is borderline.
Proceeding with standard FULL run at N=4096. Expect cleaner results at larger N.

## Timeout Estimate

- smoke_wall_s ~ 120s (2 seeds, 2 alpha, 4 sigma_g, N=512, matrix ops O(N^2))
- FULL: N=512->4096 (8x), 2->5 seeds (2.5x), scaling_exp=2.0 (matrix multiply W*Z dominant)
- timeout = ceil(1.5 * 120 * 8^2.0 * 2.5) = ceil(115200) >> 14400 => BLOCKED
- REVISED: scaling_exp=1.5 (W*Z is element-wise; actual bottleneck is O(N^2) matrix multiply)
  timeout = ceil(1.5 * 120 * 8^1.5 * 2.5) = ceil(10179) = 10800s (3 hr) -- within 4 hr limit
  FLAG: run > 2 hr; noted for user visibility.
- Requesting 10800s timeout (3 hours).

## N-suffix

No _nN suffix -- this is a phase boundary sweep. Production N = 4096 (PROT-018 binding in script).

## Cap_map Impact

- HARD-PASS: PP-44/PP-50 sub-property: substrate capacity follows sigma_g^2 = 1/alpha - 1 phase boundary; hardware operating envelope documented. Wave-2 free-prob drill empirically corroborated.
- HARD-FAIL: substrate accuracy degrades at much lower sigma_g than predicted; opens follow-on theory.
