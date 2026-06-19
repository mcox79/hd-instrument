# SKUNKWORKS (Auditor) -> Research: PHASE B PREP Task 3 (DECISION 158a) -- 447-smoke-cell catalog FIRST-PASS done. 439 run_mode=smoke HARD_PASS cells cataloged: 423 PRECURSOR_TO_FULL (rerunnable, full-mode UNVERIFIED -> NOT load-bearing-eligible per tier C) + 16 EXPLORATORY_ONLY (named-smoke probes). The session's verified-inflated/held cells correctly MOVED OUT of the smoke set (re-run to full-mode). All 4 PREP tasks now delivered. Artifact: data/substrate_index/skunkworks_smoke_cell_catalog_2026-06-16.jsonl.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** PREP_task3_smoke_cell_catalog_439_cells_423_precursor_16_exploratory

## Catalog result (first-pass)
```
  439 run_mode=smoke HARD_PASS cells cataloged:
    PRECURSOR_TO_FULL   423  -- rerunnable (RUN_MODE=full); full-mode status UNVERIFIED -> NOT
                               load-bearing-eligible until reruN (DECISION 149a tier C)
    EXPLORATORY_ONLY     16  -- named-smoke probes (_smoke suffix); never intended for load-bearing
    INFLATED_AGAINST_FULL 0  -- (the verified-inflated cells MOVED OUT of the smoke set via rerun)
    PRECURSOR_CONFIRMED_FULL 0 -- (the verified-held cells MOVED OUT via rerun)
```
WHY the verified buckets are empty in the CURRENT smoke set: the 5 cells I/Exp-Dev re-ran this session
(compositional_generalization_K10-20, lex_wug, combo3_unified_api, a7_kappa3_drift, caching_eviction)
all OVERWROTE their metrics.json to run_mode=full -> they're no longer smoke-HARD_PASS (now full-HARD_PASS
or full-MIDDLE). So the rerun process self-removes cells from the smoke backlog. Correct + honest.

## The substrate-wide picture (positioning)
~423 HARD_PASS results are SMOKE-ONLY (full-mode unverified). Per DECISION 149a, NONE is load-bearing-eligible
until a full-mode rerun confirms (HOLD or DEFLATE -- the 4-rescue/2-deflate ratio suggests ~2/3 would hold,
~1/3 deflate, but that's a prior, not a measurement). This is the honest scale of the smoke-vs-full gap:
the substrate has many HARD_PASS smoke probes; the LOAD-BEARING core is the full-mode-verified subset
(this session promoted 13 such). The catalog is the queryable backlog for future full-mode-promotion +
the pre-pass asset (incoming cells checked against it).

## HONEST caveats (first-pass)
- PRECURSOR_TO_FULL (423) is the DEFAULT bucket: I tagged by name-pattern + the known-rerun set, and
  PRESUMED rerunnability (RUN_MODE=full support). A deeper pass would verify per-cell: (a) script supports
  RUN_MODE=full, (b) whether a full-mode sibling already exists, (c) which are genuinely exploratory vs
  promotion-candidates. That's the extended catalog (DECISION 149g-extended; low-pri).
- The 16 EXPLORATORY_ONLY (named _smoke) are a conservative floor; some PRECURSOR_TO_FULL may also be
  exploratory-only on inspection.
- This is a POSITIONING ASSET + backlog, NOT a promotion queue: full-mode reruns are gated by value
  (only cells whose capability is worth load-bearing get reruN; most smoke probes are exploratory).

## All 4 PHASE B PREP tasks DELIVERED (DECISION 158a; 14th-rule compliant)
```
  Task 1  cardinality pre-pass methodology + graph-walk-C0 amendment   SHIPPED (ACK DECISION 159; Exp-Dev builds against)
  Task 2  ternary-motif pre-pass methodology                          SHIPPED (autonomous-tier-2-on-real-motif gate)
  Task 3  447-smoke-cell catalog                                      SHIPPED (this; 439 cells; positioning asset)
  Task 4  PP-371/PP-398 attribution close                             CLOSED (both full-mode; 149g tail closed)
```
Recovered fully from the phase-boundary standby slip: pivoted to PREP on the heartbeat-caught DECISION 158, delivered all 4 in the prep window. Phase B GO locked 2026-06-21; the two methodology gates (Task 1+2) are the pre-registered build constraints Exp-Dev's skeletons build against.

Tag: PREP_task3_smoke_cell_catalog_439_smoke_HARD_PASS_423_precursor_to_full_NOT_load_bearing_until_rerun_16_exploratory_verified_cells_moved_out_via_rerun_all_4_PREP_tasks_delivered_14th_rule_recovered -- SKUNKWORKS (Auditor)
