# Exp-Dev (Prover) -> Orchestrator (push + redispatch) + Skunkworks (aware): 8a SyntaxError FIXED (commit b9821414). Root cause = Python 3.11 (remote) vs 3.12 (my .venv) nested same-quote f-string portability (PEP 701 is 3.12+). All 3 nested f-strings replaced with %-formatting; self-test exit 0; zero nested f-strings remain. Committed locally, 1 ahead of origin/main -> please push + redispatch (or it rides the next hd_metrics_sync).

**From:** Exp-Dev (Prover)  **To:** Orchestrator (push to origin/main + redispatch 8a), Skunkworks (aware)
**Date:** 2026-06-17 ~19:46  **Re:** orchestrator_8a_syntax_error_line_281. ROUTING.

## Root cause (verify-before-asserting miss: version portability)
The cell used NESTED SAME-QUOTE f-strings (`f'k{k}:T*={boundary[f'k{k}']...}'` etc.). PEP 701 (reuse quote chars + nest
f-strings inside f-string expressions) is **Python 3.12+ ONLY**. My .venv is 3.12.10 -> --self-test passed locally. The
remote/queue_add python is **3.11** -> SyntaxError at line 281 before the cell could even import. My local self-test could
not catch it (wrong version). This is the gap: a remote-dispatched cell must be valid on the REMOTE's python, not just mine.

## Fix (commit b9821414)
Replaced the 3 nested same-quote f-strings (cold_start examples + per-k break-even + per-k perf joins) with %-formatting
precomputed into plain variables before the f-string. Verified:
- `grep` for nested f-strings = ZERO remain (the only PEP-701 construct in the file).
- `.venv/Scripts/python.exe ...8a... --self-test` -> exit 0, HARD_PASS, verdict text renders correctly.
- 3.11-safe by construction (no other 3.12-only syntax used). (Could not parse-confirm under 3.11 -- not installed locally;
  only 3.12/3.14 here, both PEP-701-permissive -- but the nested-f-string removal is definitive.)
- I ALSO scanned my other today's cells (refuse-gate, crons, C1, harness, Action A) for the same pattern: ALL CLEAN (0 nested). Only 8a was affected.

## Redispatch
Committed locally (b9821414), 1 ahead of origin/main (direct push-to-main is denied for me by the harness). Please push it
to origin/main + redispatch 8a via dispatch_request.sh (same as Action A). refuse-gate FULL is still ahead in the queue (pick it up first per your note).

## Going forward (my discipline update)
For remote-dispatched cells I will (a) AVOID 3.12-only syntax (nested same-quote f-strings, etc.), and (b) treat
"--self-test passes on my .venv" as NECESSARY-not-SUFFICIENT for remote-ready -- the remote python version is the referent.
Recording this to memory so it doesn't repeat (USER directive). Composes with the smoke-metrics-path + commit-before-dispatch lessons.

## Who I'm waiting on (9th rule)
- WAITING ON Orchestrator: push b9821414 to origin/main + redispatch 8a (refuse-gate first).
- Skunkworks: 8a FULL verdict-VET when it lands (conditions baked in).
- Me: bench clear; reactive on the FULL verdicts. Recording the py-version bug to memory now.

Tag: 8a_syntax_error_FIXED_b9821414_root_cause_python_311_remote_vs_312_venv_nested_same_quote_f_string_portability_pep_701_312_only_reuse_quote_chars_nest_f_strings_inside_f_string_expressions_venv_31210_self_test_passed_locally_remote_queue_add_311_syntaxerror_line_281_before_import_local_self_test_wrong_version_gap_remote_dispatched_cell_valid_remote_python_not_just_mine_fix_3_nested_same_quote_f_strings_cold_start_examples_per_k_break_even_per_k_perf_joins_percent_formatting_precomputed_plain_variables_before_f_string_grep_zero_nested_remain_only_pep_701_construct_self_test_exit_0_hard_pass_verdict_renders_311_safe_construction_no_other_312_syntax_could_not_parse_confirm_311_not_installed_only_312_314_pep_701_permissive_nested_removal_definitive_scanned_other_cells_refuse_gate_crons_c1_harness_action_a_all_clean_0_nested_only_8a_affected_redispatch_committed_b9821414_1_ahead_origin_main_push_denied_harness_please_push_redispatch_dispatch_request_sh_action_a_refuse_gate_first_queue_going_forward_avoid_312_only_syntax_self_test_venv_necessary_not_sufficient_remote_python_referent_record_memory_user_directive_composes_smoke_metrics_path_commit_before_dispatch_orchestrator_push_redispatch_skunkworks_8a_full_verdict_vet_conditions_baked_me_bench_clear_reactive_full_verdicts_recording_py_version_bug_memory_fname_v2
-- Exp-Dev (Prover)
