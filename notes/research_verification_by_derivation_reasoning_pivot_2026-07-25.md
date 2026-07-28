# Research: verification-by-derivation — reasoning over ARC candidate answers (design drill)

**Date:** 2026-07-25
**Role:** research (direct, no child sub-agent per Director instruction), tight design-oriented drill
**Serves:** atom 29549 (VET-CONFIRMED root cause: the whole retrieve->select->combine ARC pipeline is
SIMILARITY all the way down at confidence ~0.72; it never reasons — 7 consecutive selection HARD_FAILs
across fixed/learned/relational/answer-conditioned/set-level signals all trace to the same cause).
USER-directed pivot (decisive, twice): "of COURSE we need to reason — that's the whole goal here."

---

## 0. KB-check (done before drilling; per [[feedback-kb-check-before-dispatch]])

`bash tools/substrate_query.sh` run twice:
- "reason derive candidate answer inference chain forward backward chaining entailment proof" -> top
  hit cosine=0.36, `notes/research_drill_brain_multihop_M3_bidirectional_meet_in_middle_3x_2026-06-27.md`
  section 3.2, which had ALREADY flagged (2026-06-27, one month before this pivot): *"A 'proof-search'
  variant would prune Z's that have no path-to-S in the W matrix support... new cell candidate."* This
  drill was never built. It is the closest direct ancestor of this design and is treated as the primary
  precedent below, not a fresh idea.
- "verify hypothesis answer model based reasoning mental simulation" -> top hit cosine=0.33, noise-level
  (WordNet "mental stimulation" typo-entity, an unrelated MWP-mechanism-classes note). **No prior KB
  drill directly answers "how does the brain verify a candidate answer by derivation."** Confirmed new
  ground for THIS specific question.

Also read in full (not re-drilled, cross-referenced in section 6): `research_holistic_set_selection_
2026-07-25.md` (Kintsch CI / ECHO / Usher-McClelland competitive accumulator, reused here), `research_
drill_answer_conditioned_selection_biology_2026-07-25.md` (PFC goal-biased retrieval, reused here),
`research_relational_grounded_meaning_relevance_wall_2026-07-24.md` (RotatE/Tversky/DistMult asymmetry
argument, reused here), `research_content_thin_concept_meaning_featural_enrichment_2026-07-25.md`
(concept-content sparsity, flagged as a residual risk to node-unification below), and the director
backup doc's live pipeline-state line (atom 29549 lineage) confirming the exact baseline numbers used
throughout (~0.36-0.38 current best similarity pipeline; 0.687-0.71 oracle-given-gold-set; 0.25 chance).

**How this build differs from the 5 prior selection attempts (fixed/learned/relational/answer-cond/set-
level), all HARD_FAIL:** every prior attempt kept the SAME core operation — score something (a fact, a
fact-set, a fact-conditioned-on-a-choice) by a similarity/cosine-derived number and threshold or rank it.
This design replaces scoring with SEARCH: does a chain of TYPED, DIRECTIONAL rule-applications connect
the question's givens to the candidate answer at all? Existence-of-a-valid-derivation is a different
KIND of quantity than any similarity score, however cleverly conditioned — this is the actual novel
variable, not a relabeled 6th similarity feature.

---

## 1. Disk-verified state of the "already have" pieces (before designing on top of them)

Checked directly, not assumed:

- **Typed rule-facts are REAL and already parsed once.** `data/corpora/worldtree/.../tablestore/v2.1/
  tables/*.tsv` contains 81 tables. Confirmed header + sample rows for the causal/conditional ones:
  `IFTHEN.tsv` (508 rows, e.g. "if a disease can be prevented by eating a certain kind of food then that
  disease is probably caused by a nutritional deficiency" — a genuine universally-quantified rule with
  arg0/arg1 coreference), `CAUSE.tsv` (381 rows, e.g. "acid ... causes ... chemical change" — a grounded
  directional causal fact usable directly as an inference step), `REQUIRES.tsv` (216 rows), `COUPLED
  RELATIONSHIP.tsv` (253 rows, comparative co-variation rules: "as roughness of a surface increases,
  friction will increase"). Taxonomic/compositional tables (`KINDOF.tsv` 2137 rows, `PARTOF.tsv` 236,
  `USEDFOR.tsv` 338, `MADEOF.tsv`, `SOURCEOF.tsv`) are not causal-inferential but are still usable as
  premise-linking / property-inheritance steps.
- **A typed parser already exists and is reusable as-is:** `experiments/exp_arc_selection_relational_
  meaning_v1.py::parse_tablestore_typed()` parses every tablestore TSV into `uid -> {relation, arg0,
  arg1, confident}` (confirmed at lines 262-361 of that file). This is the exact "rule-application step"
  substrate the task asks for — it does NOT need to be rebuilt, only reused with a different consumer.
- **Directional role-bind primitive already exists:** `hdlab/event_bundle.py::EventBundleCodec` (ARG0/
  ARG1 role keys) plus `bind_bundle()` in the relational-meaning cell — used previously only to produce
  ANOTHER similarity feature (HARD_FAIL, atom 29546); reusable here for the DIFFERENT purpose of
  unifying a rule's arg1 filler with the next rule's arg0 filler across a chain (transitivity check).
- **A contradiction/consistency mechanism already exists:** `experiments/exp_arc_aggregation_polarity_
  ci_v1.py` (`PolarityLexicon.contradicts`, `_ci_two_phase_pol`, `aggregate_pol`) — a Kintsch-CI-style
  settling network with antonym/negation-based inhibitory edges. This is the "conflict-monitor" the task
  references; reusable as the chain-consistency check (section 3.3 below) rather than rebuilding one.
- **A proven bidirectional meet-in-the-middle SEARCH SHAPE already exists and is chain-grade in
  production** (`substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail`, HARD_PASS at depth-5,
  top1=0.620 vs forward-only 0.323, per the M3 note). It was built for dense pointer-chain W-matrix
  multihop, not a typed sparse KG — but the SEARCH ALGORITHM (forward from S, backward from T, meet via
  cosine, argmax) is exactly the shape this design needs, now applied to a typed graph instead of a dense
  matrix. This is a second independent substrate precedent (in addition to the theorem-proving/AI-search
  literature below) that forward+backward meeting is a working substrate-native mechanism, not a new bet.
- **What could NOT be verified on disk:** the backup doc references "the READER = comprehension ->
  structured claim" and "khop.py + trustworthy-reader gate (29465)" as existing but unwired primitives.
  Searched by filename (`*khop*`, `*reader*.py`) across the full repo — neither was found. Either they
  live under different names than cited, or the reference is to conceptual/planned work not yet landed
  as a discoverable file. **Flagged honestly: do not assume a dedicated comprehension-reader module
  exists as wired infrastructure.** The nearest working substitute for "parse the question into givens"
  is the plain content-word extraction already used in `exp_arc_knowledge_scale_ingest_climb_v1.py::
  _content_words()` plus `SemanticHDEncoder` cosine matching — cruder than a real structured-claim
  parser, but real and on disk. The design below is specified against what verifiably exists.

---

## 2. Biology first: how does the brain verify a candidate answer by REASONING?

### 2a. Forward vs. backward chaining — the brain uses both, and verification-of-a-given-candidate is
specifically a BACKWARD-chaining setting (well-grounded, converging evidence, not speculative)

Classical AI (Russell & Norvig, *AIMA* ch. 9) formalizes forward chaining as data-driven (facts+rules ->
conclusions) and backward chaining as goal-driven (goal -> rules -> required facts), and notes production
systems (OPS5, SOAR) combine both because forward alone explodes combinatorially and backward alone can
loop without anchoring in known facts. This AI-theoretic framing has a direct cognitive-science mirror:
forward chaining is associated with fast, reactive, bottom-up associative inference from new input, while
backward chaining models slower, deliberate, goal-oriented processing — and human reasoning empirically
uses both, not one exclusively.

Biologically, **backward/goal-directed chaining specifically implicates PFC**: Tanji & Hoshi (*Physiol.
Rev.* 2008, already in KB from the M3 note) show PFC supports backward chaining from goals / means-end
analysis during problem-solving, and PFC-damaged patients cannot work backward from a goal. This is
directly on-point: **verifying a GIVEN candidate answer is structurally a goal-directed / backward-
chaining task** — the "goal" (the candidate) is already fixed; the question is only whether known facts
license reaching it. This is different from open-ended forward exploration from the question alone.

Two theories of *how* humans do the deduction itself, both real and only partially reconciled in the
literature — the design below does not have to choose between them, because they map onto two different
sub-steps we already need:

- **Mental-model theory (Johnson-Laird)**: reasoners construct explicit mental MODELS of the possibilities
  compatible with the premises; a conclusion is valid iff it holds in ALL such models, and reasoners
  (when competent enough) search for COUNTEREXAMPLES — a model compatible with the premises but not the
  candidate conclusion — to falsify an invalid inference. This is fundamentally a model-checking /
  simulate-and-inspect account, not a symbol-manipulation account.
- **Mental-logic / natural-deduction theory (Rips, *The Psychology of Proof*; PSYCOP)**: deduction depends
  on the ability to make suppositions, posit sub-goals, and construct an explicit mental PROOF — a chain
  of applications of ~50 inference rules linking given information to a conclusion it warrants. This is a
  symbolic rule-chaining account, structurally identical in shape to what forward/backward chaining over
  typed rules already is.

**Design implication:** these two theories are not a contradiction to resolve before building — they
correspond to the two halves this design already needs: **Rips'-style rule-chaining IS the derivation
search** (section 3.2 below: chain typed IFTHEN/CAUSE/REQUIRES rules as licensed proof steps), and
**Johnson-Laird's-style model-checking IS the consistency/counterexample check** (section 3.3: does the
assembled chain, read as a small situation model, contain a contradiction — exactly what the already-
built polarity/CI settle machinery computes). Implementing both as complementary mechanisms is the
honest reading of an unresolved-in-the-literature debate, not a hedge.

### 2b. Proof/derivation vs. mere association — how the brain avoids "it's all connected"
(well-grounded, converging evidence from 4 independent literatures)

This is the crux the task specifically asks to ground, because it is the exact failure atom 29549 named
(similarity != entailment). Four independent lines of evidence converge on the same answer: **a valid
inference step must be TYPED/DIRECTIONAL and GATED to one licensed application at a time — undirected,
parallel, symmetric spreading activation cannot do this by construction.**

- **Structured relational binding, not flat similarity (Hummel & Holyoak, LISA — *Psychological Review*
  2003).** LISA solves the binding problem for relational structure using temporal synchrony: role
  (agent/patient) and filler (who/what) are bound by firing together, keeping role-content and filler-
  content in representations that preserve DIRECTIONAL structure ("X causes Y" is not "Y causes X," and
  is not the same representation as "X and Y co-occur"). This is a real, primary-source-confirmed
  computational-neuroscience account of exactly the "structure vs. flat similarity" distinction the task
  asks about, and is the same mechanism-class already cited in the substrate's own relational-meaning
  note (RotatE/Tversky/DistMult, atom 29546) — now reused for a different purpose (chaining, not scoring).
- **Systematicity: connected relational structure is privileged over isolated matches (Gentner 1983;
  Gentner & Toupin 1986, *Cognitive Science*; Gentner & Markman, structure-mapping).** A relation that
  belongs to a mappable SYSTEM of mutually-constraining relations (a causal chain, a chain of
  implications) is far more likely to be imported/trusted than an isolated, unconnected relational match.
  This is a direct, citable justification for scoring a MULTI-STEP CHAIN higher than a single lucky
  topical overlap — connectedness itself is evidence, isolated similarity is not. Directly answers "how
  do you not let a single similar-sounding fact carry the same weight as a genuine derivation."
- **Relational integration recruits a specific, capacity-limited PFC circuit (rostrolateral PFC / area
  10; Waltz, Knowlton & Holyoak, *Psychological Science* 1999 — "A System for Relational Reasoning in
  Human Prefrontal Cortex"; Christoff et al. and related work on a PFC hierarchy for relational
  reasoning).** Integrating multiple relations simultaneously is a distinct, effortful, anatomically
  localized process — not a side-effect of generic associative spreading activation, which by definition
  has no such capacity limit or dedicated circuit. This is direct biological evidence that structured
  multi-relation integration is a DIFFERENT KIND of computation from associative spread, implemented in
  different tissue.
- **Serial, gated rule application — not diffuse parallel activation (ACT-R production-rule theory;
  Anderson, *Psychological Review* 2004; Stocco et al. on basal ganglia).** In the ACT-R account (itself
  grounded in basal-ganglia circuitry, not purely a software analogy), the striatum performs pattern
  recognition over which rules currently match, the pallidum performs conflict resolution via broad
  inhibition, and the thalamus gates through only ONE winning rule per cycle — a winner-take-all circuit.
  This directly explains, mechanistically, why "everything connects to everything" does not paralyze
  reasoning: only one licensed rule fires per step, chained serially, not all matching associations
  acting at once.
- **Directional causal structure vs. symmetric association (Pearl; "explaining away").** Pearl's causal
  Bayesian-network formalism shows that genuinely causal/directional reasoning (e.g., "explaining away":
  confirming one cause of an observed effect makes a rival cause LESS credible) requires bidirectional
  information flow over a DIRECTED graph and is explicitly noted in the literature as "difficult to model
  naturally in rule-based systems and neural networks... because it seems to require propagation in two
  directions" — i.e., even the classical AI/connectionist literature flags that symmetric association
  cannot reproduce directional causal inference; you need the directionality as a first-class structural
  fact, not an emergent property of similarity magnitude.

**Conclusion, converging across all four:** the brain-grounded and AI-grounded answer to "how do you
avoid it's-all-connected" is (i) edges must be TYPED and DIRECTIONAL (not generic similarity edges),
(ii) rule application is SERIAL and GATED — one step licensed at a time, not parallel diffuse spread,
(iii) CONNECTED multi-step structure is itself evidence (systematicity), privileged over isolated
matches. All three map directly onto concrete, checkable properties of the build in section 3.

### 2c. Mental simulation as a complementary check (well-grounded for the general claim; the SPECIFIC
tie to Kintsch's own theory is our synthesis, flagged as such)

Barsalou's perceptual symbol systems account and the broader embodied-simulation literature show the
brain re-enacts perceptual/motor states to verify situational claims (e.g., picture-verification tasks:
readers form perceptual-like situation models from sentences, and response times reflect a match/mismatch
between the simulated state and a subsequently shown picture). This is real, biology-grounded evidence
for a SIMULATE-AND-CHECK verification step distinct from symbolic chaining.

**Direct, non-metaphorical connection to a primitive already in this substrate:** Kintsch's own theory
(already reused in this substrate via the polarity/CI module) explicitly distinguishes a shallow TEXT-BASE
layer from a deeper SITUATION MODEL layer — the CI settling process is literally Kintsch's own name for
constructing that situation model. This means the substrate's existing polarity/CI settle is not merely
ANALOGOUS to mental simulation — it is, by the primary theory's own terminology, a computational
instantiation of the same construct. Reusing it as the chain-consistency check (section 3.3) is therefore
a stronger claim than "these two mechanisms are similar," though flagged: this equivalence is the
research's own reading of Kintsch's terminology, not a claim independently made by Barsalou or any
embodied-cognition source — the bridging is OUR synthesis.

### 2d. Competitive verification across N candidates (well-grounded, direct reuse of same-day KB findings)

Already established in same-day prior drills and reused here rather than re-derived: Usher & McClelland's
leaky competing accumulator, Wang/Wong-Wang attractor models, and Albantakis & Deco's N-alternative
extension show the brain evaluates several live hypotheses in parallel under mutual inhibition and reads
the decision off the MARGIN between the current leader and its closest rival, not any candidate's
absolute score alone. Thagard's ECHO formalizes the same idea for explanatory hypotheses specifically:
rival hypotheses are linked by INHIBITORY edges in one settling network. Combined with 2b's basal-ganglia
gating (only one thing wins per cycle) and 2a's Johnson-Laird counterexample search, the composite
picture for 4-candidate verification is: **run derivation search for all 4 candidates; among those with
a complete, non-contradictory chain, prefer the shortest/most-connected (systematicity) one; if exactly
one candidate derives and the others provably do not, that is the strongest possible verdict (a
counterexample was found for the rivals); if none or multiple derive, fall back to existing similarity
combiner as a tie-break of last resort** (this fallback path is a pragmatic engineering choice, not a
literature claim, and is flagged as such in section 3.5).

---

## 3. Concrete build design: VERIFICATION-BY-DERIVATION

### 3.1 What stays UNCHANGED (reuse, do not rebuild)

- `parse_tablestore_typed()` (relational-meaning cell) — typed relation/arg0/arg1/confidence extraction.
- `agg.parse_tablestore()` / `agg._TABLES`, the wide RR retrieval pool (`mr.reformulate_seeds`), and the
  bundle combiner (`agg.aggregate('bundle')`) — kept as the FALLBACK path when derivation is inconclusive.
- `EventBundleCodec` ARG0/ARG1 role keys (`hdlab/event_bundle.py`).
- `SemanticHDEncoder` (GloVe+WordNet cosine) — reused ONLY for node unification (fuzzy string matching
  between a rule's arg0/arg1 filler and a question/choice content word), not for scoring the chain itself.
- `PolarityLexicon` / `_ci_two_phase_pol` / `aggregate_pol` (polarity-CI cell) — reused unmodified as the
  chain-consistency check.
- The bidirectional meet-in-middle SEARCH SHAPE from the M3 multihop cell (forward-state, backward-state,
  cosine-meet, argmax) — reused as the SEARCH ALGORITHM template, retargeted from a dense pointer-chain W
  matrix onto the sparse typed KG.

### 3.2 The ONE new mechanism: typed-graph derivation search (this is what changes)

**Graph construction (one-time, per corpus, not per-question):**
- Nodes = normalized content-word/noun-phrase fillers. Two fillers are the SAME node if
  `cosine(SemanticHDEncoder(filler_a), SemanticHDEncoder(filler_b)) >= tau_unify` (tau_unify a tuned
  threshold, e.g. 0.80-0.90 — start strict; this is a cleanup/unification step, not a relevance score).
- Directed, TYPED edges: for every parsed row `{relation, arg0, arg1, confident}`, add edge
  `arg0_node --relation--> arg1_node`. Split relation types into two classes explicitly, per section 2b's
  "edges must be typed and directional" finding:
  - **LICENSED (causal/conditional/functional — a valid derivation step):** CAUSE, IFTHEN, REQUIRES,
    COUPLEDRELATIONSHIP, SOURCEOF, USEDFOR.
  - **STRUCTURAL (taxonomic/compositional — usable for premise-linking/inheritance, not causal license):**
    KINDOF, PARTOF, MADEOF. A chain may pass through a STRUCTURAL edge to restate an entity at a
    different granularity, but the chain's licensing justification rests on its LICENSED edges.
- Only `confident=True` rows (per the existing typed parser's own confidence flag) are added as edges,
  by default — an explicit coverage/precision tradeoff, revisited in section 5.

**Per-question derivation search (the new step):**
1. Extract GIVENS from the question stem via `_content_words()` (or better, whatever comprehension-parse
   is actually wired — flagged in section 1 as unverified); map each given to its unified graph node(s).
2. For each candidate choice `C_i` (4 per question): extract its content words, map to graph node(s) —
   this is the SEARCH GOAL for that candidate.
3. **Forward search** from givens (BFS over LICENSED+STRUCTURAL edges, depth <= d_fwd) and **backward
   search** from `C_i` (BFS over REVERSED edges, depth <= d_bwd), reusing the meet-in-middle shape from
   the M3 cell: `d_fwd = d_bwd = floor(D/2)` for a max total chain depth D (start D=3-4, matching typical
   WorldTree gold-explanation chain lengths of 2-6 facts).
4. **Meet test:** if the forward-reachable node set and the backward-reachable node set intersect (via
   the SAME `tau_unify` node-identity test, not a fresh similarity score), a valid derivation chain EXISTS
   for `C_i`. Record the actual chain (sequence of typed edges) — this is fully glass-box/inspectable,
   the audit-trail the substrate-product story already leans on for other cells.
5. Repeat independently for all 4 candidates (no shared state between candidates at this stage — this is
   the "run 4 separate searches, then compare" structure per section 2d, not one shared retrieval pool
   scored 4 ways as every prior attempt did).

### 3.3 Chain-quality scoring + consistency check (for when >1 candidate derives)

- **Completeness:** does the chain touch ALL of the question's extracted givens, or just one? (a chain
  anchored to only one given out of three is a weaker derivation — score by fraction of givens covered).
- **Length / systematicity (Gentner):** prefer SHORTER, more connected chains (Occam) over longer ones;
  a longer chain is not automatically worse (per systematicity, a connected multi-step system is GOOD
  evidence) but an unnecessarily long chain when a shorter one exists for a rival is suspicious.
- **Consistency (Johnson-Laird counterexample check / Kintsch situation model, reused unmodified):** feed
  the chain's propositions plus the candidate through `PolarityLexicon.contradicts` / `_ci_two_phase_pol`.
  If the settle detects an internal contradiction (e.g., a chain that both asserts and negates the same
  relation via antonym cues), the chain is REJECTED even if it formally connects givens to candidate —
  this is the "search for a counterexample" step from Johnson-Laird, operationalized with existing code.
- **Selection rule:** if exactly one candidate has a complete, non-contradictory chain, pick it (the
  Johnson-Laird ideal: the others were falsified as underivable or contradictory). If multiple candidates
  derive, pick by completeness first, then chain length, then (last resort) the existing bundle-combiner
  cosine score as tie-break. If NO candidate derives (coverage miss, expected to be common — see honest
  caveat in section 5), fall back entirely to the current best similarity pipeline for that question —
  this fallback is a pragmatic engineering choice, not itself part of the reasoning claim under test.

### 3.4 MUST-FAIL controls (the falsifiability core of this design, directly answering the task's ask)

- **SHUFFLE_DIRECTION control:** build the identical graph but randomly flip arg0<->arg1 on each LICENSED
  edge before running the search. If the mechanism is genuinely using directionality/entailment (not just
  "these two things are graph-nearby"), shuffling direction should COLLAPSE performance toward chance —
  a chain "derived" through scrambled-direction edges is not a valid derivation, it is a random walk over
  a symmetrized graph. This directly operationalizes "similarity != entailment" as a testable prediction.
- **UNTYPED_SIMILARITY_NULL control:** replace the typed/directional edge set with a generic similarity
  graph — an edge exists between any two facts whenever `cosine(fact_i, fact_j) >= tau_sim` (ignoring
  relation type and direction entirely), then run the IDENTICAL forward/backward/meet search algorithm
  over this null graph. This isolates whether any observed lift comes from the SEARCH SHAPE alone (which
  would be a confound — "any 2-hop connectivity check helps," independent of typing) or specifically from
  the TYPED/LICENSED structure. This is the single most important control: it is the exact mechanism the
  task asks to discriminate ("derivation" vs. "spreading activation, everything associates to everything")
  made into a run-able null model rather than a philosophical distinction.
- **RANDOM_CHAIN control:** for questions where a real chain is found for the correct answer, verify a
  chain of the SAME length built from randomly-selected (non-connected) LICENSED edges does not also
  "connect" by the meet test at above-chance rate — a sanity check on `tau_unify` not being so loose that
  nodes spuriously merge.

### 3.5 SHAPE / PLACE / METRIC — per the deep-brain-analysis method, stated explicitly

- **METRIC changes (primary fix, directly per the task's framing):** old metric = resemblance (cosine
  similarity/relevance/coherence/margin — every prior attempt, however conditioned or set-leveled, reduced
  to some flavor of "how similar/relevant is this to the question or choice"). New metric = **derivability**
  — a boolean (chain exists / does not) refined by completeness+consistency, which is not a similarity
  quantity at all; it cannot be computed as any monotonic function of embedding cosine, because a fact can
  be maximally topically similar to a choice and still not license a valid inference step to it (the exact
  dam-question/nuclear-lure failure mode named in the 29546/29549 lineage), and conversely a fact can be
  a valid single step in a chain while being only weakly topically similar in embedding space.
- **SHAPE changes (also primary):** old shape = score-and-threshold over an UNDIRECTED similarity graph
  (however the "graph" was constructed — a flat pool, a conditioned pool, a greedily-built set). New shape
  = **search over a DIRECTED, TYPED graph** for a path connecting two fixed endpoints (givens, candidate),
  a fundamentally different computational problem (graph reachability/path-existence vs. score-and-rank).
- **PLACE is mostly unchanged in pipeline position** (still operates after typed-parse and pool
  construction, before final answer commitment) but changes what it OPERATES OVER: instead of a flat pool
  of retrieved facts scored independently or jointly, it operates over the persistent TYPED GRAPH built
  once from the whole corpus, run per-question as 4 independent point-to-point searches. This is an honest
  middle ground versus claiming a full pipeline reframe — the "retrieve wide pool" step upstream is
  unchanged and still supplies which facts/edges are in scope; only the DECISION mechanism downstream of
  it changes shape and metric.

---

## 4. Cheap decisive test (run BEFORE building the full scored search + backtracking)

Per the design-gate discipline (real baseline, can-fail, one variable, difficulty on): before writing the
full meet-in-middle search + chain-quality scorer, run ONLY the graph-construction + connectivity check:

1. Build the typed graph (LICENSED-only edges, `confident=True` rows) once.
2. Sample ~50-100 ARC-Challenge questions with known gold labels.
3. For each, check depth<=3 forward-from-givens / backward-from-choice connectivity (the meet test, no
   scoring yet) for ALL 4 choices, not just the correct one.
4. Record: (a) **correct-choice coverage** = fraction of sampled questions where the CORRECT choice has a
   depth<=3 chain at all; (b) **selectivity gap** = correct-choice coverage minus mean WRONG-choice
   coverage (do wrong choices also connect within 3 hops, at similar rate? — the direct test of "is the
   typed graph still promiscuously connected regardless of typing"); (c) repeat (a)+(b) with the
   UNTYPED_SIMILARITY_NULL graph (3.4) as a comparison point.

**Why this is decisive and cheap:** it requires no scoring function, no learned weights, no backtracking
pass — only graph construction (reusing `parse_tablestore_typed()` unmodified) and a BFS reachability
check. It answers the single highest-risk question (is there even enough typed-rule material to chain on,
and does typing actually add selectivity over untyped connectivity) before investing in the full search +
scoring + consistency-check build.

**Pre-registered bands for the cheap test:**
- **GREEN LIGHT (build the full search):** correct-choice coverage >= 0.35 AND selectivity gap >= 0.15
  (typed graph) AND the untyped-null-model's selectivity gap is measurably SMALLER than the typed graph's
  (proving typing itself contributes, not just "any 3-hop connectivity happens to work").
- **RED LIGHT / redesign before building:** correct-choice coverage < 0.15 (too sparse — WorldTree's
  ~1,358 causal/conditional rows, see section 5, may simply not reach most ARC-Challenge questions within
  3 hops; the fix would be a coverage-expansion of the LICENSED table set or a deeper hop budget, not
  abandoning the approach) OR selectivity gap < 0.05 for BOTH typed and untyped graphs (the "everything
  is 3 hops from everything" failure reproduced even with typing — would mean depth-3 unification at
  `tau_unify` is too loose and needs tightening, or the underlying entity vocabulary is too small/dense
  for 3-hop connectivity to be informative at all).
- **YELLOW (build a scoped subset first):** coverage adequate but selectivity gap only present for the
  typed graph, not clearly separated from the untyped null — proceed but treat the METRIC claim (not just
  the SHAPE claim) as still open; the full build's HARD-PASS bands (section 6) should weight the untyped-
  null control result more heavily as a gate on whether the typing itself is doing real work.

---

## 5. Honest coverage/sparsity flag (mandatory per the task's own ask)

Counted directly on disk: `IFTHEN.tsv` (508) + `CAUSE.tsv` (381) + `REQUIRES.tsv` (216) +
`COUPLEDRELATIONSHIP.tsv` (253) + `SOURCEOF.tsv` + `USEDFOR.tsv` (338) — on the order of **~1,700-2,000
genuinely causal/conditional/functional rows total across the entire WorldTree corpus**, covering ALL
domains (physics, biology, earth science, chemistry...), against ~2,200 ARC-Challenge-adjacent questions
each needing its own 2-6-fact explanation chain. This is a SMALL, generic rule inventory relative to the
combinatorial space of specific question content — **coverage will very likely be the dominant limiting
factor, not search-algorithm quality.** Two direct consequences for the build, stated up front rather
than discovered after a full build:

1. **Expect a real, possibly large fraction of questions where NO candidate has a typed chain at all**
   (the cheap test in section 4 measures this directly before any further investment). The design already
   accounts for this via the fallback-to-similarity-combiner path (3.3) — the derivation mechanism is
   proposed as a NEW LAYER for questions it can reach, not a full replacement.
2. **Recommend starting the full build ONLY on the coverage subset** (questions where >=1 candidate
   connects within the depth budget) rather than the whole ARC-Challenge test set. Reporting accuracy on
   the coverage subset isolates the mechanism's real quality from the (much larger, and separately
   addressable) coverage problem; whole-set accuracy should ALSO be reported honestly, but the coverage-
   subset number is the one that actually tests the SHAPE/METRIC claim this note argues for.

**A second, subtler honest flag:** node-unification (matching a rule's arg0/arg1 filler string to a
question/choice content word) still runs through the SAME `SemanticHDEncoder` GloVe/WordNet meaning
representation that the 2026-07-24/25 content-thin-concept drills (`research_content_thin_concept_
meaning_featural_enrichment_2026-07-25.md`) showed is too coarse to distinguish fine content (e.g.
hydroelectric vs. nuclear vs. coal, all clustering near "power plant"). If `tau_unify` is set loosely
enough to bridge real paraphrase gaps, it may ALSO silently merge nodes that should stay distinct (merging
"nuclear fuel" and "falling water" into one node because both are near "power plant energy source"),
which would corrupt the graph itself, not just a downstream score. This is a genuine, not hypothetical,
interaction between the still-open concept-content wall and this new mechanism, and should be checked
explicitly at build time (log merged-node pairs above `tau_unify` for manual spot-check before trusting
graph connectivity results).

---

## 6. Falsifiable predictions

**Cheap test (section 4) — HARD-PASS / HARD-FAIL:** see the GREEN/RED/YELLOW bands in section 4 verbatim.

**Full build (only if cheap test is GREEN or YELLOW) — HARD-PASS:**
- On the COVERAGE SUBSET: derivation-based selection reaches ARC-Challenge accuracy >= 0.50, AND beats
  the current best similarity pipeline (~0.36-0.38) by >= 0.10 absolute on the same subset, AND beats
  BOTH must-fail controls (SHUFFLE_DIRECTION, UNTYPED_SIMILARITY_NULL) by >= 0.15 absolute, AND on the
  surface-trap/`chal_lure` subset specifically (lure_rate ~0.23, per the 2026-07-24 brain-QA-architecture
  note) exceeds chance+0.15 — this is the single most important number, since atom 29549 specifically
  showed similarity-based correctness is DECOUPLED from gold-reach on exactly this subset.

**Full build — HARD-FAIL:**
- Derivation-based accuracy on the coverage subset is statistically indistinguishable (within +/-0.05)
  from EITHER must-fail control — meaning the mechanism is not actually using directionality/typing, it
  degenerated back into a connectivity-similarity check with extra steps. OR: no improvement over the
  current baseline specifically on the `chal_lure` subset — meaning the mechanism does not address the
  exact failure mode (surface-lure resistance) it was built to fix, even if it helps elsewhere.

**MIDDLE:** chain-existence is discriminative (beats both controls, beats baseline on `chal_lure`) but
falls short of the 0.50 coverage-subset threshold — real mechanism, insufficient chain-quality scoring or
insufficient coverage; next iteration tunes the completeness/consistency scoring or expands the LICENSED
table set, not abandon the approach.

---

## 7. Cross-thread synthesis with prior entries (per the task's explicit ask)

- `research_drill_brain_multihop_M3_bidirectional_meet_in_middle_3x_2026-06-27.md`: this note's section
  3.2 already named "a proof-search variant" as an un-built new-cell candidate, one month before the
  current pivot's root-cause diagnosis existed. This design is that candidate, now motivated by a much
  stronger diagnosis (atom 29549) than was available in June. The M3 note's PROVEN bidirectional
  meet-in-middle SEARCH SHAPE (0.620 chain-grade at depth-5) is reused directly (section 3.2), giving this
  design a genuine substrate-native precedent that the search ALGORITHM works, independent of whether it
  works on THIS typed KG at this coverage level.
- `research_relational_grounded_meaning_relevance_wall_2026-07-24.md` (atom 29546 lineage): established
  that symmetric cosine cannot encode asymmetric/causal structure (RotatE/Tversky/DistMult) and built the
  typed-parse + role-bind infrastructure this design reuses. That note used the SAME typed structure to
  build ANOTHER SIMILARITY FEATURE (HARD_FAIL) — this design's key departure is using the identical typed
  structure for SEARCH (existence of a path) rather than SCORING (a directional cosine number), which is
  the actual shape/metric change atom 29549 calls for, not a re-run of the relational-meaning attempt.
- `research_holistic_set_selection_2026-07-25.md` and `research_drill_answer_conditioned_selection_
  biology_2026-07-25.md`: both same-day notes proposed increasingly sophisticated SCORING mechanisms
  (set-level margin construction; answer-conditioned contrastive bind) — both landed HARD_FAIL
  (`SET_LEVEL_HARD_FAIL`, `COND_SELECTION_HARD_FAIL` per the backup doc), and atom 29549's root-cause
  finding explains why in retrospect: no amount of conditioning or set-construction sophistication changes
  the fact that the underlying operation is still a similarity/margin computation, not an entailment
  check. This design is offered as the first attempt in the 2026-07-24/25 arc that changes the OPERATION
  itself, not just how similarity is computed or aggregated. The competitive-verification and consistency-
  check sub-mechanisms from both notes (Usher-McClelland/ECHO margin; Kintsch-CI settle) are reused here,
  not discarded — they become the TIE-BREAK layer (3.3) for when derivation search alone is ambiguous,
  rather than the PRIMARY mechanism.
- `research_combiner_robustness_imperfect_facts_2026-07-24.md`: found CI/PCS settling degrades brittly
  (not gracefully) near competing-hypothesis thresholds. Directly relevant caution for section 3.3's
  consistency check — if the polarity/CI settle oscillates near a threshold when scoring a genuine
  derivation chain (as opposed to a loose fact pool), that brittleness could reject valid chains; flagged
  for explicit monitoring at smoke time, same caution the holistic-set note already raised.
- `research_content_thin_concept_meaning_featural_enrichment_2026-07-25.md`: the still-open concept-content
  sparsity finding is the direct source of the node-unification risk flagged in section 5 — this design
  does not resolve that wall, it inherits it at the unification step, and should be watched for silent
  node-merging as a NEW failure surface introduced by this build, not assumed away.

---

## 8. Substrate-product implications

If the cheap test is GREEN and the full build reaches HARD-PASS on the coverage subset: this is a
qualitatively different capability story than any prior selection fix, because it produces a FULLY
INSPECTABLE derivation for every answered question — "here is the exact chain of typed rules that
connects the question to this answer, and here is why the other three could not be derived" — an
auditability claim no similarity-score-based combiner (however conditioned or set-constructed) can
honestly make, since a similarity score has no notion of "why," only "how similar." This is the same
audit-chain product angle already used for the bidirectional multihop cell, extended from dense-matrix
pointer-chains to symbolic, human-readable typed-rule chains — likely a STRONGER version of that same
story for any product surface that needs to justify an answer to a person.

If HARD-FAIL (indistinguishable from the untyped-similarity-null control specifically): the negative
result is still valuable and diagnostically sharp — it would mean the "entailment vs. similarity"
distinction, while real in the cited literature, is not separable AT THE SCALE AND DEPTH this WorldTree
KG supports (too sparse/shallow a graph for typing to matter vs. raw 3-hop connectivity) — redirecting the
next research cycle toward either (a) a much larger typed-rule corpus (coverage expansion) or (b) deeper
hop budgets, rather than toward yet another scoring-function variant, since scoring-function variants are
now a 6-times-refuted direction (5 prior HARD_FAILs plus whatever this control shows).

---

## 9. Calibration (lit-scan calibration penalty applied per [[feedback-lit-scan-calibration-penalty]])

- **P(cheap test in section 4 is GREEN)** — raw intuition ~0.55 (WorldTree's causal tables are real and
  the meet-in-middle search shape is independently proven at the substrate level, so this is not starting
  from zero; but coverage against ARC-Challenge's specific content is genuinely unknown) -> **deflated to
  P=0.35-0.40** (uncharted regime for THIS corpus at THIS coverage; no published precedent tested WorldTree
  IFTHEN/CAUSE/REQUIRES specifically as a derivation-chain KG for MC-QA verification, as far as this
  drill's searches found).
- **P(full build reaches HARD-PASS on the coverage subset, GIVEN the cheap test is GREEN)** — raw
  intuition ~0.55-0.60 (this is the first mechanism-shape change after 5 prior similarity-shaped HARD_FAILs,
  directly targeting the diagnosed root cause, with 2 independent reused substrate precedents — the meet-
  in-middle search shape and the typed parser — already proven to work in isolation) -> **deflated to
  P=0.35-0.40**, novel-synthesis cap of 0.50 honored (no published precedent combines VSA/HD typed-graph
  derivation search with meet-in-middle proof-search for multi-choice QA verification specifically).
- **Joint P(both stages HARD-PASS, unconditional)** ~= 0.35 x 0.38 ~= **0.13-0.15** — reported honestly as
  the compound estimate, since the cheap test is a real gate, not a formality, given the coverage math in
  section 5.

---

## 10. Citations (verified count)

**Newly verified this session (WebSearch, generic terms only, no substrate specifics off-platform), 14:**
1. Johnson-Laird mental model theory of reasoning (Wikipedia overview, cross-checked against Cambridge
   *Reasoning* ch. 10 abstract and PNAS 2010 "Mental models and human reasoning")
2. Byrne & Johnson-Laird, "Mental Models and Deductive Reasoning" (Cambridge, in *Reasoning*)
3. Khemlani & Johnson-Laird / Johnson-Laird, PNAS 2010, "Mental models and human reasoning"
4. Rips, *The Psychology of Proof: Deductive Reasoning in Human Thinking* (MIT Press) — PSYCOP model,
   natural deduction, ~50 inference rules, suppositions + sub-goals
5. Forward chaining / backward chaining, AI production-system framing (ScienceDirect Topics overview;
   Wikipedia "Backward chaining"; cognitive bottom-up/top-down mirroring)
6. Hummel & Holyoak, "A Symbolic-Connectionist Theory of Relational Inference and Generalization,"
   *Psychological Review* 2003 (LISA — temporal-synchrony role-filler binding)
7. Waltz, Knowlton, Holyoak et al., "A System for Relational Reasoning in Human Prefrontal Cortex,"
   *Psychological Science* 1999
8. Rostrolateral PFC relational-integration literature (ScienceDirect / PubMed, "Rostrolateral Prefrontal
   Cortex Involvement in Relational Integration during Reasoning"; "A hierarchy for relational reasoning
   in the prefrontal cortex")
9. Gentner & Toupin, "Systematicity and Surface Similarity in the Development of Analogy," *Cognitive
   Science* 1986
10. Gentner & Markman, "Structure Mapping in Analogy and Similarity," *American Psychologist* 1997
11. Barsalou, "Perceptual Symbol Systems," *Behavioral and Brain Sciences* 1999
12. Embodied/situated mental simulation of situation models, picture-verification paradigm (ResearchGate/
    Frontiers reviews on mental simulation in embodied cognition)
13. Pearl, causal Bayesian networks and "explaining away" (Bayesia e-book ch. 2 exposition; classic
    burglar-alarm/earthquake example; explicit note that explaining-away is hard for undirected/
    associative models because it requires bidirectional propagation)
14. Anderson, "An Integrated Theory of the Mind," *Psychological Review* 2004; Stocco et al. on ACT-R's
    basal-ganglia implementation of production-rule pattern-matching (striatum), conflict resolution
    (pallidum, inhibitory/winner-take-all), and gated execution (thalamus)

**Reused-with-attribution from same-day/prior KB notes (not re-verified independently in this session,
cross-referenced per section 7):** Tanji & Hoshi 2008 (*Physiol. Rev.*, PFC backward chaining/means-end,
from the M3 note); Thagard 1989 ECHO / Thagard & Verbeurgt 1998 (from the holistic-set-selection note);
Kintsch 1988/1998 CI (from the holistic-set-selection and bindsettle-CI notes); Usher & McClelland 2001,
Wang 2002, Wong & Wang 2006, Albantakis & Deco 2009 (from the holistic-set-selection note); Pohl 1971
bidirectional BFS and Goldberg-Harrelson 2005 (from the M3 note, underlying the reused search shape).

**Total distinct citations this note draws on: 14 freshly verified + 9 reused-with-attribution = 23.**
No citation was fabricated; all newly-verified sources came back with real author/year/venue via
WebSearch and are listed with enough detail to re-locate primary sources.
