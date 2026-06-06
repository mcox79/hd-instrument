# ROUTING — Data attribution variation sweep (4 axes, 16 cells)

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Status:** USER AUTHORIZED 2026-06-03 ($0 CPU; ~15 min wall; testbed dispatches on engineering ready).

---

## 0. WHAT THIS IS (plain language)

Variation sweep on the data-attribution experiment (Experiment A from the brain-inspired probe batch). The base experiment landed in 43 seconds with MIDDLE_BAND result: rho = 0.6937 (parity with TracIn) at 4.16× speedup. Goal of this sweep: find the Pareto frontier of accuracy vs speedup. At 43s per cell, exploring variations is essentially free.

Testbed already has the smoke-validated Experiment A script on disk. This sweep parameterizes that script across 4 axes.

---

## 1. THE FOUR SWEEP AXES

### Axis 1 — Substrate dimension N

Sweep N ∈ {1024, 2048, 4096, 8192, 16384}. Smaller N = less compute per attribution. Look for dimension at which rho holds near parity (~0.69) while wall keeps dropping.

5 cells × ~45s = ~4 min wall.

### Axis 2 — K examples sampled per query

Sweep K ∈ {10, 50, 100, 500, full}. Substrate computes counterfactual for K training examples per query; cost scales with K. Look for K at which rho approaches asymptote.

5 cells × ~45s = ~4 min wall.

### Axis 3 — Hutchinson probe count

Sweep n_probes ∈ {100, 500, 1000, 5000}. Standard MC tradeoff: fewer probes = less compute, more variance.

4 cells × ~45s = ~3 min wall.

### Axis 4 — Counterfactual primitive variant

Test 2 alternatives to rank-1 substitution:
- Rank-2 substitution (more expressive counterfactual)
- Sherman-Morrison Newton-step (uses curvature)

2 cells × ~60s = ~2 min wall.

---

## 2. TOTAL

**16 cells. Total wall ~12-17 min. Cost $0 (CPU only).** Cells can run sequentially on the same CPU runner or in parallel where bandwidth allows.

---

## 3. PRE-REGISTERED ANALYSIS

For each axis sweep, report:
- rho per cell (correlation with ground-truth attribution rankings)
- Wall time per cell
- Speedup vs TracIn baseline (= 1 / wall_ratio)

Identify Pareto-optimal configurations on the (rho, speedup) frontier.

**Strategic outcomes:**
- If any configuration delivers rho ≥ 0.69 AND speedup ≥ 10× → substrate-data-attribution product claim strengthens to "TracIn-parity with 10× speedup"
- If any configuration delivers rho ≥ 0.80 AND speedup ≥ 4× → substrate-novel claim "TracIn-beating accuracy with 4× speedup"
- Best case: configuration delivers rho ≥ 0.80 AND speedup ≥ 10× → flagship data-attribution capability

---

## 4. STATUS-CHECK REQUEST

Before dispatching, verify:
- [ ] Has any of these 16 cells already been run as a sub-cell of Experiment A?
- [ ] Is testbed's Experiment A script parameterizable across these 4 axes, or does it need scaffolding?

Expected: cells are new (not yet run); script needs minor parameterization to accept N / K / n_probes / variant args.

---

## 5. DISPATCH INSTRUCTIONS

Run the 16 cells on local CPU runner. Output: Pareto-front summary + per-cell metrics. Verdict classification per cell (HP / MIDDLE / HF using same bands as original Experiment A: rho > 0.8 = HP, 0.3-0.8 = MIDDLE, < 0.3 = HF). Aggregate verdict surfaces the Pareto-optimal configuration as the "headline" result.

Status_log entries per `feedback_for_you_tab_primary_channel`: batch launch + each-axis-complete + final Pareto summary.

---

## 6. DISCIPLINE

- Per `feedback_plain_language_experiment_tracking`: experiment described by what it tests, not by arbitrary labels
- Per `feedback_no_padding_experiments`: each axis sweep targets a specific speedup-or-accuracy lever
- Per `feedback_no_smoke_preframing_in_task_prompts`: HP/MID/HF bands explicit per cell
- Per `feedback_testbed_progress_logging_and_restart`: per-cell partial JSON output
- PROT-018: anchor names use `substrate_data_attribution_variation_<axis>_<value>_v1` family

---

**END.**

Testbed: dispatch when ready. CPU-only; $0; ~15 min total wall. Expect Pareto-front result that informs whether substrate-data-attribution capability claim should be "parity with 4× speedup" (current) or stronger (if sweep finds better configurations).
