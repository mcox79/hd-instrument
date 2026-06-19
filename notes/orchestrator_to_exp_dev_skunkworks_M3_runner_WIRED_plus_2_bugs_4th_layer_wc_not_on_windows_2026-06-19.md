# Orchestrator -> Exp-Dev (cell fix) + Skunkworks/Research (FYI): M3 runner WIRED (USER-authorized) + dry-run caught 2 bugs in --check-remote. 4th layer needs a Windows-compat fix (uses `wc`).

USER authorized -> registered the M3 runner. Dry-run verification (verify-OUTPUT) caught 2 bugs in the 4th-layer remote-check:

## M3 runner: WIRED + verified-working (detection layers)
- Scheduled task `hd_durability_cron` REGISTERED on the laptop (daily 04:10, StartWhenAvailable, ExecutionTimeLimit 1h). State=Ready.
- Args: `--check-remote --keep-snapshots 7 --remote-path C:/dev/hd-instrument`.
- Dry-run PASS: atoms=43905 / cert=574 / axiom=206 / invariant-check exit=0 hard_pass=True / manifest-gap floor 43904, 0 missing. The local detection layers + prune WORK.

## 2 bugs the dry-run caught in the 4th layer (remote-reconcile-state)
1. **--remote-path default wrong:** default `~/hd-instrument` -> ssh "cannot find the path specified". The remote repo is `C:/dev/hd-instrument`. WORKED AROUND: I pass `--remote-path C:/dev/hd-instrument` in the task args. (Consider changing the cell default, or it's fine as a required arg.)
2. **`wc` not on the Windows remote (cell fix needed):** `ssh failed (rc=255): 'wc' is not recognized as an internal or external command`. The remote-reconcile-state ssh command uses Unix `wc` (e.g., `git status --porcelain | wc -l`), but **marsh@home is Windows** (cmd/powershell; no `wc`). The check ssh's into a Windows host -> `wc` fails -> 4th layer can't run.
   - **GRACEFUL:** the cron handles it (checked=False, cron still PASS) -- so the runner is functional NOW (detection layers live); the 4th layer just no-ops until fixed.
   - **FIX (your cell lane):** make the remote-check Windows-compatible -- wrap the remote command in `powershell -Command` using `(git status --porcelain | Measure-Object -Line).Lines` instead of `| wc -l`, and `git rev-parse HEAD` etc. (the same pattern my ssh checks used). Then HEAD==origin/main + 0-dirty/behind/ahead verifies on the Windows remote.

## Status
- M3 runner-setup (my lane): DONE -- task wired + detection layers verified. 4th-layer remote-check pending your Windows-compat fix (graceful-degraded meanwhile).
- I'll re-test --check-remote once you push the cell fix.

-- Orchestrator (Custodian)
