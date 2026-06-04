# Testbed -> Exp-Dev: v5 root cause confirmed + fix shipped as v6 (file-first token precedence)

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** Orchestrator + User  **Date:** 2026-06-04
**Re:** `exp_dev_to_testbed_phase05_llama_v5_ENV_TOKEN_OVERRIDES_FILE_2026-06-04.md`

## Diagnosis you nailed

You called it exactly: the runner's shell-profile `HF_TOKEN=hf_ulw...` (unlicensed) was
overriding my SCP'd `.hf_token=hf_KH...` (licensed) because `_load_hf_token()` did env-first
resolution. `verify_runner_llama_access.py` PASSed because it reads the file directly.
The extraction script DID NOT use the file because env-first won.

## Fix shipped

**Inverted `_load_hf_token()` precedence: repo-local `.hf_token` FILE now wins over `HF_TOKEN`
env var.** Rationale (now baked into the function docstring):

- The repo-local `.hf_token` is explicit + per-repo + version-control-aware (gitignored,
  deliberately placed). It's the canonical per-anchor auth source.
- `HF_TOKEN` env vars can leak in from shell profiles, login init scripts, system env, parent
  processes, or stale `huggingface-cli login` state. On shared runners these can mask the
  correct file token without warning.
- File-first removes the env footgun permanently for this anchor (and any future anchors
  that adopt the same pattern).

Plus: **step 1 now emits two `_log_stage` lines** showing both the file prefix AND the env
prefix BEFORE auth, and the resolved-token source AFTER. So on the next runner dispatch,
the startup.log will say e.g.:
```
STAGE: step1: token sources: file=C:\dev\hd-instrument\.hf_token present=True prefix=hf_KH...; env HF_TOKEN prefix=hf_ulw...; file-first precedence (per v5 fix)
STAGE: step1: token RESOLVED len=37 prefix=hf_KH... (source: file)
```

This makes any future token-mismatch immediately visible.

## Adversarial local smoke (proves the fix works)

Set `HF_TOKEN=hf_FAKE_unlicensed_env_token_for_test_only` in env, ran the script with the real
licensed `.hf_token` (prefix `hf_KH...`) on disk. Result:

```
STAGE: step1: token sources: file=D:\AI\hd-instrument\.hf_token present=True prefix=hf_KH...;
        env HF_TOKEN prefix=hf_FA...; file-first precedence (per v5 fix)
STAGE: step1: token RESOLVED len=37 prefix=hf_KH... (source: file)
...
"verdict": "HARD_PASS"
```

The file token won over the (fake) env token, exactly as designed. Reproduces the v5 runner
state in adversarial mode + confirms the fix.

## Re-queue request

Please re-queue the SAME script (post-precedence-fix) as `--rerun-as v6_file_precedence`. The
runner's existing state is already correct:
- `.hf_token` file at `C:\dev\hd-instrument\.hf_token` has the licensed `hf_KH...` token
  (SCP'd in v5; unchanged)
- HF_TOKEN env still has the unlicensed `hf_ulw...` (per your note); the script will now
  IGNORE it and use the file

```bash
bash tools/orchestrator/queue_add.sh overnight_queue \
  phase05_v1_llama32_1b_residual_extract_v1 \
  experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py \
  preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md \
  10800 \
  --rerun-as phase05_v1_llama32_1b_residual_extract_v6_file_precedence
```

## Optional cleanup for the user (not blocking this dispatch)

You may eventually want to unset/correct the runner's persistent `HF_TOKEN` env in the shell
profile so it stops being a footgun for other scripts that use env-first precedence (most
upstream libraries do). File-first is the right call for our scripts here, but the
underlying env mismatch will surface again on other HF-gated work if not fixed at source.
Not blocking; my script now defends against it.

## Commit

Patch landed in commit (will list hash after push). The runner-side fix is purely code:
no further runner-side state changes needed beyond the `.hf_token` SCP already done in v5.

---

**END.**

**Exp-Dev:** v6 ready. File-first precedence + token-source logging in place. The same v5
runner state (SCP'd file token + stale env token) will now resolve to the file token
correctly. Should proceed past step1 → step5 model download → extraction.

**User:** the v5 SCP was correct but masked by env. v6 inverts precedence so the file wins.
Adversarial local smoke confirms the fix; runner state on next dispatch will be visible in
startup.log step1 markers.
