# Exp-Dev (Prover): Phase B COMPUTE ALLOCATION PLAN (DECISION 166b / PREP TASK 5). Grounded in MEASURED timing (smoke 0.86s; C0 microbench 261s/cell). KEY CORRECTION (verify-before-asserting): the primary arms (cardinality + ternary) are MINUTES on local CPU, NOT the 1-2hr/cell / 2-4 day estimate -- C0 graph-walk-trace is the only heavy component (261s @ N=4096) and the sole GPU-acceleration candidate; C3 abstraction-discovery is the genuine heavy arm (not yet built). 188th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** phase_B_compute_allocation_plan_local_CPU_plus_remote_GPU

## MEASURED timing (grounds the plan; not analytical guesswork)
```
  cardinality skeleton smoke (N=1024, 2 seeds, all configs+siblings+single-role+capacity): 0.86s
  C0 graph-walk-trace microbench (1500 calls = 1 N=4096 cell, multi-role): 261s (4.4 min)
  C2 cleanup microbench (1500 calls, N=4096): 0.14s
```

## Cell-level compute estimates (CORRECTS the DECISION 166a 1-2hr/cell estimate by ~100x)
```
  CARDINALITY full graded run (4 configs x 3 siblings; N=1024/2048/4096; n=5):
     C0 (graph-walk-trace, NxN matrix/scene) DOMINATES: N=4096=261s + N=2048~65s + N=1024~16s = ~342s (~5.7 min)
     C1 (norm) + C2 (cleanup) + single-role + capacity: trivial (<10s total; C2=0.14s/cell)
     => CARDINALITY full run ~ 6-7 MINUTES on local CPU (NOT 12-24 hours).
  TERNARY graded run (mining + completion over math-scoped 20 motifs + 89 ref; N=4096 n=5):
     mining <1s; vector-encoding + completion = light vector ops, embarrassingly parallel ~ MINUTES.
  C3 INTERNAL-ABSTRACTION-DISCOVERY (100-step composition search; NOT YET BUILT):
     the ONLY genuinely compute-heavy arm; cost depends on search breadth; GPU-beneficial.
```

## Local CPU vs remote GPU split (recommendation)
```
  PRIMARY ARMS (cardinality + ternary) -> LOCAL CPU, in-session (direct .venv python, as for smoke):
     - fast (~10 min combined), thermal-safe at minutes-scale
     - SINGLE BACKEND (CPU float64) -> satisfies Skunkworks's "one-backend-per-sibling-set" TRIVIALLY
       + NO near-threshold backend-flip risk (no GPU-CPU delta when all-CPU) -> clean C2-vs-C1 margins
     - local cpu_runner_local being stale (Orchestrator finding 1) is IRRELEVANT: I run in-session directly,
       not via the scheduled runner.
  C0 @ N=4096 (261s): the one GPU-acceleration candidate within cardinality (NxN matmul ~ seconds on GPU);
     but 261s on CPU is acceptable -> GPU OPTIONAL for the primary arms.
  C3 ABSTRACTION-DISCOVERY -> REMOTE GPU (heavy search; GPU-beneficial) when built. Record backend; apply
     Skunkworks's near-threshold cross-backend check there (the only place GPU is used).
```

## Compute-backend provenance gate (Skunkworks, folded)
```
  RECORD per graded cell: compute_backend {CPU|GPU} + dtype + device, alongside run_mode + N + n_seeds.
  PRIMARY arms = CPU float64 (single backend -> no cross-check needed; margins are backend-clean).
  NEAR-THRESHOLD cross-check applies ONLY if a cell runs GPU AND its metric is within ~1e-3 of a bar
     -> re-run that cell on the other backend; verdict stands only if it agrees. (Relevant to C3 on GPU.)
  Prefer one backend per sibling-set -> running all of cardinality+ternary on CPU satisfies this by default.
```

## Thermal safety (laptop overheating constraint; 2026-06-12)
The 2026-06-12 overheating was N concurrent heavy WATCHER LOOPS, not short numpy runs. Minutes-scale numpy
(cardinality ~6-7 min) is thermal-safe. Guidance: run primary cells SEQUENTIALLY or 2-3 parallel (not 12
concurrent) to stay thermal-safe; the heaviest single step (C0 @ N=4096, 261s) is one BLAS-bound stretch.

## Cloud / remote dependency status
```
  data/cloud_paused*.flag : NOT PRESENT (my check) -- consistent with Orchestrator 166c (no pauses).
  Remote GPU/CPU + ssh: AVAILABLE + queues clear (Orchestrator 166c, 184th signal). Authoritative = Orchestrator.
  hd_remote_state_emitter MISSING (Orchestrator finding 2): no Phase-B BUILD dependency -> non-blocking.
```

## Pre-Phase-B-GO compute READINESS checklist
```
  [x] full-mode config verified (SEEDS=5; N_LIST=[1024,2048,4096]; vector-encoding gate fires; readouts wired)
  [x] ternary extractor math-corpus-scope gate (canonical HARD claim = math-scoped MOTIF-B=20)
  [x] remote compute available (Orchestrator 166c); backend-provenance recording planned
  [ ] CARDINALITY skeleton: WIRE compute_verdict() -- the graded HARD-PASS/MIDDLE/HARD-FAIL threshold logic
      per the pre-registered PREREG bands (exact-count RMSE; quantifier accuracy + margin; ESCAPE vs C0;
      capacity-envelope). The sanity harness does directional checks only; the graded verdict fn is the ONE
      code gap. (Pre-register the bands in code = Lakatos no-ex-post-adjustment.) ~30 min at GO.
  [ ] C3 abstraction-discovery probe: BUILD from spec (the GPU-heavy arm) -- the largest remaining build.
```

## Bottom line for GO timing (DECISION 164a)
Primary arms (cardinality + ternary) complete in ~10-15 MIN local CPU after GO -- NOT days. The "5-7 day"
/ "1-3 day with GPU" Phase-B estimates were dominated by the (unbuilt) C3 abstraction-discovery arm; the
PRIMARY cardinality + ternary verdicts land within MINUTES of GO. Remote GPU is OPTIONAL for primary arms,
RECOMMENDED for C3. This further de-risks Option B (or C) -- the primary HARD-PASS/FAIL signal is fast.

NOT a Phase-B-GO blocker; build gated to GO (Option B 2026-06-17 morning unless USER pulls earlier).
-- EXP-DEV (Prover)
