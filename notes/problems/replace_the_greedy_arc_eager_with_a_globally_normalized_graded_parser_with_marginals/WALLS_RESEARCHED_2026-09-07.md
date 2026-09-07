# WALLS RESEARCHED (biology-first) -- the globally-normalized parser + the who-did-what chain

Owner directive: "research all walls" + "prototype the organ and the full 100% brain foundational chain." Method:
4 parallel biology-first literature drills, each LEADING WITH THE BRAIN, then a prototype of the fix. Every wall is
resolved to a MECHANISM (PINNED vs OUR-INVENTION), a CEILING-vs-GAP verdict, and a concrete glass-box build.

---

## WALL 1 -- the two-valid same-type residual (67% of who-did-what errors) : how does the brain pick which of two animate NPs is the patient?

**Brain mechanism (ranked).** (1) DOMINANT: verb-specific event knowledge + IMPLICIT CAUSALITY (Garvey-Caramazza
1974; Hartshorne-Snedeker 2013 -- IC is thematic/event-structure knowledge, not a surface heuristic; McRae/
Spivey-Knowlton/Tanenhaus 1998 thematic-fit norms). (2) Centering discourse salience (Grosz-Joshi-Weinstein 1995:
Cf subject>object, backward-looking-center continuity) -- load-bearing for the cross-clause/pronoun half.
(3) Information-structure / givenness (Gundel 1993; Prince 1981: given/definite/pronominal -> topic/agent; new/
indefinite -> patient). (4) Competition Model (Bates-MacWhinney): the integration architecture -- cues combined by
cue VALIDITY; in English word-order dominates, animacy weak, so when both NPs are animate the residual cues decide.
PINNED: anticipatory eye-movements to the IC referent BEFORE the pronoun (Pyykkonen-Jarvikivi 2010); N400 graded by
thematic fit; thematic-role-reversal -> P600 "semantic illusion" (Kim-Osterhout 2005; Kuperberg 2007).

**Ceiling vs gap.** NOT a genuine ceiling -- the dominant levers are static glass-box assets (IC norms exist:
Ferstl 2011 ~300 verbs, Hartshorne 2013 ~1000; thematic-fit -> VerbNet/FrameNet + McRae norms; givenness off
determiners/pronouns; salience off grammatical role + mention recency). The irreducible residual = Winograd-schema
cases where assignment hinges on real-world plausibility no verb-norm encodes ("...because it was too big") -- a
MINORITY.

**PROTOTYPED + the sharpened finding (`exp_full_brain_chain_v1`).** I built the argument-role competition organ
(Centering salience + givenness + word-order + locality + thematic-fit + animacy, integrated as a Competition-Model
logistic = additive cue activation -> softmax, gated by the parser marginal). RESULT: it does NOT beat the strong
labeled reader at the SENTENCE level (full UD-EWT n=1235: 0.8785 blanket -> 0.8575 full chain, delta -0.021; twin
with the top-down cues shuffled -0.024 -- i.e. FUSION == TWIN, the top-down cues are not load-bearing), and the
learned cue VALIDITIES tell us exactly why -- the sentence-internal discourse cues carry near-ZERO validity
(givenness 0.01, salience 0.157) while the weight is on syntax (1.70) / word-order (0.85) / locality (0.72), which
the labeled reader already has. Two-valid recovery 14/100. **Mechanistic reason (airtight): the two-valid cases are two GIVEN
entities (two proper nouns / pronouns), so sentence-internal givenness cannot discriminate them; the discriminating
signal is DISCOURSE SALIENCE -- which given entity is the current CENTER -- which requires PRIOR-SENTENCE context,
plus the IMPLICIT-CAUSALITY verb norm.** Neither exists in a sentence-level parser. So the two-valid residual is
NOT a parser wall and NOT resolvable by sentence-internal cues; it is the DOCUMENT-LEVEL recurrent discourse loop +
an IC-norm asset. Located, from the who-did-what side, consistent with the wall-map's dominant finding.

**Build (the last organ, out of THIS problem's scope):** (a) acquire a static IC-norm verb lexicon (Hartshorne/
Ferstl; pre-authorized offline asset); (b) run the argument-role competition at DOCUMENT level with a discourse-
salience prior = the previous sentences' center (Centering Cf + coref recency) -- the recurrent top-down loop.

---

## WALL 2 -- register / OOD attenuation (patient reliability AUC 0.77 in-domain -> 0.55 on QA-SRL)

**Brain mechanism.** Register-invariance comes from (a) ABSTRACT hierarchical structure factored from lexical
statistics (structural priming transfers across words/languages -- Bock 1986; Hartsuiker 2004), (b) LEXICALIZED
argument frames that are register-stable ("give" takes a recipient in tweets and technical prose alike; Trueswell
1993; Garnsey 1997), and (c) error-driven expectation ADAPTATION to recent input (Fine-Jaeger 2013; Kleinschmidt-
Jaeger 2015 ideal-adapter; Chang-Dell-Bock 2006 = Rescorla-Wagner). All PINNED.

**Why our scorer is brittle.** Its features -- word identity, POS, signed distance, tokens-between -- ARE the
register-conditional distributional statistics that shift OOD. The perceptron memorizes P(arc | surface) calibrated
to the training register, so OOD the margin collapses toward chance. It never represents the register-INVARIANT
object (abstract structural relation + verb argument frame): all statistics, no grammar.

**Ceiling vs gap.** A fixable representation/adaptation choice, NOT a ceiling. **Build:** add (i) lexicalized
subcategorization-frame features backed off to verb clusters (OOV verbs inherit a frame), (ii) delexicalized
abstract structural features (head-POS x dep-POS x dir x dist-bucket, valency-so-far), (iii) a per-document online
Rescorla-Wagner adaptation of a low-dim ABSTRACT-feature layer (self-supervised on high-margin anchor arcs), base
weights frozen (auditable delta). Static abstraction + online cue-reweighting = the two brain mechanisms.

---

## WALL 3 -- the buried-attachment slice (11%) + the small attachment gain : what does the brain encode that a surface arc-factored scorer lacks?

**Brain mechanism.** LEXICALIZED ARGUMENT STRUCTURE / verb SUBCATEGORIZATION (valency) is the core of the mental
lexicon (Levin 1993; VerbNet/PropBank/FrameNet as cognitive frame inventories); the verb PROJECTS typed argument
slots and pre-activates them. Structure is built by hierarchical headed combination (Merge; cortical tracking of
hierarchy -- Ding-Melloni 2016; Pallier 2011; Nelson 2017), unified from stored frames in Broca (Hagoort's
Memory-Unification-Control; Friederici's dorsal syntax network). PINNED.

**The single biggest lack.** The arc-factored model scores each (head,dep) arc INDEPENDENTLY from surface features
-- it has no representation of which slots a head licenses, whether a candidate fills the slot's type, or whether
core slots are saturated. A head's arcs must JOINTLY complete a frame; that inter-arc constraint is exactly the
discarded signal. When the gold head is far / low-frequency-with-the-dep, surface features bury it; valency re-ranks
by STRUCTURAL LICENSING (an open, type-matched slot becomes expected regardless of distance).

**Ceiling vs gap.** Buildable glass-box: VerbNet/PropBank (static) + a subcat lexicon MINED from modern UD-EWT
(per lemma: relation-multiset counts + slot-filler type distributions). Ceiling: sense-dependent frames (the WSD
wall), rare-verb tail. **Build:** add to the arc score -- frame-slot compatibility P(rel|lemma), selectional type
match P(type(dep)|slot), valency saturation, frame completeness -- as a RE-RANKING pass over the arc-factored
k-best (breaks strict arc-factoring; = Hagoort MUC unification). Note: the substrate ALREADY has
`data/frontend_assets/verb_subcat_frames_ud_ewt.json` -- reuse it.

---

## WALL 4 -- incrementality + the top-down predictive loop (the batch deviation + the missing organ)

**Brain mechanism.** Parsing is INCREMENTAL and PREDICTIVE: anticipation of the upcoming theme given verb+context
(Altmann-Kamide 1999), processing cost = surprisal / entropy-reduction over the parse distribution (Hale 2001;
Levy 2008), within a hierarchical PREDICTIVE-CODING loop where higher levels (situation/discourse model) send
predictions down and lower levels send prediction-errors up (Friston; Kuperberg-Jaeger 2016), read out as N400
(meaning prediction-error; Kutas-Federmeier) and P600 (syntactic revision). The situation model FEEDS BACK to
constrain syntactic/role commitment in real time (constraint-satisfaction: MacDonald 1994; visual-world immediacy:
Tanenhaus). PINNED.

**What batch loses.** Our parser is exact but BATCH + bottom-up + no feedback. Batch is FINE for the confidence
signal (it sees the whole sentence -> the marginal is a superset). What is genuinely lost is (a) a faithful
INCREMENTAL difficulty signal (true Hale surprisal, word-by-word -- our upgrade C used a static whole-sentence
entropy), and (b) TOP-DOWN disambiguation: which reading the situation model expects -- exactly the two-valid case.
**The recurrent top-down loop is the correct single highest-leverage build** (it lifts parser + meaning + temporal
at once -- the wall-map's dominant finding); the minimal version wires a discourse-salience / next-mention
expectation prior over entities (Centering + recency + givenness + IC) into the parser's role competition. This is
literally WALL 1's build -- the two are the SAME organ seen from two sides.

---

## SYNTHESIS -- is the chain 100% brain-foundational, and where exactly is it not?

| stage | brain-foundational? | status |
|---|---|---|
| POS tagger (Collins perceptron) | YES (error-driven cue competition) | landed |
| graded parser: exact Matrix-Tree marginal + 2nd-best (this problem) | YES (globally-normalized distribution over parses; Hale entropy) | prototyped, exact |
| exact decode (Chu-Liu/Edmonds MAP) | YES (more faithful than greedy) | prototyped |
| valency / subcat unification (WALL 3) | YES (Hagoort MUC) but NOT YET BUILT here | named build; asset exists |
| argument-role competition organ (WALL 1) | YES (Competition Model) -- sentence-internal cues insufficient | PROTOTYPED = located negative |
| register adaptation (WALL 2) | the brain adapts; we do not | named build |
| recurrent top-down loop (WALL 4 = WALL 1 document-level) | the brain has it; we do NOT | THE missing organ |

**Two honest, precisely-located deviations remain, both DIFFERENT organs (not the parser):**
1. **Lexicalized valency features + register adaptation** (Walls 2+3) -- the SCORER's features are surface-only;
   the brain uses lexicalized argument frames + online adaptation. Buildable glass-box; asset partly on disk.
2. **The recurrent DOCUMENT-LEVEL top-down discourse loop + an IC-norm lexicon** (Walls 1+4) -- the two-valid
   residual needs the discourse CENTER from prior sentences + implicit-causality norms, neither available to a
   sentence-level parser. This is the wall-map's dominant finding, now confirmed and quantified from the
   who-did-what side (the prototype's near-zero sentence-internal discourse-cue validities are the proof).

The parser this problem owns is brain-foundational in STRUCTURE + DECODE + the graded posterior; the residual is
NOT in the parser but in two named upstream/parallel organs, each PINNED, each a separate build. Nothing here is a
ceiling except the Winograd-schema world-knowledge minority.
