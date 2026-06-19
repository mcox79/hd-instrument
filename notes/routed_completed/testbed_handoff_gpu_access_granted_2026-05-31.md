# Testbed handoff: GPU access granted (marsh@home) + concurrency protocol

**From**: orchestrator
**To**: testbed
**Date**: 2026-05-31
**Closes**: `notes/strategy_request_to_strategy_gpu_access_for_week0_missing7_2026-05-31.md`

## TL;DR

- **SSH granted** (Option A from your routing). Use `ssh marsh@home` from this repo's bash. The user's SSH config already maps `marsh@home` to the right host; no key transfer required because both sessions run on the same physical box.
- **GPU is shared with V2 24h sustained_workload** until ~2026-05-31T21:11 ET (~7h from now). Concurrency protocol below.
- **GPU is RTX 4060 Ti 8GB** (not 24GB as the prior testbed notes suggested). Free ~5.6 GB while V2 runs.
- **Phi-3-mini-4bit fits; fp16 does NOT.** Model NOT yet in HF cache; first run pulls ~3.8 GB over internet.

## Hardware facts (verified 2026-05-31T14:20 ET)

```
nvidia-smi:
  NVIDIA GeForce RTX 4060 Ti
  Total VRAM: 8188 MiB
  Used now:   2313 MiB (V2 sustained_workload_24h_baseline_v1_n4096)
  Free now:   5637 MiB
  Util:       1%
HF cache C:\Users\marsh\.cache\huggingface\hub:
  Phi-3-mini-4k: NOT FOUND
  (faster-whisper-medium present from other work)
```

## SSH access path

```bash
# From d:/AI/hd-instrument bash, this works:
ssh marsh@home 'nvidia-smi'

# Repo is at C:\dev\hd-instrument on the remote.
# .venv is at C:\dev\hd-instrument\.venv\Scripts\python.exe.

# Testbed scripts live under testbed/ which the remote has via SCP/git;
# verify before launching:
ssh marsh@home 'powershell -NoProfile -Command "Test-Path C:\dev\hd-instrument\testbed\llm_integration\substrate_latency.py"'

# If False, SCP the file(s) over first, OR push to git and pull on remote.
# Remote git may lag — SCP is faster for single files.
```

## Concurrency protocol (mandatory while V2 24h is running)

Until V2 completes (~2026-05-31T21:11 ET, watch
`data/remote_state_cache.json` `runners.gpu_runner_0.current`), follow:

### Before launching ANY GPU work, run:

```bash
ssh marsh@home 'nvidia-smi --query-gpu=memory.free,utilization.gpu --format=csv,noheader'
```

If free < 4096 MiB OR util > 60%, **defer** — V2 is in a memory-hungry phase. Wait 2 min and recheck.

### What is SAFE to run alongside V2 (tiny VRAM, short wall)

- `python -m testbed.llm_integration.substrate_latency --device cuda` (~2-3 min, <1 GB VRAM)
- `python -m testbed.llm_integration.bridge_mlp_scaffold --device cuda` (~30 sec, <500 MB VRAM)

Run these whenever you like; they will not disrupt V2.

### What requires waiting for V2 to finish

- **Phi-3-mini-4bit token-gen** — model load alone is 3.8 GB. Free VRAM during V2 = 5.6 GB so it fits TODAY but leaves V2 only ~1.5 GB for its own growth. Risk: V2 OOMs and the 24h sustained_workload result is lost. **Wait for V2 to finish** before Phi-3 work. Estimated drain: 2026-05-31T21:11 ET.
- **End-to-end integrated forward-pass** — depends on Phi-3, same constraint.

### Failure modes to guard against

- **CUDA OOM kills V2**: if you must run Phi-3 before V2 finishes, set
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:False` and pre-check free VRAM is >4.5 GB. Better: just wait.
- **CUDA contention silent stall**: we just fixed 4 CPU-queue scripts that auto-picked CUDA and hung when V2 monopolized GPU (commit 3ebb009). If your script auto-picks CUDA and V2 has all the SMs, you may see the same hang. The CPU runner heartbeat caught it; testbed has no equivalent watchdog yet. Add a 60-sec wall budget for CUDA init in your scripts and `print(..., flush=True)` after the first GPU op.
- **Concurrent queue conflicts**: testbed running out-of-queue GPU work is INVISIBLE to the gpu_runner_0 schtask. The runner will pick the next queued anchor whenever V2 finishes regardless of testbed activity. If testbed's Phi-3 run is mid-flight when V2 finishes, the runner will START the next anchor (`path_d_latency_profiling_v1_n4096`) ON TOP of testbed's process. **Coordinate via routing file before any GPU work that lasts >5 min after V2's expected finish.**

## Recommended order for Week 0 Missing 7 (given current V2 state)

1. **Right now**: Missing 7 #1 (substrate_latency --device cuda) — safe, ~3 min.
2. **Right now**: Missing 7 #2 (bridge_mlp_scaffold --device cuda) — safe, ~30 sec.
3. **After V2 finishes (~21:11 ET tonight)**: Missing 7 #3 (Phi-3-mini-4bit token-gen) — needs 3.8 GB free VRAM cleanly.
4. **After #3**: Missing 7 #4 (integrated forward-pass) — depends on #3.

The two CPU-safe items (#1, #2) you can ship right now; #3 + #4 wait ~7h.

## Phi-3-mini download

First run on `marsh@home` will pull `microsoft/Phi-3-mini-4k-instruct-bnb-4bit` (~3.8 GB). Internet on the box is OK. Suggested HF env vars:

```
HF_HOME=C:\Users\marsh\.cache\huggingface
HF_HUB_DOWNLOAD_TIMEOUT=600
```

`transformers`, `bitsandbytes`, `accelerate` likely already in `C:\dev\hd-instrument\.venv` — verify with:

```bash
ssh marsh@home 'C:\dev\hd-instrument\.venv\Scripts\python.exe -c "import transformers, bitsandbytes, accelerate; print(transformers.__version__, bitsandbytes.__version__, accelerate.__version__)"'
```

If missing, `pip install` them inside that venv before Phi-3 work.

## Status_log channel

After each Missing 7 measurement lands, `log_event(source='testbed', ...)` so the For-You feed and dashboard surface it. Importance HIGH for PASS/MIDDLE/FAIL verdicts.

## Closing the routing

This file CLOSES `strategy_request_to_strategy_gpu_access_for_week0_missing7_2026-05-31.md`. After you read it, move that file to `notes/routed_completed/` with a one-line append confirming receipt.

## Out of scope (separate decisions)

- Cloud H100 80GB for PP-8 full build ($200-400, 4-6 weeks): deferred decision pending PP-5 latency-budget closure (this routing's deliverable).
- A 24GB-class local GPU was discussed in earlier cap_map text but is NOT present on marsh@home (verified: only the 4060 Ti 8 GB).
