# Pre-reg: encoder_phase_traversal_spread_condense_v1

Date: 2026-07-08
Cell: `experiments/exp_encoder_phase_traversal_spread_condense_v1.py`
Anchor: `encoder_phase_traversal_spread_condense_v1`
Trigger: the two-head cell (`exp_encoder_twohead_decoupled_store_retrieval_v1`) solved the certified
strict-tradeoff (`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval`) with TWO
SEPARATE sibling codes off a shared trunk. This cell asks the harder, more memory-efficient question: can ONE
stored representation serve BOTH if retrieval TRAVERSES it through a real structural condensation operator?
"Blow apart (store spread) then pull together (condense at read)."

Prior-work check (MANDATORY substrate-KB concept-query, MEASURED): `bash tools/substrate_query.sh "phase
traversal spread expanded decorrelated storage structural condensation retrieval superposition pointwise"` ->
top hit cosine 0.2891 (a substrate-product-positioning note about multi-field RRF / graph propagation, UNRELATED
to phase-traversal spread-store/condense-retrieve); NO prior arc cell at cosine > 0.30. Genuinely novel at the
concept level (as expected -- the substrate KB has no ingested concept for this). Distinct from
`exp_qe1_substrate_annealing_v1` (beta-knob over a static codebook) and from the two-head cell (two sibling
codes); this is ONE stored code traversed by a structural operator.

## Question
The certified decouple law says the associative store wants DECORRELATED (near-orthogonal) codes for
superposition capacity while noisy pointwise retrieval wants CORRELATED (semantic) codes -- opposite pulls, so a
SINGLE code read a SINGLE way cannot do both. Can ONE stored SPREAD code serve BOTH if the retrieval readout
applies a trained STRUCTURAL CONDENSATION operator that settles it onto the discriminative semantic manifold?

## Mechanism
SPREAD PHASE (store): each concept's NATIVE expanded code s = WTA_topk(x @ W_up), a high-dim (N=4096)
decorrelated sparse-bipolar block code (3.125% sparsity; the fly-LSH / R5 native-expansion construction that
gives high superposition recall). W_up is a fixed random Gaussian Din=1024 -> N (the encoder's native output; NOT
a retrofit sparsification of dense BGE -- guardrail 2). Superposition (bundle J, argmax-cosine top-J) is read in
THIS phase.
CONDENSATION (retrieve): a trained NONLINEAR operator settles the spread code onto the semantic manifold:
c = gelu(s @ W1) @ W2 : (N)->(H=1024)->(Din=1024). Distilled by RKD (match pairwise-cosine geometry to the BGE
teacher). Applied at read time to BOTH the noisy query (expand -> WTA -> condense) and the dictionary; the stored
engram is ONLY the spread code s. A single linear map is the weakest possible condenser (cannot invert the
sign/top-k quantization); the nonlinear MLP is the brain-grounded "settle onto the manifold" operator and gives
the sparse-store mechanism its best honest shot. C is a genuine STRUCTURAL transform of the geometry (changes
which concept wins argmax) -- NOT a scoring temperature, so NOT the QE-1 beta-knob (guardrail 1). lr=1e-3,
lambda_d=1.0.

Because condensation is retrieval-only and the STORE code is unchanged, the superposition SP is preserved BY
CONSTRUCTION; the ENTIRE question is whether SC (pointwise) can be recovered by the structural transform from the
superposition-optimized sparse code, under noise, without storing a second (semantic) code.

## Arms (6)
- `phase_traversal` [HEADLINE]: store native sign-WTA spread s; SC on condense(s) [sign-WTA input].
- `phase_traversal_mag` [ENRICH]: SC on condense(top-k magnitude of z) [same support, keep values].
- `phase_traversal_dense` [ENRICH]: SC on condense(dense z) [no WTA; isolates sparsification cost].
- `spread_static` [FRONTIER / QE-1 negative control]: SC on the raw spread code directly (NO transform; a scoring
  temperature is a monotonic rescale of cosine sims -> identical argmax, so spread_static IS the beta-knob
  ceiling). The HEADLINE must BEAT this by STRUCT_MARGIN or the cell HARD_FAILs as "reduces to QE-1 beta-knob."
- `semantic_static` [FRONTIER]: store semantic BGE-WTA (crowded SP); SC on dense BGE (~1.0). The other corner.
- `oracle` [CEILING]: SP = native spread; SC = teacher dense (decoupled existence proof).
(phase_traversal* + spread_static + oracle share the SAME native-spread store, so their SP is identical; only
semantic_static has a distinct crowded semantic store.)

## Metrics (uniform per arm)
- STORE / SP = superposition recall@J on the WTA block code of the STORE code (bundle J, argmax-cosine top-J).
- RETRIEVE / SC = single-concept pointwise recall@alpha (noisy BGE source -> arm read pipeline -> argmax-cosine).
- achieves_both = native-spread SP@J_OP(5) >= SP_HI AND phase_traversal SC@alpha_OP(1.2) >= SC_HI.
- structural_gain = phase_traversal SC - spread_static SC (must be >= STRUCT_MARGIN: the structural operator must
  beat the static/beta-knob readout, else it is the QE-1 no-op).

## Pre-reg bands (envelope-fail; HEADLINE = phase_traversal; strictly-above-floor per META_RULE_L)
SP_HI=0.83 (>= the decorrelated single-code frontier ~0.828; headroom to the 0.905 ceiling), SC_HI=0.90
(approaching teacher 1.0), MIDDLE_TOL=0.05, STRUCT_MARGIN=0.15.
- `HARD_PASS_PHASE_TRAVERSAL_ACHIEVES_BOTH` = native-spread SP@J_OP >= 0.83 AND condensed SC@alpha_OP >= 0.90
  AND structural_gain >= 0.15. One stored spread engram serves BOTH; the decouple law is realizable as a SINGLE
  traversed representation (no second stored code), approaching the oracle/two-head.
- `MIDDLE_CONDENSE_NEAR_MISS` = SP hits AND condensed SC within MIDDLE_TOL(0.05) of SC_HI AND structural_gain >=
  0.15 (structural transform is real and close; a regime/weight nudge away).
- `HARD_FAIL_REDUCES_TO_QE1_BETA_KNOB` = structural_gain < 0.15 (the condensation gained ~nothing over the static
  raw-spread readout -> the beta-knob no-op).
- `HARD_FAIL_CONDENSE_CANNOT_RECOVER_COLLAPSES_TO_TRADEOFF` = structural_gain >= 0.15 but condensed SC still below
  SC_HI - MIDDLE_TOL (the transform helps but cannot recover pointwise from the superposition-optimized sparse
  code -> collapses to the single-code tradeoff corner). Check ENRICH localizers (dense recovers => WTA is the
  culprit; even dense fails => expansion not condensable at this regime -> escalate/5x-drill).
- Schema breaches (override): `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`, `HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF`,
  `HARD_FAIL_BASELINE_SATURATED_NO_TRADEOFF_META_RULE_AG` (spread_static SC >= 0.95 => no tradeoff to solve).

## Compute architecture
Class (a) batched-GPU. Condenser training is matmul-heavy (per-iter store-code forward B x N @ N x H, nonlinear,
then B x B RKD pairwise); 3 trainable arms x seeds x hundreds of iters. Storage: no_composition/no_store
(encoder-geometry cell; per-concept codes evaluated by argmax-cosine cleanup, not a bundled store). FULL routes
to GPU (overnight_queue): N=4096, V=40000, B=8192 (B > N -> full-rank RKD sample); cell auto-selects cuda. SMOKE
is CPU-local at production N=4096 AND V=8000 (large enough to leave the tiny-V saturation regime so the
discriminator PREVIEWS FULL: the raw-spread beta-knob ceiling must drop into the discriminating band, and the
condenser gets real training signal V >> B) -- DISCRIMINATOR-MUST-SURVIVE-SCALE option C (scaled preview).

## Functional Requirements
- FR1 high superposition recall -> native-expansion + WTA sparse block code (fly-LSH / R5 native-expansion CG
  primitive). Measured: SP@J.
- FR2 noisy pointwise discrimination -> semantic-manifold code (BGE-distilled RKD geometry). Measured: SC@alpha.
- FR3 BOTH from ONE stored code -> structural nonlinear condensation operator mapping the stored spread code to
  the semantic manifold at read time. NO prior primitive maps FR3 exactly -> flagged as this cell's new
  mechanism, tested here (per gate E, new mechanism explicitly designed + flagged).

## SCHEMA-VET / cell-template fields
```json
{
  "cardinality_ok": true,
  "expected_n_units_formula": "n_seeds (each seed = all-arm measurement)",
  "arms_differ_verified": true,
  "arms_differ_exempted": [["oracle", "semantic_static"]],
  "arms_differ_note": "oracle's retrieval readout IS the teacher/semantic readout by construction (arms differ in SP source, not SC dict); declared exemption, MEASURED as the only collision.",
  "baseline_in_band": "spread_static SC@alpha_OP < 0.95 (if raw spread already does pointwise there is no tradeoff to solve -> AG iterate). MEASURED at smoke V=8000 (see below).",
  "final_metrics_atomicity": "tmp_replace",
  "crlb_n/a": "retrieval recall + geometry cosines; no closed-form noise floor. Feasibility calibrated by the two-head/anchor-sweep MEASURED SP band 0.43-0.905 and SC band 0.655-1.0 at this exact regime.",
  "discriminator_reachability": true,
  "calibration_check": "default_ok_for_this_regime (real BGE cache; J_OP/alpha_OP calibrated in the two-head cell before this pre-reg)",
  "cell_chunked": false,
  "cell_chunked_justification": "few-seed single cell with per-seed partial checkpoint+resume (atomic tmp+os.replace); runner-death loses only the in-progress seed. Pausable/restartable (operator is mobile).",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": "print_flush cadence <60s (per-iter every iters//6 + per-arm SP/SC line + per-seed [seed-done]); FULL est <45min on GPU.",
  "defensive_error_checking": "passed_all_4_patterns (start_marker, crash_metrics, no bare/BaseException except, per-seed partial atomic write)",
  "progress_logging": "print_flush_true",
  "progress_cadence_expected_s": 60,
  "sweep_alignment_verdict": "ALIGNED (no swept axis; arms are representation/readout variants each experiencing its own read pipeline directly; no partition/effective-param indirection)",
  "discriminating_fraction": "MEASURED at smoke V=8000 (see below); the load-bearing discriminator is condensed-SC vs beta-knob-ceiling spread_static SC (structural_gain).",
  "positive_control_arms": "native-spread SP reproduces the fly-LSH/native-expansion WTA superposition ceiling (~0.83-0.905); semantic_static/oracle SC reproduces BGE clean pointwise ~1.0. Both MEASURED at smoke.",
  "telemetry_sensitivity": "self-test asserts native-spread SP@J5 AND phase_traversal condensed SC@1.2 both MOVE across seeds 7 vs 13 (not analytically pinned), AND the condensed SC differs from the raw-spread static SC (the operator changes the argmax, not a monotonic rescale). MEASURED PASS.",
  "functional_requirements": "FR1 superposition (native-expansion WTA), FR2 pointwise (RKD BGE-distillation), FR3 BOTH from one traversed code (this cell's new structural condensation mechanism, flagged)."
}
```

## Self-test (MEASURED)
`--self-test` PASS (7 witnesses) MEASURED@data/exp_encoder_phase_traversal_spread_condense_v1 (self-test stdout,
SELFTEST_REGIME N=2048 V=700): valid_enc (semantic SC@0=1.000), sp_high (native spread SP@5=0.997 >= 0.83),
sp_moves + sc_moves (telemetry-sensitive across seeds 7/13), struct_changes (condensed SC 0.556 != raw-spread
0.872 -- the operator changes the argmax, not a monotonic rescale), arms_differ (all distinct except the declared
oracle/semantic_static exemption), trains (finite RKD loss), sc_noise. NOTE the tiny-V=700 selftest is NOT
predictive of the FULL-scale discriminator direction (spread_static is near-saturated at 0.87 with few concepts,
and the condenser has almost no training data); that is exactly why the SMOKE runs at V=8000 (below).

## Smoke (MEASURED)
SMOKE N=4096, V=8000, iters=300, B=1536, seeds 7/13/19; elapsed 1857s CPU. Verdict
`HARD_FAIL_REDUCES_TO_QE1_BETA_KNOB`. All schema gates pass (arms_differ True, collisions [],
baseline_in_band True, cardinality 3/3). MEASURED@data/exp_encoder_phase_traversal_spread_condense_v1/metrics.json:

| arm | SP@5 | SC@0.0 clean | SC@1.2 noisy |
|---|---|---|---|
| phase_traversal (noise-aug sign-WTA condense) [HEADLINE] | 0.977 | 1.000 | 0.538 (cv 0.013) |
| phase_traversal_clean (clean-trained condense) [ablation] | 0.977 | 1.000 | 0.556 |
| phase_traversal_dense (noise-aug dense condense) [enrich] | 0.977 | 1.000 | 0.993 |
| spread_static (raw sparse argmax == beta-knob ceiling) [FRONTIER] | 0.977 | 1.000 | 0.887 |
| semantic_static [FRONTIER] | 0.947 | 1.000 | 1.000 |
| oracle [CEILING] | 0.977 | 1.000 | 1.000 |

HEADLINE: SP@5=0.977 (hit >=0.83) BUT condensed SC@1.2=0.538 (miss <0.90); structural_gain =
0.538 - 0.887 = -0.348 (< STRUCT_MARGIN 0.15; condensation HURTS vs the raw beta-knob readout) ->
pre-registered `HARD_FAIL_REDUCES_TO_QE1_BETA_KNOB` fires.

DECISIVE DIAGNOSTIC (the SC@0.0 clean column): the condenser recovers pointwise PERFECTLY on CLEAN
queries (1.000 for EVERY condense arm incl. sign-WTA). So the condenser is NOT under-capacity /
mis-specified for the mapping task -- the ENTIRE failure is NOISE-ROBUSTNESS: sign-WTA(noisy source) is
a discontinuous, information-lossy sparse pattern (near-threshold top-k coordinate/sign flips) that the
nonlinear condenser cannot map back consistently, while raw sparse-overlap argmax (spread_static 0.887)
degrades more gracefully than the learned map (0.538). The principled remedy -- NOISE-AUGMENTED training
-- was applied and did NOT help (0.538 vs clean-trained 0.556, tight cv across 3 seeds), the strongest
evidence the pointwise-under-noise information is simply ABSENT from the noisy sign-WTA code (an
information wall of the CODE, not a weak operator).

INCIDENTAL (research threads, NOT a rescue): (a) the raw sign-WTA spread code NEARLY achieves both at
V=8000 (SP 0.977 + SC 0.887) -- the strict tradeoff is a large-V phenomenon; whether raw-spread SC holds
>=0.90 at FULL V=40000 is a DIFFERENT (and genuinely open) question this cell's spread_static/oracle arms
answer. (b) condensing the DENSE expanded code holds SC 0.993, but is almost certainly superfluous (dense
z is JL-condensable so raw dense argmax would match it; a raw-dense control arm would confirm) -- NOT a
load-bearing condensation win.

## Genuine-negative vs design-failure read (for skunkworks confirmation)
GENUINE NEGATIVE (not a fixable condenser weakness) for the specific claim "a structural condensation
operator recovers noisy pointwise from a superposition-optimized SIGN-WTA sparse code better than raw
readout." Four evidences: (1) condenser is perfect on clean queries (SC@0=1.000) -> not under-capacity;
(2) noise augmentation, the standard remedy for input-noise fragility, applied and FAILED; (3) the failure
mechanism is information-theoretic (sign+top-k is a discontinuous lossy map; near-threshold flips destroy
the fine cosine structure noisy pointwise needs); (4) raw argmax (the scoring readout) BEATS every
condenser variant on the sparse code -> the mechanism empirically collapses to (worse than) the scoring
knob, exactly the pre-registered degeneration. A condenser redesign (more capacity / different
nonlinearity) will NOT rescue it (info absent); only changing the STORE code to be less
information-destroying under noise could -- but that trades away the superposition capacity / memory
efficiency that was the whole premise. Route to skunkworks to confirm the information-theoretic read
before any 5x drill.

## Disposition
Do NOT ship FULL (smoke HARD_FAILed the headline discriminator at a scale-honest V=8000 preview;
DISCRIMINATOR-MUST-SURVIVE-SCALE -> honest abort beats a fished FULL). The queue_add below is retained
for reference ONLY (the FULL that WOULD be worth running answers the DIFFERENT incidental question --
raw-spread SC at V=40000 -- and is a Director strategy call, not a headline-mechanism ship):
`bash tools/orchestrator/queue_add.sh overnight_queue encoder_phase_traversal_spread_condense_v1 experiments/exp_encoder_phase_traversal_spread_condense_v1.py preregs/encoder_phase_traversal_spread_condense_v1.md 3600`

ASCII-only. No unicode. No emojis. No em dashes.
