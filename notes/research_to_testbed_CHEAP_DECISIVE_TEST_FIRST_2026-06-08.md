# Research -> Testbed: Cheap decisive test FIRST (validate WOW before live infra)

**From:** Research  **Date:** 2026-06-08 ~21:30 UTC
**Re:** Demo visualization drill flagged the highest-leverage operational insight.

## The insight

Before building expensive live infra (Cloudflare tunnel + Pythia serving + frontend + audit
chain UI + benchmark dashboard), build a **static HTML page** with 3 pre-cached Q&A pairs
showing substrate-augmented Pythia vs GPT-4o-mini, and validate it on real observers.

**Gate criterion:** 4/5 observers understand the value proposition in 30 seconds WITHOUT
explanation.

If this fails, FIX THE FRAMING before building anything live. Weeks of engineering wasted
if the static page doesn't communicate.

## Why this matters

Per failure-modes drill: "Isn't this just RAG?" is the highest-probability message destroyer.
Per visualization drill: "same model, different substrate" is the recommended framing (NOT
"substrate vs LLM"; that triggers the RAG comparison).

A static page tests whether the FRAMING works without needing live infra. Cheap. Decisive.

## What the static page should contain

3 pre-cached questions where substrate's value is visceral:
1. Multi-hop factual question (substrate-Pythia answers correctly with audit chain;
   GPT-4o-mini answers but no provenance)
2. Post-cutoff factual question (substrate has recent fact; GPT-4o-mini says cutoff)
3. Niche-domain question (substrate has it loaded; GPT-4o-mini doesn't or hallucinates)

For each:
- Left panel: substrate-augmented Pythia-1.4B answer + inline citations [1][2][3] + "Retrieved 3 facts in 0.4ms"
- Right panel: GPT-4o-mini answer + "Source: training data (unverifiable)"
- Cost row: $0 substrate vs $X gpt-4o-mini
- Audit chain expansion (click to see substrate's reasoning)

Page weight <= 2MB. LCP <= 1.5s. Mobile responsive.

## Recommended sequence

1. **Build static HTML page** (~2 hours; pre-cached responses; no live inference)
2. **Test on 5+ observers** (technical investors / customer types / friends-of-the-project)
3. **Iterate framing** based on what confuses or excites observers
4. **THEN build live infra** with validated framing

## Why not build everything in parallel

If the live demo's substrate-side answers are great but the FRAMING confuses observers,
the demo fails anyway. The static page is the cheapest test of framing.

If the static page wins observers' attention, then building live infra has validated demand.
If it doesn't, we save weeks of engineering.

## Cross-references
- Visualization drill: notes/research_drill_demo_visualization_ux_5x_2026-06-08.md
- Failure-modes drill: notes/research_drill_demo_failure_modes_5x_2026-06-08.md
- Panel A LIVE next-steps: notes/testbed_to_research_PANEL_A_LIVE_next_steps_2026-06-08.md
- Panel A LIVE RESPONSE: notes/research_to_testbed_PANEL_A_LIVE_RESPONSE_2026-06-08.md

---

**Testbed:** strong recommendation to interrupt Panel A hardening track briefly to build
the 2-hour static decisive-test page FIRST. Validates framing before building live UI.
Concurrent with Wikipedia 100K ingest already authorized. After static page passes observer
test, return to Panel A hardening with validated framing.

This is operationally the cheapest test of the demo's actual viability.
