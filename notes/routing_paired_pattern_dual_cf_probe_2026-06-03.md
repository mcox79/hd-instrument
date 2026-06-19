# ROUTING — Paired-pattern dual counterfactual probe (drill-1 follow-up)

**From:** Research session
**To:** Testbed
**Date:** 2026-06-03
**Status:** USER AUTHORIZED 2026-06-03 ($0 CPU; ~2h wall; testbed dispatches when ready).

---

## What this experiment is (plain language)

The PP-49 HRC counterfactual experiments at N=4096 and N=16384 both produced pred_cos=1.000 saturation. Drill 1 today (`notes/research_drill_chained_retrieval_cf_saturation_2x_2026-06-03.md`) found this is **fixed-point absorbing** — the mathematically correct answer for leaf-start measurement of rank-1 substitution. It's the deletion-certificate killer-feature property (rank-1 deletion preserves all non-target queries exactly), not a mechanism failure.

To EMPIRICALLY confirm the algebraic story, the drill recommends measuring via **paired-pattern dual heteroassociative protocol**: change both stored matrix AND query simultaneously, then measure cos. If the algebraic explanation is correct, paired-pattern dual cos should drop to near-zero (= genuine counterfactual sensitivity is available when measured correctly).

This single experiment validates the algebra empirically and unlocks two product claims:
1. **Deletion certificate**: cos=1 for non-target queries → surgical edit, zero side effects (already algebraically grounded; this empirically validates the bound)
2. **Genuine cf sensitivity**: paired-pattern dual cos near zero → counterfactual measurement IS available when needed

---

## Experiment design

**Anchor name:** `substrate_paired_pattern_dual_cf_d4_v1_n4096_n16384`

**Resource:** local CPU
**Wall:** ~2 hours
**Cost:** $0

### Test protocol

For each (N, d) cell:
1. Build hierarchical chained retrieval at depth d with M stored patterns
2. Pick a target pattern (v_j, u_j); construct a substitution pair (v_j', u_j')
3. Compute T_d(x; W) where x = u_j (root-start query for original target)
4. Compute T_d(x'; W') where x' = u_j' AND W' = W - v_j u_j^T + v_j' u_j'^T
5. Measure cos(T_d(x; W), T_d(x'; W'))

This differs from the leaf-start protocol (which only substitutes W, not x). The paired-pattern dual asks: "if I stored v_j' instead of v_j AND queried with x_j' instead of x_j, would I get a different output?"

### Cells

- N ∈ {4096, 16384}
- d ∈ {4, 6, 8} (match prior HRC depths)
- 5 seeds per cell
- M = saturate near α_c (use existing PP-49 storage protocol)

6 cells × 5 seeds = 30 measurements. Compare against the leaf-start cos=1.000 baseline (already established at d=4,6,8 across N=4096,16384).

---

## Pre-registered bands (from drill 1)

- **HARD-PASS:** cos < 0.3 at d=4 AND d=6 AND d=8 across BOTH N=4096 and N=16384 (5-seed mean per cell). Confirms protocol-artifact hypothesis. Substrate IS genuinely cf-sensitive when measured with paired-pattern dual.
- **MIDDLE:** cos in [0.3, 0.8] at some cells (mixed result; suggests partial basin overlap or insufficient orthogonality of substituted patterns)
- **HARD-FAIL:** cos > 0.8 across ALL cells (saturation is geometry-driven at all measurement levels; counterfactual sensitivity fundamentally unavailable for this substrate class)

---

## Strategic outcomes

### IF HP

- Drill 1 algebraic story empirically confirmed
- PP-49 HRC HARD-FAIL should be reclassified at orchestrator level as **confirming evidence for deletion-certificate sub-capability** (not a mechanism failure)
- Substrate has TWO cf measurement protocols with DIFFERENT capability claims:
  - Leaf-start cos=1 → "surgical edit, zero side effects" (deletion-certificate killer feature)
  - Paired-pattern dual cos < 0.3 → "genuine cf sensitivity available when needed"
- ROME/MEMIT lit anchor strengthens the deletion-certificate product narrative

### IF MIDDLE

- Partial confirmation; some cells saturate, some don't — suggests substituted pattern orthogonality threshold or basin-overlap behavior
- Diagnostic follow-up: which (N, d) cells saturate vs not? Map the boundary

### IF HF

- Substrate counterfactual sensitivity is fundamentally unavailable regardless of measurement protocol
- Deletion-certificate claim weakens (substrate provides cos=1 for ANY protocol, including ones that should be genuinely different)
- PP-49 HRC mechanism gets parked
- Drill 1 algebraic story is REFUTED → re-research the chain-cf operator algebra

---

## Status-check request

Before dispatching, please verify:
- [ ] Has any paired-pattern dual probe already been run (no — this is new from drill 1 today)
- [ ] Is the existing PP-49 HRC harness reusable with the paired-pattern dual measurement substitution?

Expected: new experiment, existing harness adaptable (only the cos measurement protocol changes; W substitution + x substitution can use existing primitives).

---

## Dispatch instructions

CPU local runner. Wall <2h, $0. Status_log per `feedback_for_you_tab_primary_channel`: at batch launch + each-N-complete + final verdict synthesis.

---

## Discipline declarations

- Per `feedback_plain_language_experiment_tracking`: described by what it tests (paired-pattern dual cf measurement)
- Per `feedback_negative_results_2x_research`: this is the empirical follow-up to the drill that 2x-researched a negative finding (PP-49 HRC HF)
- Per `feedback_rehabilitation_after_rejection`: this is rescue path R2-adjacent (algebra-informed) + R4 (alternative cf measurement)
- Per `feedback_no_smoke_preframing_in_task_prompts`: HP/MID/HF bands tied to drill 1 algebraic prediction
- Per `feedback_testbed_progress_logging_and_restart`: per-cell partial JSON
- PROT-018: anchor name `substrate_paired_pattern_dual_cf_d4_v1_n4096_n16384` with multi-N suffix

---

**END.**

**Testbed:** dispatch when ready. Compare paired-pattern dual cos to leaf-start cos=1.000 baseline. Surface Pareto + verdict per drill 1 bands.

**Research session:** if HP, ship capability-implication note to orchestrator (PP-49 reclassification + deletion-certificate strengthening + parallel cap_map row candidate "genuine cf sensitivity").
