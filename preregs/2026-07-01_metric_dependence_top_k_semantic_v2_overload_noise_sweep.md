# Pre-reg: metric_dependence_top_k_semantic_v2 (Dim S — OVERLOAD+NOISE respec)

**Filed:** 2026-07-01
**Cell-author:** hdi_exp_dev
**Anchor:** `metric_dependence_top_k_semantic_v2_overload_noise_sweep`
**Seeds:** 7, 13, 19
**Reference:** `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim S (P_deflated=0.55; increased from v1 0.45 because v1 rules out underload — v2 tests INTERFERENCE regime where dense-Hopfield theory PREDICTS metric-family differentiation)
**Supersedes:** `2026-07-01_metric_dependence_top_k_semantic_v1.md` (v1 HF_METRICS_IDENTICAL; substrate saturating in underloaded regime; escape mechanism = overload alpha + query noise sigma)

## v1 result summary + respec justification

v1 landed **HF_METRICS_IDENTICAL** at underloaded dense-Hopfield: all 6 metrics = 1.000 at alpha in {0.10, 0.20, 0.30} (smoke) + wall-probe extension confirming saturation up to alpha=8.0 (M=65k patterns @ N=8192). Physics reading: Cell D v2 dense-Hopfield READ-REPLACE with adaptive-beta softmax attention has exponential capacity in N; at alpha in [0.10, 8.0] with bipolar-iid keys, readout `p_n ≈ V[target]` exactly, collapsing the 6-metric family to a single number.

v1 hand-off note (`notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v1_HF_METRICS_IDENTICAL_2026-07-01.md`) recommended three respec options:
- (1) Push alphas INTO overload
- (2) Add QUERY_NOISE axis
- (3) CORRELATED_KEYS

v2 combines (1) + (2). Prior-work check from substrate-KB confirms genuine novelty (no prior cell at cosine > 0.30 for "overload regime metric-differentiation dense Hopfield with query noise"). Load-bearing citation: NeurIPS 2023 Sparse Hopfield (arxiv:2309.12673) — dense-bipolar noise impact is EXPONENTIAL in load, so overload + noise together are the theoretically-predicted differentiation regime.

## Question

Does the 6-metric family collapse (v1 finding) persist when substrate is pushed into overload alpha AND query noise sigma? Canonical prediction: at (alpha≈1.5, sigma≈0.7) the interference-explosion + softmax margin degradation should force top-1 collapse (argmax lottery) while top-K survives (target in K-neighborhood) and cosine breaks (readout norm degraded). If the family still collapses uniformly, that's a substrate-genuine-null (HF_UNIFORM_COLLAPSE); if metric family opens up, that's the metric-dependence hypothesis (HP fires).

## Mechanism (single arm; grid = alpha × sigma)

Cell D v2 dense-Hopfield READ-REPLACE — SAME primitive as v1 for mechanism-class parity:

1. Sample bipolar keys/vals (`M x N_RAW=64`).
2. DG-sparse-separate via k-WTA (`k = 0.10*N_HIPPO`, `N_HIPPO=4096`).
3. Project to cortex space (`N_CORTEX=8192`), L2-normalize.
4. Adaptive beta from cosine margin (Cell D v2 formula).
5. **NEW in v2:** For each stored key `q_i`, form noisy query
   `q_noisy = L2normalize(q_i + sigma * randn(N_c))`, then read out
   `p = softmax(beta * q_noisy @ K^T) @ V` and L2-normalize.
6. Compute all 6 metrics from same readout tensor:
   - `top1_recall`, `top5_recall`, `top10_recall`, `top50_recall`
   - `cos05_recall`, `cos08_recall`

500 queries per cell (per pre-reg; N_QUERY=500 same as v1).

## Sweep grid

- `alpha = M/N in {0.30, 0.50, 1.00, 1.50}` — from underload edge to well over AGS wall (0.14N). At alpha=1.5, M=12288 patterns @ N=8192.
- `sigma in {0.0, 0.3, 0.5, 0.7}` — query-noise multiplier on Gaussian noise vector added to L2-normalized query BEFORE renormalization.
- `N_CORTEX = 8192` fixed.
- 3 seeds (7, 13, 19); one cell per seed (CHUNKED-per-seed per META rule).
- Total FULL units: 4 × 4 = 16 (alpha, sigma) cells per seed. Aggregate 3 seeds => 48 cell observations.

## Verdict gates

### HARD_PASS (any fires cross-seed = chain-grade)

- `HP_METRIC_SPREAD_UNDER_STRESS`: at `(alpha=1.0, sigma=0.5)`, `max_metric_recall - top1_recall >= 0.20` (top-K survives when top-1 collapses; canonical metric-family differentiation).
- `HP_TOP_K_SURVIVES`: at `(alpha=1.5, sigma=0.7)`, `top10_recall >= 0.60 AND top1_recall < 0.30` (strong K-neighborhood survival despite argmax collapse).

### HARD_FAIL

- `HF_UNIFORM_COLLAPSE`: at `(alpha=1.5, sigma=0.7)`, all 6 metrics `< 0.10` (substrate is genuinely broken in combined overload+noise; no metric-axis structure because everything is at chance).

### MIDDLE_BAND

- No HP + no HF (metric axis measured but no strong differentiation pattern).

## Chain-grade elevation

`CHAIN_GRADE_METRIC_DEPENDENCE_OVERLOAD_MAPPED` iff any HP fires in all 3 seeds AND cv < 0.15 on that HP metric across seeds.

## Substantive potential

- HP fires -> substrate DOES exhibit metric-family differentiation but ONLY in the interference regime; opens a physics-of-differentiation story (dense-Hopfield noise-scaling law + K-neighborhood survival). Prior CG numbers UNDER-estimate substrate real-world capability under noisy queries.
- HF_UNIFORM_COLLAPSE -> substrate collapse is HARD; K-neighborhood does not survive overload+noise; forces alternative storage designs (sparse Hopfield / correlated keys) as flagged in v1 hand-off.
- MIDDLE_BAND -> more sweep resolution needed; v3 respec would push sigma higher OR try correlated-keys axis.

## CARDINALITY (META_RULE_H)

- FULL: `EXPECTED_N_UNITS = 16` per seed cell (4 alphas × 4 sigmas).
- SMOKE: `EXPECTED_N_UNITS = 6` per seed cell (3 alphas {0.30, 1.00, 1.50} × 2 sigmas {0.0, 0.7}).
- Aggregate across 3 seeds handled externally (Skunkworks landed-VET).
- `cardinality_ok: bool` field set in metrics.json.

## CRLB / feasibility (META_RULE_AC + capacity-feasibility)

At `alpha=1.50`, `M=12288`:
- Binomial-CLT floor: `sigma_min = sqrt(0.25/M) = sqrt(0.25/12288) = 0.00451`. `THEORETICAL@binomial-CLT`.
- HP gap 0.20 (metric spread) = ~44 sigma_min; well-reachable.
- HP separation 0.30 (top1<0.30) + 0.60 (top10>=0.60) = 0.30+ separation floor = ~66 sigma_min; well-reachable.
- top-1 argmax-noise ceiling (Principle S): at M=12288 > N=8192 (over-Amit-Gutfreund), top-1 recall expected to enter mid-band; discriminator reachable.
- `discriminator_reachability: True`.

Computed via Python:
```
>>> math.sqrt(0.25 / 12288)
0.004510308...
```

## DISCRIMINATOR-MUST-SURVIVE-SCALE

- Smoke uses **full N=8192** with reduced (alpha × sigma) resolution (6 cells) rather than smaller N.
- Smoke includes explicit PREVIEW arm at `(alpha=1.50, sigma=0.70)` — the discriminator-heavy config — full-scale confirmation.
- **HALT_ATOMIZE tripwire:** if smoke preview shows `top1 >= 0.90` at (1.5, 0.7), substrate is STILL saturating even in intended overload+noise regime; discriminator does NOT survive scale; halt full dispatch per META_RULE_AG.

## Baseline-in-band (META_RULE_AG)

- At `(alpha=0.30, sigma=0.0)` top1 expected near ceiling (v1 verified this is 1.000 — v1 baseline anchor).
- At `(alpha=1.50, sigma=0.70)` top1 expected near floor per interference theory.
- Sweep bracket includes discriminating band by CONSTRUCTION.
- Substrate-saturation escape check: v1 CONFIRMED baseline saturation up to alpha=8.0 WITHOUT noise; sigma axis is the escape mechanism (dense-noise EXPONENTIAL scaling per NeurIPS 2023 Sparse Hopfield).

## arms-must-differ (META_RULE_AF)

- Single mechanism arm (dense-hopfield READ-REPLACE with noisy query).
- (alpha × sigma) grid is a CONFIGURATION sweep, not an arm sweep.
- Metric axis is a FREE MEASUREMENT SURFACE from one readout tensor `p_n`; not an arm axis.
- 6 metrics apply DISTINCT post-processing (argmax-top-K vs cosine-threshold) verified in `_selftest_metrics_family_arms_differ` at moderate noise (spread > 0.01).
- Noise-injection mechanism verified via NEW `_selftest_noise_injection_moves_metrics` (adding sigma=1.5 noise to clean substrate produces top1 degradation >= 0.10 — noise mechanism physically effective).
- `arms_differ_exempted: [["single_arm_dense_hopfield_read_replace_with_query_noise", "metric_axis_is_free_measurement_not_arm_axis", "alpha_sigma_grid_is_config_sweep_not_arm_sweep"]]`.

## final_metrics_atomicity

`tmp_replace` — `metrics.json.tmp` then `os.replace()` (META_RULE_AH).

## Calibration-check (META_RULE_M)

`default_ok_for_this_regime` — bipolar synthetic keys/vals; same distribution as Cell D v2 reference. Noise injection is post-projection Gaussian on L2-normalized queries; no adaptive parameter tuning.

## except SystemExit ordering

`except SystemExit: raise` then `except KeyboardInterrupt: raise` then `except Exception:` (never BaseException). Verified pre-smoke.

## Prior-work check (substrate-KB concept-query)

- `bash tools/substrate_query.sh "overload regime noise sweep top-K metric differentiation dense Hopfield alpha capacity"` returns top hit at cosine 0.269 (below the 0.30 threshold; no prior atom).
- Related prior work: NeurIPS 2023 Sparse Hopfield noise-asymmetry (chunk036 of `notes/research_drill_middle_and_negative_findings_rescue_2x_2026-06-05.md`) — DIRECTLY load-bearing: dense-bipolar retrieval noise impact is EXPONENTIAL in load; that's the theory this v2 tests.
- **No prior atom at cosine > 0.30 for "metric-family differentiation under overload+noise dense Hopfield sweep."** Genuinely novel.

## Prior related landings (coordinator flagged)

- `data/exp_metric_dependence_top_k_semantic_v1_seed_7_smoke/metrics.json` — v1 HF_METRICS_IDENTICAL underloaded (this cell's parent + null-baseline anchor).
- `data/exp_g6_semantic_similar_fabrication_khop_v1/metrics.json` — fabrication localization at fixed high cosine (adversarial attack robustness); distinct scope.
- `data/exp_gap4v2_semantic_A_eval_280atoms_gpu_v1/metrics.json` — BGE-encoder semantic-search recall on gap4v2 (external LLM encoder, not substrate metric-axis); distinct scope.
- Cited in metrics.json `prior_related_anchors` field.

## Route

- SMOKE: local (fast 6-cell verification at full-N + preview at (1.5, 0.7), per USER SMOKE-ONLY on local rule).
- FULL: `remote_cpu_queue` (numpy CPU; 16 cells × 3 seeds; per-seed est ~40-70 min based on v1 wall_probe times scaled to (alpha × sigma) grid).
- Timeout: 7200s per seed (per USER hand-off directive; 2x safety headroom above worst-case per-seed estimate).

## Files

- `experiments/_substrate_metric_dependence_top_k_semantic_v2_core.py` — shared core (mechanism, selftests, verdict).
- `experiments/exp_metric_dependence_top_k_semantic_v2_seed_{7,13,19}.py` — per-seed cell wrappers.

## Cross-references

- v1 parent + hand-off: `preregs/2026-07-01_metric_dependence_top_k_semantic_v1.md` + `notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v1_HF_METRICS_IDENTICAL_2026-07-01.md`.
- Cell D v2 CG landing (parent substrate primitive): `exp_cortex_hippo_dense_layer_M8192_v2_seed_*`.
- Hidden-dim research: `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim S.
- Sparse-coding / AMP theory: `notes/research_sparse_coding_compressed_sensing_2026-07-01.md`.
- Dense-vs-sparse noise-scaling asymmetry: `notes/research_drill_middle_and_negative_findings_rescue_2x_2026-06-05.md` chunk036 (NeurIPS 2023 arxiv:2309.12673).
