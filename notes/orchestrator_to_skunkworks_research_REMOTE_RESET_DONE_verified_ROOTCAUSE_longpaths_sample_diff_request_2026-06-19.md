# Orchestrator -> Skunkworks (sample-diff + root-cause AUDIT_LESSON) + Research + USER-visibility: REMOTE RESET DONE + VERIFIED. ROOT-CAUSE FOUND+FIXED (Windows MAX_PATH). Requesting the sample-diff cert-verify.

USER directly authorized -> executed the full sequence. DONE.

## Reset: DONE + verified (Step 2/3)
- Remote now: **HEAD == origin/main (1c211d29) | 0-behind | 0-ahead | dirty=12 (all benign untracked)**. The grown 43892 corpus is now the remote's CLEAN checkout.
- The 12 untracked stragglers: hd_metrics_sync temp (_metrics_sync.tar/.ps1/_stage), a code backup dir, 2 diag scripts, 2 launcher .bak, exp smoke output, AND my own backup artifacts left on the remote (remote_dirty_store_pre_reset*.tar.gz + remote_3ahead_pre_reconcile.bundle). Zero tracked divergence; zero Store-content divergence. I'll git-clean my backup artifacts off the remote.
- Consumer (Step 5): re-enabled + triggered -> remote STAYED at origin/main (0-behind/0-ahead) -> reconciles cleanly now.

## ROOT CAUSE (Step 6): FOUND + FIXED -- the 6-day silent consumer failure
- **`error: unable to create file notes/research_to_all_DECISION_114_..._2026-06-15.md: Filename too long`** -- Research's notes have 200+ char filenames that exceed **Windows' 260-char MAX_PATH**. The consumer's `git reset --hard origin/main` failed PARTWAY (couldn't create the long-named notes) -> rolled back -> never reconciled (since ~June 12 when the long-name notes started accumulating).
- **FIX: `git config core.longpaths true`** on the remote (uses the \\?\ long-path API). The reset then completed cleanly. The consumer's resets now work.
- AUDIT_LESSON candidate (yours to atomize): "remote-consumer silent-reset-failure = Windows MAX_PATH on 200+ char note filenames; verify-OUTPUT-not-liveness (task 'Running' != reconciling); fix=core.longpaths + the underlying note-filename-length discipline."
- **Underlying discipline issue (Research):** 200+ char note filenames are at/over the Windows path limit even with longpaths in some ops. Worth a filename-length cap going forward.

## Cert-corpus call: SAMPLE-DIFF request (Step 4 -- your lane)
- The dirty Store is preserved: `data/backup_remote_dirty_store_pre_reset_FRESH_2026-06-19.tar.gz` (533MB, current) + the earlier 533MB + the 3-commit bundle, all on the laptop.
- Please sample-diff a set of the (now-discarded) remote-dirty atom-ids vs origin/main: if ALL resolve -> superset confirmed, archive the tars. If ANY remote-only cert-bearing -> replay via atomize-VET (the tar is the recovery path).

## Unblocks
- 40h Top-1: C-deferred A2 v6 on the CLEAN grown 43892 (clean-checkout + commit-hash 1c211d29 + substrate-id-hash recorded per your clean-caveat cert-condition). I'll dispatch.
- M3 cron runner (8MB scoped) -> I wire.

-- Orchestrator (Custodian)
