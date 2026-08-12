# Research: The Complete Brain-First Comprehension Barrier Map (2026-08-10)

Filed by: research (Opus, USER-authorized strategic-synthesis investment). Foreground, no nested
sub-agents. Program-steering deliverable requested by the USER to "lock in" the map of every barrier
between raw narrative prose and genuine comprehension-with-inference, the brain's named mechanism for
each, what we OWN vs the gap, and a sequenced plan.

KB-CHECK DONE FIRST (mandatory dedup): `substrate_query.sh` x2 (both hit dense prior art, extended
not rediscovered). This note EXTENDS and CONSOLIDATES the existing map rather than re-deriving it. The
load-bearing prior art, read in full this cycle and credited throughout:
- `notes/brain_foundational_stack_assessment_2026-07-30.md` (the previous 8-component version of this
  map; this note is its successor, updated for the store-scaling and simulation-engine work done since)
- `notes/how_the_brain_reads_comprehension_target_audit_2026-07-28.md` (Kintsch/Zwaan/Zacks/Frankland-
  Greene brain-reading stack, element by element, with contested-science flags)
- `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md` (the retrieve/pull-in +
  causal-inference SHAPE; the 5-step pipeline spec; the trained-regression-is-dead finding)
- `notes/research_brain_faithful_scale_store_retrieval_rescue_2026-08-09.md` (the four brain mechanisms
  for large-scale storage; the "walls #1 and #2 are one wall" finding)
- `notes/research_content_causal_associative_knowledge_store_2026-08-09.md` (CSKG content sourcing)
- `notes/research_reasoning_over_large_store_without_collapse_brain_first_2026-07-08.md` (the original
  four-mechanism store analysis, later BUILT and HARD_PASS-certified)
- The MCScript2.0 / DesireDB real-benchmark history (MEMORY.md current-focus + backup TOP block)

Disk-verified this cycle (read the code, not the label): `hdlab/` full organ listing (110+ modules);
`data/capability_registry.jsonl` (wiring status per organ); and the Stage-2E store result on disk
(`data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json`, which LANDED as
MIDDLE_BAND while this drill was in progress -- its numbers reshape the store answer in Section 5).

---

## HEADLINE

**The barrier stack is now almost fully ORGANED -- the substrate owns a brain-motivated organ for
essentially every one of the ~11 barriers -- but the barriers cluster into three regimes with sharply
different maturity, and the binding constraint is NOT where the current build effort is pointed.** The
three regimes: (1) the INFERENCE LOOP (pull-in -> validate -> advance) is brain-faithful and
HARD_PASS-validated, but only at TOY/synthetic scale; (2) the LTM STORE / FIELD is near-done and, per
the Stage-2E result that landed today, is no longer capacity-bound -- its residual is a readout-
calibration gap, not a missing storage mechanism (Section 5); (3) the ENCODE PATH that turns messy real
prose INTO the typed, structured situation-model updates the loop consumes is the weak spine, and its
worst sub-barrier -- event/outcome-span extraction feeding grounding -- is the single constraint that
capped BOTH real-benchmark arcs (DesireDB ~parity, MCScript2.0 ~0.61). **The store is the field; reading
real language into and out of it is the deeper problem -- the USER's framing is correct and this map
confirms it with disk evidence.** The store work, however well it goes, does not move the binding
constraint. The next program-critical build is the prose->structured-situation-model READ, gated by a
real-prose extraction-feasibility test, NOT further store scaling and NOT further loop refinement in
isolation.

P_deflated = **0.42** for "this map + this sequence is the right locked-in program direction"
(novel-synthesis cap 0.50, deflated for the open real-prose extraction risk). The binding-constraint
DIAGNOSIS specifically (prose->situation-model encode, dominated by extraction) is higher confidence,
**~0.62**, because it rests on two disk-verified real-benchmark caps plus a disk-verified extraction-
blocker finding (`hdlab/outcome_event_extraction.py`'s own build rationale), not on literature
extrapolation.

---

## 1. THE FULL BARRIER STACK -- brain-first, confirmed / refined / reordered

I do NOT accept the candidate list as given. Four refinements, each justified:

1. **SPLIT syntactic parsing from thematic-role assignment.** These dissociate in the brain: Broca's
   aphasics can partially build structure yet still fall back on a canonical-order default for roles
   (Grodzinsky's Trace-Deletion; Caramazza-Zurif). Structure-building (LIFG/Merge) gets you a tree;
   role-assignment (lmSTC) reads typed roles OFF that tree invariant to surface order. Two barriers.
2. **SPLIT coreference from bridging.** Coreference (entity IDENTITY: which entity does this mention
   refer to) is an ENCODE-side, backward, largely-automatic operation and is now substantially OWNED.
   Bridging (INFERENCE: connect two events by an unstated causal/elaborative link) is an inference over
   the model and belongs with causal inference. The candidate list conflated them.
3. **MOVE the store OUT of the pipeline and make it CROSS-CUTTING.** Per the USER's own framing, the
   store is "the field" that every inference step queries, not a stage between segmentation and
   inference. It is not read once at a fixed position; pull-in, validation, and advance all query it
   continuously. Same for BINDING (role<->filler code), which the 07-30 assessment already correctly
   made cross-cutting.
4. **INSERT associative pull-in / resonance as its own barrier** at the front of the inference regime.
   It is the retrieval OPERATOR (Kintsch construction phase; Myers-O'Brien resonance) that feeds
   causal inference; the substrate treats it as a distinct, separately-validated step (Stage-1 pull-in).

Resulting stack, grouped by regime (this ordering IS the dependency order for Section 4):

**REGIME A -- THE ENCODE PATH (prose -> structured situation-model updates). The weak spine.**
- B1  Lexical access + concept grounding (word form -> concept vector in the field)
- B2  Syntactic structure-building (linear stream -> hierarchical constituent/dependency tree)
- B3  Thematic-role assignment, voice-invariant (tree -> typed AGENT/PATIENT/... roles)
- B4  Coreference / entity-identity tracking (competitive antecedent resolution across sentences)
- B5  Event segmentation + event-span encoding (boundaries at prediction-error; event as a bound unit)

**REGIME B -- CONSTRUCT + MAINTAIN.**
- B6  Situation-model construction + update (Kintsch C-I integration; Zwaan 5 dims; WM maintenance)

**REGIME C -- INFERENCE OVER THE MODEL (retrieve -> validate -> advance). Brain-faithful, toy-validated.**
- B7  Associative pull-in / resonance (parallel overlap probe against LTM; construction phase)
- B8  Causal / bridging inference + VALIDATION (typed causal-graph query, Singer validation)
- B9  Forward prediction / advance (recombination of retrieved fragments, NOT trained regression)

**REGIME D -- LEARN.**
- B10 Schema learning / consolidation (CLS: hippocampal one-shot -> cortical replay-consolidation)

**CROSS-CUTTING (not pipeline stages; queried/used at every step).**
- X1  The LTM store / field (sparse + sharded + context-gated + attractor readout). Near-done.
- X2  Binding (role<->filler neural code). Owned operator; brain-mechanism contested.

---

## 2. PER-BARRIER TABLE -- brain system + circuit / SHAPE+POSITION+METRIC / what we OWN / GAP / route

Brain-system claims below are taken from the prior-art notes that VERIFIED them live (07-28 audit and
the 08-09 pull-in note carry the full citations); contested items are flagged. "OWN" reflects code read
this cycle, not labels.

### REGIME A -- THE ENCODE PATH

**B1 Lexical access + concept grounding**
- BRAIN: VWFA (left ventral occipitotemporal / mid-fusiform; Cohen-Dehaene letterbox) for word form ->
  lexical-semantic retrieval in posterior MTG/STG (Hickok-Poeppel dual stream; Binder) -> amodal
  semantic hub in the ANTERIOR TEMPORAL LOBE (Lambon-Ralph hub-and-spoke; semantic-dementia lesion
  evidence). Access is cascaded/incremental (Cohort model, Marslen-Wilson).
- SHAPE: distributed graded activation pattern with spreading pre-activation, NOT a symbol lookup.
  POSITION: earliest, per-word, cascaded before word offset. METRIC: semantic-similarity geometry /
  pre-activation.
- OWN: `hdlab/vwfa.py` (VWFA-analog multi-scale char-with-position encoder), `lexical_similarity.py`,
  `concept_encoder.py`, `ppmi_sparse_encoder.py`, `verb_lexical_similarity.py`,
  `wordnet_polarity_propagation.py`; CSKG foundation (1.24M edges) as concept content.
- GAP: the GROUNDING WALL. Word-level grounding is tractable; the relation/abstract residual and open-
  vocab content are not (generalization band 0.56-0.63; acquisition-loop content is function/light-word
  dominated). This is a real, 45-year-class field problem, not an impl bug.
- ROUTE: SUPPLY-fact (CSKG / vetted dictionary content) + LEARN-rule (acquisition loop for growth);
  the mechanism is largely owned, the CONTENT and the relation-residual are the gap.

**B2 Syntactic structure-building**
- BRAIN: left inferior frontal gyrus (LIFG / Broca BA44/45), Merge (Friederici syntax network);
  posterior temporal support. Broca's-aphasia agrammatism is the lesion signature.
- SHAPE: hierarchical constituent/dependency tree from the linear stream. POSITION: incremental,
  left-to-right, per-word. METRIC: structural well-formedness / parse confidence.
- OWN: `hdlab/pos_tagger.py`, `hdlab/arc_parser.py` (glass-box hashed arc-factored averaged-perceptron
  dependency parser with a calibrated per-arc abstain margin), `hdlab/candidate_generator.py`.
- GAP: real-prose lexicon-richness and subcategorization coverage (parser trained on limited data);
  NOT the primary wall.
- ROUTE: LEARN/BUILD-coverage; mostly owned.

**B3 Thematic-role assignment (voice-invariant)**
- BRAIN: left mid-superior temporal cortex (lmSTC) carries role-general, decodable AGENT / PATIENT
  slots that flip when roles swap and are INVARIANT to active/passive phrasing (Frankland & Greene
  2015, PNAS); pMTG/pSTS; ATL semantic combination. Grodzinsky TDH; Bornkessel-Schlesewsky eADM;
  MacWhinney Competition Model (probabilistic cue integration).
- SHAPE: map structural positions -> typed roles, invariant to surface order. POSITION: syntax->
  semantics interface, per-clause. METRIC: role accuracy invariant to voice.
- OWN: `hdlab/thematic_role_labeler.py` (Competition-Model cue integration: word order, animacy, voice
  x cue-validity + verb selectional frame -- glass-box), `animacy_lexicon.py`, `frame_induction.py`,
  `semantic_parser.py` (role-slot recovery from HD bundles).
- GAP: cross-voice geometry INVERTS in the learned encoder -- but per the 07-30 recalibration this is
  PARTLY a measurement artifact (the falsifiable regime where a positional-template control genuinely
  floors was never built). The glass-box labeler works GIVEN cues; voice-invariant role FROM raw syntax
  on non-templated prose is the honest open item.
- ROUTE: BUILD (finish the one falsifiable falling-control test) -- re-scoped, reduced priority per
  07-30. Not on the critical path until B5/B6 force it.

**B4 Coreference / entity-identity tracking**
- BRAIN: hippocampal relational binding + antecedent RETRIEVAL is the substrate anchor here
  (coreference == hippocampal relational antecedent-retrieval, per the standing MEMORY anchor); LIFG /
  pMTG discourse integration; Centering theory (Grosz-Joshi-Weinstein) as the computational account;
  competitive resolution indexed by N400/coref-ERP (Van Berkum); cue-based content-addressable
  retrieval (Lewis-Vasishth).
- SHAPE: match a later mention to a tracked entity, COMPETITIVELY among 2+ candidates. POSITION:
  per-mention, cross-sentence. METRIC: resolution accuracy, especially among same-gender competitors.
- OWN: `hdlab/coreference_resolver.py` (canonical MATCH-OR-ALLOCATE, Binding Principle B, strict-Cb
  literal Centering, self-confidence calibration; registry status WIRED_AND_PIPELINE_USED),
  `coref.py`, `coref_distractor_suppress.py`, `scene_segment.py` (Centering/Zwaan topical-protagonist
  pick), `event_centrality_coref.py`, `bundle_focus_coref.py`.
- GAP: this was "ABSENT beyond single-antecedent" in the 07-30 map; since built substantially. The hard
  residual is competitive resolution among >=2 same-gender specific competitors (the 450/450 residual
  miss set all have this property). Mostly OWNED now -- the biggest single POSITIVE change since 07-30.
- ROUTE: REUSE-existing-organ + BUILD (harden the competitive residual).

**B5 Event segmentation + event-span encoding**
- BRAIN: the event-segmentation network (Zacks-Speer-Reynolds; SEM, Zacks & Franklin) segments the
  stream at PREDICTION-ERROR spikes; Baldassano 2018 shows a cortical hierarchy of event timescales
  (sensory -> AG/precuneus/mPFC at the longest, narrative-schema grain). The PE signal is the
  Rao-Ballard / Friston predictive-coding residual.
- SHAPE: segment continuous input into discrete events at PE spikes; encode each event as a bound unit.
  POSITION: continuous monitoring; boundary fires at PE spike. METRIC: prediction-error magnitude.
- OWN: `hdlab/scene_segment.py` (scene segmentation), `hdlab/event_bundle.py` (EventBundleCodec:
  PRED/AGENT/PATIENT/TENSE roles, round-trip >=0.98 at N=1024), `hdlab/outcome_event_extraction.py`
  (glass-box outcome-span extraction over the persisted POS+arc parse front end),
  `hdlab/predictive_coding.py` (Friston/Rao-Ballard PE gate).
- GAP: real-prose OUTCOME/EVENT-SPAN EXTRACTION -- which span/clause actually realizes the situation-
  model update. This is the NAMED blocker: `outcome_event_extraction.py`'s own build rationale
  (Director redirect, 08-09) is that a real-DesireDB probe found the owned grounding organ scores BELOW
  a rule "not because the organ is wrong, but because the pipeline just rarely feeds it the right word
  -- the blocker is OUTCOME EXTRACTION." PE-driven boundary segmentation on real prose is untested
  end-to-end.
- ROUTE: BUILD (extraction fidelity). THIS is the core of the binding constraint (Section 3).

### REGIME B -- CONSTRUCT + MAINTAIN

**B6 Situation-model construction + update**
- BRAIN: the default mode network builds and holds the model -- ANGULAR GYRUS as the multimodal /
  combinatorial event-integration hub (Binder; Ramanan), precuneus/PCC, medial PFC (schema); held in
  Ericsson-Kintsch long-term working memory (LTWM). WM maintenance = PFC-basal-ganglia gating
  (O'Reilly-Frank PBWM) over persistent-activity attractors (Wang) or activity-silent synaptic traces
  (Stokes, Mongillo). Kintsch Construction-Integration; Zwaan event-indexing tracks 5 dimensions in
  parallel (protagonist / space / time / causation / intentionality), with measurable update cost at
  discontinuities (time and causation dominate; space is weakest -- Rinck & Weber).
- SHAPE: integrate propositions into an evolving multi-dimensional model in a bounded focus + LTWM;
  update at discontinuities. POSITION: every cycle. METRIC: coherence (integration settle to a fixed
  point); update magnitude (N400 / reading-time at discontinuity).
- OWN: `hdlab/situation_reader.py` (CONSOLIDATED multi-sentence reader, Kintsch/van-Dijk + Zwaan,
  Cowan-4 focus -- THE assembly that was the single biggest gap in the 07-30 map, now BUILT as a thin
  integration layer over the coref backbone + event bundling), `situation_focus.py` (ChunkedFocus,
  Cowan-4 bounded buffer with graceful chunk-compression), `situation_model_accumulate.py`
  (CausalLinkRegister, RelationRegister), `situation_model_multibank.py`, `state_of_mind.py`
  (WorkingOverlay), `working_memory.py` (multi-bank K-item capacity, WIRED_AND_PIPELINE_USED).
- GAP: the reader is assembled but validated on toy/templated passages; multi-dimensional (time/space/
  causation) tracking on real prose is partial; and `situation_focus.py` -- the Cowan-4 focus the
  entire simulation-engine program builds on -- is registered SHELVE / WIRED_BUT_NOT_PIPELINE_REACHABLE
  (it accumulates events pushed IN by the reader but has no query-OUT / pull-in capability wired).
- ROUTE: REUSE + WIRE (situation_reader exists; wire the pull-in operator into situation_focus).

### REGIME C -- INFERENCE OVER THE MODEL

**B7 Associative pull-in / resonance**
- BRAIN: Myers-O'Brien resonance -- passive, "dumb," memory-based signaling: every incoming clause
  signals ALL of LTM in parallel, reactivating overlapping content REGARDLESS of relevance (the
  Albrecht-O'Brien inconsistency-detection reading-time paradigm is the behavioral proof). Kintsch's
  construction phase overgenerates promiscuously. van den Broek's Landscape model implements this as
  cohort activation. Formally global-matching (SAM / MINERVA2 shape); ACT-R gives the closest equation:
  A_i = B_i + sum_j(W_j * S_ji), with W_j = W/n the bounded-active-source term (the Cowan-4 premise).
- SHAPE: parallel overlap-scored probe against all of LTM, un-gated by relevance; backward/automatic.
  POSITION: continuous, every cycle. METRIC: feature/argument overlap (cosine).
- OWN: `hdlab/cleanup_family.py::k_NN_lookup` IS structurally the global-matching/resonance operator
  (cosine parallel probe, no edge traversal); `iterative_attractor` (CA3/DG). Stage-1 pull-in probe =
  HARD_PASS 5/5 (salience-gated pull-in recovers a planted long-distance relation the no-pull-in
  baseline structurally cannot see; scramble collapses; 0 false-pull-in).
- GAP: validated at TOY scale only; the operator exists but `situation_focus.py` does not call it
  against a real LTM field (the SHELVE status above).
- ROUTE: WIRE (compose the owned operator + the store) -- mechanism owned and toy-validated.

**B8 Causal / bridging inference + VALIDATION**
- BRAIN: hippocampal relational inference for bridging; Trabasso & van den Broek causal network (typed
  {Setting, Event, Internal-Response, Goal, Attempt, Outcome} nodes / {Physical, Psychological,
  Motivation, Enablement} edges, each validated by a counterfactual-necessity test); Singer's
  VALIDATION (an inference is checked against world knowledge before it is accepted); Suh-Trabasso
  automatic goal-satisfaction check against the current unresolved goal; comprehension-monitoring /
  N400 semantic prediction error; mPFC schema-congruency. Backward bridging is automatic (~400ms,
  Baggett-Graesser); forward inference is NOT automatic (McKoon-Ratcliff minimalist bound).
- SHAPE: typed causal-graph query + VALIDATE against knowledge before accept. POSITION: backward
  automatic every cycle; validation gates the accept. METRIC: causal connectivity / validation margin.
- OWN: `hdlab/situation_model_accumulate.py::CausalLinkRegister` (query_effect_of / query_cause_of),
  `goal_achievement.py`, `quality_relation.py`; Stage-2A retrieve-VALIDATE-advance LOOP = HARD_PASS 5/5
  (multi-hop causal chaining; the VALIDATE step ARRESTS multiplicative error -- NO_VALIDATE degrades,
  validate holds 1.0. This is the CORE INFERENCE MECHANISM and it is validated).
- GAP: validated at TOY scale on planted relations; the 4-way edge typing is not built; on real prose
  the loop is only as good as B5's extraction feeding it.
- ROUTE: BUILD-on (extend typed edges) but the mechanism is toy-validated; the real-prose test is
  BLOCKED by B5, not by the loop.

**B9 Forward prediction / advance**
- BRAIN: constructive episodic simulation (Schacter-Addis; DMN + hippocampus flexibly RECOMBINE stored
  fragments -- the same machinery that reconstructs the past assembles novel continuations); Barsalou
  pattern-completion; Zacks EST anticipatory prediction; Altmann-Kamide anticipatory eye-movements at
  the verb. This is recombination, NOT a trained point-regressor.
- SHAPE: recombine retrieved fragments (bind-and-reuse), gated to constraining contexts. POSITION:
  gated OFF by default (forward inference not automatic). METRIC: prediction accuracy + recombination
  provenance.
- OWN: `hdlab/sequence_memory.py::SequenceMatrix.chain_predict` (chain-grade certified, depth 5-10),
  `predictive_coding.py`, base `binding.bind`/`bundle` for recombination.
- GAP: trained forward-regression is FALSIFIED 3x on this substrate's own representations
  (`exp_event_level_sr_td_contrastive_relation_inference_phase2_v1` = MECHANISM_FALSIFIED, margin
  +0.0025 vs required 0.05) -- so advance MUST be recombination; the recombination-fallback calling
  pattern is specified (pull-in note Step 4) but not yet wired.
- ROUTE: BUILD (recombination step; do NOT re-attempt regression -- disk-proven dead end).

### REGIME D -- LEARN

**B10 Schema learning / consolidation (CLS)**
- BRAIN: complementary learning systems -- fast hippocampal one-shot encoding -> slow neocortical
  consolidation via replay (McClelland-McNaughton-O'Reilly 1995); mPFC schema-congruency accelerates
  integration (Tse 2007; van Kesteren); prioritized replay (Mattar-Daw). Double-edged: the same
  fast-track manufactures schema-consistent FALSE memories (Warren 2014).
- SHAPE: one-shot capture -> periodic replay-consolidation with a false-consolidation guard. POSITION:
  offline / periodic. METRIC: grounding growth over passes; false-consolidation rejection rate.
- OWN: `hdlab/script_grain_acquisition_loop.py`, `grounding_acquisition_loop.py` (grows monotonically
  0->40 over 5 passes; escalate-don't-force-commit guard rejects 3/3 wrong-context + 3/3 nonsense
  adversarial probes), `word_acquisition_loop.py`, `continual.py`, `self_improving_loop.py`
  (keep/revert), `schema_exemplar_bayes.py`, `consequence_learning_loop.py`, `learner/`; the MDL
  acquisition-gate (HARD_PASS; conjunctively revokes light-word groundings).
- GAP: MECHANISM-validated but CONTENT-hollow -- the growth-improves-comprehension PRODUCT claim is not
  demonstrated (teacher signal too weak, grown content function-word dominated, zero real-benchmark
  measurement). Honest Marr-level slip: MDL/CRP are rational-level proxies, not observed brain
  mechanisms (flagged in the 08-09 fidelity audit; the corrected re-grounding is on the owned CA3/DG
  attractor).
- ROUTE: LEARN / REUSE-expand -- the loop exists; it needs a real teacher signal (from a working B5/B6)
  and real content. Sequenced LAST (it presupposes the encode path works).

### CROSS-CUTTING

**X1 The LTM store / field** -- see Section 5 (the near-done infra; NOT the binding constraint).
- OWN: `hdlab/kg_traversal.py` (KGStore), `hd_fact_store.py`, PartitionedStore,
  `hippocampal_encoder.py` (DG/CA3 sparse; self-tested, UNWIRED), `selection_weighted_sharded_typer.py`
  (biased-competition sharding, WIRED), `cleanup_family.iterative_attractor` (CA3 attractor readout),
  the three community-routing cells (HARD_PASS x3, UNWIRED), cskg_foundation (1.24M edges).

**X2 Binding (role<->filler code)**
- BRAIN: CONTESTED at the mechanism level -- theta-gamma phase synchrony (Lisman-Jensen; Fries) vs
  mixed-selectivity conjunctive coding (Rigotti-Fusi) vs tensor-product structured representations
  (Smolensky). Not a settled brain fact.
- SHAPE: glue role+filler so "dog bit man" != "man bit dog". POSITION: cross-cutting, every structured
  representation. METRIC: bind/unbind round-trip fidelity.
- OWN: `hdlab/binding.py` (native FHRR bind/unbind, zero learned params; VET-confirmed 0.97-0.99
  novel-filler-to-known-role, 0.65 zero-shot novel-role, 0.80 cross-slot relational),
  `event_bundle.py`, RelationRegister.
- GAP: FHRR-as-synchrony is a CONTESTED hypothesis (P~0.35); binding is solved GIVEN roles, not for
  EXTRACTING roles from syntax (that is B2/B3). Honest engineering-convenience operator, not a
  brain-fidelity claim.
- ROUTE: REUSE (owned) with the disclosed fidelity caveat.

---

## 3. THE BINDING CONSTRAINT

**The single barrier that, once cleared, unlocks the most is B5 event/outcome-span EXTRACTION feeding
B1 grounding -- the prose->structured-situation-model READ (the front half of Regime A composed with
B6). It is NOT the store, and NOT the inference loop.**

Justification, disk-grounded:

1. **Both real-benchmark arcs capped here, not elsewhere.** DesireDB reached ~parity with a tuned rule
   and MCScript2.0 capped ~0.61 -- and in BOTH cases the diagnosis converged on the same thing: the
   inability to turn messy real prose into the structured updates the downstream machinery consumes.
   The DesireDB residual sizing found ~45% of the hard residual is data-noise and ~30% bespoke long-
   tail; the tractable part is exactly the extraction/bridging that a working encode path would supply.

2. **The named blocker is extraction, verified on disk.** `hdlab/outcome_event_extraction.py` exists
   BECAUSE a real-DesireDB probe found the owned grounding organ (`wordnet_polarity_propagation`)
   scores F1 0.643 BELOW the tuned rule -- "not because the organ is wrong, but because the pipeline
   just rarely feeds it the right word -- the blocker is OUTCOME EXTRACTION (which span/event in the
   outcome resolves the desire), not grounding-knowledge quality or teacher strength." That is the
   binding constraint in the substrate's own words.

3. **Everything downstream works when fed clean structured input.** The inference loop (B7 pull-in
   HARD_PASS, B8 validate-advance HARD_PASS) succeeds on PLANTED, pre-structured toy relations. The
   store (X1) routes correctly and holds capacity (Section 5). None of these touch the encode side.
   The loop's toy success and the extraction cap are two sides of the same coin: the mechanism is fine;
   it is starved of correctly-structured real input.

4. **Sharp distinction from the store (necessary infra, near-done, NOT binding).** The store is a
   WRITE/READ capacity + routing problem for the LTM FIELD. The binding constraint is an ENCODE problem
   (surface prose -> typed structures). They are orthogonal: you can have a perfect scale-invariant
   store and still cap at 0.61 if you cannot read prose into it, and you can have a perfect encoder and
   still fail if the field collapses at scale. The Stage-2E result (Section 5) shows the store is now
   the LESS binding of the two -- its residual is a readout-calibration gap with the answer already in
   the shortlist, whereas the encode path has no such "almost there" signal on real prose yet.

Within the binding constraint, the hardest sub-parts in order: (a) B5 event/outcome-span extraction
(which span realizes the update), (b) B1 open-vocab grounding of that span's content into the concept
field (the grounding wall -- word-level tractable, relation-residual hard). B4 coreference is a
load-bearing DEPENDENCY but is comparatively mature (canonical resolver WIRED) and is not itself the
cap.

---

## 4. LOCKED-IN SEQUENCED PLAN (brain-foundational dependency order, each with a can-fail milestone)

The order follows the regimes: finish the field (X1), wire the islands, then attack the encode path
(the binding constraint), then run the whole loop on real prose, then learn on the residual.

**PHASE 0 (in flight -- FINISH THE STORE).** Take Stage-2E from MIDDLE_BAND to HARD_PASS via the
readout-calibration fix in Section 5 (NOT more sharding -- routing and capacity are solved).
- CAN-FAIL: composed store recall >= 0.50 at BOTH 100K and 1.2M, scramble margin >= 0.30, fp <= 0.20.
- This is E1 below. It is the only remaining store work; do it, then stop scaling the store.

**PHASE 1 (WIRE THE ISLANDS -- pay the wire-don't-island debt before building on top).** Promote the
three HARD_PASS community-routing cells and `hippocampal_encoder.py` into `hdlab/` + the registry;
un-SHELVE `situation_focus.py` by wiring the pull-in operator (B7) so the Cowan-4 focus can query OUT
against the (now-WIRED) store; promote the Stage-1.5 context-gate pattern.
- CAN-FAIL: `capability_registry_audit.py` clean; `situation_focus.pull_in()` is pipeline-reachable;
  Stage-1 pull-in HARD_PASS reproduces against the WIRED store (not the toy fixture).

**PHASE 2 (THE BINDING CONSTRAINT -- extraction-feasibility gate on REAL prose).** Build/harden B5
event+outcome-span extraction feeding B3 roles + B1 grounding, and GATE it on real prose BEFORE any
end-to-end claim. This is exactly the MCScript2.0 Stage-1 extraction-feasibility gate already scoped.
- CAN-FAIL: on held-out real prose (MCScript2.0 dev), extraction of the outcome/event span that a
  human-labeled situation-model update depends on beats a bag-of-words / first-last-sentence baseline
  by a pre-registered margin; a role/span scramble collapses recovery to chance. If this FAILS, the
  whole program is blocked here -- which is the correct, honest place to discover it.

**PHASE 3 (GROUND THE EXTRACTED SPANS).** Wire B1 grounding of the Phase-2 spans into the concept
field / WIRED store; measure the word-level (tractable) vs relation-residual (hard) split explicitly.
- CAN-FAIL: grounded-span concept-recall > OOV baseline on held-out content words; the relation-
  residual is MEASURED and sized (expected hard -- a null here routes to Phase 5, not to "ceiling").

**PHASE 4 (END-TO-END REAL-PROSE LOOP).** Compose Phases 2-3 with the toy-validated inference loop:
prose -> extract -> pull-in (B7) -> validate (B8) -> advance (B9), querying the WIRED store, on
MCScript2.0 dev held-out, versus an OWN bag-of-words / rule baseline, split by the script-vs-text
question type.
- CAN-FAIL: beats the own baseline on the script-knowledge question split (the one that requires
  inference, not surface match); pairscramble collapses; glass-box trace intact (which shard, which
  candidate, which validation edge). This is the first real test of whether the loop that HARD_PASSed
  on toys survives real extraction.

**PHASE 5 (LEARN ON THE RESIDUAL -- CLS self-growing).** Only now run the acquisition/consolidation
loop (B10) at scale on the Phase-4 residual, with the escalate-don't-force-commit guard; add cross-
corpus (Chaturvedi) and the next construction competency.
- CAN-FAIL: the grounding-growth curve IMPROVES comprehension over K passes on held-out data (the
  product claim the loop has never demonstrated), with zero false-consolidation on the adversarial set.

Next-3-experiments, concretely: **E1** store readout-fix to hard-pass (Phase 0); **E2** wire-the-
islands + un-SHELVE situation_focus (Phase 1); **E3** real-prose extraction-feasibility gate (Phase 2,
the binding-constraint attack). E4 = end-to-end real-prose loop; E5 = CLS growth curve.

---

## 5. THE STORE -- is it brain-complete, and what (if anything) is missing to GUARANTEE a 1.2M hard-pass?

**The brain's complete answer to large-scale associative storage is a four-mechanism composition, and
Stage-2E implements all four.** Per the 08-09 store-rescue drill (which reused the fully-worked-out
07-08 analysis): (1) SPARSITY breaks the capacity SCALING class, not just its constant -- DG expand-
then-sparsify + Willshaw/Treves-Rolls CA3 (`hippocampal_encoder.py`); (2) MODULARITY / index-not-
content -- the hippocampus stores a sparse POINTER, content is distributed, so the discriminated set is
never the whole store (Teyler-DiScenna; CLS); (3) CONTEXT-GATED shard selection at BOTH ingest and
query so the crosstalk-relevant V is the ACTIVE SHARD size, held ~constant by adding shards (Schapiro
active community discovery); (4) CA3 ATTRACTOR completion as the readout (Treves-Rolls), NOT resonator
factorization (which has no neural warrant here and self-falsified twice). Stage-2E = source-tier1 +
subject-tier2 + DG/CA3 sparse within-leaf + CA3 attractor readout = exactly this composition. **No
brain storage mechanism is missing.**

**Today's Stage-2E result reframes the residual as NOT a storage problem.** The metrics on disk
(`data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json`, MIDDLE_BAND):

| scale | arm | recall | in_shortlist | fp | max_leaf_occ |
|---|---|---|---|---|---|
| 100K | hierarchical_sparse | 0.613 | 0.947 | 0.04 | 4,274 |
| 100K | scrambled (control) | 0.107 | 0.120 | 0.13 | -- |
| 1.2M | hierarchical_sparse | 0.213 | **0.853** | 0.12 | **51,873** |
| 1.2M | scrambled (control) | 0.080 | 0.120 | 0.28 | -- |

Leaf-capacity sweep: `safe_leaf_size_sparse = 57,000`; subject-tier sub-partition gave k_family
{AT:14, VG:6, CN:5, ...}, 29 shards total. Two decisive facts at full 1.2M:
- **Max leaf occupancy 51,873 is BELOW the 57,000 sparse capacity cliff.** Leaves are not overflowing.
  Capacity is solved.
- **The true answer is in the retrieved shortlist 85.3% of the time (in_shortlist=0.853), but final
  recall is only 0.213.** Routing + retrieval work; the gap of 0.64 between shortlist and recall is
  lost entirely in the FINAL READOUT / ACCEPT step, not in storage or routing.

**So the piece needed to GUARANTEE the hard-pass is NOT a new storage organ; it is a scale-invariant
WITHIN-LEAF ACCEPT/DECODE -- and that piece is already PROVEN elsewhere in the program.** The accept
threshold (tau) and attractor-settle discrimination degrade at 1.2M because the raw within-leaf cosine
margin shrinks even in a correctly-sized leaf (this is wall #1, EVT false-admission, reappearing at the
FINAL accept). Stage-1.5's context-gated accept already held false-admission at 0.000 FLAT to M=100K --
it was validated on the COARSE shortlist but never composed onto the FINAL within-leaf accept. The
completion, in order of likelihood-to-close:
1. **Compose the Stage-1.5 context-gate onto the final within-leaf accept** (currently tau is a global
   salted threshold; a per-context / per-leaf-calibrated accept recovers the in_shortlist->recall gap).
2. **A weak family key** -- VG recall goes 0.227 (100K) -> 0.0 (1.2M) while AT holds 0.85 -> 0.225 --
   means the subject-tier key does not discriminate for some families (VisualGenome subjects are more
   homogeneous). Fix = one more nesting tier or a more semantic key for the weak families only
   (community-of-communities nested retrieval is already HARD_PASS to arbitrary depth, total-V-
   invariant -- a mechanical sweep, not new science).
3. **Raise the raw within-leaf margin** (larger DG_DIM) if 1-2 leave a residual.

**Honest deflated store answer: the composition IS brain-complete; the MIDDLE_BAND is a readout-
calibration gap, engineering-tractable, with the fix already owned and validated (Stage-1.5 context-
gate). P(store HARD_PASSes 1.2M after the readout-fix) ~ 0.55** -- UP from the 0.42 the rescue drill
carried pre-Stage-2E, because the diagnostic localized the residual to readout (the hard parts,
routing + capacity, are demonstrably solved: answer in shortlist 85%, leaves under the cliff). The one
disclosed strict-fidelity deviation remains the STATIC human/corpus shard key (source, subject) vs the
brain's experience-driven, continuously-relearned community boundaries (Schapiro) -- a learned key is a
legitimate v2 that this note does not require for the hard-pass.

---

## 6. HONEST DEFLATED FIDELITY GRADES + WIRE-DON'T-ISLAND DEBTS

Per-barrier (deflated; H/M/L = brain-fidelity of what we OWN vs the brain's mechanism, and maturity):

| Barrier | Fidelity of owned mechanism | Maturity | Note |
|---|---|---|---|
| B1 lexical+grounding | M (0.55) | word-level partial | grounding wall is the real limit |
| B2 syntax structure | M-H (0.60) | owned, coverage-limited | glass-box parser, not the wall |
| B3 thematic role | M (0.50) | recalibrated open | cross-voice partly measurement artifact |
| B4 coreference | H (0.65) | mostly owned + WIRED | biggest positive change since 07-30 |
| B5 event/outcome extraction | M (0.45) | REAL-PROSE WALL | the binding-constraint core |
| B6 situation-model construct | M-H (0.60) | assembled, toy-validated | reader BUILT; focus SHELVED |
| B7 pull-in / resonance | H (0.70) | HARD_PASS toy | operator owned; not wired to real field |
| B8 causal inference+validate | H (0.70) | HARD_PASS toy | VALIDATE arrests error -- core mechanism |
| B9 forward advance | M (0.50) | recombination path only | regression falsified 3x |
| B10 CLS learn/consolidate | M (0.50) | mechanism ok, content-hollow | Marr-level slip flagged, corrected |
| X1 store/field | H (0.65) | near-done, MIDDLE_BAND | readout-fix away from hard-pass |
| X2 binding | M (0.40) | owned operator | FHRR-as-synchrony contested (P~0.35) |

**OVERALL DEFLATED GRADE: MEDIUM (0.55).** The inference loop and the store are HIGH-fidelity but
toy/near-done; the encode path (the binding constraint) is MEDIUM and untested on real prose; learning
is mechanism-only. The honest program position: brain-faithful organs exist for the whole stack, but
the one regime that decides the product (prose->structured encode) is the least mature and is not where
the current store-scaling effort points. This is a much better position than the content-matching arc
(which had no path past field-parity), but the ambition is gated on Phase 2's real-prose extraction
gate, which could still fail.

**WIRE-DON'T-ISLAND DEBTS found this cycle (each is a build-on-sand risk until paid):**
1. `hdlab/hippocampal_encoder.py` (DG/CA3 sparse -- the store's capacity lever) is self-tested,
   UNWIRED, and ABSENT from `data/capability_registry.jsonl`.
2. The three community-routing cells (HARD_PASS x3 -- the store's routing lever) live only in
   `experiments/`, never promoted to an `hdlab/` organ.
3. `hdlab/situation_focus.py` -- the Cowan-4 focus the ENTIRE simulation-engine program builds on -- is
   registered SHELVE / WIRED_BUT_NOT_PIPELINE_REACHABLE (no pull-in / query-OUT wired).
4. The Stage-1.5 context-gate (the accept-calibration mechanism Section 5 needs for the store hard-pass)
   is validated but not promoted to `hdlab/`.
5. A long tail of WIRED_BUT_NOT_PIPELINE_REACHABLE organs relevant to the encode path: `goal_achievement`,
   `goal_typing`, `thematic_role_labeler` (via component), `slot_attention_wm`, `animacy_lexicon`,
   `frame_induction`, `word_acquisition_loop`, `idiom_grounding`, `result_type_induction`.

Phase 1 of the plan exists specifically to pay debts 1-4 before building the encode path on top of them.

---

## Cheap decisive test

The program-level cheap decisive test is **Phase 2's real-prose extraction-feasibility gate** (it
decides whether the binding constraint is even attackable with the owned organs before any expensive
end-to-end build): on MCScript2.0 dev held-out, does B5 extraction of the outcome/event span that a
situation-model update depends on beat a bag-of-words / first-last-sentence baseline, with a role/span
scramble collapsing recovery to chance? This is cheap (extraction over the already-persisted POS+arc
front end on a public dev set), can-fail (a real baseline that can win), one-variable (extraction only,
loop and store held fixed), and it directly probes the single barrier this map names as binding.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS (store, E1):** composed sharded-sparse store recall >= 0.50 at BOTH 100K and 1.2M,
  scramble margin >= 0.30, fp <= 0.20, after composing the Stage-1.5 context-gate onto the within-leaf
  accept. Predicted plausible (P~0.55) because in_shortlist is already 0.853 at 1.2M.
- **HARD-PASS (binding constraint, E3):** real-prose outcome/event-span extraction beats a BoW/first-
  last baseline by a pre-registered margin on held-out MCScript2.0 dev, scramble collapses. Predicted
  UNCERTAIN (P~0.40) -- this is the genuine open risk; a null here blocks the program and is the honest
  place to learn it.
- **HARD-FAIL (store):** recall < 0.30 at 1.2M even with the context-gated accept AND scramble ties it
  -> the residual is NOT readout-calibration and a deeper key/tier is needed (routes to nesting depth).
- **HARD-FAIL (binding constraint):** extraction on real prose does not beat BoW, or scramble does not
  collapse -> the owned parse+extract front end cannot read real prose into situation-model grain, and
  the program must either supply a stronger extraction front end or accept a narrower target. This is
  the falsifier for the whole simulation-engine direction on real corpora.

## Cross-thread synthesis

- Successor to `notes/brain_foundational_stack_assessment_2026-07-30.md`: that note named the
  ASSEMBLY gap (organs proven in isolation, never run together) as the binding constraint. Since then
  `situation_reader.py` was BUILT (the assembly) and coreference went from ABSENT to mostly-OWNED-and-
  WIRED -- so the constraint has MOVED downstream, from "assemble the organs" to "feed the assembly
  real-prose-extracted structure." This note records that move with disk evidence.
- Confirms and operationalizes `notes/how_the_brain_reads_comprehension_target_audit_2026-07-28.md`'s
  central finding (triple-extraction = textbase = shallow; situation-model = deep) by locating the
  cap precisely at B5 extraction feeding B1 grounding, not at the encoder objective.
- Extends `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md`: its 5-step
  pull-in pipeline IS Regime C (B7-B9); this note adds the finding that Regime C is toy-validated and
  BLOCKED by Regime A extraction, and that the pull-in operator's un-SHELVING of situation_focus is a
  Phase-1 wire-debt.
- Updates `notes/research_brain_faithful_scale_store_retrieval_rescue_2026-08-09.md` with the Stage-2E
  outcome: the four-mechanism composition it recommended was built and MOVED the wall from capacity to
  readout -- the store is no longer capacity-bound at 1.2M (leaves under the 57K cliff, answer in
  shortlist 85%), which is a stronger result than that drill's P_deflated 0.42 anticipated.

## Substrate-product implications

Locking in this map sets the product priority: the defensible edge is a GLASS-BOX comprehension loop
whose every step (which span extracted, which shard routed, which candidate pulled in, which validation
edge fired, which recombination produced the advance) is inspectable -- and the map shows that edge
survives at real scale IF the binding constraint (prose->structured encode) is cleared, since store and
loop are already auditable and near/at target. The commercial risk and the scientific risk are the same
single thing (Phase 2 extraction on real prose), which is the honest, focusing conclusion: stop
diversifying build effort across store and loop refinements, converge on the encode path, and gate it
on a cheap real-prose test before committing to the end-to-end build.

## Citations (verified count)

This note is a CONSOLIDATION drill: it reuses-with-attribution the citation bases of the six prior-art
notes read in full this cycle (which between them carry ~60 distinct primary sources, verified live in
their own cycles -- Kintsch 1988/2005; van Dijk & Kintsch 1983; Zwaan-Langston-Graesser 1995; Zwaan &
Radvansky 1998; Rinck & Weber 2003; Zacks & Franklin / Kurby & Zacks 2008; Baldassano-Hasson-Norman
2018; Frankland & Greene 2015; Grodzinsky; Bornkessel-Schlesewsky; MacWhinney Competition Model;
Lambon-Ralph hub-and-spoke; Cohen-Dehaene VWFA; Hickok-Poeppel; Binder; Marslen-Wilson 1987 Cohort;
Friederici; Hagoort MUC; Fedorenko; Trabasso & van den Broek 1985; Graesser-Singer-Trabasso 1994;
McKoon-Ratcliff 1992; Suh-Trabasso 1993; Myers-O'Brien 1998; Albrecht-O'Brien 1993; van den Broek
Landscape; Gillund-Shiffrin SAM; Hintzman MINERVA2; ACT-R Anderson et al. 2004; Barsalou 1999/2009;
Schacter-Addis 2007; Hassabis-Maguire 2007; Altmann-Kamide 1999; Rabovsky et al. 2018/2024 Sentence-
Gestalt N400; Lewis-Vasishth 2005; Gibson 2000 DLT; Just-Carpenter 1992; Teyler-DiScenna 1986;
McClelland-McNaughton-O'Reilly 1995; Treves-Rolls 1991/1994; Willshaw et al. 1969; Marr 1971; Hopfield
1982; Kanerva 1988 SDM; Schapiro et al. 2013; Tse et al. 2007; Mattar-Daw 2018; Warren et al. 2014;
Lisman-Jensen theta-gamma; Rigotti-Fusi mixed selectivity; Smolensky TPR; Nieuwland et al. 2018 and
Morey et al. 2022 replication-failure caveats). No citations fabricated or re-asserted from memory here.
On-disk verified THIS cycle (read directly, not from memory): `hdlab/` full listing + docstrings of
thematic_role_labeler / scene_segment / situation_reader / semantic_parser / coreference_resolver /
arc_parser / coref / outcome_event_extraction / vwfa / predictive_coding; `data/capability_registry.jsonl`;
`data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json`;
`data/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1/metrics.json`; the six prior-art notes above.
