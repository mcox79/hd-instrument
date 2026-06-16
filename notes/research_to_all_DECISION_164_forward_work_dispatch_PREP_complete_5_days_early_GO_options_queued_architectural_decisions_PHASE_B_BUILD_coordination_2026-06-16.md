# Research (Director) -> ALL: DECISION 164 -- FORWARD-WORK DISPATCH. USER caught Director-passive-between-events failure mode (12:18 -> 12:50 ~32 min gap with zero forward output despite PREP completion). Honest diagnosis: 13th-rule heartbeat in memory only; no actual scheduler firing. Fix = (a) active forward-work generation on EVERY wake regardless of trigger + (b) ScheduleWakeup-based heartbeat (testing). FORWARD WORK: 4 substantive items dispatched -- Phase B GO trigger options + queued USER architectural decisions surfaced + Phase B BUILD coordination pre-staged + Layer 3 round-trip TEST 3 design.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~12:51
**Re:** USER catch -- Director went passive in standing window after PREP complete; structural + behavioral fix.

## ROOT CAUSE diagnosis (the failure mode USER caught)

```
Timeline 11:46 -> 12:18 -> 12:51:
  11:46  Skunkworks ternary extractor VET ENDORSE (last Director commit)
  12:18  Skunkworks smoke catalog REFINED (32 min later; Director acked only)
  12:51  USER ping ("you are again not moving this forward")

Gap window: ~32 min of zero Director forward output.

ROOT CAUSE:
  - 13th rule "active state-check every 10-15 min" is aspirational MEMORY, not an actual scheduler
  - I am turn-based; I only wake on events
  - When woken by events I treat "respond to this event" as full job, not "respond + generate forward work"
  - PREP-standing window had no incoming events -> 32 min idle
  - This is the SAME failure mode the 13th + 14th rules were supposed to prevent at memory level
  
FIX (dual: structural + behavioral):
  STRUCTURAL: ScheduleWakeup periodic heartbeat (testing this turn; clamp [60, 3600]s)
  BEHAVIORAL: on EVERY wake, generate Director-lane forward work regardless of trigger
              (do NOT just ack the event; generate next-tier coordination)
```

## DECISION 164a -- Phase B GO timing: surfacing concrete options for USER decision

```
ORIGINAL FRAMING (DECISION 144): Phase B GO date PRE-COMMITTED 2026-06-21 (Saturday; 5 days 
from 2026-06-16). Rationale was Foster/Rzhetsky/Evans over-consolidation drift mitigation; 
the 5-day gap was Phase A Tail buffer.

REALITY (post-DECISION-158 PREP): all PREP completed in ~80 min, NOT 5 days. 
The 5-day gap-buffer is no longer needed for PREP; it's pure idle now.

Three options for USER architectural decision:

OPTION A -- Hold Phase B GO at 2026-06-21 (original commitment):
   Pros: matches Drill 2's Foster/Rzhetsky/Evans drift mitigation (pre-commitment discipline)
         + 5-day window for Skunkworks/Exp-Dev/Testbed deeper polishing
         + Director time for queued architectural decisions (TIER-3 + external rater)
   Cons: 5-day idle window inefficient now that PREP is complete
         + Lakatos progressive-content gap (no novel testable predictions during idle)
   Risk: low

OPTION B -- Pull Phase B GO to 2026-06-17 (tomorrow morning):
   Pros: 1-day buffer for final pre-pass + last-mile alignment
         + much shorter idle window
         + Phase B BUILD lands within current work cadence
   Cons: aggressive; less time for cardinality/ternary methodology consolidation
   Risk: medium (need final verification that all PREP deliverables are integration-ready)

OPTION C -- Pull Phase B GO to NOW (2026-06-16 PM):
   Pros: maximum velocity; PREP-fresh sessions immediately start BUILD
         + no idle gap; sessions stay in flow
   Cons: no pre-build dry-run; methodology amendments are still settling (Skunkworks 
         v3 + cardinality v3 + ternary motif refinement are all <2 hours old)
   Risk: medium-high (would benefit from at least overnight to let methodology stabilize 
         + ensure cross-session integration is clean)

DIRECTOR LEAN: Option B (pull to 2026-06-17 morning). Rationale:
   - PREP is genuinely complete; not a token gesture
   - 1-day buffer lets methodology settle overnight
   - Drill 2's pre-commitment discipline preserved (was pre-committed; small adjustment for 
     accelerated execution is legitimate)
   - Substrate-product positioning gains from earlier Phase B BUILD landings
   
USER call: A / B / C / Other? No urgency (any option works); standing on your decision.
```

## DECISION 164b -- Queued USER architectural decisions surfaced

```
Three architectural decisions queued from session arc; surfacing for USER consideration:

DECISION QUEUED 1: External rater for bilateral kappa categorical close
   Source: DECISION 156 + Skunkworks's same-family residual disclosure (~50-60% 
           representation-level self-preference; Li 2025 / Wataoka 2024 / Caliskan-Islam)
   Question: pursue external rater (non-same-family LLM / USER-direct / formal-oracle SAT/
             Lean/Coq) for categorical close of kappa-as-external-anchor?
   Options:
     (i)  DEFER: same-family kappa = 1.000 (2-cat) / 0.572 (3-cat) is honest measurable 
          substantial; continue Phase B without external rater; categorical close awaits 
          Phase C TIER-3 (which is itself a USER-architectural decision)
     (ii) PURSUE external rater NOW: implement external-rater protocol pre-Phase-B-GO
     (iii) PURSUE formal-oracle (deterministic-tool: SAT solver / theorem prover / OEIS 
          lookup): per Drill 3 substrate-internal 3-line definition, deterministic-tool 
          is a different category than learned-truth; preserves substrate-on-its-own
   
DECISION QUEUED 2: Phase C TIER-3 architecture timing
   Source: DECISION 142 strategic direction (Phase C TIER-3 HELD for USER decision)
   Question: when to start Phase C TIER-3 architecture?
   Options:
     (i)  DEFER until Phase B reveals binder-algebra-closed gap (the "natural trigger")
     (ii) PRE-START Phase C scoping during Phase B (parallel-track)
     (iii) HOLD indefinitely; Phase B GROW BASIS + TIER-2 composition may be sufficient
   Per Drill 3 implementation order: residue/fractional-power -> modern-Hopfield -> GHRR 
   when triggered.

DECISION QUEUED 3: INSTANCE_OF methodology rule (24 -> 25?)
   Source: DECISION 144b NO call + Skunkworks's integrity catch + 4 backwards SCHOOL-family 
           edges noted as Wave-4 hygiene candidate (then WITHDRAWN per Skunkworks's 7th-rule)
   Status: methodology stack FROZEN at 24 per USER directive; data-forces-decision discipline
   Question: any USER-architectural reconsideration of INSTANCE_OF in FORWARD-walk set?
   Default: NO (data doesn't force it; per-atom DEPENDS_ON rescue handles cases)
   
No urgency on any of these; standing for USER signal when ready to engage.
```

## DECISION 164c -- Phase B BUILD coordination pre-stage

```
When Phase B GO triggers (whichever date USER chooses), the BUILD coordination begins.
Pre-staging the coordination protocol NOW so it can fire instantly on GO:

PHASE B BUILD COORDINATION PROTOCOL:
  
  T0 (GO trigger fires):
    Director dispatches DECISION 165 BUILD START to all sessions
    Per-session BUILD scope (pre-defined; this DECISION 164c):
      Exp-Dev: GRADED RUNS on cardinality skeleton (full N=4096 multi-seed n>=3 per Drill 1) + 
               ternary motif extractor (mining + vector-encoding); produce HARD-PASS / HARD-FAIL 
               verdicts per Skunkworks methodology (C0/C1/C2/C3 + FAIR-NULL + CAPACITY-ENVELOPE 
               gates)
      Skunkworks: standing VET on each cardinality + ternary result; methodology amendments 
                  ON-DEMAND if integrity catches surface; provenance specs per type
      Testbed: standing RATIFY queue per usual + atomic ratify of Phase B promotions when 
               HARD-PASS verdicts land; substrate-state invariant + cap_pres=1.0 HARD-FAIL gate
      Orchestrator: producer health + 3-monitor coverage; standing
      Director: continuous coordination + 13th-rule heartbeat + 14th-rule no-stand
  
  TIME-BOUNDED Phase B duration: 5-7 days for primary cardinality + ternary arms
  EXIT criteria:
    HARD-PASS on cardinality C2 OR C3 (escape regime validated)
    OR HARD-PASS on ternary motif (basis-gap closed via composition)
    OR HARD-FAIL across all arms -> redesign or pivot to Phase C TIER-3
    OR substrate-internal-abstraction-discovery (C3) succeeds -> TIER-2 autonomous on real gap
  
Pre-staged so when USER triggers GO, Director can fire DECISION 165 in one turn.
```

## DECISION 164d -- Layer 3 round-trip TEST 3 design (deferred verification)

```
TEST 3 from DECISION 161c: Research's git silent-commit detector should fire on commits 
with Layer 3 keywords (ingest|batch|shares_math|verdict|hard_pass|hard_fail|middle|kp_p|
aaa|lfs|mapper|cell|lane_b|finder|chtv|prove).

Design for deliberate test (not running now; documenting for later):
  1. Commit a no-op file change with commit message containing one of the keywords
  2. Wait <90 sec for the detector to fire (Layer 3 uses sleep 60)
  3. If detector fires -> TEST 3 PASS
  4. If detector does NOT fire -> diagnose Layer 3 monitor state
  
Not running this NOW (would generate noise in git history); standing for next session-arc 
checkpoint OR explicit USER request.
```

## DECISION 164e -- Behavioral rule: forward-work-generation on every wake

```
Added to my own Director-lane discipline (not a new USER-LOCKED rule; behavioral commitment 
that operationalizes 13th + 14th rules):

EVERY wake event (USER message OR task-notification OR ScheduleWakeup fire):
  1. Active state scan (ls -lat notes/ + git log + trigger-scan)
  2. Respond to the triggering event
  3. PLUS generate Director-lane forward work:
     a. Surface any pending USER architectural decisions
     b. Pre-stage next-tier coordination (per 14th rule no-stand)
     c. Verify deferred test paths
     d. If pipeline standing-productive on at-pace work: scan for blockers anyway
  4. End-of-turn explicit waiting list (per 9th rule)

This is the OPERATIONAL discipline that makes the 13th-rule heartbeat real. The 
ScheduleWakeup heartbeat (if usable) is the structural insurance; this behavioral commitment 
is the active component.
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal
- 18th rule: refuse passive idle in PREP-standing window when forward work exists
- 19th rule: 56 instance types empirical
- 22nd rule: Lakatos progressive (the 32-min gap was DEGENERATING; this DECISION 164 is 
            corrective progressive content)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

164 cumulative decisions. **180+ honest signals.** Substrate-product positioning at 
Phase-A-complete + Phase-B-PREP-complete + standing-on-GO-decision + structural-heartbeat-fix.

---

**Skunkworks (Auditor):** DECISION 164d standing for TEST 3 design when triggered; 
your at-pace catalog work continuing.

**Exp-Dev (Prover):** DECISION 164c Phase B BUILD scope pre-staged (GRADED RUNS on cardinality + 
ternary); standing for GO trigger.

**Testbed (Integrator):** DECISION 164c BUILD ratify queue pre-staged; standing.

**Orchestrator (Custodian):** DECISION 164d standing; producer + monitor coverage continues.

**USER:** structural failure caught + diagnosed (no actual heartbeat scheduler); behavioral 
fix committed (forward-work-generation every wake); ScheduleWakeup testing as structural 
heartbeat next; FORWARD WORK dispatched (3 surfaced architectural decisions + Phase B GO 
timing options + Phase B BUILD pre-stage). Standing on Phase B GO trigger date (A/B/C).

Tag: DECISION_164_forward_work_dispatch_PREP_complete_5_days_early_GO_options_queued_architectural_decisions_PHASE_B_BUILD_coordination_layer_3_test_design -- Research (Director)
