# Pre-registration: exp_cortex_integration_m16_attention_router_v1

**Anchor:** `exp_cortex_integration_m16_attention_router_v1`
**Filed:** 2026-07-02
**Phase:** 3c cortex integration — M1.6 attention router coverage
**Author:** hdi_exp_dev
**Session context:** post-compaction; CERT ~697; Cortex facade Phase 2/2b/3/3b landed HARD_PASS 2026-07-02.

## Motivation

Phase 3 (`exp_cortex_integration_end_to_end_v1`, HP 2026-07-02, commit a20ef2f) tested M1.4/M1.5/M1.7/M1.8 primitives through the composed `Cortex.forward()` pipeline. M1.6 attention router (`hdlab/chunked_attention.py::chunked_attention_readout`, invoked from `hdlab/cortex.py:288-307`) was NOT in the discriminator grid. Phase 3b (a2c7722) covered noise-boundary. This Phase 3c closes M1.6 coverage.

Reproduces prior M1.6 CG (2026-07-01 kernel_active_fraction ~99% at M=1M) at reduced scale AND verifies composed pipeline correctly invokes the primitive.

## Hypothesis

H_HP: `Cortex.forward()` invokes `chunked_attention_readout` identically to a direct call at matched (query, keys, vals, chunk_size, beta) — bit-identical readouts within numerical tolerance. Ablation of attention (beta → 0, uniform pooling) collapses readout fidelity to the theoretical uniform-pool floor `1/sqrt(M)`.

## Discriminator design

**Metric:** `readout_cos_correct` = cos(readout_vec, vals[j]) for exact-match query `q = keys[j]`; averaged over Q queries and 3 seeds.

Substrate physics: at N=8192 bipolar keys/vals, for `beta=13` and exact-match query:
- softmax attention peaks at j → readout ≈ vals[j] → cos ≈ 1.0  THEORETICAL@Plate-Kanerva-VSA-cleanup-limit
- with beta≈0 → uniform weights → readout = mean(vals) → cos(mean(vals), vals[j]) = 1/sqrt(M)  THEORETICAL@bipolar-cross-term-cancellation (derived: N/M numerator / sqrt(N/M)*sqrt(N) denominator = 1/sqrt(M))

**Arms:**

| Arm | Implementation | Expected cos at FULL M=1024 |
|---|---|---|
| ARM_COMPOSED_M16 | `Cortex(attention_beta=13.0).forward(q, context_keys=K, context_vals=V)`; read `resp.retrieval` | 1.00 ± 1e-6 |
| ARM_INDIVIDUAL_M16 | `chunked_attention_readout(q_2d, K, V, chunk_size=1024, beta=13.0)` direct | 1.00 ± 1e-6 (bit-identical) |
| ARM_ABLATED_M16 | `Cortex(attention_beta=1e-3).forward(...)` — near-uniform softmax → mean-pooling readout | 1/sqrt(1024) ≈ 0.031 |

Bit-identity between COMPOSED and INDIVIDUAL is the POSITIVE proof of correct wiring (matches Phase 3/3b framing pattern). ABLATED collapse proves beta config parameter propagates end-to-end.

## Envelope bands

- **HARD_PASS:**
  - `|delta_composed_individual| <= 0.05` across all 3 seeds (bit-identity check tight)  HYPOTHESIZED@this prereg (numerical determinism of chunked_attention_readout at matched inputs)
  - `mean(composed_cos) >= 0.95` (attention router genuinely retrieves)  HYPOTHESIZED@this prereg
  - `mean(ablated_cos) <= 0.20` (ablation collapses readout below 5× uniform floor)  THEORETICAL@1/sqrt(1024)=0.031 with margin
- **MIDDLE_BAND:**
  - COMPOSED ≥ 0.95, ABLATED ≤ 0.20, but `|delta_composed_individual|` in (0.05, 0.15]
- **HARD_FAIL:**
  - `|delta_composed_individual| > 0.15` (wiring mismatch — composed does not reproduce individual)
  - OR `mean(composed_cos) < 0.90` (composed pipeline does not retrieve; router path broken)
  - OR `mean(ablated_cos) > 0.30` (beta config not propagating — mechanism is not actually load-bearing OR beta-independent code path)
  - OR cardinality breach

## MANDATORY CELL-TEMPLATE FIELDS (META_RULE_AC/AF/AG/AH + §17)

- `arms_differ_verified: true` — COMPOSED / INDIVIDUAL / ABLATED source hashes differ per META_RULE_AF; NUMERIC bit-identity between COMPOSED and INDIVIDUAL is the POSITIVE proof, not a bug
- `final_metrics_atomicity: tmp_replace`
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException); grep-gate at smoke pre-flight
- `crlb_n/a: "integration-fidelity + wiring-liveness test; ablation floor is closed-form 1/sqrt(M) not a Cramer-Rao bound"`
- `baseline_in_band: exempt` (bit-identity is by-design; ABLATED arm serves the discriminator-fires gate)
- `discriminator_survives_scale: true` — smoke M=128 has 1/sqrt(128)=0.088 (well below 0.20 floor); FULL M=1024 has 1/sqrt(1024)=0.031 (even cleaner). Discriminator strengthens with scale, not weakens.
- `discriminator_reachability: true`
- `HP_SCOPE`:
  - ARM_COMPOSED_M16: [composed_cos >= 0.95, |delta_ci| <= 0.05]
  - ARM_INDIVIDUAL_M16: [|delta_ci| <= 0.05]
  - ARM_ABLATED_M16: [ablated_cos <= 0.20]
- `cardinality_ok: true` — EXPECTED_N_UNITS = 3 arms × 3 seeds = 9
- Per-unit failure-class instrumentation: exception-class captured per unit in metrics.json
- `calibration_check: "default_ok_for_this_regime"` — bipolar cosine, attention beta=13.0 is CG-anchored at Cell D v2
- All numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (see this doc)
- `cell_chunked: false` (single-file 3-seed cell; total FULL wall ~10s <<< runner-zombie risk window)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true`
- `defensive_error_checking: passed_all_4_patterns`
- `progress_logging: line_buffered_stdout` (per §17; total wall << 30min but line-buffer harmless)

## Storage strategy

**SHARDED** — the attention tape (context_keys) has M distinct rows, one per stored item. Each item retrievable independently via cosine similarity. Complies with META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW default (no bundled storage; single-hop retrieval; no downstream chain composition tested in this cell).

## Compute architecture

**(c) mixed — CPU torch, sequential per-query loop** — Q=25 forward calls per arm per seed; each call is a single chunked_attention pass over M=1024 keys at N=8192. Per-call wall ~50ms on CPU (chunk_size=1024 → one chunk). Total FULL wall estimate: 3 arms × 25 queries × 3 seeds × 50ms ≈ 11s. Well below 10s per-phase-point threshold that would demand GPU batching per USER-locked GPU-batching mandate. Sequential is justified: cell is testing wiring integrity, not scale; each forward() call is a distinct pipeline exercise.

## Sweep gates (§15)

- Not a sweep cell (no parameter axis swept). Gates A/B not applicable.
- Gate C — composition_edges:
  - Cortex.forward (query, K, V) → chunked_attention_readout(q_2d, K, V, chunk_size, beta): SHAPE_MATCH (cortex.py:288-294 passes tensors through unchanged; chunked_attention_readout accepts (Q,N)+(M,N)+(M,V) as documented)
- Gate D — positive_control_arms:
  - ARM_INDIVIDUAL_M16 reproduces `chunked_attention_readout` CG (M1.6 attention router closure, 2026-07-01 CG atom; kernel_active_fraction ~99% at M=1M was a scale test; this cell tests wiring at M=1024 reduced scale, expected readout_cos ≥ 0.95 THEORETICAL for peaked softmax at exact-match query with beta=13)
  - Regime extension audit: CG atom cited was M=1M with softmax-active-count metric; this cell uses M=1024 with readout-fidelity metric. Both derive from the same chunked_attention_readout function. SHAPE_MATCH; different metric extraction from same primitive. Documented risk: low (function is deterministic + regime range is within tested envelope).
- Gate E — functional_requirements:
  - FR1: "Cortex.forward exercises M1.6 attention router when context_keys/vals supplied" → chunked_attention_readout invocation at cortex.py:290
  - FR2: "M1.6 readout is peaked at exact-match query and beta=13" → chunked_attention_readout with softmax(beta*sims)
  - FR3: "M1.6 attention_beta parameter propagates from CortexConfig to readout" → CortexConfig.attention_beta → cortex.py:293 → chunked_attention_readout(beta=...)

## Regime + seeds

- SMOKE: seeds=[7]; M_TAPE=128; Q_QUERIES=15
- FULL: seeds=[7, 13, 19]; M_TAPE=1024; Q_QUERIES=25
- N_DIM=8192 (Cortex default)
- V_DIM=8192 (bipolar tape vals same dim as keys for clean cosine-with-val fidelity metric)
- attention_chunk_size=1024
- attention_beta=13.0 (COMPOSED/INDIVIDUAL); 1e-3 (ABLATED)

## Expected outcomes

Most-likely: HARD_PASS. COMPOSED and INDIVIDUAL will bit-identity within floating-point noise (both invoke same function with same args). ABLATED will collapse to ~0.03 at FULL M=1024. HP_CG=0.65 prognosis; downside risks are wiring subtleties in Cortex.forward's query shape handling (unsqueeze) or beta propagation, which the cell explicitly discriminates.

## Downstream action

Cell dispatches SMOKE only (author is exp_dev; laptop-only smoke per USER-locked SMOKE-only-local-CPU rule). FULL routes to Director for orchestrator to push + queue_add to remote_cpu_queue (author cannot push).

## Cross-reference

- Sibling cells: `exp_cortex_integration_end_to_end_v1` (Phase 3 HP), `exp_cortex_integration_with_noise_channel_v1` (Phase 3b HP)
- Facade under test: `hdlab/cortex.py::Cortex.forward` (ATTENTION_ROUTER path, lines 288-307)
- Primitive under test: `hdlab/chunked_attention.py::chunked_attention_readout`
