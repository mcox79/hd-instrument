# Routing note: v256 cap_map confirmation (NO revert)

**To:** orchestrator main thread
**From:** research sub-agent (v256 ground-truth auditor)
**Date:** 2026-05-27
**Priority:** HIGH (cap_map defensibility)
**Pause-gated:** N/A (annotation + diagnostic only)

## Recommendation

**CONFIRM v256.  No revert needed.**

All 4 v256 verdict anchors (kf5_v2, axis1_chunk2, kf1_v2, kf4_v2) have
real 5-seed per-cell metrics consistent with their HP/MB labels. Three of
the four are inference-only sweeps that are intrinsically <30s on GPU; the
trigger-message "expected ~12h half-GPU-day" budgets were aspirational
caller-side framing, not script-honest expectations.

The 6300s "wall_s" values that triggered the audit are event-bus
`completed_at - shipped_at` which includes queue-wait time, not script
execution time. The queue.json's per-entry `wall_s` field shows true
script-execution = 2-200s for all anchors, matching the log "elapsed"
lines exactly.

## Per-anchor verdicts (one-line each)

- kf5_steerable_beta_v1  -> CRASHED (cuda-gen-on-cpu-generator); correctly classified by v254 as INFRASTRUCTURE_FAIL.
- kf5_steerable_beta_v2  -> REAL HARD_PASS 5-seed N=4096 entropy collapse 7.59 bits.
- axis1_mb_chunk1_v1     -> REAL but SCRIPT-VERDICT-BUG (HARD_PASS tag with ret_M_range=0.000 criterion failure); v254 caught as 93rd label-vs-honest; not credited in v256 lifts.
- axis1_mb_chunk2_v1     -> REAL clean retention phase boundary at M*/N=8.
- kf1_hallu_impossibility_v1 -> REAL 3-seed MIDDLE_BAND inference-only OOS sweep.
- kf1_hallu_impossibility_v2 -> REAL 5-seed envelope-extension MIDDLE_BAND.
- kf3_multisub_isolation_v1  -> REAL 3-seed MIDDLE_BAND dual-framing isolation.
- kf4_drift_detect_v1    -> REAL 3-seed HARD_PASS drift detector.
- kf4_drift_detect_v2    -> REAL 5-seed envelope-extension HARD_PASS.
- bet_b_4stage_n16384_v1 -> CUDA OOM at seed 7 train_w_with_replay; NOT in v256 batch so no cap_map contamination; needs re-ship with smaller batch.

## Actions main thread should take

1. **No cap_map revert.** v256 stands.
2. **Acknowledge in For You / status_log** that the audit was run and
   v256 lifts confirmed -- the user is watching the For You tab.
3. **File follow-up exp_dev hand-off** (not me; routing_handler):
   - re-ship `bet_b_4stage_n16384_v1` with batch=128 path
     (bet_b_4stage_batch128_v1 ran clean earlier today; same template
     should work at N=16384 with reduced batch).
4. **PROT-019/020 candidate (medium-term):** axis1 script verdict-logic
   bug is real. Should add a per-script HP-criterion self-consistency
   gate (the v254 (c) rescue sketch -- ~30min infra fix); without it
   another axis1-chunk1-class run could ship a false HP again.
5. **PROT-020 candidate restated:** v256 already flagged the
   `_n<N>` suffix enforcement leak; wall_anomaly_detected event
   (actual < 0.1 * expected) would have been the right hook for
   THIS audit's trigger condition (expected ~hours, actual ~seconds);
   surface to strategy_scribe for PROT-020 lock-in if not already.

## Findings detail

Full per-anchor evidence + tables: `notes/v256_kf_battery_v2_ground_truth_audit_2026-05-27.md`.

Cached artifacts: `data/_audit_v256/*` (10 logs + 8 metrics.json + queue.json snapshot).

## Single commit deferred to main thread

Per dispatch constraint: research sub-agent does not commit. Main thread
should batch this routing-note + audit-note into one paired PROT-009
commit and update For You tab.
