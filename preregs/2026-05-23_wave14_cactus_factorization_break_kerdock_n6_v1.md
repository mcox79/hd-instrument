# Prereg: wave14_cactus_factorization_break_kerdock_n6_v1

**Date filed**: 2026-05-23
**Owner**: exp_dev (sonnet sub-agent)
**Parent drill**: `notes/research_eth_thermalization_drill_2026-05-23.md` (Anchor #2 / P4)

## Question

Does the partial-thermalization (PFK) interpretation of the substrate
survive the n=6 cactus-factorization hard-pass test?

PFK 2022 / Pappalardi 2023 establish that "full ETH" holds when the
n-point cyclic operator product factorizes onto non-crossing partitions
(the "cactus expansion") with crossing contributions vanishing
exponentially in Hilbert dimension. In contrast, ergodicity-broken or
partial-thermalization systems show non-trivial crossing-partition
contributions; the moment-to-cumulant inversion breaks the non-crossing
restriction.

We test this on substrate's Kerdock-Hebbian operator on codeword basis.

## Mapping (per drill Section 2)

- Operator A   <->  Sub-sampled Kerdock Hebbian W_alpha = (1/N) C_sub^T C_sub,
                     with C_sub = M randomly chosen rows from the (4N, N)
                     bipolar Kerdock 4-coset codebook at alpha = M/N = 1.
                     This matches v167's central case where kappa_n GROWS
                     with n through n=8.
- "Cyclic n-product moment"  <->  spectral moment m_n = E_lambda[lambda^n]
                                  of W_alpha.

Note on operator choice: the FULL Kerdock 4-coset W = (1/N) C^T C with all
4N codewords is a tight frame, equal to 4*I exactly. Its spectral moments
are trivial and the operator-on-codewords cyclic product is sign-cancelled
near zero. Sub-sampling at alpha = 1 puts W back into the v167 regime
where the kappa hierarchy is non-trivial.

## Quantity

  m_n      := spectral moment E[lambda^n] of W_alpha (n=1..6).
  kappa_n  := free cumulants inverted from m_1..m_n via the moment-to-free-
              cumulant recursion on the non-crossing partition lattice
              (Nica-Speicher 2006; identical machinery to v167).
  cactus_factorized_6 := sum over pi in NC(6) with |pi| >= 2 of
                          product over B in pi of kappa_{|B|}
                       (the cactus prediction using ONLY lower kappas;
                        excludes the full-block partition which is the
                        kappa_6 atom).
  R_6      := m_6_empirical / cactus_factorized_6
            == 1 + kappa_6 / cactus_factorized_6
              (by the moment-cumulant identity m_n = full-cactus sum;
               R_6 - 1 isolates the kappa_6 contribution as a fraction
               of the lower-kappa cactus prediction).

## Config (full run)

- N = 4096 (t = 6 primitive polynomial in Kerdock 4-coset)
- alpha = M/N = 1.0 (v167 central case)
- n_seeds = 10 (each seed sub-samples a different M=N subset of 4N codewords)
- n_max_cumulant = 6 (Catalan C_6 = 132 non-crossing partitions)
- queue: remote_cpu_queue (CPU, pure numpy + eigvalsh)

## Pass / fail thresholds (HARD)

**HARD PASS (PFK_PARTIAL_ETH_CONFIRMED)**:
- R_6 > 1.20 in >= 8/10 seeds.
- Interpretation: crossing-partition contribution to the cyclic-6 product
  is > 20%; substrate is empirically a partial-thermalization regime
  in the PFK sense. PFK / BBMD framing survives this anchor.

**HARD FAIL (PFK_FULL_ETH_BULK)**:
- R_6 in [0.95, 1.05] in >= 8/10 seeds.
- Interpretation: cactus factorization dominates; substrate is
  full-ETH-class with non-Gaussian bulk shape but standard thermalization.
  PFK partial-thermalization framing KILLED at the n=6 cactus level.
  v167's kappa_n-grows-with-n finding then reflects bulk-shape
  non-Gaussianity within the full-ETH regime, not partial thermalization.

**ANOMALY (PFK_R6_ANOMALY)**:
- R_6 < 0.80 in >= 8/10 seeds.
- Interpretation: empirical 6-product is BELOW the cactus prediction;
  framing wrong in a different way (sign/normalization mismatch, or
  destructive crossing-partition interference). Needs investigation.

**INCONCLUSIVE (PFK_R6_INCONCLUSIVE)**:
- No threshold reached.

## Pre-specified bonus diagnostic

- cactus_sum excluding the full-block contribution = sum over non-crossing
  partitions of {1..6} with >= 2 blocks, of product of kappa_{|B|}.
  Reports how much of the cactus prediction is the kappa_6 atom vs
  factorized lower-cumulant products. Pre-registered for v168 cap_map
  annotation regardless of verdict.

## Honest framing

This is a single-N (N=4096) test of one PFK prediction (P4 in the
drill). It does NOT prove or disprove the full PFK mapping; it tests one
direct numerical consequence. Per [[feedback-dont-overextend-theorems]],
even a HARD PASS only confirms one prediction; the other PFK anchor
(SFF vs GUE) is needed for any "framing survives" claim, and the VAMP-SE
composition probe (Anchor #4) is needed for the VAMP-ETH correspondence.

Per [[feedback-no-papers-product-only]]: results inform substrate-product
positioning around "auditable memory substrate sits in a published
partial-thermalization regime" -- NOT publication.
