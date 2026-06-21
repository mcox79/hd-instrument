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

**NEW 2026-06-21 #3 — pre-staged 3-deep backlog:** each session adds a `### Next 3 (if bandwidth opens)` subsection under their `## <role>` — substantive in-role items to work on when idle + no event-driven trigger. Systemic fix to standing-drift: default-action the top item without prompting. Skunkworks already does this implicitly (cert-integrity audit grind); explicit + tracked for all sessions now.

**NEW 2026-06-21 — SECTION SUB-STRUCTURE** (sub-improvements per USER ack on bloat): each `## <role>` section now uses 5 fixed subsections to keep scannable + parseable:

```
## <role>
**Last-updated:** <true date -u +"%Y-%m-%dT%H:%M:%SZ">

### Waiting on
- [from=<other-role>] [type=schema_vet|landed_vet|build|cell_land|user_decision|reciprocal] [filed=<UTC>] : <≤140 chars>

### In flight
- <one-line: what you're currently doing>

### Next 3 (if bandwidth opens)
1. <next ship 1>
2. <next ship 2>
3. <next ship 3>

### Steady-state (optional)
- <"exempt from probes until X" with explicit trigger that un-sets this>

### Recently cleared (rolling; ≤5; older items drop)
- <commit/note ref + 1-line>
```

Rules: per-item length cap ≤140 chars (long content goes in routing notes; pointer here). Auto-prune `Recently cleared` to ≤5 entries (or items >6h drop). `Steady-state` is OPTIONAL — only present when declaring; un-set when named trigger fires. `[type=...]` token enables parseable dependency graph (planned dashboard "X blocking Y" tile).

---

## research
**Last-updated:** 2026-06-21T15:08:00Z (true `date -u`)  (**CERT 583** / atoms 177264 / item #4 PRE-STAGE filed; 4-gap audit closed)

### Waiting on
- [from=skunkworks] [type=schema_vet] [filed=15:05Z] : anisotropy-rescue 4-arm cell amendment v1 (C1+C2 absorbed; ARM1_RAW<0.80 KILL gate per empirical CPU verification) → her landed-VET on cell-land
- [from=skunkworks] [type=schema_vet] [filed=15:05Z] : item #4 attention-over-substrate-keys PRE-STAGE → SCHEMA-VET (Phase 3 substrate-native foundation candidate)
- [from=skunkworks] [type=landed_vet] : whitening-revival GPU cell → re-VET-upgrade-existing-atom pathway (chain-grade-at-bound IFF ARM1-whitened≥0.80)
- [from=exp_dev] [type=cell_land] : 3 USER-auth'd remote-reroute cells (NEW-4 + D1×2) → Skunkworks landed-VETs
- [from=skunkworks] [type=meta_atomize] [filed=14:55Z] : A5-atomize translation-gap META discipline (offered + requested)

### In flight
- Item #4 attention PRE-STAGE filed (commit 7e5868fa); reactive on Skunkworks SCHEMA-VET + cell-author cascade

### Next 3 (if bandwidth opens)
1. M2 amendment v5 contingent draft (if learned bound < 5000 from whitening-revival outcome; speculative-pre-result; defer until data lands)
2. Director cross-check on revival v2 clean-meter cell-land (will land per Orch's verify-it-starts; reactive)
3. plan.json maintenance — add storage_chain_item_4 priority + update item_3 with current revival-paths-in-flight state

### Recently cleared (≤5)
- 4-gap routing audit + Skunkworks disposition 3-DEFER+1-SUPERSEDED + META atomize requested (commit 7dd5c64d)
- DEEPER 5x branching research drill DELIVERED + amendment v1 absorbing C1+C2 KILL-gate fix (commits 23af3cb7 + 7e5868fa)
- 2 USER-auth'd decisions routed to Orch (remote-reroute + phase05 restore; commits this stretch)
- Storage-chain dual-cell saga COMPLETE (flagship L-build HONEST_NEGATIVE 177259 + dense-KV-envelope MM 177264; Director cross-checks; M2 amendments v3/v4; soft-retract pivot-to-item-4 premature-negativity-bias; commits 7b6e8dac/63f29c31/31511466)
- pythia desat CERT 582→583 EARNED upward atomized (commit bfcc0af7); continual-write MM 7f39f342

## skunkworks
**Last-updated:** 2026-06-21T14:45:00Z (true date -u UTC)  (**CERT 583** / atoms 177264 / dense-KV arc closed honest; whitening de-risked; 5 new atoms cross-ref clean)

### Waiting on
- [from=exp_dev] [type=cell_land] : whitening-revival GPU cell (random-perm split + shrinkage-ZCA preprocess) -> my SCHEMA-VET + landed-VET (chain-grade-at-bound IFF ARM1-whitened>=0.80, cv<=0.05)
- [from=exp_dev] [type=cell_land] : NEW-4 + D1 planted_csp/pp49_hrc (gated on local_cpu runner restore) -> my reclassify + 3-way-verdict rulings
- [from=research] [type=schema_vet] : M2 v4 cell + Milestone-1 -> SCHEMA-VETs

### In flight
- Reactive-hold: dense-KV storage arc CLOSED honest (envelope MM + learned-key collapse MM, inflation-backstop vindicated); whitening-revival de-risked (CPU PoC) + GATE-1-gap closed; whitening GPU cell being authored by Exp-Dev with my conditions.

### Next 3 (if bandwidth opens)
1. Pre-stage the whitening-cell SCHEMA-VET checklist (random-perm split + ZCA d x d M-indep + ARM1-whitened>=0.80/cv<=0.05 bar + win-axis) -> instant VET on land.
2. Extend the whitening CPU PoC to validate the full WIN-AXIS on synthetic (ZCA d x d M-indep + recover-AT-M-indep-storage).
3. Substrate-mine: existing key-isotropization / anisotropy-correction cert/atom (build on prior work, don't re-derive).

### Recently cleared (rolling; <=5)
- 93e07163 closure-audit (Next-3 default-action) CAUGHT+FIXED dangling composes_with -> all 5 new atoms cross-ref clean
- 23f42b30 learned-key collapse MM atomized (clean train-7500 confound-free; ACCEPT-GATE2)
- ed9e2f4b whitening-revival CPU PoC (mechanism CONFIRMED: isotropization recovers ARM1)
- e08199ed dense-KV envelope MM atomized (inflation-backstop vs 3-party chain-grade lean)
- 79bcc119/e32e52f3/a1cb970b 3 disciplines atomized (verify-own-routing / eval-protocol-referent / info-theoretic-floor)

## exp_dev
**Last-updated:** 2026-06-21T06:20:00Z (date -u; 3 cells shipped this cycle)
- WAITING on: GPU run (flagship probe, Orchestrator watching, 3h timeout) + local_cpu runner (NEW-4 + continual-write full 3-seed). Nothing else blocking. 3 cells in flight off my hands.
- **MASTER GATE CLEARED:** pythia desat CERT 583 (Skunkworks formal VET). Cell-author CONCUR filed (direction-correction = substrate crowds MORE than random = my v2 random-control's intended discrimination signal).
- **FLAGSHIP PROBE: GPU-DISPATCHED** (42b82758; Orchestrator overnight_queue, verified queued, remote self-test 5.2s). 4 variants x f{0.02,0.05,0.10,0.20} x 3 seeds, ratified amendment-v5. **PRE-DISPATCH CATCH (mine):** naive abs-eps ZCA recall-collapses at N>>n_keys (rank-deficiency, 0.07 vs dense 1.0); fixed shrinkage-ZCA (recall 1.0); caught model-free before a wasted GPU run; Research ratified v5, credited.
- **NEW-4 random-control: BUILT + QUEUED** (fdffe597). Smoke arm1=1.0/arm2=0.32/discrim=0.68. **DATA-DRIFT catch ELEVATED by Skunkworks to a new discipline + 10-cert hygiene action** (phase05 npz truncated 509 vs n_tok=40000; re-pointed at 106427 pool, confirmed OK to proceed).
- **CONTINUAL-WRITE: BUILT + QUEUED** (3019d04d; reuses Skunkworks GREEN-demo core verbatim). Smoke: Workload A LRU=oracle=1.0 (GREEN replicated) / Workload B scope-bound (no label-free proxy recovers silent-important = MIDDLE_BAND honest). **Proxy-semantics flag routed** (recall_error/kramers = my interpretation; B-recovery interpretation-sensitive; SCHEMA-VET requested).
- On flagship land -> probe_gate -> L-build cell 2. FUTURE: HNSW-on-#7-projected, 2-level-ingest, D1 2-suspect re-runs. Monitor clean (b0vh3rfol).

## testbed
**Last-updated:** 2026-06-21T14:40:00Z

### Waiting on
- [from=skunkworks] [type=schema_vet] [filed=2026-06-21T14:40Z] : my Layer-2 witness on next chain-grade-eligible cell (when asked)

### In flight
- Just shipped section-substructure improvements (this file's new template + my own as canonical example)

### Next 3 (if bandwidth opens)
1. Dashboard endpoint that parses sub-structured `Waiting on` items into dependency graph (X blocking Y view)
2. 2nd-witness any un-witnessed chain-grade atom from today's Store (sweep)
3. Refine RED-watcher: suppress ACK/CONCUR follow-up notes that contain RED-pattern in filename but aren't new REDs

### Steady-state (optional)
- (none — actively progressing)

### Recently cleared (rolling; ≤5; older drop)
- 1bbd0af2 R15 (first under new consolidated-cycle_responses protocol)
- 108b41ee Stop hook auto-pulse + self-test (USER #1 + #4)
- e5d89362 cycle_responses.md consolidated doc (USER #2)
- 55e58d0f 3-deep backlog template + pre-auth memory (USER #3 + #5)
- 6fd4988a Stop hook import-time bug fix (both hint helpers had been silently broken)

## orchestrator
**Last-updated:** 2026-06-21T15:07:00Z

### Waiting on
- [from=skunkworks] [type=landed_vet] [filed=15:06Z] : whitening-revival on land (~60-90min; item#3 chain-grade-at-bound IFF ARM1-whitened>=0.80, P~0.60-0.75) -> I scp + reciprocal-if-count-move
- [from=exp_dev] [type=cell_land] [filed=15:00Z] : D1/NEW-4 local cells completing (planted_csp DONE exit0; pp49+NEW-4 running on revived runner) -> Skunkworks landed-VETs

### In flight
- Watching whitening-revival GPU (94% util, verified-started) + D1/NEW-4 local cells (runner REVIVED). Both USER decisions EXECUTED.

### Next 3 (if bandwidth opens)
1. Consolidate the session's dispatch-discipline lessons into 1 note -> Skunkworks atomizes (verify-the-RESULT / GPU-free-check / ckpt-key-all-params / precision+eval-protocol-of-referent / verify-it-starts). No Store-write by me.
2. Read-only audit other GPU cells for CONFIG_VERSION ckpt-key gap (omit result-params -> stale-resume risk); verify-per-cell, no name-similarity false-alarms.
3. Prep remote-reroute readiness for the wedged-runner D1 cells (verify remote-ready) so the workaround is instant if opted-in.

### Recently cleared (rolling; <=5)
- pythia desat CERT 582->583 EARNED (bfcc0af7); my L3 reciprocal 583/177256 PASS = master gate cleared
- flagship sparse-projected-KV = MIDDLE_BAND honest-negative (L-build, no arm hits recall>=0.80); reciprocal 583/177259
- dense-KV: envelope MM + learned-key COLLAPSE MM (583/177264); whitening-revival=next upgrade; attention-retrieval=working path
- phase05 smoke-clobber: REPOINT-to-POOL (git-proven base; restore USER-gated); pythia160m "2nd clobber"=false alarm retracted
- dispatch saga lessons banked: bf16-OOM-fix / verify-it-starts / verify-the-RESULT (stale-ckpt) / precision+eval-protocol-of-referent

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
