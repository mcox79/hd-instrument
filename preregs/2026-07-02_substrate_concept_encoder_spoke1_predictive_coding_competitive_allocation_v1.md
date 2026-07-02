# Prereg: substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1

**Filed:** 2026-07-02 (Stage 2 Spoke 1 kickoff, post brain-best-in-class strategic pivot)
**Anchor:** `substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1`
**Cell:** `experiments/exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1.py`
**Design note:** `notes/design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md`
**USER strategic anchor:** `project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02`

## Motivation

Substrate's current "concepts" are random-codebook HDs. Only 1 of 6 brain-property criteria satisfied (compositional). Spoke 1 builds the base of a substrate-owned concept encoder producing sparse-bipolar HDs that EMERGE from data via LOCAL learning rules — no backprop, no borrowed embeddings, no transformer attention.

## Prior-work check

Substrate-KB concept-query 2026-07-02 top hits (cosine desc):
1. `project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23` (cosine 0.378) — this cell IS Spoke 1 of the Path C direction.
2. `research_drill_realtime_multimodal_biology_3x_2026-06-09` sec 8.2 predictive coding compression (0.363).
3. `BIO/predictive_coding` primitive atom (0.347).
4. No prior mechanism cell at cosine >= 0.40.

Director surface (Orchestrator, in-thread 2026-07-02): `sparse_engram_allocation_smoke_v1` (prereg 2026-06-23) FALSIFIED naive collision-minimizing K-winners candidate sampling at N=4096 M=10K on all 3 predicted lifts. This cell AVOIDS that mechanism: WTA here is top-K-then-sign on per-dimension E-consistency via `np.partition` threshold, NOT candidate-set sampling.

## Functional requirements (Gate E per META_RULE §15)

Substrate concept encoder must produce concept HDs that:

1. **Discriminate** semantically related from unrelated concepts (cat/kitten > cat/airplane in cosine).
2. **Emerge from data** — no per-concept codebook lookup at encode time.
3. **Are sparse-distributed** — few dims active per concept (target ~1-3%).
4. **Are stable across contexts** — same concept in different sentences produces similar HDs.
5. **Use only local learning rules** — no backprop, no global error signal.

Primitives mapped:
- (1) via mean-centered context bundling + PC-learned W projection.
- (2) via aggregation over per-concept sentence contexts (no concept-ID → HD lookup table).
- (3) via top-K per-dimension consistency mask (competitive allocation).
- (4) via mean-context aggregation (multiple sentences average to a stable concept representation).
- (5) via `hdlab.predictive_coding` (Rao-Ballard residual-gated Hebbian) and `hdlab.excitability`-style per-dim consistency scoring.

## Arms (cardinality_ok: 5 arms x 3 seeds = 15 units)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_RANDOM_BASELINE | Per-concept random bipolar HD | Chance control |
| ARM_CHAR_TRIGRAM_BASELINE | hdlab.char_trigram_encoder on concept name only | Surface-form baseline |
| ARM_PREDICTIVE_ONLY | char+positional + Rao-Ballard PC on shared W; dense output | Ablation: PC without competitive |
| ARM_COMPETITIVE_ONLY | char+positional + per-concept top-K mask; sparse output | Ablation: competitive without PC |
| ARM_FULL_HYBRID (load-bearing) | PC + competitive allocation composed | Full composition |

`arms_differ_verified: True` (SHA-256 digest of per-arm concept-HD matrix; ARMS-MUST-DIFFER gate at smoke).

## HP bands (HP_SCOPE: LOAD_BEARING on ARM_FULL_HYBRID; RANDOM_at_chance on ARM_RANDOM_BASELINE)

**HARD_PASS** (all must be true, mean across 3 seeds):
- `hyb_cat_kitten_cos_ge_HP_min`: ARM_FULL_HYBRID cat/kitten cos >= 0.30
- `hyb_cat_airplane_cos_le_HP_max`: ARM_FULL_HYBRID cat/airplane cos <= 0.15
- `hyb_gap_ge_HP`: ARM_FULL_HYBRID (cat_kitten - cat_airplane) >= 0.30
- `hyb_sparse_rate_in_HP_band`: ARM_FULL_HYBRID sparse_rate in [0.010, 0.030]
- `hyb_pop_gap_ge_HP`: ARM_FULL_HYBRID intra_cluster_mean - inter_cluster_mean >= 0.15
- `hyb_composition_lift_ge_HP`: ARM_FULL_HYBRID gap - max(ARM_PREDICTIVE_ONLY gap, ARM_COMPETITIVE_ONLY gap) >= 0.05
- `random_baseline_at_chance`: |ARM_RANDOM_BASELINE cat/kitten cos| <= 0.05

**HARD_FAIL** (any true, mean across 3 seeds):
- ARM_FULL_HYBRID cat/kitten cos < 0.15
- ARM_FULL_HYBRID sparse_rate outside [0.005, 0.10]
- ARM_FULL_HYBRID composition gap-lift < -0.05

**MIDDLE_BAND:** neither all-HP nor any-HF.

## SCHEMA-VET pre-dispatch fields

- `cell_chunked`: false (single-cell 3-seed loop; wall time ~2-3 min per seed at N=2048 smoke)
- `start_marker_written`: true
- `crash_diagnostic_present`: true (tmp+os.replace atomic write; except Exception, not BaseException; SystemExit re-raise)
- `heartbeat_present`: false (short cell; per-seed print-progress with `sys.stdout.reconfigure(line_buffering=True)`)
- `defensive_error_checking`: `"short_cell_exempt_stage_progress_via_stdout_line_buffered"`
- `arms_differ_verified`: true (SHA-256 hash-set)
- `final_metrics_atomicity`: `"tmp_replace"`
- `cardinality_ok`: true (EXPECTED_N_UNITS = 15)
- `calibration_check`: `"default_ok_for_this_regime"` (single hyperparameter set; synthetic controlled corpus; no tuning-for-pass iteration)
- `crlb_n/a`: emergent-representation cell; sparse_rate is architectural via top-K quantile mask, not a noise-floor CRLB regime
- `sweep_alignment_verdict`: N/A (no sweep axis in v1)
- `discriminating_fraction`: N/A (no sweep axis)
- `composition_edges`: SHAPE_MATCH (bipolar sentence HD -> bipolar prediction; residual is 3-valued difference; all operate on same n_dim; no adapter needed)
- `positive_control_arms`: ARM_PREDICTIVE_ONLY reproduces plain-PC on centered contexts; ARM_COMPETITIVE_ONLY reproduces plain-WTA on centered contexts. ARM_RANDOM_BASELINE and ARM_CHAR_TRIGRAM_BASELINE are pinned baselines.
- `progress_logging`: `"line_buffered_stdout"`

## Compute architecture

- Class: sequential-CPU numpy per-seed (batched matmul within arm, sequential across arms + seeds)
- Justification: N=2048 smoke, N=8192 full. Per-sentence outer-product update is unavoidable in this Rao-Ballard formulation. Wall time per seed at N=2048 = ~1-2 min; total smoke ~5 min. Not a GPU-batching candidate at this scale; the fixed-order PC update loop has genuine sequential dependency (W_t+1 depends on W_t and sentence order).
- Storage strategy: SHARDED — one HD per concept in a `[N_CONCEPTS, n_dim]` matrix, no bundling.

## Corpus

Synthetic controlled corpus, generated in-cell (smoke = full):
- 25 semantic clusters, 2 concepts per cluster = 50 concepts
- 40 sentences per concept = 2000 sentences
- Template: "the {concept} {verb}s the {object}" (5 templates rotated)
- Per-cluster 5 verbs + 5 objects (shared within cluster; distinct across clusters)
- Ground truth: `(concept_id, cluster_id)` per sentence

## Metrics per arm x seed

- `cat_kitten_cos`: paired within-cluster cosine (cluster 0)
- `cat_airplane_cos`: paired cross-cluster cosine (clusters 0 vs 10)
- `dog_puppy_cos`, `dog_boat_cos`: second paired within/cross for robustness sanity
- `intra_cluster_cos_mean`: mean cosine of concept-pair-in-cluster across all 25 clusters
- `inter_cluster_cos_mean`: mean cosine of first-concept-of-each-cluster vs first-concept-of-each-other-cluster
- `intra_concept_cv`: std/mean of intra_cluster cosines
- `n_concepts_stable`: count of clusters where intra_cluster_cos > 0.6
- `sparse_rate`: fraction of nonzero entries across all concept HDs
- `arm_digest`: SHA-256 of concept-HD matrix (ARMS-MUST-DIFFER)

## Compute wall estimate

- Per-seed at N=2048 spc=40: ~50-100s (dominated by PC-gated Hebbian outer-product updates)
- Total 3-seed smoke: ~3-5 min
- N=4096 smoke variant: ~3-4x wall = ~10-15 min
- FULL N=8192: ~15-20x wall = ~30-60 min

## Compute route

- Smoke: `local_cpu_queue` (per USER SMOKE_ONLY_LOCAL_CPU 2026-07-01)
- Full: `remote_cpu_queue` after smoke HP verified

## Post-verdict routing

- **HARD_PASS:** file CG; extract composed encoder to `hdlab/concept_encoder.py`; fire Spoke 2 (temporal contiguity).
- **HARD_FAIL:** file CG_HONEST_NEGATIVE; options for v2: (i) different sparsity target, (ii) deeper PC hierarchy, (iii) add ARM_NAIVE_WTA_SAMPLING as prior-work reference-control, (iv) alternative Hebbian rule (Oja normalization).
- **MIDDLE_BAND:** file MM_TENTATIVE; v2 with parameter tuning documented in prereg amendment.

## What CG at Spoke 1 unlocks

- Substrate has learned concept HDs from data (emerged, not designed)
- Sparse-distributed representation (architectural constraint)
- Semantically similar concepts cluster (structure emerges)
- Compositionally usable via HRR bind (M1.9 mechanism becomes REAL with substrate-learned concept HDs, not random-codebook proof)
- USER's Stage 2 substrate-load ritual becomes semantically-grounded
