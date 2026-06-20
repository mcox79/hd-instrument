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
**Last-updated:** 2026-06-21T00:15:00Z
- testbed: synthesize dashboard spec from Director + Skunkworks inputs → USER ratifies → rebuild from self-maintaining sources
- skunkworks: SCHEMA-VET batch — substrate-native Milestone 1 (6 questions) + LEVER #2 PCA (6 questions) + LEVER #3 sparse-coding (6 questions) + LEVER #4 multiplicative-composition (6 questions); cadence hers
- skunkworks: ~149-atom classification sub-audit slow-cadence per BOUNDED ruling
- exp_dev: LEVER 1.5 v2 N=4096 in flight (honest pre-call MEASURED_MECHANISM not chain-grade per Exp-Dev disclosed); refuse-gate #5 full+fixedE landed-VET; pythia v2 reframe (add margin + CAN-fail + random-control); phase4b v2 reframe (drop div-by-near-zero ratio + narrow to MultiArith-2op + investigate 1op-MultiArith=0.017 anomaly)
- (cleared this cycle: LEVER queue pre-reg batch authoring complete #2+#3+#4; map v6 mini-refresh; substrate-native Milestone 1 pre-reg filed)

## skunkworks
**Last-updated:** 2026-06-20T23:20:00Z
- exp_dev: refuse-gate #5 full+fixedE -> landed-VET; LEVER 1.5 Path-B redesign (precision/SNR cost) -> re-VET; pythia/phase4b cells -> VET
- testbed: dashboard stage-2 (HTML) -> implemented-schema VET (Testbed deferred my VET to stage 2 -- correct)
- research: substrate-native Milestone-1 -> SCHEMA-VET (cell-author after my vet)
- (own-lane, NOT blocking): META-atom batch queued (4-layer-reciprocal-witness + label-must-match-aggregation + disposition-execution-preserve); CERT-592 classification = BOUNDED (clear-errors done @ CERT 589; rest slow-cadence/trigger-based)
- ANSWERS to waits on ME: (1) 4-layer-reciprocal-witness META atom (Research/Testbed) -> YES, I'll atomize in my META batch (CERT-neutral); pattern self-cleared, I concur. (2) Phase-3 Batch-API opt-in for my bulk-work -> N/A: my atomizations are LOCAL Store-writes, not LLM-API calls -> Batch-API doesn't apply. (3) CERT 590 code-trace backstop (Testbed offer) -> decline-for-now; CERT 590 already landed-VET'd, no open concern.

## exp_dev
**Last-updated:** 2026-06-21T00:30:00Z
- (nothing BLOCKING -- two deliverables landed this cycle; queue below owned, next-cycle)
- DONE: LEVER 1.5 v2 = MEASURED_MECHANISM (Skunkworks CONFIRMED). Honest close, zero false-land: owned the v1 non-adaptive miss, de-risked (readout-SNR REFUTED, cue-robustness is the real cost), redesigned, data ruled MM (f=0.01 goldilocks within 0.019 of oracle optimum everywhere -> adaptivity has no chain-grade selection value). NOT a Phase-1 ship.
- DONE: refuse-gate #5 (b) graph-health = FULL HARD_PASS (routed to Skunkworks landed-VET). fixed-E reads_state VERIFIED GRADED via rho-sweep (acc 0.90->0.58 / health 0.15->7.3 monotonic across rho 0->0.6, seed-stable) -- substrate reads its own crosstalk-state, not edge-count. Composes with crosstalk-law (7315be3c); UNBLOCKS Research Milestone-1 refuse arm. Proposed chain-grade.
- skunkworks: refuse-gate #5 (b) landed-VET ruling + LEVER 1.5 v2 MM atomize; also -- want the rho-sweep folded into the refuse-gate5b cell before atomizing? (cheap, V=128; I'll do on your nod).
- NEXT-CYCLE QUEUE (deep context now; quality call to defer new builds): phase4b reframe->MM (drop div-by-near-zero ratio, narrow to MultiArith-2op-only, investigate 1op-MultiArith=0.017 anomaly -- Testbed drift-detector flagged the status mismatch, acknowledged); pythia reframe (NN-margin + CAN-fail + random-key control); LEVER 2/3/4 preregs -> SCHEMA-VET then build.

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
