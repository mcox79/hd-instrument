---
priority:
review: EXCELLENT
review_text: "Bar MET on cross-sentence who-did-what; re-verified FIRST-HAND 7/7 (183s, scaffold-free, real hdlab register). A clean brain-real DISSOCIATION: correct pronoun linking buys ATTRIBUTION (an entity's pronoun-referenced history stays retrievable) but NOT anticipation (does not improve next-argument prediction, even with ORACLE linking). Load-bearing NON-STRUCTURAL controls hold: ACT-R > shuffled-link twin +0.0731 CI-sep (correct binding, not any link); graded > hard argmax +0.0268 CI-sep. Reported AGAINST itself: the string-identity margin is partly structural (a pronoun can't string-match a name), and ACT-R does NOT clearly beat simple recency downstream (+0.0129 NOT separated). DEEPENING WIN: activation-weighted GRADED binding is a divisive-normalization INTERIOR optimum (peak temp~2.0; uniform hedging HURTS -> it's the activation weighting). Fan effect MEASURED (oracle decode 0.695->0.608 with event-count) -> upgrades dense->sparse from suspected to measured. NO hdlab landed; the entity-write landing (graded softmax binding) is QUEUED proven-ready for the consolidation."
---

> ## SOLVER REVIEW -- EXCELLENT (integrated 2026-08-27 by the strategy session)
> **Re-verified FIRST-HAND, scaffold-free:** `verification/test_entity_tracking_end_to_end.py` 7/7 PASS (183s), run
> by strategy, not trusting the headline. The witness recomputes live on real LitBank through the REAL
> `hdlab.situation_model_accumulate` multibank register (ORACLE = gold coref); proper doc-clustered bootstrap CIs.
> **Bar MET** on cross-sentence who-did-what: ACT-R salience-bound linking beats string-identity CI-separated (pronoun
> subset +0.115, full +0.0249), and the info-free shuffled-link twin LOSES (ACT-R +0.0731 CI-sep) -> CORRECT binding,
> not merely a link, is the source. **The finding is a DISSOCIATION** (measuring BOTH admissible tasks is the whole
> result): correct pronoun linking buys cross-sentence ATTRIBUTION, NOT anticipatory prediction (entity augment of the
> gist HURTS -0.219; correct vs string-identity -0.099; even ORACLE -0.131) -- neurally supported (item-episodic
> retrieval vs entity-agnostic schema/verb prediction are separable; hippocampal amnesia spares online prediction).
> **Adversarial audit passed:** the solver flags the string-identity margin as partly structural and stands on the
> non-structural controls; ACT-R ~ recency downstream is reported against self (NOT separated); the dilution
> stratification is reported INCONCLUSIVE (proxy saturated), not spun. **Deepening win (the cron's purpose):**
> activation-weighted GRADED binding beats hard argmax (+0.0268 CI-sep) with a uniform-weight control confirming the
> activation weighting is essential (uniform HURTS) -- a divisive-normalization interior optimum (Carandini & Heeger;
> peak temp~2.0). **Fan effect MEASURED** (0.695->0.608 with event-count) -> the dense-bundle register IS the shortcut;
> evidence now backs the pattern-separated store. **hdlab:** NO file landed (Q111); the one accuracy-relevant change
> (graded activation-weighted softmax binding, temp a swept hyperparameter) is QUEUED proven-ready for the consolidation
> with the entity line; the sparse-store redesign is an evidence-backed BUILD proposal, not a landed fix. AUDIT UPDATE
> folded (§2b). Completes the entity line (BIND + PREDICT + compose): correct linking serves RETRIEVAL, not a predictive
> prior, on running narrative at the current representation.

# PROBLEM: we validated the two halves of entity tracking SEPARATELY (bind a pronoun by salience; predict what an entity does by meaning-memory) -- but never composed them end-to-end on running narrative to show correct pronoun linking actually improves comprehension

**slug:** `wire_entity_tracking_end_to_end_on_running_narrative` - **opened:** 2026-08-27 by the strategy session
(the composition the just-integrated `entity_binding_needs_a_modern_pronoun_corpus` named: "wire the corrected binder into
the running situation model and re-run the entity-PREDICTION channel to measure the downstream marginal value of correct
pronoun linking end-to-end -- LitBank now provides the running-narrative substrate GAP snippets could not").
**status:** OPEN - **a wire-and-measure: compose the two validated entity channels (salience BINDING + content PREDICTION) + coref threads on running narrative.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2`. Both entity channels are validated in isolation
> on real data (binding: grammatical-prominence salience, GAP; prediction: role-conditioned content-addressable memory,
> QA-SRL). The open question is whether they COMPOSE -- does correctly linking pronouns into entity threads (not just
> string-identity) improve downstream entity prediction / comprehension end-to-end? This is the entity line's payoff
> measurement, and it is a wire-and-measure, not a new mechanism. Re-rank per the owner's direction / the
> consolidate-and-measure phase.

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

We built and separately proved the two halves of "track the characters in a story": working out WHO a pronoun refers to
(by grammatical prominence), and predicting WHAT a character will do next (by its role-structured memory). But we tested
them on different data and never joined them up. The real test is: in an actual running story, does correctly resolving
"he/she/they" into the right character -- instead of the cheap trick of only matching identical names -- actually make
the reader understand the story better (predict what happens next, answer who-did-what across sentences)? This joins the
two halves on running narrative and measures whether the composition pays off.

## 2. WHY THIS ONE

- **It is the entity line's payoff measurement.** Both channels are validated in isolation; comprehension needs them
  working together on continuous text, which neither isolated test showed.
- **It closes a real gap the binding work flagged.** Pronoun linking was proven on GAP snippets, which cannot support a
  running-narrative downstream task; LitBank (acquired in the binding work) is exactly that substrate.
- **It is a clean wire-and-measure of organs we own** (the ACT-R salience binder + coref threads + the content-addressable
  entity-prediction channel) -- decisive either way, no new mechanism required.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** comprehension maintains a SITUATION MODEL whose nodes are ENTITIES tracked across the discourse (Zwaan &
Radvansky 1998 event-indexing; Kintsch construction-integration). Each new mention is BOUND to a persistent entity by
salience (Centering; the just-integrated grammatical-prominence / ACT-R activation result), and the entity's accumulated
role-structured state is retrieved content-addressably to PREDICT its next behaviour (the entity-structured situation
model result). Binding and prediction are distinct computations over one entity representation.

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** how the salience-bound coref threads feed the prediction
channel; how much correct linking (vs string-identity) actually changes the entity's accumulated state; the update
schedule across the narrative. COPY the OPERATION (salience-bind mentions -> entity threads -> content-addressable
predict); SWEEP the params. Reuse the ACT-R binder + the content-addressable retrieval organ; do NOT rebuild either.

**Corpus note:** LitBank is running literary narrative (acquired in the binding work) -- the right substrate. Hold text
fixed across arms (correct-linking vs string-identity vs shuffled-link twin) so only the linking varies.

## 4. MEASURED vs INFERRED

**MEASURED (integrated 2026-08-27):** BINDING = grammatical-prominence salience / ACT-R base-level activation resolves
same-gender ambiguous pronouns 0.699 (GAP), recency at chance, semantics (implicit-causality) does not help; PREDICTION =
the entity-structured situation model (role-conditioned content-addressable memory) beats the bag-of-words gist
CI-separated (QA-SRL). Both validated in ISOLATION, on different corpora. LitBank running-narrative coref is on disk.

**INFERRED / OPEN (this problem, decisive either way):**
- On running narrative (LitBank), does composing the salience binder + coref threads + the content-addressable
  prediction channel improve DOWNSTREAM entity prediction / cross-sentence comprehension over STRING-IDENTITY linking,
  CI-separated, with an info-free twin (shuffled entity links) LOSING?
- What is the marginal value of CORRECT pronoun linking (salience-bound) over the cheap string-identity default?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT rebuild the binder or the prediction channel -- both integrated; compose them.
- Do NOT test binding on GAP snippets for the downstream task (they are not running narrative) -- use LitBank.
- Do NOT use content retrieval for the pronoun PICK (salience binds; content predicts) -- the dissociation is established.
- Query `experiment_index.py query "litbank"`, `query "entity"`, `query "coreference"`; read the entity-binding +
  entity-structured-situation-model SOLVEDs + `hdlab/content_addressable_retrieval.py` + `hdlab/situation_model_accumulate.py`
  BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read the ACT-R salience binder (from `entity_binding...`), the content-addressable prediction channel (from
  `the_situation_model_tracks_words_not_entities`), `hdlab/situation_model_accumulate.py`; confirm how to thread
  salience-bound coref into the entity store and feed the prediction channel.
- Confirm the LitBank running-narrative coref population (`data/litbank/`); recompute every floor (string-identity
  linking; majority; shuffled-link twin) on it.

## 7. THE BAR

Compose the salience binder + coref threads + the content-addressable entity-prediction channel on running narrative.
Floors recomputed on the LitBank population:

- **Correct (salience-bound) entity linking must improve a DOWNSTREAM entity task (next-argument prediction, or
  cross-sentence who-did-what) CI-separated over its UPPER bound vs STRING-IDENTITY linking, with an info-free twin
  (shuffled entity links) LOSING CI-separated.** Report CI half-width + null p95. Attribute the gain to the LINKING
  (ablate the binder -> string-identity).
- **DECISIVE EITHER WAY:** correct linking helps CI-separated -> wire the composed entity-tracking loop into the live
  reader (propose the hdlab diff). Correct linking does NOT beat string-identity downstream -> a rigorous negative
  (string-identity is a sufficient linker at this scale / the prediction channel is representation-limited), localizing
  what pronoun resolution actually buys downstream.

## 8. FILES AND ENTRY POINTS

- The ACT-R salience binder + `hdlab/situation_model_accumulate.py` (entity threads) + `hdlab/content_addressable_retrieval.py`
  (prediction channel) + `hdlab/predictive_reader.py` (the forward predictor), `data/litbank/` (running narrative).
- `experiments/exp_litbank_chain_quality_v1.py` + the entity-structured-situation-model cells (to compose).
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT rebuild the binder or prediction channel; this is the COMPOSITION + downstream measurement.
- Do NOT use GAP snippets for the running-narrative downstream task; use LitBank.
- No number crosses populations/scorers -- recompute the string-identity floor on the LitBank population.
