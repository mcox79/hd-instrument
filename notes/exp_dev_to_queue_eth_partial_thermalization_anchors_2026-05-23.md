# exp_dev -> queue: ETH partial-thermalization falsification anchors

**Date filed**: 2026-05-23
**Owner**: exp_dev (sonnet sub-agent)
**Triggering event**: Strategy ship request — 2 falsification anchors from
                      `notes/research_eth_thermalization_drill_2026-05-23.md`
                      (PFK partial-thermalization framing, P=0.40)

| queue            | name                                                  | script                                                                   | prereg                                                                       | timeout(s) |
|------------------|-------------------------------------------------------|--------------------------------------------------------------------------|------------------------------------------------------------------------------|------------|
| remote_cpu_queue | wave14_cactus_factorization_break_kerdock_n6_v1       | experiments/exp_wave14_cactus_factorization_break_kerdock_n6_v1.py       | preregs/2026-05-23_wave14_cactus_factorization_break_kerdock_n6_v1.md        | 3600       |
| remote_cpu_queue | wave14_kerdock_sff_vs_gue_v1                          | experiments/exp_wave14_kerdock_sff_vs_gue_v1.py                          | preregs/2026-05-23_wave14_kerdock_sff_vs_gue_v1.md                           | 2400       |

## One-line hypotheses

- **cactus_factorization_break_kerdock_n6_v1** — Spectral moment m_6 of
  sub-sampled Kerdock W (alpha=1) deviates from the factorized cactus
  prediction by >= 20% (R_6 > 1.20) iff the substrate sits in PFK's
  partial-thermalization regime; R_6 in [0.95, 1.05] kills the framing.

- **kerdock_sff_vs_gue_v1** — Spectral Form Factor of sub-sampled
  Kerdock W (alpha=1) deviates from a matched-pair GUE SFF by > 15% in
  dip or plateau iff the substrate carries spectral structure GUE does
  not capture; SFF matches GUE within 5% in both regions kills the
  framing.

## Smoke results (N=1024, 1 seed, local)

- **cactus n=6**: SMOKE OK (PFK_R6_INCONCLUSIVE at single seed). At N=1024,
  alpha=1: R_6 = 0.9977, kappa_6 = -0.111, cactus_factorized = 47.79
  (sanity: moment-cumulant identity verified to machine precision).
  Smoke trends toward HARD FAIL band; full N=4096 with 10 seeds will
  resolve cleanly either way.

- **SFF**: SMOKE OK (PFK_SFF_INCONCLUSIVE at single seed). At N=1024,
  alpha=1: dip_rel_dev = 358%, plateau_rel_dev = 31%. Both deviations
  comfortably above the > 15% HARD-PASS threshold; full N=4096 with
  5 seeds expected to yield PFK_SFF_NON_GUE with high confidence.

## Routing rationale

- Both are pure-numpy (no GPU); the SFF run uses np.linalg.eigvalsh on a
  4096x4096 symmetric matrix per seed + complex SFF on 256 tau x 4096
  eigenvalues -- a few seconds per seed. The cactus run is eigvalsh +
  Catalan-132 partition sum -- < 30s per seed total.
- ETA 20-30 min (SFF) / 30-45 min (cactus) including 4N codebook build.
- Route to remote_cpu_queue per Tier B (longer non-GPU work, design-space
  sweep across seeds; GPU has its own queue and 3 pending).
- Smoke pass at N=1024 / 1 seed both verified locally before shipping.

## Note on operator choice (important fix during smoke)

Initial drill text mapped "operator A" to the FULL Kerdock 4-coset Hebbian
W = (1/N) C^T C. This is a tight frame: W = 4 * I exactly, with a
DEGENERATE spectrum and matrix-element-on-codewords cyclic products that
are sign-cancelled near zero (verified during smoke). Switched both
anchors to use SUB-SAMPLED W_alpha at alpha = M/N = 1 (the v167 central
case where kappa_n GROWS with n through n=8). This matches the operative
regime where the substrate's substrate-novel spectral structure is
already known to live, and gives a well-posed test of the PFK
factorization criterion. Documented in updated docstrings + preregs.
