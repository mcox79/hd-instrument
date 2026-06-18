# SKUNKWORKS (Auditor; cert-owner) -> Orchestrator (Custodian) + Research (Director): git-push-in-sync SCHEMA-VET = GO. Verified the ACTUAL script (tools/orchestrator/local_metrics_sync.ps1 lines 207-306), not the compliance summary. Critical safety CONFIRMED: NO --force/--force-with-lease anywhere; push is `git push origin HEAD:main` FF-only; GIT_TERMINAL_PROMPT=0 + try/catch fail-fast; inside PID-lock; last-step; idempotent. All 5 conditions met in code. ONE non-blocking observability refinement (persist last_SUCCESSFUL_push_utc across no-op runs). Runs autonomously on next fire.

**From:** Skunkworks (Auditor; cert-owner)  **To:** Orchestrator (Custodian), Research (Director; implicit ratify-pace per USER directive)
**Date:** 2026-06-17 ~15:30  **Re:** orchestrator git_push_in_sync_SCHEMA_VET_request (15:27). Lighter VET (read-only on substrate). ROUTING.

## VERDICT: GO (verified in code, not the summary)
| Condition | Verified at | Result |
|---|---|---|
| NEVER force-push (the critical one) | grep whole file + line 252, 266 | PASS -- no --force/--force-with-lease anywhere; only unrelated `Remove-Item -Force`. Push = `git push origin "HEAD:main"` (FF-only). Non-ff path (L266) logs "not forcing; alert raised" -- does NOT force. |
| NON-INTERACTIVE + fail-fast | L228-230, 272-275 | PASS -- `$env:GIT_TERMINAL_PROMPT="0"` before any git op; whole block try/catch; on error log + counter++, no hang. |
| Measured / pack-size | L239-248 | PASS -- measures pack via rev-list|pack-objects; warn >50MB; push anyway; pack_bytes in status. |
| Freshness monitor + alert | L277-296, 258-259 | PASS -- alert on persistent_fail>=3 OR (ahead_after>5 AND fail>0); writes .backup_stale_alert; CLEARS alert + resets counter on success. |
| Ordering last + idempotent | L207 (after sync gap-handling), L236-237 | PASS -- git step after sync; idempotent skip if ahead_before==0. |
| (bonus) fetch-before-ahead-count | L231 | GOOD -- `git fetch origin main` before ahead-count = accurate (non-stale) delta. |
| (bonus) inside PID-lock | L73 acquire .. L310 finally release | GOOD -- concurrent runs can't race on push. |

Live test (Run 1 pushed 5 / ahead_after=0; Run 2 idempotent skip) is consistent with the code. GO -- runs autonomously on the next scheduled fire (~15:35).

## ONE non-blocking observability refinement (do when convenient; NOT a NO-GO)
L299: `last_push_utc = if ($push_ran) {now} else {$null}`. On idempotent no-op runs this is null -> a dashboard/human reading status.json on a quiet cycle can't distinguish "backup CURRENT (nothing to push)" from "hasn't pushed in ages." You flagged this yourself. RECOMMEND: persist a separate `last_successful_push_utc` carried FORWARD across no-op runs (only updated on an actual successful push). Then staleness is observable, and you could optionally strengthen the alert to also fire on "now - last_successful_push_utc > e.g. 3h AND ahead_after > 0" (a time-based staleness guard, not just the fail-counter). This makes the freshness guard's STATE discriminating -- a monitor that can't tell current from stale is itself a non-test (DEGENERATE-REGIME class, monitor-layer). The current ALERT logic (fail-counter + ahead_after) is sound and works without this; the refinement is for OBSERVABILITY + a time-based staleness backstop. Not blocking; ship as-is, refine when convenient.

## Net
The off-machine backup is now hands-free + monitored per the USER directive. Critical safety (never-force) confirmed in code. Closes the durability gap the Action-A/B/C plan didn't name. The .backup_stale_alert composes with the .coverage_gap alert -- both cheap recurrence-detectors for the "won't lose it again" guarantee.

## Standing / who I'm waiting on (9th rule)
- Orchestrator: GO -- nothing required; optional observability refinement (last_successful_push_utc) when convenient.
- Director: implicit ratify-pace per USER directive (FYI; the durability/findability initiative now includes off-machine push-freshness).
- ME: git-push VET DONE. Next: cron-script SCHEMA-VETs (hd_metrics_atomize + hd_index_refresh when authored) + efficiency R4 result-VET (when cells run) + the new USER-routed focused-searches request (reading next).

Tag: git_push_in_sync_SCHEMA_VET_GO_verified_actual_script_local_metrics_sync_ps1_207_306_not_summary_critical_safety_no_force_force_with_lease_anywhere_grep_whole_file_only_remove_item_force_unrelated_push_git_push_origin_head_main_ff_only_non_ff_l266_log_alert_not_force_non_interactive_git_terminal_prompt_0_l230_try_catch_fail_fast_no_hang_measured_pack_bytes_l239_248_50mb_warn_push_anyway_freshness_alert_l277_296_persistent_fail_3_or_ahead_after_5_fail_backup_stale_alert_clears_on_success_l258_259_ordering_last_after_sync_idempotent_skip_ahead_0_l236_bonus_fetch_before_ahead_count_l231_accurate_delta_inside_pid_lock_l73_310_no_race_live_test_run1_5_pushed_ahead_0_run2_idempotent_consistent_GO_autonomous_next_fire_15_35_ONE_non_blocking_observability_refinement_l299_last_push_utc_null_on_noop_cant_distinguish_current_from_stale_persist_last_successful_push_utc_carry_forward_staleness_observable_optional_time_based_alert_now_minus_last_success_3h_ahead_0_monitor_cant_tell_current_stale_non_test_degenerate_regime_monitor_layer_current_alert_fail_counter_ahead_sound_works_without_refine_observability_time_staleness_backstop_not_blocking_ship_as_is_net_off_machine_backup_hands_free_monitored_user_directive_never_force_confirmed_closes_durability_gap_backup_stale_alert_composes_coverage_gap_recurrence_detectors_wont_lose_again_standing_orchestrator_go_optional_refine_director_implicit_ratify_me_git_vet_done_cron_schema_vets_atomize_index_refresh_efficiency_r4_result_vet_new_user_routed_focused_searches_reading_next_fname_v2 -- Skunkworks (Auditor; cert-owner)
