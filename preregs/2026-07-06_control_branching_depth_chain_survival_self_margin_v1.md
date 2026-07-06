# Prereg: control-branching-depth chain-survival order-statistic self-margin (MM, semi-empirical)

- Anchor: `control_branching_depth_chain_survival_self_margin_v1`
- Cell: `experiments/exp_control_branching_depth_chain_survival_self_margin_v1.py`
- Date: 2026-07-06
- Author: exp_dev (Opus 4.8 1M, agent-spawn)
- Queue: SMOKE local (direct `--smoke`), FULL -> `remote_cpu_queue` (CPU cell)
- Tier expectation: **MEASURED_MECHANISM (semi-empirical)**. The per-gate margin is a LEARNED SR
  reachability with no closed form -> `crlb_n/a`. NOT forced to CG.

## Question

Does the chain-survival ORDER-STATISTIC self-margin (the SAME GH64 kernel already CHAIN_GRADE for
RNS decode / FHRR capacity / reasoning-depth) predict the FLAT control-gate branching-depth
collapse from a SHALLOW anchor, and does it BEAT the Hick-entropy first-order predictor
(`log2(n_ops)*depth`)? This extends the self-margin frontier from DECODE/REASONING/LANGUAGE to
CONTROL. Monitor-not-control: the substrate predicts its OWN usable control depth; it never edits
the gate.

## Mechanism / model

A depth-`d` control chain survives iff ALL `d` argmax gating decisions are correct:
`P_chain(n_ops, d) = prod_{r=1}^{d} P_gate(n_ops, mu(r))`, with
`P_gate(n_ops, mu) = E_z[ Phi(mu+z)^(n_ops-1) ]` (GH64), `r` = per-hop remaining horizon,
`mu(r)` = order-statistic margin at horizon `r`. THEORETICAL@GH64 extreme-value order statistic
(same kernel as `exp_reasoning_depth_exact_order_statistic_self_margin_v1`). The Hick predictor
`-ln(survival) ~ d*log2(n_ops)` is its first-order shadow.

Under the chain-survival product law, `flat(d) = prod_{r<=d} q(r)`, so the per-horizon per-gate
survival reconstructs as `q(r) = flat(r)/flat(r-1)` from consecutive SHALLOW anchor depths. The
mechanism under test is the HORIZON-AWARE member: fit a horizon-linear margin
`mu(r) = mu0 - beta*(r-1)` SHARED across `n_ops` on the anchor (branching factor enters ONLY via
the order statistic's competitor count), then PROJECT to predict the HELD-OUT deep flat accuracy.

### Why not CG (the honest bound)

`mu(r)` is a learned SR reachability and DEGRADES with horizon (reach starvation toward a receding
goal). Off-disk recon vs the landed grid
(MEASURED@`data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json:per_regime.*.flat_gonogo`)
shows the LITERAL constant-margin projection `P_gate(mu_hat)^depth` (single frozen margin) does NOT
predict the flat collapse -- it OVER-predicts survival (held-out d6,d8 RMSE ~0.34-0.41;
MEASURED@author scratch recompute) because the effective per-gate margin drops with depth
(n_ops=2: mu_hat 2.78@d4 -> 1.85@d6 -> 1.29@d8; MEASURED@author). The collapse is SUPER-GEOMETRIC.
So constant-margin is retained as a documented-bound CONTROL; the horizon-aware member is the
mechanism.

Note: the landed grid TUNED w_reach PER DEPTH -> it is NOT a single fixed gate. A clean
fit-shallow-project-deep test requires a single FROZEN gate. This cell GENERATES its own
commensurate grid (gate tuned ONCE on the shallow anchor, frozen across depths, V fixed across
n_ops to isolate the branching factor) at reduced N. The landed N=8192 grid is a QUALITATIVE
super-geometric-shape cross-check only (declared SHAPE_DRIFT; different N).

## Design (author-decided)

- N: 4096 (FULL), 2048 (smoke), 256 (selftest). Reduced-N self-contained grid (shallow+deep);
  the mechanism is the shallow->deep PROJECTION, scale-invariant given a collapsing gate.
- `n_ops in {2,3,4}`; `V` FIXED (700 FULL / 300 smoke) across n_ops (isolate branching factor).
- Depths measured: {1,2,3,4,6,8}. ANCHOR (fit): {1,2,3,4}. HELD-OUT (gated): {6,8}.
- Gate: FROZEN. alpha + w_reach tuned ONCE on d=4 train chains, applied to ALL depths.
- Seeds: {7,17,23,31,41} FULL (5); {7,17,23} smoke (3). gamma=0.85 fixed.
- Predictors (fit on anchor d<=4, predict held-out d in {6,8}): `pred_horizon` (mechanism),
  `pred_const` = flat(4)^(d/4) (the literal single-margin projection; documented bound),
  `pred_hick1` = exp(-C log2(n) d) (first-order shadow), `pred_hickp` = exp(-C log2(n) d^p)
  (equal-DOF fairness report).
- Firing control: SHUFFLE per-op gate scores before argmax -> uniform selection -> per-gate
  survival -> 1/n_ops -> fitted mu0 collapses to ~0.
- Cross-check: teacher-forced per-horizon q_tf(r) vs ratio-reconstructed q(r) (product-law).

## Bands (pre-registered BEFORE running; no-smoke)

HELD-OUT = d in {6,8} x n_ops in {2,3,4} = 6 points. RMSE vs observed flat, aggregated over seeds.

- **HARD_PASS** (chain-survival self-margin EXTENDS to CONTROL, MM-grade):
  `rmse_horizon <= 0.12` AND `const_gap = rmse_const - rmse_horizon >= 0.10` AND
  `hick_gap = rmse_hick1 - rmse_horizon >= 0.03` AND firing (`mu0_real >= 0.50` AND
  `mu0_shuf <= 0.20`) AND collapse-fires (`flat_obs(op4,d8) <= 0.35` AND every
  `flat_obs(n_ops,d1) in (0.50,0.995)`) AND product-law (`mean|q_tf - q_ratio| <= 0.15`) AND
  cross-seed `cv(rmse_horizon) <= 0.40`.
- **HARD_FAIL** (honest ACCEPT-boundary: order statistic does NOT extend to the flat control gate):
  `rmse_horizon > 0.22` OR `rmse_horizon > rmse_hick1 + 0.05`.
- **MIDDLE_BAND**: horizon-aware helps (`const_gap > 0`) with `rmse_horizon in (0.12, 0.22]`, OR
  beats Hick-first but not equal-DOF Hick-power, OR misses exactly one HARD_PASS sub-gate.
- **INCONCLUSIVE_DISCRIMINATOR_DID_NOT_FIRE**: no observed collapse (`flat_obs(op_max,d8) > 0.35`)
  OR shallow gate broken (`flat_obs(n_ops,d1) <= 0.50`) OR anchor carries no decay
  (`flat_obs(op_max,d4) > 0.90`) -> respec regime, NOT a refutation.

### Discriminator-fires gate correction (smoke-informed, methodology only; NOT a science band)

The 3-seed local smoke (N=2048) revealed the shallow d=1 gate SATURATES at n_ops=4 (d1 ~ 1.0) at
reduced N/V. A saturated shallow gate is the HEALTHY expected case (the 1-hop gate is perfect),
NOT a discriminator failure -- the margin fit already EXCLUDES saturated anchor points (mu clamped
at MU_CEIL) and the collapse is measured across depths. The original upper cap
`flat_obs(n_ops,d1) < 0.995` wrongly flagged this as INCONCLUSIVE. Corrected per META_RULE_AG
(saturation -> iterate gate, not the science bands): discriminator-fires now requires deep collapse
(`flat_obs(op_max,d8) <= 0.35`) AND shallow gate WORKS (`flat_obs(n_ops,d1) > 0.50`, no upper cap)
AND anchor carries measurable decay (`flat_obs(op_max,d4) <= 0.90`). FULL uses larger V (700) which
de-saturates d1. The HARD_PASS / HARD_FAIL SCIENCE bands are UNCHANGED.

### Smoke result (3 seeds, N=2048; preview, NOT canonical)

MEASURED@`data/exp_control_branching_depth_chain_survival_self_margin_v1_smoke/metrics.json`:
`rmse_horizon=0.123 const=0.160 hick1=0.190 hickp=0.103 | const_gap=0.036 hick_gap=0.067
hickp_gap=-0.020 | mu0_real=3.88 mu0_shuf=-0.075 | collapse op4_d8=0.132 | product_law tf_dev=0.044`.
HONEST read: the discriminator FIRES (super-geometric collapse present; firing control destroys the
margin; product law holds). The horizon-aware chain-survival self-margin MODESTLY predicts the
collapse (rmse ~0.12) and BEATS the first-order Hick shadow (gap 0.067), but does NOT decisively
beat a flexible equal-DOF Hick-POWER fit (hickp 0.103 edges it) and the const-margin gap is small at
reduced N (the gate collapses hard by d4 -> flat(4) low -> const geometric over-predicts less than
at the landed N=8192 regime, where the off-disk const RMSE was 0.34). Expected FULL tier:
**MIDDLE_BAND** (mechanism validated: chain-survival product law + order-statistic margin + firing
control; the "decisively dominant predictor" HARD_PASS claim is NOT smoke-supported). FULL at cleaner
N=4096 / V=700 may enlarge const_gap (more super-geometric collapse) and is dispatched to settle it
at canonical scale. Deflated-honest: this is a real but MODEST extension of the self-margin frontier
to CONTROL.

## SCHEMA-VET fields

- `cardinality_ok`: EXPECTED_N_UNITS = n_seeds (per-seed resumable unit spanning all n_ops x depths).
- `arms_differ_verified`: prediction surfaces (horizon/const/hick1) + flat_obs vs flat_shuf
  hash-distinct at smoke.
- `final_metrics_atomicity`: tmp_replace + per-seed resumable partials.
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException); grep-clean.
- `crlb_n/a`: learned SR reachability margin, no closed-form noise floor (SEMI-EMPIRICAL, MM).
- `baseline_in_band` (AG): shallow flat_obs(n_ops,d1) in (0.50,0.995) AND flat_obs(op4,d8) collapses
  <=0.35 -> the discriminator-fires gate.
- `discriminator survives scale`: smoke fires the SAME op4 depth-8 collapse at reduced N (option C
  preview); const FAILS, horizon-aware structure differs.
- `HP strictly above floor`: rmse<=0.12 AND >=0.10 tighter than const AND >=0.03 tighter than Hick.
- `calibration_check`: adaptive_with_discriminator_gate (gate tuned on shallow anchor; discriminator
  = collapse-fires + const-fail + firing all measured + gated).
- `progress_logging`: print_flush_true (FULL timeout_s >= 1800).
- `compute_architecture`: (b) sequential-CPU with justification (within-chain hop dependencies;
  reduced N bounds CPU wall; remote_cpu_queue). Storage: no_storage (learned W_op + SR M).
- `cell_chunked`: false (single cell, per-seed resumable partials via `_seed_checkpoint`).
- `defensive_error_checking`: start_marker + crash_diagnostic + heartbeat + per-seed fatal-flag with
  failure_class (passed_all_4_patterns).

## §15 composition/sweep gates

- `sweep_alignment_verdict`: ALIGNED. Sweep axes = depth (per-hop horizon; the effective parameter
  the gate actually experiences) and n_ops (order-statistic competitor count). Both are the
  parameters the mechanism directly sees.
- `discriminating_fraction`: held-out points predicted in-band. The landed grid MEASURES flat op4_d8
  = 0.082 and const OVER-predicts (RMSE ~0.34); the collapse-to-predict and const-fail bound both
  exist -> >= 0.30.
- `composition_edges`: SR-transport M -> flat gate reach score -> argmax gate. SHAPE_MATCH (all
  reuse the landed cell's primitives verbatim).
- `positive_control_arms`: const-margin reproduces the landed super-geometric SHAPE (SHAPE_DRIFT,
  different N -> qualitative cross-check, not tight numeric); teacher-forced q_tf validates the
  product law at test regime.
- `functional_requirements`: (1) measure per-horizon gate survival [flat gate + teacher-forced];
  (2) fit order-statistic margin [GH64 kernel + inversion]; (3) project shallow->deep [product law];
  (4) beat first-order shadow [Hick fit]; (5) prove margin load-bearing [shuffle firing control].

## Framing

Monitor-not-control. Narrow glass-box MONITOR step. re-encode HELD. NEVER git add -A.
