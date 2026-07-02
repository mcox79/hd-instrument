# Pre-registration: correlated_key_capacity_rho_sweep_v1

**Date:** 2026-07-01
**Anchor base:** correlated_key_capacity_rho_sweep_v1_seed_{7,13,19}
**Chunks:** 3 single-seed cells (seed_7 smoke first; seeds 13/19 dispatched on HP smoke)
**Scripts:**
- experiments/_substrate_correlated_key_capacity_rho_sweep_v1_core.py (shared)
- experiments/exp_correlated_key_capacity_rho_sweep_v1_seed_7.py
- experiments/exp_correlated_key_capacity_rho_sweep_v1_seed_13.py
- experiments/exp_correlated_key_capacity_rho_sweep_v1_seed_19.py

**Queue:** local_cpu_queue for smoke ONLY (USER-locked 2026-07-01: no FULL to
local). FULL runs -> remote_cpu_queue via hdi_orchestrator push (numpy cell;
no GPU required).

**Parent + prior work (substrate-KB verified):**
- Research drill: notes/research_correlated_key_capacity_hopfield_fhrr_2026-07-01.md
  (predicted alpha_c(rho) approx alpha_0 * (1 - rho^2); HP1-HP4 falsifiable).
- Cell D v2 CG (Atom 1): independent-key alpha_c approx 0.138 wall (AGS baseline).
- Substrate-KB concept-query at authoring time returned top-1 cosine=0.27
  (preregs/2026-05-20_wave14h_alpha_sweep_v2.md); DIFFERENT cell (measures
  LEAK RATE for anti-Hebbian ERASE on rank-L subspace correlated keys at
  N=4096, not capacity WALL). Adjacent but not overlapping. Genuinely novel:
  first substrate empirical test of Loewe (1998) alpha_c(rho) prediction.
- Prior-work citation: `notes/research_to_expdev_K_max_NESS_baseline_alpha_c_138_formula_a_genuine_multi_hop_operationalize_2026-06-20.md`
  (baseline alpha_c=0.138 discussion; motivates this cell's test of the
  correlated shift).

**Design pivot from initial brief (documented HYPOTHESIZED@brief -> MEASURED
prototype at N=8192 seed=7 2026-07-01):**
- Initial brief: use Cell D v2 dense-Hopfield READ-REPLACE (softmax attention).
- Prototype at N=8192 with softmax READ-REPLACE at beta=13 showed universal
  saturation up to alpha=0.30 across rho in {0.0, 0.5} — dense softmax
  Hopfield has Ramsauer exponential capacity, does NOT exhibit AGS 0.138 wall.
- Loewe (1998) prediction alpha_c(rho) = 0.138*(1-rho^2) applies to the
  CLASSICAL Hebbian outer-product regime (the storage regime the theorem
  derives from). Cell PIVOTED to classical Hebbian storage
  (_standard_recall_numpy-style) MEASURED@ this-cell-prototype-2026-07-01.
- Cross-rho signal confirmed empirically at N=8192 (MEASURED prototype):
  - alpha=0.10 rho=0.0 recall=1.000; rho=0.5 recall=0.253; rho=0.7 recall=0.001
  - alpha=0.05 rho=0.0 recall=1.000; rho=0.5 recall=0.695; rho=0.7 recall=0.780
  - alpha=0.138 rho=0.0 recall=1.000; rho=0.5 recall=0.168; rho=0.7 recall=0.015
  - alpha=0.20 rho=0.0 recall=1.000; rho=0.5 recall=0.046; rho=0.7 recall=0.056
- rho=0.0 (independent) recall stays saturated across grid -- 0.138 wall
  doesn't crumble here due to bipolar-sign readout tolerance. NOT a HP
  requirement; we test the SHIFT with rho, not absolute rho=0.0 wall.

## Hypothesis

Under classical Hebbian outer-product storage (W = V^T K) with keys generated
via shared-component correlation model x_i = sqrt(rho)*z + sqrt(1-rho)*e_i
(then l2-normalized), pairwise correlation rho DEGRADES recall accuracy at
fixed alpha=M/N. As rho increases, effective alpha_c drops per Loewe (1998):
alpha_c(rho) approx 0.138 * (1 - rho^2).

**Predicted structural finding (HYPOTHESIZED@theory + prototype @N=8192 seed=7):**
- rho=0.0: recall stays >= 0.90 across alpha in {0.05, ..., 0.20} (independent
  keys well below classical wall on this substrate with bipolar-sign readout).
- rho=0.3: mild degradation; recall(alpha=0.138) roughly 0.5-0.9.
- rho=0.5: sharp wall between alpha=0.05 and alpha=0.10 (prototype: 0.695 ->
  0.253); recall(alpha=0.138) MEASURED at 0.168.
- rho=0.7: sharp wall at or below alpha=0.10 (prototype: 0.780 -> 0.001);
  recall(alpha=0.20) MEASURED at 0.056.

If HP fires 3-of-3 seeds:
**CHAIN_GRADE_CORRELATED_KEY_CAPACITY_WALL_CHARACTERIZED**.
- Adds Stage 1 substrate primitive: "classical Hebbian capacity has predictable
  shift under key correlation; alpha_c(rho) approx alpha_0 * (1 - rho^2)".
- Informs M3 architecture (Research drill sec "Substrate-product implications"):
  de-correlate keys at write time OR use bind-structured VSA encoding to keep
  effective rho near zero.

## Design

**Grid (FULL):** 5 rho x 5 alpha = 25 phase points per seed.
- rho in {0.0, 0.1, 0.3, 0.5, 0.7}          (correlation levels)
- alpha in {0.05, 0.10, 0.138, 0.15, 0.20}  (loads bracketing walls)

**Grid (SMOKE):** 3 phase points at FULL N (DISCRIMINATOR-MUST-SURVIVE-SCALE):
- (rho=0.0, alpha=0.10): independent-baseline saturation control
- (rho=0.5, alpha=0.10): correlated wall crossing (~theory alpha_c(0.5)=0.104)
- (rho=0.7, alpha=0.20): deep-wall check (theory alpha_c(0.7)=0.070)

**Fixed:** N = 8192 for both SMOKE and FULL. Max M = 0.20 * 8192 = 1638.

**Backend:** numpy (CPU). No GPU required. Per-unit wall ~30-60s at N=8192 max
alpha; full grid = 25 x ~40s = ~1000s per seed FULL (16 min budget); smoke
= 3 x ~40s = 120s per seed SMOKE.

**Seeds:** 7, 13, 19 (dispatched sequentially: seed_7 smoke first via local_cpu).

**Correlated-key generation (algorithm; MEASURED@core.generate_correlated_keys):**
1. Draw z ~ N(0, I_N)                           (shared base direction)
2. Draw E ~ N(0, I_{MxN})                       (independent components)
3. keys_raw = sqrt(rho) * z + sqrt(1-rho) * E   (shape (M, N))
4. keys = keys_raw / ||keys_raw||_2             (l2-normalize)
5. Empirical E[<x_i, x_j>] approx rho for i != j after normalization.

**Values (targets):**
- v_i ~ Uniform({+1, -1})^N                      (bipolar; matches AGS)
- v_i normalized to 1/sqrt(N) magnitude          (stability in outer product)

**Storage + retrieval (CLASSICAL HEBBIAN; matches Cell D v1 primitive style):**
- W = V^T @ K  shape (N, N)                      (outer-product Hebb)
- For each stored key k_q (recall probe):
  - pred_raw = W @ k_q                           (matmul readout)
  - pred = sign(pred_raw) / ||sign(pred_raw)||   (bipolar quantize + norm)
- recall = fraction where argmax(pred @ V^T) == q

**Discriminator sanity (self-tested at cell load):**
- Empirical rho matches nominal to +/- 0.05 at M=400 N=1024 (selftest).
- rho=0.0 alpha=0.05 N=1024: recall >= 0.90 (baseline saturation).
- rho=0.7 alpha=0.15 N=1024: recall STRICTLY LESS than rho=0.0 same alpha
  (wall-ordering; ensures classical Hebbian mechanism wired correctly).
- 3 different rho at same alpha produce 3 distinct sha256 fingerprints
  (arms-must-differ selftest).
- Bipolar values are +/- 1/sqrt(N) (encoding regime correct).

## Discriminator gates

**HP (per seed; both must fire):**

- HP_MONOTONE:
    In FULL grid: for AT LEAST ONE alpha in {0.10, 0.138, 0.15},
    Spearman(rho, recall) across rho in {0.0, 0.1, 0.3, 0.5, 0.7} <= -0.5
    (recall trending downward with correlation).
    In SMOKE grid: recall(rho=0.0, alpha=0.10) - recall(rho=0.7, alpha=0.20)
    >= 0.30 (large observable drop across rho).

- HP_WALL_SHIFTS_DOWN:
    For SOME rho in {0.5, 0.7} at SOME alpha in {0.05, 0.10, 0.138, 0.15, 0.20},
    recall(rho, alpha) < 0.50 (wall crossed for correlated) AND
    recall(rho=0.0, alpha) >= 0.90 (independent baseline intact at same alpha).

**HF (per seed):**

- HF_CARDINALITY: n_units != expected (25 FULL / 3 SMOKE).
- HF_INDEP_CRUMBLES: recall(rho=0.0, alpha=0.10) < 0.90 (broken-PC:
  independent baseline collapses; can't trust correlation wall).
- HF_CRUMBLE_ALL: all rho at alpha=0.05 below 0.20 recall (encoder broken).
- HF_NO_WALL_ANY_RHO: recall(rho=0.7, alpha=0.20) >= 0.50 (substrate does
  NOT exhibit correlation-induced capacity wall; refutes Loewe on substrate).
- HF_META_RULE_AF: bit-identical arm sha256 across DIFFERENT (rho, alpha)
  configs (ceiling-tie exempt: both at exactly 1.000 AND same alpha).
- HF_CORRELATION_GEN_BREACH: empirical rho at M>=200 deviates from nominal
  by > 0.03 (correlated-key generator broken).

**MB:** partial HP condition (e.g., monotone fires but wall_shifts doesn't,
or vice versa).

**Chain-grade (Skunkworks 3-seed aggregation):**
- 3-of-3 seeds HARD_PASS AND cv(recall) < 15% at each (rho, alpha).
- CHAIN_GRADE_CORRELATED_KEY_CAPACITY_WALL_CHARACTERIZED.

## Pre-registered fairness disciplines

1. Same N=8192 for all phase points across all seeds.
2. Same generation algorithm (shared-component) for all rho values.
3. Same storage (classical Hebbian outer-product) for all phase points.
4. Per-unit RNG seeded (seed*251 + rho-index*100003 + alpha-index*31); no
   cross-unit aliasing.
5. Values ALWAYS drawn independent of keys' rho (only keys carry correlation).
6. Empirical rho check (at M>=200) verifies correlation-generation is honest.
7. META_RULE_AF bit-identical guard on arm sha256 (keys + vals + recall hash).
8. rho=0.0 arm at alpha=0.10 acts as positive control (broken-PC): must
   maintain recall >= 0.90 else HF fires.

## Pre-reg fields (SCHEMA-VET)

- expected_n_units = 25 (FULL) or 3 (SMOKE).
- cardinality_ok mandatory.
- HARD_FAIL_CARDINALITY_BREACH_META_RULE_H when n_units mismatch.
- HARD_FAIL_META_RULE_AF_BIT_EXACT (any bit-identical arms outside exemption).
- HARD_FAIL_CRUMBLE, HF_INDEP_CRUMBLES, HF_NO_WALL_ANY_RHO per verdict logic.
- discriminator_survives_scale: True (smoke uses N=N_FULL=8192).
- CRLB fields (COMPUTED@python):
  - crlb_floor_computed_M_max = sqrt(0.25/1638) = 0.0124 THEORETICAL@binomial-CLT
  - crlb_floor_computed_M_alpha_010 = sqrt(0.25/819) = 0.0175 THEORETICAL
  - discriminator_reachability = True (HP gap 0.40 >> CRLB 0.02; ratio ~23x)
- calibration_check = "correlated_key_capacity_wall_shift".
- sec 13 patterns: start_marker + crash_diagnostic + per-seed ckpt + heartbeat.
- arms_differ_verified: True (META_RULE_AF gate in verdict).
- final_metrics_atomicity: "tmp_replace" (META_RULE_AH).
- positive_control_arms: (rho=0.0, alpha=0.10) at every seed.
- theory_reference: Loewe (1998) alpha_c(rho) = alpha_0 * (1 - rho^2).
- prior_work_check: substrate-KB cosine top-1 = 0.27 (not overlapping).
- run_mode wiring: cell defaults RUN_MODE=full unless --smoke or HDLAB_RUN_MODE=smoke
  or HDLAB_EXP_NAME ends with _smoke.

## Smoke config

- N=8192 (same as FULL; DISCRIMINATOR-MUST-SURVIVE-SCALE).
- 3 phase points: (0.0, 0.10), (0.5, 0.10), (0.7, 0.20).
- Numpy backend on local_cpu_queue (USER-locked: smoke ONLY on local).
- Discriminator MUST FIRE at smoke to justify FULL dispatch:
  - Prototype MEASURED: expected recall(0.0, 0.10)=1.000; recall(0.5, 0.10)=0.253;
    recall(0.7, 0.20)=0.056.
  - HP fires if drop across rho >= 0.30 (measured drop 1.000 - 0.056 = 0.944)
    AND (0.5, 0.10) recall < 0.50 (measured 0.253) AND (0.0, 0.10) recall
    >= 0.90 (measured 1.000).
  - HF fires if (0.7, 0.20) recall >= 0.50 (substrate lacks wall) OR
    (0.0, 0.10) recall < 0.90 (broken baseline).
- Expected smoke wall: ~2-4 min per seed (3 units at N=8192 numpy Hebbian).

## FULL config (per seed, if smoke HP)

- N=8192, 25 phase points, all seeds.
- Numpy backend on remote_cpu_queue.
- Per-seed timeout: 3600s (60 min). Empirical estimate: alpha=0.20 M=1638
  unit takes ~200s on laptop CPU (prototype); scaled to 25 units at variable
  M yields ~600-1200s per seed on remote; 3600s = 3x safety.
- If any seed exceeds timeout: partial-checkpointed via
  experiments/_seed_checkpoint helpers (write_partial_key + aggregate_partials).

## Cap-map rows (proposed; on 3-of-3 HP across seeds)

- CG on correlated-key classical-Hebbian capacity wall:
  "Substrate classical Hebbian storage exhibits alpha_c(rho) shift matching
  Loewe (1998) prediction alpha_c(rho) approx alpha_0 * (1 - rho^2); wall
  crossed at rho=0.5 for alpha >= 0.10 and rho=0.7 for alpha >= 0.10."
- M3 architecture implication: de-correlate keys at write time OR route through
  VSA bind-structured encoding to keep effective rho near zero.

## Coordination

- Cell-author: hdi_exp_dev (this dispatch; seed_7 smoke first via local_cpu).
- Push+FULL dispatch: hdi_orchestrator (harness-DENIED push for exp_dev;
  routes to remote_cpu_queue via SSH after commit-and-push).
- Landed-VET: hdi_skunkworks (3-seed aggregation + Spearman audit).

## Risk + mitigations

- **rho=0.0 recall stays saturated across grid**: NOT a bug. Prototype shows
  bipolar-sign readout absorbs the classical 0.138 wall (rho=0.0 recall=1.000
  at alpha=0.20). This is a known substrate behavior; the cell tests the SHIFT
  in alpha_c with rho, not the absolute rho=0.0 wall. HP does not require
  rho=0.0 to crumble.
- **rho=0.3 may be too mild to observe distinct wall**: predicted alpha_c(0.3)
  = 0.126, close to alpha_0=0.138. Prototype not tested for rho=0.3; may
  land in MIDDLE_BAND at alpha=0.138 (recall ~0.5). This is INFORMATIVE; not
  a fail.
- **Empirical rho at low N (near-independent keys with small M)**: at rho=0.0
  and small M, off-diagonal cosine has 1/sqrt(N) shot noise; may deviate from
  0.0 by ~0.02. EMP_RHO_TOLERANCE=0.03 accepts this. Only checked at M>=200.
- **Verdict Spearman with 5 rho values only**: cannot reject monotone at
  p < 0.05 with 5 points; using Spearman <= -0.5 as effect-size floor
  (equivalent to at least ~"clear negative trend"). Cross-seed 3-of-3
  consistency is the chain-grade guard.

## Differences from adjacent cells

- v1 (this) vs wave14h_alpha_sweep_v2 (2026-05-20):
  - This cell: capacity WALL (recall vs alpha under classical Hebbian).
  - v2: LEAK RATE (retention after anti-Hebbian erase). Different question.
  - This cell uses shared-component rho model; v2 uses rank-L subspace.
- v1 (this) vs cortex_hippo_dense_beta_sweep_v2_correlated_keys (2026-07-01):
  - This cell: rho-alpha grid at classical Hebbian; measures capacity wall.
  - Sibling cell: beta-axis discrimination at dense softmax READ-REPLACE.
  - Different mechanism, different question, complementary sub-drills.

## Milestone significance

If HP (all 3 seeds pass): **CG on correlated-key capacity wall characterization**.
Stage 1 100% close per USER directive; substrate matches Loewe (1998)
prediction and gives quantitative alpha_c(rho) shift for M3 architecture design.

If MB (partial): monotone fires but wall shift narrower than predicted;
suggests classical Hebbian primitive is more correlation-tolerant than
theory predicts. Informative substrate physics finding.

If HF (crumble): baseline broken; encoder issue; re-queue after debug.

If HF (no wall): substrate does NOT exhibit correlation-induced capacity
wall. This is the most interesting negative result: refutes classical
correlated-Hopfield theory on substrate; would motivate a Research drill
into WHY (e.g., bipolar-sign readout absorbs correlation).

## Citations

- Loewe, M. (1998). "On the storage capacity of Hopfield models with
  correlated patterns." Annals of Applied Probability 8(4).
- Amit, Gutfreund, Sompolinsky (1987). "Statistical mechanics of neural
  networks near saturation." Annals of Physics 173. -- alpha_0=0.138.
- Kanerva, P. (1988). Sparse Distributed Memory. -- SDM correlated-address
  degradation ties in.
- Research drill: notes/research_correlated_key_capacity_hopfield_fhrr_2026-07-01.md
  (this cell's motivating drill; source of HP1-HP4 falsifiable predictions).

## Reference prior cells

- Cell D v1 CG: independent-key alpha_c=0.138 (baseline).
- Wave 14h alpha_sweep_v2 (adjacent; correlated-keys anti-Hebbian erase):
  preregs/2026-05-20_wave14h_alpha_sweep_v2.md.
- cortex_hippo_dense_beta_sweep_v2_correlated_keys (sibling; different
  mechanism/regime): preregs/2026-07-01_cortex_hippo_dense_beta_sweep_v2_correlated_keys.md.
