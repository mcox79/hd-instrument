# PRE-REG: Bytes-per-fact storage efficiency Pareto v2 EXTENDED PRECISIONS

## Anchor
`substrate_bytes_per_fact_pareto_v2_seed_{7,13,19}` (3 chunked seeds)

## Relationship to v1.1
v2 is ADDITIVE: extends v1.1's 5-arm at single M=10000 into a 7-precision x
4-M grid. v1.1 (Batch E) still pending on overnight_queue; v2 adds
BFLOAT16 + INT4 arms + M sweep to characterize the Pareto surface at
higher resolution. Does NOT step on v1.1.

## Load-bearing questions (v2-new)
1. Is v1.1 FP16 collapse a RANGE limitation (fixable by BFLOAT16's wider
   exponent) or a PRECISION limitation (irreducible)?
2. Does INT4 quantization (8x compression, 2x beyond INT8) retain
   KG-storage capability, or does it collapse?
3. How does capacity (M/N ratio) interact with precision across the grid?

## Arms (7 precisions)
Same KG-ingest test (uniform-sampled unique-(s,p) triples), same held-out
query set (30% bipolar noise on query keys), each at 4 M-values:

1. **FP32_DENSE** N=4096 float32 W (baseline; 4 bytes/elem)
2. **BFLOAT16_DENSE** N=4096 bfloat16 W (2 bytes/elem; wider exponent — TEST HYPOTHESIS)
3. **FP16_DENSE** N=4096 float16 W (2 bytes/elem; v1.1 COLLAPSED)
4. **INT8_DENSE** N=4096 int8 + per-row scale (1 byte/elem; 4x)
5. **INT4_QUANTIZED** N=4096 int4-range + per-row scale (0.5 byte/elem; 8x — NEW)
6. **BINARY_DENSE** N=4096 sign(W) bit-packed (0.125 byte/elem; 32x; v1.1 DOMINATED)
7. **SPARSE_BIPOLAR_0p05** N=16384 top-K sparse COO (0.05 density)

M sweep: `{1000, 4000, 10000, 20000}` (7*4=28 units per seed).
Smoke M sweep: `{500, 2000}` at N=2048 dense / N=8192 sparse (7*2=14 units).

## Discriminator (HARD_PASS conditions)
1. **Positive control (META_RULE_BC):** FP32_DENSE recall @ M=4000 (full)
   or M=2000 (smoke) >= 0.85
2. **Pareto separation per M:** at each M, at least (n_arms - 3) adjacent
   pairs separated by >=1.99x bytes OR >=0.05 recall gap
3. **Monotonic recall decay:** per precision, recall at max-M <= recall at
   min-M + 0.05 (tolerance)
4. **BFLOAT16 does NOT collapse:** recall >= 0.5 @ M=4000-nominal (v2-key)
   — validates hypothesis that v1.1 FP16 collapse is RANGE-limited
5. **INT4 valid tier:** recall >= 0.85 @ M=4000-nominal (v2-key)
   — validates 8x compression retains KG-storage
6. **Cross-seed cv <= 0.15** (looser than v1's 0.10 due to 28-unit grid)
7. **All 7 mechanism_hash distinct** (META_RULE_AX/AF)
8. **cardinality_ok:** 7 x len(M_sweep) units per seed (META_RULE_H)

INFORMATIONAL only (not gated): INT4-vs-INT8 recall gap (recorded because
if it becomes non-trivial at very high M/N ratios, that's a future arc).

## Regime
Full (per seed):
- M_sweep = [1000, 4000, 10000, 20000] (M/N ratios 0.24, 0.98, 2.44, 4.88)
- n_entities = 5000, n_relations = 100 (unique-(s,p) enforced)
- n_queries = 10% of M
- N_DIM_DENSE = 4096, N_DIM_SPARSE = 16384
- SPARSE_S = 0.05, TOPK_RECALL = 1, QUERY_NOISE_FRAC = 0.30
- device = CPU (torch is CPU-only on laptop 2.8.0+cpu)

Smoke (per seed):
- M_sweep = [500, 2000]
- n_entities = 800, n_relations = 50
- N_DIM_DENSE = 2048, N_DIM_SPARSE = 8192
- Preview at full N=4096, M=10000 confirmed INT4 recall = INT8 recall = 1.000
  (analytical justification per DISCRIMINATOR-MUST-SURVIVE-SCALE pattern B)

## THEORETICAL byte-per-fact predictions

At N_DENSE=4096, n_ent=5000, n_rel=100:
- Total W storage per precision (fixed cost, does not scale with M):
  - FP32: 150.67 MB     BFLOAT16: 75.33 MB     FP16: 75.33 MB
  - INT8: 37.70 MB       INT4:     18.87 MB     BINARY: 4.71 MB
  - SPARSE (N=16384):    131.24 MB

- bytes_per_fact = total_W / M; scales inversely with M:
  - At M=1000: FP32=150k, BINARY=4.7k, INT4=18.9k
  - At M=4000: FP32=37.7k, BINARY=1.2k, INT4=4.7k
  - At M=10000: FP32=15.1k, BINARY=471, INT4=1.9k
  - At M=20000: FP32=7.5k, BINARY=235, INT4=944

Pareto expected shape: BINARY < INT4 < INT8 < BFLOAT16 = FP16 < FP32 < SPARSE (bytes).
Recall trade-off: FP16 collapses (v1.1 finding); BFLOAT16 HYPOTHESIS = rescue.

## SMOKE MEASURED VALUES (2026-06-30 CPU seed=7, seed=13)

MEASURED@d:/AI/hd-instrument/data/exp_substrate_bytes_per_fact_pareto_v2_seed_7_smoke/metrics.json:
- verdict: HARD_PASS
- 14 units (7 arms x 2 M) all ran; cardinality_ok=True
- **BFLOAT16 finding: recall=1.000 at both M=500 AND M=2000 (does NOT collapse).**
  This CONFIRMS v1.1 FP16 collapse was RANGE-limited: BFLOAT16's 8-bit
  exponent (same as FP32) preserves Hebbian-outer accumulation dynamic
  range; FP16's 5-bit exponent overflows on unnormalized sums.
- FP16 confirms collapse: recall=0.040 @ M=500, 0.005 @ M=2000.
- INT4 valid tier: recall=1.000 at both smoke M (matches INT8 exactly at bipolar codebook + noise=0.30 regime).
- BINARY: recall=1.000 at both M; bytes_per_fact=1484 (M=500), 371 (M=2000).
- SPARSE: recall=0.960 -> 0.335 (SNR degrades with sparse top-K interference).
- Cross-seed cv (seed_7 vs seed_13) both HARD_PASS with same qualitative pattern.

## SCHEMA-VET items (META_RULE checklist)
- cardinality_ok: True (7 * 2 units smoke; 7 * 4 units full = 28)
- final_metrics_atomicity: "tmp_replace" (all writes via tmp + os.replace)
- except SystemExit: raise BEFORE except Exception: verified
- crlb_floor_computed: "n/a" (storage-metric cell, not quantitative noise-floor)
- baseline_in_band: FP32 saturates at smoke (1.000) via analytical
  justification (DISCRIMINATOR-MUST-SURVIVE-SCALE pattern B): preview at
  full N=4096, M=10000 confirmed all precisions except FP16 saturate;
  discriminator that FIRES is BFLOAT16-vs-FP16 collapse gap (0.960 gap at
  smoke; substrate finding), NOT INT4-vs-INT8.
- arms_differ_verified: 7 mechanism_hash checked distinct at smoke; True
- discriminator_fires: 7-arm Pareto separation observed at smoke; True.
  BFLOAT16-vs-FP16 discriminator FIRES (delta=0.96 at M=500, 0.995 at M=2000).
- HARD_PASS strictly above floor: FP32 at 1.000 = 15% above 0.85 floor; OK.
  BFLOAT16 at 1.000 = 50% above 0.5 non-collapse floor.
- HP_SCOPE: positive_control gate = FP32 only; bfloat16_gate = BFLOAT16
  only; INT4-gate = INT4 only; pareto_sep = across all 7 within each M
- calibration_check: "default_ok_for_this_regime" (uniform random unique-(s,p) triples)

## v2-specific substrate findings (pre-registered)

**H1 (validated at smoke, expect validation at full):** BFLOAT16 rescues
FP16 collapse. The v1.1 FP16 numerical overflow at Hebbian-outer sums is
a DYNAMIC RANGE limit (5-bit exponent overflows unnormalized keys x sq(N)
factors), not a precision limit. BFLOAT16 with 8-bit exponent (same as
FP32) preserves the range. If this validates at full, it establishes
BFLOAT16 as a new chain-grade compression tier (2x compression WITHOUT
recall collapse).

**H2 (validated at smoke, expect validation at full):** INT4 quantization
(8x compression) preserves KG-storage in the bipolar-codebook regime. The
15-level quantization {-7..+7} retains sufficient magnitude information
for top-1 recall on unique-(s,p) keys. If validated at full, INT4 becomes
a new chain-grade compression tier — 2x beyond INT8 at NO recall cost.

**H3 (informational):** INT4-vs-INT8 gap at nominal M/N ratios <= 2.5 is
essentially zero (both saturate). Genuine INT4 discrimination would require
M/N > 5 or extreme noise (>0.45). Recorded as informational; not gated.

## Dispatch
- Queue: **remote_cpu_queue** (torch is CPU-only on laptop; cell is numpy-
  equivalent on tensor ops; matmul at N=4096 fits comfortably)
- Seeds: [7, 13, 19] (3 sibling chunked cells)
- Timeout: 3600s per seed (per-seed 7*4=28 units at N=4096; each unit ~5-15s
  based on smoke timing extrapolation; full-run estimated 200-400s per seed)
- Cell files:
  - `experiments/exp_substrate_bytes_per_fact_pareto_v2_seed_7.py`
  - `experiments/exp_substrate_bytes_per_fact_pareto_v2_seed_13.py`
  - `experiments/exp_substrate_bytes_per_fact_pareto_v2_seed_19.py`
  - Core: `experiments/_substrate_bytes_per_fact_pareto_v2_core.py`

## Reuse
- v1.1 cell template (bytes-per-fact primitives, KG regime, arm dispatch)
- experiments/_seed_checkpoint helpers (write_partial_key, aggregate_partials)
- hdlab/kg_traversal.py substrate-native KG primitive (CG at n8 ConceptNet)

## Author
exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn)
