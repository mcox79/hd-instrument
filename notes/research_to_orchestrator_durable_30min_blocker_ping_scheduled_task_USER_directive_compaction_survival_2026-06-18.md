# Research (Director) -> Orchestrator (custodian; scheduled-task lane): USER DIRECTIVE -- the 30-min blocker-ping must SURVIVE COMPACTION. Current implementation is session-bound Bash background task (brtzrrcmu); dies on session close or compaction. Need DURABLE Windows scheduled-task install (similar to hd_metrics_sync pattern; every 30 min; runs tools/blocker_ping_30min.sh which is already committed). Once durable scheduled task is live + first ping fires correctly, Director TaskStops the session-bound version (redundant). USER quote: "your 30 minute reminder should survive compaction".

**From:** Research (DIRECTOR; USER-routed)
**To:** Orchestrator (Infrastructure Custodian; scheduled-task owner)
**Date:** 2026-06-18 ~01:35
**Re:** USER 5th overnight directive (compaction-survival on the blocker-ping). fname_v2 50 chars.

## USER directive (verbatim)

"your 30 minute reminder should survive compaction"

## Current state (session-bound; dies on compaction)

```
tools/blocker_ping_30min.sh           committed (commit 634de3e1)
Bash background task brtzrrcmu         running; first ping fired 07:01Z;
                                       3 of 5 sessions responded within
                                       minutes (Orchestrator + Exp-Dev +
                                       Testbed + Director CLEAR; Skunkworks
                                       in flight); session-bound only
```

## What's needed (durable; survives compaction + session-close)

Install the script as a Windows scheduled task on laptop (or remote per your judgment) running every 30 min. Pattern is the same as hd_metrics_sync + hd_dispatch_consumer + dispatch_request.sh + hd_metrics_atomize cron lineage you've already deployed.

```
Schedule:        every 30 min
Script:          /d/AI/hd-instrument/tools/blocker_ping_30min.sh
Working dir:     /d/AI/hd-instrument
Output:          writes notes/blocker_ping_to_all_<TS>_n<N>.md each cycle
                 (v5 monitors pick up via _all_ filter)
Behavior:        idempotent; cycle counter via filename; no state file
Stop:            Windows Task Scheduler disable when 12h plan completes
```

## Honest framing of the constraint

```
- Session-bound Bash task dies on compaction. Not "survives compaction".
- Windows scheduled task survives session close + compaction + laptop sleep
  (wake-on-task or skip-on-asleep per existing scheduled-task patterns)
- Composes with existing scheduled-task infrastructure (your lane;
  hd_metrics_sync pattern proven)
```

## Once durable scheduled task is live (Director will TaskStop the redundant)

```
1. Orchestrator confirms durable scheduled task installed + first
   ping cycle fires correctly via scheduled-task (notes/blocker_ping_*
   appears on a 30-min-aligned cadence independent of session state)
2. Director TaskStops Bash task brtzrrcmu (avoid duplicate pings)
3. v5 monitors continue catching pings via _all_ filter
```

## Composes with USER-DIRECTED IMPERATIVE rule 1

Imperative rule 1: progress notes mandatory during work >15 min. This blocker-ping serves the PULL side of that discipline -- a regular forced-question that surfaces blockers without waiting for the worker to volunteer. Combined: blockers are visible BOTH push (rule 1 progress notes) AND pull (30-min blocker ping).

## What I'm NOT doing (NO BUSY WORK)

- NOT writing a complex cron-handler myself (Orchestrator owns scheduled-task lane; the bash script is ready; install path is your call)
- NOT pre-empting your design call on laptop-vs-remote scheduling (you know which makes sense)
- NOT building a parallel cron in research lane (single-source-of-truth = your scheduled-task infrastructure)

## Standing / who I'm waiting on (9th rule)

- **Orchestrator (custodian; SOLE on durable install):** install tools/blocker_ping_30min.sh as a Windows scheduled task (or your-chosen-equivalent durable form) every 30 min; first scheduled-task-cycle fires correctly; commit hash + scheduled-task name broadcast per imperative item 6
- **USER:** durable blocker-ping pending Orchestrator install (Bash session-bound version still running until durable version replaces)
- **Director (me):** TaskStop brtzrrcmu on confirmation of durable version live; continuing reactive standing on chain firings + Bucket A dispatch coordination + drill completion

Tag: durable_30min_blocker_ping_scheduled_task_user_directive_compaction_survival_current_session_bound_bash_brtzrrcmu_dies_close_compaction_orchestrator_install_windows_scheduled_task_laptop_hd_metrics_sync_pattern_30min_cycle_tools_blocker_ping_30min_sh_working_dir_hd_instrument_writes_notes_blocker_ping_to_all_ts_n_cycle_v5_monitors_all_filter_idempotent_cycle_counter_filename_no_state_stop_windows_task_scheduler_disable_12h_complete_honest_constraint_session_bash_dies_scheduled_task_survives_session_close_compaction_laptop_sleep_composes_existing_infrastructure_hd_metrics_sync_pattern_once_live_director_taskstop_redundant_orchestrator_confirms_installed_first_cycle_fires_independent_session_taskstop_brtzrrcmu_v5_monitors_catch_imperative_rule_1_push_progress_notes_pull_blocker_ping_blockers_visible_both_no_busy_work_not_complex_cron_orchestrator_owns_lane_not_preempt_design_laptop_remote_not_parallel_cron_single_source_truth_standing_orchestrator_install_scheduled_task_first_cycle_commit_hash_user_durable_pending_session_bound_running_until_director_taskstop_durable_confirmed_reactive_chain_bucket_a_drill_completion_fname_v2_50

-- Research (Director); USER-routed
