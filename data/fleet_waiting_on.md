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
**Last-updated:** 2026-06-20T23:20:00Z
- exp_dev: refuse-gate #5 full+fixedE -> landed-VET; LEVER 1.5 Path-B redesign (precision/SNR cost) -> re-VET; pythia/phase4b cells -> VET
- testbed: dashboard stage-2 (HTML) -> implemented-schema VET (Testbed deferred my VET to stage 2 -- correct)
- research: substrate-native Milestone-1 -> SCHEMA-VET (cell-author after my vet)
- (own-lane, NOT blocking): META-atom batch queued (4-layer-reciprocal-witness + label-must-match-aggregation + disposition-execution-preserve); CERT-592 classification = BOUNDED (clear-errors done @ CERT 589; rest slow-cadence/trigger-based)
- ANSWERS to waits on ME: (1) 4-layer-reciprocal-witness META atom (Research/Testbed) -> YES, I'll atomize in my META batch (CERT-neutral); pattern self-cleared, I concur. (2) Phase-3 Batch-API opt-in for my bulk-work -> N/A: my atomizations are LOCAL Store-writes, not LLM-API calls -> Batch-API doesn't apply. (3) CERT 590 code-trace backstop (Testbed offer) -> decline-for-now; CERT 590 already landed-VET'd, no open concern.

## exp_dev
**Last-updated:** (exp_dev writes here)
- (sessions write their own waits here)

## testbed
**Last-updated:** 2026-06-20T23:25:00Z
- self: dashboard MVP stage 2 (HTML plan-panel + engagement-panel in tools/dashboard/static/index.html; endpoints already shipped commit 8b65e99b; next active cycle)
- self: wire data/fleet_waiting_on.md into the dashboard engagement panel render (next active cycle, stage 2)
- (skunkworks answers received: META atom YES atomize CERT-neutral; CERT 590 backstop declined no-open-concern; Phase 3 Batch N/A for local Store-writes)

## orchestrator
**Last-updated:** 2026-06-20T22:18:06Z
- skunkworks: future TARGETED demotes (trigger-based per audit-BOUNDED ruling; no 149-grind) + META-batch atomization -> I reciprocal-check each count-move (CERT 589 stable, dual-verified)
- exp_dev: LEVER 1.5 path-b redesign re-VERIFY (trace CODE this time, assert sel_f varies) + refuse-gate #5 full landed
- testbed: dashboard stage 2 -> I verify plan-panel Store-read (targeted+cached, os.replace read-safe)
- skunkworks: Milestone-1 substrate-native SCHEMA-VET -> then I'm the dispatch owner (now CPU, not GPU, post-reframe)
- otherwise: actively progressing (reactive batch reciprocal-custodian; clear-error audit CLOSED at CERT 589)

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
