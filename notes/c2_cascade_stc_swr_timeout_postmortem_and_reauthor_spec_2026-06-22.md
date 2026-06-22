# c2_cascade_stc_swr_continual_v1 — timeout post-mortem + re-author spec

**Date:** 2026-06-22 (Director post-mortem; cell timed out on remote_cpu)
**Original cell:** `experiments/exp_c2_cascade_stc_swr_continual_v1.py` (commit 44a1cf26, 692 lines)
**Outcome:** HARNESS_TIMEOUT (status=failed, wall=9000s = 2.5hr, no metrics produced)
**Original Research drill estimate:** ~90min per drill #2 5x DEEPER deliverable

## Why it timed out

Per-cell computational cost compounds across loops:

| Dimension | Value | Cost contribution |
|---|---|---|
| N_DIM | 4096 | per-write outer-product is O(N²) = 16M ops |
| J_TASKS | 12 | per ingest cycle (≥ max K_EVALS=12) |
| M_PER_TASK | 1024 | ALPHA=3.0 × N_DIM / J = 12288 total writes per seed |
| Total writes/seed | ~12288 | 3× N_DIM (well into overload regime) |
| n_seeds | 3 | [7, 17, 23] |
| ARMS | 3 | NO_REPLAY / C1_BASELINE / CASCADE_STC_SWR |
| K_EVALS | 3 | [3, 6, 12] — recall measured at each |

Per-seed cost: 12 tasks × 1024 writes × N=4096² ops × cascade-depth-state-update + STC-tag + SWR-gated-replay-budget.

Estimated: ~50 min/arm/seed at this scale × 9 (3 arms × 3 seeds) = ~7.5hr (way over 9000s timeout).

Research drill's ~90min estimate likely assumed:
- Smaller N (1024 not 4096) OR
- Simpler cascade-state update (single depth vs 5-state Markov chain) OR
- No SWR-gated expanding-interval replay (just simple replay)

Cell-author followed the drill spec faithfully; the spec underestimated compute at the discriminating-regime scale.

## c2-v2 re-author spec

Goal: same mechanism + same discriminator-regime claim, but tractable wall ≤90min remote_cpu.

### Option A — Smaller N_DIM (cleanest reduction)

Change N_DIM from 4096 → **2048**. Per-write outer-product drops 4×. All else unchanged. Estimated wall: ~110min remote_cpu (still close to but within reasonable timeout).

Risk: at N=2048 the discriminator-regime (ALPHA=3.0 → M=6144 total writes per seed) may bear less mechanism signal than at N=4096 because the Hebbian floor is shallower. Mitigation: pre-reg HARD bands remain same; if at N=2048 mechanism fails to discriminate, that's also a signal.

### Option B — Smaller J_TASKS + K_EVALS

Change J_TASKS from 12 → **6**; K_EVALS from [3, 6, 12] → **[2, 4, 6]**. Halves the ingest loop count. Discriminator still fires at k=6 (well past c1 cliff at α=0.5).

Per-seed cost drops ~2.5× (less than 2× because cascade-state update doesn't scale linearly with J). Estimated wall: ~110min.

### Option C — Drop NO_REPLAY arm (forgetting-floor is well-established)

Forgetting-floor was the c1 finding — substrate forgets without replay. Re-measuring in c2 is redundant. Drop to 2 arms (C1_BASELINE vs CASCADE_STC_SWR). Saves 33% wall.

Combined with A or B: A+C ≈ 75min remote_cpu; B+C ≈ 75min remote_cpu.

### Option D — Longer timeout (12000s = 200min)

Simplest. No spec change. Just bump cell's `--timeout` arg at queue_add. Acknowledges drill's underestimate. ~2.5x the original timeout; uses ~3.5hr remote_cpu slot.

Risk: ties up remote_cpu queue slot for longer, blocking other CPU work (v2c is currently using the slot).

### Director's recommendation: **A + C combined**

- N_DIM=2048 (4× faster outer-product)
- Drop NO_REPLAY arm (2 arms instead of 3)
- All other config unchanged
- Wall estimate ~60-75min remote_cpu
- Discriminator still valid (C1 1:1 replay vs C2 cascade-STC-SWR is the load-bearing comparison; NO_REPLAY floor is well-established from c1)

## Pre-reg HARD bands (unchanged from original)

- HARD_PASS: C2 retention at k=6 ≥ 0.85 AND C2 > C1 retention by ≥0.20 at k=6 (mechanism-discriminating in the overload regime past c1's cliff)
- HARD_FAIL: C2 retention at k=6 < 0.40 OR C2 ≤ C1 (cascade-STC-SWR doesn't beat simple replay in overload regime)
- MIDDLE_BAND: in between

## Composes with

- Brain-drill #2 5x DEEPER drill spec
- c1 prior HARD_FAIL (the failure path c2 was designed to fix)
- r2 revival drill (same root pattern: original mechanism over-spec'd; cell-author refines)

## When to dispatch c2-v2

After v2c lands (~30-150min from now). r2c is on remote_cpu queue ahead; c2-v2 queues behind.

## What this cell does NOT need

- Cell-author re-design from scratch (use original 692-line cell; change 3 constants)
- Research re-drill (mechanism spec is sound; only the scale was over-estimated)
- New hdlab/ primitive (uses existing primitives)

— Director (post-mortem + spec; pre-design for next-cycle dispatch)
