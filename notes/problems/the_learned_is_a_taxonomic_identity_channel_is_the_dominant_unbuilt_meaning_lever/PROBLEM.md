---
slug: the_learned_is_a_taxonomic_identity_channel_is_the_dominant_unbuilt_meaning_lever
status: INTEGRATED
review:
review_text:
---

# PROBLEM: the reader's meaning channel has a GROUNDED spoke and a distributional spoke, but NO is-a / TAXONOMIC IDENTITY channel learned from reading — and the just-integrated `measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage` solver proved (on the LIVE sense-assignment decision, SimLex gold) that the taxonomic channel is **the single dominant meaning lever**: taxonomic AUF-MRR **0.650 vs grounded-distinctive 0.188 (+0.488 CI[+0.360,+0.620])**, grounded+taxonomic **0.657** (best), info-free twin 0.006 — supplying is-a identity takes the live meaning decision from ~15% to ~65% of achievable. That lever-proof used WordNet definitional features (partly CIRCULAR with SimLex = NOT a landable number). The BRAIN-FOUNDATIONAL way to BANK it is already PROTOTYPED and beats grounded WITHOUT WordNet: a LEARNED property-covariance is-a channel (Rogers-McClelland ordered SVD over read property predications + Levy-Goldberg dependency contexts + genus-centroid differentia) scores AUF **0.260 vs grounded 0.188**, twin losing — a real learned-from-reading is-a signal. BUILD the brain-foundational learned is-a/taxonomic identity channel, GROW it by reading (it builds on the landed directional grow-by-reading store), and fuse it into the live meaning read so the sense decision approaches the taxonomic ceiling — NO WordNet at inference (circular with the eval), glass-box, NO external LLM.

**slug:** `the_learned_is_a_taxonomic_identity_channel_is_the_dominant_unbuilt_meaning_lever` — **opened:** 2026-09-10 by the strategy session, from the integrated `measure_end_to_end...` solver (its NEXT-STEP #3: "THE biggest optimization — quantified: the is-a/taxonomic identity channel is the dominant lever") + the standing knowledge north-star (is-a learned-from-reading is the dominant meaning lever; NO WordNet at inference — circular with SimLex). **status:** OPEN. Distinct from the INTEGRATED `expand_the_clean_semantic_memory_foundation_with_world_knowledge` (which ingests CURATED WordNet is-a offline) — this LEARNS is-a from reading, the BF route that escapes the SimLex circularity. Strategy lands any hdlab wire (Q111, witnessed). Glass-box, NO external LLM / NO WordNet at inference.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL, and spaCy/GLUCOSE/MAVEN + any off-the-shelf parser/dataset/model
> are NOT brain-foundational -- never reach for a convenient/easy tool without careful consideration (a vetted static
> offline FOUNDATION asset is admissible; an external tool AT INFERENCE or a fitted/convenient stand-in is a DEFECT
> that BLOCKS).**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When the reader decides what a word means, it leans on two signals: what the word feels/looks like (grounded) and what words it appears near (distributional). It has no signal for **what KIND of thing the word IS** — its place in the is-a hierarchy (a robin IS-A bird IS-A animal). That "is-a identity" turns out to be the single biggest missing piece: when the reader was given it (in a proof measurement), its meaning decisions jumped from getting ~15% of the way to ~65% of the way to the best achievable. The catch: that proof used a dictionary (WordNet), which is circular with the test, so it doesn't count as a real result. But the brain doesn't read a dictionary — it LEARNS what kind of thing something is from how it's described and used across everything it reads (robins fly, have feathers, lay eggs → they cluster with birds). A first learned-from-reading version already beats the grounded signal without any dictionary. The task: build that learned is-a channel properly, grow it by reading, and fuse it into the live meaning decision.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
It is **the dominant meaning lever, quantified** on the LIVE sense-assignment decision (`measure_end_to_end` NEXT-STEP #3): taxonomic 0.650 vs grounded 0.188 (**+0.488 CI-sep**); the meaning channel is at ~15% of achievable without it, ~65% with it. It is UNBUILT in a brain-foundational form: the curated-WordNet ingest (`expand_the_clean_semantic_memory_foundation`, integrated) proves the *lever* but is CIRCULAR with SimLex (WordNet definitional features) — a lever-proof, not a landable number, and NOT brain-foundational at inference (the brain doesn't consult WordNet). The BF route is LEARNED-FROM-READING (Rogers-McClelland 2004 semantic-cognition property-covariance = the brain's is-a acquisition; Levy-Goldberg 2014 dependency contexts; genus+differentia = Collins-Quillian hierarchy), which is already prototyped BEATING grounded WITHOUT WordNet (AUF 0.260 vs 0.188, twin losing). This is the meaning cluster's #1 open lever (CROSS_SOLUTION map Target 2) and the standing knowledge north-star.

## 3. MEASURED vs INFERRED
- **MEASURED (on disk):** taxonomic AUF-MRR 0.650 vs grounded 0.188 (+0.488 CI-sep), grounded+taxonomic 0.657 best, twin 0.006 (the LEVER-PROOF, WordNet-circular — `exp_meaning_fusion_taxonomic_lever_v1.py`); the LEARNED property-SVD is-a channel (NO WordNet) beats grounded AUF 0.260 vs 0.188, twin losing (the BF prototype, referenced in the `measure_end_to_end` SOLVED). The directional grow-by-reading store is landed (`reading_grounding_loop.track_directional_context_counts`).
- **INFERRED (to prove or refute WITH A NUMBER):** that the learned is-a channel, GROWN by reading (more volume) + a read-edge genus for the differentia, becomes CI-clean over grounded and approaches the taxonomic ceiling on the LIVE sense decision — WITHOUT WordNet. Do not assume the grow closes the gap; measure the growth curve.

## 4. ALREADY TRIED / DO NOT REDO
- **Do NOT re-ingest curated WordNet is-a** — that is `expand_the_clean_semantic_memory_foundation` (integrated) + it is CIRCULAR with SimLex (a lever-proof, not a landable BF number). No WordNet at inference.
- The property-SVD is-a prototype (Rogers-McClelland + Levy-Goldberg) already BEATS grounded without WordNet — REUSE/extend it, don't re-derive. Genus-by-clustering was measured NEGATIVE (needs READ is-a edges, not clustering) — do not re-attempt clustering-genus.
- Build ON the landed directional grow-by-reading store (`ConceptSpace` ROUTE-B); the grow-by-reading rare-sense lever (`grow_broad_coverage...`, integrated) is a DIFFERENT (rare-sense-experience) lever — this is the is-a IDENTITY axis.

## 4b. RESEARCH FOLDED IN (strategy drill, 2026-09-10) — read `RESEARCH_bf_isa_acquisition.md` in this folder
A BF research drill de-risked the central open question (how the brain acquires DIRECTED is-a/genus edges from reading). Headline for your FIRST build step:
- **The prototype's 0.26 is missing the DIRECTED, LABELLED genus EDGE, not reading volume.** Property-covariance / ordered-SVD (Rogers-McClelland; Saxe-McClelland-Ganguli, PINNED) yields category STRUCTURE (clusters) but NOT directed superordinate edges — exactly why genus-by-clustering was negative. The 0.65 lever (WordNet) IS directed is-a edges.
- **BF first build:** extract read is-a edges from the IN-SUBSTRATE PARSE via copular / appositive / set-inclusion predication ("a robin is a bird", "robins and other birds", "birds such as robins" — the Hearst family, which IS brain-foundational-COMPATIBLE as *evidence a reader uses*; reuse `causation_typing`'s construction extraction), accumulate them GRADED + reliability-weighted + cross-occurrence-confirmed into the landed directional store (CLS/Bayesian, NOT hard-count; Probase noisy-OR / NELL agreement is the BF-compatible confirmation rule), then run the SAME ordered SVD on THAT is-a-edge PPMI matrix (not the distributional matrix). Direct precedent: Roller-Kiela-Nickel 2018 SVD-densified Hearst-PPMI jumped BLESS AP 0.45→0.76. Compose genus (read edge) + differentia (property-SVD) = Collins-Quillian. SWEEP pattern weights / agreement threshold / rank / mix / volume.
- **Risks (in the note):** OOV is the known SVD-pattern limit (backfill with distributional); pooled edges are noisy (polysemy/sense-conflation → attach to the context-selected sense; metaphorical copula; parse errors → reliability + cross-occurrence weighting). NO WordNet at inference; no clustering-genus; no hard-count.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: the `measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage` SOLVED (its NEXT-STEP #3 + `exp_meaning_fusion_taxonomic_lever_v1.py` + the property-SVD is-a prototype), `notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md`, `hdlab/reading_grounding_loop.py` (the directional grow-by-reading store + `distributional_meaning_channel` PPMI+SVD), `hdlab/grounded_similarity.py` + the meaning fusion path. Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the meaning-channel entries) + `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` Target 2. Run `python tools/reader_capabilities.py`. Understand the meaning organs before proposing the channel.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
Build the LEARNED is-a/taxonomic identity channel (Rogers-McClelland property-SVD + Levy-Goldberg contexts + genus-differentia, NO WordNet at inference), GROW it by reading, and fuse it into the live meaning read; SHOW the sense-assignment decision rises **CI-separated over the grounded floor on the live decision (SimLex-held-out), with the info-free twin LOSING**, and report the grow-by-reading curve toward the taxonomic ceiling (0.65) — OR a rigorous LOCATED NEGATIVE naming exactly why the learned is-a channel cannot approach the ceiling without WordNet (with a number; the brain's actual mechanism faithfully built). INVARIANT: recall path byte-identical; NO WordNet / NO external LLM at inference.

## 7. FILES AND ENTRY POINTS
`hdlab/reading_grounding_loop.py` (the directional grow-by-reading store), `hdlab/distributional_meaning_channel.py` (PPMI+SVD), `hdlab/grounded_similarity.py` + the meaning fusion path, `hdlab/typed_spokes.py` (the C5 is-a closure, for comparison NOT inference); `experiments/exp_meaning_fusion_taxonomic_lever_v1.py` + the property-SVD is-a prototype (from `measure_end_to_end`); `notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md`; the board `experiments/exp_situation_model_qa_modern_v1.py` (wic + the meaning dims).

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use WordNet (or any dictionary/ontology) AT INFERENCE — it is circular with the SimLex eval + not brain-foundational (a static offline FOUNDATION asset is fine to BUILD from, but the inference-time channel must be learned-from-reading). Do NOT re-run genus-by-clustering (measured negative). Do NOT re-ingest curated is-a (that is the integrated `expand_the_clean_semantic_memory_foundation`). Do NOT claim "converged" on engineering variations; the bar is the brain's learned is-a acquisition approaching the taxonomic ceiling by reading — or a numbered located negative.
