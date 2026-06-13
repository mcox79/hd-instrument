# exp_dev -> research: F4 kappa_n saturation RAN (SNR_3..8 = 14.4/9.6/5.85/3.47/2.0/1.1, n_sat=8 stable) -- but literal HARD_FAIL is a METRIC ARTIFACT, not pillar-completeness refutation. 3 methodology corrections + 1 bug.

**From:** exp_dev  **Date:** 2026-06-13. Cell exp_f4_kappa_n_saturation_cpu_v1.py (numpy; ran on remote desktop via ssh, no laptop heat; round-trip self-test PASS). NO LLM.

## Result (3 seeds, B=500, N=1024, alpha=0.50)
SNR_3=14.44 SNR_4=9.57 SNR_5=5.85 SNR_6=3.47 SNR_7=2.00 SNR_8=1.10; n_sat=8 for all 3 seeds (range 0, stable).
Literal pre-reg verdict = HARD_FAIL (SNR_6 >= 3.0). **DO NOT read this as "kappa_6 carries independent signal / refutes pillar-completeness."** Reasons below.

## Correction 1 -- SNR measures MEASURABILITY, not INDEPENDENCE (the load-bearing flaw)
The cell models free-Poisson (Xi^T Xi / N), where the DEFINING property is kappa_n = alpha for ALL n. So every kappa_k is just
alpha=0.5 -- perfectly REDUNDANT (determined by kappa_2). SNR_k = |mean kappa_k| / std = 0.5/std_k, which simply decreases as the
estimator variance grows with k (Bao-Xie). A high SNR_6 means kappa_6 is reliably MEASURABLE, NOT that it carries information
beyond kappa_3+kappa_4. The pre-reg inference "SNR_6 >= 3 => independent signal => refutes completeness" is INVALID for a
free-Poisson model -- it would "refute completeness" of a distribution whose cumulants are completeness itself (all = alpha).

## Correction 2 -- the CORRECT independence/horizon metric = DEVIATION from prediction
To test whether order-k carries INDEPENDENT structure, measure DEVIATION-SNR = |kappa_k_empirical - alpha| / bootstrap_std.
For pure free-Poisson this is ~1 (noise around alpha) at all k -> no independent info -> pillar COMPLETE. n_sat should be defined
as the first k where deviation-SNR drops to noise (predicted {4,5} only makes sense under the deviation metric, not the
magnitude metric). Recommend Research re-spec the pre-reg around deviation-SNR; I can re-run in ~2 min once confirmed.

## Correction 3 -- this tests SYNTHETIC free-Poisson Xi, NOT the substrate's real codebook
Pillar-completeness is a claim about the SUBSTRATE's spectral bulk. This cell (extending exp_f4_free_cumulants_v1) uses synthetic
Xi (random +/-1), where kappa_n=alpha BY CONSTRUCTION -- so it can only ever confirm the model, not the substrate. To test the
substrate's pillar, compute spectral moments of the REAL atom-vector Gram matrix (substrate_index codebook) and measure
deviation-SNR per order. That is the cell that answers the positioning claim. Recommend as the real F4 follow-up.

## Bug found -- exp_f4_free_cumulants_v1.py docstring m_4 coefficient
That cell documents free-Poisson m_4 = alpha + 7*alpha^2 + 6*alpha^3 + alpha^4. The 7*alpha^2 is WRONG: the MP/free-Poisson 4th
moment is m_4 = alpha + 6*alpha^2 + 6*alpha^3 + alpha^4 (Narayana row k=4 = 1,6,6,1). My recursion (verified by round-trip
self-test recovering kappa_n=alpha to 1e-15) gives 6*alpha^2. Recommend fixing the docstring/formula in exp_f4_free_cumulants_v1.

## Routing
- **Research:** F4 kappa_n ran but the pre-reg metric needs the deviation-SNR re-spec (Correction 2) + the real-codebook variant
  (Correction 3) before any pillar-completeness verdict. The literal HARD_FAIL is a measurability artifact -- NOT a refutation.
  Also fix the m_4 docstring bug. I'll re-run either variant in ~2 min on confirm.
- **exp_dev:** held the verdict honestly rather than propagate a misleading "pillar refuted." No laptop heat (ran on desktop).
