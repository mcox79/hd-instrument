---
priority: 4
slug: the_common_noun_binder_is_string_identity_not_the_brains_content_addressable_typed_coref
status: OPEN
review:
review_text:
---

# PROBLEM: the reader's live definite-COMMON-NOUN coreference binder (`commonnoun_binder`) links "the dog"/"the man" to its antecedent by HEAD-LEMMA STRING MATCH + a modifier veto + an event-centrality tie-break — an OUR-INVENTION heuristic that is one of the 8 live NOT-brain-foundational organs and that MEASURES WORSE than the trivial baseline it should beat (0.4904 vs plain string-identity 0.5412, reader CATALOG C2). The brain does not resolve reference by string identity; it binds by CONTENT-ADDRESSABLE graded competition over typed entity representations (the anaphor is a retrieval cue; the antecedent is the best-matching entity by type + salience + recency, settled softly, not filtered by a shared surface string). The brain-foundational replacement already exists as a landed organ (`typed_coref`, content-addressable typed binding). Make the C2 common-noun binding brain-foundational: route common-noun coreference through the typed content-addressable binding, LIVE, and show it beats the string-identity floor on the honest de-leaked slice — or a rigorous located negative. Glass-box, NO external LLM at inference.

**slug:** `the_common_noun_binder_is_string_identity_not_the_brains_content_addressable_typed_coref` — **opened:** 2026-09-10 by the strategy session, from the BF-certification of the live set (`commonnoun_binder` is one of the 8 live NOT_BF organs) + the owner directive "get the substrate to 100% BF UPCHAIN first" (coref is upstream of the whole situation/reasoning layer). **status:** OPEN. Strategy lands any hdlab change (Q111, witnessed); the solver builds the live route-through + the witness in `experiments/`, `verification/`, and this folder. Glass-box, NO external LLM at inference (the invariant). MEASURE ON THE HONEST DE-LEAKED FLOOR — never the gold-coref inheritance peek.

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
When the reader meets "the dog" and has to decide which dog, it currently checks whether an earlier phrase had the same head word ("dog") and, if so, links them — with a couple of hand-tuned tweaks. That is matching by spelling, and it is actually worse than just saying "same word = same thing." The brain does something different: it uses the phrase as a cue and lets the best-matching entity in memory answer, weighing what KIND of thing each candidate is, how recently it was mentioned, and how central it is — a soft competition, not a spelling filter. So "the animal" can pick up an earlier "dog" (no shared word) and "the black dog" need not merge with "the other dog." We already built the brain-like version as a separate organ; this problem is to make the reader actually USE it for common-noun reference, and show it beats the spelling baseline on honest data.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate + the owner's "100% BF upchain first"
`commonnoun_binder` is one of the **8 live NOT_BF organs** (`notes/bf_status_registry.jsonl`): head-lemma STRING MATCH + modifier veto + event-centrality tie-break, an OUR-INVENTION that the reader CATALOG (C2) measured at **0.4904, BELOW plain string-identity 0.5412** — a placeholder that loses to the trivial baseline. Coref is UPCHAIN of the entire situation/reasoning layer (entities feed roles, events, causal, ToM), so a non-brain-faithful binder degrades everything downstream. The brain-foundational mechanism — content-addressable graded binding over TYPED entities (the anaphor cues retrieval; type+salience+recency compete softly) — is already a landed organ (`typed_coref`), and typed common-noun coref has prior honest-floor wins. This is a high-leverage, low-invention BF-upchain fix: retire the string-identity placeholder, route the live C2 decision through the typed content-addressable binding.

## 3. MEASURED vs INFERRED
- **MEASURED (on disk, verified 2026-09-10):** `commonnoun_binder` 0.4904 < string-identity 0.5412 on the C2 slice (reader CATALOG); **`hdlab/typed_coref.py` already WINS on its instrument** — `TypedCorefResolver(bridge=True, bridge_write=False, type_comparator="typed_spokes")` common_noun_coref **0.5671 vs same-head string-identity 0.5412 (+0.0259 CI-sep)**, +0.0792 over the URG incumbent, info-free twin LOSES, pronoun/kb byte-identical (its docstring; GUM modern TEST n=2855). Its 4 brain-faithful levers: typed-card nominal-dominant identity, NON-writing Nref type bridge (the WRITE is the cost, not the resolution), typed-spokes seed (`coref_type_license`), consumer-specific `kb_eids` merge view. **The organ SELF-FLAGS the exact remaining task:** "re-porting `resolve_doc` onto the live `hdlab.coref.parse_litbank_conll` dict stream (live-reader deployment) is a separate, fidelity-risky follow-on" — THAT live re-port (with the honest de-leaked no-regress) is this problem.
- **INFERRED (to prove or refute WITH A NUMBER):** that routing the LIVE C2 common-noun binding through `typed_coref` beats the string-identity floor on the HONEST de-leaked slice with no downstream regress. Measure on the de-leaked floor (the gold-coref inheritance leak is a known confound — never inherit gold cluster IDs).

## 4. ALREADY TRIED / DO NOT REDO
- `typed_coref` is BUILT (do not re-derive it); typed common-noun coref was promoted with honest-floor wins. The gap is the LIVE re-port: `commonnoun_binder` is still what `situation_predict` calls. Do NOT re-benchmark the string-identity binder as if it were a candidate; it is the component being retired.
- The gold-coref inheritance leak (`replace_the_entity_gate_gold_coref_inheritance…`) is the measurement confound — use the de-leaked floor, do not re-discover the leak.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/typed_coref.py` (the REUSE target), `hdlab/commonnoun_binder.py` (the organ being replaced), the `situation_predict` C2 call site in `hdlab/situation_reader.py`, and the sibling coref organs (`graded_coref_pick`, `coreference_resolver`, `event_centrality_coref`). Read the reader CATALOG C2 entry + `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` Target 3 + the typed-common-noun-coref prior SOLVED IN FULL + `notes/BRAIN_FOUNDATIONAL_AUDIT.md` E3. Run `python tools/reader_capabilities.py` for the live coref wiring. Understand ALL the coref organs before proposing the route-through.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
Route the LIVE C2 definite-common-noun binding through the typed content-addressable competition (`typed_coref`) replacing the string-identity heuristic, and SHOW it beats the string-identity floor **CI-separated on the honest de-leaked C2 slice** (info-free twin LOSING) with **no downstream board regress** (coref / common_noun_coref / who_did_what dims) — OR a rigorous LOCATED NEGATIVE naming exactly why typed binding cannot beat string identity on the reader's own metric (with a number; the brain's actual mechanism faithfully built). INVARIANT: the recall path + non-C2 consumers byte-identical off the changed decision; no external tool/LLM at inference.

## 7. FILES AND ENTRY POINTS
`hdlab/typed_coref.py`, `hdlab/commonnoun_binder.py`, `hdlab/graded_coref_pick.py`, `hdlab/coreference_resolver.py`, `hdlab/event_centrality_coref.py`; the `situation_predict` C2 call site in `hdlab/situation_reader.py`; the board `experiments/exp_situation_model_qa_modern_v1.py` (coref / common_noun_coref dims); `notes/bf_status_registry.jsonl` (the `commonnoun_binder` NOT_BF entry to retire); the typed-common-noun-coref prior problem folder + `notes/problems/replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering/` (the de-leak).

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT re-quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT measure on the gold-coref-inheritance floor (a leak — use the de-leaked slice). Do NOT re-derive `typed_coref` (built) or re-benchmark the string-identity binder as a candidate (it is being retired). Do NOT reach for an external coref model at inference (NOT_BF). Do NOT claim "converged" on engineering variations; the bar is the brain's content-addressable typed binding, live, beating the string-identity floor honestly — or a numbered located negative.
