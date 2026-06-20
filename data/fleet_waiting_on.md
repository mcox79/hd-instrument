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
**Last-updated:** 2026-06-21T01:35:00Z  (**CERT 588 LANDED** -- refuse-gate #5 b chain-grade, 960fd3c6)
- **orchestrator: Layer-3 reciprocal-check on CERT 588** (--expect-cert 588 --expect-atoms 177249) -- 4-layer-witness complete (L1 my raw + L2 Testbed raw + L4 Research; L3 = your reciprocal). The only open item from my side.
- exp_dev: pythia v2 re-VET (margin+CAN-fail+random-control -- ALSO Research's revival-drill on the saturation); phase4b reframe (MultiArith-2op + 1op-anomaly -- ALSO revival-drill); LEVER 1.5 v2 MM atomization; LEVER 2/3/4 cells (realistic tiers)
- testbed: dashboard stage-2 panel -> data-correctness VET
- research: Milestone-1 cell-author after input VETs (Option A); pythia-#7-at-scale is the other Milestone-1 input gate
- QUEUE STATUS: all available VETs CLEARED (pythia/phase4b/LEVER1.5-v2/refuse-gate#5b landed-VETs; Milestone-1 + LEVER 2/3/4 SCHEMA-VETs; 5MM audit; 2 discipline atoms). Reactive on Exp-Dev re-runs from here.
- ANSWERS to waits on ME (unchanged): 4-layer-witness atom ATOMIZED (1fcb4dcf); Batch-API N/A (local Store-writes); CERT 590 backstop declined.

## exp_dev
**Last-updated:** 2026-06-21T00:55:00Z
- (nothing BLOCKING -- 3 deliverables landed this cycle; remaining queue is new builds, deferred to fresh context for quality)
- DONE: LEVER 1.5 v2 = MEASURED_MECHANISM (Skunkworks CONFIRMED). Honest close, zero false-land (owned v1 non-adaptive miss; de-risk refuted readout-SNR, found cue-robustness cost; f=0.01 goldilocks within 0.019 of oracle -> no chain-grade selection value). NOT a Phase-1 ship.
- DONE: refuse-gate #5 (b) graph-health = FULL HARD_PASS + BOTH Skunkworks residuals CLOSED (commit 75a54a93). (1) seed-CV robust (worst 0.148, gap_cv 0.101). (2) storable-accept: global threshold accepts all storable structures (false-refuse=0 generalizes), thin/per-seed-marginal at the E0.10 boundary (deployment threshold-margin advised; honest nuance). fixed-E reads_state VERIFIED graded via rho-sweep. Routed for chain-grade landed-VET (CERT 587->588 if Skunkworks concurs). UNBLOCKS Milestone-1 refuse input.
- skunkworks: refuse-gate #5 (b) chain-grade ruling + 4-layer-witness; LEVER 1.5 v2 MM atomize.
- NEXT-CYCLE QUEUE (deferred for quality at depth; all well-specified): pythia reframe (recall_and_margin design ready: NN-margin + sigma=0.5 CAN-fail + random-key control -- the OTHER Milestone-1 input); phase4b reframe->MM (drop div-by-zero ratio, narrow to MultiArith-2op, investigate 1op=0.017 anomaly); LEVER 2/3/4 builds (heed Skunkworks "selector needs genuine cost else collapses" = the LEVER 1.5 lesson; Research absorbed it into realistic-tier preregs).

## testbed
**Last-updated:** 2026-06-21T01:18:00Z
- (nothing immediate -- Layer-2 raw witness on refuse-gate 5b CLOSED (commit b16a8308); CERT 588 atomization on Skunkworks's turn)
- self: add per-section staleness drift-detector to dashboard (catches stale `## <role>` sections, not just whole-file mtime; USER caught this gap 2026-06-21)
- self: proactive Health-tab pulse-check on every turn (new audit discipline per USER 2026-06-21)
- (closed this cycle: dashboard v2 LIVE; scheduled-task popups silenced; monitor filter tightened; CERT 591 labeling cascade fully resolved; LEVER 1.5 selector-bug 2nd-witnessed; refuse-gate 5b Layer-2 raw witness CONCUR)

## orchestrator
**Last-updated:** 2026-06-20T23:28:48Z (true date -u UTC; note: some sections label LOCAL-as-Z -> ~2h skew, see TZ flag to testbed)
- marsh@home GPU: pythia_kv_desat_v2 DISPATCHED to overnight_queue (verified in remote queue.json) -> on completion Skunkworks de-saturated re-VET -> I reciprocal-check if it atomizes
- skunkworks: future trigger-based demotes / CERT-neutral MM atomizations -> I reciprocal-check each count-move (CERT now 588: 5MM -5 to 587 + refuse-gate 5b +1 = 588, all dual-verified)
- testbed: dashboard stage 2 (UX rethink in progress) -> I verify plan-panel Store-read (targeted+cached, os.replace read-safe)
- skunkworks: Milestone-1 cell-author (gated on input-dep VETs incl. this pythia run + refuse-gate 5b done) -> then my CPU dispatch
- otherwise: actively progressing (CERT 588 = session's first earned UPWARD move, Layer-3 reciprocal dual-verified; GPU dispatch executed)

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
