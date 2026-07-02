# Pre-reg — substrate_concept_encoder_spoke1_phase_diagram_SPC_data_hunger_v1

**Filed:** 2026-07-02 late evening (Director main-thread; Cell 2 of the phase-diagram Option C hierarchical strategy)
**Anchor:** `substrate_concept_encoder_spoke1_phase_diagram_SPC_data_hunger_v1_2026_07_02`
**Design note:** `notes/research_spoke1_phase_diagram_extension_axes_and_probe_design_2026-07-02.md`
**Sister prereg:** `2026-07-02_substrate_concept_encoder_spoke1_phase_diagram_N_DIM_x_N_CONCEPTS_grid_v1.md` (Cell 1)
**Motivation:** USER 2026-07-02 late evening: "fill out the phase diagram and load-bearing CGs at the same time." Axis A3 (SPC — sentences-per-concept — DATA_HUNGER claim). Stage 4 Wikipedia-ingest needs long-tail concept coverage; if mechanism requires SPC ≥ 100 to consolidate, low-frequency Wikipedia concepts fail.

## Prereq

Spoke 1 v3-D FULL landed CG (a5f042d2; commit e8f15a036 remote HP wall 39.6s). Cell 1 (N_DIM × N_CONCEPTS grid) can dispatch in parallel to Cell 2.

## Framing discipline (LOAD-BEARING)

Under USER 2026-07-02 brain-best-in-class: tests the substrate-owned competitive-Hebbian mechanism's INVARIANCE across the DATA_HUNGER axis. Analogous to Stage 4 corpus-scale claim without doing Stage 4 language ingest (still MECHANISM PROOF; synthetic controlled corpus at variable SPC).

## Regime

Grid axis:
- **SPC ∈ {10, 20, 40, 80, 160, 320}** — 6 values (DATA_HUNGER)
- N_DIM = 4096 (fixed at v3-D baseline)
- N_CONCEPTS = 50 (fixed at v3-D baseline)
- k_sparsity = 0.02 (fixed at v3-D baseline)
- Storage: SHARDED

Seeds: {11, 17, 23}

## Arms (8 arms × 3 seeds = 24 units)

**6 SPC arms:** `ARM_CH_SPC{10|20|40|80|160|320}` — competitive-Hebbian at each SPC value

**2 controls at central SPC=40:**
- `ARM_NAIVE_WTA_SPC40` — 2026-06-23 falsified mechanism (progress control)
- `ARM_RANDOM_SPC40` — chance control

Cardinality target: `EXPECTED_N_UNITS = 8 * 3 = 24`; `arms_differ_verified` required.

## Metrics per arm × seed

Existing v3-D metrics + new:
- `cat_kitten_cos_mean`, `cat_airplane_cos_mean`, `gap`, `intra_concept_cv`, `sparse_rate`
- New:
  - `spc_saturation_slope`: derivative of cat_kitten_cos wrt log(SPC); flat at high SPC = saturated, positive at low = data-hungry
  - `spc_minimum_viable_threshold`: lowest SPC where cat_kitten_cos_mean ≥ 0.35 (HP1 floor)
  - `spc_saturation_ratio`: cat_kitten_cos_mean(SPC=320) / cat_kitten_cos_mean(SPC=40) — should be ≤ 1.15 if saturated

## HP bands (HP_SCOPE: LOAD_BEARING on SPC arms)

**HARD_PASS (target CG per axis):**
- HP1: SPC ∈ {40, 80, 160, 320} arms cat_kitten_cos_mean ≥ 0.35 (mechanism works at typical + high SPC)
- HP2: SPC ∈ {40, 80, 160, 320} arms cat_airplane_cos_mean ≤ 0.15
- HP3: all 6 SPC arms sparse_rate ∈ [0.010, 0.030]
- HP4: `spc_minimum_viable_threshold` ≤ 40 (mechanism doesn't need extreme data — data-hunger not prohibitive)
- HP5: `spc_saturation_ratio` ≤ 1.15 (saturates at typical SPC; more data doesn't dramatically lift)
- HP6: central arm SPC=40 reproduces v3-D baseline within ±0.05 (Gate D)
- HP7: RANDOM control |cat_kitten_cos| ≤ 0.05
- HP8: SPC=40_gap - NAIVE_gap ≥ 0.15 (progress)
- DATA_HUNGER band: monotone-non-decreasing cat_kitten_cos as SPC grows (allowed decrease ≤ 0.02 per doubling due to noise)

**HARD_FAIL:**
- SPC ∈ {80, 160, 320} arms cat_kitten_cos < 0.30 → HF (mechanism doesn't work at abundant data)
- OR SPC=40 arm below v3-D baseline (Gate D violation, INVOCATION_MISMATCH)
- OR sparse_rate outside [0.005, 0.10] any arm

**MIDDLE_BAND:**
- `spc_minimum_viable_threshold` ∈ (40, 80] — mechanism needs above-typical data; partial DATA_HUNGER claim
- OR `spc_saturation_ratio` > 1.15 — mechanism keeps lifting with more data; not saturated

## Sanity + integration gates

- ARM_RANDOM_SPC40 chance ±0.05; scoring rig verified
- ARM_NAIVE_WTA_SPC40 gap=0.000 reproduces 2026-06-23 HF; falsified prior confirmed
- Central SPC=40 reproduces v3-D baseline; cell invocation sound

## Substrate primitives called

- `hdlab/concept_encoder.py` (Spoke 1 v3-D extraction) — imports post-a718b151 completion
- `hdlab/char_positional_encoder.py`
- No PC layer

## CELL-TEMPLATE MANDATORY compliance

- arms_differ_verified (24 distinct)
- tmp_replace metrics
- except SystemExit before except Exception
- HP_SCOPE=LOAD_BEARING on 6 SPC arms; controls report + chance
- cardinality_ok: 24 units
- discriminator survives scale (SPC-320 tests largest data volume)
- HP strictly above floor
- env-var contract check (bias-checklist META pattern per session finding)
- scale sentinel selftest at real N_DIM=8192

## Compute architecture

- (a) batched-CPU-torch or NumPy vectorized
- Per-unit wall: SPC scaling → O(SPC × N × C) accumulator time
  - SPC=10: ~10s
  - SPC=40: ~30-40s (v3-D baseline)
  - SPC=80: ~60-80s
  - SPC=160: ~2-3 min
  - SPC=320: ~4-6 min
- Total FULL wall (24 units, all at N=4096, mostly at lower SPC): ~30-50 min
- Route: `remote_cpu_queue` (well under 60 min)
- Smoke wall: ~2-5 min (2 SPC endpoints + 2 controls at reduced concept count)

## Dispatch prerequisites

1. Spoke 1 v3-D FULL landed CG (DONE)
2. `hdlab/concept_encoder.py` extraction landed (a718b151 in flight)
3. Skunkworks SCHEMA-VET on this prereg
4. Smoke gate on local_cpu

## Post-verdict routing

**HARD_PASS at CG:**
- Cell 2 CG'd; closes A3 (SPC DATA_HUNGER) axis
- Cell 3 (sparse-rate) also independent — dispatch in parallel or sequential
- Post-Cells-1+2+3 CG → promote META `T4/META_SPOKE1_COMPETITIVE_HEBBIAN_CONCEPT_ENCODER_SCALE_FREE_AND_CAPACITY_UNIVERSAL_LAW_v1` to CG_META tier

**HARD_FAIL:**
- If SPC≥80 fails: mechanism has DATA_HUNGER ceiling; scope-tighten META claim + note ingest constraint for Stage 4
- If Gate D fails: cell bug; halt investigate

**MIDDLE_BAND:**
- File as MM_TENTATIVE_SPC_LIMITED_LAW; propose v2 with hyperparameter tuning at low SPC

## Composability + META candidates

- Composes with Spoke 1 v3-D CG + Cell 1 CG for 3-axis physics-law claim
- Independent from Stage 1 storage-strategy META
- Data-hunger claim is Stage 4 relevant — motivates future concept-encoder training at real corpus scale

## Priors

- Spoke 1 v3-D CG (baseline)
- Cell 1 phase-diagram (N_DIM × N_CONCEPTS grid) — parallel dispatch
- Stage 1 CG_META atoms (precedent)

## Estimated timeline

- Cell authoring: ~30-45 min
- Local smoke: ~5-15 min
- SCHEMA-VET: ~5 min
- FULL dispatch on remote_cpu_queue: ~30-50 min wall
- Landed-VET: ~5 min

Total: ~1.5-2 hrs from Spoke 1 v3-D CG + hdlab extraction.
