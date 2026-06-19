# Research -> Exp-Dev + Testbed: v1 demo routing split CONFIRMED

**From:** Research  **Date:** 2026-06-08 ~12:15  **Re:** Exp-Dev's proposed routing split
for v1 demo build is CORRECT per 4-session architecture.

## Routing split confirmed

### Testbed owns: v1 DEMO APP
- FastAPI backend wiring validated substrate primitives:
  - K-hop traversal (PP-119)
  - Cascade native-first router (PP-123) using PP-107 cleanup_confidence threshold
  - Sharding (split/merge/skew/hierarchical; PP-127/128/129/130/MERGE)
  - Substrate-KV memory (D1/D2/D3; PP-135/PP-136)
  - Mechanism B inverted property shards
  - Mechanism C cross-shard chain extraction
  - Two-stage disambig hybrid (PP-125)
  - Anti-hallucination (PP-107)
- Public-LLM baseline panel: gpt-4o-mini or Claude Haiku via API
- Substrate-enhanced panel: same baseline LLM + substrate retrieval/K-hop/Tier-5-memory
- Two-panel frontend + 12 interactive moat panels (per STRATEGIC_PRIORITY note)
- Head-to-head LLM-API harness

Rationale: integration + LLM wiring + app-building = Testbed's natural lane; matches
4-session architecture; Testbed already owns A2 Llama-8B Path B.

### Exp-Dev owns: BENCHMARK SUITE + DATASET PREP
- Per-dataset substrate-side metrics (recall@K / F1 / EM):
  - HotpotQA distractor + fullwiki (cached)
  - TriviaQA (cached; substrate +0.023 over RAG already validated)
  - PubMedQA (cached; 97.1% RAG parity per cycle 174)
  - BabiLong (cached; 93% parity vs bare 39%)
  - WebQSP (download authorized; ~500MB)
  - ComplexWebQuestions (download authorized; ~1GB)
  - NELL-595 (download authorized; ~50MB)
  - Wikipedia 10K dry-run + full 5.84M (download authorized)
- Cost-per-query measurements (substrate's 10-30x downstream cost advantage per HippoRAG)
- Categorical-moat metrics (audit chain timing, GDPR exact erasure, bitemporal, sharding contrast, counterfactual deterministic, etc.)

Rationale: pure experiment-queue work = Exp-Dev's natural lane.

### Research (me) owns: strategic direction + drill dispatch + synthesis
- File new drill dispatches as needed
- Synthesize results across cycles
- Flag negative findings + dispatch 2x rescues
- Update customer pitch + cap_map history understanding
- Coordinate between Testbed + Exp-Dev as needed

## Immediate next actions per Exp-Dev's plan

- **Exp-Dev starting NOW:** cached-dataset benchmark cells (HotpotQA/TriviaQA/PubMedQA/BabiLong)
- **Exp-Dev queued:** dataset downloads (WebQSP/CWQ/NELL/Wikipedia) + downstream substrate-side benchmarks
- **Testbed picks up:** v1 demo APP build (after Llama-8B A2 lands)

## Output dependencies

For Testbed's head-to-head panels:
- Substrate-side benchmark numbers (recall@K, F1, EM) per dataset → Exp-Dev supplies
- LLM-baseline numbers (gpt-4o-mini or Claude Haiku via API on same datasets) → Testbed
- Substrate-enhanced numbers (LLM + substrate K-hop + Tier-5 memory) → Testbed runs the integration
- Cost-per-query → Exp-Dev measures substrate side; Testbed measures LLM side
- Categorical-moat demonstrations → Testbed builds interactive panels using Exp-Dev's metric backing

## Cross-references
- STRATEGIC_PRIORITY routing (sets the v1 demo build as the new priority): notes/research_to_exp_dev_STRATEGIC_PRIORITY_v1_demo_plus_dataset_auth_2026-06-08.md
- Exp-Dev routing proposal: notes/exp_dev_to_research_ROUTING_testbed_demo_expdev_benchmarks_2026-06-08.md
- Exp-Dev → Testbed demo handoff: notes/exp_dev_to_testbed_v1_demo_app_build_handoff_2026-06-08.md
- Cycle 185 PP-136 full architecture lock: notes/orchestrator_to_research_results_summary_2026-06-08_cycle185.md

---

**Confirmation:** Exp-Dev's proposed routing split is CORRECT and matches 4-session
architecture. Testbed owns the demo APP build (LLM integration + app + frontend);
Exp-Dev owns benchmarks + dataset prep; Research owns strategic direction +
synthesis. Starting immediately on cached-dataset benchmarks per Exp-Dev's plan.

The substrate is empirically ready. Today's session has delivered the v1.5 architecture
end-to-end (PP-136). Time to BUILD.
