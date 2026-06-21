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
**Last-updated:** 2026-06-21T04:1xZ (true date -u UTC)  (**CERT 588 honest** / atoms 177253 / STORAGE-chain VETs all cleared; reactive on landed-VETs)
- (nothing BLOCKING -- reactive-hold on the GPU builds: pythia desat v2 -> flagship -> continual-write, each lands to my VET)
- **3 critical-path SCHEMA-VETs cleared this stretch (storage chain build-cleared):** phase-0 sparse-onset (295882fa) + FLAGSHIP sparse-projected-KV (39cb073c, 4-layer) + continual-write lever (0a01b235, 4-layer) -- all BUILD_GO; bars pre-staged -> fast turnaround. Exp-Dev's whole storage queue is unblocked.
- **Sub-audit batches 1-3 DONE (headline-honesty):** 147 non-PASS chain-grades sampled (MIDDLE_BAND 73 / HARD_FAIL 64 / custom 10) -> **0 demotes; population verified-GENUINE** (deterministic-justified single-seeds + documented honest-negatives + genuine bounds). Symmetric-verify found a buried POSITIVE (2-level-ingest lift) not inflation -> 3 relevance-promotes (count-neutral). Confirms: CERT 588 precise; 147 won't recover cert-count (my phase-plan honest-read holds).
- **D4 cert-integrity self-check live** (fc5ea754, 0 stale/588) + paired discipline (5502fe27). Future enhancement noted: extend D4 to soft-flag non-PASS-vs-non-PASS verdict-label drift (t3_phaseA witness; mostly-legitimate so SOFT).
- exp_dev: pythia desat v2 re-VET (my landed-VET, gates flagship+M1); flagship build (4-layer landed-VET); 2-axis full re-run (atomize-on-VET, smoke-mislabel caught); continual-write build (4-layer).
- research: PHASE PLAN v1 USER-RATIFIED (my STORAGE thread central); next Director ships = cross-domain probe + M2 multi-hop pre-reg (-> my SCHEMA-VET).
- QUEUE STATUS: ALL actionable VETs CLEARED. Reactive on the GPU-build landed-VETs + 2-axis full + continual-write/M2 pre-regs. Sub-audit complete.

## exp_dev
**Last-updated:** 2026-06-21T04:16:37Z (date -u)
- (nothing BLOCKING; NOTHING waiting on me -- all deliverables routed/atomized; cleared per WAITING_ON_CYCLE)
- LANDED+ATOMIZED this cycle: refuse-gate #5b = CERT 588 + LEVER #4 depth-refuse = CERT 589 (2 chain-grade safety certs, 4-layer); 3 MMs atomized (LEVER 1.5 cue-cost, phase4b native-op-depth, LEVER #2 PCA-negative); 2-axis composition MM + safety-vs-utility-gate discipline (atomized off verified 3-seed data); 2 revival-drills resolved. Zero false-land.
- Phase-0 sparse-onset: SMOKE result stands (onset 0.02-0.10 located, 0.002-0.01 >=LB). FULL was a CPU runaway (O(M) python sparse_pat) -> I KILLED + owned it; re-dispatch = vectorize THEN remote-cpu (NOT laptop), low priority. Discipline banked.
- FLAGSHIP sparse-projected-KV: BUILD_GO 4-layer + design-converged + novel-confirmed(x2). OWNED, fully teed-up; de-risk probe written (not run -- no local load post-runaway). Build on pythia land (GPU-free + pythia informs the key regime).
- waiting on: **pythia de-sat GPU re-VET = the single master gate** -> unblocks flagship + Milestone-1 + storage chain. No local CPU load until clear.
- monitor: re-armed twice today (leak-fix killed 4 of my orphans; windowless-fix) -> clean (b0vh3rfol).

## testbed
**Last-updated:** 2026-06-20T23:32:00Z (true `date -u` UTC; prior label "01:18Z" was local-as-Z — Orchestrator caught it)
- (nothing immediate -- Layer-2 raw witness on refuse-gate 5b CLOSED (commit b16a8308); CERT 588 LANDED + Orchestrator Layer-3 reciprocal PASS)
- self: add per-section staleness drift-detector to dashboard (catches stale `## <role>` sections, not just whole-file mtime; USER caught this gap)
- self: refine plan-stall detector to be reframe-aware (currently false-positives on priorities awaiting cell-author start)
- self: standing audit discipline -- proactive Health-tab pulse on every turn + drive resolution on RED, not observe-only
- (closed this cycle: dashboard v2 LIVE; scheduled-task popups silenced; monitor filter tightened; refuse-gate 5b Layer-2 raw witness CONCUR -> CERT 588 landed)

## orchestrator
**Last-updated:** 2026-06-21T04:30:42Z (true date -u UTC)
- marsh@home GPU: pythia_kv_desat_v2 = VERIFIED HEALTHY+PROGRESSING (resume picked up 12:20AM, log skipped all 28 ckpts, now on size100k s31+s41+aggregation; proc 32488/37528 alive) -> ETA ~60-75min -> on completion I scp metrics local + flag Skunkworks de-saturated VET -> I reciprocal-check if it atomizes
- NOTED (not blocking): separate heavy remote run exp_substrate_bge_index_refresh_full_corpus_v1 (proc 34036, 8.6 CPU-hrs, NOT mine) on marsh@home; GPU 0% util so no compute contention, but VRAM 89% (7288/8188MiB) = memory-pressure risk for 100k seeds -> watching for OOM
- exp_dev: LEVER 2/3/4 + Milestone-1 + 2-axis-compose-refuse cells -> I dispatch (CPU local / GPU remote) when authored, code-trace re-verify
- skunkworks: future trigger-based count-moves -> I reciprocal-check SILENTLY (P4: verify count, note ONLY on FAIL)
- testbed: dashboard stage 2 -> I verify plan-panel Store-read; windowless-monitor re-arm DONE my side
- CLEARED this session: laptop HEAT (runaway sparse-onset killed by exp_dev + monitor process/console leak fixed via re-arm, bash 70->46); CERT 591 relabel + 5MM demotes (592->587) + refuse-gate 5b (588) + LEVER 4 (589) + phase4b demote (588) + META batch -- ALL reciprocal-dual-verified

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
