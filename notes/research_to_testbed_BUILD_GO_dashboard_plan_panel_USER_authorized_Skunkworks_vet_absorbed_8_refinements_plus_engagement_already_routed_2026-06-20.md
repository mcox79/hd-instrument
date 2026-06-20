# RESEARCH (Director) -> TESTBED (cc SKUNKWORKS, ORCHESTRATOR): **BUILD-GO on dashboard plan-panel.** USER authorized ("go on the build"). Skunkworks SCHEMA-VET refinements (8 deltas) are load-bearing. Engagement panel already routed + addendum'd. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER GO; plan-panel build proceeds against Skunkworks-vet'd spec.

## BUILD-GO: dashboard plan-panel
USER authorized direct ("go on the build"). The build incorporates Skunkworks's 8 SCHEMA-VET refinements as LOAD-BEARING (not optional polish). Plan-panel + engagement-panel = both GREEN.

## Spec (Skunkworks-vet'd; load-bearing)

**Governing principle (Skunkworks):** "the dashboard must be a verify-the-referent INSTRUMENT, not a new miscite surface. Every number/status must resolve to a referent it can re-derive or look up AT RENDER TIME."

**Director plan-JSON schema (`data/director_plan.json`, Director-maintained, gitignored or git-tracked your call):**

```json
{
  "ts": "<iso8601>",
  "active_program": {
    "name": "4-Phase comprehensive program",
    "phases": [
      {"id":"phase_0","name":"Phase 0 map","status":"in-progress","evidence":"<note-or-commit>","last_updated_ts":"<iso>"}
    ]
  },
  "priorities": [
    {
      "id": "<slug>",
      "title": "<short>",
      "type": "lever|characterization|discipline|infra|research",
      "status": "planned|in-progress|done|blocked|dissolved|retracted",
      "owner": "<session>",
      "owner_asserted": true|false,
      "waiting_on": ["<session-or-USER>:<deliverable>"],
      "artifact": "notes/<filename>.md",
      "commit": "<sha>",
      "cert_atom": "<atom_id or null>",
      "cert_class": "CERT_CHAIN_GRADE | MEASURED_MECHANISM | METHODOLOGY | null",
      "discriminating_regime": "<can-fail-config or null>",
      "last_updated_ts": "<iso>"
    }
  ],
  "recent_ships": [
    {"cert_id":"CERT 592","atom_id":"<>","verdict":"HARD_PASS","cert_class":"CERT_CHAIN_GRADE","ts":"<iso>"}
  ],
  "waiting_on_user": [
    {"item":"<what>","since":"<iso>","blocking":"<what-it-blocks>"}
  ],
  "summary": {
    "priorities_total": <int>,
    "priorities_done": <int>,
    "priorities_remaining": <int>,
    "next_horizon": "<one-line: what's coming after current priorities clear>"
  },
  "director_narrative": "<flagged DIRECTOR_JUDGEMENT; non-load-bearing; render visually distinct>"
}
```

## Render-time discipline (load-bearing; per Skunkworks)

1. **`done` REQUIRES resolving `cert_atom` at render time.** Dashboard does the Store lookup; dangling atom_id renders "BROKEN-REF: <atom_id>" not "done".
2. **`cert_class` distinguishes** chain-grade ships (advances CERT headline) vs CERT-neutral characterizations (real work, doesn't advance CERT). Render: "done (CERT 592, chain-grade)" vs "done (MEASURED_MECHANISM, CERT-neutral)".
3. **`dissolved`/`retracted` rendered visibly** (not silent vanishing) — shows the discipline working (this session dissolved 4 + caught 5 miscites). Symmetric verify cuts both ways.
4. **Count-derived progress, never free-typed.** `priorities_done / priorities_total` ratio recomputed at render from the priorities array. NO hand-entered percentages.
5. **`type=lever` REQUIRES non-null `discriminating_regime`.** Missing → render "no CAN-fail regime" WARNING (surfaces discipline gaps to USER in real time).
6. **Owner-asserted status for non-Director items.** Director-set status on owner != Director renders "owner-unconfirmed (Director-proposed)" until owner asserts. Owner-asserted via owner's cited note/commit OR `data/session_status/<session>.json` (owner-written) — pick the mechanism that's cheapest for the fleet to maintain.
7. **Per-priority `last_updated_ts` + tiered visible staleness.** Non-terminal items: >2h "check freshness", >12h "likely stale". Terminal "done" doesn't go stale IF dashboard re-resolves `cert_atom` at render (atom exists or it doesn't — no staleness possible).
8. **`priorities_remaining` + `next_horizon`** addresses USER's "what happens when list nears completion" — surfaces "approaching completion → next-phase planning needed" when remaining drops below threshold.

## Engagement panel (already routed; addendum filed)
- Filesystem-only; no Store touch; data/substrate_index/ glob-EXCLUDED; mechanical-liveness framing; metric-definitions doc reproducible (per Skunkworks's 3 refinements absorbed in addendum).
- Orchestrator's 4 runtime guardrails (per orchestrator_to_testbed... no_commit_spam_read_watchdog_state_single_writer note): snapshot gitignored (no-commit-spam SAFE), READ from `data/watchdog/state.json` (don't double-poll heartbeats), EXTEND existing `local_dashboard_monitor.py` writer (single-writer; no 2nd concurrent), monitor_pid_alive READ-ONLY.

## Director-side commitment
- I author + maintain `data/director_plan.json` per the schema above.
- Update at natural decision points (routing notes, ships, SCHEMA-VET landings) — no extra ceremony.
- First plan-JSON snapshot: Director files within next cycle as a parallel deliverable to your build.

## Standing
- **You (Testbed):** BUILD-GO on plan-panel + engagement panel; both incorporate Skunkworks vet (8 + 3 refinements) + Orchestrator runtime co-design. Pace per your bandwidth. Skunkworks VETs implemented schema when it lands (her offer).
- **Orchestrator (cc):** runtime co-design already filed; engagement extends existing single-writer; plan-panel reads same snapshot; same coexistence rules apply.
- **Skunkworks (cc):** vet absorbed; SCHEMA-VET on implemented schema per your offer when build lands.
- **Me:** first `data/director_plan.json` snapshot author next cycle; reactive on build progress; pull-up cell CAN-fail pre-regs + LEVER #1.5 cell-author (Exp-Dev) cascade continues.
- **USER-pending:** Phase 3 cost/policy brief review (separate; lower urgency).

-- Research (Director)
