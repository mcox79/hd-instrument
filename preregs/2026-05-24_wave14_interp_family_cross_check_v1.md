# Pre-registration: wave14_interp_family_cross_check_v1

**Date**: 2026-05-24
**Queue**: remote_cpu_queue (pure-CPU; ~30-60 min wallclock at N=1024 5-seed)
**Axis probed**: BBMD Cap-12 rehab — R1 (cross-interpolation AMP-error predictor)
**Trigger**: Research deep assessment `notes/research_bbmd_cap12_rehab_assessment_2026-05-24.md`; 2nd-ranked anchor (P=0.30 after harsher deflation)
**Script**: experiments/exp_wave14_interp_family_cross_check_v1.py
**Expected elapsed**: ~30-60 min CPU full sweep

---

## Scientific question

Anchor 1 of the BBMD-regime promotion (v170 BBMD_VAMP_CORRESPONDENCE_PASS at
Spearman rho = 0.900 across iid-Gauss -> Kerdock interpolation) gave n=1
family evidence that AMP rel-err tracks the free-cumulant divergence sum.
Does the monotone-curve property GENERALIZE to a different interpolation
family, or is it specific to a Kerdock-internal property?

We test iid-Gauss -> SRHT interpolation as the FIRST non-Kerdock family
(Research's recommendation).  SRHT is provably AMP-universal (Dudeja-Lu-Kini
2022) so the SRHT-end AMP rel-err should stay low; if the predictor still
tracks monotone, that's CROSS-FAMILY generalization evidence.

---

## Design

- **N**: 1024 (matches Anchor 1's N=4096 normalization but smaller for budget)
- **M/N**: 1.0
- **alpha_interp**: [0.0, 0.25, 0.5, 0.75, 1.0] (5 cells, same grid as v170)
- **sigma_noise**: 0.1; **signal_var**: 1.0 (same as v170)
- **n_seeds**: 5; **n_iter**: 300 (matched to v170)
- **n_max_moment**: 6 (matched)
- **W_alpha**: `((1-alpha) * G + alpha * W_srht_unnormalized) / sqrt(N)`
  - G iid N(0,1) entries (un-normalized; same +/-1 scale as SRHT entries)
  - W_srht_unnormalized = row-subsampled DH (Dudeja-Lu-Kini SRHT) without 1/sqrt(N)
  - Caches W_srht per (N, M, seed) so only alpha varies along the interpolation
- **AMP**: scalar Bayati-Montanari Onsager
- **VAMP**: RSF 2017 Alg 1 with MMSE Gaussian denoiser
- **BBMD-distance**: sum_{n=2..6} | kappa_n - c | where c = M/N

---

## Formula self-tests (per [[feedback-strategy-spec-formula-selftests]])

| # | Formula | Input | Expected | Verified |
|---|---|---|---|---|
| 1 | `bbmd_distance(kappas, c, 2, 6)` | kappas=[c]*6, c=0.5 | 0 | YES |
| 2 | `bbmd_distance` on deviating cumulants | kappas=[c, c+0.1, ..., c+0.5], c=0.5 | 1.5 | YES |
| 3 | Spearman rho on monotone-increasing pair | ([0.01,0.02,0.10,0.20,0.30], [0,0.5,1.0,1.5,2.0]) | 1.0 | YES |
| 4 | full PASS verdict | synthetic monotone cells (rho=1.0, max_vamp=0.06) | PASS | YES |
| 5 | KILLED via low rho | non-monotone amp_rel_err | KILLED | YES |
| 6 | KILLED via VAMP blowup | vamp=0.30 at alpha=1 | KILLED | YES |
| 7 | INCONCLUSIVE branch | monotone rho but vamp in (0.10, 0.20) | INCONCLUSIVE | YES |
| 8 | too-few-cells -> INCONCLUSIVE | 1 cell only | INCONCLUSIVE | YES |

All 8 cells PASS (self-test exits cleanly).

---

## Falsifiable predictions

### INTERP_FAMILY_SRHT_PASS (HARD PASS)

- Spearman `rho(amp_rel_err, bbmd_distance)` >= 0.70 across 5 alpha cells
- `max(vamp_rel_err)` < 0.10
- Deflated P = 0.30 (Research calibration; harsher than Strategy's 0.40
  because v170 is n=1 family evidence).

Predictor generalizes; the free-cumulant divergence sum is a cross-family
META-DIAGNOSTIC capability.  Validates R1 as 12th portfolio capability
candidate.

### INTERP_FAMILY_SRHT_KILLED (HARD FAIL)

- Spearman rho < 0.50
- OR `max(vamp_rel_err)` > 0.20
- P = 0.45.

Predictor is Kerdock-specific; R1 closes.  If Anchor 1 (R3) passed
independently, portfolio sits at 12 via R3 alone; if R3 also failed,
consolidate at 11.

### INTERP_FAMILY_SRHT_INCONCLUSIVE

- rho in [0.50, 0.70) OR (rho >= 0.70 AND max_vamp in [0.10, 0.20])
- P = 0.25.

---

## Substrate-product interpretation

- **PASS**: substrate-product story = "we ship a kappa_n-moment diagnostic that
  predicts AMP-failure regime across customer matrix families."  Customer
  measures their codebook; substrate outputs an expected AMP convergence
  regime.  Capability class: META-DIAGNOSTIC.  Generalizes beyond Kerdock,
  the substrate's chosen anchor codebook.
- **KILLED**: predictor is Kerdock-internal; substrate has the Kerdock-
  specific characterization (v164a fingerprint) but no cross-family extension.
  R1 closes; Cap 1/3/8 + v164a annotations capture the existing scope.

---

## PROT compliance

- Schema A inline key=value entry filed.
- Background experiments per [[feedback-no-blocking-runs]].
- Pause flag CLEARED at dispatch time.
- `HDLAB_EXP_NAME` env var supported.
- Atomic write_metrics (tmp + replace).
- Formula self-tests per [[feedback-strategy-spec-formula-selftests]] all PASS.
- Honest framing per [[feedback-no-smoke]]: META-tool capability, not
  substrate-physics novelty.
