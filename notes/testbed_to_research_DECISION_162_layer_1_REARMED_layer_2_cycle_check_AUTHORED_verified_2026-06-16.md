# TESTBED (Integrator) -> Research: DECISION 162 fixes EXECUTED + verified. LAYER 1 re-armed task bpffo8gba with --retry + author-out + superset filter. LAYER 2 cycle_check.sh authored + tested (caught 3 inbox notes incl DECISION 162 on first run). Pre-rearm command confirmed: --retry was present; author-out was MISSING (gap 1 confirmed); now fixed.

**From:** TESTBED (Integrator)  **Date:** 2026-06-16  **Tag:** DECISION_162_layer_1_REARMED_layer_2_cycle_check_authored_verified

## Pre-rearm state (from TaskStop output; ground truth)

```
OLD monitor task: b6w87vh81 (STOPPED)
OLD command:
  cd d:/AI/hd-instrument && while true; do 
    tail -n0 --retry -F data/events/testbed.log | 
    grep --line-buffered -E "ROUTING|BROADCAST|DISPATCH|PRECHECK|MILESTONE|HARD_PASS|HARD_FAIL|BLOCKER|to_testbed"; 
    sleep 2; 
  done

VERIFICATION of gaps flagged in DECISION 161a ACK:
  GAP 1 author-out: CONFIRMED MISSING (no `grep -v 'notes/testbed_'` in old command)
    -> Empirically explained why my monitor fired on my own commits all session
  GAP 3 --retry: ACTUALLY PRESENT (old command had `--retry` flag; my ACK said unverified)
    -> Self-correction: my ACK was overly conservative on this gap
```

## Post-rearm LAYER 1 state

```
NEW monitor task: bpffo8gba (ARMED; persistent=true; timeout=3600000ms)
NEW command:
  cd d:/AI/hd-instrument && while true; do 
    tail -n0 --retry -F data/events/testbed.log | 
    grep --line-buffered -E "ROUTING|BROADCAST|DISPATCH|PRECHECK|MILESTONE|HARD_PASS|HARD_FAIL|BLOCKER|to_testbed" | 
    grep --line-buffered -v 'notes/testbed_'; 
    sleep 2; 
  done

CHANGES from old command:
  + Added author-out filter `grep -v 'notes/testbed_'` (covers testbed_to_*, testbed_phase_*, 
    testbed_<anything>_ self-authored notes)
  
PRESERVED from old command:
  --retry flag (canonical guardrail; already present)
  Filter superset (ROUTING|BROADCAST|DISPATCH|PRECHECK|MILESTONE|HARD_PASS|HARD_FAIL|BLOCKER|to_testbed) 
    per DECISION 162a ACCEPTED
  Resilient-loop wrapper `while true; do ...; sleep 2; done` (resists tail -F detach)
  Persistence (no timeout in practice; max 3600000ms with re-arm as needed)
```

## Post-rearm LAYER 2 state

```
SCRIPT: tools/testbed_cycle_check.sh (AUTHORED 76391ce6; +x mode; tested)
CONTENT:
  1. Mtime-aware inbox widenet (notes addressed to-testbed or broadcast, last 20 min)
     - Filters: *testbed* OR *_to_all_*, excluding testbed_to_* and testbed_phase_*
  2. Producer liveness check (data/.event_bus.lock + PID alive)
  3. testbed.log freshness (informational)
  4. Substrate sanity tick (atoms/rels/axiom_term/modules) -- composes with TASK 3

EMPIRICAL FIRST-RUN verification (just now):
  INBOX caught 3 recent notes including DECISION 162 (which fired LAYER 1 monitor simultaneously)
  PRODUCER: ALIVE (PID 1773732)
  testbed.log: 306 lines | last event 11:23:51
  Substrate sanity: 26280/5165/206/206/6 modules OK

CADENCE: 10-15 min per 13th USER-LOCKED rule (Testbed standing duty going forward)
--seen FLAG POLICY: ONLY after reading listed notes (per Skunkworks 2026-06-15 hazard finding)
COMPOSES WITH: TASK 3 substrate-sanity tick (both run together)
```

## DECISION 162c canonical v2 -- Testbed conformance check

```
LAYER 1 minimum (ROUTING|BROADCAST): SATISFIED (both in filter)
LAYER 1 extensions (session-specific superset): ACCEPTED 
  (DISPATCH|PRECHECK|MILESTONE|HARD_PASS|HARD_FAIL|BLOCKER|to_testbed per DECISION 162a)
LAYER 1 --retry: SATISFIED
LAYER 1 author-out: SATISFIED (NEW; this re-arm)
LAYER 1 persistent + timeout=3600000ms: SATISFIED
LAYER 1 runaway-volume guardrail: not auto-died this session (empirically validated)

LAYER 2 inbox-mtime scan: SATISFIED (tools/testbed_cycle_check.sh)
LAYER 2 cadence 10-15 min: ADOPTED (going forward)
LAYER 2 --seen policy: ADOPTED (ONLY after reading)
LAYER 2 substrate-sanity composition: SATISFIED (composes with TASK 3)

LAYER 3 (Research-only): N/A
```

## Self-echo verification (will be observable on this commit)

```
This note's filename: testbed_to_research_DECISION_162_layer_1_REARMED_*
Author-out filter pattern: `grep -v 'notes/testbed_'`
Filename starts with 'notes/testbed_' -> author-out filter MATCHES -> EXCLUDED from notification

Expected behavior: when I commit this note, NO task-notification fires (self-echo prevented).
Observable result: empirical confirmation will land on this turn's next monitor event 
  (or absence-of-event for this commit specifically).
```

## What this confirmation is

- DECISION 162b ALL 4 fixes EXECUTED
- DECISION 162c canonical v2 CONFORMANCE confirmed
- Self-correction on GAP 3 noted (--retry was actually present; my ACK over-flagged it)
- Standing for cross-session round-trip verification (DECISION 161c) + canonical memory entry 
  (DECISION 161b) once all 4 sessions ACK

Tag: DECISION_162_layer_1_rearm_task_bpffo8gba_layer_2_cycle_check_authored_tested_verified_self_correction_on_retry_gap_canonical_v2_conformance_confirmed -- TESTBED (Integrator)
