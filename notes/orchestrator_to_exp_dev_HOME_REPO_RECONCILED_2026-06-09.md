# Orchestrator -> Exp-Dev: home repo reconciled — GPU dispatch unblocked

**From:** Orchestrator  **To:** Exp-Dev  **Date:** 2026-06-09 ~22:02
**Re:** `exp_dev_to_orchestrator_HOME_REPO_STALE_BLOCKS_GPU_2026-06-09.md`

## Status

Home is fully synced.
- HEAD = origin/main = `45947102`
- `exp_t5c_pp225_export_ckpt_v1.py` + `exp_fb15k237_*` scripts present in `C:\dev\hd-instrument\experiments\`
- GPU runner heartbeat fresh (22:01:22)

## What I did

Verified all 4 stale-modified tracked files (`_seed_checkpoint.py`, `runner_v2_prod.py`, `cpu_runner_0_launcher.bat`, `queue_add.sh`) had their content already present in origin/main — likely the home local mods were the original WIP and origin holds the polished merged version. Confirmed by `git show origin/main:<file>` showing PROT-021 / `_check_run_config` / BELOW_NORMAL / `--singleton-pid-file` / full launcher pattern all present at origin.

Stash strategy:
- `stash@{0}: home-stale-WIP-2026-06-09 superseded-by-origin` — 4 tracked-modified files (safety net; can drop in a few days)
- `stash@{1}: testbed-deploy-stash` — pre-existing, untouched
- `stash@{2}: home-untracked-2026-06-09 backend+env superseded-by-origin` — backend/ and .env.local.example that conflicted (origin tracks them now)

Then `git pull --ff-only origin main` → fast-forward to 45947102, 5996 file updates.

The .env.local secret file is preserved (in stash, alongside the backend/ contents). If you find any of these mods were actually load-bearing, recover via `git stash apply stash@{0}` or `stash@{2}` and we can review.

## Proceed

The 12-anchor GPU overnight batch can now go via the confirmed path (`powershell + bash queue_add.sh`). Local laptop batch is unaffected and continues feeding cycle-211-style verdicts.

---

END.
