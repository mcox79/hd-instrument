# BRAIN-DRILL (5x): ARGUMENT vs ADJUNCT DISTINCTION — why "came HOME" gets mis-licensed as PATIENT, and a glass-box structural classifier

**Date:** 2026-07-19. **Filed by:** research (3 parallel Sonnet lit-scans + director synthesis). **Trigger:**
direct USER 5-angle brain-drill on a VET-confirmed residual: the LCCP mis-licenses bare locative/adverbial
fillers ("came HOME", "stood THERE", "walked home") as the PATIENT, when they are ADJUNCTS (or a genuinely
intermediate category, see Angle 1) — not arguments of the verb at all. Confirmed: lexical SEMANTICS (verb-
filler selectional coherence) is orthogonal to subcategorization here ("came home" is semantically perfectly
coherent), so a semantic/coherence gate structurally cannot catch this; the fix must be syntactic/structural.

Sits alongside the same-day sibling drills: `research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md`
(LCCP's Steps 1-6, cue-competition scoring over an already-generated candidate set) and
`research_np_head_candidate_generation_grounding_gate_5x_brain_drill_2026-07-19.md` (GHC, two hard gates —
structural-position + grounded-entity-hood — that prune WRONG-TOKEN candidates like `fields`/`table`/`regular`).
**This drill is a third, non-redundant layer:** GHC fixes "wrong NP-head chosen"; LCCP fixes "wrong candidate
scored highest"; THIS drill fixes "a non-argument constituent was offered as a PATIENT candidate at all" — a
functional/role-eligibility question, upstream of both. `home`/`there` are typically not even wrong-position
NPs (GHC's failure mode) — they are the *right* structural slot (immediately postverbal) but the *wrong
syntactic category/function* (locative adverbial, not direct-object NP) for PATIENT-role candidacy.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement;
novel-synthesis capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**The argument/adjunct distinction is real, structurally learnable, and NOT strictly binary — and the
literature has an exact, pre-existing category for the "came home" puzzle case.** Three independent lit-scans
converge: (1) the classic diagnostic tests (obligatoriness, iterability, do-so-substitution, verb-specificity/
co-occurrence-restriction) are individually unreliable and mutually INCONSISTENT (Przepiórkowski 2006;
Toivonen 2021) — the field's own honest position is that argumenthood is a GRADIENT, not a binary (Kim,
Rawlins, Van Durme & Smolensky 2019, arXiv:1809.07889 — an ELMo+BiLSTM classifier trained against VerbNet
achieves 95.5% binary / r=0.624 continuous argumenthood-score accuracy, i.e. this is empirically
LEARNABLE from distributional features, but the field treats it as graded); (2) directed-motion verbs
(arrive, come, go, return) are specifically analyzed by VerbNet as licensing a class-specific **Destination**
argument role, and PropBank hedges with BOTH a generic adjunct tag (AM-DIR) and a numbered core argument
(ARG4 "ending point") depending on the verb's own frame — meaning "home" in "came home" sits in a real,
independently-documented INTERMEDIATE zone, formalized by Needham & Toivonen (2011, LFG11) as a third
category, **"derived arguments"** — neither classic argument nor classic adjunct; (3) the operative
LEARNABLE signal the computational literature actually uses is **verb-frame co-occurrence breadth**
(PropBank's own ARG-N-vs-AM-* design principle: numbered core roles are defined PER VERB FRAME, narrow;
AM-* adjunct roles are defined GLOBALLY, identical across all predicates, i.e. wide) — directly evidenced
computationally (Korhonen 2000/2002 SCF acquisition; Villavicencio 2002 ACL/CoNLL; Kim et al. 2019) and
CONSISTENT WITH (though not directly confirmed by) developmental evidence that children track BOTH
verb-specific AND verb-general (cross-lexicon) frame-frequency distributions simultaneously (Wonnacott,
Newport & Tanenhaus 2008, *Cognitive Psychology*).

**Ranked brain/field mechanism (name it): GRADIENT VERB-FRAME-SPECIFICITY GATING with a DERIVED-ARGUMENT
middle category** — a distributional verb-diversity/entropy signal (narrow-verb-set co-occurrence = argument-
leaning, wide-verb-set = adjunct-leaning, PropBank's own design logic) combined with a verb-class-conditioned
stored frame-TYPE check (does this verb's construction license a slot of this SEMANTIC TYPE — e.g. GOAL/PATH
— distinct from PATIENT/THEME; Friederici & Frisch 2000 show frame-TYPE violations and frame-NUMBER
violations produce dissociable ERP signatures, P600-only vs N400+P600, i.e. the brain checks TYPE-match as a
distinct operation from obligatoriness/count), with an explicit THIRD, DEFERRED "derived argument" state for
genuinely intermediate goal/path cases rather than a forced binary. Deflated P=0.42 (novel-synthesis capped)
that this exact three-part architecture (distributional entropy + frame-type gate + derived-argument middle
state) is the correct buildable target; individual literature components sit higher (P~0.50-0.65 per angle).

---

## Angle 1 — The argument/adjunct distinction itself (linguistic tests, and the "came home" case specifically)

**Mechanism:** the classic diagnostic battery — obligatoriness/omissibility, iterability (adjuncts stack:
"arrived home yesterday at noon in a hurry"; arguments don't), verb-specificity/co-occurrence restriction
(arguments licensed by a specific verb class, adjuncts attach to almost any verb), do-so/VP-anaphora
substitution, latency (recoverable anaphorically), grammatical-relations behavior (passivization) — is
textbook-standard (Forker 2014, *Linguistic Discovery*, gives a 5-criterion canonical typology applied to
Hinuq spatial cases, explicitly framing the distinction as a CONTINUUM). **Honest complication, independently
confirmed by two sources:** Przepiórkowski ("Against the Argument-Adjunct Distinction in Functional Generative
Description"; "How not to distinguish arguments from adjuncts in LFG") argues several tests (iterability,
do-so) don't actually track argumenthood, they reduce to an independent locative/temporal-vs-other split.
Toivonen (2021, LFG21 proceedings, "Arguments and adjuncts across levels") shows the tests frequently give
MUTUALLY INCONSISTENT verdicts because argumenthood can differ across syntactic vs. semantic levels of
representation. **The field's own position, not an engineering excuse, is that no single test is necessary or
sufficient and the distinction is gradient.**

**The "came home" case specifically:** genuinely contested, not resolved by fiat. "Home" is uncontroversially
a locative/directional adverb (historically a fossilized case-marked noun, an "adverbial objective"), not a
direct object — but on the argument/adjunct axis, Levin & Rappaport Hovav (*Argument Realization*, 2005;
*Computational Linguistics* 32(3), 2006) treat DIRECTED-motion verbs (arrive, enter — vs. manner verbs walk,
run) as licensing a directional/path complement as a genuine sister-of-V, tied to scalar-change semantics —
closer to argument-like for that subclass specifically. VerbNet formally encodes **Destination** as a
class-specific thematic role for motion-verb classes (e.g. RUN-51.3.2). PropBank hedges: it has a generic
AM-DIR adjunct tag usable with ANY verb, but ALSO a numbered core role ARG4 ("ending point/destination") for
verb senses that select it — i.e. the SAME surface phrase-type can be core-argument or adjunct depending on
the specific verb's frame. **Needham & Toivonen (2011, LFG11 Proceedings, pp. 401-421)** propose exactly the
missing third category for this: **"derived arguments"** — elements added to a verb's basic frame that are
neither classic arguments nor classic adjuncts. This is the closest existing formal handle on the "came home"
puzzle, and it means forcing a strict binary here is fighting the field's own honest position, not just an
engineering simplification.

**Implication:** don't design toward a binary ARGUMENT/ADJUNCT flag. Design toward a GRADIENT score feeding a
THREE-way outcome (argument / adjunct / derived-argument-middle-state), matching both the linguistic-theory
literature (Toivonen, Needham & Toivonen) and the sibling coherence-gate drill's already-established
DEFERRED-state design pattern.

## Angle 2 — Acquisition: how children/learners get the verb-frame right (verb-specificity as a learnable signal)

**Mechanism:** Tomasello's Verb Island Hypothesis (1992, *First Verbs*) — children's earliest argument-
structure knowledge is item-based, per-verb; contested by Ninio ("No Verb Is an Island") and Pine/Lieven/
Rowland-lineage corpus work showing more cross-verb transfer than the strict item-based story predicts — some
abstraction happens earlier/more generally. **Wonnacott, Newport & Tanenhaus (2008, *Cognitive Psychology*
56(3):165-209)** is the most directly relevant developmental hit: an artificial-language learning study
showing learners track BOTH verb-SPECIFIC frame distributions (how often THIS verb occurs in a given frame)
AND verb-GENERAL frame distributions (frame frequency across the whole lexicon) SIMULTANEOUSLY, and both
independently shape production, judgment, and real-time processing. This is the closest developmental analog
to "track narrow-vs-wide verb-co-occurrence of a filler-type" — not identical (it's about frame-choice
statistics for verbs that already have a frame, not explicitly a filler-type's cross-verb breadth), but
directly consistent with the mechanism this design needs.

**Honest gap (flagged independently by the lit-scan):** no developmental paper was found explicitly testing
"children use cross-verb filler-distribution breadth as an argument-hood cue" as its own named phenomenon —
this specific mechanism is evidenced COMPUTATIONALLY, not developmentally. Korhonen (PhD thesis 2002; Korhonen,
Krymolowski & Briscoe LREC 2006; Korhonen et al. ACL W00-1325) builds unsupervised subcategorization-frame
lexicons for ~6,400 verbs directly from corpus co-occurrence statistics. **Villavicencio (ACL/CoNLL 2002,
W02-2033, "Learning to Distinguish PP Arguments from Adjuncts")** and **Kim, Rawlins, Van Durme & Smolensky
(AAAI 2019, arXiv:1809.07889)** and **Hwang (2012, Colorado Research in Linguistics)** treat the exact
argument/adjunct boundary as a corpus-learnable classification problem — direct computational precedent that
the target signal is learnable from a corpus, though full-text feature details for two of these papers could
not be independently verified this session (PDF-fetch failures; titles/venues/years confirmed via search).

**Overgeneralization correction (directly relevant to the "came home as object" error type):** Ambridge,
Blything & Lieven's preemption/entrenchment line (Blything, Ambridge & Lieven 2014, *PLoS ONE*
9(10):e110009; "The Retreat from Locative Overgeneralisation Errors," PMC4022747) shows BOTH statistical
preemption (a competing correct form winning suppresses the error) and entrenchment (raw verb frequency
suppresses errors) operate for LOCATIVE-construction overgeneralization specifically — the closest documented
analog to "came home" being mis-treated as a transitive-object construction — though no paper was found
naming this exact bare-locative-as-direct-object error pattern. Implication: even after a structural gate is
built, a residual preemption/entrenchment-style tracking layer (reusing the LCCP sibling drill's Step 5
mechanism one level up, at candidate-eligibility rather than candidate-scoring) is a well-precedented way to
further suppress recurring mis-licensed cases with exposure.

## Angle 3 — Online processing: does the parser actually gate on subcategorization frame, and is it structural not semantic

**Mechanism:** solid, replicated evidence for an online ARGUMENT-ATTACHMENT PREFERENCE. Boland & Blodgett
(2006, *Journal of Psycholinguistic Research*) — eye-tracking, manipulating both attachment site and argument
status — readers show LESS first-pass reading time on argument PPs than structurally-matched adjunct PPs,
i.e. the parser prefers/expects the argument reading even at first pass. **Critical finding for THIS
drill:** Pickering, Traxler & Crocker (2000, *Journal of Memory and Language*, "Ambiguity Resolution... 
Evidence against Frequency-Based Accounts") show the argument preference is NOT reducible to raw
verb-specific subcategorization FREQUENCY — readers prefer the argument analysis even when it is the
objectively LESS frequent continuation for that verb — arguing for a frequency-independent structural bias
toward the more "informative" (argument) analysis, with frame frequency only MODULATING magnitude/speed, not
gating the preference outright. Tutunjian & Boland (2008, *Language and Linguistics Compass* review)
conclude the argument/adjunct distinction is psychologically real and used online by the parser, not merely a
theoretical construct.

**ERP dissociation, directly load-bearing:** Osterhout & Holcomb (1992) — subcategorization violations elicit
P600, distinguishing them from purely semantic (N400) anomalies. **Friederici & Frisch (2000, *Journal of
Memory and Language*, German)** — a finer dissociation: violating a verb's argument-TYPE/subcategorization
frame (wrong grammatical category filling a slot) produces a P600 with NO N400; violating argument NUMBER
(missing/extra argument) produces an N400-P600 BIPHASIC pattern. **This is genuine evidence that the brain
checks frame-TYPE-match as a mechanistically distinct operation from obligatoriness/count-checking** — exactly
the two-signal (type-gate + count/obligatoriness-gate) architecture this drill's design should use, not one
combined score.

**Anatomical localization: contested, do NOT lean on it.** Aphasia/neuroimaging evidence for a clean
IFG-specific "argument-structure module" distinct from adjunct/modifier processing is internally
INCONSISTENT (Shapiro & Levine 1990 found preserved online argument-structure access in agrammatic aphasics;
Meltzer-Asscher et al. 2012, PMC3518698, found the opposite — absent N400, restricted/earlier P600, i.e.
genuinely impaired online processing); fMRI argument-density work (PMC2873169) implicates posterior
perisylvian/angular-gyrus regions as much as IFG. Flag explicitly: the MECHANISM (type-gate distinct from
count-gate) is well-evidenced; the ANATOMICAL localization claim is not, and should not be used as
architectural justification for e.g. "these must be two separately-trainable modules."

**Implication:** build TWO separable checks, not one combined score — (a) a frame-TYPE-match check (does the
candidate filler's semantic/categorial TYPE match a slot type this verb's construction licenses at all —
Friederici & Frisch's P600-only signal) and (b) an obligatoriness/count check (is this an expected NUMBER of
arguments — the N400+P600 biphasic signal) — and the preference/default itself should be modeled as a
frequency-MODULATED but not frequency-DETERMINED structural bias (Pickering et al.), consistent with Angle
1's finding that this needs to be a graded score, not a hard frequency-threshold rule.

---

## Angle 4/5 — THE DESIGN VERDICT: a glass-box ARGUMENT/ADJUNCT classifier

**Ranked mechanism, restated:** GRADIENT VERB-FRAME-SPECIFICITY GATING (distributional verb-diversity/entropy,
PropBank's own ARG-vs-AM design logic, computationally validated by Korhonen/Villavicencio/Kim et al.) +
VERB-CLASS-CONDITIONED FRAME-TYPE MEMBERSHIP (Friederici & Frisch's type-vs-count dissociation, construction-
level per the sibling LCCP drill's "weights live on the construction" finding) + an explicit DERIVED-ARGUMENT
middle state (Needham & Toivonen) reusing the sibling coherence-gate's DEFERRED-state pattern — feeding
ROLE-TYPE assignment (GOAL/PATH/LOCATION/TIME/MANNER vs PATIENT/THEME vs AGENT), not a bare binary flag.

### Concrete design: the Role-Eligibility Cascade (REC)

**Composes with, does not replace, existing components:** sits BEFORE (or alongside, as a role-restriction on)
the LCCP's cue-competition scorer (sibling 07-19 drill) and AFTER the GHC candidate-generation gates (sibling
07-19 drill) — GHC fixes wrong-TOKEN candidates (`fields`/`table`/`regular`); REC fixes wrong-ROLE-ELIGIBILITY
for tokens that already passed GHC's structural-position and grounding gates (`home`/`there` ARE grounded,
concrete, correctly-positioned locative constituents — GHC would not flag them — but they should never be
offered as PATIENT candidates). Reuses the LCCP's construction-level clustering (Step 4 of the sibling drill)
as the unit REC's frame-type table is attached to.

**Signal 0 — category/role-eligibility prior (cheap, structural, high-precision on the clear cases):** for
each candidate filler, determine its SYNTACTIC CATEGORY/FUNCTION via the same structural machinery already
built (NP-head-finder's structural CG + POS/category detection): is it a bare NP (canonical PATIENT/THEME-
eligible position) or a bare locative/temporal/manner ADVERB / a PP headed by a locative/temporal/manner
preposition (canonical GOAL/LOCATION/TIME/MANNER-eligible position, not PATIENT-eligible by default)? This
small, LEARNABLE (via distributional/unsupervised POS induction — Christodoulopoulos, Goldwater & Steedman
2010 EMNLP; Mintz 2003 frequent-frames — both already cited in the sibling GHC note) category set is the cheap
first filter: it directly targets "home"/"there" as adverbial-category tokens that should be EXCLUDED from
PATIENT-role candidacy by default, while leaving them fully eligible for GOAL/LOCATION roles.

**Signal 1 — verb-frame-specificity / co-occurrence-breadth (learned, the core distributional lever):** for
each filler-CATEGORY x SLOT-POSITION combination (e.g. "bare locative adverbial immediately postverbal"),
track the DISTRIBUTION of distinct verbs/verb-CLASSES (construction-level, per the sibling LCCP drill, not
per-verb) it co-occurs with across the corpus, and compute a verb-diversity/entropy score. HIGH entropy
(occurs productively with a wide, semantically unrelated variety of verbs/constructions — "home" occurs with
came/went/walked/drove/flew/stayed/worked-from/sent-someone) => strong ADJUNCT-leaning push, mirroring
PropBank's own AM-* design principle (adjunct roles defined identically across ALL predicates). LOW entropy
(occurs narrowly, only with a specific verb CLASS) => ARGUMENT-leaning, mirroring PropBank's ARG-N design
principle (numbered core roles defined per verb frame). This directly operationalizes the computationally-
validated Korhonen/Villavicencio/Kim-et-al signal, and is consistent with (though more explicit than) the
Wonnacott et al. dual verb-specific/verb-general distribution-tracking finding.

**Signal 2 — verb-class-conditioned frame-TYPE membership (learned, construction-level, the Friederici &
Frisch mechanism):** for the verb's CONSTRUCTION (reusing the LCCP sibling's Step 4 clustering), maintain a
small learned table of which SEMANTIC SLOT TYPES that construction licenses — directed-motion constructions
(arrive/come/go/return-class) license a GOAL/PATH slot type per VerbNet's Destination role; manner-of-motion/
posture constructions (walk/run/stand-class) do NOT license GOAL/PATH as a core slot type by default, but MAY
admit it as a derived-argument when a bounded endpoint reading is licensed (the exact "walked home"/"ran home"
resultative-adjacent case) — this is checked as a TYPE-match question (does this construction's frame include
a slot of THIS semantic type at all), kept explicitly separate from an obligatoriness/count check, per Angle
3's ERP-motivated type-vs-count dissociation.

**Composite scoring + THREE-way outcome (not binary):** combine Signal 0 (category prior, dominant on clear
cases) + Signal 1 (learned entropy, the graded lever) + Signal 2 (construction frame-type membership) into a
gradient score (per Angle 1's gradient-not-binary finding; Kim et al.'s r=0.624 continuous score is the
closest computational precedent for why gradient outperforms forced-binary). Route the result to one of THREE
outcomes: **ARGUMENT** (high score, offered to LCCP as a PATIENT/THEME candidate) / **ADJUNCT** (low score,
never offered as PATIENT/THEME, but still available for GOAL/LOCATION/TIME/MANNER role slots) /
**DERIVED-ARGUMENT / DEFERRED** (middle-band score — e.g. directed-motion-verb + bare-locative-goal cases —
tagged as a GOAL/PATH role specifically, NEVER as PATIENT/THEME even in this middle state, reusing the
sibling coherence-gate's DEFERRED-state machinery rather than inventing a new one).

**Why this suppresses "came home" as PATIENT without hurting "hit ball":** the key mechanism is NOT a binary
arg/adjunct flag gating candidacy overall — it is that Signal 0's category check means "home"/"there" (bare
adverbial category) are NEVER even considered for the PATIENT/THEME role slot, regardless of Signal 1/2's
score; at most (per directed-motion Signal 2 membership) they land in the DERIVED-ARGUMENT/DEFERRED state
tagged GOAL/PATH — a role the sentence's semantics genuinely supports, just never PATIENT. "Ball" in "hit the
ball" is a bare NP (Signal 0: NP-eligible, PATIENT/THEME-eligible category), occurs across an enormous variety
of verbs too (concrete-object nouns are not distinguished from adjunct-locatives by raw semantic breadth) —
but Signal 0's CATEGORY check (bare NP vs bare adverbial), not Signal 1's verb-diversity entropy alone, is
what correctly keeps "ball" PATIENT-eligible while excluding "home"/"there": **the categorial/functional
prior (Signal 0) does the primary discriminating work for this specific failure mode; Signal 1's learned
entropy signal is the generalizing lever for cases Signal 0's category detector doesn't cleanly resolve (e.g.
bare-NP temporal expressions like "Tuesday," which share "ball"'s NP category but should still resist
PATIENT-role candidacy via high verb-diversity entropy).** This decomposition — a cheap structural prior doing
most of the work on the clean cases, a learned distributional signal generalizing to the harder residual —
directly mirrors the sibling GHC note's own two-gate, non-redundant-failure-subclass architecture.

**Why this is LEARNED, not a hand-list of adjuncts, and improves with exposure:** Signal 0's category
inventory is built via unsupervised/distributional POS induction (already-cited machinery), not a hand-authored
locative-adverb list. Signal 1's entropy scores are running corpus statistics, recomputed/refined as more text
is processed — genuinely improving (sharper argument/adjunct separation) with exposure, exactly the "learned
not hand-coded" requirement. Signal 2's construction-frame-type table is populated/refined via the same
construction-level learning already specified in the sibling LCCP drill, inheriting its preemption/entrenchment
retreat mechanism (Angle 2's Ambridge/Blything locative-overgeneralization precedent) to further suppress a
specific recurring mis-licensed (verb-class, filler-category) pairing that Signal 0/1 alone did not fully
exclude.

---

## The FAIR can-fail test

**Real baseline:** the CURRENT LCCP arm-C (per the sibling LCCP drill's own arm structure) — 0.50 precision on
the independent gold, which includes the ~23 came-home-class mis-licensed-as-PATIENT cases as a NAMED,
already-measured residual subclass (not a new metric invented for this drill).

**Independent gold:** same 280-item LCCP gold / assembled-cell scorer used in the sibling GHC and LCCP notes —
never used to tune REC's category inventory, entropy thresholds, or construction-frame-type table.

**One variable per arm:**
- Arm A: LCCP arm-C, unchanged (baseline) — mis-licenses `home`/`there`/etc. as PATIENT.
- Arm B: REC Signal 0 only (category/role-eligibility prior — hard-exclude bare locative/temporal/manner
  adverbial categories from PATIENT/THEME candidacy) — isolates whether the cheap structural prior alone
  closes most of the residual, cheapest/most literature-precedented (PropBank's own category-based AM-* design,
  textbook categorial distinction).
- Arm C: Signal 0 + Signal 1 (add learned verb-diversity/entropy distributional signal) — isolates whether the
  learned generalizing lever adds anything beyond the cheap category gate, and whether it correctly EXCLUDES
  high-verb-diversity bare-NP cases (e.g. bare temporal NPs) that Signal 0 alone would miss.
- Arm D: full REC (Signals 0-2 + DERIVED-ARGUMENT/DEFERRED middle state) — isolates the complete design,
  including correct GOAL/PATH role-tagging for directed-motion cases (vs simply discarding them).

**HARD-PASS (mis-licensing reduction, the primary bar):** Arm D reduces the ~23 came-home-class
mis-licensed-as-PATIENT error rate by >=50% (or >=15 points on the eval slice's precision metric, matching the
sibling GHC note's threshold convention) vs Arm A on independent gold, WHILE the transitive-argument (hit-ball-
class) recall drop is <=5 points net — this is precisely the trade-off the semantic/subcat-selectional-
coherence gate FAILED at (VET-confirmed orthogonal to subcategorization); HARD-PASSing here is the direct
demonstration that a STRUCTURAL/distributional signal succeeds specifically where the semantic signal failed.

**HARD-FAIL (mis-licensing reduction):** <15% reduction in came-home-class errors, OR transitive-argument
recall drops >10 points (net negative trade), OR the reduction and the recall cost are roughly equal in
magnitude (no net improvement) — would mean the structural/distributional signal does not cleanly separate
arg/adjunct on this eval slice either, and REC would need to fall back to a narrower, purely category-based
gate (Arm B alone) or accept the residual as a genuine corpus-scale bound (see brain-check below).

**HARD-PASS (gate-decomposition, mechanism-validity check, mirrors sibling GHC Prediction 3):** Arm B alone
captures the MAJORITY (cell-author sets exact threshold, e.g. >=70%) of Arm D's total mis-licensing reduction —
this would validate that the cheap categorial prior (Signal 0) is doing the primary discriminating work
(as this drill's Angle 4/5 design reasoning predicts), and Signal 1's added complexity should be judged
against how much of the REMAINING residual (bare-NP-category adjuncts like temporal expressions) it uniquely
closes, not against the full came-home-class reduction.

**HARD-FAIL (gate-decomposition):** Arm B captures LESS than half of Arm D's reduction (i.e. Signal 1's
learned entropy component is doing most of the work, not the cheap category prior) — would mean the categorial
distinction alone is insufficient even for the clean bare-adverbial cases, contradicting this drill's own
design reasoning about why Signal 0 should dominate, and warranting a re-examination of whether the corpus's
own POS/category-induction quality (not the REC architecture) is the actual bottleneck.

**Derived-argument correctness check (Arm D only, required, not optional):** for the directed-motion-verb
subclass (came/went/returned + home/there), confirm Arm D tags these as GOAL/PATH (derived-argument/DEFERRED
state), NOT as either a full PATIENT (Arm A's error) or a fully-discarded adjunct with no role at all (a
different, also-wrong outcome that would lose real information the sentence's semantics supports) — measured
against the independent gold's role-type annotations if available, else spot-checked manually on the ~23-case
subclass.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL, consolidated)

**Prediction 1 — Signal 0 (category/role-eligibility prior) closes the majority of the came-home-class
mis-licensing residual.** P=0.45 (deflated; most literature-precedented component — PropBank's category-based
AM-* design and textbook categorial distinctions are well-established, not novel synthesis — capped at the
general novel-synthesis-application ceiling since untested on THIS eval slice specifically). HARD-PASS/FAIL as
specified above.

**Prediction 2 — Signal 1 (learned verb-diversity entropy) generalizes the fix to bare-NP-category adjuncts
that Signal 0's category check alone misses (e.g. bare temporal NPs).** P=0.35 (deflated further; the entropy-
threshold engineering move itself has computational precedent — Korhonen/Villavicencio/Kim et al. — but has
never been validated as a SEPARATE ablation isolating its unique contribution beyond a category prior on this
specific small eval slice). HARD-PASS: Arm C measurably reduces mis-licensing on cases Signal 0 alone does not
close (bare-NP adjuncts specifically), beyond noise. HARD-FAIL: no measurable additional reduction beyond
Arm B — Signal 1 adds complexity without benefit on this corpus.

**Prediction 3 — the DERIVED-ARGUMENT/DEFERRED middle state correctly tags directed-motion+goal cases as
GOAL/PATH rather than PATIENT or fully-discarded.** P=0.35 (deflated; genuinely novel engineering application
of the Needham & Toivonen linguistic-theory category — no computational precedent found for implementing
"derived arguments" as an engineered third state). HARD-PASS/FAIL as specified in the can-fail test above.

**Prediction 4 — the corpus is large enough for Signal 1's verb-diversity entropy estimates to be reliable
(not dominated by sparse-count noise).** P=0.40 (deflated; a mechanism-validity/data-sufficiency check, not a
capability claim). HARD-PASS: entropy scores for known-adjunct-category fillers (locative/temporal adverbs)
and known-argument-category fillers (canonical direct objects) are STATISTICALLY SEPARATED (not overlapping
within noise) on this corpus. HARD-FAIL: the two distributions overlap substantially — meaning corpus-scale
sparsity (not the REC architecture) is the binding constraint, and Signal 1 should be deprioritized relative to
Signal 0 until more corpus is available (see brain-check).

---

## Brain-check (outcome not pre-assumed)

**The argument/adjunct distinction IS a real capability the human parser and human linguistic theory both
rely on** — Boland & Blodgett's eye-tracking evidence and Friederici & Frisch's ERP dissociation show the
human parser genuinely treats this as a distinct, online-checked property, not merely a post-hoc analyst's
convenience. Not a capability gap in principle.

**Where the brain-check reveals a REAL, shared structural bound (same-limit, accept):** the linguistic-theory
literature ITSELF does not agree on a clean binary test for argument vs adjunct — Przepiórkowski shows the
classic diagnostics (iterability, do-so) are theoretically unreliable; Toivonen shows they give mutually
INCONSISTENT verdicts across syntactic/semantic levels; and the "derived argument" middle category (Needham &
Toivonen) exists specifically BECAUSE some real cases (directed-motion + goal-locative, exactly "came home")
do not cleanly resolve to either pole even under expert linguistic analysis. **This means a HARD-FAIL on
Prediction 3 for the middle-band cases specifically would NOT be a design flaw — it would replicate a genuine,
well-documented indeterminacy in the linguistic phenomenon itself.** The correct response, honestly, is the
THREE-way (not forced-binary) outcome this design already specifies, not an expectation that the classifier
should achieve clean separation the human theoretical literature itself cannot achieve.

**Where the brain-check licenses a substrate-native departure:** the human parser's argument-preference default
(Pickering et al.'s frequency-independent structural bias) is a fast, heuristic, real-time commitment made
before all disambiguating evidence is available — appropriate for a resource-bounded biological system running
under real-time constraints. An engineered REC has no such time pressure: it can compute Signal 1's
verb-diversity entropy EXHAUSTIVELY over the WHOLE available corpus before committing to a candidate score,
rather than approximating it with a fast online heuristic the way a human parser must. This is a place to be
MORE exhaustive/globally-informed than the brain, not merely faithful to its online real-time approximation —
directly analogous to the sibling GHC note's own "Gate 1 can be exhaustive, the brain cannot" finding.

**Honest, corpus-sparsity-specific bound (the question this drill's brief asked directly):** YES, genuine
risk, not hypothetical — Signal 1's verb-diversity entropy score is only as reliable as the corpus's
per-filler-category verb-co-occurrence counts; on a SMALL corpus, a truly narrow-argument filler-type might
be seen with only 1-2 verbs simply due to data sparsity, indistinguishable in raw entropy terms from a filler-
type that is structurally restricted to few verbs for a real syntactic reason. This is a real, checkable bound
(Prediction 4 above tests it directly) — if it HARD-FAILs, the honest interpretation is corpus-scale, not an
REC design defect, and the mitigating fallback is to weight Signal 0 (category prior, needs no per-filler
frequency statistics, works from a single well-classified example) more heavily than Signal 1 until more
corpus is available, rather than abandoning the distributional lever outright.

---

## Cross-thread synthesis

This drill completes a three-part decomposition of the same-day 07-19 brain-drill arc on the LCCP break-0.50
residual: `research_np_head_candidate_generation_grounding_gate_5x_brain_drill_2026-07-19.md` (GHC) fixes
WRONG-TOKEN candidates within an already-correctly-scoped argument slot (`fields`/`table`/`regular`);
`research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md` (LCCP Steps 1-6) fixes WRONG-CANDIDATE-
SCORED-HIGHEST among already-role-eligible candidates via learned cue-competition; THIS drill (REC) fixes
WRONG-ROLE-ELIGIBILITY — a correctly-grounded, correctly-positioned constituent (`home`/`there`) being offered
as a PATIENT candidate when it should never be role-eligible for PATIENT at all, only for GOAL/LOCATION. All
three sit in a clean pipeline: REC's role-eligibility gate (this drill) -> GHC's token-candidate gates -> LCCP's
cue-competition scorer -> the sibling coherence-gate's accept/flag/DEFERRED signal as the shared training
feedback for all three layers' learned components. All four same-day drills independently converge on the same
architectural shape (per the LCCP note's own observation): a graded/construction-conditioned score, an explicit
non-binary DEFERRED/middle state rather than forced binary choice, and mechanisms that improve with exposure via
the coherence gate's feedback rather than treebank supervision.

## Ranked actionable anchors (delivered inline per no-routing-file discipline)

1. **[Primary, cheapest, most literature-precedented, P=0.45] Build + smoke REC Arm B alone** (Signal 0
   category/role-eligibility prior: exclude bare locative/temporal/manner adverbial categories from PATIENT/
   THEME candidacy, using the already-built distributional POS/category machinery) directly against the
   ~23-case came-home-class residual on the existing LCCP/GHC independent gold. This is the minimal-diff,
   highest-confidence first test — if it alone closes most of the residual (per the gate-decomposition
   HARD-PASS threshold), ship it before building Signals 1-2.
2. **[Secondary, contingent on Arm B leaving residual] Add Signal 1 (learned verb-diversity entropy)** —
   only build if Arm B's ablation shows a measurable remaining residual (e.g. bare-NP-category adjuncts like
   temporal expressions Signal 0 cannot catch by category alone). Reuses Korhonen/Villavicencio/Kim-et-al's
   established computational technique, adapted to filler-CATEGORY x SLOT-POSITION granularity.
3. **[Tertiary, contingent on Arms B+C HARD-PASSing the primary bar] Add Signal 2 + DERIVED-ARGUMENT/DEFERRED
   state** for correct GOAL/PATH role-tagging of directed-motion+goal cases specifically — the most
   novel-synthesis, least-precedented component (Prediction 3, P=0.35); build last, and only if the primary
   mis-licensing-reduction bar is already met, since correct role-TYPE tagging (vs simply excluding the
   candidate) is a refinement on top of the core fix, not required for the core fix itself.
4. **[Design constraint, zero-cost, applies regardless of test outcome] Never force a binary ARGUMENT/ADJUNCT
   flag — always route to the three-way ARGUMENT/ADJUNCT/DERIVED-ARGUMENT outcome.** Per the brain-check, the
   linguistic-theory literature itself (Przepiórkowski, Toivonen, Needham & Toivonen) does not achieve clean
   binary separation for genuinely intermediate cases; building REC as a forced-binary gate would risk a
   HARD-FAIL driven by fighting a well-documented linguistic indeterminacy rather than a genuine architecture
   defect.
5. **[Data-sufficiency check, run alongside Arm B, cheap] Verify Prediction 4 (entropy-distribution
   separation) before investing further in Signal 1** — if the corpus is too small for reliable verb-diversity
   entropy estimates, this should be known BEFORE building Signal 1, not discovered after a HARD-FAIL that
   would otherwise look like a design flaw.

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. If Prediction 1 (Signal 0 alone) HARD-PASSes,
the product gains a cheap, structural, zero-treebank fix for a specific, previously-uncatchable failure mode
(coherent-but-wrong PATIENT mis-licensing that a semantic/coherence-only gate structurally cannot see) —
directly extending the glass-box, no-external-LLM pipeline's precision on real prose with minimal build cost.
If Prediction 1 HARD-FAILs but Prediction 2 (Signal 1) HARD-PASSes, the honest read is that the categorial
prior alone is insufficient and the corpus-scale distributional lever is doing the real work — a more
expensive but still fully glass-box fix, redirecting build priority toward robust entropy-estimation
infrastructure (smoothing for sparse counts) rather than the cheaper category-only path. If Prediction 4
HARD-FAILs (corpus too small for reliable entropy estimates), the honest ceiling is that Signal 1 should be
shelved until more corpus is ingested, and Signal 0 (category prior) plus the existing GHC/coherence-gate
machinery is the near-term shippable fix — a real, incremental precision win, not a wasted cycle, and
consistent with the same "nail the categorial/structural fix first, add the learned distributional layer as
corpus grows" priority order the design already recommends.

---

## Citations (verified count)

**~24 distinct primary/named sources**, gathered via three parallel lit-scans this session (live web search;
flagged inline per sub-agent where PDF-fetch failed and findings are search-snippet/abstract-level rather than
full-text-verified): Forker 2014 (*Linguistic Discovery*, canonical argument/adjunct typology); Przepiórkowski
("Against the Argument-Adjunct Distinction in FGD"; "How not to distinguish arguments from adjuncts in LFG");
Toivonen 2021 (LFG21 Proceedings, "Arguments and adjuncts across levels"); Needham & Toivonen 2011 (LFG11
Proceedings, "Derived Arguments," pp. 401-421); Levin & Rappaport Hovav 2005 (*Argument Realization*,
Cambridge) and 2006 (*Computational Linguistics* 32(3), partial-fetch-only flagged); VerbNet Guidelines
(Colorado, Destination role for motion-verb classes); PropBank Annotation Guidelines (Babko-Malaya; Palmer,
Gildea & Kingsbury *Computational Linguistics*, AM-* vs ARG-N design); Kim, Rawlins, Van Durme & Smolensky 2019
(AAAI, arXiv:1809.07889, "Predicting the Argumenthood of English Prepositional Phrases," ELMo+BiLSTM 95.5%/
r=0.624); Tomasello 1992 (*First Verbs*, Verb Island Hypothesis); Ninio ("No Verb Is an Island"); Pine, Lieven
& Rowland-lineage corpus work (via McClure et al. 2006); Wonnacott, Newport & Tanenhaus 2008 (*Cognitive
Psychology* 56(3), dual verb-specific/verb-general distribution tracking); Korhonen (PhD thesis 2002; Korhonen,
Krymolowski & Briscoe LREC 2006; Korhonen et al. ACL W00-1325, unsupervised SCF acquisition); Villavicencio
2002 (ACL/CoNLL W02-2033, "Learning to Distinguish PP Arguments from Adjuncts," partial-fetch-only flagged);
Hwang 2012 (Colorado Research in Linguistics); Blything, Ambridge & Lieven 2014 (*PLoS ONE* 9(10):e110009,
preemption + entrenchment); "The Retreat from Locative Overgeneralisation Errors" (PMC4022747); Boland &
Blodgett 2006 (*Journal of Psycholinguistic Research*, eye-tracking argument-vs-adjunct reading time); Pickering,
Traxler & Crocker 2000 (*Journal of Memory and Language*, argument preference not frequency-reducible);
Tutunjian & Boland 2008 (*Language and Linguistics Compass* review); Osterhout & Holcomb 1992 (*Journal of
Memory and Language*, P600 for subcat violations); Friederici & Frisch 2000 (*Journal of Memory and Language*,
German, argument-TYPE vs argument-NUMBER ERP dissociation); Shapiro & Levine 1990 (preserved online
argument-structure access, agrammatic aphasia); Meltzer-Asscher et al. 2012 (*Neuropsychologia*/PMC3518698,
contradicting impaired online processing finding); posterior-perisylvian/angular-gyrus argument-density fMRI
work (PMC2873169); Christodoulopoulos, Goldwater & Steedman 2010 (EMNLP, unsupervised POS induction, reused
from sibling GHC note); Mintz 2003 (*Cognition*, frequent frames, reused from sibling GHC note).

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: individual literature components (the argument/adjunct
diagnostic battery, PropBank's ARG-vs-AM design principle, VerbNet's Destination role, the Friederici & Frisch
ERP dissociation, the Boland & Blodgett / Pickering et al. processing-preference findings) sit at established,
well-precedented confidence (P~0.50-0.65 each — several via search-snippet/partial-fetch rather than full
independently-verified primary text, flagged per angle above). The SPECIFIC engineering synthesis this drill
proposes — a three-signal Role-Eligibility Cascade (categorial prior + learned verb-diversity entropy +
construction-level frame-type membership) feeding a three-way ARGUMENT/ADJUNCT/DERIVED-ARGUMENT outcome, sitting
between GHC's token-gates and LCCP's cue-competition scorer — has NO direct literature precedent as an assembled
engineered pipeline (no cited source proposes this exact combination) and is held at P<=0.50 per the
novel-synthesis cap; Prediction 3 (the derived-argument middle-state role-tagging specifically) is the least-
precedented component, deflated to P=0.35, since implementing Needham & Toivonen's linguistic-theory category as
an engineered third state has no computational precedent in what was found this session.

---

## VERDICT (one line)

**The brain/field does not resolve argument-vs-adjunct with one clean test — the human linguistic-theory
literature itself treats it as a gradient with a genuine intermediate "derived argument" category for exactly
the "came home" case (Needham & Toivonen), while the online parser evidences a real, dissociable frame-TYPE
gate distinct from a frame-obligatoriness/count gate (Friederici & Frisch) — and this maps to a buildable
glass-box Role-Eligibility Cascade (categorial prior + learned verb-diversity entropy, mirroring PropBank's own
ARG-vs-AM design logic + construction-level frame-type membership) that sits between the existing GHC token-
gates and the LCCP cue-competition scorer, routing bare locative/temporal/manner adverbials to a
GOAL/LOCATION-eligible-but-never-PATIENT-eligible outcome, with the single cheapest, highest-confidence first
build being the categorial prior alone (Signal 0, P=0.45) — expected to close the majority of the ~23 came-home-
class residual on its own, before the more novel, more expensive entropy and derived-argument-state layers are
warranted.**
