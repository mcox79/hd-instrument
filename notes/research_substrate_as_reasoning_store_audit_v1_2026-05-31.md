# Research: substrate-as-reasoning-store proposal audit (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- shared comprehensive external evaluation proposing 8 experiments for "substrate as memory and reasoning layer for context-limited LLMs"; user said "the below too!"
Method: main-thread audit + cap_map cross-reference + overlap-with-in-flight-work analysis + 1 Sonnet drill dispatched on the prerequisite encoding-scheme question

## HEADLINE

The doc's reasoning-store FRAMING SHIFT is valuable for product positioning (cap_map is fact-framed throughout; reasoning-store framing opens a positioning lane for compliance customers needing verifiable DERIVATION chains, not just verifiable fact storage). The doc's 8 EXPERIMENTS substantially overlap with what's already in flight or filed: 5 of 8 are duplicates of D1 (compositional binding production scope, filed earlier today), substrate-LLM build's Week 5 4-way comparison + 4 bespoke benchmarks (already locked), V2 24h sustained workload (already complete), or Pattern B service capability validation (already 5/5 PASS). ONE experiment is genuinely new (Exp 2 reasoning amortization measurement); ONE prerequisite drill is needed (reasoning-step bipolar-encoding scheme; dispatched today). The doc's quantitative claims (10-25x cost, 100-1000x latency) are mostly standard RAG-vs-LLM numbers, not substrate-specific; should be deflated when communicating externally.

## What's valuable in the doc

### The framing shift

The cap_map currently frames every substrate property as fact-related:
- "Audit trail completeness" (for fact storage)
- "Edit-then-query" (for facts)
- "Deletion certificates" (for fact erasure)
- "Path D multi-hop" (over fact chains)

The doc proposes RE-FRAMING these as reasoning-store-applicable:
- "Audit trail" → "verifiable DERIVATION chains" (compliance positioning)
- "Edit-then-query" → "reasoning step corrections without invalidating unrelated chains"
- "Deletion certificates" → "certified erasure of derivation steps"
- "Path D multi-hop" → "Path D over REASONING chains"

This re-framing is mostly FREE (no new engineering) and strengthens the moat narrative for regulated-industry customers. Worth adopting as cap_map naming convention going forward.

## Overlap audit (5 of 8 duplicates)

| Doc's experiment | Already covered by |
|---|---|
| **Exp 1** reasoning chain storage + retrieval | **D1 compositional binding production-scope** (filed earlier today, `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md`): same Path D mechanism, same depth-5 multi-hop, same memorization-trap discrimination; corpus framing is "fact relations" but substantively tests the same retrieval primitive |
| **Exp 3** standard-benchmark quality | **Substrate-LLM Week 5 4-way comparison** (LLM-only / LLM-only-control / LLM+text-RAG / LLM+substrate) on ARC/HellaSwag/PIQA/BoolQ/WinoGrande/TriviaQA + MuSiQue/HotpotQA/2WikiMultihop -- already locked in testbed handoff |
| **Exp 6** hybrid retrieval + LLM extension | **Substrate-LLM build's Rescue C**: substrate runs Path D autonomously, LLM emits single query; this IS the recommended architecture |
| **Exp 7** compositional reasoning over stored chains | **D1 again** -- compositional binding production scope IS this test |
| **Exp 8** cross-session reasoning persistence | **V2 24h sustained workload COMPLETE** + Pattern B service capability validation 5/5 PASS; reasoning encoded as facts inherits this validation transitively |

## What's genuinely new

### Exp 2: reasoning amortization measurement (file as new experiment proposal)

Cost-economics scenario testing: LLM-only derives reasoning each query via chain-of-thought (~5-30s per query, ~$X per query) vs LLM+substrate where LLM derives once + substrate stores + subsequent similar queries retrieve stored reasoning.

This is NEW because no current experiment measures the amortization economics. It's also straightforward: workload = 100 queries with 30% repeated reasoning patterns, 70% novel. Cost-per-query measured for both systems.

Worth filing as a separate routing for orchestrator. ~2-3 weeks engineering + ~$50-100 Anthropic API costs (within Tier 2b LLM comparison harness scope; Anthropic key already available per `project_anthropic_api_key_available` memory).

### Exp 4 + Exp 5: domain-specific deployment scenarios

Compliance reasoning corpus (Exp 4) and real-time decision support (Exp 5) are DOMAIN-SPECIFIC DEPLOYMENT SCENARIOS, not foundational capability tests. Defer to pilot-deployment-driven scoping. Not "research drills" in the standard sense -- they're product validation engagements.

## The prerequisite gap the doc misses

**HOW does a reasoning step become a single bipolar codeword in W?**

The doc says: `key = (reasoning_context, current_state)` and `value = (next_state, justification, derivation_method)` -- but doesn't specify the encoding.

This matters because a reasoning step has STRUCTURE that a fact doesn't:
- Multiple premises (one or more existing fact codewords)
- Inference rule type (modus ponens / abductive / transitive / analogical / causal)
- Conclusion (the derived fact)
- Justification (which rule applied, which premises used, confidence)

Encoding this as a bipolar codeword in {-1,+1}^N=4096 requires a non-trivial bind/superpose scheme. The substantive substrate-physics question:

**Does "reasoning storage" reduce to "multi-hop fact retrieval where the relation slot encodes the inference-rule-applied"? Or does it require a DISTINCT binding scheme to encode inference rules as composable substrate atoms?**

Three candidate schemes:
- **Scheme A (FACT-CHAIN)**: encode inference rules as fact-graph relations; reasoning = multi-hop traversal. This IS what D1 already tests.
- **Scheme B (RULE-AUGMENTED)**: distinct binding mechanism for rules; rules apply to many premise pairs.
- **Scheme C (CONCLUSION-CACHE)**: store derived conclusions explicitly; "reasoning" reduces to caching.

If Scheme A gives 80% of the value, Scheme B's additional engineering is wasted. If Scheme B can do things Scheme A cannot (universal quantification over premises), it's a distinct substrate-physics capability worth a separate experiment.

A Sonnet lit-scan drill on this question was dispatched today; when it returns, the answer determines whether reasoning storage needs its own experimental track or is subsumed by D1.

## Quantitative claims to deflate

The doc throws around big numbers that should be deflated when communicating externally:

| Doc's claim | Honest framing |
|---|---|
| 10-25x cost reduction | Standard RAG-vs-LLM number; not substrate-specific; achievable by any caching layer |
| 100-1000x latency reduction | True mathematically (13ms Path D vs 5-30s LLM CoT) but ASSUMES EQUIVALENT QUALITY -- the open question |
| 20-40pp accuracy improvement | Standard RAG-vs-long-context-LLM number; substrate's improvement IS substrate-specific only if it beats text-RAG (which Week 5 4-way comparison tests) |
| 10-100x cost reduction for repeated reasoning | Amortization economics; applies to any caching layer; substrate-distinctive only if combined with audit + edit-isolation + deletion-cert (which competitors lack) |

The deflated framing: substrate offers SUBSTANTIVE quantitative improvements ON TOP OF amortization gains a vanilla cache would also provide, because the audit + edit-isolation + deletion-cert make the amortization SAFE under regulatory scrutiny (corrections to derivation steps don't invalidate unrelated chains; deleted reasoning produces a cert).

## Recommendation

**Don't dispatch 8 experiments.** Instead:

1. **Adopt reasoning-store FRAMING for cap_map** (no engineering; positioning win). Re-label existing rows where applicable. ~30 min annotation work for orchestrator.

2. **File Exp 2 (reasoning amortization)** as new experiment proposal in a separate routing. ~2-3w + ~$100 API. Genuinely distinct from current work.

3. **Encoding-scheme prerequisite drill DISPATCHED today** (Sonnet, ~40min). Answer determines whether reasoning storage needs distinct track or is subsumed by D1.

4. **Reframe D1 (already filed)** to OPTIONALLY include a reasoning-chain test corpus alongside the fact-graph corpus. Modest scope expansion: tests the unified hypothesis "reasoning is just multi-hop with structured relations" empirically.

5. **Reject Exps 3, 6, 7, 8 as duplicates** with explicit reasoning. User can override if they want, but the work is being done.

6. **Defer Exps 4, 5 with criteria** -- pilot-deployment-driven scoping.

## Cap_map implications

If adopted as I recommend:
- Reasoning-store framing annotation added to several existing rows
- Path D sub-row caveat list extended: "validated for fact-chain multi-hop; reasoning-chain multi-hop subsumed via Scheme A pending D1 verdict"
- NEW row "Reasoning amortization economics" at 🔬 P-band TBD pending Exp 2
- NO new substrate-physics row for "reasoning storage" until encoding-scheme drill returns + verdict on whether Scheme B is distinct from Scheme A

## Files of interest

- `notes/strategy_request_to_strategy_capability_exploration_3_drills_2026-05-31.md` (D1 production-scope compositional binding -- already covers Exps 1+7)
- `notes/research_substrate_llm_aggressive_eval_v1_2026-05-31.md` (Week 5 4-way comparison + 4 bespoke benchmarks -- already covers Exp 3)
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md` (Rescue C autonomous Path D -- already covers Exp 6)
- `notes/testbed_decisions_2026-05-31.md` (Pattern B service 5/5 PASS + V2 24h sustained workload context -- already covers Exp 8)
- `project_anthropic_api_key_available` memory (Anthropic key ready for Exp 2)

## Method note

Audit completed in main thread (~25 min); 1 Sonnet drill dispatched on the prerequisite encoding-scheme question (~40min). Pattern reconfirmed: when external doc proposes large N of experiments, cross-reference against in-flight work FIRST, then dispatch drills only on genuinely-novel questions. Avoids 8-simultaneous-drill padding per [[feedback-no-padding-experiments]] and [[feedback-no-smoke]] (don't validate by dispatch volume; validate by leverage and overlap).

## What I'll file when the encoding drill returns

A small follow-on routing with:
- Verdict: does reasoning storage require Scheme B (distinct from fact-chain), or is it Scheme A in disguise?
- If Scheme A: recommend reframing D1 to include reasoning-chain corpus; no new experiment.
- If Scheme B: propose a focused experiment to test the distinct binding scheme; ~2-3 weeks; substrate-physics moat-extender.

Plus an Exp 2 reasoning-amortization-measurement routing file as a separate dispatch (independent of the encoding-scheme verdict).
