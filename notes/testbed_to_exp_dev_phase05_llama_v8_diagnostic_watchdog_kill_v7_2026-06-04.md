# Testbed -> Exp-Dev: AUTHORIZE kill v7 + ship v8 with diagnostic watchdog + tokenizers fix

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-04
**Re:** `exp_dev_to_testbed_llama_v7_stuck_post_load_2026-06-04.md`

## Authorize: kill v7 procs + re-queue as v8

User authorized 3-track plan (cornerstone HF recovery + Rung A unblock + tokenizer fix); v7 unblock is Track 2.

**Kill PIDs**: kill v7 procs holding the GPU (you noted pid 116084 + the v7 sibling). Same caveats as v6 kill: in-memory residuals not recoverable; per-doc partials persist for v8 resume.

**v8 anchor**: `phase05_v1_llama32_1b_residual_extract_v8_diagnostic_watchdog`
**Same script**, now patched in commit (below) with these v8 changes:

## v8 patches (all in `exp_phase05_v1_llama32_1b_residual_extract_v1.py`)

1. **TOKENIZERS_PARALLELISM=false at module top** (BEFORE any transformers import). Likely root cause of both v6 + v7 silent hangs: huggingface/tokenizers spawns its rayon thread pool early; a later fork() (HF datasets workers, our own pool, anything) deadlocks against the locked pool. Both runs froze with NO traceback -- canonical fork-after-parallelism symptom.

2. **Per-doc watchdog with `os._exit(99)`**: daemon thread monitors `_LAST_DOC_COMPLETE_TS` updated on every doc loop iteration. If no doc completes within `WATCHDOG_PER_DOC_TIMEOUT_S=120s`, watchdog writes `watchdog_exit.json` + exits the process. Runner can then re-queue and the next dispatch resumes from per-doc partials (PROT-021 partials persisted via `write_partial_key` survive a hard exit).

   **Result**: silent hangs convert to fast-fail exits. No more 30-min GPU-blocked dead procs.

3. **PROGRESS_EVERY 100 -> 25**: 4x more frequent flushes. Stall window between visible progress prints is ~2 sec instead of ~8 sec (at v6's 6.5 docs/s throughput). Makes the actual stuck doc clearly visible.

4. **GPU memory in progress lines**: each `progress: doc X/Y` line now logs `gpu_alloc_gb=A.AA gpu_reserved_gb=B.BB` so we can SEE if memory is leaking pre-stall.

## Why this attacks BOTH v6 and v7 stalls

- v6 hung at doc 70300 (deep into run): could be the rayon pool deadlock kicking in after enough tokenizer reuse; the fix prevents the pool from starting in the first place.
- v7 hung at doc 0 (immediately): same rayon-pool culprit but tripped at the first batch instead of late. Same fix applies.
- Either way, if the underlying cause is DIFFERENT, watchdog turns silent stall -> fast 120s exit -> we see a clean traceback / partial state and diagnose.

## v8 wall budget

Still --max-docs=50000 cap per v7 spec. At v6 throughput (6.5 docs/s steady-state pre-stall), 50k docs is ~2h10m wall. With watchdog + tokenizers fix, expect smooth completion or fast-fail with diagnostic.

## Re-queue command (PowerShell on marsh@home)

```powershell
# 1. kill v7 procs
Stop-Process -Id 116084 -Force  # and any sibling pid your tasklist shows
# 2. (optional) cleanup pre-v7 attempt state
Remove-Item -Recurse -Force "C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_residual_extract_v7_max_docs_50k" -ErrorAction SilentlyContinue
# 3. pull latest commit
git -C C:\dev\hd-instrument pull origin main
# 4. queue_add
bash tools/orchestrator/queue_add.sh overnight_queue \
  phase05_v1_llama32_1b_residual_extract_v1 \
  experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py \
  preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md \
  10800 \
  --rerun-as phase05_v1_llama32_1b_residual_extract_v8_diagnostic_watchdog \
  -- --max-docs 50000
```

## What you'll see in the log if v8 works

```
  watchdog armed: will exit if no doc completes in 120s; PROGRESS_EVERY=25
  progress: doc 25/50000 extracted=25 failed=0 wall_so_far=3.8s mem_mb=... gpu_alloc_gb=4.50 gpu_reserved_gb=5.20
  progress: doc 50/50000 extracted=50 failed=0 wall_so_far=7.5s mem_mb=... gpu_alloc_gb=4.50 ...
  ...
```

## What you'll see in the log if v8 still stalls (but watchdog fires)

```
  progress: doc <N>/50000 ...  <- LAST visible doc before stall
  <120s of silence>
  [WATCHDOG] no doc completed in 120.5s (threshold 120s); presumed deadlock; exiting via os._exit(99). Resume on next dispatch from per-doc partials.
```

Plus `watchdog_exit.json` written to the run's out_dir. Then runner re-queue continues from the per-doc partials.

## What this UNBLOCKS

- Per Research (`research_to_testbed_cornerstone_response_4_questions`): C2 + C3 substrate-audit-core can run on REAL Llama-3.2-1B residuals at $0 (your lane). That's the Tier-1 product anchor.
- Your Tier-6 GPU work (per `exp_dev_to_research_p1_p2_HP_v7_stuck`): unblocked the moment v8 lands and frees the GPU.
- My cornerstone targeted 8B retry (Track 3 in 3-track plan): conditional on C2+C3 working at 1B first.

## Track 3 status (for your awareness; independent of v8)

I'm refactoring cornerstone's C2+C3 `_extract_residuals_via_hyperprobe` to use `hyperprobe.ingest_embeddings(docs=..., model_name=LLM_MODEL_ID, ...)` per Research's Q1 answer (probe_validation_v1.py is the canonical pattern; my sub-agent's earlier `model=AutoModel_instance` was wrong). No cloud spend; engineering only; waits on v8 + 1B substrate-audit-core validation before any cloud retry.

## Commit

Patches committed (hash forthcoming after push). Same file
`experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py`. ASCII-only, no
em-dash, per-doc timestamp updates inside the loop.

---

**END.**

**Exp-Dev:** authorized; please proceed with v7 kill + v8 re-queue per the sequence above. Watchdog will give us either a clean run OR a fast-fail with diagnostic JSON within 2 min of stall.

**User:** Track 2 v8 patches engineered; awaiting Exp-Dev queue + first log lines to confirm tokenizer-parallelism fix works.

**Research:** v8 is the unblocker for your hybrid C+D plan. C2 + C3 on 1B residuals can run as soon as v8 produces a clean npz.
