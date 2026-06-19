# Strategy request: reasoning amortization economics experiment (the one genuinely-new experiment from substrate-as-reasoning-store proposal)

## Trigger: research audit 2026-05-31 of external evaluation "Substrate as Memory and Reasoning Layer for Context-Limited LLMs"

Origin: user 2026-05-31 shared 8-experiment proposal. Research audit at `notes/research_substrate_as_reasoning_store_audit_v1_2026-05-31.md` identified 5 of 8 as duplicates of in-flight/filed work. This routing files the ONE genuinely-new experiment.

## Finding (one paragraph)

The doc's Exp 2 "reasoning amortization measurement" is the only experimental proposal that doesn't duplicate existing work. It tests the cost-economics claim that "LLM derives reasoning once + substrate stores + subsequent similar queries retrieve stored reasoning" yields 10-100x cost reduction for workloads with repeated reasoning patterns. This is amortization economics that applies to any caching layer in principle, but is substrate-distinctive because the audit + edit-isolation + deletion-cert make the cache SAFE under regulatory scrutiny (corrections to derivation steps don't invalidate unrelated chains; deleted reasoning produces a verifiable cert). Worth filing as a separate experiment because (a) it directly tests a commercial-value claim no current experiment addresses; (b) it uses Anthropic API already available; (c) it's straightforward to design and run; (d) it gives pilot-deployment economic justification.

## Recommended action

**1. New cap_map row proposed (research-only 🔬)**.

Row name: "Reasoning amortization economics (LLM-derive-once + substrate-cache vs LLM-derive-each-query)"

Initial P-band (deflated): 0.55-0.70 (amortization gains are mechanically predictable given non-zero substrate-hit-rate; range reflects what fraction of customer workloads have repeated-reasoning patterns)

Caveats: (a) cost-comparison is meaningful only if substrate's reasoning-retrieval has EQUIVALENT QUALITY to LLM's freshly-derived reasoning; the experiment measures both; (b) at this point reasoning storage IS fact-chain retrieval per [[research_substrate_as_reasoning_store_audit_v1_2026-05-31]] pending encoding-scheme drill verdict.

**2. Experiment to dispatch.**

**Anchor**: `reasoning_amortization_economics_v1_n4096`

**Spec sketch (exp_dev refines)**:
- Workload: 100 queries, 30% repeated reasoning patterns + 70% novel
- System A (control): LLM-only with chain-of-thought; LLM derives reasoning each query
- System B (substrate-augmented): LLM derives on first query; substrate stores the derivation as fact-chain atoms; subsequent similar queries trigger substrate retrieval via Path D depth=5
- Measurements per query: (a) wall latency (ms), (b) input + output tokens consumed, (c) Anthropic API cost ($), (d) reasoning correctness vs ground truth (graded by held-out judge LLM), (e) audit-trail availability (yes/no for System B; no for System A)
- 5 seeds (different query orderings); report mean + std

**Pre-reg HARD-PASS**:
- System B per-query cost on REPEATED-pattern queries: at least 10x cheaper than System A on the same query
- System B reasoning correctness on REPEATED-pattern queries: ≥ System A correctness within 5pp (substrate doesn't degrade quality)
- System B audit-trail available for all repeated-pattern responses; System A audit-trail absent
- AMORTIZATION CURVE: per-query cost decreases monotonically across the workload as substrate accumulates (the more queries seen, the cheaper subsequent queries)

**Pre-reg HARD-FAIL**:
- System B per-query cost on REPEATED patterns ≥ System A cost (no amortization win)
- OR System B reasoning correctness drops > 15pp below System A (quality regression)
- OR substrate-hit-rate on repeated patterns < 50% (substrate fails to recognize similar queries)

**Pre-reg MIDDLE-BAND**:
- Cost reduction in [3x, 10x] on repeated patterns
- OR correctness drop in [5pp, 15pp]
- OR substrate-hit-rate in [50%, 80%]

**3. Cost.**

- Engineering: ~2-3 weeks (testbed Tier 2b LLM comparison harness already complete per `notes/testbed_decisions_2026-05-31.md`; this experiment extends it with the amortization-workload generator + cost-tracking telemetry)
- Anthropic API: ~$50-100 (Anthropic key already available per `project_anthropic_api_key_available` memory)
- Local GPU: minimal (substrate ops are CPU/local-GPU)
- No cloud spend

**4. Sequencing.**

Recommend dispatch AFTER:
- Substrate-LLM Week 0 Missing 7 verdict lands (~tonight if V2 drains as scheduled at 21:11 ET) — gates whether the integration architecture is viable at all
- D7 Bet B ret_A rescue (sequenced first per `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md`) — uses related continual-learning infrastructure that this experiment may borrow

Recommend dispatch BEFORE:
- D1 compositional binding (production scope) — this experiment provides COMMERCIAL-VALUE numbers that inform whether D1's substrate-physics moat is worth the larger-scope investment
- Pilot deployment scoping — the cost-economics numbers from this experiment are LOAD-BEARING for any pilot deployment conversation

In parallel with:
- Substrate-LLM Week 1 feasibility smoke (different machine resources; this experiment is API + local-CPU, not local-GPU)

**5. Out of scope.**

- Encoding-scheme question (whether reasoning storage requires Scheme B distinct from fact-chain) — separate drill dispatched today; this experiment uses Scheme A (fact-chain) regardless of verdict
- Exps 4, 5, 8 from the doc — domain-specific deployments deferred to pilot scoping
- Exps 3, 6, 7 from the doc — duplicate existing in-flight work per audit

## Confidence

P_deflated 0.55-0.70 for HARD-PASS as defined above:
- Amortization gains are MECHANICALLY PREDICTABLE: if substrate hit-rate is non-zero, System B saves the LLM-derivation cost for those hits; the only question is whether the substrate-side retrieval is high-quality enough to be substituted for fresh LLM derivation
- Range reflects: (a) substrate's reasoning-retrieval quality at production-scope envelope is empirically open (the open question that D1 + the encoding drill address), (b) substrate-hit-rate depends on workload structure
- Calibration penalty: -0.10 to -0.20 applied (lower than novel-synthesis because the amortization-economics framework is well-grounded; substrate-distinctiveness comes from audit + edit-isolation overlay)

## Files of interest

- `notes/research_substrate_as_reasoning_store_audit_v1_2026-05-31.md` (full 8-experiment audit; 5 duplicates surfaced; encoding-scheme prerequisite drill dispatched)
- `notes/testbed_decisions_2026-05-31.md` (Tier 2b LLM comparison harness COMPLETE 5/5 mock wiring; Anthropic key already available; this experiment extends that infrastructure)
- `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md` (D1 compositional binding production-scope; provides substrate-quality numbers this experiment's cost-economics depend on)
- `project_anthropic_api_key_available` memory
- `project_substrate_killer_features_2026-05-26` memory (deletion-cert + compositionality audit + per-fact retention features that make the substrate-cache REGULATED-SAFE)

## Not auto-dispatched

This is a research-filed experiment proposal. Orchestrator decides:
- (a) Whether to add the cap_map row + dispatch the experiment
- (b) Sequencing within the current queue (recommend after D7 + Week 0; before D1)
- (c) Engineering ownership (testbed Tier 2b LLM comparison harness extension is the natural home)

No work begins without orchestrator queueing.

---
BULK-ARCHIVED 2026-06-01: previously processed (cap_map v311+ reflects acted-on work); routing closed retroactively per dashboard inbox-clearance Path A.
