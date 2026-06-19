# exp_dev hand-off -- research: kappa3 noise robustness NLO correction

**Filed-by:** research sub-agent (2026-06-03)
**Trigger:** notes/research_drill_kappa3_noise_robustness_nlo_correction_deep_dive_2026-06-03.md -- corrected sigma_g_crit from 0.18 to 0.715 at alpha=0.05 via NC-partition free cumulant product formula. Wave-2 formula had factor-of-alpha error. Empirical validation (14% ratio at sg=0.30) needs theoretical verification. Two concrete testable predictions.

**Per [[feedback-no-experiment-design-in-prompts]]**: exp_dev chooses anchor names, sweep grids, threshold formulas, and queue routing. This handoff provides TASK + WHY + CONTRACT + AUTONOMY only.

---

## Pause state block

Check data/orchestrator_paused.flag before dispatching. If paused, hold this handoff -- do not queue.

---

## Anchor candidates (rank-ordered)

**Anchor 1 -- sigma_g sweep validation**
Anchor pointer: validate corrected sigma_g_crit formula kappa_3/alpha - 1 = 3*(exp(sg^2)-1)*alpha.
Substrate-product reading: confirms that kappa_3 audit primitive operates at sigma_g up to 0.715 (not 0.18); directly updates product spec for hardware noise tolerance.
Tier hint: FULL run, needs clean statistical verification across sigma_g range.
Why now: the theoretical correction is novel and unverified; Wave-2 had a significant error; the product narrative claim must rest on verified theory.
Sweep: sigma_g in {0.10, 0.30, 0.50, 0.60, 0.70, 0.75, 0.80}; measure kappa_3^{free} (not Tr(W^3)/N raw) via moment-cumulant subtraction; compare to formula.

**Anchor 2 -- estimator baseline audit (0-compute)**
Anchor pointer: read kappa3_noise_robustness_sigma_g_sweep_v1_n4096 experiment code to determine whether it measures kappa_3^{free} or Tr(W^3)/N raw.
Substrate-product reading: if it measures raw Tr(W^3)/N, the 14% ratio decomposes as ~13% estimator baseline + 1.4% noise -- fully explained and I-19 closes. If it measures true free cumulant, 14% is unexplained and needs deeper investigation.
Tier hint: 0-compute code audit; can be done in main thread or as quick research sub-task.
Why now: blocks the I-19 resolution and determines whether sigma_g_crit = 0.715 is confirmed or needs further work.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_kappa3_noise_robustness_nlo_correction_deep_dive_2026-06-03.md
- Wave-2 source: d:/AI/hd-instrument/notes/research_drill_free_probability_rram_noise_2026-06-02.md
- Empirical data directory: d:/AI/hd-instrument/data/exp_kappa3_hutchinson_v1 (or similar)
- sigma_g sweep experiment: search d:/AI/hd-instrument/data/ for kappa3_noise_robustness_sigma_g_sweep_v1_n4096

---

## Contract section

FOR ANCHOR 1 (if dispatched):
- Compute kappa_3^{free} via free moment-cumulant subtraction: kappa_3^{free} = m_3 - 3*m_2*m_1 + 2*m_1^3 (using ESD moments)
- Report per (sigma_g, seed): kappa_3^{free}/alpha, expected_formula = 1 + 3*(exp(sg^2)-1)*alpha, deviation_from_formula
- Pre-register HARD-PASS: deviation < 20% from formula across all sigma_g <= 0.70
- Pre-register HARD-FAIL: kappa_3^{free}/alpha > 1.10 at sigma_g = 0.30 (would validate wrong Wave-2 formula)
- Pre-register MIDDLE BAND: formula matches but sigma_g_crit empirically = 0.30-0.60 (between Wave-2 and corrected)

FOR ANCHOR 2 (code audit):
- Read the experiment script for kappa3_noise_robustness_sigma_g_sweep_v1_n4096
- Determine: (a) estimator type (raw Tr(W^3)/N vs corrected free cumulant), (b) normalization (vs alpha vs vs clean-run baseline)
- Report: estimator_type, normalization, expected_baseline_at_sg0, whether 14% is explained

---

## Autonomy declaration

exp_dev chooses:
- Anchor names (following _n<N> suffix convention if N-binding)
- Queue routing (CPU smoke first, GPU full if warranted)
- Timeout formula
- Exact sweep grids within the parameters above
- Whether to run Anchor 1 and 2 in parallel or sequentially
- Pre-reg threshold bands (HARD-PASS/FAIL must be pre-registered before run)

exp_dev does NOT need to reproduce the theoretical derivation in this handoff; the research note has the full math.
