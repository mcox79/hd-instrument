# Pre-registration: cortex_hippo_dense_beta_sweep_v1

**Date:** 2026-07-01
**Anchor base:** cortex_hippo_dense_beta_sweep_v1_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 smoke first; seeds 13/19 dispatched on HP smoke)
**Scripts:**
- experiments/_substrate_cortex_hippo_dense_beta_sweep_v1_core.py (shared)
- experiments/exp_cortex_hippo_dense_beta_sweep_v1_seed_7.py
- experiments/exp_cortex_hippo_dense_beta_sweep_v1_seed_13.py
- experiments/exp_cortex_hippo_dense_beta_sweep_v1_seed_19.py

**Queue:** local_cpu_queue for smoke ONLY (USER-locked 2026-07-01: no FULL to local);
overnight_queue (GPU) for FULL via hdi_orchestrator push.

**Parent + prior work:**
- v2 REPLACE landed fc47b1bb (3-seed HP at M=8192; recall~=1.000 with adaptive beta).
  MEASURED@data/exp_cortex_hippo_dense_layer_M8192_v2_seed_{7,13,19}/metrics.json.
- v3 M-sweep in flight; uses SAME adaptive beta = log2(M) / cosine_margin formula.
- Wave 14 (2026-05-22) preregs/2026-05-22_wave14_betY_phase1_beta_calibration.md
  did CONSTANT-beta calibration for a different family. This cell is complementary,
  not a rediscovery: it characterizes the optimum + robustness of the ADAPTIVE beta
  formula used by v2 REPLACE + v3 M-sweep by SWEEPING beta at fixed M.

## Hypothesis (v1 BETA-SWEEP)

Cell D v2 replacement-mode adaptive beta = log2(M) / cos_margin ~= 17-20 for M in
{4096, 8192, 16384} at margin=0.7. This cell asks: how close is that adaptive
value to the recall-maximizing beta at each M, and how robust is recall to
beta perturbations?

Predicted structural finding:
- Modern Hopfield theory (Ramsauer 2021 eq.14) predicts a beta-scaling regime
  where recall peaks at beta ~ log(M) / margin (up to constants). Adaptive
  formula (from v2) selects raw = log2(M) / margin, then clamps [8, 128].
- If SWEEP-best-beta at each M lands within +/- 30% of the adaptive-formula
  value AND recall(adaptive-beta) >= 0.95 * recall(sweep-best-beta) at each M:
  adaptive formula is well-calibrated to the operating regime; HARD_PASS.
- If SWEEP-best-beta is far from adaptive value OR adaptive-recall < 0.90 of
  best-recall: formula is miscalibrated or beta axis has broad optimum;
  MIDDLE_BAND (formula usable but not optimal).
- If NO beta reaches recall >= 0.60 at some M: mechanism is beta-sensitive
  beyond the swept range; HARD_FAIL (falsifies scale-independence claim).

## Design (cell-author owns)

**Sweep:** beta in {5.0, 8.0, 13.0, 20.0, 32.0} x M in {4096, 8192, 16384}
x seeds {7, 13, 19} (chunked; one cell per seed).

Rationale for beta choices:
- beta=5.0: BELOW BETA_MIN clamp floor of v2 (probes sub-clamp regime).
- beta=8.0: at BETA_MIN clamp floor.
- beta=13.0: mid-range; adaptive formula value at M=8192, margin=1.0.
- beta=20.0: adaptive formula value at M=16384, margin=0.7.
- beta=32.0: 1.6x the adaptive value; probes over-saturation regime.

Rationale for M choices: match v3 sweep so results align with the operating regime.

Rationale for 3 seeds: cross-seed cv reveals whether the optimum is robust
(cv < 15% at best-beta) or noisy (cv > 30% at best-beta implies the formula
is picking up chance).

## Discriminator

**Primary (per M):** which beta value maximizes recall(ARM_HA_DENSE_REPLACE)?
- Compute beta_star = argmax over {5, 8, 13, 20, 32} of mean(recall) across seeds.
- Compute recall_star = recall(beta_star, M).
- Compute recall_adaptive = recall(beta ~ log2(M)/0.7, M) at the swept beta nearest
  to log2(M)/0.7. (M=4096: 12/0.7=17.1 -> 20.0; M=8192: 13/0.7=18.6 -> 20.0;
  M=16384: 14/0.7=20.0 -> 20.0.)

**HP condition (per seed cell):** for each M:
- recall_star >= 0.80 (mechanism attains high recall at SOME beta at this M).
- recall(nearest-swept-beta-to-adaptive) >= 0.95 * recall_star (adaptive is
  well-calibrated).
- No beta value drives NaN/error (arm_status OK at all 5 beta values).

**HF (per seed cell):**
- recall_star < 0.60 at ANY M (mechanism fails to reach floor even at best beta).
- OR nearest-adaptive recall < 0.60 at ANY M (adaptive formula misaligns to
  a broken regime).
- OR ANY arm-pair bit-identical at ANY (M, beta) pair (META_RULE_AF).
- OR CARDINALITY_BREACH (n arm outcomes != 15 in FULL per seed).
- OR NaN/error in any arm.

**MB:**
- 0.60 <= recall_star < 0.80 at any M, OR
- recall(nearest-adaptive) / recall_star in [0.80, 0.95) at any M (adaptive
  usable but leaves >5% recall on the table).

**Chain-grade promotion (Skunkworks aggregation across 3 seeds):**
3-of-3 seeds HARD_PASS AND cross-seed cv(recall) < 15% at best-beta at each M.

## Arms

- **ARM_STANDARD** (per M; sanity ceiling; runs ONCE per M not per beta).
- **ARM_HA_ONLY** (per M; fairness floor; runs ONCE per M not per beta).
- **ARM_HA_DENSE_REPLACE_beta{5,8,13,20,32}** (per M; 5 beta values SWEPT).

**Cardinality per seed cell (FULL):**
- STANDARD: 3 M = 3 outcomes
- HA_ONLY: 3 M = 3 outcomes
- REPLACE_beta_X: 3 M * 5 beta = 15 outcomes
- Total: 21 arm-outcomes per seed cell.

EXPECTED_N_UNITS = 21 (per seed cell) in FULL.
Smoke: 1 M (=4096) * (STANDARD + HA_ONLY + 5 beta REPLACE) = 7 arm-outcomes.

## Pre-registered fairness disciplines

1. W_h and tape K_c/V_c different objects, different shapes (v2-inherited).
2. Tape written ONCE per M (same tape shared across all 5 beta reads).
3. ARM_HA_ONLY: recall <= 0.20 (tape not read).
4. Same fixed projection P_hc structure across all arms and M values.
5. Beta values FIXED per arm (no adaptive computation); logged in metrics.
6. META_RULE_AF: bit-identical arm pairs auto-HF at any (M, beta) pair
   (ceiling-tie exempt only for co-saturated 1.0 at low alpha AND arm-pair
   is {STANDARD, REPLACE_beta_X}).
7. RNG per-M seeded with (seed + m_items); no cross-M aliasing. Beta is a
   READ-side parameter; same encoded tape used for all beta values within
   one (seed, M) pair.

## Pre-registered thresholds (per seed cell)

**HARD_PASS (per seed; ALL 3 M values must satisfy):**
- For each M in {4096, 8192, 16384}:
  - max_beta recall_replace >= 0.80 (recall_star)
  - recall(nearest-adaptive-beta) / recall_star >= 0.95
  - All 5 beta arms status OK; no NaN

**HARD_FAIL (per seed):**
- recall_star < 0.60 at ANY M (task-spec HF)
- OR nearest-adaptive recall < 0.60 at ANY M
- OR HA_ONLY > 0.20 at ANY M (fairness)
- OR ANY arm-pair bit-identical at ANY (M, beta) (META_RULE_AF)
- OR EXPECTED_N_UNITS mismatch (M_CARDINALITY_BREACH; BETA_CARDINALITY_BREACH)

**MIDDLE_BAND (per seed):**
- recall_star in [0.60, 0.80) at any M, OR
- adaptive/star ratio in [0.80, 0.95) at any M
- Interpretation: adaptive formula usable, not optimal; drill on beta schedule.

## Pre-registered MANDATORY sec 15 envelope-fail-bands

1. **Sweep alignment (Gate A):** beta is the primary readout-side sweep axis;
   M is a secondary axis. effective_beta_per_primitive:
   {ARM_HA_DENSE_REPLACE.beta = swept-value (FIXED, no adaptive computation)}.
   sweep_alignment_verdict: ALIGNED.

2. **Discriminating bracket (Gate B):**
   beta values selected to span:
   - beta=5.0: below BETA_MIN clamp (probe undershoot regime)
   - beta=8.0: at BETA_MIN clamp
   - beta=13.0: mid-range (log2(8192)~=13)
   - beta=20.0: adaptive-formula target for M=16384, margin=0.7
   - beta=32.0: 1.6x adaptive (probe overshoot regime)

   Predicted recall per point (HYPOTHESIZED@formula):
   - M=4096: {5:0.30, 8:0.85, 13:0.99, 20:0.99, 32:0.95} -> band-fill ~0.85
   - M=8192: {5:0.20, 8:0.75, 13:0.99, 20:0.99, 32:0.95} -> band-fill ~0.85
   - M=16384: {5:0.15, 8:0.65, 13:0.98, 20:0.99, 32:0.95} -> band-fill ~0.85

   discriminating_fraction predicted: >= 3/5 = 0.60 per M (>= 0.30 required).

3. **Signal-shape audit (Gate C):**
   Same shape edges as v2/v3: keys_c(N_c) -> attention -> p(N_c). SHAPE_MATCH.
   No new primitive edges.

4. **Positive control at test regime (Gate D):**
   - ARM_STANDARD per M is the sanity ceiling arm (reproduces v3 M-sweep result
     at M=4096; MEASURED@data/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_*).
   - ARM_HA_DENSE_REPLACE at beta=20 reproduces v2 M=8192 recall~=1.000
     regime (adaptive-nearest beta) within tolerance 0.10.
   - Smoke preview arm at M=16384, beta=20 (adaptive-target for M=16384) proves
     discriminator fires at largest M.

5. **Functional-requirement decomposition (unchanged):**
   - (a) hippo fast encode.
   - (b) hippo-to-cortex projection.
   - (c) tape write per M (ONCE per M; shared across beta arms).
   - (d) attention read per (M, beta).
   - (e) match: argmax cosine.

## Pre-reg fields (SCHEMA-VET)

- expected_n_units = 21 (per seed cell FULL); 7 in smoke.
- cardinality_ok mandatory.
- HARD_FAIL_M_CARDINALITY_BREACH when n_M_values != 3 (FULL).
- HARD_FAIL_BETA_CARDINALITY_BREACH when n_beta_values != 5 per M (FULL).
- HARD_FAIL_META_RULE_AF_BIT_EXACT (any arm-pair recall identical at any
  (M, beta), with ceiling-tie exempt above).
- HARD_FAIL_FAIRNESS (HA_ONLY > 0.20 at any M).
- HARD_FAIL_REPLACE_BELOW_FLOOR (recall_star < 0.60 at any M).
- HARD_FAIL_ADAPTIVE_MISALIGN (nearest-adaptive recall < 0.60 at any M).
- discriminator_survives_scale: True (smoke has FULL_N preview at M=16384).
- CRLB fields per M (same as v3):
  - crlb_floor_computed_M4096 = 0.00781 THEORETICAL@sqrt(0.25/M)
  - crlb_floor_computed_M8192 = 0.00552 THEORETICAL
  - crlb_floor_computed_M16384 = 0.00390 THEORETICAL
  - discriminator_reachability = True (HP gap 0.80-0.60=0.20 >> CRLB floor).
- calibration_check = "adaptive_with_discriminator_gate" (probing the
  adaptive formula itself; discriminator = per-(M,beta) recall).
- sec 13 patterns: start_marker + crash_diagnostic + per-seed ckpt + heartbeat.
- arms_differ_verified: True (META_RULE_AF gate in verdict).
- final_metrics_atomicity: "tmp_replace" (META_RULE_AH).
- composition_edges: 1 edge per (M, beta) (keys_c -> attention -> p).
- positive_control_arms: ARM_STANDARD per M; ARM_HA_DENSE_REPLACE_beta20 vs v2.
- functional_requirements: (a)-(e).
- cell_chunked: True (single-seed-per-cell).
- start_marker_written: True.
- crash_diagnostic_present: True.
- heartbeat_present: True.
- defensive_error_checking: "passed_all_4_patterns" (SystemExit before Exception).
- cardinality_ok: True (enforced in metrics).
- parent_v2_landing: "fc47b1bb_recall_1.000_M8192_3seed".
- parent_v3_context: "v3 M-sweep in-flight; this v1 asks whether adaptive
  formula = argmax-beta at each M".

## HP_SCOPE (per-arm HP gate applicability, per M)

- ARM_HA_DENSE_REPLACE_beta{X}: HP scope = {recall >= 0.60 floor;
  recall / max_beta_recall >= 0.95 required for adaptive-target beta only}
  per M.
- ARM_STANDARD: per M sanity ceiling (recall >= 0.95 at M=4096; may drop
  at M=16384 as bipolar readout saturates; NOT a HP gate on itself).
- ARM_HA_ONLY: per M fairness floor (recall <= 0.20; HARD_FAIL if breached).

## Smoke config

- N_h=512, N_c=1024, M=4096 (smoke smallest sweep point).
- Full beta grid (5 values) at smoke M.
- Numpy backend; CPU-eligible (~5-15 min target smoke wall on local laptop).
- Preview arm at N_h=4096 N_c=4096 M=16384, beta=20 to prove discriminator
  survives full-scale largest M.

## FULL config (per seed, if smoke HP)

- N_h=4096, N_c=4096, M in {4096, 8192, 16384}, beta in {5, 8, 13, 20, 32}.
- Torch+cuda backend; overnight_queue on GPU at C:/dev/hd-instrument.
- Per-seed timeout 7200s (2h; 15 attention reads at M=16384 is
  ~5x v3 wall = 45-60min budget with margin).

## Cap-map rows (proposed; on 3-of-3 HP across seeds)

- Adaptive beta ~ log2(M)/cos_margin selects beta within 5% of argmax-recall
  beta at M in {4096, 8192, 16384}.
- Cortex dense-Hopfield READ-REPLACE recall is broad-optimum in beta
  (multiple beta values reach recall >= 0.80).
- v2 M=8192 result generalizes across the beta axis; not lucky-regime.

## Coordination

- Cell-author: exp_dev (this dispatch; seed_7 smoke first via local_cpu).
- Push+FULL dispatch: hdi_orchestrator (harness-DENIED push for exp_dev;
  routes to overnight_queue via SSH after commit-and-push).
- Landed-VET: skunkworks (3-seed aggregation + adaptive-vs-star audit per M).

## Risk + mitigations

- **Attention at M=16384 x 5 beta = 5x v3 wall**: batched over chunk=1024;
  reuses encoded tape across beta arms (encoded ONCE per M, reads 5 times).
  Actual expected wall: ~2x v3 (not 5x) because encode dominates.
- **beta=5 below BETA_MIN clamp**: intentional; probes undershoot regime. If
  ALL 5 beta drive NaN/error, cell HF's; this is the intended low-beta failure.
- **beta=32 near BETA_MAX**: intentional; probes overshoot. If softmax exp()
  overflows, cell handles via sims_scaled -= max trick (v2-inherited).
- **Per-seed runtime**: 2h timeout. If GPU wall exceeds 90min, chunk-down.

## Differences from v3 M-sweep

- v3: sweeps M with ADAPTIVE beta formula (one beta per M).
- v1 (this): sweeps BETA at fixed M grid (5 beta per M).
- v3 asks "does recall survive M scaling with formula?"; v1 asks "is formula
  at the optimum for each M?".
- Complementary; results should co-inform whether the adaptive formula is
  chain-grade or heuristic.

## Milestone significance

If HP (all 3 seeds pass all 3 M): validates the adaptive beta formula as
CHAIN-GRADE regime-independent calibration for cortex dense-Hopfield READ.
The formula becomes a substrate primitive with published constants.

If MB (formula usable but not optimal): pivots to beta-schedule drill or
richer adaptive formula (e.g., include capacity alpha=M/N term).

If HF (formula misaligns): the M-sweep v3 result (if HP) becomes suspect
regime-locked; falls back to per-M tuning or Cell E (Product-Key Memory).

## Citations

- Ramsauer et al. (2021) "Hopfield Networks is All You Need" ICLR 2021.
- Provably Optimal Capacity for Modern Hopfield (2024) arxiv/2410.23126.
- Scalable-Softmax (2025) arxiv/2501.19399.

## Reference prior cells

- v2 M=8192 (parent): experiments/exp_cortex_hippo_dense_layer_M8192_v2_seed_*.py
- v3 M-sweep (sibling): experiments/exp_cortex_hippo_dense_layer_M_sweep_v3_seed_*.py
- v3 prereg: preregs/2026-07-01_substrate_cortex_hippo_dense_layer_M_sweep_v3.md
- Wave 14 (2026-05-22, distant prior; constant-beta for different family):
  preregs/2026-05-22_wave14_betY_phase1_beta_calibration.md
