# BRAIN-DRILL (5x): ANIMACY vs FULL WORLD-KNOWLEDGE for the coref/parser shared residual

**Date:** 2026-07-19. **Filed by:** research (4 parallel Sonnet lit-scans + director synthesis). **Trigger:**
direct USER 5-angle brain-drill on the shared root that BOTH the coref ceiling (they->flowers/huts) AND the
hard parser residual (build/huts vs build/stream) localize to: is a cheap, discrete, learnable ANIMACY feature
a different kind of semantic signal that resolves a meaningful chunk of the residual, distinct from the
selectional-coherence-cosine that FAILED all session — or does the residual genuinely need full commonsense
world-knowledge (a real investment)? Composes with, does not re-derive: coref VET (atom 29355,
`research_coref_entity_tracking_brain_drill_2026-07-19.md`) and parser VET (atom 29350,
`research_argument_adjunct_subcat_hard_residual_brain_drill_2026-07-19.md`).

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement;
novel-synthesis capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]]. Established-lit findings
below are NOT deflated (textbook/replicated results are not our synthesis) but are confidence-flagged per
source, per the two companion drills' convention.

---

## HEADLINE

**Animacy is a genuinely different KIND of signal than the selectional-coherence-cosine that failed all
session — it is DISCRETE/CATEGORICAL, early-computed, and cheaply learnable, not a graded plausibility
estimate — and it escapes the structural-beats-semantic wall for exactly that reason: it is architecturally
the SAME kind of thing as gender/number agreement (a hard categorical pre-filter, already working in the
existing coref design) not the same kind of thing as topical-coherence-cosine (a graded similarity score,
already failed twice this session). But the lit scan draws a second, load-bearing line the task explicitly
asked for: animacy-the-cheap-feature is NOT the same thing as animacy-as-a-substitute-for-full-commonsense-
reasoning. The literature does not treat these as interchangeable — McRae/Ferretti/Elman's generalized-
event-knowledge tradition explicitly finds animacy is usually just ONE feature embedded within a much richer,
graded, combinatorial event-knowledge system, not a separable stand-in for it. Verdict: build the cheap
animacy slice now (hours-to-a-day, no KB, stays glass-box) — it should resolve most of the NAMED
they->inanimate coref harm (a genuinely categorical exclusion problem: person/plural-people vs thing) and
contribute a small, real, secondary signal to the parser's selectional-type-check — but do not expect it to
close the parser's argument-structure residual (that mechanism is already identified as subcat-frame +
directional-PP, not entity-type) or the contested/gradient PropBank-vs-FrameNet slice. Full commonsense
world-knowledge (ConceptNet/ATOMIC/COMET-class resources) is confirmed by the lit scan as a categorically
LARGER, multi-year/multi-person-scale investment with known coverage/noise problems even after that
investment — a real USER-steer fork, not a cheap next build.**

---

## Ranked verdict (viability ladder)

1. **Mechanism-class fit: STRONG that animacy is architecturally distinct from the failed cosine signals.**
   Weckerly & Kutas (1999) and the "is animacy special?" ERP literature show animacy violations produce a
   distinct signature (N400 + an amplified P600) even in structures that are otherwise syntactically and
   semantically legal — i.e., animacy is computed as a privileged, early, largely categorical feature, not
   folded into one generic graded semantic-fit computation. This is the same mechanism CLASS as gender/number
   agreement (a hard, discrete pre-filter), which the coref drill (angle 1) already ranked as a "strong
   early-acting cue" and which is already a working feature in the existing design (A_animate, gendered
   pronouns only). Confidence: medium-high that the mechanism class is right; the "animacy is a fully separate
   module" framing itself is an ACTIVE, UNRESOLVED debate in the ERP literature (see angle 2 below), so this
   is not overclaimed as settled neuroscience.
2. **Cheap-glass-box buildability: STRONG, with one honest corpus-scale caveat.** Distributional/unsupervised
   animacy classification (no hand-built ontology, no KB) is a converged, decades-old computational-linguistics
   sub-literature reaching high-80s to mid-90s percent accuracy across multiple languages (Dutch, Norwegian,
   English) from small feature sets: subject-of-verb-class frequency, who/which relativizer co-occurrence,
   pronoun co-occurrence. This is genuinely cheap engineering — classical classifiers (kNN/MaxEnt/SVM), not
   deep learning, not a KB. Caveat (own it): every cited classifier was trained/evaluated on corpora far larger
   than this project's 163-sentence set; per-verb subject-frequency statistics are already flagged elsewhere
   this session as corpus-sparse. The honest fix is the SAME pattern already used for the parser drill's
   Villavicencio-style selectional check: seed from a small, CREDITED list (e.g. a WordNet-hypernymy-derived or
   hand-listed ~50-150 word animate/inanimate seed set) rather than induce cold from 163 sentences, then refine
   distributionally as more text is read. Confidence: high that the METHOD is cheap and real; medium that it
   reaches the literature's 85-94% ceiling AT THIS CORPUS'S SCALE without the seed-bootstrap.
3. **Fraction-of-residual resolved: HIGH for the coref harm class specifically, LOW-MODERATE for the parser
   residual.** The named coref harm (they/plural-pronoun resolving to an inanimate antecedent when a
   plural-people antecedent is available) is fundamentally a categorical EXCLUSION problem — person/people vs.
   thing — which is exactly the kind of binary distinction the cheap classifier is built for and validated on.
   The parser's hard residual (motion/aspectual verbs given spurious patients: come/sit/stand/walk) was already
   independently diagnosed (parser VET, atom 29350) as an ARGUMENT-STRUCTURE problem (subcat-frame-frequency +
   directional-PP diagnostic), not an entity-TYPE problem — animacy is not absent from that picture (a
   directional/locative NP like "home" or "there" is itself usually inanimate, which is mildly informative) but
   it is a small, secondary contributor there, not the primary fix. Confidence: medium-high on the coref-harm
   fraction being large; medium-low, explicitly flagged, on any specific numeric estimate for the parser-residual
   fraction (this drill did not find literature that quantifies animacy's marginal contribution to
   argument/adjunct disambiguation specifically — it is a plausible, small, INFERRED contribution).
4. **Does animacy substitute for full world-knowledge: NO — this is the drill's central, most important
   negative finding.** The McRae/Ferretti/Elman generalized-event-knowledge line, the strongest established
   psycholinguistic account of how humans bring world knowledge to bear during real-time comprehension, treats
   animacy as ONE feature embedded within a much richer, graded, combinatorial system (verb-specific thematic
   expectations, e.g. "arrest" implies a cop-like agent and criminal-like patient) — not as a separable,
   sufficient stand-in for it. No source found in this scan draws a clean line "animacy handles X%, full
   commonsense handles the rest" — this dividing line does not exist as an established quantitative fact; it is
   this drill's own inference (see angle 5, capped P=0.45).
5. **Overall: VIABLE AS A CHEAP, GATED, SCOPE-LIMITED BUILD — not a general world-knowledge substitute.**
   Build distributional animacy now (small, seeded, glass-box), gate it into the SAME hard-pre-filter slot
   gender/number already occupies in the coref design, and measure its effect on (a) the named coref harm class
   specifically and (b) the parser residual's entity-type-driven subset specifically (separated by triage from
   the argument-structure-driven subset, which needs the already-identified subcat-frame/directional-PP fix
   instead). Deflated novel-synthesis P = **0.45** for the overall verdict (capped by policy at 0.50).

---

## 5-angle findings (credited, confidence-flagged)

**Angle 1 — Animacy in the brain / linguistic typology.** The animacy hierarchy (Silverstein 1976; Comrie
1989; Dixon 1979/1994 on split ergativity; Dahl & Fraurud 1996 on discourse/referential accessibility) is
well-established as a cross-linguistic organizing principle for case marking, differential object marking
(Aissen 2003) and agent/patient prototypicality (Dowty 1991's Proto-Role account — animacy contributes to but
does not equal agenthood). Whether the underlying construct is strictly DISCRETE or GRADED is itself contested:
mainstream typology treats it as a small number of ranked, language-specific cut-points (a discrete grammatical
device), but corpus and cognitive work increasingly treats the underlying conceptual variable as graded even
within the inanimate category — the discreteness is at least partly an artifact of grammar imposing categorical
cuts on a continuous scale (this synthesis point is the sub-agent's own inference, flagged). Neurally, the
animate/inanimate axis is one of the most robust, well-replicated organizing dimensions of object representation
in ventral temporal cortex, largely task-independent (established, high confidence). Distributional/unsupervised
animacy induction is a converged sub-literature (Bloem & Bouma; Bowman & Chopra 2012; Bergsma & Lin-style
n-gram mining; a 2018 ACL paper reframing it at the coreference-chain level) reaching high-80s to mid-90s
percent accuracy from small feature sets — established, moderate-to-high confidence on the specific numbers
(several came from search snippets rather than independently-verified full-text reads, flagged per source).

**Angle 2 — World-knowledge in real-time comprehension.** N400 plausibility effects (Kutas & Hillyard 1980
onward) are fast and largely automatic (established), but the field itself distinguishes N400 (lexical/
associative fit, possibly closer to "prediction strength" than "deep event-plausibility") from later
posterior-parietal positivities tied more specifically to genuine plausibility violation — the exact
mechanism-to-signal mapping is contested, not settled. The "good-enough processing" literature (Ferreira and
colleagues) is directly on point: comprehenders build shallow, heuristic-driven representations (an
agent-first NVN heuristic, plausibility/animacy-based shortcuts) rather than complete parses, and get
canonical-but-implausible sentences WRONG at rates well above floor (Ferreira 2003's passive-implausibility
studies) — a real, replicated human error mode, not just a slower-RT phenomenon; flagged as a genuinely
contested/under-specified framework by a 2024 review, not a fully quantitative settled model. Critically for
this drill's central question: the McRae/Ferretti/Elman generalized-event-knowledge tradition shows thematic
fit is graded, verb-specific, and combinatorial (jointly driven by the verb AND the preceding argument, not a
lookup), and the literature does NOT draw a clean separating line between "animacy as a cheap discrete
feature" and "full event/world knowledge as an expensive graded resource" — the dominant treatment nests
animacy INSIDE the richer system rather than beside it as an independent shortcut (this specific
"not-cleanly-separable" characterization is the sub-agent's synthesis of converging findings, medium
confidence, flagged as inference not a single paper's explicit claim). Honest human ceiling: WinoGrande human
accuracy is ~94% (majority vote, Sakaguchi et al. 2020), not 100% — humans are highly but not perfectly
accurate on curated commonsense-reference tasks, and separately show substantially higher error rates on
adversarially-constructed implausible-but-grammatical sentences (a different task type, not directly
comparable numerically). No paper found gives an explicit quantitative split of how much disambiguation work
is done by a cheap animacy-like feature vs. the fuller commonsense system — this is an open question in the
field, not a settled estimate (a genuine literature gap, not a recall failure).

**Angle 3 — Acquisition.** Animacy/agency perception is present remarkably early — infants as young as 3-7
months distinguish animate from inanimate motion via self-propulsion and causal-contact cues (established,
multiple converging studies); Mandler's "perceptual meaning analysis" account treats this as a perceptual/
conceptual primitive that PRECEDES and scaffolds the linguistic category, though whether this is innate/
domain-specific or built through domain-general perceptual learning remains an open, explicitly-contested
debate in the retrieved sources. The Bates & MacWhinney Competition Model treats animacy as a fast, LOCAL,
low-working-memory-cost cue in cross-linguistic sentence interpretation, in explicit contrast to word order (a
"distributed," more processing-costly cue) — a well-established, decades-deep, cross-linguistic empirical
program (high confidence). By contrast, Winograd-schema-class ambiguity resolution (the genuinely
commonsense-world-knowledge-dependent case) has essentially NO direct developmental literature — this is a
confirmed gap, not a recall failure, since the Winograd Schema Challenge itself originates purely as an
AI-benchmark construct with no developmental-psychology counterpart found. The closest analog, implicit-
causality-driven pronoun resolution, has a documented PROTRACTED developmental timeline extending into
adolescence and continuing to be refined by print exposure into adulthood — supporting (as an inference, not a
directly-cited dissociation claim) that early/cheap animacy-like cues and late/effortful full-commonsense
disambiguation follow genuinely different developmental trajectories, exactly the split this drill's central
question asks about. No study was found on whether animacy is learnable from distributional co-occurrence
ALONE without perceptual grounding, nor one that refutes distributional-only learning — this remains an open
question, flagged rather than resolved.

**Angle 4 — Computational: cheap animacy vs. investment-grade commonsense.** Distributional animacy
classification is confirmed cheap: classical classifiers, small feature sets, high-80s-to-mid-90s percent
accuracy, converged across multiple language replications (established, Angle 1's computational sources).
Historically, animacy/gender filters in rule-based coreference (Hobbs 1978's baseline, later WordNet-augmented
pipelines) provided a real but CORPUS-DEPENDENT, bounded improvement — not a dominant driver on their own
(Orasan & Evans, JAIR ~2007) — directly consistent with this drill's framing that animacy is a real,
worthwhile, but BOUNDED lever, not a silver bullet. By contrast, commonsense-knowledge resources (ConceptNet,
built from Open Mind Common Sense's multi-year crowdsourced contributions; ATOMIC, Sap et al. 2019, 1.33M
crowdsourced triples; COMET, Bosselut et al. 2019, a generative model trained on top of that curated base) are
confirmed to be multi-year, multi-person-scale engineering efforts — categorically larger than an animacy
classifier — and COMET's own paper explicitly names coverage gaps and lack of context-sensitivity as
persisting problems even after this investment, directly relevant to Winograd-style disambiguation quality.
Weak-supervision/distillation selectional-preference learning without a KB (Resnik 1996; Rooth et al. 1999;
Erk 2007; later LDA/tensor-factorization approaches) sits in between: cheaper than a curated KB, evaluated
mainly via the easier pseudo-disambiguation proxy task, with known coverage-vs-accuracy tradeoffs — a real
middle option if a full KB investment is later rejected, worth flagging as a fallback for the
world-knowledge slice rather than only "build a KB or nothing." No single paper explicitly states "animacy is
cheap and bounded, full commonsense is categorically bigger" as its own thesis — this is the sub-agent's
inference from the size/cost/coverage contrast across the two literatures (moderate-to-good confidence,
flagged as inference).

**Angle 5 — Structural verdict, synthesis (this drill's own contribution, capped P=0.45).** See Ranked
verdict above. The core move: separate the MECHANISM-CLASS question (is animacy a discrete, early, cheap
signal, architecturally distinct from a graded cosine plausibility estimate? — yes, well-supported) from the
SUBSTITUTABILITY question (can animacy stand in for full world-knowledge? — no, the strongest lit tradition on
real-time world-knowledge use nests animacy inside the richer system, does not treat it as a free-standing
replacement) from the DEPLOYMENT question (so build the cheap animacy slice for the specific categorical-
exclusion problems it is suited to — the coref they-harm class — and route the parser's argument-structure
residual and the genuinely gradient/contested cases to their already-identified fixes or an honest ceiling,
not to animacy). This directly answers why animacy escapes the session's structural-beats-semantic wall while
selectional-coherence-cosine and topical-coherence did not: the wall is not "semantic signals fail," it is
"GRADED graded-similarity estimates fail" — animacy is discrete/categorical, architecturally kin to gender/
number agreement (already working) and head-finder-style hard structural constraints (already working), not
kin to a cosine score over a graded embedding space (already failed twice).

---

## Design: human cue -> HD operation mapping

| Human cue (angle 1/2/3 evidence) | HD-substrate operation |
|---|---|
| Animacy is computed fast, early, and (at least partially) categorically-distinct from graded semantic fit (Weckerly & Kutas ERP dissociation) | A HARD PRE-FILTER MASK on candidate feature vectors, evaluated BEFORE any cosine/graded scoring step — same architectural slot as gender/number in the existing coref design, not a new scoring dimension mixed into a cosine |
| Distributional animacy is cheaply learnable from small feature sets (subject-of-verb-class frequency, who/which relativizer, pronoun co-occurrence) | A small classical classifier (kNN/MaxEnt-equivalent glass-box scorer) trained on THIS corpus's own subject-position/relativizer/pronoun statistics |
| Corpus-sparsity risk (163 sentences vs. the literature's much larger training corpora) | Seed from a small, CREDITED animate/inanimate word list (WordNet-hypernymy-derived or hand-listed ~50-150 words) rather than induce cold — mirrors the parser drill's Levin-class-seed discipline, not a departure from it |
| Competition Model: animacy is a fast/LOCAL/low-cost cue, distinct from costlier/distributed cues (word order, full event knowledge) | Keep animacy as a CHEAP, EARLY-APPLIED gate; do not fold it into the same computation as the (already-planned, already-flagged-as-secondary) selectional-type check |
| Generalized event-knowledge (McRae/Ferretti/Elman): animacy is nested inside, not a substitute for, full graded thematic-fit/world-knowledge | Animacy feeds the parser's selectional-type-check as ONE additional cheap feature (per the sibling parser drill's Step 2/4), not as a replacement for the subcat-frame-frequency + directional-PP diagnostic already identified as the primary fix there |
| Winograd-schema-class resolution has no early developmental precedent and matures late (implicit-causality analog) | Do NOT attempt to route the genuinely gradient/contested residual slice (PropBank-vs-FrameNet-disagreement cases, per the parser drill) through animacy; flag those as either the parser drill's honest-ceiling bucket or a future KB/weak-supervision-selectional-preference investment |

---

## First buildable component

**Distributional animacy classifier, seeded (not cold-induced), extending the existing A_animate feature from
gendered pronouns (he/she) to ALL entity mentions (they/plurals/general nouns), deployed as a hard pre-filter
mask in the coref cleanup-memory candidate pool — the exact slot the coref drill's design table already
reserves for "gender/number/animacy agreement."** Concretely:

1. Seed list: a small, CREDITED animate/inanimate word list (~50-150 entries, WordNet-hypernymy-derived or
   hand-listed, explicitly credited as borrowed not induced, mirroring the parser drill's Levin-class-seed
   discipline).
2. Distributional refinement: for NP heads not in the seed list, score animacy from THIS corpus's own
   subject-of-verb-class frequency, who/which relativizer co-occurrence, and pronoun co-occurrence (the same
   three cheap features the literature's classifiers use) — small classical classifier, no deep model, no KB
   lookup at runtime, stays glass-box.
3. Output: a discrete (ideally 3-way: person/animal-or-generic-animate/inanimate, to match "they" resolving to
   people vs. things rather than a strict binary) label per candidate, consulted as a HARD PRE-FILTER before
   the coref cleanup-memory cosine match — candidates whose animacy label conflicts with the pronoun's
   implied animacy (e.g. "they" with strong person-antecedent evidence vs. an inanimate candidate) are masked
   OUT of the candidate pool, not merely down-weighted in a blended score.
4. Secondary consumer: the SAME animacy label is exposed as one additional (small-weight) feature in the
   parser's Villavicencio-style selectional-type-check (parser drill's Step 2/4), explicitly NOT as a
   replacement for that drill's already-identified primary fix (subcat-frame-frequency-at-verb +
   directional-PP diagnostic).

---

## Cheap decisive test / design-gated can-fail

Real baseline = current reader (0.557, animacy feature only for gendered he/she). One variable changes: extend
the animacy feature to all entities, hard-gated as a pre-filter (per
[[feedback-experiment-design-gate-can-fail-real-baseline-difficulty-on]]). Measure BOTH consumers named in the
task (the coref they-harm class AND the parser residual's entity-type-driven subset), triaged separately —
conflating them would make either ablation uninterpretable (mirrors the parser drill's own caution against
conflating its residual with the coref-mechanism residual).

**Prediction A (coref they-harm class — the drill's best-precedented claim).** P=0.45 (deflated, capped).
**HARD-PASS:** on the specifically-named they/plural-pronoun -> inanimate-antecedent harm class, the
extended animacy pre-filter reduces wrong resolutions with a break-budget no worse than the coref drill's own
Prediction A criterion (net breakage must not exceed net fixes, ideally near-zero given the hard-mask design).
**HARD-FAIL:** net breakage still exceeds net fixes on this harm class even with the hard pre-filter mask —
this would mean the bound is not (only) missing-animacy-signal but something deeper in candidate generation or
the cleanup-memory margin mechanism itself, echoing the coref drill's own HARD-FAIL branch.

**Prediction B (distributional-classifier viability at THIS corpus's scale — a genuine, separate can-fail).**
P=0.35 (deflated; this is the drill's own flagged corpus-scale risk, not a literature-reported number).
**HARD-PASS:** the seeded classifier reaches usable precision (its false-positive rate on animacy labels for
NPs NOT in the seed list is low enough that the hard pre-filter mask does not itself introduce new errors by
mis-masking a correct animate candidate) — measured on a held-out slice of this corpus's own NP heads against
independent gold animacy labels. **HARD-FAIL:** the corpus-sparsity concern is confirmed — distributional
refinement beyond the seed list is too noisy at 163 sentences to trust as a hard mask; the honest fallback is
to run animacy as a SOFT down-weight (not a hard mask) restricted to the seed list only, a smaller, still-real,
but explicitly reduced-scope win.

**Prediction C (parser residual's entity-type-driven subset — pre-registered LOW expectation, explicit).**
P=0.25 (deflated; explicitly low per the lit finding that this residual is dominantly an argument-structure,
not entity-type, problem). **HARD-PASS:** after triaging the parser drill's 92 coherent-but-wrong FPs into
entity-type-driven vs. argument-structure-driven vs. contested/gradient (reusing that drill's own Step 1
triage), animacy-as-a-selectional-check-feature measurably reduces FPs on the (likely small) entity-type-driven
sub-bucket specifically. **HARD-FAIL:** no measurable reduction on that sub-bucket, or the sub-bucket is
near-empty after triage — this would CONFIRM (not contradict) this drill's own prediction that the parser
residual's fix lies almost entirely with the already-identified subcat-frame/directional-PP mechanism, and
animacy's contribution there is genuinely negligible; an informative, expected negative, not a design failure.

**Cross-check (both-ways can-fail, explicit).** If A passes and C is a genuine near-empty-bucket null: the
cheap-animacy-slice hypothesis is CONFIRMED exactly as this drill predicts — animacy is a real, bounded,
coref-specific win, and the parser residual stays owned by the subcat-frame/directional-PP fix, not animacy.
If A fails: the coref harm class needs deeper investigation (candidate-gen or margin-mechanism), independent
of whether animacy labels themselves are accurate — do not conclude "animacy doesn't help" without first
checking Prediction B's classifier-quality result. If B fails (classifier itself too noisy at this scale):
the METHOD (distributional induction) is confirmed cheap in the general literature but NOT viable at this
project's specific corpus size without a larger seed list or more text — a genuine, informative,
corpus-scale-specific negative, not a refutation of the mechanism-class claim in Angle 1.

---

## Cross-thread synthesis

Composes directly with the coref VET (atom 29355): that drill already identifies gender/number/animacy
agreement as a "strong early-acting cue" in its design table but explicitly scopes A_animate to gendered
pronouns only — this drill supplies the literature-grounded case AND a concrete, seeded, glass-box method for
extending it to they/plurals/general nouns, targeting the SAME named harm class (they->flowers/huts) that
drill's HEADLINE calls out as unaddressed. Composes with the parser VET (atom 29350): that drill's Step 2/4
feature list (subcat-frame-frequency, directional-PP diagnostic) remains the PRIMARY fix for the motion/
aspectual residual; this drill adds animacy only as a small, secondary, explicitly-low-expectation feature to
that same feature set — not a competing mechanism, not a redundant build. Both companion drills already
establish the discipline this drill inherits and extends: seed from a small credited list rather than induce
cold on a 163-sentence corpus (Levin-class seed for the parser drill; animate/inanimate seed list here); gate
new signals behind a hard-break-budget can-fail rather than assume net-positive (mirrors both drills'
Prediction-A designs); and separate "genuine missing mechanism" from "honest, partly brain-shared ceiling"
before declaring victory or defeat on any post-fix residual. This drill's own contribution to that shared
discipline: the session-long "structural signals work, semantic signals fail" pattern is refined, not
overturned — the operative distinction is DISCRETE-CATEGORICAL vs. GRADED-CONTINUOUS, not
STRUCTURAL-SYNTACTIC vs. SEMANTIC-LEXICAL. Animacy is semantically-flavored content sitting on the
discrete-categorical side of that line, alongside gender/number/head-finding, which is exactly why the lit
scan finds it should behave like a structural signal (cheap, learnable, effective) rather than like the failed
graded-cosine semantic signals.

---

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. This drill separates a CHEAP, buildable-now
component (extended distributional animacy, hours-to-a-day, no KB, fully glass-box, targets the SPECIFIC
named they->inanimate coref harm) from a REAL, categorically larger investment decision (a commonsense-
knowledge resource for the genuinely gradient/world-knowledge-dependent remainder of the residual, whether that
means integrating a curated resource like ConceptNet with its known coverage/noise costs, or building a
weak-supervision selectional-preference model as a cheaper middle path). If Prediction A HARD-PASSes, this is
a second small, well-precedented, glass-box precision win on top of the coref drill's own gated build — a
genuine "gets smarter as it reads" increment, reusing an existing architectural slot rather than adding new
machinery. If Prediction C HARD-FAILs as pre-registered (expected), that is NOT evidence against the fork —
it is the honest confirmation that the parser residual's fix lives elsewhere, and the product decision about
whether to invest in full commonsense/event-knowledge should be made on its OWN merits (cost, expected
residual-fraction recovered, glass-box-noise tension) rather than being bundled into "animacy didn't work."
The USER-steer decision this drill surfaces cleanly: cheap animacy build = approve-and-ship-now-class decision;
commonsense-KB investment = a separate, larger, explicitly-flagged strategic fork requiring its own scoping
(cost, which resource, how to filter noise per [[feedback_vet_every_base_ingredient_fair_correct_brain_faithful_USER_2026-07-18]]),
not something to default into as a side effect of this drill.

---

## Citations (verified count)

**~35 distinct primary/named sources across 4 parallel lit-scans**, live-searched this session (flagged inline
per sub-agent where a search-snippet summary was the source rather than an independently-verified full-text
fetch): Silverstein 1976; Comrie 1989 (*Language Universals and Linguistic Typology*); Dixon 1979 (*Language*),
1994 (*Ergativity*); Dahl & Fraurud 1996; Aissen 2003 (DOM, *NLLT*); Dowty 1991 (Proto-Roles, *Language*);
Weckerly & Kutas 1999 + "Is animacy special?" ERP follow-ups; ventral-temporal-cortex animacy-organization
work (eLife 2019/arXiv:1904.02866-adjacent); Bloem & Bouma (Dutch animacy classifier); Bowman & Chopra 2012
(Stanford, MaxEnt animacy classifier); Bergsma & Lin-style web n-gram animacy/gender mining; 2018 ACL animacy
reframing paper (coreference-chain level); Kutas & Hillyard 1980 (N400); DeLong, Quante & Kutas 2014; "A Tale
of Two Positivities and the N400" (bioRxiv/PMC); Ferreira, Ferreira & Patson 2002/2007 (good-enough
processing); Christianson, Hollingworth, Halliwell & Ferreira 2001 (garden-path lingering); Ferreira 2003
(passive-implausibility errors); 2024 Frontiers/PMC good-enough-processing review; McRae, Ferretti & Elman
thematic-fit/generalized-event-knowledge line; Sakaguchi et al. 2020 (WinoGrande, human accuracy); Japanese-WSC
CHI 2024 comparison; infant animacy-perception studies (newborn speed-change sensitivity, *Scientific Reports*
2020; 7-month-old animacy perception, *Frontiers in Psychology* 2014; Hofrichter, Siddiqui, Morrisey &
Rutherford 2021, *i-Perception*); Mandler's perceptual-meaning-analysis account; Bates & MacWhinney Competition
Model; Dittmar, Abbot-Smith, Lieven & Tomasello 2008 (*Child Development*); implicit-causality developmental
literature (Hartshorne-lineage, protracted maturation into adulthood); Bever 1970 (recalled, syntax-vs-
plausibility competition); Hobbs 1978 (rule-based coref baseline); Orasan & Evans (~2007, JAIR, NP animacy for
anaphora); Lee et al. end-to-end neural coreference + gender-ablation study (arXiv:1910.13913); Open Mind
Common Sense / ConceptNet (Havasi, Speer et al.); ATOMIC (Sap et al. 2019, AAAI); COMET (Bosselut et al. 2019,
ACL P19-1470); Resnik 1996; Rooth et al. 1999; Erk 2007 (ACL P07-1028); Ritter et al. 2010 (LDA selectional
preferences); Van de Cruys 2014 (tensor-factorization selectional preferences).

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis capped at P<=0.50 throughout. The unified
verdict (cheap discrete-categorical animacy escapes the structural-beats-semantic wall for the coref harm
class specifically; full commonsense world-knowledge remains a categorically larger, separate investment; the
parser's argument-structure residual is NOT primarily animacy's to fix) is this drill's own synthesis across
four independently-sourced literatures, held at P=0.45 (low end of the calibration band) — no single cited
source proposes this exact combination or draws this exact separating line; each component literature
individually sits higher (P~0.55-0.70 for the established sub-claims: animacy-hierarchy typology, distributional
animacy classifiers' accuracy, good-enough-processing's core claims, Competition-Model cue-weighting) as
reported per-angle above. The corpus-scale risk flag (163 sentences vs. the literature's much larger training
sets) is this drill's own extrapolation, held at P=0.35, explicitly not a literature-reported number.

---

## VERDICT (one line)

**Animacy is a cheap, discrete, glass-box, brain-faithful feature (extend the existing gendered-only
A_animate to all entities via a small SEEDED distributional classifier, hard-gated as a candidate pre-filter
in the same slot gender/number already occupies) that should resolve most of the NAMED they->inanimate coref
harm and contribute a small secondary signal to the parser's selectional check — but it is NOT a substitute
for full commonsense world-knowledge (a categorically larger, multi-year-scale investment per ConceptNet/
ATOMIC/COMET, with known coverage/noise costs even after that investment), and it is NOT expected to close the
parser's argument-structure-driven residual (already correctly identified elsewhere as needing subcat-frame-
frequency + directional-PP, not entity-type) or the genuinely gradient/contested PropBank-vs-FrameNet slice —
build the cheap slice now, treat the world-knowledge slice as a separate, explicitly-scoped USER-steer fork.**
