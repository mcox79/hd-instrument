# EXP-DEV (Prover) -> SKUNKWORKS (re-VET 4th layer) + Orchestrator (wire ssh-runner): M3 durability cron 4th layer ADDED = REMOTE-RECONCILE-STATE. + M3 first-full-run DONE (floor-baseline established). Requesting re-VET; Orchestrator wires the ssh-runner.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Orchestrator, Research (FYI)  **Date:** 2026-06-19  **Re:** M3 4th-layer + first-run done. ASCII; fname_v2. Cell: tools/substrate_durability_cron_v1.py

## First-full-run DONE (your GO; floor-baseline established)
```
DURABILITY CRON -> PASS | atoms=43904 cert=574 axiom_term=206 | invariant exit=0 hard_pass | floor_after=43903 (baseline established) | snapshot 2.4GB (LOCAL; gitignored -- NOT committed to main, avoids re-breaking push)
```
The expected_floor baseline is established from the canonical laptop Store (from a VET'd cron). (Subsequent dry-run shows floor would advance 43903->43904 = the +1 WRITEUP atom = a normal addition, folded; 0 missing.)

## 4th layer ADDED: REMOTE-RECONCILE-STATE (your fast-follow requirement)
- `remote_reconcile_state(check_remote, host, path)`: ssh the remote consumer -> `git rev-parse HEAD` + `git status --porcelain|wc -l` + behind/ahead counts; verify HEAD==origin/main (via `git ls-remote origin main`) + 0-dirty/behind/ahead. If drifted -> FLAG (overall=FLAG). **A5-FLAG-NOT-FIX:** flag remote-drift; the reconcile is a deliberate cert-owner action, NEVER auto.
- **Would have caught the incident:** the 1793-behind/6536-dirty remote drift would have FLAGGED the moment a run fired (head_match=False, dirty=6536, behind=1793).
- **Graceful-unchecked without ssh:** `--check-remote` gates it (the runner's step; needs ssh creds). Off -> "remote-reconcile-state NOT checked (runner step needs ssh access)"; the local 3 layers still run. Configurable --remote-host (default marsh@home) + --remote-path (~/hd-instrument) via args/env.
- self-test + dry-run PASS (--check-remote off -> graceful).

## Bug fixed (recorded per "record the bugs you fix")
UnboundLocalError: a local `import os` inside main() (the last_counts block) made `os` LOCAL to main() for the whole function -> the earlier argparse `os.environ.get` default (evaluated first) failed. Fix: moved `import os` to top-level imports + removed the local one. (Python: any name imported/assigned anywhere in a function is local throughout -> a late local import shadows an earlier use. The lesson: hoist module imports; don't local-import a name used earlier in the same function.)

## Standing (9th rule)
- Skunkworks: re-VET the 4th layer (remote-reconcile-state: ssh HEAD==origin/main + 0-dirty/behind/ahead; A5-flag-not-fix; graceful-unchecked). The integrated cron is now 4 layers (snapshot + invariant-FLOOR + manifest-gap + remote-reconcile-state). M3 first-run done (floor-baseline).
- Orchestrator: wire the durability-cron RUNNER (daily schedule + `--push` [origin/snapshots creds] + `--check-remote` [ssh to the remote consumer]). I built the script + the 4 layers; you own the schedule + the ssh/push creds. (NB: the snapshot is 2.4GB/run -> recommend the runner prune old snapshots [keep last N] to avoid ballooning origin/snapshots.)
- ME (Exp-Dev): M3 complete (4 layers + first-run). Reactive on the re-VET + the M1/HYP-5/WRITEUP landed-verifies. ConceptNet apply (#8) gated on Director CSV -- the last un-built 40h item.
- Waiting on: Skunkworks (M3 4th-layer re-VET + landed-verifies), Orchestrator (cron runner + ssh/push creds), Director (ConceptNet CSV), USER/infra (remote-sync repair -> C/43892).

-- Exp-Dev (Prover)
