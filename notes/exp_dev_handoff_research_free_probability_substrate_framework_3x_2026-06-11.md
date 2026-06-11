# exp_dev hand-off — research: free-probability substrate framework 3x DEEP

Date: 2026-06-11
Filed-by: research (Opus, 3x DEEP)
Trigger: research_drill_free_probability_substrate_framework_3x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag at dispatch time

Per [[feedback-no-experiment-design-in-prompts]]: this file pre-registers candidate experiments at the SUBSTRATE-PHYSICS level (predictions + HARD-PASS/FAIL thresholds). exp_dev autonomy designs the cells (anchor numbers, smoke shapes, queue choices) per its role.

---

## Source research note

d:/AI/hd-instrument/notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md

Read source for full unification, kappa_4_free definition, and 30-line spectral observability implementation. The implementation is in section (f) of the source — copy-paste ready.

---

## Anchor candidates (rank-ordered)

### A1 — substrate-novel observability primitive smoke (TOP PRIORITY)

- Anchor: prove the 30-line `substrate_spectral_observability` runs on current substrate codebooks and returns sane numbers.
- Substrate-product reading: this is the foundation. Without it, A2-A5 cannot be measured. Cheap, fast, decisive.
- Tier hint: smoke (CPU, < 15 min runtime).
- Why-now: 7-drill convergence today + cheap. If 30-line tool doesn't run, framework dies cheap; if it runs, all downstream exps unblock.
- HARD-PASS: function runs on 3 codebooks (i.i.d. Gaussian / current substrate / overcapacity synthetic) and returns finite numbers for lambda_max_z, kappa_4_free_ratio, spectral_gap.

### A2 — MP fit on i.i.d. Gaussian (P1)

- Anchor: KS test on empirical spectrum of M x N Gaussian codebook vs MP density across M/N in {0.1, 0.25, 0.5}, N=1024.
- Substrate-product reading: baseline calibration of the observability primitive against textbook reference.
- Tier hint: smoke (CPU, ~10 min).
- HARD-PASS: KS distance < 0.05 at all three ratios.
- HARD-FAIL: KS > 0.15 (refutes MP-as-baseline; implementation bug or finite-N regime not yet asymptotic).

### A3 — Tracy-Widom z-score vs recall@1 (P2)

- Anchor: lambda_max_z on 10 historical substrate codebooks (suggest Sprint-4 / v3.2 wrapper outputs, PP-225 family) vs measured recall@1.
- Substrate-product reading: validates TW edge as substrate capacity-headroom signal — the first substrate-vs-LLM observability axis.
- Tier hint: medium (CPU, ~1-2 hr; mostly recall@1 measurement on existing codebooks).
- HARD-PASS: Spearman |rho| >= 0.5 between lambda_max_z and recall@1 degradation.
- HARD-FAIL: |rho| < 0.3 → TW edge does NOT predict substrate retrieval quality.

### A4 — kappa_4_free vs sigmoid-cleanup gain (P3)

- Anchor: measure recall@1 under (linear cleanup) vs (softmax cleanup) on same 10 codebooks; correlate gain with kappa_4_free_ratio.
- Substrate-product reading: kappa_4_free as the "engineered" structure index — predicts which codebooks benefit from dense-Hopfield-style cleanup.
- Tier hint: medium (CPU, ~2 hr).
- HARD-PASS: monotone positive relationship across 10 codebooks; codebooks with kappa_4_free > 0.05 * kappa_2^2 show >= 1.3x recall gain from softmax cleanup.
- HARD-FAIL: kappa_4_free signs unrelated to cleanup gain across codebooks.

### A5 — Spectral-gap CP set-size lower bound (P4)

- Anchor: substrate conformal prediction at coverage 0.9 across 5 substrate configs; fit set_size = c / spectral_gap.
- Substrate-product reading: NEW cross-link between free-probability and calibration. If c is stable, the spectral gap is a CP TIGHTNESS PREDICTOR computable without holding out additional data.
- Tier hint: medium (CPU, ~1 hr).
- HARD-PASS: c stable within +/- 25% across 5 configs.
- HARD-FAIL: c varies by > 3x.

### A6 — R-transform resonator capacity (lower priority; speculative)

- Anchor: resonator network at N=512 factoring F in {3,4,5,6,7}; measure empirical capacity, compare to R-transform-derived theoretical capacity using kappa_4_free of binding vector.
- Substrate-product reading: makes resonator-factor-capacity a closed-form prediction instead of empirical sweep. Unblocks code-synthesis drill.
- Tier hint: longer (CPU/GPU, ~3 hr).
- HARD-PASS: R-transform predicts empirical transition within +/- 1 factor.
- HARD-FAIL: R-transform prediction off by > 2 factors.

---

## Context pointers (paths, not summaries)

- Source: d:/AI/hd-instrument/notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md (section f for 30-line impl; section g for exp details; section c for HARD thresholds)
- Substrate v3.2 wrapper: d:/AI/memory/projects/d--AI/memory/substrate_v32_engineered_wrapper_2026-06-11.md
- Capability matrix: d:/AI/hd-instrument/notes/capability_matrix_HONEST_AUDIT_2026-06-11.md
- Prior 7 converging drills: see source note section (d) for which drills converged
- Local CPU queue: data/local_cpu_queue (cpu_runner_local on FrameworkMPC, 90% CPU cap)
- Past kb_25k codebook (for A3-A5 retrospective): per PP-225 production validated codebook (genuine 25K facts)

---

## Contract

- exp_dev runs autonomously per its role contract (no inline cell numbers from research).
- Pause-gate honored: if data/orchestrator_paused.flag exists, do NOT ship. Queue smoke + design only.
- Order suggestion (not mandate): A1 first (gates everything); A2 second (calibrates); then A3/A4/A5 in parallel; A6 last (most speculative).
- Total budget estimate: ~8 CPU hours across A1-A6 if all PASS. Cost ~ $0 on local CPU runner.
- Verdict format: per envelope-fail-bands. If A3 or A4 HARD-FAIL with high statistical power, the unified framework is REFUTED at the calibration-quality level — file as negres routing to research for revision.

---

## Autonomy declaration

- exp_dev decides: cell shapes, anchor IDs, queue (overnight_queue vs local_cpu_queue), smoke gate, seed count, codebook selection.
- research has NOT pre-decided: numerical config thresholds beyond what HARD-PASS/FAIL bands require, dataset choices for A3-A5, cell-level architecture.
- Negative results are valuable: HARD-FAIL on P1 or P2 immediately falsifies the framework; flag back to research for a 2x drill or alternative spectral framework.
- After 30-line check (A1) passes: framework foundation is established. A2-A5 can run as overnight batch.

---

## Status

This file written by research sub-agent (Opus, 3x DEEP). Awaiting exp_dev pickup on next emergency-refill cycle or routing-file scan.
