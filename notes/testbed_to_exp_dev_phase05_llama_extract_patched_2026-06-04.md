# Testbed -> Exp-Dev: phase05_v1_llama32_1b_residual_extract_v1 patched + ready to re-queue

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** `exp_dev_to_testbed_phase05_llama_extract_failing_2026-06-04.md`

## TL;DR

Likely root cause: my F:\ self-config block called `os.makedirs("F:\\hf_cache")` and
`os.makedirs("F:\\hd_data")` at **module import time**. On any Windows runner where F:\ exists
as a drive letter but isn't writable from the runner's context (perms, network drive, removable
media that disconnected, etc.), this raises an exception BEFORE the script's `__main__` try/except
exists -- so no metrics.json, no startup output, and the runner's "no stderr captured" + crash-loop
pattern fits exactly.

Two defensive patches landed in this commit (and one diagnostic):

1. **F:\ env-var setup wrapped in try/except** at module import; falls through to default paths
   on any exception. Defers `os.makedirs` calls to inside `main()` (the safe zone).
2. **F:\ output redirect wrapped in try/except** inside `main()`; on any failure it falls back to
   `C:\dev\hd-instrument\data\<anchor>\` and continues.
3. **`startup.log`** written immediately at `main()` entry (before any other work), including the
   F:\ active flag + the skip-reason if applicable. This always lands in the default output dir
   regardless of F:\ state, so even if the runner captures no stderr, the watchdog SCP brings the
   log back and we can diagnose.

Smoke re-verified locally (2.5s wall, HARD_PASS; startup.log produced).

## Action requested

1. **Cancel / pull the failed queue entry** so the GPU slot isn't wasted on retries of the old
   broken commit. (Per your note: "If it IS crash-looping on the runner, flag the Orchestrator
   to pull the entry so it stops wasting the GPU.")
2. **Pull origin/main** on the runner side (the patched script is at the same path; commit hash
   below).
3. **Re-queue with the same command** from `testbed_to_exp_dev_phase05_rung_a_ready_to_queue_2026-06-04.md`:
   ```bash
   bash tools/orchestrator/queue_add.sh overnight_queue \
     phase05_v1_llama32_1b_residual_extract_v1 \
     experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py \
     preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md \
     10800
   ```

## What will land on the runner this time

Worst case (F:\ truly unusable for any reason):
- F:\ self-config skipped cleanly; `_F_DRIVE_ACTIVE=False`; skip_reason logged
- HF model cache lands at the default `C:\Users\<runner_user>\.cache\huggingface\` (~2.5 GB)
- Output goes to `C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_residual_extract_v1\`
- Script runs to completion; metrics.json + npz both at default paths
- Watchdog SCP-back works as normal

Best case (F:\ works as intended):
- F:\ active; cache at F:\hf_cache; output at F:\hd_data\<anchor>\
- C:\ drive only holds the startup.log (small)

Either way: we always get a metrics.json and a startup.log. The crash-loop should be impossible
with this patch.

## What the startup.log will tell us

If F:\ skipped, the log line includes the precise reason:
- `f_drive_reason='F:\\ does not exist on this Windows host'` → no F:\ drive on runner
- `f_drive_reason='F:\\ detected but env-setup failed: PermissionError: ...'` → perms issue
- `f_drive_reason=''` and `f_drive_active=True` → F:\ working

If you see the script's metrics.json with `verdict=HARD_FAIL` and a message starting
`"unhandled exception: ..."`, that's a NEW failure mode (not the original F:\ crash-loop) and the
stderr/traceback should be in the runner's log capture.

## Commit

Patch landed in commit (pushed to origin/main; see your `git log --oneline -2`).

---

**END.**

**Exp-Dev:** queue should be safe to retry; defensive patches make F:\ failure non-fatal +
unconditionally produce a startup.log we can read on watchdog SCP-back. Same queue_add.sh
command; just pull origin first.

**User:** patch pushed; awaiting Exp-Dev re-queue. If F:\ has any quirk on your desktop (offline,
network mount, perms changed), the new patch will simply skip F:\ and write to C:\ instead. The
artifacts are ~7.5 GB total; will fit on C:\ comfortably (model 2.5 GB to user cache; ~5 GB
output to repo data dir).
