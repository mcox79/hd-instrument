# Research drill: is compositional Reichenbach tense/aspect the brain-faithful way to assign event temporal location?

**Date:** 2026-08-31 | **Drill type:** RESEARCH-ONLY (no code) | **Problem:** `the_tense_agnostic_detector_drops_tense_needed_by_the_time_dimension`
**Prior-work check:** `experiment_index.py` -- `tense` 3 cells (the stock `_temporal_ordering` extractor + a drop-tense scramble control, HARD_FAIL), `aspect` 11, `temporal` 61, `Reichenbach` 0. No prior lit-scan on the Reichenbach frame on record.
**Substrate KB concept-query** returned empty (the index is a known livelock; empty != absence).

---

## Q1 -- FIDELITY OF THE FRAME (PINNED, with one correction)

**Reichenbach's E/R/S triple is the standard computational-level model and is well-established.** Tense = relation between Reference and Speech time; aspect = relation between Event and Reference time (perfect = E before R; progressive/imperfective = E surrounds R; simple = E at R). This is the near-universal frame in formal semantics (Stanford Encyclopedia "Tense and Aspect"; Reichenbach 1947) and has been directly validated as an annotation scheme against corpora (Derczynski, ACL W13-0107). **Our voice/aspect/tense decomposition maps onto it cleanly -- PINNED.**

**The situation-model TIME dimension is genuinely read from tense+aspect during comprehension -- PINNED.** Zwaan & Radvansky's event-indexing model shows readers actively monitor a TIME index: temporal-shift sentences reliably increase reading time (a continuity break the reader is tracking), and the number of discontinuities scales the cost. So TIME is a real, incrementally-maintained dimension -- not post-hoc.

**Aspect is computed online, not inferred after the fact -- PINNED.** Grammatical aspect shapes the situation model *as it is read*: imperfective/progressive keeps the event's internal structure, participants, instruments and location active; perfective/perfect foregrounds the completed result-state (Ferretti/Madden/Zwaan; PLOS One "Grammatical verb aspect and event roles"; Russian perfective/imperfective + event-knowledge activation studies). Vendler's four classes (state/activity/accomplishment/achievement) and the telic/atelic cut (Aktionsart) are the lexical-aspect substrate that grammatical aspect operates on.

**Neuro evidence -- PINNED that tense/aspect morphosyntax is a distinct composition step.** Tense-agreement/inflection violations elicit a LAN (left anterior negativity) then P600 -- the morphosyntactic-then-repair signature -- and the LIFG (Broca's) is causally implicated: LIFG-lesioned patients show an N400 where controls show LAN-P600, i.e. they fall back to lexical processing when morphosyntactic composition is unavailable (Kielar et al., *Cortex* 2016). So "read the inflection to compose a temporal feature" is a real, separable brain operation.

**CORRECTION (a fidelity gap to name):** "temporal location" is *not* tense alone. Bastiaanse's PADILIH states plainly that time-reference assignment is **an interaction of tense, aspect AND context/discourse**. A morphology-only Reichenbach parse recovers the *features* correctly, but the situation-model's actual timeline *placement* -- especially for PAST and perfect/relative tenses -- needs the Reference time resolved against prior discourse (see Q2). Our per-verb-group compositional parse supplies the features; it does **not** by itself place events on a discourse timeline. That is the right division of labour, but it means the TIME dimension is tense-features PLUS a discourse reference-time step, not tense-features alone.

## Q2 -- DETECTION vs LOCATION ARE SEPARABLE (PINNED, complicated productively)

The **neo-Davidsonian event variable is tenseless**: every verb introduces an event argument `e` and event-hood is lexical predication; tense is a separate operator that *locates* `e`, applied to an already-identified predicate (Parsons; Davidson). This is exactly our architecture -- detection = "there is an `e`", location = a downstream operator. **PINNED: detecting an event does not require its tense.**

Bastiaanse et al. (2011, PADILIH) *complicates but supports* this: PAST time-reference is the hard, **discourse-linked** form (it requires linking speech time to a non-coincident event time via discourse syntax), whereas present/future -- where event and reference coincide -- are spared in agrammatism. Crucially, "PADILIH does not apply to tense but to the *time reference of the verb form as a whole*." So: tense is computed on already-found predicates (supports the split), but the *cost* lives in the discourse-linking of PAST, not in detection. **Implication for us:** the tense-agnostic detector is brain-faithful; the expensive part the brain isolates is precisely the discourse reference-time for past/perfect forms, which is where a proper TIME dimension (not per-verb morphology) must do work.

## Q3 -- THE NON-FINITE WALL: INHERIT, don't assign standalone tense (this reframes the target)

**Linguistically pinned: non-finite forms carry NO independent absolute tense; they are anchored by the matrix/controlling verb.** The syntax/semantics is explicit:
- **To-infinitives** have a **constant** temporal relation to the matrix -- typically future-shifted/unrealised-relative (Ogihara 1996 treats them as "present-tensed" relative to the embedding verb, with the attitude verb fixing the evaluation time; Abusch 2004 distinguishes future-shifting F-verbs from B-verbs). Present-oriented infinitival complements must be progressive/stative/habitual and reject `yesterday/tomorrow` framing -- i.e. they have no free tense of their own.
- **Gerund-participles** have a **variable** relation resolved by matrix + aspectual class + context; participial temporal adjuncts ("while feeding the owl") inherit their time from the matrix event and controller.
- **Sequence-of-tense** is a syntactic licensing rule: an embedded past under a matrix past is read *simultaneously*, not doubly-shifted -- the embedded morphology does not compute its own backward shift.

**This says our low non-finite accuracy is largely a category error, not a morphology bug.** The faithful target for a non-finite event is: **mark it non-finite, then inherit the Reference time from its controlling finite verb** (constant future-shift for to-infinitives; matrix-anchored, aspect/context-resolved for gerunds/participles). Trying to stamp a standalone past/present/future on "to walk" in isolation measures against a gold that *itself must inherit* -- so both our detector and any per-token tense gold are the wrong instrument there. **PINNED recommendation: for non-finite detections, emit `finite=False` + an inheritance pointer to the governing finite verb, rather than a guessed absolute tense.** This likely converts the "wall" into a correctly-scoped PASS (mark + inherit) and a clean, enumerated NEGATIVE for standalone assignment.

## Q4 -- GENERALIZATION & LEARNING: a small closed rule + lexicalized irregulars IS the faithful model

Two established findings bear directly on "hardcode the English lexicon: fair parameter-supply or shortcut?":
- **Aspect Hypothesis (Andersen & Shirai 1994):** children/L2 learners bootstrap grammatical tense-aspect morphology **from lexical aspect** -- past/perfective attaches first to telic achievements/accomplishments, progressive to atelic activities, before generalising. So the surface-form -> morpheme mapping is *acquired*, and it is acquired *conditioned on Vendler class*.
- **Past-tense debate (Pinker "Words and Rules" dual-route vs Rumelhart-McClelland single-route):** the productive regular pattern behaves rule-like (a small closed rule: `-ed/-s/-ing` + the auxiliary system), while irregulars are **memorised lexical entries**; overregularization ("goed") is the rule mis-firing over a not-yet-memorised item. Neurophysiology supports dual-route (Kielar; regular vs irregular dissociate).

**Verdict:** hardcoding the **regular** auxiliary/suffix mapping is a **fair parameter-supply** -- it is genuinely a small closed productive rule, exactly the "rule route," and FOUNDATION-is-free-to-build makes a supplied closed rule admissible. Hardcoding the **irregular** verb list is *also* faithful -- the brain memorises those (the lexical route), it does not compute them. The **fidelity shortcut to avoid** is (a) claiming the mapping is universal (it is English-specific and acquired), and (b) **hardcoding aspectual/telicity class** if we ever need it -- lexical aspect is learned distributionally and is the thing the child bootstraps *from*, so telic/atelic should be LEARNED (distributional), never a hand list. For the immediate build, the auxiliary+suffix rule table + an irregular lexicon is brain-faithful as-is.

---

## PINNED vs CONTESTED summary
- **PINNED:** Reichenbach E/R/S frame; TIME as an online-monitored situation-model dimension; aspect computed online; tenseless neo-Davidsonian event variable (detection/location separable); LAN-P600/LIFG morphosyntactic composition; non-finite forms inherit (no independent absolute tense); to-infinitive constant vs gerund variable relation; dual-route regular-rule + irregular-lexicon.
- **CONTESTED / our-call:** single- vs dual-route is still debated (modern seq2seq nets reopened it) -- but both agree the *regular* pattern is a compact productive mapping, which is all our parameter-supply needs.
- **BRAIN-UNFAITHFUL if we do it:** (1) assigning a standalone absolute tense to a non-finite verb instead of marking-non-finite + inheriting; (2) treating the situation-model TIME placement as tense-morphology alone, dropping the discourse reference-time that PADILIH shows is the actual locus of PAST-reference difficulty; (3) hand-coding telic/atelic aspectual class (should be learned).

## TLDR (5 bullets)
- The compositional Reichenbach parse (tense/aspect/voice from the verb group) is the **right, PINNED computational-level model**, and the tense-agnostic detector + separate temporal-location operator matches the brain's tenseless-event-variable architecture -- keep the split.
- Aspect is a **genuinely computed online grammatical property** (imperfective keeps the event open; perfect foregrounds the result), not a post-hoc inference -- our aspect channel is well-founded.
- **The non-finite "wall" is mostly a category error, not a morphology bug:** non-finite forms carry no independent tense; the faithful move is `finite=False` + inherit the reference time from the controlling finite verb (constant future-shift for to-infinitives) -- so mark-and-inherit is the PASS target, and standalone non-finite tense is a clean enumerated NEGATIVE.
- Hardcoding the English **regular** auxiliary/suffix rule + an **irregular** lexicon is **brain-faithful** (dual-route: small productive rule + memorised irregulars); the shortcut to avoid is hand-coding **telic/atelic aspectual class**, which the brain learns distributionally (Aspect Hypothesis).
- **One real fidelity gap surfaced:** situation-model TIME *placement* is tense+aspect+**discourse context** (Bastiaanse/PADILIH), so unifying the event set is right but the TIME dimension needs a discourse reference-time step beyond per-verb morphology -- past/perfect placement is exactly where the brain spends its effort.

## QUESTIONS
None blocking. (One judgement call for the solver: whether to score non-finite events under "mark-and-inherit" gold vs the current per-token absolute-tense gold -- the literature says the former is the faithful instrument.)

## NEXT STEPS (for the solver, not this drill)
- Build the tense-preserving variant to emit the Reichenbach triple on finite detections; for non-finite detections emit `finite=False` + a pointer to the governing finite verb (inherit), rather than a guessed absolute tense.
- Score finite tense/aspect against UD features (CI-separated over placeholder-constant, shuffled-tense twin LOSING); score non-finite as mark-and-inherit, and report the standalone-tense NEGATIVE enumerated.
- Keep the auxiliary/suffix rule + irregular lexicon as supplied parameters; do NOT hand-code aspectual class if telicity is ever needed -- learn it.

## Sources
- [Tense and Aspect -- Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/tense-aspect/)
- [Reichenbach (1947), The Tenses of Verbs (excerpt)](https://perso.atilf.fr/apotheloz/wp-content/uploads/sites/59/2016/11/Reichenbach3.pdf)
- [Derczynski, Empirical Validation of Reichenbach's Tense Framework, ACL W13-0107](https://aclanthology.org/W13-0107.pdf)
- [Zwaan & Radvansky (1998), Situation Models in Language Comprehension and Memory](https://sites.ualberta.ca/~dmiall/Cognitive/Readings/Zwaan_Radvansky_1998.pdf)
- [Who/when/where: experimental test of the event-indexing model (Springer)](https://link.springer.com/article/10.3758/BF03195811)
- [Grammatical verb aspect and event roles in sentence processing, PLOS One / PMC5747445](https://pmc.ncbi.nlm.nih.gov/articles/PMC5747445/)
- [Kielar et al., LIFG mediates morphosyntax: ERP from verb processing in LH-damaged patients, Cortex (PubMed 28011396)](https://pubmed.ncbi.nlm.nih.gov/28011396/)
- [Bos & Bastiaanse, Time reference decoupled from tense in agrammatic and fluent aphasia (PADILIH)](https://www.semanticscholar.org/paper/Time-reference-decoupled-from-tense-in-agrammatic-Bos-Bastiaanse/cf684773c03ac2441472b198f748c8b9b1a9db34)
- [Parsons / neo-Davidsonian event semantics (Landman class notes)](https://www.tau.ac.il/~landman/Online%20Class%20Notes/2%20ADVANCED%20SEMANTICS/8%20Neo-davidsonian%20event%20semantics.pdf)
- [Arregui, On Abusch's "Sequence of Tense and Temporal de re"](https://ana-arregui.com/wp-content/uploads/2025/02/abusch-draft.pdf)
- [Tense selection and temporal interpretation of complement clauses (Ogihara-based), Sinn und Bedeutung](https://ojs.ub.uni-konstanz.de/sub/index.php/sub/article/download/825/737/1494)
- [Arregui, Tense in Temporal Adjunct Clauses, SALT](https://journals.linguisticsociety.org/proceedings/index.php/SALT/article/download/2814/2554/3089)
- [Andersen & Shirai (1994), Discourse motivations / Aspect Hypothesis](https://www.academia.edu/9232148/)
- [Vendler (1957), Verbs and Times](https://www.academia.edu/3016007/_Verbs_and_Times_Vendler_1957_)
- [Pinker, The Past-Tense Debate (Words and Rules)](https://stevenpinker.com/files/pinker/files/edinburgh.pdf)
