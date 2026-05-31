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
