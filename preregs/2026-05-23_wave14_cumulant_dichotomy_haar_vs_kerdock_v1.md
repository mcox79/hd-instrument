# Pre-reg: wave14_cumulant_dichotomy_haar_vs_kerdock_v1

**Date filed:** 2026-05-23
**Author:** exp_dev
**Script:** `experiments/exp_wave14_cumulant_dichotomy_haar_vs_kerdock_v1.py`
**Queue:** `remote_cpu_queue` (Tier B — non-GPU, 30-60 min wallclock)

## Motivation

Cross-domain Research probe `notes/research_cross_domain_probe_2026-05-23.md`
identified the ETH-free-probability framing (Pappalardi-Foini-Kurchan;
Jindal-Hosur JHEP09(2024)066) as the top angle for reframing BBMD as a
"partially-thermalized algebraic-codebook regime." Domain 6 (NN-Jacobian
asymptotic freeness, Hayase 2019, Collins-Hayase 2022) gives a clean
mathematical dichotomy:

  - Haar-random codebook -> classical higher cumulants of the angle
    distribution collapse to zero (off-diagonal Gram entries asymptotically
    Gaussian on the sphere).
  - Algebraic codebook (Kerdock 4-coset MM) -> discrete +-1/sqrt(N) inner
    products produce non-Gaussian higher cumulants that DON'T collapse.

This experiment is the cheapest disambiguator for the ETH framing.

## Design

For each family (Haar / Kerdock) at each seed (10 seeds, N=4096, single N):

1. Build M = 4N = 16384 unit-norm rows in R^N.
   - Haar: M iid N(0, I_N) rows, L2-normalised (spherical uniform).
   - Kerdock: 4-coset Maiorana-McFarland codebook from
     `exp_wave14y_erase_kerdock_v3.make_kerdock_4coset_codebook`,
     bipolar +-1/sqrt(N).
2. Compute off-diagonal entries of (rows @ rows.T), scaled by sqrt(N) so
   variance is O(1) (standard free-probability normalisation).
3. Compute raw moments m_1..m_6 of the off-diagonal sample.
4. Invert to CLASSICAL cumulants kappa_1..kappa_6 (primary metric) via the
   standard cumulant-from-moments recursion.
5. Also compute FREE cumulants via Mobius inversion on the non-crossing
   partition lattice (secondary metric; same routine as
   `exp_wave14_kappa_n_profile_v1`).

Aggregate across seeds: kappa_mean, kappa_std, per-seed kappa_4/kappa_2^2.

## Hypothesis

  - Haar: classical |kappa_n| < 0.1 for ALL n in {3,4,5,6}, all 10 seeds.
    The off-diagonal Gram entries of a Haar codebook look Gaussian
    (asymptotic freeness in the Hayase-Collins sense maps numerically to
    classical-higher-cumulant collapse for the marginal angle distribution).
  - Kerdock: classical |kappa_n| > 0.2 for n=4 AND n=6 (mean).
    Encodes the discrete +-1/sqrt(N) inner-product spectrum.
  - kappa_4/kappa_2^2 substantially LARGER for Kerdock (absolute value).

## HARD PASS (ETH framing survives -> CUMULANT_DICHOTOMY_HOLDS)

  - Haar: |kappa_n| < 0.1 for ALL n in {3,4,5,6} across 10/10 seeds.
  - Kerdock: |kappa_n| > 0.2 for at least n=4 AND n=6 (mean).
  - |kappa_4/kappa_2^2| substantially larger for Kerdock than for Haar
    (Kerdock excess > 5x Haar excess OR Kerdock |excess| > 0.5).

## HARD FAIL (ETH framing as a regime axis is killed)

  - Haar shows |kappa_n| > 0.1 for any n >= 3 across the seed sample
    -> CUMULANT_DICHOTOMY_HAAR_FAILS. Asymptotic freeness fails at this
    N; need much larger N to see it; weakens the "Haar = fully thermalized"
    claim.
  - OR Kerdock |kappa_4/kappa_2^2| < 0.05
    -> CUMULANT_DICHOTOMY_KERDOCK_FAILS. The kappa_n divergence is not
    actually meaningful; prior v164a finding called into question.

## Verdict labels

  - `CUMULANT_DICHOTOMY_HOLDS` -- both arms pass + discriminator clean.
  - `CUMULANT_DICHOTOMY_HAAR_FAILS` -- Haar leaks |kappa_n| > 0.1 for n>=3.
  - `CUMULANT_DICHOTOMY_KERDOCK_FAILS` -- Kerdock |kappa_4/kappa_2^2| < 0.05
    or Kerdock |kappa_4| or |kappa_6| <= 0.2.
  - `CUMULANT_DICHOTOMY_INCONCLUSIVE` -- both arms fail or data missing.

## Smoke result (local, N=1024, 2 seeds, both families)

VERDICT: `CUMULANT_DICHOTOMY_HOLDS`. Haar k_3..k_6 = {0.000, -0.006, +0.003, +0.000}
all < 0.1. Kerdock k_4 = -0.935, k_6 = +4.94. Excess-kurtosis magnitude
ratio Kerdock/Haar = 255x. The dichotomy is visible even at N=1024.

## Rehab path if HARD FAIL fires

Per [[feedback-rehabilitation-after-rejection]]:

  - HAAR_FAILS: re-run at N=16384 / 32768 to test finite-size effects;
    or try alternative spherical-uniform constructions (QR with Mezzadri
    sign correction; iid Bernoulli +-1/sqrt(N) -- a different "random
    structured" codebook).
  - KERDOCK_FAILS: verify the bipolar/sqrt(N) scaling is right; cross-check
    against v167 KAPPA_PROFILE_GROWS result on the SPECTRUM (eigenvalue
    kappa_n profile, not entrywise); inspect whether the moment computation
    is numerically conditioned at N=4096 (cancellation across +-1/sqrt(N)).

## Mandatory

  - Script includes metrics-write block with env-var-driven outdir and
    atomic write_metrics(...). [confirmed]
  - Pre-run smoke at N=1024, 2 seeds, both families locally. [PASSED]
  - status_log entry with importance=HIGH and plain_language framing the
    ETH-thermalization angle.
