# Prereg: kappa3_nlo_formula_validation_v2_per_pattern_lognormal_noise

## Anchor
kappa3_nlo_formula_validation_v2_per_pattern_lognormal_noise

## Priority
A (Research Q1: SIGN discriminator, dual-anchor with v1). Per-pattern multiplicative log-normal noise
on Xi (Research PP-50 spec) -> POSITIVE kappa_3 deviation; v1 (additive-on-W) gave NEGATIVE. Together =
empirical evidence that noise convention determines the sign (not substrate-specific).

## Scientific question
Sweep sigma_g in {0.10..0.80} at alpha=0.05, N=4096; W = Xi_noisy^T Xi_noisy/N with per-pattern
log-normal scale exp(sigma_g*Z). Is the noise-induced free-kappa_3 deviation POSITIVE + monotone in
sigma_g (vs v1's negative)?

## Pre-registered bands (SIGN; v2 purpose)
HARD-PASS: deviation positive on >=5/7 cells AND monotone non-decreasing in sigma_g.
MIDDLE: positive but non-monotone.
HARD-FAIL: <=2/7 positive (contradicts convention claim).

## MAGNITUDE CAVEAT (routed to Research)
Raw free-cumulant kappa_3/alpha-1 OVERSHOOTS the leading-order formula 3*(exp(sg^2)-1)*alpha by orders
of magnitude even at N=4096 (heavy-tailed lognormal weights). Exact kappa_3 NORMALIZATION the formula
uses is the open question (in-flight kappa3-NLO drill). Magnitude-vs-formula reported as SECONDARY.

## Formula self-tests (PROT-022)
1. formula(0.30,0.05)=0.0141255. 2. free kappa_3 equal-diagonal=0. 3. per-pattern lognormal mean=exp(sg^2/2). [PASS]

## N-suffix binding (PROT-018)
script N=4096 (declared); 5 seeds (PROT-021). v1 KEPT (not superseded) per Research Q1.

## Timeout
sigma_g sweep x 5 seeds x Hutchinson at N=4096. timeout_s=14400.

## Smoke gate
Smoke PASSED (N=256): all 7 cells POSITIVE (n_pos=7/7); non-monotone at tiny M (expected); full N=4096
should be monotone. Sign signal is the headline + is clearly positive.

## Queue
remote_cpu_queue (CPU; pure numpy).
