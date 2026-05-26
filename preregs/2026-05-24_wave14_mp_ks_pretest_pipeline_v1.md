# Pre-registration: wave14_mp_ks_pretest_pipeline_v1

**Date**: 2026-05-24
**Queue**: remote_cpu_queue (pure-CPU; ~15-30 min wallclock at N=1024 5-seed)
**Axis probed**: BBMD Cap-12 rehab — R3 (MP-KS pre-test as infrastructure capability)
**Trigger**: Research deep assessment `notes/research_bbmd_cap12_rehab_assessment_2026-05-24.md`; top-ranked anchor (P=0.55 after deflation)
**Script**: experiments/exp_wave14_mp_ks_pretest_pipeline_v1.py
**Expected elapsed**: ~15-30 min CPU full sweep

---

## Scientific question

The v171 negative result (KAPPA_CROSS_CODEBOOK_KILLED) revealed MP-KS at the
empirical eigenvalue distribution already discriminates AMP-fragile structured
codebooks (SRHT 0.59, Hadamard 0.59, RM(1,m) 0.34) from iid Gaussian (~0)
WITHOUT needing the kappa_n divergence-sum scalar.  The natural rehab move is
to operationalize this as an INFRASTRUCTURE-class capability:

  > Given a customer codebook W, run a 15ms MP-KS pre-test.  If KS > tau, the
  > codebook is OUTSIDE the standard Marchenko-Pastur regime; route to
  > substrate's VAMP-on-chain primitive.  Else allow scalar-Onsager AMP.

Two questions:
1. Does tau=0.20 route at least 4/5 known codebooks correctly?
2. Is the pre-test cheap enough (>=10x speedup) vs running AMP to convergence
   or failure?

---

## Design

- **N**: 1024 (smallest size supporting all 5 codebooks including Kerdock t=5)
- **M/N**: 1.0 (alpha_ratio = 1)
- **sigma_noise**: 0.1 (SNR ~ 100, diagnostic regime)
- **signal_var**: 1.0 (matched Gaussian prior, MMSE denoiser)
- **n_iter**: 300 (AMP and VAMP loops, both)
- **n_seeds**: 5 per codebook
- **codebooks**: iid_gauss, srht, hadamard, rm_1_m, kerdock
- **a-priori labels**: iid_gauss + srht = AMP_OK; hadamard + rm + kerdock = VAMP_REQUIRED
- **tau_declared**: 0.20
- **AMP**: scalar Bayati-Montanari Onsager with matched Gaussian denoiser
- **VAMP**: standard Rangan-Schniter-Fletcher Alg 1 with MMSE Gaussian denoiser
- **empirical truth**: codebook is AMP_OK if AMP rel-err vs AMP-SE < 0.10, else VAMP_REQUIRED
- **t_ks_per_seed**: time of MP-KS computation only (SVD shared with VAMP)
- **t_amp_per_seed**: full empirical AMP loop end-to-end

---

## Formula self-tests (per [[feedback-strategy-spec-formula-selftests]])

Each formula in the prereg has an (input -> expected output) self-test cell
that runs BEFORE compute spend.

| # | Formula | Input | Expected output | Verified |
|---|---|---|---|---|
| 1 | `route_from_ks(ks, tau)` | (0.05, 0.20) | "AMP_OK" | YES (assert in self_test) |
| 1 | `route_from_ks(ks, tau)` | (0.20, 0.20) | "AMP_OK" (boundary inclusive) | YES |
| 1 | `route_from_ks(ks, tau)` | (0.21, 0.20) | "VAMP_REQUIRED" | YES |
| 1 | `route_from_ks(ks, tau)` | (0.59, 0.20) | "VAMP_REQUIRED" | YES |
| 2 | `empirical_truth_from_errs(amp_rel, vamp_rel)` | (0.05, 0.02) | "AMP_OK" | YES |
| 2 | `empirical_truth_from_errs(amp_rel, vamp_rel)` | (0.50, 0.02) | "VAMP_REQUIRED" | YES |
| 2 | `empirical_truth_from_errs(amp_rel, vamp_rel)` | (0.10, 0.02) | "VAMP_REQUIRED" (exclusive) | YES |
| 3 | speedup = t_amp / t_ks | (1.0, 0.05) | 20.0 | YES |
| 4 | routing-accuracy counter over 5 fake codebooks | 4 correct routings | correct == 4 | YES |
| 5 | full PASS-verdict pipeline | synthetic 4/5-correct + 300x-speedup cells | PASS | YES |
| 6 | KILLED via <3/5 correct | synthetic 1/5-correct cells | KILLED | YES |
| 7 | KILLED via speedup<2x | synthetic 4/5-correct + 1.25x-speedup | KILLED | YES |
| 8 | INCONCLUSIVE branch (3/5 correct) | synthetic 3/5-correct cells | INCONCLUSIVE | YES |
| 9 | missing codebooks -> INCONCLUSIVE | 3 of 5 codebooks | INCONCLUSIVE | YES |

All 9 cells PASS (self-test exits cleanly).

---

## Falsifiable predictions

### MP_KS_PRETEST_PIPELINE_PASS (HARD PASS)

- `routing_correct_at_tau_declared` >= 4 (out of 5)
- `speedup_amp_over_ks` >= 10.0
- Deflated P = 0.55 (Research calibration).

Substrate ships a customer-visible "pre-flight codebook diagnostic": customer
submits matrix, substrate runs MP-KS pre-test (~ms), routes to AMP or
VAMP-on-chain.  Capability class = INFRASTRUCTURE.  Validates R3 as 12th
portfolio capability candidate.

### MP_KS_PRETEST_PIPELINE_KILLED (HARD FAIL)

- `routing_correct_at_tau_declared` < 3 (out of 5)
- OR `speedup_amp_over_ks` < 2.0
- P = 0.20.

Pre-test cannot route reliably or saves no compute -> infrastructure-class
12th capability candidate killed.  Fall back to R1 anchor only.

### MP_KS_PRETEST_PIPELINE_INCONCLUSIVE

- 3/5 correct OR (4/5 correct with speedup in [2, 10)).
- P = 0.25.

---

## Substrate-product interpretation

- **PASS**: substrate's product story = "we ship a 15ms pre-flight that decides
  AMP vs VAMP-on-chain per customer matrix; the AMP path is fastest when it
  works, and the pre-test catches when it won't.  No hand-tuning."  Capability
  class: INFRASTRUCTURE (orthogonal to Cap 8 VAMP-on-chain it routes TO).
- **KILLED**: substrate has the VAMP-on-chain primitive (Cap 8) but no clean
  way to know when to use it; customer must run AMP-then-observe-failure each
  time.  R3 closes; lean on R1 backup.

---

## PROT compliance

- Schema A inline key=value entry filed.
- Background experiments per [[feedback-no-blocking-runs]].
- Pause flag CLEARED at dispatch time.
- `HDLAB_EXP_NAME` env var supported by `get_output_dir`.
- Atomic write_metrics (tmp + replace).
- Formula self-tests per [[feedback-strategy-spec-formula-selftests]] all PASS.
