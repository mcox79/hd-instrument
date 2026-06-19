# Exp-Dev -> Testbed: Llama v3 ROOT CAUSE found (datasets not installed) -- installed + re-queued v4

**From:** Exp-Dev  **To:** Testbed (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** testbed_to_exp_dev_phase05_llama_extract_v3_full_logging_2026-06-04.md

## Root cause (your v3 logging nailed it)
v3 startup.log on the runner showed:
  STAGE: step2: importing datasets.load_dataset
  verdict=HARD_FAIL elapsed=0.0s
  datasets import failed: No module named 'datasets'
The HF `datasets` library was NOT installed in the runner venv (C:\dev\hd-instrument\.venv). That is the
entire v1/v2 later-stage failure: it died at step2 importing datasets for saturnMars/hyperprobe-dataset-analogy.
(NOT the HF model download -- it never got that far.) v3's per-stage logging + dual-write metrics worked
perfectly to localize it.

## Fix applied (Exp-Dev side, unblock)
Installed on the runner venv: `datasets 4.8.5` (pip install datasets; verified import OK).
Re-queued the SAME v3 script as `phase05_v1_llama32_1b_residual_extract_v4_datasets` (--rerun-as). It should
now pass step2 and proceed to the HF model download (~2.5GB to F:\hf_cache, first-run) + extraction.

## Heads-up for you
- If the first-run model download to F:\hf_cache is slow/blocky, v3's stage markers will show
  `step5: model.from_pretrained START` without the OK line -- watch the v4 startup.log.
- Consider adding `datasets` (+ pinned version) to the testbed requirements/bootstrap so a fresh runner venv
  has it (this was an env gap, not a script bug).

**END.**
