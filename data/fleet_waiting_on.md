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

### In flight (REQUIRED — write the active task OR an explicit idle reason)
- <one-line: what you're currently doing — if reactive-waiting, name the dependency. Empty = idle-without-reason which the dashboard flags as a discipline gap.>

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
**Last-updated:** 2026-06-21T19:55:00Z (true `date -u`)  (**CERT 583** / atoms 177266 / cascade absorbed; N1 DEFINITIVE + 4-arm partial-rescue + N2 3-way knot; 22+ disciplines)

### Waiting on
- [from=orchestrator] [type=cell_land] : JOINT V_C × N scaling N2 #1 (V_C=1024 × N={8192,16384} × K={1,2,3}, ~10min wall) → Director cross-check + Skunkworks landed-VET on outcome
- [from=skunkworks] [type=schema_vet] : N2 JOINT V_C × N cell vs N3 absolute-floor BPC bands + alpha<1 saturation guard
- [from=USER] [type=user_decision] : agent-teams migration timing — NOT-NOW recommendation filed (testbed PROPOSE; Skunkworks disruption-risk consult requested separately)
- [from=skunkworks] [type=meta_atomize] [filed=14:55Z] : A5-atomize translation-gap META (Skunkworks bandwidth)
- [from=skunkworks] [type=director_consult] [filed=19:55Z] : disruption-risk advisor consult on agent-teams migration (3 Qs: Store-coord survives task-status-lag / cert-write-discipline survives SendMessage routing / cert-integrity during multi-day migration window)

### In flight
- Director-stance on agent-teams migration filed (NOT-NOW + LIGHT-SCOPE-NOW; 4-phase rough plan; USER decision-point flagged)
- SimVQ/FSQ #2 N2 frontier research-drill QUEUED to launch when bandwidth (post-tracker-refresh)
- ARM A FAIL revival drill QUEUED (Angles 1+3+5 topology/capacity/biology) after SimVQ

### Next 3 (if bandwidth opens)
1. Launch SimVQ/FSQ subagent research-drill (#2 N2 frontier per ranking note)
2. Launch ARM A FAIL revival drill (after SimVQ; topology-variant + capacity-regime + biology-5x)
3. pp49 deeper-sweep LOW-pri OR N4 governance wrap pre-stage (gates on N2 frontier outcome)

### Recently cleared (≤5)
- 10-cycle ping catch-up + Director 4-layer cross-check FILED on 5 cell-lands (4-arm MIDDLE_BAND tag-retrieval CLASS / N1 v3.1 DEFINITIVE PROVEN-BOUND beats unigram NOT bigram / N2 depth HARD_FAIL floor-masked / N2 co-opt DEFINITIVE 3-way knot discovery / Skunkworks phase_d_tier6 CORRECTION no count impact)
- N2 frontier RANKING RESPONSE FILED — refactored framework (3-way knot V_C × N_DIM × depth = knot-resolution sequence, not independent levers); endorse Orch solo-drive on JOINT V_C × N as #1; SimVQ/FSQ as #2; depth-3+ as #3
- ARM A sparse-superposition FAIL routed for 2x revival drill per route-negatives USER STANDING (5 angles: topology / decode / capacity-regime / projected-key / biology-5x)
- Testbed agent-teams migration RESPONSE filed (NOT-NOW + LIGHT-SCOPE-NOW; Director-stance with 4-phase rough plan + USER decision-point + Skunkworks consult)
- N1↔N3 boundary RULING FILED (architecture-AGNOSTIC eval harness) + RESCUE-CONTINGENCY chain folded into plan.json (commit 7c8925ba)

## skunkworks
**Last-updated:** 2026-06-21T18:3xZ (true date -u UTC)  (**CERT 583**/177266; SUBSTRATE-NATIVE; /loop yolo; whitening MM ruled; exp_dev 3 waits cleared)

### Waiting on (all REACTIVE-on-land; nothing owed-now)
- [from=orchestrator] [type=cell_land] : N1 concept-LM + substrate-native token-decode (per fbfccc99) -> landed-VET (BPC off per_unit + AUDIT zero-LLM-calls), 4-layer
- [from=exp_dev] [type=cell_land] : anisotropy-rescue 4-arm (LIVE rescue; vs exp_dev pre-reg fc3b8771 A-fails/B-wins) -> landed-VET; pre-flight PROJECTED-eff-rank = definitive; NEW-4 -> reclassify
- [from=research] [type=schema_vet] : N2 frontier-drill output -> SCHEMA-VET vs N3 absolute-floor BPC bands
- [from=exp_dev/orch] [type=cell_land] : whitening full-metrics scp (item#3 experiment-MM atomize on the data; ruling=MM honest-negative already filed 03452c77)

### In flight
- /loop yolo (monitor bi5a08i70 primary wake + ~30min fallback). RESCUE-DRIVE: dense closed (whitening MM) + dense-reopen "more-headroom-not-reopened" (eff-rank: readable 3.6x residual but low-abs); high-M path = fly-LSH tag-retrieval (ARM B, rank-agnostic). 3 deferred rescues (PC-AM/phase-coding/product-key) routed to plan.
- **PENDING classifier-recovery (Bash/Python down): commit response note (skunkworks_to_expdev..RESPONSES); atomize gameable-ratio-band + synthetic-to-real-deflation discipline; A5-flag phase_d_tier6 if chain-grade-counted.**

### Next 3 (if bandwidth opens)
1. CPU: highest-eff-rank key-source sweep DONE (no raw contextual source >24; projection is the eff-rank-raiser) -> next: pre-stage M2 multi-hop assembly bands.
2. Closure-audit new substrate-native atoms as they land.
3. pp49 deeper-sweep low-pri (Hopfield ~573 empirical-clearance).

### Recently cleared (rolling; <=5)
- exp_dev 3 waits: eff-rank CONCUR (own last-token-conflation; more-headroom-not-reopened) + phase_d_tier6 NEEDS-RERUN (synthetic-fallback+gameable-band) + N3 absolute-floor ADOPTED (RESPONSES note)
- 03452c77 whitening landed-VET = MM honest-negative + OWN synthetic-PoC over-estimate + 8856b2ce synthetic-to-real-deflation discipline atomized
- 2b6cbb28 whitening scope-caveat + eba1d121 rescue-drive (eff-rank intrinsic; sparse/structured chain + 3 deferred) + 2 CPU de-risks (templated-vs-readable, key-source)
- dfb41903 N2 context-depth PoC (levers COUPLED: depth x codebook-granularity; floor-masks) + b9e4485f U1 ingest-eval/M1 bands
- 5afb8133 M2 pre-stage SCHEMA-VET + bab6f9b7 N3 cert-bands + fbfccc99 N1 SCHEMA-VET + 9a41c60e D1 (CERT verified-precise)

## exp_dev
**Last-updated:** 2026-06-21T18:50:00Z (true date -u; assembly phase, SUBSTRATE-NATIVE)

### Waiting on
- [from=skunkworks] [type=schema_vet] [filed=18:50Z] : U1 OPEN A-E VET (incl. multi-value-ingest) -- Skunkworks RESPONSES note WRITTEN but UNCOMMITTED (their Bash/Python down per their L83) -> arrives on infra-recovery -> unblocks U1 load-bearing build
- [from=orchestrator] [type=cell_land] [filed=18:50Z] : anisotropy-rescue land -- PAST ETA (152min vs 60-120) + Orchestrator SILENT ~2hr (it scp's the result) -> likely done/running-but-UN-SYNCED; FLEET-STALL surfaced to USER
- [from=research] [type=research_drill] [filed=17:10Z] : N1<->N3 boundary confirm -> unblocks N3 text8 cert structure
- [from=runner] [type=cell_land] : NEW-4 land -> Skunkworks reclassify

### In flight
- Tracker check-in: my 3 flags ALL resolved by Skunkworks (their L91): eff-rank CONCUR (they owned a last-token-conflation behind their 1.15x; my 3-metric reconciliation [PR 3.56x/Roy 4.71x/stable 2.07x, 813990a3] independently confirms more-headroom-not-reopened) + phase_d_tier6 NEEDS-RERUN adopted + N3 absolute-floor ADOPTED. So NO discrepancy note needed (avoided re-litigating). U1 load-bearing build still VET-gated (Skunkworks RESPONSES uncommitted due to their infra).

### Next 3 (if bandwidth opens)
1. On Skunkworks U1 VET (OPEN A-E): fill refuse-gate + inference-transfer (multi-value set-readout per de-risk) + dispatch U1 full (scale-curve M=50k separating 1-to-many ceiling from capacity crosstalk).
2. On N1<->N3 confirm: extend the shakedown harness -> N3 text8 cert (GPU) w/ absolute-floor bands + provenance-asserted real data.
3. On rescue land confirming tag-retrieval: M1 retrieval-core around TAG-RETRIEVAL (Willshaw/fly-LSH), mechanism-independent of U1 knowledge.

### Recently cleared (rolling; <=5)
- U1: scaffold 41aa9f89 (selftest+smoke PASS) + design-VET ec5e5638 + 1-to-many fidelity-ceiling addendum e95d3c96 + OPEN-E de-risk 8f26a6b7 (set-ingest feasible)
- 2702fa64 N3 shakedown PASS + 2 findings (substrate at-chance on real text / BPC-ratio gameable -> validates Skunkworks N3 absolute-floor bands)
- 6d3d2d82 LOAD-BEARING eff-rank RESULT (common-mode intrinsic / rank 3.56x templating-sensitive but low-absolute -> dense more-headroom-not-reopened; self-corrected own headline)
- 50870993/76db14e8/f31c6e9a N3 scope-DECISION + shakespeare loader + caught wikitext2 silent-synthetic bug
- WHITENING MM (item#3 CLOSED) + anisotropy-rescue authored+DISPATCHED + PRE-REG fc3b8771 + diagnostic 9ddb53fc

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
**Last-updated:** 2026-06-21T18:49:00Z (driving N1 substrate-native LM end-to-end; background subagents keep dying on process-restarts -> building v3 IN-THREAD)

### Waiting on
- (nothing blocking -- building N1 v3 in-thread; token_ids + density-params + optimized-recall all satisfied)

### In flight
- Building N1 v3 IN-THREAD: calibrated decode (temperature + unigram back-off) + Laplace-smoothed bigram/ceiling + ceiling<=log2(V) correctness gate -> dispatch remote_cpu + watcher for the FAIR token-BPC answer

### Next 3 (if bandwidth opens)
1. On v3 land: relay FAIR BPC to Research ([from=orchestrator] N1 cell-land 4-layer cross-check -- they wait) + Skunkworks (landed-VET: recompute BPC off per_unit + AUDIT zero-LLM-calls)
2. Route anisotropy 4-arm MIDDLE_BAND -> Skunkworks landed-VET + Research revival (fly-LSH B=0.998 vs raw-collapse 0.013 BUT Charikar control B'=1.000 -> WTA-tag NOT load-bearing; sparse-projection rescues recall generally; ARM A sparse-superpos FAILS 0.048)
3. N2 sweep dispatch (V_C {64,256,1024} + N_DIM) once v3 calibrated-BPC validated -- cell is sweep-ready (batched recall)

### Recently cleared (rolling; <=5)
- N1 v2 FIRST substrate-native token-LM run (off recovered token_ids): top-1=0.445 BEATS unigram 0.276, ~bigram 0.473; BPC=HARD_FAIL but METRIC-BROKEN (no smoothing; ceiling 18.16 > log2(V) 15.62 = impossible) -> v3 fixes calibration (7697c99b)
- token_ids recovery PASS after 3 Windows-bug fixes (savez .npz auto-append + 2x open-handle os.replace lock); npz now has aligned tokens (49634)
- N1 re-authored v2 substrate-optimal per Research density scour (sparse Willshaw N=4096 f=0.006, NOT under-capacity dense N=1024) + batch-optimized recall 6h->min (66544cb4)
- anisotropy 4-arm DISPATCHED + LANDED MIDDLE_BAND (b9e4485f); whitening MIDDLE_BAND routed (747430fd; isotropization does NOT rescue dense superposition)
- USER storage-density directive fully threaded into N1 (Research scour -> sparse params -> v2 -> v3)

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
