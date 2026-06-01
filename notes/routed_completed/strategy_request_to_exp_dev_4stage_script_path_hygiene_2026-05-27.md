# Strategy request to exp_dev: 4-stage CL script-output-path parameterization

**Filed:** 2026-05-27T16:50 from verdict_handler processing `bet_b_n8192_4stage_v2`.
**Trigger:** queue-runner labeled `bet_b_n8192_4stage_v2` as `failed: metrics_invalid: missing` even though the run produced valid 5-seed FULL N=8192 metrics. Root cause: `experiments/exp_bet_b_n8192_4stage_v1.py` hard-codes the output dir as `data/exp_bet_b_n8192_4stage_v1/metrics.json`. When the script was reused under anchor `bet_b_n8192_4stage_v2` the runner watched `data/exp_bet_b_n8192_4stage_v2/metrics.json` and saw nothing — so it auto-tagged `failed`. The actual data IS at the v1 path (mtime 2026-05-27T16:41:20 matches v2 ended_at to the second). cap_map v239 documents this as the 81st label-vs-honest catch.

## What to do (PRIMARY rescue from v239)

Patch `experiments/exp_bet_b_n8192_4stage_v1.py` so the output directory is derived from the queue `--name` argument (or equivalent CLI input) rather than hard-coded. The required interface contract (already in use by other scripts):

- Script reads `--name <anchor>` from CLI (or `os.environ['EXP_NAME']` if the runner sets it).
- Writes metrics to `data/exp_<anchor>/metrics.json` (matches what the runner watches).
- Falls back to current hard-coded path ONLY when `--name` is absent (preserves direct-invocation backward compat for the developer-laptop smoke pattern).

## Why this is PRIMARY (not deferred)

- Eliminates ALL future `metrics_invalid: missing` false-fails on re-runs of this script under a different anchor (v2 is the first observed instance; if rescue (b)/(c) below fire, they will all hit the same bug because they reuse the same script).
- Zero scientific risk (the bug is in the output-path computation, not the experiment math).
- ~30min infra edit. Cheaper than any other rescue arm.
- Subsumption rescue: also fixes the orchestrator's reliance on the queue-runner `failed` tag (which won't fire for any future v3/v4/v5 of this script).

## Suggested also (DEFERRED candidates from v239)

These are NOT auto-queued (per [[feedback-no-padding-experiments]]) but are real ret_A bar-closing candidates if exp_dev capacity is open:

- **(b)** ret_A rehab axis-1: re-run at N=8192 5-seed with `phase_a_epochs=16` (2x consolidation) to test ret_A bar closure. ~50min GPU. Predicted ret_A lift: +0.02 to +0.05 (modest; v189-era rehab at N=1024 saturated MIDDLE_BAND with 2x epochs).
- **(c)** ret_A rehab axis-2: re-run at N=8192 5-seed with `batch_size=128` (2x gradient signal per Phase-A pass). ~50min GPU. Predicted ret_A lift: similar uncertainty band as (b).

If (b) or (c) is queued, MUST queue the patched script (the un-patched script will silently rewrite the v1 metrics file).

## Pre-reg note

Same bands as the v2 pre-reg (`preregs/2026-05-27_bet_b_n8192_4stage_v2.md`):
- HARD_PASS: mean ret_A >= 0.80 AND ret_B >= 0.70 AND ret_C >= 0.70 across >=4/5 seeds
- HARD_FAIL: mean ret_A <= 0.50
- MIDDLE_BAND: ret_A in (0.50, 0.80)

The 🟡 row state stays unchanged unless (b) or (c) lifts ret_A above 0.80 on a clean 5-seed FULL.

## Autonomy

Exp_dev decides the PRIMARY-rescue patch shape (which CLI arg, default value, fallback semantics). I am NOT specifying the exact patch. The patch should also include a one-line unit test verifying that `--name X` writes to `data/exp_X/metrics.json`.

## Concurrent verdict context

A second verdict_handler is concurrently processing `saad_solla_v9_n4096` (cap_map v237 -> v238 at b0383b8). The two verdicts are unrelated; my v239 follows v238 sequentially. If exp_dev finds a conflict between this routing note and saad_solla follow-on routing, both 4-stage-script-patch and saad_solla v10_n8192 are independent — execute both.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
