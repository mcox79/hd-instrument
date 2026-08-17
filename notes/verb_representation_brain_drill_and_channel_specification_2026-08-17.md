# DRILL: which brain structure represents verb meaning, and what should our verb channel BE?

**2026-08-17, Director (research role). BIOLOGY-FIRST DRILL + BUILD SPECIFICATION.
No experiment cell authored. No experiment run. No subagent dispatched. No file under
`experiments/`, `hdlab/`, `data/foundation/`, `preregs/` or `data/capability_registry.jsonl`
modified. Nothing deleted. Only this note is written and committed; no push to origin.**

**No tool call was denied during this drill.** Two tool ERRORS are disclosed rather than worked
around, both on external publishers: `WebFetch` returned **HTTP 403 Forbidden** on
`sciencedirect.com/science/article/pii/S0093934X1400039X`, on
`biorxiv.org/content/10.1101/2025.08.22.671793v1.full` and on
`jneurosci.org/content/45/41/e2166242025`; and the ACL PDF of the SimLex-999 paper returned raw
PDF binary that the fetcher could not parse. In each case the SAME finding was obtained from an
accessible mirror (PMC for the J Neurosci paper; search-result summaries for the ScienceDirect
one) and I say below which claims rest on a full-text read versus on an abstract or a search
summary.

---

## WHAT LICENSES THIS DRILL

`notes/item2_verb_target_space_n222_measurement_2026-08-17.md` +
`data/exp_verb_target_space_n222_v1/metrics.json` (commit `0652e20a5`), both read off disk this
pass. At a sample size where a margin could separate, the 12-dimensional meaning space:

| stratum | n | K1_OWN_NORMS rho | strongest floor | margin over it | band |
|---|---|---|---|---|---|
| N | 666 | 0.2745 | F_SCRAMBLE_PERM_P95 0.0680 | **+0.2065 [+0.1015, +0.3102]** | **ABOVE**, CI-separated over all four |
| **V** | **222** | **0.2607** | **F_SCRAMBLE_PERM_P95 0.1152** | **+0.1452 [-0.0496, +0.3379]** | **NOT_SEPARATED** (row-permutation p=0.000999) |
| A | 111 | 0.1472 | F_SCRAMBLE_PERM_P95 0.1546 | -0.0074 [-0.2666, +0.2479] | NOT_SEPARATED (p=0.0605) |

The verb null width fell from 0.1784 at n=86 to a measured 0.1152 at n=222, matching the analytic
orientation 1.645/sqrt(221)=0.1107 (ratio 1.04). **The null tightened as predicted, so this is an
honest negative and not the underpowered artifact it replaced.** Every number in this drill's build
specification cites THIS measurement. The retired n=86 measurement is never quoted.

---

# (a) PLAIN-LANGUAGE SUMMARY — read this part if you read nothing else

**The one-sentence finding.** Our 12 numbers per word are, almost exactly, the list of things that
tell OBJECTS apart — and almost none of the things that tell EVENTS apart. A 2025 brain study
ranked which experiential qualities matter most for event concepts versus object concepts; our 12
numbers cover roughly **6 of their 13 object-defining qualities and only 2 of their 13
event-defining qualities.** So nouns clearing and verbs not clearing is not a mystery and not a
ceiling — it is what you would predict from the shopping list we happen to have bought.

**The thing we were missing is not "more numbers", it is the RIGHT numbers.** The event-defining
qualities they found are: whether something involves *thinking*, *harm*, *communication*, *social
life*, *benefit*, *speech*, *fear*, *complexity*, and *whether it has consequences*. Our list is
sight, sound, taste, smell, touch, gut-feeling, and which body part you use. Those two lists barely
overlap. A verb like *persuade* scores near zero on every single one of our 12 — which is exactly
why the owner, asked what *persuade* feels like, said "I picture the conversation, and also a
feeling". Conversation is *communication*. The feeling is *affect*. We measure neither.

**Is a verb a POINT (a place in a space, like a noun) or a TRANSFORMATION (a machine that takes
things in and changes them)?** The honest answer is **BOTH, in two different brain places, and we
have been trying to make one thing do both jobs.**

- The *dictionary entry* for a verb — what "pour" is like, how it resembles "spill" — really does
  live as a point in the same kind of space nouns live in. A 2025 study trained a decoder on event
  concepts and it successfully read out object concepts, and vice versa. Same code. So landing
  verbs in a shared space is **not** a category error, provided the space has the event axes.
- The *argument structure* — "someone pours something into something" — is a **separate
  representation in a separate structure**. There is a strip of left temporal cortex that holds
  "who did it" and "to whom was it done" in adjacent but distinct subregions, as slots whose
  contents change sentence by sentence. That is not a longer vector. No number of extra dimensions
  produces a slot.

So the build is: **give verbs the event axes they are missing (a point-like fix, cheap, testable
now), and keep argument structure as a separate typed-slot organ (which we already partly own and
which is the genuinely hard build).** Do not try to cram slots into the vector.

**The strongest argument AGAINST doing any of this, stated honestly.** Our ruler may simply be too
short. SimLex-999 gives us only 222 verb pairs. Human raters agree with each other much less on
verb similarity than the headline figure suggests (the verb-specific benchmark's agreement was
corrected downward from 84.0 to 61.2). With 222 pairs the error bar on the number we need to move
is about +/-0.19, which is bigger than the whole effect. **A longer ruler exists — SimVerb-3500,
3,500 verb pairs — and it is not on our disk.** Acquiring a gold-standard test set is not the same
as importing a meaning source; it is buying a tape measure. **I recommend acquiring it BEFORE
running the channel experiment, because otherwise a real improvement will very likely come back as
"not separated" again and be banked as a null.**

**What I recommend, in order.** (1) Acquire SimVerb-3500 as a ruler. (2) Run one experiment that
adds five event-axis columns to the verb's vector and, in the same run, tests the rival idea that a
verb should instead be described by *what fills its slots* — with a deliberately useless
five-column control that must NOT improve anything, or the whole story is refuted. (3) Only after
that, build the typed-slot organ.

---

# (b) THE PER-SYSTEM COMPUTATIONAL ACCOUNT

Every claim is marked **[PINNED]** (the evidence fixes it), **[PINNED-AS-PROPOSAL]** (a published
framework, not an independently dissociated neural system), or **[UNPINNED]** (ours to choose and
test). Where a claim is a *cognitive-theory label* rather than a *neural system* I say so
explicitly, per the standing MECHANISM-vs-TASK-ANALOG rule.

## B1. MOTOR AND PREMOTOR CORTEX — the embodied/simulation account, and why it does NOT get to be our verb channel

**What it computes (on the strong version):** verb meaning is re-enactment. Reading *kick*
partially re-runs the leg's motor program in a somatotopically appropriate strip of precentral
cortex; meaning IS that simulation.

**What is PINNED:** somatotopic modulation of motor/premotor cortex by effector-specific action
verbs is a real and replicated *effect* (e.g. dissociable somatotopic responses to Chinese action
verbs in motor and premotor cortex, *Sci Rep* 2:2049). TMS to primary motor cortex measurably
changes the time course of motor-verb processing (PMC2643000). **[PINNED as an effect.]**

**What is NOT pinned, and this is decisive for us — three independent lines cut against the strong
version:**

1. **The meta-analysis does not find it.** Watson, Cardillo, Ianni & Chatterjee (2013, *JOCN*
   25:1191) ran an activation-likelihood-estimation meta-analysis over action-concept studies and
   **did not observe significant concordance in motor or premotor cortex in any analysis**;
   significant concordance instead emerged in or adjacent to **visual motion areas** and left
   lateral temporo-occipital cortex. **[PINNED.]** (Read via the authors' hosted PDF listing and
   search summary; abstract-level, not a full-text audit.)
2. **Lesion double dissociations.** In left-hemisphere-damaged patients, the ability to *imitate
   pantomimes* and the ability to *comprehend the corresponding action verbs* doubly dissociate;
   likewise tool USE versus tool-word comprehension (Papeo, Negri, Zadini & Rumiati; PubMed
   21718215). Apraxic patients with a genuine production deficit still identify actions from
   pantomime within the normal range. **Action-word comprehension survives loss of the ability to
   perform the action.** **[PINNED.]**
3. **Verb-selective cortex is indifferent to how much motion or motor content a verb has.** Peelen,
   Romagno & Caramazza (2012, *JOCN* 24:2096) localised verb-selective left lateral temporal
   cortex, then showed its responses are **not modulated by the amount of visual motion or motor
   activity associated with the verb — it responds equally selectively to *to jump* and *to
   think*.** **[PINNED.]** Independently, typical neural representations of action verbs develop
   **without vision** in congenitally blind adults (*Cereb Cortex* 22:286), so the code is not a
   stored percept either.

**THE CONSEQUENCE FOR OUR BUILD, stated plainly: an "action/motor/effector" channel is the WRONG
build.** It is the channel we already have (five Lancaster effector dimensions: `Foot_leg`,
`Hand_arm`, `Head`, `Mouth`, `Torso`) and it is the one the verb literature most clearly says is
not carrying verb meaning. This is a case where the convenient tool and the brain point in
different directions, and the brain says do not widen the motor spokes.

**Cognitive-theory label vs neural system:** "embodied simulation" is a *theory label*. The neural
systems are precentral/premotor cortex (real, and modulated) and the question is whether they are
*constitutive* or *downstream*. The evidence above says downstream/contextual. A well-argued
middle position exists (Kemmerer, *Psychon Bull Rev* 2014: motor features ARE in precentral
cortices, but inside a flexible multilevel architecture) — I report the dispute rather than
adjudicating it, and note only that on either reading it does not license a motor channel for us.

## B2. POSTERIOR MIDDLE TEMPORAL GYRUS — the actual verb hub, and what it computes

This is the structure to name when asked "which brain structure represents verb meaning".

**Convergent PINNED facts:**

- **Grammatical class is decodable there, after confounds are partialled out.** A 2024 *Cerebral
  Cortex* study (bhae242) used **partial RSA** and reported that the activation pattern in **left
  pMTG** correlated with the grammatical-class dissimilarity matrix **after eliminating
  imageability, visual-pixel and semantic-similarity confounds**, and did not overlap the
  frontal-parietal task-difficulty regions. **[PINNED]** — and note the method: they had to
  *partial out* imageability and semantics to see it. We must copy that control (see D and F).
- **It scales with ARGUMENT VALENCY.** Left pMTG extending into angular gyrus scales with the
  number of arguments a verb takes: three-argument (*put*) > two (*chase*) > one (*sleep*)
  (Thompson et al., PMC2632636; the two-stage picture there is left inferior temporal/fusiform
  tracking argument-count at the isolated-verb level, left IFG engaging once syntactic integration
  is required). **[PINNED]**
- **It is driven by PREDICATION, not by action.** Bedny and colleagues, *Predication Drives Verb
  Cortical Signatures* (*JOCN* 26:1829; PubMed 24564433): activity in left pMTG and inferior
  frontal gyrus correlates with **transitivity** — a verb's tendency to select a direct object —
  i.e. with the verb's function of *binding arguments into a proposition*. **[PINNED]** This is the
  single most decision-relevant result in the drill: the hub's tuning variable is *how many things
  this word needs in order to mean anything*, which is a property of a FUNCTION, not of a point.
- **It appreciates whether an event has an endpoint.** Left pMTG shows significantly higher
  activation for **telic** verbs (*reach*, which entails a final state) than **atelic** verbs
  (*chase*, which does not) — "the first evidence that the human brain appreciates whether events
  lead to an end or a change of state" (*Brain Lang*, PubMed 22819309). Reported alongside:
  telicity modulates left pMTG and bilateral precuneus; iterativity engages IPS; dynamicity engages
  MTG/STS. **[PINNED]** (Abstract-level read.)
- **It carries an anterior-posterior TRANSFORMATION gradient.** Leshinskaya & Thompson-Schill
  (2020, *Cereb Cortex* 30:3148, full text read this pass): after participants learned predictive
  structure among visual events, MVPA showed **perceptual coding peaking posteriorly and
  associative/predictive coding peaking reliably anterior to it (t=-3.51, p=0.001), with abstract
  relational-category coding emerging anteriorly in tandem with associative coding** (relational
  vs associative r=0.74; relational vs perceptual r=-0.54). **[PINNED for learned visual events;
  UNPINNED as a claim about verb lexical semantics specifically — the authors' stimuli were learned
  event contingencies, not words.]**

**What pMTG computes, in one line:** it converts perceptual event features into **learned
predictive relations and relational categories**, and its response is graded by **how many
arguments the word demands and whether the event it names culminates**. That is a
change-and-structure computation, not a similarity-space lookup.

## B3. LEFT MID-SUPERIOR TEMPORAL CORTEX — the slot organ

Frankland & Greene: left mid-superior temporal cortex (lmSTC) **flexibly encodes "who did what to
whom"**. *The truck hit the ball* patterns with its passive paraphrase (same relation) and against
*the ball hit the truck* (same words, different relation). **Adjacent but distinct subregions
separately carry the identity of the AGENT and of the PATIENT** — i.e. the brain holds the current
*values* of abstract semantic variables "who did it" and "to whom was it done". **[PINNED]**

**This is the structure that makes the slot claim a neural claim rather than a linguistic one.**
Role-filler binding is implemented as *spatially distinct subregions holding role-specific
content*, which is much closer to our `EventBundleCodec` (`hdlab/event_bundle.py`, role-keyed bind
then bundle) than to any per-word vector. Thematic-role ASSIGNMENT additionally recruits posterior
parietal cortex — TMS to posterior intraparietal sulcus changes agent-decision accuracy on passive
sentences (PMC10158617), noted in our own `notes/drill_target_space_dimensionality_semantic_
representation_verbs_2026-08-16.md`.

**Caveat that must travel with this:** a role-slot organ is a *composition-time* structure. It
holds the arguments of the sentence currently being read. It is not, by itself, the *lexical entry*
for a verb — nothing in Frankland & Greene says the stored meaning of *pour* is a slot frame; it
says the meaning of *the boy poured the milk* is.

## B4. EVENT STRUCTURE AND ASPECT — meaning as a change over time

**What the account says:** a verb's meaning is decomposed into an event template — Vendler's
state/activity/accomplishment/achievement; Dowty's CAUSE / BECOME / DO operators; a scalar change
with a scale, a boundedness and a direction (Beavers); a result root versus a manner root
(Rappaport Hovav & Levin). *Break* = CAUSE(x, BECOME(broken(y))): a before-state, a transition, an
after-state.

**Status, and this is where drills usually overreach: Vendler/Dowty/Levin/Beavers are COGNITIVE-
THEORY LABELS, not neural systems. [PINNED-AS-PROPOSAL only.]** The linguistic decomposition is
excellent and we already use it (`notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md`
tabulates it, and `data/verbnet_affectedness_lexicon_v1_corrected/lexicon.json` is on disk).
The *neural* claims that survive on their own feet are narrower and I list only those:

- **Telicity (does the event culminate?) modulates left pMTG.** [PINNED]
- **A separate five-way fMRI decomposition of verb semantics into ACTION, MOTION, CONTACT, CHANGE
  OF STATE and TOOL USE has a distinct anatomical distribution per component** (*Brain Lang*,
  S0093934X07002611). [PINNED-AS-PROPOSAL — component set is the authors' choice; the anatomical
  separability is the measured part. Abstract-level read.]
- **Alternating-transitivity verbs** (*break*/*open*: one surface form, several thematic frames)
  recruit bilateral angular/supramarginal gyri and posterior STG/MTG more than simple intransitives
  (PMC4485426, via our own 2026-08-05 drill). [PINNED]

**The honest reading:** the brain demonstrably registers *whether an event ends* and *how many
frames a verb can enter*. It has not been shown to store a verb as an explicit before-state /
after-state PAIR of representations. Treating "verb = trajectory between two states" as pinned
biology would be exactly the overreach this drill is supposed to avoid. It is a live, testable
hypothesis — **OURS-INVENTION-UNDER-TEST** — and the build spec below gives it its own arm so it
can lose.

## B5. HOW ROBUST IS THE NOUN/VERB DISSOCIATION, ACTUALLY?

**Weaker than its reputation, and the weakness is specific.**

- **Group-level noun/verb production dissociations disappear when imageability and lexical
  frequency are matched or covaried** (Vigliocco et al. 2011 and the literature it summarises;
  Bird, Howard & Franklin argued many reported dissociations are driven by an imageability effect —
  in picture naming, nouns are systematically more imageable than verbs). **[PINNED]**
- **Vigliocco's own account is SEMANTIC, not grammatical:** the semantic makeup of concrete nouns
  and verbs differs, so a semantic impairment for objects or actions is easily *mistaken* for a
  grammatical-class deficit when materials confound the two. **[PINNED]**
- **A residue survives:** a minority of individual patients remain differentially impaired on verbs
  with imageability controlled. **[PINNED]** So the dissociation is real but rare and small at the
  group level.
- **The imaging version of the same correction:** the 2024 pMTG RSA result survives *only* after
  partialling imageability and semantic similarity — which is the same correction applied
  proactively.

**What this does to our position.** It does **not** say "don't build a verb channel". It says the
noun/verb split is **SEMANTIC (events vs objects have different experiential content), not
GRAMMATICAL (a category tag)**. That is precisely the shape of the fix proposed below — add the
*content* verbs need, do not add a *category flag*. And it hands us a mandatory control: **our
measurement partials out neither imageability nor concreteness, and our space contains a
concreteness dimension.** That is a live, unaddressed confound in the licensing measurement itself
and the build spec treats it as a required arm, not an optional one.

---

# (b-2) THE DECISIVE STRUCTURAL QUESTION: POINT, FUNCTION, OR TRAJECTORY?

**The question, restated so it can be answered:** is a verb's meaning representable as a POINT in
the same static similarity space as a noun, or is it intrinsically a FUNCTION (maps arguments to an
outcome) or a TRAJECTORY (before-state to after-state)? If it is a function, then landing verbs in
a static similarity space is a category error that no number of extra dimensions repairs.

## The answer: TWO THINGS, IN TWO STRUCTURES. The lexical entry is point-like; the argument structure is a separate typed-slot organ. Confidence MODERATE-HIGH on the first half, MODERATE on the second, LOW on the trajectory reading.

### Half one — the LEXICAL entry IS point-like, and this is the strongest new evidence in the drill

**Tong et al. (2025), *A Common Representational Code for Event and Object Concepts in the Brain*,
J Neurosci 45(41):e2166242025 (full text read via PMC12393606 this pass).** 320 nouns: 160 object
nouns and **160 EVENT nouns** — critically, *"all items were nouns"*, deliberately excluding the
verb/noun contrast to isolate conceptual content from grammatical class. MVPA showed both
categories represented **in overlapping fashion throughout association cortex, even in the areas
most selective for one or the other**. And the decisive result:

> a feature-based model trained on neural responses to individual **event** concepts successfully
> decoded **object** concepts from their activation patterns (and vice versa) — the two categories
> **share a common representational code**, effectively modelled by **experiential feature
> ratings** [Binder's 65-dimensional space], and the anatomical dissociations between events and
> objects **emerge from quantitative differences in the cortical distribution of more fundamental
> features of experience**.

Cross-category encoding was significant in both the event-favouring and object-favouring networks
(all FDR-corrected p<0.001, except objects-to-events in the object-favouring network, p=0.003).

**Reading, and its limit.** Event concepts and object concepts sit in ONE experiential space and a
decoder crosses between them. So a shared landing space is **not** a category error, and the
event/object difference is **quantitative — which axes are loaded — not a difference of format**.
That is a direct, 2025, brain-based answer to the structural question, and it lands on the POINT
side. **[PINNED for event NOUNS.] [UNPINNED for VERBS]** — the authors explicitly declined the
verb/noun contrast because of *"unknown effects that grammatical class may have on the results"*,
and note their shared-code finding may not extend to argument-structure representation in verbs.
**I must not, and do not, present this as settled for verbs.** It is the strongest available
evidence and it is one grammatical category short of the question.

Converging support that the lexical entry is not a re-enacted trajectory: verb-selective LTC
responds equally to *to jump* and *to think* (B1.3); action-verb representations develop normally
without vision; action-word comprehension survives loss of the ability to act.

### Half two — the ARGUMENT STRUCTURE is a separate representation, and it is NOT more dimensions

Three PINNED facts, none of which a longer vector can express:

1. **lmSTC holds AGENT and PATIENT in adjacent, distinct subregions as the current values of
   abstract variables** (B3). Slots with contents, not magnitudes.
2. **pMTG activity is graded by TRANSITIVITY / argument valency** (B2) — the hub's tuning variable
   is *how many arguments this word demands*, which is the arity of a function.
3. **Alternating-transitivity verbs recruit extra cortex** (B4) — one word, several frames, and the
   brain pays for the ambiguity.

"Takes an agent and a patient and causes a change of state in the patient" is a **typed structure,
not a magnitude.** No scalar on any dimension expresses it — the same conclusion our own 2026-08-16
drill reached, restated here with the lmSTC slot evidence added.

### Half three — the TRAJECTORY reading is the weakest of the three, and I am not going to inflate it

The owner's introspection ("a picture I think of first"), the telicity result, and the
Vendler/Dowty/Beavers decomposition all point the same way, and it is intuitively compelling. But
the *neural* evidence is that pMTG **registers whether an event culminates** — a scalar
telic/atelic contrast — not that a verb is stored as an ordered PAIR of state representations.
Leshinskaya & Thompson-Schill's gradient is the closest thing to a measured transformation and its
stimuli were **learned visual event contingencies, not words**. **Verb-as-trajectory is
OURS-INVENTION-UNDER-TEST. [UNPINNED.]** It gets an arm below (`S2_SLOT_DELTA`) precisely so it can
be refuted cheaply rather than assumed.

### What this settles for us, operationally

| claim | verdict | confidence |
|---|---|---|
| Landing verbs in the same experiential space as nouns is a CATEGORY ERROR | **NO** — refuted by cross-decoding between event and object concepts in one 65-dim experiential space | MODERATE-HIGH (one grammatical category short) |
| The current 12-dim space is ADEQUATE for verbs | **NO** — it is the object-salient half of that space (see (c)) | HIGH |
| Argument structure can be added as EXTRA DIMENSIONS of the word vector | **NO** — slots are held as distinct subregions with variable contents; arity is a tuning variable, not a coordinate | MODERATE-HIGH |
| A verb is stored as a before/after STATE PAIR | **UNPROVEN** — telicity is a scalar contrast, not a stored pair | LOW; test it, do not assume it |

**Therefore the architecture is TWO ORGANS, not one wider vector:** an experiential POINT with the
event axes added (cheap, testable this week), plus a TYPED-SLOT organ that already partly exists
(`hdlab/thematic_role_labeler.py`, **228 `VERB_FRAMES` entries confirmed by import this pass**;
`hdlab/event_bundle.py`; `hdlab/frame_induction.py`). **Trying to make the vector do the slot's job
is the category error — not the shared space itself.**

---

# (b-3) BINDER'S EXPERIENTIAL BLOCKS — WHICH ONES CARRY VERB MEANING

Binder, Conant, Humphries et al. (2016, *Cogn Neuropsychol* 33:130; PMID 27310469) propose **65
experiential attributes in 14 domains**, grouped as seven blocks: sensory, motor, spatial,
temporal, **affective**, **social**, **cognitive**. Ratings 0-6, 1,743 crowdworkers.

**PINNED:** the blocks are **dissociable** — separate substrates, separately lesionable. Sensory
and motor spokes converge on an ATL hub; affect has amygdala / OFC / vmPFC; social semantics has
its own network (superior ATL, TPJ/angular gyrus, dmPFC, posterior cingulate/precuneus), and the
literature states sensory-motor and social information are supported by **two separate semantic
subsystems**. Independently confirmed for socialness by Diveica, Pexman & Binney (2022, *Behav Res
Methods*; ratings for 8,388 words) whose own analysis reports socialness *"captures an aspect of
word meaning distinct to those measured by other key semantic variables"*.

**OUR INVENTION UNDER TEST:** that a handful of per-word scalars faithfully operationalises a
block. A block is a *neural subsystem*; a rating column is a *human introspective proxy* for it.
The proxy's own authors say so (Wingfield & Connell, PMC10615916: the norms *"rely on participant
introspection rather than direct neural recordings"*, and would *"not generally capture all forms
of semantic similarity, such as those based on thematic relationships between concepts"*). Every
per-word-scalar operationalisation below is OURS and can fail.

## Which blocks carry VERB meaning — now measured, not asserted

Tong et al. ranked feature importance and reported **13 event-salient** and **13 object-salient**
Binder features (their Table 1, read via PMC this pass):

| | features |
|---|---|
| **EVENT-salient (13)** | Cognition, Harm, Communication, Social, Complexity, Benefit, Sound, Speech, Fearful, Consequential, Large, Vision, Unpleasant |
| **OBJECT-salient (13)** | Biomotion, Path, Motion, Fast, Taste, Smell, Head, Human, Body, Upper Limb, Away, Manipulation, Color |

**Our 12 dimensions, verbatim from `hdlab/grounded_similarity.py` (`SENSORIMOTOR_COLS` + `Conc.M`,
read off disk this pass):** Auditory, Gustatory, Haptic, Interoceptive, Olfactory, Visual,
Foot_leg, Hand_arm, Head, Mouth, Torso, Concreteness.

**THE CROSSWALK — and I flag it immediately as OURS.** No published crosswalk between the Lancaster
and Binder instruments exists that I found. The alignment below is **my judgment call between two
different rating instruments**, and it is itself testable (the build's `A2_EVENT_ONLY` arm tests it
directly).

| Binder feature | our column | covered? |
|---|---|---|
| **Event-salient** | | |
| Sound | Auditory.mean | yes (approx) |
| Vision | Visual.mean | yes |
| Speech | Mouth.mean | **arguable at best** — Mouth is an *effector* rating, not a "does it involve speech" rating |
| Cognition, Harm, Communication, Social, Complexity, Benefit, Fearful, Consequential, Large, Unpleasant | -- | **absent (10 of 13)** |
| **Object-salient** | | |
| Taste | Gustatory.mean | yes |
| Smell | Olfactory.mean | yes |
| Head | Head.mean | yes |
| Upper Limb | Hand_arm.mean | yes |
| Manipulation | Haptic.mean / Hand_arm.mean | yes (approx) |
| Body | Torso.mean | yes (approx) |
| Color | Visual.mean | partial |
| Biomotion, Path, Motion, Fast, Human, Away | -- | absent |

**THE COUNT: roughly 6 (arguably 7) of 13 object-salient features, and 2 (arguably 3) of 13
event-salient features.** A ~3x coverage asymmetry, in the direction that exactly predicts the
measured result: **nouns CI-separated at n=666, verbs NOT_SEPARATED at n=222.**

**This is the drill's headline and it changes the framing of the negative.** The verb shortfall is
not "verbs are hard" and not "12 dimensions is too few". It is that **we bought the object-defining
half of a brain-derived feature set and are asking it to order events.** Note also that the missing
event-salient features are *not motor* — they are cognition, harm, communication, social, benefit,
consequentiality. The fix the embodied-semantics literature would suggest (more motor detail) is
the fix this ranking says is useless.

**And it matches the owner's own introspection precisely.** *Persuade* = "talking to someone and
convincing them - I picture the conversation... and also a feeling". *Communication* + *Social* +
*Speech* + affect. Every one of those is on the event-salient list. **Not one of them is in our 12.**

**One caution, held honestly:** Tong et al.'s items were event NOUNS. Whether the same 13
event-salient features rank top for VERBS is **UNPINNED** and is a genuine assumption of this
build. It is also, conveniently, the thing the experiment measures.

---

# (b-4) THE HONEST NEGATIVE CASE — steelmanned

A drill that only finds support for the thing it was sent to support is not a drill. Four
independent arguments against building a verb channel, strongest first. **One of them changes my
recommended sequencing.**

## N1 (STRONGEST — and it changes the plan). The ruler is too short, and the shortfall may be instrument noise rather than representation.

SimLex-999 gives 222 verb pairs; overall inter-annotator agreement rho = 0.67. Verb similarity is
harder for humans than the headline suggests: SimVerb-3500's authors originally reported pairwise
rho 84.0 and **the corrected figure, after an error in their agreement computation, is 61.2**. A
lower human ceiling directly caps the achievable rho. And SimLex's own paper reports the **highest**
inter-rater consistency and lowest per-pair variation on **adjective** pairs — yet our adjective arm
is the flattest of the three (-0.0074). So gold-noise does not explain the adjective result, which
weakens a pure noise story; but for verbs the combination of n=222 and lower human agreement is
severe. **At n=222 the paired-bootstrap CI half-width on the margin is ~0.19 — larger than the
entire effect we need to detect (+0.145).**

**Verdict: this argument is CORRECT and I am adopting it, but as a PRECONDITION rather than a
refutation.** A gold set is a **RULER, not a meaning source** — acquiring it does not touch the
no-external-model-at-inference invariant (the same ruling our 2026-08-16 drill reached). SimVerb-3500
is **not on disk**: `data/encoder_eval_benchmarks/` contains exactly `simlex999.txt` (44,050 B) and
`wordsim353_combined.csv` (7,433 B), enumerated by `ls -la` this pass. **Recommendation: acquire it
BEFORE the channel cell runs.** Doing the channel build first, on a 222-pair ruler, is the textbook
way to bank a real effect as a null.

## N2. Events and objects share ONE code, so a separate verb CHANNEL is over-engineering.

Tong et al.'s cross-decoding says the event/object difference is **quantitative, not categorical**.
If so, the right move is more of the *same kind* of dimension, not a different representational
format for verbs.

**Verdict: CORRECT, and the design already concedes it.** The A-family arms below are exactly "more
of the same kind of dimension, chosen by the brain's own feature-importance ranking". The S-family
(slot/delta) arms are the rival format, and this argument predicts they will LOSE. Good — that is a
pre-registered prediction that can embarrass me.

## N3. The noun/verb difference is an imageability/frequency artifact.

Group-level noun/verb dissociations vanish under imageability and frequency matching (Vigliocco et
al. 2011; Bird et al.). Our space contains a concreteness dimension and our measurement partials out
**neither** imageability nor concreteness. SimLex verbs are systematically less concrete than SimLex
nouns. So "our 12-dim space orders nouns and not verbs" may be restating "our space is largely a
concreteness detector and nouns vary more in concreteness".

**Verdict: PARTIALLY DEFUSED, NOT DEFEATED.** Defused on frequency: our own
`F_FREQUENCY_HARDENED` floor on V is 0.0341 and is CI-separated below K1 (+0.2266 [+0.0484,
+0.4059]), so frequency alone is not producing the noun/verb difference. **NOT defused on
imageability/concreteness — that control has never been run.** Mandatory arm below (`C1_PARTIAL`),
copying the exact method the 2024 pMTG RSA study needed in order to see grammatical class at all.

## N4. Sense-averaging, not a missing channel.

A per-word rating is an average over senses; verbs are markedly more polysemous than nouns. Trott &
Bergen show same-sense uses have more similar sensorimotor profiles than different-sense uses, and
that contextual ratings carry information beyond per-word norms. **The brain settles on a sense in
context; it does not store a sense-average.** [PINNED] If this is the dominant cause, **no per-word
channel of any width fixes verbs** and only context-conditioned codes do.

**Verdict: LIVE, UNRESOLVED, and given its own detector.** If `A1` fails AND `S1` fails AND even the
`K_WORDNET_ORACLE` ceiling reference fails on this stratum, sense-averaging becomes the leading
explanation and the next build is context-conditioned coding
(`hdlab/context_conditioned_sense_selection` line of work), not a wider space.

## Where the negative case does NOT reach

It does not touch the coverage count. Whatever else is true, our space carries ~6/13 object-salient
and ~2/13 event-salient brain-derived features, and that is a fact about a shopping list, not about
verbs.

---

# (c) PINNED vs OUR-INVENTION-UNDER-TEST — every design choice below

Per the standing rule: invent freely; presenting an invention as pinned is barred.

| # | design choice | status | basis / what makes it ours |
|---|---|---|---|
| 1 | pMTG is the verb/action-knowledge hub | **PINNED** | grammatical-class RSA after partialling confounds (*Cereb Cortex* bhae242); valency gradient (PMC2632636); transitivity/predication (*JOCN* 26:1829); telicity (PubMed 22819309) |
| 2 | Verb meaning is NOT constituted by motor simulation | **PINNED** | ALE meta-analysis finds no motor/premotor concordance (Watson 2013); pantomime/verb double dissociations (PubMed 21718215); verb-selective LTC equal for *jump* and *think* (*JOCN* 24:2096); normal development without vision (*Cereb Cortex* 22:286) |
| 3 | Agent and patient are held as distinct role-slots with variable contents | **PINNED** | lmSTC adjacent subregions coding "who did it" / "to whom" (Frankland & Greene) |
| 4 | Binder's blocks are dissociable neural subsystems | **PINNED** | separate substrates per block; social semantic network distinct from sensorimotor; socialness statistically distinct from other norms (Diveica 2022) |
| 5 | Event and object CONCEPTS share one experiential code | **PINNED for event NOUNS; UNPINNED for VERBS** | Tong et al. 2025 cross-decoding; authors explicitly excluded the verb/noun contrast |
| 6 | The 13 event-salient / 13 object-salient feature ranking | **PINNED as measured on event vs object NOUNS** | Tong et al. Table 1 |
| 7 | **That the same 13 event-salient features rank top for VERBS** | **OURS — a load-bearing assumption of this build** | untested; the experiment measures it |
| 8 | **The Lancaster-to-Binder crosswalk giving ~6/13 vs ~2/13 coverage** | **OURS** | no published crosswalk found; my alignment judgment between two instruments; `A2_EVENT_ONLY` tests it |
| 9 | **Socialness / VAD / consequentiality as a 5-scalar operationalisation of the event-salient block** | **OURS — invention under test** | the BLOCK is pinned; that 5 per-word scalars faithfully carry it is not |
| 10 | **Consequentiality derived from ATOMIC v4 if-then edge counts** | **OURS** | ATOMIC is a crowd-authored commonsense resource, not a brain measurement; used as a *feature source*, never as a meaning source or a verdict |
| 11 | **A verb characterised by the mean grounded code of its argument-slot fillers (`S1`)** | **OURS — invention under test** | motivated by pinned valency/predication tuning, but the specific estimator is ours |
| 12 | **A verb as a before/after DELTA vector (`S2`)** | **OURS — invention under test; the weakest-supported of all** | telicity is a scalar contrast, not a stored state-pair; included so it can lose |
| 13 | Partialling imageability/concreteness is required before reading any verb result | **PINNED as a method requirement** | grammatical-class RSA only survives after partial-RSA; noun/verb dissociations vanish under imageability matching |
| 14 | A gold set is a RULER, not a meaning source | **OUR STANDING RULING** (reaffirmed) | consistent with the no-external-model-at-inference invariant |
| 15 | Hand-rated norms are a human introspective proxy for a neural block | **PINNED as a limitation** | stated by the norm authors themselves (Wingfield & Connell, PMC10615916) |

---

# (d) BUILD SPECIFICATION — ready for an `hdi_exp_dev` agent to author

**Working anchor: `exp_verb_event_salient_channel_v1`. SPECIFICATION ONLY. No cell authored, no
pre-registration file written, nothing smoked, nothing dispatched by this drill.**

## D0. ONE SENTENCE

Hold the verb stratum, the scorer, the gold, the floors, the seeds and the permutation counts
COMPLETELY FIXED, and vary ONLY **what each verb's vector is made of** — testing (i) whether adding
the brain's *event-salient* attribute channel lets the space clear the floor it failed at n=222,
(ii) whether a *slot-based* representation does better than any point, and (iii) a width-matched
control that must NOT help, or the whole story is refuted.

**THE ONE VARIABLE IS THE VERB'S CODE.** Stratum, scorer form (L2-normalise then plain cosine,
Spearman vs gold), floor construction, `N_PERM=2000`, `N_BOOT=10000` and the shared bootstrap
resample index are byte-identical across arms, imported as libraries from
`experiments/exp_verb_target_space_n222_v1.py` (not reimplemented).

## D1. WHAT THIS CELL MEASURES, AND THE CUE-REGIME DECLARATION

**This measures the INSTRUMENT, not a capability.** Every arm is a **known-answer, EXACT-KEY** arm:
each word keeps its own real code, no bridging, no held-out endpoint, no partial cue. `metrics.json`
must carry `"measures_the_instrument_not_a_capability": true` and
`"cue_regime": "exact_key_own_code"`, exactly as the licensing cell does. **No number produced here
transfers to the partial-cue regime**, which is the real one. Saying so in the metrics file, not
only in prose, is the requirement.

## D2. PRECONDITION — ACQUIRE THE RULER FIRST (this is the recommendation, not a nicety)

`data/encoder_eval_benchmarks/` contains **exactly two files** (`ls -la` this pass):
`simlex999.txt` and `wordsim353_combined.csv`. **SimVerb-3500 is NOT on disk.** At n=222 the
paired-bootstrap CI half-width on the margin is ~0.19, larger than the +0.145 effect. **Acquire
SimVerb-3500** (Gerz, Vulic, Hill, Reichart & Korhonen 2016, EMNLP D16-1235 / arXiv 1608.00869;
3,500 verb pairs with human similarity ratings, CC-BY) into `data/encoder_eval_benchmarks/` with a
`PROVENANCE_simverb.md`, and run the primary on **SimVerb**, keeping SimLex-V as a 222-pair
replication stratum scored separately and **never pooled** (never cross populations).

If SimVerb is NOT acquired, the pre-registration must state **in advance** that the primary is
expected to be power-limited, and a NOT_SEPARATED result must be reported as
`POWER_INSUFFICIENT`, never as `FAIL`.

## D3. ASSETS — enumerated from disk this pass (`ls`, `du --apparent-size`, and one Python import)

**Present:**
- `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv` (11 dims)
- `data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt`
- `data/grounding_testbed/Ratings_Warriner_et_al.csv` (VAD, ~13,905 usable lemmas)
- `data/grounding_testbed/AoA_51715_words.csv`
- `data/atomic_kb/v4_atomic_trn.csv` (31,430,641 B) + `all_agg` / `dev` / `tst` — event-centred
  if-then knowledge, **on disk and unused**
- `data/thematic_relations_v1/thematic_edges_v1.pkl` (28,724,302 B)
- `data/verbnet_affectedness_lexicon_v1_corrected/lexicon.json`
- `hdlab/thematic_role_labeler.py` — **`VERB_FRAMES` has 228 entries** (confirmed by import under
  `.venv/Scripts/python.exe` this pass, not by grep)
- `experiments/selectional_preference_extractor_v1.py` (built 2026-08-16, reusable as a library)

**ABSENT — and I am stating how I enumerated, not asserting from a search:**
- `data/verbnet_cache/` and `data/framenet_cache/` both exist as directories and are **EMPTY**
  (`ls` lists no entries; `du --apparent-size` reports 0). Their names promise assets they do not
  contain. **Do not plan around them.**
- **SimVerb-3500** — absent (see D2).
- **Socialness norms** — absent. Acquire: Diveica, Pexman & Binney 2022, *Behav Res Methods*
  (`10.3758/s13428-022-01810-x`), **8,388 English words**, public (GitHub `DiveicaV/`).
- **Binder-65 norms** — absent, and correctly SHELVED as a primary space: 535 words / 62 verbs. Our
  registry already carries `binder_direct_supply_grounding` as `SHELVE /
  closed_correctly_data_bound`. **Worth acquiring only as a 65-dim ORACLE arm on its own tiny
  stratum; never as the target space.** This drill reproduces that ruling.
- **Optional, verb-specific:** English Verbs Semantic Norms Database (*Behav Res Methods* 2025,
  `10.3758/s13428-025-02675-6`) — concreteness, embodiment, imageability, valence, arousal for
  **3,512 verbs**, on OSF. Its **imageability** column is the cleanest available way to run the
  `C1_PARTIAL` control on verbs specifically. Recommended.

## D4. THE ARMS — one variable, widths matched where it matters

**POINT family (the "add the event axes" hypothesis):**

| arm | code | dims | role |
|---|---|---|---|
| `A0_INCUMBENT_12` | Lancaster11 + `Conc.M` | 12 | **INCUMBENT / instrument-licensing arm.** Re-earns its own baseline on THIS stratum. **The 0.2607 figure MAY NOT BE IMPORTED** — different stratum, different intersection. |
| `A1_EVENT_SALIENT_17` | A0 + socialness(1) + Warriner V/A/D(3) + ATOMIC-consequentiality(1) | **17** | **PRIMARY TREATMENT.** Operationalises the event-salient block: Social/Communication (socialness), Unpleasant/Fearful/Benefit/Harm (VAD), Consequential (ATOMIC). |
| `A2_EVENT_ONLY_5` | the 5 event dims alone | 5 | **DISSOCIATION.** If `A2` matches `A1`, sensorimotor contributes nothing to verbs — a different and bigger finding. Also the direct test of design choice #8. |
| `A3_WIDER_UNINFORMATIVE_17` | A0 + **5 Lancaster rater-SD columns** | **17** | **DECISIVE NEGATIVE CONTROL — NOISE.** Same source file, same width as `A1`, no new channel. **If `A3` rises as much as `A1`, "more dimensions" is the mechanism, the event-salient story is REFUTED, and the direction dies.** |
| `A4_REAL_WRONG_CHANNEL_17` | A0 + AoA, log-frequency, length, WordNet sense-count, orthographic-neighbourhood density | **17** | **SECOND NEGATIVE CONTROL — REAL BUT WRONG.** Five genuine per-word scalars with real variance and no event-salient content. Stronger than `A3` alone: `A3` only rules out noise columns, `A4` rules out "any real scalar helps". |

**STRUCTURE family (the "a verb is a function/trajectory" hypothesis — OURS, included so it can lose):**

| arm | code | dims | role |
|---|---|---|---|
| `S1_SLOT_FRAME_24` | concat(mean 12-dim code of subject-slot fillers, mean 12-dim code of object-slot fillers), from `selectional_preference_extractor_v1` on the same 64 MB simplewiki budget | 24 | **THE FUNCTION HYPOTHESIS, cheapest testable form: a verb is characterised by WHAT IT TAKES.** Motivated by the pinned valency/predication tuning of pMTG. |
| `S2_SLOT_DELTA_12` | object-slot mean **minus** subject-slot mean | 12 | **THE TRAJECTORY HYPOTHESIS, cheapest testable form.** Width-matched to `A0`, so a `S2` > `A0` result cannot be a width effect. Weakest prior of any arm. |

**CEILING REFERENCE (no verdict weight, and labelled as cheating):**

| arm | role |
|---|---|
| `K_WORDNET_ORACLE_V` | WordNet verb-hierarchy similarity on the identical pairs. A hand-built taxonomy, not our substrate. Answers "how high can ANY structured resource get on this stratum" — i.e. is the stratum readable at all. **CEILING REFERENCE. Never a pass, never a target.** |

**NULLS:**

| arm | construction |
|---|---|
| `N1_CODE_SCRAMBLE` | within-space permutation of code-to-word assignment, `N_PERM=2000`; **this doubles as `F_SCRAMBLE_PERM_P95`** |
| `N2_RANDOM_GAUSSIAN` | every word's code replaced by an i.i.d. Gaussian vector of that arm's dimensionality, **5 seeds, MAX draw never the mean**. Catches the artifact `N1` cannot: that a wider space has a different similarity distribution. **Required because five arms differ in width.** |

## D5. THE FOUR FLOORS — recomputed per arm where the arm can change them

The bar is a **CI-separated paired-bootstrap margin over `max(all four floors)` on the identical
scorer / n / pool / gold**, never a bare number. Every floor is recomputed on **this** population;
**no floor value is imported** — not 0.1152, not 0.0680, not any figure from the licensing cell.

1. `F_ORTHOGRAPHIC` — character-trigram cosine between the two spellings. **SPACE-INDEPENDENT: ONE
   number shared by every arm.** Compute once; do not report seven bootstrap-noise variants as
   seven floors.
2. `F_FREQUENCY_HARDENED` — **max over all four channels** (`FREQ_NEG_ABS_DIFF`, `FREQ_SUM`,
   `FREQ_MIN`, `FREQ_MIN_OVER_MAX`) on the same 64 MB simplewiki budget. **Space-independent.** All
   four required.
3. `F_CONSTANT_PROTOTYPE` — **SPACE-DEPENDENT.** One endpoint replaced by that arm's own stratum
   mean, scored under both column orderings, **stronger (harder-to-beat) ordering reported**. The
   both-endpoints-constant variant is mathematically degenerate (cosine identically 1.0, Spearman
   undefined) and must be reported as `null` with that reason, never silently omitted — exactly as
   the licensing cell did.
4. `F_SCRAMBLE_PERM_P95` — **SPACE-DEPENDENT, RECOMPUTED PER ARM**, `N_PERM>=2000`, take the HIGHER
   of row-permutation p95 and gold-permutation p95. A 17-dim space has a different scramble
   distribution than a 12-dim one; reusing the 12-dim floor would hand the wide arms a free pass.

**Report the per-floor decomposition as well as the max** — the highest point-estimate floor is not
always the hardest to separate from.

**Report beside every margin: the CI half-width, and the null p95 at that n** (standing rule: a
width is not an effect). Report tie conventions both ways.

## D6. THE MANDATORY CONFOUND CONTROL — `C1_PARTIAL` (an analysis, applied to every arm)

Copy the method the pMTG grammatical-class result required. For every arm, additionally report a
**partial Spearman** of the arm's cosine against gold, **partialling out the pair's mean
concreteness and mean log-frequency** (and mean imageability if the 3,512-verb norms are acquired).

**This is not optional and it is not a robustness check — it is the difference between "our space
carries verb meaning" and "our space is a concreteness detector".** If `A0`'s verb rho does not
survive partialling, the licensing negative was an imageability artifact and the whole framing
changes. Pre-register both the raw and the partialled quantity; report both whatever they say.

## D7. THE DESIGN GATE — measure BEFORE the full run

Measure the **intersection stratum n**: pairs where BOTH endpoints are defined in **every** arm's
space (Lancaster ∩ Brysbaert ∩ Warriner ∩ socialness ∩ ATOMIC-coverage ∩ slot-filler coverage).
**ZERO-FILL IS BARRED** — it is a documented artifact in `hdlab/grounded_similarity.py` and the
warning stands. Intersection is the honest route and the smaller core is a cost, not a
disqualification.

- Spearman CI half-width ~ 1.96/sqrt(n-3): **0.176 at n=125, 0.124 at n=250, 0.099 at n=392, 0.033
  at n=3,500.**
- **GATE: if intersection n < 150, the primary is UNDERPOWERED BY CONSTRUCTION.** Report it as such
  and STOP. Do not run it and bank the null. The binding constraint is likely socialness (8,388
  words) ∩ Warriner (13,905).

## D8. STOP-IFS — pre-registered, in order

1. **STRATUM SHIFT.** If `A0` on the intersection stratum falls below its own `F_SCRAMBLE_PERM_P95`
   point estimate, the stratum change broke the instrument. Report `STRATUM_SHIFT`; report no other
   arm; do not compare anything to the n=222 measurement.
2. **POWER.** Intersection n < 150 → `POWER_INSUFFICIENT`, stop (D7).
3. **CONTROL FIRES.** If `A3` (noise widening) or `A4` (real-but-wrong channel) raises the margin as
   much as `A1` does, paired and CI-overlapping with `A1`'s gain → the event-salient story is
   **REFUTED**. Report it, stop, and do not rescue it with a different operationalisation in the
   same cell.
4. **DISSOCIATION.** If `A1` clears but `A2` (event dims alone, 5 dims) clears equally → the
   sensorimotor block contributes nothing to verbs. Report as a **separate, larger finding**; do not
   fold it into "the channel worked".
5. **INSTRUMENT LIMIT.** If **every** arm including `K_WORDNET_ORACLE_V` fails to CI-separate from
   its scramble floor, the stratum itself is at its resolution limit. The next move is **acquiring a
   longer ruler, not another channel.** (A cheating oracle that cannot clear is the cleanest
   possible proof that the problem is not the representation.)
6. **CONFOUND.** If `A0`'s verb rho does not survive `C1_PARTIAL`, report the licensing negative as
   **confounded by concreteness/imageability** and re-open it before building anything downstream.

## D9. PRE-REGISTERED PROBABILITIES

Standing lit-scan calibration penalty applied (deflate 0.15-0.25); novel synthesis capped at 0.50.

| claim | P |
|---|---|
| `A0` reproduces a point estimate within its own CI of 0.2607 on the intersection stratum | 0.75 |
| intersection n >= 150 without SimVerb | 0.55 |
| **`A1` CI-separates from `max(floors)` where `A0` did not** | **0.30** |
| `A1` beats `A0` on the PAIRED difference, CI-separated | 0.35 |
| `A3` and `A4` (both controls) show no gain — the controls behave | 0.65 |
| `A0`'s verb rho survives `C1_PARTIAL` (not a concreteness artifact) | 0.55 |
| `S1_SLOT_FRAME` beats `A0`, CI-separated | 0.25 |
| `S2_SLOT_DELTA` beats `A0`, CI-separated | 0.15 |
| `K_WORDNET_ORACLE_V` clears its floors on this stratum (the stratum is readable at all) | 0.60 |

**Basis for the low primary.** Two independent prior bridging routes are measured nulls, the
adjective arm is flat where the affect gain was predicted to be *largest*, and the nearest prior art
halved between smoke and full. 0.30 is what the priors support; it is not pessimism, and a
CI-honest 0.30 that fails is still worth running because `A3`/`A4`/`C1_PARTIAL` make the failure
*diagnostic* rather than merely disappointing.

## D10. WHAT THIS DESIGN DELIBERATELY DOES NOT DO

- **No zero-fill** of missing norms. Barred; intersection only.
- **No import of 0.2607, 0.1152, or any floor** across strata.
- **No pooling of SimVerb and SimLex-V**, and no comparison of the V margin to the N margin.
- **No use of `grounded_similarity()` as the scorer** — it saturates 76.2% of SimLex pairs onto two
  values. Raw vector, L2-normalise, plain cosine.
- **No pretrained co-occurrence table in any scored arm.** WordNet appears only as a labelled
  ceiling reference with no verdict weight.
- **No motor/effector widening.** The literature in B1 says that is the wrong channel, and this is
  the drill's clearest case of the brain contradicting the convenient tool.
- **No slot organ built here.** `S1`/`S2` are cheap *proxies* that ask whether slot information
  helps at all; they are not the typed-slot organ. Building that organ is the next, harder step and
  it needs its own drill.
- **No wiring decision.** WIRE-or-SHELVE is a separate act at land time.
- **No reliance on `tools/verdict_bar_check.py`** — it returned `NO_EVIDENCE` /
  `has_known_answer_arm: false` on the licensing cell's `pos_strata` schema, and it has false-passed
  four times. Read the arm-by-arm margins off `metrics.json` directly.

---

# (e) THE SHELVE CRITERION — BRAIN-FRAMED, NEVER PERFORMANCE-FRAMED

**What would have to be true about the BIOLOGY for us to abandon a verb channel.** No score appears
below, deliberately. A number can pause this work; only a fact about the brain can end it.

**SHELVE if any one of these becomes true:**

1. **The event-salient attributes turn out NOT to be a separable block from the sensorimotor ones.**
   The build rests on Binder's blocks being dissociable neural subsystems — separate substrates for
   affect (amygdala/OFC/vmPFC) and social semantics (superior ATL, TPJ, dmPFC, precuneus), distinct
   from the sensorimotor spokes. If that separability collapses — if affect/social/cognitive
   attributes prove to be *readouts* of the sensorimotor spokes rather than an independent block —
   then adding them is adding a linear transform of what we already have, and the direction is dead
   on brain grounds regardless of any number.
2. **A brain-based feature-importance ranking run on VERBS fails to reproduce the event-salient /
   object-salient asymmetry Tong et al. found for event vs object NOUNS.** Our whole premise is that
   verbs lean on the blocks we lack. That premise is currently supported by a *nouns-only* study
   (design choice #7, explicitly OURS). If the verb version of that analysis comes back showing
   verbs load on the same features nouns do, the premise is false and the channel is unmotivated.
3. **The verb hub is shown to compute something a per-word attribute vector cannot be a component
   of at all** — i.e. if pMTG's verb code turns out to be *purely* a predication/arity signal with
   no experiential-attribute component decodable from it. Then the lexical entry is not point-like
   even in part, Tong et al.'s common-code result does not extend to verbs, and the whole effort
   belongs in the slot organ instead of the vector.

**REVIVAL criterion, also brain-framed:** if a lesion, decoding or stimulation study establishes an
experiential-attribute component of the verb code that is dissociable from the argument-structure
component, this direction re-opens immediately, whatever the last measured number was.

**Explicitly NOT shelve criteria:** "rho did not rise", "the margin did not separate", "the
adjective arm stayed flat", "it did not beat the trigram floor". Those are reasons to diagnose,
re-power, or fix the instrument. **A miss is never a ceiling until BOTH gates pass — a fair test
and an exactly-like-the-brain implementation — and even then the brain's way is the fix.**

**A note on what this criterion protects against.** The comment in `hdlab/grounded_similarity.py`
that excluded affect for years ("affect is not an identity-content signal") was a *cognitive-theory
label*, not a brain structure, and it closed a live direction that later measured +0.12 on verbs and
+0.34 on adjectives at the ceiling level. That is the exact failure mode this section exists to
prevent recurring.

---

# (f) WHAT I COULD NOT VERIFY, AND HOW I ENUMERATED

**How I enumerated, so the absence claims are enumerations and not searches:**
- `ls hdlab/ | grep -iE "verb|action|event|selection|thematic|argument|role|frame|motor|sensorimotor"`
  and `ls experiments/` / `ls notes/` filtered the same way — full directory listings, filtered
  locally, not a content search.
- `ls -la data/encoder_eval_benchmarks/`, `ls data/grounding_testbed/`, `ls data/atomic_kb/`,
  `ls data/verbnet_cache/`, `ls data/framenet_cache/`, `du -sh --apparent-size` on the last two.
- `VERB_FRAMES` counted by **importing** `hdlab.thematic_role_labeler` under
  `.venv/Scripts/python.exe` (228 entries) — runtime evidence, not grep, per the standing rule.
- Prior-work dedup was done by **reading the three prior drills off disk**
  (`notes/drill_target_space_dimensionality_semantic_representation_verbs_2026-08-16.md`,
  `notes/drill_brain_event_predicate_recognition.md`,
  `notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md`) rather than by KB query.
  **`director_kb_query.py` was NOT used: its ingest is livelocked and its results are STALE by
  standing instruction.** My dedup coverage is therefore `hdlab/` + `data/` + those three notes +
  the two licensing artifacts, and **NOT** a full sweep of `experiments/` (5,800+ files) or
  `preregs/`. Stated because an absence claim requires an enumeration and mine is partial.

**Not verified this pass:**
- **Full text of Watson et al. 2013, the Vigliocco 2011 noun/verb review, Bird et al., the telicity
  paper, and the five-component verb fMRI paper.** ScienceDirect returned HTTP 403; these rest on
  abstracts and search summaries. **Pointers to check before any becomes individually
  load-bearing.** The two claims I lean on hardest — Tong et al.'s Table 1 and Leshinskaya &
  Thompson-Schill's gradient statistics — WERE read from full text (PMC and Oxford Academic).
- **Whether SimVerb-3500's licence permits redistribution into this repo** — believed CC-BY, not
  confirmed against the distribution page.
- **The actual intersection stratum n.** Not measured — it needs the norm joins. **It is the design
  gate (D7) and must be measured before dispatch.**
- **Whether ATOMIC v4 covers the SimLex/SimVerb verb vocabulary well enough to yield a
  consequentiality scalar.** File is on disk (31 MB train split); not parsed this pass. If coverage
  is poor, drop that column and run `A1` at 16 dims with `A3`/`A4` re-matched to 16.
- **Whether the socialness and VAD columns are near-collinear on verbs.** If they are, `A1` is a
  4-dim addition wearing a 5-dim label. Cheap to check at build time; should be reported.
- **Binder-65 SimLex/SimVerb overlap** — unmeasurable, the file is not on disk.

---

# (g) SOURCES

Brain systems and computation:
- [Representation of the noun-verb distinction in left pMTG (partial RSA), *Cereb Cortex* 34:bhae242](https://academic.oup.com/cercor/article/34/7/bhae242/7689877)
- [Peelen, Romagno & Caramazza 2012, Independent Representations of Verbs and Actions in Left Lateral Temporal Cortex, *JOCN* 24:2096](https://direct.mit.edu/jocn/article/24/10/2096/5303/Independent-Representations-of-Verbs-and-Actions)
- [Predication Drives Verb Cortical Signatures, *JOCN* 26:1829](https://direct.mit.edu/jocn/article/26/8/1829/28179/Predication-Drives-Verb-Cortical-Signatures)
- [Where the brain appreciates the final state of an event: the neural correlates of telicity](https://pubmed.ncbi.nlm.nih.gov/22819309/)
- [Leshinskaya & Thompson-Schill 2020, Transformation of Event Representations along Middle Temporal Gyrus, *Cereb Cortex* 30:3148](https://academic.oup.com/cercor/article/30/5/3148/5704026)
- [The representation of the verb's argument structure as disclosed by fMRI (PMC2632636)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2632636/)
- [Watson, Cardillo, Ianni & Chatterjee 2013, Action Concepts in the Brain: an ALE Meta-analysis, *JOCN* 25:1191](https://direct.mit.edu/jocn/article-abstract/25/8/1191/27974/Action-Concepts-in-the-Brain-An-Activation)
- [Papeo et al., Action performance and action-word understanding: double dissociations in left-damaged patients](https://pubmed.ncbi.nlm.nih.gov/21718215/)
- [Typical Neural Representations of Action Verbs Develop without Vision, *Cereb Cortex* 22:286](https://academic.oup.com/cercor/article/22/2/286/334757)
- [Kemmerer 2015, Are the motor features of verb meanings represented in the precentral motor cortices?](https://link.springer.com/article/10.3758/s13423-014-0784-1)
- [Neuroanatomical distribution of five semantic components of verbs (*Brain Lang*)](https://www.sciencedirect.com/science/article/abs/pii/S0093934X07002611)

The structural question and the feature blocks:
- [Tong et al. 2025, A Common Representational Code for Event and Object Concepts in the Brain, *J Neurosci* 45(41):e2166242025 (PMC12393606)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12393606/)
- [Binder, Conant, Humphries et al. 2016, Toward a brain-based componential semantic representation](https://pubmed.ncbi.nlm.nih.gov/27310469/)
- [Diveica, Pexman & Binney 2022, Quantifying social semantics: socialness ratings for 8,388 English words](https://link.springer.com/article/10.3758/s13428-022-01810-x)
- [Vinson & Vigliocco 2008, Semantic feature production norms for a large set of objects and events](https://link.springer.com/article/10.3758/BRM.40.1.183)
- [English verbs semantic norms database: ratings for 3,512 verbs, *Behav Res Methods* 2025](https://link.springer.com/article/10.3758/s13428-025-02675-6)

The negative case:
- [Noun-verb dissociation in aphasia: the role of imageability and functional locus of the lesion](https://www.sciencedirect.com/science/article/abs/pii/S0028393205001673)
- [Nouns, verbs, objects, actions, and abstractions: local fMRI activity indexes semantics, not lexical categories](https://www.sciencedirect.com/science/article/pii/S0093934X1400039X)
- [SimLex-999: Evaluating Semantic Models With (Genuine) Similarity Estimation](https://direct.mit.edu/coli/article/41/4/665/1517/SimLex-999-Evaluating-Semantic-Models-With-Genuine)
- [SimVerb-3500: A Large-Scale Evaluation Set of Verb Similarity](https://aclanthology.org/anthology-files/pdf/D/D16/D16-1235.pdf)
- [CARD-660 (reports the corrected SimVerb-3500 inter-annotator agreement of 61.2)](https://pilehvar.github.io/card-660/Card-660.pdf)
- [Wingfield & Connell, on the limits of sensorimotor norms as a similarity measure (PMC10615916)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10615916/)

**Prior work in this repo that this drill BUILDS ON and CREDITS** — the affect-block finding, the
target-space asset enumeration, the four-floor discipline and the `TS4` negative-control idea are
all inherited from `notes/drill_target_space_dimensionality_semantic_representation_verbs_
2026-08-16.md`; the frame-not-POS event-trigger finding from `notes/drill_brain_event_predicate_
recognition.md`; the verb-class feature basis from `notes/drill_brain_openvocab_verb_class_
membership_2026-08-06.md`; and the whole licensing measurement from
`notes/item2_verb_target_space_n222_measurement_2026-08-17.md`. This drill's new contributions are
the event-salient/object-salient coverage count, the point-vs-transformation adjudication, and the
build specification.
