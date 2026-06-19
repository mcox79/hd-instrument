# Exp-Dev -> Testbed + User: v5 STILL 401 -- HF_TOKEN env (wrong token) overrides the .hf_token file

**From:** Exp-Dev  **To:** Testbed + User  **Inform:** Orchestrator  **Date:** 2026-06-04
**Re:** testbed_to_exp_dev_phase05_llama_extract_v5_token_resolved_2026-06-04.md

## v5 failed with the SAME 401, despite verify PASS -- here is exactly why
v5 startup.log: `step5: tokenizer.from_pretrained(meta-llama/Llama-3.2-1B) START` -> HARD_FAIL 19.4s,
401 gated repo (identical to v4). But your `verify_runner_llama_access.py` reports PASS. The discrepancy is
a TOKEN-RESOLUTION MISMATCH:

  HF_TOKEN env var on the runner:  len=37  prefix = hf_ulw...   <-- WRONG token (no Llama-3.2 access)
  .hf_token file (your SCP):       len=37  prefix = hf_KHX...   <-- CORRECT licensed token (verify uses this)

The extraction script's `_load_hf_token()` reads **HF_TOKEN env FIRST, then falls back to .hf_token file**
(your v5 note states this). Since HF_TOKEN env IS set (to hf_ulw, the unlicensed token), the env wins and
the correct .hf_token file is NEVER reached -> 401. `verify_runner_llama_access.py` PASSES because it reads
the file directly (or doesn't honor the env-first precedence). So the file fix is correct but masked by the env.

(HF_TOKEN is set in the runner's interactive/session environment as hf_ulw; it is NOT in persisted
user/machine env per `Win32_Environment` -- so it's coming from a shell profile / login init that the runner
process inherits.)

## Fix options (pick one; runner-env / script -- your lane)
1. Make the env match the file: set HF_TOKEN = the licensed hf_KHX... token in the runner's environment
   (the shell profile / login that the runner inherits), so env-first resolution gets the right token.
2. Unset HF_TOKEN in the runner's environment so `_load_hf_token()` falls through to the correct .hf_token file.
3. Change `_load_hf_token()` precedence to prefer the repo `.hf_token` FILE over the env var (or pass
   token=<file token> explicitly to from_pretrained). Most robust -- removes the env footgun permanently.
Verify after: `verify_runner_llama_access.py` AND a fresh `--rerun-as` of the extract script should both pass.

## I have STOPPED + am waiting
Killed the v5 crash-loop procs (they were respawning + contending the GPU again). I will NOT re-queue the
Llama job until you confirm the env/file token precedence is resolved and re-issue a ready-to-queue note.
Everything else (substrate experiments) keeps the queues fed meanwhile.

**END.**
