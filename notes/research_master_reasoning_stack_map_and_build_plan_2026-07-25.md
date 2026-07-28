# THE MASTER MAP -- brain reasoning stack, end-to-end: gap-list + dependency-sequenced build plan

**Date:** 2026-07-25. **Filed by:** research (Opus, direct -- no child sub-agent, per Director instruction).
**Method (USER-locked):** deep-brain-analysis -> comparison -> accurate-duplication, per
[[project_formalize_deepbrain_analysis_then_comparison_accurate_duplication_method_2026-07-24]].
**Mandate (USER 2026-07-25):** "duplicate the brain function 100% -- no shortcuts ... show reasoning or
this is not a functional tool." This note is the phase-defining blueprint that mandate calls for.
**This is a SYNTHESIS.** Every biological claim, every disk-verified state, and every VET verdict below is
reused from ~10 already-VET'd research notes and ~25 landed ARC experiments produced 2026-07-24/25 --
nothing here is re-derived from scratch. Citation totals are rolled up from those notes' own verified
counts (no fresh WebSearch performed this cycle, per the task's explicit synthesize-don't-re-derive ask).

---

## HEADLINE

**Of the 8 reasoning-stack stages, 7 already have real, disk-verified, brain-cited components on this
substrate -- the debt is overwhelmingly WIRING (capability TRAPPED in unpromoted exp-cells, not capability
ABSENT), not a missing-mechanism list waiting to be invented.** The hdi_testbed integration audit
(`notes/integration_audit_hdlab_wired_vs_islands_2026-07-25.md`) is the load-bearing cross-check for this
claim: hdlab itself is B- (7/93 modules dead, mostly well-wired), but the ARC/reasoning frontier is a tower
of `exp_` cells re-importing each other, touching hdlab in only ~3 spots, with **zero composed entry point**
(4 disjoint composition roots, none is ARC). The one stage that is a **genuine, structural, not-yet-solved
gap** is Stage 8 (learning/credit-assignment): right now, credit assignment -- which component caused an
error -- is performed **by the human Director**, via hours-long manual research-drill diagnosis, playing
exactly the role three-factor eligibility traces / cerebellar climbing fibers play in the brain, at a
timescale of hours instead of milliseconds.

**The dominant CURRENT SHORTCUT, proven-failed by elimination across 7 consecutive selection HARD_FAILs
plus 2 chaining/routing HARD_FAILs this session, is that every attempt to "reason" reduced to SIMILARITY
SCORING -- never true entailment or derivation -- over THIN, disembodied GloVe/WordNet meaning (Stage 1's
own proven-failed shortcut).** Atom 29549 (VET-confirmed root cause, skunkworks a65085e7) names this
exactly: the entire retrieve->select->combine pipeline is similarity all the way down at confidence ~0.72;
it never reasons. The single design that changes the **operation itself** (not merely how similarity is
computed or combined) is **VERIFICATION-BY-DERIVATION** (`notes/research_verification_by_derivation_reasoning_pivot_2026-07-25.md`):
replace per-fact/per-set SCORING with typed-graph SEARCH for existence-of-a-derivation. Its own cheap
connectivity gate has **already run and returned RED** -- COVERAGE-BOUND, confirmed via a clean node-identity
re-run (atom 29552) and two rule-supply probes (29553/29554) that SETTLED "off-the-shelf commonsense KBs are
the wrong supply" (hub-present-in-graph = non-discriminative vacuous bridges; hub-removed = coverage
collapses to ~0; no cap threads the needle). A follow-on schema-routing (structure-only) fix also HARD_FAILed
on the entity-selection axis specifically (atom 29555's convergence). **Net: TWO independent levers are both
load-bearing and NEITHER alone suffices right now** -- (i) science-precise RULE-SUPPLY breadth (cheap,
extraction-shaped), and (ii) grounded/learned fine-CONTENT meaning (deep, Stage 1's proven wall). The build
plan below sequences the cheap, mostly-reuse unlocks first (rule-supply -> compose the reasoner ->
do-calculus routing -> credit-assignment loop) and treats the deep meaning-foundation rebuild as the
ongoing, USER-flagged macro-investment whose SCOPE gets sharpened (not replaced) by what the cheaper fixes
leave unresolved.

**P_deflated (joint, full derivation-search reasoner reaches its own pre-registered HARD-PASS band, given
rule-supply succeeds):** carried forward from the pivot note's own compound estimate, ~0.13-0.15 -- treat as
a live, not-yet-superseded number; the connectivity gate's RED verdict this session makes the FIRST factor
of that product (cheap-gate-GREEN) the currently-open, not-yet-cleared precondition.

---

## KB-check synthesis -- what each cited drill/atom already establishes (cited, not re-derived, below)

- **`notes/research_brain_qa_architecture_completeness_2026-07-24.md`** (85 citations, 4 parallel lit-scans):
  exhaustive 11-stage/~30-subsystem inventory of the brain's QA pipeline, collapsing to 4 organizing
  principles (settle/parallel-constraint-satisfaction; spreading activation; attention/reward-gated
  competition; precision-weighted control). Named the SAME missing mechanism (controlled/strategic
  retrieval + competitor suppression, Badre & Wagner anterior/mid-VLPFC) our own diagnostics (29538) had
  already converged on independently -- the lit-scan's contribution was naming it precisely, not opening a
  new direction.
- **`notes/research_verification_by_derivation_reasoning_pivot_2026-07-25.md`** (23 citations): the current
  frontier design. Disk-verified what already exists (typed tablestore parser, EventBundleCodec role-bind,
  PolarityLexicon/CI, M3 bidirectional meet-in-middle search shape) and designed the ONE new mechanism
  (typed-graph derivation search) needed to replace scoring with search. Its own cheap connectivity gate has
  since run RED (see Stage 5 below) -- this note supersedes the 5 prior scoring-shaped selection attempts as
  the design of record, without discarding their reusable sub-mechanisms (competitive margin, CI settle).
- **`notes/research_native_binding_compositional_generalization_2026-07-25.md`**: Fodor-Pylyshyn
  systematicity / Smolensky TPR / Hummel-Holyoak LISA / NVSA (learned front-end + fixed algebra) as the
  brain-faithful fix for compositional generalization; component-2 build (atom 29557) found fixed-bind ~=
  concat+linear on SINGLE-HOP completion (binding not yet shown as the lever there) -- the genuine
  multi-role/deep-composition edge remains UNTESTED, not refuted.
- **`notes/research_mental_simulation_grounding_causal_models_arc_2026-07-24.md`** (42 citations): a
  three-way split (dynamic/perceptual simulation vs. Pearl-style interventionist causal computation vs.
  cached covariation recall) with the key finding that **the substrate already has a HARD_PASS-certified
  do-calculus primitive (cap_map PP-270/PP-307, recall_l3=1.000) sitting completely unwired from ARC** -- a
  cheap, scoped, reuse-only fix for the COUPLEDRELATIONSHIP item subclass, not a new mechanism to build.
- **`notes/research_learning_control_neuromodulation_inventory_2026-07-24.md`** (46 citations, cross-referencing
  7 prior in-Store notes): the brain uses a STACK of 5+ separable learning/control mechanisms, no single
  unifying law (FEP is contested, not consensus); the substrate has genuine, disk-verified ANALOGS of 3 of
  5 (RPE/Go-No-Go actor HARD_PASS-certified; predictive-coding module MIDDLE_BAND; a fully-designed,
  unbuilt 6-channel neuromodulatory self-manager) -- **none wired to the substrate's own real
  task-correctness signal.** The single sharpest finding: credit assignment is currently performed by the
  human Director's manual diagnosis loop.
- **`notes/research_holistic_set_selection_2026-07-25.md`** (28 citations) and
  **`notes/research_drill_answer_conditioned_selection_biology_2026-07-25.md`**: both proposed
  increasingly sophisticated SCORING mechanisms (set-level margin construction; answer-conditioned
  contrastive bind); both landed HARD_FAIL (`SET_LEVEL_HARD_FAIL`, `COND_SELECTION_HARD_FAIL`). Atom 29549's
  root-cause finding explains why in retrospect -- no amount of conditioning/set-construction sophistication
  changes the fact that the underlying operation was still similarity/margin, not entailment. Their
  competitive-margin (Usher-McClelland/Albantakis-Deco) and CI-settle sub-mechanisms are REUSED, not
  discarded, as the derivation-search design's tie-break layer.
- **`notes/research_contradiction_representation_and_settle_dynamics_2026-07-24.md`** (27 citations):
  the textbook "antonym problem" (Yih/Zweig/Platt 2012) -- raw cosine similarity structurally CANNOT
  separate synonymy from antonymy (antonyms are paradigmatically close, not far). Biology converges: abstract
  propositional opposition is a LABELED RELATIONAL EDGE (amygdala intercalated-cluster bidirectional-valence
  evidence), not a geometric sign axis, which only exists for genuine sensory continua (color/motion
  opponency). N400/Fischler evidence: contradiction-handling is STAGED (early negation-agnostic mismatch,
  later truth-evaluation, separate ACC response-conflict) -- three separate computations, not one signal.
- **`notes/research_arc_retrieval_biology_and_design_2026-07-24.md`**: hippocampal pattern
  completion/modern-Hopfield, Collins-Loftus spreading activation/HippoRAG, and Tulving
  encoding-specificity/Badre-Wagner controlled retrieval all converge on "retrieval must be relational
  (typed-link spread, not raw cosine) AND discriminative (relevant to the CHOICE SET, not just the stem)."
  Confirms `substrate/khop.py` (Merkle-audited K-hop, production-validated on FB15K-237/WebQSP/CWQ) is real
  and reusable but requires an explicit relation-path, not open-ended spread; PPR/spreading-activation is
  the better-fit primary mechanism (already validated on the REAL WorldTree graph, +0.10 recall, 29539).
- **`notes/research_combiner_robustness_imperfect_facts_2026-07-24.md`**: CI/PCS-style settling degrades
  BRITTLY (not gracefully) near competing-hypothesis thresholds -- a live caution for the derivation
  design's consistency-check and stopping-rule near-threshold behavior, flagged for explicit smoke-time
  monitoring, not yet independently re-tested.
- **`hdlab/situation_reader.py`** (disk-read directly, this session): a real, consolidated, calibrated
  multi-sentence Kintsch/van-Dijk + Zwaan event-indexing reader (entities/events/time/causation in a
  Cowan-4 bounded focus), composed from ALREADY-BANKED modules (coref 29506-29517, event bundles 29511,
  temporal ordering 29510, causal-network reader 29515 -- honestly flagged as connective-adjacency-reducible,
  not genuine causal plausibility). Zero ARC consumers (integration audit) -- a well-built, unwired island.
- **`notes/integration_audit_hdlab_wired_vs_islands_2026-07-25.md`**: the disk-verified wiring map. Names
  the exact promotion sequence (P1 typed-rule-parser -> P2 stable arc_pipeline API -> P3 M3 meet-in-middle
  -> P4 CI/polarity -> P5 the MISSING composed entry `hdlab/reasoner.py` -> P6 situation_reader's role) and
  the explicit convergence: **"the verification-by-derivation reasoner build IS P5 -- building it promotes
  P1/P3/P4 as its parts."** This is the single most load-bearing cross-reference for the build plan below.

---

## THE END-TO-END MAP (8 stages, biology-cited, brain-mechanism -> our version -> gap -> shortcut flag)

| # | Stage | Brain mechanism (cited) | OUR version (disk-verified) | Gap: SHAPE / PLACE / METRIC | SHORTCUT? |
|---|---|---|---|---|---|
| 1 | **GROUNDED MEANING** | Barsalou perceptual symbol systems (grounding); ATL hub-and-spoke (Lambon Ralph; Patterson, Nestor & Rogers 2007); error-driven semantic differentiation (Rogers & McClelland PDP), learned over a curriculum, coarse-before-fine | `SemanticHDEncoder` = fused(GloVe + WordNet syn/hyper pulls) -> JL -> bipolar HD (atom 29533, AUC 0.96 meaning-match). **PROVEN-FAILED at fine discrimination**: 7 consecutive selection HARD_FAILs (29544-29550) all trace to inability to separate hydro/nuclear/coal "power-plant" facts. Component-1 (29556): a learned glass-box hub over frozen GloVe DOES acquire fine in-vocab discrimination (curve 0.14->0.75, coarse-before-fine, Rogers-McClelland-faithful) but held-out COMPOSITIONAL generalization decays to the flat floor (structural, `ho_lift 0.0`) | SHAPE: static supplied co-occurrence vector, no error-driven differentiation loop, no grounding, vs brain's learned/differentiated hub-and-spoke. PLACE: the encoder itself, upstream of everything. METRIC: symmetric cosine similarity -- structurally cannot express asymmetric/causal/support-vs-contradict relations (RotatE/Tversky/DistMult diagnosis, 29546) | **YES -- the named foundation shortcut.** Everything downstream (node-unification in derivation graphs, CI polarity precision, retrieval discrimination) inherits this wall |
| 2 | **COMPREHENSION** | Kintsch & van Dijk 1978 Construction-Integration (construction=over-generate, integration=parallel-constraint-satisfaction settle); Zwaan event-indexing (entities/events/time/causation) | `hdlab/situation_reader.py` -- REAL, consolidated, calibrated (role F1 0.57-0.67 on McGuffey/LitBank gold, coref scored vs LitBank gold), Cowan-4 bounded focus | SHAPE/METRIC mostly RIGHT (Kintsch-faithful). PLACE: built for NARRATIVE-PASSAGE comprehension; ARC needs question+candidate -> claim/givens extraction, a different consumer shape not yet adapted. Zero ARC consumers today (integration audit) | **YES, for the ARC consumer specifically** -- ARC currently uses crude `_content_words()` extraction instead of the real reader. The reader itself is honestly benchmarked, not a shortcut; its internal causal-link extractor IS a shortcut (connective-adjacency, not force-dynamics causal reasoning, flagged in its own docstring) |
| 3 | **BINDING** | LISA temporal-synchrony role-filler binding (Hummel & Holyoak 1997/2003); Smolensky tensor-product reps; Fodor-Pylyshyn systematicity | Native VSA bind (circular-convolution/Hadamard) -- fixed, invertible, zero-parameter, systematic BY CONSTRUCTION. `EventBundleCodec` ARG0/ARG1 role-slot bundles used throughout (fact store, reader, relational-meaning cell). Component-2 (29557): fixed bind ~= concat+linear on SINGLE-HOP completion | SHAPE mostly RIGHT (native bind IS the LISA/TPR analog). PLACE: used for storage/retrieval keys; not yet exercised in the multi-role/deep-composition regime where it should show its edge over flat concat, per component-2's own honest scoping | **NO for the bind operator** (the right primitive) -- but validating it only at single-hop is an INCOMPLETE test, not a refutation; multi-role systematicity remains open |
| 4 | **KNOWLEDGE RECALL** | Badre & Wagner controlled/strategic retrieval (anterior VLPFC) vs. automatic association; competitor suppression/RIF (Anderson, Bjork & Bjork); Collins & Loftus spreading activation; Tulving encoding specificity; HippoRAG (Gutierrez 2024) | `hd_fact_store.py` (sharded, trust-vetted, O(1) exact-key, proven to 1M facts / 100k semantic, 29531-29534); PPR spreading-activation VALIDATED on the REAL WorldTree graph (recall@10 0.28->0.38, real-structure-driven, 29539); K-sweep shows recall@100=0.69 (**reachability SOLVED**, 29543); SELECTION GATE (29541) = goal-biased select+suppress, both halves fire+dissociate | Retrieval RECALL is largely SOLVED (K-bound, not reachability-bound). Remaining gap is PRECISION: 7 HARD_FAILs show similarity-only scoring cannot isolate gold from a contains-gold pool. SHAPE: missing the controlled-retrieval-on-conflict + competitor-suppression loop the brain-QA-architecture map names as THE identified gap; DESIGNED (cheap lure-subset test) but not yet built | Retrieval mechanism (PPR/sharded store) is brain-faithful, not a shortcut. **Similarity-only SELECTION scoring is effectively the shortcut**, now being superseded by Stage 5's derivation reframe (search, not scoring) |
| 5 | **INFERENCE / MENTAL SIMULATION** | Backward-chaining goal-directed derivation (Tanji & Hoshi PFC; Rips PSYCOP); Johnson-Laird mental-model counterexample search; Pearl do-calculus/interventionist causal computation (Gopnik, Sloman) for coupled covariation; qualitative-physics/mental-animation ONLY for genuinely dynamic/perceptual prediction (Hegarty; Battaglia & Tenenbaum) | `substrate/khop.py` -- Merkle-audited K-hop, PRODUCTION-VALIDATED (FB15K-237 r@5=0.705, WebQSP 97.6%, CWQ 92.6%) but needs an explicit relation-path, no open-ended entity-linking front end. M3 bidirectional meet-in-middle search (0.62 chain-grade @depth5) -- proven search-shape, exp-trapped. Pearl do-calculus: HARD_PASS-certified at L3 (PP-270/307, recall=1.0), **completely UNWIRED from ARC**. `parse_tablestore_typed()` -- real typed-relation parser, exp-trapped | **THE central pivot.** Atom 29549 (VET-confirmed): the whole retrieve->select->combine pipeline is similarity at confidence ~0.72, never entailment. Verification-by-derivation design replaces SCORING with SEARCH (typed/directed graph, forward+backward meet, existence-of-chain as the new METRIC). Cheap connectivity gate ALREADY RUN: **RED -- COVERAGE-BOUND** (WorldTree's ~1700-2000 causal rows too sparse; confirmed via clean node-identity re-run, atom 29552; CSKG rule-supply gives a hub-present/hub-removed dichotomy that never threads coverage+selectivity, atoms 29553-29554) | **YES, historically -- the entire prior 7-attempt selection arc WAS the shortcut** (scoring standing in for reasoning). The fix is DESIGNED and partially gated (RED on the coverage precondition); the shortcut is actively being retired, this is the live frontier |
| 6 | **COHERENCE / CONSISTENCY** | Kintsch CI settle (signed W, +coherent/-contradictory/0-irrelevant, converge eps=.001); Thagard ECHO (inhibitory rival-hypothesis links); N400/Fischler STAGED negation-agnostic-mismatch -> truth-eval -> ACC response-conflict (3 separate stages); abstract opposition = labeled relational edge, NOT a geometric axis (Yih/Zweig/Platt 2012 antonym problem) | `PolarityLexicon`/`_ci_two_phase_pol` -- real Kintsch-CI-style settle with antonym/negation edges, exp-trapped, imported by nothing in the current ARC frontier. VET'd (29538): coverage fired (30.8%) but the CRUDE lexical polarity detector is ANTI-PRECISE (fires MORE on the correct choice, 22% vs 12%) -- suppresses the right answer. Root cause (research_contradiction_representation): the encoder has only similarity, never opposition (0.04% of fact-fact edges negative) -- CI's ingredient never fires, an UNFIRED mechanism not a refutation | SHAPE is right (Kintsch CI re-confirmed reusable, UNCHANGED, as the derivation design's own consistency check). PLACE: needs a POL override BEFORE the crude detector, from (i) WorldTree directional-relation type [highest-priority, cheapest, unused], (ii) WordNet antonym, (iii) negation-cue detection. METRIC: currently raw-cosine-sign (wrong, textbook antonym problem); needs a labeled relation-polarity slot | **YES** -- deriving polarity FROM cosine similarity is the shortcut (biologically and mathematically wrong). Fix (POL-override cell, `af029d82`) is designed and **IN FLIGHT**, not yet landed/VET'd |
| 7 | **DECISION / ANSWER** | Usher-McClelland leaky competing accumulator; Wang/Wong-Wang attractor; Albantakis-Deco N-alternative extension -- N candidates race under mutual inhibition, decision = margin between leader and closest rival | Bundle combiner (HD superposition + cosine-to-choice) = population-vector-style readout (Georgopoulos 1986 analog) -- **PROVEN at 0.687-0.71 given the TRUE gold set**, near oracle 0.97. Holistic-set-selection extension to SELECTION HARD_FAILed (7th consecutive fail): from a wide noisy pool, every choice can greedily assemble an equally self-supporting set; margin is NOT informative there | The DECISION/readout mechanism is SOUND and brain-faithful GIVEN a clean input set. The gap is entirely UPSTREAM (Stages 4-6 feeding it a noisy/non-discriminating set); this stage's literature-predicted mechanism is already implemented and already validated | **NO** -- the one stage that already matches the biology and does not need replacing. Its "failures" were upstream evidence-selection failures misattributed to decision |
| 8 | **LEARNING / NEUROMODULATION** | Stack of 5+ mechanisms: RPE/dopamine actor-critic (Schultz, Dayan & Montague 1997); predictive-coding residual (Rao & Ballard); 6-channel neuromodulatory precision/gain control (NE/ACh/5HT/DA/ACC-EVC/homeostasis); three-factor local credit-assignment (eligibility traces + cerebellar climbing-fiber spatial exactness); CLS offline consolidation/replay. NO single unifying principle (FEP contested, not consensus) | `exp_pfc_gate_cfrpe_trained_v2` -- RPE/TD delta-rule + Go/NoGo actor, HARD_PASS-certified (closure 0.661), trained on a SYNTHETIC nav task, never wired to real ARC correctness. `hdlab/predictive_coding.py` + Spoke1 cell -- MIDDLE_BAND (+0.031, short of bar). 6-channel neuromodulatory self-manager -- fully designed, unbuilt. LEARNER MODULE (29487) -- model-selection spine, real. Sleep-consolidation loop -- genuine MDL rule-induction on curated content, weaker on high-entropy real news | The single sharpest, previously-unnamed finding: **credit assignment is performed BY THE HUMAN DIRECTOR** via hours-long manual diagnosis -- functionally the exact role three-factor tags / cerebellar climbing fibers play, at hours-instead-of-milliseconds. No local/structural credit-assignment mechanism exists on the substrate at all | **YES, explicitly.** "Director-does-credit-assignment-by-hand" is the load-bearing shortcut standing in for this stage's machinery. Cheap decisive test designed (`substrate_rpe_tuned_combination_weight_v1`) but NOT yet built/dispatched |

---

## REUSABLE (wire, don't rebuild) vs SHORTCUTS-to-replace -- flat list

**REUSABLE, disk-verified, do not rebuild:**
`substrate/khop.py` (production-validated K-hop) - `hdlab/hd_fact_store.py` (sharded, trust-vetted, 1M-capable)
- `SemanticHDEncoder` (meaning-match AUC 0.96; reused as-is for node-unification even though content-thin --
that thinness is Stage-1's problem, not a reason to rebuild the encoder's WordNet/GloVe fusion mechanics) -
`parse_tablestore_typed()` (typed relation parser) - M3 bidirectional meet-in-middle search shape (0.62
chain-grade) - native VSA bind + `EventBundleCodec` (LISA/TPR-faithful) - the bundle combiner /
population-vector readout (0.687-0.71 given gold) - `hdlab/situation_reader.py` (Kintsch-faithful reader) -
`PolarityLexicon`/`_ci_two_phase_pol` (CI settle mechanics -- needs a new POL INPUT, not new dynamics) -
the do-calculus primitive (PP-270/307, HARD_PASS-certified) - `exp_pfc_gate_cfrpe_trained_v2` (RPE/Go-No-Go
actor, HARD_PASS-certified) - the LEARNER MODULE (29487, model-selection spine).

**SHORTCUTS TO RETIRE (named, with the replacement already designed for each):**
1. Crude cosine-derived "contradiction" (antonym problem) -> POL-override matrix (in flight, `af029d82`).
2. Flat MLP hub for meaning differentiation -> error-driven differentiated hub + multi-role binding
   (in progress: real-data validation dispatched, `af0335c6`).
3. Similarity-scoring-as-selection (the 7x HARD_FAIL lineage) -> typed-graph derivation search
   (designed, gated RED on rule-supply).
4. Director-manual credit assignment -> RPE-tuned-weight loop (designed, `substrate_rpe_tuned_combination_weight_v1`,
   not yet dispatched).
5. `_content_words()` crude ARC question-parsing -> adapt `situation_reader` for question->claim extraction
   (medium-term, Stage 2/P6 of the integration audit).
6. Off-the-shelf commonsense-KB rule supply (CSKG/ConceptNet) -> SETTLED as the wrong supply (atoms
   29553-29554); replacement = science-precise extraction from already-ingested `ARC_Corpus.txt` +
   WorldTree gold-explanation mining (Step 1 of the build plan below).

---

## THE DEPENDENCY-SEQUENCED BUILD PLAN

**STEP 0 [DONE, this session].** Cheap connectivity/coverage gate for typed-graph derivation search =
**RED, COVERAGE-BOUND** (confirmed via clean negation-aware node-identity re-run, atom 29552 -- ruled out
mega-hub artifact as the cause). Off-the-shelf commonsense-KB rule-supply (CSKG) SETTLED as the wrong
supply across 2 probes (29553-29554): hub-present-in-graph gives non-discriminative vacuous bridges
(typed_gap 0.0516, within noise); hub-removed collapses coverage toward ~0; no cap threads both needles.
Schema-routing (a structure-only fix, no new rules) also HARD_FAILed on the entity-selection axis (atom
29555's convergence: "ENTITY-SELECTION / fine-meaning axis is the wall"). **Honest current state: two
levers are both load-bearing, neither alone suffices. This step is the reason Steps 1-2 below exist.**

**STEP 1 (next, cheap, THIS WEEK).** SCIENCE-PRECISE RULE-SUPPLY EXTRACTION. Build a targeted extraction
pass over `ARC_Corpus.txt` (14M science sentences, already ingested locally) + WorldTree gold-explanation
mining, using dependency-pattern matching calibrated against WorldTree's own existing typed rows (e.g.
"if X then Y" -> IFTHEN; "as X [comparative] Y [comparative]" -> COUPLEDRELATIONSHIP; causal connectives ->
CAUSE) to grow the LICENSED rule table beyond its current ~1,700-2,000 WorldTree rows, specifically in the
content domains ARC-Challenge questions actually probe (per the fact-type diagnostic: IFTHEN/CAUSE/
COUPLEDRELATIONSHIP/REQUIRES). This is NOT a repeat of the CSKG probe (that used a generic, unfiltered
commonsense graph); this targets SCIENCE-DOMAIN, TYPED, causal/conditional sentences specifically, the
gap the CSKG probes explicitly diagnosed as needed next ("need SCIENCE-PRECISE extraction," atom 29554).
**Cheap can-fail gate:** re-run the SAME connectivity/coverage harness already built
(`research_verification_by_derivation_reasoning_pivot_2026-07-25.md`, section 4) with the expanded table.
GREEN if correct-choice coverage >=0.35 AND selectivity gap >=0.15 AND typed-graph selectivity beats the
untyped-similarity-null control. RED again (coverage still <0.15) would mean the extraction quality/recall
itself is the bottleneck, not corpus availability -- escalate to a broader source (CK-12/OpenStax full-text)
before trying a third rule-supply route.

**STEP 2 (contingent on Step 1 GREEN or YELLOW).** Build `hdlab/reasoner.py` -- the integration audit's P5,
the currently-MISSING composed entry point. This promotes, per the audit's own prioritized order:
P1 `parse_tablestore_typed` -> `hdlab/typed_rule_parser.py`; P3 the M3 meet-in-middle search shape,
superseding the weaker K=2 `hdlab/multi_hop.py`; P4 `PolarityLexicon`/CI with the POL-override (contingent
on the in-flight `af029d82` cell landing+VET'ing first). Compose: reader (or, short-term, the crude
`_content_words()` extractor honestly flagged as a stand-in) -> typed-graph construction -> forward-from-
givens/backward-from-candidate meet-in-middle derivation search -> CI consistency check (Johnson-Laird
counterexample rejection) -> selection. Run the FULL build (verification-by-derivation note, section 3)
scoped to the coverage-passing subset identified in Step 1, with BOTH must-fail controls mandatory:
SHUFFLE_DIRECTION (collapse toward chance if genuinely using directionality) and UNTYPED_SIMILARITY_NULL
(isolate whether any lift is from the search shape alone vs. specifically from typing). **This produces the
FIRST demonstrable glass-box reasoning trace** -- the USER's stated success criterion. HARD-PASS bands
exactly as pre-registered in that note's section 6 (coverage-subset accuracy >=0.50, beats similarity
pipeline by >=0.10, beats both must-fail controls by >=0.15, beats chance+0.15 on the `chal_lure`/surface-
trap subset specifically).

**STEP 3 (parallel, cheap, independent of 1-2, reuses an ALREADY-CERTIFIED primitive).** Wire the do-calculus
primitive (PP-270/307) for the COUPLEDRELATIONSHIP item subclass, per
`research_mental_simulation_grounding_causal_models_arc_2026-07-24.md`'s design: triage a subset of items
whose gold answer requires a monotonic covariation across >=2 named variables not co-stated in one sentence
(rotation-rate/day-length, pressure/volume, etc.); Arm A = current semantic retrieval (real baseline), Arm B
= extract the qualitative direction as a first-class COUPLEDRELATIONSHIP triple and propagate an
intervention through the already-certified do-calculus code path. Pre-registered predictions 1-3 in that
note apply verbatim (subset-size gate >=5%/8%; Arm B beats Arm A by >=10pp on the subset; Arm A holds on
single-hop items outside the subset). This is genuinely independent of Steps 1-2 (uses a different,
already-working mechanism) and should NOT wait on the derivation-search gate.

**STEP 4 (after Step 2 lands with a stable held-out metric).** Credit-assignment cheap test
(`substrate_rpe_tuned_combination_weight_v1`, per `research_learning_control_neuromodulation_inventory_2026-07-24.md`):
take ONE hand-set scalar the reasoner now depends on (e.g. `tau_unify`'s node-merge threshold, or a CI
settle edge weight), adapt it online via the brain-canonical duration-extension eligibility rule (dopamine-LR
note) keyed to real per-question correctness on a labeled dev slice, vs `ARM_FIXED` / `ARM_SHUFFLED_RPE`
(anti-tautology guard) / `ARM_RANDOM_WALK_WEIGHT` (isolates whether the REWARD SIGNAL's content, not mere
weight variance, is doing the work). This is the FIRST piece of Stage 8's machinery wired to a real
correctness signal rather than a synthetic task -- the concrete first step toward closing the
credit-assignment gap, not a claim of closing it.

**STEP 5 (the deep, ongoing macro-investment; runs in parallel with 1-4, sequenced LAST for scope-sharpening
not low priority).** Continue the REAL-DATA VALIDATION of the learned-differentiation hub (already IN
FLIGHT, `af0335c6`) past the toy 9-pair noise floor onto real WorldTree/ARC content, and test multi-role
native binding for compositional generalization (component-2's genuinely untested edge, per
`research_native_binding_compositional_generalization_2026-07-25.md`). **Per the answer-conditioned-
selection note's own explicit sequencing logic (reused here as the general principle for the whole plan):
ship the cheaper mechanism fixes first; their RESIDUAL failure pattern self-diagnoses whether grounding is
genuinely needed and where.** Concretely: log every node-merge pair above `tau_unify` during Step 2's build
(the derivation note's own section 5 flags this exact risk -- loose unification could silently merge
"nuclear fuel" and "falling water" into one node because both are near "power plant energy source") and use
those SPECIFIC confusions as the targeted curriculum for the meaning-differentiation rebuild, rather than a
from-scratch investment with no diagnostic target.

**SUCCESS CRITERION (USER's mandate, operationalized):** on a held-out ARC-Challenge item -- especially from
the `chal_lure`/surface-trap subset (lure_rate 0.23, where a distractor out-overlaps the correct answer) --
the system outputs (a) an accuracy on the coverage-subset clearing Step 2's pre-registered HARD-PASS bands,
AND (b) a fully inspectable derivation: the exact chain of typed rules connecting the question's givens to
the chosen answer, and why the other 3 choices could not be derived or were rejected by the consistency
check. This is the literal, demonstrable "show reasoning" deliverable the mandate calls for -- not a
similarity score with no "why," which is what every prior HARD_FAIL produced.

---

## Cheap decisive test (top-level, for this whole plan)

Already executed: the Step-0 connectivity/coverage gate (RED). The NEXT cheap decisive test is Step 1's
re-run of that SAME gate with the expanded science-precise rule table -- cheap because it reuses the
already-built harness (`research_verification_by_derivation_reasoning_pivot_2026-07-25.md` section 4),
requires no new scoring function, no learned weights, no backtracking pass -- only graph construction and a
BFS reachability check. GREEN unblocks Step 2 (the reasoner build); RED again would redirect to a broader
extraction source before any further reasoner investment, per that section's own pre-registered RED-light
language.

## Falsifiable predictions (rolled up per step, HARD-PASS / HARD-FAIL, calibration-penalty applied)

- **Step 1 (rule-supply):** HARD-PASS = coverage >=0.35 AND selectivity gap >=0.15 AND typed>untyped on the
  re-run gate. HARD-FAIL = coverage stays <0.15 even after science-precise extraction (would mean extraction
  RECALL, not corpus availability, is the bottleneck). P(GREEN) = 0.40 (deflated; CSKG probes already showed
  coverage CAN be raised via broader supply, 0.07->0.56, but selectivity/domain-precision for a
  science-specific extraction is unproven).
- **Step 2 (reasoner build):** verbatim per `research_verification_by_derivation_reasoning_pivot_2026-07-25.md`
  section 6 -- coverage-subset accuracy >=0.50, beats similarity pipeline by >=0.10, beats both must-fail
  controls by >=0.15, beats chance+0.15 on `chal_lure`. HARD-FAIL = statistically indistinguishable from
  either must-fail control (mechanism degenerated back to connectivity-similarity with extra steps), or no
  lift specifically on `chal_lure` (doesn't fix the failure mode it targets). P(HARD-PASS | Step1 GREEN) =
  0.35-0.40 (novel-synthesis capped at 0.50, per that note's own calibration).
- **Step 3 (do-calculus routing):** verbatim per `research_mental_simulation_grounding_causal_models_arc_2026-07-24.md`
  predictions 1-3. P(subset non-trivial) = 0.40; P(Arm B beats Arm A on subset by >=10pp) = 0.40 (deflated,
  capped below the general novel-synthesis ceiling).
- **Step 4 (credit-assignment):** verbatim per `research_learning_control_neuromodulation_inventory_2026-07-24.md`.
  HARD-PASS = RPE-adaptive arm beats fixed by >=0.03 AND beats random-walk by >=0.02 AND shuffled-RPE
  collapses to fixed AND cv<0.05. P(HARD-PASS) = 0.30 (deflated per the compounding-uncertainty convention
  already used in that note for composing two independently-designed pieces onto a new target).
- **Step 5 (meaning foundation, ongoing):** no fresh HARD-PASS/FAIL band re-derived here -- the in-flight
  real-data validation (`af0335c6`) and the multi-role binding test both carry their own pre-registered bands
  from their originating notes (29556/29557 lineage); this note's contribution is the SEQUENCING logic
  (surgical targeting via Step 2's node-merge log), not a new calibration.
- **Joint, full stack (Step 0 through 2, "demonstrated reasoning" criterion):** P ~= 0.13-0.16 (Step-1-GREEN
  0.40 x Step-2-HARD-PASS-given-GREEN 0.35-0.40), carried forward from the pivot note's own compound estimate
  and NOT improved by this synthesis (the RED gate this session, if anything, is a live reminder this
  estimate has a real, not-yet-cleared precondition, not a formality).

---

## Cross-thread synthesis

This note does not open a new empirical claim -- its contribution is assembling the ~10 already-VET'd
drills and ~25 landed experiments into one dependency-ordered sequence and cross-checking each stage's
"OUR version" against the hdi_testbed integration audit's disk-verified wiring map, which is the one piece
of infrastructure evidence that reframes the whole exercise: most of what looks like "missing capability"
across Stages 2-6 is actually **capability that exists, is honestly benchmarked, and sits unpromoted in a
terminal exp-cell with no consumer.** The single genuinely open empirical question this note surfaces (not
previously stated this way) is that the derivation-search reframe (Stage 5, atom 29549's pivot) and the
prior scoring-based selection arc (29544-29555) BOTH independently converge on the SAME two-part diagnosis
-- rule-supply breadth AND fine-content discrimination are both load-bearing, neither alone sufficient --
even though they were investigated via completely different mechanisms (similarity scoring vs. typed-graph
search). That convergence, from two structurally different methods hitting the same wall, is stronger
evidence for the two-lever diagnosis than either arc alone would provide, and directly justifies Step 5's
"sharpen the meaning investment using Step 2's residual failures" sequencing rather than either abandoning
the meaning investment or attempting it in isolation before the cheaper fixes are tried.

## Substrate-product implications

If Steps 1-2 clear their HARD-PASS bands: the productizable claim becomes exactly what the USER's mandate
demands -- "here is the exact chain of typed rules that connects this question to this answer, and here is
why the other three choices could not be derived" -- a fully auditable reasoning trace no similarity-score
combiner (however conditioned, set-constructed, or enriched) can honestly produce, since a similarity score
has no notion of "why," only "how similar." This composes directly with the existing FDA/regulatory-
audit-traceability product angle (PP-215, do-calculus's own step-traceability) and extends the same
audit-chain story already used for the certified bidirectional multihop cell from dense-matrix pointer-
chains to symbolic, human-readable typed-rule chains. If Step 1 or Step 2 HARD-FAILs: the negative results
are still diagnostically sharp (coverage-bound vs. mechanism-bound are cleanly distinguished by the
pre-registered bands) and redirect cleanly -- to a broader extraction source (Step 1 HARD-FAIL) or to
accepting that entailment-vs-similarity, while real in the literature, is not separable at this KG's scale/
depth (Step 2 HARD-FAIL, per that note's own honest framing) -- rather than motivating a 6th scoring-function
variant, which the whole 2026-07-24/25 arc has already shown is a dead-end direction.

## Citations (verified count -- rolled up, not freshly re-verified this cycle)

This note performed NO new WebSearch/WebFetch; every citation below is reused-with-attribution from the
10 source notes cited throughout, each of which independently verified its own citations at dispatch time:
brain_qa_architecture_completeness (~85), verification_by_derivation_reasoning_pivot (23),
mental_simulation_grounding_causal_models (42), learning_control_neuromodulation_inventory (46),
holistic_set_selection (28), drill_answer_conditioned_selection_biology (16 sources listed),
contradiction_representation_and_settle_dynamics (27), native_binding_compositional_generalization
(partial read this cycle, own count not re-tallied here -- treat as unverified-count, flagged honestly),
arc_retrieval_biology_and_design (citations present, not separately counted in this synthesis),
combiner_robustness_imperfect_facts (citations present, not separately counted). **Approximate aggregate:
~270+ distinct citations across the synthesized corpus**, with meaningful cross-note overlap (Kintsch
1988/1998, Tulving 1972/1973, Usher & McClelland 2001, and Badre & Wagner 2007 each independently cited by
3+ of the source notes -- a mild corroboration signal, not inflation). Per this note's own synthesis
mandate, no individual citation was independently re-verified in this cycle; treat citation-level details as
inherited at whatever confidence the originating note assigned them (most are flagged primary-source-
verified within their own notes; a minority are explicitly flagged secondary/unverified in-line, e.g. the
Kuperberg 2024 predictive-coding N400 claim in the contradiction-representation note).

## Next-drill candidate

Per this session's own field-coverage state (this topic-family is a cognitive-architecture/biology
synthesis feeding the ARC/reasoning program, orthogonal to the substrate-physics field taxonomy
`research_field_advisor.py` tracks): the natural next DRILL (as opposed to build step) is a focused 2x-depth
scan on SCIENCE-DOMAIN rule/relation EXTRACTION methods specifically (dependency-pattern mining for
causal/conditional sentences from raw science text, e.g. distant-supervision or seed-pattern bootstrapping
for IFTHEN/CAUSE/COUPLEDRELATIONSHIP-shaped sentences) -- this is the literature Step 1 above needs and has
not yet been separately drilled; everything upstream of it (derivation search design, contradiction/POL
design, do-calculus routing, credit-assignment design) is already drilled and just needs building.
