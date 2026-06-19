# Pre-registration: wave14_betB_pac_bayes_kl_predictor_v1

**Filed:** 2026-05-24  
**Script:** experiments/exp_wave14_betB_pac_bayes_kl_predictor_v1.py  
**Queue:** overnight_queue (GPU)  
**Timeout:** 10800s  

## Hypothesis

Alt3: Diagonal-Laplace Fisher KL between Phase-A and Phase-B trained-weight posteriors predicts retention_A (how much Phase-A knowledge survives Phase-B training). This uses the R-PRIME-1 Laplace-Fisher derivation (commit 0140545) — NOT input-data KL (R-PRIME-3 HARD-FAIL) and NOT identity-covariance KL (vacuous KL = N^2/2).

Formula (eq. ** from handoff):
  KL_diag(q_B || q_A) = 0.5 * sum_i [ (f_{A,i}/f_{B,i}) - 1 - log(f_{B,i}/f_{A,i}) + f_{A,i}*(W_B-W_A)_i^2 ]

This is computed from: (1) W_A (after Phase-A), (2) W_B (after Phase-B), (3) diagonal Fisher at W_A from Phase-A batches, (4) diagonal Fisher at W_B from Phase-B batches.

## Method

- 5 seeds x 5 corpus-pair types (shuffled_same, reversed_same, python_source, verification, random_bytes)
- N=4096, Phase-A: 8 epochs, Phase-B: 5 epochs, 200k bytes per phase
- Snapshot W_A after Phase-A, W_B after Phase-B
- Compute diagonal empirical Fisher at each checkpoint
- Compute KL_diag + Euclidean proxy ||W_B-W_A||_F^2 for each cell
- Correlate each predictor vs measured retention_A

## Pre-registered bands

**HARD-PASS:**
- Pearson r^2(KL_diag, retention_A) >= 0.50 across >= 15 cells
- AND Fisher improvement over Euclidean >= 0.10 in r^2
→ R-PRIME-1 Laplace-Fisher KL is binding mechanism. Alt3 promoted. PAC-Bayes posterior-over-W track opened.

**HARD-FAIL:**
- r^2(KL_diag, retention_A) < 0.20 AND r^2(Euclidean, retention_A) < 0.20
→ No weight-space geometry predicts Bet B retention. Rehab: function-space KL, empirical Bernstein, task-arithmetic.

**MIDDLE:**
- r^2 in [0.20, 0.50) OR Fisher improves Euclidean by < 0.10
→ Partial signal; try larger sweep or KFAC Fisher upgrade.

**LAPLACE-ASSUMPTION-VIOLATED:**
- ||Delta_W||_F / ||W_A||_F > 0.5 in majority of seeds
→ Laplace posterior approximation invalid; KL estimate unreliable; flag before reporting.

## Calibration

P(r^2 >= 0.50) before lit-scan deflation: 0.55  
After deflation (uncharted regime, novel synthesis): 0.40  
Lineage: McAllester 1999, Dziugaite-Roy 2017, Khan-Nielsen 2018, Daxberger 2021

## Notes

- Builds on Alt2 (W_internal_signature HARD-FAIL) and Alt1 (shift-class HARD-PASS)
- Triggered by R-PRIME-1 derivation landing at commit 0140545
- Per [[feedback-strategy-spec-formula-selftests]]: 5 self-test cells inline in script
- Per [[feedback-envelope-expansion-fail-bands]]: 4 outcome bands pre-registered
- Per [[feedback-lit-scan-calibration-penalty]]: calibration penalty applied
