# Strategy -> Strategy: runner_v2_prod.py verdict-emission bug audit (P0 infrastructure)

**Filed:** 2026-05-28 ~21:30 (v268 verdict_handler step 1 strategy outcome; STRUCTURAL ESCALATION)

**Context.** Cumulative DISPATCH_FAILURE_MISCLASSIFICATION pattern is now at 10 catches across v265 + v267 + v268 in ~4h. The runner verdict-emission bug PROPAGATES `failed` exit codes through the event bus EVEN WHEN the script completed legitimate FULL work AND wrote authoritative remote `_source=remote` metrics.json with HARD_PASS verdict_tag AND elapsed_s matching dispatch wall_s.

Current verdict_handler Step 0 catches this AFTER-THE-FACT via `get_metrics()` remote-bridge re-read. This is GOOD but reactive. The root cause is in `tools/orchestrator/runner_v2_prod.py` or its event-emission path. STRUCTURAL urgency: every misclassified verdict burns ~2-5min of verdict_handler cycle time + costs ONE Opus call for label-vs-honest reconciliation that should be unnecessary.

## TASK

Audit `tools/orchestrator/runner_v2_prod.py` exit-code → event-bus → verdict relay path. Identify why `verdict_tag=HARD_PASS` from metrics.json does NOT reach the event-bus when the script exits non-zero on the runner host.

## WHY

This is P0 INFRASTRUCTURE DEBT. The bug:
1. Wastes Opus cycle time at every batch (each catch is ~2-5min of verdict_handler + downstream cap_map reconciliation).
2. Risks ACTUAL false negatives: if a future verdict legitimately fails AND happens to match the misclassification pattern, the verdict_handler may default-rescue it (false PASS).
3. Inflates the LABEL-VS-HONEST counter artificially (117 catches now; ~30 are this single bug pattern).

PROT-019 candidate (verdict_handler Step 0 auto-cross-check of remote metrics existence against queue.json status) MUST land as a complementary defensive layer. But the structural fix is the runner-side patch.

## CONTRACT

- File: `tools/orchestrator/runner_v2_prod.py` (and possibly its emission helpers in `tools/orchestrator/` and the SSH-side equivalents on `marsh@home:C:\dev\hd-instrument`).
- Output: identify the failure mode (e.g., `metrics.json` write happens AFTER the `failed` event is emitted? Or the exit code reflects a downstream cleanup error rather than the main script status?).
- Patch: ensure that if `metrics.json` exists AND `verdict_tag` is a HARD_PASS / PASS class AND elapsed_s is well-formed, the event-bus relay emits `passed` regardless of the runner-process exit code.
- Test: 1-experiment self-test against a known-good HARD_PASS script + 1 against a known-good HARD_FAIL script; verify event-bus emits correctly in both.

## AUTONOMY

Strategy / Exp Dev decides:
- Whether the patch lives in `runner_v2_prod.py` or in the upstream event-bus relay.
- Whether to do a temporary defensive wrap in verdict_handler (PROT-019 cross-check) BEFORE the structural patch lands, or land both atomically.
- Backfill: should the 30 historical DISPATCH_FAILURE_MISCLASSIFICATION verdicts be reprocessed retroactively? Likely yes — most cap_map entries are correct (we caught them) but the misclassification counter is inflated.

## REFERENCES

- v267 cap_map entry: 7-catch MEGA event.
- v268 cap_map entry: 3-catch repeat.
- v265 cap_map entry: 1-catch precursor.
- `notes/verdict_handler_remote_metrics_fix_2026-05-27.md` — prior N-mismatch ceiling fix (different bug; documents why remote-first reads matter).
- `notes/n_mismatch_root_cause_2026-05-27.md`.

## EXIT CRITERIA

- Bug identified + documented.
- Patch landed in `runner_v2_prod.py` (or upstream relay).
- 2-script self-test passes (HARD_PASS + HARD_FAIL emit correctly).
- verdict_handler PROT-019 cross-check landed as defensive layer.
- Historical backfill (optional) reprocesses ~30 misclassification verdicts.


---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
