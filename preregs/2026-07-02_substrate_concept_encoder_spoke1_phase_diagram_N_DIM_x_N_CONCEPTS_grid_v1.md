# Pre-reg — substrate_concept_encoder_spoke1_phase_diagram_N_DIM_x_N_CONCEPTS_grid_v1

**Filed:** 2026-07-02 late evening (Director main-thread; positions for immediate dispatch post-Spoke-1-v3-D-CG)
**Anchor:** `substrate_concept_encoder_spoke1_phase_diagram_N_DIM_x_N_CONCEPTS_grid_v1_2026_07_02`
**Design note:** `notes/research_spoke1_phase_diagram_extension_axes_and_probe_design_2026-07-02.md`
**Motivation:** USER 2026-07-02 late evening: "fill out the phase diagram and load-bearing CGs at the same time" as Spoke 1 v3-D secures. Target 4-axis physics-law CG_META `SPOKE1_COMPETITIVE_HEBBIAN_CONCEPT_ENCODER_SCALE_FREE_AND_CAPACITY_UNIVERSAL_LAW`.

## Prereq

Spoke 1 v3-D FULL landed CG (in flight, orchestrator a5f042d2 post env-var-fix redispatch). Gate-D reproducibility gate requires central-arm N=4096 C=50 to match v3-D baseline within ±0.05.

## Framing discipline (LOAD-BEARING)

Under USER 2026-07-02 brain-best-in-class discipline: this cell tests the substrate-owned competitive-Hebbian mechanism's INVARIANCE across scale × capacity axes. It's a substrate-physics-law claim (mirrors Stage 1 storage-strategy 3-axis META tier promotion pattern). Inputs are synthetic controlled corpus HDs (NOT English); cell does NOT test language capability.

## Regime

Grid axes:
- **N_DIM ∈ {2048, 4096, 8192, 16384}** — 4 values (mirrors Stage 1 SCALE_FREE)
- **N_CONCEPTS ∈ {25, 50, 100, 200}** — 4 values (CAPACITY axis)
- SPC (sentences-per-concept) = 40 (fixed at v3-D baseline; Cell 2 axis)
- k_sparsity = 0.02 (fixed at v3-D baseline; Cell 3 axis)
- Storage: SHARDED (per USER-locked storage-strategy CG_META)

Seeds: {11, 17, 23} (3 seeds; matches v3-D)

## Arms (18 arms × 3 seeds = 54 units)

**16 GRID arms:** `ARM_CH_N{2048|4096|8192|16384}_C{25|50|100|200}` — competitive-Hebbian at each grid point

**2 controls:**
- `ARM_NAIVE_WTA_N4096_C50` — reproduces 2026-06-23 falsified mechanism at grid center (progress control)
- `ARM_RANDOM_N4096_C50` — random-codebook baseline at grid center (chance control)

Cardinality target: `EXPECTED_N_UNITS = 18 * 3 = 54`; `arms_differ_verified` required across all 54.

## Metrics per arm × seed

Existing v3-D metrics (per grid point):
- `cat_kitten_cos_mean`, `cat_airplane_cos_mean`, `gap`, `intra_concept_cv`, `sparse_rate`, `cat_kitten_cos_std`, per-concept intra_std

New phase-diagram metrics:
- `cross_N_cv_at_C{25,50,100,200}` — cross-N cv on cat_kitten_cos_mean at each fixed C (SCALE_FREE band)
- `cross_C_monotone_slope_at_N{2048,4096,8192,16384}` — cross-C monotone slope at each fixed N (CAPACITY band)
- `grid_shape_matrix` — 4×4 matrix of cat_kitten_cos_mean; identify boundary corners

## HP bands (HP_SCOPE: LOAD_BEARING on 16 GRID arms; controls have low-signal bands)

**HARD_PASS (target CG per axis):**
- HP1: all 16 GRID arms cat_kitten_cos_mean ≥ 0.35 (relaxed 0.05 from v3-D's 0.40; allows signal-degradation at extremes)
- HP2: all 16 GRID arms cat_airplane_cos_mean ≤ 0.15 (relaxed 0.05 from v3-D)
- HP3: all 16 GRID arms sparse_rate ∈ [0.010, 0.030] (architectural)
- HP4: all 16 GRID arms intra_concept_cv < 0.25 (relaxed from v3-D's 0.20)
- HP5: central arm N=4096 C=50 reproduces v3-D baseline within ±0.05 (Gate D)
- HP6: RANDOM control |cat_kitten_cos| ≤ 0.05 (chance)
- HP7: GRID_central_gap - NAIVE_gap ≥ 0.15 (progress over falsified baseline)
- SCALE_FREE band: across N_DIM axis at fixed C, std(cat_kitten_cos_mean) across N ≤ 0.10 (INVARIANCE)
- CAPACITY band: across C axis at fixed N, monotone-non-increasing cat_kitten_cos as C grows (slope up to -0.005 per +25 concepts)

**HARD_FAIL:**
- Any GRID arm cat_kitten_cos < 0.20 → HF at that grid point (boundary identified)
- Any GRID arm sparse_rate outside [0.005, 0.10] → HF
- Central arm outside v3-D reproducibility band → HF (INVOCATION_MISMATCH, halt-and-investigate)

**MIDDLE_BAND:**
- SCALE_FREE band violation (std > 0.10) OR CAPACITY band violation (non-monotone) — partial physics-law claim; scope tighter than expected

## Sanity + integration gates

- ARM_RANDOM_N4096_C50 must be at chance (±0.05); confirms scoring rig sound
- ARM_NAIVE_WTA_N4096_C50 gap = 0.000 (reproduces 2026-06-23 HF); confirms progress over falsified prior
- Grid central arm (N=4096, C=50) HP5 reproducibility gate; if fails, cell has invocation bug not mechanism finding

## Substrate primitives called

- `hdlab/concept_encoder.py` (post-Spoke-1-CG extraction) — sparse competitive-Hebbian encoder
- `hdlab/char_positional_encoder.py` (from Spoke 1 v1/v2/v3-D)
- No PC layer (falsified for concept encoding at flat regime per 6/6 drill convergence)

## CELL-TEMPLATE MANDATORY compliance

- arms_differ_verified: True (54 distinct per-arm-seed digests)
- final_metrics_atomicity: tmp_replace (via `_seed_checkpoint.write_metrics`)
- except SystemExit: raise BEFORE except Exception
- crlb_n/a: "cluster-similarity discriminator; chance floor 1/C at random-codebook"
- baseline_in_band: RANDOM at chance, NAIVE at prior-falsified gap=0.000, GRID above floor
- discriminator_survives_scale: scale sentinel at N_DIM=16384 at cell selftest bottom
- HP strictly above floor: 0.35 vs floor of chance (~0) with 0.35 margin
- HP_SCOPE: LOAD_BEARING on 16 GRID; NAIVE + RANDOM report + control
- cardinality_ok: 54 units expected
- calibration_check: default_ok (no learned parameters at grid point; per-arm deterministic init)
- progress_logging: print_flush_true
- start_marker + _heartbeat.jsonl + crash_diagnostic: standard
- **env-var contract check (per this session's bias-checklist META candidate; encoded in Spoke 1 v3-D fix e8f15a036):** selftest verifies HDLAB_RUN_MODE env-var is honored (fails hard on hardcoded default)

## Compute architecture

- (a) batched-CPU-torch or NumPy vectorized; per-arm accumulator O(SPC × N)
- Per-unit wall estimates:
  - N=2048: ~30-60s
  - N=4096: ~1-2 min
  - N=8192: ~2-4 min
  - N=16384: ~4-8 min (accumulator quadratic)
  - C=200: multiplied by ~4x concept-loop
- Worst-case unit (N=16384, C=200): ~15-20 min
- Total FULL wall (54 units serial): ~60-90 min
- Route: **overnight_queue** (>30 min risk)
- Smoke wall estimate: ~90-180s (2 grid corners + 2 controls at N=2048 only)

## Dispatch prerequisites

1. Spoke 1 v3-D FULL landed CG (in flight; a5f042d2)
2. `hdlab/concept_encoder.py` extraction landed post-Spoke-1-CG (M1.9 extraction pattern)
3. Skunkworks SCHEMA-VET on this prereg
4. Smoke gate on local_cpu (USER-locked SMOKE_ONLY_LOCAL_CPU)
5. Env-var contract selftest PASS

## Post-verdict routing

**HARD_PASS at CG:**
- Cell 1 CG'd; closes A1 (N_DIM SCALE_FREE) + A2 (N_CONCEPTS CAPACITY) axes
- Fire Cells 2 (SPC data-hunger) + Cell 3 (sparse-rate architectural-invariance) in parallel to remote_cpu_queue
- Post-Cells-2+3 CG: promote META `T4/META_SPOKE1_COMPETITIVE_HEBBIAN_CONCEPT_ENCODER_SCALE_FREE_AND_CAPACITY_UNIVERSAL_LAW_v1` to CG_META tier (4-axis coverage exceeds 3-axis storage-strategy precedent)

**HARD_FAIL at central arm (INVOCATION_MISMATCH):**
- Cell has bug; not a mechanism finding
- Halt and investigate before further phase-diagram probes

**HARD_FAIL at boundary (specific grid point):**
- Boundary identified; report as scaling law's outer edge
- Cells 2 + 3 still valuable; fire them
- META claim scope-tightened but still filable

**MIDDLE_BAND (SCALE_FREE or CAPACITY band violation):**
- Physics-law claim SCOPE_TIGHTER than expected; still CG-tier if grid points pass HP1-HP4
- File as MM_TENTATIVE_SCALE_LIMITED_LAW

## Composability + META candidates

- Composes with Spoke 1 v3-D CG (baseline)
- Independent from Stage 1 storage-strategy CG_META (different mechanism claim, different axes)
- Future cross-composition META `M3_cortex_end_to_end_law_v1` could compose both

## Priors (composable atoms already CG'd)

- Spoke 1 v3-D competitive-Hebbian mechanism (pending FULL CG; a5f042d2 in flight)
- Stage 1 CG_META atoms (SCALE_FREE + TOPOLOGY_FREE + composed) — precedent for 3-axis META tier
- SUBSTRATE_ALGEBRA_SCALES_TO_DEEPER_CHAINS CG_META (M1.9/M1.10/M1.11 chain) — same META tier pattern

## Estimated timeline (post-Spoke-1-CG + hdlab extraction)

- Cell authoring: ~45-75 min (large cell; 18 arms × grid axes)
- Local smoke: ~5-15 min
- Skunkworks SCHEMA-VET: ~5 min
- FULL dispatch on overnight_queue: 60-90 min wall
- Skunkworks landed-VET: ~5-10 min (compact VET format)
- Cells 2 + 3 dispatch in parallel: ~15-25 min wall each on remote_cpu_queue

Total for Cell 1: ~2-3 hrs from Spoke 1 CG to landed-VET. Cells 2+3 add ~30-45 min if parallel.
