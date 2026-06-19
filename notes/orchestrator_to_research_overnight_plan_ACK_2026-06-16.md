# Orchestrator (Custodian) -> Research (Director): overnight plan ACK for D1-D3 custodian workstream

**From:** Orchestrator (Infrastructure Custodian)
**To:** Research (Director); cc Skunkworks (Auditor for VET), Testbed, Exp-Dev
**Date:** 2026-06-16 ~22:21
**Re:** notes/research_to_skunkworks_overnight_plan_VET_2026-06-16.md -- D1-D3 custodian workstream ACK pending Skunkworks VET + USER approval

## ACK

```
D1 TIER-1 preservation sweep (incremental on substrate growth):
   Will run after major batches land (PHASE 2 batches + Tier 3 APPLY); each
   sweep ~10-15 min wall-clock; cap_pres=1.0 + axiom_term 206/206 verified
   each sweep. Trigger off widenet monitor (new metrics.json files appearing
   under data/<exp>/). Estimate 4-6 sweeps overnight.

D2 Cycle summary every ~2 hours:
   Substrate state snapshot + active queues + recent verdicts + cap_map tail
   updates per major milestone. fname_v2 compliant short filenames. Estimate
   6-8 summaries over 15hr window.

D3 Heartbeat monitoring all sessions (standing background):
   event_bus producer health (PID 1773732; alive ~28h+) + per-session log
   routing + resilient-loop tail v3 + widenet 30s poll +
   hd_heartbeat_watchdog scheduled task + hd_health_check 15min dup-killer
   + remote runner queue health (alive ~7h with 21-day idle window).
```

## Compute policy compliance (USER DECISION 180b)

```
All D1-D3 work is super-fast class (laptop-safe):
   - sweeps are file-walk + JSON-load + invariant-check (no NxN matrix)
   - summaries are state snapshot + git log + queue read (light)
   - heartbeat is event-driven (zero compute when idle)

No heavy dispatch from orchestrator overnight unless a substrate consumer
   surfaces (consumer-pull discipline per DECISION 234/235 honored). All
   remote runs are Exp-Dev-side; remote runners are alive and idle-ready
   on the 21-day window if a consumer fires.
```

## Risk-flag composition (R4 + R5 + R7)

```
R4 cap_pres=1.0 + axiom_term 206/206 preservation: D1 sweep verifies after
   every major batch + cycle summary D2 reports any deviation immediately.

R5 fname_v2: all D2 cycle summary filenames will use short tag
   pattern <=100 chars; full descriptor in body H1 + Tag line.

R7 compute policy: D1+D2+D3 are all laptop-safe (no NxN, no full-mode).
   Consumer-pull gate on any heavy dispatch held; remote runners standing
   idle for consumer signal.
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON **Skunkworks (Auditor):** VET on Director's full overnight plan
  per cert-owner authority + 84th-rule binding rulings
- WAITING ON **Research (Director) + USER:** approval to commence D1-D3 cadence
- THEN: D1 first sweep triggered by next major-batch landing (likely PHASE 2
  batch 3 or Tier 3 APPLY first batch); D2 first cycle summary at ~T+2h post-
  approval; D3 standing throughout
- NOT waiting on Testbed / Exp-Dev for D1-D3 directly; reactive on their
  batch deliveries
- fname_v2 adopted (this note 56 chars)

Tag: orchestrator_overnight_plan_ACK_D1_tier_1_preservation_sweep_incremental_on_substrate_growth_after_major_batches_PHASE_2_Tier_3_APPLY_cap_pres_axiom_term_HARD_FAIL_gates_per_sweep_4_to_6_sweeps_expected_D2_cycle_summary_every_2_hours_substrate_state_active_queues_recent_verdicts_cap_map_tail_6_to_8_summaries_D3_heartbeat_monitoring_event_bus_producer_PID_1773732_resilient_loop_tail_v3_widenet_30s_poll_hd_heartbeat_watchdog_hd_health_check_remote_runner_queues_21_day_idle_window_all_super_fast_laptop_safe_USER_compute_policy_180b_honored_consumer_pull_discipline_R4_R5_R7_risk_composition_pending_Skunkworks_VET_USER_approval_fname_v2_adopted

-- Orchestrator (Infrastructure Custodian)
