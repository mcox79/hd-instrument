# Testbed handoff: external-distribution priority list (11 priorities)

**From**: orchestrator
**To**: testbed
**Date**: 2026-05-31
**Source**: external-Claude discussion synthesis brought back by user
**Cap_map state when filed**: v297 (commit eb86886). Cap_map JUST compacted (commit 8728223) — main file 80% smaller.

## Orchestrator's pre-filing evaluation

The document is sound but predates today's verdict cascade. Specifically:
- Path D 32N HARD_PASSED today (G7, cloud, $0.23) -> testbed P1 Experiment C extends naturally to 48-64N.
- a_query_sim defense HARD_PASSED today (G8, cloud, $0.12, 1.000/0.000 at 5-seed N=4096) -> testbed P1 Experiment A cross-N replication is well-motivated next.
- Modern Hopfield 16N corroborated CPU + cloud today (C9 second-source, $0.25) -> ceiling extension still open; cliff-locator (v10) in flight on CPU.
- Several "in flight" items in the doc match what orchestrator just shipped:
  - **P4 C3 v3 compression cross-N** -> orchestrator shipped `substrate_state_compression_v3_n8192` (commit 8729450), pending in CPU queue behind v10.
  - **P10 LRU Cache v3** -> orchestrator shipped `multi_hop_caching_baseline_v3_n4096` (CACHE_CAP=16 << K_PATHS=100, alpha {0.5-2.0}; commit da16482), pending in CPU queue.
  - **P11 codebook-collision x deletion-cert** -> orchestrator shipped `state_compression_adversarial_codebook_v1_n4096` (commit da16482), pending in CPU queue.

So P4 + P10 + P11 in the document are already-shipped; verdict_handler will process when they land.

## Authorization-pending items (need user OK before testbed dispatches)

These items are NOT free-action for testbed. Orchestrator surfaces them to user separately:

1. **P1 Lambda batch ($1.45 total)** — 3 cloud experiments (a_query_sim cross-N at N=16384 ~$0.50; a_query_sim vs p4 edit-fact-traverse ~$0.30; Path D 48-64N envelope ~$0.65). Each user-authorized per standing rule.
2. **P2 Pattern B with Anthropic API ($30-75 across 3 phases)** — needs (a) user provides / confirms Anthropic API key, (b) Phase 1 smoke ~$1-5, (c) Phase 2 production query eval ~$20-50, (d) Phase 3 distinctive-value scenarios ~$10-20.

## Priorities (as filed)

### Priority 1 — Lambda Batch Relaunch (PENDING user auth)

**Experiment A** — a_query_sim cross-N replication at N=16384 (5-seed, M ∈ {4096, 8192, 12288}). Tests whether today's G8 defense scales. PASS -> adversarial sub-row 0.45-0.65 -> 0.55-0.75. ~$0.50.

**Experiment B** — a_query_sim vs p4 edit-fact-traverse (5-seed, N=4096 M=2048). Second known adversarial pattern; tests whether a_query_sim is general or codebook-collision-specific. PASS -> closes second known vulnerability. ~$0.30.

**Experiment C** — Path D 48-64N envelope extension (M ∈ {196608, 262144} at N=4096, depth ∈ {30, 50}, 3 seeds). Continues today's G7 ceiling characterization past 32N. ~$0.65.

**Strategic value**: cross-N adversarial defense replication is the single highest-leverage item; closes the "single-N defense" caveat on today's G8 LIFT.

### Priority 2 — Pattern B LLM Integration with Anthropic API (PENDING user auth)

3 phases:
- Phase 1 mock-vs-real wiring smoke (~$1-5)
- Phase 2 production query evaluation vs LLM-only + LLM+RAG (~$20-50)
- Phase 3 edit-then-query + deletion-with-cert scenarios (~$10-20)

**Strategic value**: HIGHEST among external-integration priorities. Load-bearing product test.

### Priority 3 — Phi-3 Missing 7 #3 + #4 Completion

**Prerequisites**: V2 24h sustained_workload drains at ~21:11 ET tonight (frees ~5GB VRAM for Phi-3-mini-4bit). See `notes/testbed_handoff_gpu_access_granted_2026-05-31.md` for concurrency protocol.

**Strategic value**: closes Week 0 latency budget. Sets up research Week 1 feasibility smoke GO/NO-GO.

### Priority 4 — Compression Cross-N (C3 v3) — ALREADY IN FLIGHT (orchestrator-shipped)

`substrate_state_compression_v3_n8192` queued, pending behind `modern_hopfield_cpu_extended_v10_n16384`. Verdict will land today / tomorrow. No testbed action needed.

### Priority 5 — TCFT Recovery Engineering — DEPENDS ON RESEARCH P2

Hold. Research's TCFT degradation analysis must identify the recovery mechanism first. After that lands as a routing file, this becomes a defined engineering build.

### Priority 6 — D7 Edit-Log-Replay Mechanism Implementation

Second adversarial defense candidate. **Orchestrator note**: re-evaluate need after testbed P1 Experiment B lands. If a_query_sim defeats both codebook-collision AND p4 edit-fact-traverse, D7's motivation reduces substantially. If a_query_sim is codebook-collision-only, D7 is still needed.

**Cost**: ~1-2 weeks engineering.

### Priority 7 — Storage Efficiency Drill (Missing 2)

Substrate footprint at N ∈ {4096, 8192, 16384}, M ∈ {1K, 5K, 10K}; codebook + audit-chain footprint; multi-tenant K=10 sharding overhead; comparison to FAISS / Pinecone / Weaviate; Pareto frontier with bits8 compression (if C3 v3 validates today's foothold).

**Strategic value**: PP-2 row evidence + customer cost modeling. ~1-2 weeks CPU.

### Priority 8 — Audit-Trail Rotation Drill (Missing 3)

**Prerequisites**: V2 24h workload completes (provides realistic growth data, ~21:11 ET tonight).

Compression approaches (structure-aware, dedup, summarization) + rotation strategies (time / op-count / hierarchical) + compliance mapping (GDPR / HIPAA / SOC2) + queryability after compression/rotation.

**Strategic value**: PP-3 row evidence. ~2 weeks engineering + analysis.

### Priority 9 — Per-Store Latency Decomposition

Instrument substrate store ops at N ∈ {4096, 8192, 16384}, 1000 ops each. Decompose codebook-lookup / rank-1-update / audit-chain-update. Update cost model. ~2-3 days engineering + ~$0.10 Lambda if large-N timing.

### Priority 10 — LRU Cache v3 — ALREADY IN FLIGHT (orchestrator-shipped)

`multi_hop_caching_baseline_v3_n4096` queued (CACHE_CAP=16, K_PATHS=100, alpha {0.5, 1.0, 1.5, 2.0}, HP: hit@a2 >= 0.50 + monotone + hot < cold). Verdict will land today / tomorrow.

### Priority 11 — Codebook-Collision x Deletion-Cert — ALREADY IN FLIGHT (orchestrator-shipped)

`state_compression_adversarial_codebook_v1_n4096` queued (c_quant bits8, 100%/50% adversarial collision, HP: kf1_adv100 >= 0.70 + kf3 >= 0.70 + kf2). Verdict will land today / tomorrow.

## Cross-session dependencies

- Phi-3 #3 + #4 tonight -> research Week 1 feasibility smoke design.
- Lambda batch (P1) results -> research can incorporate cross-N adversarial-defense evidence into Week 1 smoke design.
- TCFT recovery (research P2) -> TCFT engineering (testbed P5) sequential.

## How to file deliverables

- Engineering milestones: `notes/testbed_milestone_<topic>_<date>.md`
- Decisions log: `notes/testbed_decisions_<date>.md`
- Cap_map-affecting findings: `notes/strategy_request_to_strategy_<topic>_<date>.md`
- Routing back to orchestrator (e.g., authorization needs): `notes/strategy_request_to_strategy_<topic>_<date>.md`
- Status_log: `log_event(source='testbed', ...)`

## Files referenced

- This handoff file
- `notes/testbed_handoff_gpu_access_granted_2026-05-31.md` (GPU concurrency protocol)
- Today's commits: eb86886 (cloud 3-pack verdicts), da16482 (multi_hop v3 + adversarial compression), 8729450 (v295 follow-ups), b116da9 (Modern Hopfield CPU + D1 + C3 v2), 7959353 (cloud-dispatch blocker fix + reships)
