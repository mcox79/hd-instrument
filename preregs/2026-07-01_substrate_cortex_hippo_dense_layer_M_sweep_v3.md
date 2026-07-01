# Pre-registration: cortex_hippo_dense_layer_M_sweep_v3 (cross-M expansion of v2 REPLACE)

**Date:** 2026-07-01
**Anchor base:** cortex_hippo_dense_layer_M_sweep_v3_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 first; seeds 13/19 dispatched on HP smoke)
**Scripts:**
- experiments/_substrate_cortex_hippo_dense_layer_M_sweep_v3_core.py (shared)
- experiments/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_7.py
- experiments/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_13.py
- experiments/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_19.py

**Queue:** local_cpu_queue for smoke; overnight_queue (GPU) for FULL via Orchestrator push.

**Parent:** v2 REPLACE landed fc47b1bb (3-seed HP at M=8192; recall~=1.000).
  MEASURED@data/exp_cortex_hippo_dense_layer_M8192_v2_seed_{7,13,19}/metrics.json.

**Meta-insight source:** Skunkworks M3 MM_TENTATIVE expansion criterion (c)
  (edf59e18): "Pattern verified at other M values (M=4096, M=16384)".
  This cell operationalizes criterion (c).

## Hypothesis (v3 CROSS-M)

Cortex-side dense-Hopfield READ-REPLACE recall closes >=80% of clean-baseline
ceiling AT EVERY M in {4096, 8192, 16384} with adaptive beta ~ log2(M)/margin.

Predicted structural finding:
- Ramsauer 2021 eq.14 + Provably Optimal 2024 arxiv/2410.23126 predict
  exponential capacity in dimensionality; N_c=4096 vastly exceeds M=16384 for
  uncorrelated bipolar keys (alpha_effective << 1). CITED@lit.
- Adaptive beta compensates for softmax saturation as M grows (drill Q4).
- If v2 M=8192 result is regime-conditional, v3 sweep reveals the scaling
  wall; if not, HP across all 3 M => M3 architecture meta MM_TENTATIVE
  graduates to MM_STANDARD or chain-grade.

## Arms (identical to v2)

- **ARM_STANDARD** = direct cortex Hebbian only. Sanity ceiling.
- **ARM_HA_ONLY** = sparse-DG hippo one-shot; cortex empty. Fairness floor
  (recall <= 0.20).
- **ARM_HA_DENSE_REPLACE** = Ha writes tape (K_c, V_c); attention reads via
  softmax(beta * queries @ K_c^T) @ V_c. NO cortex-Hebbian W_c.

Beta calibration (adaptive; identical to v2 formula):
  beta = clamp(log2(M) / cosine_margin_estimate, BETA_MIN=8.0, BETA_MAX=128.0)
  For M in {4096, 8192, 16384} at margin=0.7:
    beta(4096) = 12/0.7 = 17.14  HYPOTHESIZED@formula
    beta(8192) = 13/0.7 = 18.57  HYPOTHESIZED@formula
    beta(16384) = 14/0.7 = 20.00 HYPOTHESIZED@formula
  Cell logs computed beta into metrics per-M.

Preview arm in smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE):
  Smoke runs M=4096 main arms + ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW at
  N_h=4096 N_c=4096 M=16384 (largest sweep point). If preview recall < 0.60
  at M=16384, REJECT full dispatch.

## Pre-registered fairness disciplines

1. W_h and tape K_c/V_c different objects, different shapes (v2-inherited).
2. Tape written ONCE by Ha per M value (no iterated replay).
3. ARM_HA_ONLY: recall <= 0.20 (tape not read).
4. Same fixed projection P_hc structure across all arms and M values.
5. Beta adaptive per keys_c cosine margin at each M value independently
   (declared; calibration_check = adaptive_with_discriminator_gate).
6. META_RULE_AF: bit-identical arm pairs auto-HF at any M (ceiling-tie
   exempt only if alpha<1.0 AND both saturate 1.000 AND pair is
   {STANDARD, REPLACE}).
7. RNG per-M seeded with (seed + m_items) so keys differ across M values;
   no cross-M aliasing.

## Pre-registered thresholds (per seed cell)

**HARD_PASS (per seed; requires ALL 3 M values to pass):**
- For each M in {4096, 8192, 16384}:
  - recall(ARM_HA_DENSE_REPLACE) / recall(ARM_STANDARD) >= 0.80
  - recall(ARM_HA_DENSE_REPLACE) - recall(ARM_HA_ONLY) >= 0.60
  - recall(ARM_HA_ONLY) <= 0.20

**HARD_FAIL (per seed):**
- recall(REPLACE) < 0.60 at ANY M (regime-conditional wall; task-spec HF)
- OR recall(HA_ONLY) > 0.20 at ANY M
- OR ANY arm-pair bit-identical at ANY M (META_RULE_AF; ceiling-tie exempt
  only under exemption above)
- OR M_CARDINALITY_BREACH (n_M_values != 3 in FULL)
- OR ARM_CARDINALITY_BREACH at any M (n_core_arms != 3)
- OR beta_used / margin degenerate at any M

**MIDDLE_BAND (per seed):**
- At least one M passes REPLACE >= 0.60 floor
- Some M pass HP gates (ratio>=0.80 AND gap>=0.60), some don't
- Interpretation: regime-conditional; cross-M scaling wall revealed;
  pivot to M-finer-sweep or beta-schedule drill.

**Chain-grade promotion (Skunkworks aggregation across 3 seeds):**
3-of-3 seeds HARD_PASS AND cross-seed cv(REPLACE) < 15% AT EACH M. Then:
- Atomize cross-M cortex dense-Hopfield READ-REPLACE as CLS-integration
  primitive with regime-independent scale.
- Validate M3 architecture MM_TENTATIVE -> MM_STANDARD (or chain-grade)
  per Skunkworks meta criterion (c).

## Pre-registered MANDATORY sec 15 envelope-fail-bands

1. **Sweep alignment:** M-sweep IS the primary axis; 3 M values * 3 arms
   per seed = 9 arm-outcomes; cardinality_ok flag = (9 == expected).

2. **Discriminating bracket (per M):**
   - Primary: ratio(REPLACE/STANDARD) >= 0.80 (HP), < 0.60 REPLACE (HF).
   - Mechanism: REPLACE - HA_ONLY >= 0.60 required.
   - Meta: bit-identical arm auto-HF (ceiling-tie exempt).

3. **Signal-shape audit (META_RULE_AP_v3):**
   - Hippo state sparse_N_h bipolar (10% active).
   - P_hc: R^{N_h} -> R^{N_c} dense Gaussian (unchanged across M).
   - Tape (K_c, V_c): (M, N_c) L2-normalized rows.
   - Queries: keys_c directly at each M.
   - Shape edges: keys_c(N_c) -> attention -> p(N_c). SHAPE_MATCH per M.

4. **Positive control at test regime (per M):**
   - ARM_STANDARD at M=4096 alpha=1.0 exercises capacity floor.
   - ARM_STANDARD at M=16384 alpha=4.0 well above Amit-Gutfreund 0.138N
     wall; STANDARD expected to collapse or ride bipolar-quantization floor.
   - Smoke preview arm at M=16384 proves discriminator fires at largest M.
   - Small-world dense-Hopfield self-recall (inherited from v2 selftest).

5. **Functional-requirement decomposition (unchanged from v2):**
   - (a) hippo fast encode (sparse-DG one-shot).
   - (b) hippo-to-cortex projection.
   - (c) tape write per M.
   - (d) attention read per M with M-scaled beta.
   - (e) match: argmax cosine.

## Pre-reg fields (SCHEMA-VET)

- expected_n_units = 9 (3 M * 3 arms) in FULL; 3 in smoke (single M).
- cardinality_ok mandatory.
- HARD_FAIL_M_CARDINALITY_BREACH when n_M_values != 3 (FULL).
- HARD_FAIL_META_RULE_AF_BIT_EXACT (any arm-pair recall identical at any M).
- HARD_FAIL_FAIRNESS (HA_ONLY > 0.20 at any M).
- HARD_FAIL_REPLACE_BELOW_FLOOR (REPLACE < 0.60 at any M).
- discriminator_survives_scale: True (smoke has FULL_N preview at M=16384).
- CRLB fields per M:
  - crlb_floor_computed_M4096 = 0.00781 = sqrt(0.25/4096) THEORETICAL@CLT
  - crlb_floor_computed_M8192 = 0.00552 = sqrt(0.25/8192) THEORETICAL@CLT
  - crlb_floor_computed_M16384 = 0.00390 = sqrt(0.25/16384) THEORETICAL@CLT
  - crlb_formula_reference = "sigma_min = sqrt(0.25/M) binomial-CLT"
  - discriminator_reachability = True (HP gap 0.60 = 77-154*sigma across M)
- calibration_check = "adaptive_with_discriminator_gate".
- sec 13 patterns: start_marker + crash_diagnostic + per-seed ckpt + heartbeat.
- arms_differ_verified: True (META_RULE_AF gate in verdict per M).
- final_metrics_atomicity: "tmp_replace" (META_RULE_AH).
- composition_edges: 1 edge per M (keys_c -> attention -> p).
- positive_control_arms: ARM_STANDARD per M.
- functional_requirements: (a)-(e) unchanged from v2.
- cell_chunked: True (single-seed-per-cell).
- start_marker_written: True.
- crash_diagnostic_present: True.
- heartbeat_present: True.
- defensive_error_checking: "passed_all_4_patterns" (SystemExit before Exception).
- cardinality_ok: True (enforced in metrics).
- parent_v2_landing: "fc47b1bb_recall_1.000_M8192_3seed".
- M_SWEEP_expansion_criterion: "MM_TENTATIVE_criterion_c_verify_other_M".

## HP_SCOPE (per-arm HP gate applicability, per M)

- ARM_HA_DENSE_REPLACE: {ratio_vs_standard >= 0.80, gap_vs_ha_only >= 0.60}
  per M in {4096, 8192, 16384}.
- ARM_STANDARD: per M sanity ceiling (recall >= 0.95 at M=4096; may drop
  at M=16384 as bipolar readout saturates).
- ARM_HA_ONLY: per M fairness floor (recall <= 0.20).

## Smoke config

- N_h=512, N_c=1024, M=4096 (smoke smallest sweep point).
- Numpy backend; CPU-eligible (~2-5 min target smoke wall).
- Adaptive beta per M (logged per-arm).
- Preview arm at N_h=4096 N_c=4096 M=16384 to prove discriminator survives
  full-scale largest M.

## FULL config (per seed, if smoke HP)

- N_h=4096, N_c=4096, M in {4096, 8192, 16384}.
- Torch+cuda backend; overnight_queue on GPU at C:/dev/hd-instrument.
- Per-seed timeout 5400s (1.5h; attention read at M=16384 is
  O(M^2 * N_c) = 4.3e12 FLOPs but batched over chunk=1024; ~30-50min/seed
  on GPU).

## Cap-map rows (proposed; on 3-of-3 HP across seeds)

- Cortex dense-Hopfield READ-REPLACE recall closes >=80% of ceiling at
  M in {4096, 8192, 16384} (validates M3 cortex-layer scale independence).
- Attention-over-Ha-written-tape works across 4x range of memory sizes;
  no regime-conditional wall in tested band.
- Adaptive beta ~ log2(M)/margin schedule generalizes across M values;
  no per-M tuning needed.

## Coordination

- Cell-author: exp_dev (this dispatch; seed_7 smoke first via local_cpu).
- Push+FULL dispatch: hdi_orchestrator (harness-DENIED push for exp_dev).
- Landed-VET: skunkworks (3-seed aggregation + META_RULE_AF audit per M).

## Risk + mitigations

- **Attention at M=16384 is O(M^2 * N_c) = 4.3e12 FLOPs**: batched over
  chunk=1024 -> 268MB per chunk; fits GPU. If OOM, chunk down to 512.
- **Bipolar quantization may cluster at high M**: HARD_FAIL floor
  REPLACE < 0.60 catches; falls back to Cell E (Product-Key Memory).
- **Adaptive beta degenerate at very-low margin**: BETA_MIN=8.0 floor;
  HF flags degenerate margin.
- **Softmax saturation at high beta/M=16384**: adaptive formula gives
  beta~=20 for margin=0.7; well below BETA_MAX=128.
- **Per-seed runtime**: 1.5h timeout. If wall exceeds 60min, chunk down.

## Differences from v2 (one-line summary)

v2 (fc47b1bb) runs single M=8192 replicated 3-seed at recall~=1.000.
v3 (this) runs SAME mechanism at M in {4096, 8192, 16384} per seed to
verify Skunkworks M3 meta-insight MM_TENTATIVE criterion (c): pattern
verified at other M values.

Cell structure: shared _core.py; 3 per-seed wrappers; each seed cell runs
all 3 M values internally in FULL; smoke runs smallest M plus full-scale
preview at largest M.

## Milestone significance

If HP (all 3 seeds pass all 3 M): closes MM_TENTATIVE criterion (c) for
M3 cortex-layer architecture; graduates the READ-REPLACE mechanism to
MM_STANDARD or chain-grade. Concrete validation that the transformer-
attention-over-Ha-tape pattern is scale-independent across at least a
4x M range.

If MIDDLE_BAND (regime-conditional): reveals cross-M scaling wall;
pivot to finer M sweep + beta schedule drill to characterize onset.

If HARD_FAIL (any M below 0.60): novel structural finding that v2 M=8192
was a lucky-regime; pivot to Cell E (Product-Key Memory hierarchical
decomposition; drill option #2).

## Citations (drill-verified; identical to v2)

- Ramsauer et al. (2021) "Hopfield Networks is All You Need" ICLR 2021.
- Lample et al. (2019) "Large Memory Layers with Product Keys" NeurIPS 2019.
- Provably Optimal Capacity for Modern Hopfield (2024) arxiv/2410.23126.
- Scalable-Softmax (2025) arxiv/2501.19399.

## Reference prior cells

- v2 (this v3 expands): experiments/exp_cortex_hippo_dense_layer_M8192_v2_seed_{7,13,19}.py
- v2 prereg: preregs/2026-07-01_substrate_cortex_hippo_dense_layer_v2_replacement_M8192.md
- v2 landing: data/exp_cortex_hippo_dense_layer_M8192_v2_seed_{7,13,19}/metrics.json
  MEASURED HP recall~=1.000 across 3 seeds at fc47b1bb.
- Skunkworks meta-insight source: edf59e18 MM_TENTATIVE expansion criterion (c).
