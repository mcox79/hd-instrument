# Brain-mechanism grounding: tense-agnostic event/predicate detection and noun/verb disambiguation

Research drill for problem `the_extraction_front_end_recovers_only_a_third_of_events_and_roles`.
Date: 2026-08-30. Scope: RESEARCH-ONLY literature synthesis. No code or config touched.

**Operational context being grounded.** The reader's event detector was TENSE-GATED (fired
only on past-tense / aux-marked verbs; missed present-tense finite verbs ~100%). A
TENSE-AGNOSTIC, lexical-CATEGORY-based detector (fire an event at every lexical VERB
regardless of tense) recovered event-detection recall from ~0.33 to ~0.87 and generalized
out-of-domain. The precision wall (zero-derivation N/V ambiguity: *runs / plans / results /
needs*) was resolved by swapping an isolated-word POS tagger for a context-sensitive Viterbi
tagger. This document asks whether these two moves are brain-faithful.

**Discipline flags applied.** (1) Lit-scan calibration penalty: prediction confidences are
deflated and novel-synthesis is capped; stated as hypotheses-pending-VET. (2) Every mechanism
is marked PINNED (published brain finding) vs OUR-INVENTION / interpretation. (3) The
strategic read "our detector ≈ the brain" is a hypothesis, not an established equivalence.

---

## Q1. TENSE-AGNOSTIC PREDICATE / EVENT DETECTION

### The mechanism (PINNED)

**1a. Event-hood is carried by argument structure, not by tense.** Neo-Davidsonian semantics
(Parsons 1990; Kratzer 2002) treats a clause as introducing an *event variable* `e` to which
thematic-role predicates (Agent(e,x), Theme(e,y)) are separately conjoined. There is direct
neural support for this *factorized* code: Frankland & Greene (2015, *PNAS*, "An architecture
for encoding sentence meaning in left mid-superior temporal cortex") showed that adjacent
subregions of left mid-superior temporal cortex (lmSTC) independently decode the **agent** and
the **patient** of a described event — i.e., the brain stores role-fillers as separately bound
variables attached to a predicate, exactly the neo-Davidsonian shape. Frankland & Greene (2020,
*Annu. Rev. Psychol.*, "Concepts and Compositionality") generalize this to a language-of-thought
factorized structure. **None of this machinery references tense**: the event variable and its
argument slots are defined by the predicate's frame, not by when it happened.

**1b. Structure-building is incremental and predicate-centred.** Matchin & Hickok (2020,
*Cerebral Cortex*, "The Cortical Organization of Syntax") locate hierarchical syntactic
structure-building in left posterior IFG (BA44) plus posterior temporal cortex (pMTG/pSTS),
across BOTH comprehension and production. Electrophysiologically, phrase-composition violations
drive broadband high-gamma increases first in pMTG/pSTS (~300 ms post verb-onset) then in
inferior frontal cortex (~500 ms) (Matchin/Flick-line intracranial work; see Matchin & Hickok
2020 for review). The verb/predicate is the pivot around which the argument frame is
projected — again, a lexical-category operation, not a tense operation.

**1c. Tense is a SEPARATE, dissociable feature bound to the event — it does not gate detection.**
Two independent literatures pin this:

- **Declarative/procedural dissociation.** Ullman (2001, *Nat. Rev. Neurosci.*, "A neurocognitive
  perspective on language: the declarative/procedural model") places inflectional morphology
  (regular *-ed* tense marking) in a fronto-striatal PROCEDURAL system (LIFG + basal ganglia),
  distinct from the temporal-lobe DECLARATIVE system that stores the lexical stem. The
  event-bearing content (the verb stem) is retrieved regardless of whether/how it is inflected;
  tense is a *rule-applied feature layered on top*, not a precondition for lexical/event access.

- **Agrammatism dissociations.** Thompson's Argument Structure Complexity Hypothesis (ASCH;
  Thompson 2003, *J. Neurolinguistics*) shows verb production difficulty scales with the DENSITY
  of a verb's argument structure — a dimension orthogonal to tense/inflection. Conversely, the
  tense/time-reference deficit is itself a *separable* impairment: Bastiaanse et al.'s PADILIH
  (Bastiaanse et al. 2011, *J. Neurolinguistics*, "Time reference in agrammatic aphasia: a
  cross-linguistic study") and the meta-analysis by Faroqi-Shah & Friedman (2015,
  *Behavioural Neurology*) establish that time reference can be selectively impaired while
  argument/event structure is spared. The two deficits doubly dissociate → detecting that a
  clause encodes an event is computed by different circuitry than computing WHEN it happened.

### Is present-tense detected LESS reliably than past? (PINNED: NO — the asymmetry runs the OTHER way)

This was the key empirical question. The answer is not merely "no difference" — it is that,
where an asymmetry exists, **PAST is the more effortful/impaired form, not present.** PADILIH
(Bastiaanse et al. 2011) holds that PAST time reference is *selectively* impaired because it
requires extra discourse-linking (relating event time to a prior speech time); present/non-past
is the LESS demanding, better-preserved form. Faroqi-Shah & Dickey (2009,
*Brain & Language*/online-processing work) found longer reaction times to PAST-reference stimuli
than present. So the brain, if anything, finds present-tense events *cheaper* to represent than
past-tense ones.

**Implication for us:** our original TENSE-GATED detector was not just "slightly off" — it was
**backwards relative to the brain.** It made present-tense events invisible, when the brain's own
gradient makes present-tense the low-cost default and PAST the marked, discourse-linked extra.
This is a strong, specific mechanistic vindication of the tense-agnostic move.

### Faithfulness verdict (Q1)

- **PINNED:** event-hood = argument-structure / lexical-predicate detection; tense = a
  separable feature bound onto the event afterward; no evidence present is detected less
  reliably than past (evidence points the opposite way).
- **Our detector is a FAITHFUL replication** of the computation: "fire an event at the lexical
  predicate, independent of tense." Prior tense-gating conflated a *separable temporal feature*
  with *event detection itself* — the exact confound the declarative/procedural and PADILIH
  dissociations rule out. (This aligns with the project discipline "copy the COMPUTATION, sweep
  the PARAMETER": event-detection-at-the-predicate is the shared computation; tense marking is a
  parameter/feature we must NOT let gate the computation.)
- **Refinement suggested:** the brain BINDS a tense/time-reference feature to each detected
  event rather than discarding it. Our detector currently only fires (or not); a
  brain-faithful upgrade would emit the event AND attach a separate `time_reference` slot
  (past / non-past / discourse-linked) — cheap, and it matches the factorized code.

---

## Q2. NOUN/VERB CATEGORY DISAMBIGUATION (the precision wall)

### The mechanism (PINNED)

The brain resolves zero-derivation N/V ambiguity by **left-context-driven syntactic prediction**,
not by isolated word-form lookup:

- **Grammatical class is committed from predictive context within ~80–100 ms in LIFG.**
  Strijkers et al. (2019, *Scientific Reports*, "Grammatical class modulates the (left) inferior
  frontal gyrus within 100 milliseconds when syntactic context is predictive") preceded
  category-relevant words with predictive syntactic contexts (possessive pronoun → noun;
  personal pronoun → verb) vs non-predictive baselines. When context was predictive, LIFG (pars
  triangularis) discriminated noun-vs-verb starting **~80 ms** post word-onset — far too fast for
  bottom-up form analysis, indicating top-down predictive assignment of category from the
  preceding structure. This is the single most on-point citation for our fix.

- **Syntactic context preactivates the predicted category before the word arrives.** Dikker &
  Pylkkänen (2013, *Brain & Language*, "Predicting language: MEG evidence for lexical
  preactivation") and Dikker, Rabagliati & Pylkkänen (2009, *Cognition*, "Sensitivity to syntax
  in visual cortex") show predictive contexts preactivate form-features of the expected
  syntactic category in left mid-temporal cortex and even visual cortex — the parser commits an
  expected category from left context, then checks the incoming form against it.

- **First-pass parse keys on word CATEGORY.** Friederici's model (2002, *TICS*) posits an early
  syntactic-category first-pass parse (the ELAN, ~120–150 ms, LIFG/anterior STG) driven by
  word-category / phrase-structure fit. **Caveat (honesty):** the ELAN's status is contested —
  Steinhauer & Drury (2012, *Brain & Language*, "On the early left-anterior negativity (ELAN) in
  syntax studies") argue much of it reflects baseline/artifact confounds. Cite it as
  *suggestive* that category is an early parsing variable, not as settled localization.

- **Agreement / subcategorization are used online as category cues.** Subject-verb agreement
  violations elicit LAN/P600 responses at the verb (review: Molinaro, Barber & Carreiras 2011,
  *Cortex*, "Grammatical agreement processing in reading"), evidence the parser exploits
  agreement between the preceding subject NP and a candidate verb — precisely the
  disambiguation cue that separates *the plan* (N) from *she plans* (V).

- **The N/V distinction is carried by distributional/contextual regularities, not a pure
  grammatical-category organ.** Shapiro & Caramazza (2003, *Neuropsychologia*) reported left
  frontal grammatical-class effects, but Vigliocco et al. (response; and Vigliocco et al. 2011,
  *Psychol. Bull.*, review) argue grammatical class per se is NOT the organizing principle;
  rather semantic + DISTRIBUTIONAL (contextual co-occurrence) cues distinguish nouns from
  verbs. This directly endorses a context/distribution-based tagger over an isolated-form one.

### Faithfulness verdict (Q2)

- **PINNED:** category assignment for ambiguous forms is CONTEXT-driven (agreement, preceding
  determiner/pronoun, subcategorization, distributional expectation), committed rapidly in LIFG
  from LEFT context — not from the isolated word form.
- **Swapping an isolated-word tagger for a context-sensitive (Viterbi / left-context) tagger is
  brain-faithful** in its core computation: both replace point-wise form lookup with
  context-conditioned category inference. The isolated tagger was the analogue of a lesioned
  parser that cannot use preceding structure — exactly where isolated taggers fail (bare-form
  present-tense verbs).
- **Refinement suggested:** the brain is *predictive/incremental left-to-right* and weights
  agreement + local functional-word cues heavily. A Viterbi HMM uses local transition context
  but is not explicitly agreement-aware or predictive. If residual errors persist on
  agreement-diagnostic items (*the results* N vs *she results* — rare), an incremental,
  agreement-featuring model (or an explicit determiner/pronoun/agreement feature) would be
  strictly more brain-faithful than a bare bigram-transition Viterbi.

---

## Q3. GENERALIZATION / SYSTEMATICITY

### The mechanism (PINNED)

Event/predicate detection is a **systematic, content-independent structural operation**, which
predicts transfer across novel verbs, genres and registers:

- **Structure-building generalizes independent of lexical content.** The language-selective
  network (Fedorenko and colleagues; e.g., Fedorenko et al. 2010, *J. Neurophysiol.*; Fedorenko
  et al. 2012, *PNAS*) builds structure over **Jabberwocky** sentences (grammatical frames with
  pseudowords) that it does NOT build over word-lists or nonword-lists — the compositional
  machinery applies to *novel/meaningless* items purely by grammatical form. Recent work
  (Fedorenko lab, 2024, "Linguistic inputs must be syntactically parsable to fully engage the
  language network") reinforces that PARSABILITY, not familiarity, drives the network. Systematic
  application to novel instances is the definition of the capability we want to transfer.

- **Compositionality is systematic in the neo-Davidsonian / LoT sense.** Frankland & Greene
  (2020, *Annu. Rev. Psychol.*) argue the semantic system recombines a fixed inventory of roles
  and predicates over arbitrary fillers — new verbs slot into the same Agent/Theme frame the
  system already applies. Minimal composition recruits a stable substrate (left anterior temporal
  lobe; Bemis & Pylkkänen 2011, *J. Neurosci.*) regardless of the specific words combined.

- **The impairment dimension is register-general.** The agrammatism argument-structure deficit
  (Thompson ASCH) is defined over the verb's frame, not over a genre — it does not "switch off"
  in expository vs narrative text. So the healthy operation it mirrors is likewise register-general.

### Faithfulness verdict (Q3)

- **PINNED:** event detection is a systematic structural operation the brain applies to novel
  verbs/registers by grammatical form, not an operating-point-specific pattern.
- A detector tuned on ONE register (past-tense narrative) that FAILS to transfer to another
  (present-tense expository) is therefore **diagnostic of a non-structural shortcut** (here: a
  surface tense cue), NOT of an intrinsic ceiling. This is exactly what we saw: removing the
  tense shortcut restored transfer. The observed out-of-domain generalization of the
  tense-agnostic detector is the *expected* signature of a brain-faithful, structural operation.
- **Refinement:** a residual register gap would be evidence of a *remaining* surface confound
  (e.g., a domain-specific lexical-verb list) rather than a capability limit — worth probing.

---

## Q4. SECONDARY GAP — COPULAR & NOMINALIZED EVENTS

### The mechanism (PINNED where imaging exists; PARTIALLY PINNED for copula)

**4a. Nominalized events (the DESTRUCTION of the city) recruit the VERB/event route because
they inherit argument structure.** Grimshaw (1990, *Argument Structure*) distinguishes
COMPLEX-EVENT nominals (retain the base verb's thematic grid + obligatory arguments) from RESULT
nominals (no argument structure). Neurally, Garbin, Collina & Tabossi (2012, *PLOS ONE*,
"Argument structure and morphological factors in noun and verb processing: an fMRI study") found
that **event nouns pattern with VERBS** — recruiting LIFG (BA45/46) — whereas OBJECT nouns
recruit parietal/temporal regions (BA40). Their conclusion: "when words sharing aspects of
knowledge are compared, they may act in similar ways regardless of their grammatical class" —
argument structure, not surface category, drives the event route. Alexiadou (2001,
*Functional Structure in Nominals*) gives the syntactic account: eventive interpretation is tied
to the presence of verbal argument-structure layers inside the nominal.

**4b. Copular / stative predication is handled by the general combinatory structure-building
network; the copula is a functional (light) element, the predicate content sits in its
complement.** Linguistically, copular clauses are syntactic predications (Mikkelsen 2011,
"Copular clauses", in *Semantics: An International Handbook*); *be* is largely a functional tense/
agreement carrier and the predicate is the AP/NP/PP complement (*Paris IS [the capital]*).
Neurally, predication and combinatory semantics engage the same IFG + pSTS/ATL composition
network identified in Q1 (Matchin & Hickok 2020; Bemis & Pylkkänen 2011; Pylkkänen 2019,
*Science*, "The neural basis of combinatory syntax and semantics" — review of the composition
network). **Caveat (honesty / absence-enumeration):** I did not find a dedicated fMRI/MEG study
isolating COPULAR predication as a category; this route is inferred from the general predication/
composition literature, so treat 4b as PARTIALLY PINNED (linguistic pinning strong; direct
neuroimaging localization weak).

### Faithfulness verdict (Q4)

- **Our detector, and the gold UPOS=VERB target class, EXCLUDE both** copular predications and
  event nominals — this is a genuine, brain-relevant gap, because the brain routes complex-event
  nominals through the SAME event machinery as verbs, and treats copular clauses as predications.
- **NOT faithful on this axis (by construction).** A UPOS=VERB gate under-generates events: it
  will miss *the destruction of the city* (an event the brain represents with full argument
  structure) and *Paris is the capital* (a predication).
- **Refinement suggested (strong):** the brain-faithful target is not "surface part-of-speech =
  VERB" but "**predicate that projects argument/event structure**." That reunites finite verbs,
  copular predications, and complex-event nominals under ONE detection criterion — matching the
  Garbin et al. finding that event nouns and verbs share the route. This is the single largest
  fidelity upgrade the literature points to, and it subsumes the tense-agnostic fix as a special
  case (drop surface features — tense AND part-of-speech-label — key on argument-structure
  projection instead).

---

## Summary table: PINNED mechanism vs our detector

| Question | PINNED brain mechanism | Our detector faithful? | Refinement |
|---|---|---|---|
| Q1 tense-agnostic | Event = argument-structure at the predicate; tense a separable bound feature; present ≤ past in cost (never gated) | YES (core computation copied) | Emit event + attach separate time-reference slot |
| Q2 N/V disambig. | Category committed from LEFT/predictive context in LIFG ~80 ms; agreement + distribution cues | YES (context tagger replaces form lookup) | Add explicit agreement/determiner feature; make it incremental-predictive |
| Q3 systematicity | Structure-building generalizes to novel items by grammatical form (Jabberwocky) | YES; transfer is the expected signature | Residual register gap ⇒ hunt remaining surface confound |
| Q4 copular/nominal | Complex-event nominals share the VERB route via argument structure; copula = functional, predicate in complement | NO (UPOS=VERB under-generates) | Retarget to "projects argument/event structure," not surface POS |

---

## PRE-REGISTERED PREDICTIONS (for a follow-on experiment)

Confidences are lit-scan-deflated and stated as hypotheses-pending-VET (fair-test + can-fail +
one-variable required before any is treated as a result). Each has a can-fail discriminator.

**P1 — Present-is-not-harder (Q1 core).** On a tense-balanced gold set, the tense-agnostic
detector's event-recall on PRESENT-tense finite clauses will be ≥ its recall on PAST-tense
clauses (matched for verb frequency and argument-structure density), within CI. *Can-fail:* if
present-recall is significantly BELOW past, a residual surface-tense dependency remains.
*Prior confidence ~0.65* (brain gradient makes present the cheaper form; risk = corpus
imbalance in verb types).

**P2 — Context beats form on zero-derivation items (Q2).** On a held-out set of the N/V
zero-derivation ambiguous forms (*runs/plans/results/needs/…*), the context-sensitive (Viterbi/
left-context) tagger will cut category errors by ≥50% relative to the isolated-word tagger, with
the largest gains on items whose disambiguation requires a preceding determiner/pronoun or
subject-verb agreement cue. *Can-fail:* if error reduction is uniform across cue-present and
cue-absent items, the win is not context-driven. *Prior confidence ~0.6.*

**P3 — Agreement cue carries the residual (Q2 refinement).** Adding an explicit
agreement/determiner feature (or an incremental left-context model) on top of the Viterbi tagger
will further reduce N/V errors specifically on agreement-diagnostic items (subject-number
disambiguates), with negligible change on non-diagnostic items. *Can-fail:* no differential gain
⇒ agreement is already implicitly captured and the refinement is unnecessary. *Prior confidence
~0.45* (novel-synthesis-capped).

**P4 — Register transfer is structural, not tuned (Q3).** The tense-agnostic detector trained/
tuned on past-tense narrative will retain ≥90% of its in-domain event-recall when evaluated on
present-tense expository text, and any residual drop will be traceable to specific
out-of-vocabulary lexical verbs (not to tense or genre per se). *Can-fail:* a drop that
correlates with tense/genre rather than OOV-verb rate indicates a lingering surface confound.
*Prior confidence ~0.6* (consistent with observed OOD generalization).

**P5 — Argument-structure target subsumes the POS target (Q4).** Retargeting detection to
"predicate that projects argument/event structure" (adding copular predications and
complex-event nominals, excluding result nominals) will raise total event/role recall on a
gold set that INCLUDES copular + nominalized events, WITHOUT lowering precision on the original
finite-verb items. *Can-fail:* if precision on finite verbs drops materially, the broadened
criterion over-generates (e.g., swallows result nominals / stative non-events) and needs a
tighter argument-structure test. *Prior confidence ~0.4* (novel-synthesis-capped; the
complex-vs-result nominal boundary is the main risk).

---

## TLDR (plain language)

The brain decides "this clause describes something happening" by spotting a predicate and the
who/what slots around it — and it does this the same way whether the sentence is in the past or
the present. In fact, where there's any difference, the PAST is the harder, more effortful form
for the brain, and the present is the easy default. So our old detector, which only fired on
past-tense verbs, was working backwards from how the brain does it; firing on every verb
regardless of tense matches the brain. For telling apart words that can be either a noun or a
verb (like "runs" or "plans"), the brain does NOT look at the word alone — it uses the words
around it and grammatical agreement, and it commits the decision extremely fast. So switching
from a one-word-at-a-time tagger to one that reads the surrounding context is also how the brain
works. One real gap remains: the brain also treats "the destruction of the city" and "Paris is
the capital" as events/predications, but our detector (and its scoring target) currently ignore
both. The literature says the better target is "anything that projects an event with roles,"
which would fold verbs, "is"-statements, and event-nouns into one rule.

## QUESTIONS
None blocking. (One open design choice for the solver, not a question for the owner: whether P5's
argument-structure retarget is in-scope for THIS problem or a separate follow-on — it is the
largest fidelity lever but also the largest new surface.)

## NEXT STEPS
1. Solver: treat P1/P2/P4 as the immediate can-fail confirmations of the moves already made
   (cheap; data already on hand).
2. Solver: scope P5 (argument-structure-projecting predicate as the detection target) as the
   next fidelity build — it subsumes the tense fix and closes the copular/nominal gap in one move.
3. Bind a separate `time_reference` feature onto each detected event (Q1 refinement) rather than
   discarding tense — matches the brain's factorized code and is near-free.

---

## References (author, year, finding)

- Alexiadou, A. (2001). *Functional Structure in Nominals*. Eventive nominals contain verbal
  argument-structure layers → argument structure licenses event interpretation.
- Bastiaanse, R., et al. (2011, *J. Neurolinguistics*). PADILIH: PAST time reference selectively
  impaired (needs discourse-linking); present/non-past better preserved.
- Bemis, D.K. & Pylkkänen, L. (2011, *J. Neurosci.*). Minimal two-word composition recruits left
  anterior temporal lobe regardless of the specific words.
- Dikker, S. & Pylkkänen, L. (2013, *Brain & Language*); Dikker, Rabagliati & Pylkkänen (2009,
  *Cognition*). Predictive syntactic context preactivates the expected word-category's form
  features in left temporal / visual cortex.
- Faroqi-Shah, Y. & Dickey, M.W. (2009, *Brain & Language*). Longer RTs to past- than
  present-reference stimuli; tense as a diacritic morphosemantic feature.
- Faroqi-Shah, Y. & Friedman, L. (2015, *Behavioural Neurology*). Meta-analysis: verb-tense
  production deficit is a separable impairment in agrammatism.
- Fedorenko, E., et al. (2010, *J. Neurophysiol.*; 2012, *PNAS*; lab 2024). Language network
  builds structure over Jabberwocky but not word-lists → content-independent, systematic
  composition; parsability drives engagement.
- Frankland, S.M. & Greene, J.D. (2015, *PNAS*). lmSTC independently decodes agent and patient →
  factorized (neo-Davidsonian) argument code, tense-independent.
- Frankland, S.M. & Greene, J.D. (2020, *Annu. Rev. Psychol.*). Compositionality / language of
  thought: systematic recombination of roles and predicates over arbitrary fillers.
- Garbin, G., Collina, S. & Tabossi, P. (2012, *PLOS ONE*). Event nouns pattern with VERBS (LIFG)
  via inherited thematic grid/subcategorization; object nouns pattern with parietal noun regions.
- Grimshaw, J. (1990, *Argument Structure*). Complex-event nominals retain the verb's argument
  structure; result nominals do not.
- Kratzer, A. (2002); Parsons, T. (1990). Neo-Davidsonian event semantics: clause = event
  variable + separately conjoined thematic-role predicates.
- Matchin, W. & Hickok, G. (2020, *Cerebral Cortex*). Posterior IFG (BA44) + posterior temporal
  cortex build hierarchical syntax in comprehension AND production.
- Mikkelsen, L. (2011, "Copular clauses"). Copular clauses are syntactic predications; *be* is a
  functional element, the predicate is its complement.
- Molinaro, N., Barber, H.A. & Carreiras, M. (2011, *Cortex*). Subject-verb agreement processed
  online; violations elicit LAN/P600 at the verb.
- Pylkkänen, L. (2019, *Science*). Review of the neural composition network (IFG, ATL, pSTS/AG).
- Shapiro, K. & Caramazza, A. (2003, *Neuropsychologia*); Vigliocco et al. (2011, *Psychol.
  Bull.*). N/V processing differences; grammatical class per se is not the organizing principle —
  distributional + semantic cues distinguish nouns from verbs.
- Steinhauer, K. & Drury, J.E. (2012, *Brain & Language*). Critique of the ELAN as a reliable
  word-category first-pass marker (baseline/artifact confounds) — cite ELAN cautiously.
- Strijkers, K., et al. (2019, *Scientific Reports*). Grammatical class discriminated in LIFG
  ~80–100 ms WHEN syntactic context is predictive → context-driven, not isolated-form.
- Thompson, C.K. (2003, *J. Neurolinguistics*). Argument Structure Complexity Hypothesis: verb
  difficulty scales with argument-structure density, orthogonal to tense/inflection.
- Ullman, M.T. (2001, *Nat. Rev. Neurosci.*). Declarative/procedural model: inflectional tense =
  procedural (LIFG + basal ganglia), separate from declarative lexical stem storage.
