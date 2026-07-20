# BRAIN-DRILL (5x): can the DIRECTIONAL/PATH closed-class detector be LEARNED FROM DISTRIBUTION, de-confounding atom 29349

**Date:** 2026-07-19. **Filed by:** research (4 parallel Sonnet lit-scans + director synthesis). **Trigger:** direct
USER 5-angle brain-drill on the confound the adversarial VET found in atom 29349: the syntactic-frame-frequency
teacher genuinely learns the correct anti-patient SIGN (w[f_dirpp] flips -2.47 syntactic vs +0.45 semantic), but a
hand-authored directional closed-class inventory (DIR_ADV/DIR_PREP) feeds BOTH the teacher's frame-typing AND the
f_dirpp feature, so the must-fail control fires but does not fully collapse -- "genuine learning" applies only to
the SIGN, given a hand-built scaffold, not learned-from-scratch. VET named the MM->CG path as: a distributionally-
learned directional detector that removes the shared-hand-list confound.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement; novel-synthesis
capped at P<=0.50), per [[feedback-lit-scan-calibration-penalty]]. Brain-check outcome NOT pre-assumed -- see
Angle 3/4 below, the literature does not hand the substrate a clean win.

---

## HEADLINE

**The hand-authored word list can be de-confounded, but not eliminated to zero, and the honest reason why maps
exactly onto a real asymmetry between the substrate and the brain: humans bootstrap the directional/path category
from an INDEPENDENT PERCEPTUAL channel (prelinguistic path/goal/manner discrimination, Pulverman/Golinkoff/
Landau/Mandler/Talmy) that a text-only substrate structurally does not have.** Stripped of that perceptual channel,
the only channel left is the one humans ALSO use in parallel -- a prosodic/frequency/positional signature that
flags "this is a closed-class function word" (Shi/Werker/Cutler) -- and the computational literature is explicit
and consistent that this signal identifies the COARSE function-word class well, but does NOT cleanly resolve the
FINE directional/path subclass (vs. temporal, causal, or other closed-class subclasses) without at least a small
seed set to expand from (Redington, Chater & Finch's own finding is that closed-class words are *harder*, not
easier, for pure distributional clustering than content words). So: **a genuine, buildable de-confound exists for
the SPECIFIC circularity VET flagged** (the SAME list feeding both teacher and feature) by building the candidate
set from a DIFFERENT statistic than the frame-typing use -- but a small, CREDITED seed set is a legitimate,
brain-analogous "given floor," not a violation of learn-like-a-human, because humans' fine subclass also isn't
free -- they get it from perceptual grounding we can't replicate from text, and even their coarse-class-only
distributional channel needs convergent cues, not one clean signal.

**Ranked verdict:** MISSING MECHANISM is buildable and worth building (Rank 1 below) for the SPECIFIC confound
(shared detector) -- P=0.38 (deflated, novel synthesis) that it fully de-confounds VET's specific finding (sign
stays negative + must-fail still fires when re-run on an INDUCED, not hand-authored, candidate set). The FULL
elimination of any hand-authored seed is NOT supported as achievable from text alone -- P=0.65 (established
literature: function words are the *harder*, not easier, case for zero-seed distributional induction; no paper
found demonstrating zero-seed fine-grained directional-subclass induction) that some minimal seed remains a
legitimate honest floor, analogous to (not a copy of) the brain's own reliance on a channel (perceptual grounding)
the substrate does not have.

---

## Angle 1 -- Acquisition: closed-class + spatial/directional terms specifically (established, not synthesis)

**Timing is protracted, not instant, and NOT purely perceptual.** Six core spatial particles (up/down/in/out/on/
off) emerge productively as verb-particle-like forms at 14-30 months, tied to caregiver routines and motion --
but these are NOT yet adult prepositional uses; **full closed-class prepositional integration for the same word
forms is not achieved until after age 4** (multi-year gap between first surface use and true category membership;
Frontiers 2019 review, Roadmap 0-60 months). Topological locatives (in/on) become true prepositions ~2-3y;
projective terms (under/behind/in front of) ~3-4y.

**Bowerman & Choi (1991, 1994, 2001, 2003) is the load-bearing finding against a purely-perceptual/innate origin
for the fine category boundaries:** cross-linguistic elicited-production work shows English-, Korean-, and
Dutch-learning toddlers categorize the SAME spatial events differently (support/containment vs. tightness-of-fit)
by 2.0-2.5 years, well before this could be innate-universal unfolding -- if the category were handed down by
nonlinguistic perception alone, children learning different languages should carve identical categories; they do
not. This directly answers part of the task's Angle-1 question: directional/path is NOT a purely perceptual/
innate category with language-independent boundaries -- the language-specific distributional input determines
where the fine category lines fall, even though (per Angle 4) a nonlinguistic substrate constrains what's
learnable at all.

**Gentner's relational-category program** (object nouns ~8-16mo, relational categories/words later, ~17-30mo,
CDI data) is directly relevant: directional/path markers are RELATIONAL (figure-to-ground/goal), predicting and
explaining their later, more effortful acquisition relative to nouns -- consistent with the protracted timing
above, not an isolated coincidence.

**Landau & Jackendoff's "what vs. where" dissociation** (1993, BBS) is a representational/neuropsychological
claim (parallels separate visual "what"/"where" cortical pathways) that a distinct place/path system exists
architecturally, separate from object-kind representation -- but this is a claim about ADULT representational
architecture with developmental plausibility, not itself a demonstrated acquisition mechanism. Slobin's
"thinking-for-speaking" (1996/2003) establishes that English (satellite-framed: path in a separate closed-class
particle, distinct from the verb which carries manner) vs. verb-framed languages (path folded into the main verb)
shapes what children encode early -- children calibrate to their language's framing pattern, another point against
a purely universal/innate category.

P~0.60 (established developmental literature; deflated for the specific claim that this bears directly on a
TEXT-ONLY system's induction problem, which these child studies do not test).

**Honest limit, not pre-assumed success:** full closed-class integration is LATE (age 4+) even for the exact word
forms in early productive use from 14 months -- directly undercutting any assumption that humans acquire this
category cleanly or quickly. The category is genuinely hard for humans too, just on a different axis (production/
integration timing) than the substrate's axis (distributional discoverability).

## Angle 2 -- Distributional/computational: the honest unsupervised ceiling (established, not synthesis)

**Redington, Chater & Finch (1998, Cognitive Science)** is the single most load-bearing and most inconvenient
finding here: their landmark demonstration that raw context-word co-occurrence + clustering recovers syntactic
categories strongly found that **distributional information is MORE useful for classifying content words (nouns,
verbs) than function words** -- i.e., the closed class the substrate wants is the HARDER case for the exact
technique being proposed, not an easier one. This directly informs the honest ceiling: pure co-occurrence gets you
"this word behaves like a function word" with LOWER confidence than it gets you "this word behaves like a noun."

**Coarse function-vs-content separation is well-solved** (Brown clustering, HMM-based unsupervised POS induction,
Clark 2003, mutual-information POS induction) -- these methods reliably produce a broad function-word cluster
distinguishable from content words, and Brown-clustering's hierarchical structure in principle supports descending
further into syntactically-coherent subclusters. **But no retrieved study demonstrates a clean, zero-seed
induction of the FINE directional/path subclass** specifically (as opposed to temporal, causal, or other
closed-class semantic subtypes) from pure co-occurrence alone -- every path found in the literature to a
fine-grained subclass goes through either (a) a small seed set + distributional-similarity expansion
(bootstrapping literature, e.g. semantic-seed noun/verb category acquisition), or (b) descending a hierarchical
cluster tree and hand-labeling the resulting subcluster. Verb-particle-construction detection (hybrid
syntactic+statistical, ~83% F-score) is the closest positive precedent for flagging particle-like directional
words from unannotated text, but it still leans on an upstream POS tagger, not zero-supervision raw distribution.

**Concrete, actionable, buildable signal (my inference, flagged as synthesis not a literature-reported result):**
frequency + shortness + closed/small neighbor-set diversity (the general grammaticalization fingerprint --
Hopper & Traugott's cline, Bybee's frequency-driven erosion account, both established diachronic-linguistics
literature, language-general not directional-specific) COMBINED with a POSITIONAL-SLOT signature (specifically:
concentrated occurrence in the post-verb / pre-clause-boundary slot, conditioned on an independently-induced
motion-verb cluster) is the most concrete, literature-adjacent candidate for a fine-grained bootstrap. This is NOT
directly reported as a combined result by any single source -- it is this drill's synthesis of the grammaticalization
literature + the VPC-detection methodology + argument-structure verb clustering, held at P~0.40 (deflated,
synthesis).

**Honest ceiling stated plainly:** distribution alone reliably answers "is this probably a function word," not
"is this specifically a directional/path marker" -- the last-mile fine subclass needs either a seed or a
post-hoc human/heuristic label. This is not a defect of the proposed design; it is a documented property of the
field going back to the foundational 1993-1998 papers.

## Angle 3 -- Neuro: is directional/path a distinct, learnable representational class? (established, mixed)

**Robust, well-established coarse dissociation:** agrammatic (Broca's) aphasia selectively impairs closed-class/
functional morphology while relatively sparing open-class content words, cross-linguistically -- one of the most
replicated findings in aphasiology. ERP work shows closed-class words elicit markedly smaller N400 than open-class
words of similar frequency. Friederici's staged neurocognitive model places function-word-driven phrase-structure
building (ELAN, 150-200ms) as an early, separable processing stage from later lexical-semantic integration --
though **ELAN's functional interpretation is actively disputed** in the literature (design-artifact critiques), a
caveat this drill flags rather than smooths over. The specific mechanistic claim behind the classic Bradley-
Garrett-Zurif "separate closed-class lexical route" hypothesis **failed to replicate** in normal subjects --
another honest caveat against over-claiming a clean, uncontested dissociation.

**A genuinely useful and more specific finding for this task: locative/spatial prepositions have their OWN
dedicated neural subclass signature, not just the coarse function/content split.** Spatial/locative prepositions
("above," "into," "up") reliably and specifically engage left inferior parietal cortex (supramarginal/angular
gyrus) -- a visuospatial-processing region -- distinct from the general frontal/temporal circuitry of generic
closed-class syntactic processing, and distinct from areas for other word types (sound-, action-, color-related).
Damage there produces selective spatial-preposition comprehension deficits (documented in posterior cortical
atrophy) that dissociate from general agrammatism. This is real, specific, positive evidence that "directional/
spatial marker" is a genuine, separately-instantiated NEURAL subclass in the brain, not merely a convenient
engineering category -- P~0.55 (established but from a smaller, more specialized literature than the coarse
function/content dissociation).

**But grammaticalization evidence shows this category is historically EMERGENT from content words, not a clean
innate primitive:** "back" derives from an Old English body-part noun; directional particles/path satellites
grammaticalize from full directional verbs cross-linguistically (Talmy's satellite typology, documented Cantonese
and English diachronic case studies). Grammaticalization's unidirectionality (lexical -> grammatical) is
uncontroversial historical linguistics. This is a genuine tension the drill does not resolve away: the category
has a real, dedicated neural home AND is historically graded/derived, not primitive.

**Developmental/L2 evidence supports "given structure, learned content, not given content":** infants as young as
8 months show early perceptual/statistical sensitivity to the functor-vs-content distinction (tracking ordering),
yet functional-morpheme PRODUCTION lags well behind (telegraphic speech) -- likely a production bottleneck, not a
comprehension one. L2/bilingual grammatical (closed-class) processing is measurably more fragile and
proficiency-dependent than lexical-semantic processing, requiring substantial experience to reach native-like
automaticity.

**Honest synthesis (this drill's own read, not a single source's conclusion):** the evidence leans toward a
"given architectural bias/floor for treating closed-class items differently (including a dedicated spatial-marker
channel), with the specific membership and fine semantics of the class learned/graded with exposure" -- neither
pure nativism nor pure blank-slate learnability is supported, and the tension (real dedicated neural home vs.
historically-derived/graded category) is left genuinely unresolved in the literature itself, not glossed as one
clean answer.

## Angle 4 -- THE CIRCULARITY RISK: do humans have an independent source? (established, directly answers the crux)

**Yes -- but via TWO half-channels that must be BOUND together, and one of the two is unavailable to a text-only
substrate.** This is the single most decision-relevant finding of the whole drill.

**Channel A (perceptual, prelinguistic, genuinely independent of syntax):** infants as young as 6-14 months
discriminate and independently categorize PATH vs. MANNER in dynamic motion events (Pulverman, Golinkoff,
Hirsh-Pasek et al. 2006-2013), forming path categories BEFORE manner categories, and this happens before the
child has any syntactic argument-structure competence to use it for. Lakusta & Landau's work shows a nonlinguistic
goal-over-source encoding asymmetry in prelinguistic event memory that later surfaces in linguistic path-expression
asymmetries -- the nonlinguistic representation PREDATES and SHAPES the linguistic category, not the reverse.
Mandler's Perceptual Meaning Analysis and Talmy's cognitive semantics both treat PATH/SOURCE-PATH-GOAL as a
conceptual primitive extracted directly from perceptual/motor experience, independent of language. This channel is
structurally, categorically unavailable to a text-only substrate -- there is no perceptual stream to extract path
concepts from independent of the words describing them.

**Channel B (prosodic/frequency, prelinguistic, also independent of syntax):** infants 8-13 months use
phonological/prosodic form (segmental + prosodic signature distinguishing real function words from nonsense
function words) to recognize the closed-class SET itself, entirely prior to syntactic competence (Shi, Cutler,
Werker & Cruickshank). This identifies "these tokens form a closed grammatical class" from FORM statistics alone,
without reference to argument-structure well-formedness judgments -- genuinely independent of the downstream
syntactic-typing use. This channel HAS a text analog: frequency + shortness + closed-inventory distributional
statistics (Angle 2's grammaticalization fingerprint).

**The honest synthesis: neither channel alone identifies "directional marker."** Channel A gives the CONTENT (path/
goal meaning-cluster exists, is perceptually real, dissociable from manner). Channel B gives the FORM-CLASS
boundary (which phonological items are closed-class). BINDING the two -- noticing the perceptually-grounded
path/goal concept recurrently co-occurs with a particular prosodically-flagged closed-class form -- is what
cross-situational learning does, and it is genuinely independent of the argument-structure-typing signal (which is
a downstream syntactic use that presupposes the category already exists, not a channel that constructs it). So:
**yes, humans have a real, non-circular bootstrap path, but a text-only substrate only has HALF of it (Channel B),
and Channel B alone is the exact channel Angle 2 shows is insufficient for the fine subclass without a seed.**

**Directly for the computational proposal:** the honest INDEPENDENT proxy available to a text-only system is
frequency + length + closed-neighbor-set-diversity + positional-slot-constraint (Channel B's text analog) --
computed as its OWN statistic over the whole corpus, NOT derived from or dependent on the argument-structure
teacher's frame-typing judgments. Using co-occurrence with an independently-induced motion-verb cluster as an
ADDITIONAL signal is weaker and risks RELOCATING rather than breaking the circularity, unless that motion-verb
cluster is itself grounded via a channel independent of the directional-marker list (e.g., verb clustering by
distributional argument-structure signature/Levin-style class, which the design already partially has available
from the sibling LCCP work, credited not re-derived).

## Angle 5 -- STRUCTURAL VERDICT: separate buildable-de-confound from honest-given-floor

**Buildable now (Rank 1, addresses VET's SPECIFIC 29349 finding):** compute a candidate closed-class/directional
set from Channel B's text analog -- frequency rank, word length, closed-neighbor-set size (type/token ratio in
slot), and post-verb/pre-clause-boundary positional-slot concentration -- over the WHOLE corpus, entirely
independent of the syntactic-frame teacher's use of any word list. Seed this candidate-set induction with a SMALL
(5-10 item), explicitly CREDITED exemplar list (home, there, up, down, into, away -- mirroring how the design
already credits Levin's classes elsewhere rather than inventing lists from scratch), then EXPAND via distributional
similarity to the seed centroid (the same Alishahi & Stevenson-style no-negative-evidence update-rule shape already
validated elsewhere in this design, applied here to CATEGORY induction rather than role-weight learning). Feed the
resulting INDUCED set (not the original hand-authored DIR_ADV/DIR_PREP list) into BOTH the teacher's frame-typing
and the f_dirpp feature. **This breaks the SPECIFIC confound VET named** -- the two consumers now draw from a set
built by an INDEPENDENT statistic (surface distributional fingerprint) rather than being IDENTICAL to a
hand-authored list feeding two consumers directly. P=0.38 (deflated, novel synthesis, capped) that this specific
re-run reproduces the negative sign AND the must-fail control still fires -- i.e., that the earlier result was
about genuine teacher-driven sign-learning and not an artifact of the ORIGINAL list's specific hand-curated
quality.

**Legitimate honest-given floor (Rank 2, do NOT chase past this):** full ELIMINATION of any seed/credited exemplar
list is NOT supported as achievable from text alone. The strongest available literature finding (Redington,
Chater & Finch) is that closed-class words are the HARDER, not easier, case for zero-seed distributional
clustering; no study found demonstrates zero-seed induction of a FINE semantic subclass (directional specifically,
vs. temporal/causal/other) without a seed or downstream human labeling. This maps onto a real, non-arbitrary
asymmetry: humans get the fine subclass by BINDING a perceptual channel (Angle 4, Channel A) that a text-only
substrate structurally lacks, to a frequency/form channel (Channel B) that Angle 2 independently shows is
insufficient alone. **The honest claim after Rank 1 is built: "learns the correct rule (sign) given a
DISTRIBUTIONALLY-INDUCED (not manually complete) directional detector, seeded from a small credited exemplar set,"
NOT "learns the whole category from zero."** This is not a cop-out -- it is the same structure the brain uses
(given architectural bias + convergent-cue binding, Angle 3's synthesis), just missing the one channel (perceptual
grounding) that is out of scope for a text-only system. P=0.65 (established: function words harder not easier for
zero-seed induction; no counter-example found) that some minimal seed remains a legitimate, brain-analogous floor.

**Speculative extension (Rank 3, exploratory, not recommended as the next build):** attempt a text-only proxy for
Channel A (perceptual path-grounding) via co-occurrence with an independently-induced motion-verb cluster (itself
grounded via distributional argument-structure clustering, not via the directional list). Flagged explicitly as
RISKING relocation of the circularity rather than resolving it, unless the motion-verb cluster's own independence
is separately verified. P=0.25 (speculative).

**Brain-check outcome, stated honestly, not pre-assumed:** MIXED, and the substrate's honest position is BETTER
than "we hand-built a list because the field can't do it" and WORSE than "children learn this fully from
distribution with no given seed." Humans do not derive the fine directional subclass from pure distribution either
(Angle 2's Redington-Chater finding, Angle 1's protracted multi-year timing, Angle 3's given-floor-plus-learned-
content synthesis) -- they succeed via a channel (perceptual path/goal grounding) that is simply not available to a
text corpus. The correct, non-self-flattering claim: a minimal credited seed is a legitimate structural analog of
the brain's given floor, and the specific circularity VET caught (identical list feeding two consumers) IS
buildable-away via an independently-computed distributional statistic -- these are two different claims and must
not be conflated when reporting the test result.

---

## Cheap decisive test

**Step 1 (free, do first):** compute the Channel-B distributional fingerprint (frequency rank, word length,
closed-neighbor-set/type-token ratio in slot, post-verb/pre-clause-boundary positional-slot concentration) for
every word type in the existing reading corpus, WITHOUT reference to the hand DIR_ADV/DIR_PREP list. This is a
static analysis pass over already-parsed data, no new architecture.

**Step 2 (build):** seed the induction with a small, explicitly credited 5-10 item exemplar set (e.g. home, there,
up, down, into, away -- overlap with, but far smaller than, the current hand list); expand via distributional
similarity to the seed centroid using the fingerprint features from Step 1 (Alishahi & Stevenson-style update-rule
shape, already validated elsewhere in this design's lineage). Produce the INDUCED candidate set.

**Step 3 (validation-only, not training):** score the induced set's precision/recall against the ORIGINAL
hand-authored DIR_ADV/DIR_PREP list, used here purely as a validation reference, never as a training signal.

**Step 4 (must-fail / can-fail control, mirrors the design-gate discipline):** re-run the induction with a
SCRAMBLED seed -- a matched-frequency/length control set of non-directional closed-class words (e.g. common
temporal/causal adverbs) substituted for the true directional seed -- and confirm it does NOT recover the true
directional set at comparable rates. This checks the fingerprint signal is doing real seed-specific work, not just
generic closed-class clustering that would grab any small function-word class handed to it.

**Step 5 (the decisive de-confound re-run, directly answers 29349):** re-run the syntactic-frame-frequency teacher
test from the prior drill, substituting the INDUCED set (Step 2's output) for the hand-authored list in BOTH the
teacher's frame-typing AND the f_dirpp feature computation. This is the test that actually answers the USER's
question.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 -- the induced set is a genuine, seed-specific recovery of the directional category, not generic
function-word clustering.** P=0.40 (deflated; novel synthesis, best-precedented piece of this drill's proposal).
**HARD-PASS:** induced set recovers >=70% recall of the hand list at >=50% precision, AND the scrambled-seed
control (Step 4) recovers <30% overlap with the true hand list. **HARD-FAIL:** induced-set recall <40%, OR the
scrambled-seed control performs comparably (>=50% of the true-seed's recovery rate) to the true seed -- meaning
the fingerprint signal is not doing category-specific work, just generic closed-class detection, and the fine
directional subclass genuinely requires the fuller hand list (this would CONFIRM Rank 2's honest floor is larger
than hoped, not merely present).

**Prediction 2 -- the de-confounded re-run reproduces genuine teacher-driven sign learning.** P=0.38 (deflated,
this is the test that directly answers the USER's framing question). **HARD-PASS:** using the INDUCED set (not
the original hand list) for both teacher and feature, w[f_dirpp] remains negative-signed across seeds under the
syntactic-frame teacher (replicating the -2.47-family result), AND the pre-registered must-fail control (cue-
degradation / membership-randomization) still fires -- i.e., the learned weight measurably degrades when the
induced set's reliability is synthetically corrupted. **HARD-FAIL:** sign flips positive, or the must-fail control
stops firing when run on the induced set -- this would mean the ORIGINAL result depended on the hand list's
specific curated quality (e.g., its precision on the exact test corpus) rather than on genuine teacher-driven
learning, a materially different and more damaging finding than the confound VET already flagged.

**Prediction 3 -- the induced set generalizes the fix beyond the original hand list's coverage (a positive test of
"more learned than before," not just "as good as before").** P=0.30 (deflated, exploratory, most speculative
prediction in this drill). **HARD-PASS:** the induced set includes correctly-directional words ABSENT from the
original hand-authored list (spot-checked manually against a linguist-style judgment, small sample n>=10), showing
the induction adds coverage the hand list did not have. **HARD-FAIL:** induced set is a strict subset of the hand
list with no novel correct members -- would mean this is at best a de-confounding RELABELING of the same
information, not a genuine expansion of learned coverage, and the honest claim should downgrade from "learns an
expanded detector" to "learns a re-derived version of the same list."

---

## Cross-thread synthesis

Directly resolves the fork flagged in the 07-19 BACKUP's SESSION ARC RESOLUTION block (atom 29349): "(A)
DE-CONFOUND -- learn the directional detector distributionally (removes the hand-scaffold)." This drill's verdict
is that (A) is buildable but must be reported precisely: it de-confounds the SPECIFIC shared-detector circularity
(Rank 1, testable via Prediction 2), while a small credited seed remains a legitimate, brain-analogous given floor
(Rank 2) -- NOT the "learns the whole rule, detector included, from scratch" framing in the task's own opening
line, which this drill's Angle 4 finding (the brain uses a perceptual channel unavailable to text) shows is not an
achievable honest target for a text-only substrate. This connects to and refines
`research_argument_adjunct_subcat_hard_residual_brain_drill_2026-07-19.md` (subcat-frame-frequency + directional-PP
diagnostic mechanism) and to the atom-29347/29348/29349 sequence (semantic teachers fail to teach structural rules;
the syntactic teacher succeeds at the sign but was confounded on the detector). It also connects to
`research_reading_pedagogy_craft_lit_scan_2026-07-19.md`'s concrete-vocabulary grounding gap (Harnad/dual-coding) --
the SAME structural asymmetry (text-only substrate lacks a perceptual grounding channel humans use) surfaces here
independently, in a completely different sub-problem (directional-category induction vs. concrete-noun grounding),
which strengthens (without proving) the case that "text-only substrate structurally lacks perceptual grounding" is
a recurring, real category of honest ceiling for this project, not a one-off excuse.

**Explicitly out of scope for this drill:** whether the induced-set approach should be extended to OTHER
closed-class subtypes (temporal, causal connectives) is a natural follow-on but not tested here -- the fingerprint
features (frequency/length/position) are claimed as language-general (grammaticalization theory), so the same
induction method likely transfers, but this drill only validates it for the directional/path case named in the
task.

## Substrate-product implications

Build-priority and honesty framing, not a publication angle. If Predictions 1+2 both HARD-PASS, the substrate gets
a genuinely de-confounded version of the 29349 result -- a real, reportable "the substrate learned this rule from
an independently-induced category, not a fully hand-installed one" claim, closing the open fork from the 07-19
BACKUP cleanly and honestly. If Prediction 1 HARD-FAILs but Prediction 2 still HARD-PASSes on the (smaller,
lower-recall) induced set, that is still a meaningful partial win -- report it as such, do not inflate a partial
recovery into "learned the whole category." If Prediction 2 HARD-FAILs, the honest and IMPORTANT finding is that
the original 29349 sign-learning result was more fragile/hand-list-dependent than previously reported, which
should prompt a re-audit of that atom's claimed strength (a genuinely bad outcome to catch now rather than let
stand as banked). Either way, this drill's Rank-2 finding (a small credited seed is a legitimate honest floor, not
a violation of learn-like-a-human) should be adopted going forward as the calibrated framing for ANY future
closed-class-category-induction work in this project -- eliminates a recurring temptation to over-claim "fully
from scratch" for categories where the literature shows humans also rely on a given floor.

---

## Citations (verified count)

**~35 distinct primary/named sources**, freshly verified via live web search this session across four parallel
lit-scans (each source individually verified by its originating sub-agent; none recalled-from-training without a
live-search citation): Bowerman & Choi 1991/1994/2001/2003 (cross-linguistic spatial semantics); Choi 2006
(language-specific input); Landau & Jackendoff 1993 (BBS, what/where dissociation); Gentner & Kurtz 2005
(relational category development); Slobin 1996/2003 (thinking-for-speaking); Frontiers 2019 spatial-terms
acquisition review; Roadmap 0-60-months developmental summary; multi-lab replication on infant path/goal
anticipation (2019); Redington, Chater & Finch 1998 (Cognitive Science, distributional category induction);
Clark 2003 / Stratos et al. 2016 (arXiv:1804.07849, unsupervised POS induction); Hopper & Traugott 2003
(grammaticalization); Bybee (frequency/erosion account); verb-particle-construction detection literature
(deep lexical acquisition of VPCs, learning VPC meaning from corpora); Riloff-tradition bootstrapping / seed
selection literature; automatic verb classification via argument-structure distribution; Bradley, Garrett &
Zurif 1980 (lexical-status hypothesis) + its documented failed replication; agrammatism/closed-class-deficit
literature (multiple, cross-linguistic); Friederici 2002/2011 (staged neurocognitive model, ELAN) + ELAN
critical-review literature (disputed functional interpretation); Amorapanth, Widick & Chatterjee 2009 (neural
basis for spatial relations); locative-preposition parietal-cortex literature + posterior-cortical-atrophy
spatial-preposition deficit case studies; open/closed-class N400-amplitude ERP literature; etymonline "back"
(grammaticalization example); Chor (Cantonese directional particles, grammaticalization); directional "out of"
in the history of English (Journal of Germanic Linguistics); functional-morpheme-in-acquisition literature
(8-month functor sensitivity, production lag); heritage-bilingual grammatical-processing N400/P600 literature;
Pulverman, Golinkoff, Hirsh-Pasek et al. 2006-2013 (preverbal path/manner discrimination); Lakusta & Landau
(goal/source preverbal event representation, Cognitive Science 2012); Mandler (Perceptual Meaning Analysis,
image schemas); Talmy (cognitive semantics, Path as conceptual primitive, satellite-framing typology); Yu & Smith
/ Smith, Suanda & Yu (cross-situational statistical word learning); narrative-input spatial-preposition learning
at 28 months; Shi, Cutler, Werker & Cruickshank (prosodic/segmental function-word recognition in infancy); Werker
& Gervain (overview).

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: novel-synthesis capped at P<=0.50 throughout. The unified verdict
(buildable specific-confound de-confound + legitimate honest-given-floor, with the floor's SIZE and REASON both
identified) is this drill's own synthesis across four independently-sourced literatures, held at P=0.38 for the
de-confound re-run succeeding cleanly (Prediction 2) -- the low-mid end of the calibration band, because no single
cited source proposes this exact induction-plus-re-run design; each component literature individually sits higher
(P~0.55-0.65) as reported per-angle above. The honest-given-floor claim (P=0.65) is the highest-confidence claim in
this drill because it rests on an explicit, repeated NEGATIVE finding in the literature (function words are harder,
not easier, for zero-seed distributional methods) rather than an optimistic extrapolation.

---

## VERDICT (one line)

**The specific circularity VET flagged in atom 29349 (an identical hand-authored list feeding both the teacher and
the feature) is buildable-away via an independently-computed distributional fingerprint (frequency + length +
closed-neighbor-set + post-verb positional-slot statistics) seeded from a small credited exemplar set and expanded
distributionally -- but full elimination of any seed is not an honest target, because the literature shows humans
themselves resolve the fine directional/path subclass by binding a perceptual channel (prelinguistic path/goal/
manner discrimination) that a text-only substrate structurally lacks to a frequency/form channel that, alone
(per Redington-Chater), is demonstrably insufficient for this fine a subclass; the correct claim after the
de-confound build is "learns the rule given a distributionally-induced, seed-expanded detector," not "learns the
whole category from zero," and this is a legitimate brain-analogous floor, not a hand-rules violation.**
