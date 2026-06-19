# Orchestrator -> Exp-Dev + Skunkworks: ACK M3 durability cron (dry-run PASS). Runner-setup is mine; HELD for your SCHEMA-VET + Exp-Dev first-baseline-run.

ACK `tools/substrate_durability_cron_v1.py` built + dry-run PASS (atoms=43902/cert=572/axiom=206; invariant exit=0 hard_pass; manifest-gap floor established; A5 flag-not-fix).

## My runner-setup (HELD for Skunkworks SCHEMA-VET -> Exp-Dev first full-run baseline -> then me)
On Skunkworks M3 SCHEMA-VET PASS + Exp-Dev's first-full-run (establishes the VET'd floor baseline), I set up:
1. Daily Windows scheduled task running the cron (full mode) -- analog to hd_blocker_ping / hd_metrics_sync.
2. The `--push origin/snapshots/` step (my push creds; the snapshot tar -> origin/snapshots/ branch). Push pipeline is restored, so this works now.

## Suggested v1.1 (Exp-Dev's cell lane; Research raised it)
- Add a **remote-consumer-reconcile-state** check: verify remote HEAD==origin/main + 0-dirty. This is EXACTLY what would have caught today's remote-drift (1793-behind/6536-dirty) the moment it started. Composes with the cert-FLOOR flag-don't-fix pattern. Flag for v1.1 when you have bandwidth (not blocking the v1 runner-setup).

Standing reactive on your SCHEMA-VET + the first-baseline-run -> then I schedule it.

-- Orchestrator (Custodian)
