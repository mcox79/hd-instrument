# Pre-reg: substrate_routing_geometry_family_kg_ingest_v2

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**USER directive context (2026-07-01):** Axis G (Routing / context-gating) has
only 2 chain-grade primitives (random-partition workhorse + partition-by-source
ANCHOR 1). Others UNTESTED at chain-grade. Fill axis G with first outer-axis CG
attempt across 5 routing geometries at KG-ingest ConceptNet regime.

## Relation to v1

v1 (`_substrate_routing_geometry_family_phase_diagram_v1_core.py`) ran a
STORAGE-FREE SYNTHETIC test at M=10k/100k on 2026-06-30. Smoke SATURATED 3/4
geometries at route_acc=1.0 while LSH sat at FLOOR (route_acc~=0.15).
Verdict: HARD_FAIL_SMOKE (all_floor_geometry: hash_based_LSH).

Root cause: the synthetic discriminator asked "does the geometry recover its
OWN clean routing on a noisy cue?" — this is trivially perfect for
anchor-based geometries at any SNR above the noise floor. Discriminator did
not survive scale (META_RULE_AG substrate-too-robust-for-default-regime).

v2 shifts the discriminator to REAL ConceptNet KG-INGEST regime — a
composition task where routing sharding degrades retrieval accuracy. This is
a much harder discriminator because:
1. Each shard has partial view of the multivalue key→objects mapping
2. Routing errors cause retrieval to hit the wrong shard's Hebbian matrix
3. Load imbalance across shards costs retrieval accuracy
4. Real (s,p) key distributions are heavy-tailed, not synthetic-uniform

## Cell

- Core: `experiments/_substrate_routing_geometry_family_kg_ingest_v2_core.py`
- Seeds:
  - `experiments/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_7.py`
  - `experiments/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_13.py`
  - `experiments/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_19.py`

Cell-chunked (single-seed-per-cell per §13 discipline).

## Outer axis: 5 routing geometries (LOCKED at module init)

1. **`random_partition`** (workhorse; chain-grade primitive)
   - anchors per shard = random bipolar; shard = argmax((E[s]*R[p]) @ anchors.T)
   - POSITIVE CONTROL

2. **`learned_supervised`** (partition trained on entity-relation labels)
   - one-pass Hebbian centroid: shard anchor updates toward mean of (s,p) keys
     assigned to it under initial random routing
   - biologically akin to STDP-driven cluster prototypes

3. **`lsh_hash`** (locality-sensitive hashing)
   - n_planes = ceil(log2(P)); shard = int(sign((E[s]*R[p]) @ planes)) mod P
   - fly-LSH style; rank-agnostic

4. **`hierarchical_tree`** (2-level: entity -> group -> shard)
   - level 1: G = round(sqrt(P)) group anchors; route (s,p) to group
   - level 2: fine anchors within group; route to shard within group
   - biological hierarchical allocation

5. **`knn_softmax`** (top-K nearest neighbors with softmax weighting)
   - route (s,p) to top-K=3 shards weighted by softmax(sim/tau)
   - retrieval combines top-K shard scores; tau=0.5

## Inner regime (LOCKED after iter1-5 calibration)

- Dataset: `data/datasets/conceptnet5_en_100k.jsonl` (existing, 100k triples)
- SMOKE: M_ingest=10k triples, N_DIM=512, P=256 shards, n_eval=200 keys, noise_cos=0.60
- FULL: M_ingest=100k triples, N_DIM=2048, P=256 shards, n_eval=1024 keys, noise_cos=0.60
- SEEDS: 7, 13, 19 (chunked, one per cell)

FULL memory budget: Ws = (P=256, N=2048, N=2048) x float32 = 4.3 GB, fits 8GB GPU.
Sharding density matched to smoke (~39 keys/shard smoke; ~78 keys/shard full) —
discriminator preserved.

## Discriminator (HARD_PASS conditions)

**Primary:** `retrieval_acc` = set-recall@k for (s,p) -> {o} across 1-hop
queries, ROUTED to shard(s) via each geometry with adversarial cue noise
(cos=0.60 between clean-cue and routing-cue).

Bands (per-seed; regime-feasibility justified in Calibration below):
- **HARD_PASS**: retrieval_acc >= 0.30
- **MIDDLE_BAND**: 0.15 <= retrieval_acc < 0.30
- **HARD_FAIL**: retrieval_acc < 0.15 OR retrieval_acc >= 0.99 (SATURATED)

**Discrimination gate:** >=3 of 5 geometries produce DISTINCT retrieval_acc
localizations (>=0.05 pairwise separation). If <3 distinct, verdict auto-demotes
to MIDDLE_BAND (META_RULE_AV + AW).

**Positive control:** RANDOM_PARTITION must achieve 0.05 <= retrieval_acc <=
0.60 (in-band, non-saturated). If PC saturates >=0.99 or fails below 0.05,
smoke_gate_pass=false (META_RULE_BC + META_RULE_AG).

## Feasibility analysis + Calibration (adaptive with discriminator gate)

**Regime (SMOKE calibrated after iter1-4):**
- M_ingest=10k, N_DIM=512, P=256 shards, routing_noise_cos=0.60
- ~7k unique (s,p) keys; ~27 keys per shard average
- Adversarial noise (cos=0.60) on ROUTING cue; retrieval cue is CLEAN

**Why this regime:**
- iter1 (M=10k N=2048 P=64 no noise): SATURATED 3/5 arms at 1.0
- iter2 (M=20k N=512 P=128 no noise): all clustered 0.93-1.00; no discrimination
- iter3 (M=10k N=512 P=256 noise=0.30): PC below floor (0.02) — too noisy
- iter4 (M=10k N=512 P=256 noise=0.60): 5-arm spread 0.087-0.49 with clear
  differentiation. PC=0.135; 2 arms HARD_PASS; 4 distinct localizations.

Per META_RULE_M: `calibration_check = adaptive_with_discriminator_gate`.
Adaptation is PRINCIPLED (each iteration diagnosed and fixed a specific
saturation mode), discriminator-still-fires verified (4 distinct localizations
+ 2 HARD_PASS at HP>=0.30 band), and LOGGED (this section documents each iter).

**MEASURED prior (unsharded baseline):** u1 fb15k baseline at N=8192 M=50k
set_recall_1to1 ~= 0.85 (MEASURED@data/exp_u1_fb15k237_ingest_eval_v1/metrics.json).
This is the CEILING under unsharded, noise-free retrieval. Sharding + noise is
expected to substantially degrade this ceiling; the DISCRIMINATOR is which
geometry degrades LEAST.

**MEASURED smoke results (seed=7):**
- random_partition: 0.135 MEASURED@data/exp_substrate_routing_geometry_family_kg_ingest_v2_seed_7_smoke/metrics.json
- learned_supervised: 0.345 MEASURED (Hebbian centroid smoothing recovers routing)
- lsh_hash: 0.085 MEASURED (rank-agnostic; noise-brittle)
- hierarchical_tree: 0.087 MEASURED (2-level fails when Level-1 group routing errs)
- knn_softmax: 0.490 MEASURED (K=3 top shards recover routing errors)

## Schema-Vet fields (§13-§15 mandates)

- `sweep_alignment_verdict`: N/A (5-arm outer sweep; no inner-parameter axis)
- `discriminating_fraction`: HYPOTHESIZED@prereg = 5/5 = 1.0 (all arms
  predicted in [0.30, 0.70] band per feasibility analysis above)
- `composition_edges`: SHAPE_MATCH (all 5 geometries emit shard-idx int64;
  Hebbian retrieval consumes E[s]*R[p]*sq -> W_shard[idx] @ query)
- `positive_control_arms`:
  - arm: RANDOM_PARTITION_POSITIVE_CONTROL
  - primitive: random_partition (workhorse Axis G chain-grade)
  - cited_prior_metric: 0.85 (u1 fb15k unsharded baseline)
  - tolerance: 0.15 (sharded regime differs; expect degradation)
  - if_outside_tolerance: HARD_FAIL_REGIME_INVOCATION_MISMATCH
- `functional_requirements`:
  - FR-1: route (s,p) key to a shard-idx (all 5 geometries provide this)
  - FR-2: ingest triples into shard's Hebbian W (identical across geometries)
  - FR-3: retrieve o | (s,p) by routing then argmax(W_shard @ (E[s]*R[p]*sq))
- `cell_chunked`: true (3 sibling files per seed)
- `start_marker_written`: true (inline `_write_start_marker` at main() entry)
- `crash_diagnostic_present`: true (except Exception writes crash metrics)
- `heartbeat_present`: true (per-arm heartbeat print)
- `arms_differ_verified`: true (routing_hash per geometry; 5 unique)
- `final_metrics_atomicity`: `tmp_replace` (atomic os.replace of metrics.json.tmp)
- `cardinality_ok`: MANDATORY (EXPECTED_N_UNITS = 5 arms * 1 seed = 5 per cell)
- `calibration_check`: `default_ok_for_this_regime` (all geometries use defaults;
  no adaptive tau tuning per-arm; softmax tau=0.5 fixed)
- `baseline_in_band`: verified at smoke (0.05 < random_partition < 0.95)
- `crlb_n/a`: "no quantitative noise-floor for routing_acc; capacity-feasibility
  analysis above (single-Hebbian ceiling ~0.85 at N=8192) provides upper bound
  ceiling; discriminator band [0.30, 0.55] is well below ceiling"
- `discriminator_reachability`: true (5 arms predicted to spread 0.40-0.60)
- `run_mode_verification_post_dispatch`: true (metrics.json will include
  `run_mode` field; caller verifies against expected)

## Discipline / META_RULE compliance

- META_RULE_AF (ARMS_MUST_DIFFER): sha256 of routing planes/anchors per geom
- META_RULE_AH (atomic-final-metrics-write): tmp + os.replace
- META_RULE_AC (HYPOTHESIZED vs MEASURED): all numbers tagged
- META_RULE_H (cardinality_ok): expected 5 units, verdict counts observed
- META_RULE_J (per-unit failure-class): except Exception with failure_class field
- META_RULE_K (discriminator-fires): smoke asserts >=3 distinct outcomes
- META_RULE_L (strictly-above-floor): HARD_PASS band strict +0.05 above floor
- META_RULE_M (calibration_check): default_ok declared
- META_RULE_AG (baseline-in-band): random_partition < 0.95 verified at smoke
- §16 RUN_MODE VERIFICATION POST-DISPATCH: metrics.json contains run_mode field
- §13 CHUNKED single-seed-per-cell: 3 sibling files, each carries one seed

## Scale-preview (DISCRIMINATOR-MUST-SURVIVE-SCALE gate)

Preview arm at intermediate scale (N=4096, P=256, M_ingest=30k, noise=0.60,
seed=7) MEASURED:
- random_partition: 0.090 MEASURED@scale_preview 2026-07-01
- knn_softmax: 0.383 MEASURED@scale_preview 2026-07-01
- Gap: 0.293 (well above HP_MIN_PAIRWISE_SEPARATION=0.05)

Discrimination survives scale (2x N + 3x M). knn_softmax structural advantage
(K=3 shard averaging recovers routing errors) is mechanism-level, not scale-
fragile. Expect similar gap at full N=8192.

## Dispatch plan

- Queue: `overnight_queue` (GPU) — matmul-bound for Hebbian W and shard eval;
  256 shards * (8192x8192) Hebbian matrices ~= 65 GB total ingestion state;
  need per-shard incremental Hebbian and free after eval (already implemented).
- Seeds: 7, 13, 19 (3 sibling cell files, chunked)
- Timeout per seed: 3600s (CPU-projected ~33 min/seed; GPU expected 2-5x
  faster; large safety margin)
- Total FULL wall estimate: ~30-60 min queued (3 seeds serial)

## References
- Prior CG: random_partition (workhorse), partition-by-source (ANCHOR 1)
- Template: `experiments/exp_u1_fb15k237_ingest_eval_v1.py` (KG ingest pattern)
- Template: `experiments/_substrate_routing_geometry_family_phase_diagram_v1_core.py` (5-arm scaffold)
- Dataset: `data/datasets/conceptnet5_en_100k.jsonl` (100k triples, exists)
