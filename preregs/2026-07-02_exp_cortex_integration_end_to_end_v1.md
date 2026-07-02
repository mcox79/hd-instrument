# Pre-registration: exp_cortex_integration_end_to_end_v1

**Date:** 2026-07-02
**Anchor:** exp_cortex_integration_end_to_end_v1
**Queue:** remote_cpu_queue (FULL); local_cpu_queue (smoke only per USER 2026-07-01)
**N:** 8192, **Seeds:** [7, 13, 19] (3 seeds), **Primitives:** {M1.4, M1.5, M1.7, M1.8}

## Scientific question
Does the composed `hdlab.cortex.Cortex` facade reproduce individual-primitive CG
numbers on the same discriminator grids? Phase 3 of cortex integration proposal
(`notes/proposal_cortex_integration_hdlab_module_2026-07-02.md`). If HP, the M3
architecture has a callable `Cortex.forward()` API composing M1.4 refuse-gate +
M1.5 TwoTierContext + M1.7 RoleSlotSummarizer + M1.8 ClarifyGate with
composition guarantee `|COMPOSED - INDIVIDUAL| <= 0.05` per primitive across
3 seeds.

## Pre-registered bands

**HARD-PASS:**
- All 4 primitives satisfy `|composed_metric - individual_metric| <= 0.05` on
  every seed in [7, 13, 19]. Formally: for each p in {M14, M15, M17, M18},
  `max_seed(|delta_p|) <= 0.05`.
- All 4 primitives satisfy cross-seed cv <= 0.05 on the COMPOSED arm
  (matches Phase 1 selftest fidelity target).
- All 4 ABLATED arms show mechanism collapse: `ablated_metric` degrades below
  primitive-specific ABLATION_FLOOR (see calibration below); proves each
  primitive is load-bearing in the composed pipeline.
- `arms_differ_verified: True` — COMPOSED and INDIVIDUAL arms use distinct
  call sites (hash-checked via `_arms_must_differ` on the primitive-invocation
  code paths; NUMERIC equality on outputs is the discriminator, not a bug).

**MIDDLE:** 3 of 4 primitives reproduce within 0.05; one primitive shows
`delta_p in (0.05, 0.10]` — small integration drift, flag as
INTEGRATION_HAZARD but not blocking. Ablation arms all fire as expected.

**HARD-FAIL:** >= 2 primitives fail reproduction (`max_seed(|delta_p|) > 0.05`)
OR pipeline construction raises OR any ablation arm shows no degradation
(mechanism is not actually load-bearing) OR cardinality breach (n_units < 36).

## Calibration rationale

Per-primitive metric + ABLATION_FLOOR derivation, all MEASURED@ source-cell
CG metrics.json (Phase 1 extraction reproduced these exactly per module
selftests landing 2026-07-02):

**M1.4 refuse-gate** (metric = REFUSE rate on uncorrelated 8192-D queries with
M=32 tape keys, N_QUERIES=50 per seed):
- COMPOSED path: `Cortex.forward(query, context_keys, context_vals)` -> route.
  Confidence = max cos sim(query, keys); refuse-gate applies at
  `refuse_gate_accept_tau=0.20`.
- INDIVIDUAL path: compute max_sim via numpy, call `apply_refuse(s, 0.20)`.
- Metric: `refuse_rate = mean(route == "REFUSE")` on N_QUERIES uncorrelated
  queries. Expected ~ 1.00 both arms (uncorrelated bipolar in 8192-D has
  |max sim over M=32| ~ 0.03 < 0.20; refuse fires).
- Reference: MEASURED@hdlab.refuse_gate selftest reproduction; CG 2026-07-02
  v9 joint-controller (M1.4 CG this session).
- ABLATION_FLOOR: with `refuse_gate_accept_tau=-1.0` (never refuses), expected
  refuse_rate = 0.00. ABLATION_FLOOR = 0.10 (must be < 0.10 to prove primitive
  is load-bearing).

**M1.5 TwoTierContext** (metric = STM read recall on K=5 write-then-read
sequence at N_DIM=8192, V_CB=1024, seed = per-run):
- COMPOSED path: `cx.forward(role_key_i, role_key_for_memory_write=role_key_i,
  val_idx_for_memory_write=val_i)` for K writes; then read via
  `cx.forward(role_key_j)` for K reads; extract `predicted_val_idx`.
- INDIVIDUAL path: instantiate `TwoTierContext(...)`; `.write()` K times; `.read()`
  K times; compare `predicted_val_idx` per query.
- Metric: `recall = mean(predicted_val_idx == true_val_idx)` on K=5 sequence.
  Expected >= 0.80 both arms (STM is direct-write within capacity envelope;
  target_cos_noise=1.0 default is generous).
- Reference: MEASURED@data/exp_cortex_context_retention_v2_seed_7_smoke/
  metrics.json:aggregate cv=0.024 (Atom 18 CG 2026-07-01).
- ABLATION_FLOOR: with EMPTY context (skip writes), `predicted_val_idx == -1`
  for all reads; recall = 0.00. ABLATION_FLOOR = 0.10.

**M1.7 RoleSlotSummarizer** (metric = ROLE top-1 accuracy at K=16 items,
S_ROLES=4, N_DIM=8192, V_CB=1024):
- COMPOSED path: `cx._summarizer.summarize_role(item_keys, role_assign,
  val_indices)` invoked via `role_slot_context` kwarg on `cx.forward()`;
  read `cx_response.role_slots` (S, N).
- INDIVIDUAL path: instantiate `RoleSlotSummarizer(...)`;
  `.summarize_role(...)` directly.
- Metric: `role_top1 = mean(argmax(cos(slot_s, val_codebook)) == expected_val_idx)`
  over S=4 slots on K=16 items -- role-slot recall of per-role bundled
  representation.
- Expected: both arms bit-identical since RoleSlotSummarizer is stateless
  given (n_dim, n_roles, v_cb, seed). Tolerance 0.05 for downstream sampling.
- Reference: MEASURED@data/exp_cortex_summarization_role_slot_v1_seed_7_smoke/
  metrics.json ROLE 0.79/0.83/0.79 cv=0.024 (M1.7 CG 2026-07-01).
- ABLATION_FLOOR: skip `role_slot_context` kwarg -> `resp.role_slots is None`.
  Treated as `role_top1 = 0.00`. ABLATION_FLOOR = 0.10.

**M1.8 ClarifyGate** (metric = clarify_recall on 4-class synthetic max_sim
distributions matching source cell ambient means, N_PER_CLASS=25 per seed):
- COMPOSED path: for each synthetic score, invoke
  `cx.forward(query, context_keys, context_vals)` with keys/vals crafted to
  produce that max_sim; classify via `cx_response.provenance["m18_clarify_
  gate_outcome"]`.
- INDIVIDUAL path: `ClarifyGate(0.35, 0.55).evaluate(score)` on same score
  array.
- Metric: `clarify_recall = mean(outcome == "CLARIFY")` on ambiguous scores.
  Expected ~ 0.75 both arms (matches source cell measurement 0.75; ceiling
  is 3/4 = 0.75 because RETRIEVE ambiguous mean=0.763 > refuse_tau=0.55 by
  construction -- see clarify_gate.py:203-234).
- Reference: MEASURED@data/exp_stage3_m3_stack_5_primitive_clarify_v1_seed_7_smoke/
  metrics.json:B_clarify_recall=0.75, B_clarify_FP=0.00 (M1.8 CG 2026-07-02).
- ABLATION_FLOOR: with `clarify_gate_lower_tau=0.0, upper_tau=1e-9`, all
  scores >= upper -> outcome=ACCEPT; clarify_recall = 0.00.
  ABLATION_FLOOR = 0.10.

Discriminating band per Gate B: 4 primitives x 3 outcomes (COMPOSED,
INDIVIDUAL, ABLATED) x 3 seeds = 36 units; per-primitive delta is scalar in
[0, 1]. All 4 primitives predicted to land COMPOSED and INDIVIDUAL within 0.05
(bit-identity expectation) and ABLATED at < 0.10. Discriminating fraction =
4/4 = 1.00 (all primitives predict distinct COMPOSED-vs-ABLATED behavior).

## Compute architecture (mandatory per USER-locked 2026-07-02)

Class: **(c) mixed** -- inherits `hdlab.cortex.Cortex` MIXED storage strategy.
Justification:
- Each sub-primitive keeps its storage strategy per Phase 2 module docstring:
  - M1.5 TwoTierContext: MIXED (STM sharded across banks; LTM dense-Hopfield)
  - M1.7 RoleSlotSummarizer: SHARDED (per-role slot buffers)
  - M1.4 refuse_gate + M1.8 clarify_gate: NO_STORAGE (functional)
- Compute mode: numpy/torch CPU; no torch.cuda used. Each primitive is
  CPU-modest per its own CG cell wall (M1.5 seed 7 smoke ~5s; M1.7 seed 7
  smoke ~10s; M1.4 ~1s; M1.8 ~1s).
- Not a GPU-batching candidate (per-primitive walls << 10s each; total wall
  expected ~30-60s per seed FULL; total FULL ~3-6 min).
- Sequential-CPU is genuinely appropriate here because the primitives compose
  a natural pipeline (write -> read -> summarize -> classify) with sequential
  dependencies; there is no per-phase-point independent axis to batch.

## Storage strategy declaration
`storage_strategy: "MIXED_inherited_per_primitive_no_facade_storage"` --
matches Cortex facade line 526.

## SCHEMA-VET pre-reg fields (mandatory per hdi_exp_dev CHECKLIST)

- `cardinality_ok: True`. `EXPECTED_N_UNITS = 4 primitives x 3 arms x 3 seeds = 36`.
  Verdict logic counts `len(per_unit)`; if `!= 36`, emit
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `arms_differ_verified: True`. COMPOSED path invokes primitives via
  `cx.forward()` / `cx._context.read()` / etc.; INDIVIDUAL path calls
  functions directly. Distinct call-sites; NUMERIC equality on outputs is
  the discriminator not a bit-identity bug. `_arms_must_differ` runs on the
  code-path fingerprint (hash of arm-implementation strings), NOT on numeric
  output tensors (which SHOULD match).
- `final_metrics_atomicity: "tmp_replace"`. Single-shot cell; writes
  metrics.json.tmp then os.replace.
- `crlb_n/a: "integration-fidelity test; no capacity-noise floor; metric is
  |composed - individual| tolerance not a signal-detection threshold"`.
- `baseline_in_band: True`. COMPOSED baseline for each primitive lands in
  (0.05, 0.95) at pre-registered discriminator regime (M1.4 refuse_rate=1.0
  saturates but is CORRECT-BY-DESIGN -- this is bit-identity check, not
  baseline saturation; declare exempt via calibration_check).
- `calibration_check: "default_ok_for_this_regime"`. Sub-primitive defaults
  (refuse_gate_accept_tau=0.20; clarify 0.35/0.55) are inherited from
  Phase 1 CG selftests; no adaptive calibration in Phase 3.
- `discriminator_reachability: True`. HP threshold `delta <= 0.05` is
  achievable given Phase 1 selftests reproduced numbers within 1e-6 for
  deterministic-seed stateful primitives + within 0.10 for
  distribution-based clarify recall.
- `discriminator_fires: True`. ABLATION arms are the discriminator-fires
  gate; each is predicted to move the metric below ABLATION_FLOOR = 0.10.
- `cell_chunked: False`. Single-seed-per-run via for-loop over [7,13,19];
  wall per seed < 60s; runner-death risk negligible on remote_cpu_queue.
- `start_marker_written: True`. `_write_start_marker` at main() entry.
- `crash_diagnostic_present: True`. `except Exception -> _write_crash_metrics`
  with SystemExit/KeyboardInterrupt ordering per META_RULE.
- `heartbeat_present: True`. `emit_heartbeat` per seed via
  `experiments._cell_heartbeat` helper.
- `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "print_flush_true"`. All progress lines use flush=True
  since wall > ~30s per seed.

## §15 test-design gates
- Gate A `effective_vs_nominal_parameter_audit`: N/A -- no sweep axis; single
  regime per primitive.
- Gate B `bracket_includes_discriminating_band`: N/A -- integration-fidelity
  test; not a sweep. Discriminator is delta from reference.
- Gate C `signal_shape_compatibility_audit`: SHAPE_MATCH for all edges.
  Cortex facade already validated by Phase 2 selftests (5 selftests passed;
  M1.6 router uses (M, N) tape; M1.5 STM writes are (n_dim,) role_keys with
  int val_idx; M1.7 accepts (K, n_dim) item_keys + (K,) role_assign +
  (K,) val_indices; M1.8 evaluates scalar max_sim).
- Gate D `reproduce_prior_chain_grade_result_as_positive_control`: THIS CELL
  IS Gate D writ large. Each primitive's INDIVIDUAL arm IS the positive
  control at test regime; COMPOSED arm claims same primitive on same
  regime; tolerance 0.05.
- Gate E `functional_requirement_decomposition_present`:
  - FR1: Cortex must refuse uncorrelated queries (M1.4)
  - FR2: Cortex must retain multi-turn context (M1.5)
  - FR3: Cortex must summarize role-slot bindings (M1.7)
  - FR4: Cortex must emit CLARIFY on middle-band confidence (M1.8)
  Each FR maps to one primitive; each primitive already CG'd this session
  or last.

## Ablation-fires discipline (per §10 baseline_in_band adaptation)
For each ablated primitive p, the ABLATED arm's metric MUST be below
`ABLATION_FLOOR = 0.10`; if not, the primitive is not actually load-bearing
in the composed pipeline (framing error in Phase 2 architecture) -> HF.

## N-suffix section
Not sweep-axis dependent. N_DIM = 8192 (Cortex default); anchor is
`exp_cortex_integration_end_to_end_v1` (no _n<N> suffix because there is no
N-sweep; single N regime matches Phase 2 CG envelope).

## Timeout estimate

Per-seed wall (measured on Phase 1 selftests + Phase 2 selftests):
- M1.4 arms: ~1s (deterministic function eval)
- M1.5 arms: ~5s (K=5 write-then-read at N=8192)
- M1.7 arms: ~10s (K=16 summarize at N=8192, S=4)
- M1.8 arms: ~1s (25-score evaluation)
- Overhead (setup, cross-arm compare, metrics writes): ~5s

Total per seed FULL: ~25s. 3 seeds -> ~75s. Add 4x margin for CPU-runner
variance + heartbeat overhead: `timeout_s = 600s` (10 min floor per PROT-019).

Smoke: 1 seed, reduced K per primitive (M1.5 K=3 / M1.7 K=8 / M1.8 N_PER_CLASS=10).
Smoke wall ~15s. Smoke timeout_s = 300s.

## Framing warning
Bit-identical results (delta = 0.000000) on stateful primitives with matched
seeds are the CORRECT positive proof -- COMPOSED goes through the Cortex
facade even when output equals INDIVIDUAL (per `_arms_must_differ` code-path
distinction). Verdict logic distinguishes: (a) COMPOSED == INDIVIDUAL numeric
match on stateful primitives = HP evidence; (b) COMPOSED matches ABLATED
(nothing degrades) = HF evidence.

## Prognosis (from spawn prompt)
P_CG=0.60 (Phase 1 module extractions reproduced source CG numbers within tol;
Phase 2 selftests all pass; primitives are known bit-identical to their source
cells within seed-noise); P_MB=0.30 (small drift plausible in composed
pipeline due to torch.float32 accumulation order or sub-primitive re-seeding);
P_HF=0.10 (integration bug not caught by Phase 2 selftests).
