# LABEL-VS-HONEST BACK-VALIDATION (2026-05-29)

## Trigger and scope

Commit 32b1337 trimmed `_validate_metrics_schema` in `experiments/runner_v2_prod.py`
to `("verdict_msg", "elapsed_s")` plus an OR-accept on `verdict` / `verdict_tag`.
The OLD schema gate (pre-32b1337) hard-required `("verdict", "verdict_msg",
"elapsed_s", "summary")`, which falsely failed any script emitting `verdict_tag`,
`cells`, `all_cells`, or `config` instead of `verdict` + `summary`. That false-fail
manifested as the DISPATCH_FAILURE_MISCLASSIFICATION sub-flavor in the
label-vs-honest history.

This back-validation re-applies the NEW (32b1337) schema gate to every catch
recorded under the DFM sub-flavor and to the adjacent v265 / v266 catches that
shared the same forensic class (DISPATCH_HEADLINE_OVER_CLAIM +
MIDDLE_BAND_HIDES_DIRECTIONAL_CORROBORATION). Total in scope = 18 catches
(idx 106..123 in the cumulative label-vs-honest counter).

Catches 1..105 were OVER-CLAIM / UNDER-CLAIM / dispatch-framing / MMD-vs-MP-KS
flavors unrelated to the schema-gate fix; they are NOT in scope for this re-read
and remain as recorded (verdict_handler honest reads at the time were the
truth, no schema mismatch).

## Method

For each catch:
1. Loaded the REMOTE metrics.json via SSH (per the e51aee7 remote-first contract;
   local copies are typically pre-ship smoke at N<=1024).
2. Applied the NEW `_validate_metrics_schema` (verdict_msg + elapsed_s required;
   either `verdict` or `verdict_tag` accepted).
3. Classified per the back-validation taxonomy:
   - VERIFIED_HARD_PASS = gate accepts AND verdict tag is HARD_PASS-flavored
     AND per-cell evidence meets pre-reg.
   - PARTIAL = gate accepts AND verdict tag is MIDDLE_BAND / PARTIAL.
   - GENUINE_FAILURE = gate rejects, OR verdict tag is HARD_FAIL.
   - UNRECOVERABLE = metrics.json missing on remote (and local).

## Summary table

| class                  | count | percent of 18 |
|------------------------|-------|---------------|
| VERIFIED_HARD_PASS     | 13    | 72%           |
| PARTIAL                | 5     | 28%           |
| GENUINE_FAILURE        | 0     | 0%            |
| UNRECOVERABLE          | 0     | 0%            |
| TOTAL                  | 18    | 100%          |

Headline: **0 of 18 converts to a NEW HARD_PASS not already absorbed by the
cap_map**. Every one of the 13 VERIFIED_HARD_PASS catches was already overridden
to HARD_PASS by the verdict_handler at the time it processed the verdict, with
the remote metrics as the authoritative source (the queue-status "failed" label
was discarded). The "label-vs-honest catch" counter records the override event,
not a still-pending discrepancy.

## Per-catch detail (catch index 106..123)

### v265 (1 catch, sub-flavor DISPATCH_HEADLINE_OVER_CLAIM)

- **106 saad_solla_v14_n8192_3seed** -> PARTIAL
  - vtag=SS_V14_MIDDLE_BAND elapsed=5283s N=8192 smoke=False
  - pass_seeds=0/3 (mean_r2=0.936, mean_max_dev=0.141 vs HP gate r2<0.85 OR
    max_dev>=0.40 fires only via R^2 NEAR-MISS; TIGHT max_dev<0.08 fails)
  - Cap_map honest read = MIDDLE_BAND (Saad-Solla checkmark UNCHANGED, sub-objective
    TIGHT-gate not met). No conversion.

### v266 (1 catch, sub-flavor MIDDLE_BAND_HIDES_DIRECTIONAL_CORROBORATION)

- **107 bid_n_stability_v4_n12288** -> PARTIAL
  - vtag=BID_N4_MIDDLE_BAND elapsed=4277s N=12288 smoke=False
  - BID(N=12288)=270 OUTSIDE [110, 250] static-Hopfield corridor on HIGH side
    (extrapolation 278 within stochastic envelope)
  - Cap_map honest read = MIDDLE_BAND with directional corroboration noted
    (substrate-outside-static-Hopfield row 60-72% UNCHANGED). No conversion.

### v267 (7 catches, sub-flavor DISPATCH_FAILURE_MISCLASSIFICATION)

- **108 saad_solla_v16_n8192** -> VERIFIED_HARD_PASS
  - vtag=SS_V16_HARD_PASS elapsed=10769s N=8192 smoke=False
  - pass_results=2/2 BOTH M_fracs=[0.25, 0.5] M-density plateau
  - Cap_map: Saad-Solla checkmark UNCHANGED + M-density evidence strengthened.
    Already applied.

- **109 t1_beta_sweep_v1_n4096** -> VERIFIED_HARD_PASS
  - vtag=T1_BETA_HARD_PASS elapsed=4.23s N=4096 smoke=False
  - pass_seeds=5/5 mean_max_gradient=0.247 (vs HP_grad=0.15)
  - Cap_map: NEW row "beta-axis phase boundary green-smoke 60-72%". Already applied.

- **110 t2_codebook_boundary_v1_n4096** -> VERIFIED_HARD_PASS
  - vtag=T2_CB_HARD_PASS elapsed=2.5s N=4096 smoke=False
  - pass_seeds=3/3 mean_slope=0.202 monotone
  - Cap_map: NEW row "codebook-order phase boundary green-smoke 55-68%". Already applied.

- **111 saad_solla_v17_cross_cb_v1_n4096** -> VERIFIED_HARD_PASS
  - vtag=SS_V17_HARD_PASS elapsed=1.62s N=4096 smoke=False
  - family_pass={bsc: 3, antipodal: 3} HP_MAJORITY_MIN=2 both clear
  - Cap_map: Saad-Solla checkmark + codebook-axis strengthened. Already applied.

- **112 moe_capacity_aware_router_v1_n4096** -> VERIFIED_HARD_PASS
  - vtag=MOE_CAP_HARD_PASS elapsed=2082s N=4096 smoke=False
  - mean_ret_by_K K=16=0.979 delta=-0.000 (vs HP_RET>=0.7 delta>=-0.05)
  - Cap_map: MoE K-scaling checkmark + meta-learning corroborated. Already applied.

- **113 pb2_corr_len_v2_n1024** -> VERIFIED_HARD_PASS
  - vtag=PB2_CORR_HARD_PASS elapsed=2.33s N=1024 smoke=False
  - xi_normalized=0.094 < HP_xi_max=1.0 at M_frac=1 monotone bounded
  - Cap_map: NEW row "edit-propagation finite correlation-length green-smoke 55-68%".
    Already applied.

- **114 kf2_cross_codebook_v1_n4096** -> VERIFIED_HARD_PASS
  - vtag=KF2_CROSS_HARD_PASS elapsed=82.3s N=4096 smoke=False
  - family_max={kerdock: 0.0202, bsc: 0.0303, gaussian: 0.0202} all < HP=0.05
  - Cap_map: KF-2 checkmark + cross-codebook strengthened. Already applied.

### v268 (3 catches, sub-flavor DISPATCH_FAILURE_MISCLASSIFICATION)

- **115 kf1_hallu_rescue_v1_n4096** -> VERIFIED_HARD_PASS
  - vtag=KF1_RESCUE_HARD_PASS elapsed=3.87s N=4096 smoke=False
  - pass_seeds=3/3 entropy_gap=12.94 bits (12.9x safety vs HP_min=1.0)
  - Cap_map: KF-1 row at-risk -> green-smoke 55-70%. Already applied.

- **116 t1_beta_fine_v2_n4096** -> VERIFIED_HARD_PASS
  - vtag=T1_FINE_HARD_PASS elapsed=3.89s N=4096 smoke=False
  - pass_seeds=5/5 gradient=0.582 (2.4x sharper than v1) beta_c=10.0+/-0.0
  - Cap_map: beta-axis row 60-72% -> 65-78% LIFT +5%. Already applied.

- **117 kf2_cross_codebook_v2_n8192** -> VERIFIED_HARD_PASS
  - vtag=KF2_CROSS_V2_HARD_PASS elapsed=14.71s N=8192 smoke=False
  - family_max all 0.0202 < HP=0.05 (2.48x safety margin)
  - Cap_map: KF-2 production-scale strengthened. Already applied.

### v269 (6 catches, sub-flavor DISPATCH_FAILURE_MISCLASSIFICATION)

- **118 tcft_alpha_sweep_v1_n8192** -> PARTIAL
  - vtag=TCFT_ALPHA_MIDDLE_BAND elapsed=17217s N=8192 smoke=False
  - alpha_max_cert=0.500 (2x HP_alpha_target=0.25); alpha_c=None (no sharp
    transition)
  - Cap_map honest read = MIDDLE_BAND; no row impact recorded. No conversion.

- **119 moe_fixed_total_capacity_K_sweep_v1_n4096** -> VERIFIED_HARD_PASS
  - vtag=MOE_FIXED_CAP_HARD_PASS_NO_CEILING elapsed=16.55s N=4096 smoke=False
  - ret_K16=1.0 delta=0.0; entropy_by_K reaches log2(K) all cells
  - Cap_map: MoE K=32 CEILING-BUSTER annotation. Already applied.

- **120 pb2_corr_len_v3_n4096** -> VERIFIED_HARD_PASS
  - vtag=PB2_V3_HARD_PASS elapsed=33.15s N=4096 smoke=False
  - xi_m1=0.0197 << HP=1.0 (50x safety margin) pass_finite=3/3
  - Cap_map: edit-propagation row promotion smoke->green +10%. Already applied.

- **121 lyapunov_v1_n4096** -> PARTIAL
  - vtag=LYAP_MIDDLE_BAND elapsed=62.16s N=4096 smoke=False
  - 4-cell M-sweep mono_frac=1.0 spec_norms [2.21, 4.0, 8.0, 12.0] (perfectly
    linear but no HARD_PASS-tier criterion fired -- exploratory NEW row)
  - Cap_map: NEW row "edge-of-chaos Lyapunov dynamical structure yellow-smoke
    55-68%" at creation. MIDDLE_BAND drove the NEW row at conservative yellow-
    smoke band. No conversion (row creation already captures the value).

- **122 lyapunov_v2_n8192_bsc** -> VERIFIED_HARD_PASS
  - vtag=LYAP_V2_HARD_PASS elapsed=71.8s N=8192 smoke=False
  - variation=1.49 monotone in 3/3 seeds N=8192 BSC
  - Cap_map: NEW row edge-of-chaos Lyapunov strengthened at creation
    (dual-N evidence). Already applied.

- **123 bid_order_parameter_v5_n8192_bsc** -> PARTIAL
  - vtag=BID_V5_MIDDLE_BAND elapsed=94.82s N=8192 smoke=False
  - bid_outside_at_low=True 3/3 mean_bid_at_0.5=664 (decreasing=False so not
    HARD_PASS; outside-at-low is directional MIDDLE_BAND)
  - Cap_map: substrate-outside-static-Hopfield 60-72% -> 64-75% LIFT +4%.
    Already applied as directional MIDDLE_BAND lift.

## VERIFIED_HARD_PASS catches that warrant cap_map row promotions

**ZERO**. Every one of the 13 VERIFIED_HARD_PASS catches was already promoted
into the cap_map at the time the verdict_handler processed the verdict. The
verdict_handler's honest re-read protocol (per
[[feedback-verdict-msg-honest-reread]]) and the remote-first contract (e51aee7)
correctly treated the remote metrics.json as authoritative and overrode the
runner's queue-status "failed" tag.

## GENUINE_FAILURE catches that should stay as recorded

**ZERO**. None of the 18 catches re-classifies to GENUINE_FAILURE. The 5
PARTIAL re-classifications are honest MIDDLE_BAND outcomes that the cap_map
correctly recorded as MIDDLE_BAND at the time.

## Recommended cap_map deltas

**ZERO row LIFTS recommended**. The forward-process worked as designed: the
verdict_handler caught the runner's schema-gate false-fail in real time and
wrote the honest reading into the cap_map. The 32b1337 fix is structural
prevention for FUTURE verdicts; it does not change the truth of any past
cap_map row.

## Audit-trail observation

The "label-vs-honest catch counter" naming is slightly misleading on re-read:
the counter records moments where the verdict_handler's honest reading DIFFERED
from a literal label (queue-status, dispatch context, or runner output) and the
honest reading prevailed in the cap_map. The cap_map state therefore already
reflects the honest reading; there is no backlog of un-applied promotions.

The 16 DFM catches in v265+v267+v268+v269 are exactly the population the user
hypothesized would convert, but they are ALL already in the HARD_PASS state in
the cap_map -- the verdict_handler honest re-read absorbed them at the time.

The structural value of 32b1337 is to eliminate the FUTURE verdict_handler tax:
without 32b1337, every future HARD_PASS run that emits `verdict_tag`/`cells`/
`config` would need a manual honest re-read to recover from the false-fail.
With 32b1337 the runner emits accurate verdicts and the verdict_handler honest
re-read step rarely fires for this sub-flavor.

## ONE-line summary

back-validated 18/123 (DFM sub-flavor scope): 13 VERIFIED_HARD_PASS / 0
GENUINE_FAILURE / 5 PARTIAL / 0 UNRECOVERABLE; 0 cap_map row LIFTS recommended
(all 13 HARD_PASS were already absorbed by verdict_handler honest re-read at
time of verdict).
