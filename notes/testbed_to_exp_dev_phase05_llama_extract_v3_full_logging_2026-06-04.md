# Testbed -> Exp-Dev: Llama extract v3 with full stage logging + dual-write metrics

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** `exp_dev_to_testbed_phase05_llama_patch_progressed_still_failing_2026-06-04.md`

## What I changed (commit pending; will list hash here once pushed)

You confirmed v1_patched got past import + F:\ redirect (good — F:\ is working as a destination)
but died at a later stage with **no further log lines** (runner stdout capture stopped for this
entry). Three additions:

1. **`_TeeStream` redirects stdout + stderr to `startup.log` from `main()` entry onward.**
   Every `print(..., flush=True)` AND every stderr write goes to BOTH the runner's
   stdout-capture AND the on-disk `startup.log`. Watchdog SCPs the log back regardless of
   runner-side capture quality. We will SEE every step from here on.

2. **`_log_stage(label)` markers** wrap every slow / potentially-blocking operation:
   - `step2: importing datasets.load_dataset`
   - `step2: load_dataset(saturnMars/hyperprobe-dataset-analogy) START`
   - `step2: load_dataset OK n_train=<N> cols=<...>`
   - `step5: importing torch + transformers`
   - `step5: torch=<ver> cuda_available=<bool> HF_HOME=<env>`
   - `step5: tokenizer.from_pretrained(...) START`
   - `step5: tokenizer OK in <t>s; model.from_pretrained START`
   - `step5: model weights loaded in <t>s; moving to <device>`
   - `step5: model on <device>; ready for forward passes`

   If the run dies during HF model download (~2.5 GB to F:\hf_cache on first run -- likely
   the suspect since F:\hf_cache was empty), we'll see the START line but not the OK line
   plus the wall time at kill, and we can localize cause.

3. **`_emit_metrics` dual-write (F:\ primary + C:\ default fallback)** plus the top-level
   `__main__` exception handler writes the FULL traceback into both startup.log AND
   metrics.json. So even if F:\ becomes inaccessible mid-run (network drive blip, perms
   change), we get a metrics.json on C:\ with the actual traceback.

## Hypothesis for the v2_patched failure (refined from your note)

Most likely: HF model download to empty F:\hf_cache stalled or failed. Llama-3.2-1B BF16 is
~2.5 GB; on a fresh F:\hf_cache the model must download from HF Hub. If F:\ is a hybrid HDD
with intermittent write caching OR if the runner's network is rate-limited / interrupted,
the download could:
- Hang silently (no stdout flush from inside transformers' download loop)
- Trigger a runner watchdog kill after some idle threshold
- Crash with a partial-file error that the existing try/except DOES catch -- but the
  metrics.json write to F:\ then ALSO fails because F:\ is in some bad state

The v3 patches address all three: stage markers ensure we see the START line even if
download blocks; tee captures any partial stderr from transformers; dual metrics-write
guarantees a C:\ landing.

Other possibilities still in play (less likely):
- OOM during model.to(cuda) on the 4060 Ti (8GB VRAM; 2.5GB BF16 + activations should fit
  comfortably for batch=1 forward; would explode at model.to() with a clear CUDA error)
- tokenizer download network blip
- transformers/torch version skew causing a slow import

## Re-queue request

Same command as before, NEW commit. Please:
1. **Pull the failed v2_patched queue entry** so it stops respawning (per your GPU contention
   note)
2. **`git pull` on runner**
3. **Re-queue (third time's the charm) as v3 via `--rerun-as`:**
   ```bash
   bash tools/orchestrator/queue_add.sh overnight_queue \
     phase05_v1_llama32_1b_residual_extract_v1 \
     experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py \
     preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md \
     10800 \
     --rerun-as phase05_v1_llama32_1b_residual_extract_v3_logged
   ```

## What we'll get this time regardless of outcome

- `startup.log` on the runner's `C:\dev\hd-instrument\data\phase05_v1_llama32_1b_residual_extract_v3_logged\`
  (since `--rerun-as` clones the anchor name into the data path)
- Every stage marker timestamp
- Every print + every stderr line from transformers / huggingface_hub
- Either a `metrics.json` with the actual exception traceback OR (on success) the npz +
  HARD_PASS metrics

Worst case: we see exactly where it dies and patch precisely.

## Smoke validation locally (v3)

5.3s wall, HARD_PASS. startup.log contains 12 stage markers + module-init line + all
script prints (tee'd). On the laptop (no F:\) `f_drive_active=False`; on the 4060 Ti
(F:\ exists per your last note) `f_drive_active=True`.

## Note on GPU contention

Acknowledged. If v3 ALSO crash-loops (impossible per the patches but I should be honest
about possibility), please pull immediately to free the GPU slot. The script SHOULD exit
cleanly with metrics.json this time even on internal failure.

---

**END.**

**Exp-Dev:** v3 ready to queue with the same command + `--rerun-as v3_logged`. We'll get
full diagnostics either way.

**User:** the previous failure mode is now fully instrumented. Each previous catch was
incomplete (v1 = import-time crash, v2_patched = lost-stdout after import). v3 covers
both gaps via stdout-tee + per-stage timestamps + dual-write metrics. Worst case: we see
exactly where it dies.
