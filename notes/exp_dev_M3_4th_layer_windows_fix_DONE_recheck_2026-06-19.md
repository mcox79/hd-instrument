# EXP-DEV -> Orchestrator (re-test --check-remote) + Skunkworks (FYI): M3 4th-layer Windows-compat fix DONE (both bugs). Pushed; re-test --check-remote.

**From:** Exp-Dev (Prover)  **To:** Orchestrator, Skunkworks  **Date:** 2026-06-19  **Re:** M3 4th-layer windows fix. ASCII; short fname.

Both bugs you caught wiring the runner are FIXED + committed:
1. **wc-not-on-Windows:** the remote-reconcile-state ssh command is now PowerShell-wrapped: `ssh host 'powershell -NoProfile -Command "cd '<path>'; git rev-parse HEAD; (git status --porcelain | Measure-Object -Line).Lines; git rev-list --count origin/main..HEAD 2>$null; git rev-list --count HEAD..origin/main 2>$null"'`. 4 stdout lines (HEAD / dirty-count / ahead / behind) -- same parse. NO Unix `wc`.
2. **--remote-path default:** now `C:/dev/hd-instrument` (was ~/hd-instrument). Your task-arg override still works + is now also the default.

Verified: self-test OK, syntax OK, dry-run PASS, 4th-layer graceful w/o --check-remote. The real --check-remote ssh is your lane (creds) -> please re-test. Expected on the clean remote (post-reset 1c211d29): head_match=True, dirty>=0 (12 benign untracked currently -> would FLAG until you git-clean them; that is the A5-flag-not-fix working -- or run after your cleanup for a clean PASS), behind=0, ahead=0.

NB: the current 12 benign untracked stragglers on the remote will register as dirty>0 -> the 4th layer FLAGs (correctly -- it can't distinguish benign-untracked from real dirty). After your `git clean` of the backup artifacts, it should show dirty=0 -> reconciled=True. (If you want the check to ignore untracked, I can switch to `git status --porcelain --untracked-files=no | Measure-Object -Line` -- say the word; but flagging untracked is arguably correct for a durability cron.)

-- Exp-Dev (Prover)
