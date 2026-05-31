# Testbed handoff: reasoning amortization economics — build the experiment

**From**: orchestrator
**To**: testbed
**Date**: 2026-05-31
**Closes**: corresponds to cap_map PP-9 row added v297 -> v298 (commit aba66b1)
**Source**: `notes/routed_completed/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md`
**Authorization**: user-authorized 2026-05-31 ("do both now"; both = reasoning amortization + reasoning storage Phase 1 smoke)

## TL;DR

Build a Tier 2b harness extension to measure substrate-cached reasoning vs LLM-derived reasoning across a workload with repeated-pattern queries. This is a 2-3 week engineering build. Anthropic API budget ~$50-100. No cloud spend.

Cap_map row PP-9 anticipates this experiment as the empirical anchor. Verdict_handler will process the result when testbed ships.

## Anchor

**Anchor name**: `reasoning_amortization_economics_v1_n4096`

**PROT-018 compliance**: `_n4096` binds the substrate N. The "reasoning" part of the experiment uses the substrate at N=4096 sub-saturation; the LLM is the cost driver, not N.

## Experiment design (verbatim from research routing)

### Workload

- 100 queries, 30% repeated reasoning patterns + 70% novel
- Repeated patterns share the same reasoning chain (e.g., "What is X's parent?" where X varies but the relation-traversal is identical)
- Novel patterns require fresh derivation each time

### Two systems

- **System A (control)**: LLM-only with chain-of-thought; LLM derives reasoning each query (no caching layer)
- **System B (substrate-augmented)**: LLM derives on first query of each pattern; substrate stores the derivation as fact-chain atoms; subsequent similar queries trigger substrate retrieval via Path D depth=5 instead of re-derivation

### Measurements per query

- (a) Wall latency (ms)
- (b) Input + output tokens consumed
- (c) Anthropic API cost ($)
- (d) Reasoning correctness vs ground truth (graded by held-out judge LLM)
- (e) Audit-trail availability (yes/no for System B; no for System A)

### Replication

5 seeds (different query orderings); report mean + std

## Pre-registered HP / HF / MIDDLE bands

### HARD-PASS

- System B per-query cost on REPEATED-pattern queries: at least 10x cheaper than System A on the same query
- System B reasoning correctness on REPEATED-pattern queries: >= System A correctness within 5pp (substrate doesn't degrade quality)
- System B audit-trail available for all repeated-pattern responses; System A audit-trail absent
- AMORTIZATION CURVE: per-query cost decreases monotonically across the workload as substrate accumulates (the more queries seen, the cheaper subsequent queries)

### HARD-FAIL

- System B per-query cost on REPEATED patterns >= System A cost (no amortization win)
- OR System B reasoning correctness drops > 15pp below System A (quality regression)
- OR substrate-hit-rate on repeated patterns < 50% (substrate fails to recognize similar queries)

### MIDDLE-BAND

- Cost reduction in [3x, 10x] on repeated patterns
- OR correctness drop in [5pp, 15pp]
- OR substrate-hit-rate in [50%, 80%]

## Engineering ownership

- **Workload generator**: testbed builds; 100 queries with 30/70 split; ground truth annotations; deterministic seeds for replicability
- **System A baseline**: testbed Tier 2b LLM comparison harness already in `hdlab_service/baselines/llm_client.py` (AnthropicLLMClient is implemented per memory); just add CoT prompting + cost tracking
- **System B substrate side**: substrate retrieval via existing Path D infrastructure in `experiments/_multi_hop_mechanisms.py`; reasoning storage encoding scheme is OPEN per the 2x research drill (see Open question below)
- **Judge LLM grading**: held-out Anthropic call per response; testbed implements
- **Cost tracker**: testbed extends `tools/cloud/cost_tracker.py` or adds `data/anthropic_amortization_cost_tracker.json` for symmetry
- **Verdict synthesis**: testbed produces a results-JSON in `data/exp_reasoning_amortization_economics_v1_n4096_metrics.json` analogous to Lambda result format; verdict_handler will process

## Sequencing

Per research routing:
- AFTER Week 0 Missing 7 #1-#4 verdict (gates whether substrate-LLM integration architecture is viable)
- AFTER D7 Bet B ret_A rescue (uses related continual-learning infrastructure this experiment may borrow)
- BEFORE D1 compositional binding (production scope) — this experiment provides COMMERCIAL-VALUE numbers that inform D1 investment decision
- IN PARALLEL with substrate-LLM Week 1 feasibility smoke (different resources: this is API + local-CPU; Week 1 is local-GPU)

**Orchestrator clarification**: "AFTER Week 0" means after substrate-LLM Week 1 GO/NO-GO review (tomorrow morning after Phi-3 #3 + #4 land tonight). If Week 1 GO/NO-GO is NO-GO, testbed has more bandwidth for this build; if GO, runs in parallel with the Week 2-6 build.

## Open question (gate before testbed starts coding)

The 2x reasoning-storage research drill (`notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md`) flagged that **Scheme A (plain fact-chain encoding) and Scheme B (three-way bipolar binding) may give different amortization properties**. The Phase 1 reasoning-storage smoke (just dispatched to CPU queue as `reasoning_storage_scheme_b_smoke_v1_n16384`) tests this empirically.

**Recommendation**: testbed uses Scheme A for the amortization build initially (simpler, matches existing fact-chain infrastructure). Annotate the experiment results with a note that "Scheme A used; Scheme B may extend the operating envelope per Phase 1 smoke verdict pending."

If Phase 1 smoke lands a clean Scheme B PASS within the build window, testbed can either (a) re-spec for Scheme B mid-build or (b) ship Scheme A results then file a follow-up Scheme B build.

## Anthropic API key dependency

Per `notes/strategy_request_to_strategy_anthropic_key_location_2026-05-31.md` (testbed's earlier query): testbed needs the Anthropic key in env var `ANTHROPIC_API_KEY` or `.env.anthropic`. User-side action pending; surface to user that this gates this build.

**Orchestrator note for testbed**: even with the key, the build itself is 2-3 weeks engineering before API spend ramps up; you can scaffold workload generator, System A CoT, cost tracker harness in parallel with key resolution. Phase 1 smoke (~$1-5) can happen as soon as key lands; this amortization build's full API run happens after the harness is complete.

## Cap_map ref

- PP-9: "Reasoning amortization economics (LLM-derive-once + substrate-cache vs LLM-derive-each-query)" — research-only, P 0.55-0.70 — anticipates this experiment's PASS/FAIL verdict for row movement.

## Files referenced

- This handoff file (closes when testbed reads + acks via testbed_decisions log)
- `notes/research_substrate_as_reasoning_store_audit_v1_2026-05-31.md` (research audit, source of the proposal)
- `notes/research_substrate_reasoning_storage_2x_synthesis_v1_2026-05-31.md` (2x deep drill flagging Scheme A vs B question)
- `notes/routed_completed/strategy_request_to_strategy_reasoning_amortization_experiment_2026-05-31.md` (the closed research routing)
- `notes/testbed_handoff_lambda_and_anthropic_authorized_2026-05-31.md` (Anthropic API auth already granted; key location is the open question)
- Cap_map PP-9 row (commit aba66b1)

## Closing the routing

Testbed moves this file to `notes/routed_completed/` when the build is dispatched (not when it completes).
