# Psycholinguistics of figurative/conventional-language comprehension for goal-conditioned flag-and-fit disambiguation

**Filed:** 2026-08-09 by research (Opus synthesis over 4 parallel Sonnet lit-scan lanes).
**Trigger:** Director+USER high-priority drill — design the "flag-and-fit" disambiguator for
outcome expressions with a literal reading AND a conventional/figurative reading ("walked away" =
physically left vs. disengaged/avoided), where the reader's maintained GOAL should select which
reading applies (dynamic, goal-relative), not a static gloss.
**Query-privacy:** all 4 lanes searched only public psycholinguistic/academic terms (author names,
theory names, journal venues). No substrate-internal module names, configs, or numbers went
off-platform.

## HEADLINE

**Goal-conditioned fit-selection is brain-faithful, and the strongest existing formal precedent —
Rational Speech Act / QUD pragmatics (Kao, Wu, Bergen & Goodman 2014) — already computes almost
exactly the flag-and-fit architecture: ground the literal semantics, then select a reading by
scoring it against an active goal/QUD-relative utility function, not a fixed gloss.** Independently,
mainstream psycholinguistics converges on three refinements the raw "flag then fit" sketch is
currently missing: (1) BOTH senses are activated in PARALLEL, early, by default — not literal-first
then figurative-repair — so "ground both senses" is not just a workaround, it is the empirically
correct architecture (Swinney & Cutler 1979 direct-access; Kessler, Weber & Friedrich 2021 shows
literal constituent meanings stay co-activated even inside figurative contexts); (2) meaning access
is ordered by SALIENCE (frequency/conventionality), not by a clean literal/figurative split (Giora's
Graded Salience Hypothesis) — the fit step needs a salience-weighted prior, not a neutral 50/50
race, and "walked away" specifically sits mid-continuum as a "weak," semi-compositional
"idiomatically combining expression" (Nunberg, Sag & Wasow 1994), never a frozen idiom; (3) readers
do NOT always pay the cost of full disambiguation — Ferreira's Good-Enough processing account, with
direct experimental support (Swets, Desmet, Clifton & Ferreira 2008: task-goal type gates whether
ambiguity gets resolved at all) — meaning the expensive goal-relative FIT computation should be
GATED on a coherence-check failure against the default/salient reading, not run unconditionally on
every flagged item.

**P_deflated (existence-claim confidence — the cited mechanisms are real and correctly characterized):
0.72** (raw ~0.85-0.90 across 4 independently-corroborating lanes, most claims HIGH confidence and
cross-lane-convergent; deflated per lit-scan calibration for the several MEDIUM/UNVERIFIED secondary
details flagged inline by each lane — exact Gibbs 1980 citation detail, several ERP effect-size
specifics, the Gibbs-vs-Giora reconciliation framing).
**P_deflated (the narrower claim that the refined flag-and-fit mechanism below, mapped onto our own
substrate primitives, is the right next build): capped at 0.50** per mandatory novel-synthesis
ceiling — this is a plausibility read connecting verified external theory to our own architecture,
not a tested claim.

## 1. What the four lanes found (organized by question)

### 1a. Is the "race" literal-first-then-figurative-repair, or parallel? PARALLEL is now dominant.
Two historically opposed models: Bobrow & Bell (1973) serial/literal-first ("idiom list" consulted
only after literal parsing fails) vs. Swinney & Cutler (1979, *JVLB*) "Lexical Representation
Hypothesis" — idioms stored/retrieved like long words, literal and figurative senses activated
**simultaneously**. Cacciari & Tabossi's (1988, *JML*) Configuration Hypothesis sits between: literal
processing dominates only up to a "recognition point/key" (enough of the string to signal
idiomaticity), after which the idiomatic meaning is retrieved — this gives a principled, testable
FLAG-TRIGGER MOMENT, not a vague notion of "conventionalizable expression." Gibbs & Nayak's (1989)
Idiom Decomposition Hypothesis adds that "decomposable" idioms (parts map transparently onto the
figurative meaning, e.g. "pop the question") keep literal constituents active and contributing,
while "non-decomposable" idioms ("kick the bucket") do not. Modern consensus (Titone & Connine 1999
hybrid multidetermined model; Libben & Titone 2008; Kessler, Weber & Friedrich 2021 eye-tracking+ERP,
PMC8406370) is a **hybrid/parallel-race**: both routes activate early, familiarity/predictability/
decomposability/context determine the winner. Kessler et al. specifically found literal
constituent-word semantic associates get transient fixation bias even during figurative-biasing
idiom recognition — literal grounding is never fully suppressed. Confidence: HIGH on parallel-access
being the dominant modern position; MEDIUM on how "settled" the field considers this (a 2026 preprint
found by lane 1 suggests decomposability-as-graded-vs-categorical is still actively contested).

### 1b. Graded Salience Hypothesis + the conventionalization spectrum
Giora (1997, *Cognitive Linguistics* 8(3); 1999; 2003 *On Our Mind*, Oxford UP): meaning access is
ordered by **salience** (frequency, conventionality, familiarity, prototypicality), NOT by a
literal/figurative dichotomy. The salient meaning (whichever it is) activates first, fast, and
**obligatorily** — context can boost a less-salient meaning into contention but cannot suppress the
salient one's activation. Giora & Fein (1999) irony data: unfamiliar/novel figurative expressions
show only the salient (usually literal) meaning at short SOA, the intended reading emerging later;
familiar/conventional expressions activate both meanings early because both are salient. Peleg, Giora
& Fein (2001, *Metaphor and Symbol* 16) formalize this as two parallel, non-inhibiting mechanisms
(bottom-up salience-ordered lexical access + top-down contextual access). Wray (2002 *Formulaic
Language and the Lexicon*, Cambridge UP; 2008) frames formulaic sequences on a continuum from fully
novel/compositional through weakly-fixed collocations to fully frozen idioms, with holistic
(prefab-unit) retrieval favored as conventionalization increases. Nunberg, Sag & Wasow (1994,
*Language* 70) give the operative distinction for our exact case: **idiomatically combining
expressions** ("walk away," "pull strings," "take advantage" — figurative meaning distributed
transparently across the parts, i.e. compositional-but-conventionalized) vs. **idiomatic phrases**
("kick the bucket" — non-distributable). Titone & Connine (1994) provide the standard
familiarity/transparency/predictability norming instrument for exactly this graded space. This is a
directly load-bearing finding for the flag step: "walked away" is NOT a frozen idiom needing a
single gloss — it is a graded, weakly-conventionalized VPC where both readings stay genuinely live,
which is precisely why the earlier static-gloss->verdict approach (a single fixed reading) is the
wrong representational choice for this class of expression specifically, independent of the goal-fit
question. Confidence: HIGH throughout; MEDIUM on the specific Gibbs-vs-Giora reconciliation framing
(secondary-sourced).

### 1c. Context/expectation-driven disambiguation: constraint-satisfaction + good-enough processing
Kuperberg & Jaeger (2016, *Lang Cog Neurosci* 31(1)) give the reference taxonomy: prior context
generates probabilistic expectations over upcoming MEANINGS (not just forms), consistent with
surprisal-based accounts (Hale 2001; Levy 2008, *Cognition* 106). MacDonald, Pearlmutter & Seidenberg
(1994, *Psych Review* 101) constraint-satisfaction/biased-competition: multiple probabilistic cues
(frequency, local semantic fit, discourse context) are integrated continuously and in parallel — this
is the direct mechanistic license for treating a maintained goal as "one more constraint entered into
the same competition," exactly the framing the task specified ("top-down biased competition").
Ferreira's Good-Enough processing (Ferreira, Bailey & Ferraro 2002, *Curr Dir Psych Sci* 11; Ferreira
& Patson 2007, *Lang Ling Compass* 1): comprehenders often build shallow, task-sufficient
representations and skip full disambiguation UNLESS the task/goal demands it. The sharpest direct
evidence: **Swets, Desmet, Clifton & Ferreira (2008, *Mem Cogn* 36)** — manipulating expected
question depth (shallow vs. detailed comprehension questions) around ambiguous relative-clause
attachments, the "ambiguity advantage" (faster reading when left underspecified) appeared ONLY under
shallow-question expectation; detailed-question expectation eliminated it, i.e. readers strategically
DEEPEN disambiguation when task goals demand precision. Ortony, Schallert, Reynolds & Antos (1978,
*JVLB* 17(4)): a sufficiently rich prior CONTEXT eliminates the literal-processing-cost penalty for
figurative targets entirely (context-sufficiency, not just facilitation) — weak-context items are
where genuine ambiguity/difficulty concentrates. Confidence: HIGH throughout (canonical, repeatedly
cross-referenced sources; Swets et al. is the strongest single piece of direct evidence in this
entire drill for "task/goal changes WHETHER disambiguation happens," independent of the harder
question of whether goal changes WHICH sense wins).

### 1d. Is goal-conditioned figurative-sense selection psychologically real? (the load-bearing question)
This is the honest, most carefully hedged section — direct vs. indirect evidence matters most here.

- **Strongest, most directly formalized evidence: Rational Speech Act / QUD pragmatics.** Frank &
  Goodman (2012, *Science*); Goodman & Frank (2016, *TiCS*); **Kao, Wu, Bergen & Goodman (2014,
  "Formalizing the Pragmatics of Metaphor Understanding," CogSci)** and the companion hyperbole model
  (Kao et al. 2014, PNAS, the "$10,000 kettle" model). The pragmatic listener computes P(meaning |
  utterance) by inverting a speaker model whose utility is **QUD-relative** (Question Under
  Discussion = the implicit conversational goal). The SAME literally-false/ambiguous utterance is
  assigned different figurative-vs-literal readings depending on which QUD is inferred active, fit
  and validated against human interpretation-judgment data. This is not merely a framework that
  "would predict" goal-conditioning — it is a working, quantitatively fit computational model of
  exactly this phenomenon. Confidence: HIGH that RSA formalizes and empirically validates
  goal-conditioned reading-selection. Important caveat: these are OFFLINE interpretation-judgment
  studies, not online real-time processing measures — direct evidence that goal-conditioning happens
  as *final interpretation selection*, agnostic on whether it happens at *early lexical access* vs.
  as *post-access arbitration*.
- **Relevance Theory** (Sperber & Wilson 1986/1995; Wilson & Carston 2007 on ad hoc concepts; Carston
  2002 *Thoughts and Utterances*): architecturally builds "expectations of relevance" around the
  hearer's currently active goal/effort-minimization as a foundational, defining claim — but no
  paper was found that manipulates a reader's task-goal orthogonally to context content and shows a
  resulting sense-selection shift for idioms specifically. The goal-sensitivity is baked into the
  theory's architecture; the classic experiments probe effort/timing, not a goal-vs-frequency
  dissociation. Confidence: HIGH on the theoretical claim; MEDIUM-LOW on direct empirical isolation.
- **Narrative goal-outcome interpretation** (Trabasso, van den Broek & Suh 1989 causal-network model:
  Outcome nodes are evaluated relative to the preceding Goal node; Gerrig & colleagues on reading-time
  differences driven by reader-inferred character preferences): the closest evidence in our own
  domain (narrative goal/outcome reading) — goal context measurably changes processing cost/importance
  of an outcome event. But this is evidence for differential processing COST, not crisply for sense
  SELECTION of an ambiguous phrase. Confidence: MEDIUM-HIGH, direct for goal-conditioned outcome
  evaluation, indirect for lexical/phrasal sense-selection specifically.
- **Counter-evidence check:** Fodor's (1983) modularity-of-mind position (encapsulated, bottom-up,
  goal-immune lexical access) is the canonical skeptical position, anchored empirically in Swinney's
  (1979) exhaustive-access data. But this debate is fought almost entirely over CONTEXT/FREQUENCY
  effects on early access, not GOAL/task-purpose specifically — it is an adjacent debate, not a
  direct rebuttal of goal-conditioned selection. No direct strong counter-evidence against
  goal-conditioning was found. Confidence: HIGH that the modularity debate exists and is real; MEDIUM
  that it fails to directly engage the goal-specific question (a genuine, honestly-flagged gap in the
  literature, not resolved by this drill).

**Bottom line on 1d:** direct, quantitatively real, validated evidence for goal-conditioned reading
selection is strong at the level of a working computational-pragmatics model (RSA/QUD) and at the
level of narrative goal-outcome differential processing (our own domain), but thin at the level of
online lexical-competition timecourse specifically isolating GOAL from CONTEXT. This is an honest gap
to carry forward, not a disqualifier — it is exactly the gap a novel-synthesis capped-P=0.50 finding
should carry.

## 2. Verdict: is goal-conditioned fit-selection brain-faithful?

**YES, with a specific, actionable caveat.** Convergent support: (a) parallel dual-sense activation
(1a) licenses "ground both senses" as the correct default architecture, not a workaround; (b) graded
salience (1b) means the fit computation needs a conventionality-weighted prior, not a neutral race;
(c) constraint-satisfaction/biased-competition (1c) is the textbook license for treating the goal as
one more probabilistic cue integrated with salience and local context, matching the task's own framing;
(d) RSA/QUD (1d) is a working, validated formal precedent for goal-conditioned FINAL selection. The
caveat: no direct online-timecourse evidence isolates goal (vs. context/frequency) as the thing doing
the reordering — so build the mechanism as **post-access arbitration over two already-grounded
candidates** (matching what RSA computes and what parallel-access psycholinguistics licenses), not as
a claim about early lexical access being goal-gated. This sidesteps the evidential gap entirely: we
do not need "goal reorders early access" to be true for flag-and-fit to be brain-faithful — we only
need "both senses are grounded in parallel, then goal-conditioned utility scoring selects among them,"
which IS well-supported.

## 3. Refined mechanism (WHEN to flag / HOW to fit / arbitration)

**WHEN to flag.** Treat the dictionary-lookup FLAG (kaikki/Wiktionary/WordNet-MWE match) as
Cacciari & Tabossi's recognition-point/"key": flag fires the moment the sentence's verb-particle /
light-verb span matches a listed MWE entry — this is a real, literature-grounded trigger moment, not
an arbitrary lookup. Attach a **salience/conventionality weight** at flag time (proxy: dictionary
figurative-sense-frequency rank, or a simple idiom/figurative tag-presence signal per
Titone-&-Connine-style transparency norming) — this operationalizes Giora's graded salience and
Wray/Nunberg-Sag-Wasow's continuum directly: a near-frozen idiom gets a strong default-bias prior; a
weak colloquialism like "walked away" gets a near-neutral prior (both readings stay genuinely live).

**HOW to ground.** Ground BOTH candidate senses as concept-feature hypervectors via the existing
`concept_vector`/`CONCEPT_FEATURES` grounding pipeline (reuse, not new): the literal sense via normal
compositional grounding of the verb+particle heads (already-owned organs), the conventional/figurative
sense via the dictionary gloss's head concept(s), grounded the same way — reusing the
script_bridge/learned_script_bridge mechanism class already proven this arc (per
`notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md`). Neither sense is discarded at flag
time, matching finding 1a.

**HOW to fit.** For each grounded sense candidate, compute goal-relevant fit against the maintained
goal's attribute-predicate bundle (the situation-model register in `hdlab/state_of_mind.py` /
Direction-B's utility_channel attribute-predicates) via `hdlab/quality_relation.py`'s
concept-similarity/opposition primitive (`quality_relation(sense_concept, goal_attribute_concept)` —
the existing WordNet-antonym-closure + FPE-axis-relation mechanism is a direct, already-owned
implementation of "concept opposed to / aligned with a goal attribute"). Aggregate per-sense fit
across active goal-attributes with a max-margin combination (reuse `cleanup_with_margin`'s existing
discipline, do not invent a new combination rule).

**Arbitration.** `combined_score(sense) = w_salience * default_bias(sense) + w_goal * fit(sense, goal)`
— a weighted combination, not goal-fit alone (per Giora: context/goal can promote the less-salient
reading but the salient one never drops to zero weight). Select `argmax(combined_score)` subject to a
margin gate; below-margin => ABSTAIN rather than force a verdict (matches the director's own
Krippendorff-alpha finding, 0.63 < the 0.67 "tentative" floor — some residual is genuinely ambiguous
even to human annotators, and the mechanism should say so rather than guess).

**Gate the FIT step itself (the good-enough refinement).** Per Ferreira/Swets et al.: do not run the
expensive goal-relative FIT computation on every flagged item. First check whether the DEFAULT
(salience-weighted) reading's implied MET/UNMET verdict is COHERENT with the currently active goal's
expected-polarity direction (a cheap pre-check, reusing the existing congruence-decision fast path).
Only escalate to full FIT when the default reading conflicts with or is ambiguous relative to the
goal — this is both brain-faithful (readers do not always pay for full disambiguation) and a real
compute-efficiency win (avoid running the expensive per-attribute quality_relation scan on every
flagged MWE in a passage).

## Cheap decisive test

Three-arm comparison on the DesireDB flagged-residual cohort (the M1 idiom-grounding gate in
`notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md`, or the Stage-2 utility-channel
idiomatic hardest cohort that HARD-FAILED at 0/8 recovery per
`notes/director_brain_fidelity_SYNTHESIS_and_direction_verdict_2026-08-09.md` — same cohort, reused,
do not re-mine):

- **Arm 1 (already-tried baseline): static gloss->verdict.** Flag the expression, ground ONE
  conventional gloss, map directly to MET/UNMET. This is the mechanism that already HARD-FAILED
  (0/8 on the idiomatic hardest cohort) — rerun only if the cohort changed since; otherwise cite the
  existing number.
- **Arm 2 (salience-only heuristic — the critical NEW control this drill adds, not in the current
  plan).** Flag the expression, ground both senses, select the higher-salience/more-conventional
  reading REGARDLESS of goal (goal-blind). This isolates whether goal-conditioning adds anything
  beyond Giora's obligatory-salience default. If Arm 2 matches or beats Arm 3, the "goal selects the
  reading" claim is not earning its complexity — this is the sharpest test the literature review
  motivates (per the honest 1d gap: online evidence for GOAL specifically, vs. context/frequency, is
  thin — Arm 2 vs Arm 3 is exactly the discriminating experiment).
- **Arm 3 (the proposed mechanism): goal-conditioned flag-and-fit.** Full mechanism above — ground
  both senses, fit each via `quality_relation` against the maintained goal's attribute bundle,
  salience-weighted arbitration.
- **Control (mandatory, both Arm 2 and Arm 3): wrong-goal pairscramble.** Shuffle goal<->outcome
  pairings so each flagged expression is scored against a goal it was not actually paired with in the
  source text. Arm 3's accuracy must COLLAPSE toward Arm 2's (goal-blind) level or chance under
  scramble — if it does not collapse, the mechanism is not actually using the goal, some other
  correlate is doing the work (a required per-role control per this drill's own architecture, not
  optional).

## Falsifiable predictions

**HARD-PASS:** Arm 3 (goal-fit) recovers >=40% of the flagged-residual abstain/wrong cohort (matching
the M1 gate already registered in `direction_b_grounded_knowledge_build_plan_2026-08-09.md`) **AND**
beats Arm 2 (salience-only) by a real margin (not statistically indistinguishable) **AND** the
wrong-goal pairscramble control collapses Arm 3's accuracy to within noise of Arm 2's goal-blind level.
This combination is necessary: recovery alone does not establish that GOAL (as opposed to salience
alone) is doing the work — the Arm2-vs-Arm3 gap plus the pairscramble collapse together are the
minimum bar for the mechanism's core claim to be validated, not just its output metric.

**HARD-FAIL:** any of — (a) Arm 3 does not beat Arm 2 (goal-conditioning adds nothing beyond a
context-blind conventionality prior — matches the honestly-flagged 1d evidence gap; if this happens,
report it as a real, informative negative, not a broken experiment: it would mean this specific
narrative-outcome domain behaves like Giora's obligatory-salience default more than like RSA's
QUD-driven pragmatic reasoning, which is itself a useful, citable finding); (b) the pairscramble
control does NOT collapse (the mechanism is not actually goal-sensitive, something else — e.g. a
correlate of narrative position, sentiment leakage, or entity identity — is driving the apparent fit);
(c) recovery <15% (matches the direction_b plan's own kill criterion for the grounding hypothesis more
broadly, on this cohort).

## Cross-thread synthesis

- **Directly sharpens `notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md`'s M1 gate.** M1
  as currently specified ("recover >=40% of the Stage-2 abstain-to-majority cohort" via
  idiom-grounding) does not distinguish goal-conditioning from a goal-blind salience/conventionality
  default. This drill's Arm 2 (salience-only) control is the missing piece — without it, an M1
  HARD-PASS would be ambiguous about WHY it passed. Recommend folding Arm 2 into M1's design before
  it ships.
- **Directly explains WHY the Stage-2 static-gloss->verdict channel HARD-FAILED** (0/8 on the
  idiomatic hardest cohort, per `notes/director_brain_fidelity_SYNTHESIS_and_direction_verdict_2026-08-09.md`):
  a single fixed gloss per expression is exactly the representational choice section 1b's literature
  says is wrong for graded/weakly-conventionalized items — "walked away"-class expressions keep BOTH
  readings live per Nunberg/Sag/Wasow's "idiomatically combining expressions" category, so collapsing
  to one gloss before any goal-relative scoring discards the information the fit step needs. This is a
  structural diagnosis, not merely "the grounding was incomplete."
  We now have a literature-grounded reason the fix is "ground both, then fit," not "ground the right
  one gloss better."
- **Extends `notes/research_desiredb_hard_residual_prior_art_2026-08-08.md`'s failure-type (a)**
  (valence-present-but-misleading) and reinforces its OCC/Scherer appraisal-goal-conduciveness
  citations: both that drill and this one independently converge on "score relative to the goal, do
  not treat the surface signal as free-floating" as the general fix pattern across multiple distinct
  failure types (appraisal valence there, sense-selection here) — a recurring structural lesson, not
  a one-off.
- **Extends `notes/research_drill_word_sense_disambiguation_frame_selectional_2026-07-21.md` and
  `notes/research_brain_scene_coherence_graded_thematic_fit_disambiguation_2026-07-19.md`.** Both
  prior drills independently found GRADED, mutual-constraint, context-integrated disambiguation beats
  binary/hard-gated approaches (word-sense frame-matching; thematic-fit typicality). This drill adds a
  THIRD, convergent instance at the phrase/construction level (literal-vs-figurative sense selection)
  — reinforcing graded, salience-weighted, goal-integrated scoring as the substrate's general answer
  to disambiguation problems, not a one-off design choice for idioms specifically.

## Substrate-product implications

Never framed as publication value — product-relevant only. The auditable trace this mechanism
produces is a genuine product differentiator: for each flagged expression, the system can show (a)
which two senses were grounded, (b) their salience priors, (c) their per-attribute fit scores against
the stated goal, (d) the arbitration margin — a fully inspectable disagreement/confidence report no
black-box classifier gives. The Arm-2-vs-Arm-3 test is cheap (reuses the already-mined M1 cohort, no
new data collection) and directly de-risks the larger M2/M3 grounding investment in
`direction_b_grounded_knowledge_build_plan_2026-08-09.md`: if goal-conditioning does not beat a
salience-only default on this cohort, that is worth knowing BEFORE scaling idiom-grounding coverage
to the full DesireDB residual, because it would mean the multi-month M3 investment should target
BROADER conventional-sense coverage (a coverage problem) rather than SHARPER goal-relative arbitration
(a scoring-mechanism problem) — a real fork in the roadmap this cheap test resolves early. The
dictionary-lookup FLAG primitive itself (kaikki/Wiktionary/WordNet-MWE match) does not yet exist in
the substrate (confirmed absent by file search this session) — it is a small, well-scoped, genuinely-
new primitive (data supply, not a new learning mechanism) that both this mechanism and the broader
M1-M3 grounding program need; building it once serves both.

## Citations (verified count)

**~40 distinct real citations verified via WebSearch/WebFetch across 4 parallel lit-scan lanes**
(some overlap/reinforcement across lanes on core sources — Swinney & Cutler 1979, Giora 1997, Ferreira
& Patson 2007 — independently surfaced by more than one lane, reinforcing confidence). Confidence is
HIGH on the great majority of author/year/venue bibliographic facts and core theoretical claims
(cross-checked against multiple independent sources per lane); a smaller set of fine-grained secondary
details are flagged MEDIUM/LOW-UNVERIFIED inline in section 1 (exact Gibbs 1980 citation details,
several ERP-study effect-size/latency specifics, the precise Gibbs-vs-Giora reconciliation framing,
whether Relevance Theory has ever been DIRECTLY tested with an orthogonal goal manipulation) — these
were sourced from convergent secondary summaries within this session's time budget, not from
primary-text re-derivation of every numeric detail.
