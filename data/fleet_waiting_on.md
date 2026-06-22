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
**Last-updated:** 2026-06-22T??:??Z (Phase 3 COMPLETE; STANDSTILL LIFTED; **CERT 584 / 177267 atoms / cert_ledger 631 rows**; first chain-grade post-STANDSTILL landed via Path F; team lead Agent Teams autonomous arc)

### Waiting on
- [from=USER] [type=user_check_in] : return from few-hours absence; check the priority-refactor finding (Path B over Path A per n2 landed-VET DECODE-side bottleneck) + ratify or override
- (otherwise reactive; autonomous arc spawns teammates as work demands)

### In flight
- Path B n3 `exp_n3_vq_alignment_simvq_v1` RUNNING on remote_cpu (~135min from dispatch; cell-land via watcher; pre-reg HARD-PASS ceiling_bpc ≤ 1.75 / HARD-FAIL change < 0.05; commit f5a0685a)
- Path C `exp_armA_projected_key_revival_v1` RUNNING on local_cpu (~44min from dispatch; sharper discriminator vs 4-arm; commit 39d614a0; watcher armed)
- Path D 4-arm storage-win VALUE scrutiny RESOLVED (storage-compression real 103x; compute 5x more than attention; noise-robustness unverified above sigma=0.1; commit 72f87742; ledger row `de73c03c0510d4b2` supersedes `1e1302ff6293598f`)

### Next 3 (autonomous arc bounded spawns)
1. Reactive on Path C cell-land (~44min ETA); spawn fresh hdi_skunkworks for landed-VET
2. Reactive on Path B n3 SimVQ cell-land (~135min ETA); spawn fresh hdi_skunkworks for landed-VET (HARD-PASS = first chain-grade decode-side improvement; or HARD-FAIL → reroute to Path A V_C frontier)
3. Background Phase B window 2 (2026-06-08 to 2026-06-14) ready when active hdi_skunkworks slots open

### Background (incremental, non-blocking)
- Phase B chronological windows 2-N (skunkworks bounded; ~5 windows × 1-2hr each; serialized to avoid Store-write race)
- Path A n2_capacity_scaling_v2 (V_C=4096 frontier; queued behind Path B research)
- Path C ARM A projected-key revival (cheap CPU; 2x negatives discipline)
- Phase A reconcile-cert-N mismatch audit (595 vs 583 chain_grade classification-logic; 12-atom delta)

### Recently cleared (≤5)
- **Path D 4-arm storage-win VALUE RESOLVED**: 103x compression real BUT 5x compute trade + noise-robustness unverified above sigma=0.1; ARM B is single-probe exact-tag (not multi-probe); META atom `AUDIT_storage_win_claims_require_compute_and_noise_decomposition` shipped; cert_ledger relabel `de73c03c0510d4b2` supersedes `1e1302ff6293598f` (commit 72f87742)
- **Path B research-drill DELIVERED**: SimVQ #1 lever (P~0.40-0.45 for ≥0.30 BPC ceiling improvement); MKN #2 drop-in (P~0.45-0.55); composition insight: once ceiling drops, depth_concept_gain auto-propagates. Pre-reg HARD bands. (`notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md`)
- **6th self-correction owned (this turn)**: 4-arm MIDDLE_BAND framing was based on SMOKE not full GPU; Path C cell-author + Path D Skunkworks both caught independently. Discipline atom `verify-run_mode-before-treating-verdict-as-cert-grade` banks (`notes/research_to_all_DIRECTOR_REFRAME_4arm_was_smoke_not_full_path_C_reframed_2026-06-22.md`)
- **CERT 583 → 584** (first chain-grade post-STANDSTILL): U1 FB15k-237 ingest-eval HARD_PASS ratified off-data (7410x over random); substrate ingest pipeline OPERATIONAL + governable + composable; Phase C live-write helper validated in production
- **Phase 3 migration COMPLETE INFRA OPERATIONAL** (commits a147e027/f18156a8/2b97c564/017174e5/8a19df9f); STANDSTILL LIFTED

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
**Last-updated:** 2026-06-22T07:10:00Z (n10 whitening-projection revival cell-author in-flight; 2nd field-test of Fix #11 pipeline-template)

### Waiting on
- [from=runner] [type=cell_land] [filed=2026-06-22T07:10Z] : exp_n10_whitening_projection_revival_v1 (smoke->FULL; 3x revival of Path C ARM A; ZCA-whiten contrastive-projected keys; pre-reg HARD_PASS arm B>=0.35 at M=10k sig=0.1 AND proj_recall_sanity>=0.15; 4-arm A/B/C/D; pythia-160m; 3 seeds; wall 7200-10800s per TODO #8)
- [from=runner] [type=cell_land] [filed=2026-06-22T06:26Z] : humaneval_stdlib_split_qwen_v1 (FULL 164 problems x 2 arms on local_cpu_queue, ~3.0h ETA, timeout 14400s) -> verify Class A gain_A vs +15/+5 pre-reg bands + discriminating-regime Class B gain
- [from=runner] [type=cell_land] [filed=2026-06-22T05:35Z] : n8_conceptnet_ingest_eval_v1 (FULL 3-seed at remote_cpu_queue, timeout 3600s) -> verify HARD_PASS bands incl. OPEN-C frozen-encoder >=2x ratio
- [from=runner] [type=cell_land] [filed=2026-06-22T05:28Z] : n6_wikitext103 + n7_arxiv_abstracts SMOKE lands on remote_cpu_queue -> verify provenance-real + bigram baselines + walls; gate FULL dispatch on smoke-clean
- [from=skunkworks] [type=schema_vet] : prior open VETs (U1 OPEN A-E etc.) -- still routed/ratified per arc; no NEW wait from this turn

### In flight
- n10 whitening-projection revival (Skunkworks #1 revival from n9 landed-VET 2026-06-22; eff-rank raising at projection step BEFORE encoder upgrade): authoring exp_n10_whitening_projection_revival_v1.py from n9 base + ZCA-whitening over CERT591-style contrastive projection. 4 arms: A=un-white argmax anchor, B=ZCA-white argmax rescue, C=un-white SMH cross-cell anchor, D=ZCA-white-then-random-rotation control. Pre-reg HARD_PASS B>=0.35 AND sanity>=0.15; HARD_FAIL <0.10 OR sanity<0.05. eff_rank BEFORE/AFTER whitening logged as load-bearing diagnostic. Applies Fix #11 TODO #6 (in-cell smoke detect), #8 (conservative wall), #9 (atexit synthesize). Second field-test of patched template.
- HumanEval Anchor-1 stdlib-class split (Research scope-drill 2026-06-22): authored exp_humaneval_stdlib_split_qwen_v1.py; FULL 164*2 ETA ~3.0h on local_cpu_queue (status=running).
- N8 ConceptNet ingest-eval prior dispatch on remote_cpu_queue (still pending).
- Tier-2 n6 WikiText-103 + n7 arxiv-abstracts smokes on remote_cpu_queue.

### Next 3 (if bandwidth opens)
1. On HumanEval Anchor-1 cell-land: re-derive Class A pass@1 off per_problem; if HARD_PASS (gain_A >= +15 AND Class B gain < +5), route landed-VET to Skunkworks; if MIDDLE_BAND/HARD_FAIL, route 2x-revival to Research with angle (richer stdlib index? Qwen-3B?).
2. On n8 ConceptNet land: re-derive headline numbers + route landed-VET.
3. On n6 + n7 smoke lands: triage + gate FULL dispatch.

### Recently cleared (rolling; <=5)
- humaneval_stdlib_split_qwen_v1 smoke (commit 47505370) -- harness operational, n=10 zero-flips on Class A (tiny-sample), typing-import bug FIXED + selftest dep-free (queue_add system-python gate).
- U1: scaffold 41aa9f89 (selftest+smoke PASS) + design-VET ec5e5638 + 1-to-many fidelity-ceiling addendum e95d3c96 + OPEN-E de-risk 8f26a6b7 (set-ingest feasible)
- 2702fa64 N3 shakedown PASS + 2 findings (substrate at-chance on real text / BPC-ratio gameable -> validates Skunkworks N3 absolute-floor bands)
- 6d3d2d82 LOAD-BEARING eff-rank RESULT (common-mode intrinsic / rank 3.56x templating-sensitive but low-absolute -> dense more-headroom-not-reopened; self-corrected own headline)
- 50870993/76db14e8/f31c6e9a N3 scope-DECISION + shakespeare loader + caught wikitext2 silent-synthetic bug

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
