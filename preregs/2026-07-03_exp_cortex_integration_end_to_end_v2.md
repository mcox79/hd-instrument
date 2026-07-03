# Pre-registration: exp_cortex_integration_end_to_end_v2

**Date:** 2026-07-03
**Anchor:** exp_cortex_integration_end_to_end_v2
**Queue:** local_cpu_queue (SMOKE per USER-locked 2026-07-01 SMOKE-ONLY-LOCAL);
FULL dispatch local per USER-authorized "FULL SPEED FULL AUTO" 2026-07-04 00:47Z
task-explicit auth OR remote_cpu_queue via Orchestrator.
**N:** 8192, **Seeds:** [7, 13, 19] (3 seeds), **Primitives:** {M1.3, M1.4, M1.5, M1.6, M1.7, M1.8}

## Scientific question

Does the composed `hdlab.cortex.Cortex` facade reproduce individual-primitive CG
numbers across ALL 6 primitives (adding M1.3 NoiseChannel + M1.6
chunked_attention_readout to v1's 4-primitive coverage)? Phase 3b extends v1
(commit c16c72ca5, HP-landed 2026-07-03 with m14/m15/m17 CG-promoted +
m18 MM_STANDARD-declared-bypass) to close the 4-of-6 primitive-coverage gap
flagged by Skunkworks landed-VET.

If HP, the M3 cortex facade's end-to-end integration is measured over the FULL
6-primitive stack -- CG upgrade candidacy for m13 + m16 arms (analogous to
m14/m15/m17 in v1) contingent on Skunkworks landed-VET post-FULL.

**Framing (arc-continuation NOT arc-closure):** per USER-locked
feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03,
smoke lands MM_TENTATIVE at most; FULL needed for cross-seed evidence; CG
upgrade candidacy contingent on Skunkworks landed-VET.

## Pre-registered bands

**HARD-PASS:**
- All 6 primitives satisfy `|composed_metric - individual_metric| <= 0.05` on
  every seed in [7, 13, 19]. Formally: for each p in {M13, M14, M15, M16, M17,
  M18}, `max_seed(|delta_p|) <= 0.05`.
- All 6 primitives satisfy cross-seed cv <= 0.05 on the COMPOSED arm.
- All 6 ABLATED arms show mechanism collapse: `ablated_metric < ABLATION_FLOOR`
  (0.10) -- proves each primitive is load-bearing in composed pipeline.
- `arms_differ_verified: True` via RUNTIME-CALL-TRACE (Cortex.forward
  monkey-patched; per-arm forward-call delta matches _ARM_TRACE_EXPECTED).

**MIDDLE:** 4-5 of 6 primitives reproduce within 0.05; 1-2 primitives show
`delta_p in (0.05, 0.10]` -- small integration drift, INTEGRATION_HAZARD flag.
Ablation arms all fire as expected.

**HARD-FAIL:** >=2 primitives fail reproduction (`max_seed(|delta_p|) > 0.10`)
OR pipeline construction raises OR any ablation arm shows no degradation
OR cardinality breach (n_units < 54 FULL / 18 SMOKE).

## Calibration rationale

Per-primitive metric + ABLATION_FLOOR derivation. Numbers tagged
MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ per META_RULE_AC.

### M1.3 NoiseChannel (NEW in v2)

Source signature: CITED@hdlab/noise_channel.py CG source c5e5e66a 2026-07-01
(substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14 HP); Phase 2b
extraction 2026-07-02.

**Metric:** `perturbation = 1 - mean(resp.confidence)` on exact-match queries.
Queries = ctx_keys[idx].clone() (bit-identical to a tape key); noise injection
lowers max_sim from 1.0 (no noise) to `1/sqrt(1+sigma^2)` on bipolar queries
(see calibration note below).

**Sigma calibration -- BIPOLAR VS UNIT-NORM regime distinction (design decision):**
The M1.3 primitive's CG regime is sigma_boundary=0.15 ("moderate") on UNIT-NORM
HRR queries (source selftests use `_hrr_unit(1024, seed=1)`). Under unit-norm
(||q||=1), cos(q, inject(q)) ~= 1/sqrt(1 + N*sigma^2) which at sigma=0.15,
N=8192 gives ~0.074 -> perturbation ~0.93.

BUT this cell's data uses BIPOLAR queries (||q||^2 = N, per-element variance=1),
matching the other primitives' data regimes. On bipolar the formula reduces to
`cos(q, inject(q)) ~= 1/sqrt(1 + sigma^2)` (INDEPENDENT of N -- the noise/signal
ratio per-element is fixed). At sigma=0.15, N=8192, bipolar: cos ~= 0.989 ->
perturbation ~0.011 (below floor). At sigma=1.0, bipolar: cos ~= 0.707 ->
perturbation ~= 0.293 (comfortable margin above 0.10 floor).

We therefore use `M13_SIGMA_BOUNDARY = 1.0` as the INTEGRATION-DISCRIMINATOR
sigma for the m13 arm. This is NOT a claim about the M1.3 primitive at sigma=1.0
in production; it is a fixed-config knob chosen so the ablation gap is
measurable at 8192-D bipolar. The M1.3 primitive itself remains CG at sigma=0.15
on unit-norm queries per source cell.

- COMPOSED path: `cx.forward(query, context_keys, context_vals)` with
  `noise_channel_enabled=True, noise_channel_sigma_boundary=1.0`. Cortex
  invokes NoiseChannel.inject(q_2d) at cortex.py:273. Perturbation = 1 -
  resp.confidence.
- INDIVIDUAL path: instantiate `NoiseChannel(sigma_boundary=1.0,
  generator=noise_rng)` with `noise_rng.manual_seed(seed * 10007 + 42)` --
  matches cortex.py:195 formula for bit-identity. Inject each query manually;
  compute max_sim on original keys; perturbation = 1 - max_sim.
- ABLATED path: `noise_channel_enabled=False` (facade-config ablation); queries
  unmodified. Perturbation ~ 0 (exact match hits with max_sim=1.0).
- Expected: COMPOSED ~ INDIVIDUAL ~ 0.28-0.31 THEORETICAL@
  `1 - 1/sqrt(1+sigma^2)` = 0.293 at sigma=1.0 on bipolar (independent of N).
- ABLATION_FLOOR = 0.10. Ablated perturbation predicted ~0 (exact-match with
  no noise gives confidence=1.0).

Discriminator-fires assertion (selftest): at sigma=1.0, COMPOSED perturbation
> 0.10 (proves NoiseChannel actually operates through facade).

### M1.4 refuse-gate (unchanged from v1)

Source: MEASURED@hdlab.refuse_gate selftest reproduction; CG 2026-07-02 v9
joint-controller (M1.4 CG this session).

Metric: `refuse_rate = mean(route == "REFUSE")` on N_QUERIES uncorrelated
bipolar queries. Predicted ~ 1.00 both arms (|max sim over M=32| ~ 0.03 <
tau=0.20). ABLATION_FLOOR = 0.10.

### M1.5 TwoTierContext (unchanged from v1)

Source: MEASURED@data/exp_cortex_context_retention_v2_seed_7_smoke/
metrics.json:aggregate cv=0.024 (Atom 18 CG 2026-07-01).

Metric: `recall = mean(predicted_val_idx == true_val_idx)` on K writes.
Predicted >= 0.80 both arms. ABLATION_FLOOR = 0.10.

### M1.6 chunked_attention_readout (NEW in v2)

Source signature: CITED@hdlab/chunked_attention.py Phase 3c design 2026-07-02
(FlashAttention-style online-softmax; numerically equivalent to
reference_attention_readout across chunk_size).

**Metric:** `argmax_match_accuracy = mean(argmax(cos(resp.retrieval,
context_vals)) == target_idx)` on exact-match queries. At beta=13.0 (CG
regime), softmax concentrates on target -> retrieval ~= context_vals[target_idx]
-> argmax accuracy ~= 1.0.

- COMPOSED path: `cx.forward` with `attention_chunk_size=8, attention_beta=13.0`
  (chunk_size=8 < m_tape ensures online-softmax exercised). Cortex facade
  invokes chunked_attention_readout at cortex.py:290. Argmax on retrieval.
- INDIVIDUAL path: `chunked_attention_readout(q_2d, keys, vals, chunk_size=8,
  beta=13.0)` directly; same argmax check. Bit-identical because cortex passes
  same args.
- ABLATED path: `attention_beta=0.0` -> uniform attention weights -> retrieval
  = mean(context_vals). Argmax over cos(mean_vals, vals[i]) is near-random
  (~ 1/M for bipolar-random vals). At M=16 (smoke) / M=32 (FULL), predicted
  ablated accuracy ~ 0.06-0.03.
- Expected: COMPOSED ~ INDIVIDUAL ~ 1.00; ABLATED ~ 1/M ~ 0.03-0.06.
- ABLATION_FLOOR = 0.10 (requires M_TAPE >= 16 for below-floor guarantee).

**Design decision on ablation semantics (per USER task deliverable 5):**
chunked_attention is BY DESIGN numerically equivalent regardless of chunk_size
(online-softmax construction; primitive-level test is chunked=reference). So
chunk_size-based ablation trivially non-discriminating. We ablate the
LOAD-BEARING softmax discriminator (beta=0 -> uniform weights) instead --
this is a facade-config ablation that actually collapses retrieval quality.
Documented HONESTLY per Fix#28 discipline.

Discriminator-fires assertion (selftest): at beta=13.0, COMPOSED argmax
accuracy > 0.90 (proves softmax-weighted retrieval concentrates).

### M1.7 RoleSlotSummarizer (unchanged from v1)

Source: MEASURED@data/exp_cortex_summarization_role_slot_v1_seed_7_smoke/
metrics.json ROLE 0.79/0.83/0.79 cv=0.024 (M1.7 CG 2026-07-01).

Metric: `role_top1` recall. Predicted >= 0.75. ABLATION_FLOOR = 0.10.

### M1.8 ClarifyGate (unchanged from v1)

Source: MEASURED@data/exp_stage3_m3_stack_5_primitive_clarify_v1_seed_7_smoke/
metrics.json:B_clarify_recall=0.75, B_clarify_FP=0.00 (M1.8 CG 2026-07-02).

Metric: `clarify_recall`. Predicted ~ 0.75. ABLATION_FLOOR = 0.10.

Discriminating band per Gate B: 6 primitives x 3 outcomes (COMPOSED,
INDIVIDUAL, ABLATED) x 3 seeds = 54 units FULL / 18 units SMOKE. All 6
primitives predicted to land COMPOSED and INDIVIDUAL within 0.05 (bit-
identity via matched implementation + matched noise/seed formulas) and
ABLATED below 0.10.

## Compute architecture (mandatory per USER-locked 2026-07-02)

Class: **(c) mixed** -- inherits `hdlab.cortex.Cortex` MIXED storage strategy
(m13 + m16 both add NO_STORAGE primitives; facade-composition-safety
inherits unchanged).

Justification:
- Each sub-primitive keeps its storage strategy verbatim per Phase 2 module
  docstring; adding M1.3 (NO_STORAGE stateless boundary injector) and M1.6
  (NO_STORAGE functional read) does not change the facade's inherited MIXED
  strategy.
- Compute mode: numpy/torch CPU; no torch.cuda. Per-seed FULL wall estimated:
  v1 c16c72ca5 = 9.24s at 4 primitives -> ~14s at 6 primitives (linear
  extrapolation; m13/m16 both CPU-modest at 8192-D exact-match retrieval).
- Not a GPU-batching candidate: per-primitive walls << 10s each; total FULL
  ~50s wall (3 seeds x ~14s x margin).
- Sequential-CPU appropriate: primitives compose a natural pipeline (write ->
  read -> summarize -> classify) with sequential dependencies; no per-phase-
  point independent axis to batch.

## Storage strategy declaration
`storage_strategy: "MIXED_inherited_per_primitive_no_facade_storage"` --
matches Cortex facade docstring line 19.

## SCHEMA-VET pre-reg fields (mandatory per hdi_exp_dev CHECKLIST)

- `cardinality_ok: True`. FULL EXPECTED_N_UNITS = 6 primitives x 3 arms x 3
  seeds = 54; SMOKE = 6 x 3 x 1 = 18. Verdict logic counts `len(per_unit)`;
  if `!= expected`, emit `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`.
- `arms_differ_verified: True` via RUNTIME-CALL-TRACE (extended v1 discriminator):
  COMPOSED arms invoke cx.forward (>= 1 call); INDIVIDUAL arms bypass facade
  (== 0 calls); ABLATED arms invoke cx.forward with disabled config (>= 1
  call) EXCEPT m15/m18 which bypass by design (documented). Per-arm expected
  pattern in `_ARM_TRACE_EXPECTED` (18 entries).
- `final_metrics_atomicity: "tmp_replace"`.
- `crlb_n/a: "integration-fidelity test; no capacity-noise floor; metric is
  |composed - individual| tolerance not signal-detection"`.
- `baseline_in_band: True` (exempt: bit-identity check by-design; ABLATED arm
  is discriminator-fires gate).
- `calibration_check: "default_ok_for_this_regime"`. Sub-primitive defaults
  inherited from Phase 1 CG selftests; no adaptive calibration.
- `discriminator_reachability: True`. HP threshold `delta <= 0.05` achievable
  given Phase 1 selftests reproduced numbers within 1e-6 for deterministic-
  seed stateful primitives + matched noise-gen seed formula for m13.
- `discriminator_fires: True`. ABLATION arms are discriminator-fires gate;
  each predicted to move below ABLATION_FLOOR=0.10.
- `cell_chunked: False`. Single-seed-per-run via for-loop over [7,13,19];
  wall per seed < 60s; runner-death risk negligible.
- `start_marker_written: True`.
- `crash_diagnostic_present: True`.
- `heartbeat_present: True`.
- `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "print_flush_true"` + `line_buffered_stdout` (defense-in-
  depth for cells with total wall < 30min).

## §15 test-design gates

- Gate A `effective_vs_nominal_parameter_audit`: N/A -- no sweep axis; single
  regime per primitive.
- Gate B `bracket_includes_discriminating_band`: N/A -- integration-fidelity
  test; not a sweep. Discriminator = delta from reference + ablation gap.
- Gate C `signal_shape_compatibility_audit`: SHAPE_MATCH for all edges.
  - M1.3 NoiseChannel: input (1, N) float32 / (N,) float32; output same shape.
    Cortex.forward:257 unsqueezes to 2D, casts to float32, passes to inject.
    Individual: same normalization pre-inject.
  - M1.6 chunked_attention: query (Q, N) + keys (M, N) + vals (M, V); output
    (Q, V). Cortex.forward:290 passes q_2d, keys, vals with matched dtypes.
    Individual: same call.
  - m14/m15/m17/m18: unchanged from v1 (SHAPE_MATCH validated in v1 landing).
- Gate D `reproduce_prior_chain_grade_result_as_positive_control`: THIS CELL
  IS Gate D writ large. Each primitive's INDIVIDUAL arm IS the positive
  control at test regime; COMPOSED claims same primitive on same regime;
  tolerance 0.05. m13/m16 positive-control:
  - m13: INDIVIDUAL uses NoiseChannel(sigma=0.15, gen=matched_seed) matching
    the source primitive's exact API; matched-seed formula gives bit-identity
    to COMPOSED. Tolerance 0.05.
  - m16: INDIVIDUAL calls chunked_attention_readout with same args as
    Cortex.forward passes internally. Tolerance 0.05.
- Gate E `functional_requirement_decomposition_present`:
  - FR1 (NEW): Cortex must inject boundary noise for adaptive downstream (M1.3)
  - FR2: Cortex must refuse uncorrelated queries (M1.4)
  - FR3: Cortex must retain multi-turn context (M1.5)
  - FR4 (NEW): Cortex must attend over context_keys with online-softmax (M1.6)
  - FR5: Cortex must summarize role-slot bindings (M1.7)
  - FR6: Cortex must emit CLARIFY on middle-band confidence (M1.8)
  Each FR maps to one primitive; each primitive already CG'd this session or
  last (m13/m16 CG'd Phase 2b/1 2026-07-02).

## Ablation-fires discipline (per §10 baseline_in_band adaptation)

For each ablated primitive p, the ABLATED arm's metric MUST be below
`ABLATION_FLOOR = 0.10`; else primitive not load-bearing -> HF.

### Ablation semantics per primitive (with rationale):

- **m13:** ABLATED = `noise_channel_enabled=False` (config-level bypass; queries
  unmodified). Perturbation collapses to ~0. Discriminates FACADE INVOCATION
  of NoiseChannel (composed) vs BYPASS (ablated).
- **m14:** ABLATED = `refuse_gate_accept_tau=-1.0` (unreachable low tau; never
  refuses). Refuse_rate collapses to 0.
- **m15:** ABLATED = skip writes (empty context read). Recall ~= 1/V_CB.
- **m16:** ABLATED = `attention_beta=0.0` (uniform weights). See design
  decision note above; chunk_size-based ablation trivially non-discriminating
  by primitive design.
- **m17:** ABLATED = skip `role_slot_context` kwarg (facade doesn't invoke
  summarizer). recall = 0.
- **m18:** ABLATED = `clarify_gate_upper_tau=1e-6` (unreachable low upper).
  clarify_recall = 0.

## N-suffix section

Not sweep-axis dependent. N_DIM = 8192 (Cortex default); anchor is
`exp_cortex_integration_end_to_end_v2` (no _n<N> suffix).

## Timeout estimate

Per-seed FULL wall estimate (extrapolated from v1 c16c72ca5 = 9.24s):
- v1: 4 primitives x 3 arms x 3 seeds -> 36 units in 9.24s = ~0.26s/unit
- v2: 6 primitives x 3 arms x 3 seeds -> 54 units at ~0.26s/unit = ~14s FULL
- Adding runtime-trace pre-flight (18 arms at smoke sizes = ~2s)

Total FULL wall: ~15-20s + margin. `timeout_s = 600s` (10 min floor per
PROT-019 for N=8192).

SMOKE: 1 seed x 6 x 3 = 18 units. ~5-10s + trace ~2s = ~12s + margin.
`timeout_s = 300s`.

## Framing warning

Bit-identical results (delta = 0.000000) on stateful primitives with matched
seeds are the CORRECT positive proof -- COMPOSED goes through the Cortex
facade even when output equals INDIVIDUAL. Verdict logic distinguishes: (a)
COMPOSED == INDIVIDUAL numeric match on stateful/matched-noise primitives =
HP evidence; (b) COMPOSED matches ABLATED (nothing degrades) = HF evidence.

Runtime-trace discriminator (Skunkworks-hardened, v1 c16c72ca5) provides
SEMANTIC path-distinction proof: COMPOSED invokes cx.forward; INDIVIDUAL
bypasses; ABLATED invokes cx.forward with config-disabled primitive.

## Prognosis (from spawn prompt Phase 3b task)

P_CG=0.55 (v1 4/6 CG-promoted this session; extending to 6/6 straightforward
if m13/m16 bit-identity holds via matched noise-gen seed + matched arg
passing; Phase 2b + Phase 3c primitives independently CG'd 2026-07-02).
P_MB=0.35 (small drift plausible in m13 due to noise-gen state ordering
across cortex vs manual; m16 chunked_attention is deterministic so drift
unlikely).
P_HF=0.10 (integration bug not caught by selftests).
