# Prereg: substrate_wm_multibank_K_cliff_phase_diagram_v1

**Date:** 2026-06-28
**Author:** exp_dev (chunked sibling cell trio)
**Cells:**
- `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1.py`
- `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_13_v1.py`
- `experiments/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_19_v1.py`
- Base infra fork: `exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3.py`
**Anchor (per seed):** `substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_<7|13|19>`

## Scientific question
Layer-1 phase diagram for working memory multi-bank K-cliff. Prior chain-grade: K=4096 (rail), K=8192 (`MULTI_128x`, 3-seed). Prior single-seed: K=8192. Prior cliff between K=16384 (PARTIAL) and K=32768. Layer-2 phase operations need cliff data per (K, bank_overlap, routing_noise) tuple.

## Sweep axes
- **K (PRIMARY, 5 points):** {4096, 8192, 16384, 32768, 65536}
- **bank_overlap (secondary, 3 points):** {0.0, 0.1, 0.3} — fraction of dims shared between adjacent bank_tags (perturbation of bank_tag basis off-orthogonal)
- **routing_noise (tertiary, 3 points):** {0.0, 0.05, 0.15} — additional bipolar noise added to routing cue (degrades route_acc)
- Full grid per seed: 5 x 3 x 3 = **45 points**.
- Smoke corners (per seed): 5 = {(K=4096, ov=0.0, rn=0.0), (K=65536, ov=0.0, rn=0.0), (K=4096, ov=0.3, rn=0.15), (K=65536, ov=0.3, rn=0.15), (K=16384, ov=0.1, rn=0.05)}.

## Arms (per (K, overlap, noise) point)
1. **SUBSTRATE**: multi-bank WM with k_per_bank=64 envelope, cleanup-twice over codebook (the chain-grade mechanism from v3 base).
2. **RANDOM**: random vector floor — substrate writes nothing; cleanup retrieves a random codebook row. Expected top1 = 1/CB = 1.5e-5.

Arms must differ at EACH point (META_RULE_AF).

## CRLB pre-validation (computed in Python BEFORE this prereg)
- Bank-routing SNR: `0.70 * sqrt(N) / sqrt(n_banks)` where n_banks = K/64.
  - K=4096:  snr=7.92  (route saturates ~1.0)
  - K=8192:  snr=5.60  (route saturates ~1.0)
  - K=16384: snr=3.96  (route ~1.0)
  - K=32768: snr=2.80  (route ~0.99)
  - K=65536: snr=1.98  (route ~0.97; degrades with routing_noise + overlap)
- Cleanup-1 SNR per dim: `1/sqrt(k_per_bank-1) = 0.126`. Two cleanups make 0.95+ recall feasible at K<=8192; for K=65536 + overlap=0.3 + rn=0.15 we expect cliff.
- RANDOM floor: top1 = 1/65536 ≈ 1.5e-5.

## VRAM pre-validation (computed in Python BEFORE this prereg)
- Estimated eval peak (fp16, CB=65536, N=8192, k_per_bank=64):
  - K=4096:  1.61 GB
  - K=8192:  2.15 GB
  - K=16384: 3.23 GB
  - K=32768: 5.38 GB
  - K=65536: 9.68 GB
- Cell uses v3's VRAM probe gate (`HP_VRAM_PROBE_FRACTION=0.85`). On a <12GB GPU the K=65536 unit may be probe-denied; this is **correct cliff detection**, not a bug.

## PASS bands (HARD_PASS, per seed)
For at least 3 of 5 K values at (overlap=0.0, routing_noise=0.0) baseline corridor:
- SUBSTRATE recall >= 0.50
- SUBSTRATE - RANDOM > 0.20 (discriminator)
- arms_differ_sha256 distinct (META_RULE_AF)

Per-seed HARD_PASS aggregates to a 3-seed envelope when Skunkworks aggregates the chunked siblings.

## MIDDLE_BAND
- Discriminator holds at K<=16384 but cliffs at K>=32768 across overlap/noise; or
- Phase-diagram MAP returns coherent cliff structure (cliff K monotone in overlap+noise) but absolute SUBSTRATE recalls in [0.30, 0.50).

## HARD_FAIL bands
- `HARD_FAIL_CARDINALITY_BREACH` (META_RULE_H): n_units_observed != EXPECTED_N_UNITS (smoke=10 [5 pts x 2 arms]; full=90 [45 pts x 2 arms]).
- `HARD_FAIL_UNIT_EXCEPTION`: any unit raises (no silent-except per META_RULE_AN); HP_VRAM_PROBE_BREACH is NOT a failure — it is the cliff itself.
- `HARD_FAIL_ARMS_IDENTICAL`: SUBSTRATE and RANDOM identical hashes anywhere.
- `HARD_FAIL_SATURATION_ONLY`: every point at SUBSTRATE >= 0.995 (no cliff observed; need larger K_max).
- `HARD_FAIL_FLOOR_ONLY`: every point at SUBSTRATE <= RANDOM + 0.05 (mechanism broken at smoke).
- `HARD_FAIL_LLM_CALL`: `_LLM_CALL_COUNTER[0] != 0` (substrate-only gate).

## Smoke gate (must pass BEFORE full dispatch)
1. 5 corner points all ran (no silent except).
2. At least 2 points discriminate (SUBSTRATE - RANDOM > 0.20).
3. At least 1 point saturates (low-K low-noise corner: K=4096 ov=0.0 rn=0.0 expected ~1.0).
4. At least 1 point fails (high-K high-noise corner: K=65536 ov=0.3 rn=0.15 expected cliff OR VRAM-probe denial).
5. GPU util p50 >= 50%.
6. cardinality_ok = True (n_units=10).
7. arms_differ_sha256 distinct.

## Disciplines (load-bearing)
- META_RULE_AC (substrate-empirical baseline): substrate ~3.7x more capable than cone-formula at N=8192 — discriminator margin 0.20 already empirically justified by prior K=8192 chain-grade.
- META_RULE_AE: pre-reg HARD_PASS/MIDDLE/HARD_FAIL bands before dispatch.
- META_RULE_AF: arms must differ.
- META_RULE_AG: corpus_provenance + allow_synthetic recorded in metrics.
- META_RULE_AH: atomic-write partials (.tmp + os.replace via _seed_checkpoint).
- META_RULE_AN: no silent except; record + halt OR re-raise.
- Discriminator-must-survive-scale (USER 2026-06-26): smoke uses 5 corners at FULL N_DIM=8192 (NOT scaled-down N); the discriminator is the cliff structure, validated at full scale in the smoke corners.

## Functional-requirement decomposition
- **F1 mechanism end-to-end:** smoke corners all run (cardinality_ok=True; no exceptions/probe-denials at low-K low-noise corner).
- **F2 discriminator:** SUBSTRATE - RANDOM > 0.20 at >= 2 smoke corners (low-K corner pairs).
- **F3 cliff observable:** at least 1 corner saturates AND at least 1 corner fails or probe-denies.
- **F4 substrate-only:** `_LLM_CALL_COUNTER[0] == 0`.
- **F5 GPU utilization:** smoke `gpu_util_p50 >= 50%` (Fix #24 NON-NEGOTIABLE).
- **F6 phase-coherence:** in full, cliff K monotone in (overlap+noise) — higher overlap+noise => lower cliff K.

## Output schema (`metrics.json`)
- `per_unit`: each entry has `{seed, K_total, bank_overlap, routing_noise, regime (SUBSTRATE|RANDOM), recall, route_acc, peak_mem_mb, wall_s, ...}`.
- `phase_map`: list of `{K, bank_overlap, routing_noise, top1_substrate, top1_random, arms_differ_sha256, verdict_tier (PASS|MIDDLE|FAIL|CLIFF), saturation (bool), cliff_marker (bool)}`.
- `headline`: K-cliff location per (overlap, noise) tuple (highest K where SUBSTRATE >= 0.50).

## Dispatch plan
- Smoke (1 seed: seed_7; 5 corner points): if local has CUDA, run local; else route via Orchestrator to `overnight_queue` GPU. Timeout 1800s.
- Full (3 sibling cells, each 1 seed x 45 points): dispatch via Orchestrator to `overnight_queue` GPU each at 18000s timeout (45 points x ~3-5 min). Parallelizable across remote slots.
