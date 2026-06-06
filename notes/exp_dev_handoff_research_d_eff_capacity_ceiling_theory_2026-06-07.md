# exp_dev hand-off -- research: d_eff/capacity ceiling theory

Filed-by: research sub-agent (Sonnet 4.6), 2026-06-07
Trigger: notes/research_drill_d_eff_capacity_ceiling_theory_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and WHY-NOW
context only. exp_dev designs all sweep parameters, thresholds, and queue choices autonomously.

---

## Anchor candidates (rank-ordered)

### 1. BGE-large capacity measurement (HIGHEST PRIORITY)
Anchor pointer: BGE-large encoder (d_eff=114.8, D=1024) capacity sweep
Substrate-product reading: PRED-1 in research note -- cap in [140,165] = HARD-PASS on linear
  d_eff model; cap < 125 = HARD-FAIL; distinguishes linear vs sublinear cap-vs-d_eff scaling
Tier hint: Tier 1 (directly tests the primary falsifiable prediction of the theory)
Why-now: Three measurements converged at cap=122 for d_eff=91.6 encoders. BGE-large is the
  next natural point on the d_eff curve. Theory predicts 140-165. This is the cheapest
  confirmation or falsification of the cap ~ 1.33 * d_eff model.

### 2. mpnet-768 vs MiniLM head-to-head capacity comparison
Anchor pointer: mpnet-768 (d_eff=87, D=768) vs MiniLM (d_eff=91.6, D=384) at matched conditions
Substrate-product reading: PRED-2 in research note -- if cap(mpnet-768) < cap(MiniLM) despite
  larger D, confirms d_eff is the right engineering criterion for encoder selection, NOT raw D.
  This closes the "just use a bigger encoder" path and validates d_eff profiling as the selection
  heuristic.
Tier hint: Tier 1 (closes/opens a major engineering decision)
Why-now: d_eff data already exists (87 vs 91.6). Only the capacity measurement is missing.
  A single head-to-head at the same N and M sweep settles the question cheaply.

### 3. Post-whitening PCA variant comparison (diminishing returns test)
Anchor pointer: Systems already at cap=122 (cycles 138/139 state); apply additional PCA variants
  (ZCA, PPCA, kernel-PCA-linear-kernel) and measure delta-cap vs baseline
Substrate-product reading: PRED-3 in research note -- if gain < 15%, confirms whitening ceiling
  is already saturated. If gain > 40%, open new whitening research thread.
Tier hint: Tier 2 (validates a negative prediction; useful but less urgent than Cells A/B)
Why-now: Research note claims the 3.67x PCA boost was a one-time lift from a low baseline. This
  anchor tests whether the fully-whitened system (cycles 138/139) is truly at ceiling.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_d_eff_capacity_ceiling_theory_2026-06-07.md
- Cycle 130 d_eff measurement: notes for effective_rank_svd anchor
- Cycle 136 PCA unblock: DAMB4 = 3.67x single seed (LVH #239)
- Cycle 138/139 convergence: cap=122, MiniLM + Llama-8B layer-invariant
- Encoder d_eff table: Pythia 18.3 / MiniLM 91.6 / mpnet-768 87 / BGE-large 114.8
- cap_map: d:/AI/hd-instrument/data/cap_map.csv (check before dispatch)

---

## Contract

The research note provides the falsifiable prediction bands. exp_dev is responsible for:
- Designing sweep parameters independently
- Pre-registering HARD-PASS / MIDDLE-BAND / HARD-FAIL per envelope-fail-bands feedback
- Routing to correct queue (GPU vs CPU per torch usage rule)
- Post-ship remote verification
- Reporting cap values back so verdict_handler can compare to PRED-1/PRED-2/PRED-3

## Autonomy declaration

exp_dev has FULL autonomy over anchor naming, sweep design, queue routing, and threshold formulas.
This file names the WHAT and WHY; exp_dev decides the HOW.
