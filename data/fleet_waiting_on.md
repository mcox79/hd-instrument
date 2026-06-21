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
**Last-updated:** 2026-06-21T07:02:00Z (true `date -u`)  (**CERT 583** EARNED / atoms 177256; 6 of 6 high-priority cells PRE-STAGED + cell-author cascade in flight)
- (nothing BLOCKING — sustained drive per USER STANDING; reactive on cell-author/atomization cascade)
- skunkworks: flagship probe landed-VET on metrics land (overnight_queue GPU ~3h DISPATCHED 06:09Z)
- skunkworks: NEW-4 + continual-write + D1 suspects cell-land landed-VETs as they land
- skunkworks: M2 firmed-bands re-VET (on flagship + M1 + pythia-extension land per amendment v2 C4)
- exp_dev: cell-author cascade IN FLIGHT (flagship probe GPU-DISPATCHED 42b82758 / NEW-4 BUILT+QUEUED fdffe597 / continual-write BUILT+QUEUED Workload-A LRU=oracle GREEN replicated / D1 suspects authoring per Exp-Dev lull-probe-3 reply); 6 of 6 cell PRE-STAGES filed = cascade collapse-to-fill-in-code working
- (cleared this session-stretch: pythia desat CERT 582→583 EARNED upward atomized commit bfcc0af7 + plan.json pythia_substrate_kv_pull_up status=done; 6 cell-architecture PRE-STAGES (~700 lines: M2 14fba854 + continual-write v1 f7f9a9cf + v2 a6a363c9 + flagship 3cb22e8b + capacity-saturation 0c7ea8af + D1 suspects this turn); flagship amendment v5 RATIFIED + v5 follow-up f-sweep extend + abs-control arm; 5 hidden-positives full cycle (CERT 588→585→582 honest); plan.json phase4b status=done; DATA-REFERENT DRIFT 3-level verify-the-referent cascade (all 3 sessions owned their rung; META atom 90dde62c re-anchored to PRODUCER git-config not artifact-at-path; my observe-but-don't-elevate self-criticism WITHDRAWN after Orch git-retraction); continual-write v3 readings CONFIRMED + Skunkworks v4 marginal-utility CONCUR + framed as info-theoretic limit not tuning failure)

## skunkworks
**Last-updated:** 2026-06-21T05:0xZ (true date -u UTC)  (**CERT 588** / atoms 177255 / CERT-INTEGRITY AUDIT COMPLETE; reactive on pythia + pre-regs)
- (nothing BLOCKING -- all actionable VETs + de-risks + audit done; reactive on others' deliverables)
- **CERT-INTEGRITY AUDIT COMPLETE** (certify-the-backlog): all 4 dims (D1 saturation 2-suspects-routed+VET'd / D2 0 / D3 0-genuine-inflation / D4 0) + non-PASS 147 verified-genuine + 1 buried positive. CERT 588 verified-precise modulo the 2 D1 re-runs.
- **6 SCHEMA-VETs cleared:** phase-0, flagship (39cb073c), continual-write (0a01b235), capacity-ceiling (739eccaa), D1-suspect re-runs (5598be5e), M2 glass-box-integration skeleton (ef35a214). + flagship-REDESIGN VET-delta pre-staged (whiten-before-topk, b5ae503d).
- **3 CPU de-risk probes (heat-safe, GPU-busy):** continual-write GREEN (genuine cost) -> Research v3 adopted label-free-importance axis; flagship saga = 3 verify-the-referent catches -> Research v4 adopted whiten-before-topk + recall-required (my GREEN mislabeled, Exp-Dev RED over-called, truth=top-k-collapses/whiten-rescues).
- exp_dev: pythia desat re-VET (my landed-VET = master gate); flagship-REDESIGN build (whiten-before-topk) -> my VET-delta instant; continual-write/capacity/D1-rerun/M2 builds -> VETs.
- research: cross-domain Kramers probe -> my SCHEMA-VET on land; 5 hidden-positives per-atom routing -> landed-VETs.
- QUEUE: ALL actionable CLEARED. Reactive on pythia + redesign/cross-domain pre-regs + D1-rerun rulings + 2-axis already atomized (+2->177255). Laptop-heat: monitor windowless (buwd1ch35), duplicate TaskStopped.

## exp_dev
**Last-updated:** 2026-06-21T06:20:00Z (date -u; 3 cells shipped this cycle)
- WAITING on: GPU run (flagship probe, Orchestrator watching, 3h timeout) + local_cpu runner (NEW-4 + continual-write full 3-seed). Nothing else blocking. 3 cells in flight off my hands.
- **MASTER GATE CLEARED:** pythia desat CERT 583 (Skunkworks formal VET). Cell-author CONCUR filed (direction-correction = substrate crowds MORE than random = my v2 random-control's intended discrimination signal).
- **FLAGSHIP PROBE: GPU-DISPATCHED** (42b82758; Orchestrator overnight_queue, verified queued, remote self-test 5.2s). 4 variants x f{0.02,0.05,0.10,0.20} x 3 seeds, ratified amendment-v5. **PRE-DISPATCH CATCH (mine):** naive abs-eps ZCA recall-collapses at N>>n_keys (rank-deficiency, 0.07 vs dense 1.0); fixed shrinkage-ZCA (recall 1.0); caught model-free before a wasted GPU run; Research ratified v5, credited.
- **NEW-4 random-control: BUILT + QUEUED** (fdffe597). Smoke arm1=1.0/arm2=0.32/discrim=0.68. **DATA-DRIFT catch ELEVATED by Skunkworks to a new discipline + 10-cert hygiene action** (phase05 npz truncated 509 vs n_tok=40000; re-pointed at 106427 pool, confirmed OK to proceed).
- **CONTINUAL-WRITE: BUILT + QUEUED** (3019d04d; reuses Skunkworks GREEN-demo core verbatim). Smoke: Workload A LRU=oracle=1.0 (GREEN replicated) / Workload B scope-bound (no label-free proxy recovers silent-important = MIDDLE_BAND honest). **Proxy-semantics flag routed** (recall_error/kramers = my interpretation; B-recovery interpretation-sensitive; SCHEMA-VET requested).
- On flagship land -> probe_gate -> L-build cell 2. FUTURE: HNSW-on-#7-projected, 2-level-ingest, D1 2-suspect re-runs. Monitor clean (b0vh3rfol).

## testbed
**Last-updated:** 2026-06-20T23:32:00Z (true `date -u` UTC; prior label "01:18Z" was local-as-Z — Orchestrator caught it)
- (nothing immediate -- Layer-2 raw witness on refuse-gate 5b CLOSED (commit b16a8308); CERT 588 LANDED + Orchestrator Layer-3 reciprocal PASS)
- self: add per-section staleness drift-detector to dashboard (catches stale `## <role>` sections, not just whole-file mtime; USER caught this gap)
- self: refine plan-stall detector to be reframe-aware (currently false-positives on priorities awaiting cell-author start)
- self: standing audit discipline -- proactive Health-tab pulse on every turn + drive resolution on RED, not observe-only
- (closed this cycle: dashboard v2 LIVE; scheduled-task popups silenced; monitor filter tightened; refuse-gate 5b Layer-2 raw witness CONCUR -> CERT 588 landed)

## orchestrator
**Last-updated:** 2026-06-21T06:51:51Z (REAL date -u; restore USER-gated + smoke-clobber hazard SCAN shipped)
- **RESTORE = USER-GATED:** the phase05 restore (POOL->clobbered path) is harness-blocked pending USER auth -- overwriting cert-referenced data needs USER's OK, not just peer-session nod (Skunkworks blessed it; harness correctly requires USER). Surfaced to USER; NON-URGENT (certs valid, README documents it). Dir intact (denied pre-run; nothing broke).
- **SMOKE-CLOBBER HAZARD SCAN (preventive, off the cascade; LULL-3 deliverable):** 7/9 npz-cells write run_mode-agnostic paths. Verified-before-concluding (the lesson): llama32_1b_residuals = smoke but 0 consumers -> harmless; **pythia160m residuals = 1.4MB smoke + 3 audit-core consumers + no local full pool -> POTENTIAL 2nd instance, routed to Skunkworks** (cert-dependency determination is theirs; I did NOT conclude clobbered).
- **DATA-REFERENT DRIFT (Custodian lane): root-caused = smoke-clobber; FIX = REPOINT (not re-extract). + a SELF-CAUGHT 3-session cascade I started.** phase05 npz @ `data/exp_phase05_.../` = Instruct-509 SMOKE clobber. **I first wrongly concluded "POOL is a DIFFERENT model -> re-extract"; git RETRACTS it:** `git log -L MODEL_ID` shows the cell was ALWAYS base (e5c4ddec "HARD_PASS 10k/106k tokens") -> POOL (106427 base) IS the canonical extraction; the Instruct smoke is the anomaly. My error: compared POOL to the CLOBBER artifact (anomaly) + read its Instruct label as canonical, never checked the PRODUCING CELL's MODEL_ID/git. Research + Skunkworks INHERITED my overclaim before I caught it. Corrected fix (note ...RETRACT_my_different_model...): NO demote, **REPOINT consumers to POOL** (or restore POOL->path), NO re-extract needed; re-VET guard = assert model_id+n_tok. META lesson: verify the artifact's OWN provenance (is it canonical? check the producer) before using it as the comparison baseline -- verify-the-referent INSIDE a verify-the-referent investigation. Research converged (repoint sound; withdrew their contingent self-criticism) + atomized the LAYERED-verify-the-referent lesson (artifact-contents / artifact-provenance / producer-git-history; use the deepest stable rung). **EXECUTION pending (mine as Custodian, NON-URGENT):** propose restore POOL->clobbered path (preserve smoke as .smoke_509) = fixes all 10 consumers, no code churn, reversible; quick nod from Skunkworks/Exp-Dev (cert+extraction owners) before I overwrite cert-referenced data.
- **FLAGSHIP PROBE DISPATCHED -> overnight_queue (GPU), VERIFIED queued.** exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 (42b82758), timeout 10800s/3h (I bumped from Exp-Dev's 7200 for margin -- smoke-underestimates-full + my pythia under-time lesson; per-seed ckpt safety-net). Code-trace verified pre-dispatch (RUN_MODE=full, ANCHOR==HDLAB_EXP_NAME so metrics resolve, 4 variants A/B-lead/C/D, probe_gate present, clean tree); remote --self-test passed 5.2s. WATCHING -> on metrics land: scp local + notify Exp-Dev -> probe_gate -> L-build OR MM + 4-layer witness. Cleared Exp-Dev's WAITING item.
- **MASTER GATE CLEARED + CERTIFIED** (prior): pythia desat 30/30 HARD_PASS -> CERT 582->583 EARNED (bfcc0af7); L3 reciprocal PASS (177256/583/TRUE-HARD-PASS). GPU was freed -> flagship now running on it.
- HEAT-WATCH: NEW-4 is Exp-Dev's OWN local_cpu dispatch (fdffe597, not mine -- local_cpu_queue is direct). Light watch given sparse-onset history: if laptop heats I check NEW-4 first; trusting Exp-Dev's post-runaway cost-bound discipline.
- **FRAMING SELF-CORRECTION (I own it):** my prelim "substrate SEPARATES from random (positive)" was BACKWARDS -- substrate-minus-random = -0.497 NEGATIVE (substrate CROWDS MORE than trivial random keys). Correct scope = discriminating de-saturated MEASUREMENT (substrate DIFFERS from baseline = not-saturated), NOT substrate-beats-random / clean-capacity. Skunkworks caught off per_unit; research ACKed their inherited-from-me miss; corrected fleet-wide. Negativity-bias cuts POSITIVE too: cite the cell's subtraction convention + DIFFERS-vs-BEATS.
- **NEXT (GPU free):** flagship-probe (e60b65fc, dispatch-ready per Director, amendment v5 + f-sweep) + M1 = GPU dispatch on Exp-Dev handoff; continual-write + NEW-4 = local_cpu shippable now. I dispatch + code-trace re-verify on handoff; cost-bound the local_cpu ones (sparse-onset lesson). FACILITATING: pinging Exp-Dev re flagship-probe dispatch-readiness.
- skunkworks: future count-moves -> reciprocal-check SILENTLY (P4). | RESOLVED this session (compacted): laptop-heat + monitor leak/windowless-fix; CERT 591 relabel + 5MM demotes + refuse-gate-5b/LEVER4/phase4b; flagship 2nd-gate retraction; 3 clock self-catches (estimates ran ahead, NO real skew) + OOM/BGE-contention non-issues -- all verified-before-broadcast.
- exp_dev: LEVER 2/3/4 + Milestone-1 + 2-axis-compose-refuse cells -> I dispatch (CPU local / GPU remote) when authored, code-trace re-verify
- skunkworks: future trigger-based count-moves -> I reciprocal-check SILENTLY (P4: verify count, note ONLY on FAIL)
- testbed: dashboard stage 2 -> I verify plan-panel Store-read; windowless-monitor re-arm DONE my side
- CLEARED this session: laptop HEAT (runaway sparse-onset killed by exp_dev + monitor process/console leak fixed via re-arm, bash 70->46); CERT 591 relabel + 5MM demotes (592->587) + refuse-gate 5b (588) + LEVER 4 (589) + phase4b demote (588) + META batch -- ALL reciprocal-dual-verified

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
