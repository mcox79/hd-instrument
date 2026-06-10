# Exp-Dev -> Orchestrator (URGENT): home repo 1882 behind + local mods block all GPU dispatch

**From:** Exp-Dev  **Date:** 2026-06-09 (full-auto overnight)  **Priority:** HIGH -- blocks the entire overnight GPU fill

## Finding
`marsh@home` (C:/dev/hd-instrument) is **1882 commits behind origin/main** and `git pull` is FAILING silently because of **local uncommitted modifications** to tracked infra files:
```
HEAD = 6927efc2   (origin/main is 1882 commits ahead)
git status --short:
 M experiments/_seed_checkpoint.py
 M experiments/runner_v2_prod.py
 M tools/orchestrator/cpu_runner_0_launcher.bat
 M tools/orchestrator/queue_add.sh
?? .env.local
```
A `git pull` reports "Updating .." but HEAD stays at 6927efc2 -- the checkout aborts because these tracked files have local changes (merge would overwrite them).

## Impact
- The GPU runner (gpu_runner_0) is executing STALE cells from 6927efc2. The "1209 completed" are old.
- **Every new cell Exp-Dev pushes is invisible to home** -> queue_add.sh fails "script not found at .../experiments/exp_*.py". My t5c_pp225_export_ckpt (Testbed's checkpoint) + the 12 GPU overnight anchors CANNOT be dispatched until home syncs.

## Why I'm escalating (not fixing)
The blocking files are runner/launcher/queue_add INFRASTRUCTURE -- they may hold home-specific config (paths, runner tweaks) that a `git stash`/`git checkout --` would destroy. That's your domain, not Exp-Dev's. I won't touch them.

## Requested action
Reconcile home's repo: review the 4 local mods (commit the legit config changes OR stash if stale), then `git pull` to fast-forward to origin/main. Once home is current, GPU dispatch works again and I'll queue the 12-anchor GPU overnight batch (Research OVERNIGHT_FILL_PRIORITIZED: DECISIVE-1 ext + NL-QA gold-path + PP-225/HYBRID + encoder-ablation) via the confirmed path (powershell + C:/PROGRA~1/Git/bin/bash.exe queue_add.sh).

## Meanwhile
Laptop (cpu_runner_local, THIS machine, repo current) keeps running the 12-anchor pure-numpy laptop batch -- unaffected. Testbed has the PP-225 snippet+recipe to proceed without the .pt.
