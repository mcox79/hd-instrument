---
priority: 7
slug: harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic
status: OPEN
review:
review_text:
---

# PROBLEM: the reader decides whether an event HARMS or HELPS its patient (`force_dynamics_valence`) by a WordNet-animacy check plus membership in a hand-curated verb LIST — not by any force simulation — and it runs an in-process FrameNet-style parse ON THE READ PATH to do it. That is one of the 8 live NOT-brain-foundational organs: a fitted/convenient lexical stand-in for what the brain computes as FORCE DYNAMICS (Talmy; Wolff 2007 physical-causation model) — the interaction of an AGONIST's intrinsic tendency with an ANTAGONIST force, whose RESULT (the patient ends up worse / better off / unchanged) IS the harm/help valence. Harm/help event valence is UPCHAIN of the causal and affective layers (it feeds causation typing, OCC appraisal, and experiencer affect), so a verb-list stand-in caps all of them. Make it brain-foundational: compute harm/help from the substrate's OWN force-dynamic arithmetic (`force_dynamics_typer` / `force_dynamics_lexicon` + animacy/patient-tendency), retire the fitted verb-list and the read-path FrameNet parse — or a rigorous located negative. Glass-box, NO external LLM at inference.

**slug:** `harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic` — **opened:** 2026-09-10 by the strategy session, from the BF-certification of the live set (`force_dynamics_valence` is one of the 8 live NOT_BF organs) + the owner directive "get the substrate to 100% BF UPCHAIN first" (harm/help valence feeds causation typing + affect). **status:** OPEN. Strategy lands any hdlab change (Q111, witnessed); the solver builds the force-dynamic computation + the witness in `experiments/`, `verification/`, and this folder. Glass-box, NO external LLM at inference (the invariant); an in-process external-style parse ON THE READ PATH is itself a defect to remove.

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
When the reader decides whether something bad or good happened to a character — did the event hurt them or help them — it currently just checks a hand-written list of "harmful" and "helpful" verbs (and whether the target is animate). A list is brittle: it only knows the verbs someone typed in, and it says nothing about WHY an event helps or harms. The brain understands harm/help as physics-of-interaction: an entity has a tendency (to keep going, to stay whole), some force acts on it, and the RESULT — the entity ends up worse off, better off, or unchanged — is what "harm" or "help" MEANS. Computing it that way generalizes to verbs no one listed, and it is the same force-reasoning the reader already uses elsewhere. The task is to compute harm/help from that force-interaction, using the substrate's existing force-dynamics machinery, and stop consulting a fitted verb list — and stop running an extra parse at read time to feed it.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate + the owner's "100% BF upchain first"
`force_dynamics_valence` is one of the **8 live NOT_BF organs** (`notes/bf_status_registry.jsonl`): harm/help = WordNet-animacy + verb-LIST membership (NOT a force simulation), and it runs an **in-process FrameNet-style parse ON THE READ PATH** (a second defect — an external-style parse at inference). The brain's mechanism is FORCE DYNAMICS (Talmy 1988; Wolff 2007 physical-causation / force-vector model; the substrate already has `force_dynamics_typer` + `force_dynamics_lexicon` for the AGONIST/ANTAGONIST tendency-vs-force computation used by causation typing). Harm/help event valence is UPCHAIN of causation typing (a harmed patient signals a causal outcome), OCC appraisal, and experiencer affect — so a verb-list stand-in caps all of them. This is a bounded, high-fidelity BF-upchain fix: derive the harm/help RESULT from the force-dynamic arithmetic + patient tendency, retire the fitted list, and remove the read-path parse.

## 3. MEASURED vs INFERRED
- **MEASURED (on disk, verified 2026-09-10):** `force_dynamics_valence` uses a hand verb-list + WordNet animacy (the `HARM_BACKOFF` test-fitted list was already retired — registry note). The REUSE target `hdlab/force_dynamics_typer.py` (+ `force_dynamics_lexicon.py`) is the **PINNED Wolff/Talmy truth-table** (CAUSE/ENABLE/PREVENT from patient-tendency × force-concordance × endstate-reached; typed the three 0.929 vs placeholder 0.190 CI-sep, PREVENT-killer 0.900 vs 0.000). **THREE PRECISE NUANCES the solver must handle (verified, so you don't assume a free drop-in):** (i) the typer outputs causal STRUCTURE (CAUSE/ENABLE/PREVENT), NOT harm/help VALENCE directly — harm/help is the PATIENT-OUTCOME POLARITY (is the reached endstate good or bad FOR THE PATIENT), a further bit on top of the force structure; (ii) the force lexicon is **~16% coverage (PHYSICAL causation only)** per its own `__bf_note__` — harm/help spans mental/social harm too, so broadening coverage brain-foundationally is part of the task (this is what the verb-list was crudely standing in for); (iii) **FrameNet as a STATIC nltk LEXICON is admissible** (the typer uses it, cached to `data/force_dynamics_lexicon_v1/lexicon.json`, like location_register's WordNet) — the DEFECT to remove is specifically any FrameNet-style *frame-semantic PARSE at read time*, not the lexicon lookup; confirm which `force_dynamics_valence` actually does before removing.
- **INFERRED (to prove or refute WITH A NUMBER):** that a force-dynamic harm/help computation (Wolff tendency+result) matches or beats the verb-list on the reader's harm/help metric AND GENERALIZES to held-out verbs the list misses (info-free twin losing); that removing the read-path parse costs nothing. Measure — do not assume the force model wins.

## 4. ALREADY TRIED / DO NOT REDO
- The `HARM_BACKOFF` test-fitted force-verb list was ALREADY retired (do not re-introduce it or re-discover its removal). `force_dynamics_typer`/`force_dynamics_lexicon` are BUILT (reuse, do not re-derive). Causation typing already consumes the force computation — study that path.
- Do NOT re-add or keep the in-process read-path parse "for coverage"; removing it is part of the fix (route through the reader's already-computed parse, or the substrate's own force lexicon).

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/force_dynamics_valence.py` (the organ), `hdlab/force_dynamics_typer.py` + `hdlab/force_dynamics_lexicon.py` (the REUSE targets), and the causation-typing consumer of the force computation. Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the Wolff force-dynamics entries §2b + the causal-selection SOLVED that landed `event_type` and the mental-causation bridge) + `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` (the causal/affect consumers). Enumerate the harm/help call sites in `hdlab/situation_reader.py` (affect / valence / causation). Run `python tools/reader_capabilities.py`. Understand the force-dynamics + causation + affect organs before proposing the change.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
Compute harm/help event valence from the substrate's FORCE-DYNAMIC arithmetic (AGONIST tendency × ANTAGONIST force → RESULT worse/better/unchanged, per Wolff), retiring the verb-LIST membership test AND the in-process read-path parse, and SHOW it matches-or-beats the verb-list on the harm/help metric while GENERALIZING to held-out verbs the list misses (info-free twin LOSING, no downstream regress to causation/affect dims) — OR a rigorous LOCATED NEGATIVE naming exactly why the force computation cannot match the list on the reader's own metric (with a number; the brain's actual mechanism faithfully built). INVARIANT: recall path + non-valence consumers byte-identical off the changed decision; no external tool/LLM/read-path parse at inference.

## 7. FILES AND ENTRY POINTS
`hdlab/force_dynamics_valence.py`, `hdlab/force_dynamics_typer.py`, `hdlab/force_dynamics_lexicon.py`; the causation-typing + affect/valence call sites in `hdlab/situation_reader.py`; the board `experiments/exp_situation_model_qa_modern_v1.py` (affect / valence / state / causal dims to not-regress); `notes/bf_status_registry.jsonl` (the `force_dynamics_valence` NOT_BF entry); the causal-selection prior problem folder (`a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround`).

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT re-quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT re-introduce the retired `HARM_BACKOFF` test-fitted list. Do NOT keep an in-process external-style parse on the read path "for coverage" (a defect to remove). Do NOT reach for FrameNet / an external semantic-role tool at inference (NOT_BF). Do NOT claim "converged" on engineering variations; the bar is the brain's force-dynamic harm/help computation, faithfully built, generalizing beyond the list — or a numbered located negative.
