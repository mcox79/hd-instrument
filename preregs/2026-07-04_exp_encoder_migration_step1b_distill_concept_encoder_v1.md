# Pre-reg: Encoder Migration Step 1b -- Dense-teacher (BGE) distillation into sparse BLOCK-bipolar concept codes, dual-gated (semantic + algebra)

Date: 2026-07-04. Author: exp_dev. Status: PRE-REGISTERED BEFORE FULL DISPATCH.
Cell: `experiments/exp_encoder_migration_step1b_distill_concept_encoder_v1_core.py`
Anchor: `encoder_migration_step1b_distill_concept_encoder_v1` (smoke suffix `_smoke`).
Responds to: `notes/research_drill_concept_encoder_design_correctness_2026-07-04.md`
(rank-1 fix: dense-teacher distillation) as amended by
`notes/research_drill_algebra_preserving_semantic_distillation_2026-07-04.md`
(block codes + SBC algebra + relational objective + semi-hard negatives) and the
design-ablation input (`data/exp_encoder_design_ablation_v1_smoke/metrics.json`,
commit e069ce430: bundle-superposition is the sensitive algebra axis; ~3.1 pct
sparsity dominates 2 pct).

Prior-work check (substrate concept-query, USER-locked): NONE at cosine>0.30
(top hit 0.292 = encoder-family phase-diagram cert ledger). Genuinely novel cell:
no prior BGE-distill -> sparse-block-VSA cell in the arc.

Feasibility probe (MEASURED, band basis):
`notes/cell_design_step1b_distill_feasibility_probe_2026-07-04.md`.

## Hypothesis

A linear student W: R^1024 -> R^N_DIM with block-structured sparsification
(K_BLOCKS blocks, 1 signed active unit per block), trained by relational
similarity-distillation from cached BGE-large teacher embeddings plus InfoNCE with
semi-hard teacher-mined negatives, produces concept codes that (A) preserve BGE
semantic geometry on held-out concepts AND (B) remain fully algebra-grade under
SBC block-local circular convolution composition -- dissolving the semantic-vs-
algebra tension that caps the Step-1 orthographic design at ~0.52.

## Composition algebra decision (drill-mandated explicit field)

`composition_algebra: "SBC_block_local_circular_convolution"` -- the sparse block
code is NOT a valid literal-FHRR atom (not unit-modulus on all dims); binding is
performed block-locally via `hdlab.binding.bind/unbind` (real float path = circular
convolution/correlation per block on [K_BLOCKS, L]-reshaped codes) with random
one-active-per-block signed keys. Rationale: Frady/Kleyko/Sommer 2020 lossless SBC
unbind; empirically reproduced in probe (keyed roundtrip 1.000 at J<=20,
shuffled-key 0.000). The naive top-k + literal-FHRR path is retained ONLY as the
false-win comparison arm (probe: 0.483 roundtrip at J=20).

## Config

- Teacher cache: auto-resolve largest `bge_large_v2_name_*.npz` under
  `data/substrate_index/cached_indices/` (local smoke = 43905-concept cache;
  remote FULL = 177861-concept cache `bge_large_v2_name_177861_d1b9dff5.npz`,
  built by `prebuild_bge_index_cache_gpu_v1`, lives on remote runner). NEVER
  recompute teacher embeddings.
- N_DIM = 4096 (parameterized `--n-dim`). Primary K_BLOCKS = 128 (L = 32,
  sparsity = 128/4096 = 3.125 pct). K_BLOCKS parameterized `--k-blocks`.
  FULL sweeps K_BLOCKS in {64, 128} (rate-transfer question from ablation);
  SMOKE trains primary 128 only (same code path/branches, smaller grid).
  Sparsity rationale: CRLB bound (below) rules out K=64 for the 0.85 GO band;
  3.125 pct is at the proven [0.01,0.03] window edge with fresh ablation
  evidence that ~3.1 pct dominates 2 pct at equal algebra fidelity.
- Split: seeded permutation (seed 7); held-out fraction 0.10 of cache concepts
  (held-out NEVER seen by training; student generalizes to held-out via W applied
  to their teacher embeddings = the deployment path for novel concepts).
  SMOKE: train 3000 + held 800 (subsampled from the local cache).
  FULL: train = 0.9 * 177861 ~ 160075, held ~ 17786.
- Objective: L = 1.0 * RKD(in-batch pairwise-cosine MSE, off-diag)
  + 0.5 * InfoNCE(tau=0.07; positive = teacher top-1 NN; 4 mined semi-hard
  negatives/anchor from teacher-cos band [0.3, 0.6] + in-batch negatives).
  NO absolute-MSE-to-teacher term (drill Q2: false-win trap).
- Sparsifier: per-block argmax straight-through (hard one-hot * sign forward;
  softmax(|z|/tau_g=1.0) + tanh(z) backward).
- Optimizer Adam lr 1e-3, batch 256. SMOKE steps 150; FULL steps 20000.
- Seeds: single seed 7 (torch.Generator + numpy default_rng, fixed). This is an
  artifact-producer + characterization cell with deterministic discriminators
  given the mechanism, not an AUC/confidence cell -> multi-seed smoke rule N/A;
  seed sensitivity deferred to the design-ablation lane.
- Device: `--device auto` (cuda if available else cpu). SMOKE = local CPU only
  (USER-locked SMOKE-only-local); FULL = GPU (overnight_queue via Orchestrator).

## Arms

| arm | role | code | algebra path |
|---|---|---|---|
| BLOCK_K128 | PRIMARY mechanism | block student K=128 | SBC block circconv |
| BLOCK_K64 | FULL-only sweep point | block student K=64 | SBC block circconv |
| TOPK_NAIVE | false-win comparison | unstructured top-k=128 student | literal FHRR + dense phasor keys |
| CHARPOS | Step-1-style honest baseline | orthographic top-k of entity name | (semantic eval only) |
| RANDOM_BLOCK | algebra ceiling / semantic negative control | random 1-per-block signed | SBC block circconv |
| DENSE_SIGN | sparse-vs-dense control (drill Q5 ii) | sign(W_block z), dense bipolar | FHRR (valid dense phasor) |

`HP_SCOPE`: {BLOCK_K128: [G_A, G_B1, G_B2], BLOCK_K64: [] (report-only),
TOPK_NAIVE: [] (comparison), CHARPOS: [] (baseline), RANDOM_BLOCK: [C_pos_control],
DENSE_SIGN: [] (control)}. Chain-grade gates do NOT apply to control/baseline arms.

## Metrics (all on HELD-OUT concepts; every number lands in per_unit records)

Semantic (per arm): spearman_all (rank corr of student vs teacher pairwise cosines,
up to 500K sampled held-out pairs), pearson_all, hi80_cos (mean student cos on pairs
with teacher cos >= 0.80) + hi80_calib_err, ret_agree@10 (top-10 NN overlap vs
teacher within eval codebook).

Algebra (per arm x J in J_grid; J_grid SMOKE {5, 20}, FULL {2, 5, 10, 20}):
- keyed_roundtrip@1: bind(key_j, code_j) summed over J, unbind key_q, cosine-argmax
  cleanup over eval codebook; + mean unbind SNR margin (cos_true - max cos_distractor).
- bundle_recall@J: un-keyed superposition of J codes; per-item top-J recall
  (ablation's sensitive axis).
Controls: shuffled_key hit-rate (BLOCK_K128, J=5; wrong key must give ~chance);
sparse-vs-dense = BLOCK vs DENSE_SIGN bundle curves.

## Bands (FULL; primary arm BLOCK_K128)

- G_A semantic: spearman_all >= 0.85 HARD_PASS; [0.70, 0.85) MIDDLE_BAND;
  < 0.70 HARD_FAIL. (Drill Q5 Metric A bands; floor 0.70, HP is floor + 100 pct
  of band width -> META_RULE_L satisfied trivially.)
- G_B1 keyed algebra (non-negotiable): keyed_roundtrip@1 at J=5 >= 0.95 HARD_PASS;
  [0.90, 0.95) MIDDLE_BAND; **< 0.90 -> verdict FALSE_WIN_ALGEBRA (HARD_FAIL class)
  REGARDLESS of G_A** (drill Q5 false-win gate).
- G_B2 superposition axis: bundle_recall@5 >= 0.55 AND >= DENSE_SIGN bundle_recall@5
  + 0.03 AND >= DENSE_SIGN at every J (curve dominance) -> PASS; dominance holds but
  level < 0.55 -> MIDDLE_BAND; BLOCK below DENSE anywhere -> HARD_FAIL
  (sparsity-not-protecting = structure bug).
  HYPOTHESIZED@probe: 0.664 vs 0.624 at J=5, 0.106 vs 0.048 at J=20 at V_eval=5000;
  regime-extension risk to V=178K documented (more distractors); level band set
  BELOW probe value accordingly.
- C_shuffled_key: hit-rate <= 0.05 (MEASURED@probe 0.000).
- C_pos_control (RANDOM_BLOCK reproduces SBC lossless prior AT TEST REGIME):
  keyed_roundtrip@1 >= 0.98 at J=5 (THEORETICAL@Frady2020 lossless;
  MEASURED@probe 1.000). Outside tolerance -> HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH.
- Overall verdict: HARD_PASS iff G_A HP AND G_B1 HP AND G_B2 PASS AND both controls
  pass. G_A MIDDLE with algebra gates green -> MIDDLE_BAND (semantic undertrained,
  not false-win).

## Bands (SMOKE; reduced scale, 150 steps, probe-calibrated)

- S_A: BLOCK_K128 spearman_all >= 0.60 HP; [0.40, 0.60) MB; < 0.40 SMOKE_GATE_FAIL.
  (Probe: 0.807 at 400 steps; 150-step margin built in.)
- S_gap (discriminator-fires, META_RULE_K): BLOCK_K128 ret_agree@10 >=
  CHARPOS ret_agree@10 + 0.10 (probe: 0.516 vs 0.066).
- S_B1: keyed_roundtrip@1 = 1.0 expected at J=5; gate >= 0.95 (probe: 1.000).
- S_B2: bundle dominance BLOCK >= DENSE_SIGN at J=5 and J=20; level >= 0.50 at J=5.
- S_falsewin_demo (mechanism-fires for the comparison axis): TOPK_NAIVE
  keyed_roundtrip@1 at J=20 <= 0.80 (probe: 0.483) while RANDOM/BLOCK hold >= 0.95
  -- demonstrates the false-win the block structure prevents.
- S_shuffled_key <= 0.05; S_pos_control RANDOM_BLOCK >= 0.98 at J=5.
- Smoke wall budget: <= 180s (queue_add gate cap).

## SCHEMA-VET / META_RULE fields

- cardinality_ok: true. EXPECTED_N_UNITS: SMOKE = 5 semantic (BLOCK_K128,
  TOPK_NAIVE, CHARPOS, RANDOM_BLOCK, DENSE_SIGN) + 4 arms x 2 J keyed + 4 arms x
  2 J bundle (BLOCK_K128, TOPK_NAIVE, RANDOM_BLOCK, DENSE_SIGN) + 1 shuffled-key
  = 22. FULL = 6 semantic (+BLOCK_K64) + 5 arms x 4 J keyed + 5 arms x 4 J bundle
  + 1 shuffled-key = 47. Verdict logic counts per_unit; shortfall ->
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- arms_differ_verified: true (sha256 over the 5/6 semantic-arm code matrices,
  pairwise distinct; no exemptions).
- final_metrics_atomicity: "tmp_replace" (write_metrics helper; tmp + os.replace).
- except-discipline: except SystemExit/KeyboardInterrupt re-raise before
  except Exception; no bare except; per-unit failure_class instrumentation
  (META_RULE_J); no silent continue.
- crlb_floor_computed: 0.901 attenuation bound at K_BLOCKS=128
  (crlb_formula_reference: r_max = sigma_teacher / sqrt(sigma_teacher^2 + 0.25/K),
  sigma_teacher = 0.0918 MEASURED on 2000-concept teacher sample; K=64 -> 0.826,
  K=102 -> 0.880, K=128 -> 0.901). discriminator_reachability: true for G_A at
  K=128 (0.85 < 0.901); false at K=64 -> K64 arm is report-only, NOT gated on 0.85.
- baseline_in_band (META_RULE_AG): CHARPOS ret_agree@10 = 0.0655 MEASURED@probe,
  inside (0.05, 0.95). RANDOM arms are declared negative controls (floor expected,
  exempt). No baseline saturation possible on correlation-type metrics here.
- calibration_check: "default_ok_for_this_regime" -- k-sparsity 3.125 pct evidence:
  ablation MEASURED (k=32/1024 dominates k=20/1024 at equal cleanup) + CRLB bound;
  semi-hard band [0.3, 0.6] covers 0.801 of train pairs MEASURED@probe.
- discriminator survives scale: option (A)+(B) hybrid. Smoke runs at FULL N_DIM
  = 4096 and FULL K_BLOCKS = 128 (identical code geometry); scale axes that grow in
  FULL are V (43905-subset -> 177861) and steps (150 -> 20000). Analytical: RKD/NCE
  quality is monotone in data+steps (more concepts+steps cannot reduce the
  discriminator below smoke floor); cleanup difficulty grows with V -- bands for
  G_B2 set BELOW probe values for that reason, and keyed G_B1 is V-insensitive by
  SBC losslessness (crosstalk governed by keys, not codebook size; probe 1.000).
- cell_chunked: false (single-seed artifact-producer; within-cell checkpoint/resume
  instead: mining shards + training ckpt each 500 steps, atomic, resumable).
- start_marker_written: true. crash_diagnostic_present: true.
  heartbeat_present: true (_heartbeat.jsonl every 100 train steps + per eval unit).
- defensive_error_checking: "passed_all_4_patterns".
- progress_logging: "print_flush_true" (timeout >= 1800 FULL).
- run_mode wiring: --run-mode {self_test,smoke,full} default env HDLAB_RUN_MODE
  else self_test (Step-1 convention); post-dispatch run_mode verification per §16
  mandatory in completion report.

## §15 gates

- sweep_alignment_verdict: ALIGNED (J bundle-depth axis is experienced directly by
  every primitive; K_BLOCKS axis is the student architecture itself; no composed
  primitive sees a divided/effective parameter).
- discriminating_fraction: 0.50 on the J axis (TOPK_NAIVE MEASURED@probe lands in
  [0.30, 0.70] at J=20 (0.483) and near-band at J=10 (0.800); BLOCK bundle axis
  MEASURED in-band at J=5 (0.664)). >= 0.30 satisfied.
- composition_edges:
  - encoder(block code [K,L]) -> SBC bind/unbind (hdlab binding on last dim of
    [K,L]): SHAPE_MATCH (reshape adapter, lossless by construction).
  - encoder(top-k sparse real) -> literal FHRR bind: SHAPE_MISMATCH_adapter_
    complexify_zero_dims -- INTENTIONAL negative-comparison arm demonstrating the
    drill's category error; documented risk IS the measurement.
  - unbound vector -> cosine-argmax cleanup over codebook: SHAPE_MATCH.
- positive_control_arms: RANDOM_BLOCK keyed_roundtrip reproduces SBC-lossless prior
  at THIS test regime (N=4096, K=128, V_eval, J grid), cited_prior =
  Frady/Kleyko/Sommer 2020 (CITED) + probe 1.000 (MEASURED); tolerance 0.02 at J=5.
- functional_requirements:
  - FR1 preserve teacher semantic geometry -> RKD + InfoNCE objective (new
    mechanism, this cell's point).
  - FR2 exact sparsity in proven window -> block architecture (1/block, k=K/N).
  - FR3 invertible composition -> SBC block circconv (hdlab bind/unbind).
  - FR4 novel-concept encodability -> linear W on teacher embedding (held-out eval).
  - FR5 restartability -> mining shards + train ckpt + resume (Step-1 pattern).
  - FR6 storage strategy -> SHARDED per-concept codes (bundling appears ONLY as
    explicit discriminator arms, exemption (b) of the sharded-default rule).

## Compute architecture

Class (a) batched-GPU for FULL (mining = chunked [4096 x V] teacher matmuls on GPU;
training = batched matmul; evals = chunked codebook matmuls). SMOKE runs the same
torch code on CPU (SMOKE-only-local rule; wall <= 180s). No per-phase-point
sequential Python matmul loops. Storage strategy: sharded (see FR6).

## Timeout

SMOKE: 600s queue timeout (measured probe-analog wall ~155s target + margin).
FULL (GPU): timeout_s = ceil(1.5 * smoke_wall_s * (steps_full/steps_smoke) *
cpu_to_gpu_factor) with cpu_to_gpu_factor ~ 1/20 for these matmul shapes, plus
mining + eval overhead ~ 1200s => estimate ~ 3600-5400s wall; **--timeout 10800**
(3h) with justification: first GPU run of this cell family, 178K-concept mining +
two students (K sweep) + 47 eval units; > 4h NOT expected.

## Artifacts

- `data/exp_encoder_migration_step1b_distill_concept_encoder_v1{_smoke}/metrics.json`
- `data/substrate_concept_encoder_v1b{_smoke}/encoder_distilled_K128.npz`
  (+ `_K64` in FULL): int8 codes [V, N_DIM], W float32 [N_DIM, 1024], id order,
  metadata (teacher cache name/sha-prefix, config, source signature).

## Halt conditions

Training loss NaN/Inf -> CELL_CRASHED with failure_class. Any eval unit exception
-> recorded failure_class + fatal-flag + FAIL_LOUD (no silent continue). Teacher
cache missing/id-count mismatch -> hard abort before training.
