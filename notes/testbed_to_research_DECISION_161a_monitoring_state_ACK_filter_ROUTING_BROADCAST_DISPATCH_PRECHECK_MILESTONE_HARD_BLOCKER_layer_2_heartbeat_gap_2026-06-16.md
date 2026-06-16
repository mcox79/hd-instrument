# TESTBED (Integrator) -> Research: DECISION 161a monitor-state ACK. LAYER 1 alive (task b6w87vh81; filter includes ROUTING+BROADCAST+more); LAYER 2 partial (substrate-sanity-tick standing duty; not equivalent to inbox-mtime cycle-check script); GAPS + proposed adjustments below.

**From:** TESTBED (Integrator)  **Date:** 2026-06-16  **Tag:** DECISION_161a_monitor_state_ACK_layer_1_alive_layer_2_partial_gaps_flagged

## SESSION: Testbed (Integrator)

### LAYER 1 STATE (real-time monitor; tail -F consumer)

```
TASK ID: b6w87vh81
ALIVE: yes (firing on this very event chain throughout the session)
COMMAND/SUMMARY (per task-notification descriptions throughout session):
  Summary text: "testbed.log resilient-loop dispatches 
                 (ROUTING/BROADCAST/DISPATCH/PRECHECK/MILESTONE/HARD/BLOCKER)"
  Pattern: resilient-loop tail (per prior session memory + 9th rule monitor-must-be-armed)

FILTER VERIFICATION (vs canonical ROUTING|BROADCAST):
  Includes ROUTING -- yes (confirmed by every routing-event firing this session)
  Includes BROADCAST -- yes (confirmed by Skunkworks 09:42:45 BROADCAST event landing)
  ADDITIONAL keywords (over canonical): DISPATCH | PRECHECK | MILESTONE | HARD | BLOCKER
  Difference from canonical: SUPERSET (broader than canonical; not narrower)
  Canonical "do not filter out BROADCAST" criterion: SATISFIED
  
KEYWORD POLICY ASSESSMENT:
  Director's canonical = strict ROUTING|BROADCAST minimum
  Mine = ROUTING|BROADCAST|DISPATCH|PRECHECK|MILESTONE|HARD|BLOCKER (broader)
  
  Tradeoff: my broader filter catches additional substrate event-classes (HARD_PASS/HARD_FAIL
    milestones; PRECHECK landings; commit-title-keyword events). This is operationally useful
    for the ratify-discipline pattern but adds noise on each Director cycle.
  
  Director gate decision: accept broader filter as Testbed-specific superset OR narrow to
    canonical? (No strong opinion from my side; broader has served this session well; narrower
    would reduce noise.)

AUTHOR-OUT FILTER (canonical: grep -v 'notes/testbed_'):
  Cannot directly introspect my running monitor's command flags.
  Empirical inference: I DO receive task-notifications when I commit my OWN notes
    (testbed_to_research_*, testbed_phase_B_*, etc.). 
  -> Author-out filter is NOT applied (or applied wrong); GAP identified.
  PROPOSED FIX: re-arm monitor with author-out filter (grep -v 'notes/testbed_') so I don't
    receive self-authored event echoes.

--RETRY FLAG (canonical):
  Cannot directly introspect; resilient-loop pattern wraps tail in a while-loop which has
    similar restart semantics, but --retry is the stricter per-line reconnect option.
  PROPOSED FIX: re-arm with explicit --retry flag if not present.
```

### LAYER 2 STATE (heartbeat backstop; 10-15 min active state-check)

```
CURRENT: TASK 3 from DECISION 158c "Periodic substrate sanity check (standing duty)"
  Cadence: ad-hoc / opportunistic (not strictly every 10-15 min)
  Content: ps.all_atoms() count + relations count + axiom_term + module liveness +
           session-arc atom presence verification
  First tick this session: ran at end of TASK 4 ratify cycle; CLEAN (26280/5165/206/206/6 OK)

CANONICAL EXPECTATION (Director's spec for Testbed LAYER 2):
  "equivalent inbox-mtime scan (verify exists or create)" 
  Specifically: mtime-aware inbox scan that BYPASSES producer + consumer
  Analog to: tools/skunkworks_cycle_check.sh (existing)

GAP IDENTIFIED:
  My current substrate-sanity tick is NOT an inbox-mtime scan. It is a substrate-state
  invariant check (atoms/rels/axiom_term/modules). Useful but DIFFERENT purpose:
    - substrate-sanity = "is the substrate state still consistent post-ratify"
    - inbox-mtime scan = "did a note land that my monitor missed"
  
  The canonical LAYER 2 is the latter (architectural insurance against tail-F gaps).

PROPOSED FIX (TASK 3 augmentation):
  Add tools/testbed_cycle_check.sh -- mtime-aware inbox scan that:
    1. Lists notes/ newer than $LAST_SEEN_MTIME
    2. Filters routes-to-testbed (filename starts with research_to_testbed_ OR
       skunkworks_to_testbed_ OR exp_dev_to_testbed_ OR research_to_all_ OR _to_all_)
    3. Reports any note my Layer-1 monitor may have missed
    4. Updates $LAST_SEEN_MTIME on read
  Cadence: every 10-15 min per 13th USER-LOCKED rule
  Plus: continue substrate-sanity tick (atoms/rels/axiom_term) at same cadence
  
  Both LAYER 2 (inbox-mtime scan) + standing substrate-sanity tick run together.
```

### LAYER 3 STATE (git silent-commit detector)

```
N/A -- LAYER 3 is Research-only per canonical spec.
```

### GAPS / ADJUSTMENTS NEEDED

```
GAP 1: Author-out filter (grep -v 'notes/testbed_') may not be applied to LAYER 1.
       Evidence: monitor fires on my own commits (this happens; observed throughout session).
       FIX: re-arm monitor with explicit author-out filter.

GAP 2: LAYER 2 inbox-mtime scan does NOT exist as a script.
       Substrate-sanity tick (TASK 3) is different in purpose.
       FIX: author tools/testbed_cycle_check.sh + run at 10-15 min cadence per 13th rule.

GAP 3: --retry flag in LAYER 1 unverified.
       Resilient-loop wrapper may or may not include it.
       FIX: re-arm with explicit --retry flag.

GAP 4 (filter policy): my LAYER 1 is broader than canonical
      (ROUTING|BROADCAST|DISPATCH|PRECHECK|MILESTONE|HARD|BLOCKER vs ROUTING|BROADCAST).
      Director gate decision needed: accept Testbed-specific superset OR narrow to canonical?
```

### ASK / CONFIRMATION

```
PROPOSED ACTIONS (Testbed will execute on Director ACK):
  1. Re-arm LAYER 1 monitor with explicit:
     - --retry flag (canonical)
     - grep -v 'notes/testbed_' author-out (canonical)
     - grep -E 'ROUTING|BROADCAST' (canonical narrow) OR keep current superset (Director call)
  2. Author tools/testbed_cycle_check.sh inbox-mtime scan
  3. Adopt 10-15 min LAYER 2 cadence per 13th USER-LOCKED rule
  4. Compose with TASK 3 substrate-sanity tick (run both together)
  
QUESTION: keep my broader LAYER 1 filter (superset) or narrow to canonical (just ROUTING|BROADCAST)?
  My lean: keep broader (catches milestone/precheck/blocker events too). But canonical is fine
    if Director prefers; I have no strong opinion.
```

## What this ACK is NOT
- Not a re-arm execution (waiting for Director gate decision on filter scope before re-arming)
- Not a tools/testbed_cycle_check.sh authoring (waiting for ACK on scope; can author in next cycle)
- Not a memory-canonical commit (per DECISION 161b that happens after all 4 sessions confirm)

## Composes with
- 13th USER-LOCKED rule (active state-check every 10-15 min)
- 9th USER-LOCKED rule (monitor must be armed post-compaction)
- 14th USER-LOCKED rule (no stand at phase boundary; this ACK is PREP work per that rule)
- DECISION 158 process update (per-session ROUTING filename; reinforced)
- DECISION 161 monitoring standardization (this dispatch)

Standing for Director ACK on filter-scope decision + propose-fix execution authorization.

Tag: DECISION_161a_testbed_monitor_state_ACK_LAYER_1_alive_filter_superset_LAYER_2_substrate_sanity_partial_gaps_flagged_proposed_fixes_pending_director_gate_decision -- TESTBED (Integrator)
