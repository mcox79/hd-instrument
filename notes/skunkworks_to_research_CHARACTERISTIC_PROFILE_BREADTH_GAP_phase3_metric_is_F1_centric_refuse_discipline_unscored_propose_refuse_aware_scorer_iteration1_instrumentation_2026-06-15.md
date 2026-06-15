# SKUNKWORKS (Auditor) -> Research (Director): MEASUREMENT-BREADTH FLAG (responds to USER strategic question "is it measuring all the substrate characteristics we tested re: LLM comparisons?"). Phase 3 v0 measures F1 + soundness-invariants but NOT refuse-discipline; the refuse/gap questions I authored sit UNSCORED. Propose adding the refuse-aware scorer as cheap Iteration-1 instrumentation (questions already exist).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** USER asked whether the substrate is measuring its own process quality across the LLM-comparison characteristics, or just retrieval. Honest answer below + a cheap fix.

## The honest state of WHAT WE MEASURE
This session optimized ONE axis hard -- held-out retrieval F1 (M4d) -- which is correct per 11th rule (substrate-on-its-own first) but is only ONE substrate characteristic. Mapping to the LLM-comparison characteristics we established in prior sessions:
- **Retrieval F1**: heavily measured (M4d; held-out; commit-and-reveal). GOOD.
- **Soundness / capability_preservation / axiom-termination**: MEASURED + ENFORCED as live invariants in Phase 3 v0 (CHTV + L6-PROOF gate every edge; capability_preservation rolling check; rollback on regression). GOOD -- this is the categorical differentiator and it is now operationalized, not just asserted.
- **Refuse-discipline** (substrate refuses what it cannot ground; LLM hallucinates): **AUTHORED BUT UNSCORED.** I put 7 gap/refuse-control questions in 56d + 6 in 56d-v2 (Galois theory, Riemann hypothesis, Navier-Stokes, Yoneda, Banach-Tarski, FLT, four-color, Noether, Hahn-Banach, Sylow, Zorn, p-adic, Mandelbrot -- all verified absent from substrate). The current M4d scorer SKIPS empty-gold questions, so refuse-discipline is currently MEASURED NOWHERE. This is THE priority LLM-differentiator and it is dark.
- **LLM head-to-head (CH-P6 soundness gap; "0 false-accepts vs Qwen 3/12 hallucinated")**: CARRIED FORWARD from prior sessions, NOT re-measured this session as the substrate changed (26272 -> 26286 atoms).

## Why this matters now
Phase 3 v0's success metric (DECISION 67) is M4d F1 lift on 56d-v2 + soundness invariants. That is a strong, defensible metric -- but it is F1-centric. The substrate-product story is broader than retrieval F1: it is "retrieval F1 (in-distribution) + sound-by-construction growth + refuses-what-it-cannot-prove." Two of those three are measured; refuse-discipline is not. As Phase 3 grows the graph, a key honest question is: does refuse-discipline HOLD (substrate still returns nothing on Galois theory after it has grown 100s of edges), or does graph-growth start producing spurious confident retrievals on out-of-substrate topics? That is a drift/safety signal the Auditor should be watching -- and it is exactly an LLM-differentiator.

## PROPOSAL (cheap; the questions already exist)
Add the refuse-aware scorer (the deferred 61b; ~30-60 min Exp-Dev) as Iteration-1 instrumentation:
- For the 13 gap questions (7 in 56d + 6 in 56d-v2... 56d-v2 gap RESERVED until final), score: does the system return EMPTY / below-confidence-threshold? F1_present already gives 1.0 for empty-pred on empty-gold; needs the scorer to NOT skip empty-gold + a confidence/abstention threshold on retrieval.
- Report a refuse-discipline number per iteration alongside F1: "substrate refused N/7 out-of-substrate topics."
- Track it as a DRIFT signal in my Iteration-1 audit (does refuse-rate degrade as edges are added? = spurious-confidence drift).

This makes Phase 3's metric MULTI-AXIS (recall-F1 + refuse-discipline + soundness-invariants) = the full substrate-characteristic profile the USER asked about, not F1 alone. Low cost, high positioning value, and it puts the priority LLM-differentiator back under measurement.

## Also recommend (lower priority, when bandwidth)
Periodically RE-RUN the CH-P6-style LLM soundness head-to-head as the substrate grows, so the "categorically different from an LLM" claim stays MEASURED on the current substrate state, not asserted from a prior snapshot.

I am NOT blocking Phase 3 Iteration 1 -- it should proceed. This is a parallel instrumentation add. I will fold refuse-rate into my Iteration-1 drift audit if Exp-Dev exposes the gap-question scores.

Tag: CHARACTERISTIC_PROFILE_BREADTH_refuse_discipline_unscored_propose_refuse_aware_scorer -- SKUNKWORKS (Auditor)
