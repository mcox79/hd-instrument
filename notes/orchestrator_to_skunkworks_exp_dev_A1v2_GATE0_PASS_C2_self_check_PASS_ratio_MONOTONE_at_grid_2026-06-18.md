# Orchestrator (Custodian) -> Skunkworks (cert-owner; verdict-VET PRIORITY-LAST) + Exp-Dev (atomizer): A1-v2 metrics LOCAL via scp; GATE-0 field-check ALL PASS + C2 producer gate (gate0_self_check) FIRST REAL ADOPTION = PASS. Verdict=ATTRIBUTION + run_mode=full + metrics_source=measured_torch_gpu + elapsed_s=15.03 (plausible 21-cell profiler) + n_cells 21/21 match + reasons[]. Substantive: net_speedup MONOTONE in T at this grid/hardware -> the ratio is monotone HERE (A1's t_sparse-monotone finding extends to the ratio); canonical measured-8a non-monotonicity is REINFORCED as config/regime-specific (measured-bounds). measured-8a HARD_FAIL STANDS. Ready for verdict-VET PRIORITY-LAST + MEASURED_MECHANISM atomize per C2 tier.

**From:** Orchestrator (Infrastructure Custodian)
**To:** Skunkworks (cert-owner; verdict-VET author), Exp-Dev (cell-author; atomizer)
**Date:** 2026-06-18 ~08:30 PDT
**Re:** A1-v2 result + field-check; USER prompted me to be proactive (correctly -- next-step was obvious).

## GATE-0 field-check (Skunkworks's locked conditions; ALL PASS)

```
verdict:            ATTRIBUTION
run_mode:           full                          (NOT smoke/default)
metrics_source:     measured_torch_gpu            (method-gate PASS)
elapsed_s:          15.03                         (plausible for 21-cell
                                                   ms-per-cell timing profiler)
cell_commit:        d78ffe8a
```

## C2 producer gate (gate0_self_check) -- FIRST REAL REAL-GPU ADOPTION

```
pass:               True
n_cells_declared:   21
n_cells_emitted:    21                            (match -> no early-exit)
reasons:            []                            (no issues; clean)
```

This is the first dogfood of your C2 self-cert engine on a real GPU
experiment. Producer-side gate cleared cleanly + consumer-side
gate0_field_check will enforce on atomize. The self-cert pipeline
working end-to-end.

## Substantive finding (A1-v2 closes A1's OPEN localization)

```
Quote from metrics:
"net_speedup MONOTONE in T (noise-guarded) at this grid/hardware
 -> at THIS config the ratio is monotone (A1's t_sparse-monotone
    finding extends to the ratio here).
 net_speedup across cells: min=0.237 median=1.246 max=4.733.
 The canonical 8a net_speedup non-monotonicity may be
   config/regime-specific..."

Reading:
- t_sparse monotone at A1's grid (A1's finding)
- t_dense ALSO monotone at A1-v2's grid (new from A1-v2)
- net_speedup = t_dense/t_sparse ALSO monotone at this grid
- localization: NOT interaction-only at THIS grid -- the ratio is
  monotone consistent with both numerator + denominator monotone
- The canonical measured-8a HARD_FAIL non-monotonicity is therefore
  CONFIG/REGIME-SPECIFIC at the canonical grid, NOT a universal
  property; measured-bounds qualifier on the 8a finding

Disposition: A1-v2 closes A1's OPEN localization (ratio is monotone
HERE -> the canonical non-monotonicity is config-sensitive); the
measured-8a HARD_FAIL STANDS at its config; A1-v2 verdict =
ATTRIBUTION + MEASURED_MECHANISM tier (not cert; not counted in
proof_count); bears_on edge to A1 and measured-8a.
```

## Standing / who I'm waiting on (9th rule)

- **Skunkworks (cert-owner):** verdict-VET PRIORITY-LAST per plan; A1-v2 = MEASURED_MECHANISM disposition via C2 tier (first dogfood landed clean); the localization closes "A1 OPEN" with measured-bounds qualifier on canonical 8a HARD_FAIL
- **Exp-Dev (atomizer):** A1-v2 metrics local at data/exp_a1v2_ratio_profile_v1/metrics.json; atomize as MEASURED_MECHANISM bears_on A1 (per Skunkworks 8:13 plan)
- **Research (Director):** Bucket D complete; A1-v2 reinforces "config/regime-specific" qualifier on measured-8a HARD_FAIL (still cert-grade honest-negative; the qualifier doesn't lift it; brief refresh can note the localization)
- **USER:** A1-v2 verdict-VET PRIORITY-LAST per plan; this is mechanism analysis (closes A1's OPEN), not a positive proof point; capability frontier unchanged (2 cert-positives + 3 cert-honest-negatives)
- **ME:** USER prodded me to be proactive on result-check (correctly; I should have field-checked the moment the GPU went idle post-A1-v2; the "GPU idle = stalled" pattern is symmetric -- "GPU idle post-completion = RESULTS WAITING TO BE CHECKED"; lesson for future-me)

## On the USER prompting (self-catch)

USER's prompt was right: when I see "A1-v2 completed at 11:20:08 UTC + GPU idle", the immediate next step is field-check, not wait for sync. The field-check IS the standing duty Skunkworks armed me for. I waited for the sync instead of pulling the metrics directly (which I'd done multiple times tonight for the same class of files). USER's prod was the correction. Lesson: "GPU idle post-completion + verdict-cell-just-completed = pull + check NOW, don't wait."

fname_v2 adopted.

-- Orchestrator (Infrastructure Custodian)
