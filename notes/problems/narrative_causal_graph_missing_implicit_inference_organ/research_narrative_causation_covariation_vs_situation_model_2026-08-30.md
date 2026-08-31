# Research drill: narrative implicit causation -- event-type COVARIATION vs SITUATION-MODEL BRIDGING

Date: 2026-08-30
Scope: hdi_research online literature drill for the solver on
`narrative_causal_graph_missing_implicit_inference_organ`.
Kind: brain-mechanism / lit-scan ONLY (no experiment).
Calibration: lit-scan penalty applied (naive confidence deflated 0.15-0.25; novel-synthesis P
capped at 0.50). "[VERIFIED 08-30]" = confirmed by a primary/authoritative source this session;
"[BACKGROUND]" = from prior knowledge, not re-verified this session; treat as provisional.

--------------------------------------------------------------------------------
## HEADLINE VERDICT

For IMPLICIT narrative causation between two connective-less events, the human-comprehension
literature does NOT compute the causal edge by scanning event-type covariation. It computes it as a
SITUATION-SPECIFIC, TOKEN-LEVEL BRIDGE: construct a specific mediating proposition, then validate it
against world knowledge AS IT APPLIES TO THIS SITUATION'S entities and circumstances (Singer &
Halldorson 1992; Trabasso & van den Broek 1985; Graesser, Singer & Trabasso 1994). Covariation lives
one level DOWN -- it is a good model of the general-knowledge PRIOR (which event-type pairs are
plausibly causal: "attacks tend to cause deaths"), i.e. the semantic-memory store that the online
bridge draws candidates from. It is NOT a model of the online bridging/validation process, and it
structurally cannot perform the two things that dominate open narrative: (a) validate a candidate
bridge against the SPECIFIC tokens of the situation, and (b) infer INTENTIONAL/goal-based causation,
which is the majority causal type in fiction and requires inferring an UNOBSERVED mental state (a
goal) plus recognizing the effect as a plan-step toward it.

So the covariation organ is the RIGHT mechanism for (i) recurring-event-type / encyclopedic physical
causation (its MAVEN-ERE win is exactly this), and it is a NECESSARY-BUT-NOT-SUFFICIENT COMPONENT --
a prior / candidate-bridge generator -- for (ii) open narrative causation. It cannot BE the mechanism
for open narrative on its own. The decisive brain evidence that narrative causal integration exceeds
surface co-occurrence is Kuperberg, Paczynski & Ditman (2011): a causal N400 effect that SURVIVES
matching lexical co-occurrence (LSA). The reconciliation is Kuperberg's (2016) dual-stream account: a
semantic-memory stream (associative, covariation-like) plus an event/situation-model stream
(generative, predictive), where the second contributes beyond the first. This maps onto the Feng et
al. (2021) discourse-causal substrate: left MTG (semantic memory / the covariation prior) + left IFG
(semantic control / unification) + medial PFC (mentalizing / situation model / the bridge).

One honesty caveat carried throughout: Kuperberg's control matched WORD-level co-occurrence (LSA).
The organ does not use word co-occurrence -- it uses EVENT-TYPE contingency (Cheng power-PC +
Griffiths-Tenenbaum support over verb lemmas), which is more structured than LSA. So Kuperberg does
not by itself refute the ORGAN; what refutes a pure covariation-over-types account for narrative is
the STRUCTURAL argument from Trabasso/Singer/Graesser (token-level bridge + situation validation +
intentional causation), for which Kuperberg is corroborating, not sole, evidence.

--------------------------------------------------------------------------------
## PER-QUESTION INVENTORY (PINNED / MODELING / UNCONFIRMED)

### Q1. COVARIATION vs SITUATION-SPECIFIC -- where do the theories place the computation?

Verdict: The classic narrative-comprehension theories place the CAUSAL EDGE at the SPECIFIC
proposition/token level (this situation), NOT at the event-type level. General world knowledge enters
only as the VALIDATION material for a specifically-constructed bridge.

- Trabasso & van den Broek (1985), "Causal thinking and the representation of narrative events,"
  J. Memory & Language. Causal relations between story events are identified by a COUNTERFACTUAL
  NECESSITY-IN-THE-CIRCUMSTANCES test: "If event A had not occurred, then, in the circumstances of
  the story, event B would not have occurred." Two network properties (number of direct causal
  connections; membership in the opening-to-closing causal chain) predict judged importance and
  recall. The counterfactual "in the circumstances of the story" is explicitly TOKEN-LEVEL /
  situation-specific, not a type-frequency. Strength ordering of causal categories: physical >
  motivational > psychological > enabling. [VERIFIED 08-30]
  Status: PINNED (that the edge is computed per-situation by a counterfactual test). Deflated
  P(narrative causal edge is token/situation-level in the human account) = 0.75.

- Singer & Halldorson (1992), "Validation of causal bridging inferences in discourse understanding,"
  J. Memory & Language 31:507-524. The bridging inference is a syllogism-analog: the two sentences
  are minor premise + conclusion; the reader COMPUTES the missing (major) premise -- a specific
  mediating proposition, e.g. RELIEVE[ASPIRIN, PAIN] for "Dorothy took the aspirins. Her pain went
  away." -- and then VALIDATES its truth against general world knowledge (probe: "Does water
  extinguish fire?" answered faster after a causal than a temporal sequence). So the mediator is
  CONSTRUCTED for the specific tokens; the world knowledge is general but is RETRIEVED and CHECKED
  for THIS pair. [VERIFIED 08-30]
  Status: PINNED (construct-specific-mediator-then-validate). This is the single most important
  structural template: it is a token bridge licensed by general knowledge, which is NEITHER pure
  covariation NOR pure situation-invention. Deflated P = 0.75.

- Kintsch (1988) Construction-Integration. Construction builds a network of text propositions PLUS
  knowledge-based elaborations bottom-up and associatively ("dumb"); integration then settles by
  constraint satisfaction / spreading activation over the SPECIFIC network. Bridging inferences are
  drawn from long-term memory during construction and survive/decay in integration. This is the
  natural HYBRID home: the associative construction step is covariation-compatible (the prior), the
  constraint-satisfaction integration step is situation-specific. [BACKGROUND -- theory recalled, not
  re-verified this session].
  Status: MODELING (hybrid placement). Deflated P = 0.55.

- Graesser, Singer & Trabasso (1994), "Constructing inferences during narrative text comprehension,"
  Psychological Review 101:371-395. "Search after meaning": readers build a referential situation
  model and construct causal-antecedent (explanation) inferences to answer WHY an action/event/state
  occurred, guided by reader goals + local/global coherence + world knowledge. Selective (not all
  inferences drawn). Explicitly a situation-model, knowledge-and-goal-driven process. [VERIFIED
  08-30]
  Status: PINNED (situation-model, explanation-driven). Deflated P = 0.72.

Synthesis for Q1: All four converge -- the causal LINK is a property RECOMPUTED per situation over
specific propositions, using general knowledge only as the validation reservoir. Type-covariation is
where the reservoir comes from, not where the link is decided. The organ implements the reservoir,
not the decision. (Novel-synthesis mapping to the organ -> capped P = 0.50.)

### Q2. KUPERBERG 2011 -- does it refute a pure event/verb-covariation account?

Verdict: It refutes reducibility of narrative causal integration to SURFACE (word) co-occurrence, and
so refutes a PURE-covariation account of the INTEGRATION step; it is consistent with covariation as a
necessary-but-not-sufficient COMPONENT. It does not by itself indict the organ's type-level
contingency (different, more-structured measure).

- Kuperberg, Paczynski & Ditman (2011), "Establishing causal coherence across sentences: an ERP
  study," J. Cognitive Neuroscience 23:1230-1246. Three-sentence scenarios; final sentence highly /
  intermediately / un-related causally to context. Lexico-semantic co-occurrence MATCHED across
  conditions via LSA. Result: causally UNRELATED critical words evoked a LARGER N400 than both highly
  and intermediately related, before and at sentence-final position -- i.e. a causal-relatedness
  effect on semantic integration (N400) that is NOT explained by matched lexical co-occurrence.
  [VERIFIED 08-30]
  Reading: the brain's causal integration uses more than surface association -- bridging /
  world-knowledge / situation model. Refutes "pure surface co-occurrence." Status: PINNED (empirical).
  Deflated P(effect is real and beyond LSA co-occurrence) = 0.85.

- Reconciliation via Kuperberg (2016), "Separate streams or probabilistic inference? What the N400
  can tell us about the comprehension of events," Language, Cognition and Neuroscience (hierarchical
  generative framework): a semantic-memory-based mechanism (associative facilitation; left anterior
  temporal, ~300-500 ms) PLUS an event/situation-model-based, predictive/generative mechanism. The
  two can be dissociated; causal coherence recruits the second beyond the first. [VERIFIED 08-30 for
  the dual-stream framing; exact title recalled BACKGROUND].
  Status: MODELING (framework, not one decisive experiment). Deflated P(necessary-but-not-sufficient
  reconciliation holds) = 0.45.

Caveat (load-bearing, honesty): LSA is WORD co-occurrence. The organ's contingency is EVENT-TYPE
(verb-lemma) power-PC/support -- structurally richer than LSA. Therefore Kuperberg does not directly
falsify the organ; it falsifies the weaker claim that causal integration = surface association. The
organ-specific indictment must come from the structural arguments (Q1, Q3, Q4), with Kuperberg as
corroboration. Flag this in any writeup that cites Kuperberg "against covariation."

### Q3. WORLD KNOWLEDGE / SCHEMAS vs STATISTICS -- minimal or constructionist? Which is the organ?

Verdict: Implicit causal bridging FOR LOCAL COHERENCE is made AUTOMATICALLY on BOTH the minimalist
and constructionist accounts -- so both camps agree the target inference happens. But BOTH describe
it as a KNOWLEDGE-BASED LOCAL BRIDGE (retrieve readily-available general knowledge + connect the two
specific propositions), NOT as a corpus-wide type-covariation scan. The covariation organ is closest
to the "readily available general knowledge" reservoir that BOTH camps presuppose; it is not the
bridging process itself.

- McKoon & Ratcliff (1992), "Inference during reading," Psychological Review 99:440-466 (minimalist
  hypothesis): the only automatic inferences are those needed for LOCAL COHERENCE or based on
  readily-available information (explicit text OR general knowledge). Bridging causal inferences that
  establish local coherence ARE in the automatic set. Elaborative / predictive / global-goal
  inferences are NOT automatic. [VERIFIED 08-30]
- Graesser, Singer & Trabasso (1994) constructionist: local causal bridges PLUS a wider set of
  goal/explanation inferences, driven by search-after-meaning. [VERIFIED 08-30]
- The debate is now often framed as a false dichotomy for local coherence: local coherence itself
  frequently REQUIRES knowledge-based (constructionist-style) processes. [VERIFIED 08-30 -- multiple
  sources note minimalism mischaracterizes how much local coherence needs knowledge].

Placement of the organ: The organ pre-computes P(effect-type | cause-type)-baseline over a corpus.
That is a good MODEL of the semantic-memory prior both camps invoke as "readily available general
knowledge" -- i.e. it can tell you attack->death is a plausible causal pairing. It does NOT perform
the automatic LOCAL BRIDGE (select a specific mediator, connect THESE two propositions, hold it for
local coherence). Open narrative needs the bridge; the organ supplies the prior.
Status: PINNED (local causal bridging is automatic, knowledge-based). MODELING (mapping the organ to
"the prior, not the bridge"). Deflated P(organ = prior/candidate-generator, not the online bridge) =
0.48.

### Q4. PHYSICAL vs MENTAL/INTENTIONAL causation -- can a covariation organ reach the dominant
### narrative type IN PRINCIPLE?

Verdict: No -- this is the strongest STRUCTURAL reach limit. Fiction is dominated by
intentional/goal-based (motivational + psychological) causation. Intentional causation is computed by
GOAL/PLAN RECOGNITION + THEORY-OF-MIND (mentalizing), where the "cause" is an UNOBSERVED MENTAL STATE
that must be INFERRED and the effect is recognized as a plan-step toward that goal for THIS agent in
THIS situation. That is not an event-type frequency and cannot be recovered by covariation over verb
lemmas.

- Trabasso categories: motivation (M), psychological (Psi), physical (P), enablement (E). Narrative
  causal chains are dominated by motivational/psychological (intentional) links by prevalence
  (goals->actions), even though PHYSICAL links carry the highest per-link counterfactual STRENGTH
  ratings (physical > motivational > psychological > enabling; Trabasso & van den Broek 1985). Do not
  confuse per-link strength with prevalence: fiction has MORE intentional links. [VERIFIED 08-30 for
  the strength ordering; BACKGROUND for "intentional dominates by count" -- well-established in the
  causal-network literature but not re-counted this session].
- Intentional-causation mechanism = goal/plan recognition (Schank & Abelson scripts/plans/goals;
  Schank dynamic memory) + theory-of-mind / mentalizing. Neurally, mentalizing = medial PFC + TPJ +
  precuneus; note Feng et al. (2021) found bilateral mPFC in the discourse-causal network, and the
  mentalizing meta-analysis overlaps mPFC/MTG. So the brain recruits a mentalizing substrate for
  discourse causation -- consistent with intentional causation being a mentalizing computation, not a
  covariation lookup. [VERIFIED 08-30 for Feng regions + mentalizing overlap; the causal
  interpretation is MODELING].
- Physical/outcome causation = counterfactual mental simulation. Gerstenberg, Goodman, Lagnado &
  Tenenbaum, "A counterfactual simulation model of causal judgments for physical events,"
  Psychological Review (2021); Gerstenberg (2024) review "Counterfactual simulation in causal
  cognition." Causal judgment tracks whether the outcome WOULD HAVE DIFFERED without the candidate
  cause, via situation-specific mental simulation -- again token-level, not type-frequency. [VERIFIED
  08-30].

Structural prediction: A covariation-over-event-types organ CANNOT capture intentional causation in
principle, because (a) the cause is an unobserved GOAL that must be inferred (mentalizing), not
observed as an event token to be counted, and (b) the causal license is plan-coherence for a specific
agent/goal/situation, not a type co-occurrence. Example: "John wanted the book. He went to the
library." The link want->go-to-library is not a high-frequency verb-type covariation; it is inferred
by recognizing the library as a place to obtain books and going-there as a plan step for John's goal
here. Verb-type covariation (want->go) is far too coarse and context-free.
Status: PINNED (intentional causation is mentalizing/plan-based in theory; physical is
counterfactual-simulation-based). The claim "organ CANNOT reach intentional causation in principle" =
MODELING/SYNTHESIS, but strong. Novel-synthesis cap -> P = 0.50. This is the load-bearing
structural-limit claim; it is the one to TEST directly (see Q5 intentional-vs-physical split).

### Q5. THE VALID TEST + GLASS-BOX BRIDGING IMPLEMENTATION

Two parts: (a) a valid transfer test that avoids the confounds the solver hit; (b) if bridging is
needed, a glass-box non-LLM sketch.

#### (a) Valid-test corpora (annotate IMPLICIT, connective-less, EVENT-level causal relations)

Ranked for THIS question:

1. GLUCOSE (Mostafazadeh et al. 2020, EMNLP), "GeneraLized and COntextualized Story Explanations."
   Built on ROCStories (5-sentence everyday stories). ~670K entries; 10 dimensions of causal
   explanation (causes/enables/motivates/results-in over events, states, motivations, emotions). KEY
   PROPERTY: every entry pairs a STORY-SPECIFIC causal statement WITH a GENERALIZED inference rule.
   This operationalizes the covariation-vs-bridging distinction DIRECTLY: the "general rule" is the
   type-level (covariation-predictable) form; the "specific statement" is the situation form.
   [VERIFIED 08-30]. BEST corpus for the discriminator.

2. CaTeRS (Mostafazadeh et al. 2016, NAACL Events workshop), "Causal and Temporal Relation Scheme."
   320 ROCStories / 1600 sentences; 9 causal + 4 temporal relation classes; annotated from a
   COMMONSENSE-REASONING perspective "rather than starting from linguistic markers" (i.e. it captures
   CONNECTIVE-LESS/implicit causal relations) with high IAA (0.74-0.96). Gives EVENT SPANS + both
   causal AND temporal-only labels -> a clean WITHIN-CORPUS, SAME-POPULATION causal-vs-temporal
   discriminator (exactly what the withdrawn cross-genre test lacked). [VERIFIED 08-30]. BEST corpus
   for the causal-vs-temporal edge-detection floor.

3. EventStoryLine / ESC v1.0 (Caselli & Vossen 2017). News; 22 topics, 258 docs, 5334 event
   mentions, 5625 causal event pairs; explicit + implicit, event-level. Genre = news (physical/event
   causation), NOT fiction -- use as a PHYSICAL-causation comparison arm, not the narrative arm.
   [VERIFIED 08-30].

4. PDTB implicit Contingency.Cause (Penn Discourse Treebank 2.0). WSJ; where NO connective is
   present, annotators INSERT an implicit connective ("because") -> a large source of connective-less
   causal pairs. Caveat: annotation is at the ARGUMENT-SPAN level, not the event-head level, so you
   must extract event heads yourself (partial re-introduction of the confound). Secondary. [VERIFIED
   08-30].

5. CausalTimeBank (Mirza & Tonelli 2014); RED / Richer Event Description (O'Gorman et al. 2016,
   CAUSE + PRECONDITION at event level); BECauSE 2.0 (Dunietz et al. 2017, construction-based, mostly
   EXPLICIT connectives). [BACKGROUND -- named for completeness, not re-verified this session]. RED
   is attractive (event-level CAUSE vs PRECONDITION mirrors the organ's own type distinction) but
   verify availability before committing.

AVOID: McGuffey and Anne of Green Gables via root-verb extraction (the withdrawn test). Those are
(i) explicit-connective populations and (ii) the extractor returned matrix/copula/mental verbs, not
causal-event verbs -- two confounds. Do not re-run that instrument.

#### (a-cont.) Extraction + task + floors (design-gate compliant)

- Extraction: USE THE CORPUS-ANNOTATED EVENT HEADS (CaTeRS event spans; GLUCOSE cause/effect event
  phrases). Do NOT use root-verb heuristics. This single change fixes the extraction confound.
- Task: binary CAUSAL vs TEMPORAL-ONLY edge classification at the event-pair level, WITHIN CaTeRS
  (same population, both label classes present) -- a can-fail, one-variable discriminator with a real
  in-distribution baseline.
- Floors the organ must beat (report CI half-width + null p95 beside each margin):
  1. Chance (0.5 AUC).
  2. Verb-lemma PMI / co-occurrence floor (the Kuperberg control at the organ's own granularity):
     does the organ beat raw event-word co-occurrence? If not, it is only measuring association.
  3. Temporal-adjacency floor (label all adjacent pairs causal).
  4. Type-frequency positive control: the organ's OWN prior with the specific tokens STRIPPED. For a
     genuine covariation model this should NOT lose much -- confirms the organ is behaving as a
     covariation model and localizes where any token-level signal would have to come from.
- THE KEY SCIENCE (discriminator that tests the structural claim), one variable:
  Split the CAUSAL links into (a) GENERAL-RULE-BACKED (the pair instantiates a high-frequency GLUCOSE
  general rule / high event-type contingency) vs (b) SITUATION-SPECIFIC / NOVEL (low type-frequency;
  requires the specific circumstances). PREDICTION from this drill: AUC(general) >> AUC(specific),
  with AUC(specific) ~ chance. If confirmed, that is a positive, can-fail demonstration of the
  structural reach limit: covariation captures the encyclopedic prior and misses situation-specific
  bridges. This is the single highest-value experiment.
- SECOND discriminator (tests Q4 directly): split CAUSAL links by Trabasso category
  (motivational/psychological/intentional vs physical/enabling; CaTeRS classes and GLUCOSE dimensions
  map onto these). PREDICTION: covariation organ AUC(intentional) << AUC(physical). If confirmed,
  intentional causation is empirically out of reach for the covariation mechanism.

Status: DESIGN (not a truth claim). Whether the organ passes/fails is the experiment. The two
predictions above are the falsifiable content. Deflated P(the general-vs-specific split will show the
predicted gap) = 0.55 -> capped/deflated to 0.50 (strong prior from theory, but unproven on THIS
organ and corpus).

#### (b) Glass-box, non-LLM bridging mechanism (if bridging is needed)

Purpose: an organ that does what covariation cannot -- construct and situation-validate a specific
mediating proposition -- while staying glass-box (every step inspectable) and using NO external LLM at
inference. Foundation KBs are external tools built FULL + VETTED offline as a static asset, which the
PIVOT admits.

Components:
1. Event linker. Map each story event (predicate + arguments) to KB nodes: ConceptNet phrase nodes +
   ATOMIC event templates ("PersonX <verb> ..."). Lexicalized, inspectable.
2. Mediator constructor (bridge search). For cause-event A and effect-event B, search a 1-2 hop path
   A -> m -> B over CAUSAL-TYPED KB edges. The mediator m is the explicit MISSING PREMISE (the
   Singer-Halldorson syllogism middle term) -- glass-box, because you can print the exact KB triple
   that licensed the bridge.
   - Physical/result edges: ConceptNet Causes, HasPrerequisite, UsedFor; ATOMIC xEffect / oEffect.
   - Intentional/goal edges (this is the part covariation cannot do): ConceptNet MotivatedByGoal
     (~12K triples), CausesDesire (~1K), plus ATOMIC xIntent / xWant / xNeed. These encode
     goal/plan-recognition-lite: does B serve a goal that A creates or reveals? [ConceptNet relation
     inventory + counts VERIFIED 08-30; ATOMIC 9 if-then relations VERIFIED 08-30].
3. Situation validator (what makes it TOKEN-grounded, not type-covariation).
   - Selectional / argument-consistency: the entities in A and B must satisfy the mediator's slots
     (the agent whose goal is in A is the actor of B; the object of A is the thing acted on in B).
     This is the "in the circumstances of THIS story" test.
   - Counterfactual-necessity proxy (cheap Trabasso analog): remove A; is there ANOTHER
     already-present event in the local situation graph that licenses B via the KB? If yes, A is not
     necessary -> downweight. Glass-box and situation-specific.
4. Score = path-existence x path-reliability (edge weights) x validator-pass. Every factor
   inspectable; the organ can REFUSE a high-type-frequency pair when the situation blocks it, and
   ACCEPT a novel pair never seen in any corpus when a KB path + situation-consistency exist.

Operational contrast with the covariation organ (the crux):
- Covariation organ: outputs a SCALAR contingency over TYPES, P(effect-type | cause-type)-baseline,
  computed OFFLINE over a corpus, IGNORING the specific entities. Cannot license a novel pair; cannot
  block a frequent pair the situation forbids; no mediator.
- Bridging organ: outputs a TOKEN-GROUNDED PATH (A -> named mediator -> B) whose validity depends on
  THIS story's entities and local situation graph. Exactly the two capabilities covariation lacks.
The clean division of labor: the covariation organ REMAINS the general-knowledge prior /
candidate-edge scorer feeding step 2 (it ranks which mediators/pairs are a priori plausible); the
bridge does construction + situation validation on top. This is Kintsch's construction (associative
prior) + integration (constraint satisfaction) split, made mechanical.

Status: MODELING (feasibility). A non-LLM ConceptNet+ATOMIC bridger that beats the co-occurrence
floor is plausible but UNPROVEN. Deflated P(such a glass-box bridger beats the Kuperberg/co-occurrence
floor on GLUCOSE/CaTeRS situation-specific links) = 0.40. Known risks: KB coverage gaps and
entity/event linking noise (the same class of failure that broke the withdrawn test if done sloppily);
mitigate by scoring only pairs where BOTH events link to KB nodes and reporting coverage explicitly.

--------------------------------------------------------------------------------
## EXPLICIT STATEMENT: IS THE COVARIATION ORGAN THE RIGHT MECHANISM?

(i) RECURRING-EVENT-TYPE / ENCYCLOPEDIC PHYSICAL CAUSATION -- YES, right mechanism. Power-PC +
causal-support over event types is exactly the normative computation for "how strongly does cause-type
raise effect-type," and this is what the MAVEN-ERE win measured. It maps onto the semantic-memory
stream (left MTG in Feng 2021). KEEP and PIN for this regime. [PINNED for the regime; the organ's win
is real for it.]

(ii) OPEN NARRATIVE CAUSATION -- NO, not as the primary computation; YES as a necessary component.
The covariation organ can serve as the general-knowledge PRIOR / candidate-bridge generator, but the
narrative causal edge itself requires: (b1) constructing a SPECIFIC mediating proposition
(Singer-Halldorson), (b2) validating it against the situation's tokens and circumstances (Trabasso
counterfactual-in-the-circumstances), and (b3) for the DOMINANT intentional type, inferring an
unobserved goal + recognizing plan-coherence (mentalizing / goal-plan recognition). The organ
STRUCTURALLY CANNOT reach (b2) or (b3). Therefore: necessary (the prior) but not sufficient (the
mechanism). Where it structurally cannot reach: any causal edge that is (1) situation-specific / novel
at the type level, or (2) intentional/goal-based. These two classes are the majority of open
narrative causation.

--------------------------------------------------------------------------------
## TLDR

The brain does not decide "did event A cause event B?" in a story by looking up how often that kind of
event causes that kind of event. It builds a specific little explanation -- "A led to B because of
this in-between fact" -- and checks that explanation against what it knows about the world AS IT
APPLIES TO THESE CHARACTERS IN THIS SITUATION. The best brain evidence: when researchers carefully
matched how often the words tend to appear together and STILL found a brain signature of causal
connection, showing the brain uses more than word-level association. And most story causation is about
WHY a character did something (their goals) -- which needs mind-reading, not counting. So our existing
"how often does this cause that" tool is the RIGHT tool for encyclopedic, repeat-pattern physical
causation (its recent win), and a USEFUL INGREDIENT for stories, but it cannot BE the story-causation
mechanism by itself. To test this cleanly we should use commonsense-story datasets that mark the
actual cause/effect events (GLUCOSE, CaTeRS) instead of the mis-extracted classic-literature text that
produced the withdrawn result, and specifically compare "general-rule" causal links (which counting
should get) against "specific-situation" links (which it should miss).

## QUESTIONS

None for the solver's substrate direction. One flag for whoever cites this drill: do NOT state
"Kuperberg 2011 refutes the covariation organ" -- Kuperberg matched WORD co-occurrence, and the organ
uses the richer event-type contingency; Kuperberg refutes only surface-association accounts. The
organ-specific limit rests on the Trabasso/Singer/Graesser structural argument, with Kuperberg as
corroboration.

## NEXT STEPS (for the solver to implement; this drill does not run them)

1. Build the VALID test on CaTeRS: causal-vs-temporal-only edge classification using the ANNOTATED
   event heads (not root verbs); floors = chance, verb-lemma co-occurrence (Kuperberg control at the
   organ's granularity), temporal-adjacency. Same-population, can-fail, one-variable.
2. Run THE discriminator on GLUCOSE: split causal links into general-rule-backed vs
   situation-specific; predict AUC(general) >> AUC(specific) ~ chance. This is the highest-value cell
   -- it turns the structural claim into a falsifiable measurement.
3. Run the Q4 split: intentional (motivational/psychological) vs physical/enabling causal links;
   predict AUC(intentional) << AUC(physical).
4. If (2)/(3) confirm the reach limit, prototype the glass-box bridging organ (event linker + KB
   mediator search over ConceptNet Causes/HasPrerequisite/MotivatedByGoal/CausesDesire + ATOMIC
   xIntent/xWant/xNeed, with a selectional + counterfactual-necessity situation validator), keeping
   the covariation organ as the prior/candidate scorer. Gate it on beating the co-occurrence floor on
   the situation-specific links.
5. Report every margin with CI half-width + null p95, recomputing each floor on the item's own
   population/representation (measurement bar).

--------------------------------------------------------------------------------
## PRIMARY SOURCES (verified this session unless flagged BACKGROUND)

- Kuperberg, Paczynski & Ditman (2011). Establishing causal coherence across sentences: an ERP study.
  J. Cognitive Neuroscience 23:1230-1246.
  https://projects.iq.harvard.edu/kuperberglab/publications/establishing-causal-coherence-across-sentences-erp-study
- Kuperberg (2016). Separate streams or probabilistic inference? What the N400 can tell us about the
  comprehension of events. Language, Cognition and Neuroscience. (title BACKGROUND; dual-stream framing
  VERIFIED). https://kuperberglab.com/publications/
- Singer, Halldorson, Lear & Andrusiak (1992). Validation of causal bridging inferences in discourse
  understanding. J. Memory & Language 31:507-524.
  https://www.sciencedirect.com/science/article/abs/pii/0749596X9290026T
- Trabasso & van den Broek (1985). Causal thinking and the representation of narrative events.
  J. Memory & Language. https://www.sciencedirect.com/science/article/abs/pii/0749596X8590049X
  (and Trabasso, van den Broek & Suh 1989, Discourse Processes, causal-network model).
- Graesser, Singer & Trabasso (1994). Constructing inferences during narrative text comprehension.
  Psychological Review 101:371-395. https://pubmed.ncbi.nlm.nih.gov/7938337/
- McKoon & Ratcliff (1992). Inference during reading. Psychological Review 99:440-466.
  https://pubmed.ncbi.nlm.nih.gov/1502273/ ; PDF:
  https://bpb-us-w2.wpmucdn.com/u.osu.edu/dist/6/60429/files/2018/07/psychrev92a-y8qm4a.pdf
- Gerstenberg, Goodman, Lagnado & Tenenbaum (2021). A counterfactual simulation model of causal
  judgments for physical events. Psychological Review. https://cicl.stanford.edu/papers/gerstenberg2021csm.pdf
  ; Gerstenberg (2024) review. https://cicl.stanford.edu/papers/gerstenberg2024counterfactual.pdf
- Feng et al. (2021). Neural correlates of causal inferences in discourse understanding and logical
  problem-solving: a meta-analysis (ALE). Left IFG + left MTG + bilateral mPFC.
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8261065/
- Kintsch (1988). The role of knowledge in discourse comprehension: a construction-integration model.
  Psychological Review 95:163-182. [BACKGROUND -- not re-verified this session].
- CaTeRS: Mostafazadeh, Grealish, Chambers, Allen & Vanderwende (2016). Causal and Temporal Relation
  Scheme for Semantic Annotation of Event Structures. NAACL Events workshop.
  https://aclanthology.org/W16-1007/
- GLUCOSE: Mostafazadeh, Kalyanpur et al. (2020). GeneraLized and COntextualized Story Explanations.
  EMNLP. https://aclanthology.org/2020.emnlp-main.370/
- EventStoryLine / ESC v1.0: Caselli & Vossen (2017). The Event StoryLine Corpus. Events & Stories in
  the News workshop. https://aclanthology.org/W17-2711/
- PDTB 2.0 (implicit Contingency.Cause via inserted connectives). PDTB Research Group.
  https://catalog.ldc.upenn.edu/LDC2008T05 (annotation manual:
  https://projects.csail.mit.edu/workbench/update/guides/10%20-%20Discourse%20Relations%20Detailed%20Guide.pdf)
- ATOMIC: Sap et al. (2019). ATOMIC: An Atlas of Machine Commonsense for If-Then Reasoning. AAAI.
  877K if-then; 9 relations (xIntent, xNeed, xAttr, xEffect, xWant, xReact, oEffect, oWant, oReact).
  https://arxiv.org/pdf/1811.00146 (ATOMIC-2020: Hwang et al. 2021, BACKGROUND).
- ConceptNet 5.5: Speer, Chin & Havasi (2017). Relations Causes, CausesDesire, HasPrerequisite
  (~4.2K), MotivatedByGoal (~12K), CausesDesire (~1K), UsedFor. https://ar5iv.labs.arxiv.org/html/1612.03975
- Schank & Abelson (1977). Scripts, Plans, Goals and Understanding. [BACKGROUND].
- Cheng (1997) power-PC; Griffiths & Tenenbaum (2005) causal support. [BACKGROUND -- the organ's own
  basis; established in prior drill research_covariation_causal_inference_mechanism_2026-08-30.md].
