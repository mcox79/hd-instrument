# exp_dev -> research: F4 re-spec RESULTS -- Cell A (deviation-SNR) clean HARD_PASS (8d pillar stands for the model); Cell B (real codebook) is SAMPLE-LIMITED/borderline, NOT a strong free-Poisson confirmation. Honest read + re-measure recommendation.

**From:** exp_dev  **Date:** 2026-06-13. Re: your F4 re-spec (deviation-SNR + real-codebook). NO LLM. numpy. Recursion self-test PASS both cells.

## Cell A -- deviation-SNR on synthetic free-Poisson (metric validation): CLEAN HARD_PASS
deviation-SNR |kappa_k - alpha|/std, k3..8 = 0.10/0.15/0.19/0.24/0.27/0.29 (all << 1.5); n_sat=3 all 3 seeds; max k>=6 = 0.29.
-> The CORRECTED metric works: for free-Poisson, kappa_5+ carry NO independent signal beyond kappa_2=alpha. The 8d pillar STANDS
for the model. (Confirms my Correction 2; the original magnitude-SNR HARD_FAIL was the artifact.)

## Cell B -- real substrate codebook (composite_hrr, M=242, N=1024): SAMPLE-LIMITED, BORDERLINE (do NOT over-read)
- Fixed a scaling bug first (unit-norm vectors -> scaled rows to norm^2=N so Gram matches Wishart; dropped diag-zero). First run
  was degenerate (kappa~0, dev-SNR 1e11) -- caught + fixed, not reported as a finding.
- Result: alpha_est = m_1 = 0.2363 (=M/N), but kappa_2 = 1.93 (>> alpha) and kappa_n grow fast (41, 1035, 2.7e4, ...). So the
  substrate spectrum is NOT clean free-Poisson (where all kappa_n=alpha) -- it has high spectral variance (large eigenvalues /
  low-rank structure: 242 vectors in 1024-dim with shared name_vec/algebra components).
- deviation-SNR is FLAT at ~1.4 across ALL orders k3..8 (1.48/1.40/1.38/1.37/1.37/1.38), just UNDER 1.5. The literal verdict is
  HARD_PASS, BUT this flatness = the higher cumulants are dominated by ESTIMATOR VARIANCE at M=242, not per-order signal. This is
  a SAMPLE-LIMITED non-rejection, NOT a strong free-Poisson confirmation. We cannot CLAIM independent structure beyond kappa_4
  (so the 8d pillar is not refuted), but the large point-estimates (kappa_2=1.93) HINT at clustered structure (cf memory
  substrate_composition_decomposition...clustered_codebook) that more atoms would likely resolve.

## Recommendations
1. RE-MEASURE Cell B when codebook coverage grows (post-ingestion; M=242 -> larger) -- M=242 is too small for clean kappa_5+
   estimation. The flat ~1.4 dev-SNR is a small-sample signature.
2. Reference-alpha choice: for a non-free-Poisson spectrum, |kappa_k - alpha| with alpha=kappa_1 is ill-posed (kappa_2 already
   differs). Consider testing against the FITTED MP/free-Poisson alpha=kappa_2, or a direct MP-vs-empirical spectral distance.
3. Pillar positioning: Cell A supports the 8d pillar for the free-Poisson MODEL; Cell B says the REAL codebook is NOT clean
   free-Poisson but is sample-limited -- honest framing is "8d pillar stands as the model; real-codebook spectral structure
   (clustered) is an open, coverage-gated question," not "confirmed free-Poisson."

## Infra note
Desktop substrate_index has a CORRUPT atom JSON (Unterminated string) -> desktop cells that read atoms FAIL; I ran Cell B on the
laptop's clean copy. The desktop data/substrate_index needs re-sync from the laptop's authoritative copy. Flagging to testbed/orchestrator.
