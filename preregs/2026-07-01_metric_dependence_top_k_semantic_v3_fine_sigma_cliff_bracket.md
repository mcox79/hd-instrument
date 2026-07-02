# Pre-reg: metric_dependence_top_k_semantic_v3 (Dim S — FINE SIGMA CLIFF BRACKET)

**Filed:** 2026-07-01
**Cell-author:** hdi_exp_dev
**Anchor:** `metric_dependence_top_k_semantic_v3_fine_sigma_cliff_bracket`
**Seeds:** 7, 13, 19
**Reference:** `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim S (P_deflated=0.55)
**Parent:** `preregs/2026-07-01_metric_dependence_top_k_semantic_v2_overload_noise_sweep.md`

## v2 result summary + respec justification

v2 landed **HF_UNIFORM_COLLAPSE** with BIMODAL knife-edge behavior across (alpha in {0.30, 1.00, 1.50}, sigma in {0.0, 0.7}) at N=8192: sigma=0 saturates all 6 metrics at 1.000 across all alphas; sigma=0.7 collapses all 6 metrics to <0.03 uniformly across same alphas. Transition cliff is NARROWER than v2 grid resolved.

v3 respec (per Director hand-off 2026-07-01) brackets the cliff with FINE sigma sweep at 2 fixed alphas — v2 confirmed alpha shape-invariance across [0.30, 1.50], so no need to sweep alpha further.

## Question

Where does the substrate transition from perfect-recall to total-collapse under query noise? Is the transition band a NARROW cliff (<0.05 sigma) or a resolvable phase boundary? Within the transition band, does the 6-metric family finally differentiate (top-K > top-1)?

## Mechanism (single arm; grid = alpha × sigma)

Identical to v2 — same Cell D v2 dense-Hopfield READ-REPLACE primitive with query-noise injection. **IMPORTED from v2 core** (`_substrate_metric_dependence_top_k_semantic_v2_core.py`) for guaranteed mechanism-class parity.

500 queries per cell (N_QUERY=500).

## Sweep grid

- `alpha = M/N in {0.30, 1.00}` — 2 fixed loads (underload edge + at-wall).
- `sigma in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50}` — 8 fine points bracketing the transition zone with extension past cliff on both sides.
- `N_CORTEX = 8192` fixed.
- 3 seeds (7, 13, 19); one cell per seed (CHUNKED-per-seed per META rule).
- Total FULL units: 2 × 8 = 16 (alpha, sigma) cells per seed. Aggregate 3 seeds => 48 cell observations.

## Verdict gates

### HARD_PASS (any fires cross-seed = chain-grade eligible)

- `HP_CLIFF_BRACKET`: at least 1 cell has `max_metric_recall in [0.20, 0.80]` (partial-recovery zone — cliff is bracketed).
- `HP_METRIC_DIFFERENTIATION`: within cliff-band cells, `top10_recall - top1_recall >= 0.10` for at least one cell (top-K survives claim; sparse-coding drill's structured-sparsity prediction confirmed).
- `HP_BIMODAL_CONFIRMED`: at sigma<0.10 all metrics >=0.90 at both alphas AND at sigma>0.40 all metrics <=0.10 at both alphas (v2 bimodal reconfirmed at fine grain).

### HARD_FAIL

- `HF_NO_TRANSITION`: no cell in cliff-band anywhere in sweep (cliff width <=0.05 or entirely outside sigma range).
- `HF_METRIC_DIFFERENTIATION_FAILS`: cliff bracketed but `top10-top1 < 0.02` everywhere in-band (metric-family fundamentally cannot disambiguate on this substrate).

### MIDDLE_BAND

- No HP + no HF (unlikely given verdict logic; would indicate cliff is bracketed at exactly non-differentiating points but not uniformly non-differentiating).

## Chain-grade elevation

`CHAIN_GRADE_METRIC_CLIFF_MAPPED` iff `HP_CLIFF_BRACKET AND HP_METRIC_DIFFERENTIATION` both fire in all 3 seeds AND cv < 0.15 on the peak top10-top1 gap across seeds.

## Substantive potential

- HP_CLIFF_BRACKET + HP_METRIC_DIFFERENTIATION -> substrate has NARROW-BAND metric-family differentiation; positive Dim S result at fine resolution; sparse-Hopfield NeurIPS 2023 top-K survival prediction empirically confirmed. Load-bearing for M3 cortex: cortex-layer can EXPLOIT the narrow band by controlling query noise level.
- HP_BIMODAL_CONFIRMED (only) -> v2 finding validated at fine grain; substrate is truly knife-edge; metric-differentiation gates require operating exactly on cliff which is engineeringly hard.
- HF_NO_TRANSITION -> cliff is EVEN NARROWER than v3 sigma grain (0.05); Dim S is a true singularity.
- HF_METRIC_DIFFERENTIATION_FAILS -> cliff exists but all 6 metrics fail together; substrate cannot support top-K rescue at any noise level.

## CARDINALITY (META_RULE_H)

- FULL: `EXPECTED_N_UNITS = 16` per seed (2 alphas × 8 sigmas).
- SMOKE: `EXPECTED_N_UNITS = 8` per seed (2 alphas × 4 sigmas {0.05, 0.15, 0.25, 0.40}).
- Aggregate across 3 seeds handled externally (Skunkworks landed-VET).
- `cardinality_ok: bool` field set in metrics.json.

## CRLB / feasibility (META_RULE_AC + capacity-feasibility)

At `alpha=1.00`, `M=8192`:
- Binomial-CLT floor: `sigma_min = sqrt(0.25/M) = sqrt(0.25/8192) = 0.00553`. `THEORETICAL@binomial-CLT`.
- HP_METRIC_DIFFERENTIATION gap 0.10 = ~18 sigma_min; reachable.
- HP_CLIFF_BRACKET band width 0.60 (in [0.20, 0.80]) = ~108 sigma_min; easily resolvable.
- `discriminator_reachability: True`.

Computed via Python:
```
>>> math.sqrt(0.25 / 8192)
0.005524271...
```

## DISCRIMINATOR-MUST-SURVIVE-SCALE

- Smoke uses **full N=8192** with 4-point sigma coverage across [0.05, 0.40] at 2 alphas + preview at (1.0, 0.20) expected mid-cliff.
- **HALT_ATOMIZE tripwire:** if NO smoke cell (including preview) lands with max_metric in [0.20, 0.80], cliff is NOT bracketed by this grid; HALT + v4 sigma-grid respec.

## Baseline-in-band (META_RULE_AG)

- At `(alpha=0.30, sigma=0.05)` top1 expected near-ceiling (~1.000; anchors to v2 clean baseline).
- At `(alpha=1.00, sigma=0.50)` top1 expected near-floor (~0.000; anchors to v2 overload+noise collapse).
- Sweep bracket includes discriminating band by CONSTRUCTION.
- v2 established BOTH endpoints; v3 fills the gap.

## arms-must-differ (META_RULE_AF)

- Single mechanism arm (dense-hopfield READ-REPLACE with noisy query).
- (alpha × sigma) grid is a CONFIGURATION sweep, not an arm sweep.
- Metric axis is a FREE MEASUREMENT SURFACE from one readout tensor `p_n`; not an arm axis.
- 6 metrics apply DISTINCT post-processing verified in `_selftest_metrics_family_arms_differ` (inherited from v2).
- Noise-injection mechanism verified via `_selftest_noise_injection_moves_metrics` (inherited from v2).
- `arms_differ_exempted: [["single_arm_dense_hopfield_read_replace_with_query_noise", "metric_axis_is_free_measurement_not_arm_axis", "alpha_sigma_grid_is_config_sweep_not_arm_sweep"]]`.

## final_metrics_atomicity

`tmp_replace` — `metrics.json.tmp` then `os.replace()` (META_RULE_AH).

## Calibration-check (META_RULE_M)

`default_ok_for_this_regime` — bipolar synthetic keys/vals; same distribution as v1+v2. Noise injection is post-projection Gaussian on L2-normalized queries; no adaptive parameter tuning.

## except SystemExit ordering

`except SystemExit: raise` then `except KeyboardInterrupt: raise` then `except Exception:` (never BaseException). Inherited discipline from v2 code path.

## Prior-work check (substrate-KB concept-query)

Per Director hand-off: "no substrate-KB check needed (novel by shifted-parameter continuation of v2)." v2's own prior-work check verified genuine novelty for the metric-family × overload+noise sweep concept; v3 is a resolution refinement of the same territory.

## Prior related landings

- `data/exp_metric_dependence_top_k_semantic_v2_seed_7_smoke/metrics.json` — v2 HF_UNIFORM_COLLAPSE bimodal (parent + cliff-endpoint anchor).
- `data/exp_metric_dependence_top_k_semantic_v1_seed_7_smoke/metrics.json` — v1 HF_METRICS_IDENTICAL underloaded (v2 parent).
- Cited in metrics.json `prior_related_anchors` field.

## Route

- SMOKE: local (8-cell verification at full-N + preview, per USER SMOKE-ONLY on local rule).
- FULL: `remote_cpu_queue` (numpy CPU; 16 cells × 3 seeds; per-seed est ~15-30 min).
- Timeout: 3600s per seed (2x safety headroom above worst-case per-seed estimate).
- Full dispatch CONDITIONAL on smoke firing HP_CLIFF_BRACKET (at least 1 smoke cell in [0.20, 0.80]).

## Files

- `experiments/_substrate_metric_dependence_top_k_semantic_v3_core.py` — v3 sweep grid + verdict logic; IMPORTS mechanism primitives from v2 core.
- `experiments/exp_metric_dependence_top_k_semantic_v3_seed_{7,13,19}.py` — per-seed cell wrappers.

## Cross-references

- v2 parent + hand-off: `preregs/2026-07-01_metric_dependence_top_k_semantic_v2_overload_noise_sweep.md` + `notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v2_HF_UNIFORM_COLLAPSE_bimodal_2026-07-01.md`.
- v1 grandparent: `notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v1_HF_METRICS_IDENTICAL_2026-07-01.md`.
- Hidden-dim research: `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` Dim S.
- Sparse-coding / AMP theory: `notes/research_sparse_coding_compressed_sensing_2026-07-01.md`.
- Dense-vs-sparse noise-scaling asymmetry: `notes/research_drill_middle_and_negative_findings_rescue_2x_2026-06-05.md` chunk036 (NeurIPS 2023 arxiv:2309.12673).
- **M3 architecture implication (both v2 + v3 findings):** Cortex layer must denoise/re-attend queries before hitting substrate; substrate itself CANNOT provide broad metric-band tolerance. Atomize into M3 design guidance meta.
