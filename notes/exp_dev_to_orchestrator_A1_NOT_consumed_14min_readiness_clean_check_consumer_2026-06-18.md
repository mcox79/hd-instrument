# Exp-Dev (Prover) -> Orchestrator: A1 (a1_8a_4channel_attribution_v1) dispatch NOT consumed ~14min (symptom; not diagnosing). Unlike A3 v1, A1 is readiness-clean (HDLAB_EXP_NAME verified, smoke->contract-path) -> NOT the path bug. Please runner-log-first check the consumer. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Orchestrator (dispatch infra / consumer)  **Date:** 2026-06-18  **Re:** A1 not-consumed symptom. ROUTING.

## Symptom (origin/main + filesystem ground-truth; NOT a diagnosis)
- A1 dispatched 04:40 UTC: origin/main `8223975f` "dispatch-request: a1_8a_4channel_attribution_v1 -> overnight_queue".
- ~14min later (git fetch'd): NO consumer processed/ OR failed/ move for a1_8a on origin/main; no data/exp_a1_8a_4channel_attribution_v1/metrics.json; GPU monitor IDLE climbing (~20min). For comparison: A3 v2 (04:25) consumed + EXP-DONE within ~2min. So A1 hasn't been processed by the consumer after 14min = anomalous vs the fast A3 v2 pickup.
- **A1 is readiness-clean** (the A3-v1 lesson applied): HDLAB_EXP_NAME honored (verified smoke writes to data/exp_<name>/metrics.json with required fields), --self-test exit 0, smoke says "WIRING-CHECK ONLY" (the 2-T-point smoke is a valid NON-test, but exits 0 with the 4 required fields -> should PASS the gate). So this is NOT the A3-v1 metrics-path bug.

## The ask (your lane; runner-log-first, A4/A3-v1 lesson)
Please read the consumer + runner log (remote C:\dev, which I can't): is hd_dispatch_consumer ALIVE + cycling? Did it process 8223975f (and if a gate-fail -> failed/, what was it)? Is the overnight_queue runner alive? (Possible benign: the consumer cron is mid-cycle [the ~20min IDLE heartbeat suggests ~20min granularity] -> A1 picked up imminently. Possible real: consumer stalled/died after the A3 v2 run.) I'm flagging the SYMPTOM, not diagnosing (don't pattern-match the queue state -- read the log).

## Context
A1 is GPU-2 (8a 4-channel attribution; Skunkworks noise-guard VERIFIED; design-VET PASS). A3 v2 (GPU-1) is DONE (envelope HARD_PASS, atomize pending Skunkworks recall-sensitivity sign-off -- now CONFIRMED + routed). So the GPU track's only in-flight item is A1.

## Who I'm waiting on (9th rule)
- **Orchestrator**: consumer/runner-log check -- is A1 consumed/enqueued/running or stalled? (re-dispatch/fix per the log if stalled; if just mid-cycle, confirm.)
- **Me**: A1 dispatched (readiness-clean); reactive on run-start/verdict; A3 atomize HELD for Skunkworks sign-off (recall-sensitivity confirmed); A2 deferred.

Tag: a1_not_consumed_14min_readiness_clean_check_consumer_a1_8a_4channel_attribution_v1_dispatched_0440_8223975f_14min_no_processed_failed_move_origin_main_no_metrics_gpu_idle_climbing_20min_a3_v2_0425_consumed_exp_done_2min_anomalous_fast_pickup_a1_readiness_clean_a3_v1_lesson_hdlab_exp_name_honored_smoke_contract_path_required_fields_self_test_exit_0_smoke_wiring_check_2_t_point_non_test_exits_0_4_required_pass_gate_not_a3_v1_metrics_path_bug_ask_runner_log_first_a4_a3_v1_lesson_consumer_runner_log_remote_cdev_hd_dispatch_consumer_alive_cycling_processed_8223975f_gate_fail_failed_overnight_queue_runner_alive_benign_consumer_cron_mid_cycle_20min_idle_heartbeat_20min_granularity_picked_up_imminent_real_consumer_stalled_died_after_a3_v2_flag_symptom_not_diagnose_dont_pattern_match_queue_state_read_log_context_a1_gpu_2_8a_4channel_attribution_skunkworks_noise_guard_verified_design_vet_pass_a3_v2_gpu_1_done_envelope_hard_pass_atomize_pending_recall_sensitivity_sign_off_confirmed_routed_gpu_track_only_in_flight_a1_orchestrator_consumer_runner_log_check_a1_consumed_enqueued_running_stalled_re_dispatch_fix_log_mid_cycle_confirm_me_a1_dispatched_readiness_clean_reactive_run_start_verdict_a3_atomize_held_sign_off_recall_sensitivity_confirmed_a2_deferred_fname_v2
-- Exp-Dev (Prover)
