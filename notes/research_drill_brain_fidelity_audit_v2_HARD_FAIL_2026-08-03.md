# Brain-fidelity element audit: v2 event-predictor HARD_FAIL (2026-08-03)

Filed by: Director, per USER directive after the v2 redo's `MECHANISM_HARD_FAIL`
(`data/exp_event_level_prediction_error_relation_inference_phase1_v2_associative/metrics.json`,
commit 9b9781fda). Scope: confirm/refute that v2 was brain-faithful IN EVERY ASPECT as a TEST,
per the always-on brain-fidelity-element-audit discipline
(`feedback_on_every_negative_audit_each_element_brain_fidelity_2026-07-25`): a miss is never a
ceiling until the test is exactly like the brain; a similarity-proxy where the brain reasons is
an architecture-fix case, not evidence against the mechanism.

## 0. KB-check (mandatory before writing)

`substrate_query.sh "event predictor loses to copy context baseline narrative continuity linear
map fidelity"` — top hit `Continuity`/`continuity` concept nodes at cosine 0.3281 (WordNet
lexical, not conceptual overlap); highest non-trivial hit is a coref pre-reg chunk at 0.3037
(different mechanism entirely — pronoun-carry continuity, not event-prediction fidelity). No
duplicate prior audit of THIS specific v2 setup. Reusing, not re-deriving, two existing docs:
`notes/research_drill_biology_led_encoder_target_representation_2026-08-03.md` (the Zacks /
Trabasso / Zwaan / Mar citation set, DOI/venue-verified there) and
`notes/research_drill_brain_fidelity_audit_event_relation_inference_phase1_2026-08-03.md` (the
v1 component-by-component audit, commit 5bfe20d24) — cited below, not re-derived. This audit's
job is narrower and specific to v2: which of v1's named deviations still apply, which changed,
and whether v2's specific empirical failure (trained loses to copy-context) is explained by a
non-faithful element.

## 1. Disk-verified facts (v2 code + metrics.json, re-read, not assumed)

Source: `experiments/exp_event_level_prediction_error_relation_inference_phase1_v2_associative.py`
(lines 1-966+); `data/exp_event_level_prediction_error_relation_inference_phase1_v2_associative/metrics.json`.

- `verdict_msg`: `TOP_VERDICT=MECHANISM_HARD_FAIL; stage_b_pass=False (retrieval: trained=0.1077
  random=0.0838 mean=0.0984 copy=0.1189; margins rand=+0.0239 mean=+0.0093 copy=-0.0112;
  n_test_pairs=3222)`. Chance = 1/10 = 0.10. Required margin over ALL THREE baselines = 0.05
  absolute. Trained cleared none by the required margin, and **lost outright to copy-context**
  (margin -0.0112).
- Diagnostic-only MSE (not the gate, but informative): `mse_test_trained=0.333`,
  `mse_test_random_init=0.654`, **`cosine_test_trained=0.578`** vs
  `cosine_test_random_init=0.025`. The trained predictor's output is highly uniform/cosine-close
  across test inputs (0.578 mean cosine to target is suspiciously high for a context-sensitive
  predictor) — the same **mean-reversion signature** that got v1 disqualified
  (`notes/skunkworks_audit_phase1_event_level_prediction_error_STAGE_B_FAILS_FAIR_BASELINE_2026-08-03.md`),
  now hiding behind a metric (retrieval) designed specifically to NOT reward mean-reversion. This
  is corroborating evidence, not the gate itself.
- `EVENT_CONTEXT_WINDOW = 1` (line 276): a single preceding **sentence** (segmented by naive
  regex sentence-split, Stage A unchanged from v1), taken as-is, no bundling, no binding beyond
  what `build_event_struct_v6` already does per-sentence.
- The 2-event directional bind+bundle scheme was tried and self-test-falsified BEFORE any full
  run (docstring lines 37-64): summing two unit-magnitude phasors and renormalizing
  per-component collapses swap-order to a bit-identical composite (`overlap=1.0` for A-then-B vs
  B-then-A). Window=1 was adopted as the "nothing to swap" fallback, not a principled context
  design.
- Retrieval metric (`score_retrieval`, lines 491-530): for each held-out test pair, rank the
  **true literal next sentence's bound FHRR structure** against 9 same-novel distractor
  sentences via `structure_overlap`; top-1 correct only if the true target strictly maximizes
  overlap (ties count as wrong). `n_test_pairs=3222` pooled across 5 novels.
- Representation: `build_event_struct_v6`, AGENT/ACTION/OBJECT only (no GOAL/OUTCOME slot) —
  unchanged from v1.
- Predictor: `EventPredictor`, a single linear map `x @ W`, trained by full-batch delta-rule
  (Widrow-Hoff) gradient descent on squared error, 300 epochs, L2=1e-4 — unchanged from v1.
- Stage C did not run (`stage_c_readout_ran=False`) — Stage B's gate failed, so the readout
  deviations named in the v1 audit (Deviation 1: similarity-proxy vs mentalizing; Deviation 4:
  no GOAL/OUTCOME slot) are **not implicated in this specific HARD_FAIL** — they never got the
  chance to matter.

## 2. Element table: brain SHAPE/POSITION/METRIC vs v2, and is-this-plausibly-causal for the HARD_FAIL

| Element | Brain SHAPE/POSITION/METRIC (Zacks/Trabasso/Zwaan, cited in the two source drills) | v2 | Deviation severity | Plausibly causes THIS HARD_FAIL? |
|---|---|---|---|---|
| **Context breadth** | Zwaan & Radvansky 1998: prediction draws on the ACCUMULATED situation model (space/time/causation/intentionality/protagonist) built over the WHOLE narrative so far. Trabasso & van den Broek 1985: causal CONNECTIVITY, possibly multi-hop and NON-ADJACENT, beats serial position as the predictor of narrative importance — the brain's central, most-replicated finding on this exact question. The brain never predicts "what happens next" from a single isolated prior event. | `EVENT_CONTEXT_WINDOW=1` — literally one preceding sentence, nothing else, by construction (self-declared "sidesteps, does not solve" the order problem). Went from v1's window=2 (already a severe gap per the prior audit) DOWN to window=1 — a REGRESSION in fidelity forced by a math bug, not a design choice. | **SEVERE — worst deviation in the whole cell, and got WORSE from v1 to v2.** | **YES, highest-plausibility cause.** A 1-sentence context is close to information-theoretically starved for predicting an arbitrary next sentence in 5 different novels pooled together; the delta-rule/L2 update has every incentive to smooth toward a near-constant output (matches the observed cosine_test_trained=0.578, the same mean-reversion signature that sank v1) rather than learn context-specific structure, because there just isn't enough context-carried information to differentiate on. This also directly predicts the specific LOSS to copy-context: copy-context exploits genuine local narrative continuity (adjacent sentences share topic/vocabulary) for free, while the trained linear map, given the same single-sentence input, converges toward a global-mean-ish output that discards exactly that local-continuity signal in favor of smoothing. |
| **Prediction target / metric grain** | Zacks: event-model prediction is at the SITUATIONAL grain (goal shift, causal shift, spatial/temporal shift) — the brain predicts the SCHEMA/gist of what's coming, not the literal lexical continuation. Real narrative prose is highly multi-valued at the surface-sentence level (many plausible next sentences satisfy the same situational continuation); the brain's success criterion was never framed as "guess the literal next sentence among candidates." | `score_retrieval`: exact literal next-SENTENCE structural-overlap retrieval against 9 same-novel (deliberately hard, shared-vocabulary) distractors. This asks for surface-form identification, not schema/gist-level prediction. | **HIGH — a non-faithful operationalization of "prediction."** | **YES, second most plausible cause, compounding the first.** Even an architecturally-ideal brain-style situation-model predictor would not be expected to reliably win literal-next-sentence retrieval, because the surface-form entropy of "which exact sentence comes next" is high and largely orthogonal to situational/schematic correctness. This metric is arguably HARDER than the brain's actual task in one sense (surface retrieval, not gist matching) while simultaneously being EASIER to game via raw local continuity in another (which is exactly what copy-context exploits) — the combination structurally favors "copy the input" over "predict the schema," independent of whether the underlying event-level prediction-error paradigm is sound. |
| **Event segmentation (Stage A)** | Zacks/Speer/Reynolds 2007: boundaries = local maxima of SITUATIONAL prediction error, variable-length, online. | Naive regex sentence-split — unchanged from v1, self-flagged "rough, not the variable" in both v1 and v2 docstrings. | **SEVERE (per v1 audit, Deviation 1/3), unchanged.** | **Secondary/compounding, not primary.** Sentence≠event noise degrades both the context (a "preceding event" that may really be mid-scene, a one-word sentence, a dialogue tag) and the target (a "next event" that may just be the same event continuing) — this adds noise on top of the window=1 starvation and the surface-retrieval-metric mismatch, but the magnitude of the observed failure (losing to copy, not just failing to clear margin) is more parsimoniously explained by context breadth + target grain than by segmentation noise alone. Still a real, load-bearing deviation for any re-test. |
| **Event representation (AGENT/ACTION/OBJECT, no GOAL/OUTCOME)** | Trabasso: goal-action-outcome PROPOSITION nodes; the very content the relation-inference axes (unstated_goal, satisfy_restate, thwart_cause) are ABOUT. | `build_event_struct_v6`, AGENT/ACTION/OBJECT only — unchanged from v1 (v1 audit Deviation 4). | Real SHAPE gap. | **NOT implicated in THIS HARD_FAIL** — Stage C (where this would matter) never ran because Stage B failed first. Stays load-bearing for any future re-test that gets past Stage B. |
| **Predictor (linear, single hop)** | Reynolds-Zacks-Braver 2007's own computational model: hierarchical, multi-timescale, RNN-style; not a single linear map. | `EventPredictor`: `x @ W`, one linear layer, delta-rule/Widrow-Hoff trained. | Real SHAPE gap (v1 audit Deviation 6), but **lower priority** — a linear map is a defensible first-stage scaffold per both docstrings' own framing, and delta-rule learning over a genuinely-informative context CAN in principle learn real linear structure (Rescorla-Wagner generalizes cleanly to linear systems). | **Unlikely to be the primary cause.** Given only 1 event of input, no amount of predictor sophistication (short of memorizing training data, which L2 regularization actively discourages) can manufacture information the context doesn't carry. Nonlinearity is a legitimate REVIVAL lever (per the cell's own criteria) but only AFTER context breadth is fixed — layering nonlinearity onto a 1-event input would very likely reproduce the same mean-reversion-toward-copy-loss pattern. |
| **Learning rule (delta-rule / Widrow-Hoff)** | Rescorla-Wagner-family error-driven update — matches. | Unchanged, explicit batch-GD on squared prediction error. | **Faithful, in family.** | **No** — this is the one element the cell gets right, per both this audit and the v1 audit's own conclusion ("METRIC itself is brain-consistent in FAMILY — the closest sub-component to faithful"). The v2 docstring's own framing (training rule "UNCHANGED and NOT the thing that failed") is correct as far as it goes — but it conflates "the update rule is faithful" with "therefore the SETUP as a whole is faithful," which section 3 below argues is not established. |

## 3. Ranked non-faithful elements (by threat to fidelity AND plausibility of causing the observed HARD_FAIL)

1. **`EVENT_CONTEXT_WINDOW=1` (single-sentence context)** — the single most severe deviation
   from Trabasso's non-adjacent causal-connectivity finding and Zwaan's whole-narrative
   accumulated situation model, AND the most plausible proximate cause of the specific failure
   mode observed (mean-reversion-flavored trained output losing to raw copy-context). The brain
   literally never does event-prediction from one isolated prior event; this is not a simplified
   version of the brain's mechanism, it is a categorically different, information-starved task.
2. **Literal-next-sentence surface retrieval as the success metric** — asks for surface-form
   identification among same-novel (deliberately vocabulary-sharing, i.e. hard) distractors, not
   schema/gist-level situational prediction. Compounds (1): a starved context predicting a
   high-surface-entropy target, scored on exact retrieval, structurally favors "copy what you
   just saw" over "predict the situational schema" — independent of whether event-level
   prediction-error learning per se is a sound paradigm.
3. **Naive sentence-split segmentation (Stage A)** — real, self-acknowledged, unchanged from v1;
   secondary/compounding contributor (adds noise to both context and target) rather than primary.
4. **Linear-only, single-hop predictor** — real gap vs. hierarchical predictive coding, but
   plausibly NOT causal for this specific failure (no predictor capacity increase manufactures
   information a 1-event context doesn't carry); legitimate but lower-priority revival lever.
5. Missing GOAL/OUTCOME representation slots — real, but **not implicated** in this HARD_FAIL
   (Stage C never ran).
6. Delta-rule learning objective — faithful, not a deviation.

## 4. Verdict: is the v2 HARD_FAIL a brain-faithful test (negative stands), or an artifact?

**ARTIFACT, not a faithful ceiling.** Per the discipline ("a miss is never a ceiling until it is
exactly like the brain"), v2 fails this bar on the two elements most proximate to the observed
failure: context breadth (window=1, a self-acknowledged emergency fallback from a math bug, not
a design choice) and target/metric grain (literal-sentence surface retrieval, not schema-level
prediction — arguably an unfairly-hard-in-one-sense/easy-in-another operationalization that
structurally favors copy-context regardless of whether the underlying mechanism is sound). The
corroborating diagnostic (`cosine_test_trained=0.578`, high and near-uniform) is consistent with
the trained predictor converging toward a mean-ish output because a 1-sentence context carries
too little differentiating signal to do otherwise — the SAME mean-reversion failure mode that
independently sank v1 (per the numbers-VET, `notes/skunkworks_audit_phase1_event_level_
prediction_error_STAGE_B_FAILS_FAIR_BASELINE_2026-08-03.md`), now recurring under a different
gate. Two independent redos (v1: MSE-gate, symmetric 2-event bundle; v2: retrieval-gate,
window=1) have BOTH shown the trained linear map defaulting toward smoothed/mean-like output
rather than genuine context-conditioned prediction — but in both cases the context supplied was
either symmetric/order-discarding (v1) or starved to a single event (v2), never the accumulated,
directional, whole-narrative situation-model context the brain actually uses. **This is
under-testing the mechanism, not a demonstrated mechanism failure** — the linear
delta-rule-trained event predictor, run against a brain-faithful context (the accumulated
situation model, not a 1-event window), has not yet been tried.

This does **not** mean "just retry, it'll obviously work" — it means the current negative cannot
be read as evidence against event-level prediction-error learning as a paradigm; it can only be
read as evidence against THIS narrow, doubly-starved operationalization of it.

## 5. Brain-faithful re-test spec (if pursued)

Two changes, ranked by the analysis above, reusing already-built/validated substrate capacity
per wire-don't-island (this also directly supports and sharpens the Director's Fork-(B)
recommendation already logged in `notes/WHERE_WE_ARE_NOW.md`'s 2026-08-03 ~17:0XZ entry):

1. **Replace the single-event window with the ACCUMULATED situation-model state** as context —
   reuse `hdlab/situation_model_accumulate.py` + `hdlab/situation_model_multibank.py` (already
   built, WIRED_AND_PIPELINE_USED this session, decode >=0.999 on durable multi-bank memory vs
   0.655 flat-decode degradation) as the predictor's input, instead of a bespoke single-sentence
   tensor. This directly targets Trabasso non-adjacency and Zwaan accumulation, and sidesteps
   the directional bind+bundle degeneracy entirely (the accumulate register already handles
   multi-event integration by a different, already-validated mechanism, not a fragile 2-term
   phase trick).
2. **Move the success metric off literal-surface retrieval toward a schema/gist-level
   discriminator** — e.g., score whether the predicted state's causal-chain membership /
   role-pattern matches the true next event's, reusing `CausalLinkRegister` (already
   disk-verified 0.9722 vs 0.0 cross-chapter) as the judge, rather than asking the predictor to
   win literal-sentence structural-overlap retrieval against same-novel distractors.
3. Nonlinear predictor (revival criterion (a) already in the cell's own pre-reg) — legitimate
   secondary lever, apply AFTER 1+2, not as a substitute for them (a richer predictor over a
   still-starved 1-event window would likely reproduce the same failure).
4. Clause-level / error-driven segmentation — real but lower-priority for explaining THIS
   specific HARD_FAIL; Phase-2 scope as both docstrings already state.

Note this converges with, and sharpens, the already-logged Fork-(B) option in
`notes/WHERE_WE_ARE_NOW.md` (route the relation readout through already-validated organs,
decoupled from the failing bespoke predictor) — this audit's contribution is explaining WHY the
bespoke predictor failed (context-starvation + surface-retrieval-metric mismatch, not a
paradigm-level failure of event-level prediction-error learning), which argues Fork-(B) is not
merely a safe hedge but the correct diagnosis-driven next move, while leaving open that a
properly-context-fed (accumulated situation model) version of Fork-(A) has not actually been
falsified yet.

## Citations

Zacks & Swallow 2007; Zacks, Speer, Swallow, Braver, Reynolds 2007 Psych Bull; Reynolds, Zacks &
Braver 2007; Speer, Zacks & Reynolds 2007; Trabasso & van den Broek 1985; Zwaan & Radvansky 1998;
Zwaan, Langston & Graesser 1995; Mar 2011 — all DOI/venue-verified in
`notes/research_drill_biology_led_encoder_target_representation_2026-08-03.md` and carried
forward via `notes/research_drill_brain_fidelity_audit_event_relation_inference_phase1_2026-08-03.md`,
not re-verified independently here. This audit's own contribution is the v2-specific
element-by-element re-check (context window regression to 1, retrieval-metric grain analysis)
against the disk-verified v2 code and metrics.json.
