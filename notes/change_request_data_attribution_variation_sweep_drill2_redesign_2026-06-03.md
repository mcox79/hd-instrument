# CHANGE REQUEST — Data attribution variation sweep, drill-2-informed redesign

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Subject:** Update the 16-cell variation sweep design per drill 2 findings (`research_drill_data_attribution_accuracy_ceiling_2x_2026-06-03.md`)

---

## What this experiment is (plain language)

Earlier today I shipped a 16-cell variation sweep on the data-attribution experiment (testing whether we can push rho beyond TracIn-parity at 0.69). The 2x research drill on rank-r counterfactual attribution ceiling landed AFTER the sweep was shipped. Drill findings substantively change which axes are highest-leverage. This is the change request before testbed dispatches the sweep.

Original routing: `notes/routing_data_attribution_variation_sweep_2026-06-03.md`
Drill output: `notes/research_drill_data_attribution_accuracy_ceiling_2x_2026-06-03.md`

---

## Status check requested

Before applying changes:

- [ ] Has the original 16-cell sweep been dispatched yet?
- [ ] Has any sub-cell already been run?

Expected: not dispatched (just shipped same-cycle).

---

## Why the redesign

Drill 2 identified **two stacked ceilings** producing the rho=0.69 parity:

1. **Ground-truth noise floor** (P=0.60): TracIn-style and counterfactual-subset ground truths have only 0.70-0.75 bootstrap self-consistency. Both methods at rho=0.69 are at the noise floor, NOT their algorithmic limits. **Original sweep MISSED this axis entirely** — it's the highest-leverage lever.

2. **High-d rank-1 leverage ceiling** (P=0.50, structural): For OLS with X in R^{n×d}, rank-1 attribution structurally caps at rho ~ 0.72-0.78 in high-d. Need rank-2+ structural changes to break past.

Critical predicted null: **Sherman-Morrison Newton-step gives ZERO gain on linear problems** (only materializes in nonlinear models). The original sweep's Axis 4 included Sherman-Morrison — predicted to be a wasted run on the synthetic corpus.

---

## IF NOT YET dispatched → apply this redesign

### Axis 1 (kept) — Substrate dimension N

Sweep N ∈ {1024, 2048, 4096, 8192, 16384}. Still informative.

5 cells × ~45s = ~4 min wall.

### Axis 2 (kept, shrunk) — K examples sampled per query

Sweep K ∈ {10, 100, 500, full}. Drop K=50 (redundant with 10/100 endpoints).

4 cells × ~45s = ~3 min wall.

### Axis 3 (DROPPED) — Hutchinson probe count

Drill found probe count is not load-bearing on this corpus — n_probes=1000 is well above noise floor for the test scale. Drop entirely. Recovers ~3 min wall budget for new high-leverage axes.

### Axis 4 (REPLACED) — Counterfactual primitive variant

OLD: rank-1 / rank-2 / Sherman-Morrison
NEW: **rank-1 baseline / rank-2 Woodbury substitution**

Drop Sherman-Morrison (drill: zero gain on linear problems). Add rank-2 Woodbury as the structural-upgrade variant. Drill predicts delta_rho ~ 0.04-0.08 from rank-2.

2 cells × ~60s = ~2 min wall.

### Axis 5 (NEW, HIGHEST LEVERAGE) — Ground-truth definition

Sweep ground-truth construction:
- **TracIn-style** (current default)
- **Counterfactual-subset at p=0.5** (mid-noise)
- **LOO-exact retraining** (cleanest; gold standard; more expensive per ground-truth point but small corpus makes this tractable)

Drill predicts LOO-exact removes 0.05-0.10 of noise floor — this is potentially the biggest single rho gain in the whole sweep.

3 cells × ~120s = ~6 min wall (LOO is more expensive per-cell than other axes).

### Axis 6 (NEW, STRUCTURAL) — TRAK-style ensemble

TRAK-style ensemble of K rank-1 perturbations across random subspaces.

Sweep K ∈ {1, 5, 20, 50}. K=1 = baseline (current rank-1 = current MIDDLE result). Drill predicts O(1/√K) approximation noise; K=20 → ~0.05-0.10 gain.

4 cells × ~60s = ~4 min wall.

---

## Total redesigned sweep

**18 cells. ~19 min wall. Cost $0 (CPU only).**

Each axis tests a different hypothesized rho-gain mechanism. Stacked structural gains predicted: +0.14-0.30 across (LOO ground truth + rank-2 Woodbury + TRAK ensemble). Could reach rho 0.80-0.95.

---

## Pre-registered analysis (UPDATED)

Per cell:
- rho (Spearman) vs ground-truth ranking
- Wall time
- Speedup vs TracIn baseline

**Strategic outcomes:**
- **Conservative HP:** Any configuration delivers rho ≥ 0.75 AND speedup ≥ 4× → substrate-data-attribution claim strengthens beyond parity
- **Flagship HP:** Any configuration delivers rho ≥ 0.85 AND speedup ≥ 4× → substrate beats published-best data attribution at lower compute
- **Predicted-best combo:** LOO ground truth + rank-2 Woodbury + TRAK K=20 → drill predicts rho 0.80-0.90 stacking
- **HARD-FAIL:** rank-2 Woodbury cell achieves rho ≤ 0.71 on LOO-stabilized ground truth → drill 2 prediction REFUTED; rank-1 ceiling claim revisited

---

## IF ALREADY dispatched → run both in parallel

If the original 16-cell sweep has already been dispatched, do NOT abort it. Let it complete. Then run the NEW 18-cell drill-2-informed sweep as a SECOND batch. Total cost unchanged at $0; total wall doubles to ~35 min. The two batches are complementary (original tests N/K/Hutchinson; new tests ground-truth/structural-rank/ensemble). Combined result: 34-cell Pareto map.

Anchor names if running second batch: `substrate_data_attribution_drill2_<axis>_<value>_v1` family.

---

## Discipline declarations

- Per `feedback_change_request_protocol`: status check first; instructions for both cases
- Per `feedback_plain_language_experiment_tracking`: experiment described by what it tests
- Per `feedback_no_padding_experiments`: each redesigned axis targets a specific predicted-gain mechanism from drill 2
- Per `feedback_no_smoke_preframing_in_task_prompts`: HP/MID/HF bands explicit and tied to drill predictions
- Per `feedback_2x_means_depth`: drill 2 was depth on the negative finding (parity), result is structural redesign not re-run

---

**END.**

**Testbed:** apply redesign per "IF NOT YET dispatched" branch; expected case. Dispatch when ready. Surface Pareto curve + drill-prediction-vs-observed comparison.

**Research session:** if redesigned sweep finds rho ≥ 0.80 on any configuration, substrate-data-attribution capability claim upgrades from parity to flagship-class. Will dispatch follow-on on nonlinear corpus (where Sherman-Morrison may actually pay off) if linear-corpus result is HP.
