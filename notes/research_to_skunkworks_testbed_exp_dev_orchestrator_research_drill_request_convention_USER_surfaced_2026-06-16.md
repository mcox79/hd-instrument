# Research (Director) -> All sessions: research drill request convention (USER-surfaced)

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~21:18
**Re:** USER asked "other sessions should be able to request research drills through you - do they know that?" Surfacing the convention explicitly.

## CONVENTION (explicit; not previously documented)

```
ANY session (Skunkworks / Testbed / Exp-Dev / Orchestrator) MAY request
a research drill from Director by writing a routing note:

   notes/<your_session>_to_research_drill_request_<topic_slug>_<date>.md

CONTENTS:
   - WHY: what substrate gap, finding, or open question motivates the drill
   - SCOPE: literature scan (preferred) vs adversarial verification vs
            architectural comparison
   - DEPTH: 1x (single sonnet drill in-background) or 2x (two parallel
            sonnet drills for adversarial cross-check) or 3x (three
            independent drills for high-stakes findings)
   - SAFETY constraints required by /loop standing duties:
       * generic literature queries only (NO project-specific predicted
         numerical values or cycle numbers in web searches)
       * ASCII output only
   - URGENCY: routine (any time) vs blocking (Director must dispatch
              before next phase fires)

Director will dispatch the drill in-background (research subagent or
   Agent with subagent_type=research) and route the synthesis back to
   the requesting session when complete.

ANCHOR-DEPTH RULE: Director maintains anchor list depth (per /loop
   standing duties Step 4). If FEWER THAN 3 active Exp-Dev handoffs in
   last 24h, Director self-dispatches 3x deep drills on top substrate
   problems/opportunities (CHARACTERISTICS / PERFORMANCE; NOT MARKETS).
```

## CURRENT QUEUE STATE

- 0 active drills in flight (P1 + P2 cert chains closed)
- 3 fresh drills dispatching this turn per USER recommendation request:
   * 2x cap-extension techniques for resonator networks
   * 2x modern Hopfield capacity scaling
   * 1x sparse-Hopfield value regime (HEAD-3 OOS)

## NEGATIVES TO 2x / VALUABLE DRILLS (per USER question)

```
NEGATIVES of 2x:
   - Token/wall-clock cost (sonnet background; tolerable up to ~4 concurrent
     per /loop cap)
   - Drift risk: speculative drills produce output not load-bearing to
     substrate; mitigate by anchoring drills to REAL substrate gaps
     (negative findings or capacity bounds just measured)
   - Substrate-internal rule (11th USER-LOCKED) preserved: drills are
     LITERATURE SCANS, not in the invention loop

VALUABLE TODAY (3 dispatched this turn):
   1. Resonator capacity-extension techniques (anchored on P2 GATE-F
      bound at ~R<=255255; 2x)
   2. Modern Hopfield network capacity scaling (anchored on Ramsauer
      lineage + GATE-D PASS; 2x)
   3. Sparse-Hopfield value regime / dense-codebook crossover (anchored
      on HEAD-3 OOS consumer-pull deferral; 1x)

LATER (NOT dispatched; documented for reference):
   - Wasserstein/Sinkhorn alternative decoders (alternative to OLS-Gram;
     2x; defer unless P2 capacity-extension fails)
   - Capability-preservation gates in continual learning (extends 18th
     + 22nd rules theory base; 1x; defer unless methodology stack needs
     extension)
```

## Substrate state

```
26300 atoms / 5219 relations / cap_pres=1.0 / methodology FROZEN at 24
P2 cert chain on track to honest closure (kymn ADD convergent 3-of-3
   sessions; Skunkworks STEP-7 VET cert-owner adjudicates)
```

## Standing

- **Skunkworks:** STEP-7 VET + cert-owner kymn call; Tier 2 PHASE 2 spec
- **Testbed:** STEP-9 P2 atom reactive on STEP-8 (7-edge list expected)
- **Exp-Dev:** STEP-7 results DELIVERED; STEP-9 atom prose endorsement
- **Orchestrator:** STEP-9 ingest standing
- **Director:** STEP-8 ratify reactive on Skunkworks STEP-7 VET +
              3 research drills dispatching in parallel this turn

-- Research (Director)
