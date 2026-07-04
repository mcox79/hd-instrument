# Pre-reg: Encoder Migration Step 2 - Sparse-CSR Encode 970K KB Concept HDs (v1)

**Date:** 2026-07-04
**Anchor (full):** `encoder_migration_step2_sparse_encode_970K_KB_v1`
**Anchor (smoke):** `encoder_migration_step2_sparse_encode_970K_KB_v1_smoke`
**Cell:** `experiments/exp_encoder_migration_step2_sparse_encode_970K_KB_v1_core.py`
**Class:** MM_TENTATIVE at SMOKE; MM_STANDARD post-FULL. CG deferred to Step 3 gold verify (Step 2 is lossless format conversion + fidelity check; no retrieval-quality claim).
**Stage:** 3 (higher-function encoder infrastructure).

## Purpose

Convert Step 1's dense int8 `encoder.npz` to sparse-bipolar CSR `E_concept.pt` <2 GB. Step 1 output at FULL: `[970069, 4096]` int8 = 3.98 GB dense (Step 1 SMOKE observed `mean_nnz=82.0` MEASURED@`data/exp_encoder_migration_step1_..._smoke/metrics.json:mean_nonzero_per_entity`). Sparse CSR at k=82: THEORETICAL@ = 82*(2+1) + 8 = 254 bytes per entity => 970069*254 = 246 MB core arrays; entity_names overhead ~50-200 MB; total ~300-450 MB (well under 2 GB HP band).

Retrieval-quality claim (semantic cosine improvement) is explicitly Step 3's job (100-query gold-standard verify). Step 2 certifies ONLY: sparse format is correct + round-trip is bit-identical + query is fast.

## Design gaps + hard tolerances

- Format spec (from migration plan §Step 2): `active_indices, ±1 signs` per entity + offsets. Concrete choice: int16 active_indices (n_dim=4096 fits comfortably; int8 too small), int8 signs, int64 offsets [N+1]. HYPOTHESIZED optimal (uint16 not natively supported in torch).
- N_DIM=4096 (Step 1 confirmed CITED@Step1_prereg N_DIM=4096); not 8192 as migration plan states -- plan was authored before Step 1 ran.
- Round-trip tolerance: bit-identical (int8 exact; no float rounding). Any mismatch is HF (H3).
- SMOKE input: Step 1 SMOKE encoder.npz at `data/substrate_concept_encoder_v1_smoke/encoder.npz` (1000 entities, MEASURED@Step1_SMOKE_metrics sha256=28c87075617fa1bf... 4.16 MB).
- FULL input: waits for Step 1 FULL landing at `data/substrate_concept_encoder_v1/encoder.npz` (970069 entities).

## Storage strategy

**SHARDED** (per-entity own sparse HD) inherited from Step 1's sharded strategy. Step 2 is lossless format conversion; sharding property preserved by construction (each entity's active_indices + signs slice lives at offsets[i]:offsets[i+1] independent of other entities). Not `bundled` -- there is no cross-entity summation.

## Compute architecture

**Class (b): sequential-CPU with justification.**
- Justification: np.nonzero + np.bincount + numpy indexing on CPU is O(total_nnz) linear; total_nnz FULL ~= 970069 * 82 = 79.5M operations = few seconds on CPU. GPU-batching does not accelerate a linear scan of int8 -> sparse layout. Query benchmark uses np.bincount which is already vectorized C.
- Non-GPU: local_cpu_queue SMOKE authorized (per USER 2026-07-01 SMOKE-only local rule); FULL will run local_cpu_queue after Step 1 FULL lands (Orchestrator or Director routes at that time).

## Mechanism (cell core)

1. Load Step 1 `encoder.npz` (numpy int8 dense [N, 4096]).
2. `rows, cols = np.nonzero(dense)` -- row-major traversal gives rows sorted ascending.
3. `signs = dense[rows, cols].astype(int8)` -- extract sign values at active positions.
4. Validate signs are strictly in {-1, +1} (no zeros in nonzero positions; Step 1 contract).
5. `active_indices = cols.astype(int16)` (n_dim=4096 fits int16 max=32767).
6. `counts = np.bincount(rows, minlength=N)`; `offsets = [0, cumsum(counts)]` int64 [N+1].
7. Package as torch tensors + entity_names list + metadata; torch.save to `E_concept.pt` atomically (tmp + os.replace).
8. Round-trip verify: reconstruct dense[i, :] for 100 random entity indices via `np.zeros(n_dim); dense[active_indices[lo:hi]] = signs[lo:hi]`; assert bit-identical with input.
9. Query benchmark: 10 self-similarity queries (query = dense[i] for random i); vectorized sparse cosine via `np.bincount(row_ids, weights=signs * q[active_indices])` normalized by `sqrt(nnz_i) * ||q||`. Assert self-similarity >= 0.999.
10. Extrapolate SMOKE bytes to FULL for H1 SMOKE band.

## Source signature

- Input mechanism: Step 1 concept encoder, MEASURED@Step1_SMOKE_metrics sha256 stamped in Step 2 output.
- Format: sparse-bipolar CSR v1 (int16 indices + int8 signs + int64 offsets). Human-readable format_notes serialized inside `.pt`.
- No trainable parameters at Step 2 (deterministic format conversion).

## Functional requirement decomposition (per META_RULE §15E)

- FR1: Encode Step 1's dense int8 into sparse CSR without any bit loss.
  Primitive: numpy scatter/gather + np.nonzero. Deterministic; no HD algebra.
- FR2: Output file <2 GB.
  Primitive: per-entity sparse bytes formula THEORETICAL@ 254 bytes; extrapolate SMOKE actual.
- FR3: Sparse cosine query <500ms wall over 970K entities.
  Primitive: np.bincount vectorized dot accumulation.
- FR4: Round-trip bit-identical for arbitrary sample entity.
  Primitive: reconstruct dense from sparse then np.array_equal.

## SMOKE-vs-FULL code path

SMOKE (n_entities <= 1000, from `substrate_concept_encoder_v1_smoke/encoder.npz`): identical code path -- load npz, nonzero+bincount, torch.save, round-trip 100 samples, 10 queries. Extrapolates SMOKE bytes to FULL for H1 band evaluation.

FULL (n_entities=970069, from `substrate_concept_encoder_v1/encoder.npz`): same code path; H1 evaluated on actual output bytes.

## Hypotheses + pass bands

### H1: Output size <2 GB
- **HP:** FULL `pt_bytes < 2 GB` (SMOKE: extrapolated <2 GB)
- **MB:** `pt_bytes in [2 GB, 4 GB)`
- **HF:** `pt_bytes >= 4 GB`

### H2: Coverage complete
- **HP:** `sparse_nonzero_rows / step1_nonzero_rows >= 0.9999` (bit-loss impossible by construction; guards against int16 overflow if n_dim>32767)
- **HF:** coverage < 0.9999

### H3: Round-trip fidelity
- **HP:** 0 mismatches / 100 samples (bit-identical)
- **HF:** any mismatch

### H4: Query speed
- **HP FULL:** `query_mean_ms < 500` for 10 queries × 970069 entities
- **HP SMOKE:** `query_mean_ms < 100` for 10 queries × 1000 entities (scaled)
- **MB:** at or above HP threshold (not HF; slow doesn't mean broken)

## Pre-reg required fields (SCHEMA-VET checklist)

- `cardinality_ok: True` -- EXPECTED_N_UNITS = 1 (single cell producing single artifact). Cardinality-checked at completion by asserting `sparse_rep["n_entities"] == concept_hds.shape[0]`.
- `arms_differ_verified: N/A_single_arm` -- artifact-producer + fidelity gates; no discriminator arms.
- `final_metrics_atomicity: "tmp_replace"` -- metrics.json AND E_concept.pt written via `os.replace`.
- `crlb_n/a: "artifact-producer; no quantitative discriminator threshold. H3 tolerance = 0 by design (bit-identical); no floor-to-band conversion possible."`
- `discriminator_reachability: True` -- H1-H4 all measurable at cell exit.
- `baseline_in_band: N/A_no_baseline` -- artifact-producer + fidelity gates.
- `calibration_check: "default_ok_for_this_regime"` -- k_sparsity is inherited from Step 1; Step 2 is lossless format conversion; no calibration knobs.
- `sweep_alignment_verdict: N/A_no_sweep`.
- `discriminating_fraction: N/A_no_sweep`.
- `composition_edges:` [`step1_encoder.npz -> np.nonzero_bincount -> sparse_CSR -> torch.save`, all SHAPE_MATCH; no adapters needed]
- `positive_control_arms: []` -- no prior chain-grade primitive being reproduced (mechanism is deterministic format conversion; H3 bit-identity is the invariant).
- `functional_requirements:` FR1/FR2/FR3/FR4 above.
- `cell_chunked: False` -- single-seed (seed=7) artifact-producer cell.
- `start_marker_written: True` -- `_start_marker.json` at main() entry.
- `crash_diagnostic_present: True` -- outer try catches Exception (not BaseException) and writes CELL_CRASHED metrics.json via `_write_crash_metrics`.
- `heartbeat_present: True` -- `_heartbeat.jsonl` emitted at each of 4 stages (loaded_step1 / converted / round_tripped / saved).
- `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "line_buffered_stdout"` + explicit `flush=True` on all progress prints. Cadence: sub-second at SMOKE; per-second-order at FULL (all print sites are pre/post major numpy ops).
- `run_mode_declared: "smoke_then_full"` -- SMOKE dispatch first (this ship); FULL dispatch deferred until Step 1 FULL lands.

## Wall-time estimates

- SMOKE (1000 entities, 4096 dim): np.nonzero + bincount ~ ms; torch.save ~ 100 ms; 100 round-trips ~ 50 ms; 10 queries at N=1000 ~ 20 ms. Total ~ 5-10 s wall; well under queue_add SMOKE gate cap of 180s. Timeout: --timeout 300 for local dispatch (defense margin).
- FULL (970069 entities): np.nonzero + bincount ~ 5-10 s; torch.save (~250-450 MB) ~ 5-15 s; 100 round-trips ~ 100 ms; 10 queries at N=970069 ~ 500-2000 ms total. Total ~ 30-120 s wall. Timeout: --timeout 1800 (30 min; generous defense).

## Off-disk verify (post-smoke gates)

- `data/exp_encoder_migration_step2_sparse_encode_970K_KB_v1_smoke/metrics.json` exists with H1/H2/H3/H4 all HP.
- `data/substrate_concept_encoder_v1_smoke/E_concept.pt` exists.
- `pt_bytes` at SMOKE tracks THEORETICAL 254 bytes/entity + names overhead.
- `round_trip_mismatch == 0`.
- `query_mean_ms < 100` at SMOKE.
- Extrapolated FULL bytes < 2 GB (H1 SMOKE).

Only after ALL five gates pass does FULL dispatch fire (when Step 1 FULL lands).

## Post-FULL Skunkworks gates (surfaced in report; NOT Step 2's job)

- Landed-VET on E_concept.pt (verify pt_bytes < 2 GB actual).
- Sanity self-query on 10 randomly picked entities: cosine([entity], sparse_rep) at self-position >= 0.999.
- Retrieval-quality claim explicitly deferred to Step 3.

## Framing at SMOKE

Advisory-only sparse-encoding fidelity check. Nothing about semantic quality is claimed. H3 bit-identity is a correctness gate; H1 size + H4 query speed are operational engineering targets.

## References

- Migration plan: `notes/design_substrate_KB_bag_word_to_concept_encoder_migration_plan_2026-07-02.md` §Step 2.
- Step 1 cell: `experiments/exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1_core.py`.
- Step 1 SMOKE output: `data/substrate_concept_encoder_v1_smoke/encoder.npz` MEASURED@`data/exp_encoder_migration_step1_..._smoke/metrics.json:encoder_sha256=28c87075617fa1bf...`.
- Step 1 pre-reg: `preregs/2026-07-04_encoder_migration_step1_train_concept_encoder_970K_KB_v1.md`.
- USER strategic direction 2026-07-04 00:47Z "FULL SPEED FULL AUTO" for encoder migration.

ASCII-only. No emojis. No em dashes.
