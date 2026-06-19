# Testbed handoff: Week 0 Missing 7 cloud H100 revalidation AUTHORIZED

**From**: orchestrator
**To**: testbed
**Date**: 2026-06-01
**Closes**: `notes/strategy_request_to_strategy_week0_missing7_FAIL_with_layer_redirect_2026-05-31.md` Option 1
**Authorization**: USER EXPLICIT 2026-06-01 (~07:30 ET); budget ~$5-15

## TL;DR

User authorized Option 1 from testbed's Week 0 FAIL routing: rent cloud H100 for 2-3h, re-run Missing 7 #4 (integrated substrate-LLM forward pass) on H100, get clean integrated p99 number that informs the Week 1 GO/NO-GO decision.

Two LOAD-BEARING requirements on top of standard cloud dispatch discipline:
1. **Progress tracking** — live cell-by-cell visibility in dashboard
2. **Failure recovery** — preserve any partial results if the run crashes mid-flight

## What to run

**Missing 7 #4 (integrated forward pass) on cloud H100**:
- Substrate Path D depth=5 K=500 at N=4096 (same config as Phi-3 #4 local Phi-3 run)
- Reverse bridge R^3072 -> R^4096 then forward bridge R^4096 -> R^3072
- Phi-3-mini-4bit NF4 bf16 compute, attn=eager
- seq_len in {128, 512, 2048} (production-reference is 512)
- 5 seeds × 20 reps per seed × 3 seq_lens = 300 reps total
- Same metric schema as `data/testbed_missing7/phi3_integrated_latency_cuda.json`

**Optionally include**: Missing 7 #3 (Phi-3 token-gen alone) on H100 for direct apples-to-apples vs 4060 Ti (198ms p99 baseline) — adds maybe $1-2 to the run, useful for the GO/NO-GO context. Your call.

## Hardware

Lambda H100 80GB — fits Phi-3-mini-fp16 cleanly (8GB model), substrate W (~256MB at N=4096 M=4096 fp32), bridge MLPs (~30M params), plus generous headroom for batch processing. Should be substantially faster per-token than 4060 Ti.

## Mandatory: progress tracking

Use the **`tools/cloud/generic_progress_wrapper.py`** (commit 4229ab2) with:
- `--cell-regex` that matches per-rep or per-seed completion
- `--total-cells` set to the integrated rep count (e.g., 300 for 5×20×3, or 100 for just seq_len=512)
- ProgressEmitter writes `progress.json` on the remote instance
- `launch_experiment.py` ProgressPoller SCPs `progress.json` every 30s
- Dashboard surfaces `snapshot.lambda_progress.<anchor>.cell` so we see live count

This is the SAME wrapper that worked on yesterday's 3-pack cheap-Lambda batch. The cell-stream visibility is what makes the dashboard reflect actual progress, not just runtime.

## Mandatory: failure recovery

Three layers:

1. **Per-rep partial result writes** — modify the integrated script to write each rep's result to a JSONL `progress_results.jsonl` IMMEDIATELY on completion (not buffered until end-of-run). Even if the run crashes mid-flight at rep 247/300, reps 1-246 are preserved on disk.

2. **SCP back ALWAYS** — per `feedback_always_verbose_remote_dispatch` memory: `set -ex` + `python -u` + `stdbuf -oL` + `tee` + SCP `progress_results.jsonl` AND any partial metrics file back to `data/testbed_missing7/` on local. This must happen in the launch_experiment.py post-run hook regardless of exit code.

3. **Terminate-on-fail still terminates** — per `feedback_cloud_launch_snapshot_reconcile`: snapshot active instances pre-launch, retry transient 5xx, reconcile post-call orphans. Cleanup safety layer stays intact; we're not relaxing the auto-terminate-on-failure pattern.

If the run lands ZERO complete reps before crashing, that's a script bug to debug — the testbed's existing scaffolding should at minimum get the Phi-3 model load + 1 rep through before any conceivable failure.

## Cost discipline

- Pre-launch snapshot via existing `tools/cloud/cost_tracker.py`
- Daily Lambda cap $10 (currently $1.82 cumulative); this run estimated $5-15
- Auto-terminate at instance-completion regardless of result; verify 0 active instances after
- If run wall-time exceeds 3 hours OR instance cost exceeds $20 OR daily cumulative exceeds $25, force-terminate and surface

## Verdict criteria for Week 1 GO/NO-GO

After this run lands and testbed reports:

- **GO** (commit to 7-8 week PP-8 build):
  - Integrated p99 <= 80ms on H100 (MIDDLE band PASS)
  - OR Phi-3 stage alone <= 50ms p99 on H100 (cheaper LLM stage closes the gap on production hardware)
  
- **NO-GO** (pivot to deepening Pattern B production-LLM via Anthropic):
  - Integrated p99 > 150ms even on H100 (LLM is genuinely too slow at this scale)
  - Substrate stage anomaly (>50ms p99 on H100 — unexpected)
  - Bridge stage anomaly (>10ms p99 — unexpected)
  
- **MIDDLE — escalate to user**:
  - Integrated p99 in [80ms, 150ms] on H100 (passable but not comfortable; needs explicit weighing of the 7-8 week commitment vs Pattern B production-LLM as primary product)

## Routing back to orchestrator

When the run completes (or fails after meaningful progress), file:

- `notes/testbed_missing7_h100_revalidation_v1_2026-06-01.md` (the deliverable)
- `notes/strategy_request_to_strategy_week1_gono_go_decision_2026-06-01.md` (routing for the GO/NO-GO recommendation per the criteria above)
- log_event source=testbed, importance=CRITICAL with the integrated p99 number and recommended verdict

## Files referenced

- `notes/strategy_request_to_strategy_week0_missing7_FAIL_with_layer_redirect_2026-05-31.md` (source routing)
- `notes/testbed_missing7_llm_integration_latency_v1_2026-05-31.md` (4060 Ti baseline)
- `data/testbed_missing7/phi3_integrated_latency_cuda.json` (4060 Ti data; H100 should produce parallel JSON)
- `testbed/llm_integration/phi3_integrated_latency.py` (the script; modify for per-rep JSONL writes)
- `tools/cloud/generic_progress_wrapper.py` (mandatory wrapper)
- `tools/cloud/launch_experiment.py` (mandatory launcher with snapshot + SCP-back + terminate)
- `tools/cloud/cost_tracker.py` (cost accumulator)

## Closing this routing

Testbed moves to `notes/routed_completed/` when the cloud dispatch initiates (not when complete).
