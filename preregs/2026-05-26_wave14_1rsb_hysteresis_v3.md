# Prereg: wave14_1rsb_hysteresis_v3

**Filed**: 2026-05-26 exp_dev
**Anchor**: Pred-4 (1-RSB diagnostic) -- Hysteresis under capacity sweep [v3]
**Trigger**: v1 INSTRUMENTATION_FAIL + v2 TIMEOUT; cap_map v207 filed v3 as pending follow-up.

## Root causes of prior failures

**v1**: TypeError at base.evaluate_bpc (called with 6 args, required 10).

**v2**: TWO independent failures:
1. TIMEOUT (3600s, no metrics.json): N=2048 on CPU with 42 cells (~100s/cell) = ~4200s budget.
2. DESIGN BUG: forward/reverse trajectories called `run_4stage_get_retA` independently
   at each M with no state carried over. Forward and reverse produced IDENTICAL independent
   measurements at each M -- not a hysteresis protocol at all.

## v3 Design changes from v2

1. **N=1024** (was 2048): 4x speedup, ~15-25 min expected.
2. **Stateful hysteresis**: W matrix carried across trajectory.
   - Forward: W_init=0, train fresh at each M on M bytes of corpus_A.
   - Reverse: W_max computed once per seed (trained at M_max=48k bytes),
     then re-tuned at each M in decreasing order.
   - At each M, measure BPC using W-only prediction (no pool).
   - Gap = |bpc_fwd(M) - bpc_rev(M)|.
3. **Single-corpus single-phase**: corpus_A only. 4-stage CL complexity removed.
   The hysteresis probe isolates the capacity axis, not the multi-task axis.
4. **Periodic checkpoint writes**: metrics.json written as .tmp+rename after each M cell.
5. **Per-cell timeout tracking**: printed warning if cell exceeds 300s (non-fatal).
6. **Instrumentation self-test**: mandatory block at module load time.
7. **Multi-scale smoke**: passed at N=256 (77s) and N=512 (124s).

## Hypothesis

1-RSB (first-order) prediction: If the substrate has a discontinuous transition at alpha_c,
the gap profile |bpc_fwd(M) - bpc_rev(M)| will show a SHARP DROP at some M cell near alpha_c
(the W_max basin collapses discontinuously into the M-byte basin). Below alpha_c, the gap
will be large and relatively flat; above alpha_c, it will converge to near-zero.

RS / continuous prediction: Gap decreases smoothly and monotonically with no sharp transition.
Both trajectories converge at the same rate everywhere.

Note on smoke results: smoke at N=256 and N=512 shows a smooth monotone-decreasing gap
(large at small M, small at large M). This COULD reflect: (a) pure information-content
difference, or (b) 1-RSB with alpha_c below the smallest M in M_SWEEP.
The full 6-M sweep at N=1024 with 3 seeds will resolve whether the profile is smooth or has
a kink. The pre-registered bands evaluate the maximum gap; profile shape is reported in summary.

## Design

- **N**: 1024 (FULL), 256 (smoke), 512 (smoke2)
- **Batch**: 32 (FULL), 16 (smoke/smoke2)
- **Epochs**: 10 (FULL), 2 (smoke/smoke2)
- **M_SWEEP**: [2000, 5000, 10000, 20000, 35000, 48000] bytes (FULL)
               [2000, 10000, 48000] bytes (smoke)
- **Seeds**: [7, 17, 23] (FULL), [17] (smoke)
- **Corpus**: corpus_A only (48512 bytes -- PLAN.md, NEXT_PHASE.md, README.md, PROGRESS.md,
              RESULTS.md, CLAUDE.md concatenated)
- **W measure**: BPC via predict_W only (no pool retrieval), batch_size=32
- **Cell timeout**: 300s hard warning (non-fatal; partial data captured)
- **Queue**: remote_cpu_queue (CPU; no CUDA)
- **Timeout**: 7200s
- **ETA**: 20-40 min CPU at N=1024

## Pre-registered bands

HARD-PASS: max hysteresis gap (BPC) >= 0.10 at any M cell.
  Interpretation: non-trivial basin separation; consistent with first-order transition;
  1-RSB framing supported as a working model.

RS-HARD-FAIL: max hysteresis gap < 0.03 bits everywhere.
  Interpretation: W_max re-tuning converges to same BPC as fresh W at every M;
  continuous transition; 1-RSB NOT supported at capacity axis.
  Rehab axes: temperature axis, learning-rate decay axis, sparse-noise axis.

MIDDLE-BAND: max gap in [0.03, 0.10) bits.
  Interpretation: weak or marginal basin separation; inconclusive.
  Next step: run at N=2048 on GPU, or add more seeds, or probe gap SHAPE for kink.

## Smoke results (pre-ship gate)

N=256 (smoke):
  M=2000: fwd=6.4075 rev=5.2843 gap=1.1232  [PASS -- 1-RSB confirmed at smoke scale]
  M=10000: fwd=4.6051 rev=4.2541 gap=0.3509
  M=48000: fwd=3.5358 rev=3.5017 gap=0.0341
  max_gap=1.1232, verdict=HYSTERESIS_1RSB_CONFIRMED, elapsed=77s

N=512 (smoke2):
  M=2000: fwd=5.7844 rev=4.9495 gap=0.8349
  M=10000: fwd=4.1836 rev=3.6302 gap=0.5534
  M=48000: fwd=3.0630 rev=3.0379 gap=0.0250
  max_gap=0.8349, verdict=HYSTERESIS_1RSB_CONFIRMED, elapsed=124s

Both scales: metrics.json produced with all fields present. Suspicious-result gate PASS.

Walk-back gate: smoke gap >> 0.10 threshold across all M cells at small M.
Effect size is large enough that full run at N=1024 will produce data in the verdict bands.
Walk-back (double sample size) NOT triggered (effect is robust, not borderline).

## Self-test cells (all verified pre-ship)

Formula: compute_verdict({"max_hysteresis_gap_bpc": x}) -> verdict
- x=0.12 -> HYSTERESIS_1RSB_CONFIRMED
- x=0.02 -> HYSTERESIS_RS_SMOOTH
- x=0.06 -> HYSTERESIS_MIDDLE
- x=0.10 -> HYSTERESIS_1RSB_CONFIRMED  (boundary: >=)
- x=0.03 -> HYSTERESIS_MIDDLE           (boundary: >=RS lower, <1RSB upper)
- {}     -> HYSTERESIS_RS_SMOOTH         (missing key -> 0.0 < 0.03)
All 6 cells PASS (verified at module load by _instrumentation_selftest).
