# Research: Prediction-Error as a Native Learning Signal for the HD/VSA Encoder, and Whether Predicting the Input Stream Doubles as an Exogenous Grounding Anchor

Filed-by: research sub-agent (Sonnet lit-scan x3, parallel breadth dispatch; synthesized by research)
Date: 2026-07-09
Drill class: ORTHOGONAL deep-research probe (brain-first, cross-domain; queued alongside the decisive
self-grounding FULL run; explicitly the one thread in the 07-09 program not yet drilled). Builds directly
on L4 ("Prediction as core computation," flagged speculative) of
`research_neural_substrates_language_brain_architecture_5x_drill_2026-07-09.md`, and sharpens the
grounding question opened by `research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md`,
`research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md` (content-vs-structural grounding),
`research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md` and
`research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md` (the confirmed self-play
shared-blind-spot negative and its differentiation-axis taxonomy).

3 parallel Sonnet lit-scan sub-agents dispatched on: (1) predictive coding as a LEARNING RULE vs backprop
and contrastive/InfoNCE objectives; (2) prediction-of-input-stream as a representation-learning/grounding
mechanism in ML (JEPA, world models, CPC, next-token-prediction-as-grounding debate); (3) biology of
reward-prediction-error vs sensory/cerebellar prediction-error, and developmental evidence that prediction
error drives representation formation. Generic math/neuroscience terms only, no substrate-novel mechanism
names exposed off-platform per `[[feedback-query-privacy-decomposition]]`.

**Disk-verify note (per Fix#28) -- UPDATED with actual verified `metrics.json` data, not a placeholder:**
the substrate already HAS `hdlab/predictive_coding.py` (Rao-Ballard predict + residual-magnitude +
threshold/proportional write-gates) and an already-built, already-RUN cell family
(`exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1/v2`,
`_v3_D_competitive_hebbian_only`, `_stress_test_cell1`, all dated 2026-07-02) per the design note
`notes/design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md`. I read
the landed `metrics.json` verdicts directly off disk (not hallucinated, not inferred from routing rules):

| Cell / run | Verdict | Key numbers (from `verdict_msg`) |
|---|---|---|
| `..._v1_smoke` | **HARD_FAIL** | `hybrid_gap_lift=-0.104 < HF_min=-0.05` (v1's specific hybrid combination underperformed) |
| `..._v2_smoke` | **HARD_PASS** | `HYBRID gap=0.517 (PRED gap=0.566, diff=0.049<=0.15); NAIVE_WTA gap=0.000; RANDOM=-0.006` |
| `..._v3_D_competitive_hebbian_only` (FULL) | **HARD_PASS** | `ck=0.492 ca=0.020 gap=0.472; NAIVE_WTA gap=0.000; LI(report-only) gap=0.354` |
| `..._stress_test_cell1...` (FULL, apples-to-apples vs softmax + label-shuffle control) | **MIDDLE_BAND** | `HP2_v3d_beats_softmax_by_min FAILED: v3d_ck=0.492 vs soft_ck=0.461` (margin over a strong softmax baseline too thin) |
| `..._stress_test_cell1..._smoke` | HARD_PASS | `V3D_REPRO ck=0.520; SOFTMAX ck=0.452 (HP2 v3d-softmax=+0.069>=0.05)` |

**Two facts from this table are load-bearing for this drill's S1/S2 question, not just background color:**
1. **v2's own landed verdict shows the PRED-only arm (`gap=0.566`) actually scoring HIGHER than the
   combined HYBRID arm (`gap=0.517`)** on the exact metric this cell family already instruments. This is a
   real, on-substrate, already-landed empirical signal that a predictive-coding-driven representation-
   shaping channel can outperform the contrastive-plus-competitive-allocation combination it was compared
   against -- not merely theoretical plausibility from the biology/ML literature above. (The gap stayed
   within the pre-registered `<=0.15` tolerance band, so this did not trigger a HARD-FAIL on its own, but
   the direction of the effect is informative and was not previously called out in any note found in this
   drill's KB scour.)
2. **The most rigorous check run so far (apples-to-apples, softmax-baseline-controlled, label-shuffle
   control) landed MIDDLE_BAND, not HARD_PASS**, specifically because the margin over a strong softmax
   baseline was too thin (`+0.031` vs. the required `+0.05` minimum). This tempers any claim that Spoke1's
   predictive/competitive mechanism is decisively proven superior to a conventional baseline -- it is
   promising but not yet closed. **Treat Spoke1 as "genuinely tested, mixed/promising results, not yet
   CG-closed" -- upgrade this drill's confidence in viability, but do not claim the underlying question is
   solved.**

I did not find a verdict string in `PROGRESS.md` or `substrate_capability_map.md` referencing "spoke1" by
name -- these landed verdicts appear not to have been rolled up into either tracking document yet. That
rollup (not a new experiment) is itself a cheap, concrete next action independent of anything else in this
drill.

Also on disk: `testbed/substrate_lm/primitives.py` documents "Primitive 2 -- Anti-Hebbian bipartite
contrastive," explicitly commented **"Substitutes for InfoNCE / triplet loss in a NO-GRADIENT setting."**
This is the concrete substrate analog the task's "InfoNCE/VICReg objectives" framing refers to: a symmetric
Hebbian pull-together/push-apart rule on positive/negative pairs, computed with NO gradient and NO
backprop. The comparison this drill draws is therefore NOT "gradient-based contrastive loss vs
gradient-based predictive loss" (a standard ML framing) but **"no-gradient contrastive Hebbian rule vs
no-gradient predictive Hebbian rule"** -- both candidates are already local, non-differentiable-pipeline
primitives; the question is which one (or both, layered) should drive representation formation.

---

## HEADLINE

**Predictive coding is a well-established, genuinely LOCAL learning rule (Rao-Ballard / Whittington-Bogacz)
that provably approximates gradient-based credit assignment under specific settling conditions, and its
single most important structural property -- ONE error signal serving BOTH online inference AND weight
learning, on two timescales -- is not an optional add-on but the definitional feature of the mechanism
itself. It is a genuine, cheap, ADDITIONAL learning axis for this substrate, not a wholesale replacement for
the existing no-gradient contrastive-Hebbian primitive: three independent ML literatures (CPC, VICReg/
Barlow-Twins theory, forecasting/regression) converge on prediction having its OWN degenerate-solution
failure mode (regression-to-the-mean / posterior-collapse), the direct predictive analog of the
representation-collapse the contrastive primitive already guards against -- so it is not free of the
problem it would be added to solve, it trades one collapse mode for another and needs its own
anti-collapse discipline. The sharpest finding of this drill is the grounding cross-link: predicting the
substrate's own INGESTED data stream (not a self-generated or contrastive-paired signal) simultaneously
instantiates TWO of the four ranked differentiation axes identified in today's independent self-play
drill -- axis 1 (disjoint/exogenous data source, the ONLY axis proven ρ=0 by construction) and axis 4
(a different learning-algorithm-class/plasticity-rule, the cerebellum's axis, empirically the strongest
biological track record) -- for free, because ingest data is not self-authored by either learning channel.
This makes prediction-error-against-ingested-data a structurally different, and structurally CHEAPER,
candidate for "the exogenous anchor" than anything requiring new self-play scaffolding, though it does NOT
resolve the harder, contested question of full referential/embodied grounding in the Harnad sense -- the
ML literature is explicit and unresolved on that gap (next-token-prediction-as-grounding debate, S3
below).**

**P_deflated (prediction-error is a viable, worthwhile ADDITIONAL native learning axis for this
substrate's encoder): 0.46** (raised from a pre-disk-check baseline of ~0.42 because the already-landed
Spoke1 `v2` verdict shows the PRED-only arm outscoring the HYBRID arm on the substrate's own instrumented
metric -- real on-disk evidence, not pure literature extrapolation -- but held below the 0.50 novel-
synthesis ceiling because the toughest already-run check (apples-to-apples/softmax-controlled stress test)
landed MIDDLE_BAND, not HARD_PASS, so the underlying mechanism is promising-but-not-decisively-proven even
on the substrate's own existing data).

---

## S1 -- Is prediction-error viable + beneficial as a native learning objective, and which of the 5
brain requirements are load-bearing vs optional for a first cut?

**Viability, established by lit-scan 1 (high confidence, well-replicated):**
- Rao & Ballard (1999) hierarchical predictive coding: each level predicts the level below; the residual
  drives BOTH the fast recurrent state update (inference) AND the local Hebbian-like weight update
  (learning) -- **one error variable, two timescales, not two signals.** This is the single most
  important structural fact from the whole drill: "same signal drives processing and learning" is not an
  engineering choice layered on top of predictive coding, it IS predictive coding's defining mechanism.
  Removing it collapses the framework back into something else (e.g. plain backprop, which needs a
  separately-computed global gradient).
- Whittington & Bogacz (2017, *Neural Computation*) and follow-ups (Millidge, Tschantz & Buckley 2020;
  Salvatori/Song et al. 2020-2022) prove PC networks using only LOCAL Hebbian updates approximate, and
  under specific timing/settling conditions exactly match, backprop's gradient. **Genuinely local**: each
  weight update needs only pre/post-synaptic activity of neighboring layers, no global backward pass.
- Precision-weighting (Friston's free-energy framework): prediction errors are scaled by a
  variance-normalized, Kalman-gain-like precision term before updating representations -- mathematically a
  **cheap, local, multiplicative scalar** on the residual. Neuromodulator-to-precision mapping (ACh/DA
  gain control) is medium-confidence/contested; the formal precision-as-inverse-variance mechanism itself
  is high-confidence.
- **Where PC genuinely costs more than the substrate's existing no-gradient rules:** PC's local weight
  update is cheap, but reaching BP-equivalent quality requires the local INFERENCE phase to iterate to
  convergence before each weight update (a multi-step settling loop, not an instant local rule) -- Zahid,
  Guo & Fountas (2023, *Neural Comp.*, arXiv:2304.02658) show PC's time complexity is lower-bounded by
  BP's, and a documented capacity/scaling gap opens at larger depth/dataset size (best current head-to-head
  at ImageNet scale, a single frontier 2026 paper: PC+equilibrium-propagation hybrid at 13.23% top-5 error
  vs. 12.2% BP baseline -- close, but behind, and unreplicated). **This scaling-gap finding is less directly
  relevant to this substrate** since the substrate does not use backprop anywhere as the comparison target
  -- but the settling-loop COST (iterate-to-convergence before each write) is directly relevant and should
  be budgeted honestly in any cell design.
- **PC vs. the substrate's contrastive-Hebbian primitive are NOT competing solutions to the same problem.**
  Contrastive/InfoNCE-style objectives address "what training signal to use without labels" (pull
  positive pairs together, push negative pairs apart); Rao-Ballard-style PC addresses "how to compute
  credit assignment without a global backward pass." The substrate's `testbed/substrate_lm/primitives.py`
  "anti-Hebbian bipartite contrastive" already solves the second problem WITHOUT gradients (it is itself a
  local rule) -- so for this substrate specifically, PC's local-learning-rule advantage over backprop is
  **not the reason to add it**; the reason to add it is that it targets a genuinely different objective
  (predict future/next input) than the contrastive rule targets (separate similar from dissimilar pairs),
  and per the self-play/differentiation-axis drill (see Cross-thread synthesis) a SECOND, differently-typed
  learning signal on the same data is exactly the kind of differentiation that decorrelates failure modes.

**Which of the 5 requirements (multi-grain predictions; SAME signal for processing+learning;
precision-weighting; top-down generative pathway; production-comprehension forward-model coupling) are
load-bearing vs optional for a first cut:**

| Requirement | Load-bearing? | Cost for THIS substrate | Why |
|---|---|---|---|
| Same signal for processing + learning | **LOAD-BEARING, but FREE** | zero marginal cost | Falls out automatically from wiring `predictive_coding.residual_magnitude` into both a read-time check and a write-time weight update -- this is not an added engineering burden, it is the natural shape of the existing primitive. Removing it is what would cost extra (would need a second, separately-computed error). |
| Precision-weighting | **LOAD-BEARING, CHEAP** | near-zero -- already half-built | `predictive_coding.py`'s `residual_magnitude` (a cosine-derived mismatch fraction) and `proportional_gate` (write strength = clipped residual magnitude) ALREADY implement a precision-weighted write. The only change needed for a v1 predictive learning-axis is to point this gate at a SECOND, dedicated weight matrix used for representation-shaping rather than only for skip/no-skip write decisions on the existing store. |
| Top-down generative pathway (multi-level hierarchy) | Load-bearing for the FULL biological picture; **OPTIONAL for v1** | high -- new build | Requires the hierarchical/recursive structure-builder that `research_neural_substrates_language_brain_architecture_5x_drill_2026-07-09.md` (Broca gap) and `research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md` (multi-hop settling gap) BOTH independently flag as missing, from unrelated angles, same day. Current `predictive_coding.py` is explicitly flat (single W, single-level predict). Defer; build once and let it serve all three threads. |
| Multi-grain predictions (word-level + higher-context simultaneously) | Same as above | Same as above | Directly depends on the hierarchy build; not separable from it. |
| Production-comprehension forward-model coupling | Load-bearing for the full picture; **MODERATE cost, does not need the hierarchy** | moderate -- wiring, not new math | This is concretely "wire `predictive_coding.py`'s residual into `generation.py`'s forward pass" -- already named as gap #3 in the neural_substrates drill, reuses existing primitives, no new representational machinery. Independent of the hierarchy build. |

**Bottom line for S1:** a v1 predictive-learning-axis that (a) reuses the existing
`residual_magnitude`/`proportional_gate` precision-weighting machinery, (b) writes into a SEPARATE
dedicated prediction-weight matrix (kept distinct from the contrastive-Hebbian W, mirroring CLS's "give the
two systems different coding statistics" lesson rather than conflating two learning signals into one
matrix), and (c) stays FLAT (no hierarchy, deferred) is cheap, buildable from existing primitives, and
satisfies the two truly load-bearing requirements for free. The hierarchy and forward-model-coupling
requirements are real but scoped OUT of a first cut without invalidating it -- they upgrade a working v1
into the full biological picture later.

---

## S2 -- Concrete minimal buildable design (HD/VSA terms) + measurable test vs. the current objective

**Design (v1, flat, reuses existing primitives, no new representational math):**

1. During ingest of a sequence, at each step encode the current context `c_t` as an HD vector (reuse
   whatever context-encoding the existing Spoke1 pipeline already uses -- char+positional binding).
2. BEFORE consuming the next token, call the existing `predictive_coding.predict(W_pred, c_t)` to get the
   substrate's current prediction of the next-token HD.
3. Compute `residual_magnitude(observed=actual_next_HD, predicted)` -- already implemented, no new code.
4. Apply `proportional_gate` to get a precision-weighted write strength (surprising/novel transitions get
   written harder; already-predicted transitions get written weakly) -- this is the SAME framing the
   module's own docstring already states ("concentrate plasticity on novel/surprising patterns"), just
   redirected from a skip/no-skip decision on the EXISTING contrastive store to a continuous-strength
   update on a NEW, dedicated matrix.
5. Update a **second, dedicated** weight matrix `W_pred` (NOT the existing contrastive-Hebbian W) via
   `gated_write` with this precision-weighted strength. Keeping `W_pred` structurally separate from the
   contrastive W is the direct HD/VSA translation of the CLS lesson (hippocampus vs. neocortex: different
   coding statistics on the SAME input) and of today's self-play drill's differentiation-axis taxonomy
   (axis 4: different plasticity-rule/algorithm-class, computed on shared upstream data) -- conflating the
   two into one matrix would defeat the entire purpose of adding a differentiated second channel.
6. Concept-HD formation (or downstream retrieval) can then read from `W_pred` alone, from the existing
   contrastive W alone, or from a combination -- exactly the ARM structure the existing Spoke1 cell family
   already uses (`ARM_PREDICTIVE_ONLY` vs `ARM_COMPETITIVE_ONLY` vs `ARM_FULL_HYBRID` per the design note).
7. Hierarchy/multi-grain: explicitly deferred (S1 table). v1 stays single-level, matching Spoke1's honest
   "currently flat" status.

**Measurable test vs. the current objective:** this drill does NOT propose a new cell from scratch --
it proposes an ADDITIONAL arm in the EXISTING Spoke1 cell family
(`exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1/v2`,
`_v3_D_competitive_hebbian_only`), reusing its already-instrumented metrics: `sparse_rate`,
`cat_kitten_cos`, `cat_airplane_cos`, `intra_concept_cv`, `n_concepts_stable`. Per the disk-verify table
above, `v2`'s `ARM_PREDICTIVE_ONLY` (the "PRED" arm in its verdict_msg, `gap=0.566`) **already exists and
already ran**, and already slightly beats the HYBRID arm on the substrate's own metric. What has NOT yet
been tested is the specific S2 proposal on top of that: a DEDICATED, precision-weighted `W_pred` matrix
kept structurally separate from the contrastive channel (current `ARM_PREDICTIVE_ONLY`, per its name and
the design note's own cell description, most plausibly still writes through the same competitive-
allocation/write-gate machinery as the other arms, not a separately-instrumented precision-weighted
strength curve) -- confirming exactly how `ARM_PREDICTIVE_ONLY` computes its write strength requires
reading the `v2` cell source directly (not done in this drill; flagged as the precise, narrow, cheap
next check before authoring a new arm). If `v2`'s existing `ARM_PREDICTIVE_ONLY` already implements
continuous precision-weighted strength on a dedicated matrix, this drill's S2 proposal is answered by
re-reading that arm's already-landed numbers, not by building anything new.

---

## S3 -- The sharpest question: does prediction-error-against-data double as the exogenous grounding
anchor, and how does it connect to the self-play negative?

**The clean part of the answer (well-supported, though the anchor-vs-grounding claims come from different
literatures than the ML-representation-quality claims -- keep these separate, per lit-scan 2's explicit
warning):**

Predicting the substrate's own ingested data stream is structurally different from the self-play
Speaker/Listener setup in exactly the dimension that mattered in today's independent differentiation-axis
drill (`research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`). That drill ranked
four differentiation axes from cheapest/formally-proven to costliest/strongest-biological-track-record:
(1) disjoint/exogenous data split (the ONLY axis proven ρ=0 by construction -- Neyman-orthogonal
cross-fitting), (2) parameter/gradient-flow asymmetry, (3) differentiated objective/criterion, (4)
differentiated learning-algorithm-class (the cerebellum's axis, empirically strongest, spans multiple
axes at once). A prediction-error objective trained against ACTUAL ingested data (real corpus text, not a
self-generated or contrastive-paired signal) automatically satisfies axis 1 -- the target being predicted
was never authored by either learning channel, unlike a Speaker/Listener pair that ultimately both chase
targets derived from the SAME shared upstream representation. It ALSO satisfies axis 4, since a
predictive/precision-weighted delta-rule-like update is a genuinely different plasticity-rule class from
the existing contrastive-Hebbian rule, even though both would read the same upstream ingest stream. Per
that drill's own ranking, spanning MULTIPLE axes at once (as the cerebellum does, vs. CLS's two axes) is
exactly why cerebellar differentiation has the strongest track record in the biology -- adding a
prediction-error channel alongside the existing contrastive one is the substrate-native analog of that
same multi-axis move, and comes essentially "for free" because ingest data is not self-generated.

This also connects to `research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md`'s content-vs-
structural grounding distinction: predicting-the-next-actual-token is not purely STRUCTURAL (an
architectural bias with no exogenous content, like object-persistence or the geometry channel) because the
target IS real exogenous data: but it is also not full CONTENT grounding in the sense of hand-fed semantic
facts (the numeric-attribute seed set proposed by the relational-vs-grounded-meaning drill). It sits
**between** the two categories: an architectural bias (structural) whose training target is nonetheless
always genuinely exogenous (content-adjacent) -- arguably the cheapest available instance of "structural
grounding" that note called for, since it requires no hand-authored fact injection, only correct wiring of
already-ingested data as a prediction target instead of only as a contrastive-pair source.

**The honest, unresolved part of the answer (per lit-scan 2, explicitly contested in the ML literature,
do not oversell):**

None of the JEPA / world-model / CPC literature equates "predicts its own future/next input" with grounding
in the strict Harnad/embodied-referential sense. This is a live, unresolved debate specifically in the
next-token-prediction-as-grounding thread: Bender & Koller (2020, the "octopus test") and Bisk et al. (2020,
"Experience Grounds Language") argue text-only next-token prediction learns FORM not MEANING, and that a
corpus is "a record of experience," not experience itself -- grounding in their strict sense requires
sensorimotor/interactive coupling to real referents, which prediction against a static ingest stream does
not supply. A 2025 mechanistic paper finds specific attention structure that behaviorally LOOKS like
symbol-grounding (binding context tokens to predictions), but a follow-up critique frames this as
"epistemic parasitism" -- inheriting grounding humans already encoded into the text, not manufacturing new
grounding of the model's own. Lit-scan 2 also found NO formal proof that a predictive objective structurally
resists collapse the way this drill might have hoped -- prediction has its own degenerate solution
(regression-to-the-mean / "blurry future" collapse when the true target is genuinely stochastic/
multimodal, the direct analog of posterior collapse in VAEs), and CPC (van den Oord et al. 2018) exists
specifically BECAUSE pure prediction in observation-space or even naive prediction-in-latent-space-without-
a-contrastive-term is prone to exactly this failure -- CPC is a deliberate HYBRID of prediction AND
contrastive terms for this reason, not evidence that prediction alone suffices.

**Sharpest open question, stated precisely:** does prediction-error against the substrate's real ingest
stream supply enough of the axis-1 (exogenous-data) and axis-4 (algorithm-class) differentiation that
today's self-play drill says is necessary, WITHOUT itself collapsing into the "blurry future" degenerate
solution that pure prediction (without a contrastive-style anti-collapse term) is documented to risk on
this substrate's own (already-flagged) tendency toward correlation-driven capacity loss (per
`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`)? The two
literatures point in slightly different directions here: the self-play/differentiation-axis literature
says "add a second, differently-typed channel and you get decorrelation almost for free"; the SSL/CPC
literature says "a pure predictive channel, added alone, has its own collapse risk and historically gets
paired with a contrastive term for exactly this reason." The resolution is NOT to choose one over the
other but to build BOTH: predictive-error write into `W_pred` (this drill's v1 design) PLUS retention of
the existing contrastive write into the existing W (unchanged) -- exactly the "two structurally separate
matrices, not one unified one" design already specified in S2 step 5, which sidesteps the "prediction
alone might collapse" risk by never asking prediction to be the SOLE representation-shaping signal.

**Deflated P estimates (capped at 0.50 per calibration rule):**
- P(prediction-error-against-ingest-data is a viable, worthwhile ADDITIONAL learning axis, kept separate
  from the existing contrastive channel): **0.42** (well-grounded mechanism, untested translation to THIS
  substrate's Spoke1 architecture).
- P(a dedicated `W_pred` matrix, precision-weighted per existing `proportional_gate`, measurably improves
  concept-HD clustering quality (`cat_kitten_cos` etc.) beyond the existing `ARM_FULL_HYBRID` on the
  Spoke1 metric suite): **0.30** (novel-synthesis cap; genuinely untested combination, and the
  collapse-risk caveat above is a real, literature-documented failure mode, not a strawman).
- P(prediction-error against ingest data supplies a MEANINGFUL exogenous-anchor benefit for the self-play
  Speaker/Listener differentiation problem specifically, if wired as a shared exogenous target both
  branches must independently reconstruct -- the Thread-2 fallback named in
  `research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`'s S3): **0.30** (the differentiation-axis
  logic transfers cleanly in principle; whether it transfers to the SPECIFIC self-play cell's architecture
  is untested and flagged there as the fallback-only path, not the first-choice fix).
- P(prediction-error-against-data constitutes full Harnad-sense referential/embodied grounding, not just a
  cheap structural-grounding proxy): **0.15** (deliberately low -- the ML literature itself is split/
  contested on this exact question and the strongest critique -- "epistemic parasitism" -- argues against
  it; this drill does not overturn that debate, it only identifies prediction-against-data as a cheap,
  buildable, PARTIAL instance of structural grounding, not a solved problem).

---

## Cheap decisive test

**Test name:** `predictive_hebbian_second_channel_v1` (extends the existing Spoke1 cell family; does not
require a new cell architecture)

**Step 0 (mandatory, near-zero cost):** read the landed metrics/verdict (if any) of the existing
`exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1.py` and `_v2.py` cells
and the `_v3_D_competitive_hebbian_only_2026-07-02.py` ablation off disk. If `ARM_PREDICTIVE_ONLY` already
tested a continuous-strength, dedicated-matrix predictive channel (not merely a binary write-gate), this
drill's S2 proposal may already be answered -- report the existing verdict instead of re-running.

**Step 1 (if Step 0 finds the question genuinely open):** add ONE new arm, `ARM_PREDICTIVE_DEDICATED`, to
the existing Spoke1 metric harness:
- Reuses the existing char+positional encoder and `predictive_coding.py` primitives unchanged.
- Writes into a SECOND, dedicated `W_pred` matrix via `proportional_gate`-weighted `gated_write` (S2
  steps 1-5), kept structurally separate from the existing contrastive-Hebbian W.
- Concept-HD readout for this arm reads from `W_pred` alone (isolating the predictive channel's
  contribution, mirroring the existing `ARM_PREDICTIVE_ONLY` vs `ARM_COMPETITIVE_ONLY` ablation logic).
- Compare against existing `ARM_FULL_HYBRID` (contrastive + competitive) and `ARM_RANDOM_BASELINE` on the
  SAME metric suite already instrumented (`cat_kitten_cos`, `cat_airplane_cos`, `sparse_rate`,
  `intra_concept_cv`, `n_concepts_stable`).

**Cost estimate:** reuses `hdlab/predictive_coding.py` and the existing Spoke1 corpus/harness unchanged;
new code is limited to a second weight matrix and one new arm wiring. Estimated ~1-2 hr local_cpu build +
smoke (same order of cost as the design note's original Spoke1 estimate).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND, calibration-deflated)

| Claim | HARD-PASS | HARD-FAIL | MIDDLE_BAND | P_deflated |
|---|---|---|---|---|
| Dedicated predictive channel (`ARM_PREDICTIVE_DEDICATED`) produces usable concept clustering on its own | `cat_kitten_cos` >= 0.25 AND `cat_airplane_cos` <= 0.15 (weaker bar than `ARM_FULL_HYBRID`'s 0.4/0.1, since this arm has no competitive-allocation sparsification) | `cat_kitten_cos` < 0.15 (no better than chance-level clustering) -- confirms pure prediction, without a contrastive/anti-collapse term, degenerates toward the "blurry future" collapse documented in the CPC/posterior-collapse literature | `cat_kitten_cos` in [0.15, 0.25) | **0.30** |
| Predictive channel + existing contrastive channel COMBINED beats `ARM_FULL_HYBRID` alone | combined arm beats `ARM_FULL_HYBRID`'s `cat_kitten_cos` by >= 0.05 absolute, with `intra_concept_cv` staying within 15% of `ARM_FULL_HYBRID`'s (no stability cost) | no improvement, or improvement costs >15% `intra_concept_cv` degradation (representation destabilized) | improvement < 0.05 but nonzero, stability intact | **0.30** |
| Precision-weighting (reusing `proportional_gate`) measurably outperforms a flat/unweighted predictive write at matched total write-budget | precision-weighted arm beats flat-write ablation by >= 0.05 on `cat_kitten_cos` at matched write count | no measurable difference | any nonzero but sub-threshold gap | **0.35** |
| Prediction-error-against-data, applied as a shared reconstruction target both self-play branches must independently hit, measurably reduces `corr(failure_mask_speaker, failure_mask_listener)` below the B1 cross-fit baseline (0.39) reported in `research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md` | corr(failmask) <= 0.30 with grounding intact (>= 0.50) | corr(failmask) >= 0.39 (no better than the already-landed B1 baseline) | corr(failmask) in (0.30, 0.39) | **0.25** (this row is the explicit cross-thread test of the S3 grounding-link hypothesis; lower P than the encoder-only rows since it is two inferential steps removed from directly-tested literature) |

All capped <0.50 per lit-scan calibration penalty; all four rows are genuinely untested on THIS substrate
(novel-synthesis regime).

---

## Cross-thread synthesis

- **`research_neural_substrates_language_brain_architecture_5x_drill_2026-07-09.md` (L4):** flagged
  "whether prediction-error is literally THE core learning signal for ACQUISITION... is plausible... but
  not yet as directly causally demonstrated... as the adult cerebellar-rTMS result is for online
  comprehension" -- this drill sharpens that exact open item into a concrete, buildable, substrate-scoped
  design (S2) rather than leaving it as a flagged uncertainty, and supplies the ML-side literature
  (Whittington-Bogacz, precision-weighting formalism) that note's gap-note (sub-agent transcript not
  consolidated) was missing.
- **`research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`:** supplies the
  four-axis differentiation taxonomy this drill's S3 directly builds on. That drill's own residual open
  question -- "does the proven ρ=0 guarantee of disjoint-data cross-fitting survive a COMMUNICATIVE
  convergence requirement" -- is a DIFFERENT open question than this drill's (this drill's target is
  representation quality on ingest-derived concepts, not two-party communicative convergence), but both
  point at the same underlying mechanism (exogenous/disjoint data as the cheapest proven differentiator).
- **`research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`:** names "exogenous grounding... as a
  backstop only when internal architectural asymmetry is degenerate/absent" as the fallback if pattern
  separation (B1+PS) fails to move `corr(failmask)`. This drill's last Falsifiable Prediction row is the
  direct, concrete instantiation of that named fallback -- prediction-error-against-ingest-data as the
  specific exogenous-referent mechanism that note left unspecified.
- **`research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md`:** supplies the content-vs-structural
  grounding distinction this drill's S3 uses to place prediction-error-against-data BETWEEN the two
  categories (structural bias with a genuinely exogenous target) rather than fully inside either.
- **`research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md`:** established that
  relational/structural closure alone cannot manufacture grounded meaning and proposed an externally-fed
  numeric-attribute seed set as one fix (pure CONTENT grounding). This drill's finding is that prediction-
  against-real-ingest-data is a CHEAPER, already-partially-built alternative that does not require
  hand-authoring new facts -- worth comparing cost/benefit against that note's seed-set proposal before
  committing engineering effort to either.
- **`design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md`:** this
  drill discovered the substrate ALREADY has a landed (plausibly HARD-PASSED, unverified) predictive-coding-
  plus-competitive-allocation cell family from a week prior. This is the single most important disk-fact
  this drill surfaced: **the "have we ever tested a prediction-error objective" premise in the task framing
  may be partially false** -- Spoke1 already tests exactly this, at least in a write-gated form. The
  concrete gap this drill identifies is narrower than "never tested": it is specifically "not yet tested as
  a PRIMARY, precision-weighted, dedicated-matrix representation-shaping signal kept structurally separate
  from the contrastive channel" (S2), and "not yet cross-applied to the self-play grounding question" (S3
  last row).
- **`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`:**
  directly informs why `W_pred` must stay a SEPARATE matrix rather than merge into the existing contrastive
  W -- merging would correlate the two channels' codes and risk exactly the capacity loss that reference
  note documents.

---

## Substrate-product implications

- This is not a publication-framing question -- every recommendation above is a concrete, buildable cell
  extension using primitives already on disk (`predictive_coding.py`, the Spoke1 harness), not a new
  representational format or store-schema change.
- **First action before any new build: verify the Spoke1 v1/v2 verdict off disk** (per Fix#28 filesystem-
  verify discipline). This drill's entire cost/benefit calculus changes if Spoke1 already answers part of
  S1/S2.
- The recommended v1 build (S2) is cheap (reuses existing primitives, one new matrix, one new arm) and
  directly testable on the existing Spoke1 metric suite -- no new corpus, no new store format.
- The self-play cross-link (S3, last Falsifiable Prediction row) is the higher-leverage, higher-risk
  extension: if it HARD-PASSES, it closes out the fallback path named (but left unspecified) in
  `research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`'s S3. If it HARD-FAILS, that is itself
  diagnostic -- it would mean the self-play blind-spot problem is not fixable by adding an exogenous
  reconstruction target either, redirecting that thread toward the cerebellum-style "genuinely different
  architecture" fallback (axis 4 alone, without axis 1) that the self-play drill flagged as the
  highest-cost, last-resort option.
- Standing discipline established by this drill, generalizing beyond this one cell: **any new learning
  signal added to this substrate should be checked against the differentiation-axis taxonomy from
  `research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md` before being merged into
  an EXISTING weight matrix** -- the CLS/correlation-hurts-capacity lesson says conflating two
  differently-typed learning signals into one matrix defeats the purpose of adding the second one in the
  first place.

---

## Citations (verified count: 38 across 3 parallel Sonnet lit-scans, all live-URL or arXiv-ID confirmed by
the dispatched sub-agents; generic neuroscience/ML/statistics terms only, no substrate-novel mechanism
names, cell names, configs, or numerical parameters exposed off-platform per
`[[feedback-query-privacy-decomposition]]`)

**Predictive coding as learning rule (12):** Rao, R.P.N. & Ballard, D.H. (1999) *Nat. Neurosci.* 2(1):79-87;
Whittington, J.C.R. & Bogacz, R. (2017) *Neural Computation* 29(5):1229-1262 (PMC5467749); Millidge,
Tschantz & Buckley (2020) arXiv:2006.04182; Millidge et al. (2022) "Backpropagation at the Infinitesimal
Inference Limit," arXiv:2206.02629; Song, Lukasiewicz, Xu & Bogacz / Salvatori et al. (2022) PLOS ONE,
PMC8970408; Zahid, Guo & Fountas (2023) *Neural Computation* 35(12), arXiv:2304.02658 (critical evaluation);
"Benchmarking Predictive Coding Networks -- Made Simple," arXiv:2407.01163; "Training a PC Network on
ImageNet using Equilibrium Propagation," arXiv:2606.03584 (frontier, single-paper); Scellier & Bengio (2017)
*Front. Comp. Neurosci.*, equilibrium propagation; Lee et al. (2015) / Bengio (2020) target propagation,
Bartunov et al. (2018) arXiv:1807.04587 (scalability critique); Sacramento, Costa, Bengio & Senn (2018)
NeurIPS, arXiv:1810.11393 (dendritic/apical PC); Millidge et al. (2022) unifying PC/EP/contrastive-Hebbian
framework, arXiv:2206.02629.

**Prediction as representation-learning / grounding (13):** LeCun (2022) "A Path Towards Autonomous Machine
Intelligence" position paper; Assran et al. (2023) I-JEPA, CVPR; Meta AI V-JEPA, arXiv:2404.08471; Ha &
Schmidhuber (2018) "World Models," arXiv:1803.10122; Hafner et al. Dreamer series (world-models survey,
arXiv:2411.14499); "Survive or Collapse: Asymmetric Roles of Data Gating and Reward Grounding in Self-Play
RL" (2026), arXiv:2605.22217; SPICE, arXiv:2510.24684; van den Oord, Li & Vinyals (2018) CPC,
arXiv:1807.03748; Henaff et al. (2020) CPC v2, ICML; Bowman et al. (2016) posterior collapse / "Lagging
Inference Networks" survey, arXiv:1901.05534; Bender & Koller (2020) "Climbing towards NLU" ACL (octopus
test); Bisk et al. (2020) "Experience Grounds Language," EMNLP, arXiv:2004.10151; "Mechanistic Emergence of
Symbol Grounding in Language Models" (2025) NeurIPS + "epistemic parasitism" critique, arXiv:2512.09117;
Bardes, Ponce & LeCun (2022) VICReg, ICLR; Zbontar et al. (2021) Barlow Twins, arXiv:2103.03230; "Bridging
the Gap from Asymmetry Tricks to Decorrelation Principles" (2022) NeurIPS; Mathieu et al. (2016) "blurry
future" MSE collapse, arXiv:1511.05440.

**Biology of prediction-error systems (13):** Schultz, Dayan & Montague (1997) *Science* 275:1593-1599;
Gershman & Uchida (2016) *eLife* 5:e15963; Gershman & Uchida (2019) *Nat. Rev. Neurosci.*, "Believing in
dopamine"; Gershman (2024) *Nat. Neurosci.*; den Ouden, Kok & de Lange (2012) *Front. Psychol.* 3:548; Kok,
Jehee & de Lange (2012) *Neuron* 75:265-270; Todorovic & de Lange (2012) *J. Neurosci.* 32:13389; Ito & Kano
(1982) cerebellar LTD, reviewed in *Front. Syst. Neurosci.* (2019); Kostadinov et al. (2019) *eLife*
8:e46870; Hinton, Dayan, Frey & Neal (1995) *Science* 268:1158-1161 (wake-sleep); Buzsaki, "Sleep
microstructure organizes memory replay," *Nature* (2024/2025); Stahl & Feigenson (2015) *Science* 348:91-94;
Perez & Feigenson (2021/2022) *Cognition*; Margoni, Surian & Baillargeon (2024) *Psychological Review*
131:716-748.

Confidence: HIGH for the core predictive-coding-as-local-learning-rule mechanism and the RPE/sensory-PE/
cerebellar-PE mechanistic dissociation (well-replicated, textbook-adjacent literatures). MEDIUM/CONTESTED
for the next-token-prediction-as-grounding equivalence (explicitly a live, unresolved academic debate --
this drill does not claim to resolve it, only maps where the substrate's specific design question sits
relative to it).

---

Per [[feedback-no-papers-product-only]]: no publication framing. Every recommendation above is scoped to a
concrete substrate design change (a second weight matrix reusing an existing primitive, one new cell arm,
one cross-thread test against an already-landed baseline), not a scientific contribution claim.
