# Research: language-ingest scoping for the glass-box-LM capstone -- what must be ingested, how much, and glass-box how

Date: 2026-07-05. Owner: Research. Type: scoping/design drill (no dispatch, per task instruction). Level-2 operational
drill on EXISTING findings (2x discipline) -- most of the mechanism-level lit (Levelt/Dell/Garrett, resonator networks,
competitive queuing, theta-gamma phase-slot coding) was already gathered TODAY by two sibling drills
(`research_5x_drill_generation_spec_and_brain_mechanism_2026-07-05.md`,
`research_substrate_native_language_path_5x_angle5_2026-07-05.md`) and is reused, not re-derived. NEW external lit-scan
in this pass targets exactly the gaps those drills did not cover: (a) developmental language-acquisition stage/scale
numbers, (b) symbolic/grammar-based NLG engineering precedent for the glass-box question, (c) morphological rule-count
and vocabulary-coverage scale numbers. 3 parallel Sonnet sub-agents dispatched for these three angles (generic academic
query terms only, per query-privacy discipline); results synthesized below.

Method: `python tools/orchestrator/research_field_advisor.py` run at cycle start (physics-field advisor; confirmed no
adjacent physics field bears on this architecture/linguistics question -- correctly orthogonal, not skipped). Internal
scour: read end-to-end on 6 same-day M3/decoder/generation notes + the strategic-pivot note that CLOSED the old
statistical-LM track + director backup + brain-component inventory; direct filesystem verification of 6 existing
NLP-primitive cells' metrics.json (POS tagger, dep-parser, WUG morphology test, lexicon emission, frame-slot planner)
plus their source files (corpus provenance: NLTK-bundled PTB sample, Universal Dependencies treebank, synthetic WUG
stems) to ground "what's already ingested" in verified numbers, not inference.

---

## HEADLINE

**The USER's flag is correct in spirit (fluent language needs more than facts) but the gap is narrower and cheaper
than "a large ingest" implies, and it is NOT one ingest -- it is four small, independently-provable layers, three of
which already have a working substrate-native mechanism proven at TOY scale, and the fourth (function words +
recursive grammar) is the only genuinely unbuilt, non-trivial piece.** Concretely: (1) the LEXICON layer is
essentially already done -- the 177,899-name ConceptNet/taxonomy table the native decoder already reads from IS a
vocabulary, just uncurated and without morphological features; (2) MORPHOLOGY is proven AS A MECHANISM (WUG test
HARD_PASS: substrate infers a present->past rule from 1-3 examples and generalizes to novel stems at 1.000) but only
ONE of English's ~8-10 core rules has been built, and it is not wired into the generation decoder; (3) SYNTACTIC
COMBINATORICS (frame-and-slot ordering) is the best-proven piece -- a native block-local decoder factors bound
propositions into an exact-ordered token sequence (1.000 to D<=26 slots, V<=1024), independently cross-validated
against Levelt/Garrett psycholinguistics, competitive-queuing, and theta-gamma phase-slot neuroscience (4 of 5
literatures converge on the SAME abstraction: position is a bound factor, not invented at decode time); (4) FUNCTION
WORDS + grammar beyond fixed-slot order (determiners, prepositions, auxiliaries, recursive embedding, agreement) is
the one layer that is genuinely unbuilt -- no cell anywhere in the corpus has attempted it. The MINIMUM ingest for a
first fluent grounded sentence is near-zero new ingest (a common-word frequency filter over the existing name table +
a ~20-30-entry ConceptNet-relation-to-verb-phrase lookup table -- both glue, not research). The ingest for BROAD
conversational capability is a real, substantive, multi-week build (function-word closed class, full morphological
rule set + exception list wired into decoding, recursive grammar beyond fixed-slot templates) and is honestly the
capstone, not close. Developmental acquisition literature (below) independently corroborates the STAGING: human
children also go through a telegraphic (content-word, fixed-order, no-morphology, no-function-word) stage before
grammatical morphemes and function words are layered in -- the substrate today sits at the mechanism-analog of that
exact stage, which is a legitimate cross-check on the sequencing (not a claim the substrate "is" a toddler; the
parallel is at the level of production ARCHITECTURE, per the mechanism-analog-is-not-task-analog discipline).

---

## 1. WHAT must be ingested beyond ConceptNet facts -- four layers, rough scale, what's already proven

### Layer A -- VOCABULARY / LEXICON (concept -> surface word FORM)

**Already have, verified off-disk:** the native decoder's filler codebook (`data/gen_decoder_gsbc_fillers/
gsbc_expand2x_pool_v1.npz`) traces through `concept_rows` to the master `bge_large_v2_name_177899_54f7cf6a.npz`
table's `id_order_json` field -- 177,899 REAL name strings (ConceptNet-derived `CN_*` entity names + `T1/T2` math-
taxonomy atoms), hand-inspected this week by a sibling drill. This is a real lexicon in the weak sense (concept-id
<-> surface string), already the decoder's vocabulary source. It is NOT yet a lexical entry in the linguistic sense
(no POS tag, no inflectional class, no frequency rank, many entries are Latin-binomial or obscure ConceptNet nodes
unreadable as "common language" -- the "willet-shorebird problem").

**Gap + scale, now grounded with verified lit-scan numbers (Section 6):** curating this into a common-word functional
vocabulary is a FILTER, not an ingest -- a one-time frequency/regex pass over 177,899 existing names down to a few
hundred-to-low-thousand common-word entries. Frequency-coverage curves for English are well-established and steep
(Zipfian): the top 100 words alone cover ~48-50% of running text tokens (Penn-Treebank-derived figure, cross-corpus
stable); the top 1,000 cover ~75-80%; the top 2,000 (General Service List scale, West 1953) cover ~80-87%; Nation
(2006, *Canadian Modern Language Review*) establishes 6,000-7,000 word families for ~98% coverage of spoken text and
8,000-9,000 for ~98% of written text (novels/newspapers) -- these are the well-established "comfortable fluency"
thresholds, an order of magnitude above the "functional minimum" and two orders below "full adult vocabulary." The
ConceptNet relation vocabulary itself is already small and enumerated in-repo (`tools/substrate_conceptnet_ingest_v1.py`
lists ~20-30 relation types: IsA, PartOf, HasA, UsedFor, Causes, HasProperty, AtLocation, CapableOf, MadeOf,
DerivedFrom, RelatedTo, Synonym, Antonym, MannerOf, MotivatedByGoal, ReceivesAction, CausesDesire, DistinctFrom,
...). A relation-to-natural-verb-phrase lookup table (AtLocation -> "is in/at"; CausesDesire -> "makes you want"; IsA
-> "is a") is therefore a ~20-30-row table, not a corpus.

**Full conversational scale (capstone, far):** adult receptive vocabulary is now best-anchored by Brysbaert, Stevens,
Mandera & Keuleers (2016, *Frontiers in Psychology*, N=220,000+ crowdsourced) at **~42,000 lemmas / ~11,100 word
families at age 20**, rising to ~48,200 lemmas / ~13,400 word families by age 60 -- this is the field's best-powered
modern re-estimate and resolves much of the older 20,000-40,000-and-up variance as an artifact of counting lemmas vs.
word families vs. inflected forms. Building EITHER number with real morphological/POS metadata per entry (not just a
bare name string) is a genuine ingest job that has not been started at scale. The only existing precedent at real
corpus scale is the POS tagger cell (below), which used a TINY sample (NLTK's bundled Penn Treebank excerpt: 3,131
train sentences / 20,039 tokens / 46 tags -- roughly 5% of the full ~1M-word WSJ Treebank), not a production-scale
tagged lexicon.

### Layer B -- MORPHOLOGY (word-form assembly: inflection, tense, agreement)

**Already proven AS A MECHANISM, verified off-disk:** `exp_lex_wug_test_cpu_v1` -- HARD_PASS, 3-shot=1.000,
1-shot=1.000: infers a present->past transformation (a literal algebraic vector-transform `R`, inferred by averaging
a few present/past example pairs) and applies it correctly to NOVEL, never-seen stems. This is genuine rule-based
(dual-route, Pinker/Prince-style) morphological generalization, substrate-native, and mechanically inspectable (you
can read off which rule `R` fired -- no statistics, no next-token probability).

**Gap + scale, verified by lit-scan (Section 6):** only ONE of English's core productive inflectional rules has been
built (present->past), tested on SYNTHETIC stems in isolation, and it is NOT wired into the generation decoder's
Stage C (cleanup today is a frozen table lookup, not a rule-application step). English is a morphologically SIMPLE
language: the well-established textbook count is **exactly 8 inflectional morphemes/rules** (plural -s, possessive
-'s, 3rd-person-singular present -s, past -ed, past participle -en/-ed, present participle -ing, comparative -er,
superlative -est) -- not "8-10," the field's own count is precisely 8. The exception list is likewise small and
well-cited: Pinker's own figure (*Words and Rules*, 1999) is **160-180 irregular verbs** in productive adult use
(pedagogical sources converge on ~150-200; corpus-trawled counts including archaic/rare forms balloon to ~680, but
that is not the dual-route-relevant "listed" set). Irregular plural nouns are a genuinely smaller, less-canonically-
counted class: a core non-productive vowel-change set of just ~7-8 items (foot/feet, tooth/teeth, mouse/mice,
man/men, woman/women, goose/geese), ~3 -en plurals (ox/oxen, child/children), plus a longer but optional tail of
Latin/Greek loan-plurals (cactus/cacti) that often have regular alternatives -- dozens, not hundreds, with no single
canonical total in the literature (a genuine, minor gap, honestly flagged). **This is, numerically, the CHEAPEST of
the four layers** -- 8 algebraic rules plus a ~150-200-entry hand-curated exception list, not a corpus, and the
mechanism to build each rule (average a few example pairs, per the WUG cell -- directly the Berko 1958 "Wug test"
paradigm, which found 97% of children age 5+ correctly generalize a novel plural to an unseen nonce word, the
original empirical proof that rule-application, not rote memorization, is at work) is already proven.

**Cross-linguistic contrast (context, not a build target):** English's near-zero morphology is the favorable end of
a real range -- a single Finnish noun has a theoretical paradigm of ~2,200-2,249 inflected forms (case x number x
possessive x clitic combinations; the commonly-cited example "kauppa" = 2,249), though corpus studies show only
~1-2% of that theoretical space (~27.6 forms/noun on average) is actually attested in use -- itself a Zipfian
sparsity finding parallel to the vocabulary-coverage curves below. This is cited only to calibrate how favorable
English's ~8-rule system is for a first build; it is not a claim the substrate needs Finnish-scale morphology.

### Layer C -- SYNTACTIC / COMBINATORIAL PATTERNS (how words order into phrases)

**Already have, strongest-proven piece, verified off-disk:**
- Comprehension direction: `exp_pos_tagger_ptb_substrate_cpu_v1` HARD_PASS (tag-acc 0.9066, 46 tags, real NLTK-PTB
  sample, substrate associative lexicon + suffix backoff); `exp_depparse_discriminative_cpu_v1` MIDDLE_BAND (UAS
  0.735, 24,444 real dependency arcs, Universal Dependencies treebank via `_ud_loader.load_conllu`). Both are
  substrate-only (no LLM), on REAL annotated corpora, at small (toy-to-modest) scale.
- Generation direction: `exp_substrate_response_planner_frame_slot_composition_v1` HARD_PASS (frame=0.912,
  slot=1.000, 25 frames x 5 roles x 20 fillers/role, toy scale) and the newly-LANDED
  `exp_generation_decoder_gsbc_native_blocklocal_v1` -- exact-ordered token recovery = 1.000 to D<=26 slots at
  V<=1024 per slot, on the REAL native GSBC encoder geometry (not a synthetic stand-in). Design lock (verified
  empirically, not a choice): a bound term MUST be exactly F=2 factors (`bind(position_role, filler)`) -- F=3 collapses
  to 0.217, F=4 to 0.000. Position is therefore carried AS a role-slot factor, never a third dimension or a decode-time
  heuristic.
- Cross-field validation (already gathered, reused not re-derived): 4 of 5 independent literatures (systems/cognitive
  neuroscience -- competitive queuing, theta-gamma phase-slot coding; psycholinguistics -- Levelt/Garrett frame-and-
  slot, lemma/lexeme dissociation; VSA/HDC theory -- resonator-network role-filler binding, the field's actual
  mainstream answer, not a fringe pick) independently hand-derive the SAME abstraction: position-as-bound-factor,
  recovered by iterative competitive/resonant readout, content and position separated until late. Modern ML diverges
  (autoregressive chain-rule decoding) but its own set-to-sequence literature (Vinyals 2016; Slot Attention 2020)
  confirms "impose order on an order-free compositional representation" is itself an OPEN problem there too -- not an
  established better answer we are ignoring.

**What this buys:** ordered recovery of up to 26 CONTENT-word slots in a pre-specified FIXED frame -- telegraphic
order (subject-verb-object and simple extensions), not recursive grammar.

**Gap + scale, verified by lit-scan:** function words (determiners, prepositions, auxiliaries, pronouns) are a SMALL
closed class in English -- well-established figure ~150-300 word TYPES total, essentially non-productive (English
does not coin new prepositions or auxiliaries the way it coins new nouns) -- but they carry wildly disproportionate
weight in running TEXT: despite being <0.1% of distinct word types, function words account for roughly HALF of all
word-token occurrences in running text (directly consistent with the top-100-words ~48-50% token-coverage figure
above, since the two sets heavily overlap). NOTHING in the corpus attempts them or attempts recursive embedding /
agreement-driven word choice. This is real, unbuilt work, though numerically still a SMALL lexicon (hundreds of
entries) -- the hard part is the GRAMMAR governing when/how they attach (agreement, obligatory-context selection),
not the vocabulary size.

### Layer D -- COMMON PHRASINGS (relation -> idiomatic verb-phrase mapping)

This is really the small enumerable table described in Layer A (the ConceptNet relation vocabulary is already
~20-30 closed-class relation types; each needs exactly one canonical natural-language verb/phrase gloss). Not a
separate ingest -- a lookup table, buildable in an afternoon, already scoped as step 5 of the proposed
`exp_generation_grounded_fact_utterance_v1` cell (angle5 note, not dispatched).

### MINIMUM ingest for a first fluent grounded sentence vs. broad conversational capability

| | Minimum (first grounded utterance) | Broad conversational (capstone) |
|---|---|---|
| Vocabulary | Filter existing 177,899-name pool to ~hundreds-low-thousands common words (glue, ~0 new ingest) | Tens of thousands of word families WITH morphological/POS metadata (real ingest, not started) |
| Morphology | 0 rules required (content words emitted in citation form) OR reuse the 1 proven WUG rule if a tensed sentence is wanted | ~8-10 core rules + ~150-200-entry irregular exception list, wired into decode (mechanism proven, not built at scale) |
| Syntax | Reuse existing native block-local decoder as-is (D<=26, V<=1024, fixed SVO-style frame) | Function-word closed class (~150-300 entries, unbuilt) + recursive/agreement grammar beyond fixed-slot (unbuilt, no cell has attempted it) |
| Phrasings | ~20-30-row relation->verb-phrase table (glue) | Same table, extended with register/idiom variants (small, optional polish) |
| Effort | ~100-150 lines of glue + a manual curation pass, CPU-local, minutes | Multi-week build; genuinely the capstone |

---

## 2. GLASS-BOX vs LLM ingestion -- the inspectable representation of "knowing a language"

**Yes, structurally and inspectably, and this is not a proposal -- it is already the substrate's existing
architecture, proven in isolated pieces:**

- **Lexicon** = a literal name-string table (`id_order_json`), not a distributed embedding matrix. Every "word" the
  substrate can emit is a readable string keyed by a concept-id; you can print the entire vocabulary.
- **Morphology** = an explicit ALGEBRAIC TRANSFORM per rule (the WUG cell's `R`, inferred by averaging a handful of
  example pairs) plus a short LISTED exception table for irregulars -- textbook dual-route morphology (Pinker &
  Prince 1988). Every inflected form traces to "rule R fired" or "exception-list lookup," never a next-token
  probability. This is categorically different from an LLM's morphology, which is an emergent, non-enumerable
  byproduct of subword statistics.
- **Grammar/frame** = the block-local decoder's Stage B: position is a BOUND FACTOR (`bind(position_role, filler)`),
  not a learned attention weight. Every slot's content is one literal unbind operation on one specific bound
  structure, auditable step by step (which unbind produced which token, and its cleanup cosine) -- faithful by
  construction, not observed after the fact.
- **Combination/search** = Stage A resonator factorization -- iterative algebra (unbind + cleanup + explaining-away
  peel-off) recovering the D role-filler tuples from a superposed bound vector. This is a search procedure over a
  known algebraic structure, not a hidden state evolving through billions of opaque weights.

So the inspectable representation of "knowing a language" in this substrate decomposes into exactly four objects: (1)
a printable lexicon table, (2) a small set of algebraic morphological transforms + a short exception list, (3) a set
of frame templates with bound positional slots, (4) the bind/unbind/resonator algebra connecting them. None of it is
opaque next-token statistics; all four objects can be inspected, edited, and unit-tested independently of the whole.
This is the direct grounding for calling the substrate's generation glass-box: not an aspiration, a description of
already-built pieces that merely need to be wired together at a larger, curated scale.

**External engineering precedent (verified by lit-scan):** the classic pre-neural-LM natural-language-generation
(NLG) pipeline (Reiter & Dale 2000) -- document/content planning (content determination + document structuring, a
symbolic tree of communicative goals) -> microplanning (lexicalization, referring-expression generation, aggregation,
a symbolic sentence-plan feature-structure) -> surface realization (syntax + morphology, a syntactic
tree emitting linear text) -- is EXACTLY this kind of structured, symbolic, inspectable architecture: every stage's
data structure is a symbolic object (tree or typed feature structure), every micro-decision a discrete rule firing,
traceable end to end. It long precedes and continues to coexist alongside statistical/neural generation in
narrow-domain deployed systems.

**Scale precedent, verified with hard numbers where the literature reports them:** broad-coverage symbolic
realizer/grammar projects need roughly **10^4 lexicon entries and 10^2-10^3 grammar rules/tree-templates** --
concretely, COMLEX Syntax has ~38,000 headwords with full subcategorization features; the LinGO English Resource
Grammar has ~10,500-35,000 lexical entries expanding via 59 lexical rules, with a ~600-4,000-type grammar hierarchy;
XTAG's lexicalized grammar has 1,226 elementary trees, ~37,000 syntactic-lexicon entries, and 317,000 fully-inflected
word forms. A NARROW-DOMAIN but grammatically fluent realizer (SimpleNLG-class, single application domain) needs
only hundreds-to-low-thousands of lexicon entries and a comparably small hand-curated rule set (an order-of-magnitude
inference from how these systems are deployed, not a directly-published count -- flagged as approximate) --
directly consistent with this note's Section 1 claim that the MINIMUM ingest is small. Template/frame-based
generation (the closest precedent to the substrate's frame-slot decoder) has a well-documented, convergently-cited
FAILURE MODE: naive full-coverage templating scales as the PRODUCT of its combinatorial dimensions (Reiter 1995
cites a real form-letter system needing ~1,000 templates just for "the simplest divisions" of one domain; a
schema-guided dialogue system needed >200 templates naively, reduced to ~44-88 with a hybrid neural-smoothing layer)
-- templates do not generalize to novel slot/fact combinations not anticipated at authoring time. This is the exact
scaling risk the substrate's own capacity envelope already characterizes structurally (D<=26 slots, V<=1024 per
slot, F=2 factors, a hard architectural wall not a template-authoring limit) -- a genuinely different, more
principled failure mode than hand-authored templates, since the substrate's frame IS an algebraic bound structure,
not an enumerated string template.

**Rule-based morphological generation, direct engineering precedent for Layer B:** two-level morphology
(Koskenniemi 1983) represents word-formation as parallel finite-state rules mapping a lexical string to a surface
string alongside a lexicon of roots + inflectional morphemes -- the architecture behind PC-KIMMO and Xerox
finite-state tools (`lexc`/`twolc`), fully rule-based and inspectable, the direct precedent for the WUG cell's
"infer a transform, apply it" mechanism. English's regular inflection is conventionally handled by a small number
(order ~5-10) of named orthographic/spelling rules (consonant doubling, e-deletion/insertion, y-replacement,
k-insertion) layered on the ~8 core inflectional categories -- i.e. a DOZEN-ish total rule instances covers all of
regular English inflection, corroborating this note's "cheapest layer" claim numerically.

**What the literature says is lost/gained (directly answers the "which route to choose" question):** the field's
own consensus (Reiter's applied-NLG writing, Gatt & Krahmer's 2018 survey) is that symbolic/rule-based generation is
factually reliable and NEVER hallucinates (every decision traces to a rule), at the cost of engineering effort for
edge cases and sometimes-lower raw fluency; neural generation is fluent and cheap to build from a corpus but
hallucinates and omits content not grounded in the input. The emerging consensus explicitly recommended in the
literature (not merely one option among equals) is a HYBRID: keep a symbolic layer in charge of content/correctness
decisions, and reserve any statistical/neural component for local fluency polishing only, deliberately kept away
from decisions that could introduce hallucination -- this is a direct, independent validation of this note's own
recommended sequencing (structured glass-box layers first; any future fluency polish is a thin, non-load-bearing
shell on top, exactly per the 2026-06-26 strategic pivot that closed the old statistics-first track).

---

## 3. Intersection with held constraints -- sequencing, re-encode, cortex-layer

**Verified dependency table (from the angle5 note, cross-checked here):** the minimal grounded-utterance demo does
NOT wait on ANY currently-blocked gate. Everything that gates it is already done:

| Dependency | Status | Blocks the minimal demo? |
|---|---|---|
| Perception/encoder (GSBC_EXPAND2X) | DONE, retrieval gap solved via graded codes | NO |
| Narrow KG ingest (ConceptNet/FB15k-237, ~178k atoms) | DONE, real named atoms (the Layer-A vocabulary source) | NO |
| General-knowledge ingest (Wikipedia/books) | USER-LOCKED "not yet" | NO -- minimal demo needs only the existing narrow KG |
| Bind/unbind compositional algebra | CHAIN_GRADE, mature | NO |
| Multi-hop KG retrieval | CHAIN_GRADE | NO |
| INTEGRATION (reason -> generate bridge) | HARD_PASS at FULL (2026-07-05) | NO |
| Generation decoder (native GSBC block-local) | LANDED, MM_STANDARD/CHAIN_GRADE (VET-scoped down from HARD_PASS) | NO -- this IS the demo's output stage |
| Re-encode (HELD, USER safety gate) | HELD | NO -- language ingest curates EXISTING names, does not require touching the encoder |
| Cortex-1 (noise/attention facade) | HONEST_NEGATIVE on its one utility probe | NO |
| Cortex-2 (atom-consultation) | Parked, self-referential, zero wiring to the concept encoder or language | NO -- does not touch language at all |
| Dogfood ingest (substrate's own notes) | Not yet run | NO -- irrelevant to a demo sourced from existing KG facts |

**So: the language ingest does NOT require the HELD re-encode, and does NOT require the cortex-layer (neither
Cortex-1's noise-injection facade nor Cortex-2's atom-consultation reasoning layer) to begin.** Both are commonly
conflated with "prerequisite for language" in planning discussions; the filesystem does not support that
conflation for the narrow capability. The cortex-layer WOULD matter for the capstone's "answer any question,
reason about what to say" layer (Layer C's grammar-beyond-templates and any goal-driven phrasing choice), but not
for curating a lexicon or wiring morphology rules.

**Sequencing -- NOT one big ingest, staged by cost and dependency:**
1. **[Ready now, near-zero cost]** Common-word FILTER over the existing 177,899-name pool + ~20-30-row
   relation-to-verb-phrase table. Pure glue. Unlocks the minimal grounded-utterance demo
   (`exp_generation_grounded_fact_utterance_v1`, already scoped, not dispatched).
2. **[Cheap, mechanism already proven in isolation]** Expand the WUG-test morphology mechanism from 1 rule to the
   full ~8-10-rule English inflection set + a short irregular-exception list, and WIRE it into the decoder's Stage
   C (currently a frozen lookup). This is the cheapest genuinely-new build of the three real layers -- small,
   enumerable, and the "infer a rule from examples" mechanism is already HARD_PASS.
3. **[Real build, not started]** Function-word closed class (~150-300 entries) + grammar beyond fixed-slot
   (recursive embedding, subject-verb agreement, question/negation transformations). No cell anywhere in the corpus
   attempts this. This is the genuine long pole of the LANGUAGE track specifically.
4. **[Capstone, gated on separate USER-locked bets]** General-knowledge ingest (explicitly out of scope today),
   Cortex-2 graduating past parked/self-referential status to a demonstrated reasoning payoff, and the one-to-many
   generalization/entropy-ceiling result (closed this session as a genuine ceiling, not a bug -- Hits@k achievable,
   rank-1 for multi-valued relations is not) resolved or reframed for "answer any question" generation rather than
   "speak a known fact."

Stages 1-2 do not depend on stage 3 or 4 starting; they are buildable and demoable independently and in parallel
with the capstone bets, exactly mirroring the angle5 note's "parallel track for the narrow capability; capstone for
the full one" verdict.

---

## 4. How the brain acquires language (developmental) -- and what it validates about the staging

External lit-scan targeted this specifically (new angle this pass, not covered by the production-mechanism lit
already gathered). Findings, organized by developmental stage and scale (full citations in Section 6; confidence
flagged per finding by the sub-agent):

- **Stage order and rough age ranges (HIGH confidence on sequence, MEDIUM on exact boundary ages):** canonical
  babbling (~6-8mo onset, continues to ~12mo, acquiring ambient-language prosody by 8-10mo -- "babbling drift") ->
  first words (~10-14mo, median ~12mo) -> slow initial growth (~12-16mo, only 1-3 new words/month; median ~10 words
  at 12mo, ~40 at 16mo) -> a marked ACCELERATION, the "vocabulary spurt"/"naming explosion" (~16-24mo, commonly
  anchored to a **~50-word productive threshold** as the conventional spurt-onset marker, reaching ~20 words/month
  then ~46 words/month in one dataset) -> two-word/TELEGRAPHIC stage (Brown's Stage I, MLU ~1.0-2.0 morphemes,
  ~18-30mo) -> grammatical morphemes added in a robust, frequency/complexity-driven ORDER (Brown 1973's 14-morpheme
  study, ~24mo-4yr) -> increasingly complex recursive syntax (embedding, questions, negation, passives) through
  ~3-5+ years. **Honest caveat surfaced by the lit-scan:** whether the "spurt" is a genuine discontinuity or a
  gradual acceleration is itself contested -- Ganger & Brent (2004, *Developmental Psychology*) found only 5 of 38
  children's growth curves better fit a discontinuous (logistic) model than a smooth quadratic one; the ~50-word
  threshold is a useful conventional landmark, not proof of a sharp inflection.
- **Vocabulary scale at milestones (HIGH confidence at the anchors, MEDIUM on intermediate ages):** ~10 words
  (median, 12mo) -> ~40 words (16mo) -> ~50-90 words (18mo, spurt onset) -> ~300-600 words (24mo, post-spurt; 573
  median at 30mo per Fenson et al. 1994 CDI norms, N=1,803) -> commonly-cited-but-less-precisely-sourced ranges of
  ~1,000 words (age 3) and ~4,000-10,000 receptive words (age 5-6, school entry) -> **adult: Brysbaert et al. (2016,
  *Frontiers in Psychology*, N=220,000+) give the best-powered modern anchor at ~42,000 lemmas / ~11,100 word
  families at age 20**, resolving much of the older 20,000-40,000+-and-up variance as a lemma-vs-word-family
  counting-unit artifact (their own 42,000-lemma figure is only ~11,100 word families -- nearly 4x different
  depending on the unit).
- **Brown's (1973) 14 grammatical morphemes, in acquisition order (HIGH confidence, one of the most-replicated
  findings in developmental psycholinguistics -- de Villiers & de Villiers 1973 cross-sectionally replicated the
  exact order in 21 children):** (1) present progressive -ing, (2) preposition "in", (3) preposition "on", (4)
  regular plural -s, (5) irregular past tense, (6) possessive -'s, (7) uncontractible copula, (8) articles (a/the),
  (9) regular past -ed, (10) regular 3rd-person -s, (11) irregular 3rd-person, (12) uncontractible auxiliary, (13)
  contractible copula, (14) contractible auxiliary. **Critically: de Villiers & de Villiers found acquisition order
  correlates with grammatical/semantic COMPLEXITY, not with frequency of parental input** -- the order is
  rule-governed, not frequency-driven, the same "rule not memorization" signature the substrate's WUG-test cell
  demonstrates.
- **Telegraphic speech, precisely what's retained vs. omitted (HIGH confidence, essentially uncontested across
  sources):** content words (nouns, verbs, adjectives) in a largely FIXED, adult-consistent word order are retained;
  function words (articles, prepositions, auxiliaries, copulas) and inflectional morphology (tense, plural,
  possessive marking) are OMITTED, lasting roughly 6-12 months (Brown's Stage I, ~18-30mo) before morphemes begin
  filling in systematically (full mastery of all 14 not until close to age 4). This is the exact functional
  description of the substrate's currently-proven capability (Layer C above): content words, fixed positional-frame
  order, no function words, no morphology wired in yet. The parallel is at the level of PRODUCTION-ARCHITECTURE
  STAGE (which pipeline components are present vs. not yet present), not a claim that the substrate has toddler-like
  general cognition -- flagged explicitly per the mechanism-analog-is-not-task-analog discipline.
- **Minimum functional-communication vocabularies (HIGH confidence on the figures, well-corroborated):** Ogden's
  Basic English (850 core words, expandable to ~2,000 general core); the General Service List (West 1953, 2,000
  headwords, ~80-90% coverage of general text depending on spoken/written); the New General Service List (2,809
  words, >92% coverage); Nation (2006) establishing 6,000-7,000 word families for ~98% coverage of SPOKEN text and
  8,000-9,000 for ~98% of WRITTEN text. These corpus-frequency figures independently corroborate the
  developmental-acquisition numbers above: both literatures converge on "a few hundred-to-low-thousands of words is
  functionally adequate," with the long productive-vocabulary tail (10,000s+) being a fluency/precision multiplier,
  not a functional-floor requirement -- not a coincidence, since child vocabulary growth and adult text-frequency
  distributions are both governed by the same Zipfian statistics of language use.

**What this validates:** the substrate's proposed staging (vocabulary/lexicon essentially reused -> morphology as
a cheap add-on -> function words/recursive grammar as the genuine long pole) is not an arbitrary engineering
guess -- it independently matches the ORDER in which the one confirmed biological existence-proof (human child
language acquisition) builds the same capability. This is a legitimate cross-check on the build sequence, not a
claim of task-level equivalence.

---

## Cheap decisive test

Unchanged from the sibling angle5 drill (this drill does not propose a new cell, per task instruction: design/scope
only): `exp_generation_grounded_fact_utterance_v1` (proposed, NOT dispatched) -- source real facts from the existing
ConceptNet ingest via the CG multi-hop retrieval primitive, compose via the HARD_PASS Integration bridge, decode via
the LANDED native block-local decoder, and print the recovered token strings via the existing `id_order_json` name
lookup (the ONE new step -- instrumentation, not research). This is also the cheapest test of Layer A + D above (the
common-word filter and relation-verb table are exactly its curation inputs).

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered)

- **HARD-PASS (minimum ingest sufficiency):** given ONLY the glue described in Layer A/D (common-word filter +
  relation-verb table, ~0 new ingest) plus the EXISTING decoder, an end-to-end retrieve->compose->decode->print cell
  achieves exact-ordered token match >= 0.70 on >= 20 curated common-word ConceptNet S/V/O facts, with zero
  garbled/obscure-to-a-human decodes and a shuffled-fact control that collapses (discriminator fires). This would
  confirm the minimum-ingest claim in Section 1 is sufficient for a first legible grounded utterance.
- **HARD-FAIL (minimum ingest insufficiency):** exact-ordered match < 0.30 on the same cell despite every component
  independently clearing its own bar in isolation -- would mean an UNDIAGNOSED integration-joint problem exists
  between already-proven primitives, not a vocabulary-scale problem (since the vocabulary/lookup layers are
  deliberately minimal and cheap to inspect for bugs).
- **HARD-PASS (morphology-wiring, Layer B next step):** expanding the WUG mechanism from 1 rule to >= 5 of the
  ~8-10 core English inflectional rules, each independently tested the same way (few-shot rule inference, novel-stem
  generalization), holds novel-stem generalization >= 0.85 per rule (matching the already-proven single-rule
  result). HARD-FAIL: any rule's novel-stem generalization < 0.60 -- would indicate the WUG mechanism's HARD_PASS
  was rule-specific (present->past may be an easier transform than, say, plural formation with its 3 allomorphs
  -s/-z/-Iz) rather than a general dual-route capability, a genuine and useful negative result.
- **HARD-FAIL (over-claim guard, applies regardless of numeric result):** if any future framing represents the
  minimum-ingest demo, if it passes, as "the substrate speaks fluent English" or "language is solved" -- it is NOT;
  it remains telegraphic (no function words, no morphology wired in by default, no recursive grammar) and drawn from
  a narrow pre-ingested KG, not general knowledge. This over-claim is itself the HARD-FAIL condition for honest
  framing, independent of any cell's numeric outcome.

## Cross-thread synthesis

Directly extends and cross-checks, without redoing:
`notes/research_substrate_native_language_path_5x_angle5_2026-07-05.md` (the grounded-utterance finding and
dependency table this note reuses verbatim, cross-checked against this note's own independent read of the same
metrics files); `notes/research_5x_drill_generation_spec_and_brain_mechanism_2026-07-05.md` (the 5-field convergence
on position-as-bound-factor, reused not re-derived); `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md`
(Stage A/B/C design + the envelope-verified F=2 hard wall + V<=1024 cliff, the load-bearing capacity numbers behind
Layer C's scale claim); `notes/integrated_short_term_spec_sheet_5x_drills_what_we_want_how_brain_does_it_2026-07-05.md`
(VET results: decoder MM_STANDARD not HARD_PASS -- generation is "frame-known," not blind-factorization; the honest
tier this note's P-estimate is calibrated against); `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
(why the OLD bigram/trigram statistical-LM track was CLOSED by USER directive -- a Hebbian/HRR associative-memory
W-matrix capacity wall on context-transition storage, ~13,500x over capacity at production scale -- a categorically
DIFFERENT mechanism from today's frame-known decoder, which factors a KNOWN bound proposition rather than predicting
from co-occurrence statistics, and so does not inherit that wall; this is the direct evidence base for why "language
ingest" today means structured concept/frame/morphology ingest, NOT a return to raw-text statistical ingest);
`notes/research_thrust_brain_component_inventory_and_build_priorities_2026-07-05.md` (frame-slot decoder listed as
one of 4 brain components already load-bearing, "HAVE -- strong"); `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md`
(GENERATION/FRONTIER/REASONING tier state, cross-checked); direct filesystem verification (this pass) of
`data/exp_lex_wug_test_cpu_v1/metrics.json`, `data/exp_pos_tagger_ptb_substrate_cpu_v1/metrics.json`,
`data/exp_depparse_discriminative_cpu_v1/metrics.json`, `data/exp_comm_lex_emission_cpu_v1/metrics.json`,
`data/exp_substrate_response_planner_frame_slot_composition_v1/metrics.json`, and
`tools/substrate_conceptnet_ingest_v1.py` (relation-type enumeration, ~20-30 relations already closed-class).

## Substrate-product implications

1. **"Language ingest" is not one large undertaking -- it is four small, independently-costed layers, three of
   which reuse mechanisms already proven at toy scale.** Planning and messaging should decompose it this way rather
   than as an undifferentiated "large language ingest," which overstates the near-term cost and understates how much
   is already sitting in the substrate unwired.
2. **The cheapest, highest-signal next product milestone remains the minimum-ingest grounded-utterance demo**
   (unchanged recommendation from the sibling angle5 note) -- it requires none of the four layers' expensive parts,
   only curation glue over what already exists.
3. **Morphology is a much smaller lift than "language ingest" framing implies** -- English's productive
   morphology is famously simple (a handful of rules + a short exception list), the rule-inference mechanism is
   already HARD_PASS, and the remaining work is expansion-and-wiring, not new research.
4. **Function words + recursive grammar is the honest long pole specifically within the language track** -- name it
   explicitly as the piece that is unbuilt and non-trivial, rather than letting "language ingest" as a phrase imply
   uniform difficulty across all four layers.
5. **Neither the HELD re-encode nor the cortex-layer (either Cortex-1 or Cortex-2) gates the language-ingest work
   described here.** This should be stated explicitly in planning to prevent an artificial dependency chain from
   being assumed.
6. **The developmental-acquisition literature is a legitimate, cheap cross-check tool for future staging decisions**
   in this track (vocabulary-before-morphology-before-function-words-before-recursion is not just our engineering
   guess; it is the one confirmed biological existence-proof's own order) -- worth keeping as a standing reference
   for sequencing calls, used carefully as a mechanism-level analogy only.

## Citations (verified count)

Internal (primary, filesystem-verified this pass, not literature): 5 metrics.json files + 1 ingest-tool source file,
listed in Cross-thread synthesis above. External (literature, 3 independent Sonnet sub-agents, generic-query-only
per query-privacy discipline, ~40 total citations returned, lit-scan-calibration-penalized in the P-estimate below):

**A. Developmental language acquisition (HIGH confidence on stage sequence/morpheme order, MEDIUM on some
intermediate-age vocabulary counts):** Brown, R. (1973) *A First Language: The Early Stages* (the 14-morpheme
acquisition order, Stage I telegraphic MLU framework); de Villiers & de Villiers (1973), "A cross-sectional study of
the acquisition of grammatical morphemes in child speech," *Journal of Psycholinguistic Research* (cross-sectional
replication of Brown's order in 21 children; complexity not frequency predicts order); Fenson et al. (1994)
MacArthur-Bates CDI norming study, N=1,803 (vocabulary-by-age figures: ~10 words/12mo, ~40/16mo, 573 median/30mo);
Nelson (1973), *Structure and Strategy in Learning to Talk*, Monographs SRCD 38(1-2) (conventional ~50-word
spurt-onset landmark, approximate attribution); Ganger & Brent (2004), *Developmental Psychology* 40(4) (vocabulary
spurt is NOT a clean discontinuity for most children -- 5/38 fit a logistic better than smooth-quadratic growth);
Brysbaert, Stevens, Mandera & Keuleers (2016), "How Many Words Do We Know?", *Frontiers in Psychology* (best-powered
modern adult-vocabulary anchor: ~42,000 lemmas / ~11,100 word families at age 20, N=220,000+ crowdsourced).

**B. Symbolic/grammar-based NLG (HIGH confidence on pipeline architecture and the hard-numbered systems; MEDIUM on
narrow-domain lexicon-size inference):** Reiter & Dale (2000), *Building Natural Language Generation Systems*,
Cambridge (the document-planning -> microplanning -> surface-realization pipeline); Gatt & Krahmer (2018), "Survey
of the State of the Art in Natural Language Generation," *JAIR* 61 (arXiv:1703.09902); Reiter (1995), "NLG vs.
Templates" (arXiv cmp-lg/9504013, the ~1,000-form-letter combinatorial-explosion example); Kale & Rastogi (2020),
"Template Guided Text Generation for Task-Oriented Dialogue," EMNLP (arXiv:2004.15006, >200 naive vs ~44-88 hybrid
templates); Gatt & Reiter (2009), SimpleNLG, ENLG; Lavoie & Rambow (1997), RealPro; Grishman, Macleod & Meyers
(1994), COMLEX Syntax, ~38,000 headwords; XTAG Research Group technical report, UPenn (1,226 elementary trees,
~37,000 lexicon entries, 317,000 inflected forms); LinGO English Resource Grammar (DELPH-IN) documentation
(~10,500-35,000 lexical entries, 59 lexical rules); Koskenniemi (1983), *Two-Level Morphology*, PhD thesis
(rule-based finite-state morphological generation architecture; exact rule-count not independently verified --
flagged approximate); Reiter's applied-NLG blog series (2018-2022) on hallucination/fluency trade-offs and the
symbolic-content-plus-neural-polish hybrid recommendation.

**C. Morphology rule-counts + vocabulary-coverage curves (HIGH confidence on the core numbers, MEDIUM on irregular-
plural-noun total which the literature itself does not canonically fix):** Pinker & Prince (1988), "On language and
connectionism," *Cognition*; Pinker, S. (1999), *Words and Rules* (160-180 irregular English verbs in productive
adult use, the dual-route rule-vs-exception-list architecture); Berko, J. (1958), "The Child's Learning of English
Morphology," *Word* (the original Wug test; 97% of children age 5+ correctly generalize a novel plural to an unseen
nonce word -- the founding empirical evidence for rule-based, non-memorized morphological generalization); West, M.
(1953), *A General Service List of English Words* (2,000 headwords, ~80-90% text coverage); Coxhead, A. (1998/2000),
Academic Word List (570 word families, ~10% additional academic-text coverage); Browne, Culligan & Phillips
(2013/2016), New General Service List (2,809 words, >92% coverage); Nation, I.S.P. (2006), "How Large a Vocabulary
Is Needed for Reading and Listening?", *Canadian Modern Language Review* (6,000-7,000 word families for 98% spoken
coverage; 8,000-9,000 for 98% written coverage); corpus studies on Finnish nominal morphology (theoretical
~2,200-2,249 forms/noun; ~27.6 forms/noun actually attested in corpus data for the 2,000 most frequent nouns).

**P_deflated:**
- P(minimum glue-only ingest yields a legible, discriminator-surviving first grounded telegraphic utterance) ~=
  0.65-0.70 (every load-bearing piece is independently CG or MM_STANDARD/HARD_PASS already; deflated from a
  pre-penalty ~0.80-0.85 per the mandatory lit-scan/novel-composition calibration penalty, since the specific
  chained end-to-end composition has not itself been run).
- P(structured, non-raw-text language ingest -- as scoped in this note -- eventually yields broad conversational
  fluent generation, the capstone) ~= 0.25-0.30 (pre-penalty ~0.40-0.45; capped well under the 0.50 novel-synthesis
  ceiling since this is cross-field synthesis for an unbuilt capstone, not a directly-published result for our exact
  regime; gated on the unbuilt function-word/recursive-grammar layer, unproven Cortex-2 payoff, and the already-
  closed one-to-many entropy ceiling needing a reframe for open-ended question-answering rather than known-fact
  telegraphic utterance).

Headline P_deflated for the return line: **0.65** (the near-term, actionable minimum-ingest claim -- the capstone
number is reported separately above and should not be conflated with it).
