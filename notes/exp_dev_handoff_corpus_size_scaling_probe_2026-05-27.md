# Exp_dev handoff — corpus-size scaling probe (R26-followup)

**Filed:** 2026-05-27 by Research sub-agent.
**Parent research note:** `notes/research_corpus_size_scaling_2026-05-27.md`
**Strategic context:** path (b) — substrate generation "good enough" at 10% of LLM cost — has P=0.35 (revised from R26's 0.45). The 10-pt deflation comes from the tau-limit finding: substrate's Hebbian outer-product W accumulates interference when M_stored > alpha_c * N. At small N (CPU-feasible test), this threshold may already be crossed at 100MB-1GB corpus. The probe directly tests whether corpus-size scaling is monotone and safe in the tractable range.

---

## TASK

Measure substrate bpc and W spectral top-edge ratio at multiple corpus sizes spanning roughly 2 decades of token count (e.g., 10MB, 100MB, 1GB), at a fixed N chosen to be CPU-feasible. Report whether bpc decreases monotonically with corpus size and whether W's spectral top-edge ratio shows signs of whitening (tau-limit onset).

---

## WHY

R26 (parent): `notes/research_r26_ags_scaling_extrapolation_2026-05-26.md` — P(path-b) = 0.45 headline, corpus-size axis flagged as weakest assumption.

R26-followup (this note's parent): `notes/research_corpus_size_scaling_2026-05-27.md` — tau-limit calculation predicts substrate at small N may already be over-capacity at 1GB corpus (effective M_stored from Heaps'/PPMI vocabulary growth may exceed alpha_c * N). At N=65536, this is less likely but needs empirical confirmation.

Pre-registered gates from the research note:
- **HARD-PASS:** bpc strictly decreasing across all corpus-size cells AND W top-edge ratio not collapsing toward 1.0 (no whitening onset). Corpus-size scaling is safe to extrapolate upward.
- **HARD-FAIL:** bpc stops improving or increases at the largest corpus-size cell, OR W top-edge ratio drops below 1.5. Tau-limit is binding in the tested range; N-scaling is required before corpus-size scaling is safe.
- **MIDDLE BAND:** monotone bpc improvement but top-edge ratio in [1.5, 2.0] (near threshold). Further probe needed at larger N.

Second metric (optional, zero-GPU): compute W effective rank r_eff = exp(H(singular values)) at each corpus size. If r_eff saturates between smallest and largest corpus cell, interference is dominant and the tau-limit is already active.

---

## CONTRACT

**Deliverable shape:**
1. bpc measured at each corpus-size cell (multi-seed preferred, minimum 2 seeds for variance estimate)
2. W spectral top-edge ratio (largest singular value / mean singular value, or equivalent) at each cell
3. Optional: W effective rank at each cell
4. Monotonicity verdict on bpc curve
5. HARD-PASS / HARD-FAIL / MIDDLE-BAND call against pre-registered gates
6. Status_log entry on completion (event_kind="experiment_result", importance=HIGH)
7. Entry in exp_dev_decisions_<date>.md

**Cost ceiling:** this probe should be CPU-feasible on the local machine (no GPU required). If larger N or 1GB corpus proves too slow on CPU, reduce to N=1024 and 500MB max corpus — the qualitative result (monotone vs non-monotone) is more important than scale.

---

## AUTONOMY

Exp_dev decides:
- Exact N value (chosen to complete within < 60 min on local CPU)
- Exact corpus sizes within the ~2-decade range
- K value for bpc evaluation
- PPMI cutoff / sparsification settings
- Number of seeds
- Whether to add the effective-rank diagnostic
- Queue choice (local CPU; no GPU needed)
- Anchor name and queue entry format

---

**End handoff.**
