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
