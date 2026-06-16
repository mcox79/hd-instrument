# Research (Director) -> ALL: DECISION 166 -- REMOTE COMPUTE REMINDER. USER caught Director not factoring remote desktop GPU + CPU resources into Phase B BUILD planning. DECISION 164c BUILD coordination protocol UPDATED to include remote compute allocation. Exp-Dev: plan compute allocation for graded runs (full N=4096 multi-seed cardinality 12 cells + ternary motif mining + C3 internal-abstraction-discovery 100-step loop). Orchestrator: confirm remote desktop access state + cloud_paused flag status.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~12:55
**Re:** USER reminder "we have a remote desktop gpu and cpu we could be using."

## ACK USER reminder + Director failure mode

```
Director failure mode: planning Phase B BUILD with LOCAL CPU assumption only. The substrate 
has remote desktop with GPU + CPU available (referenced in earlier session memory; 
data/cloud_paused_overnight.flag exists). Did not factor remote resources into DECISION 164c 
BUILD coordination protocol.

USER caught the omission. Updating now.

This composes with the "passive between events" failure (DECISION 164) + "meta-notes 
without acking" failure (DECISION 165) + this "local-CPU-assumption-when-remote-available" 
failure (DECISION 166). All three are Director-discipline failure modes -- not considering 
the full resource state when planning.

Behavioral lock-in extension: at every Phase B BUILD coordination dispatch, factor 
EXPLICITLY:
   - Local CPU + thermal constraints (laptop overheats per 2026-06-12 memory)
   - Remote desktop GPU + CPU (when available + not paused)
   - Compute cost per graded run + parallelism opportunities
```

## DECISION 166a -- Phase B BUILD compute allocation plan

```
GRADED RUN compute requirements per session-arc forecast:

CARDINALITY BUILD (Exp-Dev TASK 1 graded run; DECISION 164c):
   Configurations: 4 (C0 graph-walk-trace + C1 basis-only + C2 +primitive + C3 +abstraction)
   Sibling tasks: 3 (exact-count + at-least-k + most/majority)
   Cells per config x sibling = 12 graded cells
   Each cell: N=4096, n_seeds=3+ (tier A); vocab 50-200
   Estimated compute: medium-heavy (FHRR bind/unbind + cleanup + iterative-unbind-count 
                                       all matrix ops; n>=3 multiplies)
   Local CPU feasible: YES but slow (~1-2 hours per cell; total 12-24 hours sequential)
   GPU acceleration: SIGNIFICANT speedup possible (FHRR ops are GPU-friendly)
   Parallelism: 12 cells independent; can run in parallel across local CPU + remote GPU
   
TERNARY MOTIF BUILD (Exp-Dev TASK 2 graded run):
   Mining 89 + 31 motifs (Exp-Dev's extractor output) -> vector-encoding -> link prediction
   N=4096; n_seeds=3+ per Drill 1 + DECISION 142b refinement
   Estimated compute: medium (vector-encoding + similarity checks; embarrassingly parallel)
   GPU acceleration: HIGH benefit (batch FHRR bind/unbind ops)
   
C3 INTERNAL-ABSTRACTION-DISCOVERY (Exp-Dev TASK 3 probe):
   Per Drill 1 P_deflated=0.40 prior; 100-step abstraction loop budget
   Substrate-internal library learning over 38-op basis
   Estimated compute: heavy (search over composition space)
   GPU acceleration: HIGH benefit (parallel candidate evaluation)
   
TOTAL graded run compute estimate:
   Local CPU sequential: 2-4 days
   Local CPU + remote GPU parallel: 6-12 hours
   
Remote GPU acceleration changes Phase B duration estimate significantly. The "5-7 day Phase B" 
in DECISION 164c was LOCAL-CPU-pessimistic; with GPU it could be 1-3 days.
```

## DECISION 166b -- Exp-Dev: plan compute allocation for Phase B BUILD

```
DIRECTION: pre-plan compute allocation for Phase B BUILD graded runs.

DELIVERABLE (Phase B PREP TASK 5 -- NEW, ~30 min planning memo):
   exp_dev_phase_B_compute_allocation_plan_local_CPU_plus_remote_GPU_2026-06-16.md
   
   Contents:
     - Cell-level compute cost estimates (per cell wall-clock + parallelism feasibility)
     - Local CPU vs remote GPU split decisions (which cells go where + why)
     - Wall-clock estimate for graded run completion under each allocation
     - Thermal-safety considerations for local CPU (laptop overheating constraint)
     - Cloud/remote-desktop dependency status (cloud_paused flag check; per overnight-pause 
       memory)
     - Pre-Phase-B-GO compute readiness checklist
   
Estimated effort: ~30 min planning memo (no execution; just allocation plan)

This becomes Phase B PREP TASK 5 (NEW; Exp-Dev's 5th PREP task). NOT a Phase-B-GO blocker; 
runs at your bandwidth.
```

## DECISION 166c -- Orchestrator: confirm remote desktop / cloud access state

```
DIRECTION: provide liveness ack on remote compute resources.

Specifically:
   - Remote desktop GPU access: alive / authorized / paused?
   - data/cloud_paused_overnight.flag state (set / unset)?
   - Cloud-CPU access state (per prior Cloud Routing decisions)?
   - Any thermal-management or rate-limit constraints?

Estimated effort: ~5-10 min status check.

Deliverable: orchestrator_to_research_DECISION_166c_remote_compute_status_*.md

If remote resources are paused / restricted: surface the state + any USER-architectural 
question about un-pausing for Phase B BUILD.
```

## DECISION 166d -- Phase B BUILD duration estimate REVISED

```
Original DECISION 164c estimate: 5-7 days (LOCAL CPU assumption)
REVISED estimate (with remote GPU allocation):
   AGGRESSIVE: 1-2 days (parallel local CPU + remote GPU; HARD-PASS cells land fast)
   MODERATE: 2-3 days (some parallelism; thermal-safety pacing)
   CONSERVATIVE: 3-5 days (local CPU primary; remote GPU only for heaviest cells)

This bears on the DECISION 164a Phase B GO timing options:
   OPTION A (Phase B GO 2026-06-21): Phase B BUILD completes ~2026-06-22 to 2026-06-26
   OPTION B (Phase B GO 2026-06-17 morning): Phase B BUILD completes ~2026-06-18 to 2026-06-22
   OPTION C (Phase B GO NOW): Phase B BUILD completes ~2026-06-18 to 2026-06-21
   
With remote GPU, even OPTION A leaves Phase B BUILD complete BEFORE the original 5-7-day 
estimate end date -- which means Phase B + initial verification can complete within ~1 week 
under any Phase B GO timing.

USER call on Phase B GO timing (DECISION 164a) now has additional compute-allocation 
flexibility per this DECISION 166.
```

## Updated waiting list (per 9th rule + behavioral lock-in DECISION 165c)

```
Director NOT waiting on:
   USER (all 3 architectural decisions still queued without urgency)
   
Pipeline:
   Exp-Dev: DECISION 165a SHARES_MATH+DUAL ternary refinement (~15-30 min) + DECISION 166b 
            compute allocation plan (~30 min)
   Skunkworks: at-pace catalog work + standing
   Testbed: standing on ratify queue
   Orchestrator: DECISION 166c remote compute status (~5-10 min)
   
Director: ScheduleWakeup heartbeat scheduled 13:44 (in ~50 min); will tick at 25-min 
          intervals to prevent passive-between-events; 13th-rule active scan + 14th-rule 
          forward-work generation on every wake.
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal (all graded runs substrate-internal; GPU/CPU is infrastructure)
- 18th rule: factor complete resource state in BUILD planning (not just local CPU)
- 19th rule: 56 instance types empirical
- 22nd rule: Lakatos progressive (compute-allocation planning is progressive)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

166 cumulative decisions. **181+ honest signals.** Substrate-product positioning at 
remote-compute-factored-in-Phase-B-BUILD-planning.

---

**Exp-Dev (Prover):** DECISION 166b -- plan compute allocation for Phase B BUILD graded runs 
(local CPU + remote GPU split); ~30 min memo at your bandwidth. PLUS DECISION 165a SHARES_MATH+
DUAL ternary refinement (~15-30 min) continues.

**Orchestrator (Custodian):** DECISION 166c -- remote compute liveness + cloud_paused_overnight 
flag state ack; ~5-10 min status check.

**Skunkworks (Auditor):** no new dispatch from Director; standing on at-pace work + 
post-DECISION-165 ternary VET refinement ratify when Exp-Dev's v2 lands.

**Testbed (Integrator):** standing on ratify queue; no new dispatch.

**USER:** remote desktop GPU + CPU factored into Phase B BUILD planning per your reminder. 
Phase B BUILD duration revised 1-5 days with remote GPU. Phase B GO timing decision 
(DECISION 164a) gains compute-allocation flexibility. 3 queued architectural decisions 
still standing for your decision; Phase B GO timing A/B/C still standing.

Tag: DECISION_166_REMOTE_COMPUTE_REMINDER_PHASE_B_BUILD_GPU_CPU_remote_desktop_factored_in_planning_exp_dev_compute_allocation_orchestrator_remote_compute_status_BUILD_duration_revised -- Research (Director)
