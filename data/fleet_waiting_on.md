# Fleet waiting-on (USER-directed shared blocker registry; 2026-06-20)

**Purpose:** single shared place where each session lists what they're waiting on. Replaces the "Waiting on: X / Y / Z" boilerplate at the end of every note. Reduces cross-fleet ACK overhead.

**Discipline:**
- Each session writes ONLY to their own `## <session>` section. Do NOT edit other sessions' sections.
- Update at decision points (when a wait starts or clears), not 60s-cadence.
- Format: one line per wait — `- <who-you're-waiting-on>: <deliverable>` (commit/note ref optional)
- Update `last_updated_ts` when you edit your section.
- This file is git-tracked; commit at each substantive update; path-scoped commit (`git commit -- data/fleet_waiting_on.md`).
- When NOTHING is blocking you, write `- (nothing — actively progressing)` and move on.

**Composes with:** `data/director_plan.json` (Director-maintained at decision points); dashboard engagement panel (Testbed's `/api/fleet_engagement` endpoint may render); `data/heartbeats/<role>.timestamp` (Phase 2 watchdog mechanical liveness).

**NOT a replacement for:** routing notes (`<from>_to_<to>_<topic>.md` files still ferry actual requests + deliverables); ACK notes when a real Director-stance change is being communicated (silent-adopt vs visible-stance is judgement-per-event).

---

## research
**Last-updated:** 2026-06-20T22:55:00Z
- skunkworks: META atom candidate SCHEMA-VET (4-layer reciprocal-witness pattern; commit d721aa8d)
- skunkworks: 152-atom classification sub-audit continuing (post-CERT 589; multi-cycle)
- exp_dev: LEVER 1.5 (a) reframe-as-MM / (b) redesign-with-precision-SNR-cost pick (commit 3be4a3db; Director cost-dim input filed)
- exp_dev: refuse-gate #5 full+fixedE landed-VET pending
- testbed: dashboard stage 2 (HTML rendering in index.html; endpoints already landed)
- skunkworks: Phase 3 Batch API engineering opt-in for Skunkworks's bulk-work (USER-authorized A+B)
- user: Substrate-native Milestone 1 SCHEMA-VET-then-cell-author cadence (USER ratified framing; cell-author after Skunkworks vet)

## skunkworks
**Last-updated:** (skunkworks writes here)
- (sessions write their own waits here)

## exp_dev
**Last-updated:** (exp_dev writes here)
- (sessions write their own waits here)

## testbed
**Last-updated:** 2026-06-20T23:05:00Z
- skunkworks: 4-layer-reciprocal-witness META atom SCHEMA-VET (Research-proposed; would atomize the discipline pattern)
- skunkworks: optional CERT 590 code-trace backstop go/no-go (offered earlier; their call whether to take it)
- self: dashboard MVP stage 2 (HTML plan-panel + engagement-panel in tools/dashboard/static/index.html; endpoints already shipped commit 8b65e99b; next active cycle)
- self: wire data/fleet_waiting_on.md into the dashboard engagement panel render (next active cycle, stage 2)

## orchestrator
**Last-updated:** (orchestrator writes here)
- (sessions write their own waits here)

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
