# Pre-registration: tcft_m_sweep_v1

**Filed:** 2026-05-27  
**Script:** experiments/exp_tcft_m_sweep_v1.py  
**Queue:** remote_cpu_queue  
**Timeout:** 5400s

## Scientific question

Does var_ratio (TCFT trajectory-class fluctuation variance ratio) decrease monotonically
with M at N=8192, confirming the 1/sqrt(N*M) theoretical convergence prediction?

tcft_n8192_v6/v7 HARD_PASSed at N=8192, M=1024, mean_var_ratio=3.2e-8 (6 OOM below 0.10).
Default M = N*0.125 = 1024. Theory: var_ratio ~ 1/sqrt(N*M) -- larger M -> smaller ratio.

## Parent verdict

- tcft_n8192_v6: HARD_PASS, mean_var_ratio=3.2e-8 at N=8192 M=1024 5-seed
- tcft_n8192_v7: HARD_PASS (corroborating replication)

## Pre-registered thresholds

HARD_PASS: var_ratio < 0.10 for ALL M >= 512 (consistent with v7), AND
  Spearman r(M, var_ratio) < -0.5 (monotone decrease confirmed).
  Confirms 1/sqrt(M) convergence; deletion-certificate foundation becomes bulletproof.

HARD_FAIL: var_ratio >= 0.10 at M=1024 (contradicts v7 HARD_PASS).

MIDDLE_BAND: all var_ratio < 0.10 but no clear decreasing trend (Spearman r >= -0.5).

## Formula self-tests (from script)

1. vanilla_jarzynski(works) computes variance of exp(-W/kT) array
2. tcft_conditioned(works) conditions on |W| < median -> variance_ratio = var_c0/var_all
3. For works all-zero: variance_ratio = 0
4. Spearman r([1,2,3,4,5], [5,4,3,2,1]) = -1.0
5. Theory: works = -v@W@v at loading step mu; for M large: var_ratio smaller

## Justification

v247 priority 2 (MEDIUM): M-sweep diagnostic promotes TCFT deletion-certificate
foundation from "confirmed at M=1024" to "confirmed across M range." Directly
addresses deletion-certificate Cat-A killer feature engineering confidence.
Fills the gap identified in v245 Decision 10(c).

## Production config

N_FULL=8192, M_VALUES_FULL=[128,256,512,1024,2048], SEEDS_FULL=[7,17], timeout=5400s
