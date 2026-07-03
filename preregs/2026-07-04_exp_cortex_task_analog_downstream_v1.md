# Pre-registration: exp_cortex_task_analog_downstream_v1

## Purpose

Test whether cortex facade INVOCATION on a downstream task produces measurably-
better task-utility than either (a) individual-primitives-with-no-facade-
composition, or (b) no-cortex-at-all baseline.

Distinct claim from `exp_cortex_integration_end_to_end_v1` (integration-fidelity
CG, math #51): that cell proved the composed pipeline reproduces individual
primitive numbers (BIT-IDENTITY under runtime-call-trace, MEASURED@
data/exp_cortex_integration_end_to_end_v1/metrics.json). This cell proves
"cortex layer actually helps on a downstream task the substrate cares about."

## Task selection + rationale

**Chosen: Task 5 (COMPOSITE) — noisy multi-hop retrieval with three query
intents.**

Rationale: composite stress-tests ALL 4 cortex primitives simultaneously
(M1.4 refuse-gate + M1.6 attention-router + M1.5 context tape via write-through
+ M1.8 clarify-gate three-way route). Task 1 (multi-hop QA) requires substrate-
native QA data with known answers; task 5 uses synthetic bipolar queries but
constructs 3 query intents so the discriminator has structural asymmetry
between arms.

**Substrate-cared-about grounding:** Substrate's retrieval capability (Layer 0.5
in M3 architecture) needs a gating layer to decide "answer confidently vs
refuse vs clarify" — this is critical for the substrate-as-KB dogfood
use case (Director-KB query gate). If cortex_ON > cortex_OFF here, cortex
facade delivers actual utility at Layer 1 above raw retrieval. Substrate
data source cited: HYPOTHESIZED@ synthetic bipolar KB with 3 intent tiers
modeled after real Director-KB query distribution (30% high-confidence
recall, 30% ambiguous cue, 40% out-of-KB per USER 2026-06-28 substrate-mine
discipline; direct substrate query is not yet architected at Layer 0.5 above
the raw partition index).

## Prior-work check (concept-query per USER-locked rule)

Substrate KB query 2026-07-04: `cortex downstream task multi-hop QA cleanup
refuse clarify composition end-to-end`. Top cosine = 0.2783 (below 0.30
threshold). NO direct prior. Load-bearing precedent flagged:
`cortex_hippo_replace_with_refuse_gate_v1` smoke HF HONEST_ABORT (co-saturation
at M/N_c=0.049 — task too easy). This cell explicitly avoids that failure mode
via META_RULE_AG baseline_in_band gate + engineered query-intent asymmetry
(baseline expected utility ~0.50 normalized, well inside [0.05, 0.95]).

## Arms

- **ARM_CORTEX_ON**: `cortex.forward(query, context_keys=K, context_vals=V)`
  end-to-end. Route ∈ {ACCEPT, CLARIFY, REFUSE}.
- **ARM_CORTEX_OFF**: bypass cortex entirely; compute argmax(normalized cosine
  similarity(query, K)); ALWAYS ACCEPT with argmax pred (no gating).
- **ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION**: compute argmax cosine, then
  call `hdlab.refuse_gate.apply_refuse(max_sim, refuse_tau)` standalone; if
  refused, output REFUSE; else ACCEPT with argmax pred. NO clarify-gate,
  NO M1.5 context write-through. Isolates: composition of gates > single gate.

## Task metric

**TASK_UTILITY** per query:
- ACCEPT + correct_val_idx: +1.0
- ACCEPT + wrong_val_idx: -1.0 (penalty for wrong-confident answer)
- REFUSE + out-of-KB query: +0.5 (correctly refused)
- REFUSE + in-KB query: -0.5 (incorrectly refused, missed opportunity)
- CLARIFY: 0.0 (neutral; task can re-query with clarification)

Per-arm TASK_UTILITY = mean(per-query utility) over 100 queries × 3 seeds.
Normalized to [0, 1] for band comparison via `norm_util = (util + 1.0) / 2.0`.

## Query intent mix (100 queries per seed)

- 30 CLEAN queries: exact match to a stored key (sim ~ 1.0 → cortex expects
  ACCEPT + correct)
- 30 NOISY queries: stored key + Gaussian noise sigma=0.60 (sim ~ 0.30-0.40 →
  cortex expects CLARIFY, boundary case)
- 40 OUT-OF-KB queries: random bipolar unrelated (max sim ~ 0.05-0.10 →
  cortex expects REFUSE)

## Hypotheses

- **H1 (main)**: norm_util(ARM_CORTEX_ON) - norm_util(ARM_CORTEX_OFF) ≥ 0.10
  across 3 seeds with cv < 0.20.
- **H2 (null)**: cortex doesn't help — arms tie within 2SE.
- **H3 (composition matters)**: norm_util(ARM_CORTEX_ON) -
  norm_util(ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION) ≥ 0.05. Weaker gap;
  composition-specific lift (clarify-gate + provenance vs just refuse-gate).

## Bands

- **HARD_PASS (SMOKE)**: H1 gap ≥ 0.10 at 1 seed reduced-query; H3 gap ≥ 0.05
  at 1 seed. MM_TENTATIVE only — do NOT overclaim from SMOKE.
- **HARD_PASS (FULL)**: H1 gap ≥ 0.10 across 3 seeds AND cv < 0.20; H3 gap
  ≥ 0.05 across 3 seeds AND cv < 0.20. MM_STANDARD post-FULL.
- **MIDDLE_BAND**: H1 gap in [0.05, 0.10) OR cv in [0.20, 0.30]. Honest-
  tentative "cortex helps modestly."
- **HARD_FAIL**: H1 gap < 0.05 (near-tie) OR ARM_CORTEX_OFF > ARM_CORTEX_ON
  (cortex hurts) OR cardinality != EXPECTED_N_UNITS.

## Envelope-fail-bands

- **PASS_BAND**: ARM_CORTEX_ON norm_util ∈ [0.60, 0.85]; ARM_CORTEX_OFF norm_util
  ∈ [0.35, 0.55]; ARM_INDIV norm_util ∈ [0.45, 0.65].
- **FAIL_BAND**: any arm norm_util > 0.95 (co-saturation like refuse_gate_v1) →
  auto-demote to META_RULE_AG regime-iteration. Any arm norm_util < 0.05 →
  regime too hard.

## Envelope

- N_DIM = 8192 (chain-grade CG floor per hdlab/cortex.py:44)
- M items in KB = 300 (M/N_DIM = 0.037; well below Amit-Gutfreund wall 0.138)
- V_CB = 1024
- STM_K = 100, LTM_K = 1200 (default; unused in this cell — attention-router path)
- refuse_gate_accept_tau = 0.15
- clarify_gate_lower_tau = 0.20 (CLARIFY zone [0.20, 0.40])
- clarify_gate_upper_tau = 0.40
- Noise sigma for NOISY queries: 0.60
- Seeds: SMOKE=[7]; FULL=[7, 13, 19]
- N queries per seed: SMOKE=30 (10/10/10); FULL=100 (30/30/40)

## Storage strategy

**SHARDED** (inherited from `hdlab.chunked_attention.chunked_attention_readout`
M1.6 router path). Each of the 300 KB items has its own key vector in the
attention tape; no bundling. Compliant with META_STORAGE_STRATEGY_COMPOSITION_
DEPTH_PHYSICS_LAW (CG_META 2026-07-02).

## Compute architecture

**(b) sequential-CPU with justification.** Per-query cortex.forward is
sequential: M1.4 → M1.6 → M1.8 gating logic dominated by 300×8192 = 2.5M
mul-adds per query. Total: 100 queries × 3 arms × 3 seeds = 900 forward passes,
each ~5ms on CPU → ~5s per arm-seed, ~45s total for FULL 3 seeds. Well under
wall-time-batching threshold of 10s per-phase-point. GPU batching not
justified: task IS the cortex forward path (composed pipeline), and the
cortex facade sub-primitives (M1.5/M1.7 context) are stateful sequential.

## Discriminator-survives-scale (option A: smoke at FULL envelope)

Smoke uses reduced N_queries=30 (10/10/10) but SAME N_DIM=8192 and SAME M=300.
The mechanism discriminator is per-query gating, which does not depend on
N_queries other than for statistical significance. Discriminator fires at
smoke iff arm-gap ≥ 0.10 at seed=7 with 30 queries.

## SCHEMA-VET fields

- `cardinality_ok`: True — EXPECTED_N_UNITS = 3 arms × 3 seeds = 9 (FULL);
  = 3 arms × 1 seed = 3 (SMOKE). Cell asserts len(per_unit) == expected.
- `arms_differ_verified`: True — SHA256 hash of retrieval vectors across arms
  MUST differ per query per META_RULE_AF.
- `final_metrics_atomicity`: `tmp_replace`.
- `sweep_alignment_verdict`: N/A (no sweep axis).
- `discriminating_fraction`: N/A (no sweep axis; single-regime measurement).
- `composition_edges`: query → cortex.forward → (M1.4 + M1.6 + M1.8); SHAPE_MATCH
  via cortex facade signature (all edges internal to facade).
- `positive_control_arms`: ARM_CORTEX_ON reproduces integration-fidelity cell
  route distribution AT THE TEST REGIME within tolerance 0.15 (route freq
  drift from integration cell); regime_extension_audit: SHAPE_MATCH (same
  N_DIM=8192, same cortex config family).
- `functional_requirements`:
  - FR-1 (accept-when-confident): high-sim query → ACCEPT + correct_val (M1.4/M1.6)
  - FR-2 (refuse-when-uncertain): low-sim OOB query → REFUSE (M1.4)
  - FR-3 (clarify-when-ambiguous): mid-sim noisy query → CLARIFY (M1.8)
  - FR-4 (task-utility-lift): composed pipeline > raw retrieval on TASK_UTILITY
- `calibration_check`: `default_ok_for_this_regime` — refuse_tau=0.15 and
  clarify_upper=0.40 selected from prior cortex integration cell empirical
  quantiles at N_DIM=8192 CG envelope (MEASURED@ integration-fidelity cell
  provenance stats). Adaptive quantile calibration NOT used — fixed thresholds
  chosen a-priori per pre-reg discipline.
- `crlb_n/a`: "gating-utility metric; no capacity noise floor at this M/N"
- `baseline_in_band`: True — expected ARM_CORTEX_OFF norm_util ~ 0.50, in
  [0.05, 0.95] band per META_RULE_AG.
- `cell_chunked`: True — sibling wrappers seed_7 / seed_13 / seed_19 authored
  independently per §13 chunked architecture.
- `start_marker_written`: True.
- `crash_diagnostic_present`: True.
- `heartbeat_present`: True (per-arm ticks via `experiments._cell_heartbeat`).
- `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: `print_flush_true` (per §17 for cells > 30min; this
  cell is <60s so field is compliance-formal not load-bearing).
- `run_mode_verification_post_dispatch`: True — SMOKE dispatch verifies
  landed metrics.json `run_mode` field per §16.

## Framing (Skunkworks-authoritative pre-emptive)

- **If H1 lift ≥ 0.10 AND H3 lift ≥ 0.05 at FULL 3 seeds cv<0.20**: candidate
  atom `EMPIRICAL_CORTEX_LIFTS_DOWNSTREAM_TASK_composite_v1` MM_STANDARD
  post-FULL; CG candidate only if cv<0.15 AND H3-composition-matters fires
  in both directions of ablation.
- **If null (H1 gap in [-0.05, +0.05])**: valuable finding
  `CORTEX_TASK_ANALOG_NULL_FINDING_composite_v1` MM_TENTATIVE. Cortex
  integration-fidelity does NOT translate to task-utility lift on this
  composite-gating task.
- **If ARM_CORTEX_OFF > ARM_CORTEX_ON (cortex hurts)**: honest reporting
  atom candidate `CORTEX_HURTS_DOWNSTREAM_TASK_composite_v1` MM_TENTATIVE.
  Critical for calibration; would indicate gate thresholds are miscalibrated
  or task-utility payoff structure is punishing conservative refusal.

## Provenance

- Author: hdi_exp_dev spawn under USER FULL-AUTO 2026-07-04 00:47Z
- Reference cell: `experiments/exp_cortex_integration_end_to_end_v1.py`
  (integration-fidelity CG landed math #51)
- Reference module: `hdlab/cortex.py` v1 (Phase 2b noise channel wired)
- Load-bearing memory refs: `feedback_smoke_gates_null_hypothesis_should_not_
  gate_on_discriminator_firing_2026-07-03.md`, `feedback_arc_continuation_
  vs_arc_closure_isolated_smoke_not_enough_2026-07-03.md`,
  `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_
  corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`.

## Number-tagging (META_RULE_AC)

- N_DIM=8192: CITED@ hdlab/cortex.py:74 (Cortex CG envelope floor)
- M=300 items: HYPOTHESIZED@ this prereg (M/N < Amit-Gutfreund 0.138)
- Baseline expected norm_util ~ 0.50: HYPOTHESIZED@ this prereg
  (rationale: OOB queries always-ACCEPT-and-wrong penalty balanced by
  clean-in-KB always-ACCEPT-and-correct reward)
- Cortex expected norm_util ~ 0.72: HYPOTHESIZED@ this prereg
- H1 gap ≥ 0.10: HYPOTHESIZED@ this prereg
- Integration cell arm-differ hash pattern: CITED@ experiments/exp_cortex_
  integration_end_to_end_v1.py:16-23
