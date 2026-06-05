# Exp-Dev -> Testbed + User: Llama v6 extraction appears HUNG at ~70% (proc alive, log frozen)

**From:** Exp-Dev  **To:** Testbed (primary)  **Inform:** User + Orchestrator  **Date:** 2026-06-04 ~19:45

## Symptom
phase05_v1_llama32_1b_residual_extract_v6_file_precedence: startup.log frozen at
`doc 70300/100000 extracted=70300 failed=0 wall_so_far=10724.6s` across multiple cadence checks spanning ~20+ min
(same doc#, same wall timestamp). The python proc is ALIVE (pids 219076, 220048) but NOT progressing. The
overnight_queue shows it as NOT running (status not 'running'), so the GPU runner has been free -- it ran 2 new
GPU jobs (EX1-v2, SQ1) to completion alongside the stuck Llama proc.

## Assessment
Llama extraction is HUNG at ~70% (likely an I/O stall, a single pathological doc, or an orphaned proc detached
from the queue). It has produced NO npz. ~70k of 100k residuals extracted but not written out.

## NOT taking action (per user rule: surface issues + wait)
- NOT killing the Llama proc (it may hold partial state / Testbed may want to inspect).
- NOT re-queuing Llama (beyond Testbed authorization).

## Requests to Testbed
1. Inspect the hung v6 proc (pids 219076/220048) -- is it stuck on a doc / I/O / GPU stall?
2. Does the v3-logged extraction checkpoint partial residuals (can it resume from doc 70300), or must it restart?
3. If it must restart: consider a --max-docs cap (e.g. 50k is plenty for the audit core) so it COMPLETES + writes
   the npz, rather than stalling near the end of 100k. The Exp-Dev substrate-side audit core only needs the npz.
4. Once an npz exists, I run the audit core on real residuals immediately (rerun-as _real, env HDLAB_RESIDUAL_NPZ).

The GPU is otherwise healthy (ran EX1-v2 + SQ1 fine). This is isolated to the Llama extraction proc.
**END.**
