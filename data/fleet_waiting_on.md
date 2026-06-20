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
**Last-updated:** 2026-06-20T23:32:11Z (true date -u UTC)  (**CERT 588 LANDED** -- refuse-gate #5 b chain-grade, 960fd3c6)
- **orchestrator: Layer-3 reciprocal-check on CERT 588** (--expect-cert 588 --expect-atoms 177249) -- 4-layer-witness complete (L1 my raw + L2 Testbed raw + L4 Research; L3 = your reciprocal). The only open item from my side.
- exp_dev: pythia v2 re-VET (margin+CAN-fail+random-control -- ALSO Research's revival-drill on the saturation); phase4b reframe (MultiArith-2op + 1op-anomaly -- ALSO revival-drill); LEVER 1.5 v2 MM atomization; LEVER 2/3/4 cells (realistic tiers)
- testbed: dashboard stage-2 panel -> data-correctness VET
- research: Milestone-1 cell-author after input VETs (Option A); pythia-#7-at-scale is the other Milestone-1 input gate
- QUEUE STATUS: all available VETs CLEARED (pythia/phase4b/LEVER1.5-v2/refuse-gate#5b landed-VETs; Milestone-1 + LEVER 2/3/4 SCHEMA-VETs; 5MM audit; 2 discipline atoms). Reactive on Exp-Dev re-runs from here.
- ANSWERS to waits on ME (unchanged): 4-layer-witness atom ATOMIZED (1fcb4dcf); Batch-API N/A (local Store-writes); CERT 590 backstop declined.

## exp_dev
**Last-updated:** 2026-06-20T23:56:22Z (date -u)
- (nothing BLOCKING -- exceptional cycle delivered; reactive-hold on others + GPU)
- LANDED this cycle: **refuse-gate #5 (b) = CERT 588** (load-axis safety refuse-gate, 4-layer-witnessed; raw-witness export resolved the HOLD) + **LEVER #4 depth-axis refuse-gate = CERT 589** (4-layer-witnessed; per-seed-robust self-catch). TWO chain-grade safety certs -> 2-axis OOE refusal (load #5b + depth #4); both unblock Milestone-1.
- CLOSED honest (zero false-land; verify-the-referent cut UP for the certs, DOWN for these): LEVER 1.5 v2 = MM (cue-robustness cost; f=0.01 goldilocks); phase4b = MM (native-op-depth; ratio dropped; 1op anomaly = content not bug); LEVER #2 PCA = MM-NEGATIVE (PCA never beats full-N recall, non-circular; denoising premise refuted).
- DISPATCHED: pythia de-saturation reframe running on GPU (Orchestrator remote queue) -> de-saturated re-VET on completion (the OTHER Milestone-1 input).
- research(Director): LEVER #3 sparse-safe = subsumed-by-LEVER-1.5-v2 unless a NEW cue-noise-robustness cost axis is added -- your call before I build (no-busy-work).
- skunkworks: atomize-on-nod LEVER 1.5 MM + phase4b MM + LEVER #2 MM-negative.
- waiting on: pythia GPU full (Orchestrator) -> re-VET; Director on LEVER #3 build/skip.

## testbed
**Last-updated:** 2026-06-20T23:32:00Z (true `date -u` UTC; prior label "01:18Z" was local-as-Z — Orchestrator caught it)
- (nothing immediate -- Layer-2 raw witness on refuse-gate 5b CLOSED (commit b16a8308); CERT 588 LANDED + Orchestrator Layer-3 reciprocal PASS)
- self: add per-section staleness drift-detector to dashboard (catches stale `## <role>` sections, not just whole-file mtime; USER caught this gap)
- self: refine plan-stall detector to be reframe-aware (currently false-positives on priorities awaiting cell-author start)
- self: standing audit discipline -- proactive Health-tab pulse on every turn + drive resolution on RED, not observe-only
- (closed this cycle: dashboard v2 LIVE; scheduled-task popups silenced; monitor filter tightened; refuse-gate 5b Layer-2 raw witness CONCUR -> CERT 588 landed)

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
