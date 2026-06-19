# Pre-registration: wave14_spectral_universality_kerdock_v1

**Date**: 2026-05-24
**Queue**: remote_cpu_queue (Tier B; local_cpu_runner is dead per heartbeat 2026-05-24T01:50)
**Axis probed**: Cap 8 envelope-extension to M/N=8 via Dudeja-Sen-Lu spectral universality (arXiv:2208.02753, IEEE TIT 2023); rehab path for Cap 12 M/N=8 anomaly after MAMP/VAMP equivalence (Liu-Takeuchi Thm 2) ruled out the RUI family
**Trigger**: Research drill `notes/research_mamp_kerdock_M_over_N_8_drill_2026-05-24.md` honest pivot — MAMP gives same SE fixed point as VAMP under RUI, so it can't resolve the M/N=8 gap; Dudeja-Sen-Lu's structured-deterministic class is the right anchor
**Script**: `experiments/exp_wave14_spectral_universality_kerdock_v1.py`
**Expected elapsed**: 45-60 min CPU full sweep at N=4096, 5 M/N cells, 5 seeds, 4 matrix families per cell

---

## Scientific question

Does Kerdock's 4-coset measurement matrix sit inside the Dudeja-Sen-Lu spectral-universality class for AMP, and if so which surrogate family does it match — iid Gaussian, random-sign Hadamard, or Haar-rotated with the Kerdock spectrum?

Dudeja-Sen-Lu prove that "nearly deterministic" sensing matrices with matched spectra produce the same asymptotic regularized-regression dynamics (including AMP/proximal-gradient) as their universal class peers, provided the singular-vector basis is "generic" (low-rank-coherence). Their explicit class members include randomly signed incoherent tight frames and randomly sub-sampled Hadamards — both structural cousins of Kerdock (a Z_4-linear cousin of Reed-Muller / Hadamard, and a unit-norm tight frame).

If Kerdock is in-class with at least one surrogate, the v168 + Cap 12 anomaly at M/N=8 is **inside the universality envelope** and Cap 8 ✅ extends; the apparent anomaly is just AMP-on-Kerdock-with-deterministic-spectrum (Bayati-Montanari iid AMP doesn't apply, but Dudeja-Sen-Lu universality with the empirical spectrum does).

If Kerdock disagrees with ALL 3 surrogates on at least one M/N, the substrate is genuinely outside Dudeja-Sen-Lu's class — a substrate-novel non-universality signature (Cap 12 promotes from "AMP-fails-on-Kerdock" to "Kerdock-breaks-universality").

---

## Design

| Knob | Value |
|---|---|
| N | 4096 (t=6 Kerdock primitive; even log2 N) |
| M/N grid | {0.5, 1.0, 2.0, 4.0, 8.0} (5 cells) |
| Matrix families | kerdock; iid_gaussian; random_sign_hadamard; haar_kerdock_spectrum |
| Seeds | 5 per (M/N, family) |
| Signal prior | iid N(0, 1) (matched Gaussian; signal_var=1.0) |
| Observation noise | N(0, sigma_noise^2) with sigma_noise=0.1 |
| AMP variant | matched Gaussian denoiser; gain = signal_var / (signal_var + tau_sq_eff); standard Onsager |
| AMP n_iter | 200 (with 1e-10 plateau early-stop) |
| Pre-test smoke | N=1024, M/N in {0.5, 1.0}, 1 seed, iid_gaussian-only surrogate |

### Surrogate construction (formula self-tests in `self_test_surrogate_spectrum`)

**iid Gaussian**: A_norm[i,j] iid N(0, 1/N). Singular values approximately MP-bulk; max ≈ 1+sqrt(M/N), min ≈ |1-sqrt(M/N)| for tall matrices. Self-test: sigma in [0, 4] for N=M=64.

**Random-sign Hadamard**: A_norm = D_row * (subsample-rows of H_N) * D_col, where H_N is Sylvester-Walsh-Hadamard normalized so rows have unit L2 norm, D_row, D_col are diagonal +-1. For M <= N, rows are orthonormal so all sigma == 1. For M > N, sub-rows repeat (with fresh row signs); sigma spectrum becomes non-trivial. Self-test: sigma == 1 within 1e-10 for square and tall-sub-N cases.

**Haar with Kerdock spectrum**: A_norm = U * diag(sigma_kerdock) * V^T with U Haar(O(M))-truncated to k=min(M,N) columns and V Haar(O(N))-truncated to k columns. Built via QR of Gaussian with diagonal-sign canonicalization. Sigma exactly equals sorted Kerdock empirical spectrum, truncated/padded to k. Self-test: returned sigma matches target within 1e-6 absolute.

These self-tests run BEFORE compute spend (in `--self-test`, `--smoke`, and full `--run` modes).

---

## Formula self-tests (per [[feedback-strategy-spec-formula-selftests]])

| # | Formula | Input | Expected | Verified |
|---|---|---|---|---|
| 1 | `_pair_rel_diff(a, b)` (Dudeja-Sen-Lu agreement metric) | (0.10, 0.11) | 0.0909... | YES — assert in self_test_verdict implicitly via case 1 |
| 2 | surrogate spectrum agreement (max pairwise) | 3 surrogates within 25% | accept | YES — case 1 in self_test_verdict |
| 3 | surrogate spectrum disagreement | 2 surrogates differ by 5x at one M/N | INCONCLUSIVE | YES — case 2 in self_test_verdict |
| 4 | Kerdock-out-of-class | Kerdock differs from all 3 surrogates at M/N=8 | NOVEL | YES — case 3 in self_test_verdict |
| 5 | Mixed / partial-match | Kerdock close to some surrogates but no single-surrogate all-cell match | INCONCLUSIVE | YES — case 4 in self_test_verdict |
| 6 | Empty cells list | [] | INCONCLUSIVE | YES — case 5 in self_test_verdict |
| 7 | iid Gaussian singular spectrum at N=M=64 | sigma in [0, 4] | OK | YES — self_test_surrogate_spectrum |
| 8 | Random-sign Hadamard at N=M=64 (square) | sigma == 1.0 within 1e-10 | OK | YES — self_test_surrogate_spectrum |
| 9 | Random-sign Hadamard at M=32, N=64 (sub-square) | sigma == 1.0 within 1e-10 | OK | YES — self_test_surrogate_spectrum |
| 10 | Haar-with-spectrum at N=M=64 | reconstructed sigma matches linspace(0.5, 2.0, 64) within 1e-6 | OK | YES — self_test_surrogate_spectrum |

All 10 self-tests gate execution; failure aborts before any AMP work.

---

## HARD PASS — `KERDOCK_UNIVERSALITY_IN_CLASS`

Kerdock AMP-MSE matches at least one of {iid_gaussian, random_sign_hadamard, haar_kerdock_spectrum} within ±25% across **all 5 M/N cells**.

Interpretation: Cap 8 ✅ envelope extends to M/N=8. Substrate's apparent M/N=8 AMP anomaly is explained by Dudeja-Sen-Lu universality with the empirical Kerdock spectrum — i.e., the right SE recursion is the structured-spectrum one (with Kerdock spectral law as input), not the iid-Gaussian Bayati-Montanari one.

Strategy action: Cap 8 row in `cap_map.json` annotated with "envelope extends to M/N=8 via Dudeja-Sen-Lu (in-class surrogate: {family})". Cap 12 row recategorized: AMP-Bayati-Montanari fails, but Dudeja-Sen-Lu surrogate-AMP succeeds.

## HARD FAIL — `KERDOCK_UNIVERSALITY_TEST_INCONCLUSIVE` (surrogates disagree)

Any pair of surrogates differs by >25% on at least one M/N cell. The test has no clean baseline.

Interpretation: spectrum-matching surrogate construction is structurally wrong at that scale (or AMP has not converged on at least one surrogate). Probably indicates the random-sign Hadamard or Haar-with-Kerdock-spectrum surrogate has degenerate dynamics outside M/N=1 (e.g., random-sign Hadamard rows become highly correlated for M > N if signs collide).

Strategy action: rehab follow-up — debug surrogate construction (likely the M > N branch of random-sign Hadamard) and re-ship with tightened surrogate, or retire this approach and try second-order freeness (Mingo-Speicher) for variance prediction instead of mean.

## MIDDLE BAND — `KERDOCK_UNIVERSALITY_NOVEL_OUT_OF_CLASS`

Surrogates agree among themselves on every cell (test informative), but Kerdock disagrees with **all 3** of them by >25% on at least one M/N.

Interpretation: substrate-novel non-universality finding. Kerdock's structure puts it outside the Dudeja-Sen-Lu class on at least one cell — its singular-vector basis is NOT "generic" in their precise sense. This is a defensible product claim ("our substrate is genuinely outside the known AMP-universality envelopes").

Strategy action: Cap 12 row promotes from "AMP-Bayati-Montanari fails on Kerdock" to "Kerdock breaks AMP universality (Dudeja-Sen-Lu)" with the specific out-of-class M/N values reported. Research follow-up: dispatch a drill on the Maiorana-McFarland low-rank-coherence diagnostic that Dudeja-Sen-Lu require, to see whether Kerdock violates the coherence condition at the specific failing M/N.

## Otherwise (Kerdock partial match, no single all-cell surrogate)

Returned as `KERDOCK_UNIVERSALITY_TEST_INCONCLUSIVE` with the closest-surrogate diff reported. This third inconclusive band catches the "Kerdock matches iid_gaussian for M/N<=2 but doesn't match anything at M/N=4" case. Strategy action: dispatch a finer-grained M/N=2→4 sweep to localize the universality-class boundary.

---

## Risks / known issues

- **Kerdock t=6 N=4096 is large**: codebook is 4N x N = 16384 x 4096 in {-1,+1}, ~64M entries; build cost is dominated by Maiorana-McFarland construction (one-shot per cell × seed; can be cached if needed). Past v1 Kerdock-AMP runs confirmed this is tractable on remote CPU in ~minutes per cell.
- **Haar surrogate cost** at M/N=8: U is 32768 x 4096, V is 4096 x 4096; QR + matrix product is one SVD-comparable operation per seed; expected wallclock ~30s per seed at M=32768 (dominant cost is the 32768×4096 QR).
- **AMP iteration cost** at M/N=8 with N=4096: matrix-vec on 32768×4096 ≈ 130M flops per iter × 200 iters × 5 seeds × 4 families = ~520B flops total, ~10 min on a fast CPU.
- **random-sign Hadamard for M > N** uses repeated rows with fresh signs; this may not actually produce a "generic" singular-vector basis (rows are linearly dependent for M > N). This is documented in HARD-FAIL band as expected failure mode — if it triggers, that's diagnostically informative.

---

## Status_log entry plan

After completion, runner writes verdict and status_log emits an `experiment_completed` entry with `importance=HIGH` (envelope extension OR novel non-universality annotation) and `plain_language` summarizing the in/out-of-class verdict.

This prereg's `experiment_queued` status_log entry is written by exp_dev at ship time with `importance=HIGH`.

---

## Citations

- Dudeja-Sen-Lu (2023). "Spectral Universality of Regularized Linear Regression with Nearly Deterministic Sensing Matrices." arXiv:2208.02753. IEEE TIT 2023.
- Liu-Cakmak-Liang-Takeuchi (2020/2022). "Memory AMP." arXiv:2012.10861. IEEE TIT 68(11). [shows MAMP fixed point = VAMP fixed point under RUI]
- Bayati-Montanari (2011). "The dynamics of message passing on dense graphs..." IEEE TIT 57(2). [iid Gaussian AMP-SE baseline]
- Rangan-Schniter-Fletcher (2017). "Vector Approximate Message Passing." arXiv:1610.03082.
- Can-Rengaswamy-Calderbank (2019). "Kerdock Codes Determine Unitary 2-Designs." arXiv:1904.07842.
