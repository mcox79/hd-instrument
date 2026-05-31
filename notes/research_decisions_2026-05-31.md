# Research decisions -- 2026-05-31

## alt_edit_isolation_v1 -- 2026-05-31 (research:opus, with 3 Sonnet lit-scan subagents)

**Drill.** Alternative edit-isolation mechanisms to replace v290 U3 COW infeasibility (mem-amp 10.13x vs 4x target; throughput 6-7.5/s vs 50/s target). Origin: routing file `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` (R-COW-INFEASIBILITY R3). Token-efficient parallel-subagent dispatch: 3 Sonnet lit-scans covering (1) delta-encoding storage, (2) LSM lazy-replay cost, (3) CRDT + LSH-partial-COW hybrid.

**Outcome.** Four candidate architectures mapped; M1 (delta-encoding) and M2 (LSM lazy-replay) collapse to the same mechanism family viewed from write-path vs read-path angles. Recommended PRIMARY: **log-structured rank-1 store (M1+M2 unified)**. Mem-amp 1.5-3x at K up to N (formula 1 + 2K/N); throughput 8-12K q/s GPU projected; audit-by-construction synergy with KF-2 deletion-cert (log IS audit). Joint P_deflated 0.40-0.50 in 7-day engineering budget. Load-bearing empirical risk: FP drift at large K, known fix Kahan summation. SECONDARY: M3+M4 CRDT op-log + LSH-partial-COW hybrid (P_deflated 0.35); CRDT-alone REJECTED (P_deflated 0.25; depth>=2 retrieval incompatible with eventual-consistency semantics). Path D (substrate-native T2 PASS 45/45 cells) is the substrate-native generalization of CRDT-style per-op independence at the retrieval layer; M1+M2 generalizes the SAME mechanism to the W-mutation layer.

**Note path.** notes/research_alt_edit_isolation_v1_2026-05-31.md (9 external citations: Dong RocksDB CIDR17, Sarkar LSM-VLDB21, Tas-Boneh AFT23, Kanellis F2-VLDB24, Zhou lazy-views-VLDB07, Dayan Autumn-2023, Shapiro CRDT-SSS11, Almeida delta-CRDT-2016, Almeida CRDT-survey-ACM-2023; 7 internal cross-refs).

**Routing.** notes/strategy_request_to_strategy_alt_edit_isolation_2026-05-31.md (cap_map annotation recommendation + M2 smoke proposal at ~30 min CPU laptop; orchestrator decides timing).

**Next-drill candidate.** Once M2 smoke verdict lands: if HARD_PASS, drill on full N=4096 production design (MVCC layer + Merkle audit-tree integration + hot-set tier engineering cost). If HARD_FAIL on cosine (FP drift), drill on Kahan-variant retry. If HARD_FAIL on throughput, escalate to M3+M4 hybrid drill.

**Method note.** 3 Sonnet lit-scan subagents in parallel = ~25 min wall, ~83K tokens. Main thread (Opus) synthesis + routing files = small additional cost. Token-efficient pattern confirmed for lit-scan-heavy drills per user 2026-05-31 ask "use subagents and sonnet when you can - we want to be token efficient without sacrificing accuracy and efficiency." Per [[feedback-subagent-model-optimization]] reinforced.


## external_eval_integration -- 2026-05-31 (research:opus, evaluation + verification of user-shared external doc)

**Drill.** User shared external-Claude evaluation doc proposing 7 underweighted/missing research directions + cloud-routing discipline. Research session evaluated each claim, verified against cap_map v290/v291 + status_log + grep of recent decision logs, sorted into adopt/drop/reframe categories.

**Outcome.** 6 of 7 proposed drills confirmed as genuine gaps (substrate-augmented LLM absolute-quality vs LLM-only; storage efficiency production-scale; audit trail rotation; concept drift detection mechanism; substrate-LLM token-throughput latency budget; per-store latency for bursty writes). 1 drill (multi-substrate composition) conceptually valid but external doc's anchor was wrong (K=10 sharding reference was v282 CLOSED Op E cross-shard correlation probe; needs re-anchoring from scratch). 3 tactical recommendations DROPPED for factual error: (a) Modern Hopfield "N/2 vs G5/G6 reconciliation" was stale (v288 GPU-OOM resolved by v290 CPU path; today's C1 verdict pushed max_M=4N=65536 → v291 row LIFT yellow→green); (b) "Pattern B LLM integration" conflated Path B substrate-mechanism with undefined LLM-integration framework; reframe needed; (c) "$5 cloud spend at 50% budget" -- 08:52 event internally inconsistent ($7.50/$10=75% mathematically; label says 50%) AND 08:57 testbed event confirms Lambda not yet activated; likely telemetry-source bug; flag for testbed audit not crisis. Strategic shift confirmed (plumbing > physics at maturity; cloud is exception not default).

**Note path.** Routing file `notes/strategy_request_to_strategy_research_focus_expansion_2026-05-31.md` (6 new research-only rows; 1 needs-re-anchoring row; cloud-routing discipline; queue-weighting shift; immediate/near-term/medium-term/longer-term sequencing).

**Method note.** Pull-before-significant-work caught uncommitted state from other sessions; autostash + commit pattern verified clean. Verification grep against cap_map + status_log surfaced 3 factual errors that would have introduced wrong work into the queue if adopted verbatim -- value of "verify before adopting" loop demonstrated. ~12 min wall, low-token (no subagent dispatch needed; main-thread verification sufficient).

**Next-drill candidate.** Highest-leverage among the 6 new rows: LLM-integration latency budget characterization (Missing 7) -- cheapest scope, gates everything LLM-integration-flavored. Storage efficiency analysis (Missing 2) is the most independent (CPU-bound, doesn't depend on queue state). Substrate-augmented absolute-quality benchmark (Missing 1) is the longest scope but highest-leverage product test; that's the load-bearing one.


## substrate_llm_deep_integration_v1 -- 2026-05-31 (research:opus, 3 Sonnet lit-scan subagents)

**Drill.** User raised codebook-native LLM integration question -- substrate's bipolar codewords could potentially be consumed by an LLM WITHOUT text-tokenization round-trip; deeper than RAG. Research session dispatched 3 parallel Sonnet lit-scans: (A) vector-native LLM memory interfaces, (B) multi-hop reasoning offload from LLM to external structured memory, (C) cheapest engineering path on consumer GPU.

**Outcome.** Architectural primitives exist: 4 published patterns (RETRO chunked cross-attention, Memorizing Transformers gated kNN, Flamingo/Q-Former cross-attention bridge, DNC/Memory-Layers VSA-style memory layer). DNC's outer-product write `M = M + w v^T` is MATHEMATICALLY IDENTICAL to substrate `W = (1/N) sum v_l k_l^T` modulo bipolar quantization. NVSA (Hersche, Nature MI 2023) is closest published bipolar-bridge precedent BUT in OPPOSITE direction (neural -> bipolar VSA memory; not bipolar codeword -> LLM input). Recommended starting architecture: Pattern 3 (Flamingo/LLaMA-Adapter style) -- frozen 1-3B base LM (Phi-3-mini-3.8B MIT license) + ~27M-param bidirectional MLP bridge + substrate Path D depth=5 autonomous multi-hop. Three rescues for the query-decomposition bottleneck at 1-3B scale (Subagent B's binding research risk); Rescue C (substrate-autonomous depth-5 iteration; LLM emits single initial query) is most substrate-leveraging. 6 risks identified; 8GB VRAM hardware constraint is the binding feasibility item. Build plan: 4-6 weeks single-person; Week 1 feasibility smoke is cheap insurance against committing to full 4-6w on a blocker. P_deflated 0.40-0.45 on 24GB GPU; 0.25-0.30 on 8GB.

**Note path.** notes/research_substrate_llm_deep_integration_v1_2026-05-31.md (12 external citations, 6 internal cross-refs; build plan week-by-week; test design with LLM-only vs LLM+text-RAG vs LLM+substrate comparison + substrate-favored bespoke benchmarks).

**Routing.** notes/strategy_request_to_strategy_substrate_llm_deep_integration_2026-05-31.md (cap_map new research-only row "Substrate-LLM deep integration via codebook-native interface" at 0.30-0.45 P-band; 3 decision gates -- GPU resource / feasibility smoke / queue sequencing -- NONE auto-dispatched).

**Method note.** 3 Sonnet lit-scan subagents in parallel = ~30 min wall, ~110K tokens combined. Same pattern as morning's alt-edit-isolation drill; token-efficient pattern reconfirmed. The "intrinsic language" framing IS unpublished (NVSA opposite direction; substrate is the inverse case) -- this drill formalized the design space that was implicit in the user's question.

**Next-drill candidate.** Once user decides GPU resource + sequencing: Week 1 feasibility smoke (Phi-3-mini-4bit baseline on lm-eval-harness + bridge scaffold + smoke forward-pass) is the cheap-decisive-test that gates the full 4-6w commit. Alternatively: ship the 3 cheaper drills first (Missing 7 LLM-integration latency budget; Missing 2 storage efficiency; Missing 3 audit-trail rotation) per [[feedback-rescue-sketch-first-sequencing]] cheapest-first principle -- they inform the larger build.

**Routing update (later same turn, after user said "good experiment to run; route it to testbed and/or orchestrator to implement"):** Testbed handoff filed at `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`. The handoff:
- Hands the engineering build to testbed (Phi-3-mini loader + bridge MLP + substrate-codeword glue + Path D autonomous multihop + synthetic training data + lm-eval-harness + LLM+text-RAG baseline + 3 substrate-favored bespoke benchmarks)
- Pre-decides design choices testbed implements without re-arbitrating (base LM, adapter pattern, Rescue C multi-hop strategy, training procedure, discrete-gradient handling)
- BLOCKS work-start on 3 user-side decisions: (a) GPU resource 8GB/24GB/cloud; (b) commitment depth Week 1 smoke vs full 4-6w; (c) queue sequencing vs the 3 cheaper drills
- Surfaces 3 top risks (query-decomposition bottleneck, bridge-alignment training, 8GB VRAM ceiling)
- Per session-architecture session-ownership: I (research) wrote the handoff routing file; testbed implements; orchestrator coordinates cap_map decisions + cloud-cost approvals if applicable. I do NOT cross into experiments/ or testbed/ directories.

**Decisions resolved (user 2026-05-31 "agreed - lets get these tests going"; testbed UNBLOCKED):**
- (a) GPU: LOCAL remote desktop. Default assumption marsh@home 8GB; testbed verifies actual VRAM at Week 0 start; upgrade to fp16 + faster wall if >8GB. NO cloud spend authorized.
- (b) Commitment depth: Week 1 feasibility smoke FIRST as GO/NO-GO gate.
- (c) Queue sequencing: WEEK 0 = Missing 7 LLM-integration latency budget (gates architectural assumption that substrate Path D + bridge fit in LLM token window); WEEK 1 = substrate-LLM feasibility smoke; WEEKS 2-6 = full build if Week 1 PASS. Missing 2 + Missing 3 in parallel as CPU-bound work.

Testbed handoff updated inline with Week 0 Missing 7 spec (4 measurements + PASS/MIDDLE/FAIL criteria) + full 7-week sequence table. Testbed begins Week 0 upon reading.
