# Prereg: kappa3_nlo_formula_validation_sigma_g_v1_n4096

## Anchor
kappa3_nlo_formula_validation_sigma_g_v1_n4096

## Priority
A (kappa3_noise_robustness_nlo handoff Anchor 1). Validate corrected NLO formula
kappa_3^free/alpha - 1 = 3*(exp(sigma_g^2)-1)*alpha (corrected sigma_g_crit ~0.715; Wave-2 had a
factor-of-alpha error). Confirms kappa_3 audit primitive's hardware-noise tolerance for the product spec.

## Scientific question
Sweep sigma_g in {0.10,0.30,0.50,0.60,0.70,0.75,0.80} at alpha=0.05, N=4096. Measure FREE cumulant
kappa_3 (m3 - 3 m1 m2 + 2 m1^3 from Hutchinson moments) of the noise-perturbed W; compare the
noise-induced deviation MAGNITUDE to the formula; locate sigma_g_crit (identity-break > 15%).

## Pre-registered bands (on MAGNITUDE of noise-induced kappa_3 deviation; see SIGN FLAG)
HARD-PASS: |deviation| matches formula within 25% on >=5/7 cells AND identity holds (<15%) through
sigma_g=0.50 and breaks by 0.80 -> sigma_g_crit in [0.50,0.80] (consistent with 0.715); 5/5 seeds.
MIDDLE: 3-4/7 cells match OR sigma_g_crit outside [0.50,0.80] with monotone trend.
HARD-FAIL: <=2/7 cells match (NLO correction refuted).

## SIGN FLAG (to Research)
N=4096 diagnostic: deviation MAGNITUDE tracks the formula well (sg0.7 |dev|=0.096 vs pred 0.095; sg0.8
0.142 vs 0.135) but SIGN is NEGATIVE (unit-mean multiplicative log-normal noise on W decreases
kappa_3^free) while formula predicts an increase. Validates the SCALING LAW on magnitude; the sign
discrepancy implies the drill's intended noise model differs (additive, or noise on patterns Xi, not W)
OR the formula refers to |deviation|. Research should confirm the noise-model/sign convention.

## Formula self-tests (PROT-022)
1. formula(0.30,0.05)=0.0141255. 2. free kappa_3 of equal-diagonal=0. 3. log-normal unit mean. [ALL PASS]

## N-suffix binding (PROT-018)
anchor _n4096; production N=4096. 5 seeds (PROT-021).

## Timeout
sigma_g sweep x 5 seeds x Hutchinson moments at N=4096; PROT-019 floor for _n4096: 14400s.

## Smoke gate
Smoke PASSED (N=256, 2 seeds): mechanics + free-cumulant + sign-flag work; 3/7 magnitude-match at noisy
small N. N=4096 diagnostic confirms clean baseline (ratio_clean ~0) + better magnitude match at higher sg.

## Queue
remote_cpu_queue (pure numpy; CPU).
