# Pre-registration: substrate_pc_binding_operation_family_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive (Research, 2026-06-28) — SIXTH systematic COMPONENT-SUBSTITUTION phase diagram. Prior component phase diagrams (encoder_family v1; cleanup_family; etc.) sweep encoder/cleanup as outer axis. This cell extends to the **binding operation family** — the 4th-most-load-bearing lever (after encoder, cleanup, routing). Current default: circular convolution (HRR). Alternatives: element-wise FHRR multiplication / outer-product (tensor) / Hadamard product on bipolar. Never head-to-head compared at chain-grade scale.

## Anchor

`substrate_pc_binding_operation_family_phase_diagram_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_pc_binding_operation_family_phase_diagram_v1_core.py`.

## Routing

- **Smoke queue:** local (laptop CPU; `.venv/Scripts/python.exe` direct invocation, then `local_cpu_queue` for traceability)
- **Full queue:** **overnight_queue** (GPU) — bind/unbind on N=8192 with M=100 is matmul-heavy across 4 ops; outer-product tensor at N=8192 expands to ~8100 DoF cleanup, complex64 FHRR FFT/Hadamard especially benefits from CUDA.
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator (request via SendMessage post-smoke).

## Why this cell exists (the gap)

Substrate-as-VSA literature (Plate 1995 HRR; Eliasmith FHRR; Kanerva binary spatter codes) gives us at least 4 mathematically distinct binding primitives. The hd-instrument substrate has used **circular convolution (HRR)** by default since CERT 591 — without a head-to-head audit of whether the choice is dominant, competitive, or dominated for downstream pattern completion.

Companion encoder_family_phase_diagram_v1 (in flight) tests encoder choice with **cleanup fixed**. This cell tests **binding choice** with cleanup fixed (modern-Hopfield softmax). Each binding op pairs with its **natural encoder family**: this is the standard literature framing (HRR-real with circular conv; FHRR-complex with Hadamard; bipolar with element-wise; bipolar-outer with tensor-product). Pairing exposes binding-op characteristics in their native geometry; holding encoder constant would handicap 3 of 4 ops since they require their native algebra to make sense.

**Cross-domain prior:** brain-grounded binding (cortex-thalamic) most resembles outer-product/tensor encoding for working-memory traces; HRR/FHRR are biologically inspired by phase coding (theta-gamma); binary spatter codes are Kanerva's sparse-distributed-memory primitive. All four have published reasons to dominate in specific regimes.

## Binding operations (the OUTER axis)

Four ops, each paired with natural encoder; SHAPE_MATCH semantics documented:

| Binding op | Encoder pair | bind(R, F) | unbind(mem, R) | Output dim | Notes |
|---|---|---|---|---|---|
| `circular_convolution` | hrr_real (N=N) | ifft(fft(R) * fft(F)) | ifft(conj(fft(R)) * fft(mem)) | N | classical HRR |
| `element_wise_fhrr` | fhrr (N/2 complex) | R * F (complex Hadamard) | mem * conj(R) | N/2 complex | exact inverse since |R|=1 |
| `hadamard_real` | binary_bipolar (N=N) | R * F (real prod on +/-1) | mem * R (self-inverse) | N | Kanerva binary spatter |
| `outer_product_tensor` | binary_bipolar_outer (N_outer=isqrt(N)) | outer(R, F).flatten() | mode-1 product / N_outer | N_outer^2 ~ N | expanded space; cleanup over F-codebook (N_outer) |

All four feed into the **same iterative softmax-Hopfield cleanup** over the F (filler) codebook with `beta=8.0`:
```
F_{t+1} = sign_op( softmax(beta * score(F_t, F_codebook)) @ F_codebook )
```
where `sign_op` is encoder-family-specific (sign for bipolar; L2-norm for HRR-real; unit-modulus for FHRR; sign for outer-bipolar).

**Why this is apples-to-apples:** all 4 binding ops are evaluated on the SAME PRIMITIVE (BIND-bundle-UNBIND-cleanup role-filler retrieval). M role-filler pairs are bound, summed into a single bundle, then queried with corrupted R; unbind yields noisy F; cleanup pulls back to clean F. Corruption is calibrated per encoder so initial cosine(R_corrupt, R_clean) = 1 - 2c across all ops. The discriminator is identical (top1 recall vs random-floor).

**Shape note (META_RULE_M):** `outer_product_tensor` necessarily expands dimensionality (bind output ~ N_outer^2 = N total DoF, but cleanup operates on the (M, N_outer) F-codebook after mode-1 product reduces back). All other ops preserve dimensionality. This is logged per-point in `bind_output_shape` and `unbind_output_shape`.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| binding_operation (OUTER) | {circular_convolution, element_wise_fhrr, hadamard_real, outer_product_tensor} | 4 |
| N (inner) | {1024, 4096, 8192} | 3 |
| corruption_frac (inner) | {0.10, 0.25, 0.40, 0.475} | 4 |
| cleanup_iters (inner) | {3} | 1 |

`M_items=100` role-filler pairs, `beta=8.0`.

**Cardinality FULL per seed:** `4 * 3 * 4 * 1 = 48` phase points.
**Cardinality SMOKE per seed:** `4 * 1 * 3 * 1 = 12` corner points (N=1024; c ∈ {0.10, 0.25, 0.475}; T=3).

Seeds: 7, 13, 19 (chunked per-seed; 3 sibling files).

Note: inner grid is intentionally tighter than encoder-family (3x4 not 5x2) because bundle-and-unbind is significantly more expensive per-point than encoder-only PC (the bundle is M-times as much work as a single encoding; bind+unbind is FFT-heavy for HRR).

## Hypothesis

**H1 (PRIMARY): Binding operations WILL differ in capacity (M/N cliff) AND/OR corruption tolerance.**
- Prediction per op (HYPOTHESIZED@):
  - `circular_convolution`: classical HRR baseline; cliff at ~0.40 (POSITIVE CONTROL at N=4096, c=0.10 expected top1 >= 0.50)
  - `element_wise_fhrr`: should match or beat HRR in corruption tolerance (phase coherence cleanly separates orthogonal codes); steeper cliff predicted
  - `hadamard_real`: bipolar element-wise has WORST capacity (M=100 random bipolar vectors have high crosstalk in sum) — predicted dominated at all but lowest corruption
  - `outer_product_tensor`: largest representational space (N total DoF still) but cleanup over reduced F codebook may bottleneck; predicted competitive

**H2 (regime-mapping): Different binding ops WIN in different (N, c) regimes.**
- `element_wise_fhrr` or `circular_convolution` likely dominates high-N low-c
- `outer_product_tensor` competitive at high N due to expanded capacity
- `hadamard_real` likely dominated in all regimes (this would be the load-bearing **negative** finding — downstream cells should NOT default to plain bipolar Hadamard for role-filler binding)

**H3 (positive-control): `circular_convolution` at (N=4096, c=0.10, T=3) reproduces literature HRR retrieval with top1 >= 0.50.** If this control fails, the binding-comparison harness is broken; cell aborts with CONTROL_FAIL.

**H4 (null): All 4 binding ops identical within +/- 0.05 top1 at EVERY (N, c) phase point.** If H4 holds, binding choice doesn't matter for PC — load-bearing **negative** finding (downstream cells free to pick any binding op).

**H5 (dominance): One binding op strictly dominates all others at all phase points.** If H5 holds, would be the strongest finding — substrate should switch default.

## Discriminator: per (binding_op, regime) vs random-floor

For each (binding_op, N, c, T) phase point: ARM_MECHANISM (corrupted R; unbind from bundle; cleanup; recall) vs ARM_RANDOM (fresh-random R unrelated to bundle; unbind; cleanup; recall). Random ~ 1/M = 0.01 ~ FLOOR.

**Per-op discriminating_fraction prediction (HYPOTHESIZED@):**
- circular_convolution: ~0.50 (6/12 pts in HP+MB)
- element_wise_fhrr: ~0.55
- hadamard_real: ~0.20 (predicted weakest)
- outer_product_tensor: ~0.40

**Discriminating_fraction (overall) >= 0.30** = pre-reg PASS threshold = >= 15/48 pts per seed in HARD_PASS+MIDDLE_BAND across all binding ops.

**Per-op `disc_frac >= 0.30`** required from at least **2 of 4 binding ops** for HARD_PASS verdict (i.e., binding is a meaningful discriminating lever; not just one op carrying the result).

## Pre-reg bands (per-point; LOCKED at module init)

| Tier | top1_mechanism | Discriminator (mech - random) |
|------|----------------|-------------------------------|
| SATURATED | >= 0.95 | record but down-weight (Skunkworks Q-rule) |
| HARD_PASS | [0.80, 0.95) | >= 0.50 |
| MIDDLE_BAND | [0.50, 0.80) | >= 0.30 |
| HARD_FAIL | (0.10, 0.50) | mechanism breaking |
| FLOOR | <= 0.10 | substrate at chance |

## Cell-level verdict (FULL, per seed)

- **HARD_PASS_BINDING_DISCRIMINATION**: cardinality_ok + arms_differ AND (per-binding-op hashes also differ pairwise: at least 2 of the 6 op-pair-hash comparisons must differ to claim "binding op family matters") AND >= 15/48 points in HARD_PASS+MIDDLE_BAND AND at least 2 binding ops each with disc_frac >= 0.30 AND positive control reproduces (circular_convolution @ N=4096, c=0.10, T=3: top1 >= 0.50) AND at least one binding op shows an interior cliff (cliff_locator in [0.10, 0.50])
- **MIDDLE_BAND_BINDING_DIFFERS_BUT_LOW_DISC**: arms_differ + op-pair hashes differ but disc_pts < 15 OR fewer than 2 ops above 30% disc (binding ops measurably different but not enough coverage)
- **MIDDLE_BAND_BINDING_DIFFERS_BUT_NO_CLIFF**: ops distinguish but no interior cliff at any op
- **MIDDLE_BAND_NULL_BINDING_INVARIANCE**: arms_differ but ALL binding-op-pair hashes IDENTICAL (H4 confirmed — binding choice doesn't matter for PC; cell still useful as honest-negative)
- **HARD_FAIL_CARDINALITY_BREACH**: observed != 48
- **HARD_FAIL_ARMS_IDENTICAL**: mechanism and random hashes match for any binding op (mechanism not working)
- **HARD_FAIL_CONTROL_FAIL**: circular_convolution positive control doesn't reproduce literature HRR (test rig broken; halt before any framing claims)

## Cell-level verdict (SMOKE)

- **HARD_PASS_SMOKE**: 12/12 corner points + arms_differ + 4 distinct binding op hashes (META_RULE_AF) + positive control (circular_convolution @ N=1024, c=0.10) shows top1 >= 0.30 (binding mechanism observable at smoke scale) + discriminator fires (at least one op above floor at c<=0.10)
- **HARD_FAIL_SMOKE_BINDING_COLLAPSE**: 2+ binding ops produce identical hashes at smoke (mechanism bug)
- **HARD_FAIL_SMOKE_CONTROL_FAIL**: positive control fails at smoke
- **HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE** (USER 2026-06-26): smoke at N=1024 shows zero above-floor at low corruption (substrate broken at smoke regime; full grid would also fail)

## Calibration selftest

For each binding_op at N=512, M=10, seed:
1. **Bind/unbind round-trip (clean):** bind item 0; immediately unbind; verify argmax(score(recovered, F_codebook)) == 0. Catches bind/unbind algebra bugs at selftest, BEFORE any cell-level phase points run.
2. **Bundle sanity:** M=10 bundled pairs; unbind query 0; cleanup T=3; top1 >= 0.30 (3x chance at M=10). Catches "bundle blows up" or "unbind not invertible enough" bugs.
3. **Binding bundle hashes distinct:** all 4 binding ops produce distinct bundle byte-hashes at fixed seed (sanity that binding ops actually differ at module load time).

If ANY check fails, selftest exit 1 with verdict_msg naming the failing op.

## CRLB / bundle-noise-floor prediction (META_RULE_AG)

For a bundle of M role-filler pairs in N-dimensional space:
```python
bundle_sigma = sqrt((M-1) / N)
# Top-1 recall ceiling proxy: 1 - 0.5 * exp(-0.5 / bundle_sigma)
# M=100 N=1024 -> sigma=0.31 -> ceiling ~ 0.85
# M=100 N=4096 -> sigma=0.16 -> ceiling ~ 0.92
# M=100 N=8192 -> sigma=0.11 -> ceiling ~ 0.95
```

`crlb_bundle_noise_floor` stamped per (N, M) in metrics. M=100 is well below capacity for all sweep N — so any per-op failure is binding-op-specific not capacity-limited.

## Arms per point (META_RULE_AF)

Each (binding_op, N, c, T) point logs TWO arm results:
1. `ARM_MECHANISM` — corrupted R unbinds, cleanup, top1
2. `ARM_RANDOM_FLOOR` — fresh-random R (unrelated to bundle) unbinds, cleanup, top1; floor ~ 1/M

**arms_differ_sha256** per op: SHA-256(json(mech.recall_per_point)) != SHA-256(json(random.recall_per_point)). All 4 binding op arms must differ from their random.

**binding_op_pair_hashes** (META_RULE_AF extension): SHA-256(json(top1_per_point_for_op_X)) for each op. All 4 hashes computed; for chain-grade discrimination claim, at least 2 of the 6 pairs must differ. If ALL 4 identical, that's the H4 NULL finding.

## Cardinality OK (META_RULE_H)

```
SMOKE: EXPECTED_N_UNITS = 12 (4 ops x 1 N x 3 corruption x 1 iter x 1 seed)
FULL : EXPECTED_N_UNITS = 48 (4 ops x 3 N x 4 corruption x 1 iter x 1 seed)
```

HARD_FAIL if observed != expected (silent-drop guard, USER 2026-06-26 META_RULE_J).

## GPU mandate (Fix #24)

- `import torch` at TOP of file (PROT-020 routing-gate)
- `DEVICE = torch.device("cuda")` preferred; CPU fallback ALLOWED for smoke
- **FULL on CPU REFUSED** unless `HDLAB_QUEUE=local_cpu_queue` env explicit-route (Fix #24)
- All binding pipelines vectorized: codebooks materialized once on DEVICE per (op, N, seed); FFT/Hadamard/outer batched throughout
- complex64 for FHRR; float32 elsewhere
- Per-point peak_mem_mb logged; outer-product-tensor at N=8192 dominates memory (~8100^2 = 65M entries per bind pre-sum, but bind is summed immediately so peak holds (M=100, N_outer^2=8100) = ~3MB)
- GPU util target: `peak_mem_mb / 50` >= 0.5 for 80% of points

## Chunked-per-seed architecture

3 sibling files: `experiments/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{7,13,19}.py`.
Shared core: `experiments/_substrate_pc_binding_operation_family_phase_diagram_v1_core.py`.

Per-seed checkpointing via `experiments/_seed_checkpoint.py` (PROT-021 config-mismatch guard ON).

4 defensive patterns (USER 2026-06-28 hardening):
1. start_marker: STARTED metrics written before any heavy work
2. crash-diag: outer try -> import-crash sentinel with full traceback
3. per-unit checkpoint: write_partial_key per seed
4. heartbeat: per-phase-point flush print

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (mechanism vs random; per-binding-op)
- META_RULE_AE: pre-reg bands LOCKED at module init
- META_RULE_AF: 4 binding op arms produce distinct hashes (else binding substitution didn't happen)
- META_RULE_AG: per-N CRLB bundle-noise-floor pre-validation in Python
- META_RULE_AH: tag every number MEASURED@ | HYPOTHESIZED@ | THEORETICAL@
- META_RULE_H: cardinality_ok mandatory (48 full, 12 smoke)
- META_RULE_J: no silent except; halt on any unit exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS
- META_RULE_M-S (USER 2026-06-24): production-scale calibration; verify-referent-on-per-op-discriminator; basis-vs-use-case; anisotropy-hurts-retrieval; 1.000 suspect (saturation flag)
- Functional-requirement decomposition: bind-bundle-unbind-cleanup = composition of (binding primitive) -> (existing CG primitive iterative_attractor)
- SHAPE_MATCH per binding: bind output shape verified against unbind input shape per point (logged in metrics); outer_product_tensor flagged as dim-expanding
- Substrate-as-canonical query-first: HRR/FHRR primitives + cleanup_attractor v1 reviewed; this cell extends by SUBSTITUTING the binding op, not the cleanup
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at N=1024 with c=0.10 — if NO op above floor at smoke, full at higher N would also fail; abort
- BAND-FLOOR-IS-MIDDLE-BAND (USER 2026-06-26): >=2 ops with disc_frac>=0.30 + positive control + >=2 pair-hashes differing + interior cliff at one op = HARD_PASS; otherwise MIDDLE_BAND
- Honest-downward classification per op (USER 2026-06-26): if one op dominates all regimes, that's strong; if all 4 cluster within +/- 0.05, that's H4 NULL

## Positive control

`circular_convolution` at (N=4096, c=0.10, T=3) must reproduce HRR role-filler retrieval with top1 >= 0.50 (literature: clean HRR retrieval at M < N/10 typically > 0.80; at M=100 N=4096 well below capacity; 0.50 is a SAFE floor accounting for sum-bundle interference + 10% corruption). If control fails: cell HARD_FAILs with verdict CONTROL_FAIL.

## Composition edges (substrate atomization context)

- This cell uses existing CHAIN-GRADE primitive `iterative_attractor` (modern-Hopfield softmax cleanup) as FIXED cleanup after unbind. SHAPE_MATCH: each binding op's unbind output (M, N_eff) feeds the cleanup unchanged.
- Binding op is the COMPONENT being swept; cleanup primitive is the COMPOSED-WITH-it primitive (unchanged across arms).
- The new primitive being tested is `binding_op_family`: a 4-arm comparison over the binding role of `(R, F) -> bundle -> unbind -> noisy F` flow.
- Composition edge per binding: encoder_family -> binding_op -> cleanup. SHAPE_MATCH verified per (op, N) at point eval.
- Downstream atomization: HARD_PASS_BINDING_DISCRIMINATION promotes the winning binding op for role-filler ROLE; informs downstream cells' default-binding-op choice.

## ETA

Per-point on GPU (N=8192, M=100, outer-product most expensive due to N_outer=90 -> N_outer^2 = 8100): ~3-5s. 48 pts/seed * ~4s = ~3 min science + 30s init = ~5 min/seed FULL on GPU.

Per-point on CPU (smoke; N=1024, M=50): ~1-2s. 12 pts/seed * 1.5s = ~20s science + 10s init = ~30-45s/seed SMOKE on CPU.

Timeouts:
- SMOKE: 600 s (10 min margin per seed; budget 30-45s expected)
- FULL: 1800 s (30 min margin per seed; budget 5 min expected; PROT-019 has no floor for this cell)

## Substrate-only decode gate

`_LLM_CALL_COUNTER[0] == 0` asserted at exit (no LLM calls in this cell; pure substrate mechanism).

## Smoke gate (MUST pass before FULL dispatch)

1. 12 corner points all ran (no silent except per META_RULE_J)
2. cardinality_ok: observed_n_units == 12
3. arms_differ_sha256.differ == True for ALL 4 binding ops
4. binding_op_pair_hashes: 4 distinct mechanism hashes (META_RULE_AF — binding substitution actually happened)
5. positive_control: circular_convolution @ N=1024, c=0.10 shows top1 >= 0.30
6. discriminator_fires: at least 1 binding op shows top1 > FLOOR (0.10) at low corruption (c <= 0.10)

If gates 1-6 fail, FULL dispatch is HARD-blocked.

## Binding-op routing tier classifications

Per-op downstream verdict (informational; cell aggregator stamps these):
- DOMINANT_BINDING: top1_mean > 0.10 above all other binding ops averaged across all phase points
- COMPETITIVE_BINDING: top1_mean within +/- 0.05 of best op
- DOMINATED_BINDING: top1_mean > 0.10 below best op (downstream should NOT default to this binding op for role-filler)

## Outputs

`data/exp_substrate_pc_binding_operation_family_phase_diagram_v1_seed_{7,13,19}/metrics.json` with:
- phase_map (48 entries per seed at full; 12 at smoke)
- per_op_summary (4 entries; tier classification + top1_mean + cliff_locator + avg_elapsed_per_point_s)
- op_pair_distinctness (6 pair comparisons; any-differ flag)
- positive_control_result (top1 at circular_convolution @ N=4096, c=0.10, T=3)
- crlb_predictions (bundle noise floor per N)
- arms_differ_sha256 (per op)
- tier_counts per op + overall
- disc_frac_per_op (fraction of pts in HP+MB per op)
- bind_output_shape / unbind_output_shape / f_codebook_shape per point (SHAPE_MATCH audit)

Atomization candidates (post-Skunkworks landed-VET):
- if HARD_PASS_BINDING_DISCRIMINATION: SUBSTRATE_BINDING_OP_FAMILY_DISCRIMINATING_FOR_PC + WINNING_BINDING_FOR_PC (whichever op dominates)
- if MIDDLE_BAND_NULL_BINDING_INVARIANCE: BINDING_OP_NOT_DISCRIMINATING_LEVER_FOR_PC (downstream cells free to pick any)
- if HARD_FAIL: NEEDS-RERUN with smoke-gate-specified fix
