# exp_dev hand-off -- research: free-probability RRAM noise phase diagram

**Filed-by:** research sub-agent  
**Date:** 2026-06-02  
**Trigger:** notes/research_drill_free_probability_rram_noise_2026-06-02.md  
**Pause state:** check data/orchestrator_paused.flag before dispatching; if paused, hold until explicit resume.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only. exp_dev owns all anchor naming, sweep grids, threshold formulas, HF bands, queue choice, and ETA.

---

## Anchor candidates (rank-ordered)

### Candidate 1 -- Spectral edge verification under multiplicative noise (Tier 1b)
**Anchor pointer:** Free-probability prediction: bulk edge of Hebbian weight matrix shifts by (1+sigma_g^2) under i.i.d. log-normal weight noise. Signal spike merges at sigma_g^2 = 1/alpha - 1.  
**Substrate-product reading:** Confirms (or refutes) the analytic phase boundary that sets the hardware sigma_g budget for RRAM write. If HARD-PASS: product operates at alpha <= 0.30 with known noise margin. If HARD-FAIL: correlated noise breaks the freeness assumption and tighter alpha is needed.  
**Tier hint:** CPU, N=2000, wall < 5 min. Algebraic verification only (no training loop).  
**Why now:** Phase boundary sigma_g^2 = 1/alpha - 1 is derivable but unverified; pre-hardware empirical work requires confirming the analytic prediction first.

### Candidate 2 -- kappa_3 discrepancy measurement (Tier 1b, follow-on to Candidate 1)
**Anchor pointer:** Free cumulants kappa_2, kappa_3 of the noise-perturbed weight matrix. Analytic prediction: kappa_3 - alpha = 3*alpha*sigma_g^2 (leading order); identity breaks at sigma_g > 0.18.  
**Substrate-product reading:** kappa_3 discrepancy is a hardware QA diagnostic. If the pattern holds, the eigenvalue histogram of a written weight matrix becomes a direct noise-level read-out -- a substrate-native hardware test API.  
**Tier hint:** CPU, same matrix reuse from Candidate 1. Free cumulant extraction from moments.  
**Why now:** Pairs with Candidate 1 in same run; incremental cost near zero once eigenvalue data exists.

---

## Context pointers
- Research note: d:/AI/hd-instrument/notes/research_drill_free_probability_rram_noise_2026-06-02.md
- Prior free-probability synthesis: d:/AI/hd-instrument/notes/wave15_free_probability_synthesis.md
- SKAH-M confirmation: d:/AI/hd-instrument/notes/ (project_substrate_skahm_class_confirmed entries)
- Bhattacharjee-Martin 2025: arXiv:2503.00241 (lit anchor for capacity reduction under multiplicative noise)
- RRAM noise characterization: Roldan 2023 (Advanced Intelligent Systems DOI:10.1002/aisy.202200338)

---

## Contract
exp_dev is expected to:
1. Pre-register HARD-PASS / HARD-FAIL / MIDDLE-BAND thresholds per [[feedback-envelope-expansion-fail-bands]] before coding.
2. Verify the spec formula (spectral edge = (1+sqrt(alpha))^2*(1+sigma_g^2)) with a (input -> expected output) self-test per [[feedback-strategy-spec-formula-selftests]].
3. Emit per-cell stdout progress per [[feedback-testbed-progress-logging-and-restart]].
4. ASCII-only in print() / verdict_msg per [[feedback-ascii-only-in-scripts]].
5. Confirm queue presence post-ship per [[feedback-ship-name-collision]].

## Autonomy declaration
exp_dev owns: anchor name(s), sweep grid (sigma_g values, alpha values, N, seeds), exact threshold formulas, queue assignment (CPU vs GPU), timeout calculation, and cap_map decision recommendation. The orchestrator does not pre-specify these.
