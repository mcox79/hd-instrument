# Pre-registration: wave14mp_edge_detector

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14mp_edge_detector.py](../experiments/exp_wave14mp_edge_detector.py)

## Why

Crystallography research agent finding: the Marchenko-Pastur edge of W's
spectrum IS the substrate's phase indicator. rho = lambda_+(empirical) /
lambda_+(MP, gamma=K/N) crosses 1.0 at the AGS phase transition (K ~ alpha_c * N).

This is SUBSTRATE FORENSICS WITHOUT QUERIES - a capability transformer KV
caches don't have. Companion to the security finding: at K < N/(2 log N) ~ 170
the same machinery enables full readout attack via charge-flipping.

## Hypothesis

rho = 1.0 transition midpoint falls within +/- 15% of K = alpha_c * N = 627
(using measured alpha_c=0.153 at N=4096).

## Operational

N=4096, K in {50, 100, 200, 350, 500, 627, 800, 1200, 1800, 2500, 3500}.
12 seeds per K. SVD of W @ W.T / N; lambda_+_empirical = max eigenvalue.
lambda_+_MP = (1 + sqrt(K/N))^2.

## Expected runtime

Smoke: ~5 sec
Full: ~10-15 min on GPU (SVD of 4096x4096 matrices x 12 seeds x 11 K values
= 132 SVDs of 4096x4096 ~ 5 sec each = ~10 min)

## What this enables

VALIDATED: substrate has a phase-detector primitive callable without queries.
Practical use: detect substrate overload condition; certify regime for
auditors; security primitive (forensic dump capability + risk).

DEVIATES: MP analog needs refinement; substrate is not canonical AGS Hopfield
in spectral terms.

## Cited mechanism

- Marchenko-Pastur 1967
- Baik-Ben Arous-Peche BBP transition (2005)
- Amit-Gutfreund-Sompolinsky 1985 (AGS)
- Crystallography research agent (this session)
- Yaskov arXiv:2111.04296
- "From SGD to Spectra" arXiv:2507.12709
