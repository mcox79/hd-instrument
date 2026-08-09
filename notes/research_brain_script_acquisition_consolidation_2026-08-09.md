# Research drill: the brain-faithful rule for acquiring, consolidating, and generalizing event SCRIPTS/SCHEMAS from narrative exposure (2026-08-09)

Director task: define, from primary psych/neuro literature, (1) the SELF-SUPERVISED SIGNAL that
flags a not-yet-understood narrative gap (what the loop's FLAG stage should fire on), (2) the
CONSOLIDATION+GENERALIZATION rule (when a script schema is COMMITTED vs stays episodic), and (3)
the GUARD's brain basis -- at SCRIPT/SCHEMA grain (recurring event sequences with typed roles), not
word grain. Trigger: this session diagnosed the currently-wired FLAG teacher
(`hdlab.consequence_learning_loop.teacher_verdict(signal_mode="signal_a_only")`, isolated
verb-lemma MET/UNMET polarity) as "too weak + wrong-grain." Method: 3 parallel Sonnet lit-scans on
non-overlapping angles (script/schema memory psychology; event-segmentation prediction-error +
schema-clustering formalization; schema neuroscience commit-criteria + statistical event-structure
learning), each WebSearch/WebFetch-verified against primary sources, cross-checked against the
actual code of every named owned organ (`hdlab/grounding_acquisition_loop.py`,
`hdlab/predictive_coding.py`, `hdlab/situation_model_accumulate.py`,
`hdlab/consequence_learning_loop.py`, `hdlab/learner/{core,registry}.py`) rather than descriptions
of them, so every literature-to-organ mapping below is checked against the actual function
signatures and gate logic on disk.

## HEADLINE

**The wrong-grain diagnosis is literature-confirmed, and the fix is a known, buildable
recombination of organs we already own, not a new build.** Two independent literatures converge on
the same design principle from opposite directions: (a) Event Segmentation Theory's computational
model (Reynolds, Zacks & Braver 2007) shows human event-boundary detection fires on a *relative*
signal -- current prediction error versus the perceiver's own recent running-average error, not an
absolute magnitude -- and (b) the statistical-learning literature (Baldwin et al. 2008; Stahl et al.
2014) shows event-chunk discovery works the same way, via a local dip in transitional probability
relative to neighboring transitions. `hdlab/predictive_coding.py::threshold_gate` currently uses
an ABSOLUTE fixed threshold on `residual_magnitude`; `grounding_acquisition_loop.py`'s FLAG stage
doesn't call it at all -- it flags on an isolated-lemma polarity vote with no notion of a
recurring event-type. Fixing the grain means: score each narrative window's prediction error
against the SITUATION-MODEL REGISTER of each candidate recurring schema (an
`AccumulateRegister`-shaped role-bundle across MULTIPLE episodes, not a single verb string),
relative to that schema's own recent error history -- this is the missing "against what" the
current lemma-polarity signal never had. Separately, we already own a MORE PRINCIPLED
commit-vs-stay-episodic gate than the currently-wired `schema_consistency_split_half` heuristic:
`hdlab/learner/core.py::per_cluster_gate` + `mdl_select` implements exactly the
Perfors & Tenenbaum (2009) two-part-code MDL criterion -- promote a hypothesis only if it
compresses PAST THE NULL CODE, otherwise `KEEP_EPISODIC` (the literal string already in the code)
-- which is a formal, falsifiable version of what Ghosh & Gilboa (2014) and Preston & Eichenbaum
(2013) independently describe qualitatively as the brain's schema-commit criterion (built from
MULTIPLE episodes, abstracts away idiosyncratic detail, the extracted structure must
out-predict noise). This gate is currently wired to two OTHER hypothesis-class plugins
(`estimation_plugin`, `ruleind_plugin`) for unrelated cells, never to
`grounding_acquisition_loop`'s consolidation pass. Wiring `learner.per_cluster_gate` in as the
schema-commit decision (in place of, or alongside, the coarser split-half coherence proxy) is the
single highest-leverage, lowest-new-code fix this drill identifies.

## 1. The ACQUISITION signal -- what should flag a not-yet-understood gap

| Finding | Citation | Established? | Owned organ / concrete fix |
|---|---|---|---|
| Perceivers maintain an active "event model" that predicts near-future input; when predictions are violated, a transient prediction-error spike marks an event boundary and triggers replacement of the working model (fMRI: transient activity in posterior temporal/parietal + right dorsal frontal cortex, time-locked to observer-identified boundaries) | Zacks & Swallow 2007, *Curr Dir Psychol Sci* 16:80-84; Zacks, Speer, Swallow, Braver & Reynolds 2007, *Psychol Bull* 133(2):273-293 (Event Segmentation Theory, EST) | ESTABLISHED, foundational, field consensus | This IS the brain structure/process for "flag a gap": `predictive_coding.py::predict/residual/residual_magnitude` is already the right SHAPE (generative-model prediction vs observed, bipolar mismatch). The gap is that `grounding_acquisition_loop.py`'s FLAG stage never calls it -- it flags on `consequence_learning_loop.teacher_verdict`'s isolated lemma-polarity vote instead. |
| **The precise computational mechanism**: boundary fires when `SSE_t / running_avg(SSE)_{t-1} > threshold` (relative, self-referential prediction error against the model's OWN recent error history, 0.05-weighted low-pass running average); firing resets the maintained event representation. Validated: ROC AUC ~0.92-0.94 across threshold values 0.5-2.5 (robust to the exact cutoff); self-organizing (no hand-given boundaries) version still recovers ~83% of human-identified boundaries | Reynolds, Zacks & Braver 2007, *Cogn Sci* 31(4):613-643 | ESTABLISHED computational model, single-group but heavily cited/replicated logic | **Direct, concrete fix to `threshold_gate`**: replace (or add a variant of) the absolute `residual_magnitude >= threshold` test with a RELATIVE test -- `residual_magnitude(t) / running_avg(residual_magnitude)_{t-1} >= threshold` per schema-candidate. This is new code but a small, literature-pinned addition to `predictive_coding.py`, not a new organ. |
| Event boundaries are hierarchical/multi-timescale and predictive of what gets encoded into long-term memory -- boundary-adjacent content gets privileged encoding; better online segmenters have better later recall | Kurby & Zacks 2008, *Trends Cogn Sci* 12(2):72-79 | ESTABLISHED review synthesis | Licenses the design choice that FLAG (boundary-adjacent surprise) should gate LIBRARY entry -- matches the existing `Library.flag` intake shape, just needs the relative-signal trigger above instead of the lemma-polarity trigger. |
| During NARRATIVE (not just simple-motion) perception, an HMM fit directly to neural pattern time-series (no stimulus labels) discovers a cortical HIERARCHY of event representations -- short events in sensory cortex, long/abstract multimodal "situation model" events in angular gyrus/posterior medial cortex (default-mode-adjacent); high-level boundaries co-occur with hippocampal spikes predicting later recall | Baldassano, Chen, Zadbood, Pillow, Hasson & Norman 2017, *Neuron* 95(3):709-721 | ESTABLISHED single strong empirical result, methodologically influential | Confirms the right REPRESENTATION for the "against what" question is a SITUATION-MODEL-level register, not a token/lemma-level one -- directly licenses using `hdlab/situation_model_accumulate.py::AccumulateRegister` (already the owned FHRR role-bind-per-event accumulate-via-bundle register, per the USER's own brain-foundational reframe that this register already IS the situation-model) as the thing prediction error is computed AGAINST, not a bare lemma string. |
| Event-type assignment for a new scene is a soft posterior comparison across ALL existing schemas (a sticky Chinese Restaurant Process prior weighting reuse by persistence/frequency) versus a new-schema baseline; the likelihood term for each comparison IS (inverse) one-step prediction error from that schema's own recurrent predictor over the scene's holographic-reduced-representation vector -- **no hard threshold, a graded posterior-probability comparison**; each schema's predictor is updated online as more instances accrue, causing its dynamics to drift from idiosyncratic/episodic-like toward averaged/filler-invariant/semantic-like with repetition | Franklin, Norman, Ranganath, Zacks & Gershman 2020, *Psychol Rev* 127(3):327-361 (Structured Event Memory, SEM) | Single integrative computational model, NOT independently replicated at this scale -- the field's best available FORMALIZATION of schema-reuse-vs-new-schema decision-making, not a settled psychological fact | **The key structural gap this drill surfaces**: `grounding_acquisition_loop.py::Library.flag` keys ONLY by an exact-match lemma string -- there is no "does this trace fit an EXISTING schema candidate, or does it warrant a NEW one" branch at all. SEM's CRP formalizes exactly this missing decision. Concrete, novel-synthesis (not literature-precedented as a combination) fix: replace the exact-lemma key with a soft nearest-schema match (cosine of the incoming trace's `context_vector`/situation-model-register against each existing `LibraryItem`'s accumulated register bundle) with a "spawn new LibraryItem" fallback when no existing item clears a minimum similarity -- the CRP's stickiness/concentration-parameter shape, approximated the same way `decide_keep_or_revert`'s abstain-band already approximates a graded decision with a fixed margin. |
| Continuous action streams are segmented via LOCAL transitional-probability (TP) dips between consecutive primitive units -- within-chunk TP high, cross-boundary TP lower -- with NO external labels/feedback; frequency of exposure affects segmentation QUALITY (14 vs 7 repetitions of a triplet, in a 126-second stream) but no fixed exposure count is given | Baldwin, Andersson, Saffran & Meyer 2008, *Cognition* 106(3):1382-1407; extended to 7-9mo infants in Stahl, Romberg, Roseberry, Golinkoff & Hirsh-Pasek 2014, *Child Development* 85:1821-1826 | ESTABLISHED, robust, replicated program (adult + infant) | A SECOND, independent literature converging on "relative/local, not absolute/fixed" as the right signal SHAPE -- cross-validates the EST relative-threshold design above from a completely different empirical paradigm (statistical sequence learning vs. perceptual-prediction fMRI). This convergence is the strongest single piece of evidence in this drill that a relative (self-referential) surprise signal, not an absolute threshold, is the brain-faithful choice. |

**Concrete acquisition-rule statement**: the FLAG signal is *relative* predictive surprise --
`residual_magnitude(observed_window, predicted_by_best-fitting-schema-register) /
running_avg(that schema's own recent residual_magnitude)` exceeding a threshold -- computed
against a SITUATION-MODEL-grain register (`AccumulateRegister`-shaped, role-typed, built across
multiple episodes), not an isolated lemma. This directly explains the "wrong-grain" diagnosis:
`signal_a_only` has no notion of "against what schema" at all (there is exactly one register per
lemma, not per recurring event-type), and its threshold is implicit/absolute (a fixed MET/UNMET
classification per encounter) rather than self-relative.

## 2. The CONSOLIDATION + GENERALIZATION rule -- commit a schema vs stay episodic

| Finding | Citation | Established? | Owned organ / concrete fix |
|---|---|---|---|
| Operational schema criteria (4 NECESSARY): (1) associative-network structure (bound elements, not a flat list); (2) built from **MULTIPLE** episodes, never one; (3) elements are **non-specific** -- idiosyncratic per-instance detail abstracted away in favor of shared structure; (4) **adaptable** -- keeps updating via assimilation/accommodation, never frozen. Distinguishes schema from narrative (single-episode), category (feature-membership, no associative network), gist (detail-poor single-episode), and bare statistical regularity | Ghosh & Gilboa 2014, *Neuropsychologia* 53:104-114 | Single-paper conceptual synthesis, but the field's most-cited operational definition (explicitly adopted by Gilboa & Marlatte 2017) | **This is a literal, usable checklist for the BANK decision.** Criterion (2) matches the current `MIN_CONFIRM` trace-count gate. Criterion (3) is where the current design is WEAK: `consolidation_pass` commits a bare `GROUNDED_POS`/`GROUNDED_NEG` polarity label -- a single bit, not an abstracted STRUCTURE (the shared role/slot template across traces). Criterion (4) is a genuine, honest TENSION with the current design: `Library.flag` no-ops on any non-`PENDING` item, i.e. `GROUNDED_*` is currently TERMINAL/frozen -- literature-inconsistent with "a real schema stays adaptable." Flagged as a known, deliberate deviation below (safety-first: frozen = immune to post-hoc false-memory dilution), not silently glossed over. |
| mPFC computes a congruency/"resonance" signal between an activated schema template and incoming input. HIGH congruency -> fast vmPFC/neocortical assimilation, actively SUPPRESSING hippocampal binding (schema-congruent info can become hippocampus-independent within ~48h, vs weeks normally). LOW congruency -> hippocampus dominates, stores a separate pattern-separated trace. MID-RANGE congruency -> vmPFC and hippocampus INTERACTIVELY COUPLE (not compete) -- associative-inference paradigms show coactivation reflecting replay/integration that BUILDS the schema | van Kesteren et al. 2012 SLIMM (already cited in the sister acquisition-loop note); synthesized in Gilboa & Marlatte 2017, *Trends Cogn Sci* 21(8):618-631 | ESTABLISHED synthesis; SLIMM itself is one of two competing/unresolved circuit models the review presents, not settled | **THREE-BAND gate, not the current single-threshold gate.** `consolidation_pass` currently does one comparison: `schema_score >= schema_thresh` -> bank, else patience-increment. The literature specifies THREE regimes: high congruency -> fast-track bank (already the "bank" branch, roughly right); low congruency -> this should route to "probably not this schema, consider spawning/matching a DIFFERENT candidate" (the CRP branch from section 1, currently absent -- low score just increments patience toward the SAME item, never explores whether the trace actually belongs to a different recurring pattern); mid-range congruency -> the literature says COUPLE/keep integrating over MORE passes (roughly matches the existing patience-increment branch, but the current code treats "low" and "mid" identically). |
| Hippocampus and PFC are complementary: hippocampus rapidly forms pattern-separated, detailed traces of individual episodes; PFC-hippocampal connectivity increases specifically when retrieval requires exploiting OVERLAP/regularity across episodes (supporting generalization beyond any single stored episode) while hippocampus retains individuating detail | Preston & Eichenbaum 2013, *Curr Biol* 23(17):R764-R773 [secondary-sourced via Gilboa & Marlatte's direct summary + search abstracts -- primary full text was paywalled/unreachable this drill; flag as NOT independently primary-verified, treat with slightly more caution than the other entries] | Established review (secondary-sourced this drill) | Confirms the current design's SHAPE is right (`Library` keeps every `Trace` separately, never folds/averages at intake -- matches "hippocampus retains individuating detail" and the 07-28 audit's own core finding) -- the missing piece is the STRUCTURE-EXTRACTOR itself: "promote once extracted structure out-predicts noise across traces." This is precisely what an MDL two-part-code compression test measures, and we already own one (next row). |
| Model-selection principle: among candidate hypotheses for a set of episodes, promote (induce) the hypothesis that best COMPRESSES the episodes under a simplicity prior, but ONLY if it compresses PAST THE NULL/no-model code (`compression_ratio >= 1.0`); otherwise `KEEP_EPISODIC` (Perfors & Tenenbaum 2009 two-part-code MDL criterion, already cited in this project's own `hdlab/learner/core.py` docstring) | Perfors & Tenenbaum 2009 (cited in-code); Kemp & Tenenbaum 2008 "Discovery of Structural Form" (Bayesian structural-form selection, cited in the sister `research_script_half_synthesis_2026-08-09.md` as an angle never applied to scripts) | ESTABLISHED Bayesian model-selection framework in the cognitive-science literature; the SPECIFIC application to script/schema commit-vs-episodic is this project's own novel synthesis, not literature-precedented as a combination | **This is the headline finding of this section.** `hdlab/learner/core.py::per_cluster_gate` + `mdl_select` (imported by `hdlab/learner/registry.py`, already wired to `estimation_plugin`/`ruleind_plugin`/`gam_plugin`/`proginduction_plugin` for OTHER cells) is a WORKING, ALREADY-BUILT, formally-principled implementation of "extracted structure must out-predict noise across traces, else stay episodic" -- functionally identical in SHAPE to what Preston & Eichenbaum and Ghosh & Gilboa describe qualitatively, and it already returns the literal string `KEEP_EPISODIC` when the gate fails. It is currently NOT wired to `grounding_acquisition_loop.py` at all. The concrete fix: fit `ruleind_plugin` (MDL-gated sequential-covering conjunction rule induction -- the natural plugin for inducing a slot/role-typed script structure from accumulated `LibraryItem.traces`) over each schema candidate's traces at each `consolidation_pass`, and gate BANK on `per_cluster_gate` (compresses past null) IN ADDITION TO (not instead of) the existing `schema_consistency_split_half` coherence check -- the two are complementary (split-half tests topical/contextual coherence; MDL tests whether a genuinely COMPRESSIBLE structural regularity exists across traces), and requiring BOTH is strictly more conservative than either alone (relevant to the guard, section 3). |

**Concrete consolidation-rule statement**: an item commits from episodic (`PENDING`/per-trace) to
schema (`GROUNDED_*`) status only when (a) it has traces from `>= 2` independent episodes (Ghosh &
Gilboa criterion 2, already `MIN_CONFIRM`), (b) `hdlab.learner.core.per_cluster_gate` on a
`ruleind_plugin` fit over those traces returns `True` (an MDL-genuine compressible structural
regularity exists -- Ghosh & Gilboa criterion 3, "non-specific"/abstracted structure, operationalized
via Perfors & Tenenbaum two-part-code compression, not vote-count agreement), and (c) the
schema-consistency split-half score independently clears its margin (context-level congruency, the
SLIMM signal) -- i.e. AND, not OR, of the two independently-literature-grounded checks. Criterion
(4) "adaptable" is named as an open, deliberate, honest deviation (frozen-after-commit trades away
biological adaptability for false-memory safety) rather than silently ignored.

## 3. The GUARD's brain basis

The 2026-08-09 sister note (`research_psych_acquisition_consolidation_loop_2026-08-09.md`) already
grounded the escalate-don't-force-commit guard in Warren et al. 2014 (vmPFC lesion reduces false
recall, implicating the SAME schema-integration circuit in both true and false learning) and the
DRM/Bartlett false-memory literature. This drill's finding EXTENDS that with the specific circuit
mechanism (SLIMM, section 2 above): the vmPFC congruency/resonance signal is precisely the thing
that, if fooled (e.g. topically-coherent-but-structurally-wrong text -- coherent CONTEXT without a
genuine recurring STRUCTURE), would fast-track a wrong assimilation, because congruency-detection
and false-memory-generation are explicitly the SAME circuit, not two separate ones. This is why the
guard must be a CONJUNCTION of two independently-computed signals (split-half congruency AND MDL
compression, section 2) rather than either alone -- a single fooled signal cannot force a commit if
the other signal must independently agree, which is a stronger, literature-motivated version of
"escalate-don't-force-commit" than relying on one gate's patience counter. Preston & Eichenbaum's
complementary-systems framing (section 2) supplies the other half of the guard's brain basis: the
hippocampal pattern-separated trace store is never deleted or overwritten by a schema commit
(`Library` keeps every `Trace` intact regardless of `LibraryItem.status`) -- the fallback to
individuating detail always remains available, matching the biological claim that schema-mediated
gist and hippocampal episodic detail are STORED SEPARATELY, not one overwriting the other.

## 4. Cross-thread synthesis

Extends (does not duplicate) `notes/research_psych_acquisition_consolidation_loop_2026-08-09.md`
(word/lemma-grain acquisition+sleep-consolidation, already covering Dumay & Gaskell 2007
sleep-not-just-time, Tamminen et al. 2010 replay-budget, Tse et al. 2007/2011,
van Kesteren SLIMM at the citation level, McClelland 2013, Warren et al. 2014) by supplying the
SCRIPT/SCHEMA-grain literature that note explicitly did not cover: Schank & Abelson 1977 script
representation, Bower/Black/Turner 1979 (script-generalization existence-proof: false-recognition
of unstated script-typical actions rises monotonically 3.91->4.62->4.81 (7-pt scale) across
1/2/3 exposures, with 0%/50%/100% of false "recognitions" actually sourced from a DIFFERENT studied
story -- direct behavioral evidence of cross-episode merging, gradedly, not via a discrete
threshold), Graesser/Gordon/Sawyer 1979 + Graesser & Nakamura 1982 (script pointer+tag: mature
schemas store exceptions-only, atypical actions get privileged encoding -- matches the surprise-
ordering `surprise_order` function already in `grounding_acquisition_loop.py`), Event Segmentation
Theory's relative-prediction-error mechanism (genuinely new to this project's citation set), the
Baldassano et al. 2017 narrative-fMRI hierarchy result, the Franklin/Norman/Gershman 2020 SEM
CRP-schema-clustering formalization, Ghosh & Gilboa 2014's operational schema criteria, and the
Baldwin/Stahl statistical event-segmentation program. Also extends
`notes/research_script_half_synthesis_2026-08-09.md` (VerbNet end-state-matching for the
goal<->outcome relation, Schank/Abelson script lineage, Kemp & Tenenbaum "Discovery of Structural
Form" flagged there as an unfilled angle for scripts) by supplying the psych/neuro ACQUISITION
mechanism that note deliberately scoped out (it addressed script REPRESENTATION and matching, not
how a script is learned from repeated exposure) -- and by concretely proposing the MDL-gate wiring
that operationalizes exactly the "MDL/Bayesian structural-form selection for scripts" gap that note
named as UNFILLED in the classical literature (Kemp & Tenenbaum never applied to scripts; this
drill shows we already own an MDL selection engine, `hdlab/learner`, that can be pointed at exactly
this problem). Corrects nothing in the prior notes; the two acquisition-grain findings (word-level,
script-level) are complementary layers of the same growing-library architecture, not competing
designs -- a lexical item and a recurring event-type both flow through the same
FLAG->LIBRARY->CONSOLIDATE->GUARD->BANK shape, differing only in what the trace's context vector is
built from (a word-window vs. a role-bound situation-model register) and which learner plugin
scores the compression (none currently, vs. `ruleind_plugin`).

## 5. Cheap decisive test (pre-registered here; not yet built/dispatched)

Build a small synthetic multi-script corpus: >= 3 distinct recurring event-type "scripts" (e.g.
role-typed scene templates analogous to Schank & Abelson's restaurant script), each realized in
>= 4 narrative instances with DIFFERENT named fillers (testing structural, not lexical, reuse per
SEM's own validation logic), interleaved with >= 20% genuinely one-off, non-recurring filler events
(negative controls -- these must NEVER be promoted), plus a scrambled-sentence-order and a
wrong-schema-neighborhood adversarial probe set (reusing the same negative-control discipline
`grounding_acquisition_loop.py::self_test` already applies). Run K=5 `consolidation_pass`-style
sweeps measuring, per pass:

1. **Boundary/flag quality** -- precision/recall of the relative-threshold prediction-error signal
   (section 1) against the corpus's known scene boundaries, compared directly against the CURRENT
   `signal_a_only` flag on the identical corpus (same-corpus, same-pass paired comparison -- this
   is the direct test of the wrong-grain diagnosis).
2. **Schema commit correctness** -- of the 3 injected recurring scripts, how many reach
   `GROUNDED_*` by pass 5 under the new AND-gate (split-half congruency AND
   `learner.per_cluster_gate` compression), with correct generalization to >= 1 held-out
   novel-filler instance per promoted script (a decode/apply check against `ruleind_plugin`'s
   induced rule, not just a status flip).
3. **False-consolidation resistance** -- 0% of one-off events and 0% of adversarial wrong-context
   probes reach `GROUNDED_*` at any pass (the guard's one hard invariant, unchanged discipline from
   the sister note).

## 6. Falsifiable predictions

**HARD-PASS** (both required):
- Relative-threshold flag signal achieves boundary-detection F1 >= 0.75 against known injected
  scene boundaries AND is not worse than the current `signal_a_only` flag by more than 0.05 F1 on
  the identical corpus (confirms the wrong-grain diagnosis is real and the EST-style relative
  signal is the fix, not just a different-but-equally-weak signal).
- The MDL+congruency AND-gate promotes >= 2 of the 3 injected recurring scripts to `GROUNDED_*` by
  pass 5, each with correct novel-filler generalization on >= 1 held-out instance, AND 0 of the
  one-off/adversarial-probe items are ever promoted (zero tolerance, unchanged from the sister
  note's guard invariant).

**HARD-FAIL** (any one triggers, subject to the mandatory pre-check below):
- Relative-threshold F1 < 0.50 (worse than a majority-class/random boundary baseline) -- **mandatory
  pre-check first**: confirm `residual_magnitude` itself discriminates a synthetic coherent-repeat
  trace set from a scrambled/shuffled-order control (the same coherent-vs-scrambled sanity check
  `grounding_acquisition_loop.py::self_test` already runs for `schema_consistency_split_half`) --
  if that sanity check fails, this is a harness bug, not a negative on the relative-signal
  mechanism, per the standing "flat result = broken experiment" discipline.
- Any one-off or adversarial wrong-context item reaches `GROUNDED_*` (guard failure, the one
  invariant that is never excused by a pre-check).
- Zero of the 3 injected scripts reach `GROUNDED_*` by pass 5 despite each having >= 4 consistent,
  structurally-identical (modulo filler) instances -- pre-check: verify `learner.per_cluster_gate`
  fires `True` on a hand-constructed maximally-compressible synthetic trace set FIRST (same
  harness-bug discipline) before accepting this as a negative on the MDL-commit mechanism.

## 7. Substrate-product implications

If this clears its bands, the loop's growth axis expands from "does the substrate know this WORD's
outcome polarity" to "does the substrate recognize this recurring EVENT PATTERN and correctly
predict/fill its unstated typical continuation" -- the actual capability Schank & Abelson's original
script construct targeted, and the one the field's classical literature (per the sister
`research_script_half_synthesis` note) never solved for INCREMENTAL/online acquisition (all
classical script-induction work -- Chambers & Jurafsky, Regneri, Frermann, Chambers 2013, Pichotta
-- is one-shot batch over a fixed corpus). A working relative-surprise flag plus an MDL-gated commit
decision would give the substrate a fully-inspectable, glass-box account of WHICH narrative
patterns it has generalized, from HOW MANY instances, and WHY (the induced rule + the compression
margin over episodic, both JSON-serializable per `hdlab/learner/core.py`'s own
`glass_box_assert` invariant) -- directly the auditability differentiator this project's whole
program is built on, now extended from single-word outcome polarity to multi-step event structure,
which is the actual shape "comprehension improves with exposure and generalizes to held-out
narratives" needs to take to be a genuine claim rather than a lexicon-coverage number.

## 8. Anchor candidates for exp_dev (ranked; folded in per no-routing-files discipline)

1. **Cheapest, zero-new-mechanism-risk**: wire `hdlab.learner.registry.learn` (with
   `candidate_plugins=["ruleind"]`) into `grounding_acquisition_loop.consolidation_pass` as an
   ADDITIONAL AND-gate alongside the existing `schema_consistency_split_half` check, on the CURRENT
   lemma-keyed library (no new grain, no new corpus) -- this tests only whether the MDL gate helps
   or hurts on data we already have results for (`data/exp_unified_self_learning_loop_v6_replay_
   consolidation_smoke`), cheapest possible first slice of this drill's design.
2. **Second, the relative-signal fix**: add a relative-threshold variant to
   `hdlab/predictive_coding.py` (new function, e.g. `relative_threshold_gate`, literature-pinned to
   Reynolds/Zacks/Braver 2007 Eq. 8) and A/B it against the current absolute `threshold_gate` on
   whatever corpus anchor 1 used -- isolates whether the relative-vs-absolute distinction alone
   moves the needle before touching the schema-grain question.
3. **Third, the full script-grain build**: the synthetic multi-script corpus + `AccumulateRegister`-
   keyed library + CRP-style soft-match-or-spawn + the full section-5 cheap decisive test -- do this
   only after (1) and (2) each independently clear or produce a pre-check-passed negative, same
   confound-avoidance discipline the sister note already established (don't compound three unvalidated
   primitives at once).

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

The EST relative-prediction-error mechanism (section 1, Reynolds/Zacks/Braver 2007) is
well-established and independently cross-validated by the statistical-learning literature
(Baldwin/Stahl) -- HIGH confidence this piece transfers as designed. The SEM CRP-clustering
formalization (Franklin/Norman/Gershman 2020) is a single integrative model, not independently
replicated -- MEDIUM confidence in its exact mechanics, though it is the best available
formalization of the reuse-vs-spawn decision. The specific combination proposed here -- wiring
`hdlab.learner`'s MDL gate as a script-schema commit criterion, and requiring it in CONJUNCTION with
context congruency as a two-signal guard -- has NO literature precedent as a tested combination;
this is this project's own novel synthesis. Per the calibration discipline, P(this design, once
built per the anchors above, clears its section-6 HARD-PASS bands on the synthetic corpus) is capped
at 0.50 and further deflated to **~0.32**: positive factors are the double independent
cross-validation of the relative-signal principle and the fact that `learner.per_cluster_gate`
already EXISTS and is tested (not a new build, just a new wire-point) reducing implementation risk;
negative factors are the untested CRP-style soft-match/spawn logic (genuinely new code, no owned
precedent) and the fact that requiring TWO independent gates in conjunction (safer for the guard)
mechanically makes the HARD-PASS commit criterion harder to clear, i.e. the design trades commit-rate
for false-consolidation safety in a way that could show up as an honest "guard clears, growth is
too conservative" partial result rather than a clean pass or fail.

## Citations (verified count = 3 parallel Sonnet lit-scans, primary-source WebSearch/WebFetch-checked; 24 distinct NEW citations this drill)

**New this drill:** Schank & Abelson 1977 *Scripts, Plans, Goals, and Understanding* (Erlbaum);
Bower, Black & Turner 1979 *Cognitive Psychology* 11:177-220; Graesser, Gordon & Sawyer 1979
*J Verbal Learning & Verbal Behavior* 18:319-332; Graesser & Nakamura 1982, in Bower (ed.)
*Psychology of Learning and Motivation* 16:59-109; Radvansky & Zacks 2014 *Event Cognition* (OUP);
Radvansky 2011 *WIREs Cognitive Science*; Tompary, Zhou & Davachi 2020 *Scientific Reports*
10:17359; Zacks & Swallow 2007 *Curr Dir Psychol Sci* 16:80-84; Zacks/Speer/Swallow/Braver/Reynolds
2007 *Psychol Bull* 133(2):273-293; Reynolds/Zacks/Braver 2007 *Cognitive Science* 31(4):613-643;
Kurby & Zacks 2008 *Trends Cogn Sci* 12(2):72-79; Baldassano/Chen/Zadbood/Pillow/Hasson/Norman 2017
*Neuron* 95(3):709-721; Franklin/Norman/Ranganath/Zacks/Gershman 2020 *Psychol Rev* 127(3):327-361
(SEM; cites Fox et al. 2011 and Gershman et al. 2014 sticky-CRP machinery internally,
and Schapiro et al. 2013 as a prior model it unifies); Ghosh & Gilboa 2014 *Neuropsychologia*
53:104-114; Gilboa & Marlatte 2017 *Trends Cogn Sci* 21(8):618-631; Preston & Eichenbaum 2013
*Curr Biol* 23(17):R764-R773 [secondary-sourced, primary text unreachable this drill]; Baldwin/
Andersson/Saffran/Meyer 2008 *Cognition* 106(3):1382-1407; Stahl/Romberg/Roseberry/Golinkoff/
Hirsh-Pasek 2014 *Child Development* 85:1821-1826; Perfors & Tenenbaum 2009 (two-part-code MDL,
cited in-repo in `hdlab/learner/core.py`, primary paper not re-verified this drill -- carried from
existing code citation); Kemp & Tenenbaum 2008 "Discovery of Structural Form" (flagged as unfilled
for scripts in the sister note, not independently re-verified this drill).

**Carried forward** (verified in the same-day sister drills, not re-verified this session):
Dumay & Gaskell 2007 *Psych Sci* 18(1); Tamminen et al. 2010 *J Neurosci* 30(43); Tse et al. 2007
*Science* 316; Tse et al. 2011 *Science* 333; van Kesteren et al. 2012 *Trends in Neurosciences*
35(4); McClelland 2013 *JEP:General* 142(4); Warren/Jones/Duff/Tranel 2014 *J Neurosci* 34(22);
Kumaran/Hassabis/McClelland 2016 *TiCS* 20(7); Bartlett 1932 *Remembering*; Roediger & McDermott
1995 *JEP:LMC* 21(4).
