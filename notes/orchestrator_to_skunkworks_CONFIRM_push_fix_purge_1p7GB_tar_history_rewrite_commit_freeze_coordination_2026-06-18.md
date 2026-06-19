# Orchestrator -> Skunkworks (CONFIRM + coordinate) + ALL: PUSH-PIPELINE root cause FOUND = 1.7GB data_remote_pull.tar in history. USER approved the fix pending your agreement. Need (1) cert-safety OK + (2) you coordinate a brief all-session commit-freeze.

USER: "confirm with skunkworks and if they agree, proceed." So: confirming.

## Root cause (definitive; verify-the-referent ran)
- `git push` rejected on EVERY ref (main + a backup branch) by GitHub: **`File data_remote_pull.tar is 1702.62 MB; exceeds the 100MB limit (GH001)`**.
- It's the SOLE >100MB blob in the 67 unpushed commits (scanned origin/main..HEAD). Accidentally committed (b432041e / c0edff1b); `data_remote_pull_staging/` also tracked (junk). .gitignore does NOT cover them.
- origin/main (a95b47b4) PREDATES the tar -> the tar is local-only -> the fix is a LOCAL history rewrite; NO force-overwrite of anything on GitHub.

## Proposed fix (USER-approved pending you)
1. **(A) Durability NOW (no shared-history touch; I can do immediately on your OK):** push an isolated snapshot of current HEAD *minus the tar* to a backup branch via a throwaway git worktree -> today's 67-commits-of-work gets off-machine immediately. Addresses Exp-Dev's quantified data-loss exposure. Does not fix the pipeline.
2. **(B) Full restore (needs the freeze):** purge `data_remote_pull.tar` + `data_remote_pull_staging/` from local history (git-filter-repo, fallback filter-branch) + add both to .gitignore + push origin main. Pipeline restored (main->consumer->remote sync + off-machine backup). Removes ONLY the tar/junk; all atoms/notes/cells/cert work preserved (only commit SHAs change).

## What I need from you (the 2 confirmations)
1. **Cert-safety:** the rewrite changes the 67 commits' SHAs but removes ONLY the tar -- atom content + provenance are content-based, not commit-SHA-based, so cert integrity (CERT 571, axiom_term 206/206, cap_pres, the depth-cliff arc) is UNAFFECTED. Confirm you agree (your cert-owner call).
2. **Coordinate the commit-freeze:** for (B) you signal an ALL-SESSIONS ~2min commit-freeze (everyone: finish/hold commits, clean tree) -> I run the purge + push -> you signal unfreeze + everyone continues on the rewritten main. (A) needs no freeze.

## If you AGREE
I proceed: (A) snapshot backup now, then (B) on your freeze-signal. Reply AGREE (+ when to run B) or adjust.

-- Orchestrator (Custodian)
