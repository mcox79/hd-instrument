# Research drill (DEEP): how the brain decides a clause is a FORCE-DYNAMIC CAUSATION event vs a stative / perception / possession / light-verb / idiom use of the SAME verb — online, reliably, WITHOUT a modular word-sense module

**Date:** 2026-08-30 · **Drill type:** literature (psycholinguistics / lexical semantics / neuroscience), LEAD-WITH-BIOLOGY · **For problem:** `wire_the_causation_typer_into_the_live_reader` (SOLVED; this is a verdict-INDEPENDENT fidelity drill on the OPEN precision problem the SOLVED.md names — the open-text over-fire on non-force senses of force verbs, which the filed `no_glass_box_verb_sense_disambiguation` problem owns).

**Why this drill is NOT a re-run of the two prior drills.** The prior drills (`research_within_clause_causative_extraction...`, `research_construction_generalization...`) answered the POSITIVE-DETECTION question: given a clause IS a causative, detect it, bind its roles, read its endstate, and generalize across constructions. This drill answers the orthogonal DISCRIMINATION / FALSE-POSITIVE-SUPPRESSION question: **the very same verbs the typer fires on (see, have, make, keep, give, hold) are used in non-force senses far more often than in force senses in running narrative, and the reader must NOT run force typing on those.** The measured failure that motivates this: on open text (Bleak House) the detector went 16 → 41 links once construction routes were on, mostly spurious CAUSE on light/polysemous verbs; and a verb-sense gate (the WSD organ's frame posterior + label + argument concreteness) was **net-harmful** — each cue removed only ~15% of false positives while COSTING accuracy on genuine force clauses.

**Calibration:** lit-scan penalty applied — verdicts are mechanism-class reads, not effect-size promises. Where tempted to over-claim I say "predominantly / the widest single cue".

---

## BOTTOM LINE (verdict first) — the director's hypothesis is CONFIRMED, with one addition and one sharpening

The load-bearing mechanism is **NOT verb-sense classification.** It is **graded constraint-satisfaction over the verb TOGETHER WITH its arguments** (McRae/Elman thematic-fit architecture), in which the specific force-relevant constraints are:

1. **PATIENT AFFECTEDNESS** (patient side) — does the object denote a pre-existing entity that undergoes a **scalar change of state / location**? *(the widest single discriminator)*
2. **AFFECTOR FORCE-FIT** (affector side) — does the subject denote a plausible **force source** (agent / instrument / natural force), NOT an experiencer or a static holder?
3. **EVENTIVITY / CHANGE** (clause side) — is the clause a **dynamic change** (a new event) vs a **static relation** (a state that merely holds)? *(this is the leg the director's hypothesis did not name; it is what most directly kills the STATIVE / POSSESSION cases — have/know/own/inherit)*

These three are computed **jointly** and combined into a single graded **force-engagement score** — no single one is a reliable classifier alone, which is *exactly* why the hard verb-sense gate failed (each leg alone ≈ the ~15% the project measured). **The conjunction IS the "sense"** — you never separately label the verb; you read the force-relevant properties of the whole argument configuration and let them vote. Genuine force clauses ("the key opened the gate", "the storm flooded the village", "the bar kept the gate from opening") score strongly on all three; the false positives fail two or three legs. That asymmetry is the entire mechanism, and every input is computable from what the parser already provides.

**The sharpening the literature forced:** a fourth distinct class the affectedness leg must separate — **CREATION / EFFECTED OBJECT** ("make a fire", "MAKE a pretence", "MAKE an application", "GIVE judgment", "build a house"). Here the object does NOT pre-exist to be forced — it comes INTO existence (light-verb / creation). Dowty flags it as proto-patient too ("comes into being"), so a naive change-of-state test can misfire; but it is **causal-of-existence, not force-on-a-tending-patient**, so the Wolff/Talmy CAUSE/ENABLE/PREVENT typer (which needs a patient WITH a tendency to evaluate) has nothing to type. Record it as creation if wanted; do NOT run the force-tendency typer. This is the mechanism behind the light-verb false positives specifically.

---

## MECHANISM 1 (THE ARCHITECTURE, and why the WSD gate structurally could not work) — PINNED

**Interpretation is emergent settling over the verb + its arguments simultaneously, not a pipeline of sense-selection-then-integration.** This is the load-bearing architectural claim and it is the reason a modular frame-classifier is the wrong shape.

- **McRae, Spivey-Knowlton & Tanenhaus (1998)** — thematic fit is a **graded constraint that influences interpretation immediately**, in the same time-window as syntactic cues; a *competition/constraint-satisfaction* model where "independently quantified syntactic and semantic constraints simultaneously influence interpretation" fits the reading-time data, and a **two-stage (syntax-first, then semantics) model does NOT.** A modular WSD gate is precisely a two-stage architecture (classify sense → then use arguments); the psycholinguistics rejects that ordering.
- **Elman (2009), "On the meaning of words and dinosaur bones: lexical knowledge without a lexicon"** — the **words-as-cues hypothesis**: a word is **not a container of a stored sense**; it is a **cue that operates on a distributed representation of event knowledge**. Verbatim from the source: *"Comprehension involves the computation of a representation of the relevant event, and the roles of the participants in that event, based on multiple cues... Rather than accessing fixed lexical entries, comprehenders dynamically compute an interpretation based on their knowledge of events... Knowledge of how different verbs cue other forms of knowledge is not reducible to a lexical entry."* **Consequence for us:** there is no discrete "force sense of KEEP" to retrieve and gate on. The force reading either emerges from the argument configuration or it does not. A module that tries to pick the sense *before* looking at the arguments throws away the only information that decides it.
- **Bicknell, Elman, Hare, McRae & Kutas (2010)** — the crispest evidence: whether a patient is expected depends on the **three-way fit between agent, verb, AND patient** ("mechanic checked → brakes" vs "journalist checked → spelling"), and norming **ruled out any direct agent–patient relation** — the N400 tracks the *combinatorial* fit. So the very identity of the event a verb denotes is fixed by its arguments together. **You cannot type the verb in isolation; the arguments are not noise to filter after sense selection — they ARE the disambiguator.**
- **Hare, Jones, Thomson, Kelly & McRae (2009)** + **McRae & Matsuki (2009)** — words rapidly activate **generalized event knowledge** (typical agents/patients/instruments/locations); this event knowledge is combined *intrasententially* (agent+verb) and influences online interpretation within the first fixation. Comprehenders "use their knowledge of common events... as quickly as possible."

**Verdict (PINNED architecture):** the fix is not a better upstream sense classifier. It is to compute the force-relevant properties (affectedness, force-fit, eventivity) **directly from the arguments** as graded evidence and combine them — constraint satisfaction, not classification. This is *why* the WSD gate was net-harmful: a hard label discards the graded, mutually-constraining evidence that makes the human decision robust, and applies its own noise as a veto on genuine force clauses.

---

## MECHANISM 2 — PATIENT AFFECTEDNESS as the event-structure signal (the widest single discriminator) — PINNED

A force-dynamic causative **entails a change in the patient**; perception, possession, stative relation, and light-verb uses do NOT. This is the single cue that fires against the most false-positive classes.

- **Dowty (1991), Thematic Proto-Roles and Argument Selection** — the **Proto-Patient** entailments: *undergoes a change of state (into/out of a state, change in size/shape/material), is causally affected by another participant, is an incremental theme, is stationary relative to the mover.* A true force-dynamic patient bears these; a possessed thing, a perceived stimulus, and an event-noun complement do NOT.
- **Beavers (2011), "On affectedness"** — affectedness is **scalar and relational**: an argument is affected iff there is an event and a **property scale** such that the patient **reaches a new state on that scale** through incremental motion along it. Two dimensions: *type of change* and *degree of change*. This gives a graded read: a result state / bounded change = high affectedness; a static relation = none.
- **Rappaport Hovav & Levin (2001/2010)** — **result verbs lexicalize a scalar change** (break/open/flatten); manner verbs do not, and the result comes from a secondary predicate. So a result signal (result XP, telic COS verb, path goal, particle) = a change-of-state entailment on the patient.
- **Tenny (aspectual measuring-out)** — the direct object **measures out** the event; only an affected/incremental object delimits the event. A stative or event-noun object does not measure out anything.

**Discriminating power against the given false positives:**
- "he SAW nothing" → **no affected patient** ("nothing"; the stimulus of perception does not change state). FAIL.
- "the court HAS its decaying houses" / "he INHERITED it" → the object is **possessed/received, not changed** (the houses are not altered by the court; the inherited thing is unchanged). Possession-change ≠ patient-affectedness. FAIL.
- "MAKE a pretence / MAKE an application / GIVE judgment" → the object is an **event/deverbal noun**, not an affectable entity (see Mechanism 5). FAIL.
- "KEEP an eye upon the judge" → "an eye" is a body-part idiom, not a patient being prevented from changing; and no from-complement (see the SOLVED's from-construction discipline). FAIL.

**PINNED:** affectedness = proto-patient change-of-state / scalar change. **OUR-INVENTION:** the cue detector (result-XP / path-goal / telic-COS-verb / particle / object-type check).

---

## MECHANISM 3 — AFFECTOR FORCE-FIT: the causer must be a plausible FORCE, and animacy is a COARSE, EARLY, robust constraint — PINNED

- **Wolff (2007), "Representing Causation"** (force theory; on Talmy 1988) — CAUSE/ENABLE/PREVENT are defined over **force vectors**: an **affector** force and a **patient** with a tendency, combining to a resultant directed at an endstate. The affector is, by definition, **something exerting a force.** A subject that is not a force source (an experiencer, a static institutional holder) has no affector vector — the schema does not apply.
- **Paczynski & Kuperberg (2012), JML** — the load-bearing neuro-evidence that a **coarse force-fit constraint is computed early and robustly and is DISTINCT from world-knowledge fit.** They separate two ERP signatures: (i) **animacy selectional-restriction** violations elicit an N400 that is **NOT attenuated by semantic relatedness** (and also elicit a P600), whereas (ii) real-world **event/state-knowledge** violations elicit an N400 that IS attenuated by relatedness. **Reading for us:** whether the subject is an animate/force-capable causer is a coarse, fast, hard-ish constraint the brain checks *separately* from fine world knowledge — exactly the kind of cheap, reliable, glass-box gate we can compute from argument animacy, and one that does NOT require fine sense disambiguation.
- **Experiencer ≠ agent (perception/psych verbs).** SEE/HEAR/FEEL take an **experiencer subject**, not an agentive force source; the subject does not exert force on the stimulus. So "he saw nothing" fails force-fit on the SUBJECT side too (double failure with the affectedness leg). This is a **coarse verb-CLASS** fact (perception/cognition/emotion frames), NOT fine WSD — we need to know "is this a perception/psych frame verb," not "which of KEEP's senses is this."

**Discriminating power:** perception (experiencer subject) FAILs; stative/abstract holders ("the court") FAIL; "smoke MAKING a drizzle" — smoke IS a force but the object "a drizzle" is created (Mechanism 5), so it fails on the patient side. Genuine causers (agent/instrument/wind/fire/heat/water) PASS.

**PINNED:** affector = force source (Wolff/Talmy); animacy as a coarse early selectional constraint (Paczynski & Kuperberg); experiencer ≠ agent. **OUR-INVENTION:** the animacy/force-noun/experiencer-frame lookup.

---

## MECHANISM 4 — EVENT vs STATE: the leg the hypothesis did not name, and the one that most directly kills possession/stative — PINNED

- **Zwaan & Radvansky (1998), Event-Indexing Model** — the situation model is **heightened-sensitive to DYNAMIC events (changes of state), not static elements**; **causation is one of the five tracked indices**, and a change in the causal flow is a boundary cue. Crucially the model creates/links **event nodes for changes**; a stative relation (have/know/see/own/resemble/contain) **updates a state, it does not open a new event node.** So the discourse machinery itself distinguishes "a change happened" from "a state holds," and force typing belongs only on the former.
- **Gennari & Poeppel (2003), "Processing correlates of lexical semantic complexity"** — a REAL ONLINE eventive/stative signal AT THE VERB: **eventive verbs (causally structured events) take reliably LONGER to process than stative verbs** in both lexical decision and self-paced reading, and this is a **lexical-access** effect (retrieved with the verb), not a later integration effect. So the brain marks eventive-vs-stative essentially at the verb — a fast, lexicalizable distinction we can approximate with a stative-verb inventory + the absence of any change signal.

**Discriminating power:** HAVE (possession, stative), INHERIT (a change of possession, but the PATIENT does not change — an achievement of transfer, not a force on a tending patient), KNOW/SEE/BELIEVE (stative cognition/perception), RESEMBLE/CONTAIN (stative relation) → all **state, not force-dynamic event.** FAIL. This leg is the cleanest kill for "the court HAS its decaying houses" and "he inherited it."

**PINNED:** event-vs-state distinction (Zwaan; Gennari & Poeppel). **OUR-INVENTION:** the stative-verb lexicon + "no change signal" test.

---

## MECHANISM 5 — LIGHT-VERB / CREATION: the object's own TYPE decides light-vs-causative — PINNED

This is the mechanism specifically behind the make/have/give/take/do false positives.

- **Pustejovsky, Generative Lexicon** — in a **light-verb (support-verb) construction**, the support verb (make/have/take/give/do) is **bleached**, and the eventive content comes from the **complement noun's qualia** (the AGENTIVE/TELIC quale of the deverbal noun). "make a decision" = the *deciding* event lives in "decision," not in "make." "give a look" = the *looking* is in "look." The verb contributes almost nothing; **the object IS the event.**
- **LVC detection literature (Fazly et al.; PropBank-based LVC identification)** — an LVC is reliably signalled by **a high-frequency light verb + a DEVERBAL / EVENTIVE noun object.** Concretely detectable: the object noun's WordNet class is under **{event, act, action, state, cognition, communication}** (a deverbal/eventive nominal) rather than under {physical entity, artifact, substance, person}. This is a **glass-box, sense-free** cue: you check the object's ontological type, you do NOT disambiguate the verb.
- **Creation / effected object (Dowty; Levin creation verbs)** — a distinct class: "make a fire", "build a house", "write a letter", "smoke making a drizzle". The object is an **incremental/effected theme that comes INTO existence** — there is **no pre-existing patient with a tendency** for an affector to overcome or concur with. It is causal-of-existence but **not the Talmy/Wolff force-on-a-tending-patient schema**, so the CAUSE/ENABLE/PREVENT typer has nothing to type (no tendency term). Treat as CREATION, do not force-type.

**Discriminating power:** "MAKE a pretence / an application", "GIVE judgment" → **eventive/deverbal-noun object → light verb → not a causative on a patient.** FAIL. "make a fire / a drizzle" → **effected/created object → creation → not force-on-a-tending-patient.** FAIL. This is a clean, sense-free, high-yield gate that the WSD gate was flailing at from the wrong direction.

**PINNED:** light verb gets its event from the complement's qualia (Pustejovsky); effected≠affected theme (Dowty/Levin). **OUR-INVENTION:** the WordNet-hypernym object-type buckets + deverbal-noun test.

---

## MECHANISM 6 — GROUNDED CORROBORATION: motor/force simulation does NOT engage for non-force uses, and engagement is driven by the WHOLE configuration, not the verb — PINNED

Independent, convergent evidence from the embodiment literature that the brain itself gates force/motor simulation by the argument configuration, not by the verb lemma:

- **Raposo, Moss, Stamatakis & Tyler (2009)** — motor/premotor cortex is engaged by literal action verbs (kick/grab) **but NOT when the same verb is in an idiom** ("kick the bucket"). Same lemma, no motor engagement — the configuration decides.
- **Desai, Binder, Conant & Seidenberg (2009/2011); "A piece of the action" (2013)** — a **graded LITERAL > METAPHORIC > IDIOMATIC > ABSTRACT** sensorimotor-engagement gradient for the SAME action verbs. Sensorimotor (force) simulation is *highly context-dependent*, increasing with the literal-physical fit of the whole sentence.
- **Bergen (2012), Louder Than Words** — embodied simulation is driven by the full construal, not the isolated verb.

**Reading for us:** the brain does NOT run a force-dynamic/motor simulation on "he saw nothing", "make a pretence", "keep an eye on" — and what turns simulation off is the **argument configuration** (abstract/idiomatic/non-affecting), exactly the same signal our three-leg score reads. This is a second, neural line of evidence for the same architecture, and it validates the project's already-integrated LIT>MET>ABS gradient + literalness gate as a *partial* implementation of the eventivity/concreteness leg.

---

## PER-FALSE-POSITIVE WALKTHROUGH (how the three-leg score kills each without a WSD label)

| clause | affectedness (patient) | force-fit (affector) | eventivity (clause) | verdict |
|---|---|---|---|---|
| "he SAW nothing" | FAIL (no affected patient; perception stimulus) | FAIL (experiencer subject, no force) | FAIL (perception is stative) | ABSTAIN (3 legs fail) |
| "the court HAS its decaying houses" | FAIL (houses possessed, not changed) | FAIL (static holder, no force) | FAIL (HAVE stative) | ABSTAIN |
| "he INHERITED it" | FAIL (recipient/transfer, patient unchanged) | FAIL (recipient, not force source) | WEAK (achievement of transfer, no patient change) | ABSTAIN |
| "MAKE a pretence / an application" | FAIL (eventive/deverbal-noun object → light verb) | (agent OK) | (dynamic OK) | ABSTAIN (light-verb: object IS the event) |
| "GIVE judgment" | FAIL (eventive noun → light verb) | (agent OK) | (dynamic OK) | ABSTAIN |
| "smoke MAKING a drizzle" | FAIL (effected/created object) | (smoke = force OK) | (dynamic OK) | ABSTAIN (creation, not force-on-patient) |
| "KEEP an eye upon the judge" | FAIL (body-part idiom; no from-complement) | (agent OK) | (attention state) | ABSTAIN (idiom + no prevention construction) |
| **"the key OPENED the gate"** (genuine) | PASS (gate → open, result COS) | PASS (instrument = force) | PASS (change) | **ENGAGE → type** |
| **"the bar KEPT the gate from opening"** (genuine PREVENT) | PASS (gate has tendency; endstate blocked) | PASS (bar = force) | PASS (prevented change) | **ENGAGE → type** |

The genuine force clauses pass all three legs, so **the joint gate does not cost accuracy on them** — the specific failure mode of the WSD gate. The false positives fail 2–3 legs each. No verb-sense label is computed anywhere.

---

## THE RECIPE — a glass-box FORCE-ENGAGEMENT score that does NOT depend on a reliable verb-sense classifier

Compute a graded engagement score from the parse; engage the CAUSE/ENABLE/PREVENT typer only if the joint score clears threshold. All inputs are argument/construction properties the reader/parser already exposes; **none require disambiguating the verb's sense.**

**LEG A — PATIENT AFFECTEDNESS (highest weight):**
- `patient_present`: there is a direct object / causee / nsubjpass that denotes a **pre-existing, concrete, affectable entity** (not "nothing", not a clause). [OUR-INVENTION: existence + concreteness check — reuse the substrate's object-concreteness.]
- `object_is_eventive_or_deverbal` (light-verb kill): object's WordNet hypernym ∈ {event, act, action, state, cognition, communication} OR object is a deverbal nominal → **NOT an affectable patient → subtract heavily.** [PINNED: Pustejovsky qualia light-verb; OUR-INVENTION: hypernym buckets.]
- `object_is_effected` (creation kill): verb ∈ creation set (make/build/create/form/write/draw/produce) AND the object comes into existence (no pre-state) → **creation, not force-on-patient → route to CREATION, do not force-type.** [PINNED: Dowty effected theme; OUR-INVENTION: creation-verb set.]
- `change_signal`: a result XP (resultative adj), path goal (caused-motion), telic COS result verb (break/open/flatten), or particle (up/out) → **add.** [PINNED: Dowty/Beavers/RH&L change-of-state; OUR-INVENTION: cue detector — reuse the endstate reader.]

**LEG B — AFFECTOR FORCE-FIT:**
- `affector_is_force_source`: subject is animate (WordNet person/animal) OR a canonical physical force (instrument, wind/fire/heat/water/energy nouns) OR a concrete physical entity that can transmit force → **add.** Static/abstract/institutional subject → **subtract.** [PINNED: Wolff affector=force; Paczynski & Kuperberg coarse animacy constraint; OUR-INVENTION: animacy/force-noun lookup.]
- `experiencer_frame` (perception/psych kill): verb is a perception/cognition/emotion frame (coarse VerbNet/FrameNet class — NOT fine WSD) with the subject as experiencer → **subtract heavily.** [PINNED: experiencer≠agent; OUR-INVENTION: coarse frame-class lookup.]

**LEG C — EVENTIVITY / CHANGE:**
- `verb_is_stative` (possession/stative kill): verb ∈ stative inventory (have/own/possess/know/believe/see[perceptual]/hear/contain/resemble/belong/consist/cost) AND no change signal from Leg A → **subtract heavily.** [PINNED: Zwaan event-indexing state-vs-event; Gennari & Poeppel online eventive/stative; OUR-INVENTION: stative lexicon.]
- `asserts_a_change`: the clause opens a new event node (a change happened) vs updates a state → **add** for the former. [PINNED; OUR-INVENTION: rule.]

**COMBINE (constraint satisfaction, NOT a sequential veto):** `engage_force = w_A·A + w_B·B + w_C·C ≥ θ`, a **graded additive score**, so a strong signal on two legs carries a weak third (robustness the hard gate lacked). Route: eventive-noun/effected object → CREATION/LIGHT (abstain from force typing); stative + no change → STATE (abstain); else if the joint score clears θ → ENGAGE the existing Wolff typer. **Sweep θ and the weights** on the causative-clause gold + an open-text precision slice (Bleak House) — pick the operating point that recovers open-text precision WITHOUT costing the within-clause recall the SOLVED already banked. Report it as a precision/recall curve, not a single number.

**Why this is the fix and the WSD gate was not:** the WSD gate classified the VERB (a two-stage, error-prone label) and vetoed on it, discarding graded argument evidence. This reads the FORCE-RELEVANT PROPERTIES OF THE ARGUMENTS (which the parse already provides), never labels the verb, and combines graded evidence — the McRae/Elman constraint-satisfaction architecture. It is not new machinery so much as a **reframe** of pieces the substrate already has (object concreteness, endstate/result reader, from-construction discipline, literalness/LIT-MET-ABS gate) into a three-leg additive gate, PLUS the two genuinely-missing legs: (i) the **light-verb/creation object-type check** and (ii) the **affector force-fit / experiencer-frame check.**

---

## WHAT THE LITERATURE DOES NOT SETTLE (honest caveats)

1. **The brain's constraint satisfaction is continuous, world-knowledge-rich, and massively parallel; our discrete-cue score is a coarse proxy.** McRae's thematic fit is human ratings over real event knowledge; WordNet buckets + lexicons are a lossy approximation. Where the buckets are wrong (a physical noun used as an event: "he made a FIRE" — fire is physical yet creation), the proxy errs — hence the explicit creation/effected-object route.
2. **The three legs are graded and probabilistic, so the gate is graded too** — there is no hard 100% cut. Expect a precision/recall tradeoff, not a clean separation. This is faithful (the brain is graded), but it means the deliverable is an operating-point choice, not a solved boolean.
3. **The brain's own discrimination is fallible at the same margins the project already respects** — role-reversed / non-canonical order (Ferreira good-enough; N400 insensitive to role reversal). A gate that fails there is brain-faithful, not a bug.
4. **Metaphor is intentionally left ENGAGING.** Desai shows metaphoric action sentences DO engage sensorimotor cortex (only idioms fully disengage). The already-cited LIT>MET>ABS gradient means figurative-but-apt force uses ("the news crushed her") are a **soft** case, not a hard abstain — the score should down-weight, not veto, matching the gradient. Do not over-abstain on metaphor.
5. **Not a WSD replacement in general** — this solves force-vs-non-force ENGAGEMENT, the project's specific precision leak. It does not disambiguate senses that BOTH pass the three legs (e.g. two genuine causatives in one clause — the SOLVED's "pulled the plug, allowing to drain" residual). That remains the filed cross-clause/selection problem.

---

## MAPPING TO EXISTING SUBSTRATE (this is a reframe + 2 additions, not a rebuild)

| leg | already in substrate | genuinely missing (build) |
|---|---|---|
| A affectedness | object concreteness; endstate/result reader; from-construction discipline | **object-type check: eventive/deverbal-noun (light verb) + effected-object (creation) routing** |
| B force-fit | (partial: none dedicated) | **affector animacy/force-source + experiencer-frame (coarse class) check** |
| C eventivity | literalness gate (ENGAGE_PHYSICAL) + LIT>MET>ABS gradient (partial) | **stative-verb inventory + no-change test as an explicit leg** |
| combine | (WSD gate — net-harmful, hard veto) | **replace with a graded additive 3-leg score + swept θ** |

The two missing legs (light-verb/creation object-type; affector force-fit/experiencer) are precisely what the WSD gate was trying to substitute for from the wrong direction. Both are cheap, glass-box, and sense-free.

---

## KEY CITATIONS
- **McRae, Spivey-Knowlton & Tanenhaus (1998)** "Modeling the influence of thematic fit (and other constraints) in on-line sentence comprehension," *JML* 38, 283–312. — constraint-satisfaction beats two-stage; thematic fit is immediate.
- **Elman (2009)** "On the meaning of words and dinosaur bones: lexical knowledge without a lexicon," *Cognitive Science* 33, 547–582. — words-as-cues; no stored discrete senses; interpretation computed over event knowledge + arguments.
- **Bicknell, Elman, Hare, McRae & Kutas (2010)** "Effects of event knowledge in processing verbal arguments," *JML* 63, 489–505. — the three-way agent×verb×patient fit (arguments disambiguate the event; not direct agent–patient relations).
- **Hare, Jones, Thomson, Kelly & McRae (2009)** "Activating event knowledge," *Cognition* 111, 151–167; **McRae & Matsuki (2009)**. — generalized event knowledge activated + combined rapidly.
- **Dowty (1991)** "Thematic proto-roles and argument selection," *Language* 67. — proto-patient = change of state / causally affected / incremental / effected theme.
- **Beavers (2011)** "On affectedness," *NLLT* 29, 335–370. — affectedness = scalar reach of a new state on a property scale; graded.
- **Rappaport Hovav & Levin (2001/2010)**; **Tenny (1994)**. — result = scalar change; object measures out the event.
- **Wolff (2007)** "Representing causation," *JEP:General*; **Talmy (1988)**. — affector = force vector; CAUSE/ENABLE/PREVENT over patient-tendency × concordance × endstate.
- **Paczynski & Kuperberg (2012)** "Multiple influences of semantic memory on sentence processing," *JML*. — animacy selectional-restriction is a coarse early constraint (N400 not attenuated by relatedness; +P600), DISTINCT from world-knowledge fit.
- **Zwaan & Radvansky (1998)** "Situation models in language comprehension and memory," *Psych Bulletin* — event-indexing; causation an index; sensitivity to changes not states.
- **Gennari & Poeppel (2003)** "Processing correlates of lexical semantic complexity," *Cognition* 89, B27–B41. — eventive verbs cost more than stative, at lexical access (online event/state signal).
- **Pustejovsky (1995)** *The Generative Lexicon*; LVC detection (Fazly et al.; PropBank-based). — light verb gets its event from the complement's qualia; LVC = light verb + deverbal/eventive noun.
- **Raposo, Moss, Stamatakis & Tyler (2009)**; **Desai, Binder, Conant & Seidenberg (2009/2011)** "A piece of the action" (2013); **Bergen (2012)**. — motor/force simulation gated by the whole configuration (idiom off; LIT>MET>ABS gradient), not the verb lemma.

---

## TLDR
A good reader instantly knows the difference between "the fire burned the house" (a real force) and "he saw nothing," "the court has its old houses," "he inherited it," "make an application," "give judgment," or "keep an eye on the judge" — even though these use the very same verbs our force-detector fires on, and even though the reader plainly does NOT run a "look up which meaning of the verb" step. The literature says why: people do not pick a word's meaning first and then read the sentence — the meaning EMERGES from the verb and its who/what-to arguments settling together (McRae; Elman; the agent+verb jointly decide the expected object). So the right fix is NOT a better word-sense guesser (ours was actively harmful). It is to read three cheap properties of the sentence's PARTS and let them vote: (1) does the thing acted on actually CHANGE (a real patient), or is it just possessed/perceived/an event-word like "a decision"/a thing being created? (2) is the DOER a real force (a person, wind, fire, a tool) rather than a watcher or a static owner? (3) is this a happening (a change) or just a state that holds (have/know/own)? Genuine force sentences score high on all three; the false alarms fail two or three — and none of it requires guessing the verb's sense. Two of the three checks already partly exist in our substrate; the two genuinely new ones are a check on what the OBJECT is (an event-word or a newly-created thing means "not a force") and a check on whether the SUBJECT can exert force. Build them as a graded score, not a hard on/off gate — that graded-vote design is exactly what makes the brain robust and what the hard word-sense gate lacked.

## QUESTIONS
None. (The mechanism is confirmed convergently across psycholinguistics, lexical semantics, and neuroscience; the recipe is glass-box and sense-free; the honest limits — graded operating point, metaphor left soft, role-reversal a brain-faithful bound — are enumerated.)

## NEXT STEPS
1. **Build the two missing legs as a graded FORCE-ENGAGEMENT score** in an experiment cell (NOT hdlab — that is strategy's land): (i) object-type check (WordNet hypernym: eventive/deverbal → light-verb abstain; effected → creation route) and (ii) affector force-fit (animacy/force-noun + coarse experiencer-frame). Reuse object-concreteness, the endstate reader, and the literalness/LIT-MET-ABS gate for the other cues. This is the concrete recipe the filed `no_glass_box_verb_sense_disambiguation` problem should adopt — it reframes that problem from "build a WSD gate" (measured net-harmful) to "read affectedness + force-fit + eventivity from the arguments."
2. **Measure it as a precision/recall curve** on the SOLVED's causative-clause gold (recall must not drop — the within-clause win is banked) AND an open-text precision slice (Bleak House 16→41 over-fire): sweep θ, report the operating point, verify the info-free twin loses. A rigorous negative (the graded gate cannot recover open-text precision without costing within-clause recall) is a full result — report which leg is the bottleneck.
3. **Keep metaphor SOFT, not vetoed** (Desai LIT>MET>ABS) — down-weight, do not abstain, on apt figurative force ("the news crushed her"); only idioms and stative/possession/light-verb/creation get the hard abstain.
4. **AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b:** the force-vs-non-force discrimination is PINNED to constraint-satisfaction over arguments (affectedness + force-fit + eventivity), NOT to modular WSD — record that a verb-sense-classifier gate is the wrong architecture (measured net-harmful; predicted by McRae 1998 two-stage rejection + Elman 2009 no-discrete-senses).
