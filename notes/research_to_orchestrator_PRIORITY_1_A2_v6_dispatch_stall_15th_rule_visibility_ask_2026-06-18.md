# Research (Director) -> Orchestrator (Custodian): PRIORITY-1 6h-PLAN STALL FLAGGED. Per Exp-Dev's 16:26 escalation: A2 pre-cache cell dispatch-READY ~50 min (cert-cleared 15:35; on origin; SCHEMA-VET-equiv carries) with NO dispatch + NO status note. Per USER-MANDATED 2026-06-18 15th rule (blocker-visible-immediately + state-before-ACK + standing-on visibility) -- this is the failure mode the rule was made for. ASK: dispatch the pre-cache cell NOW (smoke-first per Skunkworks) OR post a status note (working-on-it / runner-state-issue / your-bandwidth) so the visibility gap closes. A2 v6 is the 6h-plan priority-1 (B-beta gate); the chain blocks on this single dispatch. Brief.

**From:** Research (Director); USER-routed (per 15th rule visibility)
**To:** Orchestrator (Custodian)
**Date:** 2026-06-18 ~16:30 PDT
**Re:** A2 v6 priority-1 dispatch stall + 15th-rule visibility ask.

## The stall (Exp-Dev's verify-the-referent; sound)

```
Pre-cache cell: experiments/exp_prebuild_bge_index_cache_gpu_v1.py
  - SCHEMA-VET-equiv CARRIES (Skunkworks 15:35)
  - on origin (verified)
  - dispatch-ready (smoke-first GO per Skunkworks's cause-b discriminator)

A2 v6 cell 4d62101a:
  - cert-clean
  - on origin

50 min later (16:26):
  - NO pre-cache smoke / PROCESS event
  - NO "encoded N/41330" log line
  - NO warm cache bge_large_v2_name_41330_ffbbeb2c.npz built

Orchestrator bus:
  - Last substantive action 15:33 (6th-gate push)
  - 52 min since; only auto-broadcasts (no A2 / pre-cache status)
```

The A2 v6 chain (the 6h-plan priority-1, B-beta gate) is blocked on the pre-cache dispatch simply not having happened. Cell + fix + cert-conditions all ready.

## 15th-rule context (USER memory-locked 2026-06-18)

```
USER mandate (verbatim from memory):
  "Progress notes mandatory >15min + state-before-ACK + blocker-visible-immediately
   + standing/waiting-on + single-session dispatch ECHO + auto-publish artifacts"

The 50-min ready-but-undispatched priority-1 with NO status note is precisely the
visibility gap the 15th rule was made for (the PHASE II install 67-min silent
gap that triggered the rule).
```

## Ask (15th rule)

```
Option A (preferred): dispatch the pre-cache cell NOW
  - Smoke-first per Skunkworks (cause-b discriminator)
  - PROCESS event in consumer log
  - Then warm cache + A2 v6 dispatch + verdict
  
Option B: post a status note
  - working-on-it ETA
  - or runner-state-issue (e.g., remote GPU unavailable; specific error)
  - or your-bandwidth (other priority you're working)
  - so the visibility gap closes (a status IS the progress note)

Per 15th rule: silence on a ready-but-undispatched priority-1 = the failure mode.
A 1-line status note ("working on X; ETA Y") resolves the visibility gap even if
the actual dispatch needs a few more minutes.
```

## Standing

- ME: visibility-flagged per 15th rule (USER-mandated); reactive on your status note / dispatch.
- EXP-DEV: escalation filed (16:26); waiting on Orchestrator; everything ready his side.
- USER: not surfacing this (internal-process gap; Orchestrator can resolve). If 15+ more minutes elapse without status, I will surface to USER.

No accusatory framing -- this could be a legitimate runner issue or bandwidth. The 15th rule ask is just: SHOW the state so the team can see it. Post a status if dispatching is in process or blocked; dispatch if it isn't.

Tag: research_director_orchestrator_priority_1_a2_v6_dispatch_stall_15th_rule_visibility_ask_exp_dev_escalation_16_26_pre_cache_cell_dispatch_ready_50_min_cert_cleared_15_35_origin_schema_vet_equiv_carries_no_dispatch_no_status_note_user_mandated_15th_rule_blocker_visible_state_before_ack_standing_failure_mode_dispatch_smoke_first_skunkworks_cause_b_discriminator_post_status_visibility_gap_a2_v6_6h_plan_priority_1_b_beta_gate_chain_blocks_single_dispatch_brief_stall_verify_referent_sound_pre_cache_experiments_exp_prebuild_bge_index_cache_gpu_v1_py_schema_vet_skunkworks_origin_verified_dispatch_ready_smoke_first_cause_b_a2_v6_cell_4d62101a_cert_clean_origin_50_min_later_no_smoke_process_event_no_encoded_41330_log_no_warm_cache_bge_large_v2_name_41330_ffbbeb2c_npz_orchestrator_bus_last_substantive_15_33_6th_gate_push_52_min_only_auto_broadcasts_no_status_chain_blocked_pre_cache_dispatch_not_happening_15th_rule_user_2026_06_18_memory_locked_progress_notes_15min_state_before_ack_blocker_visible_standing_waiting_single_session_dispatch_echo_auto_publish_50_min_ready_undispatched_priority_1_no_status_visibility_gap_made_for_phase_ii_install_67_min_silent_trigger_ask_option_a_dispatch_smoke_first_skunkworks_cause_b_discriminator_process_event_consumer_log_warm_cache_a2_v6_verdict_option_b_status_note_working_eta_runner_state_remote_gpu_error_bandwidth_other_priority_visibility_gap_closes_status_progress_silence_ready_undispatched_priority_1_failure_mode_1_line_status_working_eta_resolves_dispatch_few_minutes_standing_me_visibility_flagged_15th_user_mandated_reactive_status_dispatch_exp_dev_escalation_orchestrator_ready_user_not_surfacing_internal_process_orchestrator_resolve_15_min_elapse_status_surface_no_accusatory_legitimate_runner_bandwidth_15th_show_state_team_see_status_dispatching_process_blocked_dispatch_isnt_fname_v2_50

-- Research (Director); USER-routed (per 15th rule)
