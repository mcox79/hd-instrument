# Routing: orchestrator -- cheap-Lambda 3-pack verdicts (3 HARD_PASS)

**From**: testbed session
**To**: orchestrator (strategy + verdict_handler)
**Date**: 2026-05-31
**Type**: cloud-experiment results delivery
**Severity**: standard; 3 verdicts for cap_map ingestion

## TL;DR

All 3 cheap-Lambda anchors HARD_PASS. Cumulative session spend $1.40.
Cleanup verified. Suggest cap_map LIFT moves on Path D ceiling +
Modern Hopfield ceiling + adversarial-defense row(s). Detailed
verdicts + metrics-file paths below.

## Pre-flight context

- Testbed dispatched the 3-pack after `_metric_battery` selftest fix
  landed (orchestrator commit 7959353); Lambda `git clone` now pulls
  the previously-missing `exp_t1_beta_sweep_v1_n4096.py`.
- Launched sequentially, each user-authorized.
- All 3 used the new `tools/cloud/generic_progress_wrapper.py` with
  `--total-cells` per anchor; live progress visible in dashboard
  (`/api/snapshot` -> `lambda_progress`) for batches 2/3 + 3/3.

## Verdict 1/3: `path_d_24n_32n_envelope_v1_n4096`

- **Verdict**: `G7_HARD_PASS`
- **verdict_msg**: `PATH_D_PAST_32N_ENVELOPE: all 40 cell-seeds >= 0.85.
  M98304: d10=1.000 d20=1.000 d30=1.000 d50=1.000 | M131072:
  d10=1.000 d20=1.000 d30=1.000 d50=1.000`
- **Hard-numeric**: 40 cells x acc=1.000 across (M, d, seed) =
  ({98304, 131072}, {10, 20, 30, 50}, {7, 17, 23, 31, 41}); N=4096
- **Wall**: 10.8 min  **Cost**: $0.23
- **Instance**: `c4f84cf820984a5992ad820d669bd6f8` (terminated clean)
- **Metrics**:
  `data/lambda_exp_path_d_24n_32n_envelope_v1_n4096_metrics_c4f84cf820984a5992ad820d669bd6f8.json`
- **Report**:
  `data/lambda_exp_path_d_24n_32n_envelope_v1_n4096_report_c4f84cf820984a5992ad820d669bd6f8.json`
- **Suggested cap_map move**: R-PATH-D-NO-CEILING row LIFT past 32N
  envelope at N=4096; per-cell numerics support a substantially
  higher upper bound. Honest re-read recommended: label "G7_HARD_PASS"
  is consistent with all-1.000 per-cell.

## Verdict 2/3: `modern_hopfield_cpu_extended_v9_n16384`

- **Verdict**: `C9_HARD_PASS`
- **verdict_msg**: `CEILING_PAST_16N (target>=262144): constructed=3/3
  max_M_per_seed=[262144, 262144, 262144]`
- **Hard-numeric**: 3 seeds (7, 17, 23) all constructed at M=262144
  = 16x N=16384; construction_s ~20-21s per seed
- **Wall**: 11.8 min  **Cost**: $0.25
- **Instance**: `b373f71fcf964657ac611b9b7b925375` (terminated clean)
- **Metrics**:
  `data/lambda_exp_modern_hopfield_cpu_extended_v9_n16384_metrics_b373f71fcf964657ac611b9b7b925375.json`
- **Report**:
  `data/lambda_exp_modern_hopfield_cpu_extended_v9_n16384_report_b373f71fcf964657ac611b9b7b925375.json`
- **Suggested cap_map move**: Modern Hopfield NEW row at v229 was
  0.65-0.80 conservative on cross-codebook + M>N. C9_HARD_PASS at
  M=16N confirms ceiling past 4N at the largest N tested.
  Per-cell numerics support LIFT.

## Verdict 3/3: `adversarial_codebook_collision_defense_probe_v1_n4096`

- **Verdict**: `G8_HARD_PASS`
- **verdict_msg**: `DEFENSE_VIABLE n_hp=1/2. a_query_sim: def=1.000
  fp=0.000 | b_dist_check: def=1.000 fp=1.000`
- **Hard-numeric**: 5 seeds (7, 17, 23, 31, 41); a_query_sim achieves
  perfect 1.000 defense at 0.000 false-positive rate; b_dist_check
  achieves 1.000 defense but at 1.000 fp (rejects all queries; broken)
- **Wall**: 5.6 min  **Cost**: $0.12
- **Instance**: `350c53eae5594733bda43c9b88424037` (terminated clean)
- **Metrics**:
  `data/lambda_exp_adversarial_codebook_collision_defense_probe_v1_n4096_metrics_350c53eae5594733bda43c9b88424037.json`
- **Report**:
  `data/lambda_exp_adversarial_codebook_collision_defense_probe_v1_n4096_report_350c53eae5594733bda43c9b88424037.json`
- **Suggested cap_map move**: adversarial-defense row -- one defense
  (a_query_sim) is viable at the production setting (n_adv=32 n_leg=64,
  N=4096, M=2048). The other (b_dist_check) is mathematically working
  but operationally broken at fp=1.0. n_hp=1/2 means HARD_PASS gate
  was set at >=1 viable defense; that's been hit.
- **Honest re-read note**: experiment elapsed=1.81s on GPU; the wall
  time was overwhelmingly bootstrap + boot. Per-cell numerics are
  tight (5/5 seeds at def=1.000 for a_query_sim).

## Session totals

- **Cumulative spend**: $1.40
  ($0.80 V1 canary chain + $0.23 + $0.25 + $0.12)
- **Active instances at session end**: 0 (all terminated, confirmed
  via `client.list_instances()`)
- **Leak flags**: none

## Infrastructure delivered this session (separate from verdicts)

- `tools/cloud/generic_progress_wrapper.py` (push 4229ab2): generic
  cell-counting wrapper for every Lambda anchor; takes `--cell-regex`
  + `--total-cells`; emits `progress.json` via ProgressEmitter.
- `tools/cloud/launch_experiment.py` ProgressPoller integration
  (push 4229ab2): SCPs `progress.json` every 30s; prints live
  `[progress HH:MM] anchor cell N/M (X%) phase ETA Ks` to stdout.
- `tools/dashboard/poller.py` + `static/index.html` (push bbd6cd6):
  exposes `snapshot.lambda_progress`; Lambda card shows active
  anchor + cell N/M + ETA in real time.
- `tools/cloud/cost_tracker.py` (pushes 5e05e34 + 53fe754):
  daily-budget framing dropped (per-run-authorized model);
  `accumulate_run_cost` helper makes accumulated_today_usd actually
  cumulative across runs, not overwriting.

## Recommended orchestrator actions

1. Run verdict_handler on 3 verdicts (G7_HARD_PASS, C9_HARD_PASS,
   G8_HARD_PASS) with the honest-re-read protocol per PROT-018.
2. cap_map version bump v294 -> v295 (or current) with the 3 LIFTs
   above as suggestions for the verdict_handler agent.
3. Status_log already has HIGH entry for batch 1/3; testbed will
   write HIGH entries for 2/3 + 3/3 right after this routing file.

## Files of interest

- This routing file
- Three metrics.json files (paths above)
- Three report.json files (paths above)
- `notes/testbed_decisions_2026-05-31.md` (full session state)
- `data/cloud_cost_tracker.json` (now correctly shows $1.40 cumulative)
