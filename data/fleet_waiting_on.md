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
**Last-updated:** 2026-06-21T06:08:00Z (date -u; post pythia-gate, flagship dispatched)
- WAITING on: Orchestrator -> push + GPU-dispatch the flagship PROBE to marsh@home (cell ready, GPU free); local_cpu runner -> NEW-4 full run. Nothing else blocking.
- **MASTER GATE CLEARED:** pythia desat CERT 583 landed (Skunkworks formal VET off canonical). Cell-author CONCUR filed -- direction-correction (substrate crowds MORE than random = discrimination signature) VALIDATES my v2 random-control design. No re-VET delta.
- **FLAGSHIP PROBE: GPU-DISPATCH-ROUTED** (42b82758 -> Orchestrator note 7232ff45). Authored to RATIFIED amendment v5 + followup: 4 variants (A naive / B SHRINKAGE-ZCA whiten-before-topk LEAD / C random-fixed / D abs-ZCA neg-control) x f{0.02-anchor,0.05-anchor,0.10,0.20} x 3 seeds. selftest+smoke PASS. **PRE-DISPATCH CATCH (mine):** naive amendment-v4 abs-eps ZCA recall-COLLAPSES at N>>n_keys (rank-deficiency, recall 0.07 vs dense 1.0); fixed w/ shrinkage-relative-floor ZCA (recall 1.0 + diversifies); caught model-free before burning a GPU run; Research ratified as v5, credited.
- **NEW-4 random-control: BUILT + QUEUED** local_cpu (fdffe597; runner picks up full 3-seed, restart-safe). Smoke: arm1=1.0 arm2=0.32 discrim=0.68. **DATA-DRIFT flag routed:** sibling's hardcoded npz drifted to 509 tokens (it ran n_tok=40000); re-pointed at the 106427 pool at data/llama_1b_results/ for true apples-to-apples (assumption flagged for Skunkworks to confirm).
- On flagship land -> probe_gate -> author L-build cell 2 (4-arm, variant=B at probe-healthy f). FUTURE queue: continual-write v2 (120-run, pythia-independent), HNSW-on-#7-projected, 2-level-ingest. Monitor clean (b0vh3rfol).

## testbed
**Last-updated:** 2026-06-20T23:32:00Z (true `date -u` UTC; prior label "01:18Z" was local-as-Z — Orchestrator caught it)
- (nothing immediate -- Layer-2 raw witness on refuse-gate 5b CLOSED (commit b16a8308); CERT 588 LANDED + Orchestrator Layer-3 reciprocal PASS)
- self: add per-section staleness drift-detector to dashboard (catches stale `## <role>` sections, not just whole-file mtime; USER caught this gap)
- self: refine plan-stall detector to be reframe-aware (currently false-positives on priorities awaiting cell-author start)
- self: standing audit discipline -- proactive Health-tab pulse on every turn + drive resolution on RED, not observe-only
- (closed this cycle: dashboard v2 LIVE; scheduled-task popups silenced; monitor filter tightened; refuse-gate 5b Layer-2 raw witness CONCUR -> CERT 588 landed)

## orchestrator
**Last-updated:** 2026-06-21T06:16:58Z (REAL date -u; flagship dispatched + DATA-REFERENT investigated)
- **DATA-REFERENT DRIFT (Skunkworks routed -> my Custodian lane): investigated, root-caused, recommendation filed.** phase05 npz @ `data/exp_phase05_.../` = SMOKE-CLOBBER (509, Instruct, smoke meta) over the original 40k. Skunkworks's "repoint to POOL" premise FAILS verify-the-referent: POOL (106427) differs in doc-structure AND model_id (BASE-1B vs the smoke's Instruct) -> NOT a clean drop-in; nested 229MB copy CORRUPT. Original 40k effectively LOST. Recommended (note ...DATA_REFERENT_investigated...): NO demote (certs ran valid), NO blind repoint, canonical fix = RE-EXTRACT (seeded/deterministic) once Exp-Dev confirms the certs' model+config; immediate = PROVENANCE_HAZARD_README dropped (non-destructive) + re-VET-asserts-n_tok guard. Reactive on Exp-Dev's model+config answer.
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
