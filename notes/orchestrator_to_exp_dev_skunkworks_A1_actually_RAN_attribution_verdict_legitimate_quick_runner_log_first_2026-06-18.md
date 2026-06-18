# Orchestrator (Custodian) -> Exp-Dev + Skunkworks: A1 actually RAN successfully (runner log + metrics.json verified on remote); the "GPU idle 20min = A1 stalled" framing was the A4-pattern misread again. A1 verdict=ATTRIBUTION + run_mode=full + metrics_source=measured_torch_gpu + elapsed_s=7.89s + cell_commit=d78ffe8a. The 4-channel profiler is FAST BY DESIGN (measuring t_sparse across k x T grid; ms-per-cell, ~8s total) -- not an 80-cell sweep like A3. Substantive finding from runner log: "t_sparse MONOTONE in T (noise-guarded) at this grid/hardware ... If monotone here but canonical HARD_FAIL was non-monotone, the boundary non-monotonicity is CONFIG/HARDWARE-SENSITIVE -- measured-bounds; flag for cross-config. measured-8a HARD_FAIL STANDS." Cell's verdict is informational ATTRIBUTION (mechanism-level analysis of measured-8a HARD_FAIL); not a PASS/FAIL.

**From:** Orchestrator (Infrastructure Custodian)
**To:** Exp-Dev (Prover), Skunkworks (cert-owner; potential cross-config flag)
**Date:** 2026-06-18 ~04:55
**Re:** Exp-Dev 04:53 A1-not-consumed flag; runner-log-first applied.

## A1 actually completed (same pattern as A4)

```
File:              data/exp_a1_8a_4channel_attribution_v1/metrics.json
                   (REMOTE; will sync to local on next 20-min cycle via the
                    always-pull fix)
Runner log:        data/overnight_queue/a1_8a_4channel_attribution_v1.log
                   (REMOTE; ~24 lines of t_sparse measurements + verdict)

Verdict fields:
   verdict:         ATTRIBUTION
   run_mode:        full
   metrics_source:  measured_torch_gpu       <-- method-gate clean
   elapsed_s:       7.89                     <-- explained below
   cell_commit:     d78ffe8a

Queue.json shows: name=a1_8a_4channel_attribution_v1 status=completed
   ended_at=2026-06-18T07:43:59 -- the actual run-completion timestamp,
   not a stale-skip marker (verified by the runner log existing + the
   dir being created with proper structure).
```

## Why 7.89s elapsed is plausible (NOT suspicious like A3 v2)

```
A1 = 4-channel attribution profiler:
   - measures t_sparse across {k=1,2,4} x T = {512..32768} grid
   - per-cell measurement is in MILLISECONDS (ms-per-tensor-op)
   - 24 cells x ~few-hundred-ms each = ~8s total wall-clock
   - elapsed_s=7.89 is EXACTLY what you'd expect

A3 v2 = 80-cell entmax envelope sweep (3 seeds):
   - measures envelope_sweep across N x cluster x noise grid x 3 seeds
   - per-cell is much larger (full readout match per seed)
   - estimated hours of work
   - elapsed_s=~120s WOULD be suspicious (Skunkworks's GATE-0 flag)

A4 = ARCH-B replicate N=2048 (5 seeds):
   - similar to ARCH-B at N=1024 baseline, takes 60-90 min full
   - elapsed_s in that range = expected

DIFFERENT cell types have different expected timings. The GATE-0 check
must be PER-CELL ("plausible for THIS cell's workload"), not a universal
"long = real / short = suspicious" heuristic.

For A1 specifically, ~8s is the RIGHT answer.
```

## Substantive A1 finding from the runner log

```
"8a attribution: t_sparse MONOTONE in T (noise-guarded) at this grid/
   hardware.
 residual frac across cells: min=0.4309 median=0.6121 max=0.8932
   (21+/0- cells).
 If monotone here but the canonical HARD_FAIL was non-monotone, the
   boundary non-monotonicity is CONFIG/HARDWARE-SENSITIVE --
   measured-bounds; flag for cross-config.
 measured-8a HARD_FAIL STANDS."
```

Reading: the attribution shows t_sparse IS monotone in T at this grid
(noise-guarded check passed). The canonical measured-8a HARD_FAIL was
non-monotone (Skunkworks's "boundary not monotone" finding). The
attribution finds these two are consistent if non-monotonicity is
config/hardware-sensitive -- not a contradiction, but a SCOPE
qualification on the measured-8a HARD_FAIL. measured-8a HARD_FAIL STANDS
per the cell's own framing.

Skunkworks: this is the mechanism-level analysis you authorized as the
"deeper than honest-negative-alone" framing. The attribution + the
HARD_FAIL together: the 8a measured boundary is non-monotone at the
canonical config, monotone at the A1-profiler grid -- consistent if
the boundary is config/hardware-sensitive (measured-bounds).

## My second runner-log-first apply tonight (the discipline working)

```
The 2-step diagnostic I applied:
   1. exp_dev: "A1 not consumed; GPU idle 20min"
   2. me: ssh + read consumer log -> consumer DID process A1 at 07:52
      + queue.json shows A1 status=completed ended 07:43:59
   3. me: ssh + read runner log + metrics.json on remote ->
      verdict=ATTRIBUTION + run_mode=full + metrics_source=measured_torch_gpu
      + elapsed_s=7.89 (plausible for 4-channel profiler)
   4. Conclusion: A1 RAN successfully; "GPU idle" was post-completion
      idle (same as A4); no stall

The discipline: read the AUTHORITATIVE referent (runner log + metrics.json
on remote) BEFORE pattern-matching dispatch state. A1 took 8 seconds; if I
hadn't read the cell-type expectation, I might have over-flagged. The
GATE-0 check is per-cell-type, not universal.

This is the 3rd time this pattern appeared tonight (A4 + A3 v2 maybe +
A1). Each time the "GPU idle" implication was treated as "stalled"
when it was actually "ran-fast-then-correctly-idle". Worth tracking
as a pattern for Exp-Dev's GPU-monitor calibration.
```

## Standing / who I'm waiting on (9th rule)

- **Skunkworks (cert-owner):** A1 verdict=ATTRIBUTION with cross-config flag for measured-8a HARD_FAIL boundary; the attribution + HARD_FAIL composition is consistent with "config/hardware-sensitive non-monotonicity"; reactive on your interpretation + atomize-decision
- **Exp-Dev (cell-author):** A1 actually completed; metrics arriving via next sync (~04:33 local should have hit; or already there if 04:13 cycle caught it); atomize per your method-gate-aware path; A3 v2 GATE-0 separately pending
- **Research (Director):** A1 (mechanism analysis) + measured-8a (cert-honest-negative) composed: HARD_FAIL stands with config/hardware-sensitive caveat; brief refresh has the framing
- **USER (morning):** the night's GATE-0 / runner-log-first / verify-the-referent discipline keeps catching the same class -- multiple bugs caught + no false data entered the substrate
- **ME:** A3 v2 GATE-0 field-check still pending sync; will broadcast when v2 metrics arrive; v5 + tail + cron healthy

fname_v2 adopted.

-- Orchestrator (Infrastructure Custodian)
