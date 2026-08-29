---
problem: situation_model_has_no_tested_temporal_order_comprehension
status: SOLVED
bar: "PASSES only with ALL of: 1. A per-event temporal-ORDER register (built in experiments/): default narration order, OVERRIDDEN by the extracted tense/aspect + explicit connectives, answering before(x, y) / order(). Copy the computation; SWEEP the representation (reuse transitive_ordering / interval bookkeeping). 2. Answers 'did X happen before Y?' CI-separated over the NARRATION-ORDER floor (assume telling order = event order, recomputed on the same population), on real narrative (or a construction gold that isolates the mechanism + a real-prose serve, like the SPACE organ). The info-free twin (shuffled tense labels / random order) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. A POSITIVE control the floor CANNOT get: a past-perfect FLASHBACK ('she had left before he arrived') where narration order != event order. 3. SERVES or COMPOSES: show the order model is real on prose (a mined past-perfect/connective serve) OR that it constrains a downstream inference (e.g. a cause must precede its effect) -- wire-don't-island, not a second island. 4. One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "before(x,y) node-exact accuracy on the construction gold that ISOLATES the ordering mechanism (real English tense/connectives, 4 discriminating structures, n=103 committed pairs / 98 items): COMPOSED register (default narration OVERRIDDEN by tense/aspect+connective cues) = 1.000 [1.000,1.000] vs the recomputed NARRATION-ORDER floor 0.272 [0.194,0.349]. Positive control (past-perfect FLASHBACK subset): register 1.000 vs narration 0.000. Downstream SERVE (flashback-causal direction, n=12): temporal-constrained cause-before-effect 1.000 [1.000,1.000] vs order-agnostic narration 0.000."
floor: "NARRATION-ORDER floor (telling order == event order), recomputed on the SAME population = 0.272 [0.194,0.349] full-pop / 0.000 on the non-linear (flashback/reorder) subset. Register lower CI 1.000 > floor upper CI 0.349. Serve floor (order-agnostic narration causal direction) 0.000."
controls: "(1) INFO-FREE TWIN (edge-direction scrambled -- destroys BOTH tense and connective info, keeps coverage): full-pop 0.527, null p95 0.602 -> LOSES CI-separated (register 1.000 > 0.602). (2) POSITIVE CONTROL: past-perfect flashback subset register 1.000 vs narration 0.000 -> the metric CAN move / narration provably cannot get these. (3) LINEAR no-regression: register 1.000 == narration on linear-order items (no over-reordering). (4) SERVE TWIN: causal-direction twin 0.472 (p95 0.727), temporal 1.000 loses it; linear-causal control 1.000 == 1.000. (5) REPRESENTATION control (Phase B): tiebreak==truth confound REMOVED (random true order, unrelated index tiebreak) -> the continuous line adds NO accuracy over discrete (max continuous-discrete = 0.0)."
files_changed: "experiments/_temporal_order_register.py; experiments/exp_temporal_order_before_after_v1.py; experiments/exp_temporal_order_distance_effect_v1.py; experiments/exp_temporal_order_serves_causal_v1.py; experiments/exp_temporal_order_extraction_recall_v1.py; experiments/exp_causal_force_dynamics_probe_v1.py (de-risking probe for the causation next-problem); verification/test_temporal_order_register.py; notes/problems/situation_model_has_no_tested_temporal_order_comprehension/{SOLVED.md, real_prose_hand_adjudication_2026-08-29.md, adjacent_components_brain_fidelity_map_2026-08-29.md, next_problem_scoping_causation_force_dynamics_2026-08-29.md}"
reverify: ".venv/Scripts/python.exe verification/test_temporal_order_register.py   # 8/8 ; then .venv/Scripts/python.exe experiments/exp_temporal_order_before_after_v1.py --mode full   # HARD_PASS 1.000 vs 0.272, twin p95 0.602 ; and .venv/Scripts/python.exe experiments/exp_temporal_order_serves_causal_v1.py --mode full   # HARD_PASS temporal 1.000 vs narration 0.000"
---

# The situation model's TIME dimension is now a TESTED before/after register -- and the brief's premise is partly REFUTED by the disk

## DISK OUTRANKS BRIEF (the most important finding first)
The brief says "the reader has NO tested TEMPORAL-ORDER COMPREHENSION ... NOTHING composes tense + aspect +
temporal connectives into a per-event ORDER model that answers before/after." **The disk disagrees on
"nothing composes," and the disk wins:**
- The temporal-order MECHANISM was BUILT on 2026-07-24: `experiments/_temporal_ordering.py` (single-frame
  past-perfect demotion + connective reorder) and `experiments/_temporal_ordering_multiframe.py` (a
  glass-box constraint-graph + topological-sort running timeline). BOTH landed **HARD_PASS**
  (`exp_read_temporal_chronological_event_order_v1`: CUE 1.000 vs TEXT 0.000; `exp_read_temporal_multiframe_chronology_v1`:
  MECH 0.895 vs narration TEXT 0.421).
- It is even **WIRED into the live reader**: `hdlab/situation_reader.py` imports the multiframe module and
  its `_read_timeline` produces per-sentence `TimelineFrame`s with `chrono_order` + a `reordered` flag.

So this was **NOT a from-scratch build**. What was genuinely absent -- and what the bar actually asks for --
is (a) a **queryable `before(x,y)`**, (b) **scored on real narrative** with the narration-order floor + an
**info-free twin** + **CI** + a **coverage/base-rate**, (c) a **representation sweep** (discrete vs
continuous), and (d) a **downstream serve**. None of those existed. I built and validated all four, and I
found and fixed concrete **wiring gaps** in the live path. That is the deliverable.

## What was built
`experiments/_temporal_order_register.py` -- the queryable **per-event temporal-order register** the bar
asks for. It COMPOSES the landed discrete front-end (tense/aspect + connective -> constraint graph ->
toposort) over the WHOLE passage and exposes `before(x, y)`:
- **`ComposedRegister`** = the bar's exact wording: **default narration order, OVERRIDDEN by the extracted
  tense/aspect + connective cues** where the mechanism has evidence (never confidently wrong -- abstains to
  narration on no-cue pairs, like a real reader).
- **Two representations swept** (bar step 1): `DiscreteOrderRegister` (toposort ordinal ranks) and
  `ContinuousOrderRegister` (the landed `hdlab.transitive_ordering` MAGNITUDE LINE -- coordinate gap = a
  graded confidence margin).
- **Two live-wiring fixes**, both brain-grounded: (i) runs over the whole passage carrying reference time
  ACROSS sentences (Past Discourse-Linking Hypothesis; the live `_read_timeline` is per-sentence); (ii)
  fires on connective-only reorderings the live reader's `"had" in sentence` gate DROPS ("Before he ate, he
  prayed").

## What was measured
1. **before/after CI-separated over the narration floor** (`exp_temporal_order_before_after_v1`, construction
   gold that ISOLATES the mechanism -- real English tense/connectives, 4 discriminating structures
   PP_FLASHBACK/CONN_REORDER/MULTIFRAME/LINEAR_CTRL, n=103 committed pairs). **COMPOSED 1.000 [1.000,1.000]
   vs NARRATION 0.272 [0.194,0.349]**; info-free twin (edge-direction scrambled) 0.527, null **p95 0.602 ->
   LOSES** CI-separated; **positive control** (past-perfect flashback) register 1.000 vs narration 0.000;
   linear control no regression (1.000 == narration).
2. **Real-prose base rate** (25 LitBank novels, all adjacent event pairs): **8.74%** of pairs are reordered
   by a temporal cue vs narration order (cue-window rate 47%). So **narration order is WRONG on ~1 in 11 real
   event pairs -> the TIME dimension is a LIVE signal on real prose, NOT a "narration suffices" negative.**
   HONEST CAVEAT: hand-adjudication of a 22-sample (see `real_prose_hand_adjudication_2026-08-29.md`) found
   **0 confident errors** but showed the 8.74% **over-counts true flashbacks** -- a majority are stative /
   generic / reported past-perfect ("had been", "had once kept") where the pluperfect correctly marks
   anteriority but the pair is not a narrative flashback. True narrative-flashback incidence is lower.
3. **Representation fork MEASURED, not asserted** (`exp_temporal_order_distance_effect_v1`, Phase B). The
   continuous magnitude line **reproduces the human symbolic-distance-effect signature** -- confidence margin
   grows monotonically with temporal distance (0.66 -> 3.98; slope **+0.66**) -- which the discrete toposort
   CANNOT (accuracy flat, slope ~0); and its margin is **calibrated** (selective acc 0.689 @ top-25% vs 0.576
   @ all under noise). **BUT it adds NO ordering accuracy or noise-robustness** (discrete >= continuous at
   every noise level; max continuous-minus-discrete = 0.0), and it does **NOT** reproduce the TCM forward
   asymmetry (symmetric 1.0/1.0 -- our settled line is not a drifting context). **Verdict: keep the DISCRETE
   toposort as the primary register; LAYER the continuous line as an optional graded-confidence read-out.**
4. **Downstream SERVE** (`exp_temporal_order_serves_causal_v1`): temporal order CONSTRAINS causal direction
   (cause precedes effect). On flashback-causal sentences where the anterior cause is mentioned AFTER its
   effect, the order-agnostic reader default scores **0.000** causal-direction accuracy; the temporal
   register scores **1.000 [1.000,1.000]**; twin 0.472 (p95 0.727) loses; linear-causal control 1.000 == 1.000.

## The wall I drilled the brain's way (owner: "if the brain can do it, we should too")
Running the register on raw LitBank exposed a real-prose PRECISION wall -- but it is an **EXTRACTION** wall,
not an ordering-logic wall. Trace of the one confident error found (Persuasion): "precisely such had the
paragraph originally **stood** ... but sir walter had **improved** it" -> the register said improved-before-
stood (WRONG). Cause: the shared extractor's fixed **3-token `had`-lookback** misses a pluperfect whose
participle is 4 tokens from `had` (subject-aux inversion + adverb), so "stood" is mistagged simple-past.
**The brain binds the perfect auxiliary to its participle via a CLAUSE-LEVEL syntactic dependency (left-IFG
parse of "have + V-en"), not a fixed window.** I built that: `promote_clause_pluperfect` binds a `had` to
the next content verb in its clause, bounded by clause breaks / subordinators / intervening finite verbs
(possession-`had` guarded). Converts the stood/improved confident-WRONG to an **abstain**, no construction-
gold regression, no reorder-count blow-up (131 -> 131, so not over-firing).

**Then I QUANTIFIED the wall against a dependency-parse reference** (`exp_temporal_order_extraction_recall_v1`,
spaCy `en_core_web_sm` aux-dependency = a `had`-governed participle; spaCy itself errs on archaic syntax so
this is a LOWER bound). On 139 real-LitBank reference pluperfects, the story REFRAMED the wall:
- **27% are COPULAR/stative "had been X"** ("had been an excellent woman", "had been ill") -- a prior STATE,
  NOT an orderable event. Our extractor correctly SKIPS these; spaCy's "pluperfect" reference over-counts by
  including them. This is the DROPPED perfect-ASPECT resultant-state channel (a different dimension -- below).
- **EVENT-pluperfect recall** (the ordering-relevant 101): fixed-WINDOW **0.911**, +CLAUSE-binder **0.941**
  (+0.030). **So the tense-extraction wall for EVENT ordering is SMALL (~6% residual)** -- the ordering
  mechanism is NOT extraction-capped in practice, and a full syntactic parse buys only ~6% on events. The
  earlier alarming "recall ~0.81" was an artefact of counting copular STATES as missed events.

## What I did NOT establish (withdraw-first if wrong)
- **The 1.000 CI-separated headline is on a CONSTRUCTION gold that ISOLATES the ordering mechanism** (real
  tense/connectives, by-construction order), NOT unrestricted natural prose. It proves the ordering LOGIC is
  correct given clean extraction. **First thing I would withdraw:** any implied claim that the register
  answers before/after at 1.000 on unrestricted natural narrative -- on raw prose it is EXTRACTION-limited
  (the had-window wall), and the real-prose burden is carried by the base rate (8.74%) + the hand-adjudicated
  sample (0 confident errors, but ~2/3 of fired reorderings are stative/backstory, not flashbacks) + the
  causal serve, NOT a natural-prose CI eval. I deliberately did NOT headline an auto-mined natural before/after
  gold: my medial-connective mining is ~as noisy as the mechanism (it picks up prepositional/adverbial
  before/after -- "ten years BEFORE", "soon AFTER his death"), so it is reported as a NOISY DIAGNOSTIC only
  (mech 0.63 ~ narr 0.69), reproducing the SPACE organ's documented lesson that a noisy auto-mined natural
  gold is not an instrument.
- **The continuous magnitude line is a FIDELITY/CONFIDENCE layer, not an accuracy upgrade.** It reproduces the
  distance-effect signature and a calibrated margin, but I would withdraw any claim that it improves before/
  after ACCURACY (it does not -- discrete is equal-or-better), and it does not reproduce the forward asymmetry.

## KEY REALIZATIONS (the enabling moves)
1. **Read the disk before building.** The brief's "nothing composes tense into an order model" was refuted by
   two landed HARD_PASS cells + live wiring; the real gap was the QUERYABLE test + representation decision +
   wiring fixes. Checking `experiment_index` and `situation_reader` first reframed a "build" into a
   "measure + decide + wire" -- and honoring disk-over-brief IS the deliverable, not a footnote.
2. **The info-free twin caught a real control bug in my OWN harness.** Re-seeding the twin RNG per item made
   every single-edge item flip together -> a bimodal null with p95 = 1.0 (a twin that "won"). Fixing it to
   independent flips gave the honest p95 0.602. And the twin had to scramble BOTH cues (edge DIRECTION), not
   just tense labels -- a tense-only twin left the connective intact and still reordered "Before he ate...".
3. **The real-prose wall is EXTRACTION, not ordering.** The stood/improved trace localized it to the fixed
   had-window vs the brain's clause-level aux->participle dependency. The ordering LOGIC is provably correct
   on clean cues (1.000); drilling the wall the brain's way turned a confident-wrong into an abstain.
4. **The representation fork was decided by MEASUREMENT, and I caught my own confound.** My first
   noise-robustness run made the continuous line look worse because the discrete toposort's index tiebreak
   COINCIDED with the ground-truth order (identity chronology). Randomizing the true order (tiebreak unrelated
   to truth -- as real prose has narration != chronology) showed a near-tie. The continuous line's genuine,
   non-confounded value is the human distance-effect signature + calibration, NOT accuracy.
5. **Splitting the extraction "wall" by aspect flipped it from a problem into a next-problem.** The raw
   pluperfect recall (~0.81) looked like a real cap until I split the reference: 27% of "had"-pluperfects are
   copular STATES ("had been an excellent woman"), which are not events and are correctly skipped. On genuine
   EVENTS the recall is 0.941. So the ordering mechanism is not extraction-capped -- and the copular 27% is not
   a bug but a DIFFERENT dimension (prior entity state) we do not yet build. Measuring the RIGHT denominator
   turned a false wall into the highest-incidence next-problem.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
The situation-model TIME dimension: **brain structure PINNED** (Zwaan & Radvansky event-indexing TIME;
Reichenbach E/R/S reference-time; hippocampal-entorhinal temporal context / MTL time cells). **Our fidelity:**
the discrete Reichenbach/connective front-end is a faithful copy of the linguistic COMPUTATION (PINNED); the
order-register REPRESENTATION was OUR-INVENTION-UNDER-TEST and is now **MEASURED** -- discrete toposort is
adequate for ordering accuracy + robustness; a continuous magnitude line (transitive_ordering) reproduces the
human distance-effect + calibration signature but not accuracy and not the forward asymmetry. **Deviations to
record:** (a) tense EXTRACTION uses a fixed 3-token had-window (OUR-INVENTION placeholder for the brain's
clause-level aux->participle syntactic dependency) -- partially fixed here; (b) perfect ASPECT's resultant-
state channel is DROPPED (we use "had V-en" only for order; the brain also feeds the resultant state to the
entity/state dimension -- Ferretti/Kutas/McRae 2007); (c) the continuous line is a settled magnitude, not a
drifting TCM context, so it lacks the forward-contiguity asymmetry.

## Adjacent components (evaluated for brain-fidelity + optimization, per owner 2026-08-28)
Full disk-grounded 5-dimension map: `adjacent_components_brain_fidelity_map_2026-08-29.md` (Zwaan's TIME /
SPACE / CAUSATION / ENTITIES / GOALS, each with built-status + brain-fidelity + leverage). Highlights:
- **`hdlab/situation_reader._read_timeline` (the live TIME wiring) -- UNDER-FIRES; a WIRING fix, high leverage.**
  Gates on `"had" in sentence` (drops connective-only reorderings) + runs PER-SENTENCE (no cross-sentence
  flashback frame, no reference-time carried forward -- PADILIH); exposes no `before(x,y)`. **Fix proposed below.**
- **CAUSATION (`_causal_network` / `_read_causation`) -- the LEAST genuinely-built dimension, and it now has
  its missing ingredient.** Live organ is order-agnostic + "reducible to connective-else-most-recent" (its OWN
  VET), despite heavy `exp_causal_*` exploration. Cause MUST precede effect; the TIME register supplies exactly
  that (Phase C: 1.000 vs 0.000). **Strongest candidate NEXT PROBLEM: a genuine causal-direction/plausibility
  organ consuming the temporal precedence constraint.**
- **Perfect-ASPECT resultant/prior-STATE channel -- a DROPPED channel, and it is HIGH-INCIDENCE.** MEASURED:
  **27% of real 'had'-pluperfects are copular "had been X"** (prior entity STATES) that nothing consumes as
  entity state-history. **Candidate NEXT PROBLEM: a per-entity prior/resultant-STATE register** (feeds the
  ENTITY dimension; composes with the SPACE register's interval bookkeeping). PINNED (Ferretti/Kutas/McRae 2007).
- **The shared tense EXTRACTOR (fixed 3-token had-window) -- OUR-INVENTION placeholder, but EVENT recall is
  already 0.941** (clause-binder). A full syntactic parse buys only ~6% on events -> LOW priority vs the two above.
- **ENTITIES/coref (~0.65 real-prose)** caps who-moved/who-did-what across all dimensions -- a standing cap (mapped).

## Proposed hdlab landing (strategy lands; Q111 -- I do not write hdlab/)
1. **Promote `experiments/_temporal_order_register.py` -> `hdlab/temporal_order_register.py`** as a first-class
   organ: passage-level `build()`, `before(x, y)`, `order()`, DEFAULT narration OVERRIDDEN by cues, with the
   brain-faithful `promote_clause_pluperfect` binder ON.
2. **Fix `situation_reader._read_timeline`:** run over the WHOLE passage (not per-sentence), REMOVE the
   `"had"`-only gate (also fire on connective-only reorderings), apply the clause-pluperfect binder -> carries
   reference time across sentences (PADILIH). This is the load-bearing wiring change.
3. **Keep the DISCRETE toposort as the primary register** (equal-best accuracy, noise-robust, glass-box, no
   torch). Expose the CONTINUOUS `transitive_ordering` magnitude-line coordinate as an OPTIONAL graded-
   confidence / distance-effect read-out where downstream needs calibrated temporal confidence.
4. **Wire the SERVE:** have `_read_causation` consult the temporal register to assign cause-before-effect
   direction instead of the order-agnostic default (Phase C: 1.000 vs 0.000 on flashback-causal).

## TLDR
When you read "He arrived. She had already left," you know she left first, even though "arrived" is told
first. The reader already had the machinery to work this out (built and passing since July, and even plugged
in) -- but nobody had ever ASKED it "did X happen before Y?" on real text, checked it against the naive
"things happened in the order they're told" guess, or decided how it should store the timeline. I built the
question-answerer and tested it: on a clean test it is right 100% of the time versus 27% for the naive guess,
a scrambled-cue version drops to chance (so the skill is really reading the tense/"before"/"after" words), and
it correctly handles the past-perfect flashback the naive guess always gets wrong. On real novels, the naive
"telling order = real order" guess is wrong about 1 time in 11 -- so this genuinely matters. I fed it into
cause-and-effect: on "The bridge collapsed. The flood had weakened it," the naive reader blames the collapse
for the flood; the timeline correctly says the weakening came first and caused the collapse (100% vs 0%).
Two brain-faithfulness findings: (1) the brain stores time on a stretchy "ruler" where far-apart events are
easier to tell apart -- I reused our number-line tool and it reproduces exactly that pattern and gives a
usable "how sure am I" score, but for plain before/after it is no more accurate than the simpler list, so keep
the list and add the ruler only as a confidence gauge; (2) the real wall on messy prose is not the ordering
logic but READING the tense correctly ("had the paragraph originally stood" -- the "had" is far from "stood"),
which I fixed the brain's way by binding "had" to its verb across the clause.

## QUESTIONS
None.

## NEXT STEPS (ranked; the push-round adjacency map sharpened these)
1. **Strategy: land the wiring fix** -- promote the register to `hdlab/temporal_order_register.py`, fix
   `_read_timeline` (whole-passage, drop the had-gate, clause-pluperfect binder), point `_read_causation` at
   the temporal register for causal direction. Highest-CERTAINTY gain (a built-but-under-firing organ becomes
   live, queryable, correctly-firing).
2. **Next problem -- CAUSATION via FORCE DYNAMICS (fully scoped in `next_problem_scoping_causation_force_dynamics_2026-08-29.md`).**
   The least genuinely-built Zwaan dimension (live organ = connective + adjacency placeholder; NO Wolff
   CAUSE/ENABLE/PREVENT typing on disk -- verified). Brain mechanism: force dynamics (Talmy/Wolff) TYPES the
   edges of the causal network (Trabasso), precedence GATES (reuse the TIME register + the landed
   `exp_causal_bitemporal_composition` harness), knowledge VALIDATES. Glass-box lexicon exists (VerbNet->Event
   Force Dynamics; FrameNet Causation family). KILLER can-fail test: **PREVENT** ("the sandbags prevented the
   flood" -> no flood node), where the link-the-nearest placeholder fails by construction. Cautionary disk
   precedent: formal do-calculus routing already HARD_FAILed -> the force-dynamic (perceptual/conceptual)
   route is the more brain-faithful bet. **DE-RISKED with a built probe** (`exp_causal_force_dynamics_probe_v1`):
   glass-box force-dynamic typing scores 1.000 on the PREVENT killer (vs placeholder 0.000) and 1.000 on
   CAUSE-vs-ENABLE where a verb-shuffle twin is at chance 0.499 -- the core bet is demonstrated; the P~=0.45
   risk now sits only on the full problem's extraction/lexicon-coverage/real-prose extras, not the typing.
3. **Next problem -- a per-entity prior/resultant-STATE register** for the DROPPED copular-aspect channel
   (MEASURED 27% of real 'had'-constructions: "had been X"). Feeds the ENTITY dimension; PINNED
   (Ferretti/Kutas/McRae 2007). High incidence, currently absent.
4. **Lower priority: a syntactic aux->participle parser** -- buys only ~6% on EVENT pluperfect recall (already
   0.941); do it only if the causal/state organs need higher tense precision.
5. **Optional fidelity: a drifting temporal-context representation** only if a downstream episodic RECALL task
   needs the forward-contiguity asymmetry our settled magnitude line lacks (a recall signature, not a
   before/after judgment capability).
