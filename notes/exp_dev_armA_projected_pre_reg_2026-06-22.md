# exp_dev PRE-REG: exp_armA_projected_key_revival_v1 (Path C angle 4 discriminator)

**Date:** 2026-06-22
**Author:** exp_dev (Prover)
**Routed by:** Research (Director) via `notes/research_to_all_ROUTE_NEGATIVE_arm_A_sparse_superposition_fail_revival_drill_2026-06-21.md` angle 4
**Cell source:** `experiments/exp_armA_projected_key_revival_v1.py`
**Queue:** local_cpu_queue
**Estimated wall:** ~44 min full (3 seeds x ~14.7 min/seed; encode-dominated)

## QUESTION (single discriminator)
Does sparse-fan-in + kWTA + superposition (ARM A) rescue dense storage when applied to **CERT 591-style contrastively projected keys**? The 4-arm cell (commit fc3b8771) showed ARM A fails at smoke (~0.04 recall, but on undertrained projection: TRAIN_M=600 / 200 steps on pythia-160m). This cell strengthens the projection (TRAIN_M=2500 / 600 steps, matching CERT 591's per-M scale) and adds a TRUE raw-keys ARM A control that was missing from 4-arm.

## HONEST SCOPE
- Encoder: pythia-160m (CPU; CERT 591 used 2.8b GPU). The discriminator question is "does projection help ARM A relative to raw, at meaningful M?" — encoder choice affects absolute numbers but the relative lift test is valid on 160m.
- This is a Path C revival drill, not a chain-grade cert. Cheap-fast over thorough.

## HONEST SURPRISE FROM SMOKE (load-bearing for VET)
The 4-arm cell ALREADY uses contrastive projection (`Kp_all = K[ho] @ W` line 114 of `exp_anisotropy_rescue_4arm_sweep_v1_gpu.py`). The original "ARM A failed on RAW keys" framing in Research's routing note is technically incorrect — ARM A in the 4-arm cell ran on already-projected keys (just an undertrained projection at smoke). The discriminator value of THIS cell is in:
  (a) stronger CERT 591-strength projection (TRAIN_M=2500/600 steps vs smoke 600/200)
  (b) explicit raw-keys ARM A control (NEW; was absent in 4-arm)
  (c) noise sweep sigma in {0, 0.1, 0.3} (4-arm fixed at 0.1)
  (d) shuffled-projection CAN-FAIL control (NEW; validates projection isn't memorizing alignment)

## PRE-REGISTERED BANDS

**HARD_PASS (discriminator: storage-chain item #3 has TWO paths):**
- Worst (M=10k, sigma in {0, 0.1}) ARM A on PROJECTED keys recall >= 0.60
- AND max cv across seeds <= 0.10 (seed-stable per Skunkworks discipline)
- AND shuffled-proj-ctrl recall <= 5x chance (1/256 = 0.0039 -> <= 0.0245; control is sane)

**HARD_FAIL (discriminator: tag-retrieval CLASS is the only path):**
- Max ARM A on projected keys recall at M=10k clean < 0.20
- OR shuffled-proj-ctrl recall > 5x chance + 0.05 (control-invalid; can't trust result)

**MIDDLE_BAND:**
- Clean recall in [0.20, 0.60) -> partial mechanism, characterize.

## METRICS SCHEMA (Skunkworks's per-unit-instrumentation discipline)
- `per_unit`: 1 entry per seed; each contains `by_cell` dict keyed `M<M>_sig<sigma>` with `recall_armA_projected`, `recall_armA_raw_control`, `recall_armA_shuffled_proj_ctrl`, `B_storage_bits_per_mem_{proj,raw}`, `M`, `sigma`.
- `detail.by_cell_agg`: 1 entry per (M, sigma) across seeds; mean/std/cv + lift_proj_over_raw.
- `detail.honest_scope`: encoder caveat + raw control definition.
- `substrate_only_decode_gate`: "N/A (KV-storage cell, not LM cell)" — explicit documentation for Skunkworks's audit so the gate-missing check doesn't false-positive.
- REQUIRED_FIELDS (queue_add validates): `verdict`, `verdict_msg`, `elapsed_s`, `summary` (all present).

## SELFTEST + SMOKE RESULT (smoke is GREEN; harness validated)
- Selftest PASS: anisotropic synthetic ARM A collapses (0.01); isotropic decode-meter holds (1.00).
- Smoke (1 seed, M=1000, sigma=0.0, TRAIN_M=600/150 steps): armA_proj=0.025, armA_raw=0.013, armA_shuf=0.009. armA_proj is in the same ~0.02-0.05 range as 4-arm's smoke armA=0.041 at M=1000 -- harness matches the 4-arm baseline.
- The smoke is GREEN as a HARNESS check, NOT as the science. The projection at smoke scale (160m, TRAIN_M=600, 150 steps) is essentially non-functional (PROJ value-cue recall sanity = 0.045 vs CERT 591 full 0.83+). Full run uses CERT 591-style training scale (TRAIN_M=2500, 600 steps); only the full result is the discriminator.
- Smoke wall: 109s (encode 105s; train 1.9s; arms ~2s). Full extrapolated: encode 12500/1600 * 105 = 820s/seed + ~30s train + ~30s arms = ~880s/seed * 3 seeds = ~44 min.

## ESTIMATED RUNTIME (cell-author HONEST measurement, not guess)
- Smoke MEASURED: 109s total wall (1 seed, 1600 facts encoded, 1 M, 1 sigma).
- Full MEASURED-EXTRAPOLATED: ~44 min (3 seeds; encode 12500 facts each; encode scales linearly in #facts dominantly; arms scale O(M*d') quickly).
- Timeout recommend: 7200s (2 hr; 2.7x cushion over extrapolated wall; cell is checkpointed per-seed so partial loss is bounded to 1 seed if killed).

## VET-RELEVANT GUARDS BAKED IN
- Per-seed CONFIG_VERSION-gated checkpoint (smoke partials WILL NOT be loaded by full per PROT-021 via `_seed_checkpoint.aggregate_partials(run_config=...)`).
- ASCII-only.
- Path-scoped commits.
- All randomness from `np.random.default_rng(seed)` + per-(M,seed) sub-generators.
- Pause flag re-checked (none active).
- ARM A logic verbatim-shape from 4-arm cell (`_kwta`, `_sparse_fanin`, decode argmax cosine) -- reproducible.

## CITES
- Research routing: `notes/research_to_all_ROUTE_NEGATIVE_arm_A_sparse_superposition_fail_revival_drill_2026-06-21.md`
- 4-arm base: `experiments/exp_anisotropy_rescue_4arm_sweep_v1_gpu.py` (smoke metrics: `data/exp_anisotropy_rescue_4arm_sweep_v1_gpu/metrics.json`)
- CERT 591 contrastive projection: `experiments/exp_kv_learned_projection_v1.py`
- USER STANDING route-negatives (2026-06-20): `feedback_route_negatives_to_research_2x_3x_revival_drills_USER_STANDING_2026-06-20.md`

-- exp_dev
