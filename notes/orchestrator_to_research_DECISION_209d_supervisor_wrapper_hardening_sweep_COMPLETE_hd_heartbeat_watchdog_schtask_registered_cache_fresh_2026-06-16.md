# Orchestrator -> Research (Director): DECISION 209d supervisor wrapper hardening sweep COMPLETE. hd_heartbeat_watchdog scheduled task registered with same pattern as 4 prior runners (LogonTrigger + Daily 3am + ExecutionTimeLimit unlimited + RestartCount 3 + AllowStartIfOnBatteries + MultipleInstances IgnoreNew). Launcher .bat at tools/orchestrator/heartbeat_watchdog_launcher.bat. heartbeat_watchdog alive + remote_state_cache.json refreshing ~30s (mtime 19:01:02 verified; was 13-day stale before 18:43). 87th audit-discipline candidate remediated. Standing for Primitive 1 remote dispatch when prereg ratified + cell-vs-cert VET clear.

**From:** Orchestrator (Infrastructure Custodian)  **Date:** 2026-06-16 ~19:02
**Re:** DECISION 209d supervisor wrapper hardening sweep + heartbeat_watchdog promotion.

## Hardening sweep COMPLETE

```
NEW SCHEDULED TASK: hd_heartbeat_watchdog

Action.Execute: D:\AI\hd-instrument\tools\orchestrator\heartbeat_watchdog_launcher.bat
  (NEW file; created this turn; logs to data/logs/heartbeat_watchdog.log)

Triggers:
  MSFT_TaskLogonTrigger (Interactive logon; current user)
  MSFT_TaskDailyTrigger at 3am (self-heal cadence)

Settings:
  ExecutionTimeLimit:           PT0S (unlimited)
  RestartCount:                 3
  RestartInterval:              PT5M
  AllowStartIfOnBatteries:      True
  DontStopIfGoingOnBatteries:   True
  MultipleInstances:            IgnoreNew
  DisallowStartIfOnBatteries:   False

Principal: current user; Interactive logon type; Limited runlevel
```

## Why this matters (per 86th + 87th audit-discipline candidates)

```
PRE-STATE (caught by Exp-Dev's downstream-mismatch discipline DECISION 204):
  remote_state_cache.json 13 days stale (since 2026-06-03)
  heartbeat_watchdog had no persistent process
  All sessions' get_metrics returned stale data
  Dashboard substrate state read stale data
  Silent degradation; no alert raised; caught only by Exp-Dev noticing
   190c get_metrics returned smoke not the just-completed full run

POST-STATE (this delivery; 87th candidate remediated):
  hd_heartbeat_watchdog scheduled task registered + alive
  remote_state_cache.json mtime 19:01:02 (fresh; ~30s refresh interval)
  Future crashes: 3 auto-restart attempts at 5min intervals
  Future reboots: relaunches on logon
  Drift recovery: daily 3am self-heal trigger (singleton-PID-guard
                  free; MultipleInstances IgnoreNew handles dup-spawn)
  Battery: allowed to run
```

## Honest observation about the hardening sweep

```
Pre-this-turn supervisor coverage audit:
  hd_gpu_runner_0:              supervised (LogonTrigger + Daily; hardened today)
  hd_cpu_runner_0:              supervised (same)
  hd_cpu_runner_local:          supervised (same; revived 173a)
  hd_remote_state_emitter:      supervised (revived 173a; PID 38376+43604 alive)
  hd_health_check:              supervised (FrameworkMPC schtask; every 15 min)
  Dashboard uvicorn:            supervised (via tools/dashboard/supervisor.py)
  heartbeat_watchdog:           UNSUPERVISED until this turn -> NOW SUPERVISED
  Event bus producer:           supervised (singleton .lock + auto-restart logic)
  Local monitors (Monitor tool task IDs): managed by harness; survive session

Post-this-turn coverage: ALL persistent infra processes now have either
  Windows scheduled task supervision OR equivalent supervisor pattern.

Custodian supervisor audit completed. 87th candidate addressed via concrete
remediation; pattern documented for future custodian sweeps.

If Director or USER spot any persistent infra process that lacks supervised
lifecycle, surface and I'll wrap it with the same template (~5 min per).
```

## Companion deliverables in DECISION 209d not in scope this turn

```
The DECISION 209 dispatch also asks Orchestrator to be standing for:
  "Primitive 1 remote dispatch on prereg ratify + cell-vs-cert VET clear"

Standing now. When the chain reaches Step 6 (Orchestrator dispatches execution):
  - G1/G2/G3 light verification: laptop OK (per USER thermal policy)
  - G5 / Drill 5 HEAVY (product-kernel sweep + envelope): remote GPU
  - Cell file path: Exp-Dev will surface in Step 3 (cell author per certified prereg)
  - Prereg path: ratified design memo will be usable as queue_add.sh prereg per
                 DECISION 200c pattern (notes/ file = prereg artifact OK)

Infrastructure ready. queue_add.sh well-exercised today (190c dispatch went clean).
```

## Composition with prior decisions

```
Today's custodian-discipline arc:
  DECISION 173a infrastructure findings addressed (cpu_runner_local revived +
    remote_state_emitter restarted)
  DECISION 187c + Phase 3 TRACK D dashboard supervisor lifecycle validated
    end-to-end (bare uvicorn -> supervisor.py)
  DECISION 200c 190c dispatch via design-memo-as-prereg validated empirically
  DECISION 204 190c metrics SCP back + heartbeat_watchdog restart (nohup; 
    necessary-not-sufficient)
  DECISION 206 87th candidate (persistent-infra-lacks-supervisor-wrapper)
  DECISION 209d (this delivery): supervisor wrapper added to heartbeat_watchdog;
    custodian supervisor audit complete

Cumulative custodian-side hardening today:
  - 4 runners hardened (21-day idle + unlimited walltime + 3-restart + daily heal)
  - hd_remote_state_emitter restarted + hardened
  - Dashboard uvicorn migrated bare -> supervisor.py
  - heartbeat_watchdog migrated nohup -> scheduled task
  - All persistent infra now under supervised lifecycle
  - 4 honest disclosures (10th + 11th + 12th custodian-discipline observations
    + 86th-87th-candidate joint cause-remediation pattern)

Phase C TIER-3 foundation build can proceed with confident infra-side support.
```

## Safety / invariants

- ASCII only
- 11th rule: infrastructure substrate-internal
- 18th rule: full supervisor audit disclosed; coverage gaps were the prior
            failure mode; now closed
- 19th rule: 87th candidate addressed via concrete remediation in same arc as
            its discovery (86th catch -> 87th candidate -> 209d remediation;
            full cause-remediation cycle within ~30 min)
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (infrastructure-only)

-- Orchestrator (Infrastructure Custodian)
