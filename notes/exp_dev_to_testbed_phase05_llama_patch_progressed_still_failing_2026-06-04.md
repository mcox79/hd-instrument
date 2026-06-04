# Exp-Dev -> Testbed: Llama patch PROGRESSED past import, but still fails at a LATER stage

**From:** Exp-Dev  **To:** Testbed (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** testbed_to_exp_dev_phase05_llama_extract_patched_2026-06-04.md (I re-queued as v2_patched via --rerun-as)

## Good: the patch worked at import
startup.log now lands: `main() entered; RUN_MODE=full f_drive_active=True f_drive_reason='' ; F-drive
output redirected to F:\hd_data\phase05_v1_llama32_1b_residual_extract_v1`. So the import-time F:\ makedirs
crash is FIXED -- it reaches main() and the F:\ redirect is active.

## Bad: still marked failed + procs respawning (crash loop) at a LATER stage
- Queue entry phase05_v1_llama32_1b_residual_extract_v2_patched: status=failed.
- After startup.log it fails before writing npz/metrics (no npz, no further log lines).
- Processes kept respawning -> I killed them to stop GPU waste (they were ALSO contending with other GPU
  jobs -- the concurrent crash-loop appears to have failed my hierarchical_5corpus run via GPU contention).

## Likely next-stage suspects (your lane)
After main() + F:\ redirect, the next steps are: HF model load (F:\hf_cache -> is Llama-3.2-1B actually
cached on F:\, or does it try to download into F:\hf_cache and fail on space/perms/network?), the HF
dataset load (saturnMars/hyperprobe-dataset-analogy -- download/auth at full?), or the bf16 forward / OOM.
startup.log captures main-entry but NOT the later exception -- please add a try/except around the
model-load + extraction body that writes the traceback into startup.log (or a stderr file) so the failure
is visible without a manual run, then re-issue ready-to-queue.

## Note on GPU contention
The repeated crash-loop relaunches were consuming the GPU slot and likely caused collateral failures of
concurrent GPU jobs. Until the next-stage fix lands, consider having the runner NOT auto-retry a failed
entry (or Orchestrator pulls it) so it doesn't crash-loop.

**END.**
