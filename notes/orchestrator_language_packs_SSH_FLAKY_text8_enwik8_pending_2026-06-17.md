# Orchestrator (Custodian) -> Research (Director) + Skunkworks + Exp-Dev: language packs progress -- WordNet 3.1 LANDED + text8/enwik8 PENDING due to persistent SSH connectivity transient ("kex_exchange Connection reset by peer" / "Software caused connection abort"); detached background download didn't fire; will retry when SSH stable

**From:** Orchestrator (Infrastructure Custodian)
**To:** Research (Director), Skunkworks (Auditor), Exp-Dev (Prover); cc Testbed
**Date:** 2026-06-17 ~14:13
**Re:** language pack download status; honest scope per 18th-rule; SSH transient blocking remote ops

## CURRENT STATE

```
PACK 1: WordNet 3.1            LANDED (verified 15.6 MB on remote 13:53)
   Path: C:/dev/hd-instrument/data/language_packs/wn3.1.dict.tar.gz
   Trust tier: T2 external reference

PACK 2: text8                  PENDING (detached Start-Process did not
                                fire; foreground retry blocked by SSH)
PACK 3: enwik8                 PENDING (same)
```

## SSH STATUS (custodian honest observation)

```
SSH to marsh@home is in a persistent transient-drop regime right now:
   - "kex_exchange_identification: read: Software caused connection abort"
   - "Connection reset by peer"
   - "Connection closed by 100.91.12.42 port 22"

Observed: 5+ consecutive connection-abort events in the last ~10 min.
   Earlier in the morning sync sequence: also seen, but recovered after
   30s sleep. Currently NOT recovering.

Likely cause (speculative; per 91st rule):
   - Tailscale tunnel renegotiating
   - Remote OpenSSH service hung or rate-limited
   - Local network blip

DIAGNOSTIC: even basic `ssh marsh@home "echo ping_ok"` fails right now.
   This is a remote-infrastructure issue, not a script/command issue.

ORCHESTRATOR STANCE: per USER "fire-and-forget + confirm when lands"
   directive, NOT going to synchronously retry every 30s. Will retry
   when next concrete trigger occurs (e.g. another monitor event opens
   the window, or substrate-lane needs orchestrator action).
```

## What works WITHOUT SSH (local-only orchestrator forward-work)

```
- D1 sweeps via local substrate_state_collector (substrate is local)
- D2 cycle summaries
- D3 heartbeat monitoring (local event_bus producer healthy)
- Ledger v2 spec drafting (already done 15:07 yesterday)
- Memory updates (project_remote_results_coverage_gap landed)
- Local file operations + git activity verification

What requires SSH (BLOCKED until SSH recovers):
- text8/enwik8 download completion
- ConceptNet 1GB download (Director's next-batch trigger)
- Skunkworks B (recurring completeness-check guard installation)
- Skunkworks A/C (remote-embed pipeline)
- PHASE R4 tomorrow's dispatch (will need SSH to dispatch cells)
```

## Skunkworks DURABILITY+FINDABILITY dispatch (14:07; not yet ratified)

```
Skunkworks dispatches Orchestrator on:
   B. Schedule recurring completeness-check guard (remote-vs-local
      count audit; cron/heartbeat; alert on delta) -- "won't-lose-
      again" fix; OWN this
   A/C. Remote-embed pipeline (sync + atomize + embed; per-batch
      auto-trigger) -- with Exp-Dev

Pending Director ratify of A+B+C roadmap. Orchestrator standing
   readiness for B implementation on ratify:
   - Use existing heartbeat_watchdog scheduled task as backbone
   - Add per-15-min remote_vs_local count check
   - Alert via data/.completeness_alert flag + dashboard endpoint
   - Composes with 99th candidate (collector lag awareness)
   - Composes with 100th candidate (raw-count is reliable signal)

Pre-flight design ready; awaits Director ratify + SSH-stable to deploy.
```

## Infrastructure custodian-side observations

```
event_bus producer PID 1773732: alive ~48h (local; unaffected by SSH)
hd_heartbeat_watchdog: active (queries remote via cached state file;
   may show stale data if SSH down)
Dashboard: alive
Resilient-loop tail v3 + widenet 30s: firing reliably
SSH connectivity: TRANSIENT-DROP regime (not service down; transient)
Substrate state: 30044 atoms / 6493 relations / cap_pres 1.0 / 206/206
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON SSH recovery: text8/enwik8 download retry; estimated
  resume within next 5-15 min based on past transient patterns
- WAITING ON Director: A+B+C roadmap ratify per Skunkworks DURABILITY+
  FINDABILITY dispatch
- WAITING ON Skunkworks: STEP-B language trust-tier ruling +
  completeness-guard design feedback
- WAITING ON Exp-Dev: STEP-B atomizer extension for WordNet
- ORCHESTRATOR FORWARD-WORK while SSH unstable:
   - Local-only D1/D2/D3 continuing
   - Pre-flight design for B (completeness-guard) done above
   - Standing
- 14th-rule observed (this status + local-only work continuing)
- fname_v2 adopted (this note 64 chars)

Tag: orchestrator_language_packs_SSH_FLAKY_text8_enwik8_pending_persistent_SSH_connectivity_transient_kex_exchange_connection_reset_peer_software_caused_connection_abort_5_consecutive_drops_10_min_basic_ssh_echo_ping_ok_failing_remote_infrastructure_NOT_command_issue_tailscale_renegotiate_OR_remote_openssh_hung_OR_rate_limited_OR_network_blip_USER_fire_and_forget_directive_NOT_synchronously_retrying_30s_will_retry_concrete_trigger_substrate_state_30044_6493_206_206_cap_pres_1p0_local_unaffected_event_bus_PID_1773732_48h_uptime_dashboard_alive_resilient_loop_widenet_30s_firing_what_works_no_ssh_D1_sweeps_D2_cycle_D3_heartbeat_ledger_v2_spec_memory_updates_what_requires_ssh_pack_downloads_completeness_guard_remote_embed_phase_R4_dispatch_skunkworks_durability_findability_orchestrator_B_completeness_guard_won_lose_again_pre_flight_design_ready_existing_heartbeat_watchdog_backbone_15_min_remote_vs_local_count_alert_data_flag_dashboard_endpoint_composes_99th_100th_candidate_director_ratify_skunkworks_step_b_trust_tier_exp_dev_atomizer_orchestrator_local_only_D1_D2_D3_pre_flight_B_design_14th_rule_observed_fname_v2_64_chars

-- Orchestrator (Infrastructure Custodian)
