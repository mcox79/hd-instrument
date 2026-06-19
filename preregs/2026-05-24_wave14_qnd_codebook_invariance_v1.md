# Prereg — wave14_qnd_codebook_invariance_v1

## Hypothesis

Cap 8 (QND-style audit-trail) requires the codebook A used by VAMP recovery
to be INVARIANT across all iterations: the effective A_eff_t at iteration t
must equal A_0 within numerical noise. If A_eff_t drifts (Frobenius drift
grows with t), the audit-trail guarantee fails because downstream verifiers
cannot pin a single A.

This probe directly measures max_t |A_eff_t - A_0|_F for both iid_gauss
(control) and 4-coset Kerdock (substrate). Pure VAMP should give zero
drift trivially; the probe is a structural sanity check that no implicit
state leak occurs in the substrate-specific VAMP path.

## Pre-registered bands

- **HARD PASS** (`QND_CB_INVARIANT`):
  - max_t |A_eff_t - A_0|_F < 1e-4 for BOTH iid_gauss AND kerdock.
  - Substrate inherits Cap 8 invariance for free under pure VAMP.

- **HARD FAIL** (`QND_CB_DRIFTS`):
  - Kerdock max drift > 1e-2 (clear structural drift).
  - Substrate has implicit state leak; Cap 8 broken under current VAMP path.

- **MIDDLE BAND** (`QND_INCONCLUSIVE`):
  - Drift in [1e-4, 1e-2]; needs follow-up.

## Design

- N = 1024, M = 1024 (square regime; Cap 8 reference operating point).
- VAMP: 50 iterations, sigma_noise_sq = 0.01.
- 2 codebooks: iid_gauss (control), kerdock (substrate).
- 3 seeds per codebook.
- Per cell: record A_eff at each iteration, compute |A_eff_t - A_0|_F.

ETA: ~30 min CPU (VAMP iterations + Frobenius norm computations are cheap).

## Citations

- Cap 8 audit-trail row in cap_map (substrate-product capability class 3).
- Rangan-Schniter-Fletcher 2019 (VAMP foundations).

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 1800 s.
- Pure numpy (no CUDA).
