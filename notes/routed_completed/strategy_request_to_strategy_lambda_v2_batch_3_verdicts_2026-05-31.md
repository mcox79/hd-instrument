# Routing: orchestrator -- Lambda v2 batch verdicts (3 HARD_PASS)

**From**: testbed session
**To**: orchestrator (strategy + verdict_handler)
**Date**: 2026-05-31
**Type**: cloud-experiment results delivery
**Closes**: `notes/testbed_handoff_lambda_and_anthropic_authorized_2026-05-31.md`
P1 (Lambda batch portion); P2 (Anthropic) ongoing separately

## TL;DR

All 3 v2 anchors HARD_PASS at perfect 1.000/0.000 numerics. Batch cost
$0.42 of the ~$1.45 budget. Cumulative session spend $1.82.

## Verdict 1/3: `adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384`

- **Verdict**: `CROSS_N_HARD_PASS`
- **verdict_msg**: `DEFENSE_HOLDS_AT_N16384: all 15 cells >= HP threshold.
  mean_def=1.000 mean_fp=0.000 n_ok=15/15 n_hp=15 n_hf_sharp=0 |
  M4096: def=1.000 fp=0.000 | M8192: def=1.000 fp=0.000 |
  M12288: def=1.000 fp=0.000`
- **Hard-numeric**: 15 cells (3 M-values x 5 seeds) all at def=1.000
  fp=0.000 at N=16384
- **Wall**: 7.4 min  **Cost**: $0.16
- **Instance**: `11e98f7934ac43d896357bb5f26280ed` (terminated clean)
- **Metrics**: `data/lambda_exp_adversarial_codebook_collision_a_query_sim_cross_n_v1_n16384_metrics_11e98f7934ac43d896357bb5f26280ed.json`
- **Suggested cap_map move**: adversarial-sub-row LIFT 0.45-0.65 ->
  0.55-0.75 (per orchestrator's pre-batch note in
  `testbed_handoff_external_distribution_2026-05-31.md`); cross-N
  defense replication now confirmed at production N=16384.
- **Honest re-read**: label CROSS_N_HARD_PASS matches per-cell numerics;
  zero variance across all 15 cells.

## Verdict 2/3: `adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096`

- **Verdict**: `P4_AQSIM_HARD_PASS`
- **verdict_msg**: `AQSIM_GENERAL_DEFEATS_P4: all 5 cells >= HP threshold.
  mean_def=1.000 mean_fp=0.000 baseline_def=1.000 n_ok=5/5 n_hp=5 n_hf=0`
- **Hard-numeric**: 5 seeds (7, 17, 23, 31, 41) at N=4096 M=2048;
  def=1.000 fp=0.000 baseline=1.000 across all cells
- **Wall**: 5.0 min (after 1 Lambda-hardware-flake retry)  **Cost**: $0.11
- **Instance**: `f72fefe0247e46cfbc749e0df27d0429` (terminated clean)
- **Metrics**: `data/lambda_exp_adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096_metrics_f72fefe0247e46cfbc749e0df27d0429.json`
- **Suggested cap_map move + strategic implication**: a_query_sim is
  GENERAL -- defeats both codebook-collision (Exp A) AND
  edit-fact-traverse (this anchor). Per orchestrator handoff strategic
  note: **D7 edit-log-replay engineering motivation reduces
  substantially** because a_query_sim subsumes that adversarial
  pattern. Recommend the D7 row state be re-evaluated by orchestrator.
- **Operational note**: first launch of this anchor came up unhealthy
  (Lambda hardware flake on instance `90d05d00e07a4533ac8a5acdfafd6b6f`);
  launcher's `wait_for_active` detected the unhealthy status and
  terminated cleanly per design. Retry got a healthy A10 box. No
  leaked instances, no extra cost beyond brief boot.

## Verdict 3/3: `path_d_48n_64n_envelope_v1_n4096`

- **Verdict**: `G7EXT_HARD_PASS`
- **verdict_msg**: `PATH_D_PAST_64N_ENVELOPE: all 12 cells >= 0.95.
  M196608(48N): d30=1.000 d50=1.000 | M262144(64N): d30=1.000 d50=1.000`
- **Hard-numeric**: 12 cells (2 M-values * 2 depths * 3 seeds) at
  N=4096; all acc=1.000
- **Wall**: 7.0 min  **Cost**: $0.15
- **Instance**: `32eb7d0474254b5585630d7f2e0fcae2` (terminated clean)
- **Metrics**: `data/lambda_exp_path_d_48n_64n_envelope_v1_n4096_metrics_32eb7d0474254b5585630d7f2e0fcae2.json`
- **Suggested cap_map move**: R-PATH-D-NO-CEILING LIFT 0.88-0.97 ->
  0.92-0.98+ (per orchestrator's pre-batch note). Today now has:
  G7 confirmed 24N-32N (this morning), G7EXT now confirms 48N-64N.
  Combined: Path D holds perfect 1.000 from at least 24N through
  64N at N=4096.
- **Honest re-read**: label G7EXT_HARD_PASS matches per-cell numerics;
  zero variance across all 12 cells.

## Session totals (cumulative)

- **Today's Lambda spend**: $1.82
  ($0.80 V1 canary chain + $0.60 v1 cheap-batch + $0.42 v2 batch)
- **Active instances at session end**: 0 (all terminated, confirmed
  via `client.list_instances()`)
- **Leak flags**: none
- **Cost tracker** correctly accumulates across runs (53fe754 fix)

## Infrastructure validated this batch

- `tools/cloud/generic_progress_wrapper.py` worked cleanly on all 3
  anchors; live cell-by-cell progress visible in dashboard for B+C
  (A streamed fast; cells flew by between 30s SCP polls).
- `tools/dashboard/poller.py` + `static/index.html` correctly surfaced
  `lambda_progress` field; UX fix (this turn) hides stale anchor
  when stale_s > 90 AND shows "in flight (booting)" placeholder when
  cost_tracker shows active instance but no fresh progress yet.
- `tools/cloud/cost_tracker.py` accumulates correctly across runs
  (the prior overwrite bug is fixed in 53fe754).
- Lambda-hardware unhealthy-on-launch behavior handled gracefully
  by `wait_for_active` + cleanup + leak-flag-on-fail pattern.

## Recommended orchestrator actions

1. Run verdict_handler on 3 verdicts (CROSS_N_HARD_PASS,
   P4_AQSIM_HARD_PASS, G7EXT_HARD_PASS) with the honest-re-read
   protocol per PROT-018.
2. cap_map version bump (v297 -> v298 or current) with the 3
   suggested LIFTs above. Specifically: adversarial-sub-row up;
   D7 edit-log-replay row re-evaluation (likely downgrade in
   priority); R-PATH-D-NO-CEILING further LIFT toward upper bound.

## Files of interest

- This routing file
- Three metrics.json files (paths above)
- Three report.json files
- `notes/testbed_decisions_2026-05-31.md` (full session state)
- `data/cloud_cost_tracker.json` (now correctly shows $1.82 cumulative)
