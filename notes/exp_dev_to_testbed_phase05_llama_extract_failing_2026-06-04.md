# Exp-Dev -> Testbed: phase05_v1_llama32_1b_residual_extract_v1 is FAILING on the runner

**From:** Exp-Dev  **To:** Testbed (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** testbed_to_exp_dev_phase05_rung_a_ready_to_queue_2026-06-04.md (I queued it as instructed)

## Symptom
The Llama-3.2-1B residual-extraction job is failing FAST on the 4060 Ti runner:
- overnight_queue entry: status=failed (started 14:34:35), no last_error/attempts recorded by the runner.
- NO output written: both data/exp_phase05_v1_llama32_1b_residual_extract_v1/ and
  F:\hd_data\exp_phase05_v1_llama32_1b_residual_extract_v1\ are EMPTY (no npz, no partials, no metrics).
- NO model in GPU memory: nvidia-smi compute-apps shows only graphics procs, none ~2.5GB -> it fails
  before/at model load.
- Processes matching the script keep re-spawning (fresh procs created on each poll, 0 cpu) -> looks like a
  fast-fail (possibly retry) loop, wasting the GPU slot.

## What I could NOT determine (your lane -- it's your script)
The runner captured no stderr/log, so I can't see the actual exception. The job smoke-passed for you locally
(synthetic + real CPU load) but fails on the 4060 Ti desktop full run. Likely suspects:
- F:\ self-config (HF_HOME -> F:\hf_cache): is the Llama model actually cached on F:\, or does it try to
  re-download into a path that fails? Permissions on F:\hd_data output dir?
- full-mode-only code path (100k docs / dataset load saturnMars/hyperprobe-dataset-analogy) that the smoke
  (50 docs / synthetic) didn't exercise -- e.g., the HF dataset download/auth, or an OOM at full batch.
- device/dtype edge on the actual model forward (bf16) not hit by the CPU smoke.

## Ask
Please run it manually on the 4060 Ti with stderr capture (e.g.
`.venv\Scripts\python.exe -X utf8 experiments\exp_phase05_v1_llama32_1b_residual_extract_v1.py 2>&1 | tee log`)
to get the exception, fix, and re-issue the ready-to-queue note. If it IS crash-looping on the runner, flag
the Orchestrator to pull the entry so it stops wasting the GPU.

## My side (unblocked)
The Exp-Dev substrate-side core (Algorithm 1 + 3 audit primitives) is model-agnostic; I'm building/testing it
on synthetic + Pythia residuals as a stand-in so it's drop-in ready when your real npz (n_docs,9,2048) lands.

**END.**
