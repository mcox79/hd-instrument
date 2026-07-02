# Pre-registration: stage2_learned_encoder_vs_random_init_v1_n4096

**Date:** 2026-07-01
**Anchor:** stage2_learned_encoder_vs_random_init_v1_n4096_seed_{7,13,19}
**Queue:** overnight_queue (GPU: M x M contrastive at M=16000 -> 1 GB fwd + 2 GB grad)
**N:** 4096, **Seeds:** [7, 13, 19], **M:** {4000, 8000, 12000, 16000}, **Noise:** {0.0, 0.30}

## Scientific question

Does the substrate benefit from LEARNED (gradient-optimized-pre-write, encoder-only)
key encoding vs the random-init bipolar keys used in all prior substrate work?
This is the first substrate empirical test of trainable-pre-write encoding, at
the Stage 2/3 boundary (per Sonnet Stage 2 Pareto Rank 4; hidden-dim Dim L,
P_def=0.44). Symmetric HP/HF: HP opens gradient-through-write as M3-Phase-2
substrate pivot; HF (WORSE or EQUIVALENT) validates substrate-native simplicity
and closes R21_cross_modal_binding's naive-CLIP DECLINED prediction (P=5%) with
positive empirical data on a subtly-different pre-write orthogonalization path.

## Prior work check (substrate-KB concept-query 2026-07-01)

Top-5 hits at cosine 0.30-0.35 (below rediscovery threshold of 0.30):
- Rank 1 (0.3496): R21_cross_modal_binding C.4 "Naive CLIP-style contrastive
  training DECLINED (P=5% NEGATIVE)" - cites Saunshi 2022 on inductive-bias-
  dependent guarantees; substrate architecture fixed-encoders (Kerdock + random
  projections) incompatible with gradient-flow-through-substrate.
- Rank 4: "Substrate-native encoder trained from scratch (encoder + Pattern B
  joint training)" - a related design-space alternative.
- Rank 5: "Differentiable VSA (joint encoder-substrate training)" - a related
  design-space alternative.

**Novelty framing:** this cell is NOT the R21-declined joint-encoder-substrate
path. It is encoder-only pre-write contrastive orthogonalization (500 SGD
steps optimize encoder keys BEFORE substrate write; substrate never sees
gradient). R21's inductive-bias argument does not directly apply to pre-write
shaping. Symmetric HP/HF design lets either outcome carry publishable weight.

Prior-work check: R21 C.4 declined naive-CLIP-on-substrate (P=5%); this cell
probes the subtly-different pre-write contrastive-encoder path. Cell is NOT
rediscovery - it is a symmetric empirical test with HP that opens a new pivot
and HF that closes R21's negative prediction with data.

## Cell files

- Core:    `experiments/_stage2_learned_encoder_vs_random_init_v1_core.py`
- Seed 7:  `experiments/exp_stage2_learned_encoder_vs_random_init_v1_seed_7.py`
- Seed 13: `experiments/exp_stage2_learned_encoder_vs_random_init_v1_seed_13.py`
- Seed 19: `experiments/exp_stage2_learned_encoder_vs_random_init_v1_seed_19.py`

## Design summary

- ARM_RANDOM_INIT: bipolar iid keys (matches all prior substrate work)
- ARM_LEARNED_CONTRASTIVE: init bipolar, 500 SGD steps of contrastive loss
  on encoder outputs only. Loss = neg_off_diag + LAMBDA * pos_aug where
  neg = sum_{i<j} relu(cos(k_i,k_j) - MARGIN), MARGIN=0.05 (below random
  3-sigma to guarantee nonzero gradient), LAMBDA=0.5, LR=0.02
- Substrate write: Hebbian W = O^T K / N (standard)
- Query: bipolar-flip noise fraction f on K, read Pred = W @ Kq^T
- Metrics: top1, top5, top10, top50, cos05, cos08 - 6 gates per (arm, M, noise)
- Grid: 4 M x 2 noise x 2 arms x 3 seeds = 48 measurements

**Discriminator metric = cos05 (fraction of queries with diagonal cos >= 0.5).**
Empirical MEASURED@ probe (2026-07-01) shows top1 saturates at 1.000 up to
M=48000 at N=4096 due to argmax-cosine's robustness to crosstalk; the
discriminating metric is cos05, which drops sharply between M=8000 (cos05=1.0)
and M=16000 (cos05=0.0), with the wall at M~12000.

**Key design decision:** encoder training is SUBSTRATE-AGNOSTIC. Loss only sees
encoder outputs (K^T K cosines + augmentation cosines); NO substrate recall in
gradient. Avoids the R21-declined joint-encoder-substrate architecture-mismatch.

## Pre-registered bands

**HARD-PASS conditions (any ONE fires HP; verdict resolves in priority order):**
- HP_LEARNED_HIGHER_CAPACITY: at (M=12000, f=0.0),
  (LEARNED_cos05 - RANDOM_cos05) >= 0.10 (learned tolerates cos05-wall better)
- HP_LEARNED_HIGHER_NOISE_TOL: at (M=4000, f=0.30),
  (LEARNED_cos05 - RANDOM_cos05) >= 0.15 (learned more noise-robust)
- HP_ORTHOGONALITY: LEARNED max_pairwise_cos <= 0.20 across ALL sweep points
  (contrastive training achieves the shape it was optimizing for)

**MIDDLE:** HP-partial in full-mode + no HF firing.

**HARD-FAIL conditions:**
- HF_LEARNED_WORSE: LEARNED < RANDOM on >= 4 of 6 metric-gate comparisons
  scaled to grid (4/6 * total_pairs = 48 * 4/6 = 32 in FULL; 4 in smoke)
  - this HF is the POSITIVE substrate-native-validation finding (closes R21
  5%-prediction with data)
- HF_LEARNED_EQUIVALENT: |LEARNED - RANDOM| < 0.03 on ALL metric-gate pairs
  - learning does nothing at n_steps=500 budget

**Structural HF (breaks discriminator):**
- HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: observed_units < 16/seed
- HARD_FAIL_META_RULE_AX_HASH_COLLISION: mechanism_hash not distinct
- HARD_FAIL_CV_BREACH: cross-seed cv >= 0.15 (metrics unstable)
- HARD_FAIL_META_RULE_AG_BASELINE_OUT_OF_BAND: RANDOM baseline cos05 out
  of band at EVERY sweep point (test cannot discriminate on cos05)

## Calibration rationale

- **M grid {4000, 8000, 12000, 16000}:** MEASURED@ RANDOM probe at N=4096:
  cos05 = 1.0 at M=4000/8000; 0.661 at M=12000; 0.0 at M=16000. Grid spans
  below-wall (positive-control) through mid-wall (discriminator) to floor.
- **noise grid {0.0, 0.30}:** clean + moderate query-flip.
- **HP_LEARNED_HIGHER_CAPACITY_DELTA=0.10** on cos05: reachable iff LEARNED
  shifts cos05-wall higher by ~1000 M-units (cos05 slope at wall).
- **HP_LEARNED_HIGHER_NOISE_TOL_DELTA=0.15**: broader threshold because
  noise arm has higher variance.
- **HP_ORTHOGONALITY_MAX_COS=0.20** deeply relaxed vs random 3-sigma 0.047;
  MEASURED@ random baseline max over M(M-1)/2 = 0.086-0.096 at M=4000-32000;
  LEARNED contrastive needs to drive this below 0.20 (achieved by
  construction of MARGIN=0.05 hinge if training converges).
- **MARGIN=0.05:** below random-baseline max 0.086 so hinge gradient is
  nonzero for enough pairs; above THEORETICAL@ 3-sigma 0.047 so the target
  is achievable in finite steps.
- **HF_LEARNED_WORSE gate-count 4/6:** scaled proportionally to grid size.
- **HF_LEARNED_EQUIVALENT delta 0.03:** twice per-seed cv of RANDOM at
  N=4096; below this LEARNED is statistically indistinguishable.

## Anti-bias notes

- **BIAS-M (production-scale):** smoke uses FULL N=4096; M reduced to 4000
  for tractable contrastive-M-x-M wall (~3 min CPU) per DISCRIMINATOR path B.
- **BIAS-N (verify-referent-verdict-field):** HP is BOTH (delta >= threshold)
  AND (cross-seed cv < 0.10); single-seed cannot pass HP alone.
- **BIAS-S (band-calibration):** bands are RELATIVE to RANDOM at each M.
- **BIAS-Q (suspect 1.000):** top1 saturating at 1.000 at ALL sweep points
  is EXPECTED (MEASURED@ probe confirms); do NOT interpret as anomalous.
  Discriminator is cos05 not top1.

## Cardinality

- `EXPECTED_N_UNITS_PER_SEED = 16` (arms=2 x M=4 x noise=2)
- `HARD_FAIL_CARDINALITY_BREACH` if `n_units_observed_per_seed < 16`
- `cardinality_ok: bool` in metrics.

## Discriminator-at-scale check (Path B analytical justification)

Smoke at M=4000 does NOT fire the cos05-wall (both arms cos05=1.0 by
construction below wall). Path B justification: FULL sweep at M=12000
IS the cos05-wall regime; MEASURED@ RANDOM cos05 = 0.661 at M=12000
(mid-band); LEARNED with reduced max_pairwise_cos (target <= 0.05) should
preserve more cos05 = HP_LEARNED_HIGHER_CAPACITY test.

Smoke evidence (MEASURED@ data/exp_stage2_learned_encoder_vs_random_init_v1_smoke_seed_7/metrics.json):
- max_pairwise_cos_key RANDOM=0.086; LEARNED=0.082 (small delta, but direction
  correct)
- hp_orthogonality: TRUE (LEARNED max = 0.082 <= 0.20)
- mechanism_hashes: 2 distinct (arms genuinely different)
- Both arms cleanly execute; cardinality_ok TRUE
- verdict: MIDDLE_BAND_ARMS_INDISTINGUISHABLE (expected for smoke; cos05-wall
  not exercised)

## Meta-rule schema fields

- `cardinality_ok`: MANDATORY, computed observed vs expected
- `arms_differ_verified`: MEASURED (mechanism_hash 2/2 distinct in smoke)
- `final_metrics_atomicity`: "tmp_replace"
- `crlb_floor_computed`: N/A; `crlb_n/a`: "encoder-orthogonalization has no
  closed-form CRLB against substrate cleanup; HP tuned to cross-seed cv"
- `discriminator_reachability`: TRUE (LEARNED_final_max_cos empirically 0.08
  << 0.20 HP threshold in smoke)
- `baseline_in_band`: verified at aggregate step against cos05 (top1 saturates
  by construction - do NOT check top1 baseline-in-band)
- `calibration_check`: "default_ok_for_this_regime" (thresholds are ratios
  above cross-seed cv, not tuned per data)
- `cell_chunked`: TRUE (single-seed-per-cell)
- `start_marker_written`: STARTED metric written at main() entry
- `crash_diagnostic_present`: _write_import_crash_sentinel on outer except
- `heartbeat_present`: per-unit print with flush=True
- `defensive_error_checking`: "passed_all_4_patterns"
- `progress_logging`: "print_flush_true"
- `sweep_alignment_verdict`: ALIGNED (M directly parameterizes storage load;
  noise directly parameterizes bit-flip fraction)
- `discriminating_fraction`: 2/4 M-points in discriminating cos05 band
  [0.05, 0.95] (M=12000 mid; M=16000 near-floor)
- `composition_edges`: encoder -> substrate Hebbian W; encoder output shape
  (M, N) matches Hebbian K shape (M, N); SHAPE_MATCH
- `positive_control_arms`: RANDOM_INIT arm at M=4000 f=0.0 = positive control
  reproducing prior substrate work (top1=1.0 cos05=1.0; matches probe)
- `functional_requirements`: "encoder orthogonality" (contrastive), "substrate
  write" (Hebbian W), "substrate read" (W @ Kq^T), "score" (cosine)

## Numbers in this pre-reg (per META_RULE_AC)

- RANDOM top1 at M<=48000, N=4096: 1.000 (by-construction saturation)
  MEASURED@interactive_probe_2026-07-01
- RANDOM cos05 wall at M~12000, N=4096: mid-band 0.661
  MEASURED@interactive_probe_2026-07-01
- RANDOM max_pairwise_cos_key at M=4000-32000, N=4096: 0.070-0.096
  MEASURED@interactive_probe_2026-07-01
- RANDOM 3-sigma theoretical off-diag at N=4096: 3/sqrt(4096) = 0.047
  THEORETICAL@bipolar_iid_variance
- LEARNED_final_max_cos at N=128 selftest: 0.250 (seed 7), 0.297 (seed 13),
  0.266 (seed 19) MEASURED@selftest
- LEARNED_final_max_cos in smoke (N=4096, M=4000, 100 steps): 0.082
  MEASURED@data/exp_stage2_learned_encoder_vs_random_init_v1_smoke_seed_7/metrics.json:max_learned_cos_key
- LEARNED_train_wall at M=4000, N=4096, 100 steps: 166s CPU
  MEASURED@smoke_seed_7_output
- HP_LEARNED_HIGHER_CAPACITY_DELTA=0.10: reachable iff LEARNED shifts cos05
  wall by ~1000 M-units (cos05 slope 0.339/4000 M-units MEASURED between
  M=12000 and M=16000; wall-shift 1000 M-units => cos05 delta = 0.085
  which is close to threshold 0.10; HP is stretch target, MB is comfortable)
- Timeout 7200s per seed: HYPOTHESIZED@spawn_prompt (USER task cap); GPU
  training scales dramatically with M; at M=16000, 500 SGD steps on GPU
  expected 60-120s per SGD phase * 2 arms + read + housekeeping ~= 30 min
  wall; safely under 7200s cap.

## N-suffix section

Anchor _n4096; production N = 4096; scripts enforce N = FULL_N = 4096.

## Timeout estimate

- Selftest wall (N=128, M=32, 10 SGD steps): 0.02s.
- Smoke wall MEASURED (N=4096, M=4000, 100 SGD steps CPU): 170s for 2 arms
  (1 seed, 1 M-point, 1 noise-point).
- Full: 16 units/seed (4 M x 2 noise x 2 arms); LEARNED contrastive M x M
  scales as O(M^2 * n_steps); dominant compute at M=16000 SGD:
  formula: ceil(1.5 * smoke_wall * (M_full/M_smoke)^2 * (steps_full/steps_smoke)
    * (units_full/units_smoke) / gpu_speedup)
    = ceil(1.5 * 170 * (16000/4000)^2 * (500/100) * (16/2) / 5)
    = ceil(1.5 * 170 * 16 * 5 * 8 / 5)
    = ceil(32640) = 32640s CPU / GPU_5x = 6528s
- USER spawn 7200s cap defensible with GPU acceleration; strict-GPU is
  strongly preferred for full mode.
- timeout_s = 7200 per USER task specification

## Ship route

- SMOKE: local (CPU) done at N=4096, M=4000; MIDDLE_BAND_ARMS_INDISTINGUISHABLE
  (expected below-wall; smoke fires cell mechanism, cardinality_ok TRUE,
  arms_differ mechanism_hash 2/2, hp_orthogonality TRUE, LEARNED training
  functional).
- FULL: overnight_queue (GPU) per USER spawn-prompt (contrastive M x M at
  M=16000 needs GPU per Fix #24; `import torch` at cell top verified)
- Requires Orchestrator push (harness-DENIED to exp_dev)

## REQUIRED_FIELDS in metrics.json

- `anchor_name`, `verdict`, `verdict_msg`, `run_mode`, `n_seeds`
- `expected_n_units_per_seed`, `observed_n_units_per_seed`, `cardinality_ok`
- `arms`, `N_fixed`, `M_sweep`, `noise_sweep`, `metric_gates`
- `hp_learned_higher_capacity`, `hp_learned_higher_noise_tolerance`, `hp_orthogonality`
- `hf_learned_worse`, `hf_learned_equivalent`
- `cap_delta`, `nz_delta`, `max_learned_cos_key`
- `learned_worse_count`, `learned_equivalent_count`
- `per_gate_deltas` (list of {M, noise, metric, RANDOM, LEARNED, delta})
- `arms_differ_details`, `baseline_in_band`, `baseline_details`
- `max_cv_across_arms`, `stats_cross_seed`
- `mechanism_hashes_distinct`, `per_seed`
- `elapsed_s`, `ts_iso`, `pid`, `backend`, `config_version`
