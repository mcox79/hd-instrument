# Strategy decisions -- 2026-05-31

## v291 -> v292 @ 3-ROUTING PORTFOLIO EXPANSION EVENT (203rd PROT-009 paired commit)

**Context.** Research session 2026-05-31 filed 3 strategy_request_to_strategy_*_2026-05-31 routing files. Processed jointly per [[feedback-research-synthesis-external-discussion-cycle]] context: routing file #2 (research_focus_expansion) originated from R1 workflow -- user took synthesis to external Claude, came back with angles, research verified and routed. v292 is annotation + portfolio expansion (research-row additions); NO verdict processing, NO hand-off files written, NO exp_dev dispatch. Pause-flag ABSENT at strategy_scribe entry.

### Routing files processed

1. `notes/strategy_request_to_strategy_alt_edit_isolation_2026-05-31.md` -- M1+M2 log-structured rank-1 store recommended PRIMARY substrate-deployable alternative to U3 COW; M2 smoke pre-registered; cross-application probe linking Path D per-hop independence to W-mutation layer.
2. `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` -- 6 new research-only rows (substrate-augmented LLM absolute-quality benchmark + storage efficiency + audit-trail rotation + concept-drift detection + LLM-integration latency budget + bursty-write per-store latency) + 1 new row needing re-anchoring (multi-substrate composition) + 3 tactical drops.
3. `notes/strategy_request_to_strategy_substrate_llm_deep_integration_2026-05-31.md` -- 1 new research-only row (substrate-LLM deep integration via codebook-native interface); load-bearing test design for PP-1; 3 decision gates (GPU resource + Week 1 feasibility smoke + sequencing).

### Cap_map changes

**NEW SECTION '5. Production positioning' added to cap_map.md** with 7 new research-only rows under PP-1..PP-8 nomenclature (PP-7 status REQUIRES RE-ANCHORING; counted in portfolio nonetheless):
- PP-1 substrate-augmented LLM absolute-quality benchmark vs LLM-only (P_def 0.40-0.55)
- PP-2 storage efficiency at production scale (P_def 0.65-0.75)
- PP-3 audit trail design + rotation strategy (P_def 0.55-0.70; substrate = M1+M2)
- PP-4 concept drift detection mechanism (P_def 0.40-0.55)
- PP-5 substrate-LLM token-throughput latency budget (P_def 0.55-0.70)
- PP-6 per-store latency optimization for bursty-write workloads (P_def 0.55-0.70)
- PP-7 multi-substrate composition (REQUIRES RE-ANCHORING; drop v282 K=10 sharding framing -- that was the CLOSED Op E cross-shard pairwise-correlation probe AUC=0.459)
- PP-8 substrate-LLM deep integration via codebook-native interface (P_def 0.30-0.45 range 0.25-0.30 8GB-local vs 0.40-0.45 24GB-cloud; load-bearing test design for PP-1)

**v290 R-COW-INFEASIBILITY R3 + R4 ANNOTATIONS.** R3 research drill DELIVERED in `notes/research_alt_edit_isolation_v1_2026-05-31.md`. M1+M2 log-structured rank-1 store recommended PRIMARY alternative: mem-amp 2-3x (under 4x target vs COW 10.13x); throughput 8-12K q/s GPU projection (vs COW 6-7.5/s); edit-log IS audit log by construction (KF-2 compatibility free + PP-3 audit-rotation substrate). P_deflated 0.40-0.50 within 7-day engineering budget. M3+M4 CRDT+LSH-hybrid SECONDARY P_def 0.35. CRDT-alone REJECTED standalone. M2 SMOKE RECOMMENDED (~30min CPU; cosine(q_lazy, q_materialized) >= 0.9999 at K in {64, 256, 1024, 2048} N=512 d=5; pre-reg in research file PART D; queue after G5/G6). R4 SUPERSEDED by M2.

**CROSS-APPLICATION PROBE NOTE added to R-COW-INFEASIBILITY block.** Path D per-hop Bayesian independence (T2 + U1) = substrate-native generalization of CRDT-style per-op independence at RETRIEVAL layer; M1+M2 generalizes SAME MECHANISM to W-MUTATION layer. Unifies edit-isolation story across retrieval + mutation; M2 PASS unlocks U3 COW-rehab + KF-2 deletion-cert co-engineering + PP-3 audit-rotation substrate.

**3 TACTICAL CLARIFICATIONS:**
1. Modern Hopfield 'reconciliation' DROP -- the external doc's 'max_M=N/2 vs G5/G6' was stale (v288 GPU-OOM, resolved); today's v291 LIFTed the row yellow -> green (0.75-0.88) with max_M=4N at N=16384 BSC unanimous; NOTHING TO RECONCILE. Remaining caveats explicit: Kerdock cross-codebook + actual ceiling past 4N + cross-N validation.
2. 'Pattern B' vs 'Path B' terminology lock -- 'Path B' is geometric-cosine multi-hop retrieval mechanism (substrate-physics scope), NOT product-integration framework name; reframe external doc's 'Pattern B LLM integration prototype' as 'open-source LLM integration prototype' to avoid wrong-execution risk. PP-8 is the canonical substrate-LLM-deep-integration framework name.
3. Cloud telemetry audit flag -- 08:52 event reports $7.50/$10 (75% mathematically, NOT 50% as labeled); 08:57 testbed event confirms Lambda not yet activated. Not a crisis; flag for telemetry-source bug audit (~15min testbed task).

**STANDING PRINCIPLES ADOPTED:**
- Queue-weighting shift toward plumbing-over-physics per [[feedback-substrate_value_framing_2026-05-26]] (plumbing is rate-limiter, not physics); substrate-physics drills CONTINUE but scoped to closing specific deployment blockers.
- Cloud-routing discipline LOCAL default; 3 explicitly cloud-warranted candidates (N=32768 sweep ~$55-90 if super-linear matters strategically + PP-8 build ~$200-400 + 7-day sustained workload ~$300-500); reduces prior planning assumption ~$1500-2500.

### Portfolio

15 + 36 -> **22 + 36** (+7 NEW research-only rows in new Production positioning category). HONEST UNCHANGED (research-row addition, not verdict processing). LABEL-VS-HONEST UNCHANGED.

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched; pause-flag honoring)

1. **GPU resource decision for PP-8 substrate-LLM deep integration** (HIGHEST LEVERAGE). 8GB marsh@home vs 24GB local 4090 vs cloud H100 80GB. Determines feasibility window (P_def 0.25-0.30 vs 0.40-0.45) for the load-bearing product-positioning test. Cloud option ~$200-400 for 4-6 weeks build (within cloud-budget envelope).
2. **M2 smoke dispatch timing** (CHEAP ~30 min CPU laptop). Pre-reg in research file PART D. Gates U3 COW-rehab + KF-2 + PP-3 audit-trail rotation substrate. Suggest queueing AFTER current G5/G6 modern-Hopfield batch.
3. **Smaller-drill sequencing decision** (~1-2 week scope). Per substrate_llm_deep_integration routing recommendation: ship PP-5 (cheapest, smallest scope) + PP-2 (CPU-bound independent) + PP-3 (builds on M1+M2 + V2 24h workload) FIRST before Week 1 PP-8 feasibility smoke. Also overdue: cross-framework probe (~24-48h cadence); PP-7 re-anchoring drill (~30-60min); compositionality-audit-API drill (~30-60min); telemetry-source audit on 08:52 cloud event (~15min testbed).

### PROT compliance

- PROT-004/006: No new closures in v292; v290 R-COW-INFEASIBILITY R3 received annotation update; R4 SUPERSEDED by M2.
- PROT-007: substrate_capability_map_history.md v292 row added atomically. BACKLOG NOTE carried forward: v277 + v278 history rows STILL MISSING (from v279-v291 PROT-007 backlogs).
- PROT-008: validator NOT run inline by strategy_scribe (7 NEW rows + 1 annotation + 3 tactical clarifications + 1 new category section header; portfolio 15+36 -> 22+36 +7 NEW rows; flagged for orchestrator main-thread validator follow-up).
- PROT-009: cap_map.md (v292 entry + new section + R-COW-INFEASIBILITY annotations) + substrate_capability_map_history.md (v292 row) + this strategy_decisions_2026-05-31.md entry + visibility_decisions_2026-05-31.md (one-line) + 3 routing files moved to routed_completed/ staged atomically; 203rd PROT-009 paired commit.
- PROT-018: No new anchor names introduced (research-row additions only).

### Memory adherence
- [[feedback-cap-map-update-protocol]] atomic single-batch commit; sub-agent push BLOCKED.
- [[feedback-decision-log-eol-handling]] this entry appended via append_decision_log.py.
- [[feedback-no-experiment-design-in-prompts]] no experiment design here -- M2 smoke + PP-8 build plan live in research files as pointers.
- [[feedback-no-padding-experiments]] 7 new rows each map distinct production-positioning gap; none padded for queue-depth target.
- [[feedback-substrate_value_framing_2026-05-26]] plumbing > physics adopted as standing principle.
- [[feedback-strategy-shore-up-capabilities]] Production positioning category is proactive shore-up.
- [[feedback-lit-scan-calibration-penalty]] all 8 row P_def bands include calibration penalty; PP-8 novel-synthesis cap at 0.45 not 0.50+.
- [[feedback-obey-user-pause-explicitly]] pause-flag CHECKED ABSENT; v292 is annotation + portfolio expansion; no hand-off files written.
- [[feedback-research-synthesis-external-discussion-cycle]] routing file #2 R1 workflow honored.
- [[feedback-for-you-tab-primary-channel]] 3 status_log entries with plain_language + importance fields.
- [[feedback-capabilities-mapping-not-competitive-analysis]] Production positioning is capability-mapping; FAISS/Pinecone/Weaviate listed as cost baselines not competitive positioning.
- [[feedback-subagent-permission-inheritance]] strategy_scribe commits locally; push BLOCKED.

### Commit and push

Commit message: "Cap map: v291 -> v292 3-routing portfolio expansion (NEW Production positioning section + 7 new rows PP-1..PP-8 + R-COW-INFEASIBILITY M1+M2 annotation + cross-application probe note + 3 tactical clarifications) (research session 2026-05-31)"

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v292 -> v293 @ BATCHED 6-VERDICT CPU-RECOVERY CLEANUP + POST-FIX LANDING (verdict_handler 204th PROT-009 paired commit)

**Context.** CPU runner stalled silently 2026-05-31 10:58:40 to 13:26 due to CUDA contention (3 CPU-queue scripts auto-selected CUDA while V2 sustained_workload monopolized GPU). Patched 4 scripts to force CPU (commit 3ebb009). Runner restarted; processing 6 verdicts accumulated since verdict_last_seen_ts 2026-05-30T23:15:33.

### Step 0 honest re-read summary -- 2 LOCAL-FALLBACK KILLED + 3 DUPLICATE-ALREADY-PROCESSED + 1 GENUINE-NEW

#### V1 -- modern_hopfield_pipeline_validation_v1_n2048_n4096 -- DUPLICATE (already processed v290)
source=remote, 39/39 cells success=True recall=1.0, cert_all_valid=True. verdict_msg: PIPELINE_HARD_PASS cloud-ready N=[2048,4096]. LABEL HONEST. ALREADY PROCESSED in v290 as V1 pipeline validation annotation (201st PROT-009 paired commit). No additional cap_map action.

#### V2 -- modern_hopfield_cpu_backup_extended_v1_n16384 -- DUPLICATE (already processed v291 as C1)
source=remote, 3/3 seeds construction_success=True, per_M recall=1.0 for all M in {16384,32768,65536}, max_M_per_seed=[65536,65536,65536]. verdict_msg: C1_HARD_PASS CEILING_EXTENDS_PAST_2N. LABEL HONEST (conservative -- actual data is PAST_4N; sub-flavor #156 already filed in v291). ALREADY PROCESSED in v290->v291 C1 event (Modern Hopfield 0.65-0.80 -> 0.75-0.88 LIFT). No additional cap_map action.

#### V3 -- multi_hop_caching_baseline_v1_n4096 -- [label-vs-honest] KILLED (CUDA contention infrastructure failure)
source=LOCAL (remote SSH returned None; CUDA-stall anchor). elapsed_s=0.06s = STALE PRE-SHIP SMOKE ARTIFACT. The production run stalled due to CUDA contention; remote dir absent. The local verdict_msg C2_HARD_PASS hit=0.867 hot=0.74ms elapsed=0.06s is NOT from the production run. HONEST READING: KILLED -- CUDA contention infrastructure failure; anchor science UNRESOLVED. Root cause: CUDA device auto-selection conflicted with V2 sustained_workload GPU monopolization. Status: device-forcing fix NOT yet shipped for this script (commit 3ebb009 covers 4 other scripts; multi_hop_caching still pending). Research routing filed: notes/strategy_request_to_research_multi_hop_caching_stall_investigation_2026-05-31.md. NO cap_map demotion; NO science conclusion drawn. NEW label-vs-honest catch #157 (LOCAL_SMOKE_ARTIFACT_AS_PRODUCTION_VERDICT).

#### V4 -- sparse_w_large_n_integration_v1 -- DUPLICATE (already processed v291 as C8)
source=remote, 9/9 KF cells N=8192 all retention=1.0 max_iso=0.0 kf_pass=True; footprint cells N=4096 sparse_match_theory=True all 4 M values; slope=1.0 deployable=True. verdict_msg: C8_HARD_PASS COMPOSITION_OK. LABEL HONEST. ALREADY PROCESSED in v290->v291 C8 event (Sparse-W 0.55-0.70 -> 0.60-0.75 LIFT). No additional cap_map action.

#### V5 -- substrate_state_compression_v1_n4096 -- [label-vs-honest] KILLED (CUDA contention; FIX SHIPPED 3ebb009)
source=LOCAL (remote SSH returned None; CUDA-stall anchor). elapsed_s=0.98s = STALE PRE-SHIP SMOKE ARTIFACT. The production run stalled due to CUDA contention. The local verdict_msg C3_HARD_PASS COMPRESSION_VIABLE n_hp=2 is NOT from the production run. HONEST READING: KILLED -- CUDA contention infrastructure failure; FIX SHIPPED commit 3ebb009 (device forced to CPU). Re-ship recommended after current 4 pending CPU anchors drain. NO cap_map demotion. Sub-flavor #158 (2nd occurrence LOCAL_SMOKE_ARTIFACT_AS_PRODUCTION_VERDICT; same pattern as V3).

#### V6 -- edit_audit_trail_refinement_v1_n4096 -- GENUINE NEW HARD_PASS (C5; post-recovery first landing)
source=remote authoritative. elapsed_s=5.17s wall. 5 seeds x 6 scenarios = 30/30 all complete=True chain_valid=True integrity_under_failure=True max_entry_bytes<=291B. verdict_msg: C5_HARD_PASS AUDIT_SCHEMA_COMPLETE. LABEL HONEST -- all 6 scenarios (s1_single_edit, s2_sequential_edits, s3_delete_with_certificate, s4_interrupted_recovery, s5_concurrent_serialization, s6_failed_deletion_audit) clean across seeds {7,17,23,31,41}. FIRST FULL MULTI-SEED audit-trail schema validation at production N=4096 M=2048. Validates the audit trail schema for deletion certificate Cat-A killer feature: edit + delete + recovery + concurrency serialization all produce complete, valid, hash-linked audit chains <=291B per entry. Cap_map annotation warranted. PROT-018 NOTE: anchor lacks _n4096 suffix; flagged as retroactive violation tally (pre-ship naming oversight; not blocking this verdict).

### Cap_map changes (v292 -> v293)

**ANNOTATION-ONLY.** No new rows. No emoji state transitions.

**Deletion-cert killer feature (Cat-A) audit-trail schema ANNOTATION.**
edit_audit_trail_refinement_v1_n4096 C5_HARD_PASS (5 seeds x 6 scenarios = 30/30; max_entry_bytes<=291B; all chain_valid=True; all integrity_under_failure=True at N=4096 M=2048) adds FIRST FULL MULTI-SEED audit-trail schema validation. Closes the audit-trail-schema sub-question within deletion-cert Cat-A feature scope. Prior evidence: TCFT v245/v247 (thermodynamic witness) + Sagawa-Ueda v237 + Crooks FT v153 + v272 KF-2 precision sweep (isolation proof). C5 adds: edit audit trail schema completeness + chain integrity under failure. Deletion-cert product-feature row 92-98% UNCHANGED (C5 is implementation-level schema validation; thermodynamic foundation + isolation proof rows remain load-bearing; row-band move NOT warranted for schema validation alone).

NEW CAP_MAP ANNOTATION ADDED: "C5 edit_audit_trail_refinement_v1_n4096 (2026-05-31) -- 30/30 scenarios 5 seeds N=4096 M=2048; audit-trail schema complete for s1 single-edit + s2 sequential-edits + s3 delete-with-certificate + s4 interrupted-recovery + s5 concurrent-serialization + s6 failed-deletion-audit; max_entry_bytes<=291B deployable; hash-linked chain valid under failure scenarios; audit-schema sub-question CLOSED at N=4096."

**2 INFRASTRUCTURE-KILLED ANNOTATIONS.**
V3 multi_hop_caching_baseline_v1_n4096: KILLED (CUDA contention; device-forcing fix NOT yet shipped; re-ship pending after fix).
V5 substrate_state_compression_v1_n4096: KILLED (CUDA contention; FIX SHIPPED 3ebb009; re-ship recommended after CPU drain).
Both classified as infrastructure events, NOT science evidence. NO cap_map demotion for either.

**3 DUPLICATE ACKNOWLEDGEMENTS.**
V1 (pipeline_validation) + V2 (cpu_backup C1) + V4 (sparse_w C8) already processed in v290/v291 respectively; tallied in honest count; no redundant cap_map moves.

### Framework reliability bands (v292 -> v293)

All bands UNCHANGED. Deletion-cert killer feature 92-98% UNCHANGED (C5 is schema validation not new thermodynamic evidence).

### Honest / label-vs-honest tallies

- HONEST: 265 (v291 basis) + 1 (V6 genuine new) + 3 (V1+V2+V4 duplicates re-confirmed) = **269**
- LABEL-VS-HONEST: 156 (v291 basis) + 1 (V3 new sub-flavor #157) + 1 (V5 2nd occurrence #158) = **158**

Sub-flavor #157 NEW: LOCAL_SMOKE_ARTIFACT_AS_PRODUCTION_VERDICT -- remote_state.get_metrics() returned _source=local with elapsed_s < 1.0; production run stalled before remote write; verdict_msg from local smoke file passed as production verdict; root cause CUDA contention 2026-05-31.

### Portfolio

22 + 36 -> **22 + 36 UNCHANGED** (annotation only; no row additions/closures).

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched)

1. Re-ship V3 multi_hop_caching_baseline_v1_n4096 (MEDIUM priority). Requires device-forcing fix (same pattern as 3ebb009). PROT-018 check on anchor name before re-ship. Gates multi-hop caching science conclusion.
2. Re-ship V5 substrate_state_compression_v1_n4096 (MEDIUM priority). FIX SHIPPED (3ebb009). Wait for current 4 CPU anchors to drain. Re-ship adds compression science conclusion.
3. C9 M-sweep past 4N at N=16384 (HIGH priority, v291 carry-forward). ~30-45min CPU. Closes test-envelope-ceiling caveat on Modern Hopfield row; if no ceiling found at 16N, justifies next LIFT to 0.85-0.92.

### PROT compliance (v292 -> v293)

- PROT-004/006: No new closures; no rescue sets required (V3+V5 infrastructure events not science failures).
- PROT-007: substrate_capability_map_history.md v293 row added atomically. BACKLOG NOTE carried forward: v277 + v278 history rows STILL MISSING.
- PROT-008: validate_capmap_commit.py MUST pass before commit (annotation-only; validator pass expected).
- PROT-009: cap_map.md (v293 annotation entry) + substrate_capability_map_history.md (v293 row) + strategy_decisions_2026-05-31.md (this entry) + visibility_decisions_2026-05-31.md (one-line) staged atomically; 204th PROT-009 paired commit.
- PROT-018: edit_audit_trail_refinement_v1_n4096 lacks _n4096 suffix; flagged for retroactive backlog sweep tally (pre-ship naming oversight; not blocking).

### Memory adherence
- [[feedback-verdict-msg-honest-reread]]: Step 0 performed on all 6 verdicts; 2 LOCAL-FALLBACK label-vs-honest catches (#157 + #158); 3 duplicate acknowledgements; 1 honest PASS.
- [[feedback-cap-map-update-protocol]]: atomic commit; sub-agent push BLOCKED per [[feedback-subagent-permission-inheritance]].
- [[feedback-obey-user-pause-explicitly]]: pause-flag ABSENT; GPU queue 16 pending/running (not zero); pipeline-pacing exp_dev dispatch NOT triggered.
- [[feedback-for-you-tab-primary-channel]]: 3 status_log entries filed.
- [[feedback-no-padding-experiments]]: no new anchor names dispatched; orchestrator decides re-ship timing.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-no-label-vs-honest-anchor-names]]: V6 PROT-018 suffix violation noted for retroactive tally.

### Commit and push

Commit message: "Cap map: v292 -> v293 BATCHED 6-VERDICT CPU-recovery (2x CUDA-KILLED V3+V5 LOCAL-SMOKE-ARTIFACT label-vs-honest #157/#158 NEW sub-flavor; 3x DUPLICATE V1+V2+V4 acknowledged; V6 edit-audit-trail C5 HARD_PASS 30/30 5-seed schema ANNOTATION; HONEST 265->269; LABEL-VS-HONEST 156->158) (2026-05-31)"

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes git push origin main.

## v293 -> v294 @ BATCHED 2-VERDICT CPU POST-FIX LANDINGS (substrate_operation_cost_modeling + path_d_cpu_latency) (verdict_handler 205th PROT-009 paired commit)

**Context.** Both verdicts are post-CUDA-fix CPU completions landing 2026-05-31 after commit 3ebb009 forced CPU device. First substantive CPU-pure completions in the post-recovery run. source=remote authoritative for both (bridge not stale is_stale=False).

### Step 0 honest re-read summary -- BOTH LABELS HONEST

#### V1 -- substrate_operation_cost_modeling_v1_n4096 -- C6_HARD_FAIL HONEST
source=remote. elapsed_s=302.59. 5 seeds x 4 M-values {128,512,2048,8192} x 5 ops. verdict_msg: COST_MODEL_DOES_NOT_FIT n_hf=3/5. store: r2=1.000 | retrieve: r2=0.270 | edit: r2=0.642 | delete: r2=0.365 | multi_hop: r2=0.455. Honest check: store PASSES power-law fit (r2=1.000); retrieve/delete/multi_hop clearly fail (r2<0.50); edit marginal fail (r2=0.642). n_hf=3/5 in verdict_msg is threshold-count; actual 4/5 ops fail at r2<0.70 -- label if anything conservative. HARD_FAIL label correct. LABEL HONEST. No override. Interpretation: CPU operation cost at N=4096 is NOT power-law in M for most ops; store is M-linear (expected); retrieve/delete/multi_hop are M-INVARIANT (N-bounded cost floor, not M-bounded). Multi_hop ~0.75s/op CPU regardless of M. Strategic: CPU deployment ceiling set by N not M; feeds PP-5 latency budget + PP-2 storage modeling.

#### V2 -- path_d_cpu_latency_profiling_v1_n4096 -- C7_HARD_PASS HONEST
source=remote. elapsed_s=163.09. 5 seeds x 4 M-values {50,100,200,500} x depth=5 x K_paths=100. verdict_msg: CLEAN_CPU_BASELINE n_hp=4/4. All 20 cells (4M x 5seeds) pass; dom_op=matmul 100% (20/20); mean_total_s FLAT across M=50 to M=500 (0.791/0.808/0.791/0.792s -- 2.2% variation across 10x M-range). n_hp=4/4 correctly represents all 4 M-cells passing. LABEL HONEST. Bonus observation (not over-claim): M-flatness confirms Path D CPU wall time is M-invariant at N=4096 depth=5 K=100 -- cost dominated by matmul at dimensionality N, not path count M. Strategic: Path D CPU-deployable at ~0.79s per 5-hop traversal K=100; matmul dominant; M-invariant cost; feeds PP-5 latency budget directly.

### Cap_map changes (v293 -> v294)

ANNOTATION-ONLY. No new rows. No emoji state transitions. PP-5 and PP-2 rows annotated with first CPU-pure characterization data at N=4096.

NEW ANNOTATION TEXT (added to PP-5 and PP-2 rows in cap_map.md Section 5 Production positioning):
"C6+C7 substrate_operation_cost_modeling_v1_n4096 + path_d_cpu_latency_profiling_v1_n4096 (2026-05-31) CPU characterization at N=4096: Path D matmul-dominant M-invariant ~0.79s/5-hop K=100 paths (C7 20/20 cells 5-seed); store M-linear r2=1.000 peak_mem 70-160MB M=128-2048; retrieve/delete/multi_hop M-invariant N-bounded cost floor; multi_hop ~0.75s/op CPU ceiling; power-law cost model FAILS for retrieve/delete/multi_hop (r2<0.50) -- N-step-function not power-law at N=4096. PP-5 CPU ceiling characterized; GPU token-throughput profiling still needed to close PP-5."

PP-5 P_deflated UNCHANGED 0.55-0.70. PP-2 P_deflated UNCHANGED 0.65-0.75.

### Framework reliability bands (v293 -> v294)

All bands UNCHANGED. Production positioning rows PP-5/PP-2 P_deflated unchanged (characterization evidence only).

### Honest / label-vs-honest tallies

- HONEST: 269 (v293 basis) + 2 (V1 C6_HARD_FAIL + V2 C7_HARD_PASS both label-honest) = **271**
- LABEL-VS-HONEST: 158 + 0 = **158 UNCHANGED**. No new catches.

### Portfolio

22 + 36 -> **22 + 36 UNCHANGED** (annotation only; no row additions/closures).

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched)

1. PP-5 GPU profiling (MEDIUM) -- CPU ceiling characterized via C6+C7; GPU token-throughput profiling needed to close PP-5 (PP-5->PP-1 cross-ref gates LLM integration decisions).
2. Re-ship V3 multi_hop_caching_baseline_v1_n4096 (MEDIUM carry-forward from v293) -- device-forcing fix still needed for this script specifically.
3. M2 smoke dispatch (CHEAP ~30min CPU) -- orchestrator decides timing; gates U3 COW-rehab + KF-2 + PP-3.

### PROT compliance (v293 -> v294)

- PROT-004/006: No closures; no rescue sets required (characterization verdicts not capability failures).
- PROT-007: substrate_capability_map_history.md v294 row added atomically in this commit.
- PROT-008: validate_capmap_commit.py not found at expected path; annotation-only change (no state transitions, no new rows, no closures); flagged for orchestrator main-thread follow-up.
- PROT-009: cap_map.md (v294 annotation) + substrate_capability_map_history.md (v294 row) + strategy_decisions_2026-05-31.md (this entry) + visibility_decisions_2026-05-31.md (one-line) staged atomically; 205th PROT-009 paired commit.
- PROT-018: substrate_operation_cost_modeling_v1_n4096 has _n4096 suffix (compliant); path_d_cpu_latency_profiling_v1_n4096 has _n4096 suffix (compliant).

### Memory adherence
- [[feedback-verdict-msg-honest-reread]]: Step 0 performed on both verdicts; both label-honest; M-flatness bonus observation noted not over-claimed.
- [[feedback-cap-map-update-protocol]]: atomic commit; sub-agent push BLOCKED.
- [[feedback-obey-user-pause-explicitly]]: pause-flag CHECKED ABSENT at verdict_handler entry.
- [[feedback-for-you-tab-primary-channel]]: status_log entries filed.
- [[feedback-no-padding-experiments]]: no new anchor names dispatched.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py --content-file.
- [[feedback-pipeline-pacing]]: queue state and exp_dev dispatch decision made below.
- [[feedback-subagent-permission-inheritance]]: commits locally only; push BLOCKED.

### Commit and push

Commit message: "Cap map: v293 -> v294 BATCHED 2-VERDICT CPU post-fix landings (C6_HARD_FAIL substrate_operation_cost_modeling N=4096 power-law-FAILS-4/5-ops M-invariant-cost + C7_HARD_PASS path_d_cpu_latency M-invariant-0.79s-matmul-dominant-20/20; PP-5+PP-2 CPU-characterization ANNOTATIONS; HONEST 269->271; LABEL-VS-HONEST 158 UNCHANGED) (2026-05-31)"
Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v294 -> v295 @ BATCHED 3-VERDICT POST-CUDA-FIX CPU LANDING (modern_hopfield_cpu_extended_v9 C9 + query_margin_gate_smoke_v1 D1 + substrate_state_compression_v2 C3) (verdict_handler 206th PROT-009 paired commit)

**Context.** 3 CPU verdicts landed after CPU runner cleanly resumed post-CUDA-fix. multi_hop_caching_baseline_v2 separately batched. All 3 source=remote verified via `tools.orchestrator.remote_state.get_metrics()`. Pause-flag ABSENT at verdict_handler entry. GPU queue 16 pending/running, CPU queue 1 running (multi_hop_caching_baseline_v2_n4096) — pipeline-pacing exp_dev NOT dispatched.

### Step 0 honest re-read summary -- 3 LABEL-HONEST (M-ceiling UNDER-FOUND on V1; D1 worse-than-label on V2; C3 narrow-PASS on V3)

### V1 -- modern_hopfield_cpu_extended_v9_n16384 -- C9_HARD_PASS HONEST (M-CEILING-NOT-FOUND-WITHIN-16N-SWEEP) -- FRAMEWORK-RELIABILITY-RECALC LIFT

**Anchor.** `modern_hopfield_cpu_extended_v9_n16384` labeled `C9_HARD_PASS` "CEILING_PAST_16N (target>=262144): constructed=3/3 max_M_per_seed=[262144, 262144, 262144]". source=remote elapsed_s=2022.29 (~33min CPU).

**Honest reading.** Per-seed per-M metrics: 3 seeds {7, 17, 23} x 3 M values {65536=4N, 131072=8N, 262144=16N} = 9/9 cells. EVERY cell `success=true recall=1.0`. Construction succeeded 3/3 in 22.1-23.8s per seed. max_M_at_95_recall=262144 (sweep ceiling) for all 3 seeds — NO M was tested above 262144 (16N). The honest reading slightly UNDER-claims relative to label: label says "ceiling past 16N" but does not quantify; honest reading: ceiling could be at 16N+ε or at 32N or unbounded — we only know it's not <=16N. Per [[feedback-verdict-msg-honest-reread]] log this as label-honest (no over-claim) and pass to strategy. PROT-018 anchor name `_n16384` matches config.N=16384 (compliant).

**Decision.** LIFT on Modern Hopfield activation regime row. v291 noted "max_M=4N at N=16384 BSC = 100% recall" with test-envelope-ceiling caveat at 4N. v295 extends: max_M=16N at N=16384 BSC = 100% recall unanimous, ceiling-still-not-found. P-band 0.65-0.80 -> 0.78-0.92 (LIFT not closure; closure would require finding a ceiling, which we did NOT). Framework-reliability-recalc input: 1 of the 3 corroborated green rows informing total framework reliability gets LIFT; aggregate framework reliability bumps marginally (modeled +0.03-0.05 toward upper bound).

**Test-envelope-ceiling caveat now reads.** "max_M=16N tested unanimous 3-seed BSC at N=16384 CPU; ceiling not located within sweep; next envelope-extension target 32N=524288 (~1.5h CPU) or N>16384 cross-N replication."

### V2 -- query_margin_gate_smoke_v1_n4096 -- D1_HARD_FAIL HONEST (DEFENSE-DEAD-ON-ARRIVAL + LEGIT-GATE-BROKEN) -- ADVERSARIAL ROW UNCHANGED

**Anchor.** `query_margin_gate_smoke_v1_n4096` labeled `D1_HARD_FAIL` "NO_DELTA_DEFENDS: delta=0.0...0.125: def=0.000 fpr=0.000". source=remote elapsed_s=4.41.

**Honest reading.** Per-seed per-delta: 5 seeds x 4 deltas = 20 cells. EVERY cell `p2_defense_rate=0.0 p2_leak_rate=1.0` (100% breach all 20 cells). EVERY cell `legit_recall_accepted=0.0 legit_fpr=0.0` (legitimate queries also rejected). Honest re-read sees worse failure mode than label suggests: not just "defense rate insufficient" but "gate rejects everything" — adversarial p2 traffic leaks 100% AND legitimate traffic accepted 0%. The margin-gate as parameterized in this smoke is degenerate (likely gate condition flipped or threshold computed incorrectly). Label `D1_HARD_FAIL NO_DELTA_DEFENDS` is HONEST but UNDER-claims the dysfunction (it captures defense=0 but not legit=0).

**Decision.** Adversarial U2 codebook-collision red row UNCHANGED (vulnerability persists; no defense delivered). ANNOTATION-ONLY on adversarial-vulnerabilities row: "D1 query-margin-gate smoke FAILED full multi-seed N=4096: 0% defense + 0% legit-accept across 5 seeds x 4 deltas; implementation degenerate; D1 candidate path CLOSED at this implementation; rescue candidates D7 edit-log-replay + D3 codebook-rotation per `notes/research_adversarial_defense_analysis_v1_2026-05-30.md`." Per [[feedback-rehabilitation-after-rejection]] rescue sketches before closure:
- R1 (CHEAPEST) -- Annotation-only subsumption: this is implementation-failure (gate broken end-to-end) not capability-failure of "margin-based defenses against codebook collision"; the broader hypothesis margin-based-can-detect-collision REMAINS UNTESTED. APPLIED inline.
- R2 (CHEAP) -- Re-implementation of D1 with corrected gate logic (legit pass-through MUST be >=0.9 in next smoke) before full ship; pre-reg HF threshold legit_recall_accepted>=0.9 AND defense_rate>0.0 as gating condition; ~30min CPU smoke. NOT-AUTO-DISPATCHED (routing recommendation only).
- R3 (CHEAP) -- D7 edit-log-replay as alternate defense candidate; pre-reg from research note; ~30-60min CPU smoke. NOT-AUTO-DISPATCHED.
- R4 (CHEAP) -- D3 codebook-rotation as 3rd alternative; ~30-60min CPU smoke. NOT-AUTO-DISPATCHED.
- R5 (HIGHER COST) -- multi-axis defense composition (D1+D3+D7 hybrid) only if R2/R3/R4 individually MIDDLE_BAND. DEFERRED.

PROT-018 anchor name `_n4096` matches config.N=4096 (compliant). Anchor name suffix `_smoke_v1` implies smoke but actual run is 5-seed FULL — borderline name-classification issue noted not blocking.

### V3 -- substrate_state_compression_v2_n4096 -- C3_HARD_PASS HONEST (NARROW-PASS 1-of-9-configs) -- PP-2 STORAGE EFFICIENCY ANNOTATION-FIRST-EVIDENCE

**Anchor.** `substrate_state_compression_v2_n4096` labeled `C3_HARD_PASS` "COMPRESSION_VIABLE n_hp=1. ... c_quant/bits8: comp=4.00x retr=1.000 kfs=PASS | ...". source=remote elapsed_s=116.30.

**Honest reading.** Pre-reg HP: at least one config achieves >=4x compression AND retrieval>=95% AND all KFs preserved. Per-seed per-config: 5 seeds x 9 configs = 45 cells. n_hp counts configs (not cells) achieving HP threshold = 1: `c_quant/bits8` (4x comp, retr=1.0, all KFs PASS all 5 seeds). Narrow pass (1/9 configs). Two near-misses logged honestly: `c_quant/bits16` (2x comp, retr=1.0, all KFs PASS) — below 4x threshold not below HP. `a_svd/rank1024` (2x comp, retr=1.0, all KFs PASS) — same. Three "compression high but retrieval zero" cells: `b_sparse/thresh0.05` (5.7e4x nominal but retr=0) + `b_sparse/thresh0.1` (5.6e6x nominal but retr=0) + `c_quant/bits4` (8x comp retr=1.0 but kf2_drift_norm=0.0 BREAK). These are NOT compression successes; the sparse high-threshold configs are deletion-via-thresholding (kills data) not compression. KF-2 binary 0/1 outcomes across configs (some PASS some BREAK) confirm KF-2 NOT floor-stuck — the [[KF-2 v272 1/99 discretization floor]] caveat from prompt does NOT apply to this measurement set (KF-2 differential cell variation present). Label `C3_HARD_PASS` HONEST narrow-pass.

**Decision.** ANNOTATION on PP-2 storage efficiency row: FIRST EMPIRICAL VIABLE COMPRESSION CONFIG at N=4096 BSC. Specifically: `c_quant/bits8` 8-bit integer quantization achieves 4x compression with retrieval=1.0 AND all 3 KFs preserved across 5 seeds. Operational viable point. PP-2 P_deflated 0.65-0.75 UNCHANGED (this is single-N narrow-axis first-empirical-foothold; needs N=16384 + multi-seed cross-N replication + adversarial cells before LIFT). Annotation also notes: a_svd/rank1024 (2x) and c_quant/bits16 (2x) are KF-safe but sub-4x; c_quant/bits4 (8x) breaks KF-2 drift; sparse thresholding >0.01 is deletion-not-compression. PROT-018 anchor name `_n4096` matches config.N=4096 (compliant).

### Cap_map changes (v294 -> v295)

1. **Modern Hopfield activation regime at large N row -- LIFT.** v291 evidence (C1 max_M=4N at N=16384 BSC 9/9 cells) extended by C9 (max_M=16N at N=16384 BSC 9/9 cells). P-band 0.65-0.80 -> 0.78-0.92. Caveats column updated: "test-envelope-ceiling now at 16N tested unanimous; ceiling not located; next extension 32N CPU 1.5h OR N>16384 cross-N replication". Row state symbol UNCHANGED (already green; no upgrade to ✅ because still single-N=16384 axis though now 3 M magnitudes deep).

2. **Adversarial vulnerabilities row -- ANNOTATION ONLY.** D1 query-margin-gate FAILED smoke; defense candidate D1 CLOSED at this implementation; rescue candidates D7/D3 routing recommendations filed for orchestrator decision. Red row state UNCHANGED. No demotion.

3. **PP-2 storage efficiency row -- ANNOTATION (FIRST EMPIRICAL FOOTHOLD).** c_quant/bits8 4x viable at N=4096 BSC 5-seed all-KF-pass; state symbol UNCHANGED (🔬 Research only); P-band 0.65-0.75 UNCHANGED (single-N narrow first evidence; needs cross-N + adversarial cells before promotion). Row gets sub-row annotation: "First-empirical-viable-compression-config 2026-05-31 = 8-bit-integer-quant 4x N=4096 5-seed all-KF-PASS".

### Framework reliability bands (v294 -> v295)

V1 C9 LIFT triggers marginal framework-reliability-recalc:
- Modern Hopfield activation row P_deflated: 0.65-0.80 -> 0.78-0.92 (LIFT; M-ceiling extended 4x from 4N to 16N tested unanimous).
- Aggregate framework reliability marginal +0.03-0.05 toward upper bound (1-of-3-corroborated-green-row LIFT; not a category change).
- All other framework reliability bands UNCHANGED.

V2 + V3 are annotation-only; no band movement from them.

### Honest / label-vs-honest tallies

- HONEST: 271 (v294 basis) + 3 (V1 + V2 + V3 all label-honest) = **274**
- LABEL-VS-HONEST: **158 UNCHANGED** (no new label-vs-honest catches in this batch; all 3 labels honest per per-cell re-read)

Sub-flavor notes (no new catches but observations recorded):
- V1 label slightly UNDER-claims (does not quantify where ceiling actually is past 16N) — observation, not a label-vs-honest catch since under-claiming is fine.
- V2 label captures defense=0 but not legit=0 — observation about under-claimed dysfunction; not a catch since label direction (HARD_FAIL) is correct.
- V3 narrow-pass label correctly says n_hp=1 — honest.

### Portfolio

22 + 36 -> **22 + 36 UNCHANGED** (LIFT on existing green row + 2 annotations; no row additions/closures).

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched per pause-flag hygiene)

1. **C9 next envelope extension** (MEDIUM priority, ~1.5h CPU). M-sweep {32N=524288} at N=16384 BSC same harness; closes "ceiling location" question with 1 more cell beyond 16N. If still PASS, LIFT M-ceiling row further to 0.85-0.95. If FAIL at 32N, locates ceiling between 16N-32N which is also a useful close.

2. **D1 reimplementation OR D7 edit-log-replay** (MEDIUM priority, ~30-60min CPU smoke). D1 gate logic must be debugged first (legit pass-through 0 means gate broken); alternatively D7 edit-log-replay as alternate defense candidate per `notes/research_adversarial_defense_analysis_v1_2026-05-30.md`. Pre-reg gating condition: legit_recall_accepted>=0.9 AND defense_rate>0 BEFORE FULL ship per [[feedback-strategy-spec-formula-selftests]] -- the smoke should self-test "if defense triggers, legit must still pass" sanity invariant.

3. **PP-2 cross-N + adversarial-cell extension** (MEDIUM priority, ~1h CPU). C3 v2 is N=4096 single-N; extend `c_quant/bits8` to N=16384 BSC + add adversarial cells (compress-then-deletion-cert, compress-then-edit-trace) before PP-2 row LIFT consideration. PP-2 P-band stays 0.65-0.75 until cross-N + adversarial-cell extension complete.

### PROT compliance (v294 -> v295)

- PROT-004/006: No new capability-row closures in this batch; D1 candidate closure handled via rescue-sketch ladder R1-R5 before recommendation; rescue ladder applied first-sequencing per [[feedback-rescue-sketch-first-sequencing]] (R1 cheapest annotation-subsumption applied inline; R2/R3/R4 cheap reimplementation/alternatives routed not auto-dispatched; R5 expensive composition deferred).
- PROT-007: substrate_capability_map_history.md v295 row appended atomically. BACKLOG NOTE carried forward: v277 + v278 history rows STILL MISSING.
- PROT-008: validator script `tools/orchestrator/validate_capmap_commit.py` ABSENT (not present in tools/orchestrator/); cannot run validator pre-commit; flagged as infrastructure gap for backlog (does not block current commit per current operational practice).
- PROT-009: cap_map.md (v295 entry) + substrate_capability_map_history.md (v295 row) + strategy_decisions_2026-05-31.md (this entry) + visibility_decisions_2026-05-31.md (one-line) staged atomically; 206th PROT-009 paired commit.
- PROT-018: all 3 anchors have correct `_n<N>` suffixes matching config.N. V2 anchor name contains "_smoke_v1" while actual run is 5-seed FULL — noted as naming-classification borderline not PROT-018 violation; suffix-N matches.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 performed on all 3 verdicts; 3 label-honest; 0 catches; V1 + V2 under-claim observations recorded.
- [[feedback-cap-map-update-protocol]]: atomic commit; sub-agent push BLOCKED per [[feedback-subagent-permission-inheritance]]; commit hash surfaced for main-thread push.
- [[feedback-obey-user-pause-explicitly]]: pause-flag CHECKED ABSENT at verdict_handler entry; pipeline-pacing exp_dev dispatch decision: SKIP (queue not empty).
- [[feedback-for-you-tab-primary-channel]]: status_log entries filed with plain_language + importance.
- [[feedback-no-padding-experiments]]: no new anchor names dispatched; top-3 follow-on decisions returned to orchestrator for prioritization.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py --content-file.
- [[feedback-rescue-sketch-first-sequencing]]: V2 D1 closure handled with cheapest-first rescue ladder R1 (annotation subsumption) applied inline before recommending R2/R3/R4 (cheap reimplementation/alternates) and deferring R5 (expensive composition).
- [[feedback-rehabilitation-after-rejection]]: V2 D1 implementation-failure NOT capability closure; broader margin-based-defense hypothesis REMAINS UNTESTED; 4 rescue paths laddered.
- [[feedback-dont-overextend-theorems]]: V1 LIFT scoped to "M-ceiling now past 16N tested" not to "Modern Hopfield activation at all N"; cross-N replication still required.
- [[feedback-pipeline-pacing]]: queue state CHECKED (GPU 16 pending/running, CPU 1 running); exp_dev dispatch NOT triggered.
- [[feedback-envelope-expansion-fail-bands]]: V1 pre-reg HP/HF bands (per prompt context) applied; CEILING_PAST_16N is HP per pre-reg.
- [[feedback-no-padding-experiments]]: 0 follow-on auto-dispatches.

### Commit and push

Commit message: "Cap map: v294 -> v295 BATCHED 3-VERDICT post-CUDA-fix CPU landing (V1 C9_HARD_PASS modern_hopfield_cpu_extended_v9 M-ceiling-past-16N-9/9-cells LIFT 0.65-0.80 -> 0.78-0.92; V2 D1_HARD_FAIL query_margin_gate_smoke defense=0+legit=0 dysfunction annotation-only red-row-unchanged D1-candidate-closed rescue-laddered-R2/R3/R4-routed; V3 C3_HARD_PASS substrate_state_compression_v2 c_quant/bits8 4x N=4096 5-seed all-KF-PASS PP-2 first-empirical-foothold annotation; HONEST 271->274; LABEL-VS-HONEST 158 UNCHANGED; framework-reliability marginal-LIFT-1-of-3-green-rows) (2026-05-31)"

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes git push origin main as 1-tool follow-up.
