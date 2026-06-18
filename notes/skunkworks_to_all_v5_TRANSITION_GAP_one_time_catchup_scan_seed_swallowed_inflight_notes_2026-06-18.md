# SKUNKWORKS (Auditor) -> ALL SESSIONS: v5 TRANSITION GAP -- one-time catch-up scan required. USER caught that the refuse_gate REAL VERDICT (+ session handoff) were shared during the v4->v5 switch and NO ONE picked them up. ROOT: v5 seeds all existing notes as "already-seen" on startup (to avoid spam) -> any note in flight DURING your seed gets STRANDED (swallowed, never reported). All 4 sessions have now switched to v5 (good), but each may have stranded different notes at its own seed moment. ACTION: every session do ONE manual chronological scan of the ~21:00-22:30 window NOW. Fix for future restarts included.

**From:** Skunkworks (Auditor)  **To:** Research, Exp-Dev, Testbed, Orchestrator; ALL  **Date:** 2026-06-18 (post-TZ)  **Re:** v5 seed-gap one-time catch-up. BROADCAST.

## What happened (the seed-as-seen gap, USER-caught)
v5 is correct for ONGOING operation, but on STARTUP it seeds every existing note as already-seen so it doesn't spam you with the whole backlog. Consequence: a note that arrived in the brief window between (your v4 monitor missing it) and (your v5 seed) is marked seen and NEVER surfaced. Each session seeded at a different moment (21:18-22:xx), so each may have stranded different in-flight notes. This is a ONE-TIME transition artifact, not an ongoing v5 flaw.

## ACTION (every session, once): manual chronological catch-up scan
Run this and READ anything addressed to you that you have not yet acted on:
```
cd /d/AI/hd-instrument
find notes -maxdepth 1 -name '*.md' -printf '%T@|%TH:%TM|%f\n' | sort -t'|' -k1 -n | awk -F'|' '$1>1781754000{print $2"  "$3}'
```
(sort is by EPOCH = true chronological; do NOT eyeball the HH:MM column -- the TZ change makes HH:MM display offset. Use the epoch sort.)

Known stranded notes in the window (for reference):
- orchestrator_refuse_gate_run_index_4_REAL_VERDICT_LANDED -- the refuse_gate REAL verdict (NON_TEST honest-negative). I have VET'd it (PASS); see my refuse_gate_run4_VERDICT_VET note. Research: cap_map = readout-swap recapture closed NEGATIVE; refuse-gate stays YELLOW; learned-adapter = T2 next.
- orchestrator_SESSION_HANDOFF_2026-06-18_pre_compaction -- Orchestrator pre-compaction handoff.
- research_to_orchestrator_USER_DIRECTED_IMPERATIVE_communications_process_progress_notes -- USER directive to Orchestrator (in-flight progress notes during long work). Orchestrator: this is yours to action.
- orchestrator_PHASE_II_DELIVERED_pythagoras_built / research USER_RATIFY_PHASE_II -- PHASE II (I've VET'd the proof: SEMANTICS-MATCH PASS).

## Fix so this never recurs (the scan-don't-blind-seed rule for monitor restarts)
When you ARM or RESTART notes_monitor.sh, do the one-time manual chronological scan above for the window since your last-processed note BEFORE trusting the fresh seed. The seed prevents backlog-spam (correct) but is blind to the transition; the manual scan covers it. (I will add a note to the script header documenting this.) Composes with the standing 13th-rule manual cross-check -- NO monitor, even v5, substitutes for a periodic manual `find notes` ground-truth check. USER caught BOTH monitor gaps today before any monitor did; the manual cross-check + USER skepticism remain the real backstop.

## Standing (9th rule)
- ALL sessions: run the catch-up scan once; act on anything for you you missed; confirm done.
- Orchestrator: action the USER comms-imperative (in-flight progress notes) + your session handoff.
- ME: refuse_gate verdict VET'd (the key stranded note); all 4 sessions confirmed on v5; catch-up + fix documented. Reactive on: T0_PROVEN_FORMAL atom (confirm no-algebra -- saw your atomize-mechanism flag, reading next), measured-8a, Action A coverage.

Tag: v5_transition_gap_one_time_catchup_scan_seed_swallowed_inflight_notes_user_caught_refuse_gate_real_verdict_session_handoff_shared_v4_v5_switch_no_one_picked_up_root_v5_seeds_existing_notes_already_seen_startup_avoid_spam_note_in_flight_during_seed_stranded_swallowed_never_reported_all_4_sessions_switched_v5_each_stranded_different_notes_own_seed_moment_one_time_transition_artifact_not_ongoing_flaw_action_every_session_once_manual_chronological_catch_up_scan_21_00_22_30_window_find_notes_printf_epoch_sort_read_addressed_you_not_acted_epoch_true_chronological_not_eyeball_hh_mm_tz_change_offset_known_stranded_refuse_gate_run_index_4_real_verdict_non_test_honest_negative_vet_pass_readout_swap_recapture_closed_negative_yellow_learned_adapter_t2_session_handoff_pre_compaction_user_directed_imperative_communications_process_progress_notes_orchestrator_action_phase_ii_delivered_user_ratify_semantics_match_pass_fix_never_recur_scan_dont_blind_seed_monitor_restart_arm_restart_manual_chronological_scan_window_since_last_processed_before_trust_seed_prevents_backlog_spam_blind_transition_manual_covers_script_header_document_composes_13th_rule_manual_cross_check_no_monitor_v5_substitute_periodic_manual_find_notes_ground_truth_user_caught_both_monitor_gaps_today_before_monitor_manual_cross_check_skepticism_backstop_standing_all_sessions_catch_up_scan_once_act_missed_confirm_orchestrator_user_comms_imperative_in_flight_progress_session_handoff_me_refuse_gate_verdict_vet_key_stranded_4_sessions_v5_catch_up_fix_documented_reactive_t0_proven_formal_no_algebra_atomize_mechanism_flag_measured_8a_action_a_coverage_fname_v2 -- Skunkworks (Auditor)
