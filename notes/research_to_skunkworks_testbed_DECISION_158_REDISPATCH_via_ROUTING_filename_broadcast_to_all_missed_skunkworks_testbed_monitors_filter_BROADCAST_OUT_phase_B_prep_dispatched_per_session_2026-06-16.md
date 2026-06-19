# Research (Director) -> Skunkworks + Testbed: DECISION 158 REDISPATCH via ROUTING filename. Original DECISION 158 PROCESS UPDATE at 10:54 was named research_to_all_*.md which routed via BROADCAST channel only. Your monitors filter ROUTING-only (NOT ROUTING|BROADCAST) per the 2026-06-15 monitor-death-prevention fix -- so you never received the original dispatch. Re-dispatching now via ROUTING filename. The 14th USER-LOCKED rule (NO STAND default at phase boundary) + your concrete Phase B PREP tasks are inside. USER caught the routing failure. New memory rule saved: Director multi-session dispatches MUST use per-session ROUTING filenames, NOT _to_all_ BROADCAST.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~11:08
**Re:** Original DECISION 158 BROADCAST failure to your sessions.

## Routing failure root cause

```
Original DECISION 158 dispatch at 10:54:
   Filename: research_to_all_DECISION_158_PROCESS_UPDATE_*.md
   Route: BROADCAST channel only (per event_bus.sh routing rules)
   
Skunkworks + Testbed monitors filter ROUTING-only (per 2026-06-15 fix preventing monitor 
death from BROADCAST volume; memory: feedback_skunkworks_run_cycle_check_every_cycle_*)
   Result: your monitors did NOT fire on the BROADCAST
   Evidence:
     skunkworks.log mtime 10:50 (4 min before my dispatch)
     testbed.log mtime 10:50
     exp_dev.log mtime 10:55 (after dispatch; Exp-Dev's monitor accepts BROADCAST)
     orchestrator.log mtime 10:57 (acked)

USER caught the missing delivery at ~10:58 ("they haven't picked up anything yet").

Director failure mode catalogued + memory rule saved (50th memory entry): 
   feedback_broadcast_vs_routing_dispatch_skunkworks_testbed_monitors_ROUTING_only_filter_USE_per_session_filenames_2026-06-16.md
```

## 14th USER-LOCKED rule (recap; in case you missed via BROADCAST)

```
NEW 14th RULE: at every phase boundary, Director dispatches concrete next-phase PREP to ALL 
sessions in the SAME Director-turn. "Stand" is NEVER the default.

Composes with: 12th (research-never-passive) + 13th (active state-check every 10-15 min) + 
9th (state-waiting-on-every-response).

File: C:\Users\marsh\.claude\projects\d--AI\memory\feedback_14th_rule_phase_boundary_dispatch_next_phase_prep_no_stand_default_USER_LOCKED_2026-06-16.md
```

## DECISION 158a -- Skunkworks PREP tasks (re-dispatched)

```
PREP TASK 1 -- Cardinality benchmark PRE-PASS methodology spec:
   Per DECISION 144 + Drill 1 (cardinality is binding-orthogonal across 4 VSA author clusters):
   Spec the pre-pass methodology for cardinality Phase B build:
     - What constitutes a "cardinality-required" task (vs cardinality-evadable retrieval)?
     - Three configurations to test (C1 basis-only, C2 +cardinality-primitive, C3 +internal-abstraction)
     - HARD-PASS / HARD-FAIL thresholds per Drill 1 pre-registered values
     - Sibling-probe-failure check (DECISION 148 47th instance type) applies to cardinality
     - Run_mode requirement (DECISION 149a tier discipline) applies to cardinality cells
     - Type-aware authoring discipline (DECISION 146) -- cardinality metric is AGGREGATE/RATIO type
   Estimated effort: 1-2 hours methodology spec
   Deliverable: skunkworks_phase_B_cardinality_prepass_methodology_*.md

PREP TASK 2 -- Ternary motif PRE-PASS methodology spec:
   Per Drill 1 + Exp-Dev's 162-motif mining (DECISION 142b addendum):
   Spec the pre-pass for ternary partial-symmetric motif Phase B build:
     - Pre-check role_filler coverage (gate-b/c from DECISION 142b memo)
     - Vector-encoding enforcement (NOT graph-walk; Exp-Dev's 11:05 PREP note already 
       flagged this for cardinality too -- generalize)
     - Frequency threshold (162 instances mined; minimum support for HARD-PASS?)
     - 4-gate ternary-motif protocol per Drill 1 + sibling-failure check
   Estimated effort: ~1 hour methodology spec
   Deliverable: skunkworks_phase_B_ternary_motif_prepass_methodology_*.md

PREP TASK 3 -- 447-smoke-cell catalog (substrate-product positioning asset):
   Per DECISION 152f / 149g extended:
   Catalog the 447 smoke-mode HARD_PASS cells:
     - SMOKE-EXPLORATORY-ONLY (never intended for load-bearing)
     - SMOKE-PRECURSOR-TO-FULL (full-mode rerun pending/possible)
     - SMOKE-INFLATED-AGAINST-FULL-MODE (verified that smoke result inflates vs full)
   Artifact: data/substrate_index/skunkworks_smoke_cell_catalog_2026-06-16.jsonl
   Estimated effort: ~3-4 hours scan + categorize
   Substrate-product positioning value: future pre-pass discipline checks incoming cells 
   against this catalog automatically (19th-rule perpetuity)

PREP TASK 4 -- PP-371 + PP-398 attribution close-out:
   Per 149g CLOSE: confirm attribution of the 0.967 (PP-371) + 1.0 (PP-398) to specific cells.
   Estimated effort: ~30 min cell-attribution scan
```

## DECISION 158c -- Testbed PREP tasks (re-dispatched)

```
PREP TASK 1 -- Phase B measurement infra scoping:
   Scope the CAP wiring + instance-class additions needed for Phase B:
     - Cardinality CAP atoms (CAP_cardinality_recall / CAP_quantifier_at_least_k / 
       CAP_quantifier_most)
     - Ternary motif CAP atoms (CAP_ternary_partial_symmetric_completion)
     - Internal-abstraction-discovery CAP atoms (CAP_substrate_internal_abstraction)
   For each: instance-class spec + relation graph wiring + 4-gate compatibility
   Estimated effort: ~2-3 hours scoping
   Deliverable: testbed_phase_B_CAP_wiring_scoping_2026-06-16.md
   
PREP TASK 2 -- Phase B kappa methodology design:
   Per DECISION 156 + bilateral kappa external anchor (2-cat=1.000 / 3-cat=0.572):
   Design the Phase B kappa methodology:
     - Per-task bilateral agreement measurement (substrate-self vs independent rater)
     - Same-family residual continues to apply; external rater questions queued
     - Sealed-sample protocol per DECISION 115b/131b precedent
   Estimated effort: ~1 hour methodology
   
PREP TASK 3 -- Periodic substrate sanity (continues from Phase A; standing duty):
   Substrate state check every ~25-30 min (atoms/relations/axiom_term/modules/self-model)
   No urgency; non-blocking
   
PREP TASK 4 -- Element-layer scoping memo refresh:
   Foundation-lane Track 2 element-layer scoping memo at a215e5ed: refresh per Drill 3 
   findings (specified-by-construction vs learned-against-external-loss; substrate-internal 
   3-line definition).
   Estimated effort: ~1 hour refresh
```

## Process update reconfirmed for this dispatch + future

- Multi-session dispatches use per-session ROUTING filename (NOT _to_all_)
- Exp-Dev's 11:05 PREP note (cardinality existing-primitive is GRAPH_WALK class; vector-encoding 
  enforcement) proves their monitor received the original; they're already executing PREP
- Orchestrator acked at 10:57 (their monitor accepts BROADCAST)
- This dispatch is to Skunkworks + Testbed specifically via ROUTING filename

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal PREP
- 18th rule: bounded concrete PREP tasks
- 19th rule: 54 instance types empirical
- 22nd rule: Lakatos progressive
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

---

**Skunkworks (Auditor):** DECISION 158a 4 PREP tasks (~6-8h) -- cardinality + ternary motif 
pre-pass methodologies + 447-smoke-cell catalog + PP-371/PP-398 attribution close-out. Begin 
at your bandwidth. Re-dispatched via ROUTING filename so your monitor fires.

**Testbed (Integrator):** DECISION 158c 4 PREP tasks (~6-7h) -- Phase B CAP wiring scoping + 
Phase B kappa methodology + periodic sanity + element-layer scoping refresh. Begin at your 
bandwidth. Re-dispatched via ROUTING filename so your monitor fires.

**USER:** routing-failure root-cause diagnosed (_to_all_ -> BROADCAST; Skunkworks + Testbed 
ROUTING-only filter); re-dispatched via per-session ROUTING filename; new memory rule saved. 
Exp-Dev already started PREP work proving their monitor received the original.

Tag: DECISION_158_REDISPATCH_via_ROUTING_filename_skunkworks_testbed_monitors_ROUTING_only_filter_BROADCAST_missed_phase_B_prep_dispatched_per_session_filename_memory_rule_saved -- Research (Director)
