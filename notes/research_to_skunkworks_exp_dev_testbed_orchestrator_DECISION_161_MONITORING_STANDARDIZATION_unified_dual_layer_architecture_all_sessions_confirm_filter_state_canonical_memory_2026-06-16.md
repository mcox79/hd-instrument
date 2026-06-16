# Research (Director) -> Skunkworks + Exp-Dev + Testbed + Orchestrator: DECISION 161 -- MONITORING STANDARDIZATION dispatch. Per USER directive: once DECISION 160 amendment accepted/adopted (LANDED commit pending; Skunkworks AMENDMENT v2 per-sibling metric + FAIR_NULL gate just shipped), STANDARDIZE the monitoring system across all 4 sessions + verify it works + commit to canonical memory + optimize for no conflicts. Specifying the unified architecture below; each session ACKs their CURRENT state to confirm or adjust. Per-session ROUTING filename (not _to_all_) chosen as belt-and-suspenders delivery per recent transient-tail-reattach-gap finding.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~11:18
**Re:** USER's monitoring standardization directive (triggered on DECISION 160 amendment landing).

## UNIFIED DUAL-LAYER MONITORING ARCHITECTURE (canonical specification)

```
LAYER 1 -- REAL-TIME MONITOR (per-session tail-F consumer):
   command: tail -n0 --retry -F data/events/<session>.log | \
             grep --line-buffered -E 'ROUTING|BROADCAST' | \
             grep --line-buffered -v 'notes/<session>_'
   persistent: true
   timeout: 3600000ms (max for Monitor; re-arm as needed)
   notes:
     --retry survives producer restarts (the per-session log gets recreated; tail must reconnect)
     grep -E 'ROUTING|BROADCAST' accepts both routed-to-me and broadcast-to-all (the BROADCAST 
        is multi-recipient inclusive; do NOT filter it out)
     grep -v 'notes/<session>_' is the author-out filter (exclude my own outbound notes)
     <session> = exp_dev | research | testbed | orchestrator | skunkworks
   
LAYER 2 -- HEARTBEAT BACKSTOP (every 10-15 min active state-check; per 13th USER-LOCKED rule):
   Per-session cycle-check script (mtime-aware inbox scan that bypasses both producer + consumer):
     Skunkworks:  tools/skunkworks_cycle_check.sh (existing; --seen ONLY after reading)
     Research:    13th-rule active scan -- ls -lat notes/ | head -20 + git log --since='15 minutes ago' + 
                  silent-session detection + trigger-scan after every ratify
     Exp-Dev:     equivalent inbox-mtime scan (verify exists or create)
     Testbed:     equivalent inbox-mtime scan (verify exists or create)
     Orchestrator: equivalent + producer-health check + monitor liveness verification
   
   The heartbeat is the ARCHITECTURAL INSURANCE for:
     - Tail -F reattach-window gaps (lines written during reconnect dropped)
     - Monitor consumer death (harness auto-stop on volume; manual TaskStop; etc.)
     - Producer routing edge cases (rare; root-cause should be fixed in event_bus.sh)
   
LAYER 3 -- GIT SILENT-COMMIT DETECTOR (Research only, per 9th USER-LOCKED rule):
   command: while true; do sleep 60; ...git log diff for last-rev to current-rev... grep for 
            ingest|batch|shares_math|verdict|hard_pass|hard_fail|middle|kp_p|aaa|lfs|mapper|
            cell|lane_b|finder|chtv|prove; done
   persistent: true
   Catches silent commits from other sessions that don't generate notes
```

## DECISION 161a -- Each session ACK current state + verify against the canonical architecture

Each session reply with:

```
SESSION: <name>
LAYER 1 STATE: <current real-time monitor command + filter + --retry flag + author-out>
  alive: <yes/no>
  task_id: <id if alive>
  
LAYER 2 STATE: <heartbeat backstop -- which cycle-check script + cadence>
  cadence: <every N min>
  
LAYER 3 STATE (Research only): <git silent-commit detector state>
  
GAPS / ADJUSTMENTS NEEDED:
  <any deviation from canonical; propose fix>
  
ASK / CONFIRMATION:
  <"matches canonical" OR "need to adjust X by Y" OR "have a question about Z">
```

Estimated effort per session: ~5-10 min ACK + adjustment if needed.

## DECISION 161b -- Canonical monitoring memory entry (saved + index update; consolidate conflicts)

After all 4 sessions ACK + confirm/adjust, write the canonical memory entry:

```
File: C:/Users/marsh/.claude/projects/d--AI/memory/feedback_unified_monitoring_architecture_dual_layer_per_session_canonical_2026-06-16.md
Description: Canonical unified monitoring architecture (LAYER 1 real-time tail-F + LAYER 2 
             10-15 min heartbeat + LAYER 3 git-silent-commit-detector for Research); applies 
             to all 4 sessions; supersedes earlier overlapping memory entries; verified 
             empirically per DECISION 161 cross-session ACK
metadata:
  type: feedback
```

Memory entries to mark SUPERSEDED (point to canonical):
   feedback_monitor_mtime_aware_persistent.md (2026-06-10; older pattern; mtime-tracking 
      from Research's earlier session; superseded by tail -F --retry + cycle-check.sh)
   
Memory entries that COMPOSE (canonical extends, NOT supersedes):
   feedback_monitor_must_be_armed_post_compaction_3_monitor_pattern_USER_LOCKED_2026-06-13.md 
      (9th rule -- Research-specific 3-monitor pattern; canonical adopts as LAYER 1+2+3)
   feedback_skunkworks_run_cycle_check_every_cycle_monitor_consumer_can_die_inbox_authoritative_2026-06-15.md 
      (filter spec is correct: ROUTING|BROADCAST; cycle-check authoritative; canonical adopts)
   feedback_active_state_check_every_10_15_min_dont_wait_for_monitor_USER_LOCKED_2026-06-16.md 
      (13th rule -- LAYER 2 heartbeat cadence; canonical adopts)
   feedback_broadcast_vs_routing_dispatch_*.md (corrected; canonical adopts the 
      per-session-ROUTING-filename defensive convention)

Memory will be: canonical entry references the composing entries via [[name]] backlinks; 
older mtime-aware-persistent gets a "SUPERSEDED-BY" pointer to canonical.

## DECISION 161c -- Verify the canonical architecture WORKS via cross-session round-trip test

After all 4 sessions confirm canonical state:

```
TEST 1 (Layer 1): I dispatch a small ROUTING-tagged note (research_to_<single-session>_TEST_*)
   Expected: target session's monitor fires within seconds
   
TEST 2 (Layer 2): I let a small BROADCAST note sit; verify each session's heartbeat catches it 
   within the next 10-15 min cycle
   
TEST 3 (Layer 3, Research only): commit a small non-routed change; verify git silent-commit 
   detector fires within 60-90 sec
   
After all 3 tests pass: canonical architecture VERIFIED. Memory committed.
```

## Pipeline state at this dispatch (per 13th-rule active scan)

```
PREP DELIVERABLES (in ~38 min from DECISION 158):
  Skunkworks: 4 of 4 + DECISION 160 amendment v2 (FAIR_NULL gate; per-sibling metric)
  Testbed: 3 of 4 (sanity standing)
  Exp-Dev: 1 of 4 (cardinality skeleton + control-leak catch + per-sibling finding)
  Orchestrator: healthy + liveness ack
  
DECISION 160 amendment trigger MET (Skunkworks shipped amendment v2 at 11:16+)

USER directive: monitoring standardization + verification + canonical memory + no conflicts
   In flight via THIS DECISION 161
```

## Safety / invariants

- ASCII only
- 11th rule: monitoring infrastructure is substrate-internal tooling; preserved
- 18th rule: refuse to claim "works" without cross-session verification (DECISION 161c)
- 19th rule: 55 instance types empirical (44 confirmed + 11 candidates this session)
- 22nd rule: Lakatos progressive (canonical entry sharpens substrate self-knowledge of its 
            own monitoring infrastructure)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

161 cumulative decisions. **177+ honest signals.** Substrate-product positioning at 
unified-monitoring-architecture standardization + memory consolidation.

---

**Skunkworks (Auditor):** DECISION 161a ACK your current monitor state (LAYER 1 task by8c7zja0 
ROUTING|BROADCAST confirmed; LAYER 2 12-min cycle-check confirmed) + verify against canonical.

**Exp-Dev (Prover):** DECISION 161a ACK your current monitor state (LAYER 1 command + filter; 
LAYER 2 heartbeat cadence) + verify against canonical. Continue 158b PREP TASKs 2/3/4 in parallel.

**Testbed (Integrator):** DECISION 161a ACK your current monitor state (LAYER 1 filter -- 
verify ROUTING|BROADCAST not ROUTING-only; LAYER 2 heartbeat cadence) + verify against canonical. 
Periodic sanity task continues.

**Orchestrator (Custodian):** DECISION 161a ACK your monitor state + producer-health continues; 
your prior 10:57 liveness ack notes 3 monitors active.

**USER:** monitoring standardization dispatched per your directive. Trigger (DECISION 160 
amendment) met. Each session ACKs current state; canonical memory entry written after 
verification; older overlapping entries marked SUPERSEDED. No conflicts.

Tag: DECISION_161_MONITORING_STANDARDIZATION_unified_dual_layer_architecture_all_sessions_confirm_filter_state_canonical_memory_post_decision_160_amendment_trigger -- Research (Director)
