# Pre-reg: substrate_seqbind_N_dim_scaling_law_v1

Filed 2026-06-30. USER 2026-07-01 overnight priority (first free-axis chain-grade
attempt at axis B: N dimensionality).

## v1.6 amendment (2026-06-30, exp_dev)

**Platform limitation discovered:** v1.0/1.1/1.2/1.3/1.5 all failed on the GPU
host (RTX 4060 Ti / Windows / 8 GiB) at N=32768 despite chunked-encode +
chunked-decode + `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. Root cause:
PyTorch on Windows does NOT support `expandable_segments` (runtime UserWarning:
"expandable_segments not supported on this platform"). Without allocator defrag
between (N,K) points, chronic fragmentation (~800 MB reserved-not-allocated) OOMs
at N=32768 gather.

**v1.6 pivot:** cap `N_DIM_SWEEP_FULL` at 16384 (was 32768). Drop top scaling
anchor. Rationale: 4 anchors N in {2048, 4096, 8192, 16384} still gives 3 log2
doublings -- sufficient statistical power for linear fit K_cliff(N) = alpha * N
with slope and R^2 identifiable. Extrapolation from 4-anchor fit predicts K_cliff
at N=32768 without requiring the measured point.

Updated cardinality:
- `EXPECTED_N_UNITS_FULL` = 2 arms x 4 N x 7 K = **56** (was 70)
- `EXPECTED_N_UNITS_SMOKE` = 2 arms x 3 N x 3 K = **18** (was 24)
- Smoke N sweep now (2048, 8192, 16384) -- includes POSCTRL_N=8192 anchor +
  N=16384 discriminator-must-survive-scale preview
- All other pre-reg fields (HP bands, MB bands, POSCTRL, tolerance, K_SEQ sweep,
  ITEM_VOCAB, NOISE_SIGMA, POSITION_SLOTS) UNCHANGED

If N=32768 becomes required for chain-grade tier: chunk the `item_codebook[item_ids]`
gather (Option B; v1.7+) OR migrate GPU host to Linux (expandable_segments
supported). Not pursued now -- 4-anchor fit is chain-grade-eligible.

## Hypothesis

Sequence-binding K-cliff scales linearly with substrate dimensionality N.
Specifically: `K_cliff(N) = alpha * N` for some constant `alpha` (predicted
`~0.12` based on theta-gamma v2 CG at N=4096 and prior K-cliff CG at N=8192).

log2(K_cliff) vs log2(N) is expected to be a straight line with slope ~= 1.0.

## Composition (per META_RULE §15.D)

- Chain-grade primitive: sequence-binding K-cliff at N=8192 (atomized;
  MEASURED@data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_7/metrics.json)
- Chain-grade primitive: theta-gamma FHRR v2 at N=4096 (atomized; K_cliff CG)
- New sweep axis: N in {2048, 4096, 8192, 16384, 32768}
- New composition: does K_cliff scale linearly with N?

positive_control_arms (Gate D):
  - arm: SEQBIND_REPRODUCE_AT_N8192_K1000
    primitive: FHRR_FLAT_PHASE_32 sequence binding + FHRR unbind
    cited_prior_atom: theta-gamma v2 FHRR K_cliff CG
    cited_prior_metric: K_cliff ~ 1000 at N=8192, ITEM_VOCAB=10000, NOISE_SIGMA=0.05
      HYPOTHESIZED@preregs/2026-06-30_substrate_theta_gamma_v2_FHRR_all_complex.md
      (source cell alpha ~ 0.12 based on cliff at K=1000)
    tolerance: log2 delta <= 0.5 (factor of 1.41)
    if_outside_tolerance: HARD_FAIL_POSITIVE_CONTROL_REGRESSION

## Config (LOCKED at cell-init; META_RULE_AE)

- N_DIM_SWEEP = [2048, 4096, 8192, 16384, 32768]  (5 values; axis B)
- K_SEQ_SWEEP = [50, 100, 200, 500, 1000, 2000, 4000]  (7 values)
- Seeds = [7, 13, 19] (dispatched as 3 chunked sibling cells per META_RULE §13.A)
- Encoder: FHRR complex64 (matches theta-gamma v2)
- Position codebook: 4096 unit-phase FHRR complex codes; each item at slot k
  bound to positions[k] (unique-per-slot, NO cyclic wrap; slot k in 0..K-1)
  NOTE: this differs from theta-gamma v2 CG which used flat-8/32 with cyclic
  wrap; here unique positions per slot are REQUIRED so the K-cliff arises
  from N-capacity, not from position collisions
- ITEM_VOCAB_SIZE: 10000 (matches theta-gamma v2 CG)
- NOISE_SIGMA: 0.05 (matches CG regime)
- N_QUERIES_PER_K = 30 (full); 10 (smoke)
- CLIFF_ACC_THRESHOLD = 0.5

## Bands (envelope; META_RULE_L)

- HARD_PASS: linear-fit R^2 >= 0.95 AND slope in [0.85, 1.15] AND
  cv-across-seeds on slope <= 0.10 AND positive-control passes
- MIDDLE_BAND: R^2 in [0.80, 0.95) OR slope in [0.70, 1.30) but not HARD_PASS
- HARD_FAIL: R^2 < 0.80 OR slope outside [0.70, 1.30] (validates scaling ceiling)
- Positive-control at N=8192: K_cliff must fall in {500, 1000, 2000} (log2 window)
- Positive-control violation => HARD_FAIL_POSITIVE_CONTROL_REGRESSION (Gate D)

## META_RULE_BC positive control (random baseline sanity)

Arm B: RANDOM_SHUFFLE_ITEMS - decoded item ids are shuffled uniformly from
codebook. Expected K_cliff ~ 0 at all N (chance level).

## Cardinality (META_RULE_H)

Per seed:
- FULL: 2 arms (SUBSTRATE, RANDOM) * 5 N * 7 K * 30 queries = 21000 records
- SMOKE: 2 arms * 3 N (2048, 4096, 8192) * 3 K (200, 1000, 4000) * 10 queries = 1800 records

expected_n_units per seed:
- FULL: 2 * 5 * 7 = 70 phase points
- SMOKE: 2 * 3 * 3 = 18 phase points

## Discriminator-must-survive-scale (§DISCRIMINATOR-MUST-SURVIVE-SCALE)

Chosen: pattern C - preview N=32768 arm at 3 K values in smoke.
Smoke runs at N in {2048, 4096, 8192} (3 lower N) + N=32768 (1 preview) with
reduced K/query counts. If N=32768 preview K_cliff does not show clean
separation vs baseline, abort full dispatch (GPU memory or numerical stability
issue at largest N).

## CRLB / capacity feasibility (§9)

K_cliff floor per Plate 1995 HRR: `K_max ~ N / (log(V) * gamma^2)` where gamma
is desired cleanup similarity. For V=10000, log(V) ~ 13.3, gamma ~ 0.5:
- N=32768: K_max ~ 32768 / (13.3 * 4) ~ 615 (order-of-magnitude estimate; empirical range 500-4000 from CG)
- discriminator_reachability: True (target slope [0.85, 1.15] achievable given
  linear K_cliff(N) scaling law)
crlb_floor_computed: N/A (this cell tests the scaling law itself; K_cliff at each
  N is the measurement, not compared against CRLB)
crlb_n/a: "scaling-law characterization; per-N K_cliff is the OUTPUT, not test-vs-floor"

## Schema-VET checklist (§ SCHEMA-VET PRE-DISPATCH CHECKLIST)

- cardinality_ok: MANDATORY at aggregate; expected_n = 70 (full) / 18 (smoke) per seed
- final_metrics_atomicity: tmp_replace (per META_RULE_AH)
- arms_differ_verified: MANDATORY at smoke gate (META_RULE_AF hash check on 2 arms)
- baseline_in_band: RANDOM arm expected < 0.05 at all K (not saturated); mechanism
  arm expected in (0.05, 0.95) across sweep points (verified in smoke)
- calibration_check: "default_ok_for_this_regime" - inherits theta-gamma v2 CG
  regime (V=10000, NOISE=0.05, N=4096 baseline extended to N sweep)
- discriminator survives scale: pattern C preview at N=32768 in smoke
- HARD_PASS strictly above floor + 5% band-width (slope band-width 0.30 => 5% = 0.015 margin)
- HP_SCOPE: {SUBSTRATE: [all HP gates], RANDOM: [baseline_in_band < 0.05 only]}

- sweep_alignment_verdict: ALIGNED (N is directly what encoder consumes; no
  routing overlay hiding effective_N)
- discriminating_fraction: 5/5 N values expected in discriminating band (K_cliff
  neither 0 nor at sweep boundary); 1.0 discriminating
- composition_edges: single primitive (sequence binding); no cross-primitive
  composition; SHAPE_MATCH trivially
- positive_control_arms: SEQBIND_REPRODUCE_AT_N8192_K1000 defined above
- functional_requirements: [substrate holds K distinct items bound to positions
  at N-dim scale; retrieval recovers argmax item within cleanup similarity floor;
  scaling law characterizes capacity growth]

## Chunked architecture (§13)

- cell_chunked: true (3 sibling files, one seed each)
- start_marker_written: true (via _write_minimal_metrics STARTED phase)
- crash_diagnostic_present: true (Exception-only outer try; NOT BaseException; per §8 & §13.C)
- heartbeat_present: true (per-phase-point via CellHeartbeat context manager)
- defensive_error_checking: passed_all_4_patterns

## Cell files

- experiments/_substrate_seqbind_N_dim_scaling_law_v1_core.py (shared core)
- experiments/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_7.py
- experiments/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_13.py
- experiments/exp_substrate_seqbind_N_dim_scaling_law_v1_seed_19.py

## Queue

Target: overnight_queue (GPU).
Rationale: complex64 matmul over V=10000 x N=32768 codebook; benefits from GPU
per PROT-020 (import torch is required and present).
Timeout per seed: 3600s (1h). Estimated wall per seed ~30-40 min; 3600s buffer.

## Numbers cited (META_RULE_AC tagging)

- alpha ~ 0.12 THEORETICAL@Plate1995_HRR (K_cliff ~ N/log(V) scaling)
- K_cliff at N=8192 ~ 1000  CITED@theta-gamma v2 K_SEQ_SWEEP CG (this cell's positive-control target)
- cb_complex64 at N=32768 = 2500 MiB  THEORETICAL@V*N*8B/(1024^2)=10000*32768*8/(1024^2)
- seq_encode at K=4000,N=32768 = 1000 MiB  THEORETICAL@K*N*8B/(1024^2)
- peak GPU memory ~3.5 GiB at N=32768 K=4000  THEORETICAL@cb+2*seq (upper bound)
- slope predicted = 1.06  THEORETICAL@log2 fit of alpha=0.12*N snapped to K_SEQ grid
- R^2 predicted = 0.996  THEORETICAL@same fit
