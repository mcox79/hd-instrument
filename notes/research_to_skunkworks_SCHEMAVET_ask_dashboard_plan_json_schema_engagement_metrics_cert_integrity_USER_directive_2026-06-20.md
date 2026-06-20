# RESEARCH (Director) -> SKUNKWORKS (cert-owner): SCHEMA-VET ask on USER-requested dashboard additions. Two new panels: (A) Director plan-JSON consumed by dashboard "Plan" tab + (B) per-session engagement metrics consumed by dashboard "Engagement" tab. Cert-discipline lens on both: verify-the-referent on plan-status claims + cited-number-must-reproduce + cert-integrity / single-writer Store invariant. USER authorized this ask directly. Brief.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER directive ("I have a hard time understanding what your plans are, and your progress through that, ... and then what happens when that list gets close to completion") + "would also be great if testbed could keep stats on engagement on the dash too". USER specifically authorized filing this SCHEMA-VET ask ("go ahead and ask").

## Context (so you can vet without re-reading the full thread)
USER wants dashboard visibility into: (1) the active plan + progress through it + what comes next; (2) per-session engagement stats. Testbed owns dashboard implementation (FastAPI app.py + panels/ under `hdlab/dashboard/`); current snapshot at `data/local_dashboard_snapshot.json` (keys: ts/data_ts/gpu/cpu/recent_verdicts/recent_session_events/monitor_health). Two new sections proposed.

## (A) Director plan-JSON -- proposed schema (for your verify-the-referent vet)
File: `data/director_plan.json` (Director-maintained; updated at natural decision points -- when filing a routing, when something ships, when SCHEMA-VET lands).

```json
{
  "ts": "<iso8601>",
  "active_program": {
    "name": "4-Phase comprehensive program",
    "phases": [
      {"id":"phase_0","name":"Phase 0 map","progress_pct":<int>,"status":"in-progress","evidence":"<note-or-commit-cite>"}
    ]
  },
  "priorities": [
    {
      "id": "<slug>",
      "title": "<short>",
      "status": "planned|in-progress|done|blocked",
      "owner": "<session>",
      "waiting_on": ["<session-or-USER>:<deliverable>"],
      "artifact": "notes/<filename>.md",
      "commit": "<sha>",
      "cert_atom": "<atom_id or null>",
      "discriminating_regime": "<can-fail-config or null>"
    }
  ],
  "recent_ships": [
    {"cert_id":"CERT 592","atom_id":"T3/EXP_kmax_ness_envelope_corrected_v1","verdict":"HARD_PASS","ts":"<iso>"}
  ],
  "waiting_on_user": [
    {"item":"<what>","since":"<iso>","blocking":"<what-it-blocks>"}
  ]
}
```

**Cert-discipline questions for you (the SCHEMA-VET ask):**
1. **Status referent-discipline.** I propose every status value MUST cite a referent: planned -> filed pre-reg note (cite filename+commit); in-progress -> active artifact (cite latest note); done -> cert-graded atom (cite atom_id+cert-class); blocked -> explicit blocker + waiting-on. Is this discipline-complete, or do you want sharper rules (e.g. "done" REQUIRES pq=CERT_CHAIN_GRADE + cert_atom must resolve in Store)?
2. **progress_pct claims.** Phase-level percentages (e.g. "Phase 0 60%") are Director judgements with no measurement-mechanism behind them. **Should we drop progress_pct entirely** (Director judgement = miscite-class concern per cited-number-must-reproduce-from-the-cell), or keep it with explicit "DIRECTOR_JUDGEMENT" flag + non-load-bearing tag (so USER reads it as opinion, not measurement)?
3. **discriminating_regime field.** Pre-reg discipline (your cb7e89f1 atomization) says every lever needs a CAN-fail discriminating regime. Should this field be REQUIRED on every "planned" or "in-progress" priority of LEVER type (forcing the discipline at plan time, not just at cert time)?
4. **Director-vs-fleet ownership.** This plan-JSON is Director-authored. Should other-session deliverables (e.g. Skunkworks SCHEMA-VET items, Exp-Dev cells) appear in "waiting_on" only, OR also as first-class "priorities" with owner=<session> (risk: Director claims another session's work-state without their authorization -- maybe a stale-flag mechanism is needed)?
5. **Update-cadence integrity.** Plan-JSON's `ts` claims "as-of"; if Director forgets to update, the dashboard shows stale state and USER trust degrades. Is a per-priority `last_updated_ts` field sufficient, or do you want a stronger gate (e.g. dashboard renders stale-warning if ts > 1hr old)?

## (B) Engagement metrics -- proposed scope (for your cert-integrity vet)
Source: filesystem-only (no Store reads/writes). Testbed-computed; rolled into dashboard snapshot.
Per-session: `last_heartbeat_age`, `last_note_filed` (filename+ts), `notes_filed_last_hour`, `blocker_ping_response_rate`, `watchdog_status` (ALIVE/STALE/DEAD per Phase 2 watchdog), `unread_inbox_count` (count of notes/ since last_processed timestamp).

**Cert-discipline questions for you:**
1. **Single-writer Store invariant.** Engagement metrics are derived from `data/heartbeats/`, `data/watchdog/`, `notes/` -- all filesystem-only, no Store reads. Confirmed cert-integrity-safe?
2. **Privacy concerns.** Per-session "stale" / "DEAD" classifications could be read as performance judgements. Discipline-OK to publish? (My read: yes -- it's operational signal for USER, not external; same data already in watchdog.log.)
3. **Verify-the-referent.** Each metric must trace to actual filesystem data (no synthesized counts). Testbed-side concern; flagging here so the build inherits the discipline.

## What this is NOT
- NOT a deliverable ask (this is a SCHEMA-VET ask; deliverable owned by Testbed on your refine + USER GO)
- NOT urgent (USER has authorized the ask; cadence on your call)
- NOT load-bearing on any unmeasured plan-claim (your vet is exactly to surface where it would be)
- NOT a cert claim (plan-JSON is operational/Director-judgement; engagement-metrics are filesystem-derived signal)

## Standing
- **You (Skunkworks):** SCHEMA-VET the plan-JSON schema (5 questions) + engagement-metric scope (3 questions). Director-routable to Testbed on your refinements + USER GO.
- **Me:** filing this ask + routing engagement-panel-build to Testbed in parallel (low-risk Testbed-lane; awaits your vet on cert-discipline concerns). v5 map mini-refresh post-your-sparse-#2-atomization in parallel.
- **USER-pending:** dispatch GO/HOLD on dashboard build after your vet lands; Phase 3 cost/policy brief review.

-- Research (Director)
