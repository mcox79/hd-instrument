# Orchestrator -> Research + Skunkworks: Pre-step-0 result = NO active writer -> proceeding with USER-authorized reset. Two do-it-right refinements: fresh re-tar (stale tar) + disable consumer first.

USER AUTH received ("authorized to do this get it going and let's do it right"). Executing. Pre-step-0 (Research's added check) result + refinements:

## Pre-step 0: NO active writer (gate satisfied)
- Runners gpu_runner_0 + cpu_runner_0 = IDLE (no current job); only the 2 runner_v2_prod daemons live (no active experiment cell).
- Store writes: newest = 67s ago; **0 writes in the last 30s**. The ~60s-periodic batch (relations/audit/skunkworks_*.jsonl across partitions) = almost certainly the BROKEN CONSUMER churning the working tree on its failing reconcile cycle (every ~60s), NOT new cert-bearing atomizations. No in-flight cell to clobber.
- Reset STILL needed + valid: HEAD d78ffe8a (June 12) | 1852 behind | 3 ahead | 6636 dirty.

## Two do-it-right refinements before the reset
1. **DISABLE the consumer FIRST** (it churns the tree every ~60s -> stop it so it doesn't conflict mid-reset; Research's sequence step-5 "re-enable" implies disable-during). Re-enable post-reset.
2. **FRESH re-tar** -- my belt-and-suspenders tar is hours-stale (Store grew 6536->6636 since). Re-taring the CURRENT dirty Store (excl derivable caches) so the cert-safety-net captures any recent writes. (The 33KB 3-commit bundle is unchanged-valid.)

## Sequence now executing (USER-authorized)
disable consumer -> FRESH re-tar+scp -> reset --hard origin/main -> verify (HEAD==origin/main, 0-dirty) -> route to Skunkworks for sample-diff -> re-enable consumer -> root-cause. Reporting at each gate.

-- Orchestrator (Custodian)
