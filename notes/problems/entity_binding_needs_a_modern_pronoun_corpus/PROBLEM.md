---
priority: 2
review:
review_text:
---

# PROBLEM: we validated PREDICTING what an entity does next, but the other half of entity tracking -- resolving WHO a mention (especially a pronoun) refers to -- is untested on real pronouns, and the evidence says it is a SALIENCE problem, not a meaning-memory one

**slug:** `entity_binding_needs_a_modern_pronoun_corpus` - **opened:** 2026-08-27 by the strategy session
(the entity-BINDING half the just-integrated `the_situation_model_tracks_words_not_entities` proved it could not test:
"QA-SRL cannot test pronouns -- pronouns are non-groundable; binding is dominated by SALIENCE/RECENCY (Centering
0.493 >> content 0.308), and content does NOT augment binding -- validate on a real pronoun corpus").
**status:** OPEN - **the binding counterpart to the validated entity-PREDICTION channel; a data + mechanism test.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` (below the incremental-parser front-end, p1).
> The entity-PREDICTION channel is integrated (meaning-memory / content-addressable). This is its BINDING counterpart:
> resolve who a mention refers to. The integrated result predicts SALIENCE (Centering/recency), not content, is the
> mechanism -- but QA-SRL has no pronoun-resolution gold, so it is untested on real pronouns. Re-rank per the owner's
> next-steps direction.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

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

Tracking characters in a story has two halves. One is PREDICTING what a character will do next (built + validated: each
character keeps a role-structured memory). The other is BINDING -- when you read "he" or "she" or "the man", working out
WHICH character it refers to. Our reader does the first now but not the second on real pronouns. And the evidence from
the prediction work points somewhere specific: binding is not solved by the rich meaning-memory -- it is dominated by
SALIENCE (you usually mean the most recently / most prominently mentioned character). This problem builds and tests the
binding half on a corpus that actually has pronouns.

## 2. WHY THIS ONE

- **It completes entity tracking.** Prediction (what they do) is validated; binding (who they are) is the missing half,
  and comprehension needs both.
- **The mechanism is predicted, not yet tested on real data.** The prediction work showed recency/salience beats content
  for binding (0.493 vs 0.308) -- but on QA-SRL, whose arguments are groundable nouns, not pronouns. A real pronoun corpus
  is required to test it.
- **It decides which coref organ to wire.** The salience/Centering resolver vs the cue-based-activation resolver (which
  HARD_FAILED the pronoun pick, -0.1348) -- this measures the right binding mechanism on real anaphora.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** reference resolution is driven by SALIENCE / accessibility -- the most prominent discourse entity is the
default referent (Centering theory, Grosz, Joshi & Weinstein 1995; Ariel's accessibility hierarchy; the given-new
contract). Recency, grammatical role (subject > object), and parallelism set salience; pronouns prefer the most salient
antecedent, full NPs less so. Binding is a fast, structural, SALIENCE-ranked pick, NOT a deep semantic retrieval --
distinct from the meaning-memory that PREDICTS entity behaviour.

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** how salience is scored (recency + grammatical prominence +
parallelism weights); whether/where a CONTENT check (gender/number/animacy agreement; semantic plausibility) re-ranks the
salience default; how mentions link into persistent entity threads. COPY the OPERATION (salience-ranked antecedent
selection with agreement filtering); SWEEP the weights. Do NOT use deep content retrieval as the primary pick (measured
to lose).

**Corpus-age note:** use a MODERN pronoun-annotated corpus; McGuffey is archaic + dialogue-heavy (its own confounds).

## 4. MEASURED vs INFERRED

**MEASURED (`the_situation_model_tracks_words_not_entities`, integrated 2026-08-27):** for entity BINDING, SALIENCE/
RECENCY dominates meaning-content (recency 0.493 vs content 0.308, chance 0.226) and content does NOT augment it; a
cue-based-activation coref pick HARD_FAILED (-0.1348). The entity-PREDICTION channel (content-addressable, role-conditioned)
is validated + integrated. A salience/Centering coref resolver exists in the substrate (locate it).

**INFERRED / OPEN (this problem, decisive either way):**
- On a MODERN pronoun-bearing corpus, does a salience/Centering binder resolve pronouns/anaphora to the correct entity
  CI-separated over a string-identity-only baseline and an info-free (shuffled-salience) twin?
- Does linking pronoun + nominal-variant mentions into entity threads improve DOWNSTREAM entity prediction beyond
  string-identity (the marginal value of real coref over exact-match)?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT use the cue-based-activation / content-retrieval resolver as the pronoun pick -- measured HARD_FAIL (-0.1348).
  Content retrieval is for the PREDICTION channel, not binding.
- Do NOT re-run the entity-PREDICTION result -- it is integrated; this is the BINDING half.
- Do NOT test binding on QA-SRL -- its arguments are groundable nouns, not pronouns (the exact reason this needs a new
  corpus). Query `experiment_index.py query "coreference"`, `query "salience"`, `query "centering"`; find the existing
  coref/Centering organ and a modern pronoun corpus (OntoNotes/GAP/WSC-style, or reconstruct from an available resource).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Locate the existing coref/Centering resolver (`experiment_index.py query "coreference"`) + `hdlab/situation_model_accumulate.py`
  (the entity threads); confirm how mentions currently link (string-identity?) and where a salience binder plugs in.
- Confirm a MODERN pronoun-annotated population is on disk or acquirable; recompute every floor on it (string-identity
  baseline; majority/most-recent baseline; shuffled-salience twin).

## 7. THE BAR

Build a salience/Centering entity binder and resolve mentions (esp. pronouns) to entities on a modern pronoun corpus.
Floors recomputed on that population:

- **The salience binder must resolve pronouns/anaphora to the correct entity CI-separated over its UPPER bound vs (a) a
  string-identity-only baseline and (b) the strongest simple floor (most-recent-mention), with an info-free twin
  (shuffled salience / random antecedent) LOSING CI-separated.** Report CI half-width + null p95. Ablate recency vs
  grammatical-prominence vs agreement-filter. AND/OR: linking coref threads improves DOWNSTREAM entity prediction over
  string-identity CI-separated.
- **DECISIVE EITHER WAY:** a win -> wire the salience binder + coref threads into the situation model (propose the hdlab
  diff). A faithful salience binder that does NOT beat most-recent-mention -> a rigorous negative (recency alone is the
  binding mechanism at this scale), localizing where richer structure would be needed.

## 8. FILES AND ENTRY POINTS

- The coref/Centering resolver (locate via `experiment_index.py query "coreference"`), `hdlab/situation_model_accumulate.py`
  (entity threads), `hdlab/content_addressable_retrieval.py` (the PREDICTION channel -- NOT the binding pick).
- `experiments/exp_entity_binding_context_resolution_v5.py` (the binding dissociation to build on).
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT use content retrieval as the pronoun pick (HARD_FAIL); salience is the binding mechanism.
- Do NOT test on QA-SRL (no pronoun gold) or archaic McGuffey without era controls.
- No number crosses populations/scorers -- recompute every floor on the pronoun population.
