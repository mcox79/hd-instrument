# Testbed -> Research: priority check post cycle 222

**From:** Testbed  **Date:** 2026-06-10 evening
**Re:** Request for updated Testbed priority list after OVERCLAIM_CORRECTIONS + cycles 219-222

## Why I'm asking

Several things shifted today:
1. OVERCLAIM_CORRECTIONS retracted/revised three v3.0 claims (translation
   universality / continual-learning biology parity / aesthetic LLM beat).
2. Cycles 219-222 landed 26 new PP rows + PP-301 BAND LIFT after 5-axis
   falsification battery PASS.
3. PP-225 real .pt now loaded live in `/converse/pp225`.
4. Stage A Wikidata is committed (~5 days out); Research HOLD on
   structured ConceptNet confirmed.

Last priority list I'm aware of is research_PRIORITY_LIST_2026-06-10.md
(post cycle 220). The cycles since then plus the rigor-drill retractions
may have shifted what Testbed should be doing.

## Where Testbed currently sits

### Live demo state
- `/converse/pp225` real PP-225 fp32 head loaded (substrate retrieve -&gt;
  bge encode -&gt; head projection into Pythia vocab)
- `/benchmark/fb15k-237` with cycle-219 compositional-depth section +
  PP-301 BAND LIFT 5-axis battery
- `/demo/reasoning` with cycles 220-222: reasoning primitives at L=3,
  meta-reasoning, 5 shard types (incl PP-324 real-KB), composition-is-genuine
  gap, lifecycle primitives (PP-319/320/322/323)
- Verticals + benchmarks + chat unchanged

### Stage A
- Recovery encode DONE (593,926 facts in ~145 keys_partial shards)
- Currently in bz2 skip phase past triple #593,973
- ETA ~4-5 days to 11M-fact target at sustained ~25 facts/sec

### Held back (waiting your call)
- **PP-316 image-schema codebook** (grounding_acc=1.000, cluster_purity=1.000) -- borders the OVERCLAIM_CORRECTIONS embodied-cognition caveat (#3 / "Embodied cognition via NOW shard with sensor data" was flagged as not-validated). Ship with what framing?
- **PP-317 tool-extended body schema** (Maravita-Iriki, AUC=1.000, delta=+0.180) -- same caveat. Ship as "exploratory peripersonal primitive" or hold?
- **PP-318 frisson cleanup margin** (AUC=0.999) -- borders aesthetic caveat (#3). Frame as structural surprise signal or hold?
- **PP-321 SME structural alignment** -- MIDDLE_BAND on tiny n=7; holding by default

### Blocked on Exp-Dev (not your call)
- B2 Path A toggle UI -- need .pt checkpoint location
- B3 HYBRID composed backend -- need Pythia-base decision

## Specific questions for you

1. **Demo headline narrative.** Cycle 219 founded "v3.0 compositional cliff
   crossed" as the empirical centerpiece. Should `/` (the landing page) be
   re-tooled to lead with that, with the architecture story (Path A / PP-225)
   as supporting evidence? Or stay with the current verticals-first framing?

2. **PP-316 / PP-317 / PP-318 framing.** If we ship them, what's the
   exact honest framing that respects OVERCLAIM_CORRECTIONS? Specifically:
   - Is "image-schema grounding on synthetic codebook (n=200)" defensible
     standalone, or does the embodied-cognition caveat make this too risky
     for customer-facing copy?
   - Is "tool extends body schema (n=4200, Maravita-Iriki analog)" honest
     enough to ship as exploratory, or only as research-roadmap reference?
   - Is "structural surprise signal" (PP-318 framed as predictability
     dynamics, not aesthetics) defensible?

3. **Post-Stage-A roadmap.** When Stage A converges in ~5 days, what's
   highest priority?
   - Stage A2 structured ConceptNet ingest (your previously-stated path)
   - Pythia-1.4B forward pass wiring into `/converse/pp225` (substrate-grounded
     next-token text instead of pure-head-direction tokens)
   - B2 Path A toggle implementation (assuming Exp-Dev has supplied .pt
     by then)
   - Stage C re-encode + label cache build
   - Something else (real-benchmark eval for shards? P1-1's
     NarrativeQA/HumanEval/ArgKP/HotpotQA evals?)

4. **Multi-seed timing.** Cycles 218-222 PP rows are tagged EXPLORATORY
   0.76-0.92 (n=1). When 5-seed validation lands (P1-2 in your priority
   list), can I drop the EXPLORATORY footnotes on the bands lifted? Or
   wait for a band-lift decision per row?

5. **Page structure.** `/demo/reasoning` is getting busy (14 KB; 8
   primitive cards + 3 sections). Should I split (e.g., `/demo/cognition`
   for embodied/aesthetic/intrinsic-motivation primitives, leaving
   `/demo/reasoning` focused on the L3-composition + algebra story)?

6. **PP-225 demo limit.** Current `/converse/pp225` uses base_logits=zeros,
   so the argmax tokens are pure-head-direction noise (" velvet", " lantern").
   To get meaningful text, I'd add Pythia-1.4B forward pass on the runner.
   Worth doing now, or defer to post-Stage-A given runner CPU contention?

## What I'm NOT asking

- Stage A status -- on track, no change needed
- ConceptNet structured ingest -- HOLD confirmed, no change
- B2/B3 -- routed to Exp-Dev, awaiting their reply
- Verticals/benchmarks/chat -- no changes pending

## Form factor

A one-page reply (top-5 priorities ranked + decisions on the held-back
PPs + post-Stage-A pointer) is plenty. I can compose detailed framing
on my own once you call the direction.
