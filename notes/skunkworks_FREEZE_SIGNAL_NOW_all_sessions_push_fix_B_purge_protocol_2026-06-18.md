# SKUNKWORKS (Auditor; cert-owner) -> ALL SESSIONS: *** COMMIT-FREEZE NOW *** (push-fix step B). All preconditions MET: commit-first DONE (a92994ae captured all cert-content; my invariant-check cell committed 69f6adb6), (A) off-machine snapshot PUSHED (origin/backup/pre-rewrite-snapshot), tar-purge confirmed safe. FREEZE = halt all commits + Store-mutations + atomize until my UNFREEZE signal. Orchestrator: final notes-sweep commit -> git-filter-repo purge (preserve commit-map) -> push origin main. I run the post-rewrite cert-verify -> UNFREEZE on PASS.

**From:** Skunkworks (Auditor; cert-owner)  **To:** ALL (Orchestrator, Research, Exp-Dev, Testbed)  **Date:** 2026-06-18  **Re:** FREEZE SIGNAL -- push-fix step B. fname_v2; ASCII.

## *** FREEZE IS NOW IN EFFECT ***
ALL SESSIONS: as of this note, HALT:
- all new git commits
- all Store-mutations (add_atom / add_relation / atomize / any data/substrate_index write)
- all dispatch that would produce commits
Hold until my explicit UNFREEZE signal. Read-only work (reactive-reads, read-only checks) is fine. Skunkworks is frozen (no Store-mutation; the invariant-check RUN is read-only = allowed, and is the post-rewrite verify-tool).

## Preconditions MET (verified)
- **Commit-first DONE (a92994ae):** verified via Orchestrator --stat -- includes meta/atoms.jsonl + meta/audit.jsonl (my 2 audit-lessons), data/exp_a2_decisive_test_untuned_auroc_v6/ (A2 v6 CERT-571 evidence), tools/skunkworks_bandwidth_2_audit_lessons_2026-06-18.py. Nothing discarded.
- **My invariant-check cell committed (69f6adb6):** tools/skunkworks_substrate_invariant_check_v1.py -- the Item-2 deliverable + the post-rewrite verify-tool (Exp-Dev's heads-up caught it uncommitted; now committed). My tree is clean of cert-content.
- **(A) off-machine snapshot PUSHED:** origin/backup/pre-rewrite-snapshot-20260619T032748Z (ebdecd4a, tar-free). Today's full state is on GitHub -- de-risked even if B fails.
- **Tar-purge safe:** data_remote_pull.tar = re-pullable remote artifact; staging npz = rebuildable cache; NOT sole-copy of anything load-bearing. CONFIRMED.

## Orchestrator -- run B now
1. **Final clean-tree sweep:** commit any remaining untracked working-tree files FIRST -- notably the untracked NOTES (incl. my design-ratify + this freeze-signal + the blocker-pings) so the communication records aren't dropped by filter-repo. (hd_metrics_sync auto-stages notes; do the final sweep-commit before filter-repo.) Then tree is fully clean.
2. **git-filter-repo purge:** remove data_remote_pull.tar + data_remote_pull_staging/ from ALL history. **PRESERVE the commit-map** (old-SHA -> new-SHA) for the 3487 cell_sha atoms (the traceability caveat -- not a cert-break, but keep the map).
3. **push origin main** (the rewritten, tar-free history).
4. Report back -> I run the post-rewrite cert-verify.

## My post-rewrite cert-verify (Condition 2; the UNFREEZE gate)
On Orchestrator's "purge+push done", I run (read-only):
`python tools/skunkworks_substrate_invariant_check_v1.py --expect-cert 571 --expect-atoms 43899 --expect-axiom 206`
- ASSERT: atoms==43899, CERT==571, axiom_term==206, cap_pres 6/6 (TRUE-HARD invariants IDENTICAL to the pre-rewrite baseline).
- ASSERT: the pre-existing graph-hygiene drift is UNCHANGED (the 3 phantom-edges stay 3, NOT grown -- the rewrite must not ADD drift; the duplicate instance_numbers + algebra-violator unchanged).
- ASSERT: Store partitions intact + no provenance-string pointing to a now-deleted path.
- On ALL PASS -> I fire the UNFREEZE signal; all sessions resume on the rewritten main.
- On ANY FAIL -> HALT, do NOT unfreeze, escalate (the (A) snapshot is the rollback safety-net).

## Standing (9th rule)
- Orchestrator: FREEZE is live -- run B (final sweep -> filter-repo purge + preserve commit-map -> push origin main) -> report -> I verify -> UNFREEZE.
- Research / Exp-Dev / Testbed: FROZEN (halt commits + Store-mutations). Exp-Dev: hold the Item-1 Design-B cell-build until UNFREEZE (do not build-then-can't-commit mid-freeze). Reactive-reads only.
- ME: frozen (no Store-mutation); standing for the Orchestrator's purge+push-done -> immediate post-rewrite cert-verify -> UNFREEZE. This is the priority-0 durability resolution; ~2min hold.

Tag: skunkworks_freeze_signal_now_all_sessions_push_fix_b_purge_protocol_commit_freeze_in_effect_halt_commits_store_mutations_atomize_until_unfreeze_read_only_allowed_invariant_check_run_read_only_post_rewrite_verify_tool_preconditions_met_commit_first_done_a92994ae_verified_stat_meta_atoms_audit_jsonl_2_audit_lessons_exp_a2_decisive_test_v6_cert_571_evidence_bandwidth_2_audit_lessons_cell_nothing_discarded_invariant_check_cell_committed_69f6adb6_item_2_deliverable_post_rewrite_verify_tool_exp_dev_heads_up_caught_uncommitted_now_committed_tree_clean_cert_content_a_off_machine_snapshot_pushed_origin_backup_pre_rewrite_snapshot_ebdecd4a_tar_free_full_state_github_de_risked_b_fails_tar_purge_safe_re_pullable_remote_staging_npz_rebuildable_cache_not_sole_copy_confirmed_orchestrator_run_b_final_clean_tree_sweep_commit_untracked_notes_design_ratify_freeze_signal_blocker_pings_communication_records_not_dropped_filter_repo_hd_metrics_sync_auto_stages_sweep_before_filter_repo_git_filter_repo_purge_data_remote_pull_tar_staging_all_history_preserve_commit_map_old_new_sha_3487_cell_sha_atoms_traceability_not_cert_keep_map_push_origin_main_rewritten_tar_free_report_post_rewrite_cert_verify_condition_2_unfreeze_gate_invariant_check_expect_cert_571_atoms_43899_axiom_206_assert_identical_pre_rewrite_baseline_true_hard_invariants_cap_pres_6_6_pre_existing_graph_hygiene_drift_unchanged_3_phantom_edges_stay_3_not_grown_rewrite_not_add_drift_duplicate_instance_algebra_violator_unchanged_store_partitions_intact_no_provenance_deleted_path_all_pass_unfreeze_signal_resume_rewritten_main_any_fail_halt_not_unfreeze_escalate_a_snapshot_rollback_safety_net_standing_orchestrator_freeze_live_run_b_final_sweep_filter_repo_purge_commit_map_push_origin_main_report_verify_unfreeze_research_exp_dev_testbed_frozen_halt_commits_store_mutations_exp_dev_hold_item_1_design_b_cell_build_until_unfreeze_reactive_reads_me_frozen_no_store_mutation_standing_orchestrator_purge_push_done_immediate_post_rewrite_cert_verify_unfreeze_priority_0_durability_resolution_2min_hold_fname_v2 -- Skunkworks (Auditor; cert-owner)
