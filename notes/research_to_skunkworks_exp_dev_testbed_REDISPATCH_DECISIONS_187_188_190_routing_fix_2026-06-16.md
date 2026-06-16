# Research (Director) -> Skunkworks + Exp-Dev + Testbed: ROUTING FAILURE CAUGHT BY USER + REDISPATCH of DECISIONs 187, 188, 190 which DID NOT ROUTE to your session event logs due to my shortened-filename workaround for Windows 260-char path limits omitting the `*skunkworks*` / `*exp_dev*` / `*testbed*` substring patterns event_bus.sh routing rules require. 78th audit-discipline instance type CANDIDATE: ROUTING-COMPLIANT-FILENAME-DISCIPLINE-BROKEN-BY-PATH-LENGTH-WORKAROUND. USER caught the failure; honestly disclosing + fixing. Sessions have been IDLE waiting for me; this redispatch unblocks. PHASE B CLOSED + PHASE C TIER-3 ARC OPENS; all 5 architectural calls dispatched per DECISION 190 (USER full delegation GO).

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~18:05
**Re:** USER catch: "you're waiting on everyone? do they know that?" -- NO, they did not, because routing failed silently.

## ACK USER catch (honest)

```
USER asked: "you're waiting on everyone? do they know that?"

Verification (data/events/<session>.log tails):
   Skunkworks: last routed event 17:24:32 (Exp-Dev TOP-3b alpha_c correction)
   Exp-Dev: last useful routed event 17:26:08 (Skunkworks VET TOP-3b sound);
            then IDLE entries 17:31/17:42/17:53 (30+ min idle)
   Testbed: last routed event 17:18:40 (DECISION 186)
   Orchestrator: kept current through TRACK D Phase 4 (filenames had _to_orchestrator_)

DECISIONs 187 + 188 + 190 DID NOT ROUTE to skunkworks/exp_dev/testbed event logs.
Diagnostic: event_bus.sh routes via filename substring match:
   *skunkworks*  -> route to skunkworks log
   *exp_dev*     -> route to exp_dev log
   *testbed*     -> route to testbed log
   *to_orchestrator_* -> route to orchestrator log

My DECISION 187/188/190 filenames:
   research_DECISION_187_track_B_FINAL_CERT_S1_S4_locked_TOP1_retracted_*
   research_DECISION_188_TOP3b_RETRACT_file_finding_TRACK_A_DRY_*
   research_DECISION_190_USER_GO_all_architectural_calls_*

NONE contain skunkworks / exp_dev / testbed substrings. They were caught only by
the widenet catch-all monitor (bluhtrdku) -> my own awareness only -> sessions
silent. Sessions have been IDLE since 17:26 (~40 min) because they hadn't seen
the recent decisions.

This is a 14th-rule violation by inadvertent silent routing: I thought I was
dispatching forward-work; in reality sessions were standing because they didn't
know there was work. USER caught it; honestly fixing.
```

## DECISION 190g -- 78th audit-discipline instance type CANDIDATE

```
78th audit-discipline instance type CANDIDATE:
   ROUTING-COMPLIANT-FILENAME-DISCIPLINE-BROKEN-BY-PATH-LENGTH-WORKAROUND

   When a workaround for one system constraint (Windows 260-char path limit)
   breaks an invariant of an adjacent system (event_bus.sh routing-by-filename
   substring match), the workaround creates a SILENT FAILURE MODE: notes
   appear committed (Director thinks dispatch happened) but don't propagate
   (sessions stand idle). The cross-system invariant must be re-verified
   when workarounds are introduced.

   Discipline pattern:
   (a) when constrained by system A (path length), re-verify the workaround
       preserves system B's invariant (routing by substring);
   (b) include the routing substrings (`skunkworks`, `exp_dev`, `testbed`,
       `to_orchestrator`) in EVERY routing-intended filename;
   (c) if path length forces choice between routing-substrings and
       descriptive-name, the routing substrings win (sessions need to know);
   (d) on USER-active-state-check catch (13th rule operating at USER lane),
       acknowledge the failure honestly + fix immediately + 19th-rule-self-
       correct + log instance for future filename discipline.

   Today's instance: Director shortened filenames after the first 187 attempt
   hit Windows path limit; the shortenings dropped session substrings;
   routing silently failed for DECISIONs 187 + 188 + 190; sessions idle 40
   min until USER active-state-check caught.

   Composes with prior:
     13th rule (active state-check + USER's catch of sessions-not-acting)
     14th rule (no-stand default; broken by silent routing failure)
     19th rule (self-correction on own dispatch mechanics)
     74th candidate (5th-verify-before-asserting-catch-on-own-prior-ranking)
     77th candidate (counters-inherited-from-checkpoint-without-verification-drift)
     78th (THIS) -- routing-compliant-filename-discipline-broken-by-path-length-
        workaround

   Pattern is: substrate-product positioning maturity = ability to recognize
   when cross-system invariants are silently broken by within-system workarounds.
   The fix is filename discipline (include routing substrings) + USER active
   state-check + honest acknowledgement when caught.
```

## REDISPATCH -- read the originals at these paths

```
ALL SESSIONS: please read these 3 notes (the originals, not this redispatch):

1. DECISION 187 (TRACK B FINAL CERT + S1-S4 LOCKED + TOP-1 RETRACTED + TRACK D
   dashboard project dispatched + 74th candidate):
   notes/research_DECISION_187_track_B_FINAL_CERT_S1_S4_locked_TOP1_retracted_74th_TOP3a_TOP3b_GO_dashboard_orchestrator_2026-06-16.md

2. DECISION 188 (TOP-3b RETRACTED + TRACK A DRY 2nd-witness confirmed + 75th + 76th
   candidates + substrate-internal authoring surface exhausted):
   notes/research_DECISION_188_TOP3b_RETRACT_file_finding_TRACK_A_DRY_CONFIRMED_2nd_independent_witness_75th_76th_candidates_USER_arc_2026-06-16.md

3. DECISION 190 (USER FULL DELEGATION GO; PHASE B CLOSED; PHASE C TIER-3 ARC OPENS;
   all 5 architectural calls dispatched parallel):
   notes/research_DECISION_190_USER_GO_all_architectural_calls_PHASE_C_TIER_3_arc_opens_parallel_dispatch_2026-06-16.md
```

## Per-session DIRECTIONS (summary of what each session is waiting on; full context in originals)

```
EXP-DEV (Prover):
   YOU HAVE 3 PARALLEL JOBS dispatched per DECISION 190:
   (a) 190a TRACK B C1 prototype-retrieval execution prereg DESIGN
       - S1-S4 HARD conditions: standard prototype additive noise documented;
         (p,k,M) grid of 144 cells [p in {0.05..0.30} 6 pts; k in {2..8} 6 pts;
         M in {32..256} 4 pts]; k>2 load-bearing not k=2 degenerate; honest-
         negative-per-axis preserved; corr(bundle,c) excluded from seed
       - Output: prereg memo for Skunkworks FINAL pre-execution VET +
         Director ratify before any execution
       - Heavy compute -> remote desktop dispatch via Orchestrator AFTER prereg
         ratifies
   (b) 190c 218-signal pure-substrate cardinality cell-build DESIGN
       - bypasses bAbI RAG (11th-rule-incompatible); pure-substrate pipeline
         (encoding -> cleanup_distinct_count -> readout); honest-negative path
       - Output: design memo
   (c) 190f drift_kappa3 MIDDLE-BAND RATIO filing (light hygiene)
       - metric_type:RATIO/detection (NOT accuracy/capability); STRICT type-
         discipline per Skunkworks; closes TRACK A ledger
       - Output: authored finding for Testbed ratify chain

SKUNKWORKS (Auditor):
   YOU HAVE 3 PARALLEL JOBS dispatched per DECISION 190:
   (a) 190b Phase C TIER-3 architecture paper-design
       - residue-FPE + modern Hopfield-cleanup + GHRR per Drill 2+4 architecture
         order; each primitive must have CHTV-1 + L6-PROOF candidate; closed-form
         theory required
       - Output: scoping memo
   (b) 190d Drill 5 continuous-FPE concurrent scoping (linked to TIER-3 trigger)
       - parallel with TIER-3 paper-design; ~1 cycle incremental
   (c) Standing FINAL pre-execution VET on Exp-Dev's 190a TRACK B C1 prereg
       when it lands (gerrymander-free verification on the actual prereg, post-
       hoc-impossible)
   (d) Standing VET on Director's 190e hookup design memo (when drafted)
   (e) Standing STRICT type-discipline VET on Exp-Dev 190f drift_kappa3 filing
       (metric_type:RATIO/detection NOT accuracy/capability)

TESTBED (Integrator):
   YOU HAVE 2 PARALLEL JOBS dispatched per DECISION 190:
   (a) 190f drift_kappa3 ratify chain when Exp-Dev hands off (light;
       metric_type:RATIO; cap_pres=1.0; STRICT type-discipline)
   (b) Standing for Phase C TIER-3 execution ratify chains as outputs land:
       - TRACK B C1 results (if Skunkworks-VET'd prereg executes and uniqueness
         either confirms or shows honest negative)
       - 218-signal pure-substrate cardinality cell results
       - TIER-3 primitive atoms (if Skunkworks scoping yields proposed atoms)

ORCHESTRATOR (Custodian):
   YOU ARE CURRENT through TRACK D Phase 4 (filenames _to_orchestrator_ routed
   correctly). Standing for:
   (a) Remote-desktop dispatch for 190a TRACK B C1 execution WHEN Skunkworks
       FINAL pre-execution VET + Director ratify clears the prereg (not yet)
   (b) Continuing state collector refreshes to keep dashboard substrate state
       tab fresh
```

## Pipeline state (unchanged from DECISION 190; sessions now know)

```
Phase B BUILD: CLOSED
Phase B tail: drift_kappa3 hygiene filing GO (closes TRACK A)
Phase C TIER-3 ARCHITECTURE ARC: OPEN
   190a TRACK B C1 execution prereg DESIGN (Exp-Dev)
   190b TIER-3 paper-design (Skunkworks)
   190c 218-signal pure-substrate cardinality cell-build design (Exp-Dev)
   190d Drill 5 continuous-FPE concurrent scoping (Skunkworks)
   190e Director hookup design + USER procurement direction (Director-side)
   190f drift_kappa3 RATIO filing (Exp-Dev + Skunkworks VET + Testbed ratify)
TRACK D: all 4 phases COMPLETE; substrate state tab + 3D viz tab LIVE
USER: 0 architectural calls standing; 1 procurement direction needed (190e);
   3 TRACK D design Q's open non-blocking

Substrate state (CORRECTED via direct corpus count):
   26285 atoms / 4947 relations / 115 signatures / 207-of-207 axiom term
   capability_preservation=1.0 / methodology FROZEN at 24
```

## Safety / invariants

- ASCII only
- 13th rule: USER active state-check caught the routing failure; honest acknowledgement
- 14th rule: redispatch unblocks the sessions; no-stand default restored
- 18th rule: refuses to hide the routing failure; honest disclosure
- 19th rule: 78 instance types empirical (44 + 34 today)
- 22nd rule: progressive (routing-discipline refinement is methodology-adjacent
            integrity progressive content)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24
- Future filename discipline: ALL routing-intended notes include `*skunkworks*` /
  `*exp_dev*` / `*testbed*` / `*to_orchestrator*` substrings; if path-length forces
  truncation, the routing substrings WIN.

## Session tally

190 cumulative decisions. **225+ honest signals.** 78 audit-discipline instance types
(44 + 34 today). Substrate state CORRECTED + PRESERVED.

---

**Skunkworks (Auditor):** READ DECISION 187 + 188 + 190 (paths above); start
190b TIER-3 paper-design + 190d Drill 5 scoping + standing FINAL pre-execution
VET on 190a + STRICT type-discipline VETs. ~40 min lost; my apology.

**Exp-Dev (Prover):** READ DECISION 187 + 188 + 190 (paths above); start
190a TRACK B C1 prereg DESIGN + 190c 218-signal cell-build design + 190f
drift_kappa3 RATIO filing. ~40 min lost; my apology.

**Testbed (Integrator):** READ DECISION 186 + 187 + 188 + 190 (paths above);
TRACK A standard outcome was TOP-1 + TOP-3b BOTH RETRACTED + drift_kappa3
hygiene filing as the only TRACK A atom-mutation; standing for Phase C TIER-3
execution ratify chains. ~40 min lost; my apology.

**Orchestrator (Custodian):** you're current; standing for remote-desktop
dispatch on 190a (when Exp-Dev prereg ratifies through Skunkworks final VET);
continuing state collector refreshes. No change.

**USER:** Caught a real silent failure. Filename-length workaround for Windows
260-char path limit broke event_bus.sh routing-by-substring rules; DECISIONs
187/188/190 didn't reach session event logs; sessions IDLE 40 min waiting.
78th audit-discipline candidate. Redispatched; sessions now actionable. Going
forward I'll keep routing substrings (`skunkworks` / `exp_dev` / `testbed` /
`to_orchestrator`) in every routing-intended filename; if path-length forces
truncation, routing substrings win.

Tag: REDISPATCH_DECISIONS_187_188_190_routing_fix_78th_candidate_routing_compliant_filename_discipline_broken_by_path_length_workaround_user_active_state_check_caught -- Research (Director)
