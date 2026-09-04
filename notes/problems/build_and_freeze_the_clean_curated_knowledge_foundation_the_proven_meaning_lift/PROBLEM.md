---
priority: 4
review:
review_text:
---

# PROBLEM: the consolidation gate (owner-DONE P1) PROVED that admitting a CLEAN CURATED knowledge foundation (WordNet relations + curated SyntagNet + ConceptNet — an admissible offline static asset, NO external LLM) lifts the meaning channel a_s 0.2512→0.3178 (+0.067 CI-sep, raw-reading twin LOSES, MFS no-regression) — "the clean foundation before learner-on," delivered — but it was landed only as a GUARD, NOT wired as the reader's default meaning foundation. This is a PROVEN, glass-box, invariant-safe meaning lift that is currently STRANDED off the live reader. BUILD + VERIFY + FREEZE the clean curated knowledge foundation as a static offline asset and WIRE it as the meaning channel's default sense-signature source (through the consolidation gate + `diagnostic_context_wsd` + the P9 precision-weighting), so the live WSD/meaning consumers get the +0.067 CI-separated — and the SAME pipeline produces the TYPED stores the other capabilities need (sense-discriminative W for meaning; typed selectional preference for parsing/roles). Prove the live meaning consumers rise CI-separated with the raw-reading twin LOSING and no MFS regression — or a located negative naming why the curated foundation cannot be wired live.

**slug:** `build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift` — **opened:** 2026-09-04 by the strategy session (the STEP-1 win from the knowledge-lever consolidation `notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md`; the +0.067 P1 proved but never shipped). **status:** OPEN. Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM, NO transformer/batch training (a STATIC OFFLINE-BUILT FOUNDATION ASSET is admissible — owner 2026-08-16).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** The mission is the most brain-faithful substrate. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar — work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure — do not build the tractable thing and cite neuroscience after.
> 2. **REUSE — does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE — does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly — copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components — that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.

## 1. THE PROBLEM IN PLAIN LANGUAGE
We already proved that giving the reader a clean, curated knowledge base (standard dictionaries/thesauri of word relations, cleaned up) makes it noticeably better at picking a word's specific meaning — a solid, measured gain. But that knowledge base was only used to test the idea; it was never actually built into the live reader. The job: assemble that clean knowledge base once, check the gain reproduces, freeze it (it doesn't change at read-time), and plug it into the reader's meaning step so every read benefits. The brain does exactly this — it consolidates a stable store of word knowledge over a lifetime and consults it; it does not re-derive it on the fly. This is the cheapest, already-proven meaning win, and the same assembly line then produces the typed knowledge the grammar/role work needs.

## 2. WHY THIS ONE — a PROVEN, glass-box, invariant-safe lift, currently stranded
The consolidation-gate SOLVED (P1) measured it: curated WordNet+SyntagNet+ConceptNet through the brain-faithful reader → a_s 0.2512→0.3178 (+0.067 CI-sep [0.048,0.087]), raw twin LOSES, MFS no-regression. But P1 landed only the admission GUARD (`hdlab/consolidation_gate.py`), not the foundation itself — so the +0.067 is off the live reader. It is the STEP-1 move in the knowledge-lever strategy (build+freeze the clean foundation BEFORE the online learner), it needs NO owner decision (glass-box, invariant-safe, unlike the P9 rare-sense route), and its pipeline is the shared factory for the typed stores the parser/role problems need.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: word meaning is a CONSOLIDATED, stable neocortical store built by complementary-learning-systems consolidation (McClelland-McNaughton-O'Reilly 1995) and CONSULTED at comprehension (not re-derived per read); the store is a graph of typed lexical-semantic relations (ATL hub — Lambon-Ralph; WordNet/ConceptNet as the curated proxy). The sense signature is the diagnostic-context readout over that store (the landed `diagnostic_context_wsd` + the P9 precision-weighting). OUR-INVENTION-under-test: the exact curated-resource merge + cleaning, the freeze/serialization, the wiring point into the meaning channel. Sweep, do not adopt. REUSE (do NOT re-derive): `hdlab/consolidation_gate.py` (the admission gate + the raw-vs-consolidated guard), `hdlab/diagnostic_context_wsd.py` (the readout + gamma/topk), `hdlab/cls_growth.py`, the P1 experiment cells (`exp_consolidation_gate_v1` + the curated-foundation arm), the shipped WordNet/SyntagNet/ConceptNet resources.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — P1 SOLVED, strict document-disjoint SemCor subordinate, n=2676):** curated clean foundation a_s 0.2512→0.3178 (+0.067 CI-sep); raw-reading twin regresses −0.033; MFS no-regression; the consolidation gate cleans + the guard blocks below-gloss admission; grounding ruled out; the deepest ceiling (rare senses) is the frozen input representation (the P9 route, a SEPARATE problem).
- **INFERRED (you must measure):** whether the curated foundation, BUILT + FROZEN as a static asset and WIRED into the live meaning channel, delivers the +0.067 to the LIVE WSD/meaning consumers CI-separated (raw twin losing, no MFS regression), and whether the same pipeline emits the typed selectional-preference store; the residual + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md` (the consolidation) + `notes/problems/build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner/SOLVED.md` (the +0.067 + the curated-foundation arm + the located negatives) IN FULL; `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; read `hdlab/consolidation_gate.py`, `hdlab/diagnostic_context_wsd.py`, `hdlab/cls_growth.py`, the P1 cells.
- Reproduce first-hand: the +0.067 curated-foundation lift (the can-fail baseline this must ship live).

## THE BAR (can-fail; CI-separated; the raw twin must lose)
PASS = a clean curated knowledge foundation, BUILT + VERIFIED + FROZEN as a static offline asset (NO LLM, NO transformer/training) and WIRED as the meaning channel's default sense-signature source, such that the LIVE WSD/meaning consumers rise CI-separated toward the +0.067, with the raw-reading info-free twin LOSING and NO MFS regression. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the curated foundation cannot be wired live without regression (with the named cause) — is a FULL PASS. Strategy lands the Q111 wire.

## ALREADY TRIED / DO NOT REDO
- The consolidation GATE + the raw-vs-consolidated guard are LANDED (P1, `hdlab/consolidation_gate.py`) — REUSE them; this is the FOUNDATION build + freeze + wire, not re-deriving the gate.
- RAW reading-derived growth is a located NEGATIVE (regresses) — this is CURATED clean knowledge, not reading-growth; the online reading learner is the SEPARATE `grow_broad_coverage...` problem (step 2).
- GROUNDING (perceptual spokes) is ruled out as the crosser — do NOT re-test it.
- Do NOT train a contextual encoder / use an external LLM (the invariant; that is the open P9 owner decision, not this problem).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/consolidation_gate.py`, `hdlab/diagnostic_context_wsd.py`, `hdlab/cls_growth.py`, the P1 cells + the WordNet/SyntagNet/ConceptNet resources. Ship the frozen foundation to `data/frontend_assets/`. Measure on the live WSD/meaning consumers + the SemCor a_s. Strategy lands the Q111 wire. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote the +0.067 as achieved live until it is measured through the WIRED reader (P1 measured it through the experiment reader).
- Do NOT conflate this with the online learner (raw growth regresses; this is the CURATED frozen foundation).
- Do NOT use an external LLM / train an encoder (the invariant; the P9 owner decision).
