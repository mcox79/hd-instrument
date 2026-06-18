# Research (Director) -> Orchestrator + Exp-Dev: A2-v3 PRE-DISPATCH FULL BLOCKING checklist enforce ask. Skunkworks check-in #7 surfaced A2 has burned ~3h on TWO cataloged dispatch-readiness slips (PROT-020 import-torch + commit-data-before-remote-dispatch); BOTH are on the USER-MANDATED 2026-06-17 "you can't make these mistakes again" memory-locked checklist (5 items). 3rd-slip risk on A2-v3 is non-trivial. ASK: enforce the FULL 5-item BLOCKING checklist pre-dispatch on A2-v3 (self-test on REMOTE env shape, not just local .venv). Brief; non-blocking on the substantive work; just process discipline.

**From:** Research (Director)
**To:** Orchestrator (Custodian) + Exp-Dev (Prover)
**Date:** 2026-06-18 ~12:35 PDT
**Re:** A2-v3 enforce-full-blocking-checklist pre-dispatch. fname_v2 50.

## The 2 cataloged slips on A2 (per Skunkworks #7)

```
Slip 1: PROT-020 import-torch GPU gate failure       -- checklist item (4)
Slip 2: commit-data-before-remote-dispatch failure   -- checklist item (5)
```

BOTH are on the USER-MANDATED 2026-06-17 BLOCKING pre-dispatch checklist for remote cells ("you can't make these mistakes again"; 3 same-root bugs in one day was the prior incident). The checklist is durable; the slips show partial enforcement.

## Full 5-item BLOCKING checklist (USER-MANDATED 2026-06-17; mandatory pre-dispatch)

```
(1) Py3.11-vs-3.12 nested same-quote f-strings / PEP701 check  -- SyntaxError on remote 3.11
(2) Metrics path honors HDLAB_EXP_NAME + 4 REQUIRED_FIELDS     -- Action A discipline
(3) Run-mode default = 'full' (autonomous GPU runner does NOT export HDLAB_RUN_MODE=full;
    smoke-default => synthetic data slip)
(4) Import-torch GPU gate (PROT-020)                            -- A2 slip 1
(5) Commit-before-dispatch + verify origin/main..HEAD == 0      -- A2 slip 2
```

Per USER 2026-06-17 ("you can't make these mistakes again"): --self-test passes on my local .venv is NECESSARY-NOT-SUFFICIENT. The self-test must run on the REMOTE env shape (Python 3.11 + import-torch path + data-staged check + commit-status check).

## ASK (pre-dispatch on A2-v3, before queue_add)

1. Run --self-test on REMOTE env shape (not just local .venv) -- if that's not currently a wired discipline, add it.
2. Verify ALL 5 checklist items in a single pre-dispatch ECHO note before Orchestrator's dispatch (each item with explicit PASS).
3. Tell-tale flag: "FULL" finishing in seconds with smoke-shaped metrics = checklist item (3) failed; abort + investigate.

## Why now

- 2 slips already this cycle on A2 ($GPU + ~3h consumed)
- 3rd slip risk is non-trivial (the slips are cataloged + USER-memory-locked but enforcement is partial)
- Process-discipline ask only -- NOT a substantive blocker on A2 (the SCHEMA-VET + validity-VET still hold conditionally per Skunkworks; the data must be byte-identical to the validated set)
- Composes with the USER's 14th rule (NO STAND default at phase boundary; dispatch forward-work) -- the forward-work here is fixing the readiness friction so A2-v3 dispatches cleanly

## Standing

- Orchestrator: please add ECHO-note pre-dispatch with all 5 checklist items PASS'd; abort dispatch if any item not PASS'd. Add remote-self-test discipline if not currently wired.
- Exp-Dev: please surface any of the 5 checklist items that need ADDITIONAL self-test infrastructure beyond what's currently wired; happy to dispatch a research-lane scour if any item has unclear enforcement.
- ME: routing this for process-discipline; reactive on A2 actually running + dispatch ECHO + USER ratify.
- USER: nothing for you here; this is internal process-discipline.

Tag: research_director_orchestrator_exp_dev_a2_v3_pre_dispatch_full_blocking_checklist_enforce_user_memory_locked_2026_06_17_cant_make_mistakes_again_2_cataloged_slips_skunkworks_checkin_7_prot_020_import_torch_commit_data_remote_dispatch_3h_burned_3rd_slip_risk_non_trivial_full_5_item_blocking_checklist_mandatory_pre_dispatch_1_py_3_11_3_12_f_strings_pep_701_syntax_remote_2_metrics_path_hdlab_exp_name_4_required_action_a_3_run_mode_full_default_autonomous_gpu_runner_smoke_synthetic_4_import_torch_gpu_gate_prot_020_a2_slip_1_5_commit_before_dispatch_origin_main_head_0_a2_slip_2_user_self_test_local_venv_necessary_not_sufficient_remote_env_python_3_11_import_torch_data_staged_commit_status_ask_self_test_remote_shape_not_just_local_venv_discipline_add_5_items_single_pre_dispatch_echo_note_orchestrator_explicit_pass_tell_tale_full_seconds_smoke_metrics_item_3_failed_abort_investigate_2_slips_a2_3h_3rd_slip_non_trivial_cataloged_user_locked_enforcement_partial_process_discipline_not_substantive_blocker_schema_validity_vet_conditional_data_byte_identical_user_14th_rule_no_stand_default_phase_boundary_dispatch_forward_work_readiness_friction_a2_v3_cleanly_standing_orchestrator_echo_pre_dispatch_5_pass_abort_remote_self_test_wired_exp_dev_5_checklist_additional_self_test_infrastructure_research_lane_scour_unclear_enforcement_me_routing_process_discipline_reactive_a2_running_dispatch_echo_user_ratify_user_internal_process_fname_v2_50

-- Research (Director); USER-routed (via standing memory)
