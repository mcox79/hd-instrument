# Pre-reg: metric_dependence_top_k_semantic_v1 (Dim S)

**Filed:** 2026-07-01
**Cell-author:** hdi_exp_dev
**Anchor:** `metric_dependence_top_k_semantic_v1`
**Seeds:** 7, 13, 19
**Reference:** `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim S (P_deflated=0.45)

## Question

Prior substrate chain-grade evidence measures capacity boundary using **top-1 recall exclusively**. Real M3 workloads use top-K, cosine-similarity thresholds, or downstream-task quality. Same substrate may show MUCH higher effective capacity under top-5 / top-10 / cosine>=tau metrics than under exact top-1.

Direct test: sweep M/N load; at each load compute all 6 metrics from the SAME readout (no re-run per metric).

## Mechanism (single arm)

Cell D v2 dense-Hopfield READ-REPLACE:

1. Sample bipolar keys/vals (`M x N_RAW=64`).
2. DG-sparse-separate via k-WTA (`k=0.10*N_HIPPO`, `N_HIPPO=4096`).
3. Project to cortex space (`N_CORTEX=8192`), L2-normalize.
4. Softmax attention readout: `p = softmax(beta * q @ K^T) @ V`, adaptive beta from cosine margin (Cell D v2 formula).
5. For each of 500 query items, compute readout `p_n` ONCE, then evaluate 6 metrics:
   - `top1_recall`: argmax(p_n @ V^T) == target
   - `top5_recall`: target in top-5 argpartition
   - `top10_recall`: target in top-10 argpartition
   - `top50_recall`: target in top-50 argpartition
   - `cos05_recall`: sim(p_n, V[target]) >= 0.5
   - `cos08_recall`: sim(p_n, V[target]) >= 0.8

## Sweep

- `alpha = M/N in {0.10, 0.15, 0.20, 0.25, 0.30}` (5 loads; bracketing capacity wall).
- `N_CORTEX = 8192` fixed.
- 3 seeds (7, 13, 19); one cell per seed (CHUNKED-per-seed per META rule).
- Total FULL units: 5 loads x 6 metrics x 3 seeds = 90 metric-observations from 15 substrate builds.
- Note: metric axis is FREE (all 6 measured per landing); only 5 substrate builds per seed.

## Verdict gates

### HARD_PASS (any fires cross-seed = chain-grade)

- `HP_TOP1_WALL`: `top1_recall >= 0.80` at `alpha=0.15` (reproduces prior Cell D v2 baseline; sanity gate).
- `HP_TOPK_HIGHER`: `top10_recall - top1_recall >= 0.15` at `alpha=0.20` (top-K reveals capacity beyond top-1).
- `HP_SEMANTIC_HIGHER`: `cos05_recall - top1_recall >= 0.20` at `alpha=0.20` (semantic-similarity threshold reveals more).

### HARD_FAIL

- `HF_METRICS_IDENTICAL`: max metric spread across 6 metrics at any load `< 0.05` (metric axis flat; unexpected null).
- `HF_TOPK_CATASTROPHIC`: at `alpha=0.30`, `top1 < 0.30 AND top50 < 0.60` (top-K does not rescue; catastrophic collapse).

### MIDDLE_BAND

- No HP fires + no HF fires (metric axis measured but no strong asymmetric pattern).

## Chain-grade elevation

`CHAIN_GRADE_METRIC_DEPENDENCE_MAPPED` iff any HP fires in all 3 seeds AND cv < 0.15 on that HP metric across seeds.

## Substantive potential

- HP fires -> substrate has MUCH higher effective capacity for realistic M3 workloads. Prior CG numbers UNDER-estimate substrate capability by ~15-30 percentage points.
- HF_METRICS_IDENTICAL -> surprising null; would reshape what "capacity" means (metric-invariant).
- HF_TOPK_CATASTROPHIC -> substrate collapse mode is HARD; top-K rescue doesn't save it; forces alternative storage designs.

## CARDINALITY (META_RULE_H)

- FULL: `EXPECTED_N_UNITS = 5` per seed cell (5 loads).
- SMOKE: `EXPECTED_N_UNITS = 3` per seed cell (3 loads).
- Aggregate across 3 seeds handled externally (Skunkworks landed-VET).
- `cardinality_ok: bool` field set in metrics.json.

## CRLB / feasibility (META_RULE_AC + capacity-feasibility)

At `alpha=0.30`, `M=2458`:
- Binomial-CLT floor: `sigma_min = sqrt(0.25/M) = sqrt(0.25/2458) = 0.01009`. `THEORETICAL@binomial-CLT`.
- HP gap 0.15 (top-K) = ~15 sigma; well-reachable.
- HP gap 0.20 (semantic) = ~20 sigma; well-reachable.
- top-1 argmax-noise ceiling (Principle S): at `M=2458 << N=8192`, top-1 recall in `[0.0, 1.0]` band; discriminator reachable.
- `discriminator_reachability: True`.

## DISCRIMINATOR-MUST-SURVIVE-SCALE

- Smoke uses **full N=8192** with reduced load-sweep (3 points {0.10, 0.20, 0.30}) rather than smaller N; scale is preserved, resolution reduced.
- Smoke includes explicit PREVIEW arm at `alpha=0.30` full-N to confirm the heaviest-load discriminator fires.

## Baseline-in-band (META_RULE_AG)

- At `alpha=0.10` (M=819), top-1 expected high (near ceiling).
- At `alpha=0.30` (M=2458), top-1 expected in mid-band / low band per capacity-wall physics.
- Load sweep BRACKETS the wall (this is what we're measuring).
- Substrate saturation check: if top-1 at `alpha=0.10` is >= 0.95 AND top-1 at `alpha=0.30` is also >= 0.95, wall is above the sweep -> MIDDLE_BAND with note "capacity wall above alpha=0.30; extend sweep upward" (would trigger v2 with `alpha in {0.30, 0.40, 0.50, 0.60}`).

## arms-must-differ (META_RULE_AF)

- Single arm (dense-hopfield READ-REPLACE).
- Metric axis is a FREE MEASUREMENT SURFACE from one readout tensor `p_n`; not an arm axis.
- 6 metrics apply DISTINCT post-processing (argmax-top-K vs cosine-threshold) verified in `_selftest_metrics_family_arms_differ` at moderate noise (spread > 0.01).
- `arms_differ_exempted: [["single_arm_dense_hopfield_read_replace", "metric_axis_is_free_measurement_not_arm_axis"]]`.

## final_metrics_atomicity

`tmp_replace` — `metrics.json.tmp` then `os.replace()` (META_RULE_AH).

## Calibration-check (META_RULE_M)

`default_ok_for_this_regime` — bipolar synthetic keys/vals; same distribution as Cell D v2 reference where this substrate class is calibrated. No adaptive tuning.

## except SystemExit ordering

`except SystemExit: raise` then `except KeyboardInterrupt: raise` then `except Exception:` (never BaseException). Grep-gate verified pre-smoke.

## Prior-work check (substrate-KB concept-query)

- `bash tools/substrate_query.sh "metric top-1 top-K semantic similarity phase boundary discriminator"` returns top hits at cosine 0.32 ("Metric semantics" in prereg 2026-06-23 sparse_bipolar_substrate_lm_param_sweep_v1) and cosine 0.29 (various "Discriminator" atoms).
- **No prior atom at cosine > 0.30 for the concept "metric-dependence phase-diagram sweep at fixed substrate."** Genuinely novel.

## Prior related landings (coordinator flagged)

- `data/exp_g6_semantic_similar_fabrication_khop_v1/metrics.json` — tests **fabrication localization at fixed high cosine** (adversarial attack robustness); NOT a metric-axis sweep. Distinct scope.
- `data/exp_gap4v2_semantic_A_eval_280atoms_gpu_v1/metrics.json` and `..._gpu_v1/metrics.json` — tests **BGE-encoder semantic-search recall** on gap4v2 dataset with fixed top-K sweep (k in {5, 8, 12, 16}); tests **external LLM encoder** (`sentence-transformers/bge-large`), not substrate metric-axis. Adjacent methodology (top-K sweep) but different question (encoder choice, not substrate capacity metric). Distinct scope.
- Cited in metrics.json `prior_related_anchors` field.

## Route

- SMOKE: local (fast 3-load verification at full-N, per USER SMOKE-ONLY on local rule).
- FULL: `remote_cpu_queue` (numpy CPU; ~30-60 min per seed at 5 loads).
- Timeout: 1800s per seed.

## Files

- `experiments/_substrate_metric_dependence_top_k_semantic_v1_core.py` — shared core (mechanism, selftests, verdict).
- `experiments/exp_metric_dependence_top_k_semantic_v1_seed_{7,13,19}.py` — per-seed cell wrappers.

## Cross-references

- Cell D v2 CG landing (parent substrate primitive): `exp_cortex_hippo_dense_layer_M8192_v2_seed_*` (recall~=1.000 at M=8192 via adaptive-beta softmax attention).
- Hidden-dim research: `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim S.
- IR literature: recall@K, cosine-threshold semantic search metrics (standard IR/dense-retrieval evaluation).
