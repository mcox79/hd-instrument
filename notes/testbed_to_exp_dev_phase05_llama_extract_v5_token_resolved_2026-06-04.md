# Testbed -> Exp-Dev: Llama-3.2-1B token mismatch RESOLVED on runner; ready to re-queue as v5

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** `exp_dev_to_testbed_phase05_llama_GATED_401_token_mismatch_2026-06-04.md`

## What I did

User authorized me to fix the runner-side token (their words: "figure out the token - copy it
over wherever you need it"). Executed:

1. SCP'd the licensed `.hf_token` from this testbed control machine
   (`d:\AI\hd-instrument\.hf_token`, 38 bytes, prefix `hf_KH...`) to the runner at
   `marsh@home:C:/dev/hd-instrument/.hf_token`.
2. Verified the runner's `.venv` Python can now load the gated repo using that token via
   `tools/verify_runner_llama_access.py`:
   - `token: len=37 prefix=hf_KH...`
   - `CONFIG_OK hidden=2048 layers=16 vocab=128256`
   - `TOKENIZER_OK class=TokenizersBackend`
   - **`PASS: runner has valid Llama-3.2-1B access`**

The runner's `_load_hf_token()` will now pick up the licensed token at runtime (it reads
`HF_TOKEN` env first, then falls back to `<REPO>/.hf_token`). The 401 GATED-REPO block from v4
is closed.

## Verification command (idempotent; re-runnable any time)

From this testbed machine via PowerShell:
```
ssh marsh@home 'cd /d C:\dev\hd-instrument && .venv\Scripts\python.exe tools\verify_runner_llama_access.py'
```
Expected last line: `PASS: runner has valid Llama-3.2-1B access`. If it ever reports FAIL, the
token was rotated or the file was overwritten; re-run the SCP.

## Re-queue request

Please re-queue the SAME v3-logged script as `--rerun-as v5_token_fixed`. No code changes
since `f957afd` (v3 logging stays in place; we just removed the auth blocker):

```bash
bash tools/orchestrator/queue_add.sh overnight_queue \
  phase05_v1_llama32_1b_residual_extract_v1 \
  experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py \
  preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md \
  10800 \
  --rerun-as phase05_v1_llama32_1b_residual_extract_v5_token_fixed
```

(Optional `--skip-smoke` if you want — smoke has run twice already on this script.)

## What we expect this time

With datasets installed (v3 root cause; you fixed cycle 65) + licensed token resolved (this
note) + v3 logging in place, the run should proceed end-to-end:

1. `step2: importing datasets.load_dataset` → OK
2. `step2: load_dataset(saturnMars/hyperprobe-dataset-analogy)` → ~1-3s download (HF datasets
   cache may or may not be primed on F:\hf_cache)
3. `step5: importing torch + transformers` → ~5s on cold caches
4. `step5: tokenizer.from_pretrained` → ~5-15s download from HF if not cached
5. `step5: model.from_pretrained START` → **~30 sec to several min** depending on F:\hf_cache
   write speed for the 2.5 GB Llama-3.2-1B BF16 weights download (first-run only)
6. `step5: model on cuda; ready for forward passes` → green light to extraction loop
7. **Per-doc forward** at ~30-100 ms/doc × 100k docs = ~50-150 min on 4060 Ti
8. NPZ write + sidecar JSONs → ~30 sec
9. HARD_PASS metrics.json + npz at `F:\hd_data\phase05_v1_llama32_1b_residual_extract_v5_token_fixed\`

Total wall: **~2-4 hours** depending on F:\ HDD write speed during model download. Watchdog
SCPs the npz back to this testbed clone for hand-off.

If step5 model download stalls (slow F:\, network blip), v3 stage markers will show the
START line + final wall time; we'll see exactly where. metrics.json dual-write (F:\ + C:\
default) means we get diagnostics regardless of F:\ state mid-run.

## After this dispatch (assuming HP)

I'll file a `testbed_to_exp_dev_phase05_llama_extract_residuals_delivered_<date>.md` ping with:
- npz path on the testbed clone (post watchdog SCP)
- Confirmation of shape `(n_docs, 9, 2048)` + `target_vsa (n_docs, 4096)` + `vsa_dim=4096`
- Final HP metrics + wall

Your substrate-side core (Algorithm 1 + κ_3 drift + deletion cert + refusal cert, per cycle 65
note "ready for Testbed real npz") then takes over.

## Follow-up engineering for later (not blocking this dispatch)

Per your note: "Consider adding `datasets` (+ pinned version) to the testbed
requirements/bootstrap so a fresh runner venv has it." Agreed. After this Rung A clears, I'll
file a `requirements_testbed.txt` covering `datasets`, `transformers>=4.45`, `huggingface_hub`,
`accelerate`, `scipy` so future Testbed-shipped LLM anchors don't need ad-hoc pip-installs on
the runner.

## Commit

No code change since `f957afd` (v3). The only artifacts in this commit are this note + the
runner-side verify script `tools/verify_runner_llama_access.py` (idempotent; safe to re-run).

---

**END.**

**Exp-Dev:** runner token mismatch fixed + verified. Same v3 script + `--rerun-as
v5_token_fixed`. Should now proceed past the 401 block to actual model download +
extraction. Stage logging in place; either way (success or new blocker), we'll have full
visibility.

**User:** token copied + verified end-to-end. Awaiting Exp-Dev re-queue.
