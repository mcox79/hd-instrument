# BRAIN-DRILL (5x): ARGUMENT-vs-ADJUNCT + SUBCATEGORIZATION for the hard residual (motion/aspectual intransitives given spurious patients)

**Date:** 2026-07-19. **Filed by:** research (4 parallel Sonnet lit-scans + director synthesis). **Trigger:**
direct USER 5-angle brain-drill, scoped to the PRECISE remaining reader bottleneck: 0.557 who-did-what
precision, ~92 VET-confirmed coherent-but-wrong subcategorization/attachment FPs that no confidence filter
or coherence gate rescues (semantic schema-fit corr only 0.139). Hard core: intransitive-motion + aspectual
verbs given spurious patients (come/sit/stand/walk/lie/struggle: "came home" / "stood there" wrongly taking
home/there as patient), plus within-transitive attachment/coref residue.

This drill is narrower than, and sits downstream of, the same-day
`research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md` (LCCP design), which addressed
general argument-ROLE learning across NPs. That design's Step 2 already lists "verb-semantic-class fit" and
"construction-type membership" as scoring features and Step 4 clusters verbs into constructions — but neither
step specifies the ONE diagnostic this drill finds to be the actual missing piece: that presence of a
directional/locative phrase after a motion-class verb is itself a positive structural signal AGAINST
patient-hood, not evidence for it. This drill's job (per task brief) is the MECHANISM, not the architecture:
does the LCCP lever already cover this residual, or is a distinct addition needed? Verdict below: a distinct,
specific, but small addition to the existing lever, not a new architecture.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement;
novel-synthesis capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**The brain has a genuine, well-precedented three-part mechanism for exactly this residual — but it is
COSTLY even for the brain, and the field's own gold-standard corpora do not agree on the right answer for a
meaningful fraction of these cases.** (1) Verb-specific SUBCATEGORIZATION-FRAME information (a per-verb
memory of which complement types this verb typically takes, and their argument-hood status) is retrieved
IMMEDIATELY at the verb — before the complement is even parsed — and resolves attachment gradedly by
frame-frequency (Ford-Bresnan-Kaplan lexical preference; Trueswell, Tanenhaus & Kello 1993; Trueswell & Kim
1998; Boland's argument-immediacy findings), directly REFUTING a purely positional/linear "next NP/adverb =
patient" default as the brain's strategy. (2) Independently, the presence of a directional/goal phrase after
a motion verb is itself diagnostic of a DISTINCT (unaccusative/oblique-goal) argument-structure configuration,
not a patient reading — a structural fact from the lexical-semantics literature (Levin & Rappaport Hovav
1995) that a subcategorization-frame store should encode as a verb-CLASS-level prior, not a per-verb
idiosyncrasy. (3) Neurally, this is measurably not free: unaccusative verbs and alternating-transitivity verbs
(exactly the come/sit/stand/walk class) show longer RTs, extra left-IFG engagement, and late thematic-role
reactivation relative to unergatives (Meltzer-Asscher et al. 2008/2015) — the brain pays a real combinatorial
cost for this class, it does not resolve it "for free" the way canonical transitive-agent-patient sentences
are resolved.

**But the honest ceiling is not 100%, and possibly not close to it.** The acquisition literature itself flags
the PP-argument-vs-PP-adjunct learning problem (as opposed to the better-studied transitive/intransitive
NP-count problem) as an OPEN research question, not a solved one (Fisher/Lidz review). The computational
literature's one system that nails our EXACT verbs (Villavicencio 2002: swim/come/put/draw/kiss) reaches 100%
accuracy only on 3 verbs / ~190 sentences, using a HAND-CURATED semantic-type selectional hierarchy — not a
purely distributional result, and not validated at scale. Fully unsupervised core-adjunct classification
(Abend & Rappoport 2010) reaches only ~70% on the PP-argument subset specifically. And critically: PropBank
and FrameNet — two independently-built, expert-curated gold standards — DISAGREE on whether "he walked into
his office" is adjunct or core-argument (Hwang 2012; Dowty 2003 argues no clean binary exists for exactly
this class). **A real fraction of the 92 FPs may be resolving a genuinely gradient linguistic category, not
a fixable engineering bug** — this must be separated from the genuinely-missing mechanism before claiming any
test result closes the residual.

**Ranked verdict:** MISSING MECHANISM (buildable, well-precedented, small, and NOT the LCCP's current Step 2/4
feature set) accounts for the majority of the recoverable fraction of the 92 FPs; a MINORITY fraction is
likely an honest ceiling shared with the brain and with expert human annotators (gradient argument-hood).
Deflated P=0.45 that the proposed addition (below) recovers a meaningful (>=15pt) fraction of the motion/
aspectual-verb subset specifically; P=0.25 (low, explicitly flagged) that it closes the FULL 92-FP residual,
because a portion of that residual is likely the within-transitive attachment/coref cases this drill's
literature does not directly address (see Cross-thread synthesis).

---

## Angle 1 — Human psycholinguistics: how humans actually resolve this (established, not synthesis)

**Verb-specific subcategorization frame frequency, not linear position, drives attachment.** Ford, Bresnan
& Kaplan (1982) showed the classic minimal pair "The woman wanted the dress on the rack" vs. "...positioned
the dress on the rack": swapping ONLY the verb flips PP-attachment preference from ~90/10 to ~30/70, with
sentence structure held fixed — the resolving cue is a per-verb LEXICAL PREFERENCE (frame frequency), not
Frazier's structural Minimal-Attachment/Late-Closure defaults, which are now considered a superseded/partial
account. Trueswell, Tanenhaus & Kello (1993) confirm this preference is used IMMEDIATELY (cross-modal naming,
self-paced reading) and GRADEDLY (proportional to the verb's own frame-frequency distribution, not a
categorical switch); Trueswell & Kim (1998) show briefly priming a verb's less-frequent frame measurably
shifts real-time attachment, establishing the frame-frequency cue as causally load-bearing, not merely
correlated. Boland (and related work) shows argument-structure/participant-role information is retrieved at
the verb itself, before the complement is parsed, with processing load scaling with expected argument count
— i.e., the human parser commits to an argument-structure EXPECTATION at the verb, before the ambiguous
material ("home", "there") ever arrives. This is the single most load-bearing, best-established finding of
this drill (P~0.65, established literature, deflated from higher raw confidence for the specific
"generalizes to this task's exact residual" application).

**The directional/goal-phrase diagnostic is a structural fact of the grammar, not just a processing
strategy.** Levin & Rappaport Hovav (1995, *Unaccusativity: At the Syntax-Lexical Semantics Interface*):
manner-of-motion verbs (walk, swim — lexically unergative in isolation) SHIFT to an unaccusative
configuration when combined with a directional/goal phrase (their diagnostic: auxiliary-selection alternation
in languages that mark it morphosyntactically). This means "came home" / "walked into the room" are not
ambiguous edge cases needing to be disambiguated by world knowledge — the directional PP itself is the
grammatical signal that the sole argument is being construed as a theme-of-a-path-event, and the following
phrase is a GOAL/PATH modifier of that event, structurally incompatible with also being read as a second,
patient-type argument. P~0.60 (established lexical-semantics framework; deflated for the specific claim that
this is available and used as a REAL-TIME processing cue — direct experimental confirmation of this exact
combination was not found this session, flagged below).

**Event structure (aktionsart) as an independent cue is theoretically motivated but experimentally
unconfirmed for this case.** Levin's verb-class taxonomy (1993) links meaning-class to syntactic-frame
behavior systematically; no direct RT/eye-tracking study isolating aktionsart as a disambiguating cue
SEPARATE from raw subcategorization frequency was found for motion+locative constructions specifically. Flag:
plausible, not evidenced. P~0.30 (this specific piece; the general aktionsart-syntax link is well-established
but its independent, separate-from-frequency causal role here is not).

**Gap:** no direct study found on aspectual/light-verb constructions' ("keep going," "started walking")
argument-structure processing. Treat as unaddressed by this drill.

## Angle 2 — Neural mechanism: real, measurable cost, not a free default

Friederici/Frisch-lineage ERP work distinguishes (a) phrase-category violations -> LAN, (b) subcategorization
violations (wrong complement TYPE) -> LAN-P600 (a syntactic signature), (c) argument-structure violations
(wrong complement COUNT, e.g. an intransitive given a direct object) -> biphasic N400-P600, where the N400
indexes thematic-integration difficulty and the P600 indexes syntactic reanalysis. Agrammatic aphasics show a
double dissociation (attenuated P600 with NO N400 for argument-structure violations, vs. attenuated-but-present
N400 for plain semantic violations) — direct evidence that combinatorial argument-structure assembly is a
separately-damageable capacity from lexical-semantic retrieval, consistent with the earlier LCCP drill's
Caramazza & Zurif finding for a different construction class. fMRI work (Meltzer-Asscher et al. 2008, 2015)
shows left IFG engaged in SELECTING/controlling the correct subcategorization frame while posterior MTG/
angular gyrus support lexical-semantic retrieval scaling with argument count; critically, **verbs with
ALTERNATING transitivity (can be used both transitively and intransitively — exactly the come/sit/stand/walk
class under discussion) elicit EXTRA activation specifically attributable to frame-SELECTION cost**, and
**nonalternating unaccusative verbs produce longer RTs and more IFG activation than unergatives**, with
late (~650-950ms) reactivation of the unaccusative's theme argument vs. near-immediate reactivation for
unergative agents (Burkhardt et al. 2003; Friedmann et al. 2008; Koring et al. 2012).

**Implication, directly on-point:** this is not a case where the brain resolves the ambiguity instantly and
for free while our reader fumbles it. The brain pays a real, measurable combinatorial cost for exactly this
verb class — which is independently consistent with this being a genuinely hard residual, not merely an
implementation gap. P~0.55 (established neuro literature; deflated for extrapolation from arrive/fall-type
unaccusatives in the cited studies to the come/sit/stand/walk set named in the task, which were not the exact
verbs tested).

The P600-subtype literature has NOT converged on one unified "argument-structure-specific" prediction-error
signal — multiple partially-overlapping P600 subtypes exist (syntactic-repair, semantic, thematic-reassignment
-scaled). This is an honest non-finding: the neat "coherence-mismatch = the single training signal" story from
the sibling LCCP drill is plausible but the ERP literature itself has not settled on one mechanism, several
coexist. Flag, do not oversell.

## Angle 3 — Acquisition: the field flags this SPECIFIC problem as open, not solved

Syntactic bootstrapping for INTRANSITIVES specifically (not just transitives) is directly evidenced: infants
as young as 15-21mo use NP-COUNT alone (absence of a second NP) to prefer one-participant over two-participant
event readings for novel verbs (Yuan, Fisher & Snedeker 2012; Jin & Fisher 2014, per the *Developmental
Origins of Syntactic Bootstrapping* review). This is good precedent for the CANDIDATE-GENERATION side (already
covered by the LCCP's Step 1, reused unchanged).

**But the PP-argument-vs-PP-adjunct distinction specifically is explicitly flagged by the acquisition
literature itself as unresolved, "needing future research."** No strong direct evidence was found this session
that children use PP-PRESENCE as a structural cue to a motion verb's argument structure (as opposed to reading
it as general event-location information). One directly-relevant, concerning finding: a 2023 study building on
Naigles (1990) found that changing an event's LOCATION between exposures actually DISRUPTS children's
intransitive-verb mapping — i.e., location/PP information can COMPETE WITH rather than cleanly CUE argument
structure for this verb class, the opposite of the clean diagnostic Angle 1's lexical-semantics literature
would predict. This is flagged as abstract-level-only (full text unparseable this session) but is an important
counter-signal against assuming the directional-PP diagnostic is trivially available to a learner.

No study was found targeting the SPECIFIC overgeneralization-retreat mechanism for a locative-PP misanalyzed
as a patient (as opposed to the well-studied causative/transitivization error class, "don't giggle me"). This
is a genuine literature gap, not a recalled-but-unverified fact — the retreat mechanism (preemption +
entrenchment, per Bidgood et al. 2021 and Boyd & Goldberg 2011) is well-established for the OTHER direction of
overgeneralization error; whether it transfers cleanly to this drill's specific error type is an open
extrapolation.

**Positive computational precedent for the update rule (not the specific cue):** Alishahi & Stevenson
(2005/2008) show a fully distributional Bayesian model recovers from argument-structure overgeneralization
using ONLY frequency/co-occurrence statistics, no negative evidence, no parameter hand-tuning — directly
validating the LCCP's Step 5 "coherence/frequency-driven retreat, no treebank" design principle in a
DIFFERENT, already-published engineered system, independent confirmation this general update-rule shape works
computationally. P~0.55 on the update-rule-shape transferring; P~0.30 (deflated, flagged as an open research
question in the human literature itself) on the specific directional-PP-as-cue claim.

## Angle 4 — Computational/NLP: the honest unsupervised ceiling, and the one system that nails our exact verbs

The classical PP-attachment literature (Hindle & Rooth 1993: ~80% via lexical co-occurrence stats, no
treebank required for the core method; Ratnaparkhi 1994 and Collins & Brooks 1995: 77.7-84.5%, but SUPERVISED
on Penn-Treebank-derived data) resolves attachment SITE (noun vs. verb), not argument-vs-adjunct STATUS —
Merlo & Esteve Ferrer (2006) explicitly note the classical task conflates these two questions, meaning this
literature does not directly answer this drill's actual question despite superficial similarity.

Unsupervised subcategorization-frame acquisition (Brent 1993, Manning 1993) achieves 76-96% precision/recall
on FRAME-CLASS detection from raw corpora with no treebank, but **Brent's own 1993 paper explicitly reports
locative adjuncts being mistaken for arguments as a documented failure mode from the very first unsupervised
system built** — this drill's residual is not a novel failure, it is the SAME failure mode noted in the
foundational unsupervised-acquisition literature over 30 years ago. Korhonen's verb-class (Levin-class)
smoothing rescues sparse per-verb statistics for medium/high-frequency verbs but explicitly does NOT rescue
low-frequency/hard cases — exactly the regime where this ambiguity bites hardest.

**Villavicencio (2002, CoNLL) is the single most directly on-point result found: she attacks THIS EXACT
ambiguity for THIS EXACT VERB CLASS** (her test verbs include swim, come, put, draw, kiss) using a frequency
threshold (>=80% co-occurrence => obligatory argument) combined with a HAND-BUILT semantically-motivated
preposition-selection hierarchy (a "motion-act" verb class selects a "motion-across" PP-type, etc.) — reaching
100% correct argument/adjunct classification. Two critical caveats: (1) tested on only 3 verbs / ~190
sentences from child-directed speech — a proof-of-concept, explicitly flagged by the author as needing
larger-scale validation, not a validated ceiling; (2) the semantic type hierarchy is CURATED, not
distributionally learned — this softens the "no hand supervision" framing considerably; it is closer to a
small, hand-authored verb-class + selectional-type lexicon than to a fully unsupervised result.

Fully unsupervised core-adjunct classification at scale (Abend & Rappoport 2010, evaluated against PropBank):
~70% on the PP-argument subset specifically (the hard subset; non-PP arguments are ~87% almost trivially).
Supervised in-domain ceiling: 99.5% (Toutanova et al. 2008); cross-domain supervised: 95.3-95.6% (CoNLL 2005).
**Most important honest-ceiling finding: PropBank and FrameNet — two independently-built EXPERT gold
standards — actively DISAGREE on this exact construction type** ("he walked into his office": PropBank tags
the directional phrase adjunct, FrameNet tags it core "Direction"). Dowty (2003) argues theoretically that no
clean binary exists for this class; Kim et al. (2019) build a SUPERVISED gradient/probabilistic model (95.5%
against VerbNet-derived gold) that explicitly treats argument-hood as a continuum rather than forcing binary
argument/adjunct, and specifically discusses locative PPs with change-of-location verbs as gradient cases.

**Honest ceiling synthesis (my own inference, not a single reported number, flagged as interpretation):**
given (a) the general unsupervised core-adjunct ceiling is ~70-82%, (b) this specific construction class is
repeatedly singled out in the literature as among the MOST contested (not an average-difficulty case, a
worse-than-average one), and (c) the one purpose-built system for this exact case required curated
verb-class-typed selectional knowledge, not pure distributional learning, and was validated on only 3 verbs
— a fully unsupervised, no-curation system should be expected to cap around **55-65%** on this specific
ambiguity class, likely below rather than above the general PP-argument average. P=0.40 on this specific
numeric range (deflated; it is an extrapolated synthesis judgment, not a directly reported number from any
single source).

## Angle 5 — STRUCTURAL VERDICT: missing mechanism (mostly), real shared ceiling (partly) — separated

**Missing mechanism (buildable now, well-precedented, recoverable fraction of the residual):**
1. A verb-specific SUBCATEGORIZATION-FRAME store — per-verb (or per-verb-class, Korhonen-style smoothed for
   low-frequency verbs) memory of which complement TYPES this verb has been seen taking, and with what
   argument-hood status — consulted IMMEDIATELY at the verb, before scoring the candidate complement, not
   only as a downstream feature in final-candidate scoring. The current LCCP design's Step 2 features
   ("verb-semantic-class fit," "construction-type membership") are adjacent but do NOT include this specific,
   well-established, immediately-consulted cue as a first-class signal. This is a genuine addition, not
   already covered.
2. A DIRECTIONAL/GOAL-PP DIAGNOSTIC keyed on VERB CLASS (motion/aspectual verbs specifically): presence of a
   directional/locative phrase after a verb in this class should carry a NEGATIVE prior on patient-hood and a
   POSITIVE prior on path/goal-modifier construal — encoding Levin & Rappaport Hovav's structural fact
   directly as a competing structural cue against the apparent positional default. This is the single most
   concrete, actionable, well-grounded fix for the named failure mode ("came home" / "stood there").
3. A verb-class-keyed SELECTIONAL TYPE CHECK (Villavicencio-style: does the filler's grounded-vector semantic
   neighborhood look like a place/goal type vs. a patient/theme type), but LEARNED distributionally from the
   coherence-gate's own accept/reject signal (per Alishahi & Stevenson's proof that this is computationally
   viable with no negative evidence) rather than hand-curated (avoiding Villavicencio's curation dependency) —
   seeded with a small, CREDITED, borrowed verb-class list (Levin's ~50 motion/aspectual classes) rather than
   induced from scratch cold, exactly mirroring the LCCP's own "reuse the ClausIE taxonomy as Step 4's seed,
   don't induce cold" design principle.

**Does the LCCP lever already address this, or is a distinct mechanism needed (per task's explicit ask)?**
The general ARCHITECTURE (construction-level weight-sharing, coherence-gate-driven update, no treebank) is
correct and reusable — Alishahi & Stevenson independently validate that exact update-rule shape. But the
CURRENT FEATURE SET (Step 2/4 of the sibling drill) does not include the three specific ingredients above.
Verdict: **a distinct, small, targeted ADDITION to the existing lever's feature set and construction inventory
— not a new architecture, and not something the existing LCCP design already covers by implication.** This
should be built as new Step-2 features (subcat-frame-frequency-at-verb, directional-PP-diagnostic-by-verb-
class) and a new Step-4 construction row (motion/aspectual verbs as their own construction, seeded from
Levin's classes), not as a separate system.

**Real, partly-brain-shared ceiling (honest, do not oversell past this):**
1. The brain pays a genuine combinatorial cost for exactly this verb class (Angle 2) — this is not a
   free/instant human capability being poorly imitated; some residual difficulty is expected even with the
   mechanism correctly built.
2. The acquisition literature itself flags the PP-argument-vs-adjunct learning problem as unresolved, with at
   least one finding suggesting location information can DISRUPT rather than cleanly cue argument-structure
   learning for this class (Angle 3) — meaning the "children obviously nail this via some knowable mechanism"
   framing is itself not fully supported; part of human competence here may be later-acquired, effortful,
   world-knowledge-dependent disambiguation rather than an early clean structural cue.
3. Expert-curated gold standards (PropBank vs. FrameNet) DISAGREE on this exact construction type, and Dowty
   argues no clean binary exists (Angle 4) — meaning a nontrivial fraction of the 92 FPs may be scoring against
   a genuinely gradient category under a forced-binary rubric. **Recommendation embedded in the test design
   below: report a GRADED argument-hood score in addition to the binary FP count**, per Kim et al. 2019's
   gradient-argument-hood framing, so a "coherent-but-wrong-by-binary-rubric but actually-gradient-correct"
   case is visible and not silently counted as a hard failure.

**Brain-check outcome (not pre-assumed, stated honestly):** MIXED. The brain has a well-precedented mechanism
we are missing (subcat-frame-frequency-at-verb + directional-PP diagnostic) — this part is a genuine,
buildable, brain-faithful fix, not a shared ceiling. But the brain also (a) pays a real cost for this class and
(b) may not have a clean, well-understood mechanism for the PP-argument-vs-adjunct sub-problem specifically
(the acquisition literature's own gap), and (c) even expert humans disagree on ground truth for a slice of
these cases. The honest reporting is: build the mechanism (expect real recovery), but do NOT expect it to
close the full 92-FP gap to zero, and do not treat a residual post-fix gap as proof the mechanism failed
without first checking whether the remaining cases are the gradient/contested subtype.

---

## Cheap decisive test

**Step 1 (free, do first):** re-triage the existing 92 coherent-but-wrong FPs into (a) motion/aspectual-verb-
given-spurious-patient (this drill's target class), (b) other within-transitive attachment/coref residue (out
of this drill's scope, see Cross-thread synthesis), and (c) cases where the "correct" label is itself
contested under a PropBank-vs-FrameNet-style disagreement (spot-check against the gradient-argument-hood
criterion, Kim et al. 2019's discussion of change-of-location verbs as a guide). This triage is required
BEFORE running any ablation — without it, a post-fix residual cannot be attributed to mechanism failure vs.
honest-ceiling gradience.

**Step 2 (build):** add the two new Step-2 features (subcat-frame-frequency table per verb/verb-class,
consulted immediately at the verb; directional-PP diagnostic keyed on a small, CREDITED Levin-class motion/
aspectual verb list) and one new Step-4 construction row (motion/aspectual verbs as their own construction),
to the existing LCCP design from `research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md`.
Learn the selectional-type-check weight distributionally via the coherence gate's accept/reject signal
(Alishahi & Stevenson update-rule shape), seeded (not fully hand-curated) from the Levin-class list.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 — the new features reduce coherent-but-wrong FPs on the motion/aspectual subset specifically.**
P=0.45 (deflated; this is the best-precedented claim in this drill, directly targets the named residual, but
untested as an engineered addition). **HARD-PASS:** >=15-point FP-rate reduction on the triaged motion/
aspectual subset (Step 1's category (a)) vs. the current reader, measured against independent gold, holding
category (c) (contested/gradient cases) OUT of the pass/fail count. **HARD-FAIL:** <5-point reduction, or no
measurable reduction — would indicate the directional-PP diagnostic and subcat-frame-frequency table are not
sufficient signal, and the failure is closer to Angle 3's "children may not have a clean early cue either"
finding than to a simple missing-feature gap.

**Prediction 2 — a meaningful fraction of the un-recovered residual (post-fix) is the gradient/contested
subtype, not mechanism failure.** P=0.35 (deflated; speculative fraction estimate). **HARD-PASS:** of the
FPs remaining after the fix, >=25% fall into Step 1's category (c) (contested under a PropBank/FrameNet-style
disagreement check) — confirming the honest-ceiling component is real and non-trivial. **HARD-FAIL:** <5% of
remaining FPs are contested-category — would mean the "genuinely gradient" framing is not actually
contributing to this residual, and the full gap should be attributed to further missing mechanism, not ceiling.

**Prediction 3 (mechanism-validity check, cheap, run alongside).** The learned selectional-type-check weight
(Alishahi & Stevenson-style, coherence-gate-driven) should measurably shift when the reliability of the
directional-PP cue is synthetically degraded in a held-out training slice (randomize verb-class tagging for a
subset of motion verbs). **HARD-PASS:** weight on the directional-PP feature measurably drops for the
degraded subset relative to a control run. **HARD-FAIL:** weight unchanged — construction-determined/vacuous
result, re-design before trusting Prediction 1's larger claim (mirrors Prediction 3 of the sibling LCCP note).

**Prediction 4 — reported graded argument-hood score correlates with human gradience where it exists.**
P=0.30 (deflated, exploratory). **HARD-PASS:** on the small subset of cases independently identified as
gradient/contested (Kim et al. 2019-style change-of-location verbs), the system's graded score sits nearer
the middle of its range than at the extremes, relative to clearly-argument and clearly-adjunct control cases.
**HARD-FAIL:** graded score shows no distributional difference between contested and clear-cut cases — the
graded-scoring addition is not adding real information, drop it and keep the binary classifier only.

---

## Cross-thread synthesis

This drill is the direct, narrower follow-on to `research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md`
(LCCP design): that drill's Step 2/4 feature set is necessary but not sufficient for this specific residual;
this drill supplies the two concrete missing features (subcat-frame-frequency-at-verb, directional-PP
diagnostic-by-verb-class) and one new construction row, to be added to that design, not built as a separate
system. It also connects to `research_coherence_schema_fit_gate_brain_drill_2026-07-19.md` (the coherence
gate remains the learning signal for the new features' weights — no new signal type is introduced) and to
`research_wm_barrier_glassbox_parsing_2026-07-17.md` (the dependency-stack structural memory is unaffected;
this drill only adds scoring features, not a new memory structure). It builds on and credits
`prior_art_scour_synthesis_focus_chaingrade_2026-07-18.md`'s commitment to Kintsch-CI + AMR/DRS +
NVSA/NS-CL-style learned-front-end-plus-fixed-symbolic-backend as the target architecture — this drill's
addition is squarely a learned-front-end feature, consistent with that commitment, not a departure from it.

**Explicitly out of scope for this drill, flagged for a follow-on:** the "within-transitive attachment/coref
residue" component of the 92 FPs (e.g., "took,herbert,one" / "passed,it,harm" style errors named in the task
brief) is a DIFFERENT mechanism class — likely coreference/pronoun-antecedent resolution and multi-argument
disambiguation, not the argument/adjunct-for-intransitives problem this drill addresses. A separate brain-drill
on anaphora/coreference resolution mechanisms (candidate: centering theory, Hobbs' naive algorithm,
binding-theory-constrained antecedent search, and their unsupervised/distributional analogs) is the natural
next-drill candidate and should NOT be folded into this drill's test design — conflating the two would make
Prediction 1's ablation uninterpretable (a null result could be wrongly attributed to the wrong mechanism).

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. If Prediction 1 HARD-PASSes, this closes the
single largest NAMED sub-category of the 0.557-precision residual with a small, well-precedented, glass-box,
no-treebank addition (two new features + one new construction row) to a design already committed to. If
Prediction 2 also HARD-PASSes (meaningful fraction of remaining FPs are genuinely contested/gradient), the
honest reporting for precision going forward is that a further ceiling exists that is NOT a bug — a real,
literature-documented, expert-disagreement-level linguistic gradience — and continuing to chase zero-FP on
this construction class past that point would be chasing an ill-posed target, not a real capability gap. If
Prediction 1 HARD-FAILs, the honest fallback (per Angle 3's acquisition-literature gap) is that the
directional-PP/subcat-frame cues are insufficient and the real disambiguating signal for this class may be
richer world-knowledge/event-simulation than a feature-level fix can supply — at which point the substrate-
native fallback from the sibling LCCP drill (always-on document-scope consistency checking) becomes the next
thing to try before concluding the residual is unrecoverable at this precision band.

---

## Citations (verified count)

**~30 distinct primary/named sources**, freshly verified via live search this session across four parallel
lit-scans (flagged inline per sub-agent where recalled-from-training/secondary-sourced rather than
independently fetched): Perlmutter 1978 (Unaccusative Hypothesis); Burzio 1986; Levin & Rappaport Hovav 1995
(*Unaccusativity: At the Syntax-Lexical Semantics Interface*); Frazier 1979/1987 (Minimal Attachment/Late
Closure); Ford, Bresnan & Kaplan 1982 (Lexical Preference); Boland 1993/2005; Schutze & Gibson 1999
(secondary-sourced this session, flagged); Trueswell, Tanenhaus & Kello 1993; Trueswell & Kim 1998; Vendler
1957 (aktionsart); Levin 1993 (*English Verb Classes and Alternations*); Friederici & Frisch 2000; Frisch,
Hahne & Friederici 2004; Ainsworth-Darnell, Shulman & Boland 1998; Osterhout, Holcomb & Swinney 1994; Grillo
et al. (agrammatism ERP, PMC3518698); Meltzer-Asscher et al. 2008 (PMC2632636), 2015 (PMC4336802,
PMC4485426); Burkhardt et al. 2003; Friedmann et al. 2008; Koring et al. 2012; Fisher/Lidz *Developmental
Origins of Syntactic Bootstrapping* review (PMC7004857); Yuan, Fisher & Snedeker 2012; Jin & Fisher 2014;
Kline & Demuth 2013; Bidgood, Pine, Rowland, Sala, Freudenthal & Ambridge 2021; Boyd & Goldberg 2011;
Alishahi & Stevenson 2005 (ACL Anthology W05-0510)/2008; Gillette, Gleitman, Gleitman & Lederer 1999 (Human
Simulation Paradigm); Hindle & Rooth 1993; Ratnaparkhi 1994; Collins & Brooks 1995; Merlo & Esteve Ferrer
2006; Brent 1991/1993; Manning 1993; Briscoe & Carroll 1997 (figures NOT independently verified, flagged);
Korhonen (subcat-frame smoothing thesis); Resnik 1996; Villavicencio 2002 (CoNLL); Abend & Rappoport 2010
(ACL, Fully Unsupervised Core-Adjunct Argument Classification); Toutanova et al. 2008; CoNLL 2005 shared task;
Dowty 2003; Hwang 2012; Kim et al. 2019 (arXiv:1809.07889).

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis capped at P<=0.50 throughout. The unified
verdict (three-part missing mechanism + partly-shared honest ceiling, and the specific claim that this is a
small ADDITION to the existing LCCP design rather than a new architecture) is this drill's own inference
across four independently-sourced literatures, held at P=0.45, the low end of the calibration band — no
single cited source proposes this exact combination or this specific fix; each component literature
individually sits higher (P~0.55-0.65) as reported per-angle above. The honest-ceiling numeric estimate
(55-65% unsupervised cap on this specific ambiguity class) is explicitly flagged as a synthesis judgment, not
a directly reported literature number, held at P=0.40.

---

## VERDICT (one line)

**The residual is MOSTLY a missing mechanism (a per-verb subcategorization-frame-frequency table consulted
immediately at the verb, plus a directional/goal-PP diagnostic keyed on verb class, both well-precedented in
human psycholinguistics and directly targeting the named come/sit/stand/walk failure mode — Villavicencio
2002 nails these exact verbs at small scale) that should be added as two new features + one new construction
row to the existing LCCP design (not a new architecture) — but PARTLY a real, partly-brain-shared honest
ceiling (the brain pays a measurable combinatorial cost for this verb class, the acquisition literature flags
the PP-argument-vs-adjunct problem as unresolved, and expert gold standards PropBank/FrameNet themselves
disagree on this exact construction type), meaning the fair test must separate a "contested/gradient" bucket
from the FP count before judging PASS/FAIL, and should not expect the fix to close the residual to zero.**
