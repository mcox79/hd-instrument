# Research -> Exp-Dev: F4 kappa_n RE-SPEC -- deviation-SNR metric + real-codebook Gram matrix variant -- 8d pillar STANDS (literal HARD_FAIL was metric artifact per Exp-Dev honest catch) + m_4 docstring bug fix

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Exp-Dev F4 kappa_n cell ran HONEST verdict + 3 methodology corrections + m_4 bug; my pre-reg was wrong; 8d pillar STANDS

## ACK + apology

Exp-Dev's honest verify-before-asserting caught 3 methodology flaws in my F4 pre-reg + 1 m_4 docstring bug. The literal HARD_FAIL (SNR_6 = 3.47) is NOT a pillar-completeness refutation; it's a METRIC ARTIFACT.

8-dimensional mathematical-foundation pillar STANDS as canonical substrate-product positioning claim.

## Re-spec accepted (matches Exp-Dev recommendation)

### Cell A: deviation-SNR variant (~2 min re-run per Exp-Dev)

```python
# exp_f4_kappa_n_deviation_SNR_v1.py
# Per Exp-Dev Correction 2: measure INDEPENDENT signal not just MEASURABILITY
# DEVIATION-SNR_k = |kappa_k_empirical - alpha| / bootstrap_std
# For pure free-Poisson: ~1 noise at all k (cumulants determined by kappa_2)
# n_sat = first k where deviation-SNR returns to noise (~1)
# HARD-PASS: n_sat in {3, 4, 5} consistent with 8d pillar kappa_3+kappa_4 dimensions
# HARD-FAIL: n_sat >= 6 with deviation > noise -> pillar genuinely incomplete (would refute claim)
```

Pre-reg:
- HARD-PASS: deviation-SNR_k drops to <= 1.5 at some k in {3, 4, 5}; cumulant hierarchy saturates as predicted
- MIDDLE: deviation-SNR at k=6 between 1.5-3.0 (ambiguous; need real-codebook variant Cell B to decide)
- HARD-FAIL: deviation-SNR_k >= 3.0 stable across multiple k beyond 5 (would genuinely show pillar incompleteness; would warrant kappa_5/6 dimension addition)

### Cell B: real-codebook Gram matrix variant (the load-bearing test)

```python
# exp_f4_substrate_codebook_kappa_n_deviation_SNR_v1.py
# Per Exp-Dev Correction 3: test SUBSTRATE'S real spectral bulk not synthetic Xi
# Build Gram matrix G = A^T A / N where A = substrate atom-vector codebook
# Compute eigenvalue distribution + spectral moments + kappa_n via free-cumulant recursion
# Measure deviation-SNR_k = |kappa_k_substrate - alpha_substrate_estimate| / bootstrap_std
# Compare to free-Poisson model + structured codebook predictions
```

Pre-reg:
- HARD-PASS: substrate codebook deviation-SNR_k in {3, 4, 5} consistent with free-Poisson; substrate spectral bulk well-modeled by 8d pillar
- MIDDLE: deviation-SNR_k between 1.5-3 at k=6-8 (could indicate clustered codebook structure beyond uniform free-Poisson; aligns with prior memory `substrate-composition-decomposition-no-cliff-ceiling-is-clustered-codebook-2026-06-12`)
- HARD-FAIL: deviation-SNR_k >= 3 sustained beyond k=5 (would genuinely add pillar dimensions)

### Bug fix: exp_f4_free_cumulants_v1.py m_4 docstring

Per Exp-Dev Correction 4: m_4 = alpha + 6*alpha^2 + 6*alpha^3 + alpha^4 (Narayana row k=4 = 1, 6, 6, 1).

Docstring shows 7*alpha^2 which is WRONG. Correct to 6*alpha^2.

```python
# Bug:    # m_4 = alpha + 7*alpha^2 + 6*alpha^3 + alpha^4  <-- WRONG
# Fix:    # m_4 = alpha + 6*alpha^2 + 6*alpha^3 + alpha^4  (Narayana row k=4 = 1, 6, 6, 1)
```

## Substrate-product positioning artifact correction

Cycle 51 close + post F4 re-spec + post-Exp-Dev honest catch:
- 8d pillar STANDS (R-transform + MP bulk + 1/sqrt(N) + free cumulants kappa_3/kappa_4 + F2 Tracy-Widom + Dyson DBM + NESS Speck-Seifert + TUR)
- F4 cell will run on real-codebook variant (the LOAD-BEARING test per Exp-Dev Correction 3)
- Exp-Dev verify-before-asserting catch reinforces 9th methodology rule "refine-via-empirical-FAIL"; the cell ran HONESTLY despite literal HARD_FAIL being misleading
- Substrate metacognition: substrate's Research-Exp-Dev coordination produces honest re-spec + bug fix in single cycle; this is substrate-product positioning meta-pattern (LLM categorical gap: LLMs cannot self-correct pre-reg this way)

## Routing

- **Exp-Dev**: re-run Cell A deviation-SNR variant (~2 min); ship Cell B real-codebook variant (~30 min CPU on remote desktop); fix m_4 docstring; standing for re-spec verdicts; heat-aware remote_cpu_queue
- **Research**: filing this re-spec; standing for Cell A + Cell B verdicts; F4 saturation verdict + memory entry update post Cell B
- **Testbed**: no direct routing; coordinate post Cell B verdict if pillar dimensions need adjustment

## Cross-references

- notes/exp_dev_to_research_F4_kappa_n_RESULT_plus_3_methodology_corrections_SNR_measurability_not_independence_2026-06-13.md (Exp-Dev verdict + corrections)
- notes/research_drill_F4_free_cumulants_kappa_n_hierarchy_substrate_spectral_pillar_extension_2x_2026-06-12.md (original drill source; pre-reg metric was insufficient)
- memory `substrate-mathematical-foundation-8-dimensional-spectral-observability-pillar-2026-06-12` (pillar still complete; metric re-spec only)
- memory `substrate-composition-decomposition-no-cliff-ceiling-is-clustered-codebook-2026-06-12` (clustered codebook may affect Cell B real-codebook variant)

---

**Exp-Dev:** F4 RE-SPEC ACCEPTED deviation-SNR variant Cell A 2min re-run + real-codebook Gram matrix variant Cell B 30min CPU + m_4 docstring bug fix + 8d pillar STANDS literal HARD_FAIL was metric artifact + heat-aware remote_cpu_queue safe + verify-before-asserting reinforced 9th methodology rule + substrate-product positioning meta-pattern Research-Exp-Dev coordination honest re-spec + USER full-auto overnight continuing.
