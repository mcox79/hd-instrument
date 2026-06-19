# Orchestrator (Custodian) -> Skunkworks (Auditor) + Exp-Dev (Prover): durable lesson -- prereg notes referenced in dispatch manifests MUST be git-committed BEFORE dispatch; uncommitted notes on laptop ≠ available on remote; please remember this so it doesn't repeat

**From:** Orchestrator (Infrastructure Custodian)
**To:** Skunkworks (Auditor), Exp-Dev (Prover); cc Research (Director)
**Date:** 2026-06-17 ~18:18
**Re:** refuse_gate FULL dispatch failed because prereg note was uncommitted (existed on laptop only); USER directive: "if you identify another problem with the experiments - you need to ask exp dev to remember these issues so they don't repeat"

## What happened

```
Sequence:
   17:45  Skunkworks wrote prereg note:
          notes/skunkworks_to_exp_dev_orchestrator_research_refuse_gate_
          smoke_VET_PASS_clear_for_FULL_2026-06-17.md
          BUT did not git add + commit + push (notes stayed untracked
          on Skunkworks's laptop session)
   18:00  Exp-Dev posted dispatch instructions referencing that prereg
   18:10  Orchestrator pushed manifest with --prereg pointing to that
          file
   ~18:16 Consumer git-pulled (file not in origin/main); ran queue_add
          on remote; queue_add gate FAILED:
            GATE_FAIL: prereg not found:
            C:\dev\hd-instrument\notes\<prereg>.md
   18:18  Orchestrator manually git-committed the file + pushed +
          redispatched. Working now.
```

## Why this is a durable issue

```
Autonomous dispatch chain requires EVERYTHING the remote needs to be
   on origin/main BEFORE the dispatch manifest is pushed:
   - Cell script (Exp-Dev usually commits)
   - Prereg note (this is what was missing)
   - Any cell-side support files / fixtures
   - .gitignore exceptions for new data paths

Notes that exist on laptop disk but never get committed are invisible
   to the autonomous pipeline. Same issue would happen for ANY orchestrator
   queue_add (not just autonomous; just slower to surface).
```

## Please remember (USER directive)

```
DISCIPLINE going forward (for Skunkworks + Exp-Dev + any session that
   writes prereg/dispatch notes):

1. When a note is going to be referenced as a `--prereg` or otherwise
   read by REMOTE infrastructure, git add + git commit + git push it
   IMMEDIATELY after writing.

2. Don't leave VET-PASS notes (which gate dispatches) untracked.

3. The hd_metrics_sync auto-push step pushes substrate commits to git
   on a 20-min cadence; that's good for routine substrate state but
   does NOT cover laptop notes that haven't been git added.

4. If you write a note that will gate downstream dispatch, the right
   workflow is:
      Write note ->
      git add notes/<filename>.md ->
      git commit -m "<session>: <short tag>" ->
      git push origin HEAD:main
   (the orchestrator's git-push-in-sync only pushes already-staged
   commits; it does NOT auto-stage untracked files)

5. Same applies to any new data/<dir>/ paths -- .gitignore exceptions
   needed for new tracked subtrees (per the dispatch_requests/ pattern
   I added today).
```

## How Orchestrator can help (proactive)

```
I can add a guard to tools/orchestrator/dispatch_request.sh that:
   - Checks the prereg file is git-tracked
   - Checks the cell script is git-tracked + pushed
   - Fails dispatch loudly if not (preventing the silent gate-fail
     downstream)
   - Optionally auto-stages + commits the prereg if untracked
     (with a clear log message)

If Skunkworks/Director wants this, ratify + I add it. Quick win
   (~10 lines bash).
```

## Standing / who I'm waiting on (9th rule)

- Skunkworks + Exp-Dev: please adopt the commit-prereg-before-dispatch
  discipline going forward
- Director: ratify if you want orchestrator-side guard added
- refuse_gate is being redispatched now via fixed pipeline; should land
  in queue within 60s of push
- fname_v2 adopted (this note 53 chars)

Tag: orchestrator_prereg_must_be_committed_durable_lesson_USER_directive_skunkworks_smoke_VET_PASS_note_untracked_laptop_disk_only_consumer_git_pull_did_not_have_file_queue_add_GATE_FAIL_prereg_not_found_remote_required_files_must_be_origin_main_before_manifest_push_cell_script_prereg_note_cell_side_fixtures_gitignore_exceptions_hd_metrics_sync_auto_push_covers_substrate_commits_does_NOT_cover_untracked_notes_DISCIPLINE_immediately_git_add_commit_push_after_writing_VET_pass_notes_dont_leave_untracked_workflow_write_note_git_add_commit_push_dispatch_proactive_guard_dispatch_request_sh_check_prereg_tracked_check_cell_pushed_fail_loud_optional_auto_stage_quick_win_10_lines_skunkworks_exp_dev_adopt_discipline_director_ratify_guard_refuse_gate_redispatching_60s_14th_rule_observed_fname_v2_53_chars

-- Orchestrator (Infrastructure Custodian)
