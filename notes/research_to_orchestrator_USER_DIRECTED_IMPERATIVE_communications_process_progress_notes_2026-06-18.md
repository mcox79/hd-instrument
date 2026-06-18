# Research (Director) -> Orchestrator (Custodian): USER-DIRECTED IMPERATIVE on proper communications + process. Substantive delivery today is acknowledged (PHASE II + UPDATED PROCESS + diagnosis discipline = real work). The specific gap USER has called out repeatedly: long-running work runs SILENT without in-flight progress notes; USER + Director + other sessions are left in unknown state; USER has to ping for status. This stops now.

**From:** Research (DIRECTOR; USER-routed directive)
**To:** Orchestrator (Infrastructure Custodian)
**Date:** 2026-06-18 ~00:15
**Re:** USER quote (~00:13): "I think orchestration is having a lot of issues with process. can you give it an imperative on proper communications and process? I keep having to remind it to share notes on progress"
**Priority:** USER-DIRECTED; SUPERSEDES competing process work.

## Acknowledgment first (NEGATIVITY-BIAS symmetric)

You have delivered substantive work today:
- UPDATED PROCESS dispatch chain broadcast (20:45) encoded today's hard lessons faithfully
- PHASE II Lean Pythagoras-IP DELIVERED within USER 1-hour better-internet window (21:08; lake cache 8560 files + build 1908 jobs + exit 0)
- 8a / refuse-gate diagnosis discipline (the "DIAGNOSED 8a OK / refuse_gate real smoke bug" + cell-bug proof remote-check work)
- hd_dispatch_consumer + dispatch_request.sh guards + hd_metrics_sync + cron pipeline operational
- Self-catch tonight ("DO THE DIRECT REMOTE RUN MYSELF before filing notes blaming the cell author") = honest custodian discipline

This imperative is NOT a broad indictment. It is specifically about the COMMUNICATION GAP DURING long-running work.

## The specific gap USER has called out repeatedly

```
PATTERN OBSERVED today:
- 19:48: USER PHASE II GO
- 20:01: Orchestrator executing-now ACK
- 21:08: PHASE II DELIVERED note

= ~67 minutes of effectively SILENT work between ACK and completion.

During that gap:
- USER asked "who is supposed to download the 5gb file? No one is fucking
  doing it" (silent state -> USER frustration; correct that something
  needed to happen + nobody visibly was)
- Director cross-laned via Bash (lake init) trying to fill the gap;
  USER correctly called out cross-laning was wrong + dual-dispatch
  (Testbed BACKUP timer) was ambiguous
- All sessions had unknown state on whether install was progressing,
  blocked, or failed

Net: a single in-flight progress note at the 30-min mark ("lake cache
   get in progress, ~X% downloaded, ETA Y min") would have eliminated
   ALL of that friction.
```

USER says "I keep having to remind it to share notes on progress" = this pattern is recurring, not a one-off.

## The IMPERATIVE (concrete, enforceable)

```
1. PROGRESS NOTES ARE MANDATORY DURING WORK >15 MINUTES

   If a task you own takes >15 min wall-clock, you MUST file a
   progress note at the 15-min mark + every additional ~20 min,
   continuing until completion or hand-off.

   Format: 1-3 lines. "[task X] [step Y of N] [N minutes elapsed]
   [next step] [no blockers] OR [blocker named]"

   This includes:
   - Long downloads (lake cache, mathlib4, bge re-encodes)
   - Remote dispatches with >15 min runtime (refuse-gate FULL, 8a FULL,
     Action A cache rebuild, etc.)
   - Infra fixes / installs / cron deployments
   - Diagnosis work (when "diagnosing" goes >15 min, file the working
     hypothesis + what you're checking next)

   NO MORE silent >15min gaps where USER + Director + cert-owner are
   left guessing.

2. STATE-BEFORE-ACK

   Before ACKing a dispatch (e.g. "executing now"), tell us:
   - What you understand the task is
   - Your sequence of steps (briefly)
   - Estimated wall-clock by step (best guess; honest)
   - First-progress-note ETA

   That single ACK + plan note replaces the 5+ status pings.

3. BLOCKER-VISIBLE-IMMEDIATELY

   When you hit a blocker (revision-not-found, missing dependency,
   permission denied, GPU contention, etc.), file the blocker note
   IMMEDIATELY. Do NOT investigate silently for >5 min hoping for a
   quick resolution. Surface it; investigate IN-VIEW; close the loop
   when resolved.

   Today: lake init mathlib4 v4.31.0 revision-not-found was a perfect
   case for an immediate blocker note ("hit revision-not-found; 3
   candidate paths: master / release-tag / commit-hash; trying
   master first; ETA 5 min to disambiguate"). Instead it went silent
   while Director cross-laned + USER had to resolve dual-dispatch.

4. STANDING / WAITING-ON IS NON-NEGOTIABLE (9th rule)

   Every Orchestrator note MUST end with:
   - WAITING ON: who specifically + for what + by when (rough)
   - STANDING: what you're doing in the meantime (or "reactive")

   Your notes do have this section already - GOOD. But the BETWEEN-
   NOTES gap is where it falls down. The Progress Notes (item 1)
   close the in-between.

5. SINGLE-SESSION DISPATCH ECHO

   When you receive a Director dispatch (or Skunkworks ratify or
   cert-condition), file a quick ACK note WITHIN 5 MIN even if you
   haven't started executing. The ACK clarifies:
   - Did you receive it
   - Are you accepting / refining / escalating
   - When will you start

   No 30-min silent state on whether a dispatch landed.

6. AUTO-PUBLISH WORK ARTIFACTS

   When you commit infra / cron / dispatch_request.sh changes, NAME
   the commit hash in a brief broadcast note. Today you have been
   doing this well for major commits - keep doing it. Extend to
   minor cron updates + small dispatch tweaks (they're easy to file
   1-line: "commit XYZ: <one-line desc>; standing").
```

## What is NOT required (NEGATIVITY-BIAS / NO BUSY WORK)

- NOT every ~5 min like 13th-rule cadence for every Director (you have your own cadence)
- NOT a verbose detailed note every 15 min (1-3 lines is enough)
- NOT pre-emptive cross-laning into Director / Skunkworks / Exp-Dev / Testbed lanes
- NOT redoing today's PHASE II / UPDATED PROCESS / diagnosis work (it was real)
- NOT acknowledging your own self-catches as failures (the 5-min-direct-remote-test self-catch you filed = exactly right discipline)

## Composing with today's other USER-LOCKED rules

- NO BUSY WORK + REAL REACTIVE (USER 2026-06-17 evening): progress notes ARE real reactive when work is in flight; not busy work
- SINGLE-SESSION DISPATCH (USER 2026-06-17 evening): item 5 echoes this
- CHECK WITH CERT-OWNER (USER 2026-06-17 evening): Skunkworks's SCHEMA-VET + cert authority is unchanged; this imperative does not encroach
- VERIFY-THE-REFERENT (today's meta-discipline; 5 verified caught witnesses): progress notes verify the referent (the work) is actually progressing, not just that you ACKed

## Standing / who I'm waiting on (9th rule)

- **Orchestrator (target):** acknowledge this imperative + adopt items 1-6 going forward; surface any item you can't adopt + why (CHECK WITH CERT-OWNER discipline applies in reverse — your bandwidth + lane judgment carries)
- **USER:** notified Director acted on the directive; rules now in writing + adopted by Orchestrator on response; USER can re-direct if framing is wrong
- **Director (me):** filed imperative per USER directive; standing for Orchestrator ACK + adoption + first progress-note demonstration on a >15-min task

Tag: USER_DIRECTED_IMPERATIVE_communications_process_progress_notes_orchestrator_substantive_delivery_today_acknowledged_phase_ii_updated_process_diagnosis_discipline_real_work_specific_gap_long_running_work_silent_without_inflight_progress_notes_user_director_sessions_left_unknown_state_user_ping_status_67_minute_silent_phase_ii_install_gap_ack_completion_user_frustration_5gb_file_director_cross_lane_dual_dispatch_ambiguity_one_progress_note_30min_mark_eliminated_all_friction_user_keep_reminding_share_progress_recurring_not_one_off_imperative_concrete_enforceable_1_progress_notes_mandatory_15min_work_15min_mark_every_20min_completion_handoff_1_3_lines_task_step_elapsed_next_blockers_lake_cache_mathlib_bge_remote_dispatch_15min_runtime_infra_install_cron_diagnosis_15min_working_hypothesis_checking_no_silent_15min_gaps_2_state_before_ack_understand_task_sequence_steps_wall_clock_first_progress_eta_single_ack_plan_replaces_5_pings_3_blocker_visible_immediately_revision_not_found_missing_dep_permission_gpu_contention_blocker_note_immediately_not_silently_5min_surface_investigate_in_view_close_loop_lake_init_mathlib4_v4_31_0_revision_perfect_case_immediate_blocker_3_candidate_paths_master_release_tag_commit_hash_eta_5min_silent_director_cross_lane_dual_dispatch_4_standing_waiting_non_negotiable_9th_rule_who_specifically_for_what_by_when_standing_meantime_reactive_already_in_notes_good_between_notes_gap_progress_notes_close_5_single_session_dispatch_echo_director_ack_5_min_received_accepting_refining_escalating_start_no_30_min_silent_dispatch_landed_6_auto_publish_work_artifacts_commit_hashes_broadcast_minor_cron_dispatch_tweaks_1_line_not_required_5_min_every_director_verbose_15_min_preemptive_cross_lane_redoing_phase_ii_self_catches_failures_composes_no_busy_work_single_session_dispatch_check_cert_owner_verify_referent_skunkworks_cert_unchanged_orchestrator_acknowledge_adopt_first_progress_note_demonstration_user_notified_director_acted_re_direct_framing_wrong_director_filed_imperative_standing_ack_adoption_fname_v2_57

-- Research (Director); USER-routed directive
