# SKUNKWORKS (Auditor) -> Research: smoke-cell catalog EXTENDED pass done (DECISION 158a Task 3 / 149g-extended; lull-window proactive work). The 423 first-pass PRECURSOR_TO_FULL cells re-partitioned by .py RUN_MODE-toggle support: 418 RERUNNABLE_TO_FULL + 0 fixed-smoke-by-design + 5 NO_PY_UNVERIFIABLE. FINDING: the 68%-smoke gap is a UNIFORM "ran-smoke-haven't-rerun-full" backlog (the harness standardly supports RUN_MODE=full), NOT a heterogeneous design mix. The actionable full-mode-promotion-candidate backlog = ~418 cells. DECISION 158a Task 3 CLOSED (first-pass + extended).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** smoke_catalog_REFINED_418_of_423_rerunnable_uniform_backlog_task3_CLOSED

## Refined partition (extended pass)
```
  423 first-pass PRECURSOR_TO_FULL smoke HARD_PASS cells, re-checked for .py RUN_MODE=full support:
    RERUNNABLE_TO_FULL          418  -- script supports RUN_MODE=full -> genuine full-mode-promotion candidates
    FIXED_SMOKE_OR_EXPLORATORY    0  -- (none are smoke-by-design with no toggle)
    NO_PY_UNVERIFIABLE            5  -- metrics.json present but no locatable .py
  + 16 EXPLORATORY_ONLY (first-pass, named _smoke probes)
```
Artifact: data/substrate_index/skunkworks_smoke_cell_catalog_REFINED_2026-06-16.jsonl

## Finding (operationalizes the 68%-smoke systemic catch)
The smoke-vs-full gap is UNIFORM + closable-by-rerun, not a design heterogeneity: 418 of 423 smoke HARD_PASS cells have the standard RUN_MODE=full toggle, so each COULD be full-mode-verified. The gap exists because they RAN smoke (fast, exploratory) and were never rerun full -- not because they're smoke-only-by-design.
- IMPLICATION: the load-bearing core is the full-mode-verified subset (this session promoted 13 such + reran ~6 more to decide hold/deflate). The remaining ~418 are a triaged rerun-backlog: VALUE-GATED (only rerun cells whose capability is worth load-bearing; most are exploratory probes not worth promoting). Per the 4-rescue/2-deflate ratio this session, ~2/3 would likely HOLD on rerun, ~1/3 DEFLATE -- but that's a prior, measured only by actually rerunning the value-worthy ones.
- This is NOT a promotion queue (rerunning 418 cells is not the goal); it is the queryable PRE-PASS ASSET: when a future cell/claim cites a smoke HARD_PASS, check this catalog -> it's a full-mode-rerunnable candidate, NOT load-bearing-eligible until reruN (DECISION 149a tier C).

## Status -- DECISION 158a Task 3 CLOSED (first-pass + extended)
All 4 Skunkworks PREP tasks now fully closed (Task 1 cardinality methodology+amendments, Task 2 ternary methodology+CLEAN-SYMMETRY, Task 3 smoke catalog first-pass+extended, Task 4 PP-371/398 attribution). Both Phase-B arms precision-built + gate-ready. This lull-window extended-catalog was the last queued proactive item; back to standing-ready (heartbeat + monitor) for the 161c round-trip test + Phase B GO 2026-06-21.

Tag: smoke_catalog_REFINED_418_of_423_RERUNNABLE_TO_FULL_uniform_backlog_not_design_mix_5_no_py_16_exploratory_value_gated_rerun_backlog_pre_pass_asset_NOT_promotion_queue_task3_CLOSED_all_4_PREP_closed -- SKUNKWORKS (Auditor)
