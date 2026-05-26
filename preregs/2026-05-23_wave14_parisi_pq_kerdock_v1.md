# Pre-registration: wave14_parisi_pq_kerdock_v1

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_parisi_pq_kerdock_v1.py
**Field-advisor anchor**: Parisi P(q) RSB probe (tier-1 spin-glass; complements
  Sinova C_ij eigenvalue probe which used random BSC, NOT Kerdock)

## Hypothesis

The Parisi overlap distribution P(q12) between two INDEPENDENT thermal
replicas under Glauber dynamics on the Kerdock-Hebbian W shows non-trivial
shape at low T (beta>=4):
  - Continuous support (RSB phase): substrate Kerdock-Hopfield has glassy
    free-energy landscape
  - Two-delta support (RS / Edwards-Anderson): standard retrieval phase
  - Single delta at q=0 (paramagnet): no order
  - Mixed: INCONCLUSIVE

This is structurally distinct from the wave14_glauber_kerdock_v* probes
(which measure overlap with STORED codewords, q = (1/N)<s, xi_mu>, a
"retrieval probe"). P(q12) is the canonical "glass order parameter" --
between two replicas thermally sampling the Boltzmann measure, NOT from
perturbed-target initialization.

Brutal-honesty P estimates:
- P(RSB / continuous support at any low-T cell): **0.25** -- Hebbian
  matrices generally have RS-like Mattis states; RSB needs degenerate
  metastable structure which Kerdock's algebraic regularity may suppress
- P(RS / two-delta): **0.40** -- standard Hopfield phenomenology
- P(PARAMAGNET): **0.15** -- substrate ordering threshold higher than tested
- P(INCONCLUSIVE): **0.20** -- finite-N + finite-chain shape ambiguity

Per [[feedback-lit-scan-calibration-penalty]]: substrate Kerdock-Hopfield
is in uncharted regime, so RSB P deflated from a naive 0.40 (classical RSB
prevalence in disorder systems) to 0.25.

## Predictions (falsifiable, hard-fail thresholds)

For each low-T cell (beta>=4), classify shape from histogram of q12 samples:
- support_width = fraction of 41 bins with density > 5% of peak
- support_continuous_fraction = longest contiguous supported run / total supported
- n_peaks = local maxima with density > 10% of peak, min spacing 3 bins
- delta_at_zero_frac = mass in central 5 bins (q in approx [-0.10, +0.10])

Shape decision:
- continuous (RSB): sw>0.5 AND scf>0.5 AND (n_peaks>=3 OR (sw>0.7 AND n_peaks>=2))
- two-deltas (RS): n_peaks==2 AND dz<0.3 AND sw<0.4
- paramagnet: dz>0.6 AND n_peaks<=1 AND sw<0.3
- undetermined: else

Verdict aggregation:
- PARISI_RSB_KERDOCK: any low-T cell classifies continuous
- PARISI_PARAMAGNET_KERDOCK: all low-T cells paramagnet
- PARISI_RS_KERDOCK: at least half low-T cells two-deltas, none continuous
- PARISI_INCONCLUSIVE: else (including undetermined-majority)

Hard-fail / kill:
- Self-test 8/8 (synthetic + verdict branches) -- PASSED
- High-T (beta=1.0) showing dz<0.3: bug (should be paramagnetic) -- halt
- FULL runtime > 60 min: halt before queue timeout

## Runtime / queue routing

- 3 alphas x 6 betas x 5 seeds x (300 burn + 500 collect) = 800 sweeps per
  PAIR of chains (2 chains so 1600 sweeps per pair). 90 pairs.
- At N=1024, ~20ms per pair-sweep (two glauber_sweep calls per step) -> 90
  * 1600 * 20ms = 48 min. Bit long for "stagger" -- but on remote CPU still
  fits comfortably; timeout = 5400s (1.9x headroom).
- Route: **remote_cpu_queue** (Rule 2)

## Smoke result

Self-test 8/8 PASS (3 synthetic shape classifications + 5 verdict branches).
Smoke (alpha=0.10, beta in {2, 6}, 2 seeds, 50 burn, 100 collect):
- alpha=0.10 beta=2.0: q12_mean=-0.21, sw=0.11, n_peaks=1, dz=0.07 -- narrow
  shifted distribution (high-T, weak ordering)
- alpha=0.10 beta=6.0: q12_mean=-0.17, sw=0.09, n_peaks=1, dz=0.38 -- narrow
  shifted distribution, more mass at 0 (consistent with single replica
  trapping but the *pair* not in same basin)
- Verdict: PARISI_INCONCLUSIVE (only 1 low-T cell, undetermined shape)

Smoke does NOT predict FULL: smoke has only 100 collect samples per chain
(not enough to resolve continuous support); FULL has 500 + 5 seeds (2500
samples per cell aggregated). The smoke is sanity-check only.

Interesting smoke detail: q12_mean is NEGATIVE in 3/4 chains (-0.19, -0.23,
-0.24, -0.10). For independent random initializations, q12 should be ~0
in expectation. Sustained negative q12 is unusual; could indicate
anti-aligned attractors (a +xi_mu vs -xi_mu basin pair). Hopfield is
spin-flip symmetric (W is symmetric in spin-flip) so +xi and -xi are
equally stable -- so independent chains land in opposite basins.
Suggestion for FULL post-hoc analysis: also report P(|q12|) to fold out
the sign-flip symmetry.

## Linkage

This probe complements:
- wave14_sinova_cij_eigenvalue_v1 (extensive-eigenvalue RSB on RANDOM BSC)
  -- if Parisi-on-Kerdock finds RSB but Sinova-on-random-BSC didn't, the
  Kerdock algebraic structure is the source of glassiness
- wave14_glauber_kerdock_v2 (retrieval probe) -- if v2 BIMODAL but Parisi
  RS, the two probes test different facets and both fire
- wave14_free_cumulants_kerdock_v1 + wave14_S_transform_kerdock_v1 (static
  spectral) -- if static spectral non-MP + dynamical RSB, the substrate
  is doubly outside AMP class

Pre-registered intent: if FULL = PARISI_RSB, follow up with Parisi tree
(ultrametricity check on q-triplets q12, q13, q23).
