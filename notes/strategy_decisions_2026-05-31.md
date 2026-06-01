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

## v295 -> v296 @ multi_hop_caching_baseline_v2_n4096 VERDICT [label-vs-honest #159] CONFOUNDED-DESIGN (verdict_handler 207th PROT-009 paired commit)

**Context.** Single-anchor verdict for multi_hop_caching_baseline_v2_n4096. v1 was KILLED by CUDA contention (infrastructure failure, not science). v2 landed with CPU fix applied (commit 3ebb009 device=cpu). source=remote authoritative (is_stale=False, _source=remote). elapsed_s=759.84 (~13min CPU). 5 seeds x 3 alphas x 16 N_STARTS = 15 cells. Pause-flag ABSENT. GPU queue 16 pending/running, CPU queue 2 pending/running.

### Step 0 honest re-read -- [label-vs-honest #159] CONFOUNDED-DESIGN (LABEL OVER-CLAIMS scientific characterization)

**Label.** verdict_msg: 'PARTIAL: a=0.5: hit=0.984 hot=51.04ms audit=1.000 | a=1.0: hit=0.984 hot=53.74ms audit=1.000 | a=1.5: hit=0.984 hot=48.23ms audit=1.000'. Classified C2_MIDDLE_BAND.

**Honest reading.** Per-cell analysis (15 cells):
- hit_rate: 0.984 in ALL 15 cells (identical across alpha=0.5, 1.0, 1.5 and all 5 seeds)
- audit_integrity: 1.000 in ALL 15 cells
- hot_latency vs cold_latency: mean ratio=1.0036; 8/15 cells hot SLOWER than cold; NO latency benefit
- ROOT CAUSE: CACHE_CAPACITY=256 > K_PATHS=100. Cache can hold ALL 100 unique path prefixes. Once warmed, every repeated query hits regardless of Zipfian alpha. The alpha sweep is CONFOUNDED -- cache saturation artifact, not Zipfian-skew characterization.
- Expected behavior (if experiment were valid): hit_rate would increase monotonically with alpha (0.5->1.0->1.5); observed: flat 0.984 at all alpha.
- The 1.6% misses (16/1000) are first-access cold misses ONLY, not alpha-dependent.

**OVER-CLAIM.** Label C2_MIDDLE_BAND implies legitimate scientific characterization of alpha-dependent caching behavior. Honest reading: the alpha sweep produced NO discriminating signal because the design was confounded (cache over-provisioned). This is NOT a MIDDLE_BAND result; it is a CONFOUNDED-DESIGN outcome. Science question 'does LRU cache yield meaningful hit-rate at moderate Zipfian skew?' remains UNANSWERED.

New label-vs-honest sub-flavor #159: CONFOUNDED_DESIGN_AS_SCIENTIFIC_RESULT -- cache saturation artifact reported as alpha-dependent characterization.

### Cap_map changes (v295 -> v296)

**ANNOTATION-ONLY.** No new rows. No emoji state transitions. No P-band changes.

**PP row (multi-hop caching / Path D production optimization) ANNOTATION:**
'multi_hop_caching_baseline_v2_n4096 (2026-05-31) CONFOUNDED: CACHE_CAPACITY=256 > K_PATHS=100; hit_rate=0.984 uniform across alpha={0.5,1.0,1.5} 5 seeds (cache saturation artifact not Zipfian-skew signal); hot_latency=cold_latency (mean ratio=1.004; no latency benefit); alpha sweep non-discriminating; experiment redesign required: CACHE_CAPACITY < K_PATHS (e.g., capacity=16 K_PATHS=100) to test Zipfian sensitivity; PP conclusion deferred pending redesign.'

**No PP-row P-band change.** The confounded design produced zero scientific signal about caching viability. Neither positive nor negative evidence for LRU caching as production optimization. PP row remains research-only at current P_deflated band.

### Framework reliability bands (v295 -> v296)

ALL UNCHANGED. Confounded-design outcome provides no framework-class evidence.

### Honest / label-vs-honest tallies

- HONEST: 274 (v295 basis) + 0 (label over-claimed; confounded not honest) = **274 UNCHANGED**
- LABEL-VS-HONEST: 158 + 1 (new #159 CONFOUNDED_DESIGN_AS_SCIENTIFIC_RESULT) = **159**

### Portfolio

22 + 36 -> **22 + 36 UNCHANGED** (annotation only; confounded result does not add or close rows).

### Rescue sketches (PROT-004/006 -- redesign before abandoning caching hypothesis)

Per [[feedback-rehabilitation-after-rejection]] and [[feedback-rescue-sketch-first-sequencing]], cheapest first:

R1 (CHEAPEST -- subsumption annotation): The caching MECHANISM is not refuted. The experiment design was confounded (CACHE_CAPACITY > K_PATHS). The hypothesis 'LRU caching provides latency benefit for Zipfian-skewed multi-hop workloads' REMAINS UNTESTED. Applied inline.
R2 (CHEAP ~30min CPU smoke): Redesign with CACHE_CAPACITY=16, K_PATHS=100, alpha in {0.5, 1.0, 1.5}. Pre-reg: HP = hit_rate(a=1.5) >= 0.80 AND hit_rate(a=0.5) <= 0.50 (demonstrates alpha sensitivity); HF = hit_rate flat across alpha within +-0.05 band (no sensitivity). This is the definitive discriminating test. NOT-AUTO-DISPATCHED.
R3 (CHEAP ~30min CPU smoke): Alternatively vary K_PATHS holding CACHE_CAPACITY=32 fixed: K_PATHS in {32, 128, 512}. Tests cache saturation boundary directly. NOT-AUTO-DISPATCHED.
R4 (MEDIUM): Path-prefix locality experiment -- measure repeat-access rate under realistic LLM-retrieval pattern (vs pure Zipfian synthetic). Tests production-relevance of caching at typical query distributions. NOT-AUTO-DISPATCHED.
R5 (HIGHER COST): LRU vs LFU vs FIFO cache policy comparison at production-realistic K_PATHS / CACHE_CAPACITY ratios. Only if R2 or R3 shows positive alpha sensitivity. DEFERRED.

### Top-3 follow-on decisions for orchestrator

1. Re-ship caching experiment with corrected design (R2 CHEAPEST substantive test): CACHE_CAPACITY=16, K_PATHS=100, pre-reg alpha-sensitivity bands. ~30min CPU. MEDIUM priority (PP hypothesis unresolved; cheap to answer correctly this time).
2. (Carry-forward) C9 next envelope extension M-sweep 32N=524288 at N=16384 (~1.5h CPU). MEDIUM priority.
3. (Carry-forward) D1 reimplementation or D7 edit-log-replay adversarial defense (~30-60min CPU smoke). MEDIUM priority.

### PROT compliance (v295 -> v296)

- PROT-004/006: No capability-row closures. Caching hypothesis NOT closed; confounded design = implementation gap, not capability failure. 5 rescue sketches R1-R5 filed per [[feedback-rehabilitation-after-rejection]]; R1 applied inline; R2/R3 routed for orchestrator decision; R4/R5 deferred.
- PROT-007: substrate_capability_map_history.md v296 row to be appended atomically.
- PROT-008: validate_capmap_commit.py ABSENT (carried forward); annotation-only change does not risk state regression.
- PROT-009: cap_map.md (v296 annotation) + substrate_capability_map_history.md (v296 row) + strategy_decisions_2026-05-31.md (this entry) + visibility_decisions_2026-05-31.md (one-line) staged atomically; 207th PROT-009 paired commit.
- PROT-018: anchor name multi_hop_caching_baseline_v2_n4096 has _n4096 suffix matching config.N=4096 (compliant).

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 performed; label-vs-honest #159 caught (CONFOUNDED_DESIGN_AS_SCIENTIFIC_RESULT); honest reading authoritative for cap_map.
- [[feedback-cap-map-update-protocol]]: atomic commit; sub-agent push BLOCKED per [[feedback-subagent-permission-inheritance]].
- [[feedback-obey-user-pause-explicitly]]: pause-flag ABSENT; queue NOT empty (GPU 16 + CPU 2); exp_dev dispatch NOT triggered.
- [[feedback-pipeline-pacing]]: queue state CHECKED (non-zero); exp_dev dispatch NOT triggered.
- [[feedback-for-you-tab-primary-channel]]: status_log entry filed with plain_language + importance.
- [[feedback-no-padding-experiments]]: no new anchor names dispatched.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-rescue-sketch-first-sequencing]]: R1 (subsumption annotation, cheapest) applied first; R2 (redesign smoke, cheap) second; R3 (K_PATHS sweep, cheap) third; R4 (medium) fourth; R5 (expensive composition, only if positive signal) last.
- [[feedback-rehabilitation-after-rejection]]: 5 rescue sketches before caching-hypothesis abandonment.
- [[feedback-no-label-vs-honest-anchor-names]]: anchor name compliant.

### Commit and push

Commit message: 'Cap map: v295 -> v296 multi_hop_caching_baseline_v2 [label-vs-honest #159] CONFOUNDED-DESIGN cache-saturation-artifact (CACHE_CAPACITY=256 > K_PATHS=100; hit=0.984-uniform-all-alpha; no-latency-benefit; alpha-sweep non-discriminating; PP-caching deferred pending redesign; rescue sketches R1-R5 filed; HONEST 274 UNCHANGED; LABEL-VS-HONEST 158->159) (2026-05-31)'

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes git push origin main.

## 2026-05-31 v296 -> v297 verdict_handler (208th PROT-009 paired commit)

BATCHED 3-VERDICT cheap-Lambda cloud corroboration event. All 3 verdicts G7/C9/G8 HARD_PASS LABEL-HONEST per Step 0 honest re-read.

### Step 0 honest re-read (mandatory)

- **V1 G7_HARD_PASS path_d_24n_32n_envelope_v1_n4096** source=Lambda-cloud-GPU (file `data/lambda_exp_path_d_24n_32n_envelope_v1_n4096_metrics_c4f84cf820984a5992ad820d669bd6f8.json`) elapsed_s=47.06. Per-cell re-read: 40/40 cells unanimous accuracy=1.000 across M={98304=24N, 131072=32N} x depth={10,20,30,50} x 5 seeds at N=4096 K_paths=100. Label '>= 0.85' UNDERSTATES true 1.000. LABEL-HONEST (no over-claim; under-claim does not count). PROT-018 `_n4096` compliant.
- **V2 C9_HARD_PASS modern_hopfield_cpu_extended_v9_n16384** source=Lambda-cloud-GPU (file `data/lambda_exp_modern_hopfield_cpu_extended_v9_n16384_metrics_b373f71fcf964657ac611b9b7b925375.json`) elapsed_s=312.36. Per-cell: 3 seeds x 3 M values {65536=4N, 131072=8N, 262144=16N} = 9/9 cells unanimous success=true recall=1.0 max_M=262144=16N for all 3 seeds. EXACT MATCH to v295 local-CPU C9 reading (same anchor name; commit b116da9 + 7fc06b5). LABEL-HONEST. PROT-018 `_n16384` compliant. DUPLICATE-ANCHOR per [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]] anti-double-count rule -- NOT added to HONEST tally.
- **V3 G8_HARD_PASS adversarial_codebook_collision_defense_probe_v1_n4096** source=Lambda-cloud-GPU (file `data/lambda_exp_adversarial_codebook_collision_defense_probe_v1_n4096_metrics_350c53eae5594733bda43c9b88424037.json`) elapsed_s=1.81 GPU. Per-cell: 5 seeds {7,17,23,31,41} all ok=True; a_query_sim def=1.000 fp=0.000 unanimous; b_dist_check def=1.000 fp=1.000 unanimous (mathematically rejects all queries -- operationally broken non-discriminating gate; gate-design pathology). n_hp=1/2 correctly counts a_query_sim PASS + b_dist_check operationally FAIL. LABEL-HONEST -- verdict_msg accurately surfaces b_dist_check pathology in the same line. PROT-018 `_n4096` compliant.

### Cap_map decision (v296 -> v297; portfolio 22+36 UNCHANGED)

1. **R-PATH-D-NO-CEILING Path D production-default sub-row LIFT 0.85-0.95 -> 0.88-0.97** (+3% lower / +2% upper CONSERVATIVE; G7 EXTENDS U1's 16N x depth=50 unanimous to 32N x depth=50 unanimous at N=4096 K_paths=100; trivialization-on-K=100 caveat persists; cross-N + adversarial-construction-at-past-32N + cross-substrate caveats remain open).
2. **Modern Hopfield activation row 0.78-0.92 UNCHANGED at band-position** (qualitative tightening within band; hardware-codepath caveat CLOSED -- local-CPU + Lambda-GPU agree 9/9 cells unanimous; single-codebook BSC + actual-ceiling-past-16N caveats REMAIN OPEN; framework-reliability marginal +0.02 toward upper bound of band).
3. **Adversarial-vulnerabilities row TRANSITIONS RED -> YELLOW** with NEW SUB-ROW 'adversarial-defense candidate' at P-band 0.45-0.65 (first viable adversarial-defense at production parameters; novel-synthesis cap 0.65 per [[feedback-lit-scan-calibration-penalty]]). YELLOW scoped to 'codebook-collision attack-class HAS A VIABLE DEFENSE AT N=4096' per [[feedback-dont-overextend-theorems]] -- p4 edit-fact-traverse REMAINS RED at this commit pending separate defense.
4. **Substrate-product-feature row 89-98% UNCHANGED at band-position** with REGULATED-INDUSTRY DEPLOYMENT BLOCKER caveat-list MODIFIED to reflect partial-mitigation: codebook-collision attack-class now has viable-defense-at-N=4096; cross-N + p4 + adaptive-adversary + SDK-wiring gates remain before BLOCKER removal.

### Tallies

- HONEST: 274 (v296 basis) + 2 (V1 + V3) = 276 (V2 NOT double-counted; duplicate anchor of v295 C9 per anti-double-count rule).
- LABEL-VS-HONEST: 159 UNCHANGED (0 new catches in this batch).
- Portfolio: 22 + 36 UNCHANGED.

### Rescue sketches (PROT-004/006 cheapest-first; 3 rescue sets; 12 rescues; R1 0-compute APPLIED inline in all 3)

- **R-PATH-D-32N-EXTENSION**: R1 0-compute subsumption applied inline. R2 (CHEAP ~30min CPU or ~10min Lambda) Path D 48N-64N at N=4096 NOT-AUTO-DISPATCHED. R3 (MEDIUM ~60min GPU) Path D cross-N at 16N envelope at N=8192/N=16384 NOT-AUTO-DISPATCHED. R4 (CHEAP ~30min CPU) Path D adversarial-construction at past-16N NOT-AUTO-DISPATCHED.
- **R-MODERN-HOPFIELD-SECOND-SOURCE**: R1 0-compute applied inline. R2 (CHEAP ~10-15min Lambda) C9 M-sweep 32N at N=16384 BSC NOT-AUTO-DISPATCHED (carry-forward v295 follow-on). R3 (MEDIUM ~30min Lambda) C10 Kerdock cross-codebook at N=16384 (Lambda A10 24GB unblocks OOM that hit 8GB local-GPU) NOT-AUTO-DISPATCHED.
- **R-ADVERSARIAL-DEFENSE-FIRST-VIABLE**: R1 0-compute applied inline. R2 (CHEAP ~30min Lambda) a_query_sim cross-N at N=16384 BSC NOT-AUTO-DISPATCHED (HIGH PRIORITY follow-on). R3 (CHEAP ~30-45min Lambda) a_query_sim vs p4 edited-fact-traverse NOT-AUTO-DISPATCHED. R4 (MEDIUM ~60-90min GPU) adaptive-adversary stress NOT-AUTO-DISPATCHED. R5 (HIGH ~2-3h GPU) defense composition / ensemble DEFERRED.

### Top-3 follow-on decisions (NOT auto-dispatched per pause-flag hygiene + cheap-Lambda-spend-already-this-turn)

1. **a_query_sim defense cross-N replication at N=16384 BSC** (HIGH PRIORITY ~30min Lambda or ~1h local-CPU; R-ADVERSARIAL-DEFENSE-FIRST-VIABLE R2). First cross-N gate; if PASS lifts adversarial-defense sub-row 0.45-0.65 -> 0.55-0.75. Most-strategically-valuable next experiment in adversarial-defense capability lane.
2. **Path D 48N-64N envelope extension at N=4096 OR cross-N at 16N envelope at N=8192/N=16384** (MEDIUM PRIORITY ~10-30min Lambda OR ~30-60min CPU; R-PATH-D-32N-EXTENSION R2/R3). R3 cross-N is more-strategic-information-per-spend.
3. **C9 M-sweep 32N=524288 at N=16384 BSC + C10 Kerdock cross-codebook at N=16384** (MEDIUM PRIORITY ~10-15min Lambda each; R-MODERN-HOPFIELD-SECOND-SOURCE R2 + R3). Carry-forward from v295 top-3; second-source-corroboration strengthens case.

### PROT compliance

- PROT-004/006: 3 rescue sets cheapest-first; R1 0-compute APPLIED inline in all 3; R2/R3/R4 cheap-medium routed; R5 expensive deferred. 0 new closures.
- PROT-007: substrate_capability_map_history.md v297 row appended atomically. v277+v278 backlog carried forward.
- PROT-008: validator script ABSENT; carried forward. Annotation-+-LIFT change.
- PROT-009: cap_map.md (v297 entry) + substrate_capability_map_history.md (v297 row) + this strategy_decisions entry + visibility_decisions one-line + status_log entries staged atomically; 208th PROT-009 paired commit.
- PROT-018: 3 anchors spot-checked _n<N> vs config.N -- all CLEAN.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 performed; 3 label-honest; 0 catches; V1 under-claim observed not counted.
- [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]: V2 anti-double-count rule applied (duplicate of v295 C9 anchor); HONEST +2 not +3.
- [[feedback-cap-map-update-protocol]]: atomic single-batch commit; sub-agent push BLOCKED per [[feedback-subagent-permission-inheritance]]; commit hash surfaced.
- [[feedback-obey-user-pause-explicitly]]: pause-flag ABSENT; pipeline-pacing exp_dev dispatch SKIP (cheap-Lambda spend already this turn + GPU saturated + routing did not request refill).
- [[feedback-for-you-tab-primary-channel]]: 3 status_log entries with plain_language + importance.
- [[feedback-no-padding-experiments]]: CONSERVATIVE LIFTs; novel-synthesis cap on adversarial-defense sub-row.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-rescue-sketch-first-sequencing]]: R1 cheapest-first in all 3 sets.
- [[feedback-rehabilitation-after-rejection]]: 0 closures; YELLOW transition is mitigation-progress.
- [[feedback-dont-overextend-theorems]]: G8 YELLOW scoped to codebook-collision attack-class only.
- [[feedback-lit-scan-calibration-penalty]]: adversarial-defense sub-row CAPPED at 0.65 upper.
- [[feedback-strategy-shore-up-capabilities]]: 3 proactive band moves.
- [[feedback-pipeline-pacing]]: queue state checked; SKIP refill (GPU 16 + Lambda spend already).
- [[feedback-no-smoke]]: CONSERVATIVE bands; pathology DOCUMENTED.
- [[feedback-substrate-value-framing-matured-2026-05-26]]: V3 RED -> YELLOW maps to deletion-cert + compositionality-audit killer-feature wedge.

### Commit and push

Commit message: 'Cap map: v296 -> v297 BATCHED 3-VERDICT cheap-Lambda cloud corroboration event (V1 G7_HARD_PASS path_d_24n_32n_envelope_v1_n4096 R-PATH-D-NO-CEILING LIFT 0.85-0.95 -> 0.88-0.97 +3%/+2%; V2 C9_HARD_PASS modern_hopfield_cpu_extended_v9_n16384 SECOND-SOURCE Lambda-GPU corroboration anti-double-count framework-reliability +0.02; V3 G8_HARD_PASS adversarial_codebook_collision_defense_probe_v1_n4096 FIRST VIABLE adversarial-defense a_query_sim 1.000/0.000 at N=4096 5-seed adversarial-vulnerabilities row RED -> YELLOW new sub-row 0.45-0.65; HONEST 274 -> 276 +2; LABEL-VS-HONEST 159 UNCHANGED; portfolio 22+36 UNCHANGED; 208th PROT-009 paired commit) (2026-05-31)'.

Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main.
2026-05-31 v297->v298 ANNOTATION-ONLY: NEW ROW PP-9 'Reasoning amortization economics (LLM-derive-once + substrate-cache vs LLM-derive-each-query)' added to Section 5 Production positioning; 🔬 Research only P_deflated 0.55-0.70; testbed Tier 2b harness extension ~0-100 Anthropic API + ~2-3 weeks eng; routing file strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md closed -> routed_completed/; portfolio 22+36 -> 23+36 (+1); 209th PROT-009 paired commit; push deferred to orchestrator main thread.
## 2026-05-31 v298 -> v299 verdict_handler (210th PROT-009 paired commit)

BATCHED 3-VERDICT Lambda v2 cloud batch event. All 3 verdicts HARD_PASS LABEL-HONEST per Step 0 honest re-read.

### Step 0 honest re-read (mandatory)

- **V1 CROSS_N_HARD_PASS adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384** source=Lambda-cloud-GPU file `data/lambda_exp_adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384_metrics_11e98f7934ac43d896357bb5f26280ed.json` elapsed_s=28.86. Per-cell: 15/15 cells unanimous defense_rate=1.0 fp_rate=0.0 ok=True at N=16384 across M={4096,8192,12288} x 5 seeds {7,17,23,31,41} n_adv=32 n_leg=64. LABEL-HONEST -- matches per-cell numerics exactly; zero variance. PROT-018 `_n16384` compliant.
- **V2 P4_AQSIM_HARD_PASS adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096** source=Lambda-cloud-GPU file `data/lambda_exp_adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096_metrics_f72fefe0247e46cfbc749e0df27d0429.json` elapsed_s=1.74 GPU. Per-cell: 5/5 cells unanimous defense_rate=1.0 fp_rate=0.0 baseline_defense_rate=1.0 ok=True at N=4096 M=2048 seeds {7,17,23,31,41} n_edit=32. LABEL-HONEST. PROT-018 `_n4096` compliant. FIRST defense-generality HARD_PASS (a_query_sim defeats p2 codebook-collision AND p4 edited-fact-traverse).
- **V3 G7EXT_HARD_PASS path_d_48n_64n_envelope_v1_n4096** source=Lambda-cloud-GPU file `data/lambda_exp_path_d_48n_64n_envelope_v1_n4096_metrics_32eb7d0474254b5585630d7f2e0fcae2.json` elapsed_s=22.07. Per-cell: 12/12 cells unanimous accuracy=1.0 at N=4096 K_paths=100 M={196608=48N,262144=64N} x depth={30,50} x 3 seeds. LABEL-HONEST -- matches per-cell numerics exactly. PROT-018 `_n4096` compliant.

### Cap_map decision (v298 -> v299; portfolio 23+36 UNCHANGED)

1. **Adversarial-defense candidate sub-row LIFT 0.45-0.65 -> 0.55-0.75** (+10%/+10% CONSERVATIVE; closes single-N caveat via V1 cross-N replication + closes single-attack-pattern caveat via V2 defense-generality; adaptive-adversary + SDK-wiring + cross-substrate + b_dist_check companion still operationally-broken caveats REMAIN; novel-synthesis upper cap 0.75 short of 0.80 per [[feedback-lit-scan-calibration-penalty]]).
2. **Adversarial-vulnerabilities row YELLOW UNCHANGED at row-state symbol** (sub-row band LIFTed within YELLOW; row promotion to GREEN gated by adaptive-adversary + SDK-wiring per [[feedback-dont-overextend-theorems]]).
3. **R-PATH-D-NO-CEILING Path D production-default sub-row LIFT 0.88-0.97 -> 0.92-0.98** (+4%/+1% CONSERVATIVE; combined U1(16N depth=50) + G7(24N-32N) + G7EXT(48N-64N) = 4 unanimous envelope-extensions at N=4096 K=100; cross-N + adversarial-construction + cross-substrate + K>100 trivialization caveats REMAIN).
4. **Substrate-product-feature row 89-98% UNCHANGED at band-position** with REGULATED-INDUSTRY DEPLOYMENT BLOCKER caveat-list MODIFIED to reflect 2-of-5 BLOCKER caveats CLOSED: codebook-collision attack-class CROSS-N DEFENSE-VIABLE (was N=4096-only); edit-fact-traverse attack-class DEFENSE-VIABLE (was untested). Remaining: adaptive-adversary + SDK-wiring + cross-substrate.
5. **PP-8 substrate-LLM deep-integration row ANNOTATION-only (no band move)**: D7 edit-log-replay defense engineering item carry-forward from v292/v295/v296 top-3 follow-on SUPERSEDED by V2 defense-generality (a_query_sim subsumes the adversarial pattern D7 was designed to defend). D7 DOWNGRADED REQUIRED -> OPTIONAL-FOLLOW-ON; testbed P6 "implement D7" engineering item bandwidth re-allocates to PP-8 Week 1 OR PP-5 latency OR PP-9 Tier 2b harness.

### Tallies

- HONEST: 276 (v297 basis) + 3 (V1 + V2 + V3 all label-honest; no anti-double-count rule applies because all 3 are NEW anchors) = **279**.
- LABEL-VS-HONEST: **159 UNCHANGED** (zero new catches; all 3 labels match per-cell numerics).
- Portfolio: 23 + 36 UNCHANGED.

### Rescue sketches (PROT-004/006 cheapest-first; 3 rescue sets; 13 rescues; R1 0-compute APPLIED inline in all 3)

- **R-ADVERSARIAL-DEFENSE-CROSS-N-GENERALITY**: R1 0-compute subsumption APPLIED inline. R2 (CHEAP ~30-45min Lambda) a_query_sim vs next adversarial attack-class NOT-AUTO-DISPATCHED. R3 (MEDIUM ~60-90min GPU) adaptive-adversary stress NOT-AUTO-DISPATCHED (HIGH PRIORITY; closes most-strategically-valuable remaining caveat). R4 (MEDIUM ~2-3h GPU + eng) SDK-wiring production-path integration NOT-AUTO-DISPATCHED. R5 (HIGH ~3-5h) defense composition / ensemble DEFERRED.
- **R-PATH-D-PAST-64N**: R1 0-compute APPLIED inline. R2 (CHEAP ~30min Lambda) Path D 96N-128N at N=4096 K=100 NOT-AUTO-DISPATCHED. R3 (MEDIUM ~60-90min GPU) Path D cross-N at 32N envelope at N=8192/16384 NOT-AUTO-DISPATCHED (HIGH PRIORITY; closes cross-N caveat). R4 (CHEAP ~30min CPU) Path D adversarial-construction at past-32N NOT-AUTO-DISPATCHED. R5 (MEDIUM ~60min) Path D at K_paths=200/500/1000 NOT-AUTO-DISPATCHED (closes K=100 trivialization caveat).
- **R-PP-8-D7-SUPERSEDED**: R1 0-compute subsumption APPLIED inline (PP-8 research-note column annotation). R2 (NO-COMPUTE routing-only) D7 engineering bandwidth re-allocation to PP-8 Week 1 OR PP-5 OR PP-9 deferred to orchestrator strategy thread. R3 (NO-COMPUTE documentation-only) D7 standalone cap_map representation check -- D7 appears only in carry-forward rescue sketches in v290+v295+v296; no standalone row mutation required; APPLIED inline as documentation.

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched per pause-flag-absent-but-cheap-Lambda-spend-already-this-turn)

1. **a_query_sim defense vs adaptive-adversary at N=4096** (HIGH PRIORITY ~60-90min GPU; R-ADVERSARIAL-DEFENSE-CROSS-N-GENERALITY R3). Closes most-strategically-valuable remaining caveat on adversarial-defense sub-row. If PASS sub-row LIFTs further 0.55-0.75 -> 0.65-0.85 candidate; adversarial-vulnerabilities row YELLOW -> GREEN promotion candidate (gated additionally by SDK-wiring closure).
2. **Path D cross-N at 32N envelope at N=8192 + N=16384** (MEDIUM PRIORITY ~60-90min GPU; R-PATH-D-PAST-64N R3). Closes cross-N caveat on Path D production-default sub-row. If PASS LIFTs further 0.92-0.98 -> 0.93-0.99 candidate; if FAIL locates cross-N ceiling (also useful).
3. **PP-8 Week 1 feasibility smoke OR PP-5 latency-budget closure** (MEDIUM PRIORITY ~1-2 weeks engineering). With D7 SUPERSEDED bandwidth re-allocates; orchestrator strategy decision required.

### PROT compliance

- PROT-004/006: 3 rescue sets cheapest-first; 13 rescues; R1 0-compute APPLIED inline in all 3; R2-R5 cheap-medium-high routed; 0 new closures.
- PROT-007: substrate_capability_map_history.md v299 row appended atomically. v277+v278 backlog carried forward.
- PROT-008: validator script ABSENT; carried forward. Annotation-+-LIFT change; no portfolio state regression risk.
- PROT-009: cap_map.md (v299 entry) + substrate_capability_map_history.md (v299 row) + this strategy_decisions entry + visibility_decisions one-line + 3 status_log entries staged atomically; 210th PROT-009 paired commit.
- PROT-018: 3 anchors spot-checked _n<N> vs config.N -- all CLEAN. V1 `_n16384` matches 16384; V2 `_n4096` matches 4096; V3 `_n4096` matches 4096.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 performed on all 3; 3 label-honest; 0 catches.
- [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]: 3 NEW anchors; no anti-double-count rule applies; HONEST +3.
- [[feedback-cap-map-update-protocol]]: atomic single-batch commit; sub-agent push BLOCKED per [[feedback-subagent-permission-inheritance]]; commit hash surfaced.
- [[feedback-obey-user-pause-explicitly]]: pause-flag CHECKED ABSENT (`data/orchestrator_paused.flag` does not exist); pipeline-pacing exp_dev dispatch SKIP (cheap-Lambda spend already this turn $0.42 batch / $1.82 cumulative + routing-file did not request refill).
- [[feedback-for-you-tab-primary-channel]]: 3 status_log entries with plain_language + importance (1 HIGH cross-N + 1 CRITICAL defense-generality + 1 HIGH Path D 64N).
- [[feedback-no-padding-experiments]]: CONSERVATIVE LIFTs (+10%/+10% vs +15%; +4%/+1% vs +5%/+2%); novel-synthesis cap on adversarial-defense sub-row at 0.75 not 0.80.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-rescue-sketch-first-sequencing]]: R1 cheapest-first in all 3 sets.
- [[feedback-rehabilitation-after-rejection]]: 0 closures; both LIFTs are mitigation-progress.
- [[feedback-dont-overextend-theorems]]: YELLOW UNCHANGED at row-state (only sub-row band LIFTed); D7-supersession scoped to defense-engineering-motivation not all D7-flavored engineering.
- [[feedback-lit-scan-calibration-penalty]]: Adversarial-defense sub-row upper bound CAPPED at 0.75 not 0.80.
- [[feedback-strategy-shore-up-capabilities]]: 2 proactive band-LIFTs + 1 engineering-roadmap reduction triggered by verdict-arrival.
- [[feedback-pipeline-pacing]]: queue state checked; SKIP refill (Lambda spend already + routing did not request).
- [[feedback-no-smoke]]: CONSERVATIVE bands; b_dist_check companion still operationally-broken NOT glossed over; +1% upper on Path D not +2% because cross-N untested at 64N.
- [[feedback-substrate-value-framing-matured-2026-05-26]]: V1+V2 + V3 all map to substrate-product-killer-features (deletion-cert + compositionality-audit-API + Path-D-as-production-default); plumbing-over-physics framing.

### Commit and push

Commit message: 'Cap map: v298 -> v299 BATCHED 3-VERDICT Lambda v2 cloud cross-N defense + defense-generality + Path D past 64N (V1 CROSS_N_HARD_PASS adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384 15/15 cells unanimous 1.000-defense-0.000-fp at N=16384 CLOSES single-N caveat; V2 P4_AQSIM_HARD_PASS adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096 5/5 cells unanimous FIRST defense-generality HARD_PASS a_query_sim defeats p2 AND p4 D7-engineering-item SUPERSEDED; V3 G7EXT_HARD_PASS path_d_48n_64n_envelope_v1_n4096 12/12 cells unanimous at 48N-64N x depth=50 N=4096 K=100 combined-with-U1-G7 Path D no-ceiling 16N-64N; Adversarial-defense sub-row LIFT 0.45-0.65 -> 0.55-0.75 +10%/+10% CONSERVATIVE; Path D sub-row LIFT 0.88-0.97 -> 0.92-0.98 +4%/+1% CONSERVATIVE; Adversarial-vulnerabilities row YELLOW UNCHANGED at row-state; Substrate-product-feature row 89-98% UNCHANGED 2-of-5-BLOCKER-caveats-CLOSED; PP-8 D7 engineering item SUPERSEDED; HONEST 276 -> 279 +3; LABEL-VS-HONEST 159 UNCHANGED; portfolio 23+36 UNCHANGED; 3 rescue sets 13 rescues R1 0-compute inline; 3 status_log entries 1 HIGH + 1 CRITICAL + 1 HIGH; Lambda batch $0.42 cumulative $1.82 cleanup-verified; pipeline-pacing exp_dev NOT dispatched; 210th PROT-009 paired commit) (2026-05-31)'.

Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main.


## v299 -> v300 BATCHED 2-VERDICT CPU overnight wave 1 INFRASTRUCTURE-FAILURE batch (verdict_handler 211th PROT-009 paired commit) -- 2026-05-31

**Context.** Overnight CPU wave 1 batch of 2 verdicts processed by verdict_handler. Pause-flag CHECKED ABSENT. GPU queue 17 pending+running, CPU queue 7 pending+running. Reliability-recalc CANDIDATE escalation on V1 EVALUATED and RESOLVED NO-CAP-MAP-LIFT-NO-CLOSURE because both verdicts classified as INFRASTRUCTURE-FAILURE rather than science conclusions.

### Step 0 honest re-read summary -- 2 LABEL-VS-HONEST catches (#160 + #161, both under existing sub-flavor #157 LOCAL_SMOKE_ARTIFACT_AS_PRODUCTION_VERDICT variant; no NEW sub-flavor)

### V1 -- modern_hopfield_cpu_extended_v10_n16384 -- TIMEOUT-INCONCLUSIVE LABEL-VS-HONEST #160

**Anchor.** `modern_hopfield_cpu_extended_v10_n16384` labeled `V10_MIDDLE_BAND` "CEILING_AT_OR_BELOW_20N: constructed=1/1 max_M_per_seed=[20480]" `_source: local` (bridge returned local-fallback; remote SSH for metrics.json failed because the FULL run never wrote one).

**Honest reading.** Local metrics is SMOKE artifact (`smoke: true`, N=1024, seeds=[17], M_sweep=[20480, 32768], elapsed_s=1.1) -- the label references smoke-N=1024 NOT the FULL N=16384 production run. Remote experiment log `data/remote_cpu_queue/modern_hopfield_cpu_extended_v10_n16384.log` shows the ACTUAL FULL run: smoke=False N=16384 M_sweep=[327680=20N, 524288=32N, 1048576=64N] 5-seed; only ONE cell completed (`[seed=7] M=327680 recall=1.0 elapsed=20501.61s` = 5.7h CPU) before PROT-019 21600s timeout exhausted by per-cell wall budget; remaining 14 cells (seed=7 at M=32N/64N + seeds 17/23/31/41 at all 3 M-values) NEVER attempted; no exp metrics.json written by FULL because run was killed before producing cell-aggregation output. Failure mode: **TIMEOUT INFRASTRUCTURE FAILURE** (NOT OOM, NOT HARD_FAIL with cliff data, NOT mixed). Single completed cell M=20N seed=7 recall=1.0 = incidental NEW EVIDENCE extending v295+v297 unanimous M=4N/8N/16N at N=16384 BSC to a 4th M-value at single-seed; cliff/ceiling location remains UNKNOWN past 20N.

LABEL-VS-HONEST catch #160 sub-flavor #157 variant: smoke-artifact-via-local-fallback misleads `CEILING_AT_OR_BELOW_20N` label (label references smoke-N=1024 NOT FULL-N=16384).

**Decision.** ANNOTATION ONLY on Modern Hopfield activation regime row; P-band 0.78-0.92 UNCHANGED. NO LIFT NO CLOSURE per honest re-read TIMEOUT-INFRA-FAILURE-not-science. Caveats column updated: M=20N=327680 at N=16384 BSC seed=7 recall=1.0 single-cell incidental positive added; CPU per-cell-wall-budget at M=20N+ infeasible for 5-seed sweep at N=16384 within PROT-019; future cliff-locator runs at M>=20N at N=16384 BSC redirect to GPU.

### V2 -- substrate_state_compression_v3_n8192 -- C3V3_INFRA_FAILURE LABEL-VS-HONEST #161

**Anchor.** `substrate_state_compression_v3_n8192` labeled `C3V3_INCONCLUSIVE` "no cells" `_source: remote` elapsed_s=0.0 cells=[]. M=4096 n_probe=100 seeds=[7,17,23,31,41]. Smoke selftest PASSED (`bits8: comp=4.00x retr=1.000 kfs=True`) but FULL did not.

**Honest reading.** Remote experiment log shows ALL 5 SEEDS failed identically at experiment INIT: `seed=X FAILED: N=8192 requires even log2(N) for MM construction (got n_log2=13)`. Root cause: MM-construction harness REQUIRES log2(N) to be EVEN; log2(8192)=13 ODD REJECTED. log2(4096)=12 EVEN ACCEPTED (which is why C3 v2 at N=4096 ran fine v295). log2(16384)=14 EVEN ACCEPTABLE for next attempt (v4 already in CPU queue position 8). Smoke selftest PASSED because smoke uses DIFFERENT code-path or smoke-N=1024 (log2=10 EVEN) -- smoke-vs-FULL coverage gap (post-compaction brief Section 3k violation candidate).

LABEL-VS-HONEST catch #161 sub-flavor #157 variant: smoke-artifact-passes-FULL-infra-rejects-INCONCLUSIVE-label-does-not-convey-failure-mode; failure is INFRA-not-experimental-ambiguity.

**Decision.** ANNOTATION ONLY on PP-2 storage efficiency row; P-band 0.65-0.75 UNCHANGED. NO LIFT NO CLOSURE. Cross-N validation REDIRECT to v4 at N=16384 already pending CPU queue position 8. PP-2 cross-N evidence count UNCHANGED (still 1 N-point at N=4096 v2). Smoke harness GAP routing: c3_smoke remedy = add n_log2 even-parity pre-check mirroring FULL MM-constraint; engineering item for exp_dev next cycle.

### Cap_map changes (v299 -> v300)

1. **Modern Hopfield activation regime at large N row -- ANNOTATION ONLY.** P-band 0.78-0.92 UNCHANGED. Single-cell M=20N=327680 at N=16384 BSC seed=7 recall=1.0 added as evidence point; CPU per-cell wall budget past 20N at N=16384 BSC infeasible for 5-seed sweep within PROT-019; cliff-locator GPU redirect documented.
2. **PP-2 storage efficiency row -- ANNOTATION ONLY.** P-band 0.65-0.75 UNCHANGED. Cross-N validation at N=8192 INFRA-BLOCKED by MM-constraint log2(N)-must-be-even; redirected to v4 N=16384 already in CPU queue.
3. **Smoke-coverage GAP annotation** -- engineering item NOT a cap_map LIFT/closure; remedy routed to exp_dev next cycle.

### Framework reliability bands (v299 -> v300)

ALL UNCHANGED. Both verdicts INFRA-FAILURE; neither produces a science conclusion that would move any band. Per [[feedback-dont-overextend-theorems]] resist treating infrastructure failures as capability failures.

### Honest / label-vs-honest tallies

- HONEST: 279 + 2 = **281**
- LABEL-VS-HONEST: 159 + 2 = **161** (both under existing sub-flavor #157 LOCAL_SMOKE_ARTIFACT_AS_PRODUCTION_VERDICT variant; NO new sub-flavor created)

### Portfolio

23 + 36 -> **23 + 36 UNCHANGED** (no row additions, no closures).

### Rescue sketches (PROT-004/006 cheapest-first; 2 rescue sets; 10 rescues; R1 0-compute APPLIED inline in both)

- **R-V1-CLIFF-LOCATOR-GPU-REDIRECT**: R1 inline subsumption applied; R2 GPU cliff-locator at M={20N,24N,32N} at N=16384 BSC 3-seed routed; R3 sparse-W cliff-locator routed; R4 M-sub-sampling cliff-locator routed; R5 full GPU 5-seed deferred.
- **R-V2-MM-CONSTRAINT-N-REDIRECT**: R1 inline subsumption applied (v4 at N=16384 ALREADY in CPU queue position 8); R2 cancel v3 N=8192 retries recommended; R3 c3_smoke harness MM-constraint coverage remedy routed; R4 active_protocols.md documentation routed; R5 alternative non-MM harness deferred.

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched)

1. **GPU cliff-locator at M={20N, 24N, 32N} at N=16384 BSC 3-seed** (HIGH PRIORITY; ~30-60min GPU). Closes most-strategically-valuable Modern Hopfield M-ceiling location caveat; CPU path EXHAUSTED at this N regime.
2. **c3_smoke harness MM-constraint coverage remedy** (LOW PRIORITY engineering; ~30-60min). Prevents future N=8192-style infra-reject.
3. **Continue PP-2 cross-N via existing v4 at N=16384 already in CPU queue** (NO ACTION; routing-only). Auto-runs at position 8.

### PROT compliance (v299 -> v300)

- PROT-004/006: 2 rescue sets cheapest-first 10 rescues R1 0-compute applied inline both; R2/R3/R4 cheap-medium routed; R5 expensive deferred. No capability-row closures.
- PROT-007: substrate_capability_map_history.md v300 row appended atomically. v277+v278 backlog carried forward.
- PROT-008: validator ABSENT carried forward. Annotation-only changes no portfolio regression risk.
- PROT-009: cap_map.md (v300) + history.md (v300 row) + this strategy_decisions entry + visibility_decisions one-line + 2 status_log entries staged atomically; 211th PROT-009 paired commit.
- PROT-018: 2 anchors spot-checked _n<N> suffix vs config.N: V1 `_n16384` matches 16384 compliant. V2 `_n8192` matches 8192 compliant (infra-failure is SEPARATE MM-constraint not PROT-018 N-mismatch).
- PROT-019: V1 first-observed CPU timeout-exhaustion at N=16384 BSC cliff-locator at 21600s floor exactly; informs future per-experiment `--timeout` formulas (5.7h-per-cell CPU wall at M=20N at N=16384 BSC documented bound).

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 mandatory via REMOTE SSH log inspection (NOT just local metrics.json which produced misleading "CEILING_AT_OR_BELOW_20N" verdict for V1 at smoke-N=1024). 2 catches under existing sub-flavor #157 variant; over-claimed label NOT propagated to cap_map.
- [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]: V1 bridge _source=local triggered manual remote SSH inspection of data/exp_<name>/ and data/remote_cpu_queue/<name>.log. V2 bridge _source=remote sufficient.
- [[feedback-cap-map-update-protocol]]: atomic single-batch commit; sub-agent push BLOCKED; commit hash surfaced for main-thread push.
- [[feedback-obey-user-pause-explicitly]]: pause-flag CHECKED ABSENT; pipeline-pacing exp_dev SKIP (queue 17+7 healthy + GPU saturated + no routing-file refill request).
- [[feedback-for-you-tab-primary-channel]]: 2 status_log entries with plain_language + importance (1 MEDIUM TIMEOUT-INCONCLUSIVE + 1 MEDIUM INFRA-FAILURE).
- [[feedback-no-padding-experiments]]: 0 follow-on auto-dispatches.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-rescue-sketch-first-sequencing]]: R1 cheapest-first 0-compute APPLIED inline in BOTH rescue sets.
- [[feedback-rehabilitation-after-rejection]]: 0 capability-row closures; both INFRA-FAILURES with clear infrastructure remedies; broader scientific hypotheses REMAIN UNTESTED at failing-N regimes.
- [[feedback-dont-overextend-theorems]]: V1 TIMEOUT scoped to per-cell-wall-budget infeasibility NOT to ceiling location; V2 INFRA scoped to MM-constraint incompatibility NOT to PP-2 closure at N=8192.
- [[feedback-pipeline-pacing]]: queue state CHECKED healthy; exp_dev SKIP.
- [[feedback-no-smoke]]: brutal honesty -- V1 local-fallback CALLED OUT as smoke artifact; V2 smoke-vs-FULL gap CALLED OUT as PROT-violation candidate; M=20N single-cell positive NOT inflated to "cliff confirmed".
- [[feedback-no-label-vs-honest-anchor-names]]: 2 anchors PROT-018 spot-check both CLEAN.
- [[feedback-strategy-spec-formula-selftests]]: V2 reveals c3_smoke selftest DID NOT cover MM-constraint pre-check; selftests should cover infrastructure-feasibility AT THE PRODUCTION N before smoke PASS.

### Commit and push

Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

Commit message: see cap_map v300 entry verbatim.

## v300 -> v301 @ SINGLE-VERDICT V2 24h sustained_workload baseline HARD_PASS FIRST 24h SUSTAINED-RUNTIME VALIDATION AT PRODUCTION SCOPE (verdict_handler 212th PROT-009 paired commit; reliability-recalc EVENT on production-readiness narrative)

**Trigger.** SINGLE VERDICT V2 24h sustained_workload completed 2026-05-31T21:15:39 wall_s=86668 (24.07h GPU). Pre-registered as long-run reliability characterization at N=4096 M=2048 24000 mixed-CRUD+Path-D ops with hourly checkpoint + KF-spot every 4h + audit verify every 1000 ops. Pause-flag CHECKED ACTIVE (`data/orchestrator_paused.flag` EXISTS). Queue depth 6 GPU + 5 remote_cpu + 0 local_cpu pending+running.

**Step 0 honest re-read (MANDATORY; remote-first per PROT N-mismatch-ceiling-fix + verdict-msg honest-reread).**

LOCAL `data/exp_sustained_workload_24h_baseline_v1_n4096/metrics.json` was a STALE PRE-SHIP SMOKE artifact (elapsed_s=60.99 ops=1000 N=512 M_initial=256 hourly_records=3 30s-proxy-hours). Bridge `get_metrics(_n4096)` returned `_source: remote` but the cached content was the stale smoke (cache-staleness on the metrics-bridge for this anchor). Manual SCP from `marsh@home:C:/dev/hd-instrument/data/exp_sustained_workload_24h_baseline_v1_n4096/metrics.json` (LastWriteTime 2026-05-31 21:15:38) returned the AUTHORITATIVE FULL-RUN payload.

Authoritative FULL-RUN metrics:
- verdict `SUSTAINED_HARD_PASS`; verdict_msg `PRODUCTION_READY: ops=24000 throughput_drift=0.059 rss_growth=1.00x kf2_drift=0.0 kf1_drift=0.0 cert_valid=True w_norm_drift=1.001`
- elapsed_s=86660.13 = 24.07h (matches dispatch context wall_s=86668 within 8s); N=4096 M_initial=2048 (matches PROT-018 `_n4096` suffix binding); total_ops_done=24000 of 24000 target (~1000 ops/hour as designed)
- KF-2 max isolation = 0.0 at ALL 6 spot checks (op 3991 @ 4.0h, op 7992 @ 8.0h, op 11993 @ 12.0h, op 15993 @ 16.0h, op 19934 @ 20.0h, op 23933 @ 24.0h). KF-1 spurious firing rate = 0.0 at ALL 6 spot checks. Zero accuracy degradation across 24h.
- W L2 norm: init 45.234 -> final 45.287 = drift_ratio 1.0011 (0.11% over 24h; essentially zero W-matrix drift)
- Cert chain: 2408 links accumulated, valid=True, 24/24 audit-verify samples valid, audit_full_corruptions=0
- GPU memory: stable at 136.12 MB across all 24 hourly records (zero leak)
- Heap: 0.79 MB -> 3.74 MB across 24h (3.0 MB linear growth; absolute tiny; mem_growth_rss_ratio=1.00; not a real leak)
- Throughput: baseline 0.2951 ops/s -> final 0.2778 ops/s = 5.86% drift; per-hour throughput stable 0.2778+/-0.005 ops/s for 23 of 24 hours
- Latency: hourly lat_mean_ms typically 1-10 ms with p99 15-50 ms; ONE outlier hour-17 (lat_mean=292ms lat_p99=4636ms thpt-dip-to-0.2613) recovered immediately to lat_mean=1.26ms in hour-18 (likely transient GPU contention or background process; flagged but isolated single-hour)
- codebook_usage_hist_drift_l1 = 0.91 (substantial codebook-usage shift over 24h workload diversity; expected behavior not a defect)
- crashed=False, crash_msg=""

Label `SUSTAINED_HARD_PASS PRODUCTION_READY` is HONEST. Every numeric in verdict_msg matches the FULL-run summary exactly. Per-cell (hourly) re-read confirms KF-1/KF-2 zero-drift unanimously at all 6 spot checks; W norm drift 0.11% over 24h; cert chain validated 24/24 audit samples. ONE caveat raised honestly above (hour-17 single-hour latency spike) does NOT contradict label; threshold criteria all clear.

Label-vs-honest cumulative: 161 UNCHANGED (this verdict is LABEL-HONEST; the metrics-bridge cache-staleness for this anchor is a separate INFRASTRUCTURE issue not a label-vs-honest catch).

**HONEST tally: 281 + 1 = 282.**

### Cap_map changes (v300 -> v301)

1. **NEW capability row added to CAN section (1. Memory primitives -> Robustness / scaling subsection): "24h sustained-runtime reliability at production scope (N=4096 M=2048 24000-op mixed-CRUD+Path-D workload)"** -- State Validated (single FULL run; first-of-kind 24h validation). Evidence: V2 24h sustained_workload_24h_baseline_v1_n4096 SUSTAINED_HARD_PASS 2026-05-31 elapsed_s=86660 throughput_drift=5.86% W-norm-drift=0.11% KF-2 zero-iso 6/6 spot-checks KF-1 zero-fp 6/6 spot-checks cert-chain 2408 links validated 24/24 audit samples zero corruptions GPU-mem stable 136 MB heap +3 MB. Caveats: single seed (V2 design was single-seed long-run; multi-seed 24h would be ~120h aggregate -- DEFERRED unless reliability concern); single-N (N=4096 only); one transient hour-17 latency spike (lat_p99=4636ms) recovered next hour (root cause undiagnosed; isolated). Product implication: "substrate maintains accuracy + audit integrity + zero W drift across continuous 24h production workload" -- enables production-readiness positioning that was previously theoretical.

2. **PP-3 audit-trail design + rotation strategy row -- INPUT DATA NOW AVAILABLE (no band move, DEPENDENCY UNBLOCKED).** V2 24h workload was the load-bearing prerequisite for PP-3 design (per PP-3 row caveat `(d) V2 24h workload output is input data for design`). Cert chain growth measured: 2408 links over 24000 ops = ~0.10 links/op = ~100 links per 1000 ops. Hourly checkpoint: chain_len went 64 (hour-0) -> 119 (hour-1) -> ~2408 (hour-24). Linear growth = ~100 links/hour at this workload mix. PP-3 input-data dependency CLOSED; row band 0.55-0.70 UNCHANGED until PP-3 design drill ships; caveat `(d) V2 24h workload output is input data for design` ANNOTATED to "input data NOW AVAILABLE; design drill remains ~2 weeks CPU-bound; M1+M2 substrate selection still gating".

3. **PP-2 storage efficiency row -- EMPIRICAL INPUT EXTENDED (no band move).** V2 provides actual production-scale storage observations: GPU stable 136 MB N=4096 M=2048; heap +3 MB over 24h; cert chain 2408 links (link-size known from substrate state-format); W matrix 45.234 L2 stable. Combined with v295 C6 store-footprint (N=4096 CPU 70-160 MB M=128-2048) + v300 v3 cross-N path (N=16384 pending v4): PP-2 row band 0.65-0.75 UNCHANGED (V2 evidence reinforces single-N N=4096 footprint model; cross-N still gated on v4 N=16384 verdict).

4. **Substrate-product-feature row 89-98% UNCHANGED at band-position** with PRODUCTION-READY ANNOTATION ADDED. Previous BLOCKER caveat list (adversarial-defense partial-mitigation from v299) is unaffected. NEW POSITIVE ANNOTATION: "24h sustained-runtime reliability VALIDATED at N=4096 M=2048 24000-op workload (V2 SUSTAINED_HARD_PASS 2026-05-31): KF-1/KF-2 zero drift across 6 spot checks; cert chain validated 24/24 samples zero corruptions; W matrix drift 0.11%; GPU memory stable; one transient hour-17 latency spike recovered immediately. Production-readiness narrative ANCHORED EMPIRICALLY at 24h continuous runtime; was previously theoretical." Row band STAYS 89-98% (band already includes operational-reliability framework; this is empirical-corroboration not framework-LIFT). CONSERVATIVE no-LIFT per [[feedback-no-padding-experiments]]: 24h single-seed single-N validation is corroboration-of-existing-framework not a NEW capability that the band underrepresented.

5. **KF-2 deletion-cert row -- 24h ROBUSTNESS ANNOTATION (no band move).** KF-2 row remains LEADING; ADD annotation: "24h sustained-runtime KF-2 zero-isolation drift confirmed at 6 spot checks across 24h continuous workload (V2 2026-05-31); KF-2 mechanism is RUNTIME-STABLE not just initialization-stable."

6. **KF-1 hallucination-detection row -- 24h ROBUSTNESS ANNOTATION (no band move).** KF-1 row band 0.65-0.80 UNCHANGED; ADD annotation: "24h sustained-runtime KF-1 zero-spurious-firing-rate confirmed at 6 spot checks across 24h continuous workload (V2 2026-05-31); KF-1 mechanism is RUNTIME-STABLE."

7. **7-day sustained workload cloud-routing candidate UPDATED.** v292 standing principle listed 7-day sustained workload as cloud-warranted "only if local 48h validates clean" (~$300-500). V2 24h CLEAN locally satisfies the partial predicate for 48h next-step (local; not cloud), not 7-day cloud yet. Cloud-routing-list ANNOTATION: "V2 24h CLEAN 2026-05-31; 48h local validation is now the sequenced next gate (NOT auto-dispatched; pause-flag ACTIVE; orchestrator decides timing); 7-day cloud routing still gated on 48h local CLEAN."

### Framework reliability bands (v300 -> v301)

ALL existing framework reliability bands UNCHANGED at band-position. V2 is empirical corroboration of OPERATIONAL framework (substrate maintains accuracy + audit + W under continuous workload); not a NEW framework class or NEW mechanism. CONSERVATIVE no-LIFT per [[feedback-no-padding-experiments]]. The NEW row "24h sustained-runtime reliability" is a NEW capability anchor (its own row at Validated single-seed single-N) NOT a band-LIFT on an existing reliability band.

### Portfolio

23 + 36 -> **24 + 36** (+1 NEW capability row "24h sustained-runtime reliability at production scope" in CAN-Robustness/scaling subsection). HONEST 281 -> 282 (+1; V2 is LABEL-HONEST). LABEL-VS-HONEST 161 UNCHANGED.

### Rescue sketches (PROT-004/006 cheapest-first per [[feedback-rescue-sketch-first-sequencing]]) -- NOT TRIGGERED

V2 is a HARD_PASS HARD-EVIDENCE single-seed single-N validation. No row closures. No rescue sketches required by PROT-004/006. Forward-test extension sketches (cheap-first-sequenced, NOT auto-dispatched per pause-flag-ACTIVE):

**R-V2-SUSTAINED-RUNTIME-EXTENSIONS (extending 24h single-seed single-N to multi-seed + cross-N + cross-workload):**
- R1 (CHEAPEST, 0-compute) -- Subsumption: "V2 24h N=4096 M=2048 single-seed single-N SUSTAINED_HARD_PASS CLEAN; NEW capability row ADDED Validated; production-readiness narrative ANCHORED EMPIRICALLY; PP-3 input data dependency CLOSED; CONSERVATIVE no-band-LIFT on existing framework reliability." APPLIED inline above.
- R2 (CHEAPEST, ~5 min documentation) -- Document hour-17 latency-spike root-cause investigation as engineering follow-on: was this GPU-contention from a colocated process, a substrate-internal pathology, or a measurement artifact? Inspect remote machine logs for 2026-05-31 hour-17 window. NOT-AUTO-DISPATCHED (engineering item; pause-flag ACTIVE; not blocking).
- R3 (CHEAP, ~30-60min CPU) -- Multi-seed 24h reliability via SHORTER duration (e.g., 4h x 5 seeds = ~20h aggregate at N=4096 M=2048) for variance characterization on throughput + cert-chain growth + W drift; pre-reg HP all 5 seeds throughput_drift <= 0.10 and KF-2/KF-1 drift = 0.0 at all spot checks. NOT-AUTO-DISPATCHED (gated on pause-flag).
- R4 (MEDIUM, ~24h local-GPU) -- 24h sustained workload at cross-N N=8192 M=4096 OR N=16384 M=8192 to verify the production-readiness claim is N-scaling-independent; pre-reg HP same thresholds at higher-N. NOT-AUTO-DISPATCHED (pause-flag; 24h local GPU monopolizes substrate).
- R5 (MEDIUM, ~48h local-GPU) -- 48h local sustained workload as the next gate toward 7-day cloud-routing candidate (v292 cloud-routing-discipline list). NOT-AUTO-DISPATCHED (pause-flag).
- R6 (HIGH-COST, ~7-day cloud-GPU ~$300-500) -- 7-day sustained workload cloud-routing candidate per v292 standing principle. DEFERRED until 48h local CLEAN (R5).

**R-PP-3-AUDIT-ROTATION-SUBSTRATE-DESIGN (PP-3 input-data dependency CLOSED; design drill now ungated on V2):**
- R1 (CHEAPEST, 0-compute) -- Subsumption: "V2 cert-chain growth measured at 2408 links over 24000 ops = ~100 links/hour at production-scale mixed-CRUD+Path-D workload; PP-3 input-data dependency CLOSED; PP-3 design drill ungated; ~2 weeks CPU-bound." APPLIED inline above (PP-3 row caveat annotation).
- R2 (CHEAP, routing-only) -- File `strategy_request_to_research_pp_3_audit_rotation_design_2026-05-31.md` request to research for PP-3 audit-rotation-strategy design drill using V2 24h cert-chain trajectory data (links/hour growth rate + cert-link payload size + GDPR/HIPAA/SOC2 retention windows). NOT-AUTO-DISPATCHED (per pause-flag ACTIVE + filed-not-dispatched policy).

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched per pause-flag ACTIVE)

1. **Hour-17 latency-spike investigation** (LOW PRIORITY engineering; ~30-60min). One-hour outlier in an otherwise clean 24h run; recovered immediately. Root-cause TBD: GPU contention from colocated process / substrate-internal pathology / measurement artifact. Investigate remote-machine logs for the 2026-05-31 hour-17 window before next 24h+ run.

2. **PP-3 audit-rotation design drill -- INPUT DATA NOW AVAILABLE** (HIGH PRIORITY research; ~2 weeks CPU). Filed as R-PP-3-AUDIT-ROTATION-SUBSTRATE-DESIGN R2 routing-only above. V2 cert-chain growth (~100 links/hour at production-scale mixed workload) is the empirical input PP-3 was waiting on. PP-3 row band 0.55-0.70 will move based on design-drill outcome (not auto-dispatched per pause-flag).

3. **48h local sustained workload (R5)** (MEDIUM PRIORITY GPU; ~48h GPU). The next reliability-extension gate toward 7-day cloud routing per v292 cloud-routing-discipline. Decision deferred to orchestrator strategy thread when pause-flag releases.

### PROT compliance (v300 -> v301)

- **PROT-004/006**: V2 is HARD_PASS with row addition; no row closures; forward-test rescue extension sketches filed cheapest-first per [[feedback-rescue-sketch-first-sequencing]] (R-V2-SUSTAINED-RUNTIME-EXTENSIONS 6 rescues + R-PP-3-AUDIT-ROTATION-SUBSTRATE-DESIGN 2 rescues = 8 total rescues; R1 0-compute APPLIED inline in BOTH sets; R2-R5 cheap-medium variants ROUTED-not-auto-dispatched per pause-flag ACTIVE; R6 expensive cloud DEFERRED).
- **PROT-007**: substrate_capability_map_history.md v301 row appended atomically. BACKLOG NOTE carried forward: v277 + v278 history rows STILL MISSING.
- **PROT-008**: validator script `tools/orchestrator/validate_capmap_commit.py` STILL ABSENT (carried forward); infrastructure gap flagged not blocking. Row addition + annotations (no band moves); no portfolio state regression risk.
- **PROT-009**: cap_map.md (v301 entry) + substrate_capability_map_history.md (v301 row) + strategy_decisions_2026-05-31.md (this v301 entry) + visibility_decisions_2026-05-31.md (one-line) + 1 status_log entry staged atomically; **212th PROT-009 paired commit**.
- **PROT-018**: anchor `sustained_workload_24h_baseline_v1_n4096` `_n4096` matches config.N=4096 (PROT-018 compliant).
- **PROT-019**: V2 wall_s=86668 within timeout=90000s (LONG-RUN flag); PROT-019 compliant.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 performed; bridge get_metrics returned _source=remote but content was STALE-CACHE; required manual SCP-pull for authoritative data; honest re-read confirms label-honest. ZERO new label-vs-honest catch but FLAGGED metrics-bridge cache-staleness on this specific anchor as engineering item (likely the 24h-LongRun-completion remote-state-emitter SCP-poll window missed the final file-write or bridge cache TTL exceeded poll cadence).
- [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]: Bridge returned _source=remote but content STALE; honest workflow REQUIRES manual SCP fallback when verdict claims FULL-run wall_s differs from metrics-file elapsed_s by >>1%. ADD to engineering item: bridge get_metrics SHOULD compare file LastWriteTime against expected verdict-arrival window OR support force-fresh-pull on demand.
- [[feedback-obey-user-pause-explicitly]]: pause-flag CHECKED ACTIVE (`data/orchestrator_paused.flag` EXISTS); pipeline-pacing exp_dev dispatch SKIPPED entirely; queue-refill outcome NOT logged; honored user pause directive.
- [[feedback-pipeline-pacing]]: queue state CHECKED (GPU 6 + remote_cpu 5 + local_cpu 0 = 11 pending+running); HEALTHY; pipeline-pacing exp_dev would have been a CANDIDATE if pause-flag absent but pause-flag ACTIVE OVERRIDES.
- [[feedback-cap-map-update-protocol]]: atomic single-batch commit; sub-agent push BLOCKED per [[feedback-subagent-permission-inheritance]]; commit hash surfaced for main-thread push.
- [[feedback-for-you-tab-primary-channel]]: 1 status_log entry with plain_language + importance HIGH (24h sustained reliability validation).
- [[feedback-no-padding-experiments]]: NEW capability row added is genuinely a new capability (first 24h sustained-runtime validation; was previously untested at any production scope); NOT padding. CONSERVATIVE no-band-LIFT on substrate-product-feature row and framework-reliability bands (V2 is empirical-corroboration not framework-LIFT).
- [[feedback-decision-log-eol-handling]]: this strategy_decisions entry appended via tools/orchestrator/append_decision_log.py (LF EOL preserved); cap_map + history CRLF preserved.
- [[feedback-rescue-sketch-first-sequencing]]: 2 forward-test extension sketches filed cheapest-first; R1 0-compute APPLIED inline in BOTH; R2-R5 cheap-medium routed; R6 expensive cloud DEFERRED.
- [[feedback-rehabilitation-after-rejection]]: NOT TRIGGERED (V2 HARD_PASS not rejection).
- [[feedback-no-smoke]]: brutal honesty applied -- one transient hour-17 latency-spike CALLED OUT in NEW-row caveats (not buried); local-cache-stale-vs-remote-fresh issue CALLED OUT as infrastructure caveat.
- [[feedback-substrate-value-framing-matured-2026-05-26]]: V2 anchors production-readiness narrative empirically; "killer features ship first" framing reinforced -- the substrate-product-feature row PRODUCTION-READY annotation is now empirical not theoretical.
- [[feedback-no-label-vs-honest-anchor-names]]: PROT-018 anchor `_n4096` matches config.N=4096 (compliant).
- [[feedback-strategy-spec-formula-selftests]]: V2 self-test PASS (recorded in exp_dev_decisions_2026-05-30 line 91 6.5s); FULL-run honors the spec.
- [[feedback-dont-overextend-theorems]]: 24h single-seed single-N validation scoped to "production-scope reliability at N=4096 M=2048 24000-op mixed workload" NOT to "substrate is multi-seed cross-N production-ready at all scopes"; CONSERVATIVE row addition with explicit caveats.

### Commit and push

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up.


## v301 -> v302 BATCHED 3-VERDICT CPU evening wave (213th PROT-009 paired commit) -- 2026-05-31

**Context.** 3 CPU verdicts landed 2026-05-31 21:23-21:32: V1 multi_hop_caching_baseline_v3_n4096 wall_s=2769, V2 state_compression_adversarial_codebook_v1_n4096 wall_s=88, V3 reasoning_storage_scheme_b_smoke_v1_n16384 wall_s=463. All 3 source=remote via bridge get_metrics. Pause-flag CHECKED ABSENT. Queue 6 GPU + 4 CPU pending+running. REMOTE-FIRST honest re-read.

### Step 0 honest re-read summary -- 0 NEW LABEL-VS-HONEST catches; all 3 labels HONEST

**V1 multi_hop_caching_baseline_v3_n4096 C2_HARD_PASS HONEST** -- 25-cells (5 alpha x 5 seed) unanimous hit-rate monotone in alpha {0.5: 0.831, 0.75: 0.869, 1.0: 0.906, 1.5: 0.958, 2.0: 0.982} all >= 0.50 HP threshold; audit_integrity=1.000 unanimous all 25 cells; hot<cold aggregate-true but ALPHA-DEPENDENT (clean at alpha=2.0 ~14% speedup; tied at alpha<1 within noise). Honest reading: HARD_PASS HONEST with alpha-dependence annotation (not catch); REVERSES v296 v2 confounded-design DEFER (CACHE_CAP=16 << K_PATHS=100 forces evictions vs v2 CACHE_CAP=256 > K_PATHS=100 cache-saturation artifact).

**V2 state_compression_adversarial_codebook_v1_n4096 PP2ADV_HARD_PASS HONEST** -- 5 seeds unanimous kf1_adv100=1.000 (deletion-cert preserved unanimous), kf3_adv100 mean 0.950 (worst-cell 0.922 well above 0.70 HP threshold), kf2_drift_norm=1.0 unanimous (compression-layer stable). c_quant/bits8 4x compression PRESERVES audit-cert under codebook-collision adversary at adv_100% AND adv_50% at N=4096 M=2048. Honest reading: HARD_PASS HONEST verdict_msg numerics match per-cell aggregates exactly. PROT-018 _n4096 compliant.

**V3 reasoning_storage_scheme_b_smoke_v1_n16384 RSB_MIDDLE_BAND HONEST** -- Arm A (audit decode of three-way bipolar binding k_step=r_type XOR k_premise1 XOR k_premise2): HARD_PASS UNANIMOUS all 3 seeds all 3 components recoverable confidence=1.000 (substrate PRIMITIVE viable). Arm B (structured-key Path D differential vs random-key baseline): per-seed ratios 0.958/0.939/0.951 mean 0.949 BORDERLINE just below 0.95 HARD_PASS (1 of 3 seeds passes pre-reg, 1 below); ~5% per-hop accuracy penalty for structured vs random keys. Arm C (rho-mitigation): mean 0.956 just clears HARD_PASS by 0.006; delta over Arm B +0.007 negligible within noise; mitigation provides essentially zero benefit at this scope. SVD spectra essentially identical structured vs random (sigma_1/sigma_2 ratio 1.004-1.011 across both arms; structural correlation NOT showing up in spectrum). Honest reading: MIDDLE_BAND label HONEST; STRATEGIC INSIGHT: substrate-as-reasoning-store framing SURVIVES the De Marzo-Iannelli (2023) + Amit-Gutfreund-Sompolinsky (1985) theoretical concern (5-25% capacity degradation under structural correlation); substrate lands at OPTIMISTIC END of that band (~5%); however the empirical evidence is BORDERLINE-MIDDLE_BAND not clean HARD_PASS -- "retrieval primitive with structured-key support" framing is more empirically anchored than "full reasoning primitive" framing at this regime.

### Cap_map state-transition decisions (v301 -> v302)

1. **NEW ROW PP-10** "Multi-hop production-paths caching at Zipfian-skewed query distributions" -- Validated single-N single-workload-shape P-band 0.70-0.85. Reverses v296 PP-caching-deferred conclusion via v3 cache-cap-redesign empirical resolution. Alpha-dependent latency benefit caveat explicit; single-N + Zipfian-only + cache_cap=16 production-sizing-untested caveats explicit.
2. **NEW ROW PP-11** "Substrate-as-reasoning-store primitive (Scheme B three-way bipolar binding)" -- Inconclusive (MIDDLE_BAND at smoke N=16384 3-seed) P-band 0.40-0.55 lower-end of research-estimated 0.35-0.55. Arm A audit-decode perfect; Arm B structured-key Path D borderline-MIDDLE_BAND (~5% penalty); Arm C rho-mitigation negligible. Framing SURVIVES with caveats.
3. **PP-2 storage efficiency row LIFT 0.65-0.75 -> 0.70-0.80** (+5%/+5% CONSERVATIVE). v302 V2 first adversarial extension; 2nd PP-2 corroboration after v295 first-empirical-foothold; single-N N=4096 caveat persists pending v4 cross-N at N=16384.
4. **Adversarial-defense candidate sub-row** -- 0.55-0.75 UNCHANGED at band-position. ANNOTATION: c_quant/bits8 compression-layer-defense DIFFERENT axis from a_query_sim-query-layer-defense; compositional {compression + a_query_sim} hybrid defense plausible.
5. **PP-9 reasoning-amortization-economics row** -- 0.55-0.70 UNCHANGED at band-position; caveat (b) UPDATED with PP-11 cross-ref + ~5% quality-degradation budget for amortization claim vs LLM-only baseline.
6. **Substrate-product-feature row 89-98% UNCHANGED at band-position** -- PP-10 caching corroboration; PP-11 product-framing sharpens to "retrieval primitive with structured-key support".

### Framework reliability bands (v301 -> v302)

- **PP-2 storage efficiency row LIFT 0.65-0.75 -> 0.70-0.80** (+5%/+5% CONSERVATIVE).
- **All other framework reliability bands UNCHANGED at band-position.**

### Portfolio

24 + 36 -> **26 + 36** (+2 NEW Production positioning rows: PP-10 Validated + PP-11 Inconclusive).

### Honest / label-vs-honest tallies

- HONEST: 282 + 3 = **285** (V1 + V2 + V3 all label-honest).
- LABEL-VS-HONEST: **161 UNCHANGED** (zero new catches).

### Rescue sketches (PROT-004/006 cheapest-first per [[feedback-rescue-sketch-first-sequencing]]) -- 3 rescue/extension sets; 15 rescues; R1 0-compute APPLIED inline in ALL 3 sets

**R-V1-PP-CACHING-EXTENSIONS:** R1 subsumption inline + R2 cross-N at N=8192/N=16384 + R3 production-LLM query distribution probe + R4 cache-size sweep + R5 hybrid LRU+W-similarity cache mechanism deferred.

**R-V2-PP-2-ADVERSARIAL-EXTENSIONS:** R1 subsumption inline + R2 v4 cross-N at N=16384 routing-only (already in CPU queue position 8) + R3 c_quant/bits8 vs other adversarial attack-axes + R4 compositional defense {c_quant/bits8 + a_query_sim} HIGHEST-STRATEGIC-VALUE + R5 adaptive-adversary stress deferred.

**R-V3-PP-11-REASONING-STORE-EXTENSIONS:** R1 subsumption inline + R2 multi-seed FULL at N=16384 10-seed + R3 alternative encoding schemes (FHRR HRR Fourier-circular-convolution OR 4-way XOR + per-hop cleanup) HIGHEST-STRATEGIC-VALUE + R4 alternative rho-mitigation formulations + R5 multi-N cross-scale deferred.

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched per pause-handshake + queue-state-decision)

1. **PP-11 alternative encoding-scheme probe** (HIGH PRIORITY; ~1-2h CPU; R-V3 R3). Closes "Scheme B three-way XOR is the only encoding tested" caveat; if alternative encoding HARD_PASSes Arm B substrate-as-reasoning-store framing LIFTs PP-11 MIDDLE_BAND -> HARD_PASS; informs substrate-LLM Week 1 GO/NO-GO.
2. **PP-10 cross-N at N=8192 + N=16384 cache-viability** (MEDIUM PRIORITY; ~30-60min CPU; R-V1 R2). Closes single-N caveat on PP-10 NEW row.
3. **PP-2 compositional defense {c_quant/bits8 + a_query_sim} hybrid** (MEDIUM PRIORITY; ~1-2h CPU; R-V2 R4). Tests whether compression-layer + query-layer defense composes additively; potential adversarial-defense sub-row LIFT.

### PROT compliance (v301 -> v302)

- PROT-004/006: 3 rescue sets cheapest-first 15 rescues R1 0-compute APPLIED inline all 3 sets; R2-R4 cheap-medium routed; R5 high-cost deferred; 0 capability-row closures.
- PROT-007: history v302 row appended atomically; v277+v278 backlog still carried forward.
- PROT-008: validator ABSENT carried forward; PP-2 band-move + 2 row additions no regression risk on existing portfolio.
- PROT-009: cap_map.md (v302) + history.md (v302 row) + this strategy_decisions entry + visibility_decisions one-line + 3 status_log entries staged atomically; 213th PROT-009 paired commit.
- PROT-018: all 3 anchors PROT-018 spot-check CLEAN (V1 _n4096 V2 _n4096 V3 _n16384 all match config.N).

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 on all 3; 3 label-honest; 0 new catches; V1 hot<cold alpha-dependence ANNOTATION recorded.
- [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]: all 3 source=remote bridge get_metrics; no SCP fallback needed.
- [[feedback-cap-map-update-protocol]]: atomic single-batch commit per dispatch `Single batched commit` requirement; sub-agent push BLOCKED.
- [[feedback-obey-user-pause-explicitly]]: pause-flag CHECKED ABSENT; queue healthy; pipeline-pacing exp_dev SKIP (queue healthy + no routing-file refill request + 3 substantive verdicts represent cycle work).
- [[feedback-for-you-tab-primary-channel]]: 3 status_log entries with plain_language + importance.
- [[feedback-no-padding-experiments]]: PP-2 LIFT +5%/+5% CONSERVATIVE; PP-10 P 0.70-0.85 (single-N caveats); PP-11 P 0.40-0.55 lower-end-of-research-estimate (Arm B borderline).
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-rescue-sketch-first-sequencing]]: R1 cheapest-first APPLIED inline in all 3 rescue sets.
- [[feedback-rehabilitation-after-rejection]]: PP-10 REVERSES v296 deferred conclusion via cache-cap-redesign empirical rescue; cleanly demonstrated; no new closures.
- [[feedback-dont-overextend-theorems]]: PP-11 framing SURVIVES scoped to "Scheme B three-way XOR at smoke N=16384 3-seed structured-key penalty ~5%" NOT to full-reasoning-primitive-at-all-encoding-and-scales.
- [[feedback-lit-scan-calibration-penalty]]: PP-11 P 0.40-0.55 LOWER end of research-estimated 0.35-0.55 because Arm B borderline-MIDDLE_BAND not clean HARD_PASS.
- [[feedback-no-smoke]]: brutal honesty -- V1 alpha-dependence + V3 Arm B borderline + V3 mitigation negligible all CALLED OUT.
- [[feedback-substrate-value-framing-matured-2026-05-26]]: PP-10 caching plumbing/SDK milestone; PP-11 framing-sharpening to retrieval-primitive is killer-feature-product-positioning honesty.

### Commit and push

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

Commit message: see cap_map v302 entry verbatim.


## v302 -> v303 BATCHED 4-VERDICT CPU evening wave 2 (214th PROT-009 paired commit) -- 2026-05-31

**Context.** 4 CPU verdicts landed 2026-05-31 21:38-21:43: V1 reasoning_storage_threshold_sweep_v1_n4096 wall_s=372, V2 substrate_state_compression_v4_n16384 wall_s=179, V3 adversarial_a_query_sim_defense_cpu_n8192 wall_s=9 (INFRA_FAILURE: 0 cells), V4 compressed_path_d_composition_v1_n4096 wall_s=117. All 4 source=remote via bridge get_metrics. Pause-flag CHECKED ABSENT. GPU queue 6 pending+running; CPU queue 0 (IDLE post-batch). REMOTE-FIRST honest re-read.

### Step 0 honest re-read summary -- 1 NEW LABEL-VS-HONEST catch (V1) + V3 INFRA-FAILURE no-cap-shift + V2 and V4 label-honest

**V1 reasoning_storage_threshold_sweep_v1_n4096 RSTS_HARD_PASS LABEL-VS-HONEST CATCH 162** -- per-cell ratio_s1_s2 unanimous ~1.00-1.02 across ALL n_chains {100, 1K, 10K, 44K, 100K} 3-seed at N=4096; NO spectral collapse at any n_chains including 100K (2.27x beyond theoretical 32N/3 ~ 44K threshold). Pre-reg HP was BIDIRECTIONAL: (a) ratio < 3x MP-edge at <=44K AND (b) collapse evident at 100K. Empirical satisfies (a) but REFUTES (b) -- theoretical 32N/3 prediction broken. HARD_PASS tag over-claims theory-empirical alignment that DID NOT occur; substrate retains spectral integrity 2.27x beyond predicted threshold. Honest reading: CAPACITY-ENVELOPE-EXTENSION (good news for substrate-as-reasoning-store capacity at N=4096 through 100K chains) NOT theory-empirical-alignment HARD_PASS. PP-11 LIFT 0.40-0.55 -> 0.45-0.60 CONSERVATIVE on capacity-envelope-extension; theory-empirical narrative REMOVED. 162nd cumulative label-vs-honest catch.

**V2 substrate_state_compression_v4_n16384 C3V4_HARD_PASS HONEST** -- 3 seeds {7, 17, 23} at N=16384 M=8192. bits8 config: retr=1.000 unanimous, compression=4.0x unanimous, kfs_all_pass=True unanimous all 3 KFs=1.000. bits4 fails (retr=0); bits16 only 2x compression. verdict_msg `n_hp_configs=1` structurally honest. CAVEAT: M=32768 from pre-reg M_grid {8192, 32768} did NOT execute (single-M coverage). 3rd PP-2 corroboration after v295 nominal-N=4096 + v302 adversarial-N=4096. PROT-018 `_n16384` compliant. PP-2 LIFT 0.70-0.80 -> 0.75-0.85 CONSERVATIVE.

**V3 adversarial_a_query_sim_defense_cpu_n8192 AQS_CPU_INCONCLUSIVE INFRA_FAILURE** -- wall_s=9 elapsed_s=0.0 cells=[]. Same Kerdock log2(8192)=13 odd MM-construction-constraint pre-check rejection that hit v300 V2. NO STATE TRANSITION. 2nd INFRA_FAILURE this hour from same root cause; PROT-022 queue_add guard urgency REINFORCED. Adversarial-defense sub-row 0.55-0.75 UNCHANGED (no empirical signal). a_query_sim cross-codepath at N=8192 REMAINS UNTESTED.

**V4 compressed_path_d_composition_v1_n4096 CPD_HARD_PASS HONEST -- FIRST COMPOSITIONAL HARD_PASS in portfolio** -- 5 seeds {7, 17, 23, 31, 41} at N=4096 M=8192 depth=5 K=100. All 5 cells: ok=True acc_baseline=1.000 acc_compressed=1.000 delta=0.0 unanimous. verdict_msg `n_m_hp=1/1` structurally honest. CAVEAT: M=32768 cell from pre-reg M_grid {8192, 32768} did NOT execute (single-M coverage; only M=2N tested, M=8N missing). PROT-018 `_n4096` compliant. PP-2 c_quant/bits8 x R-PATH-D-NO-CEILING COMPOSE at M=2N N=4096 K=100 depth=5. NEW SUB-ROW under PP-2 Validated single-M single-N single-K single-depth P 0.65-0.80 CONSERVATIVE; substrate-product-feature row UNCHANGED at band-position per [[feedback-no-padding-experiments]] single-M execution.

### Cap_map state-transition decisions (v302 -> v303)

1. **PP-2 storage efficiency row LIFT 0.70-0.80 -> 0.75-0.85** (+5%/+5% CONSERVATIVE). V2 third corroboration; cross-N at N=16384 single-M 3-seed unanimous perfect.
2. **PP-11 reasoning-store-primitive row LIFT 0.40-0.55 -> 0.45-0.60** (+5%/+5% CONSERVATIVE). V1 capacity-envelope-extension through 100K chains at N=4096 (2.27x beyond theoretical 32N/3 prediction); theory-empirical-alignment narrative REMOVED.
3. **NEW SUB-ROW under PP-2** "PP-2 x R-PATH-D production-default compositional substrate (c_quant/bits8 x Path D)" -- Validated single-M (M=2N) single-N (N=4096) P-band 0.65-0.80. FIRST COMPOSITIONAL HARD_PASS in portfolio.
4. **Adversarial-defense candidate sub-row** 0.55-0.75 UNCHANGED. V3 INFRA_FAILURE no signal.
5. **PP-9 reasoning-amortization-economics row** 0.55-0.70 UNCHANGED at band-position. PP-11 LIFT informs upper-quality-budget bound; narrative refresh only.
6. **Substrate-product-feature row 89-98% UNCHANGED at band-position**. First compositional HARD_PASS narratively belongs here but stays at band per CONSERVATIVE single-M policy.

### Framework reliability bands (v302 -> v303)

- **PP-2 storage efficiency row LIFT 0.70-0.80 -> 0.75-0.85** (+5%/+5% CONSERVATIVE; 3rd corroboration via cross-N).
- **PP-11 reasoning-store-primitive row LIFT 0.40-0.55 -> 0.45-0.60** (+5%/+5% CONSERVATIVE; capacity-envelope-extension; theory-empirical-alignment narrative removed).
- **NEW SUB-ROW under PP-2 0.65-0.80** (first compositional HARD_PASS at single-M).
- **All other framework reliability bands UNCHANGED at band-position**.

### Portfolio

26 + 36 -> **26 + 36 UNCHANGED** (PP-2 LIFT within row; PP-11 LIFT within row; NEW compositional sub-row attaches to PP-2; V3 KILLED; V1 reframed). 4 verdicts; 3 mutations (2 row LIFTs + 1 sub-row); 0 closures.

### Honest / label-vs-honest tallies

- HONEST: 285 + 2 (V2 + V4) = **287**.
- LABEL-VS-HONEST: 161 + 1 (V1 RSTS_HARD_PASS theoretical-alignment over-claim) = **162**.
- INFRA_FAILURE: V3 not in tallies; cumulative-via-log2-odd root cause = 2 (v300 V2 + v303 V3).
- Per-cell sample size: V1 15 + V2 9 + V4 5 = 29 new cells.

### Rescue sketches (PROT-004/006 cheapest-first per [[feedback-rescue-sketch-first-sequencing]]) -- 3 sets; 13 rescues; R1 0-compute APPLIED inline in ALL 3 sets

**R-V1-PP-11-CAPACITY-ENVELOPE-EXTENSION:** R1 subsumption inline + R2 n_chains extension to {200K, 500K, 1M} + R3 cross-N reasoning-storage threshold at N={8192, 16384} + R4 alternative encoding probe + R5 adaptive-collision adversary deferred.

**R-V2-PP-2-CROSS-N-CORROBORATION:** R1 subsumption inline + R2 V2 re-run with M=32768 cell forced + R3 c_quant alternative bit-widths cross-config probe + R4 PP-2 adversarial extension at N=16384 HIGH-STRATEGIC-VALUE + R5 full grid deferred.

**R-V4-COMPOSITIONAL-HARD-PASS-EXTENSION:** R1 subsumption inline + R2 V4 re-run with M=32768 cell forced HIGH-STRATEGIC-VALUE + R3 compositional cross-N at N={8192, 16384} + R4 compositional cross-K {200/500/1000} + R5 compositional cross-depth {10/20/50}.

### Top-3 follow-on decisions for orchestrator (NOT auto-dispatched)

1. **V4 R2: M=32768 cell re-run for compositional HARD_PASS upper-band LIFT** (HIGH PRIORITY; ~10-30min CPU OR ~5-10min Lambda).
2. **V1 R2: n_chains capacity-envelope extension to {200K, 500K, 1M}** (HIGH PRIORITY; ~30-60min CPU).
3. **V2 R4: PP-2 adversarial extension at N=16384** (MEDIUM PRIORITY; ~30min CPU).

### PROT compliance (v302 -> v303)

- PROT-004/006: 3 rescue sets cheapest-first 13 rescues; R1 0-compute APPLIED inline all 3 sets; R2 cheap routed; R3-R5 routed/deferred; 0 closures.
- PROT-007: history v303 row appended atomically.
- PROT-008: validator ABSENT carried forward; within-row band-LIFTs + sub-row addition no regression risk.
- PROT-009: cap_map.md (v303) + history.md (v303 row) + this strategy_decisions entry + visibility_decisions one-line + 4 status_log entries staged atomically; 214th PROT-009 paired commit.
- PROT-018: V1 V2 V4 anchor-name `_n<N>` matches config.N (all compliant); V3 `_n8192` compliant in name but INFRA-FAILURE bypasses cell-execution.
- PROT-019: V3 9s wall well below 21600s floor (instant Kerdock pre-check rejection).
- PROT-022: V3 = 2nd log2-odd MM-construction-constraint catch this hour; guard urgency REINFORCED.

### Memory adherence

- [[feedback-verdict-msg-honest-reread]]: Step 0 on all 4; 1 catch (V1 over-claim theoretical-alignment); V2 + V4 label-honest with single-M caveats called out; V3 INFRA-FAILURE not a label issue.
- [[feedback-verdict-handler-remote-metrics-fix-2026-05-27]]: all 4 source=remote bridge get_metrics.
- [[feedback-cap-map-update-protocol]]: atomic single-batch commit; sub-agent push BLOCKED.
- [[feedback-obey-user-pause-explicitly]]: pause-flag CHECKED ABSENT; CPU queue IDLE; pipeline-pacing exp_dev dispatch SKIPPED (4 substantive verdicts; routing-only follow-ups identified; orchestrator discretion on R-V1/V2/V4 R2 routing).
- [[feedback-for-you-tab-primary-channel]]: 4 status_log entries with plain_language + importance.
- [[feedback-no-padding-experiments]]: PP-2 +5%/+5% CONSERVATIVE; PP-11 +5%/+5% CONSERVATIVE; compositional sub-row P 0.65-0.80 CONSERVATIVE on single-M; substrate-product-feature row UNCHANGED.
- [[feedback-decision-log-eol-handling]]: this entry appended via append_decision_log.py.
- [[feedback-rescue-sketch-first-sequencing]]: R1 cheapest-first APPLIED inline all 3 rescue sets.
- [[feedback-rehabilitation-after-rejection]]: 0 row closures; V3 INFRA-FAILURE clear remedy (PROT-022 guard); a_query_sim cross-codepath at N=8192 REMAINS UNTESTED.
- [[feedback-dont-overextend-theorems]]: V1 capacity-envelope scoped to "100K chains at N=4096"; V4 compositional scoped to "M=2N N=4096 K=100 depth=5 5-seed"; not over-extended.
- [[feedback-lit-scan-calibration-penalty]]: PP-11 LIFT to 0.45-0.60 lower-end of capacity-evidence band per CONSERVATIVE policy on theory refutation.
- [[feedback-no-smoke]]: brutal honesty -- V1 over-claim caught; V3 INFRA-FAILURE called out; V2 + V4 partial M-coverage explicit caveats.
- [[feedback-substrate-value-framing-matured-2026-05-26]]: V4 FIRST compositional HARD_PASS maps to compositional-audit-API + production-default-positioning killer-feature; plumbing rate-limiter framing maintained; CONSERVATIVE sub-row reflects single-M not narrative restraint on the milestone.

### Commit and push

Push: BLOCKED from sub-agent context per [[feedback-subagent-permission-inheritance]]; orchestrator main thread executes `git push origin main` as 1-tool follow-up.

Commit message: see cap_map v303 entry verbatim.
