---
priority: 2
review:
review_text:
---

# PROBLEM: the reader's running "situation model" is a bag of content-word meanings, not a set of tracked ENTITIES -- so it cannot follow WHO is who across sentences, and its top-down predictions are entity-blind

**slug:** `the_situation_model_tracks_words_not_entities` - **opened:** 2026-08-26 by the strategy session
(the "remaining foundational build" the just-integrated `the_reader_is_feed_forward_where_the_brain_is_predictive`
named as the correct next problem: "the discourse gist is a bag-of-content running mean; the brain tracks ENTITIES
across sentences -- wiring the coreference organ into the situation model so the top-down prediction is
entity-structured is the next genuinely-foundational step").
**status:** OPEN - **on the retrieval-first / prediction critical path; composes the coref organ + the situation model + the forward predictor + content-addressable retrieval (the session's convergence).**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2`, below p1 (retrieval-first wire-and-measure)
> but above the data-gated meaning lane (p8). It is the direct successor the predictive-reader SOLVED named, and it
> sits on the convergence: entity representations are retrieved content-addressably (the #1 lever), the running
> situation model conditions the forward predictor (just built), and coref binds mentions to entities. Re-rank only
> if p1 stalls or the owner directs.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When you read a story, you build a mental model of the PEOPLE and THINGS in it -- "the waiter," "the customer" -- and
you track each one as the story refers back to it ("he," "she," "the man"). That entity model is what lets you answer
"who paid?" three sentences later. Our reader's running "situation model" is not that: it is a blurry AVERAGE of the
meaning-words it has seen recently (a bag-of-words gist). It has no notion of distinct, persistent entities, so it
cannot follow who "it" or "they" refers to, and its predictions about what comes next are entity-blind.

The just-built forward predictor showed the running gist DOES help predict the next argument -- but it is a
content-word mean. This problem asks: **replace that bag-of-words gist with an ENTITY-STRUCTURED situation model** --
wire the coreference organ so recurring mentions bind to persistent entity representations -- and test whether an
entity-structured model predicts / comprehends better than the bag-of-words gist.

## 2. WHY THIS ONE

- **It is the successor the predictive-reader SOLVED explicitly named**, and it sits on the session's convergence:
  entity representations are RETRIEVED content-addressably (the #1 retrieval lever), the situation model top-down
  conditions the forward predictor (just built), and coreference binds mentions to entities. One build ties three
  organs together.
- **The pieces already exist, unwired.** A coreference organ is built (audit: coref is "heavily built now"; the E3
  content-addressable retrieval mention→entity link is `NEEDS_ADAPTER`), and the situation-model register +
  `n400_coherence_monitor` exist. This is a WIRING + a representation choice, not a from-scratch build.
- **It is the difference between a reader and a comprehender.** "Who did what to whom, across sentences" is entity
  tracking; without it the situation model cannot support cross-sentence QA, bridging, or ToM.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** comprehension builds an EVENT/SITUATION MODEL whose nodes are ENTITIES tracked across the discourse
(Zwaan & Radvansky 1998 event-indexing; Kintsch construction-integration). Coreference resolution binds each new
mention to a persistent discourse entity; the hippocampal/entorhinal system and the default-mode network maintain the
evolving situation model, and entities are retrieved by CONTENT-ADDRESSABLE cue-based retrieval (the same
Lewis-Vasishth operation this project has unified E1/E2/E3 + parsing + the fan effect under -- see audit §1). Pronoun/
anaphor resolution is cue-based retrieval of the matching entity from the situation model.

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** the ENTITY representation (a slot bound to accumulated
mentions? a content-addressable register entry per entity?); how a new mention is matched to an existing entity vs
opening a new one (the cue-based retrieval threshold); how the entity-structured model conditions the forward
predictor (replace / augment the bag-of-words gist). COPY the OPERATION (persistent entities, cue-based mention→entity
binding, entity-structured top-down prediction); SWEEP the parameters.

**Corpus-age note (MIND IT):** use modern text (the predictive-reader used reconstructed QA-SRL documents; the coref
resource must be modern too). Do not score entity tracking on ~200-year-old McGuffey prose without holding era fixed.

## 4. MEASURED vs INFERRED

**MEASURED (`the_reader_is_feed_forward...`, integrated 2026-08-26):** the running situation-model gist is a
BAG-OF-CONTENT-WORDS mean (the mean grounded vector of recent content words), reset at event boundaries by
`n400_coherence_monitor`. It DOES carry useful top-down signal (discourse-conditioned prediction beats local +0.088
CI-sep; a random-document gist HURTS) -- but it is ENTITY-BLIND (it cannot represent "the same person, referred to
again"). The coreference organ exists (E3, `NEEDS_ADAPTER` for the FHRR retrieval adapter); content-addressable
retrieval is validated (p3, p2-fan-effect) as the mention→entity matching operation.

**INFERRED / OPEN (this problem, decisive either way):**
- Whether an ENTITY-STRUCTURED situation model (mentions bound to persistent entities via cue-based retrieval) beats
  the bag-of-words gist at a task where entity identity matters -- e.g. resolving a pronoun/anaphor to the right prior
  entity, or predicting a RECURRING entity's next role/argument across sentences.
- Whether entity-structured top-down context improves the forward predictor over the bag-of-words gist.

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT rebuild coreference from scratch -- an organ exists; this is WIRING it (with the FHRR retrieval adapter it
  needs) into the situation model. Query `experiment_index.py query "coreference"`, `query "entity"`, and read the
  coref organ + `situation_model_accumulate.py` / `situation_model_multibank.py` BEFORE building.
- Do NOT re-derive content-addressable retrieval -- `hdlab.content_addressable_retrieval.AdditiveCueRetrieval` is
  landed and feature-agnostic; the mention→entity match is a USAGE of it (cue = the mention's features; items =
  entities), and the fan-effect SOLVED showed context reinstatement resolves similar-entity interference.
- Do NOT re-run the bag-of-words discourse gist as the headline -- it is the FLOOR to beat (predictive-reader finding 9).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read the coreference organ (find it: `experiment_index.py query "coreference"`), `hdlab/situation_model_accumulate.py`,
  `hdlab/content_addressable_retrieval.py`, and the predictive-reader's discourse cell
  (`exp_predictive_reader_discourse_hierarchy_v1`) so you inherit the exact gist the entity model must beat.
- Confirm a modern coref-annotated or reconstructed-document population and recompute every floor on it.
- Confirm on disk whether the coref organ already exposes entity representations or only mention-pair links -- that
  determines how much wiring vs representation-building this is.

## 7. THE BAR

Build the entity-structured situation model (coref binds mentions to persistent entities via cue-based retrieval; the
model conditions the reader). On a held-out modern population where entity identity matters, floors recomputed on it:

- **The ENTITY-STRUCTURED model must beat the BAG-OF-WORDS gist CI-separated over its UPPER bound** on an
  entity-dependent task (pronoun/anaphor resolution to the correct prior entity, OR predicting a recurring entity's
  next role/argument), **with an info-free twin (SHUFFLED entity links / random entity assignment) LOSING
  CI-separated.** Report CI half-width + null p95 beside every margin.
- **DECISIVE EITHER WAY:**
  - Entity-structured beats bag-of-words -> the situation model should be entity-structured; propose the hdlab wiring
    (strategy lands it; it composes coref + the register + the forward predictor).
  - A faithfully-built entity model does NOT beat the bag-of-words gist on our representations -> a rigorous negative
    (entity structure does not earn its machinery yet, likely a representation-quality ceiling) -- as valuable as the
    win. State the entity mechanism you built and why it is the brain's.

## 8. FILES AND ENTRY POINTS

- The coreference organ (locate via `experiment_index.py query "coreference"`), `hdlab/situation_model_accumulate.py` /
  `situation_model_multibank.py` (the register / situation model), `hdlab/content_addressable_retrieval.py`
  (`AdditiveCueRetrieval` -- the mention→entity match + context reinstatement), `hdlab/n400_coherence_monitor.py` (event
  boundaries that reset/segment the model), `hdlab/grounded_similarity.py` (entity feature vectors).
- `experiments/exp_predictive_reader_discourse_hierarchy_v1.py` (the bag-of-words discourse gist to beat).
- Prove in `experiments/` + `verification/`; propose the hdlab WIRING diff in `SOLVED.md` (strategy lands it, Q111).
  **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT rebuild coref or content-addressable retrieval; this is WIRING existing organs into the situation model.
- Do NOT score on ~200-year-old McGuffey prose without holding corpus era fixed; prefer modern reconstructed documents.
- No number crosses populations/scorers; the bag-of-words discourse gist is the floor -- recompute it on your population.
