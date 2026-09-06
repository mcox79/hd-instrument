# Research — brain-foundational mechanism for GROUND/GOAL role assignment in motion events (2026-09-05)

**Trigger:** solver diagnosis on the spatial situation-model reader — three upstream thematic-role-extractor
faults feeding the location register: (1) goal mislabeled as belonging to a spurious "theme" on intransitive
self-motion ("she headed into the locker room" — she IS the mover, no separate theme); (2) goal resolves to
the wrong token on a nested PP ("a ward on the fourth floor" -> "floor" not "ward"); (3) eager firing on every
locative PP, no relevance gate distinguishing a location-updating PP from an incidental one.

**Grounded in the actual failing code** (read before dispatching lit-scans, so recommendations map to real
call sites): `hdlab/predicate_argument_frontend.py` — `route_predicate_arguments()` is a Competition-Model-style
multi-cue router (CUE1 prep-telicity default / CUE2 verb-class / CUE3 animacy / CUE5 destination-verb,
precedence documented in its own docstring, lines 536-538) that already resembles Bates & MacWhinney's cue
competition. `_goal_belongs_to()` (355-363) is the Figure/Ground (agent-vs-theme) decision. `_pp_args_for_verb()`
+ `_attaches_to_verb()` (300-352) resolve which PP objects attach to the verb. Fault 3 is directly visible in
`_route_one_pp()` (500-503): `# CUE1 default stands: roles["goal"] = obj` fires **unconditionally** for any
to/into/onto PP when no other cue disambiguates — no relevance/argument-hood gate exists at all.

**Method:** 4 parallel Sonnet lit-scan sub-agents dispatched (thematic-role neural substrate; Figure-Ground
self-motion vs caused-motion; PP-attachment relevance-gating; glass-box selectional/attachment mechanisms).
**2 returned full findings** (thematic-role substrate; Figure-Ground). **2 failed with a connection error
mid-response** (PP-attachment/relevance-gating; glass-box selectional mechanisms) — per coordinator
instruction, NOT re-dispatched this cycle. Sections resting on the failed threads' turf are explicitly marked
**UNVERIFIED THIS CYCLE** (resting on the author's pre-existing general knowledge, not independently
re-checked by a fresh scan) and carry a hard confidence cap of 0.35.

---

## (a) HEADLINE

A verb-frame-first, construction-fallback model IS brain-foundational and should be copied: the verb's lexical
argument-structure frame (a VerbNet/FrameNet-style static asset, already present in this codebase as
`get_event_classes`/`is_destination_verb`) pre-activates a typed Goal/Destination slot at the verb (Altmann &
Kamide 1999-style anticipation, PINNED 0.75); when the verb itself carries no such slot (coercion cases), the
argument-structure CONSTRUCTION supplies/overrides it (Goldberg's Override Principle, evidenced online by
Johnson & Goldberg 2013's Jabberwocky-priming result, PINNED 0.65). Figure-vs-Ground for self-motion is a
near-deterministic function of clause VALENCY gated by a small closed verb-class exception list (Rappaport
Hovav & Levin manner/result complementarity, read at primary-source level, PINNED 0.8; Choi et al. 2019's
canonical mapping formula, PINNED 0.85). The relevance-gating question (which PP updates location) is only
PARTIALLY covered by verified lit this cycle (Boland 2005 / Lee & Thompson 2011 argument-vs-adjunct asymmetry,
PINNED 0.55) — the deeper PP-attachment-ambiguity mechanism (nested-PP head resolution) rests on pre-existing
knowledge (Hindle & Rooth 1993; Frazier) that was **not re-verified this cycle** (its dedicated lit-scan
thread failed) and is flagged UNVERIFIED, capped at 0.35.

**P_deflated for the composite claim = 0.45** (below the usual 0.50 novel-synthesis cap, penalized further for
the two failed threads leaving Q3/Q4b partially unverified).

---

## (b) Cheap decisive test

Build a ~120-token stratified gold set from the same modern-narrative corpus already used for the 44%
motion-recall diagnostic, in 4 buckets mapping 1:1 onto the fixes in (e):

1. **Intransitive self-motion, no object NP** ("she headed into the locker room", "he slipped into bed") —
   tests the valency gate (fix 1). Score whether `theme_idx` stays `None`/agent-identical post-fix.
2. **Nested-PP destination** ("wheeled her to a ward on the fourth floor", "found a desk on the third floor
   in the annex") — tests attachment-first head resolution (fix 2). Score whether the outer NP head (ward,
   desk) is bound as Ground, with the nested PP recorded as a sub-location refinement, not a competing Ground.
3. **Motion-verb + argument Goal PP vs adjunct PP in the same clause** ("walked into the kitchen quickly", "ran
   to the door with a lantern") — tests that the argument PP (into the kitchen / to the door) wins over the
   superficially similar adjunct (with a lantern) even when both are technically locative-typed nouns.
4. **Non-motion verb + incidental locative PP** ("she frowned at the letter on the table", "he laughed in the
   hallway") — tests the relevance gate (fix 3): the PP should NOT fire an eager location update for a
   non-MOTION/PUT-classed verb.

Score current detector per bucket first (diagnostic), then each fix incrementally, holding the SOLVED build's
existing bucket-1/bucket-2 (manner-motion, result-verb) recall/precision as a must-not-regress guardrail.

---

## (c) Falsifiable predictions

**HARD-PASS:** the valency gate (fix 1) alone resolves **>=90%** of bucket-1 self-motion theme-mislabels
(n>=40) with **zero** regression on transitive caused-motion theme routing (bucket already covered by the
SOLVED build); the attachment-first fix (fix 2) resolves **>=80%** of bucket-2 nested-PP cases (n>=30) without
new false Ground bindings on non-destination nested PPs; the verb-frame goal-slot gate (fix 3) cuts
false-positive location updates on bucket-4 (incidental PPs) by **>=70%** while bucket-3 argument-PP recall
stays **>=85%** (CI-separated over the current unconditional-CUE1-default baseline).

**MIDDLE_BAND:** fixes 1-2 land cleanly (both are near-deterministic, well-evidenced structural checks) but
fix 3 only partially separates argument-PP from adjunct-PP (50-70% false-positive reduction) because the
verb-frame classification (MOTION/PUT) itself has coverage gaps on less-common verbs, OR because some
"incidental" PPs in bucket 4 are structurally indistinguishable from arguments without deeper selectional
typing than a static VerbNet lookup provides. Correct read: fix 3 is real and worth keeping, but needs the
selectional-restriction typing (Resnik-style / VerbNet +location field) strengthened as a SEPARATE follow-up,
not evidence the mechanism is wrong.

**HARD-FAIL:** fix 1 fails to resolve >70% of bucket-1 cases (would mean the theme-binder's false-positive
source is NOT clause valency but something else — e.g. a parser head-attachment bug unrelated to argument
structure, report before touching fixes 2-3); OR fix 2 introduces new false Ground bindings on >15% of
non-destination nested PPs (would mean naive "trust the outer NP head" is too blunt and the parser's own
dependency arcs need auditing first, not a new heuristic layered on top); OR fix 3's false-positive reduction
is **<30%** (would mean the verb-frame MOTION/PUT classification itself is too sparse/unreliable to gate on,
and the relevance question needs a genuinely different signal — flag for a dedicated PP-attachment/selectional
follow-up drill, since that is exactly the turf the two failed lit-scan threads were meant to cover).

---

## (d) Cross-thread synthesis

### Q1 — Is a verb-frame / construction-grammar / selectional model of GROUND-role assignment brain-foundational?

**YES**, with real but incomplete/extrapolated neural correlates. **One-line mechanism to copy:**
*a verb-specific argument-structure frame pre-activates its typed argument slots (including a Goal/Destination
slot when the verb is motion/path-classed); when the verb's own lexical entailments don't supply one, the
syntactic argument-structure construction overrides/supplies it; the filled slot is checked against a static
selectional-restriction TYPE (place-noun) rather than lexically pre-activated the way Agent/Patient fillers
are.*

Supporting pieces, each independently sourced (thread 1):
- **Hagoort's MUC model** (Hagoort 2013, *Front. Psychol.* 4:416): LIFG = domain-general "unification" —
  binds retrieved lexical/argument-structure material into larger structure. PINNED that the model and this
  function exist (0.6); SPECULATIVE that this is *specifically* the Ground-binding step vs. a fully
  general-purpose operation (the model is stated too generally to isolate).
- **pMTG/posterior temporal cortex** tracks verb argument-structure complexity (activation scales with number
  of obligatory arguments) — PINNED (0.5), converging fMRI/aphasia evidence, is the retrieval-of-the-frame
  substrate.
- **Left posterior parietal cortex/IPS** is causally required for thematic-role *reanalysis* — TMS evidence
  (Finocchiaro et al. 2015 *Neuropsychologia* 77:223; Finocchiaro et al. 2021 *Neurobiol. Lang.* 2(3):416,
  the latter read directly). PINNED for Agent/Patient reanalysis in passives (0.55-0.75); **NOT tested for
  Ground/Goal specifically — extrapolating this to spatial-role binding is a real gap, flagged, not invented.**
- **Landau & Jackendoff 1993** (*Behav. Brain Sci.* 16:217) "What and Where" — PINNED that this
  what/where-system proposal exists (0.55); SPECULATIVE that it maps onto live sentence-level Ground-binding
  (it is a theoretical synthesis of *prior*, non-sentence-processing neuropsychological dissociations, not
  itself a processing study).
- **Kemmerer/Tranel/Damasio locative-preposition lesion+PET work** (Tranel & Kemmerer 2004; Damasio et al.
  2001 PET) localizes categorical spatial-relation-term processing to **left supramarginal
  gyrus/inferior parietal lobe** — the same general neighborhood as the thematic-reanalysis TMS site above,
  but from a *never-directly-compared* paradigm. Confidence 0.5-0.55.
- **Ferretti, McRae & Hatherell (2001, *J. Mem. Lang.* 44:516)**: verbs prime typical Agents/Patients/
  Instruments but **NOT typical Locations** ("swam" does not prime "ocean"). PINNED (0.55) — this is the
  single most decision-relevant finding: **Ground-role filling is NOT lexical-associative pre-activation like
  Agent/Patient/Instrument filling is.** It is closer to a *typed slot* the verb's frame opens (motion verbs
  open a Goal slot) that gets filled by whatever PP passes a selectional TYPE check, not by the verb dragging
  a stereotyped filler into working memory the way "arrest" drags "cop"/"criminal."
- **Construction Grammar coercion** (Goldberg 1995 Override Principle; **Johnson & Goldberg 2013**,
  *Lang. Cogn. Process.* 28:1439 — nonce-verb "Jabberwocky" ditransitive/caused-motion sentences prime
  semantically related real verbs even though the nonce verb has zero stored meaning) — PINNED (0.65), the
  single strongest online-processing evidence that construction-level argument structure is a real,
  automatically-accessed unit, not a linguist's redescription. Directly explains "sneezed the napkin off the
  table"-type coercions the verb-frame-alone account cannot.
- **No dedicated Ground-selectional-restriction ERP/eye-tracking study** (the Agent-animacy analog — Kim &
  Osterhout 2005's semantic-P600 paradigm — has never been run for a Ground/place-type violation, per an
  explicit, bounded search). This is a genuine literature gap, not a settled negative; flagged, confidence 0.3
  on the absence claim itself.

### Q2 — Self-motion Figure/Ground: what tells the brain the subject is Figure, PP-object is Ground, no theme?

**Clause VALENCY (argument count) gated by verb-class**, read at primary-source confidence:
- **Rappaport Hovav & Levin** (2008 ms., in *Lexical Semantics, Syntax, and Event Structure*, Oxford; primary
  text read, p.8-9): manner-of-motion verbs (walk, run, slip, head, amble) are **ACT/manner predicates with a
  single core argument** — the mover. A following path PP is a compositional **adjunct**, not a second
  argument slot; there is no theme slot for it to introduce. Directed-motion/path verbs (arrive, enter, exit)
  are **scalar-change (result) predicates** that obligatorily entail a theme changing location relative to a
  Ground, surfacing as subject (unaccusative, "she arrived") or object (if causativized). PINNED (0.8).
- **Choi et al. (2019, *Language and Cognition*)**, canonical mapping (primary text read, 47 speakers, 96
  videos, N=4,512 descriptions, mixed-effects models) confirms: intransitive self-motion clause -> Subject =
  Figure, Oblique = Ground; caused-motion clause -> Object/Theme = Figure, Oblique = Ground. PINNED (0.85).

**So YES — it is the verb's intransitive argument frame (valency=1, manner/ACT class) + the resulting
construction that tells the parser "the sole argument is Figure; don't look for/create a theme."** This is a
near-deterministic, cheaply computable default. It has three well-characterized, closed-class exceptions
(PINNED 0.6-0.8, thread 2): (i) **path-object verbs** (climb, enter, cross, swim, traverse) — transitive
despite self-motion, where the OBJECT is Ground not Figure (Rappaport Hovav & Levin p.16-17 discuss this
directly, citing Fillmore 1982/Jackendoff 1985/Kiparsky 1997 — requires a verb-sense/class lookup, not
valency alone); (ii) **passive voice** detransitivizes a caused-motion clause without changing who the Figure
is (check voice before applying the valency default); (iii) unergative/unaccusative indeterminacy — does not
actually threaten the self-motion default (subject is Figure regardless), more a nuance for other analyses.

### Q3 — Computable, glass-box relevance signal for which locative PP updates location

**Verified this cycle (thread 1):**
- **Boland (2005)** + **Lee & Thompson (2011)**: a true ARGUMENT PP (subcategorized by the verb's frame, e.g.
  a VerbNet Destination slot) is read faster / preferred over a superficially similar ADJUNCT PP (e.g. Goal
  "to the baby" vs. Beneficiary "for the baby" — shorter gaze duration for the argument reading). PINNED
  (0.55). This gives a real, implementable ARGUMENT-vs-ADJUNCT precedence rule.
- **Altmann & Kamide (1999, *Cognition* 73:247)**: the verb pre-activates an expectation for its argument
  TYPE before the argument is encountered. PINNED (0.75) for the general mechanism (tested for Theme, not
  Goal specifically, but the mechanism class generalizes directly to a motion verb pre-activating a
  "expects a locative Goal" flag).
- **McKoon & Ratcliff (1992)** minimalist/bridging hypothesis, carried over from the prior vetted note
  (`research_spatial_recall_beyond_motion_verbs_2026-09-05.md`, P=0.50 there): only trivially-available,
  locally-needed inferences are automatic; a locative-PP-bearing non-motion clause should be resolved
  **lazily, on-demand**, not eagerly.

**Minimal implementable rule (combining the above):**
1. Look up the verb's frame (already an asset: `get_event_classes`/`is_destination_verb`). If MOTION/PUT/
   path-object-classed -> the verb genuinely predicts a Goal slot.
2. Among candidate PPs, the one filling that slot AND passing a static place-type check (`is_place_ground`,
   already an asset) is the Goal that updates location; a competing PP that reads as manner/instrument/time
   is an adjunct and loses by the Boland/Lee-Thompson argument-precedence rule.
3. If the verb has NO Goal-predicting frame, do not let any locative PP eagerly fire a location update by
   default — fall through to (i) the already-recommended stative-locative gate (sit/stand/wait+PP) or (ii)
   lazy on-demand bridging when a downstream consumer actually needs the entity's location.

**UNVERIFIED THIS CYCLE (its dedicated lit-scan thread failed — flagged, not invented, capped at 0.35):** the
deeper mechanism for resolving WHICH nested PP is the true attachment site (fault 2, "ward on the fourth
floor") rests on pre-existing, not-re-checked-this-session knowledge of classic PP-attachment literature
(Hindle & Rooth 1993 lexical-association statistics; Frazier's Minimal Attachment/Late Closure). The general
shape of that literature (from memory, not verified this cycle): PP-attachment ambiguity between a preceding
VERB and a preceding NOUN is resolved by a mix of structural preference (attaching to the more recent/closer
NP, "low attachment") and lexical-specific co-occurrence statistics (verb-noun-preposition association
strength), NOT purely by a fixed structural rule. **This should be treated as a hypothesis needing its own
follow-up drill, not a pinned finding** — recommend re-dispatching the failed PP-attachment/relevance-gating
and glass-box-selectional threads next cycle rather than trusting this paragraph at face value.

### Figure-Ground failure modes not yet asked about, worth flagging

Thread 2 also surfaced (PINNED 0.55, not directly requested but load-bearing for fault 1's implementation):
Talmy's Figure-Ground framework itself (Talmy 1978/1985/2000, definitions read directly via Choi et al. 2019's
reprint) is a genuine dual semantic+syntactic claim, well-corroborated by production data, but **has no
independent adult online-comprehension (RT/ERP) validation found** — treat "Talmy's framework is
processing-validated" as unsupported; it is the right *computational-level* (Marr sense) description, not a
directly measured *processing-level* one. This does not weaken the recommendation (Rappaport Hovav & Levin's
independently-verified argument-realization account gives the processing-relevant mechanism instead), but it
means citing "Talmy" alone as brain-processing evidence would overclaim.

---

## (e) Substrate-product implications — ranked implementable recommendations

**1. [Highest confidence, cheapest, fixes fault (a)] VALENCY GATE before the theme-binder fires.**
For a verb classed self-motion/manner-of-motion (VerbNet run-51.3.2/escape-51.1-style classes; NOT PUT, NOT
caused-motion) with no independent direct-object NP in the clause (only PP complements), set `theme_idx = None`
by construction — do not invoke `hybrid_role_patient`/`structural_patient_pick`'s general heuristic at all for
this verb class/valency combination. This makes `_goal_belongs_to()` (predicate_argument_frontend.py:355-363)
correctly fall through to `"agent"` by construction rather than depending on the heuristic's guess
coincidentally matching the PP object. Mirrors the existing "check verb class first, only fall back to the
general heuristic when the class doesn't resolve it" precedent already used for quotative inversion
(lines 570-579 in the same file). Brain-basis: Rappaport Hovav & Levin (PINNED 0.8) + Choi et al. 2019
(PINNED 0.85) — the highest-confidence recommendation in this note.

**2. [High confidence, fixes fault (c)] VERB-FRAME GOAL-SLOT GATE on the CUE1 default.**
`_route_one_pp()`'s `base == "GOAL"` branch (predicate_argument_frontend.py:486-503) currently lets
"CUE1 default stands" fire unconditionally when no other cue disambiguates. Gate this: only let a bare
to/into/onto PP default to GOAL when the verb IS classed MOTION/PUT/path-object (i.e., its frame genuinely
predicts a Goal slot, Altmann & Kamide-style, PINNED 0.75); for an unclassified verb, route the PP to a
lower-confidence bucket instead of an unconditional GOAL assignment, deferring to the stative-locative gate or
lazy bridging (already-adopted design from the prior note) rather than guessing.

**3. [Medium confidence, fixes fault (b), flagged partially unverified] ATTACHMENT-FIRST HEAD RESOLUTION for
nested PPs.** Audit `_pp_args_for_verb()`/`_attaches_to_verb()` (lines 300-352): if a PP's own governor (per
the dependency parse) is a NOUN rather than the verb/copula, it should be excluded from the verb-level
`pp_args` list entirely — it is a noun-modifier ("on the fourth floor" modifying "ward"), and its content
should attach as a refinement of the outer NP's resolved Ground entity, not compete as a second candidate
Ground. This is a structural-attachment fix (trust/tighten the existing dependency arcs), not a new semantic
heuristic. Flagged medium-confidence because the specific literature basis (Hindle & Rooth 1993 lexical
association, Frazier attachment principles) was the target of a lit-scan thread that failed this cycle and
was not re-verified — recommend confirming this with a follow-up drill before treating it as pinned.

**4. [Medium confidence, secondary precedence rule for fault (c)] ARGUMENT-OVER-ADJUNCT PRECEDENCE.** When a
motion-classed verb has multiple candidate PPs, prefer the one reading as a subcategorized argument (Goal
slot) over one reading as manner/instrument/time, per Boland (2005)/Lee & Thompson (2011), PINNED 0.55 this
cycle.

**5. [Confirmation only, already adopted] Keep lazy/on-demand bridging** for locative-PP-bearing non-motion
clauses (prior note, P=0.50) — do not build an eager omniscient scan; this note's findings do not overturn
that design.

**6. [Flagged, not recommended to build yet] A dedicated Resnik-style selectional-association table or a
VerbNet-restriction-completeness audit** would strengthen recommendation 2's type-check step, but this rests
on the glass-box-selectional lit-scan thread that failed this cycle — recommend re-dispatching that thread
specifically (Resnik 1996 selectional association; VerbNet restriction-hierarchy completeness; SpaceEval/
ISO-Space non-neural spatial-role-labeling feature sets) before investing build effort here.

---

## (f) Citations (verified count = 19, from the 2 threads that returned; primary-source-read items marked *)

Thread 1 (thematic-role substrate): Hagoort 2013 (*Front. Psychol.* 4:416); Finocchiaro, Capasso, Cattaneo,
Zuanazzi & Miceli 2015 (*Neuropsychologia* 77:223-232); Finocchiaro, Cattaneo, Lega & Miceli 2021*
(*Neurobiol. Lang.* 2(3):416-432); Landau & Jackendoff 1993 (*Behav. Brain Sci.* 16(2):217-265); Damasio et
al. 2001 (PET, spatial-relation naming); Tranel & Kemmerer 2004 (lesion study, locative prepositions); Altmann
& Kamide 1999 (*Cognition* 73:247-264); Boland 2005 (*Cognitive Mechanisms & Syntactic Theory*); Lee &
Thompson 2011 (eye-tracking, Goal vs Beneficiary); Snedeker & Trueswell 2003 (visual-world, verb-bias PP
attachment); Bencini & Goldberg 2000 (*J. Mem. Lang.*, sentence-sorting); Johnson & Goldberg 2013
(*Lang. Cogn. Process.* 28:1439-1452); Kaschak & Glenberg 2000 (*J. Mem. Lang.* 43:508-529); Kutas & Hillyard
(foundational N400); Kim & Osterhout 2005 (semantic-P600, animacy); Ferretti, McRae & Hatherell 2001
(*J. Mem. Lang.* 44:516-547).

Thread 2 (Figure-Ground): Talmy 1978/1985/2000* (Figure-Ground definitions, read via Choi et al. 2019
reprint); Rappaport Hovav & Levin 2008* (ms., in *Lexical Semantics, Syntax, and Event Structure*, Oxford —
primary text read, p.1, p.8-9, p.16-17); Levin & Rappaport Hovav 1992/1995 (*Unaccusativity*, MIT Press);
Choi, Goller, Hong, Ansorge & Yun 2019* (*Language and Cognition*, primary text read); Goldberg 1995
(*Constructions*, Univ. Chicago Press); Muehleisen & Imai 1997 (Japanese path-verb transitivity).

**Flagged as unverified / do not cite:** "Allen et al. 2012" fMRI constructional-processing study (thread 1
could not confirm this citation exists as described — likely search-engine confabulation).

**Not covered this cycle (threads failed, flag for follow-up):** Hindle & Rooth 1993; Frazier Minimal
Attachment/Late Closure; MacDonald/Seidenberg constraint-based lexicalist PP-attachment; Resnik 1996
selectional association; McRae/Ferretti thematic-fit norms as a static-resource proxy; VerbNet selectional-
restriction-hierarchy completeness; SpaceEval/ISO-Space non-neural spatial-role-labeling feature sets; Zacks
Event Segmentation Theory as a computable relevance-gating trigger.

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):** raw synthesis estimate for the composite
claim ~0.65 (buoyed by two primary-source-read papers, Rappaport Hovav & Levin 2008 and Choi et al. 2019, at
0.8-0.85); deflated by 0.20 for two failed lit-scan threads leaving Q3's attachment mechanism and Q4's
selectional-typing recommendation partially unverified -> **P_deflated = 0.45**. The narrower sub-claims for
Q1 (verb-frame-first/construction-fallback) and Q2 (valency-gated Figure/Ground) individually run higher
(0.65-0.85, primary-source-backed); the nested-PP-attachment sub-claim (recommendation 3) is capped at 0.35
pending a follow-up drill.

---

## TLDR

The brain figures out WHERE someone ends up by using the verb's own "shape": a verb like "walk" or "head"
normally has just one main participant (the person moving), so any following "into the room" naturally
describes where that same person ends up — there's no second person or thing to confuse it with. A verb like
"wheeled" has two participants (the pusher and the person being pushed), so the destination belongs to whoever
is being moved, not the pusher. This one-argument-vs-two-argument distinction, plus a short list of
well-known exceptions (climb/enter/cross behave oddly), should fix the "she headed into the locker room"
mislabeling cheaply and with strong evidence behind it. Separately, the brain seems to expect a destination
right after certain verbs (much like it expects something edible right after "eat") — that expectation is
what should decide WHICH place-phrase counts as the real destination when more than one appears in a sentence,
rather than grabbing the first or last one. The harder sub-problem — figuring out that "on the fourth floor"
describes the ward, not the destination itself, when both phrases are chained together — is a well-known,
long-studied kind of ambiguity in language, but this particular research pass could not get fresh confirmation
of the exact fix (that search failed partway through and was not re-run), so that specific recommendation
should be treated as a reasonable but not yet double-checked guess.

## QUESTIONS

None.

## NEXT STEPS

1. Ship recommendation 1 (valency gate) first — cheapest, most directly evidenced, and additive per the
   existing quotative-inversion precedent in the same file.
2. Ship recommendation 2 (verb-frame goal-slot gate on the CUE1 default) next — directly targets the diagnosed
   eager-firing fault, evidenced this cycle.
3. Re-dispatch the two failed lit-scan threads (PP-attachment/relevance-gating; glass-box selectional
   mechanisms) before building recommendation 3 (nested-PP attachment fix) or investing in recommendation 6
   (a selectional-association table) — that turf is currently unverified, not refuted.
4. Run the 4-bucket cheap decisive test (section b) once fixes 1-2 are built, before touching fix 3.
