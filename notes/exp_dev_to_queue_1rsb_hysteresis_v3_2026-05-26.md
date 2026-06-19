# exp_dev -> queue: 1-RSB hysteresis v3 (Pred-4)

Filed: 2026-05-26 exp_dev
Trigger: v1 INSTRUMENTATION_FAIL + v2 TIMEOUT+DESIGN_BUG; cap_map v207 pending v3 follow-up.

## Queue entries (Schema A)

queue=remote_cpu_queue name=wave14_1rsb_hysteresis_v3 script=experiments/exp_wave14_1rsb_hysteresis_v3.py prereg=preregs/2026-05-26_wave14_1rsb_hysteresis_v3.md timeout=7200

## Root cause diagnosis of prior failures

v1: TypeError at base.evaluate_bpc (called with 6 positional args; required 10).

v2 TWO failures:
1. TIMEOUT (3600s, no metrics.json): N=2048 on CPU with 7 M-values * 2 trajectories * 3 seeds * 4 stages
   = ~42 cells * ~100s/cell = ~4200s >> 3600s budget.
2. DESIGN BUG: forward/reverse trajectories each called run_4stage_get_retA(seed, m, config, device)
   independently at each M with NO state carried between M values. Forward and reverse were
   therefore IDENTICAL independent measurements. Any observed gap was pure noise.
   The hysteresis protocol was NOT implemented in v2.

## v3 design summary

- N=1024 (was 2048): 4x CPU speedup -> ~15-25 min expected.
- Stateful W trajectories:
    Forward: W_init=0 at M_min, train fresh at each M on corpus_A[:M] bytes.
    Reverse: compute W_max (trained on M_max=48k bytes) once per seed,
             then re-tune at each M in decreasing order.
  At each M, measure BPC using W-only prediction (no pool retrieval).
  Gap = |bpc_fwd(M) - bpc_rev(M)|.
- Single-corpus single-phase: corpus_A only (48512 bytes). 4-stage CL removed.
  Isolates capacity axis.
- M_SWEEP_FULL = [2000, 5000, 10000, 20000, 35000, 48000] (6 values, FULL)
- Periodic checkpoint writes: metrics saved as .tmp+rename after each M cell.
- Per-cell timeout tracking: 300s warning (non-fatal).
- Instrumentation self-test (mandatory): runs at module load.
- Multi-scale smoke: PASS at N=256 (77s) and N=512 (124s).

## Pre-registered bands (unchanged from v1/v2)

HARD-PASS: max BPC gap >= 0.10 -> 1-RSB supported
HARD-FAIL: max BPC gap < 0.03 -> RS/continuous, 1-RSB NOT supported
MIDDLE: gap in [0.03, 0.10) -> inconclusive

## Ship verification

- Name uniqueness: grep in remote_cpu_queue/queue.json + event_outcomes/ -> clean.
- Remote self-test gate: PASS in 2.7s on marsh@home.
- Post-ship VERIFIED: wave14_1rsb_hysteresis_v3 present in remote remote_cpu_queue/queue.json.
- Queue depth after ship: remote_cpu_queue pending=2 (wave14_saddle_cascade_plateau_v2 + this).
