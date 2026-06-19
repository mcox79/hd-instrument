# Research -> Orchestrator + Exp-Dev: NORTH STAR REFRAME (user-locked 2026-06-07 evening)

**From:** Research session
**To:** Orchestrator + Exp-Dev (parallel sessions)
**Date:** 2026-06-07 evening
**User authorization:** "going to sleep now - authorized for all searches and notes to other sessions"

---

## The user-stated north star

> "Goal is to have a fully functional system up and running sometime soon that has performance that exceeds straight LLM's of relative size, in a way that is empirical and clear."

NOT: substrate as complementary audit layer.
YES: substrate that OUTPERFORMS LLMs at chosen benchmarks.

## What this means for each session

### For Orchestrator:
- Continue cycle-by-cycle verdict synthesis as today
- When verdicts land that ENABLE LLM-comparison benchmarks (e.g., end-to-end retrieval accuracy at large M, multi-hop verifiable QA, adversarial robustness), flag prominently
- Cap_map should track NEW capability category: "LLM head-to-head readiness" with sub-rows for benchmark suite components
- Avoid drift into substrate-internal performance tuning when the macro goal is benchmark integration

### For Exp-Dev:
- Continue queue-pull discipline as today
- When choosing among queued cells, PREFER those that advance LLM-comparison benchmark readiness (e.g., RetroMAE pipeline; integrated end-to-end retrieval; benchmark suite components) over those that further explore substrate-internal capability gaps
- Cell candidates that build toward INTEGRATED system: Chain 3 v1 build (substrate + Llama-1B generation layer; cross-shard K-hop coordinator); counterfactual Components 11-12 (causal extension); RetroMAE customer-onboarding pipeline
- Cells that explore substrate-internal capability without integration context are LOWER priority

### For Research (me; my overnight loop):
- Already adjusted standing duties in overnight_loop_research_session.md memory entry
- New priority order for drills:
  1. Drills that advance benchmark-readiness (LLM-comparison test design; integration architecture)
  2. Drills that validate cycle 150 GOLD claims empirically against LLM baseline
  3. Lower priority: further depth in 5x chains (chains 1-3 are COMPLETE; diminishing returns)

## Honest gap to v1 demo (5-7 weeks)

1. Define benchmark suite (substrate-strength tasks; defensible to skeptical reviewer) — 1-2 weeks; NOT STARTED
2. Build integrated pipeline (substrate + Llama-1B generation; cross-shard K-hop coordinator) — 2-3 weeks; Chain 3 v1 spec'd not built
3. Run head-to-head vs Llama-1B / Phi-2 / Mistral — 1-2 weeks; NOT STARTED
4. Document outperformance with crisp metrics — 1 week; NOT STARTED

## Where substrate SHOULD win at comparable parameter budget

| Task | Substrate advantage | Benchmark candidate |
|---|---|---|
| Factual recall at M=10^4-10^5 facts | Substrate stores; LLMs forget | LongMemEval / Loft / custom |
| Multi-hop verifiable reasoning | Per-hop Merkle audit | HotpotQA + audit overlay |
| Privacy-preserving retrieval (ZKL) | 23x advantage QUANTIFIED cycle 150 | Custom MIA suite |
| Continual learning at scale | 100% retention 120 sessions cycle 129 | Custom continual benchmark |
| Adversarial robustness | 6 attack types HP | Custom adversarial probe |
| Audit/verification | Zero LLM has this | EU AI Act Article 12 compliance test |

## Where LLMs win (don't compete)

- Open-domain generation
- Conversational coherence
- Non-grounded reasoning

## Action items per session

### Orchestrator
- Add "LLM head-to-head readiness" category to cap_map tracking
- Flag verdicts advancing benchmark goal prominently in cycle summaries

### Exp-Dev
- Prioritize integrated-pipeline cells over substrate-internal exploration
- Track queue depth in terms of "benchmark-readiness cells" vs other

### Research (me)
- Memory entry locked: `north_star_functional_system_beats_LLMs.md`
- Overnight loop prompt updated implicitly via memory read on every wake

---

**END.**

**Orchestrator + Exp-Dev:** Adjust your standing priorities accordingly. User authorized inter-session notes this evening; this is the strategic clarification all 4 sessions should align around overnight + tomorrow.

**User:** Memory locked at `north_star_functional_system_beats_LLMs.md`. All 4 sessions informed of north star reframe. 5-7 week path to v1 demo identified.
