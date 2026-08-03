# Brain-fidelity audit: event-level prediction-error relation-inference architecture (2026-08-03)

Filed by: research sub-agent (Sonnet), dispatched by Director in PARALLEL to the running
Phase-1 cell VET, per the FORMALIZE discipline (map brain anatomy+order+metric -> compare
our architecture component-by-component on SHAPE+POSITION+METRIC -> name every deviation ->
hand back brain-accurate corrections judged on the brain's own metric). This audit does NOT
touch the running Phase-1 cell, does not author/dispatch experiments, and is explicitly a
parallel fidelity check, not a verdict re-litigation.

## 0. KB-check (mandatory, run before writing)

`substrate_query.sh --chunk-content --schema-version v2 --tau 0.15 --k 5` run against:
"event segmentation prediction error", "posterior medial network event models", "mentalizing
goal inference theory of mind", "predictive coding hierarchy", "hippocampal relational
binding", "mentalizing theory of mind unstated goal inference mPFC TPJ". Results (cosine,
top hits): "segmentation"/"CN_segmentation"/"mentation"/"sedimentation" (~0.43-0.48, WordNet/GO
lexical near-misses, not conceptual overlap); "state of mind" (0.2695, WordNet lexical
near-miss, not conceptual); **`theory_of_mind_sally_anne_nested_hrr_v1` (cosine=0.2627,
VERDICT_OF->HARD_PASS)** — this IS genuine prior-art overlap and is treated as such below (see
Deviation 4). All cosines are below the 0.30 KB-treat-as-duplicate threshold this project uses,
so no full-drill duplication is being re-litigated here; the one above-noise hit
(theory_of_mind_sally_anne_nested_hrr_v1) is real prior art this audit surfaces as UNDERUSED,
not un-discovered. Two "posterior medial network" / "predictive coding hierarchy" /
"hippocampal relational binding" queries hung past budget on the known KB memory-thrash issue
(logged 2026-08-01, `data/orchestrator_status_log.jsonl`) and returned no output; this audit
does not block on them — the encoder-target drill dated 2026-08-03
(`notes/research_drill_biology_led_encoder_target_representation_2026-08-03.md`) already ran
and verified the Zacks/Trabasso/Zwaan/Mar citation set this audit builds on, cited as prior art
throughout rather than re-derived.

**Already known (do not re-derive):** Zacks Event Segmentation Theory (Zacks & Swallow 2007;
Zacks et al. 2007 Psych Bull; Reynolds, Zacks & Braver 2007 computational model); Trabasso &
van den Broek 1985 causal-network story grammar; Zwaan & Radvansky 1998 situation-model
event-indexing (space/time/causation/intentionality/protagonist); Mar 2011 mentalizing
meta-analysis (mPFC/TPJ/precuneus/temporal poles); Speer, Zacks & Reynolds 2007 (event
boundaries time-locked to SITUATIONAL not lexical changes) — all verified in the prior drill
and cited there with full DOI/venue detail, not repeated here.

**New in this audit:** the direct component-by-component SHAPE/POSITION/METRIC comparison
against the actual Phase-1 code (`experiments/exp_event_level_prediction_error_relation_
inference_phase1_v1.py`), disk-verified line-by-line below, plus the surfaced-but-unused
`theory_of_mind_sally_anne_nested_hrr_v1` HARD_PASS organ as a directly-relevant existing
capability for the unstated-goal axis specifically.

---

## 1. The brain's actual event-cognition -> relation-inference pipeline (anatomy, order, metric)

Ordered as the brain actually computes it, each stage's error/objective metric named:

1. **Perceptual/lexical intake -> continuous prediction, every moment** (not just at
   sentence boundaries). Hierarchical predictive coding: each cortical level predicts the
   level below; METRIC = local sensory/lexical prediction error, propagated up only when it
   exceeds expectation (Friston free-energy; concretely indexed by the N400 at the
   lexical-semantic level per Michaelov et al. 2025).
2. **Event-model maintenance + boundary detection** (posterior medial cortex: precuneus,
   posterior cingulate, retrosplenial + superior/anterior temporal + right middle frontal
   gyrus; Speer/Zacks/Reynolds 2007). The brain holds a running event MODEL that predicts what
   happens next; POSITION = continuous, running alongside comprehension, not a separate
   pre-processing pass. METRIC = transient spike in sequential/situational prediction error
   (Reynolds-Zacks-Braver 2007's RNN formalizes this: boundaries = local maxima in
   next-perceptual-feature prediction error, not a fixed cadence or fixed unit like "one
   sentence = one event"). Critically, boundary triggers are SITUATIONAL (goal shift, causal
   shift, spatial/temporal shift) not lexical/syntactic (Speer et al. 2007's key finding).
3. **Structured event/proposition representation** (goal-action-outcome nodes; Trabasso &
   van den Broek 1985). SHAPE = a GRAPH of causally-linked propositions accumulating over the
   WHOLE narrative read so far, not a fixed 1-2-item sliding window. POSITION = built
   incrementally as segmentation produces each new event, feeding into working memory /
   situation-model structures (hippocampal relational binding supports this: rapid,
   arbitrary binding of arbitrary role-fillers into a structure that supports FLEXIBLE,
   non-adjacent-only retrieval — not restricted to bind only the immediately-prior 1-2 items).
4. **Causal-integration computation** (still Trabasso & van den Broek): CAUSAL CONNECTIVITY —
   whether event B is reachable from event A via a chain of antecedent-consequent links,
   possibly MULTI-STEP and non-adjacent — predicts recall/importance/summarization inclusion
   OVER AND ABOVE serial position. METRIC here is graph-connectivity / chain-reachability, not
   a single-hop similarity score, and definitively NOT computed only from immediately-adjacent
   events (the entire empirical signature of Trabasso's finding is that causal relatedness
   beats serial adjacency as a predictor).
5. **Mentalizing for UNSTATED goals** (mPFC/dmPFC, bilateral TPJ, precuneus/PCC, temporal
   poles; Mar 2011 ALE meta-analysis; substantially overlaps DMN). POSITION = a
   PARTIALLY-DISTINCT computation layered on top of the causal/situation-model structure, not
   the same single mechanism that does causal-chain integration (the Ferstl/von Cramon
   coherence-vs-mentalizing dissociation is contested but the two are at minimum
   dissociable in some studies). METRIC here is inference to the BEST-EXPLAINING latent
   mental state (goal/intention) given observed action, not similarity-to-a-fixed-category-
   prototype — a genuine ABDUCTIVE/inferential computation, and the false-belief literature
   (Sally-Anne; this project's own `theory_of_mind_sally_anne_nested_hrr_v1` HARD_PASS cell)
   shows this requires tracking WHOSE epistemic state is being represented (observer-only
   access vs world-state), i.e. a PARTITIONED, agent-indexed representation, not one pooled
   event-state.
6. **Verification/read-out is graph-integration, not one-shot rollout.** Multi-index
   situation-model tracking (Zwaan & Radvansky's five indices: space, time, causation,
   intentionality/goal, protagonist) means a SATISFY/THWART/CAUSE judgment about two narrative
   events draws on the ACCUMULATED situation model up to and including both events, checked
   for consistency across all five indices simultaneously — not a single one-step forward
   prediction from event A alone.

**Order, restated tersely:** continuous local prediction error (word-grain) -> event-model
prediction error spikes = segmentation (situational grain, variable-length) -> incremental
graph-structured event/causal representation (accumulates over the WHOLE narrative,
non-adjacent links included) -> mentalizing-specific abductive inference over that graph for
UNSTATED content -> multi-index consistency check as the relation-inference readout.

---

## 2. Component-by-component comparison (brain SHAPE/POSITION/METRIC vs ours vs GAP)

| # | Component | Brain: SHAPE | Brain: POSITION | Brain: METRIC | Ours | GAP |
|---|---|---|---|---|---|---|
| 1 | Event segmentation | Variable-length events, boundaries = local MAXIMA of situational (not lexical) prediction error; a genuinely PREDICTIVE, online process | Continuous, concurrent with comprehension | Transient spike in the SAME predictive-coding error signal used everywhere else in the pipeline | Naive regex sentence-split (`segment_events`, line 336-344); 1 sentence = 1 event, fixed-grain, NOT predictive, NOT boundary-detected — computed with zero reference to any error signal | **SHAPE + METRIC gap, largest structural one.** Brain's segmentation IS an instance of the SAME predictive mechanism Stage B trains — ours puts a syntactic heuristic in that slot and reserves prediction-error only for the DOWNSTREAM predictor. This is explicitly declared "rough, not the variable" in the source (line 69-82), so the deviation is KNOWN and flagged by the cell's own author, but it means Stage A cannot itself produce a boundary-quality signal, and coarse/wrong-grain events propagate error into every downstream stage. |
| 2 | Event representation | Goal-action-outcome PROPOSITION nodes in a growing GRAPH; hippocampal binding supports arbitrary, flexible (non-adjacent) role-filler binding across the WHOLE narrative so far | Built incrementally, retained cumulatively (situation model), not discarded after a fixed window | N/A (representational, not itself an error metric) | Bound AGENT/ACTION/OBJECT FHRR composite per sentence (`build_event_struct_v6`, reused verbatim) — **no GOAL slot, no OUTCOME slot**, and no graph/persistent-store: each event-struct exists only transiently inside a 2-event bundled window (`EVENT_CONTEXT_WINDOW = 2`, line 281) | **SHAPE gap.** Missing GOAL and OUTCOME roles specifically undercuts the axes this cell is trying to measure (unstated_goal, satisfy/restate, thwart/cause ARE goal-and-outcome relations) — the representation being bound doesn't have a place to put the very thing being inferred. Missing persistent graph store means causal/goal relations spanning more than 2 events are structurally unrepresentable, independent of whether the predictor "learns" anything. |
| 3 | Predictive mechanism | Hierarchical, multi-timescale; RNN-style temporal integration in Reynolds-Zacks-Braver's own computational model (not a fixed 2-step window); error signal is SITUATIONAL-feature prediction error, propagated at MULTIPLE grains simultaneously (word-level N400 grain AND event-level grain are BOTH active, not either/or) | Runs continuously as text is read; boundary-relevant signal is inherently non-adjacent-capable via the running event model, not window-capped | MSE-equivalent sequential prediction error (matches ours in FAMILY) but computed over a representation the model ITSELF updates/retains (a recurrent state), not a hand-fixed lookback window | Linear delta-rule (Widrow-Hoff), `EventPredictor.train_step`, 2-event BUNDLED (not concatenated/ordered) context predicting 1-event target via full-batch GD MSE minimization | **POSITION + SHAPE gap.** (a) Fixed EVENT_CONTEXT_WINDOW=2 is a hard architectural ceiling far short of Trabasso's non-adjacent, whole-graph causal reachability — a linear map over a 2-event bundle CANNOT represent a causal link between event 1 and event 20. (b) Bundling (superposition) the 2 context events LOSES their relative ORDER (FHRR bundle of A and B is symmetric in A,B up to the bind-order already baked into build_event_struct_v6, but the CONTEXT window itself has no positional encoding distinguishing "A then B" from "B then A") — the brain's event model is inherently ORDERED/sequential (an RNN carries a directional temporal state), ours is a symmetric superposition, discarding order information at exactly the joint the mechanism most needs it (event sequence IS the causal-direction signal). (c) Linear-only: the brain's hierarchy is explicitly MULTI-LEVEL predictive coding (word-grain error feeds event-grain error feeds higher levels); ours has a single linear layer with no hierarchy. METRIC itself (squared error) is brain-consistent in FAMILY — this is the one sub-component closest to faithful. |
| 4 | Relation-inference readout | (a) Causal/goal relations = MULTI-STEP graph-reachability check over the WHOLE situation model, not a 1-hop rollout. (b) Unstated-GOAL inference specifically is MENTALIZING — an agent-indexed, abductive best-explanation computation (Mar 2011; and this project's OWN validated `theory_of_mind_sally_anne_nested_hrr_v1` HARD_PASS cell, which implements exactly this via per-agent multi-bank partitioning + refuse-gate) | Layered on top of (not identical to) the causal-graph mechanism; partitioned by WHOSE mental state is being represented | Best-explanation / abductive inference metric (which latent goal explains the observed action best, given agent-specific epistemic access) — categorically different from a similarity/overlap metric | ONE-STEP forward roll (`predict_next_struct`, single hop) then `structure_overlap` — a COSINE-SIMILARITY-style overlap between a predicted vector and a fixed set of hand-authored category-PROTOTYPE vectors (`CATEGORY_PROTOTYPES`), with no agent-partitioning, no multi-step graph traversal, no abductive/best-explanation computation | **METRIC gap, the deepest one — this is the "similarity-proxy where the brain reasons" case named by the brain-fidelity discipline.** Brain-side unstated-goal inference is an INFERENCE over agent-specific mental content (this project already proved that mechanism works, HARD_PASS, in `theory_of_mind_sally_anne_nested_hrr_v1`); ours substitutes nearest-prototype-by-cosine-overlap through a single predicted vector. Even a perfectly-trained predictor can only ever move the readout's answer toward "which fixed prototype text is the predicted vector closest to" — structurally incapable of the kind of inference the Sally-Anne cell already demonstrates this substrate CAN do. Likewise thwart_cause is checked via a single 1-hop overlap-to-B-vs-distractor test, not graph reachability — explicitly excluded from the greenlight axis in the pre-reg (line 131-137) precisely because it's recognized as lexically shortcuttable, which is itself evidence the readout metric is doing pattern-match, not causal reasoning. |
| 5 | Learning objective | Prediction-error minimization operates at MULTIPLE levels concurrently (lexical/N400-grain AND event/situational-grain); the mentalizing layer is NOT trained by the same error signal — ToM inference is a separate, likely inferential/reasoning-based computation, not itself learned by minimizing next-event MSE | Multi-level, hierarchical, concurrent | Sequential prediction error (event-grain: matches); mentalizing/goal-inference metric is a DIFFERENT kind of objective (best-explanation, not reconstruction error) | Single-level MSE on FHRR structure is the ONLY learning signal in the whole cell; the goal/relation readout is entirely DERIVED from this one predictor with no separate goal-inference training or mechanism at all | **Conflation gap.** The architecture treats "learn to predict the next event's surface form" and "infer the unstated goal/causal relation" as the SAME learned quantity read out two different ways. The brain's own evidence (mentalizing as a partially-distinct network, Mar 2011; Ferstl/von Cramon dissociation) says these are NOT the same computation. A predictor that gets very good at surface-form MSE has NO guaranteed relationship to correct goal/causal inference — which is very likely why Stage C failed to clear the word-level baseline (see readout in section 3) even where Stage B showed learning. |

---

## 3. Named deviations, ranked by threat to brain-fidelity (and how much each likely explains the Phase-1 shortfall)

**Deviation 1 (highest-priority, deepest): readout is a similarity-proxy, not a reasoning
computation — THIS IS THE ARCHITECTURE-FIX CASE the discipline calls for.** `structure_overlap`
against fixed hand-authored prototypes, through a ONE-STEP linear roll, cannot in principle
implement mentalizing-style abductive inference (Mar 2011) or Trabasso's multi-step causal
reachability. Crucially, this project has ALREADY BUILT AND VALIDATED (HARD_PASS,
`theory_of_mind_sally_anne_nested_hrr_v1`) a mechanism-class that is brain-shaped for exactly
the unstated-goal axis — per-agent multi-bank partitioning + refuse-gate — and Phase-1 does not
use it at all. This is not merely "a gap," it is an available, disk-verified capability sitting
unused while a weaker proxy mechanism is used in its place. Most likely single explanation for
why Stage C readout underperforms even where Stage B (MSE) shows genuine learning: the
predictor can get better at reconstructing surface event-state without that improvement being
routed through anything resembling the brain's actual goal-inference computation.

**Deviation 2 (high): fixed 2-event window with no persistent graph, discarding
non-adjacent causal structure.** Trabasso's central, most-replicated finding is that causal
CONNECTIVITY (potentially multi-hop, non-adjacent) beats serial position as a predictor of
narrative importance/recall. `EVENT_CONTEXT_WINDOW=2` structurally forecloses any relation
spanning more than 2 sentences — for a novel-length corpus this eliminates almost all
of the causal graph the brain would actually use. This directly caps thwart_cause and any
goal-satisfaction relation that unfolds over more than an adjacent sentence pair (which,
empirically, most SATISFY/THWART pairs in real narrative prose do).

**Deviation 3 (high): segmentation grain is syntactic, not error-driven/situational.**
Sentence-as-event throws away the brain's own definition of an event boundary (a spike in
prediction error at a SITUATIONAL change) and replaces it with a fixed, content-blind
heuristic. This is explicitly self-flagged in the source as "rough... Phase 2 hardens this,"
so it is a KNOWN, not hidden, deviation — but its downstream cost is real: many sentences
contain zero or multiple genuine "events" (a compound sentence with two clauses = one event
here; a one-word sentence "Wait." = a whole event here), degrading the input to every later
stage regardless of how well the predictor trains.

**Deviation 4 (medium-high, an opportunity not just a gap): missing GOAL/OUTCOME role
slots in the bound event representation.** `build_event_struct_v6` binds AGENT/ACTION/OBJECT
only. The axes this cell measures (unstated_goal, satisfy_restate, thwart_cause) are
definitionally about GOAL and OUTCOME relations, yet the representation being predicted over
has no slot to place either. The predictor is being asked to infer goal/outcome content it was
never given a structural place to represent — analogous to asking a system to report a variable
it never declared.

**Deviation 5 (medium): context window discards temporal order via symmetric bundling.**
`make_context_struct` bundles (superposes) the window's events rather than encoding their
sequence order distinctly. The brain's event-model mechanism is inherently DIRECTIONAL
(an online, forward-running process) — order IS the causal-direction signal (A causing B is a
different fact from B causing A), and superposition is, by construction, insensitive to swap
order beyond whatever asymmetry the individual event-structs already carry internally. This
compounds Deviation 2 rather than being independent of it.

**Deviation 6 (medium): single-level, linear predictor vs. hierarchical, multi-timescale
predictive coding.** The brain's own computational model of this exact mechanism
(Reynolds-Zacks-Braver 2007) is an RNN over perceptual features with graded/hierarchical
error propagation, not a single linear map trained by one batch-GD objective. This is a
real SHAPE gap but lower-priority than 1-4 because METRIC-family (squared prediction error) is
preserved and a linear map is a defensible FIRST STAGE of a later, richer hierarchy — the
Phase-1 cell's own framing ("simplest honest version," "Phase 2 hardens") already treats this
as intentionally-deferred scaffolding rather than a claimed-final architecture.

**Deviation 7 (lower, structural conflation not yet causing visible harm but risky
going forward): one learning objective (event-state MSE) is asked to double as the goal/causal
inference signal.** Per Mar 2011 and the Ferstl/von Cramon dissociation (itself flagged
contested in the prior drill), mentalizing is evidence-consistent with being a PARTIALLY
SEPARATE computation from causal/situational coherence-tracking, not simply "good next-event
prediction, read out differently." Ranked below 1-4 because it is more a forward-looking risk
(scaling the predictor further will not by itself fix Deviation 1) than a demonstrated cause of
the current shortfall, but it is the reason Deviation 1's fix needs a GENUINELY SEPARATE
readout mechanism, not just a better-trained shared predictor.

---

## 4. Prioritized brain-accurate corrections for Phase 2 (each: brain does X, we deviate by Y, fix is Z, judge on the brain's metric)

**Correction 1 (addresses Deviation 1, highest priority): route unstated-goal inference
through the ALREADY-VALIDATED per-agent/multi-bank + refuse-gate ToM mechanism
(`theory_of_mind_sally_anne_nested_hrr_v1`, capability-registry-eligible HARD_PASS organ),
not through one-step-predict + prototype-overlap.**
- Brain does: mentalizing = agent-indexed, abductive best-explanation inference (Mar 2011);
  this project already proved a brain-shaped mechanism-class for exactly this (Sally-Anne
  false-belief, per-agent bank partitioning, refuse-gate for unknowable content) at HARD_PASS.
- Our deviation: cosine-similarity readout against fixed category prototypes via one linear
  hop — a pattern-match proxy standing in for an inference the substrate has already
  demonstrated it CAN do properly elsewhere.
- Fix: adapt the multi-bank/refuse-gate organ so "agent" partitions index whose GOAL is being
  tracked (the narrative's protagonist per scene, not literal dialogue-participant Sally/Anne),
  writing goal-state into that agent's bank as events accumulate, and reading it back via the
  SAME refuse-gate-guarded decode used in the Sally-Anne cell (so "we don't know" is an honest
  answer, not a forced nearest-prototype guess).
- Judge on the brain's metric: abductive best-explanation accuracy on a HELD-OUT set with an
  explicit REFUSE option scored separately from wrong-guess (mirrors the Sally-Anne cell's own
  Q4 refuse-control axis), not raw overlap-to-prototype accuracy alone.

**Correction 2 (addresses Deviation 2 + 5, high priority): replace the fixed 2-event bundled
window with a persistent, GRAPH-structured event/causal store (reuse `CausalLinkRegister`,
already built and disk-verified 0.9722 vs 0.0 cross-chapter baseline in `hdlab/
situation_model_accumulate.py`), so causal/goal relations spanning MORE than 2 adjacent
sentences are representable and directionally ordered.**
- Brain does: Trabasso causal-network integration is graph-reachability over the WHOLE
  narrative read so far, non-adjacent links included, and is inherently directional
  (CAUSE -> EFFECT, not symmetric).
- Our deviation: `EVENT_CONTEXT_WINDOW=2`, symmetric bundle, discarding both range and
  direction.
- Fix: for each newly-segmented event, write CAUSE/EFFECT links into the already-built,
  already-validated `CausalLinkRegister` (directional bind, per-event-slot accumulate) rather
  than only ever predicting from the immediately-preceding 1-2 events; SATISFY/THWART/CAUSE
  readout queries `query_effect_of`/`query_cause_of` (multi-hop traversal via repeated query)
  instead of a single forward roll.
- Judge on the brain's metric: does causal-CONNECTIVITY (chain-reachability, possibly
  multi-hop) predict the gold SATISFY/THWART/CAUSE labels better than adjacency/serial-position
  alone — the exact discriminating test Trabasso & van den Broek (1985) used empirically
  (causal-chain membership beating serial position as a predictor).

**Correction 3 (addresses Deviation 3, medium-high priority): make segmentation itself
error-driven (a genuine instance of Reynolds-Zacks-Braver's boundary = local-maximum-of-
prediction-error rule), not syntactic.**
- Brain does: event boundaries ARE prediction-error spikes in the SAME predictive mechanism
  used downstream, at SITUATIONAL grain.
- Our deviation: fixed regex sentence-split, computed with zero reference to any error
  signal, self-declared as a placeholder.
- Fix: run the (now-corrected, per Correction 2) predictor CONTINUOUSLY over a token/clause
  stream and place event boundaries at local maxima of its own next-state prediction error,
  closing the loop the brain actually uses (segmentation and the predictive mechanism become
  the SAME error signal, not two unrelated stages) — this is explicitly what the source
  document already earmarks as the Phase-2 target ("Phase 2 hardens segmentation... clause-
  level events"), so this correction is confirmatory of the plan already declared, not new
  scope.
- Judge on the brain's metric: do learned boundaries correlate with independently-judged
  situational changes (goal shift / causal shift / spatial-temporal shift) better than sentence
  boundaries do — the same criterion Speer et al. (2007) used to validate the theory against
  human boundary judgments and neural event-boundary signals.

**Correction 4 (addresses Deviation 4, medium priority): add explicit GOAL and OUTCOME role
slots to the bound event representation, not just AGENT/ACTION/OBJECT.**
- Brain does: goal-action-outcome proposition nodes (Trabasso); Zwaan's intentionality index
  is a first-class tracked dimension, not inferred solely from action content.
- Our deviation: `build_event_struct_v6` has no GOAL/OUTCOME role.
- Fix: extend the role vocabulary (reusing the SAME role-vec binding primitive, no new
  binding mechanism) so an event-struct can bind a GOAL filler and an OUTCOME filler when the
  text supplies one (even sparsely populated at first), giving the predictor and the readout an
  actual structural slot to place the content being inferred rather than asking it to recover
  goal information from an AGENT/ACTION/OBJECT-only composite.
- Judge on the brain's metric: does readout accuracy on the goal/outcome axes improve when the
  representation HAS the relevant slot vs. when it doesn't (a direct ablation, the fairest test
  of whether "no slot for the thing being asked about" was actually load-bearing).

**Correction 5 (addresses Deviation 6/7, lower priority, defer past the above): only after
1-4 land, consider hierarchical/multi-timescale prediction (word-grain error feeding
event-grain error) instead of a single linear layer, and treat the mentalizing/goal-inference
readout as its own partially-separate learned or hand-designed mechanism rather than a
byproduct of surface-state MSE minimization.** Lower priority because Corrections 1-4 already
give the readout an appropriately brain-shaped mechanism and structure to draw on; layering in
hierarchy without those fixes first would still be feeding a good hierarchy into a proxy
readout (Deviation 1) via too-narrow a window (Deviation 2).

---

## Flagged "similarity-proxy where the brain reasons" case (per the always-on brain-fidelity-
element-audit discipline)

Section 2 row 4 / Deviation 1 IS this case, named explicitly per the discipline
(`feedback_on_every_negative_audit_each_element_brain_fidelity_2026-07-25`): `structure_overlap`
cosine-style matching against a small fixed prototype set, reached through a single linear
predictive hop, stands in for what the brain does via a dissociable, agent-indexed, abductive
mentalizing computation. This audit's central claim is that this substitution — not predictor
undertraining, not corpus size, not word-filler quality (already separately audited and
partially fixed in the encoder-target drill) — is the most likely root cause of any Stage C
shortfall that occurs even where Stage B (MSE) shows the predictor genuinely learned something.
Per discipline, this is an ARCHITECTURE fix (Correction 1), not a data/tuning fix.

---

## Citations

All citations in Section 1 (Zacks & Swallow 2007; Zacks, Speer, Swallow, Braver, Reynolds
2007; Reynolds, Zacks & Braver 2007; Speer, Zacks & Reynolds 2007; Trabasso & van den Broek
1985; Zwaan & Radvansky 1998; Zwaan, Langston & Graesser 1995; Mar 2011; Saxe & Kanwisher
2003) are carried forward, DOI/venue-verified, from
`notes/research_drill_biology_led_encoder_target_representation_2026-08-03.md` (Section 2 of
that drill) — not re-verified independently in this session; that drill's own citation-count
footer records their verification provenance. This audit's own contribution is the
component-by-component architectural mapping (Section 2), the ranked deviation list (Section
3), and the disk-verified pointer to `theory_of_mind_sally_anne_nested_hrr_v1` as an existing,
underused HARD_PASS capability (surfaced via the KB-check in Section 0, confirmed by direct
file read of `experiments/exp_theory_of_mind_sally_anne_nested_hrr_v1.py` lines 1-49).

## HEADLINE

The brain's relation-inference pipeline is: continuous word-grain prediction error -> event
boundaries at situational (not lexical) prediction-error spikes -> an incrementally-growing,
DIRECTIONAL causal/goal graph over the WHOLE narrative (non-adjacent links included) ->
a partially-separate, agent-indexed MENTALIZING computation for unstated goals -> multi-index
consistency checking as the actual relation-inference readout. Our Phase-1 cell gets the
predictive-error MECHANISM FAMILY right (delta-rule/MSE, matches Q1's discriminative-learning
evidence) but deviates on SHAPE (fixed 2-event symmetric-bundle window vs. whole-narrative
directional graph; no GOAL/OUTCOME role slots; syntactic not error-driven segmentation) and
most importantly on METRIC at the READOUT (one-hop cosine-overlap-to-fixed-prototype standing
in for mentalizing's abductive best-explanation inference — the discipline's "similarity-proxy
where the brain reasons" case). The single highest-leverage, already-available fix is
Correction 1: route unstated-goal inference through this project's OWN already-validated
(HARD_PASS) per-agent/multi-bank + refuse-gate ToM mechanism
(`theory_of_mind_sally_anne_nested_hrr_v1`) instead of prototype-overlap, paired with
Correction 2 (persistent directional causal graph via the already-built `CausalLinkRegister`)
to give causal/thwart/satisfy relations the non-adjacent reach Trabasso's evidence says they
need. Both reuse EXISTING, disk-verified substrate capabilities rather than requiring new
mechanism-building — this audit's main actionable finding is under-reuse of prior art, not a
missing capability.
