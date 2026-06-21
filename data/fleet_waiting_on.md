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
**Last-updated:** 2026-06-21T15:55:00Z (true `date -u`)  (**CERT 583** VERIFIED-PRECISE / atoms 177265 / U0 substrate-native pivot folded; N0-N4 plan live; D1 closed)

### Waiting on
- [from=orchestrator] [type=cell_land] : N1 concept-LM cell land (Orch driving cell-authoring; substrate-native-decode + token-BPC + VQ-floor guard) → Director 4-layer cross-check on land
- [from=exp_dev] [type=cell_land] : whitening-revival GPU (~30-60min ETA; ARM1-whitened≥0.80 → re-VET-upgrade item #3 to chain-grade-at-bound) → Director cross-check + Skunkworks re-VET
- [from=exp_dev] [type=cell_land] : NEW-4 + pp49 (running on revived runner) → Skunkworks landed-VETs
- [from=skunkworks] [type=schema_vet] : pp49 deeper-sweep d>>12 (LOW-priority backlog; Hopfield ~573 capacity empirical-clearance upgrade)
- [from=skunkworks] [type=meta_atomize] [filed=14:55Z] : A5-atomize translation-gap META discipline (offered + requested; pending Skunkworks bandwidth)

### In flight
- U1 ingest-scope subagent (~25min in flight; was augmented framing; will re-interpret substrate-native lens on land)
- N2 frontier-drill subagent dispatching NOW (Skunkworks's explicit ask; per USER 'definitely work' directive)

### Next 3 (if bandwidth opens)
1. Director cross-check on N1 cell-land (Phase-3-native high-stakes 4-layer; substrate-native-decode gate verification + token-BPC ladder + VQ-floor)
2. N3 text-corpus scope-to-confirm Research drill OR pre-stage (Skunkworks asked Exp-Dev but Director-lane can pre-stage candidates)
3. pp49 deeper-sweep dispatch LOW-priority (Hopfield ~573 cliff; empirical-clearance tier upgrade for KEEP)

### Recently cleared (≤5)
- U0 misframe caught + reverted + substrate-native N0-N4 FOLDED + charLM un-defer (commits b687df86 + 1b44734a)
- D1 closure both KEEP-genuine + CERT-integrity-audit D1 routing CLOSED → CERT 583 VERIFIED-PRECISE (commit e368d25b)
- Item #4 attention RESCOPED to N4-substrate-LM-memory (NOT Phase-3-foundation) + substrate-only-compatibility check + tier=MM (commit c8088adb)
- Orch N1 cell-authoring lane-assignment + substrate-only-ness gate SHARPENED off-code (commit 0e221845)
- Monitor Python re-armed + orphans killed + cycle_responses.md R1 entry (Testbed process improvements adopted; commit c98a5f11)

## skunkworks
**Last-updated:** 2026-06-21T16:2xZ (true date -u UTC)  (**CERT 583**/177265 verified-precise; SUBSTRATE-NATIVE; /loop yolo-mode active; all owed cleared)

### Waiting on (all REACTIVE-on-land; nothing owed-now)
- [from=orchestrator] [type=cell_land] : N1 concept-LM + substrate-native token-decode (per bands fbfccc99) -> landed-VET (recompute BPC off per_unit + AUDIT zero-LLM-calls), 4-layer
- [from=exp_dev] [type=cell_land] : whitening-revival proj768/A (verified-started 94% GPU per Orch) -> landed-VET (chain-grade-at-bound IFF ARM1-whitened>=0.80 cv<=0.05; FLAG: smoke recovery weak -> watch real-anisotropy vs synthetic-PoC)
- [from=exp_dev] [type=cell_land] : anisotropy-rescue 4-arm (C1/C2) -> landed-VET ; NEW-4 -> reclassify
- [from=research] [type=schema_vet] : N2 frontier-drill output -> SCHEMA-VET vs N3 BPC bands

### In flight
- /loop yolo-mode (dynamic self-pace; monitor bi5a08i70 primary wake + ~30min fallback). Cert-gating SUBSTRATE-NATIVE plan; surface to USER only on decision/verdict/blocker/cost.

### Next 3 (if bandwidth opens)
1. CPU PoC: N2 context-depth lever (does trigram-concept-transition beat bigram-concept on synthetic? quantify gain) — de-risk the #1 beat-bigram lever (coordinate w/ Research N2 drill to not duplicate).
2. Pre-stage M2 multi-hop assembly-demo bands (the chain-grade tier; per my task-coupled-ablations catch — 4 components meaningful only at multi-hop).
3. Closure-audit any new substrate-native atoms as they land.

### Recently cleared (rolling; <=5)
- b9e4485f U1 INGEST-eval bands + M1 architecture-core bands -> UNBLOCKS exp_dev U1 author (owned: had conflated N3/N1 LM-eval w/ the KB-ingest-eval; distinct -- refuse-gate + inference-transfer vs frozen-encoder + heldout_in_compose_graph==0)
- 5afb8133 M2 pre-stage SCHEMA-VET (task-coupled ablations: depth-gov inherently multi-hop; EARLY M2=2-of-4 MM, chain-grade=multi-hop)
- bab6f9b7 N3 canonical BPC cert-bands + 503aeee3 M2 ruling=B + concept-LM CPU PoC
- fbfccc99 N1 SCHEMA-VET (token-decode + substrate-only gate) + 5da82e45 item-#4 re-scope (N4-memory)
- 9a41c60e D1 rulings (CERT 583 verified-precise) + 5f7d04d4 substrate-native plan + 835d15d5 U0 correction

## exp_dev
**Last-updated:** 2026-06-21T16:15:01Z (true date -u; assembly phase, SUBSTRATE-NATIVE)

### Waiting on
- [from=orchestrator] [type=cell_land] [filed=16:15Z] : whitening-revival GPU land (verified-started 94% GPU per Orch f7afa5c8; ETA ~16:06-16:36Z) -> item#3 verdict (ARM1-whitened>=0.80 cv<=0.05 = chain-grade-at-bound) -> Skunkworks landed-VET
- [from=orchestrator] [type=cell_land] [filed=16:15Z] : anisotropy-rescue 4-arm GPU dispatch (routed ba867605/b3164349; queued behind whitening) -> verify-it-starts
- [from=skunkworks] [type=schema_vet] [filed=16:15Z] : re-anchored substrate-native ingest-eval bands (by-construction-saturation guards) + M1 bands -> unblocks U1 author
- [from=research] [type=research_drill] [filed=16:15Z] : U1 ingest scope-drill (substrate-native lens) -> de-risks U1 scope
- [from=runner] [type=cell_land] : NEW-4 per-cluster-stratified land (running local) -> Skunkworks reclassify

### In flight
- Reactive on lands. Owed cell CLEARED this turn (anisotropy-rescue authored+C1/C2+selftest+smoke PASS+routed). U1 inputs verified intact (50k FB15k-237 = 50000 lines valid; ccc1 base AST-OK) = ready-to-author the instant bands land.

### Next 3 (if bandwidth opens)
1. Pre-stage U1 ingest cell SKELETON (data-load + substrate-ingest + structure; leave eval-band thresholds as params) so authoring is instant when Skunkworks's bands land.
2. Pre-stage M1 cell scaffold (CERT591-proj + item#4-attention + C-codebook retrieval/decode components of the substrate-native LM; gated on U1 but the retrieval-core is independent).
3. Mine substrate for the optimal ingest-eval design (existing KG/multihop experiments -> facilitate Skunkworks's band-design + Research's scope-drill with a head-start artifact).

### Recently cleared (rolling; <=5)
- ba867605/b3164349 anisotropy-rescue 4-arm authored+routed (the genuine "waiting on exp_dev" item; C1 ARM1_RAW>=0.80 kill-gate + C2 storage-class; selftest+smoke PASS)
- whitening-revival referent VERIFIED in-flight (Orch f7afa5c8 started; local metrics.json=pre-dispatch smoke not the verdict; "@M=10k" summary-mislabel noted, harmless for full)
- storage-chain arc atomized (flagship sparse honest-negative -> dense random-core MM -> learned-key MM, attention=item#4)
- D1 closed (planted_csp false-alarm / pp49 cleared) + data-drift catch -> discipline + phase05 restored
- Monitor migrated to popup-free Python port (b79hunv4r); leaked bash killed (0 remaining, no respawn)

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
