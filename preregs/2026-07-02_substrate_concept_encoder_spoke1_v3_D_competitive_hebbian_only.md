# Prereg: substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02

**Filed:** 2026-07-02 (Stage 2 Spoke 1 v3-D; drop PC entirely per 6/6 convergent evidence)
**Anchor:** `substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02`
**Cell:** `experiments/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026-07-02.py`
**Predecessors:**
- v1 (anchor `..._v1`; smoke MEASURED@`data/exp_..._v1_smoke/metrics.json`)
- v2 (anchor `..._v2`; smoke MEASURED@`data/exp_..._v2_smoke/metrics.json`; empirical drill established PC does NOT earn complexity)
- Empirical drill: MEASURED@`notes/research_spoke1_pc_earning_complexity_investigation_2026-07-02.md`

## Why v3-D (drop PC from Spoke 1)

6/6 convergent evidence (5-domain drill + empirical diagnostic sweep) established:

1. **Empirical variant A pre-mask compose** (v2 architecture): at W_ALPHA in {0.10, 0.5, 1.0},
   Delta_intra_cluster_cos_mean = {-0.038, -0.173, -0.238} vs COMPETITIVE_ONLY.
   PC monotone-DEGRADES within-cluster consolidation at every tested weight.
   MEASURED@`notes/research_spoke1_pc_earning_complexity_investigation_2026-07-02.md` sec 2.3.

2. **Empirical variant B post-mask sign-modulation**: null intervention. Delta_intra = -0.002
   at W_ALPHA in {0.5, 1.0}. PC's sign contribution never flips top-K signs because raw
   accumulator magnitude dominates on those dims by construction. MEASURED same source.

3. **Seed 29 pathology root cause**: PC's W develops asymmetric amplification (cat 3.4x,
   kitten 1.2x cross-projection); top-K hijacked into airplane-space at high W_ALPHA.
   Intrinsic mechanism failure mode, not a seed-luck artifact.

4. **v2 apparent HP HARD_PASS is Goodhart on the `gap` summary metric**: cross-corpus
   anti-correlation goes up while within-cluster consolidation goes down; net gap looks
   preserved, mechanism is worse.

5. **5x drill 5-domain convergent (2026-07-02)**: math/info theory, neuroscience/biology,
   ML/AI literature, brain-analog, engineering — all 5 drills convergent that PC is
   redundant with WTA for concept encoding at the flat regime; ML/AI drill recommends
   competitive-only (Foldiak/Kohonen/SoftHebb) baseline.

6. **Brain analog check**: cortical maps (V1 SOM), Quiroga concept cells (medial temporal
   lobe), cerebellar granule cells (Marr 1969 / Albus 1971) — all competitive-Hebbian
   in brain WITHOUT a PC layer at this level. PC is legitimately brain-analog for
   HIERARCHICAL higher-level prediction (Rao-Ballard 1999); it belongs in Spoke 2+
   where temporal contiguity / trace-rule / one-shot indexing makes hierarchy earn its
   complexity. Spoke 2 design: `notes/design_stage2_concept_encoder_spoke2_temporal_contiguity_slow_feature_analysis_2026-07-02.md`.

Under the brain-best-in-class strategic anchor (USER-LOCKED 2026-07-02), a mechanism
that degrades the primary target cannot ship. V3-D drops PC entirely and reframes
Spoke 1 as its brain-analog identity: sparse competitive-Hebbian encoder.

## v3-D design

**Architecture (per empirical drill Q3 recommendation):**

1. **Character + positional encoding** (existing `hdlab/char_positional_encoder.py`,
   unchanged from v1/v2 — Kanerva-style char+pos HRR bind; brain analog: V1/primary
   sensory cortex).

2. **Competitive-Hebbian layer**:
   - Per-concept Hebbian outer-product accumulator (equivalent to online update with
     one-hot concept indicator I_c: W[c, :] += lr * x per sentence).
   - Winner-take-all: top-K on the dim axis by per-concept magnitude
     |a_c[d]| / n_c (k = 2% of N_DIM).
   - Sign selection from a_c on selected dims -> ternary bipolar HD.

3. **Optional: anti-Hebbian lateral inhibition** (Foldiak 1990) — winners in earlier
   concepts penalize dim selection in later concepts via LI_ALPHA * dim_use_count.

4. **Sparse-bipolar concept HD output** (2% dims non-zero, ±1) — sharded per-concept.

**NO PC LAYER.** PC deferred to Spoke 2 (temporal contiguity / trace rule).

## Arms (cardinality_ok: 5 arms x 3 seeds = 15 units)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_RANDOM_BASELINE | Random bipolar HD per concept | Chance control |
| ARM_CHAR_TRIGRAM_BASELINE | trigram encode of concept name | Surface-form baseline |
| ARM_COMPETITIVE_HEBBIAN | char+positional + per-concept Hebbian acc + top-K WTA + sign | **LOAD-BEARING** (Foldiak/Kohonen base) |
| ARM_COMP_HEB_LATERAL_INHIBITION | + anti-Hebbian lateral inhibition (LI_ALPHA=0.05) | Stretch (report-only) |
| ARM_NAIVE_WTA_SAMPLING | K-winners collision-minimizing sampling (2026-06-23 falsified) | Progress control |

## HP bands (v3-D)

| ID | Applies to | Metric | Threshold | Rationale |
|---|---|---|---|---|
| HP1 | ARM_COMPETITIVE_HEBBIAN | cat_kitten_cos_mean | >= 0.40 | v2 baseline MEASURED 0.522 (COMPETITIVE_ONLY); floor 0.40 with 3-seed CV margin |
| HP2 | ARM_COMPETITIVE_HEBBIAN | cat_airplane_cos_mean | <= 0.10 | v2 baseline MEASURED +0.015; ceiling 0.10 for 3-seed margin |
| HP3 | ARM_COMPETITIVE_HEBBIAN | sparse_rate | in [0.010, 0.030] | architectural via top-K quantile mask; target 2% |
| HP4 | ARM_COMPETITIVE_HEBBIAN | intra_concept_cv | < 0.20 | invariance stable across seeds; v2 COMPETITIVE_ONLY intra_std=0.006/mean=0.474 -> cv~0.013 (comfortably in band); relaxed from spec's 0.15 per USER concern about small-N variance |
| HP5 | ARM_COMPETITIVE_HEBBIAN | gap - NAIVE_WTA_gap | >= 0.15 | Mechanism progress over 2026-06-23 falsified baseline |
| HP6 | ARM_RANDOM_BASELINE | \|cat_kitten_cos_mean\| | <= 0.05 | At chance |
| HP7 | ARM_CHAR_TRIGRAM_BASELINE | \|cat_kitten_cos_mean\| | <= 0.15 | Low surface-form signal (trigram carries morphological overlap for kitten/cat) |

**Report-only (no HP gate):**
- ARM_COMP_HEB_LATERAL_INHIBITION Delta_gap vs ARM_COMPETITIVE_HEBBIAN
- ARM_COMP_HEB_LATERAL_INHIBITION Delta_intra_cluster_cos_mean vs ARM_COMPETITIVE_HEBBIAN

Any positive lift counts as bonus evidence for lateral inhibition mechanism; null or
negative is fine (cell still HARD_PASSes on the base competitive-Hebbian arm).

## HF bands (looser)

- ARM_COMPETITIVE_HEBBIAN cat_kitten_cos < 0.20 -> HARD_FAIL (mechanism broke)
- ARM_COMPETITIVE_HEBBIAN sparse_rate outside [0.005, 0.10] -> HARD_FAIL
- ARM_COMPETITIVE_HEBBIAN gap - NAIVE_WTA_gap < -0.05 -> HARD_FAIL (mechanism regresses)

## HYPOTHESIZED per-arm at smoke (N_DIM=2048, 3 seeds)

Extrapolating from v2 MEASURED@`data/exp_..._v2_smoke/metrics.json` COMPETITIVE_ONLY arm
(the v2 arm-code is bit-identical to v3-D's ARM_COMPETITIVE_HEBBIAN):

| Arm | cat_kitten_cos | cat_airplane_cos | gap | intra_mean | sparse_rate |
|---|---|---|---|---|---|
| ARM_RANDOM_BASELINE | ~0.00 | ~0.00 | ~0.00 | ~0.00 | 1.00 (dense) |
| ARM_CHAR_TRIGRAM_BASELINE | ~0.10 | ~0.00 | ~0.10 | small pos | 1.00 (dense) |
| ARM_COMPETITIVE_HEBBIAN | 0.45-0.55 | ~0.02 | ~0.50 | 0.45-0.50 | 0.020 |
| ARM_COMP_HEB_LATERAL_INHIBITION | 0.40-0.55 | -0.05 to +0.05 | 0.45-0.55 | 0.40-0.50 | 0.020 |
| ARM_NAIVE_WTA_SAMPLING | 0.00-0.10 | ~0.00 | 0.00-0.15 | ~0.00 | 0.020 |

HP5 (`ARM_COMPETITIVE_HEBBIAN - ARM_NAIVE_WTA gap >= 0.15`) HYPOTHESIZED margin
comfortable (~0.35-0.50 predicted).

## Functional requirements (Gate E per META_RULE §15)

1. **Discriminate** semantically related from unrelated concepts (cat==kitten far from
   cat==airplane). Primitive: sparse competitive-Hebbian coding.
2. **Emerge from data** — no per-concept codebook; concept HDs computed from context
   accumulator. Primitive: Hebbian outer-product update.
3. **Sparse-distributed** — target ~1-3% dims non-zero. Primitive: top-K quantile mask.
4. **Stable across contexts** — same concept in different sentences -> similar HD.
   Primitive: mean-context aggregation with per-dim consistency thresholding.
5. **Local learning rules only** — no backprop. Primitive: Hebbian outer product.
6. **Decorrelated across concepts** (aspirational, tested by lateral inhibition arm).
   Primitive: anti-Hebbian lateral inhibition (Foldiak 1990).

## Gate A -- effective vs nominal parameter audit

Parameters swept: none (no sweep axis; single hyperparameter configuration per arm).
- sweep_alignment_verdict: **N/A** (no sweep)

## Gate B -- bracket includes discriminating band

Not a sweep cell. Discriminating band applied to single-point config: HP thresholds
above are strictly above HF thresholds by >= 5% of band width (META_RULE_L).
- discriminating_fraction: **N/A** (no sweep)

## Gate C -- signal shape compatibility audit

Composition edges (this cell only, no cross-primitive composition):

| From | To | A_output_shape | B_input_shape | Verdict |
|---|---|---|---|---|
| char_positional_encoder | competitive_hebbian | bipolar HD (N,) | HD accumulator input (N,) | SHAPE_MATCH |
| char_positional_encoder | naive_wta_sampling | bipolar HD (N,) | HD mean-ctx input (N,) | SHAPE_MATCH |
| char_positional_encoder | lateral_inhibition | bipolar HD (N,) | HD accumulator input (N,) | SHAPE_MATCH |

No SHAPE_MISMATCH.

## Gate D -- reproduce prior chain-grade primitive at test regime

- **char_positional_encoder** (existing hdlab primitive): unchanged from v1/v2;
  reproduced as-is; not a chain-grade candidate needing reproduction.
- **char_trigram_encoder** (existing hdlab primitive): unchanged; baseline only.
- **Sparse competitive-Hebbian coding**: no prior chain-grade atom in substrate; this
  cell IS the establishing evidence. Positive-control comparison to v2's
  ARM_COMPETITIVE_ONLY (bit-identical arm code) via cross-seed reproducibility;
  MEASURED v2 COMPETITIVE_ONLY across seeds {11, 17, 23, 29, 37}: cat_kitten_cos
  mean=0.522 std=0.040. v3-D expected mean at same regime (N=2048, spc=40, seeds
  {11, 17, 23}) within +/-0.05 tolerance.
- positive_control_arm: ARM_COMPETITIVE_HEBBIAN reproduces v2's COMPETITIVE_ONLY
  at cited regime; tolerance 0.05; if outside -> INVOCATION_MISMATCH investigation.

## Gate E -- functional requirement decomposition present

See "Functional requirements" section above.

## Cell template compliance

- `arms_differ_verified`: **True** (META_RULE_AF hash-test at smoke gate + selftest)
- `final_metrics_atomicity`: **tmp_replace** (META_RULE_AH)
- `except SystemExit: raise BEFORE except Exception`: **True**
- `crlb_n/a`: emergent-representation cell; sparsity architectural not noise-floor
- `baseline_in_band` at smoke: RANDOM ~0, TRIGRAM ~0.10 (both in [0.05, 0.95] band)
- `HP_SCOPE`: LOAD_BEARING on ARM_COMPETITIVE_HEBBIAN (5 HP gates); baselines have
  their own low-signal HP gates; LATERAL_INHIBITION and NAIVE_WTA are report-only
- `cardinality_ok`: EXPECTED_N_UNITS = 5 arms * 3 seeds = 15
- `discriminator survives scale`: v2 MEASURED COMPETITIVE_ONLY at N=2048 (intra=0.474)
  and N=4096 (same cell, similar band); mechanism is O(N) accumulator, no
  scale-saturation regime. Scale-sentinel selftest at N=8192 asserts no NaN before
  any smoke.
- `progress_logging`: line_buffered_stdout (cell short; wall < 15 min so no long-cell
  discipline gate)
- `calibration_check`: default_ok_for_this_regime (synthetic corpus; no per-arm tuning)
- `cell_chunked`: **False** (3 seeds run in-cell; wall short; runner-death loss risk
  is small vs chunking overhead for this fast cell; if wall grows > 30 min in FULL
  reconsider chunking)
- `start_marker_written`: **True**
- `crash_diagnostic_present`: **True**
- `heartbeat_present`: **False** (cell wall < 15 min; per-seed print progress at
  each arm suffices; not gated per §13 rule since interval < 60s natural)
- `defensive_error_checking`: passed_all_4_patterns (except one heartbeat since fast)

## Compute architecture

- Class: **(b) sequential-CPU with justification**
- Justification: NumPy per-seed accumulator over ~2000 sentences at N=2048. Dominant
  cost is Hebbian accumulator (2000 * 2048 float ops per arm per seed) + one
  full-matrix topk per concept (50 * 2048 float compare + partition). Total ~50M
  float ops per seed. Per-seed wall MEASURED@v2 approx 30-60s at N=2048. GPU batching
  offers < 10x speedup for O(50M) ops per seed with kernel-launch overhead dominating;
  not worth the complexity for this scale. If N or spc grows > 4x, revisit.
- storage_strategy: **sharded_per_concept_hd_ternary_bipolar** (50 concept HDs,
  each 2048/4096 dims; not bundled — appropriate for concept-encoder where each
  concept has its own retrievable HD; composition happens downstream)

## Timeout estimate

- smoke wall MEASURED@v2 (which had 6 arms x 5 seeds = 30 units, N=2048, spc=40):
  ~178s = 3 min total (from v2 smoke). v3-D has 5 arms x 3 seeds = 15 units (50%
  fewer units) at same N=2048 spc=40 -> ~90-120s smoke expected.
- smoke --timeout 900s (15 min) with 5x headroom.
- full wall estimate: 15 units at N=4096 (2x N, so ~2x per-arm compute) -> ~180-240s;
  full --timeout 1800s (30 min) with 5x headroom.

## Rollback / notes

- If ARM_COMPETITIVE_HEBBIAN does not reproduce v2 COMPETITIVE_ONLY within 0.05, halt
  and investigate arm-code drift (should be bit-identical to v2 arm).
- If ARM_COMP_HEB_LATERAL_INHIBITION crashes / produces NaN: report but do NOT block
  HARD_PASS on COMPETITIVE_HEBBIAN arm (LI is stretch/report-only).
- If smoke MIDDLE_BAND: iterate on either K target (1% vs 2% vs 3%) or LI_ALPHA
  (0.02 / 0.10 / 0.20) — but these are for the LATERAL_INHIBITION arm which is
  report-only. Base COMPETITIVE_HEBBIAN has a single K target = 2%.
- If ARM_COMP_HEB_LATERAL_INHIBITION shows POSITIVE lift (+ delta_intra or
  + delta_gap vs COMPETITIVE_HEBBIAN): atomize as bonus evidence supporting Foldiak
  1990 mechanism in HD-substrate; consider promoting to LOAD_BEARING in v3-E.

## Substrate-KB concept-query prior-work check (MANDATORY per USER 2026-07-01)

Executed as part of empirical drill investigation (2026-07-02 evening; see
`notes/research_spoke1_pc_earning_complexity_investigation_2026-07-02.md` section 1):

- Query "predictive coding hierarchy composition Hebbian sparse coding brain":
  top hits at cosine 0.499 / 0.418 / 0.387 (all substrate research atoms on PC in
  hierarchies; NOT overlap with THIS cell's mechanism claim).
- Query "Foldiak Kohonen competitive Hebbian coding invariance": top match 0.303
  (dictionary hit; no substantive prior work). NEW LITERATURE THREAD in substrate.
- Query "hyperdimensional predictive coding capacity limit": top hits 0.364 / 0.321
  / 0.321 (PC-hierarchy atoms; NOT competitive-Hebbian).

**Prior-work verdict**: v3-D competitive-Hebbian only is NOVEL in the substrate.
Prior v2 PC-composition arm is FALSIFIED (this cell's raison d'etre). Foldiak/Kohonen
lineage is fresh literature to atomize on landed HP.

## Rehab plan on FULL PASS (post-USER-approval-only)

- Atomize ARM_COMPETITIVE_HEBBIAN as `Spoke1_v3_D_competitive_hebbian_concept_encoder_v1`
  under `concept_encoder` class.
- Atomize the empirical drill negative result on PC-in-Spoke-1 as
  `PC_does_not_earn_complexity_in_flat_concept_encoding_v1` (relative-negative,
  under 2x-drill discipline).
- Hand off to Spoke 2 (temporal contiguity / trace-rule) design; existing note at
  `notes/design_stage2_concept_encoder_spoke2_temporal_contiguity_slow_feature_analysis_2026-07-02.md`.
- If ARM_COMP_HEB_LATERAL_INHIBITION shows positive lift: fold into v3-E as
  LOAD_BEARING for a decorrelated-sparse-coding variant.
