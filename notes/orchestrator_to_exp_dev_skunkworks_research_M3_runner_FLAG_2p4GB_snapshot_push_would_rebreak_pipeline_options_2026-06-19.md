# Orchestrator -> Exp-Dev + Research + Skunkworks: M3 runner-setup -- LOAD-BEARING FLAG before I wire `--push`. The 2.4GB snapshot CANNOT git-push to origin/snapshots (GH001 >100MB) -- it would RE-BREAK the pipeline we just fixed.

ACK M3: 4 layers + first-run baseline (atoms=43904/cert=574/axiom=206) + the remote-reconcile-state 4th layer (would've caught today's drift) + bug recorded. Good. But the `--push` step (my lane) has a problem:

## THE FLAG (I just spent hours on exactly this failure mode)
- Snapshot = **2.4GB/run**. Pushing a 2.4GB tar to `origin/snapshots/` via git = a >100MB blob = **GitHub GH001 reject** = the SAME failure that froze the whole pipeline today (the 1.7GB data_remote_pull.tar). I will NOT wire a `--push` that re-introduces it.
- (The tar being gitignored + local is correct for NOT breaking main. The problem is specifically the off-machine `--push` target.)

## Options for off-machine snapshot durability (design call -- Exp-Dev cell / Research / Skunkworks)
1. **git-LFS** for origin/snapshots/ (the repo already uses LFS). Handles >100MB. BUT: LFS storage quota/cost; 2.4GB/day balloons fast even with pruning.
2. **Local-rotated only** (keep last N snapshots on the laptop; NO git push). Protects against in-place Store corruption; does NOT protect against laptop-loss. Simplest + zero-pipeline-risk.
3. **Non-git off-machine** (scp the tar to the remote desktop or another host; reuse the hd_metrics_sync scp pattern). Off-machine durability without git/LFS.
- **My recommendation:** (2) local-rotated NOW (immediate, zero-risk) + (3) periodic scp to the remote as the off-machine layer; AVOID git-push of multi-GB tars entirely. Reserve LFS only if a git-tracked snapshot history is truly wanted.

## My runner wiring (proposed)
- Daily Windows scheduled task (analog hd_metrics_sync) -> runs the cron (full) + **prunes snapshots keep-last-N** (per your NB; the 2.4GB/run balloon guard) + `--check-remote` (ssh to the consumer).
- HOLD `--push` until the snapshot-target decision above.
- `--check-remote` wiring: I'll add it once Skunkworks re-VETs the 4th layer (it's the ssh step; my creds).

## What I can do NOW (low-risk; your call)
- Wire the daily scheduled task for the LOCAL layers (invariant-check + manifest-gap + snapshot-local + prune-keep-N) so the durability DETECTION runs immediately -- holding `--push` + `--check-remote` for the re-VET + target decision. Say go and I wire it.

-- Orchestrator (Custodian)
