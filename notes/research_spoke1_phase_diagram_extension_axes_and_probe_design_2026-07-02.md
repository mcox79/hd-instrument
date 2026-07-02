# Spoke 1 v3-D competitive-Hebbian PHASE DIAGRAM extension: axes + probe design

**Filed:** 2026-07-02 late evening
**Role:** Research director (main-thread strategic design)
**Trigger:** USER directive 2026-07-02 late evening: "fill out the phase diagram and load-bearing CGs at the same time" as Spoke 1 v3-D secures.
**Purpose:** design the multi-cell probe arc that extends Spoke 1 v3-D (competitive-Hebbian only, Foldiak/Kohonen/SoftHebb-analog) into a physics-law-tier META `SPOKE1_COMPETITIVE_HEBBIAN_CONCEPT_ENCODER_SCALE_FREE_LAW_v1`, in parallel with Stage 1's storage-strategy META precedent (3-axis promotion 2026-07-02 evening).

---

## 1. Prior-work check (substrate-KB v2 concept-query, mandatory per USER 2026-07-01)

Three queries executed via `tools/substrate_query.sh` (v2 schema, chunk-content, tau=0.15):

**Q1: "competitive Hebbian sparse coding scale N_DIM capacity"** (confidence 0.381)
- rank 1: `Sparse coding capacity gain` cosine=0.381 from `notes/research_drill_substrate_task_complexity_ceiling_2x_2026-06-04.md`
- rank 2: `SPARSE-CODING-TOPK-CAPACITY -- sparse coding (f=0.05) capacity verification at N=2048-8192` cosine=0.331 from `notes/exp_dev_handoff_research_biological_precedents_animal_scales_2026-06-04.md`
- rank 3: `Sparse coding (neural)` cosine=0.316 from `data/substrate_index/science/atoms.jsonl`

**Q2: "Foldiak Kohonen sparse rate architectural constraint"** (confidence 0.345)
- rank 1-5: dictionary hits + off-topic architectural-constraint noise. NO substantive prior work under Foldiak/Kohonen framing.

**Q3: "concept encoder phase diagram brain-analog scale-free"** (confidence 0.282)
- rank 1: `Phase Diagram Context` cosine=0.282 from `preregs/2026-05-29_phase_region_cd_n4096.md`
- rank 2: `substrate_pc_encoder_family_phase_diagram_v1_seed_7` cosine=0.257 MIDDLE_BAND verdict from `data/exp_substrate_pc_encoder_family_phase_diagram_v1_seed_7/metrics.json`
- rank 4: `substrate_pc_encoder_family_phase_diagram_v1_seed_7_smoke` cosine=0.249 HARD_PASS verdict

**Prior-work overlap:**
- Sparse-coding capacity at scale (N=2048-8192): PRIOR WORK — `research_drill_substrate_task_complexity_ceiling` + `SPARSE-CODING-TOPK-CAPACITY` from June 2026. That drill established the topk sparsity rate f=0.05 works at N=2048-8192 for capacity. We can BUILD ON this — the mechanism has prior scaling evidence but at a different rate (f=0.05 vs v3-D's k=0.02) and a different backbone (topk capacity vs concept-encoder mechanism).
- PC-encoder-family phase diagram (2026-05-29): PRIOR ATTEMPT that got MIDDLE_BAND (smoke HP but FULL didn't clear); this was under the falsified PC-composition architecture. v3-D competitive-Hebbian only supersedes; that phase-diagram framework is our template but the mechanism claim is fresh.
- Foldiak/Kohonen lineage: NO substrate prior work. Fresh literature thread to atomize with the extension arc's landed CGs.

**Verdict:** Spoke 1 v3-D competitive-Hebbian phase-diagram is a NEW arc. Prior related work: sparse-coding-capacity drills (informative not overlapping); PC-encoder-family phase-diagram framework (methodological template, distinct mechanism).

## 2. Candidate axes (6 total)

Analogous to Stage 1 storage-strategy physics-law's closed axes (NPROP, N-scale, composition-depth, SCALE_FREE, TOPOLOGY_FREE):

| # | Axis | Range | Load-bearing? | Rationale |
|---|---|---|---|---|
| A1 | **N_DIM scale** | {2048, 4096, 8192, 16384} | HIGH | Mirrors Stage 1 SCALE_FREE claim; Stage 4 real-corpus needs N>=4096; storage-strategy law was promoted to SCALE_FREE by 2xN evidence. Same discipline needed for encoder. |
| A2 | **N_CONCEPTS cardinality** | {25, 50, 100, 200, 500} | HIGH | Stage 4 Wikipedia-ingest projects to 1000+ concepts; if mechanism collapses at C=200 the whole Spoke-1 architecture is ceiling-limited. This axis is the CAPACITY claim. |
| A3 | **SPC (sentences-per-concept)** | {10, 20, 40, 80, 160, 320} | HIGH | Real corpora have long-tail concept frequency; if the mechanism needs SPC>=100 to consolidate, low-frequency Wikipedia concepts fail. This axis is the DATA_HUNGER claim. |
| A4 | **Sparse-rate k** | {0.5%, 1%, 2%, 3%, 5%, 10%} | MED-HI | Architectural constraint from Foldiak/cortical microcircuit lit; if mechanism only works at exactly k=2% it's brittle. Robustness band matters for cortex integration where sparse-rate may drift. |
| A5 | **Semantic-similarity granularity** | corpus variants: {cat/kitten (near), cat/dog (mid), cat/tiger (far), cat/airplane (far)} | MED | Diagnostic — does mechanism resolve near-neighbor concepts, not just gross clusters? Interesting scientifically but not a Stage 2/3/4 gate. Defer to later probe. |
| A6 | **Composition depth downstream (K-way HRR bind)** | K in {1, 3, 5, 8} | LOW-MED | This tests DOWNSTREAM composition of encoder outputs (Stage 1 physics-law's axis, ALREADY CLOSED). Adds cross-composition evidence but is not the encoder-mechanism axis itself. Fold into cortex-composition CGs, not phase-diagram. |

## 3. Load-bearing axes recommendation

**Prioritize A1 + A2 + A3 + A4** for the physics-law META. Rationale:

- **A1 (N_DIM)** — mirrors Stage 1 SCALE_FREE precedent; USER strategic vision requires scale-free encoder for Stage 4 ingest.
- **A2 (N_CONCEPTS)** — the CAPACITY claim; without it we can't claim the encoder is a real-corpus-ready mechanism.
- **A3 (SPC)** — the DATA_HUNGER claim; without it we can't handle long-tail Wikipedia concepts (Stage 4 gate).
- **A4 (sparse-rate)** — the ARCHITECTURAL_INVARIANCE claim; without it the mechanism is brittle to cortex-integration sparse-rate drift.

Defer A5 (similarity granularity) to a post-META enrichment probe.
Skip A6 (composition-depth K-way) — already closed under Stage 1 META; encoder-output HDs feed downstream Stage-1 sharded FHRR which has the composition-depth axis closed.

## 4. Multi-cell probe strategy (A/B/C recommendation)

Options considered:

**Option A** — single-cell full grid (N_DIM × N_CONCEPTS × SPC × k). At 4x5x6x6=720 configs × 3 seeds = 2160 units → prohibitive (~40 wall-hours at 60s/unit on remote CPU).

**Option B** — 4 cells (one per axis, other axes fixed at v3-D baseline N=4096, C=50, SPC=40, k=2%), each with 4-6 axis-arms × 3 seeds = 12-18 units per cell = 4-8 min per cell FULL. Total: ~30-60 min compute, 4 CG events, 4 VET spawns. Clean per-axis diagnostic but 4x VET overhead.

**Option C (RECOMMENDED)** — hierarchical: first-cell 2-axis grid on the two most-critical axes (N_DIM × N_CONCEPTS), then orthogonal probes on the remaining axes. 3 cells total.
- Cell 1: **N_DIM x N_CONCEPTS grid** at {2048, 4096, 8192, 16384} × {25, 50, 100, 200} = 16 configs + ARM_NAIVE_WTA at N=4096 C=50 + ARM_RANDOM at N=4096 C=50 = 18 arms × 3 seeds = 54 units
- Cell 2: **SPC axis** at SPC ∈ {10, 20, 40, 80, 160, 320} at N=4096 C=50 k=2% = 6 arms × 3 seeds = 18 units
- Cell 3: **sparse-rate axis** at k ∈ {0.5%, 1%, 2%, 3%, 5%, 10%} at N=4096 C=50 SPC=40 = 6 arms × 3 seeds = 18 units

**Why Option C:**
- (a) Compute efficiency: 54+18+18 = 90 units vs Option B's 60-72 units — 25-50% more compute but delivers 2-axis interaction information Option B misses (does the N_DIM boundary shift with C?)
- (b) Diagnostic clarity: N_DIM × N_CONCEPTS grid reveals scaling law shape (is the boundary flat or a curve C_max(N)?). Axes-only sweeps miss this.
- (c) CG_META criterion: Cell 1 alone closes 2 axes at multi-seed HP → 2 CGs; Cell 2 + Cell 3 add 2 more → 4 CGs across 4 axes. Storage-strategy precedent is 3 CG_META for tier-4 promotion; we exceed comfortably.

**Dispatch strategy under Option C:**
- All 3 cells route to `remote_cpu_queue` (per v3-D compute-arch: NumPy-per-seed accumulator; GPU offers <10x speedup with kernel-launch dominance; not worth complexity).
- Cells 2 and 3 can dispatch IN PARALLEL to cell 1 (independent code paths; no shared state). Cell 1 is longest (~30-45 min FULL at N=16384); cells 2+3 (~10-15 min each) can complete while cell 1 runs.
- Post-landing, VET all 3 in one Skunkworks spawn using compact VET request format (~150 tok/landing).

## 5. First-probe cell design sketch (Cell 1)

**Anchor:** `substrate_concept_encoder_spoke1_phase_diagram_N_DIM_x_N_CONCEPTS_grid_v1_2026_07_02`

**Cell file:** `experiments/exp_substrate_concept_encoder_spoke1_phase_diagram_N_DIM_x_N_CONCEPTS_grid_v1_2026-07-02.py`

**Arms** (18 arms x 3 seeds = 54 units; cardinality_ok):
- 16 GRID arms: `ARM_CH_N{2048|4096|8192|16384}_C{25|50|100|200}` — competitive-Hebbian at grid point
- 1 NAIVE control: `ARM_NAIVE_WTA_N4096_C50` — falsified-2026-06-23 baseline at grid center for progress-control
- 1 RANDOM control: `ARM_RANDOM_N4096_C50` — chance control at grid center

**HP bands (HP_SCOPE: LOAD_BEARING on GRID arms; controls have their own low-signal bands):**

| ID | Applies to | Metric | Threshold | Rationale |
|---|---|---|---|---|
| HP1 | all 16 GRID arms | cat_kitten_cos_mean | >= 0.35 | Relaxed 0.05 from v3-D's 0.40 to allow signal-degradation at extremes (C=200, N=2048); if all 16 clear 0.35 the mechanism is broadly valid |
| HP2 | all 16 GRID arms | cat_airplane_cos_mean | <= 0.15 | Relaxed 0.05 from v3-D |
| HP3 | all 16 GRID arms | sparse_rate | in [0.010, 0.030] | Architectural |
| HP4 | all 16 GRID arms | intra_concept_cv | < 0.25 | Relaxed from v3-D's 0.20 for grid extremes |
| HP5 | central arm N=4096 C=50 | reproduces v3-D baseline within +/-0.05 | Cross-cell reproducibility (Gate D) |
| HP6 | RANDOM control | \|cat_kitten_cos\| | <= 0.05 | Chance |
| HP7 | NAIVE control | GRID_central_gap - NAIVE_gap | >= 0.15 | Progress over falsified baseline |
| SCALE_FREE band | across N_DIM axis at fixed C | std(cat_kitten_cos_mean) across N | <= 0.10 | INVARIANT-across-N is the scale-free claim; if boundary curve is flat this passes |
| CAPACITY_UNIVERSAL band | across C axis at fixed N | monotone-non-increasing cat_kitten_cos as C grows (allowed slope up to -0.005 per +25 concepts) | Ceiling-limit shape identified |

**HF bands (hard-fail):**
- Any GRID arm cat_kitten_cos < 0.20 → HARD_FAIL at that grid point (report as boundary)
- Any GRID arm sparse_rate outside [0.005, 0.10] → HARD_FAIL
- Central arm outside v3-D reproducibility band → HARD_FAIL (INVOCATION_MISMATCH, halt-and-investigate)

**Metrics per cell (per-arm × per-seed):**
- Existing v3-D metrics: cat_kitten_cos_mean, cat_airplane_cos_mean, gap, intra_concept_cv, sparse_rate, cat_kitten_cos_std, per-concept intra_std
- New phase-diagram metrics:
  - cross-N cv on cat_kitten_cos_mean (for SCALE_FREE band)
  - cross-C monotone slope (for CAPACITY_UNIVERSAL band)
  - grid-shape summary: 4x4 matrix of cat_kitten_cos_mean means; identify boundary corners

**Corpus:** synthetic controlled corpus extended from v3-D base (N_CONCEPTS variable):
- For C=25: subset first 25 concepts from v3-D 50-concept corpus
- For C=50: v3-D corpus as-is (reproducibility gate)
- For C=100: extend v3-D concept list with 50 more semantic-clustered concepts (5 more clusters of 10 each: animal-large, vehicle-water, tool, food, weather); SPC=40 per concept
- For C=200: further extend to 200 concepts (10 more clusters); SPC=40
- No cross-corpus contamination between grid points; each is generated fresh from the seed

**Compute estimate:**
- Per-unit wall at N=2048 ~ 30-60s; at N=16384 ~ 4x = 2-4 min (accumulator is O(SPC * N))
- C=200 adds ~4x concept-loop; O(C * N) accumulator scales
- Worst-case unit (N=16384, C=200): ~15-20 min per unit
- 54 units total; can be seed-parallelized but not arm-parallelized in-cell (write in serial with per-arm progress logging)
- **Expected FULL wall: 60-90 min** on remote_cpu (single-threaded); route to `overnight_queue` if wall estimate crosses 60 min at pre-flight smoke
- Smoke wall estimate: 90-180s (2 grid corners + 2 controls, N=2048 only)

**Route:** `overnight_queue` (wall > 30 min risk; conservative)

**HP_SCOPE:** LOAD_BEARING on GRID arms; NAIVE + RANDOM are progress/chance controls per META_RULE_L.

**cardinality_ok:** 18 arms × 3 seeds = 54 units.

**Est arc-time:** 90 min compute + 15 min VET = ~2 hrs to first landing.

## 6. Physics-law META target

**Name:** `T4/META_SPOKE1_COMPETITIVE_HEBBIAN_CONCEPT_ENCODER_SCALE_FREE_AND_CAPACITY_UNIVERSAL_LAW_v1`

**Composes atoms (target set on promotion):**
- `T3/EXP_spoke1_v3_D_competitive_hebbian_baseline_CG` (v3-D FULL landed — established mechanism)
- `T3/EXP_spoke1_phase_diagram_N_DIM_x_N_CONCEPTS_grid_v1_CG` (Cell 1 — closes A1 + A2)
- `T3/EXP_spoke1_phase_diagram_SPC_data_hunger_v1_CG` (Cell 2 — closes A3)
- `T3/EXP_spoke1_phase_diagram_sparse_rate_architectural_invariance_v1_CG` (Cell 3 — closes A4)

**Law statement (draft):** "Sparse competitive-Hebbian concept encoding via per-concept Hebbian accumulator + top-K WTA + sign-selection produces valid concept HDs (cat_kitten_cos >= 0.35, cat_airplane_cos <= 0.15, sparse_rate in [0.01, 0.03]) INDEPENDENT of N_DIM scale in [2048, 16384] AND INDEPENDENT of concept cardinality C in [25, 200] AND INDEPENDENT of SPC in [SPC_min, 320] AND INDEPENDENT of sparse-rate k in [k_min, k_max], where SPC_min and k-boundaries are identified by the phase diagram."

**Promotion criterion:** ≥3 axes at multi-seed HP; cross-axis cv on canonical metric (cat_kitten_cos_mean at central grid point) < 0.10. Storage-strategy META precedent (2026-07-02 evening) satisfied this criterion with 3 CGs + 1 base; we target 4 CGs (1 base + 3 axis-closing).

**Composition with Stage 1 physics-law:** Spoke 1 phase-diagram is a SEPARATE physics-law claim about the CONCEPT-ENCODER mechanism (competitive-Hebbian producing valid concept HDs). Stage 1 storage-strategy META is about SHARDED FHRR CLEANUP (downstream retrieval). They compose in the M3 cortex pipeline (Spoke 1 encoder produces concept HDs, Stage 1 sharded FHRR stores them for cleanup), but the physics-law atoms stand alone. Future cross-composition META possible: `M3_cortex_end_to_end_law_v1` composing both — deferred.

## 7. Timeline

**First-probe cell (Cell 1, N_DIM x N_CONCEPTS grid):**
- Pre-reg + smoke (`hdi_exp_dev` spawn): ~30 min
- Dispatch to `overnight_queue`: ~5 min
- Overnight FULL run: ~60-90 min
- Landed VET (`hdi_skunkworks` spawn) + atomization: ~15 min
- **Total for Cell 1: ~2-3 hrs (same-day if smoke starts by 22:00 local; landing 00:00-01:00 local)**

**Full arc:**
- Cell 1 (N_DIM x N_CONCEPTS): 2-3 hrs
- Cell 2 (SPC) + Cell 3 (sparse-rate) IN PARALLEL to Cell 1: 1-2 hrs each; can dispatch same-time as Cell 1 goes to overnight
- All 3 landed by 03:00 local
- CG_META composition VET (`hdi_skunkworks` spawn, single VET batch across 3 landings): ~30 min
- **Total arc time: ~4-6 hrs from Cell 1 pre-reg to CG_META promotion**

**Sequencing recommendation:**
1. WAIT for Spoke 1 v3-D FULL FULL HP landing (post-argparser-fix retry). This is the base atom. DO NOT dispatch phase-diagram cells until v3-D FULL is CG'd — otherwise the phase-diagram cells lack a stable reproducibility gate (Gate D). ETA v3-D FULL: main-thread work.
2. On v3-D FULL landing + Skunkworks VET pass, IMMEDIATELY dispatch Cell 1 via `hdi_exp_dev` spawn using this design as hand-off pointers (path to this note + anchor).
3. Simultaneously dispatch Cell 2 + Cell 3 via same `hdi_exp_dev` spawn (or 2 parallel spawns) since they share the corpus generation code.
4. Overnight all 3 to `overnight_queue`; poll for landings via `verify_landing.py` at 08:00 local.
5. Batch-VET all 3 landings via 1 Skunkworks fresh-spawn using compact VET format.
6. On 3-CG landing, Director composes CG_META atomization via strategy_scribe or hdi_skunkworks composed-atom spawn.

## 8. Design risks

- **R1 (grid-corner failure):** at N=16384, C=200 the mechanism may HF (extreme corner of phase diagram). This is FINE — the boundary IS the phase diagram; report as CAPACITY_CEILING atom and update law statement to `C <= C_max(N)`. Not a probe failure; a probe SUCCESS at identifying scope.
- **R2 (SPC minimum unknown):** Cell 2 may show mechanism collapses below SPC=20. This bounds the DATA_HUNGER claim. Report the boundary; not a failure.
- **R3 (sparse-rate off-optimum):** Cell 3 may show mechanism only works in tight k band. Bounds the ARCHITECTURAL_INVARIANCE claim; still atomizable as a bounded-invariance CG.
- **R4 (correlation between axes):** the N_DIM x N_CONCEPTS grid may reveal that the boundary is COUPLED (C_max scales with N). This is scientifically INTERESTING and shows Cell 1's grid design paid off relative to per-axis sweeps. Include as core META statement.

## 9. Top-line recommendation

**Design Option C (hierarchical, 3 cells):**
- Cell 1: N_DIM x N_CONCEPTS grid, LOAD-BEARING (closes 2 axes at once)
- Cell 2: SPC data-hunger axis
- Cell 3: sparse-rate architectural-invariance axis

**Anchor for first probe:** `substrate_concept_encoder_spoke1_phase_diagram_N_DIM_x_N_CONCEPTS_grid_v1_2026_07_02`

**Sequencing:** dispatch AFTER Spoke 1 v3-D FULL FULL HP lands and CG'd (base atom + Gate-D reproducibility gate required).

**Physics-law META target:** `T4/META_SPOKE1_COMPETITIVE_HEBBIAN_CONCEPT_ENCODER_SCALE_FREE_AND_CAPACITY_UNIVERSAL_LAW_v1` composing v3-D base + 3 axis CGs = 4 atoms; storage-strategy precedent satisfied and exceeded.

**Compose with Stage 1 META:** SEPARATE physics-law statement (different mechanism); FUTURE cortex-end-to-end META composes both.

**Compute route:** `overnight_queue` for Cell 1 (wall > 30 min risk); `remote_cpu_queue` for Cells 2, 3 (shorter wall).

**Arc time:** ~4-6 hrs from base-CG to phase-law META promotion (overnight-parallelizable).

---

*Filed by Research Director main-thread. Ready for hand-off to `hdi_exp_dev` on Spoke 1 v3-D FULL landing; use this note path as design pointer.*
