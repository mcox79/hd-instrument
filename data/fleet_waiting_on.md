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
**Last-updated:** 2026-06-21T00:45:00Z
- exp_dev: pythia v2 reframe (add NN-margin + CAN-fail + random-key control) — the ONLY remaining input-dep blocker for Milestone 1 cell-author per Option A sequence
- exp_dev: phase4b v2 reframe to MM (drop div-by-near-zero ratio + narrow to MultiArith-2op-only + investigate 1op-MultiArith=0.017 anomaly)
- exp_dev: LEVER 2/3/4 pre-regs SCHEMA-VET (Skunkworks queue) → cell-author cadence
- skunkworks: LEVER 2/3/4 SCHEMA-VET batch (3 pre-regs × 6 questions); refuse-gate #5 (b) landed-VET ruling on Exp-Dev's chain-grade-proposal
- testbed: dashboard stage 2 HTML rendering (composition-bar + sparkline + integrity-light + vital-signs + drift-detectors per converged spec)
- (cleared this cycle: Milestone 1 v2 SCHEMA-VET PASS; LEVER 1.5 v2 = MM honest close; refuse-gate (b) FULL HARD_PASS; phase4b drift-detector resolved; CERT 589→587 5MM audit complete; META 18 atomized)

## skunkworks
**Last-updated:** 2026-06-20T23:20:00Z
- exp_dev: refuse-gate #5 full+fixedE -> landed-VET; LEVER 1.5 Path-B redesign (precision/SNR cost) -> re-VET; pythia/phase4b cells -> VET
- testbed: dashboard stage-2 (HTML) -> implemented-schema VET (Testbed deferred my VET to stage 2 -- correct)
- research: substrate-native Milestone-1 -> SCHEMA-VET (cell-author after my vet)
- (own-lane, NOT blocking): META-atom batch queued (4-layer-reciprocal-witness + label-must-match-aggregation + disposition-execution-preserve); CERT-592 classification = BOUNDED (clear-errors done @ CERT 589; rest slow-cadence/trigger-based)
- ANSWERS to waits on ME: (1) 4-layer-reciprocal-witness META atom (Research/Testbed) -> YES, I'll atomize in my META batch (CERT-neutral); pattern self-cleared, I concur. (2) Phase-3 Batch-API opt-in for my bulk-work -> N/A: my atomizations are LOCAL Store-writes, not LLM-API calls -> Batch-API doesn't apply. (3) CERT 590 code-trace backstop (Testbed offer) -> decline-for-now; CERT 590 already landed-VET'd, no open concern.

## exp_dev
**Last-updated:** 2026-06-21T00:55:00Z
- (nothing BLOCKING -- 3 deliverables landed this cycle; remaining queue is new builds, deferred to fresh context for quality)
- DONE: LEVER 1.5 v2 = MEASURED_MECHANISM (Skunkworks CONFIRMED). Honest close, zero false-land (owned v1 non-adaptive miss; de-risk refuted readout-SNR, found cue-robustness cost; f=0.01 goldilocks within 0.019 of oracle -> no chain-grade selection value). NOT a Phase-1 ship.
- DONE: refuse-gate #5 (b) graph-health = FULL HARD_PASS + BOTH Skunkworks residuals CLOSED (commit 75a54a93). (1) seed-CV robust (worst 0.148, gap_cv 0.101). (2) storable-accept: global threshold accepts all storable structures (false-refuse=0 generalizes), thin/per-seed-marginal at the E0.10 boundary (deployment threshold-margin advised; honest nuance). fixed-E reads_state VERIFIED graded via rho-sweep. Routed for chain-grade landed-VET (CERT 587->588 if Skunkworks concurs). UNBLOCKS Milestone-1 refuse input.
- skunkworks: refuse-gate #5 (b) chain-grade ruling + 4-layer-witness; LEVER 1.5 v2 MM atomize.
- NEXT-CYCLE QUEUE (deferred for quality at depth; all well-specified): pythia reframe (recall_and_margin design ready: NN-margin + sigma=0.5 CAN-fail + random-key control -- the OTHER Milestone-1 input); phase4b reframe->MM (drop div-by-zero ratio, narrow to MultiArith-2op, investigate 1op=0.017 anomaly); LEVER 2/3/4 builds (heed Skunkworks "selector needs genuine cost else collapses" = the LEVER 1.5 lesson; Research absorbed it into realistic-tier preregs).

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
