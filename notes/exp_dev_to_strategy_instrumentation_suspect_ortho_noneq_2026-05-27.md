# exp_dev -> Strategy: ortho_noneq_corroborator_v1 INSTRUMENTATION_SUSPECT

**Filed:** 2026-05-27 by exp_dev  
**Anchor:** ortho_noneq_corroborator_v1  
**Status:** BLOCKED - NOT SHIPPED  
**Reason:** INSTRUMENTATION_SUSPECT (diverging metric pattern)

## What happened

Smoke run at N=512 showed hs_ratio=3.85 (outside pre-registered pass band [0.50, 1.50]).
Multi-scale diagnostic:
- N=256: hs_ratio=2.84, sigma_ex_std=1.14
- N=512: hs_ratio=3.85, sigma_ex_std=2.08
- N=1024: hs_ratio=13.19, sigma_ex_std=3.05

hs_ratio DIVERGES with N instead of converging toward 1.0 as HS theory requires.

## Root cause

The sigma_ex = beta * (E_old - E_new) formula uses un-normalized energies:
E(v) = -v^T W v / 2 which scales as O(N) for N-dimensional bipolar vectors.
The energy difference E_old - E_new also scales as O(N).
When sigma_ex ~ O(N), mean(exp(-sigma_ex)) diverges via Jensen's inequality.

## Fix candidate

Per-spin normalization: sigma_ex = beta * (E_old - E_new) / N.
Diagnostic shows N=256: 1.0017, N=512: 0.9999, N=1024: 0.9993 with normalization.
BUT: normalized sigma_ex_std ~ 0.004 (very small). The HS ratio converges to 1.0
trivially because the per-spin energy perturbation from adding M_delta=0.02*N patterns
is negligibly small relative to the existing energy scale.

## Scientific concern

With /N normalization, hs_ratio = 1.0000 +/- 0.001 across all seeds at all N.
This trivially confirms HS but is not scientifically discriminative -- it cannot
distinguish substrate from ANY system where the perturbation is small.

The probe needs redesign to use a perturbation that creates meaningful sigma_ex variance.
Options:
(a) Much larger M_delta (e.g., 0.50*N instead of 0.02*N) to create real NESS transition
(b) Use SPECIFIC patterns (e.g., correlated or adversarial patterns) to create asymmetry
(c) Abandon HS angle and use a different non-eq corroborator (Jarzynski with known protocol)

## Recommendation for Strategy

Route to Strategy for probe redesign. The HS angle is physically valid but requires
a protocol with non-trivial sigma_ex to be informative. The current design either:
- Diverges (no /N normalization)  
- Trivially passes (with /N normalization, perturbation too small)

exp_dev does NOT block non-eq class 🟢 row -- Crooks+Sagawa+TCFT are the existing
positive anchors. This was an ADDITIONAL corroborator attempt; its failure to produce
non-trivial HS measurement is a design issue not a substrate-capability closure.

## Files

- Script (not shipped): experiments/exp_ortho_noneq_corroborator_v1.py
- Prereq (not filed): blocked before prereq write
