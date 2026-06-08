# Research -> Testbed: v1 demo BUILD PLAN response — strong plan; 2 clarifications

**From:** Research  **Date:** 2026-06-08 ~13:00  **Re:** testbed_v1_demo_BUILD_PLAN_2026-06-08.md
proposal pending user signoff.

## Research's view

**The plan is strong.** Specifically I agree with:
- Pre-audit week (smart; acknowledges porting risk)
- Risk register honesty (Tier-5 KV fallback + spaCy fallback for NER)
- Architecture: Next.js + Modal + Vercel (reasonable; Modal for substrate GPU is the right call)
- Week-by-week structure with concrete deliverables + acceptance gates
- Budget ($250-300/month)

Research is NOT signing off (that's user's call). Filing this so Testbed has Research's
position when user reviews.

## 2 clarifications for Testbed

### Clarification 1: Tier-5 substrate-KV (PP-135) production readiness

You flagged "production-ready or research-only?" as a Week 2 dependency. Honest answer:

**PP-135 status:**
- MVE GREEN at Pythia-160M (D1) recall=1.000 at M=2000 = 31x context expansion
- D2 Pythia-1.4B HP same recall = not base-model-specific
- D3 cross-shard substrate-KV HP routing=0.999 at ndom=40 = full architecture validated

**BUT:** these are RESEARCH cells, not production-hardened. To deploy in demo:
- Pythia-1.4B as inference backend (~6 GB VRAM = fits Modal A10/T4)
- Substrate-KV layer integrated with model attention (research code; ports cleanly per port plan)
- Per-query GPU compute cost was flagged by my GPU K-hop infra 2x drill — depends on
  query traffic

**Two paths for v1 demo (in priority order):**

PATH A (PREFERRED if Tier-5 KV ports cleanly):
- Substrate-KV backend serving gpt-4o-mini retrieval queries
- Pythia-1.4B with substrate-KV layer = retrieval engine
- gpt-4o-mini consumes substrate-KV results as context
- Architecture story is intact; demonstrates Tier 5 in production

PATH B (FALLBACK if Tier-5 KV not production-ready in time):
- K-hop substrate retrieval injected as in-context (simpler integration)
- Same substrate primitives (PP-119/123/125/127 etc.)
- Architecture story slightly muted (no Tier 5 visible) but still strong
- Substrate stats sidebar can still claim "Tier 5 substrate-as-attention-backbone
  validated; v1 demo uses K-hop retrieval as initial integration"

Recommendation: build PATH A first; have PATH B as fallback per your risk register.

### Clarification 2: "Substrate wins visibly on >=3 of 5 random queries" acceptance gate

Week 5 acceptance gate says: "5 random queries on demo work cleanly; substrate wins
visibly on >=3 of 5."

**Honest expectation per the vertical analysis:**
- On corporate-recency queries (post-cutoff facts): substrate wins ~80-90% (categorical
  LLM cutoff disadvantage)
- On general Wikipedia queries: substrate wins ~30-50% (LLMs are trained on Wikipedia)
- On multi-hop queries WITH structured KB available: substrate wins via audit chain
  rendering (categorical even if bare answer is similar)
- Overall ~50-60% win rate on truly random queries; >75% if user types corporate
  queries

If acceptance gate is "≥3 of 5 random queries," that may be tight. Suggested adjustments:
- Either: relax to "≥3 of 5 corporate or multi-hop queries" (substrate's strength
  domain)
- Or: keep "≥3 of 5 random" but accept this is honest mixed win rate; demo's wow
  moments + audit + cost wins compensate for any "tie" queries

Substrate's PITCH is not "always beats LLM" — it's "categorically does things LLM
cannot" (add/delete/recency/audit). Acceptance gate should reflect that.

## Open question for user (not Testbed)

The plan asks user to sign off. From Research's side, the substrate is empirically
ready (cycle 185 PP-136 full architecture lock). User decisions needed:
- API key allocation (OpenAI + Anthropic + Crunchbase)
- Monthly budget signoff ($250-300)
- Tech stack signoff (Next.js + Modal + Vercel)
- Demo wow moment final priority (3 primary + 2 secondary; can be re-prioritized)

## What Research will do during demo build

- Continue background research drills (sparse-VALUE / fact-representation rethink already
  filed for v2.0+ roadmap; don't gate demo)
- Synthesize cycle reports as they land
- Flag any newly-discovered substrate capabilities that should ship in v1 demo
- Stand by for Testbed unblocks (architecture clarifications; substrate primitive
  questions)
- Coordinate with Exp-Dev on benchmark metric delivery to feed your dashboard

## Cross-references
- Demo SPEC (Research): notes/research_to_testbed_v1_demo_SPEC_2026-06-08.md
- Build plan (Testbed): notes/testbed_v1_demo_BUILD_PLAN_2026-06-08.md
- Exp-Dev handoff (Exp-Dev): notes/exp_dev_to_testbed_v1_demo_app_build_handoff_2026-06-08.md
- Cycle 185 full architecture lock: notes/orchestrator_to_research_results_summary_2026-06-08_cycle185.md

---

**Testbed:** plan is solid; Research's two flags above (Tier-5 KV production path + win
rate acceptance gate). Standing by for user signoff. After signoff, I'll be available
for clarifications as you do the audit week.
