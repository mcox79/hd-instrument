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
**Last-updated:** 2026-06-21T05:48:00Z (true `date -u`)  (**CERT 582** / atoms 177255; 3 cell-architecture PRE-STAGES filed)
- (nothing BLOCKING — Director-lane drove all night per USER STANDING; reactive on others' deliverables)
- orchestrator: pythia desat GPU full-run land (~05:35-40Z ETA Skunkworks landed-VET → unblocks Milestone 1 + flagship)
- exp_dev: flagship cell-author build (whiten-before-topk per amendment v4 + cell architecture PRE-STAGE v1 filed = mechanical fill-in-code lift on pythia de-gate)
- exp_dev: continual-write cell-author build (label-free importance-inference + Kramers-escape per amendment v3 + cell architecture PRE-STAGE v1 filed; **local_cpu NOT pythia-gated** so can ship NOW if Exp-Dev has bandwidth between flagship-cell-author and pythia-await)
- exp_dev: NEW-4 random-control can-fail re-run (pre-reg + Skunkworks BUILD_GO + matched-budget clarification absorbed)
- exp_dev: D1 2 suspects can-fail re-runs (planted_csp_viability + pp49_hrc per Skunkworks BUILD-GO)
- skunkworks: M2 firmed-bands re-VET (on flagship + M1 + pythia land per C4)
- skunkworks: NEW-4 cell-land landed-VET (when Exp-Dev runs)
- (cleared this stretch: M2 skeleton SCHEMA-VET PASS amendment v2 absorbing C1-C4 → cell architecture PRE-STAGE v1 (commit 14fba854); 5 hidden-positives explicit per-atom routing → 3 wrong-bar demoted + NEW-2 self-reconciled → CERT 588→585→582 net -6 honest both directions; NEW-4 concrete pre-reg + BUILD_GO + matched-budget clarification; continual-write cell architecture PRE-STAGE v1 (commit f7f9a9cf); flagship whiten-before-topk cell architecture PRE-STAGE v1 (commit 3cb22e8b); own-miscite logged cb7e89f1; ~400 lines actionable architecture across 3 pre-stages turns design-from-prereg into fill-in-code per USER drive-all-night facilitation)

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
**Last-updated:** 2026-06-21T04:36:49Z (date -u; round-2)
- (nothing BLOCKING; NOTHING waiting on me -- all routed/atomized; flagship 2nd-gate RETRACTED, single pythia gate)
- LANDED+ATOMIZED this cycle: refuse-gate #5b = CERT 588 + LEVER #4 depth-refuse = CERT 589 (2 chain-grade safety certs, 4-layer); 3 MMs atomized (LEVER 1.5 cue-cost, phase4b native-op-depth, LEVER #2 PCA-negative); 2-axis composition MM + safety-vs-utility-gate discipline (atomized off verified 3-seed data); 2 revival-drills resolved. Zero false-land.
- Phase-0 sparse-onset: SMOKE result stands (onset 0.02-0.10 located, 0.002-0.01 >=LB). FULL was a CPU runaway (O(M) python sparse_pat) -> I KILLED + owned it; re-dispatch = vectorize THEN remote-cpu (NOT laptop), low priority. Discipline banked.
- FLAGSHIP sparse-projected-KV: BUILD_GO + design-converged + novel-confirmed(x2). De-risk probe RAN (smoke) -> I OVER-CALLED a red-flag, then CAUGHT the confound (smoke projection dense-recall 0.10 << CERT591's 0.83 -> too weak to decide) -> corrected -> 2nd-gate retracted. Learnings folded into the build: (1) de-risk valid only at FULL-SCALE; (2) use a NON-top-k sparse-encode (top-k collapses projected keys). GENUINELY GPU-gated (full-scale projection). Build on pythia land.
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
**Last-updated:** 2026-06-21T04:58:22Z (REAL date -u; gate on FINAL seed)
- marsh@home GPU: pythia_kv_desat_v2 = **29/30, on the FINAL seed.** s31 just checkpointed (anchored to REMOTE clock: remote-now 00:57 -04:00 = 04:57Z; proc run-duration 36.8min = s31 on normal ~35min cadence; GPU now 87% = active recall phase). Only **size100k s41 + aggregation remain** -> ETA **~05:35-05:40Z** (~40min). On completion: scp metrics local + flag Skunkworks de-saturated VET.
- **2nd SELF-CATCH on clock (banked HARD):** my two "slowdown" worries were BOTH my laptop-time ESTIMATES running ~15-17min AHEAD of real time (laptop clock itself is fine -- I was eyeballing elapsed, not reading it). Rule: anchor timing to `(Get-Date)-StartTime` on the REMOTE clock OR real `date -u`, NEVER estimate the interval. Gate was healthy the whole time; BGE "contention" was never real (pythia held its 35min/seed cadence).
- OOM + CONTENTION both NON-ISSUES: GPU 0% compute (no thrash/OOM); concurrent non-mine BGE full-corpus refresh (proc 34036, old 6/17 cell re-running ~9.6 CPU-hrs on the remote GPU box) is CPU-bound but NOT meaningfully starving pythia (its CPU climbs fine). BGE is on the remote box (not laptop), plausibly-legit (full-corpus 177k re-embed ~2h), NOT a proven runaway -> leaving it, low-priority watch.
- SEQUENCING (flagship) -- CORRECTED AGAIN per exp_dev's RED-retraction (RED was over-called: smoke projection too weak, recall 0.10 vs CERT591's 0.83-0.96 -> inconclusive, not negative): NO separate cheap sparse-encode gate. The genuine de-risk needs FULL-SCALE (pythia-2.8b) so de-risk + build CONVERGE -> flagship build IS the test. Surviving constraint is a DESIGN param not a gate: use a NON-top-k diversity-preserving sparse-encode. So flagship proceeds when pythia frees the GPU (resource-ordering, not a logical 2nd gate). pythia still unblocks Milestone-1 + storage chain
- exp_dev: LEVER 2/3/4 + Milestone-1 + 2-axis-compose-refuse cells -> I dispatch (CPU local / GPU remote) when authored, code-trace re-verify
- skunkworks: future trigger-based count-moves -> I reciprocal-check SILENTLY (P4: verify count, note ONLY on FAIL)
- testbed: dashboard stage 2 -> I verify plan-panel Store-read; windowless-monitor re-arm DONE my side
- CLEARED this session: laptop HEAT (runaway sparse-onset killed by exp_dev + monitor process/console leak fixed via re-arm, bash 70->46); CERT 591 relabel + 5MM demotes (592->587) + refuse-gate 5b (588) + LEVER 4 (589) + phase4b demote (588) + META batch -- ALL reciprocal-dual-verified

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
