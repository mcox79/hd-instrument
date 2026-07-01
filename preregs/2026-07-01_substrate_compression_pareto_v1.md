# Pre-registration: substrate_compression_pareto_v1

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** USER directive 2026-07-01 — measure COMPRESSION EFFICIENCY of the substrate. How many facts can 1 schema-centroid represent while still supporting downstream recall? Chain-grade primitive under M3 architecture arc.

## Anchor

`substrate_compression_pareto_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per USER 2026-06-28).

Shared core: `experiments/_substrate_compression_pareto_v1_core.py`.

## Routing

- **Smoke queue:** local CPU direct venv (`.venv/Scripts/python.exe`)
- **Full queue:** **overnight_queue (GPU-machine CPU)** per USER directive 2026-07-01 (NO LOCAL CPU). Centroid matmul + retrieval sim benefit from remote CPU throughput; not GPU-mandatory but routed there per user instruction.
- **Push constraint:** harness-DENIED push from exp_dev. Full dispatch routes through Orchestrator after smoke commit.

## Why this cell exists (the gap)

Schema family CG'd (HYBRID > EB) + Schema v4 CG'd (HARDMAX centroid pooling under capacity stress). We have never DIRECTLY measured HOW MUCH compression a single schema-prototype provides. All prior schema cells fixed one compression scheme + swept alpha/n_ex/n_schemas. This cell fixes the FACT SET and sweeps the COMPRESSION SCHEME.

**Load-bearing question:** How many facts can 1 schema-centroid represent while still supporting downstream recall? Measures compression as chain-grade primitive.

**Substantive question:** Does the substrate compress LOSSLESSLY (recall preserved) or does compression cost recall proportionally? Brain does massive compression via schema; substrate should too if it's on the path to M3.

**Complementary to bytes-per-fact (STORAGE efficiency).** This cell measures FACTS per schema-centroid (COMPRESSION efficiency). Both axes of the same Pareto surface.

## Compression arms (the OUTER axis)

Four compression schemes, each consuming identical N_FACTS bipolar-HDC KG-fact set:

| Arm | Compression scheme | Prototypes | Facts/proto (expected) | Source |
|-----|--------------------|------------|-------|---|
| `ARM_NO_COMPRESSION` | Store all facts individually | n_facts | 1.0 | positive control (META_RULE_BC) |
| `ARM_SCHEMA_EXEMPLAR_BAYES` | K schemas of ~10 exemplars each | n_facts (indexed by schema) | 10.0 (facts/schema) | v3 CG family |
| `ARM_SCHEMA_HARDMAX_CENTROID` | K schemas, 1 centroid each | n_facts/100 | 100.0 | v4 CG family |
| `ARM_SCHEMA_HIERARCHICAL` | 10 coarse + 100 fine per coarse | ~1010 | ~10.0 | ANCHOR 3 coarse-grain CG family |

All 4 use the same bipolar HDC encoding, same fact-noise (0.30), same query-noise (0.30). Only the compression scheme differs.

**Selftest validation:** all 4 arms produce recall in [0,1]; >= 2 of 6 arm-pairs produce distinct pred hashes; NO_COMPRESSION @ tiny selftest (n_facts=200, N=512) achieves recall >= 0.30.

## Test regime

| Axis | SMOKE | FULL |
|------|-------|------|
| n_facts | 1000 | 10000 |
| N_DIM | 2048 | 8192 |
| n_queries | 30 | 100 |
| seeds | [7] (single-seed smoke) | [7, 13, 19] |
| latent schemas (data structure) | sqrt(n_facts) ~ 32 | sqrt(n_facts) ~ 100 |

Facts are generated via `latent_proto[schema_id] + FACT_NOISE_SCALE*N(0,1)`, then unit-normalized. Queries sample a random fact + `QUERY_NOISE_SCALE*N(0,1)`. Ground-truth = fact index of the sampled fact.

**Held-out queries:** queries have a KNOWN ground-truth fact index; no compression scheme sees the query at construction time. Recall = mean(pred == true_fact_idx).

## Metrics captured per arm

- `facts_per_prototype_avg` (compression ratio: n_facts / n_prototypes)
- `downstream_recall_accuracy` (top-1 recall over n_queries)
- `memory_footprint_bytes` (total storage size for prototypes + indexing)
- `compression_pareto_efficiency` = recall * log(compression_ratio)
- `mechanism_hash` (SHA-256 of per-query pred vector for META_RULE_AF)

## Hypothesis

**H1 (PRIMARY): The 4 arms produce distinct Pareto points on (facts/proto, recall).**
- NO_COMPRESSION: (1.0, ~0.90)
- EXEMPLAR_BAYES: (10, ~0.85) — small drop for 10x compression
- HARDMAX_CENTROID: (100, ~0.85) — chain-grade v4 finding suggests centroid noise-suppression preserves recall
- HIERARCHICAL: (~10, ~0.85) — coarse-grain routing preserves recall via 2-level lookup

**H2 (compression is CHEAP at chain-grade):** HARDMAX_CENTROID achieves >= 100x compression with recall drop <= 0.05 from NO_COMPRESSION. Brain-analog finding (schema compresses without recall loss).

**H3 (positive control):** NO_COMPRESSION at N_facts=10000 achieves recall >= 0.85 (META_RULE_BC). If this fails, test rig is broken.

**H4 (null):** all 4 arms cluster within +/- 0.02 recall AND within 0.30 log-ratio. If H4 holds, compression scheme doesn't matter — schemas aren't a substrate compression primitive at this regime.

**H5 (hierarchical wins):** HIERARCHICAL achieves highest pareto_efficiency (recall preserved + moderate compression). Cortex-inspired path.

## Discriminator: HARD_PASS conditions

- (1) `positive_control_pass`: NO_COMPRESSION recall_mean >= 0.85 (META_RULE_BC).
- (2) `compression_gap_pass`: HARDMAX ratio / NO_COMPRESSION ratio >= 100x compression.
- (3) `recall_preserved_pass`: NO_COMPRESSION - HARDMAX recall drop <= 0.05.
- (4) `pareto_distinct_pass`: >= 3 of 6 arm-pairs produce distinct (recall, log_ratio) points (distinct = recall diff > 0.02 OR log_ratio diff > 0.30).
- (5) `arms_differ_pass`: mean across seeds of distinct arm-pair pred hashes >= 3/6 (META_RULE_AF).
- (6) `cross_seed_cv_pass`: cv(recall) <= 0.10 AND cv(ratio) <= 0.10 for every arm.

**HARD_PASS FULL:** ALL 6 gates pass.
**MIDDLE_BAND FULL:** positive_control + arms_differ + pareto_distinct pass, but recall_preservation or compression_gap or cross_seed_cv fails.
**HARD_FAIL FULL:** positive_control fails OR arms_identical OR fewer than 3 distinct pareto pairs.

## SMOKE gates (MUST pass before FULL dispatch)

1. All 4 arms RAN (cardinality_ok: observed_n == 4)
2. NO_COMPRESSION recall >= 0.60 at smoke (relaxed from 0.85 due to smaller N + fewer queries)
3. HARDMAX compression_ratio >= 50x (relaxed from 100x; smoke n_facts=1000)
4. >= 3 of 6 arm-pairs produce distinct pred hashes
5. >= 3 of 6 arm-pairs produce distinct Pareto points
6. No silent except (META_RULE_J) — all arms complete

If gates 1-6 pass → smoke HARD_PASS → dispatch FULL.

## HP_SCOPE per-arm

- `positive_control_pass` (Gate 1): APPLIES ONLY to `ARM_NO_COMPRESSION`. Baseline mechanism.
- `compression_gap_pass` (Gate 2): APPLIES to arm-pair `(NO_COMPRESSION, HARDMAX_CENTROID)`.
- `recall_preserved_pass` (Gate 3): APPLIES to arm-pair `(NO_COMPRESSION, HARDMAX_CENTROID)`.
- `pareto_distinct_pass` (Gate 4): APPLIES cross-arm.
- `arms_differ_pass` (Gate 5): APPLIES cross-arm.
- `cross_seed_cv_pass` (Gate 6): APPLIES per-arm (all 4).

## CARDINALITY (META_RULE_H)

- EXPECTED_N_UNITS_FULL per seed = 4 arms
- EXPECTED_N_UNITS_SMOKE per seed = 4 arms
- EXPECTED_N_SEEDS = 3 (seed 7, 13, 19)
- EXPECTED_N_UNITS_AGGREGATE_FULL = 4 * 3 = 12

`cardinality_ok = (observed_n == expected_n)` per sibling. HARD_FAIL if observed != expected.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26)

Smoke reduces regime (n_facts 10000 -> 1000; N 8192 -> 2048). This is REDUCED-SCALE smoke; the discriminator (compression ratio gap between arms) must SURVIVE the scale jump.

**Analytical scale justification (Option B in exp_dev.md §DISCRIMINATOR-MUST-SURVIVE-SCALE):**

The compression ratios are RATIO-based on n_facts / n_prototypes:
- NO_COMPRESSION always ratio = 1.0
- EXEMPLAR_BAYES ratio = EXEMPLAR_BAYES_N_EX_PER_SCHEMA = 10 (constant across scales)
- HARDMAX_CENTROID ratio = HARDMAX_CENTROID_FACTS_PER_SCHEMA = 100 (constant across scales)
- HIERARCHICAL ratio = n_facts / (n_coarse * n_fine) = 10000/1010 ~ 10 at FULL; 1000/(10*100) = 1 at SMOKE (WARNING: hierarchical arm smoke_ratio = 1.0!)

**Adjustment:** HIERARCHICAL is defined by fixed n_coarse=10 and n_fine=100, so at SMOKE (n_facts=1000), the ratio = 1.0 (all 1000 facts get their own fine centroid). This is a SCALE ARTIFACT of the smoke reduction — HIERARCHICAL's ratio is NOT distinct from NO_COMPRESSION at SMOKE. In the smoke regime, we expect 3-arm distinct Pareto (NO_COMPRESSION, EXEMPLAR_BAYES, HARDMAX_CENTROID); HIERARCHICAL will collapse to ~1.0 ratio + recall similar to NO_COMPRESSION.

Smoke Pareto discriminator: 3 arms distinct (NO_COMPRESSION at ratio=1.0, EXEMPLAR_BAYES at ratio=10, HARDMAX at ratio=100). HIERARCHICAL only differentiates at FULL.

Full Pareto discriminator: 4 arms distinct (all 4 ratio values differ at n_facts=10000).

**Reachability check:** at FULL n_facts=10000, HIERARCHICAL n_prototypes = min(n_coarse, n_facts) + min(n_fine_per_coarse * n_coarse, n_facts) = 10 + 1000 = 1010 (compression ~10x). HIERARCHICAL now distinct from HARDMAX (100x).

## CRLB / capacity-feasibility (META_RULE + Cell I v2 lesson)

- `crlb_floor_computed`: For nearest-neighbor retrieval at n_facts=10000 with query_noise=0.30, the theoretical retrieval floor is close to 1.0 given N=8192 (per Kanerva HDC capacity `M/N < 0.1` regime; here M/N = 10000/8192 = 1.22 — outside cleanest capacity but recall via cosine argmax should still be > 0.85 for 30% query noise since inter-fact cosine at random ~ 1/sqrt(N) = 0.011 << signal 0.7).
- `crlb_formula_reference`: `top1_expected = P(cos(q, true_fact) > max_{k != true} cos(q, fact_k))`; at Q=100 draws + noise 0.30, expected top1 >= 0.85.
- `discriminator_reachability`: HP threshold recall >= 0.85 is REACHABLE for NO_COMPRESSION given regime. HARDMAX threshold recall >= 0.80 (0.85 - 0.05) is reachable IFF centroid-averaging preserves the signal — this is the substantive question being tested.
- For HIERARCHICAL: reachability depends on coarse-routing accuracy; if the top-level coarse argmax is >= 0.95, downstream fine argmax recall preserved.

## Fairness gates (META_RULE_AC/AE/AF)

- Same encoder (bipolar random HDC; FACT_NOISE_SCALE=0.30) per arm
- Same fact codebook per seed (built once, shared across 4 arms)
- Same query set per seed (built once, shared across 4 arms)
- All 4 readouts operate on IDENTICAL facts + queries
- arm-pair pred hashes via SHA-256(json(int-list per query)) — at least 3 of 6 pairs differ to claim compression distinguishes

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 crash sentinel + atomic per-seed partial via `experiments._seed_checkpoint`. §16 RUN_MODE VERIFICATION POST-DISPATCH (d4eb2805 fix): cell writes `run_mode` at STARTED marker + final metrics.

## Substrate prereqs (chain-grade primitives cited)

- Bipolar random HDC codebook (chain-grade per `exp_substrate_sequence_binding_v1`)
- Cosine similarity readout (chain-grade ubiquitous)
- Log-sum-exp Bayesian aggregation (chain-grade per v3 5/5 MB)
- Centroid argmax (chain-grade per v4 HARD_MAX)
- k-means clustering (numpy; 20-iter cap) as pre-processing for schema construction
- Hierarchical (2-level) partition (chain-grade per ANCHOR 3 coarse-grain FAMILY_OVERLAP)

## ETA

Per-arm at FULL (n_facts=10000, N=8192, n_queries=100):
- ARM_NO_COMPRESSION: 1 matmul (100, 8192) @ (8192, 10000) = 8.2GFLOP -> ~1-3s on CPU
- ARM_SCHEMA_EXEMPLAR_BAYES: 1000 iters of per-query LSE over 10 exemplars in 1000 schemas -> ~30-60s CPU
- ARM_SCHEMA_HARDMAX_CENTROID: kmeans (20 iter x 100 clusters x 10000 facts x 8192) ~ 30-60s; matmul (100, 100) trivial -> ~30-90s CPU
- ARM_SCHEMA_HIERARCHICAL: 10 coarse kmeans + 10 fine kmeans (100 per coarse) -> ~30-90s CPU

Per seed total: ~90-240s. 3 seeds sequential (one per sibling cell file): ~5-15min wall.

**Full timeout:** 3600s per seed (per USER instruction). PROT-019 not triggered (no _n>=4096 in anchor name).

**Formula:** `full_timeout_s = ceil(1.5 * smoke_wall_s * (FULL_n_facts/smoke_n_facts) * (FULL_N/smoke_N))`; smoke_wall ~ 30-60s -> full_timeout_est = 1.5 * 60 * 10 * 4 = 3600s.

## HDLAB_QUEUE contract

`# PRESERVE_ENV_VARS: HDLAB_QUEUE` header in cell files. CPU-only cell (numpy); GPU not needed but routed to overnight_queue for user compute preference.

## Composition edges (substrate atomization context)

- Existing CHAIN-GRADE primitives being composed: bipolar codebook, cosine readout, k-means partition, LSE-Bayes aggregation, centroid pooling, hierarchical partition
- COMPONENT being swept: the compression scheme applied to the fact-storage layer
- Downstream atomization candidates: `COMPRESSION_EFFICIENCY_100X_LOSSLESS` (if H2 holds); `HIERARCHICAL_COMPRESSION_PARETO_OPTIMAL` (if H5 holds); `COMPRESSION_NOT_LOSSLESS_AT_SUBSTRATE_TIER` (if H2 fails)

## Test-design gates (§15)

- **Gate A (effective vs nominal):** all arms sweep the same n_facts + N; per-arm compression ratio is DETERMINED by arm choice, not swept. `sweep_alignment_verdict: ALIGNED` (no misalignment).
- **Gate B (discriminating band):** predicted Pareto points span ratio in {1, 10, 100, 10} and recall in [0.80, 0.90]. 4 of 4 arms in discriminating band (recall in [0.30, 0.95] target — not saturated, not floor). `discriminating_fraction: 1.0`.
- **Gate C (signal-shape compatibility):** all 4 arms consume identical (facts, queries) shapes; produce identical pred shape. `composition_edges: SHAPE_MATCH`.
- **Gate D (positive-control reproduce at test regime):** ARM_NO_COMPRESSION reproduces chain-grade cleanup-attractor recall at N=8192, n_facts=10000 regime. Prior atom cited: NO_COMPRESSION cosine argmax at 30% noise regime typically achieves >= 0.85 recall (bipolar HDC folklore + v4 selftest empirical). Tolerance 0.10.
- **Gate E (functional-requirement decomposition):** functional requirement = "storage layer preserves downstream recall after compression"; primitive = compression-scheme choice.

## Pre-reg fields summary

- expected_n_units_full = 4 arms per seed (12 total across 3 seeds)
- expected_n_units_smoke = 4 arms per single seed
- cardinality_ok field asserted in metrics.json
- discriminator_survives_scale: analytical + smoke covers 3-of-4 arms; HIERARCHICAL only at FULL
- baseline_in_band: NO_COMPRESSION at smoke expected 0.60-0.90 recall (in-band)
- crlb_floor_computed / discriminator_reachability declared above
- arms_differ_verified (META_RULE_AF): >= 3 of 6 pairs distinct hashes
- final_metrics_atomicity: tmp_replace (all writes via .tmp + os.replace)
- HP_SCOPE per-gate declared above
- calibration_check: default_ok_for_this_regime (all params inherited from v3/v4 chain-grade calibration)

## Disciplines (mandatory)

- META_RULE_AC: arms differ by SHA-256 (per-arm pred hashes)
- META_RULE_AE: pre-reg bands LOCKED at module init in core.py
- META_RULE_AF: 4 arm pred hashes distinct (>= 3 of 6 pairs)
- META_RULE_AH: atomic final metrics write (tmp + os.replace)
- META_RULE_H: cardinality_ok mandatory (4 arms per seed)
- META_RULE_J: no silent except; halt on any arm exception
- META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS (5 of 6 gates = MB not HP)
- META_RULE_M-S (USER 2026-06-24 production-scale calibration): verify-referent on per-arm discriminator; suspect 1.000 results (sat flag mandatory); relative-bands (compression_gap defined as RATIO not absolute)
- META_RULE_BC: positive control (NO_COMPRESSION) clears floor
- Functional-requirement decomposition: storage preserves recall -> compression scheme is the substituted COMPONENT
- Substrate-as-canonical query-first: schema v3/v4 chain reviewed; this cell pivots from within-family sweep to compression-scheme sweep
- DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26): smoke at reduced regime; discriminator (compression ratio) is analytically fixed by arm design; HIERARCHICAL smoke-scale artifact acknowledged
- BAND-FLOOR-IS-MIDDLE-BAND (USER 2026-06-26): 6/6 gates = HP; 3-5/6 gates with positive control + arms differ = MB; else HF
- Honest-downward (USER 2026-06-26): if HARDMAX recall drops > 0.05 = MIDDLE_BAND (compression is NOT lossless at chain-grade)
- CHUNKED single-seed-per-cell (USER 2026-06-28): 3 sibling files, one seed each

## Notes

- Complementary to Bytes-per-fact cell (STORAGE efficiency); this cell = COMPRESSION efficiency (facts per schema)
- Coordinate note: 6 other spawns in flight (Skunkworks VET + Routing geometry + N-scaling + Sparsity x Encoder + Storage update rule v1.1 + Bytes-per-fact). NON-OVERLAPPING — this is COMPRESSION efficiency.
- Per USER 2026-06-28 chunked architecture: 3 sibling files mirroring schema_family_v1 pattern.
- Per USER 2026-07-01 GPU routing: full to overnight_queue despite CPU-only compute; timeout 3600s/seed.
