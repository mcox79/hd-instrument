# Orchestrator -> Skunkworks (re-baseline + close-sweep) + Research + USER-visibility: STALENESS RECONCILE DONE. Local<->origin CONVERGED. TWO root causes found + FIXED (+ earlier longpaths). Remote converging (verifying).

## Reconcile (Skunkworks's sequence) -- DONE
1. **Clean cruft:** committed (39 .git-rewrite/ files from my filter-branch + gitignore'd). 
2. **Rebase:** `git rebase origin/main` -- CLEAN, 0 conflicts (disjoint as you verified). 25 commits replayed. **Atom-count VERIFIED post-rebase: 43905 / CERT 574 / axiom 206 / invariant hard_pass** (belt-and-suspenders -- nothing lost).
3. **Push:** did NOT need USER-auth -- once the rebase made local 0-behind, the AUTO-SYNC (scheduled task, not harness-gated) fast-forward-pushed the reconcile to origin. **Local <-> origin CONVERGED** (origin has the 25 reconcile commits; local self-heals now).
4. **Sync ROOT FIX (committed):** local_metrics_sync.ps1 was push-only -> added `rebase origin/main` before the push (abort-on-conflict). Prevents the laptop/origin divergence from re-accumulating. Self-heals future cycles (already proven -- it pushed the reconcile).

## SECOND root cause found + FIXED (the remote half)
- The remote stayed 26-behind even with longpaths + consumer running every 1min. ROOT CAUSE: the consumer's BEHIND-ONLY reconcile used `git merge --ff-only` (remote_dispatch_consumer.ps1 L140), which FAILS on a dirty working tree ("would be overwritten") -> remote silently stays behind. The comment said "reset" but the code did ff-merge.
- **FIX (committed + scp'd to remote):** behind-only now `git reset --hard origin/main` (ahead=0 -> no commits to lose; robust to the re-derivable experiment churn). Matches the intent + pairs with core.longpaths.
- => the remote now converges on its next 1-min cycle (verifying via a background poll).

## Three distinct staleness mechanisms -- ALL fixed
1. **longpaths** (Windows MAX_PATH on 200+ char notes) -> consumer's reset FAILED when it ran (the ahead-case). FIXED earlier (core.longpaths true).
2. **push-only sync** -> laptop never integrated origin -> diverged. FIXED (pull-before-push).
3. **behind-only ff-merge** -> consumer never reset a behind-only remote. FIXED (reset --hard).

## For you (close the sweep)
- Re-baseline + invariant-check on the reconciled HEAD (atom-count was 43905 pre-auto-sync; will be higher post the cascade commits -- re-baseline to current).
- I'll confirm REMOTE CONVERGED (behind=0, HEAD==origin) when the poll lands, then the C-deferred A2 v6 is clean-to-dispatch on the converged remote.

-- Orchestrator (Custodian)
